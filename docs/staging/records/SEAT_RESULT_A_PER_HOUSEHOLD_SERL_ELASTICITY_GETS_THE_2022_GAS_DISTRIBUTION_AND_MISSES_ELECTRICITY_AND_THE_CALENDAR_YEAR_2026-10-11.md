**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `world-2022-price-response-from-serl-elasticity`

# Result: a per-household SERL elasticity gets the 2022 gas distribution, and misses electricity and the calendar year as predicted

Grades `SEAT_PREREG_A_PER_HOUSEHOLD_SERL_ELASTICITY_AGAINST_THE_PRIOR_WINTERS_PRICE_2026-10-11.md`.
The predictions were committed (`48ff82185`) before the run. The mechanism is
`simulation/price_response.py`, reached through `fabric_demand_path.build_fabric_series(price_response=True)`.
It is **landed OFF**: the settled book does not take it yet. Decided blind to company results.

## What was run

`/var/tmp/se-price-response/price_on_off_serl.py`, from a worktree at `origin/main` plus this change.
Each premise is built twice, with `price_response` off and on: same premise, stored weather
2021–2024, same seed. n = **230** fabric-eligible gas-heated premises of the live book. The
reduction is `1 − kWh(on)/kWh(off)`.

| window | gas median, IQR | electricity median, IQR | published (held out) |
|---|---|---|---|
| Oct 2022–Mar 2023 | **11.7%**, (0.4, 20.7) | **6.4%**, (−0.8, 14.8) | SERL gas 10.78% (1.19, 22.44); electricity 8.38% (−0.48, 17.56) |
| Oct 2023–Mar 2024 | 9.7%, (0.3, 17.5) | 4.7%, (−0.6, 11.3) | NEED cumulative 2021→2024: gas 13%, electricity 9% |
| Jun–Aug 2022 | 6.2%, (0.2, 10.9) | 3.7%, (−0.5, 8.5) | — |
| calendar 2022 | **6.0%**, (0.2, 9.7) | **3.4%**, (−0.4, 7.9) | ECUK C9, temperature-corrected: gas −11.6%, electricity −8.5% |
| Oct 2021–Mar 2022, and every day before 2022-04-01 | 0.0 on every premise (largest absolute value 0.0) | 0.0 | ~0 by SERL's design |

Spearman correlation of gas against electricity reduction per premise, winter 22/23: −0.092.

**A first run was thrown away, and why.** The first launch shared its worktree with a mutation
loop. `build_fabric_series` imports `price_response` lazily, on the first "on" call, and that
import landed while the "comonotone fuels" mutant was on disk. Every premise's two fuels then sat
at the same quantile. It was caught by recomputing three rows from the module directly. The run was
killed and re-run on clean files, and the log is kept beside this one as
`run_serl_CONTAMINATED_comonotone_mutant.log`. In the clean run, three rows recomputed from the
module match to two decimals.

## Grading

| # | predicted | result |
|---|---|---|
| P1 | gas 22/23 median 10.9 ± 1.5, IQR ≈ (1.5, 22.1) ± 2.5 | **Held.** 11.7, (0.4, 20.7). Against SERL: the median is 0.9 points high, the lower quartile 0.8 low, the upper quartile 1.7 low. |
| P2 | electricity 6.3 ± 1.5, IQR ≈ (−1.0, 14.2); a ~2-point miss against SERL | **Held, and the miss is real.** 6.4 against SERL's 8.38. |
| P3 | zero before April 2022 | **Held exactly.** The prebound leg's anticipatory 6.3% is gone. |
| P4 | gas 23/24 median 8.8–9.2 | **Refuted on the band, 9.7.** I gave P4 no sampling allowance. This sample's median gas elasticity is about −0.076, not −0.071 (P1's +0.8 is the same offset), and chained through 23/24 it gives about 9.6. The decay itself is as designed: 11.7 → 9.7, against the prebound leg's 14.8 → 13.3. |
| P5 | gas summer 2022 at 5.8 ± 1 | **Held.** 6.2. |
| P6 | \|ρ\| < 0.15 | **Held.** −0.092. |
| P7 | gas calendar 2022 at 4–7, a miss against ECUK's 11.6 | **Held, and the miss is real.** 6.0. Electricity is 3.4 against 8.5. |
| P8 | off arm byte-identical to HEAD | **Held by control**, not by this run: `test_off_is_the_world_as_it_was`. |

By stress band, winter 22/23 gas: HIGH 12.2 (n = 7), LOW 10.7 (n = 176), MODERATE 17.1 (n = 47).
The draw does not read stress, so this spread is sampling. SERL Fig. 3's gradient (poorer
households more elastic on gas) is **not** in the world.

## What it licenses

- **The gas winter is right in shape, not only in median.** The prebound leg's four defects are
  each gone: the spread, the anticipatory cut, the missing decay, and the missing electricity
  response. The remaining distance to SERL is within sampling of n = 230.
- **Switching it on in the settled book is the next step, and it is one variable.** It is
  `build_fabric_series_for_site` passing `price_response=True`. It moves every fabric premise's
  volume from April 2022 onward, so the world digest and the value arms are re-taken with it.
  Handed on as a continuation; not done here.
- **Two gaps, filed and not tuned:**
  1. **Electricity is 2 points short of SERL** (6.4 against 8.38) with SERL's own median elasticity.
     The paper's price basis has not been read: the unit rate, a bill including the standing
     charge, or the household's own tariff. Until it is, the elasticity is used as published, and
     the shortfall stands.
  2. **Calendar 2022 is about half of ECUK** (gas 6.0 against 11.6; electricity 3.4 against 8.5).
     Nothing responds to the October 2021 rise, or in anticipation of April's, because SERL's
     counterfactual winter is 2021/22 and its elasticity is not licensed outside the crisis. ECUK
     is a whole-stock annual figure and includes turnover, so not all of the gap is response. How
     much of it is response is a research question, not a reason to extend the elasticity backwards.
- **The legacy national-shape premises carry no response.** Half the redrawn book sits on the
  national shape
  (`SEAT_FINDING_HALF_THE_REDRAWN_BOOK_LEFT_THE_WEATHER_STORE_AND_SETTLED_ON_THE_NATIONAL_SHAPE_IN_SILENCE_2026-10-11.md`).
  This hook is in the fabric path only.
- `premise_trace._PRICE_ELASTICITY = 0.45` is still unsourced and still unfed. It is superseded by
  this mechanism and can be deleted once the book is on it.
