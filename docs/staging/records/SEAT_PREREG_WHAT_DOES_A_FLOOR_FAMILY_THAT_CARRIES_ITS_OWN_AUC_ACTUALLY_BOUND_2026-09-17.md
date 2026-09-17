**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`a-floor-family-that-carries-its-own-discrimination-auc-per-seed`)

**Knowledge:** none new. No domain constant moves. This is a pre-registration: predictions only,
written before the fold was run and before the AUC was compared to any ruler.

# Pre-registration: what does a floor family that carries its own AUC actually bound?

Delivery seat, 2026-09-17, ~20:15 BST. Written BEFORE `tools/fold_noise_floor_family.py` was run
on the new artefact and BEFORE the AUC was compared to any null distribution.

---

## What was already observed when this was written, and what was not

Honesty about the clock, because a prediction filed after its answer is not a prediction.

**Already read** (a previous invocation of this same claim launched the run at 16:21 BST; it
finished at 19:11:44Z, rc=0, and I read the artefact at 20:11):
`/var/tmp/value_cycle_ab_floor_with_auc_20260917.json`, 3 seeds, world `39a192ce04c1eda8`, mode
`all`, key `elasticity`, clock `settled-realised`, producing commit `c9bd2eae7`. Its per-seed
rows:

| seed | value adv | level adv | selection | level share | `discrimination_auc` | `auc_population` |
|---|---|---|---|---|---|---|
| 1234567 | £10,217.83 | £9,881.16 | +£336.68 | 96.7% | 0.5649181547619048 | 64 retained / 42 left |
| 2345678 | £10,217.83 | £4,394.44 | +£5,823.40 | 43.0% | 0.5649181547619048 | 64 retained / 42 left |
| 3456789 | £6,319.59 | £5,800.24 | +£519.35 | 91.8% | 0.5793650793650794 | 63 retained / 42 left |

**NOT yet run when this was written:** the fold, the publisher, and any comparison of the AUC to a
ruler.

---

## The predictions

**P1 — the drawn item's central claim is FALSE.** The item says
`error_bar.discrimination_across_the_family` "moves from state=asked_and_unanswerable to
state=measured ... with no code change". I predict it does NOT. `_auc_across_seeds` fails closed on
a single row without an AUC, and the published family
(`value_cycle_ab_s1_noise_floor_folded18_20260917.json`) has 18 such rows. Folding the new run into
it gives **`available: false`, `seeds_carrying_an_auc: 3`, `seeds_in_family: 21`** and the page
keeps the same refusal with a bigger denominator. The state can only move to `measured` if the
published family is REPLACED by a family all of whose members carry the figure — which at present
means dropping the advantage legs from 18 seeds to 3.

**P2 — the elasticity floor cannot put an error bar on the AUC, because the redraw does not reach
it independently.** Two of the three seeds returned the AUC identical to sixteen decimal places,
with identical `auc_population` and identical `value_advantage_gbp` — i.e. the elasticity redraw
flipped no departure at all in those two seeds, so the rank statistic could not move. I predict the
family's own standard deviation (≈0.0083) is **far narrower than the statistic's own
no-information null standard deviation** on this population, and that publishing the family spread
as "the AUC's error bar" would therefore be the tightest and most misleading interval on the page.
Quantitatively: null sd ≈ `sqrt((n1+n2+1)/(12·n1·n2))` = **0.0576** at 64×42, against a family sd
of 0.0083 — a factor of about **7**. The page's own retraction of 2026-08-30 already records the
estimator scoring 0.646, 0.672, 0.465, 0.465 and 0.130 across five runs in four days, which is a
run-to-run sd of roughly 0.22; an elasticity floor reproduces none of that.

**P3 — no discrimination is demonstrated.** Against its own null rather than against the floor's
spread, the family mean 0.5697 sits **(0.5697−0.5)/0.0576 = 1.21 null standard deviations** above
the no-information point. Below 2. So the prediction is: **the arm's belief cannot be shown to
carry information about who leaves**, and the thesis half that turns on INFERENCE stays unshown
while the level leg is determined positive at 63 sems. I am registering this before publishing it
because it is the unflattering answer and the page's `not_a_target` sentence commits us to it.

**P4 — more seeds made the selection leg LESS signable, not more.** Derived arithmetic, to be
checked against the fold: 18 seeds gave mean −£624.13, sem £347.16, **1.798** sems from zero
against a bar of 2.110. Adding these three (all positive, one an outlier at +£5,823.40) gives 21
seeds, mean **−£216.90**, sd £1,964.67, sem **£428.73**, **0.506** sems from zero against a bar of
≈2.086. The distance to a sign COLLAPSES from 1.80 to 0.51. If that holds, the rival claim's
`seeds_needed_to_state_a_sign: 24` is not a forecast: it was computed holding this family's mean
and sd fixed, and three draws moved both. The artefact's own
`distance_to_a_sign.what_this_count_is` says exactly that, and it is about to be demonstrated.

---

## What would refute each

- **P1** is refuted if the folded 21-seed family publishes `available: true`, or if the page reads
  `measured` without the published family being replaced.
- **P2** is refuted if the family sd comes out at the same order as the null sd — which would mean
  the elasticity redraw does move the departure set, and the two identical rows were a coincidence
  rather than a structural invariance.
- **P3** is refuted if the mean sits above 2 null sds from 0.5. It is NOT refuted by the mean being
  above 0.5: a rank statistic above 0.5 with no interval is the exact figure this page retracted.
- **P4** is refuted if the 21-seed sems-from-zero comes out at or above 1.798.

## What done means for this claim

The artefact committed so the evidence is in git rather than only in `/var/tmp`; the fold run and
its answer recorded; and the reading published in the family's own words — including, if P1 holds,
that the state did NOT move and why the one instrument we have cannot be made to answer by folding.
A re-run reported without the seed count and the distance from the no-information point beside it
is not done.
