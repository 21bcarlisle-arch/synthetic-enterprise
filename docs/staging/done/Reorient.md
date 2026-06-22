# Strategic Reorientation — Complete the Product Range First

## Direction

Phase 27a (second I&C customer) can proceed — but with a clearer
purpose than just adding another customer. Read this before starting.

## The Strategic Context

The company needs to understand every product type in the UK energy
market before the deeper company build begins. I&C is genuinely
different from residential and SME — different pricing, different
hedging, different risk profile, different VAT, different non-commodity
costs. Getting it right now means the company knows how to run a
complete energy business.

## I&C Products — What Makes Them Different

### Pricing
- Bespoke quoted price per customer, not a published tariff
- Volume tolerance: customer can consume ±10-15% of contracted volume
  at the contract rate; excess/deficit settled at spot
- Shape risk: I&C customers have predictable shapes (offices peak
  weekday daytime, warehouses more flat) — the company prices the
  shape, not just the volume
- Flex tranches: large I&C customers may have multiple tranches hedged
  at different times — a portion bought 2 years out, a portion 1 year,
  a portion prompt
- Pass-through vs all-inclusive: some I&C contracts pass non-commodity
  costs through at actual cost; others bundle everything into a unit rate

### Non-commodity costs for I&C
- TNUoS: charged at higher rates for larger sites (Triad risk —
  consumption during the 3 highest demand periods of the winter)
- DUoS: varies by voltage level (HV customers pay less than LV)
- BSUoS: typically passed through separately for large I&C
- MIC (Maximum Import Capacity): fixed daily charge in kVA for sites
  with large peak demand
- CCL: Climate Change Levy applies at full rate unless customer has
  Climate Change Agreement (CCA) exemption

### VAT
- Standard 20% for all I&C
- CCL exemption if renewable-backed supply with Levy Exemption
  Certificate (LEC) — this is a real product the company could offer

### Hedging
- I&C volume is larger — each customer is a meaningful position
- Volume tolerance means the company carries shape risk between
  contracted volume and actual consumption
- Flex tranche structure: model at least 2 tranches (long-dated and
  prompt) for large I&C customers

### Risk profile
- I&C customers are more sophisticated — they know the market, they
  shop around at renewal, they have brokers
- Churn model needs a separate I&C version: broker-driven switching,
  price-sensitive, longer contract terms (2-3 years not 1)
- Credit risk: I&C customers are businesses — credit checking,
  credit limits, deposit requirements for poor-credit sites

## What to build in Phase 27a and beyond

Phase 27a: Add C_IC2 (commercial office, 1 GWh, Birmingham, summer
cooling profile) as proposed. But also:

- Implement volume tolerance for both C_IC1 and C_IC2 — contracted
  volume ±10%, excess/deficit at spot
- Implement Triad risk for I&C — flag the 3 highest demand periods
  each winter, calculate TNUoS Triad exposure
- Implement CCL at correct I&C rate (vs residential exempt)
- Separate I&C churn model — broker-driven, price-sensitive

Then propose Phase 27b: flex tranche hedging for I&C. At least 2
tranches per I&C customer. Show how the hedging strategy differs
from residential.

## The bigger picture

Once I&C products are properly modelled, the company will understand:
- Fixed residential tariffs
- Variable residential tariffs  
- Time-of-use (HH smart meter)
- SME quoted prices
- I&C bespoke pricing with volume tolerance and flex tranches
- Export tariffs (solar — flag for future)

That is the complete UK retail energy product range. At that point
the company build — proper billing, accounting, customer portal,
market interfaces — has a complete product set to work with.

**The SIM's customer simulation should also evolve in parallel:**
Start thinking about the hyper-personalised household model — physical
home characteristics, economic trajectory, life events, energy
behaviour. This populates the world the company will eventually
serve. Design it now, build it when the product range is complete.

## Test for every I&C phase

"Does this make the company's I&C capability more complete and
correct compared to how a real supplier would handle this customer?"

## NTFY on Phase 27a completion

Include:
1. Volume tolerance — how many periods did C_IC1 or C_IC2 exceed
   contracted volume, and what was the spot settlement cost?
2. Triad exposure — which 3 periods were Triad candidates each winter?
3. CCL — total CCL charged to I&C customers across the run
4. I&C vs SME churn rate comparison
