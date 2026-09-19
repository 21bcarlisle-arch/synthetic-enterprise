**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

**Knowledge:** none — this is a git-topology losslessness proof about an orphaned salvage commit, not domain understanding about GB energy.

# `5bf8a122f` holds nothing unlanded: 52 of its 80 paths are byte-identical to origin, 26 are superseded by the merge that closed the fork, and the only two bytes unique to it have never been in a non-SALVAGE commit

**Filed 2026-09-15 by the delivery seat**, holding
`the-two-orphaned-salvage-commits-and-the-reworded-remedys-dead-control`.

## What was asked

Two `SALVAGE(auto)` commits were not ancestors of `origin/main` after the 09-11 fork closed.
`ead8f781a` was already known spent — its six conflict resolutions were used verbatim in
`2212d0eed`. `5bf8a122f` (2026-09-11T03:52:58Z, parent `efd831aa9`) was the one nobody had read,
differing from origin by 63 files, and its only pointer was a `/var/tmp` worktree the reaper had
just deleted.

## It is already past the prune, and that is a fact about the deadline rather than about the work

`5bf8a122f` is **unreachable**. No ref reaches it, and it appears in no reflog entry:

```
$ git for-each-ref --format='%(refname)' | while read r; do
      git merge-base --is-ancestor 5bf8a122f "$r" && echo "reachable from $r"; done
(nothing)
$ git reflog --all | grep -c 5bf8a122f
0
$ git worktree list | grep -c se-lane0-merge-20260911b
0
```

It survives only as an object pending gc, so this triage could be done at all and cannot be done
again. The SHA and the verdict are written down here because after the next gc that is all there
will be.

## The triage

`5bf8a122f` touches **80 paths** against its merge base `efd831aa9` (the doorbell's "63 files" is
the count against origin's tip, not against the base). Every one of the 80 was compared blob-by-blob
against `origin/main` as it stands now:

| | count | what it is |
|---|---|---|
| byte-identical to origin today | **52** | landed, unchanged |
| the salvage's exact blob is somewhere in origin's history | **16** | landed, then superseded |
| origin's version is the fork-close merge's resolution | **10** | superseded, and read below |
| **never in a non-SALVAGE commit** | **2** | untracked run output — read below |

That is 80. Nothing is absent from origin that was ever committed.

### The ten the merge superseded, read rather than counted

A count is not a reading, so the four that carry code were diffed by hand:

- **`simulation/net_new_acquisition.py`.** The salvage returns `chosen` as the chooser's own dict
  and adds a `headroom_cy` key; `2212d0eed` returns `chosen is not None` and does not add the key.
  The resolution is coherent and loses nothing: inside the function the local `chosen` is still the
  dict (`chosen["positions"]` at line 746 is untouched), the only caller branches on truth alone
  (`if chosen:` in `plan_growth_campaign`), and **no reader of `headroom_cy` exists outside the
  function** — the salvage's extra key was an unread return. Checked, not assumed:
  `grep -rn headroom_cy --include=*.py` returns `settlement_choice.py`, three lines inside
  `net_new_acquisition.settle_within_budget` itself, and test call sites — no `settled["headroom_cy"]`.
- **`tools/pre_commit_test_gate.py`.** Both `CONTROL_TESTS` entries — the seat-guard ratchet and
  `tests/background/test_publish_scope.py` — are present at origin. The salvage has the same two,
  ordered the other way, with the pre-merge comment. The merge's comment is strictly more
  informative (it says the two rows were written by lanes that could not see each other).
- **`tools/generate_value_arms_data.py`, `tests/tools/test_generate_value_arms_data.py`,
  `site/capabilities/index.html`, `site/test_the_baseline_comparison_reaches_the_reader.py`.**
  Origin is strictly ahead: the salvage adds **0 lines** to each and deletes 46–179. There is
  nothing in the salvage's copy that origin's does not contain.
- **`site/data/value_arms.json`.** The salvage's is the 09-11 regeneration, stamped
  `2026-09-11T03:50:04Z`; origin's is `2026-09-15T10:00:47Z` and carries the
  `retraction_refused_because` record the salvage predates. Regenerable and older.
- **The prereg record** (`SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md`).
  Origin holds **both** pre-registrations verbatim under the merge's own header; the salvage holds
  only §A. Taking the salvage here would destroy a filed prediction.

### The two that are unique, and why they are not work

`docs/observability/book_growth_campaign.json` and `docs/observability/book_subset_verdict.json`
are on disk untracked right now and are in **no** commit on `origin/main`. They look stranded and
are not:

```
$ git log --all --oneline -- docs/observability/book_growth_campaign.json | wc -l
19            # every one of the 19 is a SALVAGE(auto) commit
```

Both are **run output with named producers** — `simulation/live_population.book_subset_verdict()`
writes the second, `tools/generate_book_growth_data.py` and `tools/couple_pb3_book_growth.py` the
first — and a run regenerates them. This is the shape the worktree close on 2026-09-15 recorded and
it is the shape again: a `SALVAGE(auto)` commit sweeps up untracked run output, and the sweep is
what makes run output look like stranded source. **Ask the producer what the file is** before
reading a salvage diff as lost work.

(`docs/observability/test_execution_log.jsonl` differs by one line and is machine state, already
modified in the shared tree by a live lane.)

## Verdict

**Both orphaned salvage commits are spent.** `ead8f781a`'s content is in `2212d0eed`;
`5bf8a122f`'s is in origin except for two files the code documents as untracked. Nothing needs to
be recovered, and the object going away at the next gc costs nothing.

## What this turn did NOT settle, and is not claiming

Eleven paths that `2212d0eed` touched have dirty working copies in the shared tree that match
**neither** `HEAD`, **nor** either merge parent, **nor** any of the five `SALVAGE(auto)` commits on
disk — so they are a live lane's in-flight work and not a reversion of the merge:

```
background/supervisor.py                                   +103 -64
docs/observability/.launch_records.json                    +119 -19
simulation/customer_events.py                                +8 -82
site/capabilities/index.html                                    (binary-ish, whole-file)
site/data/book_growth.json                                  +34 -45
site/data/value_arms.json                                   +13 -10
site/test_the_baseline_comparison_reaches_the_reader.py    +229 -37
tests/tools/test_generate_value_arms_data.py                +21 -314
tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py  +121 -18
tools/demand_vector_coverage.py                             +56 -47
tools/generate_value_arms_data.py                          +189 -230
```

`tools/demand_vector_coverage.py` is the one already filed as
`WORKER_FINDING_A_DIRTY_WORKING_COPY_OF_FIT_WEIGHTS_DROPS_THE_PARAMETER_THE_JUST_MERGED_CALLER_REQUIRES_2026-09-15.md`
— its working copy drops `groups=None` from `fit_weights`, and **the shared tree cannot import
`tools.generate_value_arms_data` because of it** (`TypeError: fit_weights() got an unexpected
keyword argument 'groups'`, raised at import time through `simulation/run_phase2b.py`'s
module-level `live_population()`). That is why every measurement in this turn was taken in a clean
`git archive HEAD` extract and why the repair landed beside this document went in by
`surgical_land --content` rather than by pathspec. **The finding is wider than the one file it
names** — that is the only addition made to it here, and the repair of the eleven belongs to
H_harness, which already holds it as BLOCKING.
