**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `W2_4_affordability_as_sim_physics`

# Two red controls that predate today's work, and the affordability xfail is claiming something that stopped being true

Found while regressing the settlement-timetable correction of 2026-08-29. Both were on my
suspect list because I had just doubled the published book, and **neither is mine** — attributed by
counterfactual rather than by argument, which is the only thing that separates these two cases from
the ones I did cause.

## 1. `test_live_run_output_shows_crisis_step_up_headline` — a stale strict xfail

Marked `xfail(strict=True)` with this reason:

> *AFFORDABILITY_AS_SIM_PHYSICS.md: arrears are currently propensity-shaped, not emergent from a
> household budget meeting a price shock — so the headline bad-debt trajectory shows no real
> 2021-22 crisis step-up. EXPECTED to fail until the W2_4.. affordability cluster (M3) is built.
> Do NOT satisfy this by tuning a bad-debt parameter (R12).*

**It passes, so the strict marker turns the pass into a suite failure.** I assumed I had caused it —
the book went from 45 campaign accounts concentrated in 2016-17 to 90 spread across ten years, which
is exactly the kind of cohort-mix change that could manufacture a step-up. **The counterfactual says
otherwise.** Running the validator over the run output from `d5d58da62` (the commit before any of my
work) and over the current one:

```
BEFORE (d5d58da62): crisis(2021-22) rate=2.0059% vs pre-crisis(2016-19)=1.5698%  x1.28  PASS
AFTER  (my change): crisis(2021-22) rate=2.0059% vs pre-crisis(2016-19)=1.5698%  x1.28  PASS
```

**Byte-identical, and already passing before I touched anything.** The marker was stale on arrival.
It is a plausible member of the 17 newly-failing tests reported at HEAD at 03:30Z.

**What is NOT established, and matters more than the marker:** whether that ×1.28 is affordability
physics or an artefact. The xfail's substantive claim — arrears are propensity-shaped, not emergent
from a budget meeting a price shock — appears to be **still true**; nothing in M3 has been built. So
a control designed to stay red until the mechanism exists is green while the mechanism does not
exist, which means **it was never testing the mechanism.** Deleting the marker would publish "the
crisis step-up is real"; leaving it strict keeps every lane's suite red. Neither is right, and the
resolution belongs to whoever owns W2_4 with the evidence in front of them — the question to answer
first is *what would have to be true for a propensity-shaped arrears model to produce a 1.28x
step-up*, because something already does.

## 2. `test_the_non_domestic_share_under_a_domestic_bound_stays_small` — pre-existing, and my work moved it toward green

> *5.3% of the priceable book (8 of 150) is non-domestic and is being priced under a bound derived
> from the Ofgem DOMESTIC cap, which defends nothing about a business account. Derive a
> non-domestic bound — do NOT raise this threshold.*

Threshold is 5%. Not caused by the book change, and the arithmetic settles it without a re-run: the
campaign quotes `DOMESTIC_ONLY` (`{"resi": 1.0}`), so **every account it adds is domestic**. The 8
non-domestic accounts are opening-book, and the numerator cannot have grown while the denominator
did. Before the change the priceable book was smaller, so the share was *higher* — this control was
redder yesterday. It is genuinely open and the instruction on it stands: derive a non-domestic
bound, do not move the threshold.

## WHAT THIS CREATES

1. **A decision on the affordability marker**, owned by W2_4 and not takeable from here: the control
   cannot both stay strict and stay green, and un-marking it makes a claim about the world.
2. **The prior question underneath it:** what produces a 1.28x crisis step-up in a model that is not
   supposed to be able to produce one. That is worth more than the marker.
3. **A non-domestic price bound** (item 2), still open and still explicitly not to be satisfied by
   moving the threshold.
