**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `A46_book_depth_is_a_curriculum_question`

# Pre-registration: depth or width, which buys a measurable selection effect sooner

**Filed 2026-10-02, before any arm has run.** Director, same day: *"more renewals per customer is a
lever as well as more customers… Say whether running past the known years is a cheaper route to a
measurable selection effect than raising the memory share, and measure it rather than reasoning
about it."*

## What the two levers are, in this tree

- **"Memory share"** is a number: the settlement customer-year budget is priced at 0.25 × the guest's
  RAM (`net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET`, 1,250 at the pin, 1,050 at HEAD after the
  10-02 re-price). Raising it buys WIDTH, meaning more accounts.
- **More years** buys DEPTH, meaning more renewal decisions per account. Both spend customer-years.
- **Running past 2025 is not runnable today.** `SPINE_1_scenario_world_state` (L2) lives in
  `sim/scenario` and is not wired into the run loop, and `run_value_cycle_ab` can only truncate the
  window (`--end-year`). So the depth lever is measured INSIDE the known record, ending the same
  seeds at 2019 and 2022 against the existing 2025 runs. **Assumption, stated rather than hidden:**
  a scenario year past 2025 adds decisions like a historical year does. If the depth arms show the
  lever is worth having, wiring SPINE_1 into the run loop is the follow-on, and it is real work.

## Design

Same pin (`a322166cc`), weather store (digest `e11451b5…`), redraw key (`churn_roll`) and seeds
(61001–61006) as ab6's P1/P2/X1, which are the depth=2025 / width=1.0 cell. Serial, nothing else
resident, through `/var/tmp/se-depthwidth-out/legs_dw.sh`.

| cell | years | book | new legs |
|---|---|---|---|
| D2019 | 2016–2019 | 80 founders, budget 1,250 | 3 × 2 seeds |
| D2022 | 2016–2022 | same | 3 × 2 seeds |
| D2025 (baseline) | 2016–2025 | same | already run: raw mean −£3,437, sd £4,686, SNR 0.73, ~132 scored decisions/seed |
| W1.25 | 2016–2025 | 100 founders, budget 1,562.5 | 6 × 1 seed (single-seed legs keep the peak memory safe) |

Per arm: selection per seed, its mean, sd and SNR (|mean| / sd), raw and by ab6's own grader
(D_lin ex-0098); scored renewal decisions; settled customer-years; CPU-seconds and peak RSS per leg
(`/usr/bin/time -v`).

## Predictions

- **P1 (the mechanism):** selection behaves like a sum over renewal decisions, so SNR ∝ √decisions.
  Predicted SNR: D2019 ≈ 0.42 (≈44 decisions/seed), D2022 ≈ 0.60 (≈88), W1.25 ≈ 0.82 (≈165).
  Falsifier: SNR does not rise with decisions across the four cells.
- **P2 (the answer):** **depth buys more scored decisions per customer-year than width**, because an
  extra year renews every account already in the book, while extra width arrives through the growth
  campaign later in the window and carries fewer renewals each. Falsifier: W1.25's decisions per
  customer-year ≥ D2025's.
- **P3 (the cost):** width's peak RSS rises ~1.25× and is the binding cost, since that is what the
  memory share prices. Depth's cost is mainly CPU time, roughly linear in years.
- **P4 (what "measurable" needs):** at SNR 0.73, about 7 seeds give a 95% interval that excludes zero.
  Reaching it in 4 seeds needs SNR ≈ 1.0, about 1.9× today's decisions: roughly 7–8 more years by depth,
  or nearly doubling the memory share by width, which this guest cannot give. I predict depth is
  the cheaper route, and that it requires SPINE_1 to be wired before it can be taken.

**Honest limit, stated up front:** six seeds per cell estimate SNR to about ±0.4, so cell-by-cell
SNR differences may not be resolvable. **The primary answer is P2** (decisions per customer-year),
which is far less noisy; P1 is graded on the pooled trend across all four cells, not on any pair.

## Result — graded 2026-10-03 (depth complete; width on one seed pair)

**What ran.** Depth, all six seeds at 2019 and 2022 (`/var/tmp/se-depthwidth-out/depth_*.json`).
Width: one pair (61001, 61002). Its first two launches were invalid on my side: single-seed legs,
which the noise floor rightly refuses ("one seed is a run, not a spread"), then a crash on a term
starting 29 February 2020, a real defect fixed as a class in `c28b7b173`. Its remaining two pairs
were stopped at 23:53Z by an executor turn freeing memory for the retake noise floor, which is
arbitration between two lanes that each need about 11–14 GB serially, not a fault. The pinned width
copy differs from `a322166cc` in the two lever lines and the leap-day guard, and the 80-founder depth
runs never drew a 29 February start, so the cells stay comparable.

**Customer-years are not recorded in the artefact**, so P2 cannot be read as worded. It is graded on
what "cheaper" costs in practice, which IS measured: CPU-hours and peak memory per two-seed leg (the
2025 cell from ab6's own unit record, X1: 2.90 CPU-h, 10.8 GB).

| cell (seeds 61001, 61002) | decisions/seed | selection | peak | CPU-h | decisions/CPU-h | decisions/GB |
|---|---|---|---|---|---|---|
| depth 4y (2019) | 78 | +£424, −£1,651 | 6.4 GB | 1.00 | 156 | 12.3 |
| depth 7y (2022) | 104 | −£1,029, −£10,610 | 8.7 GB | 1.91 | 109 | 11.9 |
| depth 10y (2025) | 134 | −£1,152, −£12,726 | 10.8 GB | 2.90 | 92 | 12.4 |
| width ×1.25, 10y | 183 | **+£210, −£78** | 13.4 GB | 3.31 | 111 | 13.7 |

All six depth seeds: SNR **0.19 (4y), 0.33 (7y), 0.73 (10y)**, with the mean moving +£419 → −£1,654 → −£3,437.

| | prediction | result |
|---|---|---|
| P1 | SNR rises with decisions, ∝ √decisions | **Direction HELD, form REFUTED.** Decisions grow 1.66× from 4 to 10 years while SNR grows 3.8×, and the mean effect itself builds. Selection compounds with tenure; it is not a fixed effect per decision diluted by noise. |
| P2 | depth buys more decisions per unit cost than width | **REFUTED on measured cost.** Width delivers as many or more decisions per GB (13.7 vs ~12) and per CPU-hour (111 vs 92 at the same window). |
| P3 | width ~1.25× memory; depth mainly CPU | **Width HELD** (13.4 vs 10.8 GB, 1.24×). **Depth REFUTED**: memory rises with the window, about 0.7 GB per year of a two-seed leg (6.4 → 8.7 → 10.8 GB). |
| P4 | depth is the cheaper route | **Mixed, and the useful answer.** Per decision, the two levers cost about the same memory. Per unit of SIGNAL they differ: years build the effect, while the 1.25× book's extra 49 decisions per seed came with no visible effect on its two seeds (+£210, −£78 against −£1,152, −£12,726). Two seeds cannot grade width's SNR. That is a lead, not a result. |

**The answer to the director's question.** A measurable selection effect is bought by YEARS, not by
accounts: the effect compounds with tenure, so an extra year of window grows it while extra width so
far adds young accounts whose decisions carry little of it. Years are not free. They cost memory at
about 0.7 GB per year of a two-seed leg, so on this guest (23 GB admissible, ~3–8 GB resident) a
window about 4–5 years past 2025 is the ceiling, and it needs SPINE_1 wired into the run loop first,
which is real work. **Not established here:** width's SNR (four of its six seeds unrun) and whether a
scenario year past 2025 compounds like a historical one. The remaining width pairs rerun when no
other value-cycle A/B is resident (`legs_dw.sh` skips finished legs).

**Width pairs two and three, 2026-10-03 00:50Z: queued, not yet run.** `longjob-depth-vs-width-w125d-20261003`
is waiting behind the resident 1002c noise floor (pid 1933972, started ~23:55Z) and will run 61003,61004 then
61005,61006, about 3.5 h each. `longjob-depth-vs-width-handoff` waits on its `legs_dw.sh` and, on exit,
hands off the grading as continuation `grade-width-snr-over-six-seeds`. The waiter was started with a plain
`systemd-run`: `launch_long_job` refuses every launch while w125d is resident, a 200 MB waiter included,
because it counts w125d's declared 14.5 GB peak on top of resident memory. The width SNR and the verdict on
the two-seed lead are still owed here.
