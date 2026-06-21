# Institutional Knowledge — Synthetic Enterprise

This directory is the company's institutional memory. It captures:

1. **What we know** — domain knowledge about UK energy supply, organised by topic
2. **How we learned it** — research methodology so future sessions go faster
3. **What we don't know yet** — gap map to prioritise future discovery
4. **Source quality** — which sources were authoritative, which were shallow

## Directory structure

| File | Purpose |
|------|---------|
| `knowledge_map.md` | Master map: domain → what we know → confidence → gaps → next questions |
| `research_methodology.md` | How to run R&D sessions efficiently; agent briefing patterns that work |
| `source_guide.md` | Authoritative sources by topic: URLs, quality ratings, update frequency |
| `domain/` | Deep dives by domain (created as knowledge grows) |

## How this directory grows

After every R&D session:
1. New findings go into the relevant `knowledge_map.md` row (confidence updated)
2. Any novel methodology insight goes into `research_methodology.md`
3. High-quality new sources go into `source_guide.md`
4. When a topic gets deep enough (>3 research passes), create `domain/<topic>.md`

## Relation to `docs/market_research/`

`market_research/` holds raw research outputs — timestamped discovery docs.  
`institutional/` holds the curated, living version — what we actually believe, with confidence levels, superseding earlier findings when new data arrives.

Think: `market_research/` is the filing cabinet; `institutional/` is the whiteboard.
