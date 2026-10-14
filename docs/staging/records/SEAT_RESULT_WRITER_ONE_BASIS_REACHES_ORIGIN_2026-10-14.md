**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `acquisition-and-retention-economics` -- the page whose 8 per cent paragraph this carries onto origin

# Writer 1's unit-rate margin basis reaches origin (2026-10-14)

*Delivery seat, LANE 0 draw `writer-one-margin-basis-and-one-floor-for-the-save`.*

`e3b5ed01a` (writer 1 reads the unit-rate margin against its own strike; the save takes the renewal
desk's floor) was gated green at 08:33 in `/var/tmp/se-w1-basis` and reached no remote. It is now an
ancestor of origin/main through merge `87e9f4245`, landed by `surgical_land --merge` from an
origin base and promoted at about 12:15.

- **Draw-time credit was wrong.** `7c1ee032b` is the knowledge-first P1 page, not this fix, so the
  premise was not spent.
- **A second lane got there first and died mid-merge.** Worker pid 3855995 owned the stranded
  worktree and had a `surgical_land --merge origin/main` running at 11:53. It exited at about 11:59
  with no commit, and the worker itself was gone, so nothing would have retried. Its
  `merge3.log` is empty: whatever stopped it left no trace. If a rival landing is in flight, wait on
  its pid before taking over, and read the tree after it exits, not the log.
- **One conflict, `site/data/knowledge_topics.json`**, in the acquisition-and-retention body. Origin
  added the at-the-floor paragraph and the pre-2019 price-match GAP. This side changed the
  retention-floor sentence ("one floor for the premium, the save and the renewal cut") and added
  "What the 8 per cent counted". All four were kept. The dead lane's own resolution had the same
  content in a different paragraph order.
- **The grade is still owed and still armed.** `/var/tmp/w1-basis-out/handoff_when_done.sh` (pid
  2315101) files `grade-writer-one-basis-on-seed-61109` when `ALL_FINISHED` appears. The origin arm
  finished at 11:55, and the fix arm (seeded_arm pid 3252711) was still running at 12:15. The
  pre-registration is on origin, unchanged, and still ungraded.
