**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The coverage bought R1 a positive magnitude, and it took away the ceiling's clearance

**Found:** 2026-09-06, delivery seat, claim `r1-ceiling-coverage-is-what-buys-a-magnitude`.
Mechanism landed at `9b373b96c`. Measured on `run_output_5a256cd6d_20260906T213845Z.json`
against a one-variable ablation of that same run.

The prediction this answers was filed BEFORE the run finished:
`SEAT_PREDICTION_WHAT_THE_ACCOUNT_STATE_COVERAGE_FIX_WILL_AND_WILL_NOT_MOVE_2026-09-06.md`.
All four of its clauses hold, and the fourth — the one it explicitly declined to predict the
direction of — came out in both directions at once.

## What was done

A49 gates R3 and R4 on R1's ceiling. Lane 0's direction named three fields as the collapse from
164 households to 69, and said coverage was what would buy the rung an unbiased magnitude.

Two of the three were genuinely under-covered, and both for the same reason — a continuously-held
reading written down only where an event fired:

- `mean_recent_margin_rate`, `portfolio_premium_pct` at **149**: `decide_renewal_rate` recorded
  them only where the premium cleared `1e-6` and moved a rate. `portfolio_position` is now split
  out and called by both writers, so one reading serves the rate and the record.
- `svt_rate_gbp_per_mwh`, `rate_vs_svt_pct` at **146**: the account-state writer answered `None`
  for a gas leg because `simulation/svt_rates` published no gas series. The Ofgem cap has always
  covered both fuels and the regulation commons has carried the gas leg per window since W3_1b —
  the gap was in one module, not in the tree. `_account_state_svt_rate` now dispatches per fuel.

All four fields now stand at **164 of 164**, and all **449 of 449** gas rows carry the cap.

## The attribution is one-variable, and it is exact

The last measured book differs from this one by several commits, so the magnitude moving could not
be attributed to the coverage on its own. So the *same* run output was ablated back to the pre-fix
coverage — gas cap nulled on gas rows, the position nulled on `account_state_log` so
`dynamic_pricing_log` is again its only home — and re-measured. It reproduced every previously
published figure **exactly**: 146, 149, ceiling +0.6308, p=0.0299, whole-book +0.1492, full
coverage −0.0651 over 26/40 partitions. One identical simulation, one variable.

| on one identical run | pre-fix coverage | post-fix coverage |
|---|---|---|
| `svt_rate_gbp_per_mwh` / `rate_vs_svt_pct` | 146 | **164** |
| `mean_recent_margin_rate` / `portfolio_premium_pct` | 149 | **164** |
| full-coverage honest magnitude | **−0.0651**, 26/40 usable, 17 of 40 at or below zero | **+0.2936**, 40/40 usable, 3 at or below zero |
| whole-book pair rung magnitude | +0.1492, 7 at or below zero | **+0.2463**, 3 at or below zero |
| headline ceiling, selection-corrected | +0.6308, p=0.0299 — **CLEARS** | +0.5760, p=0.0647 — **does not clear** |
| pair rung's three-way split | REFUSED for coverage | **still REFUSED for coverage** |

## The two things this says, and they point opposite ways

**R1 has an honest positive magnitude for the first time.** The full-coverage rung moved from
−0.0651 — "the winner was noise", and computable on only 26 of 40 partitions — to **+0.2936** on
40 of 40, with 3 partitions at or below zero instead of 17. That is the quantity A49 needs and it
was bought with coverage exactly as the direction said it would be.

**And the coverage took away the clearance the record has been publishing.** The headline pair
rung cleared its selection-corrected null at p=0.0299 on 146/149-household coverage and does not
clear it at p=0.0647 on full coverage. The earlier finding that this verdict "flips on two
households" is now answered: given the coverage the record itself said was owed, it flips to
*cannot tell*. **The published clearance was resting on the missing coverage.** It goes on the page
that way round — a marginal pass that survived only while four observables were short.

## What the direction got wrong, and it is not a small thing

The direction named a third field, `perceived_bill_saving_gbp`, and predicted that at full
coverage the three-way split would get "~55 per fold and ~14 per cell". **It cannot, and it should
not.** That field is `decision_only` in the instrument's own scope table: it is what THIS renewal
appears to save against the rate it replaced, and most of this book is on indexed products that
never renew. Its 69 households are the truth about the field, not a defect in a writer.

The reported winner is still `perceived_bill_saving_gbp × mean_recent_margin_rate`, still carries
69 households, and the three-way split still refuses at 6.7 per fit cell against the 8 required.
**That refusal is correct and no amount of work will lift it**, because lifting it means writing a
renewal-window quantity for accounts that never renewed — inventing the coverage rather than
recording it. `tools/r1_inference_ceiling.py::OBSERVABLE_FIELD_SCOPE` says exactly this and it is
right.

So the honest magnitude for A49 is the **whole-book rung's +0.2463** (or the full-coverage rung's
+0.2936), on 164 households, from fields a supplier holds continuously — not a repaired version of
the headline. The headline rung is permanently capped at 69 by the definition of its own winner.

## What is still open

- The whole-book rung's own selection-corrected verdict still reads *cannot tell*
  (best pair `rate_vs_svt_pct × mean_recent_margin_rate`, held-out +0.1963, p=0.4726), so there is
  a positive magnitude and no clearance to hang it on. Both belong on the page together.
- A49's origin note and the published `/harness/` page still carry the pre-coverage figures
  (+0.6127/+0.6308 clearing at p=0.0249/0.0299, full-coverage magnitude +0.0641/−0.0651). They are
  now refuted by their own instrument and must be corrected beside the claim, not quietly revised.
- `tools/r1_inference_ceiling.py` is held by two lanes at once
  (`SEAT_FINDING_TWO_LANES_EACH_BUILT_R1S_UNBIASED_MAGNITUDE_ESTIMATOR...`); this measurement used
  the working-tree copy and deliberately landed none of it.

## Reproduce

```
python3 -m tools.run_annual_report --save-json docs/reports/run_output_<sha>_<ts>.json \
                                   --output docs/reports/ANNUAL_REPORT_<ts>.md
python3 -m tools.r1_inference_ceiling
```
For the ablation: on that run output, set `svt_rate_gbp_per_mwh` and `rate_vs_svt_pct` to `None`
on every `account_state_log` row with `commodity == "gas"`, and `mean_recent_margin_rate` and
`portfolio_premium_pct` to `None` on every `account_state_log` row; then re-run the instrument
with `--run` at that file. **Delete it afterwards** — `newest_run_output()` globs `run_output_*`
by mtime, so an ablation left on disk becomes what every downstream consumer reads.
