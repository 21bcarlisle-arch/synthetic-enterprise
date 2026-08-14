# WORKER FINDING — a finding recorded its own instance as FIXED, the fix had never been committed, and that sentence bought the wedge another 30 failures

**Severity:** BLOCKING · **Lane:** H_harness
**class:** uncommitted-and-orphaned-work
**found:** 2026-08-14, unwedging the publish gate (244 consecutive failures, ~7,086 min)
**status:** CORRECTED 2026-08-14 — this line previously read "INSTANCE FIXED (the supplier half is
now at HEAD, this tick)" and was itself FALSE, which makes this finding a second instance of its own
subject: it documented the false-FIXED mechanism in a sentence that was a false FIXED. The supplier
actually reached a tree in `c78b7a118`. Verified by `git log -S`/`git ls-tree`, never by `git status`.
CLASS OPEN — and this is
now the *third* instance of the mechanism in three days, the first two of which were also closed
with prose rather than a control.

## What was observed (observed-with-evidence)

`WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED_2026-08-14.md`
opens with:

> **status:** INSTANCE FIXED (the supplier half landed). CLASS OPEN

and closes with a "What landed this tick" section listing `atom_name` + `name` in `NOTE_FIELDS`,
297 store docs, four site generators, `tools/migrate_atom_names.py` and the facets test — *"Landed
with `tools/surgical_land`"*. The sibling finding written the same hour
(`/tmp/finding_surgical_land_tmpfs.md`, filed alongside this one) repeats it: *"the wedge's cause
was the uncommitted `name` drain (landed this tick)"*.

None of it was at HEAD when this tick began:

```
$ git log -S "def atom_name" -- tools/simplifications_store.py
                                        <- no output: never committed, at any commit, ever
$ git status --porcelain -- tools/simplifications_store.py
M  tools/simplifications_store.py        <- still in the INDEX, still not in a tree
```

And the gate said so, unchanged, for another 30 cycles. Reproducing the publish gate against the
tree a commit *would* create (`tools/surgical_land`, which is exactly that subject):

```
tests/background/test_publish_gate_subject_is_head.py:1379: in _ops2_exit_text
    text = _store.atom_name(found[0])
E   AttributeError: module 'tools.simplifications_store' has no attribute 'atom_name'
```

— the identical red the live cycles had been logging since `19d8f94da`.

## Why it matters more than an ordinary false-completion

This is not just [[feedback_the_record_can_outrun_the_code]] with a new instance. The record that
outran the code was **the finding whose entire subject is that a commit landed a consumer and left
its supplier staged.** It documented the mechanism correctly, proposed a sound R15-shaped control
for it, and was itself a fresh instance of it — written in the same tick, about the same paths.

The operational cost is measurable. A subsequent tick reads the staged finding, sees INSTANCE
FIXED with a "what landed" manifest, and diagnoses *elsewhere*; the failure count went from 229 to
244 with the same one-line cause sitting in the index the whole time. A false FIXED is worse than
no finding, because it redirects the next reader away from the live cause — the same asymmetry
CLAUDE.md names for prose-only rules ("illusion of control").

## The class, stated so a control can fail (R15)

The existing proposed control (resolve new cross-module symbol references against the resulting
tree) would have caught the *original* omission and is still the right build. It would NOT have
caught this one, because nothing here was committed at all. The missing control is narrower and
much cheaper:

> **A document may not claim a path LANDED unless that path's content is reachable from a commit.**
> For each path in a finding's "what landed" manifest, `git ls-tree HEAD -- <path>` must exist AND
> `git status --porcelain -- <path>` must be clean of staged (`M `/`A `) entries. A staged-but-
> unlanded path in a manifest is a RED naming the file.

Killer patterns to check before believing it:

* **TAUTOLOGY** — it must read the tree (`git ls-tree`/`git cat-file`), never `git status` alone and
  never the working tree, or it asks the tree that was already green
  ([[feedback_a_cut_recorded_as_executed_may_never_have_been_committed]]).
* **FAIL-OPEN** — a finding with no parseable manifest must be *named in the output as unchecked*,
  not silently skipped; otherwise the control's population is "findings that happen to use the
  heading I grep for".
* **FAIL-SILENT** — run it where a finding is *archived to `done/`*, which is the moment the claim
  becomes load-bearing for the next reader. A checker with no automated caller is the class this
  repo has already filed (`CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md`).
* **MUTATION** — re-run it against `WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_
  THE_SUPPLIER_STAGED_2026-08-14.md` at parent `75290668f`. It must red on
  `tools/simplifications_store.py`. That is the only evidence that would make it worth its runtime.

## The second half of the same hour: the diagnostics ate the disk

`/tmp` was at **99% (149MB free)** when this tick began, on a 7.8G **tmpfs** backed by the same
15.9G of RAM the suites need. `du` attributed ~4G of it to abandoned repo-sized checkouts from
*previous wedge diagnostics* — `/tmp/gatecand`, `/tmp/gatecand2`, `/tmp/wedgediag_*`,
`/tmp/wedge-pristine-*`, `/tmp/wouldbe`, `/tmp/cand2`, `/tmp/head*` (nine of them), `/tmp/rt`,
`/tmp/wb.tar`, plus 1.7G of `/tmp/pytest-of-rich` — every one a hand-rolled reproduction that a
previous tick built and never removed.

That is a **self-sustaining wedge**: hunting the red consumes the resource whose exhaustion
produces a red. Observed directly this tick — a full-pathspec gate run at 99% returned
`343 failed, 69 errors` across the whole selected suite, which says nothing about any commit. After
the sweep (99% → 21%, 6.2G free) the same run reduces to the two real reds.

The prior tick declined to sweep, and said so honestly: *"`fuser -m` on a tmpfs path matches the
whole MOUNT, so nothing here establishes which of those are abandoned. None were deleted."* That
limit is real for `fuser`, and it is answerable from the process table instead: `ps` showed no
`pytest` process on the box, so no live suite owned any of them. Recording the resolution so the
next tick does not re-derive the same block:

> **To establish that a `/tmp` checkout is abandoned, read the process table, not the mount.** No
> live `pytest`/`surgical_land`/`process_run_complete` process ⇒ every repo-shaped extract under
> `gettempdir()` is debris, whatever `fuser` says about the tmpfs.

## What is NOT claimed

- No claim that the finding's author knew the landing had failed. `surgical_land` is fail-closed and
  the likely shape is a REFUSAL (the sibling finding records one, on disk) read as a success, or an
  attempt killed by a timeout — the same 10-minute cap this tick hit on its first try. Not
  established either way; the receipt would settle it and no commit exists to carry one.
- No claim that the tmpfs debris caused the *original* wedge. It blocked and corrupted the *repair*,
  twice: one refusal on disk (prior tick) and one 343-failure scope collapse (this tick).
- No claim about the `tests/architecture/test_static_quality_ratchet.py` red at HEAD — separately
  filed, untouched here, and deliberately left staged.

**Evidence:** `git log -S "def atom_name" -- tools/simplifications_store.py` (empty) ·
`git status --porcelain -- tools/simplifications_store.py` (`M `) ·
`docs/observability/sim-runner-log.md` (`Publish gate RED -- blocking test(s):` × 244) ·
`tools/surgical_land` resulting-tree gate output, this tick, both before and after the sweep ·
`df -h /tmp` at 99% then 21% · `du -sh /tmp/*` · `ps aux | grep pytest` (empty).

**Related:** [[feedback_the_record_can_outrun_the_code]],
[[feedback_a_cut_recorded_as_executed_may_never_have_been_committed]],
[[feedback_your_repair_may_be_unlandable_alone_because_it_sits_on_unlanded_work]],
[[feedback_gate_scratch_exhaustion_becomes_a_scope_collapse]],
[[feedback_untracked_build_passes_local_green]].
