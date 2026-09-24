# RESULT — the draw regrade is a 2.74x correction to a stated confidence and it changes no verdict

**Severity:** INFORMATIONAL (a measurement and the prediction it refuted)
**Filed:** 2026-09-24, delivery seat, claim `entitled-draw-count-needs-a-family-that-records-its-rosters`
**Pre-registration:** `docs/staging/records/PREREG_THE_DRAW_REGRADE_ON_THE_ONLY_ROSTER_CARRYING_FAMILY_2026-09-24.md`
— written before the numbers below existed and kept unedited beside them.

---

## What the direction asked, and what was actually possible

1. *"Re-fold or re-run the served noise-floor family so its seed rows carry `scored_decisions`"*
   — **NOT DONE, and not doable by re-folding.** A fold reads the rows that exist.
   `scored_decisions` reached the seed-row writer on 2026-09-24; the served family
   (`..._folded18_single_arm_20260917.json`) was drawn on 2026-09-17 and its eighteen rows carry no
   roster and no fingerprint. There is nothing on disk to fold them out of. The only route is
   re-running eighteen seeds, priced by the producer's own comment at days of the only box. That is
   a compute decision, not a coding one, and it is recorded here rather than quietly skipped.

2. *"then let `sems_to_state_a_sign` take `draws_the_spread_is_entitled_to` instead of
   `selection['n']`"* — **DONE, but deliberately NOT as written.** See below.

## The direction's premise was wrong on one point, and it matters

The WHY says *"No published floor records its rosters"*. A census of all 28 floor artefacts in
`docs/observability/` finds exactly one that does: `..._five_seed_head_20260924.json`, 5 of 5 rows
carrying `scored_decisions`. It is not the SERVED family — so the headline figure still cannot move,
and that part of the direction stands — but it means the exact branch has a **live input** and did
not have to be built against a fixture.

## Why the prescribed substitution was not implemented as prescribed

The verdict is `|mean| > bar * sem`, `sem = stdev / sqrt(n)`, `bar = t(n-1)`. A repeated decision
set produces an identical residual, which touches **three** terms:

| term | effect of the repeat | does the prescribed fix move it? |
|---|---|---|
| `bar = t(n-1)` | too many degrees of freedom | yes |
| `stdev` | **deflated** — a duplicate sits at no distance from its twin | no |
| `sqrt(n)` | **inflated** | no |

Substituting the draw count into the bar alone is a third of the correction, and it grades a sem
taken over seeds at a bar earned by draws — a number over a quantity that is neither. So the whole
leg is recomputed over the collapsed family, through the same `_leg` estimator the seed-count
reading uses.

## The numbers, on the five-seed head (5 seeds, 3 distinct decision sets)

| | over 5 seeds | over 3 draws | bar-only (as prescribed) |
|---|---|---|---|
| stdev | 113.03 | **154.60** | 113.03 |
| sem | 50.55 | **89.26** | 50.55 |
| bar | t(4) = 2.7764 | t(2) = **4.3027** | 4.3027 |
| **required margin (GBP)** | **140.34** | **384.05** | 217.48 |
| errors from zero | 28.64 | **15.98** | — |
| sign stateable? | yes | **yes** | yes |

The full regrade is **2.74x** the seed-count margin; the prescribed bar-only fix is 1.55x. The
prescribed fix is therefore not merely incomplete — it understates the correction by 43%.

## The predictions, scored

1. **Collapsed stdev larger** — ✅ HELD (113.03 → 154.60).
2. **Required margin at least 2x** — ✅ HELD (2.74x).
3. **The sign verdict will flip to not-stateable** — ❌ **REFUTED.** It still clears, at 15.98
   errors from zero. The mean is enormous relative to the spread on this family and no plausible
   correction reaches it.
4. **`at_least` and the distinct-residual count agree (3 = 3)** — ✅ HELD. The measured coextension
   between an unchanged decision set and a pinned residual is **not** refuted on the one family
   able to test it.

**Prediction 3 was the headline one and it was wrong.** The useful reading is the opposite of what
I expected: this is a large correction to a *stated confidence* that changes *no published sign*.
That is what makes it safe to adopt — no claim on any surface depends on the change — and it is
also why it was never going to be caught by anyone watching verdicts rather than arithmetic.

## One thing the measurement found that was not predicted at all

Seeds 12, 14 and 15 share one fingerprint and one `selection_gbp` **to the last digit**, while seed
12 disagrees with the other two about `level_share_of_advantage`. So the coextension holds for the
residual and **does not extend to a leg the control arm survives in** — the control arm cancels out
of `selection_gbp` and does not cancel out of the share. Collapsing the share by decision set would
average a real difference away and publish it as one draw. `regrade_over_distinct_draws` therefore
refuses any key that is not constant inside a group, and that refusal is reached on the real
artefact rather than on a fixture.

## What landed

`regrade_over_distinct_draws` in `tools/fold_noise_floor_family.py`, published by `summarise` as
`selection_leg_regraded_over_draws` **beside** the existing fields rather than replacing them — a
consumer keyed to `selection_sem_gbp` keeps reading the seed-count answer, because silently swapping
a published field changes its meaning under readers who cannot see that it moved.

It **fails closed on every family published to date**, including the served one, which returns an
unavailable naming the 15–18 bound. **Nothing on any page moves today.** The day a floor is drawn
whose rows carry rosters, the regrade appears with nobody editing a string.

Four controls, 4 of 4 mutations RED, each on the leg written for it:
bar-only substitution; refusal that stops naming its bound; the within-group disagreement guard;
and `the_verdict_changed` wired to `False`. The last one drives **both** values out of the same
function — on the family as drawn the flag is `False`, which is unfalsifiable on its own, so a
constructed-residual arm proves `True` is reachable and pins the direction: the collapse may take a
sign away and may never grant one.

## What is still owed

The served family's rosters. Until eighteen seeds are re-run with `scored_decisions`, the headline
sem stays over 18 seeds against a bound of 15–18 draws, and that remains the honest publication.
This work makes the arithmetic ready and does not pretend the evidence is.
