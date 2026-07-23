# [PROPOSE-THEN-PROCEED] Premise-demand publish — Spec-003 two-level bar on the live site

**Minted:** 2026-07-23, seed ordered by DIRECTOR_RULING_WORK_IS_THE_DEFAULT §"seed the backlog NOW"
+ NIGHT_ENFORCEMENT §2. This is a SITE/EVIDENCE mint (rung 4/5), product-facing.
**Window:** propose-then-proceed, normal window; SITE lane (ungated, `site/**`, disjoint — THREE_LANES L2).

## The gap / roadmap item served

`W1_5_premise_demand_shape` (COUPLED twin of company `C13_weather_normalisation`) already has its belief
measured in `docs/observability/coupled_gap_ledger.json` at **two belief levels**, but that belief-vs-truth
result is **not published** — the director's model-on-a-page campaign (WORDS→DIAGRAM→EVIDENCE) requires every
arrow to carry its evidence chart, and the demand arrow currently shows nothing on the live site. Publishing it
is the RC6/evidence-page work the campaign is asking for, grounded in an already-measured ledger figure (no new
modelling — this is a *rendering* of an existing result, R11 pixel-verified).

## What "Spec-003 two-level bar" is (grounded in the committed ledger)

The coupled-gap ledger records the demand-normalisation belief at two forms, with the same worst-cell prediction gap:

- **L1 (comparison):** `demand ~ base + b_hdd·HDD + b_cdd·CDD` — r² ≈ 0.551.
- **L2 (headline):** `demand ~ base + b_hdd·HDD + b_cdd·CDD + b_windchill·windchill_DD` (the CWV wind-chill term),
  r² ≈ 0.552; worst cell = summer, CWV degree-day weather-normalisation MAE **2276 MW** vs no-skill **2190 MW**.

The **two-level bar** renders both belief forms against the no-skill baseline (g0 = climatological mean) so the
reader sees what the wind-chill term buys (and, honestly, that in the *worst* cell it barely helps — the gap the
company still has). Per-cell MAE (cold/warm/summer) with **N stated** (n_train = 3337), never a total-over-sample
(RC6 rule: totals over a curriculum sample are meaningless — rates/distributions with N).

## Plan (SITE lane, R11 to the rendered pixel)

1. Read the demand block of `coupled_gap_ledger.json` (`W1_5_premise_demand_shape.components`) — the data source,
   no re-computation.
2. Add the two-level bar + per-cell MAE table to the demand-arrow evidence surface (`site/**`, behind the model
   diagram's demand node), with N and belief-form labels visible, honest about the worst-cell near-tie.
3. Land LIVE on poesys.net and **R11 pixel-verify**: fetch the deployed surface, assert the rendered MAE values
   (2276 / 2190) and the N appear — the data stamp AND the visible value both asserted (R14: figures carry their
   clock/basis; here the basis is "worst summer cell, n=3337 train").

## R15 / honesty obligations

- The bar shows belief-vs-**truth** (model MAE vs no-skill), not a self-flattering single number — the arrow's
  evidence must show the RELATIONSHIP and where the company is still wrong (worst-cell near-tie is stated, not hidden).
- Link-walk (`site/link_walk.py`) stays green after the surface lands (no dead/non-canonical link introduced).

**Risk & proportionality:** SITE-lane render of an already-measured ledger figure; no sim/company code, no new
claim (the figure exists in the committed ledger). Tag: **proceed, R11 pixel-proof on landing.**
