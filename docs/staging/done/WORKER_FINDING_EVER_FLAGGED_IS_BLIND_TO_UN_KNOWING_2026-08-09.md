# WORKER FINDING — an EVER-FLAGGED population is structurally blind to the company UN-knowing something

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-09 (worker tick, during the D8 build)
**Class:** R15 — a control whose population choice removes the very failure a sibling atom exists to report
**Status:** measured, closed at the measure inside D8; filed here as the CLASS

## What happened

D11 fixed a real defect: the detection headline scored a belief held AT `as_of` against a truth
that does not move, so moving only the scorer's question date walked the published figure +70%.
The fix was to make the population EVER-FLAGGED — a case the company flagged at any date up to
`as_of` stays flagged. That is right, and the reasoning is right: a detection is a fact about the
day it happened.

One tick later, D8 needed to report the exact opposite fact. D10 had observed, case by case, that
a later ambiguous non-DD credit is allocated oldest-first onto a *failed* invoice, which then goes
quiet — the company had the arrears case and then lost it. Measured through the post-D11 headline:

    detection.missed_failure_rate   actual 0.0000   remittance-complete 0.0000   attributed 0.0000

The mechanism is live (34 of 347 detected arrears cases have left the company's arrears view by
`as_of`, all 34 attributable to the ambiguous-remittance channel) and the headline reads exactly
zero either way. Not wrong — **blind by construction**. Ever-flagged answers "did the company ever
know?", and un-knowing is unanswerable in that population's own vocabulary.

## The class

**A population change made to remove an artefact can also remove a real phenomenon, and the two
are indistinguishable from inside the fixed metric.** The fixed metric reports a stable, defensible
number; nothing fires; the finding simply stops existing on every published surface. The tell is
not a red control — it is a *sibling atom's evidence that no longer reproduces*.

This is close to, but not the same as, the recorded lesson that a chosen panel can flip the sign:
there, the population moved the answer. Here the population moved what the question *can be about*.

## What closes it

Not a change to D11 — the ever-flagged headline should stay ever-flagged. The un-knowing gets its
own measure, on the denominator it is about (`unpursued_arrears`: of the truly-failed cases the
company actually detected, how many has it stopped holding, asked of the company's own
reconciliation organ). Both are true at once and neither substitutes for the other.

**The transferable rule:** when a dimension's POPULATION is redefined to kill an artefact, name what
the old population could see that the new one cannot, and check whether any other atom's evidence
rested on it. If it did, that evidence needs a measure before the redefinition lands — otherwise a
finding is retired silently, by a fix, with nothing failing.

## Evidence

- `background/live_payment_triad.py` — `unpursued_arrears`, and the D8 attribution beside it
- `tests/background/test_live_payment_triad.py::test_d8_wrongful_non_pursuit_is_measured_where_the_headline_cannot_see_it`
  — asserts BOTH halves: the headline cannot see it (attributed == 0.0) and the atom's own measure can
- Map cells `D8_ambiguous_remittance_misdating` (build_note), `D11_detection_gap_is_recall_only`,
  `D10_detection_headline_is_single_channel` (discover_note — the case-by-case observation)
