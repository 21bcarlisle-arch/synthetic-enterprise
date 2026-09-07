# NESO Demand Flexibility Service — the called-day response, and what it costs

**Knowledge:** how-households-choose

*At best 22.4% of registered households opted in to any single event, participation did not rise with
a 12.9× price range, and NESO's own reading is that it is "not wholly financially driven". That is
this page's subject — how a household chooses, and why most don't — measured on the one GB product
that ever asked them directly.*

**Task:** settle the **called-day attention premium** that
`docs/staging/SEAT_RESULT_THE_SKEW_IS_ENTIRELY_IN_THE_TROUGH_AND_THE_TROUGH_IS_BOUNDED_IN_MONEY_2026-09-07.md`
(landed `8f5239deb`) carried as a break-even at **2.53×**, and supply the world anchor that
`docs/design/W1_9_DSR_FLEX_MARKETS_DISCOVER.md` found missing behind
`_DFS_RATE_GBP_PER_MWH = 4.5` and `_DISPATCH_EVENTS_PER_YR = 20`.

**Pre-registered** at `docs/staging/SEAT_PREDICTION_WHAT_NESOS_DFS_CAN_AND_CANNOT_SETTLE_ABOUT_THE_ATTENTION_PREMIUM_2026-09-07.md`,
landed `2ae8dc01a` **before any source below was fetched**.

**Epistemic scope:** discovery only. Sources are NESO's own published winter reviews plus one
peer-reviewed-adjacent consumer study. Nothing here reads simulation state. Every figure carries
its source; where a winter is not established from a primary source it is recorded as **NOT
ESTABLISHED** with the reason, not filled with a plausible number.

**Epistemic wall:** DFS prices, event counts, delivery volumes and rules were published by NESO on
a public data portal and in public winter reviews. A real GB supplier not only *could* know these —
31 of them were counterparties to the service. Nothing here crosses the wall.

---

## 1. What the service is, and why it is the right instrument

DFS paid consumers to **reduce** demand against a baseline, in a declared window, **only on days it
was called**. That is structurally the same product as an extreme-day-only time-of-use tariff, and
it is the only GB product that has ever run it at national scale. It ran winter 2022/23, 2023/24 and
2024/25, and from 2024/25 became an all-year merit-based tool under an Ofgem derogation to
31 March 2027.

Baseline was the BSC **P376** methodology: the consumer's average usage over the previous 10 eligible
working days, with an in-day weather adjustment for domestic consumers based on usage 4h–1h before
the delivery window. Delivery = baseline − metered actual. Half-hourly (smart) metering required.

---

## 2. The established figures

### Winter 2022/23 — the founding winter *(NESO, "Demand Flexibility Service: Winter 2022/23 review", August 2023)*

| quantity | value |
|---|---|
| events | **22** — **20 tests** and **2 live** |
| test settlement periods | 40 (20 × 1-hour events) |
| live settlement periods | 5 (23 Jan ×2, 24 Jan ×3) |
| test delivery / cost | 2,667.7 MWh / £8.0m → **£2,999/MWh** |
| live delivery / cost | 680.0 MWh / £3.1m → **£4,559/MWh** |
| **total** | **3,347.7 MWh / £11.1m → £3,316/MWh** |
| Guaranteed Acceptance Price (tests) | **£3,000/MWh**; highest accepted in live events £6,500/MWh |
| participants | >1.6m households and businesses, 31 approved providers |
| concurrent providers | grew 4 → 21 over the winter; DFS units 10 → 35 (c.350 MW) |
| live events, procured vs delivered | 795.4 MWh procured, 680.0 delivered — **85.5%** |
| test events, procured vs delivered | **over**-delivered on the winter best-fit |

Domestic household earnings, Octopus data *(via Carbon Brief Q&A)*: **23p average per household per
test event**; best case £4.35 per session; largest domestic live-event saving ≈£8.75 for the hour.
Across 22 events that is **≈£5 for the whole crisis winter**, at £3,000–4,559/MWh.

### Winter 2023/24 — **NOT ESTABLISHED**

Secondary reporting gives 2,507 MWh and separately 3,759 MWh / "over 3.7 GWh", ~2.2–2.6m registered,
and 6 tests + 2 live. **These do not reconcile and no primary NESO end-of-year report for 2023/24 was
retrieved in this pass.** Recorded as a gap rather than averaged into a number. Closing it needs the
NESO Winter 23/24 End of Year Report.

### Winter 2024/25 — the merit-based winter *(NESO, "Demand Flexibility Service", published 3 July 2025)*

| quantity | value |
|---|---|
| Service Requirements published | **56**, covering 306 SPs |
| events with volume procured | **44**, covering 236 SPs |
| bid / accepted / delivered | 10,983.5 MWh / 5,449.6 MWh / **3,917.7 MWh** |
| accepted tenders / paid for delivery | £1,223,312 / **£943,983** |
| **realised price** | 943,983 ÷ 3,917.7 = **£241/MWh** |
| delivery accuracy vs bid | **71.90%** (Dec 66.7%, Jan 64.8%, Feb 65.6%, Mar 82.1%) |
| registered | **1.98m MPANs**, 28 providers |
| best single-event participation | **443,224 MPANs** (19 Mar 25) = **22.4% of registered** |
| accepted prices, top-10 participation events | **£100 – £1,290/MWh** |
| test events / GAP issued | **none** — retained in the rules, never used |
| domestic delivery size | **91% below 1 kW**, 9% between 1–10 kW ("consistent with previous winters") |
| domestic / I&C split of volume | roughly 60 / 40 |

**£943,983 ÷ 1.98m registered MPANs = 47.7p per registered MPAN for the entire winter** — gross to
providers, before the provider's own margin and before anything reaches a household.

### Household response *(Centre for Net Zero (Octopus Energy Group), via UKERC)*

Over 1m Octopus customers studied, ~700,000 DFS participants, 13 sessions offered to 1.4m customers,
1,642 MWh reduced over 14.5 hours:

- **40%** reduction among those who **signed up and opted in** to an event
- **10%** reduction among those **simply invited** to take part
- Saving Sessions overall: **12–25%** demand reduction
- **Official DFS figures overestimate the effect by about 13%** — the P376 baseline over-credits.

---

## 3. The attention premium — three readings, and only one of them is a premium

The break-even in `tools/tou_extreme_day_concentration.py::break_evens` is a **multiplier on
called-day response at an unchanged faced price ratio** (company value is linear in response, so it
is the ratio of the two optimised company values). So the counterpart quantity must hold the price
signal and the population fixed, and vary only whether the day was *called*.

**Reading 1 — NESO's live-vs-test, the direct salience experiment. 1.20×.**
> "Enthusiasm for consumer flexibility reached an unprecedented scale during the 'live events', with
> consumption reduction **20% higher than test events**." *(NESO 2022/23 review, executive summary)*

Same enrolled households, same product, same settlement — differing in that a live event was a
genuine, nationally-reported system-margin emergency and a test was a routine scheduled monthly
event. That is the largest salience contrast the real product has ever run. **It bought 1.20×.**

And it was **not** bought at a constant price: live events paid **£4,559/MWh against the tests'
£3,000/MWh, a 1.52× uplift**. Per unit of price signal the called day therefore bought
**1.20 ÷ 1.52 = 0.79×** — *less* response per pound than the routine test.

**Reading 2 — a deliberately generous upper bound. 2.04×.**
Live delivery per settlement period 680.0 ÷ 5 = **136.0 MWh/SP**; test delivery per settlement period
2,667.7 ÷ 40 = **66.7 MWh/SP**. Ratio **2.04×**. This credits the called day with the *entire*
winter's portfolio growth (4 → 21 concurrent providers, 10 → 35 units) even though the live events
fell in January, mid-growth, and with the 1.52× price uplift as well. It is an upper bound and
nothing more. **It still does not reach 2.53×.**

I could not reconstruct NESO's own "20%" from Tables 1–3 of their report; my unnormalised
reconstruction is the 2.04× above. Both are recorded rather than reconciled, and the conclusion is
taken from the **bracket**, which is what makes it robust: *every reading that holds the population
fixed lands in 1.20×–2.04×.*

**Reading 3 — 40% ÷ 10% = 4.0×, which is NOT a premium and must not be used as one.**
This clears the break-even, and it is a composition artefact. The 40% is a **selected subgroup**
(those who opted in); the 10% is the **population average over everyone invited**, which includes
every household that ignored the call. If ~25% opt in and each cuts 40%, the population average is
exactly 10% — the two numbers are one number and an opt-in rate. Dividing them measures
**who answered**, not **how hard they pushed**.

The A49 model applies its response to every household on every qualifying day, so it needs the
population-average figure on **both** sides. Using 40% against a population-average standing
response would be the project's own named failure — *before dividing two numbers, say out loud what
each one counts* — and would have flipped the verdict on an arithmetic identity.

**Corroboration.** Across 2024/25's top-10 participation events the accepted price ranged
**£100–£1,290/MWh (12.9×)** and participation did **not** rise with price; the two most expensive
events had the *lowest* participation of the ten. NESO: *"consumers appetite to participate and
engage are not wholly financially driven."* This is confounded with registration growth over the
winter (Jan events are early and small-base, March events late and large-base), so it is
corroborating and not decisive — but no reading of it produces a positive price response.

**Correction direction.** CNZ's finding that DFS figures over-credit by ~13% applies to the called-day
side of every ratio above, pushing all of them **further below** the break-even.

### Verdict

| | |
|---|---|
| break-even the extreme-day product must clear | **2.53×** |
| best direct measurement (NESO live vs test) | **1.20×** |
| generous upper bound (unnormalised per-SP) | **2.04×** |
| per unit of price signal | **0.79×** |

**The called-day attention premium does not clear the break-even.** The MERELY RARER verdict on the
extreme-day-only TOU tariff **stands, and is now settled against the real GB product rather than
carried as a hedge.**

## 4. The independent convergence, stated for what it is

| route | household value |
|---|---|
| A49 everyday TOU tariff, perfect foresight, GB wholesale record | **£0.75/household/year** |
| DFS 2024/25, realised payments ÷ registered MPANs | **£0.48/MPAN/winter** (gross to provider) |
| DFS 2022/23, crisis winter at £3,000–4,559/MWh | **≈£5/household/winter** (23p × 22 events) |

Two independent routes — a modelled tariff over the wholesale record, and the actual settled
payments of the real product — land on the same order of magnitude, **pennies to low pounds per
household-year**, against a sourced £27.50 acquisition cost. The 2022/23 figure is ten times the
others and is a **crisis derivative**: it required a GAP of £3,000/MWh, which is 12.5× the price the
same service cleared at once it had to compete.

---

## 5. What this settles for `W1_9`'s two constants

**The rate is not a constant and 4.5 is not its value.**

| winter | realised £/MWh | vs `_DFS_RATE_GBP_PER_MWH = 4.5` |
|---|---|---|
| 2022/23 | £3,316 | **737× too low** |
| 2023/24 | NOT ESTABLISHED | — |
| 2024/25 | £241 | **54× too low** |

The comment "NESO DFS average 2022-24" cites a source that says the opposite of the value. The same
file's own docstring says suppliers "can earn **£3-6/kWh**" — £3/kWh **is** £3,000/MWh — so
`flexibility_potential.py` disagreed with itself by a factor of ~1,000 in ten lines. The value looks
like a units error (£/kWh mis-entered as £/MWh, then rounded) that nothing could catch, because the
test asserting it recomputes the production formula from the same constants.

**The event count is the wrong quantity, not just the wrong number.** `_DISPATCH_EVENTS_PER_YR = 20`
matches the 2022/23 **test** count — and 20 of those 22 events were scheduled by **calendar** ("two
onboarding tests in the first month, two regular tests per month thereafter"), not by system need.
Only **2** were called by system conditions. Established counts: **22 (2022/23)**, **44 with volume
procured, of 56 published (2024/25)**.

**Can it be world-derived? No — and this is a finding, not a deferral.**

NESO's own trigger for 2022/23: *"A live event could be triggered when insufficient upwards
flexibility was foreseen at the day ahead stage and we believed the inadequacy could not be solved
by our existing services and market incentives."* That is a **discretionary judgement**, not a rule
against an observable series, and NESO published no deterministic criterion in any winter. In
2024/25 the service moved within-day and merit-based, so events track system conditions more
closely — but NESO still published 56 requirements and procured on only 44, and the difference is
market clearing, not physics.

So a world-derived event rate keyed to a price/stress signal would model the wrong generating process
for the founding winter (91% calendar-driven) and an unpublished one thereafter.
**P6 held: the honest outcome is *sourced per winter*, not *derived*, and the derivation stays a named
gap depending on `W1_6_physics_price_signal` (`level_current: 0`).**

**Three things the constants omit entirely**, all established above and all pushing revenue down:

1. **Opt-in.** At best **22.4%** of registered MPANs participated in any single event. The model
   credits 100%.
2. **Delivery shortfall.** **71.9%** of bid volume was delivered (2024/25); live events in 2022/23
   delivered **85.5%** of procured. The model credits 100%.
3. **Per-MPAN size.** **91% of domestic delivery is below 1 kW.** The model credits a 7.4 kW EV
   charger plus a 5 kW battery at full rated power.

Compounding just the first two is a **0.224 × 0.719 = 0.161** haircut — before the size point.

---

## Sources

- [NESO — Demand Flexibility Service: Winter 2022/23 review, August 2023](https://www.neso.energy/document/287006/download)
- [NESO — Demand Flexibility Service, published 3 July 2025 (Winter 2024/25 review)](https://www.neso.energy/document/363911/download)
- [NESO — Demand Flexibility Service (DFS) service page](https://www.neso.energy/industry-information/balancing-services/demand-flexibility-service-dfs)
- [NESO — DFS 2022/23 Live Events data portal](https://www.neso.energy/data-portal/demand-flexibility-service-live-events)
- [UKERC — Demand meeting supply: how the system operator asked households to help keep the lights on](https://ukerc.ac.uk/news/demand-meeting-supply-how-the-system-operator-asked-households-to-help-keep-the-lights-on/) (reporting Centre for Net Zero analysis)
- [Centre for Net Zero — The Impact of Demand Response on Energy Consumption and Economic Welfare](https://www.centrefornetzero.org/papers/the-impact-of-demand-response-on-energy-consumption-and-economic-welfare)
- [Carbon Brief — Q&A: How Great Britain's 'demand flexibility service' is cutting costs and CO2 emissions](https://www.carbonbrief.org/qa-how-great-britains-demand-flexibility-service-is-cutting-costs-and-co2-emissions)
