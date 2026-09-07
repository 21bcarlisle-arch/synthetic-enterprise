# [DIRECTOR-CANON] — The demand vector: simulate difference, not averages (2026-09-07)

**Type:** [CANON — the deliverable the world must produce, the resolution it must produce it at, and the defect that has twice hidden the requirement. Severity: BLOCKING — two live coverage claims rest on the collapse this document names. Mechanism and measurement are the delivery seat's; the deliverable and the separation are the director's.]

---

## 1. The defect: a scalar standing in for a vector

Twice in two days a coverage claim has been measured against a single number where the thing being served is several.

**On outputs.** Demand coverage was measured on total annual kWh, giving 13 cases against 273 for a separable composition. But a cold-and-insulated house and a mild-and-leaky one can produce the same annual total and be completely different customers: different winter-to-summer ratio, different peak, different bill shock, different hedge. Gas-heated and electrically-heated households at the same total are not the same case at all. On a scalar they collapse to one; to a supplier they are several.

**On inputs.** Three separate weather grids — 21 temperature, 21 wind, 5 irradiance — assume a household's response to weather is separable. The project's own measurement says it is not: solar gain moves fuel −1.2% in a leaky pre-1919 house and −7.9% in a tight post-2000 one; wind moves the heat loss coefficient +18.6% mid-stock and +2.9% in that same modern house, because Part F's minimum air change rate clamps the calm end. **The response to each driver depends on the fabric**, so what matters is the joint weather condition, not each driver in turn. A glazed house in a sunny-but-cold cell and a leaky house in a windy-but-mild cell are different demand cases; three grids average over exactly that.

The joint partition was set aside as "a question nothing here asks". It is the question, because the sample must span **differences in response**, not averages — which is why 987 is closer to right than 21/21/5.

**This is a known class, already caught once.** On 6 September the sample size moved from 100 to 250+ on the finding that *"rejecting on outputs is still blind if they aren't the outputs anything is scored on."* The same collapse then reappeared on both sides within a day. It flatters in a consistent direction — always making the sample look smaller and the coverage look better — which is why it must be looked for rather than waited for.

---

## 2. The deliverable

The drawn population must reproduce the **observed distribution** of, per household:

- annual gas
- annual electricity
- the seasonal shape of gas
- the half-hourly shape of electricity
- heating fuel type — gas, electric, other

**A household is a vector, not a number.** The sample must span the range of those vectors across the stock, **including the tails**, not match their averages. Every coverage, ceiling and sufficiency claim is measured against that vector or it is measuring something else.

---

## 3. The resolutions, and why they differ

**Gas: seasonal shape is enough.** The price does not move within a month. What varies is the annual total and how it distributes across the year.

**Electricity: half-hourly is required.** That is where the price and the settlement live. Two households with identical annual kWh — one with a sharp evening peak, one flat through the day — are a different cost to serve and a different hedge.

**The resolution is set by the price, not by the physics.** That is the whole reason the two fuels differ here.

**The consequence for what exists today.** The world rescales one national profile, so every household has the same half-hourly shape — and therefore the same time-of-use cost profile. The price signal is invisible to the model, which makes time-of-use tariffs, flexibility, and hedging by physics all unmeasurable. Per-household shape is not an enhancement to the demand work; it is the deliverable.

---

## 4. Two layers, kept separate

The people work must hold two layers apart, even though they correlate.

**The physical layer** drives kWh and shape: occupancy count, presence pattern, heating schedule and setpoint, appliance and asset ownership.

**The commercial layer** drives payment, arrears, churn and elasticity: income, fuel poverty, payment method, credit risk, attitude.

People phase 1 as currently ruled mixes them. Merged, we cannot tell a household that used less because nobody was home from one that could not afford it — and those demand the opposite response from a supplier.

**Model the correlations between the layers** — income to house size to occupancy is real — but as correlations, not as one layer. **The physical layer is what stage 1 needs.** The commercial layer follows.

---

## 5. The standing test

**Simulate difference, not averages.** Every number in this programme — cells, cases, coverage, sample size — is only worth having if what comes out is a range of usage by fuel with credible shapes, spanning the observed spread. A well-anchored central case is not the goal and never was.

Where a coverage or sufficiency claim rests on a scalar and the thing being served is a vector, it is this defect and it has flattered us. Look for it rather than waiting for it.

**Answers come as price lists, not single numbers.** 95% and 99%, with what dominates the count stated. If the honest answer is that the sample must be much larger than anything discussed so far, that is the answer: a large sample that reproduces the range beats a neat one that cannot.

---

## 6. What this does not decide

The mechanism, the partition method, the measurement design, and the number itself. All the delivery seat's. This says what must be reproduced and at what resolution, not how.

## WORK THIS CREATES (canonical, in-document)
1. Coverage re-measured against the demand vector, reported at 95% and 99% with the dominant term named.
2. The weather partition re-opened as a joint question over a stock with varying fabric.
3. A sweep for the same scalar collapse in every other coverage, ceiling or sufficiency claim.
4. Per-household half-hourly electricity shape and seasonal gas shape as the demand deliverable.
5. People phase 1 re-cut so the physical layer stands alone, with the commercial layer correlated rather than merged.

— Director canon, 2026-09-07. The point of the world is to contain difference. A model that reproduces the average of a stock it cannot span is a model of nobody.
