**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The divergence-first repair blinded four sibling controls, and two of them were pinned to a sentence it rewrote

Found while clearing the publish gate's one cited red
(`the-one-red-the-publish-gate-cites-collapses-both-legs-of-its-own-discrimination`, landed
`697625722`). These are **four different reds, in a different file, standing at `origin/main`** and
in nobody's citation — found only because the neighbouring suite was run before landing.

`tests/background/test_a_refused_advance_names_the_paths_that_refused_it.py` — 4 failed, and they
are **two distinct causes wearing one symptom**, which is why the first repair took it from 4 to 2
rather than to 0.

## Cause one: a blanket `rc=1` fake, blinded by a correct production repair

`e89d05840` moved the divergence question AHEAD of the path judgement in `advance_shared_tree`
(line 1110) — the 2026-09-05 rule, and the right change: on a fork no working-tree path is the
cause, so naming one sends the reader at innocent files, which is what commissioned a seat to clear
four paths that were holding nothing.

It asks with `commits_ahead`, which shells `git rev-list --count origin/main..HEAD`. All nine sites
in the sibling file patched `orc._git` with `lambda *a, **k: CompletedProcess(returncode=1)` — a
**blanket refusal**. rc=1 is *"git would not answer"*, so:

* `advance_shared_tree` took its new `ahead is None` exit, and
* `_blocking_clause` took its `ahead is None` leg,

and four tests that assert what the **landing clause** says began grading a fail-closed exit two
branches upstream of it. **The reds named a sentence nobody had changed.**

This is the same class as the fifth publish-outage cause landed an hour earlier, in a different
module, found the same way: *a fake whose every answer is "could not" cannot tell "could not" apart
from any verdict downstream of it, and every leg in the file asserts on something downstream.*

**Repaired** by modelling the one question, at **0** — the number `_not_advanced`'s own
`state_fn=(3, 0)` already declares, so the fixture stops saying two things. Everything else still
refuses: *"a file is never deleted on a question that was not answered"* is the property the removal
legs are keyed to, and answering the twin hashes too would quietly license a deletion inside a test
about a refusal. Keyed to the exact range, so a caller asking `HEAD..origin/main` — the opposite
question, with the opposite remedy — falls through to the refusal rather than borrowing the answer.

## Cause two: two controls pinned to a sentence, going red because the code got MORE honest

With cause one cleared, two remained. They pinned the literal `"or by removing them"`, and
`1e204591e` had deliberately rewritten that step — because it was wrong. `FF_UNTRACKED` *means*
origin already brings a copy, so "land it" REPLACES origin's file rather than adding one, and the
orphan is routinely the older of the two. Measured on the live wedge: of three untracked blockers,
two were superseded drafts, and landing either would have reverted a landed correction — one of
which existed solely to retract its own earlier recommendation.

So the remedy now says to establish the direction first, and names the preserved ref that makes
removal lossless. **The control went red for the code becoming more honest** — CLAUDE.md's *"key a
control to the property, not to today's answer"*, precisely backwards, and the fourth instance of
that shape recorded in this repo.

**Re-keyed to `orc.ORPHAN_PRESERVED_PREFIX`**, read off the module rather than re-typed. It is the
MECHANISM the untracked door is — the bytes reach a preserved ref before they are cleared — so a
rename moves the control with it and a rewording does not touch it.

### …and the third one was asserting NOTHING

`test_the_modified_leg_names_the_hunks_door_and_NOT_the_untracked_one` was GREEN throughout. Its
negative leg, `assert "or by removing them" not in detail`, was pinned to the same dead literal —
**a negative on a string that exists nowhere is green however the partition breaks.** It was the
only leg standing between a modified-only hold and an untracked step leaking into it, and it had
stopped being a control the moment `1e204591e` landed. Re-keyed in the same pass.

## Mutation-proven, both directions

| Mutation | Result |
|---|---|
| untracked step stops naming the preserved ref | the untracked leg and the both-doors leg red; modified-only stays green |
| untracked step leaks into a MODIFIED-only hold (`if untracked or modified`) | the re-keyed **negative** reds — the leg that was vacuous before |
| `_refusing_git` reverted to the blanket `rc=1` | the original four reds return |

`background/origin_reconcile.py` was restored from backup after each; `git diff` on it is empty.
14 passed.

## What this says about the class

Both causes are **a control grading something other than its subject, while reading exactly like
the mechanism working**. Neither was in any citation. Neither would have been found by the publish
gate, whose selection is by subject module stem and did not reach this file. It took running the
neighbourhood of a change before landing it — which is the seat's own interconnection rule, and the
only thing in the architecture positioned to do it.

**The generalisable gap:** a production repair that inserts a branch AHEAD of an existing one
silently re-points every fake-driven control downstream of it, and nothing relates the two. Both
`e89d05840` and `1e204591e` were correct changes that left correct-looking reds in a file they never
named. A cheap check would be to run the test files that import a module whose control flow changed
— not a new register, one extra selection leg.
