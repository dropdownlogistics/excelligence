# Excelligence

A governed knowledge graph for Excel intelligence.

**65 entries · 156 edges · 7 types · 4 tiers · v0.2 schema**

## What This Is

Excelligence maps Excel formulas, patterns, shortcuts, conventions, architectures, and anti-patterns into a navigable knowledge graph. Every entry has a governed intent statement, working examples, failure modes, and governance notes. Entries are connected by typed edges: LEADS_TO (progression), DEPENDS_ON (prerequisites), and PAIRS_WITH (co-usage).

The graph reveals how Excel knowledge actually connects — and shows you the governed path between where you are and where you want to be.

Not a glossary. Not a tutorial. A knowledge graph you can traverse.

## Live Site

**[→ excelligence.vercel.app](https://excelligence.vercel.app)**

| Page | URL |
|------|-----|
| Landing | `/` |
| Graph Explorer | `/explorer/` |
| Radial Map | `/radial/` |
| Learning Paths | `/paths/` |
| CF Pattern Library | `/tools/cf-patterns/` |
| Tools Hub | `/tools/` |
| STD-EXCEL-001 | `/standards/excel-001/` |
| STD-EXCEL-002 | `/standards/excel-002/` |
| Registry Export | `/api/excelligence.json` |

## Registry

- **65 entries** across 7 types (FRM, PTN, KEY, CON, ARC, ANT, PQ)
- **156 typed edges** (LEADS_TO, DEPENDS_ON, PAIRS_WITH)
- **Schema v0.2** — difficulty_score, usage_frequency, excel_version on every entry
- **9-model council review** — zero REJECT, zero REVISE on schema lock
- **574 validation checks** passed at v0.1.1 lock

## Schema

```json
{
  "id": "FRM-0001",
  "name": "XLOOKUP",
  "type": "FRM",
  "tier": "Intermediate",
  "what_it_does": "...",
  "intent": "When [trigger], use [pattern] to [outcome].",
  "example": "...",
  "failure_modes": "...",
  "performance_notes": "...",
  "governance_notes": "...",
  "difficulty_score": 2,
  "usage_frequency": "Daily",
  "excel_version": "2019+",
  "created_at": "...",
  "updated_at": "..."
}
```

## Data

Static JSON export of the full registry:

```
/api/excelligence.json
```

Public. Consumable by any tool, model, or integration.

## Standards

- **STD-EXCEL-001** — Analytical Workbook Standard (9 rules)
- **STD-EXCEL-002** — Operational Workbook Standard (8 rules)

## Built By

Dave Kitchens, CPA · [Dropdown Logistics](https://www.dropdownlogistics.com)

Schema validated by a 10-seat AI council. Connor's threshold: "If it survives 50 entries, it's real." Passed.

## Doctrine

Chaos → Structured → Automated

*CottageHumble: Humble surface. Cathedral underneath.*

> "The graph is the cathedral. Everything else is scaffolding."
> — Rowan Bennett, Seat 1005, CR-EXCEL-001
