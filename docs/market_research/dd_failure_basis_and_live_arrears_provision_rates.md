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

---

## How DD failure, re-presentation and mandate cancellation reach a supplier, and when (2026-10-11)

*Knowledge pass for the forward-cash-forecast engine (director, 2026-10-11). This section covers the
scheme mechanics: which messages a supplier receives, what each code means, and on which working day
it arrives. Rates are dealt with only where a source gives one. Bacs' own rulebook, its reason-code
appendix (`bacs.co.uk/bdc-sugr/appendix-2-reason-codes/`), the DDIC guide and the indemnity research
findings are all **behind a login**. Anything here that would need them is marked as such.*

**Sources (all retrieved 2026-10-11):**
- **[G]** Bacs glossary, live: <https://www.bacs.co.uk/resources/glossary/>.
- **[F]** Bacs FAQs, live: <https://www.bacs.co.uk/resources/faqs/>.
- **[R]** Bacs *Reason codes* page, Wayback snapshot 2022-08-23:
  <http://web.archive.org/web/20220823085703/https://www.bacs.co.uk/resources/reason-codes/>. The
  live URL now returns 404. Treat this as the last public copy.
- **[A]** Bacs ADDACS service page, Wayback 2023-12-11:
  <https://www.bacs.co.uk/bacs-schemes/direct-debit/services/addacs/>.
- **[AG]** Bacs *AUDDIS service guide* v1.1 (Apr 2021), Wayback 2023-03-09:
  <https://www.bacs.co.uk/media/4tpm0bar/auddis_service_guide.pdf>.
- **[S]** Stripe, *Bacs Direct Debit payments* (vendor docs): <https://docs.stripe.com/payments/bacs-debit>.
- **[GC]** GoCardless guides (vendor): `/guides/posts/arudd-messages/`, `/addacs-messages/` and
  `/what-is-an-indemnity-claim/` on gocardless.com.
- **[DDG]** Direct Debit Guarantee: <https://www.directdebit.co.uk/direct-debit-explained/direct-debit-guarantee/>.

### 1. The collection cycle: ESTABLISHED [G]

- **Day 1 (input):** the supplier submits the file. **Day 2 (processing):** Bacs passes it to the
  paying bank. **Day 3 (entry):** the payer is debited and the supplier credited on the same day.
  Days are English bank working days, which exclude weekends and public holidays. A file can be
  "warehoused" up to 30 days before its input day.
- **Advance notice:** the default is **10 working days plus postal time** before the first collection
  or any change to amount, date or frequency [G][F][DDG]. The DDI terms can agree a shorter period.
  The scheme requires advance notice. The ±5% DD-review band is a separate matter
  (`what_a_supplier_holds_to_size_a_direct_debit.md`).
- **First collection on a new AUDDIS mandate:** possible **2 working days after the DDI is lodged**.
  Bacs *recommends* 5, so that lodgement rejections arrive first [AG]. Stripe's timeline for a new
  mandate runs submitted T+0, active and debit submitted T+3, money leaves the payer T+5 [S].
- **The supplier cannot count a collection as cash on Day 3.** Stripe treats a payment as succeeded
  at **T+3 21:00 UTC**, after the return window has passed, and makes funds available at T+4. With an
  existing mandate the money leaves the payer at T+2 [S]. (Stripe counts T+0 as submission, so its
  T+2 is the scheme's Day 3.)

### 2. Unpaid DDs: ARUDD, the 12 codes: ESTABLISHED [R], current list NOT RE-CONFIRMED

ARUDD returns the unpaid item to the supplier's account and produces a report giving the reason for
each item [G]. These are the codes, with Bacs' own instruction to the service user (the supplier):

| Code | Reason | What it means, and Bacs' instruction to the supplier |
|---|---|---|
| **0** | Refer to payer | The payer's bank is "not in a position to pay" (in practice, insufficient funds). Also used for a garnishee order or arrestment, bankruptcy, liquidation or receivership. **May be re-presented up to one month from the original processing day**; Bacs recommends notifying the payer **5 working days** before. The supplier should find out why it was not paid and how likely re-presentation is to work. |
| 1 | Instruction cancelled | Cancelled by the payer or their bank. The supplier must agree another payment method for what is outstanding. |
| 2 | Payer deceased | — |
| 3 | Account transferred | Collection is suspended until a new DDI is in place and advance notice has been given. Under a full current-account switch the DD is redirected centrally. Under the Payment Transfer Service it is not, and the collection returns code 3 [F]. |
| 4 | Advance notice disputed | Do not collect again until the dispute is resolved. |
| 5 | No account (or wrong account type) | Check the DDI details. |
| 6 | No instruction | No DDI is held at the paying bank. Obtain a new one. |
| 7 | Amount differs | The payer says the amount differs from the advance notice. Do not collect again until resolved. |
| 8 | Amount not yet due | Collected before the date in the advance notice, or (AUDDIS only) less than 2 working days after lodgement. |
| 9 | Presentation overdue | More than 3 working days after the advance-notice date, **or a re-presentation more than one month after the original processing day**. Give further advance notice. |
| A | Service user differs | — |
| B | Account closed | A new DDI on a different account is needed. |

GoCardless independently confirms "12 ARUDD reason codes" and that code 0 is "by far, the most
common" [GC]. **The code list is from a 2022 snapshot.** The live page is gone and the appendix that
replaced it is behind a login, so a 2023–26 code change cannot be ruled out. **NOT ESTABLISHED:**
the share of returns carrying each code.

**When the supplier learns of a failure: DERIVED.** GoCardless says ARUDD is triggered "the day after
the payment was due to be collected" [GC]. Stripe confirms success or failure 4 business days after
submission and declares success at T+3 [S]. Together these put the routine return on the **working
day after Day 3, about 3–4 working days after submission**. Stripe adds that a bank can report a
failure *after* a payment has been marked successful. It then arrives as a dispute (an indemnity
claim) [S]. **A late failure is therefore possible, and it comes through a different channel.**

### 3. Re-presentation: rule ESTABLISHED, how many times DERIVED, cure share NOT ESTABLISHED

- **Rule [R]:** the only code a supplier may re-present on is **code 0**. The deadline is **one month
  from the original processing day**, and a later attempt can be returned under code 9. Bacs
  recommends (it does not require) **5 working days' notice** to the payer.
- **How many times: DERIVED, not seen in the rules.** The public Bacs text sets a time limit, not a
  count. "Up to twice within 30 days" comes from vendor practice: Stripe "can automatically retry ...
  up to 2 times, no more than 30 days after the original payment attempt" [S]. The scheme summaries
  already on disk say the same (`gb_payment_method_migration_rates.md`). British Gas retries after
  14 days and then cancels the DD (`debt_and_collections.md` P1). The count may sit in the
  members-only rulebook. Treat "two" as industry practice.
- **Cure share: NOT ESTABLISHED.** The only figures are vendor figures, already filed in
  `gb_domestic_bill_payment_failure_and_arrears_prevalence.md` §2: up to 70% (a ceiling), 22%
  (Jellyfish, SME energy), and +7% over a plain retry. No published share exists for a plain Bacs
  re-presentation on domestic energy.

### 4. Mandate lodgement and cancellation: AUDDIS and ADDACS: ESTABLISHED for timing, PARTIAL for codes

- **AUDDIS** sends a new DDI electronically to the payer's bank. A rejected one comes back on the
  *AUDDIS Bank Rejected Direct Debit Instruction Report* [Bacs AUDDIS service page, Wayback 2023-12-11: https://www.bacs.co.uk/bacs-schemes/direct-debit/services/auddis/]. AUDDIS
  is mandatory for new direct submitters. **NOT ESTABLISHED: the AUDDIS rejection code list.** It is
  in the login-only appendix. It is not reproduced here from memory.
- **ADDACS** carries the bank's amendments and cancellations to the supplier. **Timing: available
  from 08:00 on the working day after the paying bank inputs the advice** [AG §3.2]. **The supplier
  must act on it within 3 working days** and is recommended to act immediately [A][G][F].
- **ADDACS codes**, as listed by GoCardless [GC]. Bacs itself confirms only code 3 [G]:
  - **Cancellations:** 0 "instruction cancelled – refer to payer", 1 "instruction cancelled by
    payer", 2 "payer deceased", B "account closed", D "advance notice disputed".
  - **Amendments:** 3 and C "account transferred to a new bank or building society", E "instruction
    amended".
  - Other codes may exist (for example a reinstatement code). **That is NOT ESTABLISHED and is left
    unlisted.**
- **A cancellation can overtake a collection already in flight.** That collection then returns
  ARUDD 1. The supplier can therefore receive two messages for one act by the customer.

### 4a. ADDACS reason 1, and the payer-cancelled share against failed collections (2026-10-25, W2_41)

- **What reason 1 is: ESTABLISHED.** ADDACS 1 is "instruction cancelled by payer". The payer asks
  their own bank to cancel. The bank inputs the advice, and the supplier can read it from 08:00 on
  the **next working day** [AG §3.2; GC]. ADDACS 0 ("cancelled, refer to payer") is the bank
  cancelling. That is a different act, and it is not drawn as the household's own act.
- **Bacs does not publish a count. Volumes are published by purpose only: ESTABLISHED.** Pay.UK's
  *Bacs Processing Statistics 2025* gives 5,029,499 thousand Direct Debits in total. Of those,
  **"Domestic fuels" is 304,227 thousand** (6.0%). A line called "Unpaid debits" sits among the
  payment purposes, at 134,931 thousand (2024: 125,258 thousand of 4,939,796 thousand)
  [https://www.wearepay.uk/wp-content/uploads/2026/03/Bacs_Annual-processing_stats_2025.pdf].
  The report has no ADDACS, AUDDIS or ARUDD counts and no reason-code split. It does not split
  "Unpaid debits" by sector, and it does not define it. **This page does not read that line as a
  failure rate:** it is listed as a payment purpose, and what it counts is NOT ESTABLISHED.
- **GAP: how often households cancel.** No published source gives the annual share of domestic
  energy mandates cancelled by the payer, by any party.
- **GAP: the payer-cancelled share against failed collections.** You would need ADDACS 1 counts
  over ARUDD counts for the same population. Neither count is published by sector, so the ratio
  cannot be formed. Do not form it from the two Pay.UK totals above. They count different things
  (all-sector DD items and a purpose line), and that ratio is not a quantity.
- **What the world does with this.** `simulation/bacs_rails.py` draws a payer cancellation as its
  own event. It reaches the supplier as an ADDACS 1 record dated the next working day, before any
  collection is presented against the cancelled mandate. The rate is
  `PAYER_CANCELLATION_PROBABILITY = None`, with this GAP as its reason. The draw refuses unless the
  caller supplies a probability from its own sourced or registered model (today, DD4b's toggled
  cancel share).

### 5. Indemnity claims (DDIC / DDICA) under the Direct Debit Guarantee

- **What they are: ESTABLISHED.** The Guarantee entitles the payer to "a full and immediate refund"
  from their bank when an error is made [DDG]. The paying bank then claims the money back from the
  supplier as an indemnity claim [G]. The supplier receives it on a DDICA report, and a DDIC
  challenge process exists [G].
- **Time limits: vendor-sourced.** There is no time limit for the payer: "Bacs has an indefinite
  indemnity period" [S]. GoCardless says the supplier has **9 days to challenge** and the claim is
  usually collected within 14 days [GC]. Stripe says its claims cannot be contested [S]. That is
  Stripe's own policy, not the scheme's.
- **Grounds [GC]:** the amount or date differs from the advance notice, no advance notice was
  received, a dispute, wrong account, or collection more than 3 working days late. These mirror
  ARUDD 4/7/8/9.
- **How often: NOT ESTABLISHED.** Bacs' "Indemnity claims research findings" is behind a login. The
  only public statement is GoCardless's "very uncommon" [GC].
- **For a supplier, a DDIC is not mainly a fraud signal.** Its grounds are almost all the supplier's
  own failures over notice or amount. A sudden DD increase sent with a short or missing notice
  invites one.

### 6. What this means for early warning and for a forward cash forecast

The order in which signals arrive around one collection, counted in working days from the supplier's
submission (S):

| Signal | Arrives | Before or after the money is due | Evidence on how well it predicts default |
|---|---|---|---|
| ADDACS 0/1 (customer cancels the mandate) | the working day after the bank inputs it, **at any time** | **Can be before**: the earliest warning, and it costs the supplier no failed collection | **NOT ESTABLISHED** |
| AUDDIS rejection (new mandate) | before the first collection, if the recommended 5-day gap is kept | before | NOT ESTABLISHED; mostly bad details, not distress (DERIVED from the code meanings) |
| ADDACS 2/3/B/C/E | the working day after input | before or between collections | these are about administration, not credit (DERIVED) |
| ARUDD 0 (insufficient funds) | about S+3 to S+4 | after: the first hard evidence of distress | **NOT ESTABLISHED**; no published P(default given a first-time code 0) |
| ARUDD 1/B | about S+3 to S+4 | after | this is a cancellation found out late (DERIVED) |
| Re-presentation outcome | the re-presentation's own S+3, inside one month | after | NOT ESTABLISHED; cure share is vendor-only (§3) |
| DDIC (indemnity claim) | **at any time, with no time limit** | long after | NOT ESTABLISHED; mostly a notice/amount defect, not credit |
| A missed manual payment, or collapsing consumption | outside Bacs: the supplier's own ledger and meter reads | — | outside this section |

**Design implications:**
1. **Model a collection as a state machine with a clock, not as a Bernoulli trial per bill.** The
   states are: submitted, then Day 3, then either cleared at S+3/S+4 or returned with a code.
   - **Code 0** branches to a re-presentation, at most twice and within one month (industry
     practice).
   - **Codes 1/B/3/5/6** go to "no mandate": stop collecting, and agree a new method or a new DDI.
   - **Codes 4/7/8/9** go to "our own error": resolve it before collecting again.
   - A cleared item can still be reversed later by a DDIC. Expected cash should be booked against
     these dates. The bill date is the wrong clock.
2. **ADDACS 0/1 is the only signal that arrives before a failed collection.** It moves expected
   collections for the next cycle to zero before any return comes in. The engine should consume it
   as the earliest warning.
3. **The reason code tells you where the problem lies, and only code 0 is about credit.** Pooling
   all returns into one "DD failure" rate repeats the bill-shock definition error that `CLAUDE.md`
   names. It mixes distress (0) with administration (3/5/6), with the supplier's own fault (4/7/8/9)
   and with switching away (1/B).
4. **The epistemic wall:** every signal here is something a real supplier receives. The ARUDD/ADDACS
   code and its date may cross the seam. The household's balance and intent may not.

**GAPs to file:**
- the share of returns by code;
- P(default) given a first code 0, and given an ADDACS cancellation;
- the cure share of a plain re-presentation (domestic energy);
- the DDIC rate;
- the AUDDIS rejection codes, the full current ADDACS list, and whether the scheme caps the number
  of re-presentations.

**2026-10-21:** the forward-cash-forecast provision now learns P(paid) after a code 0, after a
second code 0 inside the month, and after a missed manual payment from the company's own book. Where
the book has never resolved one, it carries the GAP as None (`bad_debt_provisioning.md`, "Early
warning in the forward-cash-forecast provision"). ADDACS is not read. The rails can now send an ADDACS 1 record ahead of any return (§4a, `W2_41`).
The run does not route it to the supplier yet.

All of these are behind the Bacs login or held as supplier data. **The fastest route is the
practitioner leg**: a supplier's payments team, or the director.
