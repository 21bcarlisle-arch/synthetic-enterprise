# PREREG — what the wrong-class stamp says about M9, M10 and M15

**Written 2026-09-06, after the engine change and its controls were green and mutation-proven,
while the grading run was in flight and BEFORE any cell of it was read.** The predictions restate
the claim's own `done_means`; they are recorded here so the run can refute them rather than be
read back as confirmation.

Subject: `tools/generate_grid_intensity_feed.py`, spec `tools/grid_intensity_feed_contract_battery`.
Live fingerprint at run time: **`5c3488f6809e`** — *not* the `aa5ce7785789` the claim cited, which
another lane's M12–M15 work moved before this turn opened. Graded against the direct suite that
holds M10's controls, `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`.

## The three rows and what is predicted of each

| Row | Predicted `died` | Predicted `died_by_wrong_class_in_a_control_body` | Why |
|---|---|---|---|
| **M10** | DIED | **True** | Substitutes a list where a period-ised mapping is expected. Both control bodies were measured red on `AttributeError: 'list' object has no attribute 'items'` from `sim/elexon_fuel_outturn.py:845` — they RAN and neither reached an assertion. |
| **M9** | DIED | **False** | M9's kill is a setup error: the module fixture raises before any body runs. `died_by_setup_error_only` is its stamp, and this one must stay False or the two are synonyms rather than a partition. |
| **M15** | DIED | **False** | M15 is a type-correct twin, written precisely so a control can assert past it. A control fires; the kill is the property. |

## The load-bearing prediction

**M9 and M15 must both be False, for two DIFFERENT reasons.** A stamp that fired on every death
would satisfy M10 alone. If M9 comes back True the scoping to `failed - errored` has come undone
and the new stamp is a second name for the old one. If M15 comes back True the assertion-class
vocabulary is wrong and every honest control firing in the family is about to be stamped as a
crash — the exact inversion this was built to prevent.

## What would refute the design rather than the row

`None` on any of the three. `None` means the exception class could not be read out of the run at
all, which would mean the terminal-width finding below is wrong or incomplete, and no second
pytest pass would be avoidable after all.

## The premise the claim was drawn on, re-measured

The claim states the class "is not in that output at all", and concludes the ROUND had to change —
a `--tb=line` pass, or a second pass over the rows that died. **Measured, that is false.** `-rfE`
already prints `FAILED <node> - <Class>: <message>`. What deletes the class is terminal width:
pytest truncates the summary to `COLUMNS`, captured output has no tty so that defaults to 80, and
every node id in this repository exceeds 80 characters unaided. The class was printed and then cut
off. Predicted consequence, and the reason this matters beyond tidiness: **no extra pytest pass is
needed**, on a family whose slowest cell is 655s.
