**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — land the nine-seed floor through the witness path and grade its pre-registration beside it) · **Class:** measurements_that_mirror

# RESULT — the selection leg's sign went the other way, and the pre-registration's bet is refuted

**The run finished 2026-09-09T15:17:31Z** and wrote
`docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json`
(md5 `24da1d289d6ee021d71a03e33b894763`, producing commit `c066c114b`, world digest
`39a192ce04c1eda8`, redraw mode `all`, clock `settled-realised`, 9 seeds × 3 passes).

This document grades
`SEAT_PREREGISTRATION_WHAT_SIX_MORE_SEEDS_DO_TO_THE_SELECTION_LEGS_SIGN_2026-09-09.md`
(committed `c066c114b` at 10:04:45, **thirteen seconds before the run started**) and its two
corrections, both filed while the run was in flight and before its artefact existed:

- `SEAT_FINDING_THE_ERROR_BAR_CONTROL_AND_ITS_OWN_PREREGISTRATION_WERE_BOTH_GRADED_ON_A_QUANTITY_THE_PAGE_DOES_NOT_GATE_ON_2026-09-09.md` (10:13Z)
- `SEAT_FINDING_P6_AND_THE_SIGN_BRANCH_WERE_DECIDED_BY_ARITHMETIC_BEFORE_THE_RUN_BECAUSE_THE_THREE_RETAINED_SEEDS_PIN_THE_SPREAD_2026-09-09.md` (12:20Z)

**Every timestamp above precedes the artefact's.** That is the only thing that makes the grades
below worth reading.

---

## The nine rows

| seed | `selection_gbp` | `level_share_of_advantage` | |
|---|---|---|---|
| 11111 | **+1,260.93** | 0.9357 | retained |
| 22222 | **−3,036.25** | 1.1761 | retained |
| 33333 | **+494.45** | 0.9752 | retained |
| 44444 | **−2,644.35** | 1.1566 | new |
| 55555 | **+286.06** | 0.9862 | new |
| 66666 | **+1,090.00** | 0.9494 | new |
| 77777 | **−2,482.58** | 1.1733 | new |
| 88888 | **−2,719.11** | 1.1584 | new |
| 99999 | **−1,952.63** | 1.1119 | new |

n = 9 · mean = **−£1,078.17** · sd = **£1,810.50** · SEM = £603.50 · **4 of 9 positive**.

**The six new seeds alone: mean −£1,403.77, sd £1,661.84, 2 of 6 positive.** They are *more*
negative than the three they were added to, not less.

## The grades, each prediction quoted verbatim

### P1 — **HELD**

> **P1 — the feed's n becomes 9.** `contrast_bounds.contrasts.selection_gbp.n == 9` on
> `site/data/value_arms.json` after the publish. Refuted by any other value.

The live feed carries `"n": 9`, `stdev_gbp: 1810.5007782810442`, `mean_gbp: −1078.1657011111156`.

### P2 — **HELD**, and it is the one that had to hold

> **P2 — the three old seeds reproduce to the penny.** Seeds 11111 / 22222 / 33333 return
> +1,260.93 / −3,036.25 / +494.45 again, and `world_identity.digest` is again `39a192ce04c1eda8`.
> … **If they do not reproduce, the run measures a different thing and every comparison in this
> document is void**

| seed | before | after | delta |
|---|---|---|---|
| 11111 | 1260.9261999999871 | 1260.9261999999871 | **0** |
| 22222 | −3036.2544110000017 | −3036.2544110000017 | **0** |
| 33333 | 494.4468219999822 | 494.4478329999822 | **+0.001011** |

Digest `39a192ce04c1eda8` again, across a producing-commit change `4e853a83` → `c066c114b`.

**To the penny: yes. Bit-identical: no, on one seed, by a tenth of a penny.** The prediction said
"to the penny" and is graded on what it said. The £0.001 is recorded rather than rounded away
because it is the only evidence in this artefact that the tree moved under the run, and a future
re-run that reproduces to the *penny* while drifting by pounds would be graded green by this same
criterion. **Nothing here establishes which line of code moved that tenth of a penny, and this
document does not guess.**

### P3 — **REFUTED**, and this is the deliverable

> **P3 — the mean moves TOWARD zero, not further below it.** I predict the nine-seed mean lands in
> **[−900, +900]**, and specifically that it does *not* land below −2,291.98 … Refuted if the mean
> lands outside [−900, +900].

**The mean is −£1,078.17. It is outside [−900, +900], and it moved AWAY from zero** (−426.96 →
−1,078.17), which is the direction the prediction expressly bet against.

### P4 — **HELD**

> **P4 — the sd falls.** I predict the nine-seed sd lands in **[1,200, 2,400]** and below
> 2,291.98. Refuted if it comes in above 2,400.

sd = **£1,810.50**: inside the band and below £2,291.98. The 12:20Z finding's analytic minimum for
any nine-seed sample retaining these three rows was **£1,145.99**; the realised sd sits well above
it, so P4's lower half was not the near-vacuous case that finding warned it might be.

### P5 — **REFUTED**

> **P5 — the sign test goes the other way.** At least **5 of the 9** seeds return a positive
> `selection_gbp`. Refuted if 4 or fewer do.

**4 of 9.** The six new seeds returned 2 positive against the 4 the prediction needed.

### P6 — **HELD, AND HELD VACUOUSLY**, exactly as the 12:20Z finding instructed

> **P6 — the page still refuses to state a direction.** `selection_distinguishable_from_zero` stays
> `false` and `_resolvable` withholds the directional clause.

`_resolvable` compares `|realised.split.selection_gbp|` = £319.10 against the spread: **£319.10 vs
£1,810.50 → refuses.** The page states no direction.

**This is not a prediction that survived a test.** The 12:20Z finding derived, before the run, that
no assignment of the six new seeds could let the page state a direction: the arithmetic floor on the
sd was £1,145.99, which is 3.591× the £319.10 threshold. The realised ratio is **5.674×**. P6 could
not have been refuted, and grading it "held, as predicted" would be this repository's own named
defect — a control keyed to an answer it could not fail to give.

### P7 — **HELD**

> **P7 — what will NOT move …** `level_share_of_advantage` stays within [0.90, 1.20] on its
> nine-seed mean.

**1.0692** (from 1.0290 at n = 3). Inside the band. The elasticity redraw is not reaching the level
arm, so the leg remains the instrument it is documented to be — which matters more now that P3 and
P5 are refuted, because it is what stops the negative selection mean being read as level-arm noise.

## The bet, and what actually happened

The pre-registration closed by naming its own bet:

> **I am betting on the first.** Not because it is the more interesting answer, but because the
> current negative sign rests on one seed at 98.6% of the maximum leverage a three-point sample
> allows, and the two seeds that are not that one are both positive.

**The bet is refuted.** Seed 22222 was not a lone outlier: five of nine seeds are negative, three of
the six new ones land below −£1,950, and the six new seeds' own mean is more negative than the three
they joined. The "one seed's geometry" reading of the −£426.96 was wrong, and it was wrong in the
direction that costs the arm.

**But the run did NOT reach the other branch either, and saying so is the honest grade.** The
pre-registration offered exactly two outcomes and the 12:20Z finding computed each one's window over
the six new seeds:

| branch | window on the six new seeds | actual −1,403.77 |
|---|---|---|
| P3 holds — the two cuts **disagree** | [−1,136.52, +1,563.48] | **outside, below** |
| P3 refuted downward — the two cuts **agree** | < −3,224.49 | **not reached** |

**The answer landed in the gap between the two branches, and neither pre-registered reading
applies.** The `method_skill.fixed_horizon` cut says the arm's ranking is worse than chance; the
realised pounds now point the *same direction* — but not far enough for the pre-registration's own
criterion for agreement, which it set at the arm's spread. **The two instruments now agree in sign
and the pounds do not clear the bar the pre-registration set for calling that agreement.** That is a
third state, it was not pre-registered, and it is being named here rather than assimilated to
whichever of the two branches it is nearer.

## What the page says now, in its own words

`_resolvable` ruled and nothing was hand-written. The live feed:

- `contrast_bounds.contrasts.selection_gbp`: **n = 9**, stdev £1,810.50, mean −£1,078.17, min
  −£3,036.25, max +£1,260.93.
- `error_bar`: seeds 9, passes 27, SEM £603.50, `distinguishable_from_zero: false`,
  `spread_to_point_estimate_ratio` **7.183 → 5.674**.
- The reading is unchanged in substance: *"this instrument cannot yet resolve a selection effect of
  the size it is measuring — in either direction. That is a finding about the INSTRUMENT and not
  about the pricing arm."*

**270 passed, 1 skipped** on `tests/tools/test_generate_value_arms_data.py` and
`site/test_the_baseline_comparison_reaches_the_reader.py` against the real nine-seed feed. Nothing
wedged, as the 12:20Z finding's four probes predicted.

## Three corrections to the documents this one grades, filed beside their claims

**1. The 10:13Z finding's counterfactual did not materialise, and the repair was still right.**
That finding stated the old site control — pinned to `distinguishable_from_zero is False` — "would
have wedged the tree on the very result this delivery item was drawn to produce", because at n = 9
the floor's key flips true on `|mean| > 0.667 × sd`. **It does not flip: 1,078.17 against 1,207.60.**
The old control would have stayed green. The repair (keying the precondition to the page's own gate)
was correct on its own reasoning and is untouched by this; what is withdrawn is the near-miss
offered as its urgency. **Recorded because a prediction of a wedge that did not happen is exactly as
much a refutation as one about a figure.**

The floor's own key nonetheless moved a long way toward firing: `|mean| / 2·SEM` went from **0.161
at n = 3 to 0.893 at n = 9**. It is now within 11% of a threshold that gates nothing rendered. The
class the 10:13Z finding named is live; only its instance was over-stated.

**2. The nine-seed floor reached `contrast_bounds` and did NOT reach `_verdict_stability`, because
those are fed by two different floor constants.** `_sign_determined` — which the 10:13Z finding said
"becomes an independent branch for the first time" at n ≥ 5 — is called from `_leg_in_this_world`
with `floor_current`, i.e. `CURRENT_WORLD_NOISE_FLOOR_PATH`, which is
`value_cycle_ab_s1_noise_floor_20260908.json` and **still carries three rows**. The live feed's
selection leg accordingly still reads *"re-drawn 3 times in this same world"*.

That is not a defect and it was not repaired. `CURRENT_WORLD_NOISE_FLOOR_PATH` is deliberately
pinned as a pair with `CURRENT_WORLD_THREE_ARM_PATH` — the producer's own constant block says
moving either alone is the defect the pair exists to prevent, in both directions. **But it means the
page now publishes two selection spreads at two different n, and a reader meeting "3 times" beside a
bound built from nine rows has no way to tell they are different artefacts.** Filed as the next
step, not fixed here: the honest repair is either a nine-seed current-world floor run as a pair with
its own arm, or the two n's made visibly distinct on the surface. It is a page-legibility question
and it wants the cold-eyes pass, not a hurried edit at the end of a landing turn.

**3. The comment at `generate_value_arms_data.py:4740` was checked and is still TRUE.** It reads
"So today, at three seeds, this field can only fire where `stable` is already False", and it was
expected to go false today. It did not, for reason 2 above — the field it describes is driven by the
three-row floor. **It was left alone.** Correcting a comment to match a change that did not reach it
would have made the file say something false.

## The census prediction this turn filed before promoting, now checked

`SEAT_FINDING_THE_PROMOTED_ARTEFACT_CENSUS_READS_DATES_SO_A_SENTENCE_KEYED_TO_THE_FLOORS_ROW_COUNT_IS_INVISIBLE_TO_IT_2026-09-09.md`
(landed `58b6cec1f`, **before** the promotion) predicted that replacing three-seed bytes with
nine-seed bytes at `NOISE_FLOOR_PATH` would move no row of
`tools/promoted_artefact_claim_census.py`.

**Confirmed.** Before and after the promotion the census reports the identical
`CLAIMS ABOUT WHICH RUN IS THERE 14 · ordering-only 8 · STALE 1`, the one STALE row being the known
benign false positive already recorded at `d02e678e0`. The promotion changed the published bound's
sample size by a factor of three and the control that exists for promote-by-copy saw nothing. Its
`three seeds alone` literal is still absent from the feed, so the finding's LATENT grade holds.

## What this changes, and what it does not

**It does not settle the selection sign, and no seed count on this machine will.** The 10:13Z
finding priced that before the run and this artefact sharpens the input rather than the conclusion:
σ is now estimated at **£1,810.50 on 8 degrees of freedom** instead of £2,291.98 on 2, against a
page threshold of £319.10 — a ratio of 5.67. **Do not commission the 116-seed run.** The remedy is a
lower-variance estimand or the fixed-horizon cut standing on its own evidence.

**What it does change is which way the unresolved question leans.** The delivery item was drawn on
the premise that "the pre-registration shows that negative sign is one seed's geometry". **It was
not.** At n = 9 the per-customer choosing is negative on the majority of draws, by a mean three
times further from zero than the figure that premise was built on, and on the same side as the
independent ranking cut. The page correctly refuses to state that as a direction, and the honest
sentence for anyone reading the thesis is: **the £17–19k advantage remains ~98% price level, and the
per-customer choosing — the part that is the whole claim — has now been measured nine ways and has
not once been shown to be worth positive money.**

That is not a finding about the arm yet. It is the point at which "we cannot tell" stops being
symmetric.

---

*Filed beside the pre-registration it grades. P3 and P5 refuted; the bet stated in the
pre-registration's own closing paragraph is refuted with them.*
