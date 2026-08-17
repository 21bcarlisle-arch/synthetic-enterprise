# [WORKER-REPORT] — The census ran; the stack was ONE deep, not three (2026-08-10)

**Severity:** RECORDED · **Lane:** H_harness

Against `DIRECTOR_PRIORITY_ENUMERATE_THE_STACK_2026-08-10`: *"run the scoped publish-path suite
ONCE at a clean HEAD checkout WITHOUT `-x` … Capture EVERY red in one pass. Then fix the complete
list as one batch."*

## Verify, don't redo — the census was already in flight

The tick's first act was to check state rather than start work. `tools/enumerate_publish_gate_reds.py`
had been launched by a prior tick (`--deadline-seconds 5400`) and had **already completed at 22:58**,
leaving `docs/observability/publish_gate_red_census.json`. A second census would have re-run the
heaviest job on a 15.9 GB box for a measurement that already existed.

## The measurement (observed-with-evidence)

```
census outcome: complete
  HEAD d43c2e192  rc=1  1437.9s (deadline 5400s)
  scope: 6 publish-path source(s) -> 132 blocking test file(s) via the static import graph
  1 red(s) across 1 file(s)
1 failed, 2413 passed, 178 deselected, 1 xfailed in 1434.67s (0:23:54)
```

**One red, not three:**

```
tests/background/test_derived_artefact_register.py::TestStaleness
    ::test_every_registered_artefact_is_currently_fresh
  AssertionError: stale derived artefact(s):
    ['docs/design/BLOCKED_ATOM_VISIBILITY.md', 'docs/design/FORWARD_ATTACHMENT_LEDGER.md']
```

That is the census's entire value, and it is worth stating plainly: **the eleventh wedge's
three-deep stack was already paid down.** Every previous estimate of "how close is publishing to
green" was a guess with an unknown multiplier, because `-x` reports the first red in collection
order and is structurally blind to the rest. This one cost 24 minutes and is now a fact.

## The batch (one item, one receipt)

**`63da862ff`** — re-verified at **current** HEAD `b702848e5`, five commits past the census's
subject, in a checkout built by the publisher's own `_materialise_head_into` +
`_make_checkout_a_repo` + `_overlay_untracked_data`. Both artefacts still stale, so the red was
live and not an artefact of a superseded subject.

Repaired via `derived_artefact_register.repair_from(checkout, repo)` — rendered from **committed
truth**, not from the working tree, which is the register's `source_root` contract and the reason
the working-tree copies (which had been sitting modified-but-uncommitted) were not simply
committed as-is. Converged in 2 passes, `still_stale: []`.

The renderings are real derivations, not a re-stamp: the map grew 266→272 atoms (harness share
41.7%→41.5%), `D_billing_metering` 27→30, and the attachment ledger gained `D23` plus `D22`'s
`build`→`harden` move.

**Verified on the gate's own subject, not on the tree that fixed it:**

| subject | stale artefacts |
|---|---|
| HEAD `b702848e5` (before) | `BLOCKED_ATOM_VISIBILITY.md`, `FORWARD_ATTACHMENT_LEDGER.md` |
| HEAD `63da862ff` (after) | **none** |

## The instrument landed too — it was untracked

**`c330c3cae`** — `tools/enumerate_publish_gate_reds.py`, its 14 green tests, and the census JSON
were **all untracked on the shared tree**. The tool that exists to expose
`feedback_untracked_build_passes_local_green` was itself an instance of it: one `git clean` and
both the instrument and its measurement would have been gone, with no way to reproduce either.

Because the new test file imports the tool, which imports `process_run_complete`, it **enters the
gate's blocking scope** (`feedback_an_untracked_test_changes_the_publish_gates_scope`). So the
scope change was verified where it counts rather than in the tree that wrote it — both files run
inside a clean checkout of the landed HEAD `c330c3cae`:

```
26 passed in 78.43s   (tests/tools/test_enumerate_publish_gate_reds.py
                       + tests/background/test_derived_artefact_register.py)
```

The `.log` summary is deliberately **not** committed — `.gitignore:20` covers
`docs/observability/*.log`, and `surgical_land` refused the ignored path rather than quietly
`-f`-ing it. That refusal is correct; the JSON is the record and the log is a rendering of it.

## For the next excavation's sizing

1437.9s over 132 blocking test files at **parallelism 1**. The director's "halve parallelism
before halving scope" resolves to **scope is already the floor** — the gate argv is serial, there
is no xdist to halve. The census artefact records that in `parallelism_note` rather than silently
narrowing, so the next reader does not have to re-derive it.

No OOM: the memory cleanse held (5,126 MB freed, qwen unloaded), and the run completed inside a
5400s deadline with 1437.9s used.

## What is NOT done

The director's exit has four clauses and this tick owns the first. **The batch has landed and is
pushed** (`origin/main` at `c330c3cae`, verified by fetch, not by local log). The remaining three —
one cycle green end-to-end, the 135 `run_complete_*` markers flushing, the stamp moving off
`dfefd0a14` — are the **publisher's** to do, and a `process_run_complete` cycle is live as this is
written. They are not claimable here and are not claimed.

`-x` stays on the steady-state gate. It is the right setting for a healthy pipeline and the wrong
instrument for an excavation; the census is what the wedge draw reaches for when the gate has named
four different blocking tests in six cycles.
