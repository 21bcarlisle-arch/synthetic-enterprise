**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `the-orientation-brief-misreports-the-machine-it-describes`

# The shape reader called twelve heartbeats work, and the brief never saw the box

Two repairs to the seat's own instruments, landed together because they are one subject: the
orientation brief was wrong about the machine it describes, in the commit stretch and on the box.

---

## FIRST: a commit whose only content is the proof it is alive

### The premise held, and the measurement is what it rests on

The drawn item said `_carries_work` reads a liveness-pair commit as work. Measured on this tree at
draw time, over the last 60 commits:

```
count 60   carrying_work 59   shape_is_wrong False   findings: (none)
liveness commits in stretch: 12   all carries_work True? True
```

Twelve of sixty — a fifth of the stretch — were `chore(liveness): publish heartbeat while sim
output unchanged`, touching exactly `docs/observability/agent_status.json` and
`site/data/tick_heartbeat.json`. Every one read as WORK, and the instrument whose entire job is to
notice an empty stretch reported a clean one.

### Why all three existing legs missed it, which is the part worth keeping

* The **tree rule** passes it correctly. A heartbeat really does change bytes, so the tree really
  does differ from the parent's. Structural, right, and blind here.
* **REPETITION never fires**, and this is the one I had to measure rather than assume: the subject
  embeds the publishing commit's hash, `... (git=f8a54c985) ...`. **Twelve heartbeats carry twelve
  DISTINCT subjects.** The leg that caught the 29 empty merges by their identical titles cannot
  see these at all.
* **METRONOME** rides on REPETITION's runs, so it is never asked.

### The rule now

> A commit carries work IFF its tree differs from every parent's **AND** its whole diff, against
> every parent, is NOT confined to the declared liveness surface.

**Keyed to the property, not to today's two filenames.** The surface is read from
`process_run_complete.LIVENESS_SURFACE_FILES` — the publisher's own declaration of what it commits.
A third liveness file must be declared there in order to be published at all, so this reader picks
it up without being touched. A private copy of the pair here would have been a second hand-typed
answer that goes stale in silence.

If that declaration cannot be read the stretch is **not cleared**: an UNREADABLE finding says so,
rather than falling back to the flattering answer. An empty declaration is `None` ("we do not know
the surface"), never `frozenset()` ("the surface is nothing") — the second reports the declaration
as KNOWN and clears the stretch.

### A PREDICTION I FILED BEFORE MEASURING, AND IT REFUTED THE ITEM'S REMEDY

The item asked me to *"let `findings()` name a run of them as it already names a metronome"*. I
pre-registered that the heartbeats would be **scattered**, not consecutive, and that a run-only
finding would therefore not fire on the live case. Measured:

```
positions: [23, 24, 26, 28, 29, 32, 34, 39, 43, 46, 50, 56]
consecutive run lengths: [2, 1, 2, 1, 1, 1, 1, 1, 1, 1]
```

**Longest run: 2.** Below any threshold worth having. The run finding was built anyway — it is the
loop detector, and a daemon spinning produces exactly a consecutive run, which is the disaster the
module exists for — but **on its own it would have been a control that could not fire on the
defect that motivated it.** The count leg carries the live case and states the run's absence in its
own sentence.

`NO_WORK`'s detail was also wrong once heartbeats reach it: it asserts *"each tree is identical to
one of its own parents"*, which is false of a commit whose tree genuinely differs. Rows now carry
`empty_because`, and the sentence is only stated where it is true. Same repair to the seat prompt's
own gloss on `!!`.

### After

```
count 60   carrying_work 47   liveness_only 12   shape_is_wrong True
LIVENESS_ONLY 12 | 12 of 60 commits in this stretch changed only the liveness surface...
```

0.17s for the whole reading.

---

## SECOND: the brief now states what is on the box

`build_brief` carries `running`, and `_prompt` states it as a **sentence above the JSON and outside
its 60k truncation** — the same lesson `rendered`, `previous_wrong` and `focus_drawn_never_landed`
each had to learn separately. A fact the seat must dig out of 60k of JSON is one it digs out on a
quiet stretch and skips on a busy one, which is exactly when the box has a job on it.

```
WHAT IS ON THE BOX RIGHT NOW, with the 10 declared permanent daemons subtracted so the
jobs are not buried. DO NOT LAUNCH SOMETHING THAT IS ALREADY RUNNING:

   4073589    29m02s    512.3MB  claude
   4172305     3m30s     46.5MB  tools.surgical_land
   4172397     3m28s    191.8MB  tools/pre_commit_test_gate.py
   4173904     2m58s    677.0MB  pytest
```

**The subtraction is the whole design.** The stated insufficiency for this reading was *"lists
every python process including the four permanent daemons, so the one long job that matters is
buried"* — and the daemons are the **longest-lived** things on the box (days, against a job's
minutes), so any sort by elapsed puts every one of them above the row that matters. They are
subtracted using `process_manifest.yaml`, the single declaration of what should be running, through
the token match `process_reconciler._runs_daemon` already got right. A daemon added tomorrow is
added to the manifest because nothing starts it otherwise, and stops appearing here for free.

"Nothing long is running" is a **positive statement**: only true when `ps` actually ran. An
unreadable box says `WHAT IS RUNNING COULD NOT BE READ`, because the consequence of reading "idle"
when the truth is "I could not tell" is the seat launching a duplicate of a job already in flight —
the seventeen-hour duplicate floor run is the precedent.

No scheduler, no lock, no contention register: one reading, in a brief that already prints six.

### TWO DEFECTS THE BUILD FOUND IN ITSELF, both caught by measuring rather than reasoning

1. **A sibling `claude -p` seat was named `tools.surgical_land`** on the first live run — because
   its *prompt* recites `python3 -m tools.surgical_land` as the instruction for how to land.
   Scanning every argv token for `-m` reads a process that MENTIONS a module as one that RUNS it:
   **the identical defect `_runs_daemon` exists to refuse, reached again from a different
   direction, one file away from the comment describing it.** The scan now requires a python
   interpreter and stops at its first non-option argument.
2. **`_project_namespaces` required `__init__.py`** — and every top-level package here is a
   *namespace* package. It found exactly `company` and `tests`, so `python3 -m background.anything`
   was dropped from the reading entirely, and the live box only looked right because one long argv
   happened to also mention a file path. Caught by my own test, not by the live run that preceded
   it.

---

## Controls, and the eight mutations that prove they can fail

Extended, not minted: `test_a_daemon_producing_empty_merges_lit_up_every_liveness_surface.py`
(19 pass) and `test_a_stretch_that_committed_and_changed_nothing_is_a_finding_not_silence.py`
(17 pass).

Each half carries **one assertion over the whole partition**, because a guard that calls every
stretch empty — or every box idle — passes every per-branch test written for the other side:

* a synthetic heartbeat stretch plus one real commit reads one carrying work AND the shape wrong,
  **and** a genuine stretch still reads clean, in one test;
* a box with a long job is seen AND an idle box says so positively, in one test.

Mutations run in a scratch extract under `~/.cache`, never on the shared tree. All eight fire:

| # | Mutation | Red |
|---|---|---|
| 1 | hard-code today's two filenames instead of reading the producer | `...NOT_A_COPY_OF_TODAYS_TWO_NAMES` |
| 2 | let an empty path set count as liveness-only | 6 red, incl. `THE_NO_OP_MERGE_CARRIES_NOTHING` |
| 3 | call every stretch empty | 4 red, incl. the partition test |
| 4 | unreadable declaration returns an empty surface silently | `...DOES_NOT_CLEAR_THE_STRETCH` |
| A | drop the declared-daemon subtraction | `...THE_ONE_JOB_THAT_MATTERS_IS_BURIED` |
| B | scan every token for `-m` | 3 red, incl. `...MERELY_MENTIONS_A_MODULE` |
| C | an unreadable box reports itself as idle | `...NOT_REPORTED_AS_AN_IDLE_ONE` |
| D | the running sentence lives only inside the JSON | `...OUTSIDE_ITS_TRUNCATION` |

**Mutation 4 was silent on its first run, and that was a missing test, not an equivalence.** The
unreadable-surface test monkeypatched `_liveness_surface` to return `None` — so it never executed a
line of the function it was written about, and passed under the exact mutation it names. It now
breaks the import via `sys.modules` and drives the real function. Recorded here rather than quietly
fixed, because the flattering reading of a silent mutation is the one this project keeps paying
for.

Two other fail-open traps were closed during the build and each has its own leg: `diff-tree` prints
a **merge's sha with no paths under it**, so a naive `paths <= surface` would have called every
merge in the tree liveness-only (an empty set is a subset of everything); and the liveness leg can
only ever take an answer *away* from "work" — it can never promote a commit the tree rule refused,
and never overrides an honest `None`.

---

## What I did NOT do, and why

`tests/architecture/test_static_quality_ratchet.py` is red on `I001: 1307 != 1308` and
`test_seat_guard_daemons.py` is red on `hook_chain_room_watch.py`. **Neither is mine and I left
both.** Verified rather than assumed: my four files are I001-clean in their HEAD versions *and*
now, extracted and checked separately, so my diff cannot move that count; and
`background/hook_chain_room_watch.py` is untracked, dated 09-17, in no pathspec of mine. Both are
the whole-tree-census class already filed as
`WORKER_FINDING_A_WHOLE_TREE_CENSUS_REDS_EVERY_LANE_FOR_A_NAME_ITS_OWN_AUTHOR_NEVER_SEES_2026-09-19.md`.

## Still owed

The `LIVENESS_ONLY` run leg has **never fired on real data** — the longest live run is 2. It is
justified by the 29-empty-merges shape rather than by anything observed since, and it should be
treated as unproven on this tree until a stretch produces a run of three. The count leg is what
carries the live case today.
