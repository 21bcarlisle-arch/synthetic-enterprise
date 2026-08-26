# WORKER FINDING — a worst-cell headline floored at 1.0 by axes the company cannot learn

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-10 (worker tick) · **Atom:** `W2_2_population_draw` ↔ `C_cohort_discovery`
(surfaced while landing that pair's never-landed ledger row — `H_GAP_fabric_belief_truth_gap`)
**Class:** a WORST-OF-N headline computed over a cell set containing cells that are pinned at the
no-skill baseline **by construction**, so the headline cannot move when the company learns.
**Status:** OPEN, queued (SELF_INTERRUPT_DISCIPLINE — registered, not fixed on sight).
**Rank requested:** backlog. The row it affects landed clean this tick and is honestly noted.

## The finding, observed with evidence

`python3 -m tools.couple_cohort` scores 20 cells (5 axes × 4 tenures) and publishes the **worst**
one as the pair's gap. Twelve of the twenty read **exactly 1.0**:

```
accommodation  own_outright / own_mortgage / private_rent / social_rent   gap = 1.0
cars           own_outright / own_mortgage / private_rent / social_rent   gap = 1.0
nssec          own_outright / own_mortgage / private_rent / social_rent   gap = 1.0

price_sensitivity  social_rent    1.0345      channel_pref  social_rent   0.2621
price_sensitivity  own_mortgage   0.8701      channel_pref  private_rent  0.2391
price_sensitivity  private_rent   0.7766      channel_pref  own_mortgage  0.1401
price_sensitivity  own_outright   0.7068      channel_pref  own_outright  0.1163
```

The 1.0s are **not a measurement**. `tools/couple_cohort.py` names
`_NO_DISCOVERY_AXES = {accommodation, cars, nssec}` and states plainly that cohort discovery has
no mechanism for them, so the company's honest aggregate belief for those cells **is** the national
prior — which is precisely `g0`, the no-skill baseline the gap divides by. `gap = raw/g0 = 1.0`
identically, for every tenure, on every run, forever. That part is correct and honestly documented.

**The defect is what the headline then does with them.** Worst-of-N over a set containing four
permanently-1.0 axes means the published gap **can never read below 1.0**. Every improvement the
company could actually make — price_sensitivity is at 0.71–1.03, channel_pref at 0.12–0.26, both
with real discovery mechanisms and real room to move — is invisible to the headline until it
crosses 1.0, and below that the number is pinned to a structural constant.

The pair's row landed at `gap = 1.0344827586206897`, sourced from
`price_sensitivity::tenure=social_rent`. That single cell is the *only* one that can currently
move the headline, because it is the only one above the floor.

## Why it matters

Two known shapes at once:

- `feedback_headline_taken_over_one_truth_class_is_direction_blind` — the headline is decided by
  one cell out of twenty and reports nothing about the other nineteen.
- `feedback_worst_of_n_control_is_not_scale_invariant` — adding a sixth undiscoverable axis would
  not change the headline at all; adding a sixth *discoverable* one could only change it upward.

And a third worth naming on its own: **a metric floored at its own no-skill baseline is
indistinguishable from a company that has learned nothing.** A reader of the public door sees 1.03
and concludes the company is doing worse than blind on cohort discovery. On the two axes it has any
channel for, it is doing considerably better than blind. The headline says the opposite of the
truth about the part of the problem that is actually in play.

## Separately worth a look: `price_sensitivity::social_rent` > 1.0

`1.0345` means **worse than blind** on that cell — the gap metric's own documented red. It is one
cell of twenty and could be sampling (n=434), but the metric family defines >1.0 as an actively
harmful model, and nothing currently flags it. Whether that is real or noise is a measurement this
finding does not make.

## What would close it (not built here)

The choice is a design question for whoever owns the pair, and the options are not equal:

1. **Score the headline over discoverable axes only**, and publish the undiscoverable ones as a
   named, separate *coverage* figure ("3 of 5 axes have no discovery mechanism"). Recommended:
   it keeps both facts, and neither hides the other. The undiscoverable axes are a real and
   important statement about the company — they are just not a *gap measurement*, and averaging
   a structural constant into a learned quantity destroys the learned one.
2. Keep worst-of-N over all 20 and accept the headline is a floor indicator. Cheapest, and it is
   what exists; it should then be *labelled* as a floor rather than read as a gap.
3. Report per-axis gaps with no single headline. Honest, but the coupled-triad ledger contract
   wants one number per pair.

Do **not** close it by dropping the undiscoverable axes silently — that is the exclusion-shaped
fail-open this project already has memory of
(`feedback_coverage_derived_from_exclusion_source_is_failopen`). Whatever is excluded from the
headline must be published beside it.

## Evidence

- `tools/couple_cohort.py` — `_SCORED_AXES`, `_NO_DISCOVERY_AXES` and the comment explaining why
  the no-discovery belief is the full national prior.
- `background/gap_metric.py` module docstring — `gap = 1 -> the company does no better than the
  blind prior`.
- Per-cell table above: `python3 -m tools.couple_cohort`, this tick, 3000 customers, seed 20260721.
- `docs/observability/coupled_gap_ledger.json` — `W2_2_population_draw`, landed this tick.
