# [PLANNER-MINTED] K-pilot deliverable 4 — the rung-5 chart set + a DoD gate so a chartless page cannot ship (2026-07-28)

**Source ruling:** DIRECTOR_RULING_KPILOT_SCOPE_FIRST_2026-07-28.md — deliverable 4 (WORK THIS CREATES); ruling §5.
**Serves:** DIRECTOR_AXES Axis 1 (Website — the director is a visual reader) + Axis 3 (Believability — charts rendered from the live pipeline, never static). Fidelity-ledger row: price-formation (W1_6 weather→price chain, L3; real Elexon SSP history). Campaign: knowledge-page pilot.
**Real-world fidelity gained:** an explanation of price formation that actually shows the phenomena — a price series, a merit-order stack, a seasonal shape, and a negative-price frequency — rendered from real history and the SIM pipeline (never static images), plus a mechanised definition-of-done that BLOCKS a chartless page from shipping (the DoD-5 failure that should have blocked this ship).
**Lane:** SITE + BUILD (site page + a DoD gate test; disjoint file_scope `site/knowledge/wholesale-price-formation/**` and the gate test path).
**Target level:** SITE L2 (rendered, live-verified) for the charts; the DoD gate is a control that must be R15 mutation-proven.
**Exit criteria:**
- The rung-5 chart set renders from the pipeline (NOT static images): a real GB price series (Elexon SSP history), a merit-order stack, a seasonal shape, and a negative-price frequency — sourced from `sim/system_prices_history.py` / `sim/weather_price_chain.py` (W1_6) / `sim/price_engine.py` via the existing `site/knowledge/wholesale-price-formation/_render_harness.mjs` render path. R11: verify the LIVE rendered chart values, not the code.
- A DoD gate exists that FAILS (rc≠0, blocks publish) when the knowledge page has zero rendered charts — **R15 mutation-proven both ways**: it FIRES on a chartless page and does NOT fire on the real charted page. (Fixes the "report why DoD 5 passed or was skipped, and fix the check" instruction — the check's current pass on a chartless page is the defect to close.)
- The gate is wired into the same publish/site pre-commit path that gates knowledge pages (no orphan control — R11 no-orphan-transition).
**Deps:** #3 decomposition (charts land on the decided hub/child pages); underlying data pipeline already exists (W1_6 L3, real SSP history) so no new sim build is required — this is render + gate, not physics.
**Propose-then-proceed window:** proceed by default (ruling **proceed**; site content + a test, reversible via git; machinery untouched). Walls untouched (no generator ground-truth edit — charts READ the pipeline).

## Deliverable (verbatim)
> 4. The rung-5 chart set, and the DoD check fixed so a chartless page cannot ship.

Ruling §5: "live evidence: real history and SIM charts rendered from the pipeline, never static images... Charts are not decoration here... an explanation of price formation without a price series, a merit-order stack, a seasonal shape and a negative-price frequency is not an explanation."
