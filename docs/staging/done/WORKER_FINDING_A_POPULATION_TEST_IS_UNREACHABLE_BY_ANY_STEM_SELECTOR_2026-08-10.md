# [WORKER-FINDING] A POPULATION test can never be selected by a per-file stem glob — the third half of the impact-selector class (2026-08-10)

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-10, unwedging the SIXTH publish-gate wedge (76 consecutive failures, ~751 min red).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. The instance is closed (`de59adffa`); this is
the CLASS and it is deliberately not fixed here.
**Rank:** propose TOP of backlog, above both filed siblings — this is the half that just cost 12.5
hours of publishing, and unlike the other two it cannot be fixed by widening a glob.

## What was red, observed with evidence

The gate's own log (R9 — recorded failure, not inference):

```
[2026-08-10 03:02 UTC] [process_run] Publish gate RED -- blocking test(s):
FAILED tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded
E   AssertionError: background/*.py entrypoints with no seat guard as the FIRST act of
    their __main__ block: ['suite_duration_watch.py']
```

## The mechanism

Commit `82007ad44` (PW3, 2026-08-10 01:26Z) added **a new `background/*.py` module** —
`suite_duration_watch.py`, 274 lines, with a `__main__` block and no seat guard. It shipped with its
own test (`tests/background/test_suite_duration_watch.py`), which the pre-commit gate duly selected
and ran green.

The test that actually guards it was never selected. Measured directly, not inferred:

```
$ python3 -c "from tools.pre_commit_test_gate import tests_for;
              print(tests_for('background/suite_duration_watch.py'))"
['tests/background/test_suite_duration_watch.py']
seat guard test selected? False
```

`test_seat_guard_daemons.py` is a **population test**: it walks every `background/*.py`, and its
subject is a property of the whole set, not of any one module. Its stem is `seat_guard_daemons` —
which is not the stem of any module it guards, and never will be. So:

> **No stem-based selector can ever reach it.** Not the exact-stem glob, not the
> `test_<stem>_*.py` widening that the 2026-08-09 fix added. The relationship it needs is
> *"this file JOINED a population under test"*, and a filename cannot express that.

The population's newest member is precisely the member most likely to violate the property, and it
is exactly the member the selector cannot connect to the guard.

## Why this is the third half of an already-filed class, not a new one

`WORKER_FINDING_A_TEST_NAMED_FOR_AN_ASPECT_IS_INVISIBLE_TO_THE_GATE_2026-08-09.md` stated the class
correctly — *coverage = a filename suffix instead of "what does this file actually affect"* — fixed
the aspect-suffix half, and named the non-`.py` half as "the half that will bite next."

It bit a different half instead. Three now, all fail-toward-silence:

| half | selector answers | status |
|---|---|---|
| aspect-named test (`test_<stem>_seam.py`) | `[]` | FIXED 2026-08-09 (stem widening) |
| non-`.py` file (`.json`/`.yaml`) | `[]` | OPEN — enabled wedge #5 |
| **population test over a directory** | a *wrong non-empty answer* | **OPEN — caused wedge #6** |

The third is the worst of the three and is worth separating for one reason: the first two return
`[]`, which at least *looks* like nothing was checked. This one returns a **plausible non-empty
list** — the module's own test — so the gate reports "2 tests selected, green" and the silence is
indistinguishable from coverage. A fail-open that returns a confident wrong answer is harder to
notice than one that returns nothing, and neither filed sibling covers it.

## What closing it needs

Both filed siblings already point at the same remedy and it is the right one here too:
`tools/select_impacted_tests.py` **refuses to narrow when it cannot prove impact**. That policy is
already in-repo and already mutation-proven; the pre-commit gate does not use it.

The population-test half additionally needs a positive rule, because "refuse to narrow" is a
backstop, not a mapping:

- **A test that walks a directory should declare that directory**, and the selector should treat
  *any added or renamed file under it* as impacting that test. A marker (`@pytest.mark.population(
  "background/*.py")`) or a module-level constant is enough; the walk already names the glob.
- **R15, the mutation it must fire on:** add a new unguarded `background/*.py` fixture module,
  select tests for it, and assert `test_seat_guard_daemons.py` is in the selection. Today it is not,
  so the control cannot fail on its own named defect.

## Not to be confused with the uncommitted-half class

The working tree *did* contain the correct five-line guard when this tick opened, so this looks at a
glance like `WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09.md`. It is not.
The guard was written into the tree by a *later* diagnostic tick reacting to the red, not left behind
by PW3 — `82007ad44` never had it. Checked rather than assumed: `git show 82007ad44:background/
suite_duration_watch.py | tail -3` ends at `raise SystemExit(main())` with no guard above it.

The distinction matters because the two classes have opposite fixes: that one needs the commit to be
gated instead of the tree, this one needs the selector to reach a population test. Conflating them
would have "fixed" this wedge by tightening a commit gate that was working correctly.

## Sibling sweep — done, clean

Unwedging one member of a population and leaving another is the standing trap, so the whole
population was re-derived against **HEAD content** (not the dirty working tree) using the test's own
`_background_modules()` / `_main_block()` / `_guarded_name()` helpers: **0 offenders**. No second
unguarded module is queued behind this one.

— Worker finding, 2026-08-10, during the sixth publish-wedge episode.
