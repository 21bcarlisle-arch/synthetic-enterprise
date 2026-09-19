# PRE-REGISTRATION — the six unjudged tied pointers, before their referents are probed

**Severity:** LATENT · **Lane:** H_harness

A pre-registration, not a finding: it records predictions whose subject is the six unjudged tied
pointers. LATENT carries the state it found — six published pointers whose direction nothing in
the tree could check. The result that settles it, and says where this document was wrong, is
`SEAT_RESULT_THE_TIED_POINTERS_DIRECTIONS_ARE_JUDGED_AND_ALL_SIX_UNREGISTERED_ONES_WERE_FALSE_2026-09-19.md`.

Written 2026-09-19, BEFORE the numeric referent probe exists
and before any direction in the tied half of
`tests/tools/test_the_value_arms_pages_undriven_pointers.py` has been measured. Filed so the
result below cannot be read as a prediction made after the answer.

## The premise, re-measured at draw time

`87c485285` is an ancestor of `origin/main`. It landed the tied half of the census judging HOMES
only. The direction leg is still absent, so the premise is NOT spent. Measured today against the
tree: the census puts **10 literals in the tied half and 17 in the untied half**. Four tied rows
carry a `_REFERENTS` entry; **six do not**. (The file's own docstring says eleven and seven — stale
by one, corrected in the same landing.)

The duplicate-claim note names
`the-tied-pointer-censuss-direction-leg-needs-a-referent-probe-that-can-mark-a-number`, which is
this item's own id; `.seat_work_in_hand.json` does not exist on the shared tree and the only
matching process is this invocation. No rival. Carrying on with the work.

## The reading order, read off the door (not declared)

`arms-legs-first` 0 · `arms-headline` 1 · `arms-redraw` 2 · `arms-blind-envelope` 3 ·
`arms-published` 4 · `arms-market` 5 · `arms-departure` 6 · `arms-realised` 7 · `arms-household` 8 ·
`arms-composition` 9 · `arms-split` 10 · `arms-errorbar` 11 · `arms-decisions` 12 · `arms-sample` 13
· `arms-method` 14 · `arms-inference` 15 · `arms-svt-belief` 16 · `arms-note` 17.

## What each of the six points at, and what I predict the probe will say

Landing fields are measured (a build over today's artefacts). Referents and directions are NOT.

| # | symbol:line | phrase | lands in | referent I will register | predict |
|---|---|---|---|---|---|
| 1 | `_leg_in_this_world`:9444 | "the figure above" | `.current_world.selection_leg.verdict_withheld_because` | `.current_world.selection_leg.figure_gbp` (NUMBER) | **DEFECT — same, not above** |
| 2 | `WITHDRAWN_CLAIMS`:4299 | "the choosing figure below" | `.withdrawn_claim.note` | `.current_world.selection_gbp` (NUMBER) | **DEFECT — above, not below** |
| 3 | `_control_leg_agreement`:5588 | "the control row above" | `.method_skill.fixed_horizon.the_control_leg_agreement.sentence` | the control leg's own row (STRING) | **DEFECT — same, not above** |
| 4 | `_POPULATION_REPAIR_BIAS_NOT_A_GAIN`:10492 | "the figure above" | `.current_world.selection_leg.population_repair_bias.clause` | `.current_world.selection_leg.figure_gbp` (NUMBER) | **DEFECT — same, not above** |
| 5 | `_population_repair_bias`:10581 | "the figure above" | same field as 4 | same as 4 | **DEFECT — same, not above** |
| 6 | `_population_repair_bias`:10595 | "the figure above" | same field as 4 | same as 4 | **DEFECT — same, not above** |

**Six of six predicted false.** The arithmetic that makes me say so, and it is arithmetic and not a
measurement: 1, 4, 5 and 6 all land in the block the door renders from `current_world.selection_leg`
and say "above" from `#arms-legs-first`, which is position 0 — there is nothing above it; 2 says
"below" from `#arms-note`, position 17, the last region the door declares; 3 names a row published
inside its own block. **Each is one side of a two-sided measurement and neither side has been
probed, so none of them is a defect yet.** The referent's homes are the half I do not know, and the
honest ways I could be wrong are all of the same shape: a referent that renders in MORE than one
region, so that some home really is above or below the sentence; a number the door renders in a
region I have not thought of; or a referent that renders NOWHERE, which is a different red with a
different remedy (name the subject, or give the field a door).

## The instrument I have to build first, and the way it can lie

Five of the six referents are NUMBERS. Both halves of this file locate a referent by PREFIXING a
string marker onto its value, and prefixing a float changes what the door does with it — `gbp()`,
`signed()`, `toFixed`, `toLocaleString` — so the existing probe would measure a page nobody
publishes. The numeric probe is therefore a **two-perturbation difference**: set the number to two
distinct distinctive values of the same sign and the same order of magnitude, render both, and take
the regions whose text DIFFERS.

Why a difference of two perturbations rather than one perturbation searched for its formatted
forms: searching for formatted forms requires this rung to know the door's formatter, which is
exactly the opinion `_REFERENTS` refuses to hold about anchors. And why two perturbations rather
than perturbed-against-real: a number that gates a BRANCH changes prose that does not render it,
and real-vs-perturbed cannot tell that from a home. Two values on the same side of every threshold
near the original take the same branch, so a branch flip cancels and only regions that render the
DIGITS survive.

**The stated over-report this design accepts:** a region rendering a figure DERIVED from the number
also differs, and will be counted a home. That is the conservative direction for a direction check
and it is said here rather than discovered later.

**The two ways it can lie, and both are loud rather than silent.** A probe that goes blind returns
no homes, and `_direction_defects` already reds on a referent that renders nowhere. A probe that
saturates returns every region, and a direction cannot hold from all of them at once. The silent
failure is a PARTIALLY wrong home set, which is what the mutation leg has to close: a number the
door demonstrably renders must come back WITH a home and a number no door reads must come back
with NONE, driven side by side on one build.

## What "done" means for this item

Direction is switched on for the tied half: all ten tied rows registered in `_REFERENTS`, a tied
direction leg that runs `_direction_defects` over them, a numeric referent probe, and a mutation
leg that proves the numeric probe can tell a rendered number from an unrendered one. Any defect the
measurement finds is repaired **in the producer** — the precedent is `_against_the_superseded_panel`
and `_skill_sample_size_explanation`, where the word was corrected in the producer rather than the
claim weakened here. Mechanism and repairs land together by necessity: `pre_commit_test_gate`
maps a changed test file to itself, so a red direction leg cannot land beside its own repair.
