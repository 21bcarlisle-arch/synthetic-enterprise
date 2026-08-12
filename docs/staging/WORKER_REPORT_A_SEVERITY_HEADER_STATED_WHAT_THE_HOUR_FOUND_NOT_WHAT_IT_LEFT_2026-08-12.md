# WORKER REPORT — a severity header states what the Hour FOUND, and nothing ever re-read it

**Severity:** RECORDED · **Lane:** H_harness

**Date:** 2026-08-12 · **Draw:** RUNG 1c (OPS12 clause 3), lane `H_harness`, 14 live BLOCKING findings
**Subject:** `background/finding_severity.py` — the parse both refusal mechanisms (OPS11, OPS12) read
**Outcome:** the release exists now and is checked; H_harness goes 14 blockers → 8, each release
carrying a named falsifier that was RUN GREEN before the line was written.

---

## The finding, from the population rather than from one document

The rung named fourteen blockers in one lane. Reading all fourteen: **eight are Expert-Hour
reports that repaired their own defect inside the same document** — "Mechanised, not exhorted",
"R15 both ways", "no published figure moved" — and one, `THE_SHARED_RULE_REACHED_TWO_OF_THREE_
SWEEPS`, whose repair (`COUNTERFACTUAL_KNOB_ROUTE`, `book_recon_drift_grid`,
`predict_recon_floor_from_constants`) is in HEAD and whose own suite runs **442 passed**.

The instrument each of them named as untrustworthy was trustworthy again *before the document was
saved*. The header said BLOCKING because that is the state the Hour **found**, and nothing in the
machine ever re-read it.

**The consequence is the sharp part, and it is a perverse gradient.** Clause 2's refusal is
lane-scoped and its release ("until it is repaired, or until the limitation is explicitly recorded
and accepted") had **no machine-readable form**. So a lane's blocker set could only ever GROW: the
more honestly one atom audited itself — and `H_GAP_fabric_belief_truth_gap` has run fifteen Expert
Hours, each finding something and each holding its own level — the more completely it froze twelve
other atoms' lane. Self-scrutiny was taxed, and the tax fell on the neighbours.

## Why not the release that was already in the module

`_REPAIRED_RE` already stands the by-construction namer down on the words FIXED / landed / cleared
/ accepted anywhere in a forty-line header. Using it to release a BLOCKER would have been the
defect this project has already filed against itself — *the by-construction gate is silenced by an
ordinary word*, and *G6 fires on the word "none"*. An Hour whose header mentions that something
else landed would have cleared its own lane. The higher the stakes, the less a loose pattern is
allowed.

## Mechanised, not exhorted

**`**Discharged:** `tests/x/test_y.py::test_z`, `tools/y.py` — one line saying why`**, in the
header block, fail-closed at every step:

* at least one artefact must be a **test node** whose file exists *and* whose text defines that
  node. A discharge is a claim that a defect cannot recur; the only evidence of that shape this
  project accepts is a named, runnable falsifier. A discharge naming only a source file proves the
  author typed a path — which is what a vacuous control looks like.
* **every** named artefact must exist. One missing voids the whole claim.
* a claim that fails any of this **does not release**: the severity stands exactly where the
  header put it, and `false_discharges()` names the document. A malformed release that released
  silently would be strictly worse than no release at all — the author has stopped watching.

**What it does not prove, stated because an overclaimed control is the class above:** it proves a
named falsifier EXISTS and is addressable, never that the falsifier is a good one or that running
it passes. Reading the cited test is still a human act.

## R15 both ways — three new mutations, each killing a named test

| mutation | kills |
|---|---|
| the "no test node" branch releases anyway (**vacuity**) | `test_a_discharge_naming_no_test_node_does_not_release` |
| the artefact-existence check dropped (**fail-open on a typo**) | `test_a_discharge_naming_an_artefact_that_does_not_exist_does_not_release` |
| an invalid claim reads the severity down anyway (**silent release**) | `test_an_invalid_discharge_leaves_the_severity_where_it_was` |

Proven it can PASS as well as fail (not an always-red detector):
`test_a_valid_discharge_reads_a_blocking_document_down_to_recorded`.

**R11, no orphan transitions — the release is tested where it MEANS something,** not only in the
parser: `test_a_validly_discharged_blocker_stops_blocking_its_lane` and
`test_a_discharge_the_filesystem_refuses_keeps_blocking_its_lane` drive
`supervisor._blocking_lane_draw` itself on injected staging roots.

## The disposition, individually — never a bulk pass

Six discharged, each falsifier run green before the header was written (5 selected nodes: `5
passed`; the shared-rule file: `442 passed`):

| finding | falsifier |
|---|---|
| `A_GATE_COMPARED_A_POINT_ESTIMATE_TO_ITS_BAND` | `test_the_GATE_REFUSES_A_POINT_ESTIMATE_WHOSE_INTERVAL_STRADDLES_ITS_BAND` |
| `A_PER_PREMISE_PROMISE_AUDITED_BY_THE_PANEL_MEAN` | `test_a_PER_PREMISE_PROMISE_IS_NOT_AUDITED_BY_THE_PANEL_MEAN` |
| `THE_MONEY_VERDICT_WAS_A_SUM…` | `test_a_MONEY_VERDICT_BOUGHT_BY_THE_ERROR_BAR_is_named_as_such` |
| `THE_RESAMPLE_GUARD_COUNTED_THE_PANEL…` | `test_the_ARTEFACT_EVIDENCE_COUNT_COUNTS_EITHER_CHANNEL_NOT_JUST_THE_MIRRORS` |
| `A_LEAVE_ONE_OUT_JUDGED_BY_THE_GATES_OWN_VERDICT…` | `test_the_SWITCH_COST_is_measured_on_the_homes_that_DID_NOT_force_it` |
| `THE_SHARED_RULE_REACHED_TWO_OF_THREE_SWEEPS` | `test_every_counterfactual_knob_reaches_the_one_saturation_rule` |

**Eight deliberately left BLOCKING, because they are open:**
`THE_REFRESH_COMMAND_CAN_CHANGE_THE_POPULATION` says **Status: OPEN, queued** in its own header and
has a *"What would close it (not built here)"* section; `DIRECTOR_OBSERVATION_PUBLISHED_SURFACE_
NAV_AND_STAMPS` has an unactioned *"What is asked"*; `THE_INSTRUMENT_CANNOT_RESOLVE_ITS_OWN_LATENCY`
minted rather than fixed; `THE_ACCURACY_VERDICT_HAD_NO_ERROR_BAR` and `A_FIDELITY_TERM_THAT_IS_ALL_
DENOMINATOR` were not evidenced to a specific falsifier in this tick and are **not** discharged on a
guess; the three `CLASS_*` documents inherit the maximum severity of their members and cannot be
discharged one by one at all. *Not discharged* here means *not yet evidenced*, never *not blocking*.

## R12 / R13

No published figure moved and none was recomputed. This tick changed what the queue can say about
itself, nothing the company reports.

## Leads

1. **The remaining two undischarged Hours need their falsifier identified**, which is a reading
   task on `tests/harness/test_premise_two_level.py`, not a build.
2. **A class document has no discharge path at all.** `CLASS_*` inherits the max severity of its
   members, so it clears only when its members do — correct, but nothing yet re-renders a class
   document when a member is discharged. Today `finding_classes` drops RECORDED members from
   membership, so the count moves; whether the BLOCKING inheritance recomputes on discharge is
   unproven.
3. **Nothing measures the age of a blocker.** A lane frozen for a week by a document nobody has
   re-read is exactly this defect wearing a longer coat, and the digest does not report it.
