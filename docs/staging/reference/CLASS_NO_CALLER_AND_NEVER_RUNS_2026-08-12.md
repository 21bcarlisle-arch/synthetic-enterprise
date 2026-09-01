# [CLASS] No caller, never runs: code and controls nothing reaches

**Severity:** LATENT · **Lane:** H_harness

**Instances:** 8 · **Class:** `no_caller_and_never_runs` · **Source's own count:** ~5 (`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`, clause 1, "no-caller/never-runs")

**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** Since 2026-09-01 an accruing class register is DRAWN as work (`background/class_debt.py`, rank 35), and a drawn document is normally actioned and moved to `done/`. Doing that here is the 2026-08-23 failure: a bulk archive carried all five registers out of the root and wedged four consecutive publish cycles behind `MISSING CLASS DOC` while the files sat intact in `done/`. **You action this document by writing a decision into its `## Disposition` section** — repaired and closed by a named mechanism, or accepted as a limitation with its cost beside it. That is what takes it out of the draw, and it stays exactly where it is.

This document supersedes the individual findings listed below, which are **archived, not deleted**, in `docs/staging/done/`. Membership is DERIVED, never hand-kept: `python3 -m background.finding_classes --check` re-derives it from the filesystem and fails if a live finding belongs to this class and is not listed here, if a listed instance is missing from the archive or has come back to the root, or if the count above stops equalling the length of the list below.

## The 8 instances

- `WORKER_FINDING_A_POPULATION_TEST_IS_UNREACHABLE_BY_ANY_STEM_SELECTOR_2026-08-10.md` — LATENT
- `WORKER_FINDING_THE_BILL_SHOCK_CHURN_CAP_CANNOT_BE_REACHED_BY_ANY_CALLER_2026-08-31.md` — LATENT
- `WORKER_FINDING_THE_CITATION_CONTROL_NEVER_RUNS_ON_THE_COMMIT_THAT_RENAMES_A_FALSIFIER_2026-08-27.md` — LATENT
- `WORKER_FINDING_THE_CORRECTED_SENTENCE_NEVER_REACHED_THE_READER_AND_ITS_CONTROL_HAS_NO_CALLER_2026-08-15.md` — RECORDED
- `WORKER_FINDING_THE_MAPS_TWO_CONTROLS_ARE_UNREACHABLE_FROM_THE_MAP_2026-08-14.md` — RECORDED
- `WORKER_FINDING_THE_MEMORY_GOVERNOR_ENTERED_PRESSURE_LOST_TWO_PROCESSES_AND_RECOVERED_WITHOUT_SAYING_A_WORD_2026-08-24.md` — LATENT
- `WORKER_FINDING_THE_PASS_THROUGH_IC_CUSTOMER_PRODUCES_NO_RECORDS_AND_NO_GATE_CAN_SEE_IT_2026-08-27.md` — LATENT
- `WORKER_FINDING_TWO_UNIMPORTABLE_PHASE2A_MODULES_2026-08-09.md` — LATENT

## Cumulative cost, measured from the instances' own recorded evidence

**0 hours traced** across 8 instances. No instance in this class recorded a duration with evidence, so the traced cost is zero — which is a statement about the instances' measurement, not a claim that the class was free. No prose estimate is offered in its place.

## Refused consolidation — out of lane, still live

These documents match this class but carry a different lane. They are NOT archived and NOT superseded: severity is lane-scoped, so filing them here would remove their own lane's finding while recording it under `H_harness`.

- `WORKER_FINDING_THE_WORLD_KNOWS_HOW_EACH_HOUSEHOLD_PAYS_AND_BILL_SHOCK_IS_THE_ONE_ORGAN_NOT_TOLD_2026-09-01.md` — lane `W2_customer_generator`

## Disposition

**Decision:** OPEN
**Taken:** 2026-09-01
**At:** 8 instances
**Because:** THE CHEAPEST-LOOKING CLASS IS NOT CHEAP. It reads 0.0 recorded episode-hours, and that
is a statement about its instances' measurement habit and nothing else: the second cost term added
today reads **14 persisted-days** off the same documents — *`resource_headroom` sat unwired for
nine days*, *the code/artefact gap was unguarded again for five days* — and three instances arrived
in the last seven days. Ranked on recorded hours alone it would have sorted last of the drawable
five. That is the single clearest piece of evidence that the old cost measure ranked classes by how
well they measured themselves.

The closing mechanism is *a reachability check on every control*. It exists only in fragments and
each fragment is narrower than the class: `tests/architecture/test_a_cited_constant_has_a_caller.py`
(2026-08-28) covers money constants that cite a source, which is one of the eight instances at most;
`background/stall_class_register.py`'s G2 (a named detector that no longer imports raises) covers
detectors named in one register. Neither reaches *a population test is unreachable by any stem
selector*, *the map's two controls are unreachable from the map*, *two unimportable Phase-2a
modules*, or *the bill-shock churn cap cannot be reached by any caller* (2026-08-31, the newest).

**And the nearest thing to a general mechanism is itself under a live finding**:
`WORKER_FINDING_THE_REUSE_CONVENTION_MANUFACTURES_FALSE_CALLERS_2026-08-28` is open in the staging
root and says the caller convention produces callers that do not call. A reachability control built
on that convention would go green on exactly the population it is meant to catch. **Establishing
what a real caller is, is therefore the prerequisite work here, and it comes before building the
control.**
**Re-opens if:** n/a — OPEN is the drawable state.

---

Generated by `background/finding_classes.py` (atom `OPS10_finding_class_consolidation`). Regenerate with `python3 -m background.finding_classes --render`; verify with `--check`. The `## Disposition` section, if any, is written by hand and carried through a re-render verbatim — `background/class_debt.py` reads it to decide whether this class is still work, and ranks it in the draw by what it has cost.
