**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`
· **Class:** no_caller_and_never_runs

**Knowledge:** none — this is a gap in the company's own decision surface, not domain
understanding. The physics behind the proposed offer is published already in
`docs/market_research/gas_demand_what_drives_it_and_the_term_the_model_is_missing.md`.

# Every piece of advice the company can give costs the customer at least £300

**Found 2026-09-08 at `81b355046`**, tracing what the director's stated use case would actually
call — *"a customer who wants to budget needs to see the daily cost effect of changing their
thermostat or their timer."*

---

## The offer book, in full

`company/pricing/fabric_intervention.OFFER_BOOK`:

| measure | capex |
|---|---:|
| `insulate` | £6,000 |
| `heat_pump` | £12,000 |
| `solar_pv` | £7,000 |
| `time_shift` | £300 |

**There is no zero-capital offer.** No thermostat set-point change, no heating-schedule change, no
flow-temperature reduction. The company can recommend spending money and it cannot recommend
anything else.

Against the mission, verbatim: *"saving them money, time and carbon, through personalised
modelling, tariffs and **advice**."* Advice is a third of the stated mechanism and the company has
none — every route it has to a customer's bill runs through the customer's capital.

**And this is not a small omission of value.** A 1 K set-point reduction removes roughly 6–10%
of space-heat demand at zero cost. For the median gas-heated household in our own book that is on
the order of 700 kWh a year, which is the same order as the £6,000 `insulate` measure delivers, for
nothing.

## The physics needs no new constant, which is why this is worth doing properly

`offer_annual_saving_kwh` already receives everything required:

    saving_kwh = hlc_kw_per_k * delta_T_k * heating_day_count * 24

A set-point reduction of ΔT reduces degree-days by exactly `ΔT × heating days`. Expressed against
the existing signature it is `fabric_heat_kwh(...) * (ΔT * heating_days / annual_degree_days)` —
every term already a parameter. **No coefficient is invented, and the rule this obeys is the
director's own: theorise where the physics is solid, and heat loss and ΔT are as solid as it gets.**

The same frame gives the timer: shortening the heated period changes the hours term, and
`premise_trace` already carries a per-premise setpoint schedule and derives consumption changes from
the physics rather than multiplying a factor on
(`comfort = base_schedule.comfort_setpoint_c - constraint.setpoint_reduction_c`). The machinery
exists and is pointed only at INVOLUNTARY rationing — income stress and price response. The
customer's own choice is the same mechanism with a different input.

## THE PART THAT MUST NOT BE OMITTED, AND WOULD BE

**A turn-down is not free, and the cost is comfort.** An offer book that prices capex and nothing
else would enter this at a cost of £0 and it would win every ranking, every time, for every
household. That is the director's own rule pointed at us: *omission is not neutrality — it
asserts zero, and zero is usually the one value we know is wrong.*

Worse, it is wrong in a way that harms the customer rather than the company. The households for
whom a turn-down scores best are the coldest, worst-insulated ones — and EFUS measures those
households already sitting at **17.2 °C** against 19.3 °C for EPC A–C. **The model would
recommend the coldest households in Britain turn their heating down**, and score it as value
created.

So the offer needs a stated comfort cost from the start, and the honest framing is a TRADE the
customer is shown rather than a saving the company recommends. `_MAX_SETPOINT_REDUCTION_C` and
`comfort_hours_retained` exist in `premise_trace` as the world's model of forced rationing; the
company's version is a different quantity and must not silently reuse them.

## Why it is NOT built in this commit

**It scales with `annual_heat_kwh`, which is currently inflated.** The settlement path's hot-water
model emits 1.4–1.6× the measured value
(`SEAT_FINDING_THE_SETTLEMENT_PATHS_HOT_WATER_IS_HALF_AGAIN_THE_MEASURED_VALUE_AND_I_BUILT_THE_SECOND_COPY_2026-09-08`),
which overstates every household's demand by roughly 730 kWh a year. An advice capability built on
that would tell customers they will save more than they will.

Of everything touched today this is the closest to the sharp end — it is the one output a real
person would act on — so it waits for the correction rather than being built on a number known
to be wrong and corrected afterwards. **The dependency is one-directional and the order is
therefore fixed:** fix the hot-water model, then build the advice.

## What is next, in order

1. **The hot-water correction** — one implementation, with the director's re-baseline decision.
2. **A `turn_down` offer at zero capex**, saving computed from the physics above, with a stated
   comfort cost and no default of zero.
3. **A control that the offer book contains at least one zero-capital measure**, keyed to the
   mission's "advice" leg rather than to today's catalogue, so this cannot silently revert to a
   book that only knows how to spend the customer's money.
4. **Flow temperature**, still absent and still the best cost-to-benefit measure in the real set,
   still blocked on a source rather than on physics.
