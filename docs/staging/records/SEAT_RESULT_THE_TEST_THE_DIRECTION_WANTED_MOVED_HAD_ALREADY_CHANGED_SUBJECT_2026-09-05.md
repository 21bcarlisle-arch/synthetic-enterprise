# RESULT — the test the direction wanted moved had already changed subject

**Severity: INFO** — a lane-0 direction re-measured before execution, found spent in one half and
actively harmful in the other. No code behaviour changed; two records were corrected beside their
claims. Filed against `low-water-reader-contract-lives-in-the-wrong-file`.

## What was drawn

> Move `test_THE_HEAD_READER_ITSELF_returns_None_and_never_an_empty_set` out of
> `tests/tools/test_the_canon_register_can_lose_a_claim_and_take_the_drift_with_it.py` and beside
> the mechanism it actually proves (`register_low_water.keys_at_head`), alongside a leg for the
> OSError/SubprocessError branch which nothing drives at all.

The stated hazard: after the 2026-09-05 convergence (`029c21452`) that one test was the only proof
of `keys_at_head`'s never-empty contract for all four registers, so anyone rewriting the canon's
rung would take the whole tree's proof with them and no gate would say so.

That hazard was real when written. It is not real now, and the remedy has inverted.

## Half one — the OSError leg: SPENT

`38871422b` ("prove the shared low-water reader contracts where they live") landed
`tests/background/test_the_shared_low_water_reader_refuses_rather_than_reading_empty.py`, which
drives the shared reader directly and includes the OSError/SubprocessError leg the direction asked
for. It is an ancestor of HEAD.

Re-measured against **that file alone**, canon suite excluded. Each mutation applied singly to
`background/register_low_water.py`, anchor asserted present-and-unique before patching,
`background/__pycache__` cleared between runs.

| mutation on `keys_at_head` | shared file | canon file |
|---|---|---|
| `except (OSError, SubprocessError)` → `frozenset()` | **RED** (4 failed) | green |
| `if proc.returncode != 0` → `frozenset()` | **RED** | RED |
| `except Exception` (extractor raised) → `frozenset()` | **RED** | RED |
| `if keys is None` → `frozenset()` | **RED** | RED |

All four `return None` branches — the whole never-empty contract — now red without the canon's file
participating. Deleting the canon's entire rung today takes none of the tree's proof with it. **The
hazard is discharged.** The OSError branch is additionally the one branch the canon has *never*
covered, which is exactly what the direction said and exactly what `38871422b` fixed.

## Half two — the move: A REGRESSION, and this is the finding

The test changed SUBJECT under the convergence, and the direction was keyed to what it used to
prove.

Post-convergence, `canon_drift_check._claim_ids_at_head` is a named seam onto the shared reader. So
the question `test_THE_HEAD_READER_ITSELF_...` now answers is not "what does the reader return" —
the shared file answers that four ways — but **"does the canon's seam carry the refusal through, or
swallow it?"**

Measured by re-hand-rolling the seam, i.e. reintroducing exactly the copy the convergence removed:

```python
out = register_low_water.keys_at_head(rel.as_posix(), _claim_ids_in_register,
                                      project_dir=REPO_ROOT)
return frozenset() if out is None else out      # the mutation
```

| suite | verdict |
|---|---|
| `test_the_shared_low_water_reader_refuses_rather_than_reading_empty.py` | **green** |
| `test_the_canon_register_can_lose_a_claim_and_take_the_drift_with_it.py` | **RED** — `test_THE_HEAD_READER_ITSELF_returns_None_and_never_an_empty_set`, `test_an_UNPARSEABLE_or_SHAPELESS_register_at_head_is_unestablishable` |

The shared file cannot see this mutation and never will: its subject is the reader, and the reader
is not what broke. **Moving the test beside the mechanism would have deleted the tree's only proof
of the canon seam's contract, and every suite would have stayed green while it happened.** The
direction's own reasoning — a proof that vanishes with no gate to say so — applied to its own
remedy.

The test is in the right file. Its docstring did not say why, which is how the move came to look
like a tidy; it does now.

## The sibling seam, asked because the first one had an answer

`finding_classes.removed_classes` calls `keys_at_head` directly too. Same mutation shape — swallow
`None` into `frozenset()` at the seam:

| suite | verdict |
|---|---|
| `test_the_class_register_can_lose_a_row_and_take_the_alarm_with_it.py` | **RED** — `test_an_unestablishable_baseline_is_a_refusal_and_never_a_clean_result` |
| shared reader file | green |

Covered, by a leg living in the class register's own suite. Consistent with the canon: **the seam's
proof belongs in the seam's suite, and the reader's proof belongs beside the reader.** That is the
rule the two measurements agree on, and it is the opposite of what the direction asked for.

`level_promotion_gate.low_water_failures` is not in this question's scope — it builds its baseline
itself from the union of the map's two halves and calls `removed_rows` only, never `keys_at_head`.

## What is still open, stated rather than implied

**The census seam `_dispositions_at_head` has not been put to this question.** It could not be this
turn: another lane holds `background/self_clearing_alarm_census.py` dirty in the shared tree, 237
lines deleted including `removed_dispositions` itself, and its suite is 14-red as a result. A
mutation verdict read off an already-red suite is uninterpretable, and the file is not mine to
restore. Ask it once that lane lands. `removed_dispositions` is present and correctly converged at
HEAD — this is a working-tree state, not a defect in the record.

## Disposition

Direction not executed; claim released. Two records corrected beside their claims rather than over
them — `register_low_water.py`'s closing paragraph, and the "What this leaves open" section of
`SEAT_RESULT_THE_CONVERGENCE_PROVED_A_CONTRACT_THAT_HAD_BEEN_PROVED_NOWHERE_2026-09-05.md`, whose
last three sentences are what the direction was drawn from.

**The generalisable shape.** That record offered two remedies as equivalent — "moving it, or adding
one leg beside the generic" — for a test whose subject was being changed by the very convergence
the record was writing up. One remedy was safe and one destroyed a proof. A tidy proposed for
something still in flight is a prediction about where it lands, and it gets read later as an
instruction. Both options were written in the same breath and only the second was measured.
