# Dashboard Build Instruction (staged from terminal 2026-06-22)

We now have a live dashboard at poesys.net (Cloudflare Pages, auto-deploys from site/index.html on every commit). The current dashboard shows basic P&L cards — net margin, gross margin, enterprise value, treasury.

The dashboard should evolve into a proper company intranet — the kind of thing an MD and trading desk would actually use. Priority views:

1. Trading view: wholesale spot price vs forward price by month 2016-2025, hedge fraction over time, risk committee interventions overlaid on price chart, the 2021 crisis should be visually obvious

2. Customer view: book size over time with churn/acquisition events marked, net margin per customer per year as a heatmap, bill shock events timeline, retention offers and outcomes

3. Financial view: P&L waterfall by year, revenue vs wholesale vs gross vs net margin stacked bar, treasury movement, operating costs breakdown

4. Market view: forward premium by month showing contango/backwardation, seasonal consumption patterns

All data already exists in the simulation output JSON. The dashboard reads from that. Mobile-first — Rich reviews on his phone. Propose what to build first and start building.

STATUS: In progress — building all 4 views as SPA at site/index.html, data from site/data/dashboard.json
