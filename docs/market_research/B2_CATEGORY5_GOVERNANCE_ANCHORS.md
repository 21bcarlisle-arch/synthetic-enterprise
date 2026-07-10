# B2 Category (5) — Fixed Governance & Professional cost anchors

Research for `saas/opex_ledger.py`'s "AI-irreducible floor" — real annual GBP
costs a small/mid UK licensed energy supplier pays regardless of automation
level, reported as its own P&L line (never blended into per-customer
allocation). Golive-conditional flag noted per item.

## 1. Statutory audit fee

**Estimate, partially sourced.** UK audit-fee benchmarks (auditgroup.co.uk,
teamed.global, 2025/26) give: a first/one-off statutory audit for a company
just crossing the audit thresholds (turnover ~£15m-25m) typically £6,000-
£12,000, midpoint ~£8,500. Fee-as-%-of-revenue bands: 0.25% of revenue for
£5m-£10m turnover, 0.19% for £10m-£25m. A company under the audit-exemption
threshold (small company, most private UK Ltds) is not LEGALLY required to
have a statutory audit at all -- but a regulated energy supplier seeking
lender/counterparty/Ofgem confidence typically commissions one voluntarily.
**Anchor used: ~£8,500/yr** (voluntary small-company audit, low end of the
crossing-threshold band, since this book is smaller than the £15m+ band the
range was benchmarked against -- flagged as a judgement call, not a precise
citation).
Source: https://auditgroup.co.uk/statutory-audit-costs/ ,
https://www.teamed.global/insights/uk-company-size-thresholds-2026-april-2025-changes
**Golive-conditional: NO** -- a statutory or voluntary audit is a standing
annual cost regardless of go-live status, relevant from year 1 of real
trading.

## 2. Ongoing legal costs (retainer/ad-hoc)

**Estimate, sourced range.** General UK commercial legal retainers start
~£775/month (~£9,300/yr); compliance-specific retainers for regulated
financial-services-adjacent firms range £1,485/quarter (~£5,340/yr,
discounted for annual payment) up to more comprehensive "Gold" retainers.
Energy supply licensing is a comparable regulatory burden to a small
regulated financial-services firm (SLC compliance, price-cap rules, Ofgem
reporting) even though it isn't FCA-regulated.
**Anchor used: ~£12,000/yr** (mid-point between a general commercial
retainer and a compliance-specific retainer -- a licensed energy supplier
needs more than routine contract review but is not FCA-scale).
Source: https://complianceconsultant.org/compliance-retainer-services/ ,
generic UK commercial-retainer benchmarks (no single named source with a
precise number for energy-supplier legal cost specifically -- COULD NOT
SOURCE a supplier-specific figure).
**Golive-conditional: NO** -- legal support (licence conditions, contracts,
data protection) is needed from the point of holding a live licence, but
much of it is also relevant pre-golive (licence application itself needs
legal input) -- treat as standing, not golive-gated.

## 3. Ofgem supplier licence fee

**Real figure, sourced.** Ofgem's "Licence Fee Cost Recovery Principles"
(May 2024 edition) sets a **minimum annual licence fee of £500**, applying
when the formula-calculated amount (a "relevant proportion" of Ofgem's
costs attributable to that licensee, adjusted by market share/activity)
would otherwise come out lower. For a supplier at this book's scale, the
minimum is the realistic anchor; a larger supplier pays materially more via
the market-share-weighted formula.
**Anchor used: £500/yr** (the published minimum).
Source: https://www.ofgem.gov.uk/sites/default/files/2024-05/Licence%20fee%20cost%20recovery%20principles%20May%202024.pdf ,
https://www.ofgem.gov.uk/decision/licence-fee-cost-recovery-principles
**Golive-conditional: YES** -- this fee is only payable once actually
holding a live Ofgem supply licence; not applicable to a pure backtest/
simulation with no real licence.

## 4. Insurance: PI, Cyber, D&O

**Real figures, sourced ranges (three separate policies).**
- **Professional Indemnity:** low end from ~£80-£300/yr for a small
  consultancy-scale £1m-limit policy (Simply Business benchmark data,
  Oct 2025-Mar 2026 cohort: 10% of customers paid £79.41 or less). A
  regulated energy supplier's real exposure is larger than a solo
  consultant's -- **anchor used: ~£1,500/yr**, an estimate above the
  cited consultancy floor to reflect real supplier-scale exposure, not a
  direct citation.
- **Cyber:** real range £350-£5,000/yr, "typically £1,000-£3,000/yr" for
  UK SMEs. **Anchor used: £2,000/yr** (mid-range, appropriate for a
  business holding customer payment/meter data).
  Source: https://getindemnity.co.uk/business-insurance/cyber/how-much-does-cyber-insurance-cost
- **D&O:** real range £250-£2,000/yr depending on size; small-low-risk
  firms £250-£500/yr, medium firms £500-£2,000/yr; UK-specific policies
  "start from around £250-345/yr". **Anchor used: £600/yr** (small-to-
  medium boundary, reflecting a regulated-sector board).
  Source: https://www.insurancerevolution.co.uk/blog/how-much-does-directors-officers-insurance-cost-uk-guide/ ,
  https://getindemnity.co.uk/insights/how-much-does-directors-and-officers-insurance-cost
**Combined insurance anchor used: ~£4,100/yr** (PI + Cyber + D&O).
**Golive-conditional: NO** -- a company with real customers, real payment
handling, and a real board is exposed to these risks from go-live onward;
during a pure backtest/simulation there is no real liability to insure
against, so this line is realistically golive-conditional in PRACTICE even
though the policies themselves aren't Ofgem-licence-gated. Flagging as
**golive-conditional: YES** on that basis (no real insurable exposure
pre-golive).

## 5. Company secretarial (cosec)

**Real figures, sourced range.** Basic UK cosec packages (confirmation
statement filing, statutory register maintenance, registered office) run
£100-£250/yr; more comprehensive packages covering all statutory compliance
run £400-£800/yr. Individual provider quotes seen: £129.95/yr, £180/yr,
£300+VAT/yr (up to 5 directors/shareholders), £419+VAT/yr (up to 10).
A licensed energy supplier's real governance load (regulatory filings,
board minutes, licence-condition record-keeping) sits above the basic
package tier.
**Anchor used: ~£600/yr** (comprehensive-package end of the sourced range).
Source: https://www.companyservicesuk.co.uk/secretarial-services/full-company-secretarial-support/ ,
https://www.london-registrars.co.uk/product/company-secretarial-services-for-private-limited-companies/
**Golive-conditional: NO** -- a live Ltd company has cosec obligations
(Companies House filings) from incorporation, independent of energy-supply
go-live.

## Summary table

| Line | Anchor (GBP/yr) | Sourced or Estimate | Golive-conditional |
|---|---|---|---|
| Statutory audit | ~8,500 | Estimate (sourced range, judgement on band) | No |
| Legal retainer | ~12,000 | Estimate (sourced range, no supplier-specific figure) | No |
| Ofgem licence fee | 500 | **Real, sourced** (published minimum) | **Yes** |
| Insurance (PI+Cyber+D&O) | ~4,100 | Estimate (sourced ranges per policy) | **Yes** (no real exposure pre-golive) |
| Company secretarial | ~600 | Estimate (sourced range, judgement on tier) | No |
| **Total** | **~£25,700/yr** | | |

None of these five could be found as a single precise, energy-supplier-
specific published figure -- all are judgement calls anchored to real,
cited UK SME/regulated-sector benchmark ranges, not invented numbers. The
Ofgem licence fee is the one genuinely precise, directly-sourced figure
(published minimum, not a range).
