**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `anchor-the-446-bare-world-constants-in-impact-order`
**Knowledge:** world-constant anchors -- `docs/design/world_constant_impact_ranking.md`

# The settlement-loop screen puts policy_costs fifth, and two of its three tables were already sourced

Grades P5-P9 of
`docs/staging/records/SEAT_PREREG_WHICH_OF_THE_446_BARE_WORLD_CONSTANTS_A_PRODUCTION_RUN_READS_2026-10-19.md`.
Commit 74981f336 said these would be graded "in the finding". No finding was written, because the
turn that ran the screen ended with the screen still running. Its 41 arms survived on disk
(`/tmp/wcr_arms/`, machine-local) and are graded here. The full table is in the ranking page.

- **P5 (full window reaches < 15% more): UNGRADED.** Both full-window runs were killed with their
  turns, at 2022-08 and 2018-06. No result exists. To run it, it has to be launched detached.
- **P6 (baselines agree to the last digit): HOLDS.** Three baseline arms, one of them 40 minutes after
  the other two, are identical in all 48 figures.
- **P7 (at most half the modules move gross > 0.1%): HOLDS.** 11 of 41 did.
- **P8 (`premise_trace` and `fabric_physics` in the top three on gross): REFUTED.** The top three are
  `premise_trace` 3.11%, `live_population` 3.10% and `sim/weather_hdd` 2.37%. `fabric_physics` is
  fourth at 1.31%. What I missed was that one statutory or conventional factor (the CV, the CF, the
  15.5 C HDD base) moves gross as much as 52 premise constants pushed together.
- **P9 (`feedback_survey`, `sim_satisfaction` move no money figure > 0.1%): HALF.** `feedback_survey`
  moved nothing. `sim_satisfaction` was not reached before the screen stopped.

**This screen's bad-debt column is not a ranking.** The settlement loop's bad debt is overwritten
by the published entry. P10-P13 cover that, and the published-entry screen is running.

**What it changed.** `simulation/policy_costs.py` moves gross 1.21% through three tables. Two of
them were sourced and read as bare. They are the same shape as the finding on the scan's publisher
list:
- `_GAS_SC_PENCE_PER_DAY_BY_YEAR` is re-derived from Ofgem's cap model by
  `tests/simulation/test_standing_charge_reproduces_the_cap_model.py`, but its comment only said
  "as the electricity table above".
- `_CFD_LEVY_BY_YEAR` sat inside the bands of `docs/market_research/historical_policy_costs_2016_2024.md`
  §2 and cited "EMR Settlement". That name is not in the pattern. It is now an EVIDENCE RANGE, with a
  GAP: no row is re-derived from the quarterly ILRs.

`household_segments::TENURE_POPULATION_SHARE` (gross 0.28%) cited EHS 2023-24 via a bare
"ASSUMPTIONS.md". That is now a `docs/` path. No values moved. With `DD_SHARE_GAS` (see the cohort finding) the register goes 435 -> 431.

**Open, named.** `_SME_SC_MULTIPLIER = 1.5` has no source in the tree, and it stays registered.
`sim/weather_world.py::MAX_SNAP_KM` is a refusal tolerance, and pushing it from 5 to 5.5 km moved
gross 0.23%. Its one caller, `simulation/fabric_demand_path.py::site_for`, turns a refusal into "no
cell", which takes the premise off the fabric-physics demand path. So the push moved some homes
from the fallback onto fabric physics. The tolerance sets coverage. It is not a world fact. The
fix is to add the missing cells (`ADD_THE_CELL_REMEDY`), not to cite a number.
