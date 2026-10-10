**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# Pre-registration: B8 L3 re-read on single-levy bills (origin 7252e8d72)

Filed 2026-10-10 ~15:05 BST, before either arm started. Answers unknown.
Same harness as the 10-09 reading: CURRENT_POLICY, retention_runs_holdout off vs on, default roster
(400 founders), report_end 2019-12-31. Not one-variable against 10-09: the levy fix, the 10-10
conversion gate, and ~80 other commits sit between.
1. 0 holdout rows carry decided=True. (The interval cannot decide at this book size.)
2. Holdout rows to 2019-12-31: 60-140 (10-09: 121 pre-gate; the gate can only shrink the set, but
   the founders' renewals are otherwise unchanged by the levy fix).
3. Flag-on makes 40-65% of the flag-off arm's offers.
4. |net(on) - net(off)| < flag-off booked retention cost; sign not predicted.
5. Flag-off retention cost per offer within +/-15% of 10-09's GBP 23.1 (2,776.90/120): ret_cost reads
   the unit rate and margin, not the bill total, so the levy fix should not move it much.

Why: the stretch record lists B8 L3 among the readings taken on double-levied bills (1d3c28930).
Harness: /var/tmp/b8relevy/arm.py, worktree /var/tmp/se-b8-relevy at 7252e8d72; arms started 15:06 BST.
The grade lands beside the 2026-10-09 L3 finding.
