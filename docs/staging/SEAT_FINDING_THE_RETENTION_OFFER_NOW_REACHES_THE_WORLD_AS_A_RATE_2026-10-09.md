**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The run's retention offer now reaches the world as its rate, the kept term is billed at it, and the offer-comparison results that used the flat 0.20 are budgeted for re-take

*2026-10-09. The director: "The flat 0.20 retention modifier in the run is a factual correction, not a
choice for me. Make the fix you recommended: hand the world the discounted rate, retire the flat
constant, and budget the earlier offer-comparison re-take in the same piece of work." Follows
`WORKER_FINDING_THE_RUNS_RETENTION_OFFER_REACHES_THE_WORLD_AS_A_FLAT_TWENTY_PERCENT_WHATEVER_ITS_SIZE_2026-10-09.md`
(`9470735ca`).*

## What changed

1. **The world answers at the offered rate.** `simulation/retention_offer.py`: when the company
   makes an offer at tier `s`, the run asks `roll_lifecycle_event` at the full rate, then asks it again with
   only `new_rate_gbp_per_mwh` changed to `rate x (1 - s)`, on the same kept `_roll_kwargs`. The household
   stays iff its own renewal roll (`churn_roll_for_renewal`) is at or below P(stay | offered rate). That is
   the save-on-loss-notice route, and `household_takes_save` is reused for it. The pre-offer truth
   (`realized_churn_probability`, `churn_estimate_error_pct`) stays the full-rate one.
2. **`RETENTION_EFFECTIVENESS` is deleted.** It had no reader outside `simulation/run_phase2b.py`.
   The company's `_RETENTION_EFFECTIVENESS` in `company/analytics/counterfactual_retention.py` is a
   different name: the company's own belief, on the other side of the wall. It is unsourced too, and it
   is not touched here.
3. **Framing keeps only what is sourced.** `NUDGE_PHYSICS_BENCHMARKS.md` gives a 10–35% *relative uplift
   in acceptance probability* on a matched framing (Levin, Schneider & Gaeth 1998). A household
   "accepts" when it leaves at the full rate and stays at the offered one. So the multiplier now scales
   `P(stay | offered) - P(stay | full)` on the same roll. At a multiplier of 1 the answer is the world's
   own. The 0.20 it used to multiply is gone, and no number was added.
4. **Second defect, fixed: the kept term was billed at the undiscounted rate.** The run billed a kept
   household at the full `unit_rate`. It booked the discount only as `retention_cost_events`, which
   never reaches the P&L (`test_retention_cost_events_are_minted_but_never_reach_the_pnl`; the C29
   finding of 2026-10-05 said the same). So the headline net was never charged for an offer. Now the
   decision leg's `unit_rate`, prior rate, account-state row and position-vs-default are all the
   offered rate. As with the save, its thinner margin does not feed the portfolio premium (director,
   2026-10-08: stayers must not pay for a cut). That second rule is my extension of his save ruling to
   the retention discount. **It is reversible and it is a judgement.** Without it, landing the
   billing fix would have started recovering every discount from the stayers.

## Measured: 80 founders to 2019-12-31, same seed, origin `2e612879f` against this change

| | before (flat 0.20) | after (rate) |
|---|---|---|
| offers 3% / 5% / 8% | 18 / 6 / 3 | 19 / 6 / 3 |
| kept 3% / 5% / 8% (P(stay \| offer)) | 15 (0.833) / 6 (1.0) / 3 (1.0) | 16 (0.842) / 6 (1.0) / 3 (1.0) |
| retained by offer | 24 of 27 | 25 of 28 |
| retention log: cost / Σ expected term margin, GBP | 785.47 / 9,468.53 | 771.09 / 9,167.90 |
| renewal events / departures | 51 / 15 | 53 / 15 |
| headline total net, GBP | 43,587.27 | **42,955.09 (−632.18)** |
| wall / peak RSS | 832 s / 1,295 MB | 812 s / 1,297 MB |

**On the after run's own 17 rolled offers, I asked the world both ways on identical kwargs** (shadow
run, net byte-identical at 42,955.09). Mean ΔP(stay) per offer:

| tier | n | retired flat 0.20 × framing | offered rate |
|---|---|---|---|
| 3% | 12 | +0.0270 | **+0.0055** |
| 5% | 4 | +0.0299 | +0.0201 |
| 8% | 1 | +0.0496 | +0.0512 |
| expected keeps from the offer | 17 | 0.49 | 0.20 |

No realised stay differed between the two answers on these 17 offers. The one 8% offer that left at the
full rate stayed under both.

**The pre-registered direction, graded.** The finding predicted that the retained-by-offer count would
fall, because the commonest tier is 3% and the rate response at 3% is about two-thirds of the flat.
- **In expectation it HOLDS, and more strongly than predicted.** On the run's own fixed-term renewals a
  3% cut buys **one fifth** of what the flat credited (+0.0055 against +0.0270), not two thirds. The
  finding's caveat was right: the default-tariff probe overstated the run's response.
- **In the realised count it is NOT SHOWN.** 24→25, on a book that diverged by two renewals. At 0.29
  expected keeps of difference over 17 offers, no count at this size could show it.
- **"Booked retention cost does not change": refuted in the headline.** The ex-ante log cost is
  unchanged in kind (785→771, the book moved). The headline net now carries the discount, because of
  defect 2. I cannot yet separate the −£632 between the billed discount and the premium-feed
  exclusion. The shadow shows the world's answer moved no outcome, so none of it is extra departures.

## Controls (`tests/simulation/test_retention_offer_reaches_the_world_as_a_rate.py`), mutation-proven

| control | mutation | result |
|---|---|---|
| a bigger discount keeps at least as many, monotone, on the same roll; 8% keeps strictly more than none | `offered_rate` returns the full rate | red |
| a zero discount changes nothing | the offer credited regardless of price (`p_full*1.05`) | red (3 tests) |
| the answer is the household's own roll (agrees with the direct re-ask, both outcomes occur) | `random.Random(7)` coin | red (3 tests) |
| no reader of `RETENTION_EFFECTIVENESS` (ast, whole tree, ≥1,000 files read) | re-add the constant | red |

The ast census was first written filtering absolute paths for `.claude`. That skipped every file in a
linked worktree, so the control was green on a mutation. It now filters repo-relative parts and asserts
how many files it read.

**No test was re-pinned.** No test read the constant. The `retention_modifier` parameter of
`roll_lifecycle_event` stays, together with its four tests in `tests/simulation/test_customer_events.py`.
It now has **no production caller**. That is a dead world dial, and it is worth retiring with
`departure_risks`' `retention_offer_retained_fraction` and the P6 tests in a follow-up.
Affected suites passed: 263 unit tests, and 61 run-loop tests (`test_run_phase2b*`,
`test_a_save_is_not_paid_for_by_the_stayers`, `test_run_frozen_baseline`).

## The offer-comparison re-take, budgeted as one piece

This change moves the canonical run, so `tools/generate_value_arms_data.py::_code_since_the_run`
withdraws the current-world value-arms headline until the arms are re-taken. Wall and peak come from
each result's own last run (`journalctl --user`, `sim/cache/run_cost_log.jsonl`).

| result | command | wall | peak | tier |
|---|---|---|---|---|
| value arms, 20261008r pair (`cb54420a0`, `site/data/value_arms.json`) | `tools/run_value_cycle_ab.py --noise-floor-seeds 11111,22222,33333 --redraw-mode all --out …` leg 1, then leg 2 | 1 h 56 m + 5 h 28 m (≈37–41 m per run) | 6.9 GB; 11.5 GB leg 2 | hours |
| reactive save in the settled run (`517ffec2c`, `0f1fb3f6a` arms; `SEAT_FINDING_THE_REACTIVE_SAVE_IN_THE_SETTLED_RUN`) | `tools/save_on_loss_notice_arms.py run {off,on,placebo} <out> 2024-12-31 --cut-share 0.04`, plus `on` at k=0 and 0.923 (5 runs) | 28–32 m each | 3.0–3.2 GB alone (8.8 GB co-run) | hours |
| C29 engagement-weighted guard (`789885991`) | `python3 -m tools._c29_retention_engagement_arm {off,on} <out>` | 17–20 m each | 4.8 GB | hours |
| retention guard nets bad debt (`6870d3c8b`; `SEAT_RESULT_…_WITHDRAWS_NOTHING`) | `python3 -m tools._c29_retention_engagement_arm {off,net} <out>` | 42 m each | 5.1 GB | hours |
| blind acquisition arms (`ba5728611`, `d27a2a227`; the totals include retention keeps) | the `blind-arms-*` long jobs, 2 lanes | 41 m each | 3.3 GB | hours |
| production run / annual report | `tools/run_annual_report.py --save-json …` (sim-runner cycle, automatic) | 29.6 m | 3.4 GB | hours (no action: next cycle) |
| `WORKER_RESULT_THE_COMPANY_CANNOT_LEARN…` §1 (70 offers) | re-read from the next production run's `retention_log` | 0 | 0 | none |
| frozen baseline, CURRENT against NAIVE (`tools/run_frozen_baseline.py`) | as named | not in either log since 2026-10-04: I cannot price it from its own run; ≈2 × the production run | ≈3.4 GB | hours |
| B8 coin-drawn set and L2 (`58993b3b5`, `4320ae6a5`), acquisition-selection grade (`e0c906355`, `c568a5944`), `grade_save_offer_shapes`, decision probe | — | — | — | **no re-take**: they already ask the world at the rate |

**Budget, run serially through the box queue:** about 12 h 30 m of wall. That is the value arms at ≈7 h 25 m,
save arms ≈2 h 30 m, C29 and netting ≈2 h, and blind arms ≈1 h 20 m, with peaks inside the 11.5 GB the
value arms' leg 2 already took. Nothing needs the minutes tier. Every minutes-tier instrument was
already on the rate, and that is why the run, not those instruments, was the defect.
