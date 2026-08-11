# [WORKER-FINDING] The pre-commit gate cannot see a test named for an ASPECT — the third publish wedge, cause and fix

**Found:** 2026-08-09, unwedging the publish gate (episode 4, 14 consecutive failures, ~112 min red).
**Disposition:** BOTH halves FIXED this tick, each mutation-proven. The residual half is named below.
**Rank:** the fix is landed; what follows is the class statement so it is not re-derived a fourth time.

## What was red, observed with evidence

The gate's own log named the blocking test (R9 — this is the recorded failure, not an inference):

```
[2026-08-09 16:19 UTC] [process_run] Publish gate RED -- blocking test(s):
FAILED tests/simulation/test_live_population_seam.py::test_seam_module_does_not_import_company
    assert "from company" not in text
E   assert 'from company' not in '"""LIVE POP...S) + drawn\n'
```

KNIFE pass 2 routed sixteen `simulation/` modules off `from saas.customers import CUSTOMERS` and
onto `from company.interfaces.supply_book import registered_supply_points`. One of those sixteen,
`simulation/live_population.py`, carries a wall-hygiene test asserting it imports no company code
at all. So the pass tripped a guard that **forbade the very surface the wall sanctions**:
`company.interfaces` is `SEAM_PACKAGE` in `tests/architecture/test_epistemic_wall_ratchet.py:105`,
the declared crossing in either direction.

**The routing was right; the guard was wrong.** Reverting `live_population.py` to `saas.customers`
would have re-opened a class-(b) edge the ratchet no longer allowlists — strictly worse.

## Why nothing caught it before it reached the publish gate

`tools/pre_commit_test_gate.py::tests_for()` globbed `tests/**/test_<stem>.py` — the EXACT stem:

```
$ python3 -c "from pre_commit_test_gate import tests_for; print(tests_for('simulation/live_population.py'))"
[]
$ ls tests/simulation/ | grep live_population
test_live_population_seam.py
```

The only test covering that module is named for the ASPECT it covers, so the gate selected **zero**
tests, passed, and the change landed. Naming a test file `_seam` / `_event_log` / `_guards` is a
convention this repo actively uses — the glob was blind to a whole naming convention in its own tree.

## The class, and why this is the second sighting in one day

Filed hours earlier, same shape, different surface:
`WORKER_FINDING_THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09.md` — a changed
non-`.py` file also maps to zero tests. That finding stated the class correctly:

> coverage = a **filename suffix** instead of "what does this file actually affect".

This is its `.py` sibling. Both are *fail-toward-silence*: the gate cannot answer "what does this
affect", and answers "nothing" rather than "I don't know, run more". R15's doctrine is the opposite —
an unavailable check is a FAILED check.

## What landed

1. **`tests_for()` now also globs `tests/**/test_<stem>_*.py`.** Mutation-proven both ways: restoring
   the exact-stem glob reproduces `got []` and reds the new guard
   (`test_aspect_named_test_files_are_selected_not_just_the_exact_stem`); a companion test pins that
   the widening does not over-match a different module's tests.
2. **The wall guard is now an AST scan, narrowed to company LOGIC, exempting `SEAM_PACKAGE`** —
   imported from the ratchet that DEFINES it, so the wall constant has one home and cannot drift.
   Mutation-proven on the live module: injecting `import company.analytics.cohort_discovery` fires it;
   the sanctioned seam import passes.

   The assertion it replaced (`"from company" not in text`) was the one-syntactic-form class: a
   substring scan that read the docstring as code, could not see
   `importlib.import_module("company...")`, and could not tell the sanctioned seam from company
   decisioning logic.

   The R15 both-ways proof runs on FIXTURE sources, deliberately. Deriving it from the live module
   (asserting the seam still imports `supply_book`) would have made it a vacuity guard requiring a
   LIVE DEBT — it would fire falsely the day a later pass legitimately drops that import.

## Still open — the residual, stated so it is not mistaken for closed

The **non-`.py` half is untouched**. A changed `.json`/`.yaml` the code loads still selects no
mapped tests; `background/process_manifest.yaml` and `docs/design/maturity_map.yaml` remain in that
blind spot. The prior finding's remedy stands and is the better one: reuse
`tools/select_impacted_tests.py`, which already refuses to narrow when it cannot prove impact.
That is a real fix, not this tick's, and it is the half that will bite next.

## Related

* `WORKER_FINDING_THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09.md` (the sibling half)
* `WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09.md` — same KNIFE pass; its
  coupling is why the fix here had to land in the SAME commit as the staged pass-2 code (the new
  guard is only true of a tree where `live_population.py` reads the supply book).

— Worker finding, 2026-08-09, during the episode-4 publish unwedge.
