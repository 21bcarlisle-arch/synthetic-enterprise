# [SEAT PRE-REGISTRATION] What counting recurrence in the class debt must show

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS10_finding_class_consolidation`
**Filed:** 2026-09-02, BEFORE the change, on the director's instruction: *"don't leave the draw
ordering wrong for long — a class repaired on sight twenty times reading as zero debt is the exact
thing the measure exists to prevent."*

## The change

`class_debt` derives its population from `finding_classes.derive_memberships`, which excludes
RECORDED documents — correct for CONSOLIDATION, wrong for RECURRENCE. A second count is added,
`recurrence`, which includes instances that were fixed on sight, and it drives the two decisions
that are actually about how often the shape happens: `still_accruing` and the `REOPEN_AFTER_INSTANCES`
re-arm. The consolidated instance list is untouched.

Population, stated exactly, because getting this wrong is what produced the claim being corrected:
consolidated instances + out-of-lane + RECORDED-in-root declaring the class + archived documents the
classifier assigns to the class — **minus** the two exclusions the register's own rules already
apply, externally-authored documents and self-clearing alarm documents.

## The predictions, filed before the code runs

**P1 — the counts.** Measured by hand on 2026-09-02 before any implementation:

| class | consolidated | recurrence |
|---|---:|---:|
| publish_gate_and_wedge | 56 | 86 |
| controls_that_cannot_fail | 27 | 51 |
| uncommitted_and_orphaned_work | 21 | 40 |
| measurements_that_mirror | 8 | 16 |
| no_caller_and_never_runs | 9 | 15 |
| figures_on_a_superseded_clock | 3 | 4 |

The implementation must reproduce this table. A different number means the implementation's
population is not the one described above, and the difference is a defect in one of them.

*(`no_caller_and_never_runs` is 9/15 rather than the 8/14 measured an hour earlier: the
daemon-staleness finding was consolidated into it in between. Recorded so the discrepancy is not
mistaken later for a measurement error.)*

**P2 — the draw ORDER does not change.** Both orderings are
`publish_gate > controls_that_cannot_fail > uncommitted > measurements ≥ no_caller > superseded`.
**This is the prediction most worth filing, because I published the opposite yesterday** and it was
wrong for a nameable reason (I counted a population without the exclusions its own register applies).
If the implementation re-orders anything, my correction was itself wrong and the original claim
stands.

**P3 — no class changes its draw VERDICT today.** Every register is already OPEN or drawn, so a
larger count cannot promote one that is not already promoted. The change should therefore be
invisible in today's queue and visible only in what it makes possible tomorrow.

**P4 — the value is entirely in the re-arm.** `REOPEN_AFTER_INSTANCES` keys on the count. With
recurrence counted, an ACCEPTED decision is overtaken by instances that were fixed on sight, which
today it cannot be. Nothing else about the draw should move.

## What would refute the change

* P1 not reproduced → the population is not the one described; do not ship the number.
* P2 refuted → yesterday's correction was wrong and must be corrected again, in the same document.
* Any class going from not-drawn to drawn today → P3 was wrong and I did not understand the
  verdict logic I was editing.

## What this cannot show

Recurrence counts DOCUMENTS, not incidents. Two documents about one condition (the fork-orphan alarm
filed on consecutive days is the observed case) count twice, and a defect that recurred without
anyone filing it counts zero. The hand sample put the residual misclassification rate at roughly
25% of the archived additions after the rule-based exclusions, mostly reports ABOUT a class counted
as instances OF it. So this is a FLOOR on recurrence with a known upward bias, and it must be
reported as one — never as a count of how many times the shape actually happened.

---

# RESULT, 2026-09-02, after the change. Two of four predictions refuted.

**Every prediction above is left exactly as filed.** A prediction corrected after the answer is
not a prediction, and both of these were wrong in ways worth keeping.

| class | predicted consol / recur | **actual consol / recur** |
|---|---:|---:|
| publish_gate_and_wedge | 56 / 86 | **56 / 86** ✓ |
| controls_that_cannot_fail | 27 / 51 | **27 / 51** ✓ |
| uncommitted_and_orphaned_work | 21 / 40 | **21 / 41** ✗ |
| measurements_that_mirror | 8 / 16 | **11 / 20** ✗ |
| no_caller_and_never_runs | 9 / 15 | **12 / 19** ✗ |
| figures_on_a_superseded_clock | 3 / 4 | **4 / 6** ✗ |

## P1 — REFUTED for four of six, and both causes are my measurement, not the code

**Cause 1: I predicted the wrong attribute.** `ClassDebt.instances` already includes out-of-lane
instances — my own fix from 2026-09-01. My hand table used `instance_names()`, which does not.
Adding the out-of-lane counts (measurements +3, no_caller +3, superseded +1, the rest 0) accounts
for the whole consolidated column exactly.

**Cause 2: the prediction's prose and the prediction's table disagreed, and the code followed the
prose.** The population above says *"RECORDED-in-root declaring the class + archived documents"*.
My hand count scanned only the archive. Four classes hold a RECORDED document in the root — the
findings filed today — and each contributes the missing +1.

So P1 fails against a table I measured on a narrower population than the definition I had written
one paragraph above it. **The definition was right and the measurement of it was not.** Nothing in
the implementation is wrong, which is exactly what a refuted P1 has to be checked for rather than
assumed.

## P2 — REFUTED, at one adjacent pair, and my correction of yesterday was itself wrong

    consolidated ranking : publish_gate > controls > uncommitted > no_caller > measurements > superseded
    recurrence ranking   : publish_gate > controls > uncommitted > measurements > no_caller > superseded

`measurements_that_mirror` (11 → 20) and `no_caller_and_never_runs` (12 → 19) **swap**. So:

* the ORIGINAL claim — that `uncommitted` would overtake `controls_that_cannot_fail` — stays
  refuted; and
* yesterday's CORRECTION — *"the order is identical"* — is refuted too, by the RECORDED-in-root
  leg my hand count omitted.

Wrong twice, in opposite directions, and the pre-registration is what caught the second. That is
the whole argument for filing one.

**And a distinction I collapsed in the prediction itself.** There are two orders here and I wrote
"the draw ORDER" as though there were one. `order_key` still leads with `instances`, deliberately
and unchanged: the consolidated count is a set of deliberate assignments, while recurrence carries
a measured ~25% misclassification bias, and ranking the draw on the noisier number would be paying
for reach with accuracy. **The DRAW order does not change. The RECURRENCE ranking does.** Naming
which one I meant was owed before measuring it.

## P3 — HELD

All six registers were already drawn (`still accruing, no recorded decision`) and all six still
are. No class changed its verdict, so the change is invisible in today's queue — as predicted.

## P4 — HELD, and it is now the whole justification

Nothing else moved. The value is entirely in the re-arm: `REOPEN_AFTER_INSTANCES` now reads
`max(instances, recurrence)`, so an ACCEPTED decision can be overtaken by instances that were fixed
on sight. Under the consolidated count it could not be, and most instances are fixed on sight.
