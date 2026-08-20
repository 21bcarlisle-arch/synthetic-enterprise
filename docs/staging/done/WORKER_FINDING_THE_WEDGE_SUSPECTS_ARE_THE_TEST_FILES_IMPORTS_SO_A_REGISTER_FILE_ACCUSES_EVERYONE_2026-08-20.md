**Severity:** LATENT · **Lane:** H_harness

# The wedge names 8 suspects out of 23 in breadth-first order, and this project imports the subject-under-test inside the test function — so the true culprit ranked 21st and was cut

Everything below is `observed-with-evidence` unless labelled `inferred` (R9).
MEASURED AT: HEAD `279fd1549`, diagnosing the 13-run publish-gate wedge of 2026-08-20
(`wedge_since` 1787212714; HEADs `81449dcb4` / `0f5224e98` / `8ba61d802`).

## What happened

The gate blocked on one node:

```
FAILED tests/controls/test_control_mutation.py::test_dashboard_consistency_gate_fires_on_surface_disagreement
```

`docs/observability/.publish_gate_state.json` attached this suspect set, unchanged across all
13 failures:

```
modules: company/compliance/__init__.py, company/compliance/domain_invariants.py,
         company/billing/back_billing.py, company/billing/pre_bill_validation.py,
         company/compliance/obligations_register.py, company/compliance/internal_audit.py,
         tools/epistemic_verifier.py, company/compliance/population_sanity.py
commits: 60fc315da (the meter seam computed twice)
findings: WORKER_FINDING_THE_DISCOVERY_DAEMONS_VERDICT_COULD_ONLY_EVER_BE_OK_2026-08-13.md,
          WORKER_FINDING_THE_WALLS_CONFORMANCE_CONTROL_IS_IMPORT_SHAPED_2026-08-13.md
```

**None of them can reach the red.** The cause was `03dd8c49e` deleting `_check_consistency`
from `tools/generate_dashboard_data.py` and missing this file, its last calling consumer. The
doorbell instructed the worker to draw those two cited findings FIRST, ahead of every other
lane — so the misdirection was load-bearing on what got worked, not decorative.

## The mechanism, measured

`background/process_run_complete.py::first_party_imports` (line 4331) parses the test file with
`ast` and walks it:

```python
for node in ast.walk(tree):        # breadth-first
    ...
return mods[:WEDGE_MAX_SUSPECT_MODULES]     # = 8
```

Reproduced against the real file:

| measurement | value |
|---|---|
| first-party modules resolvable from the file, **uncapped** | **23** |
| `WEDGE_MAX_SUSPECT_MODULES` | **8** |
| module-level import statements in the file | **22** |
| index of `tools/generate_dashboard_data.py` in the uncapped list | **20** (21st) |
| present in the capped list the wedge published | **no** |

The culprit **was** found by the parser — my first reading of this, that a module-level scan
could not see a function-body import, was wrong: `ast.walk` does descend into function bodies.
It is ordering plus the cap that drops it, and the two combine into something reproducible:

`ast.walk` is **breadth-first**, so all 22 module-level import statements are enumerated before
any import nested inside a function body. This project's test convention is to import the
subject-under-test *inside* each test (`def test_...(): import tools.generate_dashboard_data as gdd`)
— the four dashboard tests here all do. So in any test file with ≥8 first-party top-level
imports, **the subject of every function-scoped test is structurally unreachable within the cap**,
and what gets published instead is the file's incidental top-level surface.

`blame_commits` and `linked_findings` are both derived from that same truncated module list, so
one bad list yields a wrong commit and two wrong cited findings. One inference, three confident
outputs — which is why the suspect block read as corroborated rather than as a guess.

## Why this is a class, not an instance

R10: raising the cap, or adding a top-level `import tools.generate_dashboard_data` to this file,
fixes this instance and leaves the mechanism intact. The defect is that **the suspect set is
ranked by AST depth — an artefact of the traversal — while the red is scoped to one function.**
Depth is uncorrelated with blame; here it was inversely correlated, because the convention that
makes a test honest (import the subject where you use it) is exactly what pushes the subject to
the back of the queue.

The instrument is worst precisely where this project concentrates its controls:
`tests/controls/test_control_mutation.py` is the R15 mutation register, 104 tests spanning
compliance, billing, dashboards, health checks and daemons, and it is *supposed* to be
cross-cutting. Register-style files are the ones whose top-level imports are least related to
any single red.

Interaction with `_exonerated_for` (line 4408), noted because it looks like a defence and is
not one here: its docstring already records that the link is lexical and that a finding naming
the cause scores as a *better* suspect. That guard assumes the blame trail is roughly right. It
cannot help when the trail is wholly wrong — nothing on it is a suspect, so nothing can be
exonerated, and the exoneration channel is silent in exactly the case that needs it.

## What it costs

13 runs of a stated PRIORITY-ZERO wedge published a suspect block a reader would reasonably act
on first. The cause was instead found by grepping the failing node's own symbol —
`grep -n "_check_consistency" tools/generate_dashboard_data.py` → no match, about ten seconds —
which is the one question the instrument never asks: *does the symbol this test names still
exist?*

## Candidate repair — NOT built, queued per SELF-INTERRUPT DISCIPLINE

Rank by **the failing function**, not by traversal depth: resolve the imports and attribute
references inside the named test function's own body first, then fill remaining slots from
file-level imports. Label which scope produced each suspect, so a file-level fallback is legible
as the weaker inference it is.

Cheap and independent of the above, worth more than the ranking fix: when the blocking node's
error is an `AttributeError`/`ImportError` naming a symbol, report **the symbol and whether it
still exists in the module the test reaches for**. That is a direct read of the red, not an
inference from it, and it would have answered this wedge in the first run.

**R15 obligation for either repair:** the mutation must prove the suspect set *moves*. This
control was never silent — it emitted eight confident suspects for 13 consecutive runs — so
fail-open here looks like output, not absence. Both-ways test: a red in a register file yields
the module the failing test actually touches, AND yields **nothing** rather than the file's
incidental top-level imports when the function scan resolves no subject. An empty suspect block
is the honest answer the existing `wedge_suspects` docstring already claims for itself
("an empty dict is the whole point"), and it is not currently reachable by this path.

**Not-a-suspect-for:** none declared — this document is about the instrument, not about any
blocking test.
