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
