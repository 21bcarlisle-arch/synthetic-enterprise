**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — resolve the selection leg by seeds because the ranking cut already names its sign) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — what six more seeds do to the selection leg's sign

**Written 2026-09-09, before the nine-seed floor run was launched and before any figure from it
existed.** Nothing below is a reading of an output. Every number quoted as an input is from an
artefact already on disk at the time of writing, named with its path. It is filed so the run can
refute it.

Commissioned by the Lane 0 delivery item
`resolve-the-selection-leg-by-seeds-because-the-ranking-cut-already-names-its-sign`.

---

## The state before the run, quoted rather than paraphrased

`site/data/value_arms.json` → `contrast_bounds.contrasts.selection_gbp`, whose sole witness is
`docs/observability/value_cycle_ab_s1_noise_floor.json` (generated 2026-09-09T06:57:00Z, producing
commit `4e853a83e70317d3b636b0576baf50e6aafe6152`, world digest `39a192ce04c1eda8`, redraw mode
`all`, clock `settled-realised`):

| seed | `selection_gbp` | `level_share_of_advantage` |
|---|---|---|
| 11111 | **+1,260.93** | 0.9357 |
| 22222 | **−3,036.25** | 1.1761 |
| 33333 | **+494.45** | 0.9752 |

n = 3 · mean = **−426.96** · sd = **2,291.98** · SEM = 1,323.28 ·
`selection_distinguishable_from_zero: false`.

The independent instrument, `method_skill.fixed_horizon` on the same feed: concordance **0.4210**
against a null point of 0.4458 at p = 0.0045 on n = 161 scored decisions,
`reading: "worse_than_chance"`. That cut says the arm's *ranking* is inverted — so it bets the
*choosing* is worth less than nothing, i.e. that `selection_gbp` is genuinely negative.

## The one fact about the current spread that drives every prediction below

**The −426.96 mean and the 2,291.98 sd are one seed's doing, and at n = 3 they cannot be anything
else.** In a three-point sample the largest deviation any single point can reach is
(n−1)/√n = **1.1547** sample standard deviations. Seed 22222 sits at **−1.1384** sd — 98.6% of the
arithmetic maximum. The other two seeds are both *positive*. So the published negative sign is not
three observations agreeing; it is two positives and one point pressed as far from them as three
points geometrically permit, and the sd is very nearly *defined* by that one seed's distance.

This is why the run is worth its hours and why its answer is not foregone.

## What the run is

Nine seeds — the existing **11111, 22222, 33333** re-run unchanged, plus **44444, 55555, 66666,
77777, 88888, 99999** — as one `floor-all` leg, `--redraw-mode all --level-arm`, stamp `20260909b`,
through `tools/run_arms_rerun.py --launch`. Nothing moves but the per-household price-sensitivity
draw, exactly as the existing three did. The old three are re-run rather than carried over so the
nine rows come from one session on one tree, which is the whole reason that module exists.

**Nine and not more.** The seed count buys precision at 1/√n, and §"what would actually settle it"
below shows the count that would settle the sign *at the current point estimates* is 116 — about
48 hours of compute, which is not a thing to spend before the sd is known to better than 2 degrees
of freedom. Nine gives 8 df on the quantity that is actually in doubt.

## What is predicted

Each is falsifiable by a single field of the new artefact.

**P1 — the feed's n becomes 9.** `contrast_bounds.contrasts.selection_gbp.n == 9` on
`site/data/value_arms.json` after the publish. Refuted by any other value.

**P2 — the three old seeds reproduce to the penny.** Seeds 11111 / 22222 / 33333 return
+1,260.93 / −3,036.25 / +494.45 again, and `world_identity.digest` is again `39a192ce04c1eda8`.
This is a control, not a formality: the producing commit will differ (`4e853a83` → whatever HEAD
is at launch). **If they do not reproduce, the run measures a different thing and every comparison
in this document is void** — and *that* is then the deliverable, ahead of any sign.

**P3 — the mean moves TOWARD zero, not further below it.** I predict the nine-seed mean lands in
**[−900, +900]**, and specifically that it does *not* land below −2,291.98 (the "further below zero
and outside its own spread" case the delivery item names as the two cuts agreeing). Refuted if the
mean lands outside [−900, +900].

**P4 — the sd falls.** I predict the nine-seed sd lands in **[1,200, 2,400]** and below 2,291.98.
Refuted if it comes in above 2,400. *(The prediction is only mildly confident: seed 22222 being at
98.6% of the n=3 maximum is equally consistent with an sd inflated by one draw and with a genuinely
heavy left tail that three seeds under-sampled. The direction of the bet is set by P5, not by this.)*

**P5 — the sign test goes the other way.** At least **5 of the 9** seeds return a positive
`selection_gbp`. Refuted if 4 or fewer do.

**P6 — the page still refuses to state a direction.** `selection_distinguishable_from_zero` stays
`false` and `_resolvable` withholds the directional clause. **This is the prediction most likely to
be wrong, and the arithmetic says exactly when:** at n = 9 the page can state a direction iff
|mean| > 2·sd/√9, i.e. iff **sd < 1.5 × |mean|**. At the current mean of −426.96 that needs an sd
below **£640**, against a point estimate of £2,292 — so P6 fails only if the sd collapses by 3.6×,
which P4 does not expect. But it is a live branch and not a foregone one; if the sd really was one
seed's artefact, nine seeds can resolve this.

> **CORRECTED 2026-09-09T10:13Z, before the run wrote anything and before any figure from it was
> read.** The threshold in the paragraph above is the FLOOR key's arithmetic, and the floor key
> gates no page. P6 must be graded against the condition `generate_value_arms_data._resolvable`
> actually applies, which is a different rule over a different quantity of the opposite sign. The
> corrected threshold, the window in which the error changes P6's score, and what it does to
> §"what would actually settle it" below are in
> `SEAT_FINDING_THE_ERROR_BAR_CONTROL_AND_ITS_OWN_PREREGISTRATION_WERE_BOTH_GRADED_ON_A_QUANTITY_THE_PAGE_DOES_NOT_GATE_ON_2026-09-09.md`,
> beside this file. The numbers are stated there once and deliberately not repeated here.

**P7 — what will NOT move, and it is not merely conceptually separate.** `level_share_of_advantage`
stays within [0.90, 1.20] on its nine-seed mean. This is independent of P3–P6 in the arithmetic
sense that matters: `selection_gbp` is a *difference in pounds* between the value arm and
flat-at-level, while `level_share` is a *ratio* whose denominator is the value advantage — the two
move together only if the level arm itself moves, and the level arm's median is re-read per seed
from that seed's own run. If P7 fails while P3–P6 hold, the elasticity redraw is reaching the level
arm as well and the leg is not the clean instrument it is documented to be.

## What would actually settle it, stated before the answer

At the current point estimates the seed count that would put the mean outside 2·SEM is

    n = (2 · sd / |mean|)² = (2 × 2,291.98 / 426.96)² = **115.3 → 116 seeds**

At the measured cost of a `floor-all` leg (≈25 min/seed: the 2026-09-03 three-seed leg consumed
1h 09m of CPU and was OOM-killed at 90%), 116 seeds is **≈48 hours** on a guest that peaks at
6.4 GB per leg against 24 GB total. So if the nine-seed run comes back with the sd substantially
intact, **the honest finding is that this instrument cannot resolve the selection sign at any count
this machine can afford, and the remedy is not more seeds** — it is a lower-variance estimand, or
the fixed-horizon cut standing as the answer on its own evidence.

> **CORRECTED 2026-09-09T10:13Z, before the run wrote anything.** The 116 above comes from the same
> wrong rule as P6. Under the gate the page actually applies there is **no seed count that settles
> it** — the 48 hours buys a probability with 76 zeroes after the decimal point, and should not be
> spent. The conclusion of this paragraph is therefore reached ahead of the run rather than
> conditionally on it. Arithmetic in the finding named above.

## Which way the two cuts then point

- **P3 and P5 hold** (mean toward zero, majority of seeds positive): the two instruments
  **disagree**. The fixed-horizon estimand says the choosing is worse than chance; the realised
  pounds say it is not distinguishable from zero and if anything positive. That puts the
  fixed-horizon estimand's *construction* on trial — and it already carries a known survivorship
  problem (`SEAT_RESULT_THREE_OF_THE_FOUR_LEGS_ARE_SURVIVOR_CUTS_AND_THE_ESTIMAND_IS_THE_ONE_THAT_IS_NOT`),
  so this is the outcome that generates the next piece of work rather than closing the question.
- **P3 refuted downward** (mean below −2,292): the two cuts **agree**, the choosing is worth
  negative money on two independent instruments, and the value arm's selection component is a
  finding about the arm and not about the noise.

**I am betting on the first.** Not because it is the more interesting answer, but because the
current negative sign rests on one seed at 98.6% of the maximum leverage a three-point sample
allows, and the two seeds that are not that one are both positive.

## What is not being claimed

That nine seeds settle the thesis. The delivery item's own "done" is that the n is materially above
3 and that **the page decides for itself** whether it may state a direction. No verdict is
hand-written into the feed by this work; `_resolvable` reads the spread and rules. If it rules the
same way it does today, the result of this run is the sentence in §"what would actually settle it"
— which is a result, and belongs on the page rather than in a footnote.

---

*Filed before launch. The result goes beside this document, whichever way it lands.*

---

> **GRADED 2026-09-09, after the run.** It landed against this document.
> `SEAT_RESULT_THE_SELECTION_LEGS_SIGN_WENT_THE_OTHER_WAY_AND_THE_PREREGISTRATIONS_BET_IS_REFUTED_2026-09-09.md`,
> beside this file, carries every prediction quoted verbatim with its grade.
>
> **P1 held · P2 held · P3 REFUTED · P4 held · P5 REFUTED · P6 held vacuously · P7 held.**
>
> n = 9, mean **−£1,078.17** (not the predicted [−900, +900], and *further* from zero, not nearer),
> sd £1,810.50, **4 of 9 positive** against the 5 P5 required. The six new seeds' own mean is
> −£1,403.77 — more negative than the three they were added to.
>
> **The bet in §"Which way the two cuts then point" is refuted.** The negative sign was not seed
> 22222's geometry. It also did not reach this document's other branch: the mean sits in the gap
> between the two outcomes offered here, so neither pre-registered reading applies, and the result
> document names that third state rather than assimilating it to the nearer one.
>
> The two corrections above — both filed before the artefact existed — were graded as they
> instructed. One counterfactual inside the 10:13Z correction is itself refuted and is corrected in
> the result document beside its claim.
