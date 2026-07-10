# B2 Category (4) — Infrastructure at Commercial Rates: cost anchors

Research for `B2_OPEX_TAXONOMY_EXPANSION.md` category (4). None of these
five cost lines have a single clean public "£X/year for a UK energy
supplier" figure — each is either quote-only (enterprise B2B sales
model), or published but not extractable via automated fetch, or has a
real number for a *different* unit (e.g. per-transaction) that must be
scaled. Labelled per line: REAL (sourced), ESTIMATE (reasoned, not
sourced), or COULD NOT SOURCE.

## 1. Supplier-grade cloud hosting (multi-AZ, DR, SLA-backed)

**ESTIMATE.** No published "energy supplier cloud cost" figure exists.
General DRaaS/multi-AZ cost data: small-business disaster-recovery-as-a-
service typically runs **$6,000–$18,000/year** (~£4,700–£14,200/year) for
DR alone ([AWS DR pricing](https://aws.amazon.com/disaster-recovery/pricing/),
[n2ws DR strategies 2025](https://n2ws.com/blog/aws-disaster-recovery/aws-disaster-recovery)).
That figure covers DR/backup only, not the full compute+storage+billing-
platform+customer-portal estate a live supplier needs. Reasoned estimate
for the full IT estate (compute, storage, DR, monitoring, billing
platform hosting) at small-supplier scale: **£40,000–£120,000/year**,
built up from: base compute+storage (~£15-40k), multi-AZ/DR uplift
(~£5-15k per above), third-party billing/CRM platform hosting fees
(~£15-50k), monitoring/security tooling (~£5-15k). Wide range reflects
real variance by book size and build-vs-buy choices; not sourced to a
single citation.

## 2. Commercial market-data licences (ICIS / Argus / Montel / Platts)

**COULD NOT SOURCE a public figure — confirmed quote-only.** Both
[ICIS](https://www.lseg.com/en/data-analytics/financial-data/commodities-data/energy-data/power-data/icis-data)
and [Argus Media](https://www.argusmedia.com/en/products-platforms/prices)
publish product descriptions but no public price list; both direct
enquiries to sales ("talk to us to learn more about different packages").
This is standard for the sector — commodity price-reporting-agency
subscriptions are negotiated per-client. Reasoned estimate, not sourced:
a single UK power+gas price/forward-curve feed for a small supplier
typically runs in the **£15,000–£40,000/year** range (industry-common
knowledge, not citable); multi-market or multi-user-seat bundles run
higher. Flagged as the least-confident anchor in this set.

## 3. DCC (Data Communications Company) connection/enrolment fee

**REAL, partial.** DCC publishes a Charging Statement each regulatory
year ([RY2025/26 charging statement, PDF](https://www.smartdcc.co.uk/media/221bolkk/charging-statement-ry2526-issue-10-final.pdf),
[DCC charges overview](https://www.smartdcc.co.uk/about-dcc/governance-regulations/charges/)) —
real, current, Ofgem-approved documents, but the PDF's charge tables did
not extract cleanly via automated fetch (dense/scanned formatting) so
exact per-supplier GBP figures could not be pulled programmatically this
pass. One concrete, useful, real finding: SECAS's own guidance states
**the DCC User Entry Process Testing (UEPT) itself carries no direct
cost** ([SECAS User Entry Process guidance](https://smartenergycodecompany.co.uk/documents/sec/user-entry-process-guidance-notes-v4-0-2/)) —
the one-off "enrolment" step is not a material fee line. The real,
material DCC cost to a supplier is the recurring **per-meter-point**
service charge under the Charging Statement, which `saas/opex_ledger.py`
already models via `DCC_COMMS_CHARGE_GBP_PER_YEAR` (£19.01 elec / £14.32
gas per smart-metered account, sourced earlier this project). Recommend:
no new one-off "enrolment" line needed for category (4) — the DCC cost is
already captured correctly in the existing per-account charge. Flag this
divergence to whoever builds category (4): don't double-count.

## 4. UK energy code membership fees (BSC / REC / SEC)

**COULD NOT SOURCE an exact small-supplier figure, but the cost-recovery
mechanism is real and documented.** BSC Section D sets out Elexon's cost-
recovery: BSC Parties pay via tariff-style per-BMU/per-metering-system
charges plus a Funding Share proportional to market share
([BSC Section D](https://bscdocs.elexon.co.uk/bsc/bsc-section-d-bsc-cost-recovery-and-participation-charges),
[Drax: Elexon third-party costs explained](https://energy.drax.com/insights/third-party-costs-explained-elexon/)) —
Elexon states its own costs are under 1% of a typical electricity bill.
REC and SEC are both funded by the industry with membership costs
recovered similarly (RECCo is not-for-profit;
[retailenergycode.co.uk](https://retailenergycode.co.uk/)), but neither
publishes a flat annual small-supplier fee. Reasoned estimate for the
combined BSC+REC+SEC fixed-membership cost for a small supplier (excluding
already-modelled DCC per-meter charges, which SEC governs but doesn't fee
separately): **£10,000–£30,000/year**, dominated by BSC's Funding-Share
component scaling with book size. Not sourced to a single citation —
flagged as an estimate.

## 5. Bacs sponsorship / bureau cost for Direct Debit collection

**REAL for the marginal/per-transaction rate; ESTIMATE for the fixed
annual fee.** A small business collecting Direct Debit via a Bacs bureau
(rather than its own direct Bacs membership) typically pays a per-
transaction fee "well under £0.25"
([London & Zurich: Direct Debit for UK Businesses 2026 guide](https://www.londonandzurich.co.uk/guides/guide-direct-debit-uk-businesses/)) —
real, current, but a variable not fixed cost, and already implicitly
covered by the existing per-transaction cost structure if the sim ever
models payment-processing fees. A real, current "Bacs Approved Bureau
Tariff and Fees" schedule exists
([wearepay.uk, Dec 2024](https://www.wearepay.uk/wp-content/uploads/2025/01/BAB-Tariff-DEC-2024-V1.2.pdf))
but returned HTTP 403 on fetch — could not extract the fixed registration/
inspection fee figures it contains. Reasoned estimate for a small
supplier's fixed annual sponsorship/bureau relationship fee (distinct from
per-transaction charges): **£3,000–£10,000/year**. Least material of the
five lines in absolute terms.

## Summary for the build

| Line | Status | Range (£/yr) |
|---|---|---|
| Cloud hosting (commercial-resilience) | ESTIMATE | 40,000–120,000 |
| Market-data licence | COULD NOT SOURCE (quote-only) | 15,000–40,000 (industry-common, uncited) |
| DCC connection/enrolment | REAL — but likely £0 new, already modelled via per-meter charge | 0 (do not double-count) |
| BSC/REC/SEC membership | COULD NOT SOURCE exact fee, mechanism real | 10,000–30,000 |
| Bacs sponsorship/bureau | REAL per-txn rate; ESTIMATE fixed fee | 3,000–10,000 |

None of these should be built into `opex_ledger.py` as a single precise
constant the way the existing DCC per-account charge is — they're
genuinely estimate ranges, not citable point figures. Recommend the build
either takes the range midpoint with an explicit `is_estimate: True` flag
per line (matching the existing honest-gap discipline already in
`opex_ledger.py`), or surfaces the range itself rather than collapsing to
a point estimate.
