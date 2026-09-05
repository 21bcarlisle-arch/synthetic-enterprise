# [SEAT FINDING] Two of the four sibling registers lose a row silently, one is guarded only by a literal pin, and one is guarded only by the accident of being referenced

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `census-register-low-water-third-question`
**Filed** 2026-09-05. Pre-registration, written before any measurement below:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_CENSUS_SIBLING_REGISTERS_CAN_ALSO_LOSE_A_ROW_2026-09-05.md`.
Predecessor: `dc5fcbbc8` — `removed_dispositions()`, the same question asked of the alarm census.

---

## The question

`removed_dispositions()` landed on the alarm census because any control written as
`for key in register` has **the register as its subject set**: a key in neither the derived hits
nor the stored rows is the subject of nothing, and the register is a high-water mark that nothing
kept from falling. The direction was to ask the same third question of the four sibling registers.

## What was measured

Each register had one row deleted and every control over it re-run.

| Register | Result | Detail |
|---|---|---|
| `background/finding_classes.py` `CLASSES` | **HOLED**, second-order shape intact | Dropping `controls_that_cannot_fail` from the tuple returned `check()` **0 failures**. |
| `docs/design/maturity_map.yaml` | **HOLED for a leaf** | 314 atoms; 175 named by nothing in `depends_on`/`couples_with`/`blocked_on`. Deleting one returned **0 violations** from all five facet checks. |
| `docs/design/canon_claims.yaml` | **PROTECTED**, but not by the tool | `canon_drift_check.run()` after deleting `C1`: 14 claims → 13, drift `[]`, exit **0**. The literal pin `EXPECTED_CLAIM_IDS` in `tests/tools/test_canon_drift_check.py:51` catches it. |
| `tools/domain_constant_origins.py` | **NOT THIS SHAPE** | Subject set is derived from `scan()` over the source. Deleting a "row" means deleting the constant — the carrier itself. An honest change, not an erased record. |

**The second-order shape, measured directly on `CLASSES`.** Delete the class DOCUMENT and `check()`
refuses `MISSING CLASS DOC CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`. Delete the class ROW as
well and `check()` returns **0 failures**. Deleting the row is the cure for the refusal the row
itself raised. A red clearable by deleting the evidence is a fail-open with an extra step — the
identical shape `eroded_dispositions()` had on the census, and rules 4 and 6 of `check()` (count
mismatch, severity disagreement) refuse per class row the same way.

## Against the pre-registration

**P1 (canon is a hole, high confidence) — REFUTED, and usefully.** The *tool* is blind, but the
test suite is not: `EXPECTED_CLAIM_IDS` is pinned literally, with a comment already stating the
exact argument this direction was built on ("a parametrised test that draws its cases from the
registry it checks cannot see its own scope shrink"). The prediction was wrong because it looked
at the iterating control and not at what else stood over the register. **P2** is moot for the same
reason. **P3 (map partial) — CONFIRMED**, and the "accident" reading is the right one: 175 of 314
atoms have no referent, so the map's protection is a property of the graph, not a control. **P4
(`CLASSES` uncertain) — resolved to the worst case**, and it is the one site where the second-order
shape reproduces exactly. **P5 (`domain_constant_origins` excluded) — CONFIRMED.**

The prediction I was most confident about was the one that was wrong, and the one I recorded as
genuinely unpredictable was the one that mattered. Kept here rather than revised.

## What was done

`background/register_low_water.py` — the mechanism, shared rather than a rung per register, since
a hand-rolled copy per site regresses every repair the original holds. `keys_at_head()` returns
`None` and never an empty set for an unestablishable baseline; `removed_rows()` turns that into a
refusal that names itself. Wired at `finding_classes.check()` as rule 7, running first because it
is the only rule whose subject is the register rather than a row of it.

Seven mutations, all killed, and the wiring proved separately from the rung because a control that
calls the shared helper survives mutation of the caller. M7 — pointing the baseline at the wrong
file — produces a REFUSAL, not a clean result, which is the direction this has to fail in.

One leg's first draft was itself the defect: `removed_classes(baseline=None)` reads `None` as the
*read-HEAD sentinel*, so the refusal branch is unreachable through the parameter that names it,
and the leg passed against a clean live tree while asserting nothing. Driven through the
production route instead (`keys_at_head` returning `None`).

## What is NOT done, and is the next piece

**`docs/design/maturity_map.yaml` is measured, holed, and unwired.** The mechanism is built and
generic; what the map still needs is a decision the census did not have to make — the map is a bare
YAML list with no place to hang a retirement reason, so the escape hatch needs a home (a sibling
register file, or a `_retired` document) before the rung can be wired without making every honest
atom retirement a wedge. That choice is the work, not the plumbing.

**The canon register's guard is crude but real** and is deliberately left alone: `EXPECTED_CLAIM_IDS`
refuses ADDITIONS as well as removals, which is friction its own comment accepts on purpose.
Replacing a working low-water mark with a better-shaped one is not worth a wedge here.
