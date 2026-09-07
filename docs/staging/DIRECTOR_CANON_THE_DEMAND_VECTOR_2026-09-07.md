# [DIRECTOR-CANON] — The demand vector: simulate difference, not averages (2026-09-07)

**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

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

**And the vector is a validation target, not a sufficient design target** — adopted from the delivery seat's challenge of 2026-09-07, which is right. Two households with identical gas, electricity, shape and fuel can have opposite insulation ceilings: one already retrofitted, one not. A sample that reproduces consumption perfectly can still be unable to rank interventions, and ranking interventions is the mission. NEED carries `LI_FLAG`, `CWI_FLAG` and `PV_FLAG`, so this is measurable today.

**Two numbers are therefore reported, and the second is the real one:** N to reproduce the observed distribution, and N to also span intervention response.

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

**Answers come as price lists, not single numbers.** With what dominates the count stated. If the honest answer is that the sample must be much larger than anything discussed so far, that is the answer: a large sample that reproduces the range beats a neat one that cannot.

**Variance coverage is not the criterion, and a chosen percentage is not a test.** Also adopted from the seat's challenge: the goal here is distributional, and variance coverage is not a distributional statement. Span-the-support and reproduce-the-distribution are *opposed* criteria — a space-filling draw deliberately over-represents tails — and you get both only if **each drawn case carries the population mass it stands for**. So the sample is weighted, and N is set by a **weighted distributional acceptance test with a stated power**: the sample is statistically indistinguishable from observed at n. That is falsifiable, where a percentage chosen by the director was not.

**But the cases are chosen for difference, and the weights carry the representativeness. That ordering is the point and it is not optional.** (Clarified 2026-09-07 after the director caught the drift; the first draft of this section stated the acceptance test without the half that makes it compatible with §2, and a reader opening here would have taken representativeness as the goal.)

The sample is **not** a random draw sized until it looks like the population. It is a deliberately chosen set of distinct cases spanning the variation in outputs — near-duplicates rejected, tails deliberately included — with each case weighted by the population mass it stands for, such that the *weighted* sample reproduces the observed distribution.

**The practical tell:** if N comes out at the scale a random sample would need, the weighting is doing no work and the design has reverted to representativeness. A weighted, deliberately-chosen sample needs far fewer cases than a random draw to reproduce a distribution — that is the whole reason for choosing rather than drawing. A large N is not automatically wrong, but it is a signal to check which design is actually running.

**What we do not want** is a faithful crowd of near-identical households. Two thousand houses that look like each other reproduce the distribution and teach the company nothing, because there is nothing in them to tell apart.

**The weather cell count is derived, not designed.** Once the sample is a set of (household, cell) cases, the number of cells is whatever the drawn sample lands in. The only reason to want it in advance is sizing a data pull, which is an engineering constraint rather than a modelling one. `W1_21`'s 987 was coverage of the three drivers' own variance on one shared partition — a partition of weather against itself, which knows nothing about fabric. Right shape, wrong subject.

---

## 6. Two director decisions taken on the seat's challenge (2026-09-07)

**Shape is modelled, not validated.** The only household shape artefact available is Elexon Profile Class 1 — one population-average curve on a 1997 reference year — and NEED is annual. SERL has half-hourly with EPC linkage but is accredited-access. So seasonal and half-hourly shape are **published as modelled and explicitly not validated**, said plainly on the page. SERL access is a real-world application with a long lead time and is not pursued; if it ever becomes worth having, that is a separate director decision.

**Measure now on the heat-driven axes, with the electricity gap named.** Annual electricity is largely a people quantity — for the 81% of households on gas it is appliances, lights and EV rather than fabric — and there is no non-heat electrical base in the demand model until `W2_19` lands. Knowing whether the sample is 10³ or 10⁴ before spending on the people joint changes what gets built, and that information is cheap. The full vector is re-measured once `W2_19` exists.

## 7. What this does not decide

The mechanism, the partition method, the measurement design, and the number itself. All the delivery seat's. This says what must be reproduced and at what resolution, not how.

## WORK THIS CREATES (canonical, in-document)
1. Coverage re-measured against the demand vector under a weighted distributional acceptance test, with the dominant term named, and both N figures reported — distribution, and intervention response.
2. The weather partition re-opened as a joint question over a stock with varying fabric.
3. A control refusing any coverage, ceiling or sufficiency claim that does not declare the dimension it reduces over.
4. Per-household half-hourly electricity shape and seasonal gas shape as the demand deliverable.
5. People phase 1 re-cut so the physical layer stands alone, with the commercial layer correlated rather than merged.

— Director canon, 2026-09-07. The point of the world is to contain difference. A model that reproduces the average of a stock it cannot span is a model of nobody.
