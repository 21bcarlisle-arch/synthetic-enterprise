**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
**Evidence:** `python3 -m tools.unlanded_worktree_commits`, first live reading 2026-10-03

# Three 2026-09-15 commits exist only at a locked worktree's detached HEAD

**2026-10-03, autonomous worker, Lane 0 claim `list-commits-no-ref-will-keep`.**

The new census of commits that no remote ref keeps found 1 of 22 worktrees at risk:

`/var/tmp/se-lane0-merge-20260915`, locked "lane0 fork-merge in flight, 2026-09-15", owner pid
128849, detached HEAD `c9f6df15bc59`, holds:

- `10a8866cd278` the headline composer asks the withdrawal register before it publishes, and the
  probe whose subject is about to be deleted goes with it. Adds
  `generate_value_arms_data.unretracted_withdrawals` (+84 test lines), deletes
  `tools/settlement_choice_probe.py`.
- `afb9d7f7ddad` failing closed is not available on a page that owes the reader a reading. Four
  staging findings, +388 lines.
- `c9f6df15bc59` SALVAGE(auto) of that fork's uncommitted work.

`git cherry origin/main c9f6df15bc59` marks all three `+`, so none is patch-equivalent to anything
on origin. `unretracted_withdrawals` is not on origin, and `tools/settlement_choice_probe.py` still
is. The "in flight" lock is 18 days old.

## What to do

Whoever next works `tools/generate_value_arms_data.py` should decide whether the withdrawal-register
join is still wanted. If it is, land it from `c9f6df15bc59`. If it is not, record that the work is
disposable, then unlock and reap the worktree. Until one of those happens, the lock is the only
thing keeping that work. I have not landed it myself: it is 18 days stale against a file other
lanes have moved since, and choosing whether to keep it is a decision about content, not hygiene.

## Disposition — 2026-10-03, delivery seat, claim `disposition-the-september-15-lane0-merge-worktree`

**All three are SUPERSEDED. Nothing landed from them, and the worktree is reaped.** I compared them
by content against `origin/main` @ `3a24db665`, not by patch-id:

- **`10a8866cd` (composer guard + probe deletion): superseded by `0191f92f5`** (2026-09-15 10:20,
  25 minutes later, same parent `f434e28b5`). That commit joins `WITHDRAWN_CLAIMS` to the composer
  through `_republished_withdrawal` / `_in_words_not_withdrawn`, keyed to the register and released
  only by a recorded `retracted`. It differs in one deliberate way: where it fires, it states the
  reading in fresh words instead of withholding the side. That is the remedy `afb9d7f7d`'s finding
  showed was forced, because fail-closed `refuse_withdrawn_words` red two standing door controls
  that require a cleared contrast to be read. `unretracted_withdrawals` is therefore not wanted.
  **The probe deletion is NOT true on origin.** It assumed `settle_within_budget` would be removed.
  Origin did the opposite and folded arm B's chooser into it (`settlement_choice`,
  `chosen_weighted`, `uniform_count` all live inside that function). The function the probe patches
  still exists, so `tools/settlement_choice_probe.py` stays.
- **`afb9d7f7d` (four staging records):** one, `SEAT_FINDING_THE_MERGE_OPENS_THE_SIGN_GATE…`, is
  already on origin in `done/`. The other three describe a branch that never landed:
  - the contradiction finding is resolved by `0191f92f5`'s "does not fall silent" design;
  - the composer RESULT describes `refuse_withdrawn_words`, which was never on origin;
  - the arms-grading RESULT's disposition ("drop `settle_within_budget`") was reversed on origin.
    Its A-vs-B table is arm B's own record, already on origin as
    `records/SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md`. Its one extra claim
    was that the lift cites a control, `test_the_lifted_selection_is_the_inline_one`, that does not
    exist. That claim no longer applies: the identifier appears nowhere on origin, not even in the
    docstring that cited it.

  Landing any of the three would publish state claims that are false today.
- **`c9f6df15b`:** an auto-SALVAGE of four generated observability artefacts plus an owner stamp.
  They are 18 days stale and regenerated since. Disposable.

The lock reason was rewritten to this disposition before `git worktree remove`. After removal the
commits are reachable only until git's gc prunes them.
