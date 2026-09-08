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


---

## BUILT 2026-09-08, and the director corrected the design before it was written

The section above proposed a turn-down with a **stated comfort cost**. That design was refused, and
the refusal is better than the proposal:

> *"Don't price comfort — floor it. A comfort cost makes warmth a willingness-to-pay question,
> and the households that would accept the trade are the ones who can least afford to refuse it, so
> the model would find the fuel-poor and recommend they be cold. That's advising self-rationing in a
> cold home, which the use-case register says we detect rather than cause."*

**A price can be beaten by a large enough saving. A floor cannot.** My version would have been
defeated by exactly the households it most needed to protect, because their savings are the
largest — the section above even says so ("the households for whom a turn-down scores best are
the coldest") and then proposed a mechanism that cannot act on its own observation.

The floor is **18 °C**, WHO guidance carried into NICE NG6. It bites in the right place with no
extra rule, because EFUS measured internal temperature by EPC band: A–C clear it, D through G do
not, and an unknown band fails closed. The refusal names the finding — *the fabric needs work,
not the thermostat* — and filters the choice set rather than declining the premise, so a cold
household still gets a recommendation.

**The dependency named above was real and was honoured:** the hot-water correction landed first,
so the saving is computed on a demand figure that is no longer 1.4–1.6× the measured value.

## What is still not fixed, and it is the original point

**The only zero-capital measure now reaches EPC A–C only.** The households with no capital are
largely in D and below — and they are refused, correctly, because they are already too cold to
turn down. So this does **not** solve the problem that opened this document. It makes the model
honest about it rather than solving it.

The measure that would solve it is **flow temperature**: dropping a combi from 80 °C to 55 °C costs
nothing, recovers roughly 6–10% by letting the boiler condense as designed, and **does not make the
home one degree colder** — so it never meets the health floor at all. It is the best
cost-to-benefit measure in the real set, it is available to exactly the households this floor
excludes, and it remains absent. It is blocked on a source, not on physics, and it is now the
highest-value item in this lane.

## DISPOSITION — 2026-09-08, delivery seat

**MINTED as `W2_34_the_company_has_one_piece_of_advice_that_costs_the_customer_nothing`**
(lane `W2_customer_generator`, L1 → L3), and **BUILT**. `Atom: unminted` above is superseded by
that row.

**Item 1 — the hot-water correction — is spent.** It landed (`206b6215a`, "the hot-water
correction meets the lanes that landed beside it"), so the stated one-directional dependency that
held this finding back is discharged and the order it fixed was honoured.

**Item 2 is built and item 3 is built.** `company/pricing/fabric_intervention.OFFER_BOOK` now
carries `turn_down` at £0 capex with a one-year life and a `demand_reduction_fraction` of 0.06;
`test_THE_OFFER_BOOK_CONTAINS_A_ZERO_CAPITAL_MEASURE` is item 3's control, keyed to the mission's
advice leg rather than to today's catalogue.

**Item 2's stated design was refused and replaced, and this is the substantive correction to this
finding.** The finding asked for *"a stated comfort cost"* and *"a TRADE the customer is shown"*.
That design was put to the director and refused on 2026-09-08, verbatim: *"A comfort cost makes
warmth a willingness-to-pay question, and the households that would accept the trade are the ones
who can least afford to refuse it, so the model would find the fuel-poor and recommend they be
cold."* So comfort is **floored, not priced** — below `HEALTH_FLOOR_INDOOR_C = 18.0` (WHO/NICE NG6)
the measure is not offered at any value. The finding had already identified the hazard correctly
(EFUS: EPC F/G at 17.2 °C against 19.3 °C for A–C); what it got wrong was the remedy. A price can
be bought off by a large enough saving and a floor cannot, and
`test_NO_SAVING_HOWEVER_LARGE_BUYS_A_TURN_DOWN_BELOW_THE_FLOOR` is the control for exactly that
distinction.

**One quoted figure was NOT taken from the finding's own arithmetic.** The finding derives the
saving from degree-days. Measured over the HadUK-Grid normals for all 245,077 GB land cells, a
one-degree drop removes 11.7 % of annual degree-days at an 18 °C base and 14.3 % at 15.5 °C — but
that is an upper bound for a continuously-heated house, and real heating is intermittent. The book
quotes **6 %**, the cautious end of the published field range, because overstating a saving to a
household that then does not see it is a mis-selling harm and the asymmetry is not symmetric.

**What is NOT done, and is carried on the atom rather than here.** No production caller passes
`epc_band`, so `decide` reaches only the fail-closed branch and no household in the coupled run is
offered the measure. The seam field is missing: `thermal_inference.EpcCertificate` carries
`build_era_band` and no A–G efficiency band. That is the L2 exit. **Item 4 — flow temperature —
is untouched and is the L3 exit**; it remains the measure that actually answers this finding's
title, because it costs nothing AND does not make the home colder, so it never meets this floor.

**Moved out of the staging root to `done/`.**
