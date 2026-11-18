# Disposition: the-box-runs-the-skip-pair-before-another-book is premise-spent

**Kind:** disposition (worker tick, 2026-11-18 ~13:27Z). Drawn as LANE 0, but every part of done-means already held.

## What the tree and the box showed at draw
- `background/next_book_requires.yaml`: the null row (`commit: null`, `what: skip pair read (...skip1/... and ...skip0/control_11111_22222.json)`,
  `owner: B_commercial`, REVERSE comment) is on origin/main as `c180676463`.
- `book_admission()` returns `admitted: False`, and the reason it gives is that row.
- The step that deletes the row once both control files exist: `ec3ee1d69e` added it to DIRECTION focus
  `skip1-is-graded-against-s12es-branches`.
- pid 484274 (the 7f0723b46e book) had exited. `longjob-value-test-threshold-skip.service` was active and running.
  The skip1 driver child (pid 1873447, `--child 11111,22222 ... vts-out-skip1/control_11111_22222.json`) had been up 18 min.
- `/var/tmp/value-test-threshold-skip` existed and was `git worktree lock`ed ("s.12d threshold-skip pair; recreated 18 Nov after deletion").
- Neither control file existed yet. Nothing was launched, because a second copy would run over the same seeds.

## Disposition
Released. The remainder is grading skip1, then reading skip0 and deleting the row. That is carried by focus
`skip1-is-graded-against-s12es-branches`. The listed continuation `the-wedge-refill-names-its-wait-and-stays-quiet`
is separate work (supervisor RUNG 1), and this tick did not draw it.
