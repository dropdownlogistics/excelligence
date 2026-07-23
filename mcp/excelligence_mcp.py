"""
Excelligence MCP Server — Dream Job D
Exposes the Excelligence registry graph as callable tools for any AI session.

Tools:
  query_entry(query)         — look up an entry by ID or name
  find_path(from_id, to_id)  — BFS learning path between two entries
  diagnose(formula)          — identify functions, flag anti-patterns
  prerequisites(id)          — return what must be known before this entry

Usage:
  uvx --from . mcp run excelligence_mcp
  OR: uv run mcp run excelligence_mcp.py

Add to claude_desktop_config.json:
  "excelligence": {
    "command": "uv",
    "args": ["run", "--directory", "/path/to/excelligence/mcp", "mcp", "run", "excelligence_mcp.py"]
  }
"""

import json
import re
from collections import deque, defaultdict
from pathlib import Path
from mcp.server.fastmcp import FastMCP

REGISTRY_PATH = Path(__file__).parent.parent / "excelligence.json"

# ── Registry load + index ──────────────────────────────────────────────────────

def _build_index():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        registry = json.load(f)

    by_id = {}
    by_name = {}
    graph = defaultdict(list)       # id -> [(target_id, edge_type)]
    reverse = defaultdict(list)     # id -> [(source_id, edge_type)]

    for entry in registry["entries"]:
        by_id[entry["id"]] = entry
        by_name[entry["name"].lower()] = entry
        for alias in entry.get("aliases", []):
            by_name[alias.lower()] = entry

    for edge in registry["edges"]:
        src, tgt, etype = edge["source"], edge["target"], edge["type"]
        graph[src].append((tgt, etype))
        reverse[tgt].append((src, etype))

    return registry, by_id, by_name, dict(graph), dict(reverse)


_registry, BY_ID, BY_NAME, GRAPH, REVERSE = _build_index()

# ── Helpers ────────────────────────────────────────────────────────────────────

def _resolve(query: str):
    """Return an entry dict or None. Tries ID → exact name → substring."""
    e = BY_ID.get(query.upper())
    if e:
        return e
    e = BY_NAME.get(query.lower())
    if e:
        return e
    # substring fallback
    q = query.lower()
    for key, entry in BY_NAME.items():
        if q in key:
            return entry
    return None


def _format_entry(e: dict, brief: bool = False) -> str:
    header = f"{e['id']} — {e['name']} [{e['type']} | {e['tier']} | diff {e['difficulty_score']}/5]"
    if brief:
        return f"{header}\n  {e['intent']}"
    parts = [
        f"## {header}",
        f"**What it does:** {e['what_it_does']}",
        f"**Intent:** {e['intent']}",
        f"**Example:**\n```\n{e['example']}\n```",
        f"**Failure modes:** {e['failure_modes']}",
        f"**Governance:** {e['governance_notes']}",
    ]
    if e.get("performance_notes"):
        parts.append(f"**Performance:** {e['performance_notes']}")
    if e.get("excel_version"):
        parts.append(f"**Version:** {e['excel_version']}")
    if e.get("tags"):
        parts.append(f"**Tags:** {', '.join(e['tags'])}")
    return "\n\n".join(parts)


# ── Anti-pattern heuristics ────────────────────────────────────────────────────

VOLATILE_FUNCTIONS = {"NOW", "TODAY", "RAND", "RANDBETWEEN", "OFFSET", "INDIRECT"}
LEGACY_LOOKUPS = {"VLOOKUP", "HLOOKUP"}
_HARDCODED_NUM = re.compile(r'(?<![A-Z0-9_])[2-9]\d*(?:\.\d+)?(?![A-Z0-9_\)])')


def _diagnose_ants(formula: str) -> list[tuple[str, str]]:
    """Return list of (ANT-ID, reason) tuples for the formula."""
    warnings = []
    f_upper = formula.upper()

    # Volatile functions — ANT-0002
    found_vol = VOLATILE_FUNCTIONS & set(re.findall(r'\b([A-Z]+)\s*\(', f_upper))
    if found_vol:
        warnings.append(("ANT-0002", f"Volatile function(s) detected: {', '.join(sorted(found_vol))}"))

    # Nested IFs — ANT-0004
    if_count = len(re.findall(r'\bIF\s*\(', f_upper))
    if if_count >= 2:
        warnings.append(("ANT-0004", f"{if_count} nested IF() calls — use IFS() or LET() + CHOOSE()"))

    # Over-nesting — ANT-0014
    depth = max(
        (formula[:i].count('(') - formula[:i].count(')') for i in range(len(formula))),
        default=0
    )
    if depth >= 4:
        warnings.append(("ANT-0014", f"Nesting depth {depth} — refactor with LET() to name intermediate results"))

    # Blanket error masking — ANT-0016
    if re.search(r'IFERROR\s*\(.+,\s*""', f_upper):
        warnings.append(("ANT-0016", 'IFERROR(x,"") masks all errors — use IFERROR(x, specific_fallback)'))

    # Legacy lookups — ANT-0021
    found_leg = LEGACY_LOOKUPS & set(re.findall(r'\b([A-Z]+)\s*\(', f_upper))
    if found_leg:
        warnings.append(("ANT-0021", f"{', '.join(sorted(found_leg))} detected — replace with XLOOKUP or INDEX/MATCH"))

    # Hardcoded values — ANT-0003
    hardcoded = _HARDCODED_NUM.findall(formula)
    if len(hardcoded) >= 2:
        warnings.append(("ANT-0003", f"Hardcoded literals: {', '.join(hardcoded[:5])} — extract to named ranges or table headers"))

    return warnings


# ── MCP server ─────────────────────────────────────────────────────────────────

mcp = FastMCP(
    "excelligence",
    instructions=(
        "Excelligence is a governed Excel knowledge graph. "
        f"{len(BY_ID)} entries, {len(_registry['edges'])} typed edges, schema v{_registry['meta']['schema_version']}. "
        "Use query_entry to look up any formula, pattern, or concept. "
        "Use find_path to generate a learning sequence between two entries. "
        "Use diagnose to audit a formula against the anti-pattern registry. "
        "Use prerequisites to identify what a learner must know before tackling an entry."
    ),
)


@mcp.tool()
def query_entry(query: str) -> str:
    """
    Look up a registry entry by ID (e.g. FRM-0001, ANT-0014) or by name/alias
    (e.g. XLOOKUP, LET, Over-Nesting). Returns the full governed entry including
    intent, example, failure modes, and governance notes.
    """
    entry = _resolve(query)
    if not entry:
        # Return closest matches
        q = query.lower()
        candidates = sorted(
            {e["id"]: e for key, e in BY_NAME.items() if any(tok in key for tok in q.split())}.values(),
            key=lambda e: e["difficulty_score"]
        )[:5]
        if candidates:
            lines = [f"No exact match for '{query}'. Closest entries:"]
            for c in candidates:
                lines.append(f"  {c['id']} — {c['name']} [{c['type']}]")
            return "\n".join(lines)
        return f"No entry found for '{query}'. Registry has {len(BY_ID)} entries across FRM/PTN/ARC/ANT/CON/PQ/KEY types."
    return _format_entry(entry)


@mcp.tool()
def find_path(from_id: str, to_id: str) -> str:
    """
    Find a learning path between two registry entries by traversing LEADS_TO
    and DEPENDS_ON edges. Returns the shortest BFS path with entry names and
    tiers at each hop. Use this to build a curriculum sequence.
    """
    src = _resolve(from_id)
    tgt = _resolve(to_id)

    if not src:
        return f"Entry not found: '{from_id}'"
    if not tgt:
        return f"Entry not found: '{to_id}'"

    start, end = src["id"], tgt["id"]
    if start == end:
        return f"Same entry: {start} — {src['name']}"

    queue = deque([(start, [start], [])])
    visited = {start}

    while queue:
        current, path, edge_labels = queue.popleft()
        if current == end:
            lines = [f"Path: {src['name']} → {tgt['name']} ({len(path)-1} hop{'s' if len(path)>2 else ''})"]
            for i, node_id in enumerate(path):
                e = BY_ID[node_id]
                if i == 0:
                    lines.append(f"  ○ {node_id} — {e['name']} [{e['tier']}]")
                else:
                    lines.append(f"  → {node_id} — {e['name']} [{e['tier']}]  ({edge_labels[i-1]})")
            return "\n".join(lines)

        for target_id, etype in GRAPH.get(current, []):
            if etype in ("LEADS_TO", "DEPENDS_ON") and target_id not in visited:
                visited.add(target_id)
                queue.append((target_id, path + [target_id], edge_labels + [etype]))

    return (
        f"No path found from {start} to {end}. "
        "They may be in disconnected regions of the graph. "
        "Try query_entry on each to understand their tier and type, then build a manual sequence."
    )


@mcp.tool()
def diagnose(formula: str) -> str:
    """
    Analyze an Excel formula: identify which registry functions it uses,
    return their governance notes, and flag any anti-pattern violations
    (ANT entries) detected by heuristic analysis.
    """
    # Extract function tokens
    tokens = set(re.findall(r'\b([A-Z][A-Z0-9_]{1,})\s*\(', formula.upper()))

    matched = []
    for tok in sorted(tokens):
        e = BY_NAME.get(tok.lower())
        if e and e["type"] != "ANT":
            matched.append(e)

    ant_hits = _diagnose_ants(formula)

    lines = [f"## Formula Diagnosis\n```\n{formula}\n```"]

    if matched:
        lines.append(f"\n### Functions found ({len(matched)})")
        for e in matched:
            gov = e["governance_notes"]
            gov_short = gov[:160] + "..." if len(gov) > 160 else gov
            lines.append(f"**{e['id']} {e['name']}** [{e['tier']}]\n{gov_short}")
    else:
        unregistered = tokens - {e["name"].upper() for e in matched}
        if unregistered:
            lines.append(f"\nFunctions not in registry: {', '.join(sorted(unregistered))}")
        else:
            lines.append("\nNo registry entries matched formula tokens.")

    if ant_hits:
        lines.append(f"\n### ⚠ Anti-pattern warnings ({len(ant_hits)})")
        for ant_id, reason in ant_hits:
            ant_entry = BY_ID.get(ant_id)
            name = ant_entry["name"] if ant_entry else ant_id
            lines.append(f"**{ant_id} {name}:** {reason}")
    else:
        lines.append("\n✓ No anti-pattern violations detected.")

    return "\n\n".join(lines)


@mcp.tool()
def prerequisites(id: str) -> str:
    """
    Return what a learner must know before tackling a registry entry.
    Covers two signals: entries this one DEPENDS_ON, and entries that LEAD_TO it.
    Use this to plan a curriculum or verify readiness before introducing a concept.
    """
    entry = _resolve(id)
    if not entry:
        return f"Entry not found: '{id}'"

    eid = entry["id"]

    # What this entry depends on directly
    direct_deps = [
        BY_ID[tgt] for tgt, etype in GRAPH.get(eid, [])
        if etype == "DEPENDS_ON" and tgt in BY_ID
    ]

    # What leads to this entry (stepping stones)
    leads_to_me = [
        BY_ID[src] for src, etype in REVERSE.get(eid, [])
        if etype == "LEADS_TO" and src in BY_ID
    ]

    # What this entry pairs with (peer context)
    pairs = [
        BY_ID[tgt] for tgt, etype in GRAPH.get(eid, [])
        if etype == "PAIRS_WITH" and tgt in BY_ID
    ]

    lines = [f"## Prerequisites for {eid} — {entry['name']} [{entry['tier']}]\n"]
    lines.append(f"**Intent:** {entry['intent']}\n")

    if direct_deps:
        lines.append("### Must know first (DEPENDS_ON):")
        for e in sorted(direct_deps, key=lambda x: x["difficulty_score"]):
            lines.append(f"- {_format_entry(e, brief=True)}")

    if leads_to_me:
        lines.append("\n### Stepping stones (LEADS_TO this entry):")
        for e in sorted(leads_to_me, key=lambda x: x["difficulty_score"]):
            lines.append(f"- {_format_entry(e, brief=True)}")

    if pairs:
        lines.append("\n### Commonly paired with (PAIRS_WITH):")
        for e in sorted(pairs, key=lambda x: x["difficulty_score"]):
            lines.append(f"- {e['id']} **{e['name']}** [{e['tier']}]")

    if not direct_deps and not leads_to_me:
        lines.append(
            f"No prerequisite path found. {entry['name']} is self-contained or an entry point "
            f"at the {entry['tier']} tier. Start here if you're at that level."
        )

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
