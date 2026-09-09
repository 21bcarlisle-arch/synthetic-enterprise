**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — promote-the-09-09-pair-when-its-floor-lands) · **Class:** controls_that_cannot_fail

# RESULT — the 09-09 pair is promoted, and five of six predictions hold

Grading `docs/staging/records/SEAT_PREREGISTRATION_WHAT_PROMOTING_THE_09_09_PAIR_MAKES_THE_FIXED_HORIZON_TABLE_SAY_2026-09-09.md`,
written before the floor run finished and therefore before its own P4 and P6 inputs existed.

**The move itself was already landed on arrival.** The floor run finished (unit
`longjob-noise-floor-20260909`, PID 4064918 gone, artefact written 07:57Z), both artefacts carry
world digest `39a192ce04c1eda8`, the copy was made and `generate_value_arms_data` re-run, and the
whole thing landed at `500216b09`. `value_cycle_ab_s1_three_arm.json` and
`..._noise_floor.json` are byte-identical (`cmp`) to their `_20260909` originals at HEAD. This
document is the piece that was not there: the grading.

---

## The six predictions

| | Predicted | Measured | |
|---|---|---|---|
| **P1** | `fixed_horizon.available` true; all four rows render a number **and** an interval; none renders "no interval on this cut's own n" | `available` false→true; four rows render `0.5338 · 0.4494–0.5504`, `0.4993 · 0.4410–0.5582`, `0.5130 · 0.4403–0.5588`, `0.4210 · 0.4458–0.5540`; the phrase appears nowhere on the rendered page | **CONFIRMED** |
| **P2** | the estimand renders 0.4210 against 0.4458–0.5540, read as worse-than-chance, composed from the three numbers | renders exactly that; `reading` is `worse_than_chance`, composed by `concordance_reading` at `generate_value_arms_data.py:1900-1905` from `observed/null_low/null_high`, never from `inside_the_null` | **CONFIRMED** |
| **P3 — will not move** | control leg and headline agree to the last bit on both ends of `[0.4493929, 0.5503571]` | `the_control_leg_agreement.intervals_identical` true; both ends `0.44939285714285715` / `0.5503571428571429` | **CONFIRMED** |
| **P4 — least sure** | the promotion costs no block its bound; `error_bar` stays available | a whole-feed sweep of every `.available` flag and every `_low`/`_high`/`sem_gbp`/`stdev_gbp` against the pre-promotion feed (`500216b09^`): **0 lost, 12 gained**. `error_bar.available` and `contrast_bounds.available` both still true | **CONFIRMED** |
| **P5 — will not move** | `world_provenance.one_world_across_every_figure` stays true | true; one digest `39a192ce04c1eda8` across all five listed runs, `runs_measured_in_a_superseded_world` empty | **CONFIRMED** |
| **P6** | the render repair at `9bcea85c4` changes rendered bytes **for the first time** on this promotion | **the promoted feed renders byte-identically with and without the repair hunk** — render sha `d498f84aa225ff12` both ways, zero panels differing | **REFUTED** |

The four legs' figures were declared as facts rather than predictions in the pre-registration, and
they reproduce unchanged. What was genuinely unknown — the floor, and what the generator does when
both sides move at once — is P4, and it holds.

---

## P6, which is the useful one

The pre-registration's reasoning was: the repair is a no-op today *because* the promoted 09-08b
artefact predates the per-leg spread, so `fixedHorizonBlock` returns before reaching `row()`;
therefore promoting a run that carries the spread makes it take effect. **Reaching `row()` is
necessary and it is not sufficient.** The branch the repair added is

```js
} else if (lo === null || hi === null) {   /* render `withheld` instead of a bare number */
```

so it fires only on a leg carrying a concordance and **no** interval. The promotion supplied
intervals on all four legs — which is the exact opposite of the branch's precondition. The block
now reaches `row()` on every row and the new branch is unreachable on all four.

Measured as a one-variable test rather than argued: HEAD's `site/capabilities/index.html` against
the same file with only the `9bcea85c4` hunk reverse-applied, both driven by the live promoted feed
through `site/_live_harness.mjs`. Identical, every panel. (A first attempt compared HEAD against
`9bcea85c4^` wholesale and showed two panels differing — `arms-method` *and* `arms-departure`. The
second panel is the tell: other lanes touched the door between that parent and HEAD, so the
difference was not attributable to the repair. Isolating the hunk removed the whole difference,
which means none of it was ever the repair's.)

**So the prediction was not satisfiable by a successful promotion.** A fail-closed guard changes
rendered bytes only when the defect it guards against is present. Predicting that this one would
visibly take effect was, restated, predicting that the 09-09 run would ship a leg with a number and
no interval. It did not. The repair remains correct and its evidence is where it always was — the
door test's poison round, red on the unrepaired render and green on the repaired one — and *not* in
live bytes, which it cannot move while the feed is healthy.

**The generalisation worth keeping: for a fail-closed control, "it will change the live page when X
lands" is a prediction about a future defect, not about the control.** The honest form of P6 was
"the repair stays a no-op, and will stay one until a run ships a leg without its interval" — a
will-not-move claim, and one that would have graded CONFIRMED.

## What did move on the page, and what is still withheld

The live render is not byte-identical to the pre-promotion one (`d498f84aa225ff12` against
`2800f5e9d912b0ec`) — the four-row table with its four intervals is new, and the estimand's
worse-than-chance sentence now reaches a reader. That change is the *promotion's*, not the repair's.

One thing the block still withholds, and it should be read as a live gap rather than as noise: the
"Departures this cut can see" column renders `not measured` on all four rows, because the promoted
run predates `method_skill.fixed_horizon.leg_conditioning`. So the page can now show the four cuts
and cannot yet say which of them are computed over households that stayed — which is the same
survivorship question the estimand exists to answer, answered for the estimand and not for the
comparison. It is withheld with its reason named, which is the right behaviour; it is the next run's
work, not this one's.

## What is next

* The leg-conditioning split needs a run that carries it, so the four-cut table can say which cuts
  condition on survival. Until then the column is honestly blank.
* Nothing here changes the estimand: 0.4210 on 161 decisions against its own
  0.4458–0.5540 at p 0.0045 is on the page, with its interval, and reads as inverted rather than
  uninformative.
