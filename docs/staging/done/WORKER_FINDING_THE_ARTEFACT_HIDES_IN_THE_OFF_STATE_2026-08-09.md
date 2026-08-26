# WORKER FINDING — a determinism artefact hides in the generator's OFF STATE

**Severity:** LATENT · **Lane:** W2_customer_generator

**Date:** 2026-08-09
**Found by:** W1_12 L2->L3, diagnosing the population-scale L1.5 breach
**Class:** R15 / control-and-generator design. Queued per SELF_INTERRUPT_DISCIPLINE
(the instance is fixed because it was the drawn atom's own exit test; the CLASS
below is the part that generalises and is NOT yet mechanised anywhere).

## The instance

`L1.5_max_multiplicity_share` is the two-level suite's structural artefact
detector: it counts how often the same `x[t] / daily_total` fraction recurs, and
it exists to catch a generator that rescales one fixed base shape. On the drawn
population of 200 it failed with 7 homes outside band (worst P0108 at 0.15
against a 0.10 threshold).

The mechanism, **measured rather than inferred**: for all 7 violators, *every*
occurrence of the most-repeated fraction landed on an **away day**. Recomputing
the same statistic with away days excluded dropped all seven to 0.043-0.061,
comfortably inside the band. On P0108's five away days the daily total was
`2.031360` kWh on all five, identical to six decimal places.

Why: an away day drew nothing. Occupancy is 0, so appliance events, DHW events,
EV charging and the switched lighting/electronics banks all contribute nothing —
every stochastic component in the generator is gated on occupancy. What is left
is a constant standby plus a deterministic compressor square wave. The empty
house was a byte-identical clone of itself, every time.

Fixed in the generator, band untouched: a cold appliance's duty is a heat balance
(`room - cabinet`), not a constant, so away days now differ because the weather
does. 7/200 -> 0/200.

## The class

**Every stochastic component was correctly gated on occupancy, and that is
exactly what created a fully deterministic state.** The diversity machinery a
generator relies on is usually conditional — on occupancy, on trading hours, on
season, on a customer being active — and wherever *all* of those conditions go
false at once, the generator falls back to its skeleton. The skeleton is
deterministic, because determinism is what a skeleton is.

So the artefact does not hide where the generator is busy. It hides in the OFF
state, which is the state nobody inspects, because it looks boring and it is a
small share of the days.

Three properties made this hard to see, and all three recur:

1. **It is a minority of days inside a minority of homes.** 7 of 200 homes, each
   from ~20 of 120 days. A per-home statistic averaged over the window dilutes it
   by a factor of six before anyone looks.
2. **It is invisible to a level check.** The away-day total was *correct* — a
   plausible empty-house consumption. Only the SHAPE repeated. Any control
   reading totals, annual kWh or a mean passes it.
3. **The panel could not contain it.** It needs enough homes for the away-day
   calendars to be long enough, and the 10-home authored panel simply did not
   breach the band.

## What to check, on any generator with an off state

- Enumerate the conditions the stochastic components are gated on. Where they can
  ALL be false simultaneously, that combination is a candidate clone state.
- Assert the off state against ITSELF, not against the on state: two occurrences
  of the off state under different exogenous drivers must not be identical. The
  test is one line and it is the one nobody writes.
- Suspect any control breach whose violators share an attribute the control does
  not mention. Here the shared attribute was "has many away days" and the control
  says nothing about away days at all.

Candidate off states elsewhere in this codebase, NOT checked (this is the queued
work, not a claim): a closed/vacant supply point, a customer between supply
start and first read, an out-of-season gas trace, a settlement run with no
disputes, a day with no trades.

## Related

- `[[feedback_never_pin_generated_values_in_controls]]`
- `WORKER_FINDING_WORST_OF_N_CONTROL_IS_NOT_SCALE_INVARIANT_2026-08-09.md` — the
  same population run's other finding; that one is about the STATISTIC, this one
  is about the GENERATOR.
- `docs/design/PREMISE_TWO_LEVEL_TEST_HARNESS_SPEC.md`
