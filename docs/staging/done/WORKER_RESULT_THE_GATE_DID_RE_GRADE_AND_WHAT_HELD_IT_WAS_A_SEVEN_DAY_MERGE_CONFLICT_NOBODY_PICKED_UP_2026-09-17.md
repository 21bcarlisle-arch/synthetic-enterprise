**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The gate did re-grade, and what held it was a seven-day merge conflict nobody picked up

*Worker, 2026-09-17. Claim `the-publish-gate-must-now-grade-a-clean-publish-itself`. Predictions
filed before the work in
`docs/staging/records/WORKER_PREREGISTRATION_WHETHER_CLEARING_TEN_SUPERSEDED_WORKING_COPIES_CLOSES_THE_PUBLISH_FORK_2026-09-17.md`;
the class finding is consolidated into `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` and archived as
`WORKER_FINDING_THE_PUBLISH_WEDGE_IS_SEVEN_DAYS_OF_ONE_UNRESOLVED_MERGE_CONFLICT_AND_THE_NARROWING_THAT_DEEPENS_IT_HAS_NO_CEILING_2026-09-17.md`.*

## 1. The drawn question, answered

**The gate re-grades itself. The item's premise is spent.** It described 12 blocking tests, all
from the repaired ledger-guard set; `.publish_gate_state.json` at the start of this turn carried
`total_red: 1` and one blocking test. Nothing had to be done to make that happen and nothing in
this turn re-fixed a red.

**The item's predicted remainder is REFUTED.** It expected the HEAD ref-lock loss
(`cannot lock ref HEAD: is at aff4b153f but expected 56d746816`). No ref-lock refusal is live
anywhere in the record; the latest `liveness_surface_refusal` names `push_never_landed`, and the
cause underneath it is a **fork**: `origin/main` 6c1e769b4 and HEAD 1a69fbb23, 7 behind and 9
ahead, neither an ancestor of the other. `wedge_since: 1789011039.7` = **2026-09-10T03:30Z**.

**What held it:** `origin_reconcile` refuses to close the fork because the merge conflicts, and
refusing is correct — *"an automatic reconciler must not pick"*. Two paths:
`tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line.py` and
`tests/tools/test_the_weather_store_validator_cannot_pass_a_skipped_leg.py`. The
[ORIGIN FORK] alarm had fired **46 times over 101.9 hours** on that same refusal and escalated
itself into the draw on 2026-09-15, where it sat. The alarm worked; nothing drained it.

## 2. The correction to my own first reading, beside it rather than over it

I began by treating the ten `origin_reconcile` blocker paths as the constraint and pre-registered
that clearing them would close the fork. **Prediction 2 is refuted.** Those ten are real and every
one of them is a stale working copy of work already on origin (six byte-identical, three where
origin is strictly richer, verified hunk by hunk) — but they block only the *shared tree's
fast-forward*, which is the step AFTER the merge. The merge never got that far. **The blockers were
downstream of the thing that was actually stuck**, and running the reconciler rather than reasoning
about its refusal text is what showed it.

Predictions 1, 3, 4 and 5 hold. Prediction 5 in particular: the local side of the fork holds the
paused banner and the liveness heartbeat **twice each**, an hour apart (7c28ea31f/882ef8aad at
02:54–02:56, 8a7be23f0/1a69fbb23 at 03:56–03:58) — four unpushable commits out of nine.

## 3. A thing nobody had measured: the remaining red IS live at HEAD

The single blocking test, `test_a_level_tree_still_publishes`, runs green in the shared tree — so
it reads as a stale red census. It is not. In a clean `git archive HEAD` extract it **FAILS**
(`LiveLedgerWriteUnderTest` from `background/live_ledger_guard.py:207`), and copying in the shared
tree's *uncommitted* `tests/background/conftest.py` turns it green: the entry
`("background.process_run_complete", "LANDING_IN_FLIGHT_FILE")` is in the working copy and in
origin's copy, and **not at HEAD**. So the red is real at HEAD, already fixed on origin, and
closing the fork is what clears it. A green measured in the shared worktree measures several lanes,
and here it hid a live red behind one uncommitted line.

## 4. What landed

**The ceiling on the disjoint admission** — `background/process_run_complete.py`. The 2026-09-16
narrowing publishes while behind origin when origin's incoming paths are disjoint from ours, on the
premise that the reconciler absorbs it next cadence; its own docstring names the bound it does not
impose and delegates it to the [ORIGIN FORK] alarm. **An alarm is not a ceiling**, and path
disjointness confers no pushability — `git push` needs a fast-forward of origin's ref whatever the
commit touches. So `_unabsorbed_publish_commits` now asks `git rev-list --count FETCH_HEAD..HEAD --
<our paths>`: the first disjoint publish is the bet the narrowing exists to allow, and a **second**
is evidence the cadence is not running. `FETCH_HEAD` not `origin/main`, for the reason the sibling
control already pinned. Unreadable counts refuse rather than reading as zero.
`_our_publish_paths` is extracted rather than cloned so the ceiling and the disjointness test ask
about the same surface.

**Two controls, both mutation-proven in an isolated extract** —
`tests/background/test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py`:

* `test_one_disjoint_publish_is_admitted_and_a_SECOND_unabsorbed_one_is_REFUSED` — one control over
  the whole partition, one fixture, one variable. `if stranded:` → `if False:` reds it; a constant
  non-zero count reds the other half. Neither arm passes a constant.
* `test_an_unreadable_unabsorbed_count_refuses_rather_than_reading_as_zero` — `return None` →
  `return 0` reds it. Its first draft stubbed `rev-list --count` broadly and graded the UNREADABLE
  exit instead of the new leg, because the ahead-count uses the same subcommand in the other
  direction; it is keyed to the range string now, and the docstring says so.

## 5. The fork: resolved, and the resolution landed by the ordinary door

**Three conflicts, not two.** The two above were measured against `origin/main` = 6c1e769b4. While
this turn ran, another lane's rescue of the stranded weather store landed **directly on origin** as
6e02d6442 — the shared tree's HEAD never moved — and added a third conflicted path,
`tools/build_weather_world.py`. Re-measuring the conflict set after every origin move is not
optional: a resolution prepared against a stale tip resolves paths that are no longer the ones in
dispute, and `surgical_land --resolve` refuses a resolution for a path that did not conflict.

**Origin's version wins all three**, because in each it strictly contains the local one: origin's
liveness fixture models
`git merge-base --is-ancestor` explicitly with `is_ancestor` defaulting to False and a refusing
catch-all (the local commit `a7f9abaad` did the same repair identity-only, in eight lines), and
origin's validator suite is the local file plus
`test_a_leg_NOT_ASKED_FOR_is_never_counted_as_a_pass_either` and one extra assertion over a
`tools/validate_weather_world.py` that is byte-identical on both sides; and `build_weather_world.py`
differs by eight lines of origin's own docstring correction. **Nothing local is lost, and the local
side is not dropped either** — it carries five commits of real work alongside the four unpushable
publisher duplicates, so a merge is the only move that keeps the work and ends the duplication.

Landed by `python3 -m tools.surgical_land --merge origin/main --resolve <path>=<bytes-outside-the-repo>`
×3, run inside `origin_reconcile`'s own isolated worktree via its own `_fresh_worktree`, so the
shared index is never opened. The wait was real and is worth recording: two concurrent
`surgical_land` runs kill each other, and another lane held one on the shared tree for most of this
turn.

**One step remains after this and it is NOT the merge's fault.** The shared tree still will not
fast-forward to the merge until the ten superseded working copies in §2 are cleared — that is the
step `origin_reconcile`'s blocker list is actually about. All ten are recoverable byte-for-byte
with `git show origin/main:<path>`, six are already byte-identical to it, and the three that differ
have origin strictly richer. Until then the shared tree serves a HEAD that origin has moved past,
and the next lane to land from it opens the fork again.
