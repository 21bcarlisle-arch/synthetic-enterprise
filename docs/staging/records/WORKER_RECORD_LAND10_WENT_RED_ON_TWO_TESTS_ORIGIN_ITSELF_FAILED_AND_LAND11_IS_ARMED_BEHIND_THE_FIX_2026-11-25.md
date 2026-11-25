# land10 went red on two tests that origin/main itself failed, and land11 is armed behind the fix

*Worker, 25 Nov 2026, holding `land10-outcome-is-read-and-msc-lands-or-is-re-cut`.*

**What land10 did.** It passed both artefact waits and the fire-time stale-copy census (23:51Z, clean
apart from the declared drop). It took the landing-gate lock after 620 s and gated the MSC replacement
win on the tree the commit would create. The gate was RED at 00:59Z: 2 failed, 3,347 passed, in
3,379 s. Both failures were in `tests/simulation/test_run_phase4c_on_phase2b.py`: the two council-tax
listing tests. The ended file reads `exit 1`. None of the item's four named outcomes applies (landed,
stale copy, gate timeout, exit 7). It is a fifth outcome: a red gate.

**The red was not the MSC patch's.** On a clean worktree at origin `16fdeee0ab`, *without*
msc8.patch, both tests fail in 13 s. With the patch, they fail the same way. Both tests pinned the
listed account to `PROS-2016-0098`. `live_premises()` now draws 1,097 premises, and that prospect is not
among them. The growth campaign now asks the first-term quote before the win (`f3c6a45cbd`, 210 → 230
wins). So the feed was right to answer None, and the tests were keyed to today's answer, not to the
property.

**The fix** is `dd6901041b`, landed on its own. It re-keys both tests to the smallest id in `_listed_dwellings()`:
a drawn dwelling reads True, and an occupier at it reads True. A feed that answers None for everyone
still fails the first leg. An empty list raises.

**land11** is `/var/tmp/se-msc-keep/land11.sh`, unit
`longjob-land11-msc-replacement-win-after-council-tax-fix`, armed 01:41Z. It runs land10's fire-time
section unchanged (msc8.patch, 3-way apply, the declared drop, the census, msg9, promote). It sits
behind one new wait: the fix is on origin/main (stop 9 after 6 h). The book and rankq waits are spent,
and `busy()` is kept. Outcome files: `/var/tmp/se-msc-land11-ended.txt` and, on landing,
`/var/tmp/se-msc-replacement-win-landed-land11.txt`. The log is `/var/tmp/se-msc-keep/land11.log`.

**For the next holder:** read `land11.log`. LANDED: verify the commit is on origin and the MSC test is
green there. Stop 11: re-cut msc8.patch. A new red: check origin first, as here, before blaming the patch.
