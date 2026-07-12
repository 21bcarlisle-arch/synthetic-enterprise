# Smart Meter Half-Hourly Data Access: Supplier Billing vs. Settlement Consent (2026-07-10)

Commissioned to check an unsourced claim in `tools/generate_customer_consumption.py`'s docstring
("full HH data sharing back to the supplier is an opt-in most domestic customers never take up")
against a director challenge that the real-world default is the *opposite* — most customers are
opted in (or data flows by default) and few opt out. Read-only, external sources only.

---

## Headline finding: the claim conflates two genuinely different real-world mechanisms

The UK smart meter regime distinguishes **(a) data a supplier needs to bill the customer it
already has a contract with**, from **(b) data used for wider electricity-market settlement**,
and only (b) carries a documented opt-in/opt-out consent regime. There is no single "opt-in for
HH data sharing to supplier" rule that covers both — the SIM docstring, read literally, is
imprecise about which of the two it means, and neither reading fully supports "most domestic
customers never take up" as an unqualified claim about supplier access in general.

### (a) Billing/read data — flows to the supplier by default, not opt-in gated

A SMETS2/DCC-enrolled smart meter that is in "smart mode" (not reverted to traditional mode)
routinely sends meter reads to its own supplier for billing without a separate consumer opt-in
mechanism — this is treated as necessary for performance of the supply contract, the same legal
basis a traditional meter read would use. The main real-world "opt-out" that exists here is the
customer declining/losing smart functionality altogether (traditional mode), which DESNZ measures
at **~10% of installed smart meters** (already captured in this repo's ASSUMPTIONS.md,
`SMART_METER_NOT_COMMUNICATING_RATE = 0.10`, DESNZ Q4 2024 Smart Meters Statistics). That existing
anchor is the closest real analogue to "opt in is the default, few opt out" — and it supports the
**director's** framing for this purpose, not the code's.

### (b) Settlement-purpose HH data — a genuine, narrower opt-in/opt-out regime (pre-MHHS)

Separately, and specifically for **market-wide settlement** (reconciling a supplier's book
against actual national demand, historically done via profile classes rather than actual
consumption), Ofgem's own published rule (unchanged 2018–ongoing until MHHS goes live) is:

> "In order to settle customers half-hourly, suppliers need access to their customers'
> half-hourly consumption data from their smart meter. Under the current rules, domestic
> consumers' half-hourly data can only be accessed for settlement if they have given opt-in
> consent, and suppliers can only access half-hourly data from microbusinesses for settlement
> if they have not opted-out."

— Ofgem, *Decision for access to half-hourly electricity data for settlement purposes*, published
25 June 2019 (ofgem.gov.uk/decision/decision-access-half-hourly-electricity-data-settlement-purposes,
fetched 2026-07-10); identical wording appears in the July 2018 consultation and the July 2018
"Consumer views on sharing half-hourly settlement data" research note (same site, fetched
2026-07-10).

This is a real, narrow, genuinely opt-in (domestic) / opt-out (microbusiness) mechanism — but it
governs **settlement**, not the supplier's ability to bill its own customer using smart meter
reads. No authoritative published **uptake rate** (what fraction of domestic customers have
actually given this settlement opt-in) was found this session — Ofgem's March 2018 survey measured
*stated willingness* only ("around two-thirds of consumers are willing to share their data for
settlement purposes"), not actual consent given. This is a genuine research gap, not a confirmed
number either way.

### The ground is shifting under both readings: Market-wide Half-Hourly Settlement (MHHS)

Ofgem/Elexon's MHHS Programme is actively replacing the profile-class settlement system (and with
it, the domestic opt-in requirement above) with **universal, infrastructure-level HH settlement**
for all electricity customers — this is a systemic migration, not a per-customer consent choice.
Per Energy UK's explainer (9 Oct 2024, updated 24 Oct 2024, fetched 2026-07-10): "The Programme
aims for all electricity market trading in the UK, for both domestic and non-domestic customers,
to be based on accurate half-hourly data by October 2026" — migration phase began September 2025
(18-month window), full go-live due by May 2027. Once live, the settlement-specific opt-in ceases
to be the operative mechanism for the vast majority of meters (they are moved over as part of
supplier-led MPAN migration, not by individual customer election).

---

## Confidence-rated findings

**domain**: renewals (metering/data-access adjacent; closest existing SIM module is
`tools/generate_customer_consumption.py`)
**assumption_tested**: "Full HH data sharing back to the supplier is an opt-in most domestic
customers never take up" (SIM docstring, unsourced)
**benchmark_value**: For billing-purpose reads, data flows by default once a smart meter is
DCC-enrolled and in smart mode (~90% of installed smart meters, DESNZ Q4 2024) — this is NOT
opt-in gated. For settlement-purpose HH data specifically, domestic consumers do face a genuine
opt-in requirement (Ofgem decision, 25 Jun 2019) but no published uptake percentage was found.
**confidence**: H for the billing/default-flow claim (DESNZ published statistic, already anchored
elsewhere in this repo); M for the settlement opt-in mechanism's existence (two independent Ofgem
publications, consistent wording); L/gap for any specific opt-in uptake rate (no source found).
**source**: DESNZ Smart Meter Statistics Q4 2024 (existing anchor); Ofgem "Decision for access to
half-hourly electricity data for settlement purposes" (25 Jun 2019); Ofgem "Consumer views on
sharing half-hourly settlement data" (10 Jul 2018); Energy UK "Energy UK Explains: Market-wide
Half Hourly Settlement" (9 Oct 2024, updated 24 Oct 2024) — all fetched 2026-07-10.
**date**: 2026-07-10
**finding**: The SIM docstring's claim is not well-supported as a general statement about
"supplier data sharing" — for the routine billing relationship a supplier already has with its own
customer, data flows by default with no opt-in step, which is what the director's pushback
describes. A genuine opt-in mechanism does exist in UK law, but it is scoped narrowly to
settlement-purpose HH data, not billing, and its real-world uptake rate is unpublished/unknown
(a research gap, not evidence either way). Action: correct the docstring to distinguish billing
(default-on, ~90% smart-mode flow) from settlement-purpose HH consent (opt-in, uptake rate
unknown) rather than treating "HH data sharing to supplier" as one undifferentiated opt-in gate;
also flag that MHHS (2025-2027 migration) is retiring the settlement opt-in mechanism entirely in
favour of universal HH settlement, so any model of this as a stable "most never opt in" fact will
become outdated within the sim's own historical window if the SIM's timeline reaches 2026-2027.
