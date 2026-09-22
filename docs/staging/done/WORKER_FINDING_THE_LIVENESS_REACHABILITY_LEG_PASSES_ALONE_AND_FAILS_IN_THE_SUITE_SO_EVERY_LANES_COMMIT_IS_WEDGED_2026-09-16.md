**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# FINDING: the liveness push-verdict leg passes alone and fails inside the suite, so the commit gate is wedged for every lane

Worker seat, 2026-09-16, found while landing `make-the-per-cell-weather-store-reproducible`. Two
full gate cycles (~11 minutes) were spent on it before it was established as not-mine.

## The refusal

`tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line.py::test_every_refusing_exit_records_and_they_do_not_all_say_the_same_thing`

```
AssertionError: push_never_landed must be a refusal, or this leg is grading the success path
assert True is False
```

**1 failed, 1016 passed** — the gate refuses the commit, and it refuses it for whatever paths are
being landed. Nothing in the landing touched `background/`.

## It is order- or state-dependent, not a plain red

| how it is run | verdict |
|---|---|
| the single test, by node id, in the shared working tree | **passes** in 0.06 s |
| the same test inside the commit gate's full-suite run | **fails**, reproducibly, twice |

So it is not red at HEAD in the ordinary sense and `red_at_head` will not establish it. Something
the suite leaves behind changes the answer — this is the test-pollution wedge class, arriving
through a test that reads REAL repository state.

**AND THE DIRECTORY IS ORDER-SENSITIVE IN BOTH DIRECTIONS, WHICH IS STATED HERE RATHER THAN
ROUNDED OFF.** Running `tests/background/` on its own — with the landing's two new files in
`tests/tools/` not collected at all — produced **three failures by 32% of the run**, where the
gate's full-suite run over the same tree produced exactly **one**. So the directory alone is not a
clean control either: it is not the case that "background is simply red", and it is not the case
that the gate's single red reproduces by running its directory. Both facts are consistent only
with leaked state, and neither on its own names the leaker. What IS established: the landing
touches no file under `background/`, and the failing leg's subject changed today.

The next session should bisect with `-p no:randomly` and `--deselect`, not re-run the pair and
hope — two runs of two populations have already been spent proving only that the population
matters.

## The evidence that it reads real state

The captured stdout of the failing run is not stub output. It is the live log:

> `[process_run] Liveness heartbeat is behind origin (origin/main is 23 commit(s) AHEAD of HEAD ...)`
> `[process_run] Liveness heartbeat published to origin.`

That last line is the SUCCESS path, emitted during the `push_never_landed` leg — the exact leg
whose whole purpose is to refuse. Meanwhile the real divergence at the time of writing is **behind
2, ahead 1**, not 23, so the number in the log is neither the stub's nor the tree's present state.

## The likely cause, and why it is someone's live work

The fake in `_drive` carries a comment dated **2026-09-16 — today**:

> "AS PERMISSIVE AS ITS SUBJECT AND NO MORE (2026-09-16). The push verdict now asks REACHABILITY,
>  so this fake acquired a new subject; the rc=0 fall-through below answered 'yes, reachable' to
>  every question and graded the `push_never_landed` exit as a success."

The fake now answers `git merge-base --is-ancestor` with `0 if argv[3] == argv[4] else 1` and
falls through to `rc=0` for everything else. **If the subject under test reaches the verdict by any
call the fake does not match, the fall-through grades it a success again** — which is precisely
the defect that comment says was just fixed, reappearing through a different call. That is a
same-day change to the push verdict whose fake and whose subject are not in step.

This is the recorded shape [[a fake more permissive than its subject turns a fail-open into a green
suite]], except here it inverts: alone the fake is tight enough, and in the suite the subject
reaches a different call.

## Why it is filed rather than fixed

It is H_harness's subject, that lane already carries five BLOCKING findings, and the change that
introduced it is dated today and may still be in flight in another session's working tree. A
second lane editing `background/process_run.py` or its fake mid-change would collide.

## What it costs until it is fixed

**Every lane's commit.** The gate runs the whole suite against the tree the commit would create,
so this one leg refuses every landing in the shared tree regardless of pathspec. One completed
piece of work (`tools/build_weather_world.py` repair, `tools/validate_weather_world.py`, 15
mutation-proven controls, all gates green, orphan ratchet frozen on the record) is sitting
untracked behind it.

## The remedy

Establish which call the subject makes that the fake does not match, and make the fall-through
**refuse** rather than succeed — a stub with no commit graph cannot honestly claim reachability, so
the default must be "not reachable", not "reachable". Then assert the leg fails when the fake is
made permissive again, so the fall-through cannot silently return.

---

## DISCHARGED 2026-09-17 (worker, lane 0) — and two claims above are corrected beside themselves

**The remedy asked for was already written and sitting uncommitted on disk**, in this file's own
fake, mtime 2026-09-16 19:46. It is the `merge-base --is-ancestor` arm: identity is the only
ancestry a stub with no commit graph can honestly claim, so the fall-through now REFUSES rather
than succeeds — the remedy this finding specified, arriving from the same lane that filed it.
Landed now.

**CORRECTION 1 — it is red at HEAD, and the table above has it backwards.** This finding states
*"it is not red at HEAD in the ordinary sense and `red_at_head` will not establish it"*. Measured
2026-09-17: the single test ALONE in a clean `git archive HEAD` extract **fails**; the same test
alone in the shared working tree **passes**. The shared tree is what made it pass, because the
repair was already on disk there and every run picked it up. There is no order-dependence and no
leaked state to bisect for — `red_at_head` could not establish it only because it was being
measured in the tree that already carried the cure.

**CORRECTION 2 — "may still be in flight in another session's working tree" was the reason given
for filing rather than fixing, and it was the one thing that made this cost five days.** The hunk
was four and a half hours cold and complete. The class is worth keeping: *a finished repair on disk
looks identical to a repair in flight, and mtime is the cheap question that separates them.*

Attribution is a one-variable swap into the parent tree — HEAD plus only those eight lines:
**1 failed → 14 passed.** Nothing else was needed and nothing else was changed.

Evidence and the full account, including a prediction of mine about this finding that was made and
then refuted: `WORKER_RESULT_THE_SEVENTEEN_REDS_WERE_ONE_LEAKED_CONSTANT_AND_THE_SECOND_LEG_HAD_ALREADY_LANDED_2026-09-17.md`.
