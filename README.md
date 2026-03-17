# Excelligence — Knowledge Vault

A governed knowledge graph for Excel intelligence.

**50 entries · 118 edges · 7 types · 4 tiers · 574 checks passed · Zero failures**

## What This Is

Excelligence maps Excel formulas, patterns, shortcuts, conventions, architectures, and anti-patterns into a navigable knowledge graph. Every entry has a governed intent statement, working examples, failure modes, and governance notes. Entries are connected by typed edges: LEADS_TO (progression), DEPENDS_ON (prerequisites), and PAIRS_WITH (co-usage).

The graph reveals how Excel knowledge actually connects — and shows you the governed path between where you are and where you want to be.

## Live Site

**[→ Enter the Knowledge Vault](https://dropdownlogistics.github.io/knowledge-vault/)**

- **Landing page** — stats, types, tiers, sample learning paths
- **Graph Explorer** — interactive force-directed graph with Path Finder
- **Pricing** — Community (free), Professional, Institutional tiers

## Data

Static JSON export of the full registry:

```
/api/excelligence.json
```

Contains all entries, edges, tags, and aliases. Public. Consumable by any tool or integration.

## Schema

- **7 entry types:** FRM (Formula), PTN (Pattern), KEY (Shortcut), CON (Convention), ARC (Architecture), ANT (Anti-Pattern), PQ (Power Query)
- **4 skill tiers:** Beginner, Intermediate, Advanced, Expert
- **3 edge types:** LEADS_TO, DEPENDS_ON, PAIRS_WITH
- **8 governance addenda** enforced by automated validator

## Built By

Dave Kitchens, CPA · [Dropdown Logistics](https://www.dropdownlogistics.com)

Schema validated by a 10-seat AI council. Registry proven across 5 build batches with zero validation failures.

## Doctrine

Chaos → Structured → Automated

*CottageHumble: Humble surface. Cathedral underneath.*
