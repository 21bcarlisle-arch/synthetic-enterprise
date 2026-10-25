**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The settlement ceiling's journal leg has armed, and the 7,700 budget outruns the production peak (2026-10-25)

**What was seen.** `tests/simulation/test_net_new_acquisition.py::test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today`
is red in the commit gate (25 Oct, 01:2x BST):

> re-priced on the 5,595.3 MB cgroup peak systemd reports for sim-runner.service across 2
> lifetime(s) on code carrying 7858b89a6, the curve supports 7,430.4 customer-years and the
> constant asks for 7,700.0.

The two lifetimes are production runs at `904a091f7b`: "Run largest process peak" 5,499.7 MB
(20:50 UTC) and 5,595.3 MB (23:34 UTC, 24 Oct). This is the leg `11766c143` (21 Oct) left
UNAVAILABLE until the first run on the 400-household shape and the 7,700 budget closed. Those runs
have now closed, and the leg reads them as the control was built to.

**What it blocks.** Every commit whose gate selects `test_net_new_acquisition.py`, in any lane.
`docs/market_research/bad_debt_provisioning.md` is one such path, so its one-line correction (the
"5-7x" there was true of the 12 Oct world only; see `debt_realism_three_world_fidelity_gaps.md`
s.1a) was held out of the landing that settled the 0.15% baseline, and is owed behind this.

**The choice is not mine to make by default.** There are two honest exits, and they differ in what
they assume:
1. Re-measure the curve at today's code (the prereg of 20 Oct names its method), then let the
   ceiling follow the measurement.
2. Lower `SETTLEMENT_CUSTOMER_YEAR_BUDGET` to what the curve supports now. That shrinks the
   production book, so the run's results move.

Raising a tolerance or skipping the leg would be keyed to today's answer, so it is not on the list.
**Recommendation:** (1) first, because both runs ran on one commit: 5,500 MB and 5,595 MB is a
single program, and the curve's 4,671 MB anchor at 6,997 customer-years was measured before
`8927e9345` landed the shape. If the re-measured curve still refuses 7,700, take (2) with its
customer-years printed.
