# A stalled focus atom was drawn as a trailing line nobody works, and B11 was moving all along under other ids

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Subjects:** `B11_forward_clv_backtested_on_held_back_history`, `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `a-stalled-focus-atom-says-why-it-stalled` (Lane 0 delivery)

**2026-10-05.** The trace asked for: where each BUILD draw of B11 and D48 went since 03:23Z, and why
the anti-livelock counter (151 for each in `docs/observability/.atom_stall_tracker.json` at 14:51Z)
climbed with nothing landing. A previous run of this same item (13:49-15:19Z, seat executor) hit
its 5400s limit and landed nothing; nothing it wrote survives, so this is a re-derivation.

## Where the draws went

Read from `docs/observability/supervisor-log.md` (entries parsed as blocks, 03:15-16:08Z),
`worker-tick-log.md` and `seat-executor-log.md`.

1. **The counter counts supervisor cycles, not turns.** The supervisor runs a cycle every 3-4
   minutes. Each cycle's BUILD draw picks one primary atom and calls
   `_record_atom_draw_and_check_stall`, which adds 1 whenever the atom's fingerprint
   (level, stage, simplifications count) has not moved. 155 "Work identified for the pull-loop"
   doorbells fired between 03:15 and 16:08; B11 was the self-refill atom in 84 of them, D48 in 47,
   B7 in 15, W2_39 in 1 and none in 8. "109 unchanged draws" therefore means about six hours of cycles, not 109
   attempts to do the work.
2. **The draw reaches a process only as a trailing line.** Each doorbell is the HEAD-red/staging
   census, then a Lane 0 item when one is drawable, then `|| self-refill from maturity map
   (dial-weighted): <atom> -- ?`. That last line carries no WORK text and no landing instruction.
   113 of the 155 doorbells carried a Lane 0 item ahead of the atom.
3. **Almost no doorbell reaches a turn.** The pull-loop is the interactive pane: 15 cycles logged
   `Session busy -- skipping`, and the rest of the doorbells stopped at the log. The worker tick
   spawned 13 bounded invocations in the window. 11 had a Lane 0 claim taken at dispatch and did
   that item, which is the explicit WORK with its own landing route. The other two (09:33, 10:01)
   carried no Lane 0 item, and no commit in their window touched B11's or D48's `file_scope`. The
   seat executor runs only continuations and Lane 0 items, never the self-refill atom.
4. **B11 was moving, under other ids.** `9680fbf4b` (B11 first slice, worker tick on Lane 0
   `b11-first-slice-forward-clv-backtest-against-the-flat-rule`, 13:00Z) and `4e4637853` (B11
   slice 2, seat executor on `b11-second-slice-attribute-the-two-books-verdicts`, 16:03Z) both
   landed on B11's own `file_scope`. Its map row is still `0|3|build|1`. The counter waits for a
   map write that a Lane 0 slice does not make, so the counter reads "stalled" while the atom moves.
5. **D48 has not been started.** Its `file_scope` (`company/billing/billing_accuracy.py` and its
   test) does not exist on disk, and no commit since the window opened touched it. Its world-side
   prerequisite (W2_36: billed differs from used) was the Lane 0 item being worked at 14:29Z, so
   D48 waiting is correct. Nothing said that it was waiting, or on what.

**Why nothing landed under the atom ids:** the atom route has no consumer. Every landing on these
subjects today went through a Lane 0 slug, and the stall counter cannot see a slug.

## The change

`_record_atom_draw_and_check_stall` now writes a `stop_reason` onto any row past the threshold,
plus `episode_started_at` when an episode opens. The reason is read from git over the atom's own
`file_scope` since the episode began. It is one of four:

- commits landed on the scope but the map row did not move;
- no commit, and N of M scope paths exist;
- no `file_scope` declared;
- git could not be read.

For a streak older than the field, the window is the last seven days, and the reason says so.
`delivery_seat.build_brief` carries these rows as `atoms_stalled_with_reason`, placed before the
commit list so truncation cannot drop it, and the prompt prints each reason beside its atom.

## Pre-registration (written before the first live draw after the supervisor restarts)

- **B11:** the reason names its commits (2, latest `4e4637853`) and says the map row is unmoved at
  level 0 / build.
- **D48:** the reason says no commit, and 0 of 2 scope paths on disk.
- **If either comes out otherwise,** the git read or the scope read is wrong, and the reason must
  not be trusted until that is found.

**Not covered:** the landed code is inert in a running supervisor until `deploy-restart.timer`
restarts it. That restart happens when the code moves, but check `deploy_restart --report` before
reading an empty reason as a fault.

**What it does not fix:** the trailing `-- ?` atom line still has no consumer. The remedy is in
the seat's hands, not in more machinery: a focus atom gets worked when the seat writes a Lane 0
slice for it, as B11's two slices show. The open "focus atom drawn repeatedly and lands nothing"
row can be graded corrected once a brief shows the two reasons.

## Graded 2026-10-05 18:40 BST (claim `stalled-atom-stop-reasons-reach-the-brief`)

**The pre-registration holds.** `_atom_stop_reason` was run at real inputs: the live map rows, and
the shared tree's tracker read from an `origin/main` worktree.
- **B11:** "2 commit(s) landed on its file_scope … latest `4e4637853` B11 slice 2 …, but its map
  row did not move (level 0, build)". This is as predicted.
- **D48:** "no commit touched its file_scope …; 0 of 2 scope path(s) exist on disk". This is as
  predicted.
- Both windows say "7 days; the streak's start is unrecorded". That is correct: both streaks
  predate `episode_started_at`.

**The route to the brief was wrong, and the "Not covered" note above understated it.** A
supervisor restart would not have put the reasons on these two rows.
- The anti-livelock draw (`_prefer_least_stalled`) takes the LEAST-stalled candidate. Once B11 and
  D48 were the most-stalled rows at 151, the draw stopped taking them. Their last draw was 15:51
  BST. At 18:30 the least-stalled rows were B7 and W2_39, at 40.
- A reason written only on a draw is never written for the atoms most in need of one.
- `atoms_stalled_with_reason` listed only rows drawn in the stretch, so B11 would have dropped out
  of the brief at 18:51 BST with no reason ever shown.

This is the anti-correlated screen: the worse the stall, the less the screen can see it.

Two further facts held at that time:
- The shared checkout was still on `4e4637853`, behind `f1cbb15ca`.
- The supervisor had been up 7.8h. `deploy_restart --report` graded 0 of 10 daemons (all
  `unstamped`), so it could not say whether the supervisor was stale.

**Repair (this landing):** `atoms_stalled_with_reason` now takes the focus as an input.
- It includes stalled atoms in the previous focus and the live focus, even when the draw no longer
  takes them. It marks those rows `drawn_this_stretch: False`, and the prompt prints "not drawn
  this stretch".
- When the supervisor has not stored a reason, it reads one with the supervisor's own
  `_atom_stop_reason`. The brief therefore no longer depends on a daemon restart.
- `tests/background/test_a_stalled_atom_says_why.py` was mutation-checked. Removing the focus leg
  turns it red, and so does dropping the not-drawn marker.

**The open "focus atom drawn repeatedly and lands nothing" row** in `DIRECTION.yaml`'s `wrong` list
is NOT graded here. The orienting seat writes that file.
- The condition for grading it corrected is the first brief built on a checkout that contains this
  landing, with B11 shown beside its reason.
- B11 is in the live focus, so it will appear.
- D48 is no longer in focus. It appears only if it is drawn, which is correct: the seat has no
  steer on it to correct.

**Still open, as before:** the trailing `-- ?` atom line has no consumer.

**A caveat on reading the reasons:** H45 and PB4 also read "N commit(s) landed … landing under
other ids". Their scopes are shared with other atoms' work, for example PB4's latest is a C29
commit. That reason is evidence that the scope moved. It is not evidence that the atom moved, and
the text already says "if that is its work".
