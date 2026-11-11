# Disposition: the-close-refund-fix-and-its-run-wiring-reach-origin is premise-spent

**Kind:** disposition (worker tick, 2026-11-11). Drawn as LANE 0; nothing left to land.

## What the tree shows
- K8 page: `cf399ab43a` (home_moves.md s.8.8c, s.8.8d) is on origin/main.
- Engine, run wiring and both controls: `cab13bbd18` is on origin/main. B and C were landed
  together on purpose, and the commit message says why: the launcher requires `money_in` on origin.
  So "three commits" became two. The ask, all three pieces on origin, is met.
- The wiring in `3364405088` (`/var/tmp/crfix2/mut`) is byte-identical to origin's
  `simulation/run_phase4c_on_phase2b.py`: `git diff 3364405088 cab13bbd18 -- <path>` is empty.
- Worktrees: `/var/tmp/crfix2/mut` had 0 dirty paths and no process cwd, and has been removed.
  `/var/tmp/crfix-land-wt` and `/var/tmp/crfix-page-wt` were already gone.
  `/var/tmp/book-wt-crfix-*` were left alone, because they belong to the running book.
- The successor, `the-first-book-carrying-the-close-refund-fix-is-run-and-graded-through-the-publishers-gate`,
  carries the book (relaunched 14:07 on 6fe7827ab2, per 72ec873803).

## Recorded
`delivery_lane --premise-spent ... cab13bbd18` and then `--release`.

## A guard keyed to the wrong side (small, filed here rather than minted)
The continuation-retire check refused with "the artefact it names does not exist yet:
/var/tmp/crfix-land-wt, /var/tmp/crfix-page-wt, /var/tmp/crfix2/mut". For this item, those paths
going away IS the exit condition: they are the worktrees it was told to remove. A continuation whose
done-state is the deletion of the paths it names can never retire, so the continuation stays
offered and could be drawn again. Proposed fix: let a continuation declare whether its named paths
are things it creates or things it removes, and stop treating every named path as a creation.
Until then, the next tick to draw this id should release it on sight.
