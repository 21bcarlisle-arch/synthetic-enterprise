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

## ADDENDUM 2026-08-21 16:45Z — two corrections to the numbers above, and one item now built

Measured by the next scheduled tick, off `docs/observability/publish_gate_duration.jsonl` and
`ps` at 2026-08-21T16:43Z. Both corrections make the case for item 2 stronger, not weaker.

**1. The bound is derived from the survivors of the bound (`observed-with-evidence`).** The
`3400` at `9dc57daee` is 2× the maximum over *completed* runs — "median 1199s, p90 1384s, MAX
1674s over 310 completed runs". A run that exceeds the bound is KILLED, so it never completes and
is definitionally absent from that population. The two most recent real gate runs are
`2026-08-20T21:10:26 4503.5s outcome=timeout` and `2026-08-21T14:42:35 4503.7s outcome=timeout`,
both censored at the 4500s ceiling — i.e. the true runtime of each is ≥4503s, and NEITHER is in
the population that justified 3400. Filtering to `duration_seconds >= 300` gives 215 rows: median
1247.7s, max 4503.7s. A derivation that excludes every observation above the bound cannot
discover that the bound is too low, which is the same shape as item 2 one layer up — the record
learns the number is wrong only by a cycle dying.

This is a correction to a claim this project made in a commit message, not a new defect found
elsewhere: `9dc57daee` told the director the bound was "read from the RECORD of the thing that
actually runs". It was read from the part of the record that survived it.

**2. The step change is not scope growth, and the load is unrecorded.** Healthy runs on 2026-08-20
were 1320.8s, 1299.9s, 1246.3s, 1322.6s, 1302.9s, 1247.7s — then 4503.5s that evening. A 3.6×
jump between adjacent runs is not "a subject that kept growing underneath the bound". Observed at
16:43Z: THREE concurrent heavy pytest processes (the deadman's operational suite, the live
publish gate, and a previous tick's unattended inline gate-timing run launched at 17:14 local and
still running 34 minutes later), on a box with 15.9G total, 4455MB free and swap 100% consumed
(4095/4096MB). The series records no load, no concurrency and no memory figure, so seven
re-derivations of this bound have all been point estimates of a quantity that visibly depends on
a variable nobody wrote down. The orphaned timing run was killed at 16:44Z (it held no publisher
lock, and `tools/measure_publish_gate_subject_cost.py` exists precisely because timing a suite
into a contended box is refused there — this was the same mistake made ad-hoc).

**3. The director's third ask IS now built** — `background/suite_duration_watch.absolute_band`,
the run's raw duration against the measured 330s publish cadence, structurally unable to read the
ceiling. That is *"a limit on the absolute duration that fails loudly when crossed"*. It does not
close item 1 or item 2 of this finding and does not claim to: it makes the growth VISIBLE and
unsilenceable, where items 1 and 2 are what actually make the gate faster.

## What is NOT owed here

The parent's recommendation 1 — a named kind for the publisher's own gate timeout, so a stopwatch
stops being filed as a test regression — is built, R15-proven with nine mutations, and its
falsifiers are named in the parent's discharge. Do not re-draw it.

## Reversibility

Item 1 moves test files between two lists and is a revert away. Item 2 is additive. Neither is a
one-way door.
