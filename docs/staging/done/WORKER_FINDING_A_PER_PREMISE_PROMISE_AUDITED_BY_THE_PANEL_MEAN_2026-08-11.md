# WORKER FINDING — a per-premise promise was audited by the panel mean, so a breach on nine of two hundred homes read as faithful

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/harness/test_premise_two_level.py::test_a_PER_PREMISE_PROMISE_IS_NOT_AUDITED_BY_THE_PANEL_MEAN` — the per-premise promise is audited per premise; reinstating the mean fires this by name
<!-- DISCHARGED 2026-08-12 by a worker tick drawn at RUNG 1c. This document reported a
     defect AND its repair in the same breath; its severity header stated the state the
     Hour FOUND, and nothing re-read it afterwards, so it went on refusing level-raises in
     H_harness after the instrument it named was trustworthy again. The falsifier below was
     RUN GREEN before this line was written. -->

**Atom:** `H_GAP_fabric_belief_truth_gap` (L2→L3 draw, worker tick)
**Date:** 2026-08-11 · **NINTH EXPERT HOUR** · disposition **QUEUE** (recorded, mechanised, no interrupt)
**Verdict: IT FOUND SOMETHING, SO THE LEVEL STAYS 2.**

## The directed question

The eighth Hour left this opener verbatim:

> the REGISTER half of the gate is still a bare point comparison, and it is zero by
> algebra on every branch either published population takes — whether a term that
> cannot move can carry half a gate is the third Hour's own unfollowed note.

The expected answer was the eighth Hour's own repair copied across: give the register
channel the interval the money channel got. **That is not the defect, and the measurement
is what says so.** The register channel's fallback-branch statistic is a weighted mean of
per-premise relative errors to which *every* premise contributes, so it concentrates fast
— over 150 random subpanels of a fallback population it was unresolved on 3 of 22 at n=20
and 0 of 46 by n=50, where the money channel's share (carried by the 18 of 200 homes that
move at all) was routinely unresolved at n=100. Copying the mechanism would have been
cargo.

**The defect is one level up from the interval: the term is a MEAN, and the promise it
audits is UNIVERSAL.**

## The defect

`_reflect_level` promises, in its own docstring, "same ABSOLUTE error, opposite sign" —
about **every premise**. On the level-preserving branch, which is the branch **both
published populations take**, the honest value of the register-fidelity term is exactly
zero and any breach anywhere is a breached promise.

The gate audited that with `panel_mirror_register_infidelity`, a panel MEAN, against
`MIRROR_FIDELITY_BAND = 0.05`. That reads *"the average home may move 5%"*, and on two
hundred homes it means *"nine homes may move completely."*

The third Hour closed the **cancellation** in this term (a difference of aggregates became
an aggregate of differences). It left the **dilution**, which is the same class one step
on: an aggregate of differences is still an aggregate.

## Observed, with evidence, by running it — the fourteenth time on this atom

Every figure below came out of the tool on this atom's own two published populations, by
injecting the defect at the site it would actually occur (the reflection call inside
`panel_mirror`), never by hand-building a mirrored panel.

**Vector 1 — the PARTIAL FALLBACK, the confound the whole-panel rule exists to forbid**
("a panel reflected two different ways on two subsets is two instruments"):

| population | homes reflected by the WRONG RULE that still certify | gate reading |
|---|---|---|
| drawn 200 | **9 of 200 (4.5%)** | 0.0000 → under the 5% band |
| authored 15 | **4 of 15 (26.7%)** | under the band |

**Vector 2 — the WRONG PIVOT** (reflecting through the inferred prior instead of the
register prior; a one-identifier bug): **65 of 200 premises (32.5%)** on the drawn
population, the worst of them moving its own home's error by **1,825%**, with the gate
reading **4.50%** and certifying the mirror.

**And the failure signature, which is why this is a class and not a tuning question.**
Hold the defect FIXED at one wrongly-reflected home and grow the panel:

| n | 15 | 30 | 50 | 100 | 200 |
|---|---|---|---|---|---|
| mean (the gate) | 0.0022 | 0.0013 | 0.0008 | 0.0003 | 0.0002 |
| worst per-premise breach | 15.4% | 15.4% | 15.4% | 15.4% | 15.4% |

**SENSITIVITY FALLS WITH N.** The fourth Hour found a verdict rule that was FLAT in N and
the fifth one DECOUPLED from it; this is the third sibling and the worst-behaved of the
three, because it is monotone in the *wrong* direction — the control guarding this
instrument gets blinder exactly as the population it guards gets better.

**What it costs a reader.** A certified mirror that does not flip publishes "no
composition effect" as a finding. On a panel where a subset was reflected by the wrong
rule, that finding is made by an instrument that is two instruments.

## Mechanised, not exhorted

* `_register_breaches` — the promise measured **per premise and never averaged**, one
  entry per home, carried on the verdict as `panel_mirror_register_breaches`.
* `panel_mirror_register_worst_breach` — a promise is audited at its **worst violation**.
  Its response to a fixed defect does not fall with N.
* `panel_mirror_register_breaching_premises` — a **COUNT**, published beside the worst
  home, because one wildly-moved home and forty mildly-moved ones are different events
  that a share renders as the same small percentage.
* `panel_mirror_register_channel` — the gate, **split by branch**, because the two
  branches make different promises:
  * `level_preserving` → the promise is EXACT, so the **worst breach** decides it against
    `REGISTER_PRESERVATION_TOLERANCE`;
  * `log_preserving_fallback` → no such promise is made (the ratio error is what is
    preserved, so every premise moves by design), so the **mean against
    `MIRROR_FIDELITY_BAND`** is kept unchanged. **A promise is audited at its worst
    violation; a characteristic is summarised at its mean.**
* `REGISTER_PRESERVATION_TOLERANCE = 1e-9` — a **SIXTH constant**, not a reuse of
  `MIRROR_FIDELITY_BAND` (this atom's own recurring class: one constant, two subjects).
  It is a float-noise floor, not a tolerance for real disturbance, and it is calibrated by
  measurement with six orders of headroom either side: the clean reflection's worst
  per-premise disturbance on the published rows is **1.788e-15**, and the smallest
  disturbance any injected defect produced was **15.4%**.
* The **disclosure** is keyed to the channel and names the promise the branch actually
  makes — "1 of 20 premises moved, the worst by 10.0% of that home's own error (the panel
  MEAN reads 0.06%, which is the breach divided by the panel and is why it is not the
  gate)". The mean is printed as the thing that *hid* it, never as the ground for the
  refusal. That is the eighth Hour's own class (a disclosure inheriting the statistic its
  gate stopped using) applied *before* it could happen rather than after.
* The row carries the worst breach, the count and the channel verdict unconditionally
  (R11 — the door renders the row, and a reader who sees only a percentage cannot tell
  nine broken homes from none).

**One-directional by construction:** the worst breach is never below the mean, so on the
level branch this can only take certification away. No verdict this gate released before
is newly released now.

## R15 — seven source mutations, each firing its own named test

md5 byte-clean restore verified before and after every run
(`745b02f2385887d7a81f829003dd6b43`), 9 green on the same selection unmutated:

| mutation | fires |
|---|---|
| the level branch gated on the panel MEAN again (**the exact defect reinstated**) | 5 tests, incl. the per-premise and falls-with-N tests |
| the level tolerance widened to `MIRROR_FIDELITY_BAND` | the noise-floor test |
| the FALLBACK branch put on the worst-case shape | the always-red test |
| an empty panel reads as "the reflection disturbed nothing" (fail-open) | the raises test |
| the premise-order guard removed | the raises test |
| the zero-error corner made faithful-by-default | the infinite-breach test |
| the disclosure keyed back to the panel mean | the sentence test |

**Proven not always-red on BOTH branches, and the fallback half was searched rather than
assumed:** a fallback panel whose register the log form barely moves (80 homes, a register
accurate to 1%, one rogue certificate forcing the fallback) still certifies at a mean of
0.0306 while its worst breach is 0.600 — which is exactly the panel the worst-case shape
would have wrongly refused.

**And the suite caught the repair's own inherited check within the hour.** The existing
zero-corner test constructed `panel_mirror_register_mad=0.01` to force the gate red. After
the move it asserted nothing about the live gate and went on passing — the eighth Hour's
class landing in the *suite* rather than in a sentence. Re-pointed at
`panel_mirror_register_breaches`, with the old assertion kept and inverted so the file
records that the mean has no gate to fail on that branch any more.

## No published figure moved — checked, not asserted

Both rows re-taken on their own declared population
(`--seed 17 --unit-rate 7.4 --population 200 --population-seed 17`, read back off the row
per the refresh_args mechanism) **after** the code landed, which is the only ordering under
which the row comes out current: gap **0.4269 / 0.4042**, forgone **GBP 548,919 /
451,832**, misranked **10 / 11**, declined **89 / 73**, two-level still **RED on
`L2.4_scale_spread_p90_p10`** (the birth condition holding, not a regression). Both rows
read `panel_mirror_register_channel == "attributable"` and `attributable=False` before and
after — the money channel is still what refuses them.

The whole ledger diff is `measured_at`, `run_git_commit` and the three new fields. W2_11
re-stamped itself concurrently via its own live writer and is not this tick's change.

Suites: **325 passed, 2 xfailed** across `test_premise_two_level.py`,
`test_couple_fabric.py`, `test_gap_ledger_reconciler.py` and
`test_lcl_household_anchors.py`; `epistemic_verifier` **PASS, 553 files**.

## R10 classes

1. **A UNIVERSAL PER-PREMISE PROMISE CANNOT BE AUDITED BY A PANEL MEAN.** Fixing the
   cancellation in such a term does not fix the dilution — an aggregate of differences is
   still an aggregate. Failure signature: **sensitivity falls with N**.
2. **A TOLERANCE BAND ON AN EXACT CLAIM IS THE WRONG SHAPE OF THING**, not a loose
   setting. Where a quantity is zero by construction, the only honest constant is the
   noise floor; a 5% band there converts "no premise may move" into "nine homes may".
3. **SIBLING (confirmed again):** where one control serves two branches that make
   different promises, one constant and one statistic cannot serve both.

## Opener for the TENTH Hour

`panel_mirror_weight_artefact` is called a **SHARE** and is not bounded by 1 — the authored
row reads 80% on [73%, 122%] — because the sign flip can oppose the re-composition per
premise. Readings over 1 are real and informative and the word "share" does not admit them;
the eighth Hour named this and did not take it, and it is now the oldest untouched item on
this atom. **Also named, not touched:** `panel_mirror_register_infidelity` is retained and
published as the diluted compound; it is documented as not-the-gate, which is the same
shape as `panel_mirror_relative_infidelity` two Hours before it, and this atom now
publishes three retained-but-superseded fidelity statistics whose only defence against
being misread is their docstrings.
