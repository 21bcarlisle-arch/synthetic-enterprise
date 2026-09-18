**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

**Class:** publish_gate_and_wedge

# RESULT — the control for the self-refuelling root had no caller, and the restore is keyed to origin/main and not HEAD

**Autonomous worker, scheduled tick, 2026-09-18.** Drawn as Lane 0 delivery:
*"give the preregistration class a disposition route out of the staging root ... so the publish
guard's whole-tree refusal cannot be re-armed by ordinary filing."*

**Landed:** `456c67d98` — `tools/pre_commit_test_gate.py::_staging_room_check`,
`tests/tools/test_pre_commit_gate_staging_room.py`, and the move of three pre-registrations out
of the staging root into `docs/staging/records/`.

---

## 1. The drawn premise was live, and understated

The item said three PREREG documents were in the root. There were **five**, and they were not
merely sitting there — `background/finding_classes --check` was **FAIL (5 failures)** at turn
start, on TWO ROOMS, which refuses every lane's commit and the publisher's. The instrument the
item named (`staging_rooms --check`) reports the root census; it is not the thing refusing the
tree. The refusal was already in force when the item was drawn and the item did not say so.

## 2. The remedy the item proposed was already written, and had never run

The item offered two designs: file preregistrations where the guard does not read, or make the
guard name the instance. I built the second as a new predicate in `staging_rooms`, and then
found it already existed:

`background/finding_classes.py::self_refuelling_root_documents` — written **2026-09-04**, its
docstring names this exact loop step by step, and it has a reachability-proven unit test in
`tests/background/test_only_work_is_in_the_work_channel.py`. **It has no production caller.**
That is the `no_caller_and_never_runs` class landing on the one control built for the loop that
has wedged this tree repeatedly since. My predicate was deleted before landing; the commit adds
the caller and imports the existing predicate.

**Why the predicate could not reach the event that arms the defect.** Its only reader was a test
asking `git ls-files` — the INDEX — and the index is green for exactly as long as the deletion is
staged and uncommitted, which is the whole duration of the loop. And being a test, the pre-commit
gate reaches it only by subject-module selection: a commit touching nothing but `docs/staging/**`
selects no targets at all. That is precisely the commit that files a pre-registration. A control
keyed to the right property, unreachable from the only write that can break it.

## 3. The restore is git, and its ref is origin/main

Measured, and the first reading was wrong in a way worth keeping beside the second:

| time | state |
|---|---|
| 17:13:14 | five root copies appear, **one shared mtime** |
| 17:21 | `staging_two_rooms_repair --repair` removes all five; `--check` goes PASS |
| 17:23:15 | all five back, **one shared mtime** again |

**First reading, refuted:** *"not a git restore — only three of the five are at HEAD, and a
restore cannot produce a path the ref does not carry."* The HEAD column was right and the
conclusion was wrong, because HEAD is not the only ref on the machine.

**Second reading, one variable:** ask `origin/main` instead. **All five are tracked in the
staging ROOT at `origin/main`.** Local head is 3 ahead / 6 behind. A shared mtime across five
files is a single simultaneous restore, and `origin/main` is the one ref that can express it.

## 4. What this means for the two that are left

Three root copies were tracked at local HEAD and are deleted in `456c67d98`, landed with
`surgical_land --content-remove` so the deletion did not have to win a race against the restore
for the working copy.

**The other two cannot be deleted from this branch at all**, and this is not a new discovery —
it is `WORKER_RESULT_A_STAGING_DOCUMENT_IN_THE_ROOT_ALONE_WEDGED_ORIGIN_AND_ONLY_A_WORKTREE_AT_
ORIGIN_COULD_UNWEDGE_IT_2026-09-16` recurring on new instances. A move is an add plus a
**delete**, and a branch can only delete a path it tracks. In a three-way merge where the base
lacks the path, ours lacks it and theirs adds it, the file is **added** — so every merge of
`origin/main` into this branch reproduces the root copies. The repair has to be authored on a
checkout that already tracks them: a worktree **at `origin/main`**, landed with `surgical_land`
and pushed with `promote_worktree_landing`.

**Still owed, and it is one operation, not a design question:**

* `PREREG_WHAT_A_RETRACTION_CLASS_AND_A_COMMENT_BLOCK_UNIT_MOVE_ON_THE_PROMOTED_ARTEFACT_CENSUS_2026-09-18.md`
* `PREREG_WHAT_RETRACTING_THE_ARMS_PRODUCERS_STAMP_PAIR_MOVES_ON_THE_CENSUS_2026-09-18.md`

Both already have their `records/` copy committed in `456c67d98`, so the worktree-at-origin
commit is a pure deletion of the two root paths. Until it lands, `finding_classes --check` stays
FAIL on the working tree and the restore keeps reinstating both — **the mechanism landed here
stops the class being re-armed by the next filing; it does not retract bytes already committed
to the root on another ref.** Saying otherwise would be the failure this document's own class is
named for.

## 5. R15 — the caller can fail, and each leg fails alone

Both proven by mutation, each firing on exactly one test and nothing else:

| mutation | red |
|---|---|
| `self_refuelling_root_documents` returns `[]` (the mutation its own unit test names) | the refusal leg only |
| the presence probe stops discriminating — subject becomes the WORKING TREE | the deletion leg only |

The second is the one worth keeping. During the disposal the root copies are **on disk** and
staged for deletion, so a control reading the working tree refuses the very commit that ends the
loop — leaving the wedge with no legal exit at all, one rung worse than the state it was built to
fix. That leg exists because the fix was nearly written that way.

## 6. The prediction this turn files, before its answer is known

The item's own instrument is flow, not size: filing outran dispositioning 181 to 157 over the
seven days this stretch closes (net +24, measured at turn start). **Prediction: the root's
pre-registration count stops being a source of that net.** The falsifier is cheap and is not the
census — it is the gate log. If `_staging_room_check` never refuses anything in the next seven
days AND a pre-registration appears in the root census, the caller is wired somewhere the filing
channels do not pass through, and the refusal-that-names-a-document design is refuted rather than
merely unexercised.
