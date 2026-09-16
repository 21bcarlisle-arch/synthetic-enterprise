**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `commit-or-untrack-the-head-red-artefacts-so-a-clean-worktree-stops-reading-830`) · **Class:** controls_that_cannot_fail

# RESULT — the head-red observation is machine state, and untracking it in place would have wedged every lane

Pre-registered before measurement:
`docs/staging/records/SEAT_PREREG_WHETHER_UNTRACKING_THE_HEAD_RED_OBSERVATION_TURNS_A_FALSE_830_INTO_A_FALSE_ZERO_2026-09-10.md`.
All four predictions held. The prereg's own **refutation check** is what changed the implementation,
and that is written up below rather than quietly folded in.

## The premise was live, not spent

The item cites `b7fcbfed6`, already an ancestor of `origin/main`, so the premise had to be
re-measured. It stood:

| | this isolated worktree (clean HEAD) | shared tree |
|---|---:|---:|
| `head_red_register.drawable()` | **830** | **43** |
| runs in `head_red_observed.json` | 1 | 10 |
| latest row | `2026-09-02T04:30:02`, `passed: null`, `OSError x760` | `2026-09-10T03:46:53`, `passed: 33697` |

And the two tracked files disagreed **with each other**: the JSON (committed `bc57c8e30`,
2026-09-02) said 830; the register rendered *from* it (committed `108ff5a68`, 2026-09-05) said 21.
A derived file and its source cannot drift when both are generated together — so the drift is
itself the proof they were being committed independently, by hand, at different times. That is the
finding, not a detail: **these were never artefacts, they were state someone kept committing.**

## The decision

**The observation is machine state. The acceptance list stays tracked.** The module already drew
this line and we had simply not honoured it in git: `record()` is machine-written on every census
run, while `head_red_baseline.json` says *"NOTHING WRITES THIS FILE AUTOMATICALLY"* and is written
by a person. Three properties, each independently sufficient:

1. a machine writes it, unattended, on every run;
2. `del runs[:-MAX_RUNS_KEPT]` — **it deletes its own history to a rolling 30 rows.** A file that
   truncates itself is a cache, not a record;
3. it describes one machine, at one HEAD, on one night. A checkout inherits it as established fact,
   which is precisely how the 830 got authority it never earned.

## P1 held, and the fix is bigger than the item asked for

**A bare `git rm --cached` would have made this worse, not better.** `load_observed()` returns an
empty store for a missing file, `owed()` returns `[]`, `drawable()` returns `[]`, and
`staging_rooms._with_the_head_red_register` **drops the register from the queue entirely** when
`drawable()` is empty. Measured with the store moved aside: `drawable() == 0` and the register
absent from a **314-item** queue, with nothing anywhere naming the absence.

So the obvious fix converts a false-loud 830 into a false-silent 0 — the failure
`load_observed`'s own docstring names: *"It can never read as 'nothing is red', which is the
failure that would matter."* Both are the store speaking with unearned authority; only the
direction differs, and the silent one is worse.

The fix is a **named third state**: `UNOBSERVED`, distinct from OBSERVED-with-nothing-owed. Both
are zero and they mean opposite things. `render()` alone had the branch (`if not runs`), so the
document could say it while the DRAW and the DOORBELL — the two things that decide whether a person
ever looks — were blind to it.

## THE REFUTATION CHECK IS WHAT CHANGED THE IMPLEMENTATION

The prereg asked what would refute the decision, and the answer that came back was not the one it
anticipated. Nothing requires these paths to be *tracked* (the existing tests monkeypatch them to
`tmp_path`). But **the shared tree holds both paths dirty** — 1498/837 and 69/30 lines against HEAD
— and a commit that deletes a path whose worktree copy is dirty does not delete it:

```
error: Your local changes to the following files would be overwritten by merge:
        docs/observability/obs.json
Aborting
```

Reproduced end to end in a scratch clone before choosing: `git pull --ff-only` returns **rc=1** and
the tree stays **behind origin**. Landing the obvious untrack would have wedged every lane's
fast-forward — the exact publishing wedge this project keeps paying for, introduced by the commit
that was supposed to clean something up.

**So the path moved instead.** The live store is now
`docs/observability/.head_red_observed.json` — untracked, gitignored, dot-prefixed like every other
machine-state file in that directory. The legacy tracked path is left **strictly alone**: not
deleted, not rewritten, not gitignored. Nothing writes it from now on.

### Which needed one more rule, and it is not a new judgement

Abandoning the legacy store outright would have reset every `runs_red` to 1 on the shared tree —
destroying the ages, which are the whole signal the new doorbell clause carries. So the legacy path
is read **read-only, and only if credible**, where credible reuses the rule `record()` already
enforces: *at least one run row with a pass count*, because a pass count is the proof a run
happened.

One rule, opposite and correct answers in the two trees, neither a special case:

- a clean checkout's legacy copy holds one row, the wreck, `passed: null` → **refused** → UNOBSERVED;
- the shared tree's holds nine further rows with real pass counts → **adopted**, ages intact, still
  43 owed because those later runs already marked the wreck's 830 entries `currently_red: False`.

Measured in both: clean worktree `drawable()` **830 → 0, state UNOBSERVED**; shared tree
**43 owed, worst 10 runs since 2026-09-02** — P4 held, the real draw is untouched.

## P3 held — the doorbell now carries the count and the age

The register was surfaced ~3,421 times and drew nobody. Not because anything was silent: every
layer ran, nightly, by test id, with ages computed. It was the **6th of 132** comma-separated
filenames in one doorbell line, carrying no count, no age, no severity — and it is *structurally
permanent* ("do not archive it"), so a never-removable name sat in a list whose whole read is *a
backlog to be drained*. That is furniture.

`render()` already computed `worst`, the longest-standing red's run count, and dropped it on the
floor. It is now lifted into `summary()` and rendered:

```
before: unprocessed staging -- CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md, CLASS_CONTROLS…,
        CLASS_UNCOMMITTED…, CLASS_NO_CALLER…, CLASS_FIGURES…, HEAD_RED_REGISTER.md, SEAT_FINDING…

after:  HEAD_RED_REGISTER.md: 43 owed, longest-standing red has stood 10 consecutive census run(s)
        since 2026-09-02 (observed 2026-09-10); unprocessed staging -- CLASS_PUBLISH_GATE…
```

Measured on the real feed, not a fixture. The clause sits **outside** the comma-join, and that was
a correction mid-build: placed inside it, its own commas read as three more list entries — the same
anonymity in a longer form.

The one silent case is OBSERVED with nothing owed, which is the only case where silence is true.

## Controls

`tests/background/test_the_head_red_observation_is_machine_state.py`, 13 tests. Every one
poison-proven reachable before being believed — nine mutations run, each firing:

| mutation | fires |
|---|---|
| `observation_state` always OBSERVED | 2 |
| drop `worst_runs` from the clause | 1 |
| `find_work` reverted to the bare blob | 1 |
| clause built only when the name is already in `staged` | 1 |
| the live store gets committed | 1 |
| drop the credibility filter (adopt any legacy store) | 2 |
| remove the legacy fallback (abandon the ages) | 1 |
| point the live store back at the legacy path | 3 |

Two traps caught in the writing and worth keeping:

- **the wiring leg.** Two tests call `_differentiated_staging` directly and are blind to whether
  `find_work` uses it — reverting that one line left both green. Now asked over the AST, because a
  mention in a docstring is not a call.
- **a tree-dependent control.** `test_an_absent_store_reads_UNOBSERVED_and_not_green` patched
  `OBSERVED_PATH` but not the legacy path, so it was green here by luck (wreck refused) and would
  have gone **red on the shared tree** (credible store adopted). A control whose colour depends on
  which worktree ran it is not a control. Verified green under both conditions after the fix.

## What is NOT done, and the named remedy

**The two legacy tracked files still sit at HEAD saying 830 and 21.** Nothing reads them for the
draw any more and nothing writes them, but they are stale bytes a reader can still open.

They could not be removed in this turn without wedging the shared tree, and the remedy is a
**two-step that must run on the shared tree, not from an isolated worktree**:

1. commit the shared tree's current working-tree content for both paths — this makes them *clean*,
   which is the only condition under which the next step merges anywhere;
2. `git rm --cached` both, in a following commit. With a clean worktree copy everywhere, the
   deletion fast-forwards instead of aborting.

Doing step 2 alone, from anywhere, wedges every lane. That is the trap this turn walked up to and
measured rather than stepping into, and it is why the note is here rather than in a commit message
nobody re-reads.
