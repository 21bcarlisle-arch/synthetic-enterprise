**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_27_how_many_household_cases_cover_demand

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. This is the sample-size row it will publish; the declaration is replaced when the page
lands.

# Thirteen cases cover 99% of demand — and that is only half an answer

**Measured 2026-09-07**, delivery seat. Reproduce with
`python3 tools/demand_case_coverage.py --measure`.

The director, on the published cell counts:

> *"You've answered how many weather cells capture 99% of household-weighted variation in the
> weather drivers — 21, 21 and 5 across three grids. That's a partition of Britain. What I actually
> care about is heat demand variation, which depends on the weather cell and the house together."*

He is right that the published answer was about the wrong quantity. Over **24,662,309** England-and-
Wales households, **143,511** occupied 1 km cells and the **274** distinct house cases NEED resolves:

| coverage of demand variation | weather alone | house alone | product if separable | **joint** |
|---|---:|---:|---:|---:|
| 90% | 5 | 5 | 25 | **5** |
| 95% | 8 | 8 | 64 | **8** |
| 99% | 21 | 13 | **273** | **13** |

**The joint is twenty-one times smaller than the product.** The sample does not multiply.

---

## The reason is not the one either of us expected

He suspected correlation — northern stock differing from southern. It is there and it is **weak**:
the correlation between a region's winter temperature and its stock's demand *at a fixed climate* is
**−0.314**. Colder regions do have higher-demand stock, and that compounds rather than offsets, but
it is not what collapses the product.

**Demand is a scalar.** Two different combinations of house and weather that produce the same annual
demand are the same case for the purpose of predicting demand. The composition happens in the
*output*, so the input grids never multiply — and this is shown on a synthetic grid whose two inputs
are independent *by construction*, so it cannot be an artefact of the real data's correlation.

## Which means thirteen is close to a fact about scalars, not about Britain

Any single one-dimensional variable needs roughly thirteen to twenty optimally placed bins for 99%
of its variance, whatever drives it. So the count only becomes informative as the output space
grows:

| output space | cases for 99% |
|---|---:|
| demand level | **13** |
| level **and** weather sensitivity (kWh per degree-day) | **21** |

That is the same shape as `W2_22`'s finding, where adding inter-year volatility took N from 100 to
over 250. **The number of cases you need is a statement about how many things you want to be right
about, not about how varied Britain is.**

## And a lever needs the inputs, not the output

Knowing a household sits in demand bin 9 is enough to forecast it and useless for deciding what to
offer. Insulation acts on the **house**; a tariff acts on the **weather exposure**; a heat pump acts
on both. For anything that acts on a cause rather than describing an effect, **the product is back**
— you need to know which of the 274 house cases and which of the 21 cells, because that is what
determines whether the lever does anything.

So the honest answer to "how large must the sample be" is two numbers, not one:

- **To reproduce the distribution of demand: 13 cases, or 21 if weather sensitivity matters too.**
- **To score an intervention: the input resolution, which is 21 cells × the house detail the lever
  acts on.**

## The stock varies by region, and not mainly with temperature

At one fixed climate the regional stock spans **6,405 to 9,503 kWh — 48%** — so where a household is
does predict what it lives in. But the alignment with climate is weak and partly backwards:

| region | winter mean | stock demand at one fixed climate |
|---|---:|---:|
| London | 5.76 °C | **6,405 kWh** |
| North East | 4.54 | 7,455 |
| West Midlands | 4.90 | 7,424 |
| East of England | 5.74 | 8,175 |
| **Wales** | 5.37 | **9,503** |

London is the warmest region and has the lowest-demand stock — small flats. Wales is mild and has
the highest — old, large, rural. The colder-north-worse-stock effect is real and is not what
dominates.

## How demand is computed, and why the calibration does not matter

A closed form: heat-loss coefficient (with the SAP wind factor) × degree-days, less solar gain and
internal gains. Validated against the full 2R2C simulation over 72 (house × weather) pairs at
**r² = 0.9978** with a **3.7%** residual, fitting `full = 0.899 × proxy + 661`.

**The coverage answer is invariant to that calibration.** Coverage is a ratio of weighted sums of
squares about the mean, so an affine transform of the demand scale cancels exactly — the slope and
the offset drop out and only the residual matters. That is asserted as its own control rather than
argued, because it is the kind of claim that is true of the formula one meant and false of the one
one wrote.

## Limits

- **England and Wales only.** NEED is a DESNZ product with no Scottish dwellings, so there is no
  measured stock composition to compose with a Scottish cell. Using the E&W mixture there would be
  an assumption about the coldest 8% of the book — the worst place to make one. 24.7M of 27.3M
  households.
- **Annual level, no shape.** Nothing here says when the demand arrives. `W1_22` established that
  half of cold-day exposure comes in blocks of five days or more and that GB cells barely
  diversify; neither is in this count.
- **274 house cases is NEED's own resolution**, so "house alone: 13" is bounded above by it. A finer
  stock description could only raise the house count, not lower it.
- **The EPC-to-fabric map is a declared Choice with an unmeasured cost.** No published table maps a
  rating to a fabric state — a rating is an outcome of fabric *and* heating *and* controls. What the
  answer does under a different mapping is the obvious next question and is not answered here.
- **The 30% of NEED dwellings with no EPC are imputed, not dropped**, from the (type, age)
  conditional measured on the rated — because dropping them biases the stock toward flats (0.39×)
  and new builds (0.24×), which is exactly how they differ.
