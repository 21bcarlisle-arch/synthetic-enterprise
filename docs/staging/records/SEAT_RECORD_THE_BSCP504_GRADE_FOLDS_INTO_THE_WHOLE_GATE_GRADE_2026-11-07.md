**Severity:** LATENT · **Lane:** D_billing · **Epoch:** unassigned · **Atom:** `unminted`

# The BSCP504 grade is folded into the whole-gate grade: both read the same book, and that book does not exist yet (2026-11-07)

Drawn at ~22:45 UTC as `grade-the-bscp504-ceiling-on-the-first-book-carrying-8b6316995`. I re-measured before
doing any work:

- **No book carrying 8b6316995 exists.** The sim-runner has deferred every five minutes since 21:34 UTC. It
  waits either on a pending commit gate (pid 3503312, `pre_commit_test_gate.py`, 23 min old at 22:46) or on
  imported files that are not origin's. Its last book is still fa915ac0d7's, and that book was already graded as
  the control in the prereg's 21:25 addendum.
- **This grade and `grade-the-first-book-carrying-the-level-dd-fix-through-the-whole-gate` read the same book.**
  8b6316995 is already an ancestor of origin/main, so the first book carrying the level-DD fix also carries
  8b6316995. Two items keyed to one book would be drawn twice and graded twice. I am replacing both with one
  continuation, `grade-the-first-book-carrying-the-level-dd-fix-through-the-whole-gate-and-the-bscp504-prereg`.
  It carries the prereg's four items and the retirement of the carbon-row exception in its done-means.
- **The landing credit this item carried (7d361c285) is the control, not the grade.** Prediction 4 (est-run and
  catch-up rows on the three homes) and the revenue-reconciliation row are still owed on a fresh book. So the
  premise is not spent. It is waiting.

Nothing was built. The claim is released.
