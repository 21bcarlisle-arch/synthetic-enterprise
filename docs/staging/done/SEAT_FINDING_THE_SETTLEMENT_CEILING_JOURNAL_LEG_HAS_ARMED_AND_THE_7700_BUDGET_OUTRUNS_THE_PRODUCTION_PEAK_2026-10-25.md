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

## Closed by exit (1), 2026-10-25

**The curve was re-measured at today's code, and 7,700 stands on it.** A worker tick earlier today
ran the 20 Oct method (`tools.settlement_ceiling_probe`, scratch worktree
`/var/tmp/se-ceiling-probe-20261025`, full window, serial, both points clean, campaign record
agrees) and was stopped before landing. Its code is origin `7a692b47ae` (carries `904a091f7b`). The
salvage head differs only in observability files and the handshake. Landed as
`docs/observability/settlement_ceiling_slope_20261025.json`, with the head re-pointed as on 20 Oct.

| Budget | Committed cy | Peak child RSS | Wall |
|---|---|---|---|
| 7,700 | 7,699.3 | 5,555.9 MB | 3,567 s |
| 8,400 | 8,398.5 | 6,254.1 MB | 4,667 s |

Slope 0.999 MB per cy. With the 227 MB parent the curve supports **7,924.7 cy** against 6,008 MB.
The production peak of 5,595.3 MB, re-priced on this curve, gives 8,112.6. `SETTLEMENT_CUSTOMER_YEAR_BUDGET`
stays 7,700. The book does not move.

**What the re-measure shows.**
- At the same 7,700 point the program is 443 MB heavier than on 20 Oct (5,113.2 MB at `7858b89a6`).
  It agrees with production's 5,595.3 MB to within 40 MB, so production was not an outlier. The
  code moved. I cannot yet say which commit did it, and no single-variable run has been done.
- Wall time fell from 9,232 s to 3,567 s. That is also not attributed.
- **Why the leg went red, and why it will not just come back.** The old curve's anchor was at
  6,997 cy. The leg substitutes a production peak for the anchor's y and keeps its x, but production
  runs at 7,700, so a 7,700-cy peak was being priced as if it were a 6,997-cy one (702 cy of the
  730 cy gap). Now the anchor is at 7,699.3, production's own x, so the leg compares like with like.
  The leg also substitutes a single-process peak for an anchor that includes the parent. That
  understates by about 227 MB, in the other direction. Both of these are the leg's own arithmetic.
  They are recorded here and not changed in this landing.
- **His caveat, read honestly.** Production peaks (5,499.7 and 5,595.3 MB; systemd whole-service 5.4G)
  sit 413 MB under 6,008, outside the 5% band (5,708). The probe child plus the nominal 227 MB parent
  (5,782.9) sits inside it. His caveat names production runs, and they have not tripped it. The
  margin is thin, and that has been raised to him with a recommendation.

**Held correction landed.** `bad_debt_provisioning.md`: the "5-7x" is marked true of the 12 Oct world
only (0.665% on the 24 Oct book, 0.725% with the gone-household rule), beside the claim.
