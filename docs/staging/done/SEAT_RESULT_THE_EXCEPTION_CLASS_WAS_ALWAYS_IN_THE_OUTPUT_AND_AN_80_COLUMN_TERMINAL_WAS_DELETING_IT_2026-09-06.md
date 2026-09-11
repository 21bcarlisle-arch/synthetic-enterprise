**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the exception class was always in the output, and an 80-column terminal was deleting it

**Measured 2026-09-06 BST, shared tree at `9b08d302f`. Claim
`battery-died-cannot-see-a-wrong-class-red-in-a-control-body`. Instrument
`python3 -m tools.grid_intensity_feed_contract_battery --only M9 M10 M15` at live spec fingerprint
`5c3488f6809e`, run twice — once against each of the two direct suites that hold these rows'
controls. Prereg
`docs/staging/records/SEAT_PREREG_WHAT_THE_WRONG_CLASS_STAMP_SAYS_ABOUT_M9_M10_AND_M15_2026-09-06.md`.
Runs `/var/tmp/wrongclass_grade_5c3488f6809e.json` and
`/var/tmp/wrongclass_grade_membernames_5c3488f6809e.json`. Subject restored after both.**

## The claim's diagnosis was wrong, and the correct one is cheaper

The claim was drawn saying the exception class "is not in that output at all", and concluded that
**the round itself had to change** — a `--tb=line` pass, or `-rfE` parsing widened, or a second
pytest pass over the rows that died — and that this was "not a parser tweak".

Measured before anything was written, `-rfE` already prints exactly what is needed:

```
FAILED tests/…::test_wrong_class_in_body - AttributeError: 'list' object has no attribute 'items'
ERROR  tests/…::test_setup_error         - AttributeError: 'list' object has no attribute 'items'
```

What deletes the class is **terminal width**. pytest truncates that summary line to `COLUMNS`;
captured output has no tty so `COLUMNS` falls back to 80; and **every node id in this repository is
longer than 80 characters unaided**. The same probe at `COLUMNS=400` keeps the class and at the
default drops it, node id and all:

```
default: FAILED test_a_really_long_module_name_….py::test_a_control_whose_name_is_as_long_…
COLUMNS=400: FAILED …::test_a_control_whose_name_… - AttributeError: 'list' object has no attribute 'items'
```

So the class was being printed and then cut off, every time, and the fix is one environment
variable. **No second pytest pass.** That is the part worth having: the alternative the claim
proposed would have doubled the cost of every row that died, on a family whose slowest cell is
655s. The claim's premise was not spent — the hole is real and now closed — but its *diagnosis*
was, and following it would have bought a large recurring cost for a defect that a `COLUMNS`
assignment fixes.

*This is the project's own rule paying out: the question was settled by running something rather
than by reasoning about pytest's output format.*

## What landed

`_run_suite` now sets `COLUMNS=1000` on the pytest subprocess and records `red_classes` — node id
to exception class — beside `failed` and `errored`. `_no_verdict_was_reached` reads it and `_score`
stamps `died_by_wrong_class_in_a_control_body` on each cell.

Three-valued, and the third value is the point: **`None` means the run did not say what class the
red was**, which is not evidence that a control fired. `False` there would be indistinguishable
from a real verdict. A cell resumed from an older results file, written before this landed, stamps
`None` and not the flattering answer.

**Scoped to `failed - errored`**, so it is disjoint from `died_by_setup_error_only` by
construction. Read together the two now say *where* the red was (a body, or no body at all) and
*what* it was (a verdict, or a crash before one). A cell carrying both would mean the scoping had
come undone, and a control asserts it cannot.

Both are RESULT fields, not spec fields: not in the hashed payload, so no fingerprint in the family
moves.

## Machine-graded

Against `tests/tools/test_fuel_mix_reads_the_cache_each_member_names.py`, the suite that holds
these rows' controls — baseline `2 passed in 0.09s`, poison reaches (rc 2, `RuntimeError` at
collection), null round green (behaviour only, not a text grader):

| Row | `died` | `died_by_setup_error_only` | `died_by_wrong_class_in_a_control_body` | class |
|---|---|---|---|---|
| **M10** | DIED | False | **True** | `AttributeError` |
| M9 | DIED | False | False | `AssertionError` |
| M15 | DIED | False | False | `AssertionError` |

The three-way partition, on the real subject, in one run: one row whose body ran and never reached
an assertion, and two whose controls fired.

## The prereg was refuted on the first run, and the reason is the finding

**Predicted: M10 stamps True. It came back False, stamped `died_by_setup_error_only` instead.**

The first grading run went against
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py` — the suite the claim's own
measurement named. There M10 is a *setup error*: the module-scoped fixture raises before any body
runs, so nothing about a body can be said, and `False` is correct.

**The stamp is suite-dependent, exactly as reachability is.** One mutation is a setup error in one
suite and a wrong-class body red in another, because the two suites build the subject differently
— one through a module fixture, one through per-test `monkeypatch`. The claim measured M10 at
fingerprint `aa5ce7785789`; a concurrent lane then moved the control to a new file, which is what
`SEAT_RESULT_TWO_MORE_OF_FUEL_MIXS_CONTRACTS_DIE_AND_THE_INSTRUMENT_COULD_NOT_SEE_THE_CONTROL_UNTIL_IT_MOVED_FILE`
records, and the live fingerprint was `5c3488f6809e` before this turn opened.

Kept beside the result rather than revised: the prediction was made against the suite the claim
named and was wrong there for a reason worth having on the record. **A cell of this family is not
"row M10"; it is "row M10 in suite S", and the new stamp inherits that grain.**

## What this does NOT fix, stated plainly

`_score` runs with `-x`, so only the FIRST red is reported. In the M10 cell the node named is
`test_the_THERMAL_FLOOR_is_read_from_the_THERMAL_CACHE_…` — the first test in the file that touches
`fuel_mix()` — and not the control written for M10. The stamp's claim is therefore about *the red
that stopped the round*, not about every control in the suite. That is the same bound
`died_by_setup_error_only` already carries, and `-x` is what keeps a 655s cell affordable, so it is
recorded here rather than changed.

## Controls

`tests/tools/test_a_wrong_class_red_in_a_control_body_is_not_a_control_firing.py`, four tests.
Mutation-proven at `9b08d302f`, poison round first — an import-time raise in the subject reddens
all four, so none is vacuous:

| Mutation | Fires | Named by |
|---|---|---|
| POISON (import-time raise) | all 4 error | reachability floor |
| `_no_verdict_was_reached` → `return bool(r["died"])` (fires on any death) | 2 red | the partition control |
| `_no_verdict_was_reached` → `return False` (fires on none) | 2 red | the partition control |
| `_WIDE_COLUMNS` → `"80"` (**the real defect, restored**) | 2 red | the truncation control **and** the partition |
| drop the bare-`assert` branch of `_red_class` | 1 red | the reader control |
| unknown class → `False` instead of `None` (fail open) | 1 red | the fail-closed control |

The partition is asserted **once over all four states** — wrong-class, control-fired, setup-error,
survivor — rather than a leg each, because a stamp that fired on everything and a stamp that fired
on nothing each pass a single leg. Both directions redden it above.

The truncation control uses a node id longer than 80 characters *and asserts it is*, because the
same control written with a short name passes with the widening removed and proves nothing.
