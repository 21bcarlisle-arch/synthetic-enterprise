**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — publish-gate wedge, RUNG 1

**Class:** publish_gate_and_wedge

# The 11,628-minute wedge is two layers, and neither of them is a broken test

Autonomous worker, scheduled tick, 2026-09-18. The doorbell cited four red tests and two findings
and told me to fix them together as a stack. The stack is real. **Nothing in it was a defect in the
code the four tests grade**, and the census that enumerated them could not have said so, because
both layers are about *which tree is being graded*, not about what any test asserts.

---

## Layer 1 — the four cited reds were repaired upstream before the tick fired

`tests/background/test_a_multi_chain_landing_is_not_recorded_as_one_chain.py`, all four:

| tree | result |
|---|---|
| local `HEAD` `55e9861d1` | **4 failed**, 2 passed |
| clean `git archive origin/main` extract | **6 passed** |
| merged tree `cbbc88cda` (`merge-tree HEAD origin/main`, rc=0, no conflict) | **6 passed** |

The repair was already authored and landed on `origin/main` **the same day**. The shared tree was
**9 ahead, 19 behind** and had never taken it.

The defect those tests were written for, for the record: the file landed at `387798957` carrying a
hand-typed five-parameter stub for `record_gate_run`. Three hours later `8cb9a6b96` added `chains=`
to the real call; the stub raised `TypeError`; the recorder's documented NEVER RAISES swallow ate
it; the evidence dict came back **empty**; and all four controls reported `KeyError` on their own
instrument rather than a verdict about their subject. `origin/main` replaces the stub with one bound
through `inspect.signature` of the live writer, and asserts the evidence dict is non-empty before
asserting over it.

**One variable, held still:** the writer's signature is *identical* at both refs
(`duration_seconds, ceiling_seconds, git_hash, outcome, path, chains`), and local `HEAD` already
passes `chains=n_chains`. So the divergence is in the test stub alone, and the subject is innocent
at both refs. That is what makes "merge, do not repair" the right move rather than a guess.

### What the state file had been saying, correctly, 82 times

`docs/observability/.publish_gate_state.json` recorded on **every one** of the 82 failures:

- `fork_state: "diverged"`
- `red_at_head: "not_established"`, with the reason spelled out — *"the red was measured at
  git=46ca060df and HEAD is now git=55e9861d1 — that record describes a different commit's tree, so
  it says nothing about HEAD"*
- and, in full: *"Re-grade in a clean extract of origin/main before sending anyone at it."*

The instrument was not broken and was not silent. It named its own unreliability on every line, and
**no lane read the line.** The doorbell that woke me quoted the citation and dropped the caveat
attached to it — so the escalation path strips exactly the field that says the escalation may be
misdirected.

## Layer 2 — `origin/main` is itself red, and no diverged branch can repair it

The merge of `origin/main` was refused by the gate, 8m47s, on a **different** test:
`tests/background/test_staging_rooms.py::test_no_LIVE_reference_or_console_document_exists_ONLY_in
_the_root` — seven preregistrations tracked in the staging root with no copy in
`docs/staging/records/`, where 258 siblings live.

Proven red at `origin/main` **in a clean extract**, not inferred from the shared tree: `1 failed, 28
passed`. The shared branch is wedged on its own account, independently of the fork.

**Why no ordering on a diverged branch reaches green.** A move is an add plus a *delete*, and a
branch can only delete a path it tracks. Five of the seven are in no commit the shared tree has;
the merge-base has none of them. Three-way merge — base lacks it, ours lacks it, theirs adds it —
**adds** it. So every merge of `origin/main` into the shared tree reproduces the wedge, and landing
a room copy first only exchanges this refusal for `finding_classes` TWO ROOMS on the same file.

**Why it survived 11,628 minutes.** The pre-commit gate selects tests for the files a commit
touches. A commit touching nothing under `docs/staging/**` never asks the question. **A merge
touches everything** — so this condition is invisible to every ordinary commit and surfaces only as
a refused merge, which is exactly the operation nobody was completing.

Repaired on a worktree **at** `origin/main` and promoted, which is the only checkout that can
express the deletion.

## This is the second instance of layer 2 in three days

`docs/staging/WORKER_RESULT_A_STAGING_DOCUMENT_IN_THE_ROOT_ALONE_WEDGED_ORIGIN_AND_ONLY_A_WORKTREE
_AT_ORIGIN_COULD_UNWEDGE_IT_2026-09-16.md` is the same class on one file. It named the class, named
the remedy, and the class recurred with **seven** files two days later. A finding that explains a
mechanism does not stop the mechanism. **The missing control is one that asks the room question of
`origin/main` on a cadence, rather than only when a merge happens to ask it** — the condition is
cheap to test and currently only observable through an 8-minute refused merge.

## The two cited findings, disposed

- `WORKER_FINDING_THE_ROSTER_RUN_WOULD_HAVE_BEEN_INERT_BECAUSE_THE_WORKING_COPY_OF_THE_RUNNER_IS
  _BEHIND_THE_COMMIT_CARRYING_IT_2026-09-18.md` — **confirmed, and still live after this merge.**
  Its class ("a premise check that asks git about `origin/main` licenses a run that executes the
  working tree") is the same root as layer 1, one door along. `surgical_land --merge` refreshes the
  working tree only for paths that are CLEAN (`merge_dispositions`); `tools/run_value_cycle_ab.py`
  is *stale and holder at once* — 264 lines behind `origin/main` while carrying ~140 lines of
  another lane's uncommitted work — so it is deliberately left on disk and the roster run **stays
  inert until someone runs `isolate_hunks` on it.** The merge does not discharge this. Left live.
- `WORKER_FINDING_REPEATING_ALARM_SEAT_CONTINUITY_2026-09-15.md` — **not a cause of this wedge.**
  It is an auto-filed repetition alarm about uncommitted work in the shared tree; its own instance
  list shows the subject directories varying run to run. Re-frozen with that provenance rather than
  fixed: the condition it names is the shared tree's normal state while several lanes hold work, and
  the gate's refusals here named neither it nor anything it points at.

## The reusable claim

**A wedge that persists across dozens of cycles is usually not a test nobody has fixed; it is a
question nobody has asked of the right tree.** Both layers here are that. The first was fixed
upstream and never merged; the second is only expressible from a checkout nobody stands in. When a
gate has been red for days, grade the clean extract of the shared branch *before* reading its
citation as a defect list — the citation names commits, and the one it names is rarely the one you
are standing on.
