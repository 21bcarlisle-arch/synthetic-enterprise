# GB domestic payment-method migration rates, while staying with the same supplier (2016-2025)

**Knowledge:** none -- no knowledge page covers payment method or debt and collections, the same gap `dd_failure_basis_and_live_arrears_provision_rates.md` names; the finding reaches readers through the knowledge-map row *How often a household's payment method changes while it stays (PB8)*

Research pass, 2026-09-30, discovery agent. Question: how often does a household's PAYMENT METHOD
change (DD <-> standard credit <-> prepayment) per year, while it stays with the same supplier?
Checked first against what the repo already holds (`docs/market_research/dd_failure_basis_and_live_
arrears_provision_rates.md`, `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`,
`company_debt_management.md`, `svt_drift_by_payment_behaviour.md`, `ASSUMPTIONS.md`, the
`ADVISOR_SCOPE_BRIEF_PREPAYMENT_ESTATE_2026-08-07.md`), then live Ofgem and DESNZ sources.

**Headline: no published source gives a clean, whole-market, per-year GROSS migration rate for any
of the three routes, with a stated numerator and denominator, for a "normal" (non-crisis) year.**
What exists: (a) a well-sourced mechanism description for DD->non-DD and PPM<->credit (what happens
and under what rule), (b) one real, precisely-worded Ofgem count for route 2 (credit->PPM through
debt), but only for a 13-month crisis-era window and only for forced-install-and-remote-switch
COMBINED, not split, and not repeated for any other year, and (c) a DESNZ NET annual payment-method
SHARE series, which is explicitly not a gross flow. Nothing found overturns the repo's own prior
verdict (`dd_failure_basis_and_live_arrears_provision_rates.md` C1: "GAP") that DD-failure incidence
is not published anywhere for GB domestic energy.

## Summary table

| route | figure | what it counts | source | year | confidence |
|---|---|---|---|---|---|
| 1. DD -> standard credit/cheque | **NOT ESTABLISHED** as a rate. Mechanism only: 2 failed presentations (Bacs: within 30d) -> DD stopped, customer "moved... over to another payment option" | numerator = failed DD bills that end in a payment-method change; no published count of DD accounts moved off DD per year | British Gas help page, *Setting up an energy Direct Debit* (mechanism); Bacs re-presentation rules (Movimo/Access PaySuite, as scheme summaries) | mechanism confirmed 2026-09-27 in-repo, re-checked 2026-09-30 | H (mechanism) / — (rate, none exists) |
| 2a. Credit -> PPM, forced install + remote switch, COMBINED | **"over 150,000" involuntary PPM installations/switches assessed** | numerator = all involuntary PPM installations (warrant) AND remote smart-meter switches to prepay mode, bundled together, across domestic suppliers (excl. British Gas throughout; Utilita and OVO carved out of scope from Nov 2024/May 2025); denominator/window = 1 Jan 2022 - 31 Jan 2023 (13 months) | Ofgem, *Market compliance review: prepayment meter installations*, 3 June 2026, PDF p.3-4 | 2022-01 to 2023-01 (13-month window, crisis-era) | H (primary regulator source, direct read) |
| 2b. Credit -> PPM, same figure, annualised and rated | **~0.58%/year of the non-PPM domestic book**, i.e. roughly 1 in 170 non-PPM domestic accounts, IF the 13-month figure is spread evenly (it should not be assumed to be) | numerator = 150,000/13*12 ~ 138,000/yr (derived, not published); denominator = GB non-PPM domestic electricity+gas accounts, ~23-24m (derived from the repo's own ~28m all-domestic-electricity-accounts figure minus ~4.3-4.5m PPM stock) | derived from the row above + repo-internal denominators (`company/market/market_report.py::_UK_DOMESTIC_ACCOUNTS_M`; PPM stock in `company_debt_management.md`) | 2022-2023 (crisis-era, NOT a normal-year rate) | L (derived ratio, not a published rate; the window is the acute pre-moratorium peak, Feb 2023 pause followed immediately after) |
| 2c. Credit -> PPM, warrant only (5-year total, cited pre-existing in repo) | **94,000 PPM installs under warrant, 2018-2023, across industry (British Gas/Scottish Power/OVO = 70%)** | numerator = warrant-only installs (excludes remote switches); denominator/window = industry-wide, 5 years | `company_debt_management.md` §3 (source line only says "Ofgem PPM review", no URL attached to this specific figure) | 2018-2023 | L — **could not be matched to a specific Ofgem publication this session; UNVERIFIED at the URL level, and inconsistent in scope with row 2a (warrant-only vs combined) and in rate with row 2b (~18,800/yr implied here vs ~138,000/yr implied there for an overlapping period) — the two figures are NOT reconciled and must not both be used as if they measure the same thing** |
| 2d. Wrongful-install rate within the reviewed population | **<2% (1,925 of >150,000) found wrongly installed on re-assessment** | numerator = accounts where PPM should not have been installed on the "safe and reasonably practicable" test; denominator = the same 150,000 reviewed accounts | Same Ofgem MCR, June 2026, p.5 | 2022-01 to 2023-01 | H |
| 3. Prepayment -> credit | **NOT ESTABLISHED** as a rate. Mechanism only: SLC 28.1A requires "alternative arrangements" if PPM stops being "safe and reasonably practicable" (annual reassessment mandated since Nov 2023); Debt Assignment Protocol (since 2012) lets an indebted PPM customer switch SUPPLIER (not necessarily payment method) below a debt threshold | no published count of PPM->credit account-level reversals per year, voluntary or mandated | Ofgem SLC 28 / 28.1A; Ofgem, *New prepayment meter rules extend protections for vulnerable people*, 13 Sept 2023; Ofgem, *Ofgem makes it easier for prepayment meter customers in debt to switch supplier*, 23 Sept 2012 (DAP origin) | mechanism dated 2012/2023; no rate for any year | H (mechanism) / — (rate, none found) |
| Net DD share drift (NOT a migration rate) | Standard electricity DD share: 69% (Sept 2020, implied) -> **72%** (Sept 2025); gas: implied ~69% -> **73%** over the same period — publisher's own words: "a shift to direct debit of 3 percentage points for standard electricity and 4 percentage points for gas" over 5 years | numerator/denominator = DD accounts / all standard (non-Economy-7-only) domestic accounts by fuel, UK/GB, at a point in time, differenced 5 years apart | DESNZ, *Quarterly Energy Prices*, December 2025 release (commentary PDF), "Payment methods" section, p.9 | end-Sept 2020 vs end-Sept 2025 | H for the two share levels and the stated NET drift; **this is explicitly a stock/share comparison, not a gross flow, and DESNZ's own commentary frames it that way ("a shift to... of X percentage points"), not as a switching rate** |
| Prepayment vs standard-credit split of the non-DD remainder | **NOT ESTABLISHED** (pre-existing repo gap, re-confirmed, not closed this session) | DD share is solid (72-75% depending on fuel/quarter); the ~25-28% non-DD remainder's PPM-vs-standard-credit split was not found in the commentary text | DESNZ QEP (as above); `ASSUMPTIONS.md` line 195 (pre-existing) | — | Gap |

## Why a gross rate cannot be assembled from what is published

1. **DD -> non-DD.** Ofgem's own debt-and-arrears-indicators data page is JS-rendered with no
   extractable static table or CSV/XLSX link reachable by a scripted fetch (re-confirmed this
   session, same finding as `dd_failure_basis_and_live_arrears_provision_rates.md` §(b)). Bacs/Pay.UK
   publish a "Unpaid debits" volume that the repo's own prior research already ruled out as a
   failure-rate proxy (it sits in a payment-PURPOSE category list, not a returns-code table; see
   that file's §(a)). No energy-specific or economy-wide per-presentation DD failure/return rate
   was found this session either, confirming rather than closing the existing GAP verdict.

2. **Credit -> PPM.** This is the best-evidenced of the three routes, but the one real count (row 2a)
   is precise about its window (13 months, Jan 2022-Jan 2023) and precise about NOT splitting warrant
   installs from remote switches — Ofgem's June 2026 final MCR report and the November 2022
   regulatory-expectations letter to suppliers both treat "involuntary installation" and "remote
   switch" as one combined category throughout. No year-by-year time series (2016-2025) of this
   count was found; the 13-month figure is the only one Ofgem has published with a denominator
   attached, and it falls squarely inside the acute 2022 energy-crisis period (all suppliers agreed
   to pause both forced installs and remote switches from Feb 2023 to Nov 2023, then a phased,
   audited restart from Jan 2024) — so annualising it (row 2b) would misrepresent a crisis peak as a
   normal-year rate. That derivation is shown for orientation only and is explicitly flagged L
   confidence for that reason.

3. **PPM -> credit.** No published count of reversals — voluntary, supplier-initiated on the
   "safe and reasonably practicable" test, or Ofgem-directed after the 2023 review — was found. The
   MCR report describes suppliers being told to "consider removal and compensation" for wrongly
   installed PPMs (1,925 of the 150,000+ reviewed, row 2d) but does not publish how many were
   actually removed/reversed. The annual reassessment duty (SLC 28.1A, mandatory since Nov 2023) is a
   mechanism that WOULD generate reversals but no supplier or Ofgem publication measuring the
   resulting flow was located.

4. **DESNZ QEP.** The payment-method commentary is exactly what the question anticipated: a **net**
   share series, described by the publisher itself in shift/percentage-point language over a 5-year
   span, not a switching or churn rate. It cannot be used as a proxy for gross migration in either
   direction — a household moving DD->SC and a different household moving SC->DD in the same year
   would net to zero in this series and be invisible.

## Nearest routes to closing each gap

- **DD -> non-DD rate:** the closest published lever is Ofgem's debt-and-arrears-indicators data
  portal, which this session (and the prior C1 research pass) could not extract past its JS shell.
  A session with browser rendering (not a scripted `curl`) is the concrete next step, not a further
  text search.
- **Credit -> PPM, split by mechanism and by year:** ask Ofgem directly (an RFI response or FOI) for
  the weekly compliance-monitoring data referenced in the June 2026 MCR report ("Involuntary PPM
  activity carried out by a supplier was reported to Ofgem on a weekly basis") — that underlying
  series, if released, would give a true year-by-year, warrant-vs-remote-switch-split count. The
  94,000-2018-2023 figure already in `company_debt_management.md` needs its citation re-attached or
  retracted; it was not found by this pass and its scope conflicts with row 2a.
- **PPM -> credit:** a practitioner question as much as a published-source one (per CLAUDE.md's
  "knowledge has three sides" — this is a case where an industry contact, or a supplier's own SLC
  28.1A compliance reporting, is the only plausible source; no public aggregate was found).
- **A true gross switching-between-methods rate, any route:** DESNZ or Ofgem would need to publish
  a FLOW table (accounts moving IN and OUT of each payment method in a period), not a stock/share
  table. No such flow table exists in any source checked this session.

## Sources consulted this session (in addition to in-repo prior work cited above)

- Ofgem, *Market compliance review: prepayment meter installations*, published 3 June 2026 —
  <https://www.ofgem.gov.uk/transparency-document/market-compliance-review-prepayment-meter-installations>
  (PDF: `/sites/default/files/2026-06/Market-Compliance-Review-prepayment-meter-installations.pdf`).
  Retrieved 2026-09-30.
- Ofgem, *Compensation for involuntary installation of prepayment meters, 1 January 2022 to 31
  January 2023*, 3 April 2024 —
  <https://www.ofgem.gov.uk/news/compensation-involuntary-installation-prepayment-meters-1-january-2022-31-january-2023>.
  Retrieved 2026-09-30.
- Ofgem, *Energy regulator outlines next steps on forced Prepayment Meter (PPM) installations*, 21
  February 2023 —
  <https://www.ofgem.gov.uk/press-release/energy-regulator-outlines-next-steps-forced-prepayment-meter-ppm-installations>.
  Retrieved 2026-09-30.
- Ofgem, *New prepayment meter rules extend protections for vulnerable people*, 13 September 2023 —
  <https://www.ofgem.gov.uk/press-release/new-prepayment-meter-rules-extend-protections-vulnerable-people>.
  Retrieved 2026-09-30.
- Ofgem, *Regulatory expectations letter to suppliers regarding concerns over remote switching of
  smart meters to prepayment mode*, 14 November 2022 —
  <https://www.ofgem.gov.uk/publications/regulatory-expectations-letter-suppliers-regarding-concerns-over-remote-switching-smart-meters-prepayment-mode-november-2022>
  (PDF: `/sites/default/files/2022-11/NOV%202022%20SUPPLIER%20LETTER.pdf`, qualitative only, no
  counts). Retrieved 2026-09-30.
- Ofgem, *Ofgem statement on prepayment meters installed under warrant*, 26 May 2015 (background on
  the £500-per-fuel voluntary-switch practice, later formalised) —
  <https://www.ofgem.gov.uk/press-release/ofgem-statement-prepayment-meters-installed-under-warrant>.
  Retrieved 2026-09-30.
- Ofgem, *Ofgem makes it easier for prepayment meter customers in debt to switch supplier*, 23
  September 2012 (origin of the Debt Assignment Protocol) —
  <https://www.ofgem.gov.uk/press-release/ofgem-makes-it-easier-prepayment-meter-customers-debt-switch-supplier>.
  Retrieved 2026-09-30.
- Ofgem, *Extending protections on prepayment meters installed under warrant to 2027*, 21 May 2025 —
  <https://www.ofgem.gov.uk/decision/extending-protections-prepayment-meters-installed-under-warrant-2027>.
  Retrieved 2026-09-30. No count data; extends SLC 28.10-28.13 to 30 June 2027.
- DESNZ, *Quarterly Energy Prices*, December 2025 release, commentary PDF, "Payment methods"
  section, p.9 —
  <https://assets.publishing.service.gov.uk/media/6942cb008f4636fa2c547df5/quarterly-energy-prices-december-2025.pdf>.
  Retrieved 2026-09-30.
- Ofgem, *Debt and arrears indicators* (data page) — <https://www.ofgem.gov.uk/data/debt-and-arrears-indicators>.
  Attempted, JS-rendered shell, no static table extracted (consistent with the prior session's
  finding in `dd_failure_basis_and_live_arrears_provision_rates.md`).
- Search-engine access (DuckDuckGo lite/html, Bing) returned JS-only or empty result shells to
  scripted `curl` throughout this session, same constraint already logged in
  `dd_failure_basis_and_live_arrears_provision_rates.md`'s epistemic note. Ofgem's own sitemap
  (`https://www.ofgem.gov.uk/sitemap.xml`, 10 paginated sub-sitemaps) was used instead to enumerate
  every live Ofgem URL containing "prepay", which is how the sources above were found without a
  working search engine.
