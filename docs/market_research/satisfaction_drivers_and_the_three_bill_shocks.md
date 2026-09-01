# What drives domestic energy satisfaction, and what "bill shock" actually is

*Knowledge pass, delivery seat, 2026-09-01, on the director's instruction: "do the knowledge first —
this is the £150 shape again if we skip it." Every figure below is from a published source, fetched
live this pass, attributed to its own wave with its own sample size. Where the record runs out it
says so.*

**Why this page exists.** `simulation/sim_satisfaction.py` models satisfaction from bill shocks,
income stress, tenure and payment channel, and treats bill shock as one number. Two questions had
to be established from the published record before any of that is rebuilt: what actually moves GB
domestic satisfaction, and what a bill shock actually is.

---

## Part 1 — What drives domestic satisfaction

### The measurements, by wave

Ofgem/Citizens Advice **Energy Consumer Satisfaction Survey**, representative GB domestic bill
payers. Each column is one wave; nothing here is blended across waves.

| | Jan 2025 | Jul–Aug 2025 | Jan 2026 |
|---|---:|---:|---:|
| sample | 3,854 | 3,790 | 3,911 |
| fieldwork | 6–30 Jan 2025 | 16 Jul–13 Aug 2025 | 5 Jan–3 Feb 2026 |
| **Overall satisfaction** | 81% | **82%** (highest since 2018) | 81% |
| Dissatisfaction | 6% | 6% (lowest recorded) | — |
| Bill delivery timing | — | — | **87%** |
| Billing understanding | 82% | — | 82% |
| **Billing accuracy** | **80%** | — | *"in line with Jul–Aug 2025"* |
| Customer service | 74% | 76% | 77% |
| Ease of contact | 75% | **77%** (new high) | — |
| Made a complaint | 6% | 3% | 2% |
| **Satisfaction with how the complaint was handled** | **44%** | — | — |

### The finding is the gap, and it is not subtle

**Everything routine scores 74–87%. The moment something goes wrong and has to be resolved,
satisfaction halves to 44%.** That is not a marginal difference between drivers; it is the whole
spread of the variable sitting in one place.

Routine billing in GB domestic energy is, on the published record, a broadly solved problem —
accuracy 80%, understanding 82%, delivery timing 87%, and all three rising. **Satisfaction is not
driven by the ordinary bill. It is driven by what happens when something goes wrong.**

### What drives the dissatisfaction, in Ofgem's own words

> *"The main contributors to high levels of dissatisfaction were the length of time taken to resolve
> the issue, not being kept up to date with the progress of the complaint and suppliers not
> providing complainants with a clear view of how long the resolution will take."*

All three are **process** variables — duration, communication, and expectation-setting. None is a
price variable. Ofgem's biennial complaint-handling survey (n=3,049 domestic) corroborates the same
shape from a different instrument: **42% of complainants whose case the supplier had CLOSED thought
it remained unresolved**, only about a third were given a named contact, and 77% found it easy to
find contact details — *accessibility was fine; what happened next was not.*

### The dose, from a primary source

**52% of all complainants surveyed had switched or were planning to switch** (Ofgem biennial
complaint-handling survey, n=3,049 domestic). Against a GB annual switching rate in the mid-teens,
that is a departure hazard roughly **three times** the base rate for a household that has had a
badly-handled complaint.

This is a **primary corroboration** of the bound derived on 2026-09-01 in
`WORKER_FINDING_THE_DISSATISFACTION_DOSE_IS_BOUNDED_BY_TWO_PAGES_WE_ALREADY_HOLD_...`, which crossed
Ofgem CIM wave 5 with Wave 20 by Bayes and got ~2.98×. Two disjoint instruments, two methods, ~3×.
**`simulation/satisfaction_churn._LOW_SATISFACTION_MULTIPLIER` is 1.30.**

### What this does NOT establish

No published source gives a **per-unit dose-response** — how much a one-point movement in a
satisfaction score converts to switching probability. What exists is the endpoint (complainants
switch at ~52%) and the population base rate. That bounds the multiplier; it does not shape the
curve between.

### Consequence for the model, stated here and built elsewhere

Our satisfaction score has terms for bill shock, income stress, tenure and payment channel. **It has
no term for "something went wrong and here is how it was handled"** — which the published record
says is where essentially all of the variance lives. The world *does* generate the raw material
(a contact centre, complaint arrivals, resolution) and none of it reaches satisfaction.

---

## Part 2 — What "bill shock" actually is

The director's reading, stated before this research and confirmed by it: bill shock is **three
different things that diverge on responsibility and on remedy**. Two are things a good supplier
avoids; one is a thing a supplier chooses.

### (a) The catch-up after a run of estimates — a supplier's *inference* failure

**Mechanism, in Ofgem's own words:** *"Backbills can result from problems with a supplier's billing
system, or from suppliers estimating bills until they have an actual meter reading which may show
that the customer's consumption is higher than expected. Suppliers then send a 'catch-up' bill to
recover the difference."*

| | |
|---|---|
| **Rule** | **SLC 21BA** — suppliers may not back-bill domestic consumers for energy used more than **12 months** before the bill date, where the consumer is not at fault (in force for domestic from May 2018; exceptions where the consumer has been obstructive or manifestly unreasonable). |
| **Magnitude** | **Median domestic backbill £1,160** (2016/17). |
| **Prevalence** | One of the main reasons domestic consumers contacted Citizens Advice (**>15%** of cases) and the Energy Ombudsman (**12%** of cases) in 2016. |
| **Responsibility** | The supplier's. It estimated wrongly for months. |
| **Remedy** | Actual reads — smart metering, read chasing. Not a price change. |

### (b) The direct debit set too low, then reset — a supplier's *operational* failure

**Mechanism, published:** *"Where a consumer is in a credit position, suppliers are expected to
reduce the Direct Debit level with the intention of returning the account to a zero balance over the
next 12 months. Similarly, where a consumer account is in a debit position, suppliers commonly add
this amount to the Direct Debit and smooth the cost over the next 12 months."* (Ofgem, **Direct
Debit Market Compliance Review**, July 2022.)

That is the director's cause (b) exactly, published: the debit is not forgiven, it is *added to the
monthly payment*, so an under-set DD converts silently into a large increase a year later.

| | |
|---|---|
| **Magnitude** | **Over 7 million SVT consumers** saw a DD increase between February and April 2022, **average increase 62%**. **8% of SVT customers saw an increase of more than 100%.** |
| **Regulatory cut** | Suppliers who increased DDs **by more than 100%** were required to re-review them; **over 900,000 direct debits** fell into that exercise. 12 formal compliance engagements; an Enforcement Order against one supplier. |
| **Ofgem's finding on fault** | *"No evidence was found that any supplier intentionally increased Direct Debit payments above an adequate level. However, weaknesses in some suppliers' processes could result in suppliers setting some direct debits incorrectly."* |
| **Tolerance** | **SLC 27B** — variance beyond **±5%** triggers a DD adjustment. |
| **Responsibility** | The supplier's. Ofgem locates it in *process weakness*, not commercial intent. |
| **Remedy** | Better DD setting and review. Not a price change. |

**This is the one the household is most likely to misread as a price rise**, because it arrives as
"your monthly payment is going up by 62%" with no tariff change behind it.

### (c) The genuine renewal price rise — a supplier's *commercial* choice

The only one of the three where the household is reacting to a decision the supplier made about
price. Its published record is the one this project already holds in depth: the cap, the
fixed-to-SVT spread, and the 2022 spread inversion (`gb_switching_rate_denominators.md`,
`knowledge_price_cap.json`).

| | |
|---|---|
| **Responsibility** | The supplier's, and deliberately so. |
| **Remedy** | Price differently, or accept the departure. |

### Why the distinction is the whole point

**(a) and (b) are operational failures. (c) is a commercial position.** They produce the same
customer experience — "my bill went up a lot" — and they have opposite remedies. A world that emits
one number for all three **cannot tell a badly-run supplier from an expensive one**, which is exactly
the discrimination a per-customer belief exists to make.

And the published magnitudes say the confusion is not academic: **(b)'s average is +62%**, larger
than most genuine renewal increases. A model that conflates them will attribute to *price* what is
in fact *operational failure* — and will therefore price against a problem it should be fixing.

### A fourth axis the published record forces, which was not in the brief

**Direction.** Ofgem's DD review is symmetric: a credit position triggers a *reduction*, a debit
position an *increase*. A catch-up is likewise either an undercharge (the customer owes) or an
overcharge (the customer is refunded). **A bill falling is not a shock**, and any measure taking an
absolute difference has three causes and a sign collapsed into one scalar.

---

## What the published record does NOT settle

1. **The relative frequency of the three causes in a normal year.** The DD figures are from the 2022
   crisis quarter and the back-billing prevalence from 2016; neither is a steady-state mix.
2. **Any per-unit dose-response** from a bill-shock magnitude to a satisfaction movement or a
   switching probability. The endpoints exist; the curve does not.
3. **Whether a household distinguishes (a) from (b) from (c) at all.** Ofgem measures satisfaction
   and complaint category, never "did you understand why your bill rose". The complaint-category
   evidence (billing is 58% of Ombudsman volume, 2024) says households complain about billing far
   more than about price — which is *consistent with* them experiencing (a) and (b) as distinct from
   (c), but does not establish it.

**What would settle (3):** a survey crossing reason-for-bill-increase with satisfaction at the
individual level. Ofgem's Consumer Impacts Monitor asks reasons for *switching* and the Satisfaction
Survey asks satisfaction, and no published instrument crosses them on this question.

---

## Sources

- [Ofgem, Energy Consumer Satisfaction Survey: January 2025](https://www.ofgem.gov.uk/research/energy-consumer-satisfaction-survey-january-2025) — n=3,854, fieldwork 6–30 Jan 2025.
- [Ofgem, Energy Consumer Satisfaction Survey: July–August 2025 summary](https://www.ofgem.gov.uk/research/energy-consumer-satisfaction-survey-july-august-2025-summary) — n=3,790, fieldwork 16 Jul–13 Aug 2025.
- [Ofgem, Energy Consumer Satisfaction Survey: January 2026 summary](https://www.ofgem.gov.uk/research/energy-consumer-satisfaction-survey-january-2026-summary) — n=3,911, fieldwork 5 Jan–3 Feb 2026; full findings due Spring 2026.
- [Ofgem, biennial survey on how suppliers handle complaints](https://www.ofgem.gov.uk/press-release/ofgem-publishes-biennial-survey-how-suppliers-handle-complaints) — n=3,049 domestic, 468 micro-business.
- [Ofgem, Direct Debit Market Compliance Review / press release, July 2022](https://www.ofgem.gov.uk/press-release/ofgem-requires-improvements-energy-suppliers-customer-direct-debits) and [Progress Update](https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update).
- [Ofgem, back-billing ban beyond 12 months (SLC 21BA)](https://www.ofgem.gov.uk/press-release/ofgem-bans-suppliers-backbilling-customers-beyond-12-months) and [Energy Ombudsman, What is back billing](https://www.energyombudsman.org/advice-for-consumers/what-is-back-billing).

*Fetched live 2026-09-01. No figure on this page is simulation output. Where a wave does not publish
a metric the cell is blank rather than carried across from another wave.*
