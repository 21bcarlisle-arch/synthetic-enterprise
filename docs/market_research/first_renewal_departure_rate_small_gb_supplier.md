# What share of a small GB supplier's fixed-term customers leave at their first renewal?

**Knowledge:** acquisition-and-retention-economics

**Research completed 2026-10-01, delivery seat, Lane 0.** Opened by EP1 pass 20, which needed a prior
for the tenure horizon's hazard while the book has decided no renewal of its own. The code home is
`company/analytics/clv_three_horizon.FIRST_RENEWAL_DEPARTURE_PRIOR`.

## Answer: not established. The constant is `None`, by design.

## The quantity, defined before the search

Take a domestic customer on a one-year fixed tariff with a **small** supplier, acquired by switching.
The quantity is the probability that the customer **leaves that supplier** (an external switch) at or
around the end of the first fixed term. It excludes customers who move house mid-term and customers
who take a new deal with the same supplier. Customers who roll onto that supplier's default tariff
are stayers.

## What the tree already held

- `svt_rates_active_passive_2016_2025.md` §4 gives "fixed at expiry → active switch ~35%". It
  calls this a *structural inference, not directly cited*. It also counts internal re-fixes as
  "switches", so it is not this quantity. `tools/published_route_split.FIXED_ACTIVE_RENEWAL_SHARE`
  already says the same.
- `gb_domestic_switcher_split_cim_2022_2025.md` gives Ofgem CIM waves 1–6, external/internal on
  an all-household base. Its own §3 shows it does not identify the term-end external share (φ),
  and §6.1 names the missing instrument: an internal/external split asked of households **at a
  fixed-term end**.

## What was found this pass

**1. Ofgem, *End of Fixed Term Communications Trial* (report, September 2019)** —
https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf
(fetched and text-extracted 2026-10-01). This is the route-conditioned instrument §6.1 asked for, at
one supplier.

- Design: a two-arm randomised controlled trial with 19,553 analysed customers on two **one-year**
  fixed tariffs at **one large supplier** ("Supplier A"), both ending 2019-02-28. It excluded
  customers who "had already switched to a new tariff" a few days before term end, plus prepayment
  customers and other exclusions (§3.1, §3.4). The outcome was a switch request within **six
  weeks** (§3.7, footnote 27).
- Control arm (Fig. 4.1): **external 6%**, internal 14%, overall 19%. The intervention moved
  internal switching only (23%); external stayed at 6%.
- Mean tenure with Supplier A was **17 years** (§4.7). The supplier was shortlisted *because* its
  roll-over-to-SVT rate was above average (§3.14). Of the external switchers, about three quarters
  went to small or medium suppliers (§4.2).
- The supplier's own 2018 data implied a 16% baseline switching rate (internal and external) in
  the 30 days after tariff end (§3.5).

**Why it is not the prior:** it is a floor for an inert incumbent book. The population had a
17-year tenure, it was selected for high roll-over, and it excluded the customers who had already
acted before term end. The window was six weeks. A small supplier's book is the opposite
selection: every customer arrived by switching, within the last year. The trial's external rate
cannot be transferred to that book in either direction with a known adjustment.

**2. Ofgem, *Understanding Consumers' Energy Tariff Choices* (BMG for Ofgem, fieldwork
March–April 2024, n=3,235)** —
https://www.ofgem.gov.uk/sites/default/files/2025-07/understanding-consumers-energy-tariff-choices-%20research-report-2024.pdf
(fetched 2026-10-01). Over the previous six months: 13% switched tariff with the same supplier,
6% actively switched to a new supplier, and 4% passively changed supplier. Its base is **all
households**, not households at a term end, so it has the same identification problem as CIM.

**3. Supplier annual reports.** A search for disclosed customer churn at challenger suppliers
(Octopus, Ovo, Bulb) found no per-renewal departure figure. Octopus's FY25 report says churn
"was reviewed" and gives no rate.

## What would close it

A per-renewal external departure rate published for a supplier of the company's kind, from its
filed accounts, a regulator RFI aggregate by supplier size, or an industry practitioner's figure.
Ofgem's 2019 RFI on roll-over rates (trial report §3.13) collected exactly this by supplier and did
not publish it. **This is the director's third-side question:** what share of a small supplier's
one-year fixed customers leave at their first term end is trade knowledge.

## How the code carries the gap

`FIRST_RENEWAL_DEPARTURE_PRIOR = None`. EP1's H2 values on the book's own observed renewal
departures (`observed_book_renewals`, from the company's own settled records). It is blank under
`no_book_renewal_decisions` until the book has decided a renewal, and nothing is shrunk toward a
picked number. Once a prior is sourced, `BookRenewalRecord.hazard` returns it for an undecided book.
Shrinking toward it then needs a sourced strength as well.
