**Severity:** RECORDED · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `EP13_adapter_carbon_intensity` · **Claim:** `the-ccgt-swap-ceiling-sizes-the-named-build-target-inside-the-shipped-model`

*Drawn by the dial-weighted self-refill on the maturity map; `W4_the_wall` is the atom's own lane. RECORDED rather than LATENT: nothing here is a defect awaiting repair -- it is a measurement whose result retires a build target, and the retirement is written into the atom's level-hold note in the same commit.*

# PREREGISTRATION — what the CCGT swap ceiling must show

**Filed 2026-08-31, BEFORE the instrument was run.** Atom: `EP13_adapter_carbon_intensity`, L2,
eleventh pass. Written so the run can refute it; a prediction filed after the answer is not a
prediction.

---

## The gap this exists to close

§14 of `docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` reported that the true half-hourly
FUELHH mix, put through NESO's own factor table, scores **0.9352 in 2024 against the shipped
reconstruction's 0.7425 — +0.193** — and that the ablation ladder puts almost all of the within-day
information in **CCGT**. It ended by naming L3's build target: *a publishable proxy for within-day
CCGT dispatch.*

**That +0.193 is not attributable to CCGT timing.** The oracle did not change one thing; it
replaced the whole arithmetic at once — factor mapping, denominator, fuel coverage, the must-run
block, coal's dispatch and the CCGT efficiency band all moved together, and imports left both
numerator and denominator. This project's own rule applies to its own instrument: *when a result
moves and more than one thing changed, you cannot attribute it.* So the number that would size L3's
named build target — what perfect within-day gas timing is worth **inside the shipped
reconstruction** — has never been measured.

The one-variable version is this pass: hold `build_shape` exactly as shipped and substitute
**exactly one term**, the half hour's CCGT dispatch.

## The instrument, in one line

`tools/ep13_ccgt_swap_ceiling.py` re-implements `emissions_rate_t_per_mwh` line for line with one
override point at `ccgt_mw`, proves the re-implementation reproduces `gci.build_shape` to floating
point with the override off, and then scores four rungs through the same `neso.compare_shapes` on
the same held-out even days as every other EP13 bound.

* **`ccgt_timing`** — the model's own day mean for gas, plus TRUTH's within-day deviations. The
  level the residual already decides is untouched; only the shape inside the day moves. **This is
  the ceiling on the named build target.**
* **`ccgt_full`** — raw true CCGT MW. Level and timing together, which is a different and larger
  build.
* **`ccgt_day_mean`** — truth's day mean, flat inside the day. The level-only rung, so the two
  axes can be read apart.
* **`ccgt_timing_shuffled`** — truth's within-day profile dealt to the wrong days. The null.

**It is a CEILING and not a floor, which inverts §14.** §14's oracle was handicapped, so it bounded
from below. This one hands the shipped model *perfect* knowledge of the quantity the build would
approximate and changes nothing else, so no build of that class can beat it — **up to error
cancellation**, the standing caveat on every oracle here: an imperfect proxy whose errors happen to
offset the model's other errors could score above it, and a build that does is fitting the residual
rather than modelling gas.

---

## THE PREDICTIONS

**P1 — the re-implementation control is exact.** With the override off, my dispatch reproduces
`gci.build_shape`'s rates to better than 1e-12 on every half hour. If this fails, nothing else in
the artefact means anything and it must be read first. *Confidence: high. It is the same arithmetic
copied.*

**P2 — `ccgt_timing` clears the baseline in 2024, and by LESS than +0.193.** The direction is the
whole point of the pass; the magnitude is the test of §14's attribution. I predict **+0.05 to
+0.15** in 2024, i.e. the swap recovers a real but minority share of the oracle's gain, because the
shipped model's other terms stay wrong. **If it lands at or above +0.193, §14 understated its own
result and the build target is bigger than named. If it lands below +0.03, the named build target
is the FIFTH retired candidate and L3 needs a different input — a negative here retires it outright,
which is exactly what a ceiling is for and what §14's floor could not do.**

**P3 — the level is not where the answer is.** `ccgt_day_mean` gains less than `ccgt_timing` — I
predict under +0.02 — because the residual already sets the daily level roughly right and it is the
within-day shape that migrated out of the model's reach. If `ccgt_day_mean` carries most of the
gain instead, the diagnosis in §14 is wrong in its most quoted sentence.

**P4 — the model's implied gas is well correlated with truth BETWEEN days and poorly WITHIN them.**
Published as a direct diagnostic on the two MW series rather than inferred from the shapes: I
predict the raw correlation of implied against true CCGT above 0.85, and the within-day correlation
(each series minus its own day mean) **below 0.6**, falling across the window.

**P5 — the null collapses.** `ccgt_timing_shuffled` gains no more than +0.01 over the baseline, and
materially less than `ccgt_timing`. A shuffle preserves every value and the substitution machinery
and destroys only the correct timing, so a gain here would mean the rung is measuring the act of
substituting rather than the information substituted.

**P6 — the lower clamp binds and must be counted.** Truth's deviations added to a small modelled
day mean will go negative in quiet half hours and are clamped at zero. I predict this binds on
**under 5%** of scored half hours. If it binds on much more, `ccgt_timing` is partly measuring the
clamp and the rung's reading has to be cut down to what the unclamped half hours say.

## What this pass will NOT do, stated in advance

**No level move.** LAW A. A diagnostic cannot move a level and this instrument is R12 diagnostic
throughout: `ceiling_reaches_the_published_feed` is an AST walk over
`tools/generate_grid_intensity_feed.py`, not a promise.

**No publishable series comes out of it.** It holds metered gas, which is the largest emissions term
on the system, and handing that to the reconstruction would make it NESO's arithmetic with a
different cache — the line `sim/elexon_fuel_outturn.py` was written to draw.

**No constant anywhere is tuned to any number below.** If the ceiling is high, the next pass builds
a proxy and is scored against it; if it is low, the candidate is retired and recorded beside the
four already retired.

---

# THE SCORECARD — written after the run, beside the predictions and not over them

**Run 2026-08-31. One of the five substantive predictions survived.** The predictions are left
exactly as filed above; this section is the correction, and it is here rather than in place of them
because a prediction quietly revised to match its answer is not evidence the experiment was
designed before the answer was known.

| | prediction | measured (2024) | |
|---|---|---|---|
| P1 | re-implementation exact to 1e-12 | **drift 0.0** | **CONFIRMED** |
| P2 | `ccgt_timing` gains +0.05 to +0.15 | **+0.0485** | **REFUTED** — below the range |
| P3 | the level carries under +0.02 | **+0.1162** | **REFUTED** — the level is where the answer is |
| P4 | implied-vs-true gas within-day r below 0.6 | **0.807** (0.870 in 2019) | **REFUTED**, badly |
| P5 | the null sits within 0.01 of zero | **−0.2192** | **REFUTED**, and its control with it |
| P6 | the low clamp binds on under 5% | **0.8%** | **CONFIRMED** |

**P2 — and the retirement threshold I preregistered was itself a number picked to fill a slot.** I
wrote "below +0.03 retires it", and +0.03 is not keyed to anything. The number that decides whether
a build is worth making is the distance still to be closed: the peer bound reproduces NESO's own
outturn at 0.9711 in 2024 against this baseline's 0.7385, so the gap is **0.233** and perfect
within-day gas timing closes **21% of it**. That is the test, it was available when I filed, and I
used a bar of my own invention instead. The named build target is retired against the gap, not
against the bar.

**P3 — the prediction was written about a rung that could not have answered it.** The first draft
had four rungs and labelled `ccgt_day_mean` "the level-only rung". It is not: it flattens gas
inside the day at truth's daily level, so it *destroys* within-day variation rather than isolating
the level, and it comes in at −0.14 to −0.54. There was no level rung at all until the second
draft added `ccgt_level` — truth's day mean with the model's own within-day deviations — and that
one gains **+0.1162**. So P3 was refuted twice over: the number is not small, and the instrument as
first written could not have told me either way while reporting a confident-looking figure.

**P4 is the refutation that matters, and it inverts the reading of §14.** I predicted the shipped
model would be nearly blind to when gas runs. It is not: its implied gas tracks the metered series
within days at r = 0.807–0.870 across the whole window, falling only 0.06 over six years. §14's
ablation ladder established that the grid's within-day information is in CCGT — that stands — but
the sentence it was read as, *"the model cannot see it"*, is false. It sees most of it.

**P5 — the prediction was wrong AND the control keyed to it was wrong, which is the worse half.** I
asked for `abs(null gain) < 0.01`. Scrambled timing does not sit at zero: it replaces the model's
own gas timing with wrong timing and must HURT, measured at −0.219 to −0.307. That control went red
on the first real run against a perfectly sound instrument — a control pinned to a guessed answer,
going red because the world behaved correctly, which is this project's own named failure shape and
I wrote a fresh one. Repaired to the property (*a null may not FLATTER*) plus a discrimination leg
(*correct timing must beat scrambled timing by a margin*), because "did not gain" on its own is
satisfied by an instrument that reports one constant whatever it is handed.

**What the pass concluded is in §15 of the frame doc.** Headline, and it is not the headline this
preregistration expected: **the reconstruction knows WHEN gas runs and does not know HOW MUCH.**
