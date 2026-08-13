# [WORKER-FINDING] HEAD was red, and both reds were controls the landing commit never ran (2026-08-13)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** both reds repaired in this tick;
nothing here is owed.
**Discharged:** `tests/tools/test_map_assertion_provenance.py::test_a_non_hour_entry_beside_a_real_one_contributes_nothing_and_does_NOT_raise`, `tests/simulation/test_contact_propensity.py::test_the_runner_can_write_the_gap_ledger_and_the_row_names_the_pair`

## How it was found

Not by looking for it. A staged-but-uncommitted change from an earlier tick (OPS11 + the
fabric property-type cut) was being landed; the pre-commit gate ran 148 suites for 24
minutes and **refused the commit**. None of the failures were in the changed code.

Twenty-five failed. Twenty-two do not reproduce standalone — twelve in
`test_deadmans_switch.py` alone — and are isolation artefacts of three suites running
concurrently on this box. **Three were real, and all three were already red at HEAD**,
verified in a clean `git archive HEAD` checkout, not inferred from the dirty tree.

So the repo had been unable to accept ANY commit since `433718889`, and the thing that
discovered it was an unrelated lane paying a 24-minute gate.

## The two defects, both landed by `433718889`

**1. A family member that could not write.** `tools/couple_contact.py` shipped measuring the
contact belief-vs-truth gap and printing it. Its own docstring said it "does not yet write
the gap ledger, which is a publish-path change named rather than quietly skipped" — a
deliberate, stated deferral. But `background.gap_ledger_reconciler` derives its producer
population from the `tools/couple_*.py` **glob**, and asserts every family member is a
discovered writer. That control exists precisely so membership cannot be declined by
omission; the deferral was not available.

The fix is the opt-in `--write-ledger` flag every sibling carries. **The deferral's reasoning
was still right and is preserved**: nothing schedules this runner, so no publish path changes
and no door renders a new figure. Reading the ledger into the digest and the Proof door
remains a separate step.

Scoring uses `prediction_gap` (formula f) — both sides are continuous per-bill probabilities,
and normalising to the no-skill baseline is what makes the number readable. Measured on a
400-bill synthetic book: **gap 0.85** (the supplier's model is worth little over predicting
the mean), aggregate bias **−0.009** while the worst archetype (`disengaged`) runs **+0.39**.
That spread is the module's own stated hazard — an aggregate alone averages the archetypes'
opposing signs — so the worst archetype rides in the ledger row's components.

**2. A check that could not tell "not an Hour entry" from "the convention moved."**
`tools/map_assertion_provenance.py::entry_hour` raised when an entry named its first Expert
Hour past a 120-character self-identification window. It fired on a **DISCOVER/FRAME note**
that is not an Hour entry at all and merely mentions one in its body — `hold_record_atoms`
takes its register from `simplifications_store.for_atom`, which returns *every* entry an atom
has, not only Hour entries.

Those are two different facts and only one is an emergency. They are now measured separately:
a non-self-identifying entry contributes no ordinal, and the convention-moved alarm is the
population-level `HOUR_PARSE_FLOOR` vacuity guard, which still raises when nothing parses
anywhere. **The refusal did not weaken — it moved to the altitude the claim is true at.**

R15 both ways, driven from one call so the directions cannot be separately arranged: deleting
the window check makes the note parse as Hour #22 and produces `HOLD_STALE: register records
Hour #22, latest ANSWERED is #15` — the new test fails under mutation. The
convention-moved direction still raises `VACUITY`.

## What this says about the class, and it is not "run the tests"

Both defects are the same shape: **a control whose population is derived by GLOB or by STORE,
red-flagged by a commit that reasoned about its own file only.** A per-file mental model
cannot see a control that enumerates its subjects. Neither author was careless; both wrote a
paragraph explaining the deferral.

The honest generalisation is that the gate is the only thing that knows, and **the gate is 24
minutes and enlists the whole index** — so it is paid at landing time, by whoever lands next,
not by whoever caused it. That is why a red HEAD survived and why an unrelated lane found it.

## What is NOT claimed

The 22 non-reproducing failures are **not** diagnosed here. They are isolation artefacts under
concurrent suite load, recorded because a gate refusal that is 88% weather teaches the reader
to discount gate refusals. That is its own finding and its own lane; it is named, not fixed.
