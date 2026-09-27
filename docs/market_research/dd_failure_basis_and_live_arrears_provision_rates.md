# DD failure basis (C1) and live-arrears provision rates by age × method (C6)

**Knowledge:** none -- no knowledge page covers supplier debt and collections; the nearest, price-cap, carries the bad-debt ALLOWANCE (Table 2.1 here is context for it) and not the provision rates or DD failure basis this note answers

**2026-09-27. Research only.** Tests two unsourced sim constants: (C1) P(DD bill fails) =
3%/12%/35% by income-stress tier (`simulation`, minted 2026-07-02, origin unknown), and (C6) the
"indicative IFRS 9 provision matrix" in `company_debt_management.md` §7 (0.3–0.5% ... 70–85%, marked
there as having no source). Context already on disk, not repeated here:
`how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`, `company_debt_management.md`.

**Epistemic note on method.** Several primary-source domains (wearepay.uk, ukfinance.org.uk,
Bacs statistic pages, general web search) returned HTTP 403 or JS-only shells to a scripted `curl`.
Where that happened I used the Wayback Machine to fetch the last-known live snapshot of the actual
page (`web.archive.org`, timestamped, same content Pay.UK published) rather than recall the number —
this is noted at each such citation. One source (Octopus Energy Limited's FY2025 statutory accounts,
Companies House) is a scanned TIFF-to-PDF with no text layer and no OCR tool available in this
environment; it is marked UNVERIFIED, not estimated.

## Summary verdict

| # | Question | Verdict |
|---|---|---|
| C1 | Published, energy-specific or economy-wide, per-presentation DD failure rate by income-stress tier | **GAP.** No published source gives a DD failure rate segmented by "income stress" — that segmentation is not a category any published UK source uses. One scheme-wide (all-sectors) Bacs volume exists but its definition could not be confirmed as a failure/return rate at all (see below) — treat as UNVERIFIED, not usable to anchor 3/12/35%. |
| C6 | Live domestic-arrears provision rate by age × payment method × live/final, from a supplier ARA or Ofgem working paper | **PARTIAL, upgraded from the prior "GAP" read.** Centrica plc's FY2025 Annual Report (Note 17) publishes exactly this cross-tab for UK residential customers — age × payment method (DD / pay-on-receipt / final bill) × gross & provision, two years. That is SOURCED for one supplier. No Ofgem or industry-wide equivalent table exists: Ofgem *considered* the bottom-up age×method×live/final approach and rejected it as impractical (Appendix 2, Dec 2024); the DRS working paper's 75% is a single blended average across all methods and both account types, with its worked table (0-3/0-4) explicitly hypothetical, not real disclosed rates. |

---

## C1 — DD failure basis

### (a) Bacs/Pay.UK returned/unpaid DD statistics

Fetched (via Wayback snapshot, `web.archive.org/web/20250620044643/`, of
`wearepay.uk/what-we-do/payment-systems/bacs-payment-system/bacs-payment-system-statistics/`) the
linked **Bacs Annual Processing Statistics 2023** infographic
(`wearepay.uk/wp-content/uploads/2024/03/Bacs_Annual-processing_stats_2023.pdf`). It gives, in
thousands of items for calendar year 2023, across ALL sectors (not energy-specific):

- **TOTAL DIRECT DEBIT VOLUMES: 4,827,292** (thousand items)
- Under a category list headed **"Other payment types"** (alongside "Retail purchases",
  "Card account payments", "Vehicle finance", "Regular savings", "Occupational Pension
  Contributions"): **"Unpaid debits": 114,644** (thousand)

**Definition problem, stated plainly.** "Unpaid debits" sits in Pay.UK's own table as one of a list
of DD **purpose/sector categories** (what the collection is FOR), not in a table of return/failure
codes (ARUDD reason codes 0/A–T). Categories in the same list — "Retail purchases", "Vehicle
finance", "Regular savings" — describe what the money is collecting, which is consistent with
"Unpaid debits" meaning *Direct Debits used by debt-collection businesses to collect on debts already
in default* (a payment-purpose sector), not *Direct Debits that bounced*. I could not fetch a Pay.UK
glossary or methodology document that defines this category (wearepay.uk's glossary/statistics-notes
pages returned 403 to a scripted fetch, and general web search engines returned JS-only result pages
with no extractable text — tried Bing and DuckDuckGo, both blocked script-based scraping). **I am
not able to confirm what "Unpaid debits" counts, and I am not treating 114,644/4,827,292 (≈2.4%) as
a DD failure rate.** It is reported here as a number that exists in the primary source, flagged
UNVERIFIED for this purpose, precisely so nobody downstream mistakes it for a return rate.

No ARUDD-return-rate percentage, energy-specific or economy-wide, was found in any source I could
fetch. The Bacs rulebook itself (which would define presentation vs re-presentation counting) is
members-only, as already noted in `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`.

**Confidence: L** (the volume figures are H-confidence, direct from the primary PDF; the
interpretation as a failure rate is not supported and is explicitly rejected).

### (b) Ofgem debt & arrears indicators split by payment method

Fetched `ofgem.gov.uk/data/debt-and-arrears-indicators` directly (HTTP 200). The page is a
JavaScript-rendered data-visualisation shell (likely Flourish/Tableau embed); the static HTML
contains navigation only, no data table and no linked CSV/XLSX for the payment-method breakdown. I
could not extract the underlying arrears-by-payment-method series from this page with the tools
available (no browser rendering, no discoverable data-export link). **Marked GAP: could not fetch.**

A *different* Ofgem quantity — not an arrears-incidence rate — was found and fetched directly:
**Ofgem, *Consultation – Appendix 2: Debt-related costs*, Dec 2024, Table 2.1 (Cap 13a, Oct–Dec
2024, £ per dual-fuel customer at benchmark consumption)**:

| Payment method | Debt-related cost allowance (excl. AA) | as % of that method's price cap |
|---|---|---|
| Direct Debit | £25 | **1.4%** |
| Standard Credit | £121 | **6.5%** |
| PPM | £10 | **0.6%** |

Numerator = the bad-debt-and-collection-cost allowance embedded in the cap for that payment method;
denominator = the price cap level for that payment method. This is a **cost-recovery allowance**,
not a failure rate or an arrears-incidence rate — it is the closest thing `company_debt_management.md`
§5's "DD ~1% / SC ~6% of bills in bad debt" is actually anchored to, and the anchor is closer to
1.4%/6.5% (ratio ≈4.6×) than a clean 1%/6% (ratio 6×); the "6×" claim in that file is not exactly
reproduced by this table and should be treated as approximate, not exact.

**Confidence: H** for the table itself (read directly from the primary PDF); **not applicable** to
answering "DD failure rate" or "% of DD accounts in arrears" — it answers a different, adjacent
question, and conflating the two is exactly the kind of error this note exists to prevent.

### (c) Verdict on C1

No published figure found is a clean per-presentation or net-of-re-presentation DD failure rate,
energy-specific or general. What exists: (i) an ambiguous, probably-mis-classifiable Bacs
all-sector volume that I am declining to use; (ii) an Ofgem cost-allowance ratio by payment method
that answers "how much bad debt does this payment method generate as a share of its own bill", not
"how often does a DD fail". **The 3%/12%/35%-by-income-stress construct in the sim cannot be anchored
by any published source, and neither can the income-stress segmentation itself** — no UK collections
or payments-industry publication segments DD failure or arrears risk by a labelled "income stress"
tier. What a practitioner would use instead (see below) is a continuous, credit-bureau-informed
propensity score, plus payment history and PSR/vulnerability flags — categorical tiers are a
modelling simplification with no external analogue to calibrate against, and that absence is itself
the finding: **this is a `None`-with-reason case, not a number to invent.**

---

## C6 — provision rate on live domestic arrears by age × payment method

### (1) Energy UK, *Energy debt: Everyone pays*, Feb 2026 — Figure 5

Fetched directly (`energy-uk.org.uk/wp-content/uploads/2026/02/...pdf`, 200, 20pp). Figure 5 (p.6–7)
gives, confirmed against the primary PDF (bars re-checked against the legend order in the source
text, matching the prior note's read):

| Cohort | 2022–23 | 2023–24 | 2024–25 |
|---|---|---|---|
| Recovery rate, debt/arrears **>12 months** old | 31% | 15% | 9% |
| Recovery rate, debt/arrears **<12 months** old | 60% | 56% | 38% |

Aged (>12m) arrears rose from 52% to 65% of total arrears, 2023→2025 (same Fig./p.6 narrative).

**Definition, checked and found wanting.** Footnote 13, the only citation for Fig. 5, reads in full:
**"Energy UK's analysis."** No numerator/denominator is published — it is not stated whether
"recovery rate" is (collections in the year ÷ opening stock of that age-band), (collections ÷ total
flow of debt through that band), or something else, nor whether the sample of "a number of large
suppliers" is weighted or simple-averaged. **Because the ratio's construction is undisclosed, `1 −
recovery rate` cannot be safely read as a provisioning/expected-loss rate** — a stock-based recovery
rate and a flow-based one imply different loss rates from the same headline number. Treat the 31/15/9
vs 60/56/38 figures as directionally real (aged debt collects far worse, and is getting worse) but
not as a calibrated provision rate.

**Confidence: M** (fetched primary source directly, single source, methodology not published by
that source).

### (2) Supplier annual report ECL/ageing disclosure — Centrica plc, Annual Report and Accounts 2025

Fetched directly (`centrica.com/media/ckfb0qxj/annual-report-and-accounts-2025-untagged.pdf`, 200,
FY ended 31 Dec 2025). **Note 17, "Trade and other receivables and contract-related assets", p.175**
gives exactly the table this question asks for, for **UK residential energy customers**, separately
from business customers:

| Segment (payment method) | Age band | 2025 Gross £m | 2025 Provision £m | **Implied rate** | 2024 Gross £m | 2024 Provision £m | **Implied rate** |
|---|---|---|---|---|---|---|---|
| Direct debit | <30d | 358 | 0 | 0% | 303 | 0 | 0% |
| Direct debit | 30–90d | 73 | 1 | 1.4% | 67 | 0 | 0% |
| Direct debit | >90d | 243 | 18 | 7.4% | 227 | 10 | 4.4% |
| Direct debit | **all ages** | 674 | 19 | **2.8%** | 597 | 10 | **1.7%** |
| Payment-on-receipt-of-bill (≈Standard Credit) | <30d | 89 | 4 | 4.5% | 89 | 4 | 4.5% |
| Payment-on-receipt-of-bill | 30–90d | 86 | 13 | 15.1% | 56 | 8 | 14.3% |
| Payment-on-receipt-of-bill | >90d | 1,095 | 551 | 50.3% | 815 | 445 | 54.6% |
| Payment-on-receipt-of-bill | **all ages** | 1,270 | 568 | **44.7%** | 960 | 457 | **47.6%** |
| **Final bills** (closed accounts, footnote iv: "no longer customers ... switched supplier") | <30d | 19 | 6 | 31.6% | 19 | 7 | 36.8% |
| Final bills | 30–90d | 33 | 19 | 57.6% | 22 | 14 | 63.6% |
| Final bills | >90d | 485 | 426 | 87.8% | 347 | 311 | 89.6% |
| Final bills | **all ages** | 537 | 451 | **84.0%** | 388 | 332 | **85.6%** |

Ageing is "days beyond invoice date" (footnote ii). Direct debit and pay-on-receipt are explicitly
**live** accounts; final bills are explicitly **closed** accounts. This is domestic-only — a
separate table on the same page covers business customers (commercial & industrial / medium / small
business) and is not reproduced here as it is out of scope for this question. Total UK residential
billed receivables were £1,443m net (2025) / £1,146m net (2024), 42%/41% average provision coverage.

**This corrects a standing assumption.** Prior notes on this project (and the seat's own working
memory) held that Centrica's ECL disclosure "blends domestic+business and live+final." **That is not
true of the FY2025 Annual Report**: Note 17 explicitly splits residential from business, and within
residential explicitly splits by the three payment-method/live-final categories above. This should
be corrected wherever that assumption is repeated.

**Comparison against the unsourced matrix in `company_debt_management.md` §7.** The matrix claims DD
provisioning of 15–25% at 91–180 days and 70–85% at >365 days. Centrica's actual blended >90-day DD
rate is **7.4% (2025) / 4.4% (2024)** — DD debt of ANY age past 90 days, not broken down further.
This does not necessarily contradict the matrix's >365-day tail (a low blended average over 90d+ is
consistent with a curve that starts low and only reaches 70–85% at multi-year ages, if most >90d DD
balances are young within that bucket), but it is clear evidence that **the matrix's front end (91–180
days) is too steep for DD**: real blended DD loss at any age beyond 90 days is under 8%, an order of
magnitude below the matrix's 91–180-day band. The matrix should be treated as unsupported, not
merely "indicative" — this finding gives a reason to say so.

**Confidence: H** (read directly from the primary annual report PDF, page and note cited).

### (3) Ofgem — bottom-up age × method × live/final provisioning, and the DRS weighted rate

**Appendix 2 (Dec 2024), §3.14–3.18** (fetched, read directly): Ofgem describes a "bottom-up"
allowance-setting option that would "collect supplier debt levels by debt characteristics (ie age of
debt, payment method and live/final) and estimate the proportion of debt that is unlikely to be
recovered" — i.e. exactly this cross-tab, industry-wide. **Ofgem considered and rejected this
approach** ("difficult to implement in practice... due to the complexity of the modelling required",
§3.15) in favour of a top-down, revenue-allowance benchmark. **No such table was published as a
result — the option was named, not delivered.**

**DRS working paper (Aug 2025), §5.20–5.22** (fetched, read directly): the "notional supplier model"
takes each supplier's own provisioning rate, weights by customer numbers, "further weighting them
according...to payment method (Direct Debit, Standard Credit, Prepayment) and account type (Closed
or Live)", yielding **one blended average provisioning rate of approximately 75%**, for debt accrued
in the DRS "eligible period" **1 April 2022 – 31 March 2024** (crisis-era debt, so not representative
of a normal year). Table 0-3/0-4, which illustrate the weighting mechanism with example numbers
(Supplier A 60%, Supplier B 80%), are **explicitly a hypothetical worked example** ("Consider two
suppliers...", §5.21) — not real disclosed supplier rates. **No disaggregated table by age × method ×
live/final is published in this document either; the 75% is the only real number, and it is a single
blend across everything.**

**Confidence: H** that these documents do not contain the disaggregated table (a well-evidenced
absence); **H** for the 75% figure and its period definition.

### Octopus Energy Limited — attempted, could not read

Pulled the most recent filed statutory accounts (Octopus Energy Limited, company no. 09263424, "Full
accounts made up to 30 April 2025", filed 22 Jan 2026, Companies House). The filed PDF is a
**scanned TIFF-to-PDF image with no text layer** (`pdfinfo`: Creator `go-tiff2pdf`; `pdffonts`: no
fonts). No OCR tool is available in this environment (`tesseract`: not found). **This source is
UNVERIFIED, not estimated** — I did not attempt to recall or infer Octopus's ECL disclosure from
memory. If this matters going forward, an OCR pass on the fetched PDF
(`/tmp/octopus_accounts_fy25.pdf` at fetch time, not retained) or a re-fetch of a non-scanned filing
year would be the next step, done by a session with OCR available.

### Verdict on C6

**PARTIAL, and better than the prior GAP read.** One supplier (Centrica), one reporting entity's
residential book, two consecutive years, three age bands (<30/30–90/>90 days, the last open-ended)
gives a real, well-defined, directly-fetched age × payment-method × live/final provisioning table.
That is enough to say the unsourced matrix in `company_debt_management.md` §7 is **wrong in shape**
at the DD end (too steep too early) and roughly directionally plausible at the final-bill end (84–86%
blended, vs the matrix's 70–85% >365-day final/closed figure — though Centrica's "final bills" bucket
mixes all closed-account ages, so this is not a clean match either). No industry-wide or Ofgem-
endorsed version of this table exists; Ofgem looked for one and gave up, and the only industry-wide
number (DRS 75%) is a single blend with no disaggregation. **Use Centrica's table as the best
available real-world reference point, cited to the supplier and year, not as an industry constant.**

---

## What a practitioner would know that is not written down

- **"Income stress tier" is not an industry category.** Collections teams score customers on
  affordability/propensity-to-pay (often bureau-informed, continuous, not tiered) plus PSR and
  vulnerability flags. A model that buckets households into LOW/MODERATE/HIGH income-stress and
  reads a DD failure probability off that bucket has invented both the category and the number; no
  published source uses this frame, and this note could not find one because it likely does not
  exist in public form (it would be proprietary scorecard IP within a supplier or credit bureau).
- **DD "failure" and DD "return"/"unpaid" are not always the same clock.** A re-presented DD that
  succeeds on the second attempt is not what most published data would count as a "failure" even
  though the first presentation returned unpaid — practitioners track first-attempt bounce
  separately from net-of-re-presentation unpaid, and the industry statistics fetched here do not
  make clear which (if either) they mean, which is itself the finding for (a).
- **"Recovery rate" (Energy UK Fig. 5) almost certainly means collections-in-year over some stock
  measure a practitioner would recognise instantly from the shape of the curve** (a stock-based read
  falling from ~60% to ~38% for <12m debt over three years tracks the well-known post-2022 collections
  slowdown), but the exact stock definition is not published, and asking Energy UK or a supplier
  finance team directly would settle it in one conversation — this is a case for the third leg of
  knowledge (a practitioner), not further published-source search.
- **A live account and a closed ("final bill") account are provisioned on genuinely different curves**
  (Centrica: DD live ~3–7%, final bills ~84–90%), and a model that keys write-off/provision only to
  "did the customer eventually leave" (as `simulation/arrears_engine.py` was found to do in the
  companion note) is reproducing exactly the axis Centrica's own disclosure treats as primary.

---

## Sources

- Pay.UK (wearepay.uk), *Bacs Annual Processing Statistics 2023* — fetched via Wayback Machine
  snapshot 2025-06-20: `http://web.archive.org/web/20250620044643/https://www.wearepay.uk/wp-content/uploads/2024/03/Bacs_Annual-processing_stats_2023.pdf`
  (original: `https://www.wearepay.uk/wp-content/uploads/2024/03/Bacs_Annual-processing_stats_2023.pdf`).
  Retrieved 2026-09-27.
- Ofgem, *Consultation – Appendix 2: Debt-related costs*, Dec 2024 —
  <https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf>
  Table 2.1 (p.7), §3.14–3.18 (p.15–16). Retrieved 2026-09-27.
- Ofgem, *Debt and arrears indicators* (data page, JS-rendered, no static table found) —
  <https://www.ofgem.gov.uk/data/debt-and-arrears-indicators>. Retrieved 2026-09-27, GAP.
- Ofgem, *Debt Relief Scheme (DRS): Policy update working paper*, Aug 2025 —
  <https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf>
  §5.20–5.22 (p.15–16). Retrieved 2026-09-27.
- Energy UK, *Energy debt: Everyone pays*, Feb 2026 —
  <https://www.energy-uk.org.uk/wp-content/uploads/2026/02/Energy-UK_Energy-Debt-Everyone-Pays_February-2026.pdf>
  Figure 5 and footnote 13 (p.6–7). Retrieved 2026-09-27.
- Centrica plc, *Annual Report and Accounts 2025* —
  <https://www.centrica.com/media/ckfb0qxj/annual-report-and-accounts-2025-untagged.pdf>
  Note 17 "Trade and other receivables and contract-related assets", p.174–176. Retrieved 2026-09-27.
- Companies House, Octopus Energy Limited (09263424), full accounts made up to 30 April 2025, filed
  22 Jan 2026 — attempted, scanned image PDF with no text layer, UNVERIFIED (no OCR tool available).
  <https://find-and-update.company-information.service.gov.uk/company/09263424/filing-history>
- Attempted and could not read (403 / JS-only, no data extracted): wearepay.uk statistics/glossary
  pages (live), ukfinance.org.uk, bing.com and duckduckgo.com search result pages,
  gocardless.com guide pages (404 on the specific URLs tried).
