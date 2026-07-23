# Excelligence MCP Server — Dream Job D

Exposes the Excelligence knowledge graph as callable tools for any AI session
in the DDL federation.

## What it does

Every Claude / model session in the federation can now traverse governed Excel
knowledge instead of hallucinating advice. Four tools:

| Tool | What it answers |
|---|---|
| `query_entry(query)` | What is XLOOKUP? What is ANT-0014? |
| `find_path(from_id, to_id)` | How do I get from SUMIF to LAMBDA? |
| `diagnose(formula)` | Is this formula well-governed? What anti-patterns does it hit? |
| `prerequisites(id)` | What do I need to know before learning MAKEARRAY? |

## Install

Requires [uv](https://docs.astral.sh/uv/) and the `mcp` package.

```bash
cd excelligence/mcp
uv pip install mcp
```

## Add to Claude Desktop

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "excelligence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:/Users/dkitc/excelligence/mcp",
        "python",
        "excelligence_mcp.py"
      ]
    }
  }
}
```

Restart Claude Desktop. The four tools appear in any new conversation.

## Run directly

```bash
cd excelligence/mcp
uv run python excelligence_mcp.py
```

## Registry state

At build time: **123 entries · 337 edges · schema v0.2.0**

Entry types: FRM / PTN / ARC / ANT / CON / PQ / KEY  
Edge types: LEADS_TO / DEPENDS_ON / PAIRS_WITH

The server loads `excelligence.json` at startup from the parent directory.
Pull and restart to pick up new registry entries.

## Anti-pattern detection in `diagnose()`

The diagnose tool runs these heuristics against the formula:

| Heuristic | Flags |
|---|---|
| Volatile functions (NOW, TODAY, RAND, OFFSET, INDIRECT) | ANT-0002 |
| Nested IF count ≥ 2 | ANT-0004 |
| Nesting depth ≥ 4 | ANT-0014 |
| `IFERROR(x,"")` pattern | ANT-0016 |
| VLOOKUP / HLOOKUP present | ANT-0021 |
| Multiple hardcoded numeric literals | ANT-0003 |

## Dream Job context

This server is Dream Job D from the Undercroft session recon of Excelligence
(DREAM-JOBS-UNDERCROFT-SESSION-2026-07-18.md). It is the warm-up for Dream
Job A (Live Workbook Auditor — Office JS scan against the full ANT registry).

Operator: Dave Kitchens · Dropdown Logistics  
Built: 2026-07-22
