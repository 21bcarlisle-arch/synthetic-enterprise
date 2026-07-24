# [PLANNER-MINTED] Publish premise half-hourly demand belief-vs-truth to a visible site surface (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Rungs 1–6 drew empty this
tick; agenda + staging root empty; minted from a ratified goal. **Propose-then-proceed.**

> **Provenance / not-a-duplicate:** this ELEVATES the already-authored, already-scoped proposal
> `docs/design/proposals/PROPOSE_PREMISE_DEMAND_PUBLISH_SPEC003.md` (minted 2026-07-23 under the same
> ruling's "seed the backlog NOW") into a **staged, RUNG-1-drawable** item. The proposal was complete
> but sat in `docs/design/proposals/`, which the supervisor's unprocessed-staging scan does not read —
> so it was never drawn (this tick's empty draw is the symptom). Staging it makes it drawable next tick.
> It supersedes the proposal doc; the proposal stays as the design record.

## Ratified goal served
- **PRIORITIES.md PRODUCT-FIRST item 4 (verbatim, director-ranked 2026-07-23):** *"Premise demand
  published — half-hourly household curves to a visible surface (Spec 003's two-level test is the bar)."*
  This is the top-ranked PRODUCT-FIRST item with **no open mint** (item 1 SITE V5 closed; items 2 & 3 —
  generator draw-wiring, value-chain — are open mints; item 5 spike-tail closed).
- **DIRECTOR_AXES v1 — Axis 3 (Believability):** *"premise demand shape … does it feel like the real UK
  market to a 20-year veteran."* Demand shape is one of the three named believability sub-axes and
  currently shows **nothing** on the live site.
- **COUPLED_TRIAD doctrine + the model-on-a-page campaign (WORDS→DIAGRAM→EVIDENCE):** every diagram
  arrow must carry its evidence chart. The demand arrow (`weather → demand`) currently renders no
  evidence. `W1_5_premise_demand_shape` (COUPLED twin of company `C13_weather_normalisation`) already
  has its belief-vs-truth **measured** in `docs/observability/coupled_gap_ledger.json` — this is a
  *rendering* of an existing committed result, **not new modelling**.

## Why this is drawable now (not a wall)
Pure **SITE lane** (THREE_LANES L2 — `site/**`, disjoint, ungated, permanently parallel to builds). No
sim/company code changes, no new claim, no curriculum/ground-truth touch (R13 untouched), no level move.
The figure already exists in the committed ledger. Reversible: a site surface + a `site/data/` feed.

## The gap being closed
`site/data/` contains **no** demand/profile/load-curve feed today (verified 2026-07-24) — the demand
arrow of the walkable causal spine on `/world` renders a headline SSP/weather number but no demand-shape
evidence. A 20-year veteran opening the site sees the price and weather physics but cannot see whether
the company's household demand model is believable. Publishing the measured two-level belief closes that.

## Real-world fidelity gained
The reader can see the company's own half-hourly demand belief **against no-skill truth** — including,
honestly, that in the *worst* cell the wind-chill term barely helps (belief-vs-truth, not a
self-flattering single number). That is the coupled-triad's own definition of an honest evidence surface.

## Scope (propose) — grounded in the committed ledger, no re-computation
Per `PROPOSE_PREMISE_DEMAND_PUBLISH_SPEC003.md`:
1. **Read** `coupled_gap_ledger.json → W1_5_premise_demand_shape.components` — the data source. No recompute.
2. **Publish** a `site/data/` demand feed + render the **two-level bar** and per-cell MAE table behind the
   model diagram's demand node (`site/**`):
   - **L1 (comparison):** `demand ~ base + b_hdd·HDD + b_cdd·CDD` — r² ≈ 0.551.
   - **L2 (headline):** adds the CWV wind-chill degree-day term — r² ≈ 0.552; **worst cell = summer,
     MAE 2276 MW vs no-skill 2190 MW** (near-tie, stated not hidden).
   - N visible (`n_train = 3337`); belief-form labels visible; per-cell (cold/warm/summer) MAE with N,
     never a total-over-sample (RC6: rates/distributions with N, not curriculum-sample totals).
3. **Land LIVE on poesys.net and R11 pixel-verify:** fetch the deployed surface; assert the rendered MAE
   values (2276 / 2190) and N appear — data stamp **and** visible value both asserted. R14 basis on the
   figure: "worst summer cell, n=3337 train".

## R15 / honesty obligations
- The bar shows belief-vs-**truth** (model MAE vs no-skill g0 = climatological mean), showing the
  RELATIONSHIP and where the company is still wrong (worst-cell near-tie is on-surface, not concealed).
- `site/link_walk.py` stays green after landing (no dead/non-canonical link).
- R11+R15 by a render-harness test executing the page's real JS against the published feed, with a
  mutation that flips the rendered MAE pixel (fail-closed-visible if the feed is empty).

## Propose-then-proceed window
SITE lane, normal window. Reversible render of an already-committed figure — **proceed; R11 pixel-proof
on landing is the DoD**, no director gate (Axis-1/3 product surface, ungated site lane).

---
*Minted by the RUNG-7 planner self-refill. Becomes RUNG-1 staged work the next tick draws.*
