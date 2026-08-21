**Severity:** LATENT · **Lane:** H_harness

# FINDING — the publish gate has no way to learn its scope is over budget except by timing out a live cycle, and one file in that scope costs more than the whole publish cadence

**Found:** 2026-08-21, scheduled worker tick, while discharging
`WORKER_FINDING_A_PUBLISH_TIMEOUT_IS_RECORDED_AS_A_TEST_REGRESSION_AND_THE_SCOPE_CANNOT_MEET_ITS_CAP_2026-08-21.md`
(BLOCKING). That document made three recommendations. Its first is repaired and its BLOCKING
half is closed; recommendations **2 and 3 are not built**, and this document exists so that fact
is on the register rather than buried in a discharge line on an archived record.

## Class registration

`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12`

**Where this is visible.** As a class member it is archived on arrival and the class document in
the staging root carries it — that is the consolidation's design, not an oversight. The
consequence is worth stating plainly: `scan_staging_root` reads the root only, so this file is
NOT independently drawable, and the LATENT severity it carries reaches a reader through the class
document's instance list. If recommendation 1's repair had not closed the BLOCKING half, this
would be the wrong home for the residue.

**Intended rank (P-1):** H_harness LATENT band. Not BLOCKING: no control now lies about its own
verdict and no published figure is wrong — what remains is that the gate is expensive and
discovers that fact the most costly way available to it.

## What is owed, and the evidence it rests on

Both items are quoted from the parent finding, whose measurements were `observed-with-evidence`
at 2026-08-21 16:10-16:25Z. Nothing new was measured for this document, and the notes below say
which numbers have since moved.

### 1. Repo-invariant tests run inside the publish gate, on the publish cadence

`tests/background/test_derived_artefact_register.py` was killed at 300s without completing, and
again at 280s for its staleness class alone. Its staleness check shells out to a `--check`
entry point for each registered artefact, and one of those was independently observed holding
~100% CPU for 3m05s inside the live publisher.

It asks whether three committed markdown projections are current — a repo invariant, true or
false at commit time. The director named the remedy and it is not deselection: *"by deciding
what genuinely must run before a publish and what belongs somewhere else entirely, on its own
cadence."*

**What has moved since the parent was filed:** the 300s cap that made this acute was reverted at
`9dc57daee` (bound back to 3400s, from 2× the observed max of 1674s over 310 recorded runs), so
this is no longer wedging anything. The gate still takes ~20 minutes on a 5-minute cadence, which
is the director's original objection: *"A check that takes 75 minutes in a repo changing every 15
isn't verifying the current state, it's reporting on the past."*

### 2. The cap fails on the RUN, never on the SCOPE

The bound can only be discovered to be too small by killing a live publish. A pre-flight — the
resolved scope's own last measured wall time against the bound — would name the offending file
instead of the cycle. Additive; nothing depends on it.

**Why this is the durable half.** The bound has now been re-derived seven times (600, 1800, 2600,
2900, 3600, 4500, 300, 3400). Six of those were honest measurements of a subject that kept
growing underneath them. A scope-side check is the only one of the three items that makes the
NEXT growth visible before it costs a cycle.

## What is NOT owed here

The parent's recommendation 1 — a named kind for the publisher's own gate timeout, so a stopwatch
stops being filed as a test regression — is built, R15-proven with nine mutations, and its
falsifiers are named in the parent's discharge. Do not re-draw it.

## Reversibility

Item 1 moves test files between two lists and is a revert away. Item 2 is additive. Neither is a
one-way door.
