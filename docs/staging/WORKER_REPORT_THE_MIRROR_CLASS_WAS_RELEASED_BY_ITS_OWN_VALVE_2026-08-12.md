# WORKER REPORT — the mirror class's four blockers were repaired before they were filed, and rule 6 released the class

**Severity:** RECORDED · **Lane:** H_harness

**Date:** 2026-08-12 · **Draw:** RUNG 1c (OPS12 clause 3), lane `H_harness`, 3 live BLOCKING class documents
**Subject:** `CLASS_MEASUREMENTS_THAT_MIRROR_2026-08-12.md` and its 4 owed members
**Outcome:** the class reads LATENT, `H_harness` goes 3 blocking class documents → 2, and the
supervisor's own draw text changed to match. Each release carries a named falsifier that was RUN
GREEN before the discharge line was written.

---

## What the rung actually named

Three class documents, 12 owed BLOCKING members between them. The whole population was triaged by
each member's own close section rather than by its header, because a severity header states what the
Hour FOUND and nothing re-reads it — this project's own filed defect, one layer up.

Of the 4 members of `measurements_that_mirror`, **all four repaired their own defect inside the same
document**: "What landed (closed at the class, R10)", "What was built (HARDEN)", "Closed at the class
(R10)", each with an R15-both-ways table and a named test count. The instrument each named as
untrustworthy was trustworthy again before the document was saved. The other two classes were NOT
forced into the pattern: their members are read but not discharged here, because once a tick has
harvested the self-repaired ones the rest are genuinely open.

## The discharge, one document at a time — never a bulk pass

The falsifiers were run FIRST, at this HEAD, and the discharge line written only after:
`15 passed, 427 deselected` over the nine named nodes (some parameterised) in
`tests/tools/test_couple_w2_11_d5.py`.

| member | falsifier(s) run green |
|---|---|
| `WORKER_FINDING_THE_AGEING_TRUTH_SIDE_IS_THE_ORGANS_OWN_RULE_2026-08-10.md` | `test_the_truth_side_of_every_published_dimension_is_harness_owned`, `test_R15_an_organ_only_dating_drift_breaks_the_ageing_residual` |
| `WORKER_FINDING_THE_BELIEF_TRUTH_RULE_IS_AN_UNMEASURED_MIRROR_2026-08-10.md` | `test_the_coverage_only_claim_is_measured_not_asserted`, `test_a_dimension_whose_published_text_makes_the_claim_must_declare_it`, `test_R15_an_organ_only_rule_drift_breaks_the_coverage_only_residual` |
| `WORKER_FINDING_THE_MEMORY_GRID_WAS_STILL_THE_REGISTERS_OWN_CLAIMS_2026-08-11.md` | `test_the_memory_grid_is_derived_from_the_book_not_the_register`, `test_a_knob_with_no_book_grid_raises_rather_than_asking_the_register` |
| `WORKER_FINDING_THE_REGISTER_WAS_ONLY_EVER_ASKED_WHERE_IT_HAD_ANSWERED_2026-08-11.md` | `test_the_resolution_grid_is_derived_from_the_book_not_the_register`, `test_the_saturation_rule_is_not_keyed_to_a_register_state` |

Two of the four carry a limitation that is **recorded and accepted rather than repaired**, which is
clause 2's other release and is stated in the discharge line itself: the belief dimension's
`_severity_label` stays a mirror on purpose (deleting it deletes the independence it exists to
provide), and the ageing dimension's uniform-boundary blindness on a three-age book is pinned by test
rather than fixed. A discharge that claimed those were repaired would have been the overclaim this
lane catalogues.

## The release valve fired on its own, unprompted

`background/finding_classes.py` rule 6 (the one rule there that can LOWER a severity) failed the
check the moment the members were discharged and before anything was re-rendered:

> `STALE SEVERITY CLASS_MEASUREMENTS_THAT_MIRROR_2026-08-12.md: prints BLOCKING, instances derive
> LATENT — re-render; a discharged member does not release the class document until the header is
> rewritten`

That is the control built for exactly this transition doing its job on its first real instance, not a
test fixture. After `--render`: `check: PASS (0 failures)`, and only the one class document moved —
the other four re-rendered byte-identical.

## R11, no orphan transition — checked at the consumer, not at the parser

`background.supervisor._blocking_lane_draw()` driven on the REAL staging root now returns

> `lane H_harness carries a live BLOCKING finding -- CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md,
> CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`

— two documents where the tick's own doorbell named three. The lane census agrees:
`BLOCKING 4` repo-wide, and no `FALSE-DISCHARGE` line.

## What is still owed, stated so it is not laundered

8 BLOCKING members remain across the other two classes — 5 in `controls_that_cannot_fail`, 3 in
`publish_gate_and_wedge` — and `H_harness` therefore stays blocked. Each needs its own reading and its
own falsifier run; none is discharged by this tick. `R12`: no published figure moved — this tick
changed no code and no number, only what four documents and one derived header say about themselves.

## Tests

`tests/background/test_finding_classes.py` + `tests/background/test_finding_severity.py`: **89 passed**.
Falsifiers: **15 passed** in `tests/tools/test_couple_w2_11_d5.py`.
