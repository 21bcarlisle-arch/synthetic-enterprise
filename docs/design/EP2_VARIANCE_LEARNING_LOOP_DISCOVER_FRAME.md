# EP2_variance_learning_loop — DISCOVER + FRAME (2026-08-13)

**Atom:** `EP2_variance_learning_loop` (lane `G_data_learning`, stream `close_to_learn`, epoch 2,
L0→L3, `loop_stage: idle`)
**Draw:** LANE 3 DISCOVER/FRAME only. **No BUILD code** — epoch gating
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Level **HELD at 0**.
**Prior draws:** deprioritised 2026-08-08 by the anti-livelock rule after two consecutive draws
with no state change. This document is the state change.

---

## 0. The headline

The atom is named for something that does not exist — an *ex-post bridge decomposing
expected-vs-realised* — and the gain line calls the alternative "a shrug". **The shrug is already
built, wired, and firing 144 times a run.**

Two learning loops run live in `simulation/run_phase2b.py` today. Both read a realised margin
**scalar** and move price. Neither asks *why* the margin was what it was. And because neither
decomposes, the two of them cannot be told apart on the published surface: each renders the
other's rate move as its own (§4, filed BLOCKING).

So EP2 is not a greenfield build. It is a **decomposition** atom sitting on top of two existing
undecomposed loops, and the first thing it owes is an attribution the company can already compute
from its own books.

---

## 1. What is actually built (caller census, non-test)

| Module | Non-test callers | State |
|---|---|---|
| `company/pricing/margin_feedback.py` | `simulation/run_phase2b.py:1181`, `saas/reporting/annual_report.py` ×4 | **LIVE** — 29 events/run |
| `company/pricing/tariff_engine.compute_portfolio_premium` | `run_phase2b.py:1162`, report | **LIVE** — 115 events/run |
| `company/finance/budget.py` | `annual_report.py:52,963` | **LIVE** — publishes Budget vs Actual |
| `company/finance/period_reconciliation.py` | **zero** | **DEAD** — the module actually named for variance reconciliation |
| `company/market/settlement_reconciler.py` | **zero** | **DEAD** |
| `company/market/bsc_settlement_run_register.py` | **zero** (docstring mentions only) | **DEAD** |
| `simulation/settlement_run_series.py`, `simulation/settlement_timetable.py` | **zero** outside each other | **DEAD** (world side, W3_2 L2) |

`period_reconciliation.py` carries a `VarianceType` enum — `REVENUE_SHORTFALL`, `COST_OVERRUN`,
`SETTLEMENT_DIFFERENCE`, `ACCRUAL_REVERSAL`, `METER_READ_ERROR`. **That is EP2's decomposition
vocabulary, already written down, in a module nothing calls.** This is the
already-exists-but-unwired class again (cf. EP4: `arrears_engine` half-wired; the common failure
here is an orphaned control, not an absent one).

## 2. The two live loops, and why they are the shrug

**Loop A — per-customer recovery surcharge** (`compute_margin_surcharge`, Phase 16c):
`loss_fraction = max(0, −term_margin/term_revenue)`, `surcharge = clamp(loss_fraction − 0.05, 0,
0.20)`.

**Loop B — portfolio premium** (`compute_portfolio_premium`, Phase 17a/19a): mean of recent
realised margin *rates* vs a target, × half-life, clamped to `[MIN, MAX]`.

Measured over `docs/reports/run_output_latest.json`:

* **18 of 29** Loop-A events are **capped at 20.0%**.
* Implied loss fraction: **mean 0.519, max 1.428** — terms losing 52% of revenue on average, one
  losing 143% of revenue.

So for 62% of the events the loop's output is a **constant**: a 21%-of-revenue loss and a
143%-of-revenue loss both produce "+20%". The instrument is saturated over most of its live range,
and it was never carrying a cause in the first place — a loss from wholesale cost, from volume
error, from bad debt and from a settlement correction all arrive at the same answer, "put the
price up".

That is the gain statement made falsifiable. **"Margin volatility becomes explained variance or a
named defect" has a baseline now: today, 0% of it is explained and 62% of the response is
saturated at a cap.**

## 3. The expected side half-exists

A bridge needs an *expected* recorded at decision time. One exists — but on one path only:
`expected_term_margin_gbp` is written at `run_phase2b.py:1404,1591` for **retention decisions**
and consumed by `company/analytics/counterfactual_retention.py` and
`decision_event_ledger.py`. Nothing writes an expected margin for the **pricing** decision, which
is the decision both live loops actually adjust.

EP2's smallest closed loop (R4) is therefore: *persist the expected margin the renewal price was
set against, then difference it against the realised term margin the loop already reads.* The
minuend exists (`prev_term_margin[cid]`, `run_phase2b.py:2201`). Only the subtrahend is missing.

## 4. The published surface is already mis-attributing (filed separately, BLOCKING)

Loop B runs first and multiplies `unit_rate`; Loop A then multiplies the *already-premiumed* rate,
but logs `unit_rate_before` as `term["unit_rate_gbp_per_mwh"]` — the **pre-premium** original. Both
logs therefore claim the same starting rate, and each renders the other's move inside its own
before→after span.

Rendered, `docs/reports/ANNUAL_REPORT.md:895`:
`C_IC1 | … | Surcharge +20.0% | Rate before £112.24/MWh | Rate after £153.39/MWh`
— £112.24 × 1.20 = £134.69, not £153.39. The missing +13.88% is Loop B's premium, which
`ANNUAL_REPORT.md:2376`'s table attributes to itself off the same £112.24.

**28 of 29** margin rows disagree with their own stated surcharge; **29 of 115** dynamic-pricing
rows publish a `rate_after` that is not the rate the customer contracted.

This is EP2's own subject matter — attributing a realised change to its causes — failing on a
published board surface. Filed as its own finding rather than fixed on sight
(SELF-INTERRUPT DISCIPLINE): `docs/staging/WORKER_FINDING_TWO_PRICING_LOOPS_EACH_PUBLISH_THE_OTHERS_MOVE_AS_THEIR_OWN_2026-08-13.md`.

## 5. The only variance surface the board sees is scored against a frozen plan

`company/finance/budget.py` publishes Budget vs Actual with a RAG. Its docstring says the budget is
"derived at year-start from prior-year actuals × growth targets". That derivation **does not
reproduce against the current run's actuals** — implied prior-year actual (`budget/1.10`) vs
published actual runs 0.93–1.02 across the decade, never 1.000. The table was baked from a run that
no longer exists. Result: **8 of 10 years RED**, including +2042.1% in 2017.

A RAG that says RED almost always is not a diagnostic. Filed LATENT:
`docs/staging/WORKER_FINDING_THE_BUDGET_THE_BOARD_IS_SCORED_AGAINST_IS_FROZEN_FROM_A_RUN_THAT_NO_LONGER_EXISTS_2026-08-13.md`.

## 6. The dependency is real, and it is dark end to end

`depends_on: [EP5_settlement_true_ups]` (L0, idle). The origin note says a variance loop with
nothing late to learn from is vacuous. Confirmed, and worse than parked:

* The world's timetable modules (`settlement_timetable.py`, `settlement_run_series.py`,
  W3_2 at **L2 / idle**) have **no importer in `simulation/`** — they do not run in the sim run.
* The seam `SimInterface.get_settlement_data` returns
  `{consumption_kwh: 0.0, unit_rate_gbp_per_mwh: 0.0, _stub: True}` in **`LiveSimInterface` too**
  (`sim_interface.py:324`), not merely in `StubSimInterface`.
* It has **zero production callers** — only `recorded_sim_interface.py` delegating, and tests.

So the late-truth chain is dark at all three points: world module unwired, seam stubbed to zeros,
no consumer. Note also that EP5's own `name:` asserts "W3_2_settlement_timetable exists and is
SATURATED" while the map carries `level_current: 2, loop_stage: idle` — a record disagreeing with
the map about its own dependency.

**This does not block EP2's first half.** The expected-vs-realised bridge over the *company's own*
book (§3) needs no settlement true-up; it needs the price decision's expected margin. Only the
*late-correction* leg of the bridge — the `SETTLEMENT_DIFFERENCE` variance type — waits on EP5.

## 7. FRAME — the walls this atom must be built inside

**R13 is the live danger, and the origin note names it.** The loop may move **company belief only**.
Concretely, EP2 may write to the company's forward estimates, its cost stack and its pricing
policy; it may **never** touch generator calibration, the curriculum, or any baseline-world
parameter. The agent controls both sides of the wall here, which is exactly why the wall is
prose-plus-mechanism and not prose.

**R12 follows immediately: shrinking the variance is not the objective.** A loop scored on
"variance went down" is a goal-seek. The score is *explained fraction* — how much of realised-minus-
expected is attributed to a named cause — with the residual reported, never suppressed.

**The epistemic wall constrains the decomposition itself.** Every term in the bridge must be
something a real supplier reads off its own records: its own bills (revenue, volume), its own
trading records (hedge cost), its own settlement statements (late corrections), its own collections
book (bad debt). The harness already measures a belief-vs-truth gap
(`H_GAP_fabric_belief_truth_gap`, L3) — **the company may not read that gap.** The harness scores
the decomposition; it does not supply it.

**Coupled triad.** SIM depth = EP5's late corrections (dark, §6). COMPANY = the bridge + the
feedback into forward estimates. HARNESS = the gap between the company's attribution and the
world's actual causes. Until EP5 lands, the harness leg can only score the *self-consistent* half:
does the company's own decomposition foot back to its own realised margin?

## 8. Proposed sub-atom order (FRAME output, not opened for BUILD)

1. **Persist the expected margin at the pricing decision.** The realised side already exists; the
   expected side exists only on the retention path (§3). Smallest closed loop, no dependency.
2. **Wire the vocabulary that is already written.** `period_reconciliation.VarianceType` becomes
   the bridge's cause taxonomy instead of a fifth enum invented for the purpose (AO2 reuse).
3. **Attribute the two live loops.** Loop A and Loop B stop being two undecomposed scalars racing
   for the same `unit_rate`; the rate move carries which cause bought which basis point. §4's
   published defect is a symptom of this and would be discharged by it.
4. **Explained-fraction as the score,** residual published, R12-shaped (diagnostic, not target).
5. *(waits on EP5)* The `SETTLEMENT_DIFFERENCE` leg — late corrections restating cohort margin.

## 9. Disposition

**Level held at 0.** No BUILD code written; no map edit made — `docs/design/maturity_map.yaml`
carries another lane's staged `level_current` hunk in the shared index, and a pathspec commit would
carry it (R16). The atom's own record takes the evidence line.

**Two findings queued, neither fixed on sight** (SELF-INTERRUPT DISCIPLINE — the supply is
infinite; registering is the discipline, fixing on sight is the treadmill).
