# [PLANNER-MINTED] Make the /world believability claim MECHANICAL: external-anchor resolution + freshness harness (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). **Propose-then-proceed.**

## Ratified goal served
**DIRECTOR_AXES.md v1, Axis 3 — Believability** (verbatim): "Weather, wholesale products and prices, premise demand shape: does it feel like the real UK market to a 20-year veteran." Plus the **explicit director-named non-blocking follow-on on SITE_V5 surface_2** (`CAMPAIGN_REGISTER.yaml` surface_2_the_world note, verbatim): "(b) an external-anchor-URL resolution test."

## Real-world fidelity gained
The /world causal spine (weather 240 HDD → wholesale SSP £85.92/MWh → book → bills → carbon) hangs its believability on each node carrying a REAL external anchor (Ofgem/Elexon/NESO/Open-Meteo). Right now those anchors are asserted, not verified — a dead or drifted anchor URL silently degrades the believability claim to theatre (R15 fail-silent class). Making anchor resolution **mechanical** means the 20-year-veteran smell test rests on links that provably resolve to live real-market sources, and a rotted anchor FAILS a gate instead of rotting in place.

## Scope (propose-then-proceed; drawable NOW, no wall)
1. **DISCOVER (drawable now):** enumerate every external-anchor URL rendered across the /world spine nodes (grep `site/world/index.html` + `site/data/world.json`); classify each by source (Elexon/NESO/Ofgem/Open-Meteo/NBP) and whether it targets a stable landing vs a volatile query endpoint.
2. **BUILD a resolution harness:** a test that asserts each anchor is well-formed and points at a live real-market domain on the allowlist (`background/egress_allowlist.py`); network-optional per [[feedback_no_network_in_autonomous_runs]] — PROBE, and when offline, assert structure/allowlist-membership and mark network-resolution SKIPPED (never fail-open silently: an unavailable check is a FAILED check, R15 — so SKIPPED is logged and visible, not swallowed).
3. **R15 both ways:** mutation — point one anchor at a non-allowlisted / malformed URL and prove the harness fires; a benign anchor passes.

## Walls (untouched)
- No curriculum/ground-truth change; this VALIDATES existing anchors, never invents figures.
- Egress stays inside the app-level allowlist (`egress_allowlist.py`) — no new external surface, no secrets, no profile change.
- Harness-lane (`tests/**` / `site/test_*`) — disjoint file_scope from the 5 in-flight docs.

## Propose-then-proceed window
Fully reversible (a test + optional probe). No one-way door, no network commitment beyond read-only GETs against already-allowlisted public data domains. Proceed on draw.

---
## RESOLUTION (2026-07-24, BUILT + found live defects)
Built `site/world/test_world_anchor_resolution.py` (11 tests, all green). Design correction on the doc's own premise: the gate is keyed on a **CANONICAL_ANCHOR_DOMAINS** believability-source set, NOT the egress allowlist — a real finding is that ofgem.gov.uk / gov.uk (the UK regulator + DESNZ) are canonical believability sources yet deliberately absent from `egress_allowlist.py` (never programmatically fetched, only cited), so keying on egress would have wrongly flagged Ofgem. A consistency test documents the split (ingested market feeds must be egress-allowlisted; citation-only authorities must not be).

**The harness caught two REAL dead anchors on the live /world spine on its first run** (both HTTP 404, confirmed on GET not just HEAD):
- Weather node → `gov.uk/.../degree-days` (gone) → repointed to `open-meteo.com/en/docs/historical-weather-api` (the actual HDD data source; more honest), label "Open-Meteo historical weather".
- Carbon node → `gov.uk/.../valuation-of-greenhouse-gas-emissions-for-policy-appraisal-and-evaluation` (gone) → repointed to the current DESNZ `valuation-of-energy-use-and-greenhouse-gas-emissions-for-appraisal` (200).

R15 both ways proven: malformed / off-source / suffix-spoof anchors FAIL; canonical anchors PASS; network probe SKIPS-visibly when offline (control-host gate), runs for real when online.
