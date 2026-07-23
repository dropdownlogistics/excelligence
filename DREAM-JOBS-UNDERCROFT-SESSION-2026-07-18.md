# Dream Jobs — Undercroft Session Recon of Excelligence
Author: Claude Code (Undercroft session)
Date: 2026-07-18
Status: PROPOSAL — uncommitted, awaiting operator review
Recon basis: full repo read — CLAUDE.md, README, llms.txt, registry JSON (105 entries / 228 edges), all 14 product surfaces, git history

---

## What I saw

Excelligence is a governed knowledge graph wearing a website. The registry is the
asset: 105 entries with intent grammar, failure modes, and governance notes;
228 typed edges; a locked schema that survived a 9-model council. Around it sit
fourteen surfaces — explorer, radial, paths, learn, FormulaLab, GridTactics,
scanner, CF patterns, standards — all reading from one JSON.

The pattern I noticed: **every surface consumes the graph, but nothing yet acts
on the world with it.** The scanner takes pasted text. The paths are static
pages. The CF Pattern Library is copy-paste. The graph is a cathedral that
visitors walk through — it doesn't yet reach into anyone's actual workbook.

Meanwhile, one building over, I'm running Milestone Zero on Undercroft — an
Office JS add-in that reaches directly into live workbooks. Today it proved it
can read all 129 CF rules in a real workbook in 165ms and rewrite them.

Every dream job below is some version of the same sentence: **give the graph
hands.**

---

## Dream Job A — The Registry Grows Teeth (Live Workbook Auditor)

**One sentence:** An Office JS scan that audits a real, open workbook against
the 16 ANT anti-pattern entries and STD-EXCEL-001/002, producing a governed
audit report with registry citations — the Scanner page, but pointed at an
actual file instead of pasted text.

**Why it's the dream:** This is the moment Excelligence stops being reference
material and becomes enforcement. A CPA-governed standard that can *grade a
workbook* is a different product category than a standard you read. Output:
"STD-EXCEL-001 compliance: 6/9 rules. Violations: ANT-0003 (hardcoded values,
47 instances, Sheet2!D:D)..." — every finding cites a registry ID, every
citation links to the entry. Deterministic, auditable, no AI hand-waving.

**Why me:** The Milestone Zero spike already proved the API layer — enumeration,
batched reads, dead-object detection — on real workbooks. The audit engine is
the same two-layer architecture (API reads → pure-logic rules) as Undercroft.
The rule checks are derivable from ANT entry `failure_modes` fields today.

**Synergy:** This *is* Undercroft's "Workbook Health Scan" roadmap feature, born
inside Excelligence instead. The two products would share an engine: Undercroft
manages the invisible layer; Excelligence grades it. One codebase, two spouts.

**Effort:** Medium. Script-Lab-grade prototype in a day; a real task pane rides
Undercroft's eventual scaffolding.

---

## Dream Job B — Placement Engine (the graph as adaptive curriculum)

**One sentence:** A short diagnostic quiz that places a user *on* the graph
(which nodes they hold, which tier boundary they sit at), then BFS-generates a
personal learning path through LEADS_TO/DEPENDS_ON edges toward a goal they
pick — with traversal progress saved locally.

**Why:** The graph's tier + difficulty_score + edge data is exactly the
substrate adaptive learning engines are built on, and it's already governed.
Ten static paths exist; this makes path #11 be *yours*. "Where am I? Where am I
going? What's the governed next stone?" — nobody else in the Excel education
space can answer with a typed graph.

**Effort:** Medium-low. Pure client-side JS over excelligence.json. The quiz is
the design work: ~12 questions keyed to tier-anchor entries.

---

## Dream Job C — The Daily Grid (Wordle for Excel)

**One sentence:** A deterministic daily formula challenge generated from
registry seeds — real mini-dataset, produce the target, never told the function
— with a shareable result square, streaks, and a registry citation on solve.

**Why:** FormulaLab has one challenge; GridTactics proved the game mechanics.
A *daily* ritual with a shareable artifact is the viral object the product
lacks (same play as Undercroft's Lens tier: free, self-propagating,
"post your streak on r/excel"). Every solve ends by revealing the registry
entry — the game funnels into the graph.

**Effort:** Medium. Determinism from date-seeded generation; the challenge
templates are the real authoring work (registry `example` fields are the raw
material).

---

## Dream Job D — Excelligence MCP Server (the graph as AI infrastructure)

**One sentence:** An MCP server exposing the registry to any AI session —
`query_entry`, `find_path(from, to)`, `diagnose(formula)`, `prerequisites(id)` —
so every Claude/model in the DDL federation (and eventually anyone's agent)
traverses governed Excel knowledge instead of hallucinating advice.

**Why:** llms.txt already says "FOR AI COLLABORATORS" and begs models not to
fabricate entries — this makes compliance *structural* instead of aspirational.
DDL's whole thesis is governed knowledge + distributed cognition; this is the
first product artifact that ships that thesis as infrastructure. Also the
cheapest dream on the list: the JSON is public, the graph ops (BFS) already
exist in explorer JS.

**Effort:** Low. A day. Python or Node MCP server over excelligence.json.

---

## Dream Job E — The Bridge (Excelligence ⇄ Undercroft single source of truth)

**One sentence:** Wire the CF Pattern Library (10 copy-ready, correctly-anchored
patterns) into Undercroft's Recipe Shelf, and wire Undercroft's warnings to cite
registry IDs — one governed source, two products, bidirectional credibility.

**Why:** Undercroft's spec says "Recipes ship correctly anchored and
non-volatile because the tool has opinions." Those opinions *already exist* —
they're the registry's governance_notes and the CF Pattern Library. Instead of
authoring recipe content twice, Undercroft fetches (or build-time-bakes) pattern
definitions from Excelligence. And when Undercroft flags a volatile function in
a CF formula, the warning cites the ANT entry. Every Undercroft user meets
Excelligence; every Excelligence reader sees the tool that enforces it.

**Effort:** Low for the recipe pipeline (JSON in, recipes out). The citation
layer rides Undercroft V1 features as they're built.

---

## If I had to pick one

**A, with D as the warm-up.** D is a one-day build that makes the graph
callable by every session in the federation immediately — including the
Undercroft build sessions about to write CF code. A is the category move: the
registry stops describing good workbooks and starts *grading real ones*, on an
API layer Milestone Zero has already de-risked. C is the best pure-marketing
play and should exist before any paid tier matters.

Operator decides. This document proposes; it does not begin.

---

*Filed by the Undercroft session after excelligence recon, per operator
instruction ("do some recon, see what you like"). Not committed. EAE session
not yet briefed — recommend cross-session sync before any of these are built,
since A and E overlap Undercroft scope and EAE holds Excelligence context.*
