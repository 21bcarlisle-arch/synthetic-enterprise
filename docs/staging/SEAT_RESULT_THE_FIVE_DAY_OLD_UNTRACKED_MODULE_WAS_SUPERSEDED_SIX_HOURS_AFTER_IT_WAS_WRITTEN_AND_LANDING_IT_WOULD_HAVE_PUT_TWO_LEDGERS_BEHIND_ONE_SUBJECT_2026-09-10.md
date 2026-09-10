**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `two-always-run-ratchets-are-red-because-a-finished-module-never-left-the-working-tree`) · **Class:** uncommitted_and_orphaned_work

# RESULT — the five-day-old untracked module was superseded six hours after it was written, and landing it would have put two ledgers behind one subject

The Lane 0 item offered two exits: **LAND** the pair (guard the entrypoint, call `live_ledger_guard`
from `save`) or **DELETE** both and say why five days of work is not wanted. This is the record for
the second exit. It was not a preference between two workable options — the first exit is not
available, and the measurement below is why.

---

## 1. The item's premise was right about the ratchets and wrong about the module

Both untracked files were exactly where the item said, at the size and mtime it said:

```
background/standing_red.py        20,035 bytes  2026-09-05 16:31   untracked
tests/background/test_standing_red.py  19,701 bytes  2026-09-05 16:31   untracked
```

`git ls-files --error-unmatch` refused both; `git archive HEAD` contained neither. They were the
sole reason `test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` failed `57 <= 56`
with `standing_red.py::save` in the list.

What the item did not know is that **the module was already superseded when it was drawn**, and by
something that landed the same day:

```
background/standing_red.py          20,035 bytes  2026-09-05 16:31   UNTRACKED
background/publish_standing_red.py  23,003 bytes  2026-09-05 22:09   TRACKED, landed at b6d9cd49d
```

Six hours and eight commits apart, same subject: a standing-red ledger for the publish path.
`publish_standing_red` is wired into the publisher at `background/process_run_complete.py:3590`
(`note_refusal`) and `:3613` (`note_landing`), at HEAD and at `origin/main` alike. `standing_red`
is imported by nothing that has ever landed.

## 2. The draft's own test suite says it is unwired, and it is right

Running it was the item's first instruction. Seventeen pass, three fail:

```
FAILED test_the_publisher_folds_every_named_refusal_into_the_ledger
FAILED test_the_publisher_folds_the_uncapped_subject_not_the_cited_one
FAILED test_a_clean_publish_retires_the_standing_red_through_the_publishers_own_edge
```

All three assert that `process_run_complete` folds refusals into **this** ledger. It does not — it
folds them into `publish_standing_red`'s. The three failures are not a bug in the draft; they are
the draft correctly reporting that its seam is occupied. There is no version of "land the pair"
that makes them green without first **unwiring the successor**, which the item did not ask for and
which nothing on the queue wants.

## 3. The one thing the draft has that the successor lacks is a compensation the successor does not need

This is the part worth writing down, because the draft's docstring makes a strong argument and the
argument is sound — about the draft.

`standing_red` keys its subject to **the failing SET, whole**. A set-keyed counter resets whenever
the set varies, and two reds alternating (A, B, A) would reset it every cycle and read `not
standing` forever while the publisher stayed wedged. That is a real R15 self-clearing shape, it was
caught by the self-clearing alarm census before the draft shipped, and the draft's answer was a
**second clock** — an episode counter guarded by `episode_monotonic`, reset only by a clean publish.
Two clocks, named apart, never summed. Good design.

The successor does not have that defect to compensate for. `publish_standing_red.record_refusal`
keys `cycles_blocked` **per test**, and the only discharge is `record_landing` — the hook chain
passing. Alternating reds accumulate correctly: A→1, B→1, A→2, and A is standing. There is no
resettable first clock, so there is nothing for a second clock to protect. `grep -n
"episode\|monotonic"` over `publish_standing_red.py` returns nothing, and that absence is correct
rather than a gap.

**The draft is the more complicated earlier answer to a problem the later module dissolved.** That
is the whole finding.

## 4. Landing it would have made the fork worse, and the register it renders is the proof

The lane had a third uncommitted piece the item did not mention: **105 insertions in
`background/head_red_register.py`** — `standing_verdict()`, `_standing_section()`, a `standing=`
parameter on `render()`, and a union into `drawable()`. Absent at HEAD and at `origin/main`; the
entire local diff of that file, no other lane's edits mixed in.

That code changes the bytes of `docs/staging/reference/HEAD_RED_REGISTER.md`. And that path is one
of the **three** untracked paths currently holding this checkout's fast-forward open (§ the
reconciler finding filed alongside this). Landing the draft would have permanently diverged a
machine-rendered register from origin's copy, in a lane whose whole complaint is a fork that will
not close.

The successor already publishes its own register (`PUBLISH_STANDING_RED_REGISTER.md`) and has its
own `drawable()` route into the draw. So the head_red_register integration was not merely
redundant — it was a **second surfacing path for one subject**, which is the shape CLAUDE.md names
as this project's most expensive recurring class: one requirement, several implementations, a fix
landed in one of them and still live in another, and nothing able to notice.

## 5. What was done

- Deleted `background/standing_red.py`, `tests/background/test_standing_red.py`, and the dead
  artefact `docs/observability/.standing_red.json` (37,466 bytes, last written 2026-09-08 — while
  the successor's `publish_standing_reds.json` was current at 2026-09-10 10:23, which is confirming
  evidence about which of the two is alive). All three were untracked, so the removal is a
  working-tree act and needs no commit.
- Removed the five `standing_red` hunks from `background/head_red_register.py` by targeted edit,
  **not** by `git checkout` — the file is byte-identical to HEAD again (`git diff` empty), so no
  dangling import is left for the next lane to trip over. Left in place, `standing_verdict()` would
  have caught its own `ImportError` and returned `{"standing": False}` forever: a fail-silent branch
  in a register, which is worse than either exit the item offered.

## 6. Grading — and the item's stated done-condition names the wrong base

`live_ledger_guard`, shared tree: **57 → 56, PASSES.** The bound was not raised; it was not touched.
The ratchet's own message says widening the guard is the move that lowers the number — deleting an
unwired writer lowers it too, and costs nothing.

`test_every_main_entrypoint_is_guarded`, shared tree: **still red, and not because of this work.**
`standing_red.py` is gone from its list. What remains is exactly nine:

```
commit_narrative, doomed_at_teardown, head_red_register, launch_liveness,
launch_long_job, long_job, origin_reconcile, publish_standing_red, weekly_rhythm
```

Those are the nine `fcbf92b9b` repaired. **`fcbf92b9b` is an ancestor of `origin/main` and is NOT an
ancestor of HEAD** — this checkout is 12 behind. Each of the nine carries `refuse_if_foreign` at
`origin/main` and none carries it at HEAD, checked file by file.

So the item's done-condition — "both ratchets green in a clean HEAD extract" — **cannot be
satisfied at HEAD and should not be.** A HEAD extract is missing the repair. The right base is
`origin/main`, and in a clean `git archive origin/main` extract:

```
tests/background/test_seat_guard_daemons.py::...::test_every_main_entrypoint_is_guarded  PASSED
tests/background/test_live_ledger_guard.py::...::test_the_..._measured_not_assumed        PASSED
2 passed in 1.25s
```

Both green at the base that has the repair, with the draft deleted. The shared tree's remaining red
closes when the fork closes, and a gated `--merge origin/main` launched by `origin_reconcile` was
executing while this was written.

## 7. What is next

- Nothing is owed on the standing-red subject. `publish_standing_red` holds it, wired and landed.
- The nine-entrypoint red in this checkout is a **fork symptom**, not harness debt. Any lane that
  meets it should check `git merge-base --is-ancestor fcbf92b9b HEAD` before touching
  `UNIVERSAL_MODULES` or a bound — the repair exists and is one merge away.
- The class question this instance belongs to is filed separately: the fast-forward is held open by
  machine-written artefacts, and the reconciler's clearing rule is all-or-nothing.
