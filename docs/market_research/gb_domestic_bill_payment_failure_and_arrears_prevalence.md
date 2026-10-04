# How often does a GB domestic energy bill payment fail, and how many accounts are in arrears at any time?

**Knowledge:** acquisition-and-retention-economics

**2026-10-04, discovery agent.** Four quantities were asked for, and the single biggest error this
file exists to prevent is treating them as one quantity. Prior files on disk already establish a
great deal and are **not repeated here**, only extended:
`dd_failure_basis_and_live_arrears_provision_rates.md` (C1 — no published DD failure rate exists,
any segmentation; the Centrica age×method provision table), `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`
(a failed DD is re-presented, not written off), `company_debt_management.md` (the debt lifecycle
timeline, PPM repayment terms), `domestic_debt_objection_rates_gb.md` (the 28-day statutory debt-age
threshold and the switching-objection rate, a different mechanism from arrears incidence). This file's
new contribution is **(d)**: the Ofgem debt-and-arrears dashboard, previously logged as "JS-rendered,
no data extractable" (the prior note's verdict, 2026-09-27), turns out to carry its chart narration
— methodology, current-quarter figures and QoQ/YoY deltas — as plain, fetchable static text once
`<script>`/`<style>` blocks are stripped before tag-stripping (the earlier attempt's tooling, not the
page, was the obstacle; the raw chart **series** behind each Highcharts ID is still not reachable —
see "What is not established" below).

## What each quantity IS, before any figure is given

Six genuinely different things get asked for under the word "payment failure" or "arrears", and they
have different numerators, different denominators and different clocks:

1. **A DD return (ARUDD)** — a collection EVENT: a single Direct Debit presentation bounces. Rate =
   returns ÷ presentations, in a given period. Can be first-attempt or net-of-re-presentation
   (Bacs allows up to two re-presentations within 30 days) — these are different numbers and no
   source read this session distinguishes them.
2. **A standard-credit (pay-on-receipt) bill unpaid by its due date / within 28 days** — a collection
   EVENT on a different payment method, with no re-presentation mechanic; "late" has to be defined
   against the bill's own due date, not a fixed clock across all bills.
3. **"In arrears"** (Ofgem's own term, used in its dashboard) — a STOCK: an account with a bill
   unpaid for **more than 91 days (13 weeks)** with **no** repayment arrangement, measured at a
   point in time (end of quarter).
4. **"In debt"** (Ofgem's own term) — a STOCK: an account with a **formal repayment arrangement**
   lasting more than 91 days, measured at the same point in time. Arrears and debt are **mutually
   exclusive** categories in Ofgem's own classification (an account moves from one to the other when
   an arrangement is agreed), so they add rather than overlap.
5. **A bill >28 days unpaid** — a THRESHOLD four times lower than Ofgem's 91-day arrears bar. This is
   the SLC14 statutory debt-age minimum below which a losing supplier may not object to a switch
   (`domestic_debt_objection_rates_gb.md`, row 17) — it is a **legal gate**, not a published
   incidence rate, and no source read this session gives the share of bills, or of accounts, that
   ever cross it. It will necessarily catch many more accounts than the 91-day bar, including
   transient lateness that cures itself before 91 days and never becomes "arrears" at all.
6. **A cumulative lifetime/decade incidence** — "did this account ever miss a bill" or "was this
   household ever >28 days overdue at some point in a 10-year run" — a FLOW quantity, structurally
   different from any of the STOCK quantities 3-4. A low point-in-time stock is consistent with a
   high cumulative incidence if spells are short and many different accounts take turns; it is
   consistent with a low cumulative incidence if the same few accounts sit in arrears for years.
   **No published source converts one into the other without an assumption about spell length and
   re-entry, and this file does not invent that assumption.**

---

## (a) DD return/failure rate, energy-specific or economy-wide, 2016-2025

**Extends, does not repeat,** `dd_failure_basis_and_live_arrears_provision_rates.md` §C1, which
already found Pay.UK's 2023 "Unpaid debits" category ambiguous and declined to use it as a return
rate. This session fetched the **2024 and 2025** editions of the same Pay.UK annual infographic
(both via Wayback — the live `wearepay.uk` domain still 403s a scripted fetch) to see whether the
category is defined any more clearly in later editions, and to add a usable energy-specific
denominator that the prior note did not extract.

| Year | Total Bacs Direct Debit volume (000s) | "Unpaid debits" (000s), same category list as "Retail purchases"/"Vehicle finance" | Share | "Domestic fuels" DD volume (000s) — energy sector specifically |
|---|---|---|---|---|
| 2023 | 4,827,292 | 114,644 | 2.38% | 283,242 |
| 2024 | 4,939,796 | 125,258 | 2.54% | 298,004 |
| 2025 | 5,029,499 | 134,931 | 2.68% | 304,227 |

Source: Pay.UK (wearepay.uk), *Bacs Processing Statistics* 2023/2024/2025 editions, fetched via
Wayback Machine 2026-10-04 (originals 403 to a scripted fetch, as in the prior note):
- 2023: `http://web.archive.org/web/20240417184513/https://www.wearepay.uk/wp-content/uploads/2024/03/Bacs_Annual-processing_stats_2023.pdf`
- 2024: `http://web.archive.org/web/20260609212939/https://www.wearepay.uk/wp-content/uploads/2026/03/Bacs_Annual-processing_stats_2024.pdf`
- 2025: `http://web.archive.org/web/20260609215606/https://www.wearepay.uk/wp-content/uploads/2026/03/Bacs_Annual-processing_stats_2025.pdf`

**What this does and does not establish.** "Unpaid debits" sits in the SAME category list as
"Retail purchases", "Vehicle finance", "Regular savings", "Occupational Pension Contributions" — a
list of **what the Direct Debit is collecting FOR**, not a table of return/failure reason codes. Its
most likely reading, unchanged from the prior note, is Direct Debits used BY debt-collection
businesses to collect on debts already in default (a payment-PURPOSE sector), not "Direct Debits
that bounced." The three years' figures are internally consistent (it rises in step with total DD
volume, 2.38%→2.54%→2.68% — not a flat failure rate one would expect of a return-code share held
against its own base) and do **not** resolve the ambiguity — they corroborate that the category is
real and growing, which is equally consistent with either reading. **No Pay.UK glossary or
methodology page defining this category was fetchable this session** (`wearepay.uk` statistics and
glossary pages continue to 403 a scripted fetch; a `curl` to the bare domain for CDX discovery of a
glossary page returned a Wayback gateway timeout). **Verdict unchanged from the prior note: this is
not usable as a DD failure/return rate, energy-specific or otherwise.**

**"Domestic fuels" is new context, not a failure rate.** It is the total volume of energy-sector
Direct Debit COLLECTIONS (successful and unsuccessful combined) — 283-304 million transactions a
year, rising — and establishes the scale of the activity any failure rate would need to be divided
into. It is not itself informative about failure.

**No ARUDD-return-rate percentage, energy-specific or economy-wide, was found anywhere this
session** — this restates and stands by the prior note's C1 verdict.

---

## (b) Split by income/arrears/vulnerability — reaffirms the existing GAP; no new segmentation found

`dd_failure_basis_and_live_arrears_provision_rates.md` already establishes, at H confidence, that
**no published UK source segments DD failure or arrears risk by a labelled "income stress" tier** —
that category does not exist in the public record; practitioners use continuous, bureau-informed
propensity scores instead. This session attempted one further angle not tried before — the FCA's
*Financial Lives* survey, which does segment UK adults by income/vulnerability and sometimes reports
missed-bill behaviour — and did not surface an energy-specific, income-segmented bill-payment-failure
statistic: `fca.org.uk/financial-lives` and its 2024 survey landing page were fetched directly (200
OK) but the returned pages are navigation/overview pages with no energy or utility-bill keyword
anywhere in the static text; the actual *Financial Lives 2024* key-findings data tables were not
locatable at a guessed URL (`/publications/financial-lives/financial-lives-2024-key-findings` → 404).
**This is a session-time-boxed non-result, not evidence the data does not exist** — FCA's full
*Financial Lives* dataset (a large, downloadable survey with over-indebtedness and vulnerability
cross-tabs) is a plausible next source and was not exhausted. **Status unchanged: GAP, C1 stands as
previously filed.** The sim's 3%/12%/35%-by-income-stress construct remains unanchored by any source
found in this or the prior session.

---

## (c) Standard credit (pay-on-receipt) bills not paid by the due date / within 28 days

**Not established.** No source found this session, or in the prior sessions whose files this one
read, gives "the share of standard-credit/pay-on-receipt bills unpaid by their due date" or "...within
28 days" as a direct figure. Two adjacent, already-sourced quantities exist and must not be
substituted for it:

| Adjacent quantity (already sourced elsewhere) | What it actually counts | Why it is not (c) |
|---|---|---|
| Ofgem price-cap debt-related cost allowance, Standard Credit **6.5%** vs Direct Debit **1.4%** of that method's own cap level (`dd_failure_basis_and_live_arrears_provision_rates.md` §C1(b), Table 2.1, Dec 2024) | A **cost-recovery ratio** built into the regulated price — bad debt + collection cost as a share of the bill level for that payment method, averaged over the whole book and whatever write-off/provision policy suppliers actually run | Answers "how much bad debt does this method generate as a % of its OWN bill", not "how often does a bill miss its due date" |
| Centrica plc Note 17 (FY2025), pay-on-receipt gross receivables by **age of balance**: <30d £89m, 30-90d £86m, >90d £1,095m, out of £1,270m total (`dd_failure_basis_and_live_arrears_provision_rates.md` §C6(2)) | A **balance-age snapshot** of the receivables book at one supplier, one year-end — what fraction of the MONEY currently owed is old, not what fraction of BILLS ISSUED ever go unpaid past their due date | A stock-of-money-by-age table cannot be read as a bill-level incidence rate without knowing bill count and issuance timing, neither published |

**What would close this gap:** either a supplier's own billing-ops disclosure of "% of bills paid
within N days of issue" by payment method (not located in any annual report read this session — ARAs
disclose receivables ageing, not bill-level payment timeliness), or an Ofgem SOR/compliance return
that nobody has published in this form. **Filed as a gap, not estimated.**

---

## (d) Share of domestic accounts in arrears / in debt, by year — THE OFGEM DASHBOARD IS READABLE

### Correcting the prior "could not fetch" verdict

`dd_failure_basis_and_live_arrears_provision_rates.md` §C1(b) recorded `ofgem.gov.uk/data/debt-and-arrears-indicators`
as "a JavaScript-rendered data-visualisation shell... no data table and no linked CSV/XLSX... Marked
GAP: could not fetch." **That verdict is corrected here.** The page's Highcharts widgets ARE
JS-rendered and their raw numeric series genuinely are not in the static HTML (confirmed again this
session — see "What is still not established" below) — but every chart on the page carries a
hand-written **"At-a-glance summary"** and **"Methodology"** paragraph as plain Drupal content, and
that text states the methodology and the current reporting quarter's headline numbers in words. The
prior fetch evidently stopped at the chart canvas and did not read past it; this session's fetch
(`curl -s -L`, `-A "Mozilla/5.0"`, direct to the live URL, 200 OK, retrieved 2026-10-04) got the full
page and the narrative text extracts cleanly once `<script>`/`<style>` blocks are removed before
generic tag-stripping (a naive "strip all tags" regex on the raw HTML silently swallows the
real content too, because the page embeds a second, JSON-escaped copy of itself for client-side
hydration whose quote marks and angle-bracket escapes confuse a non-HTML-aware stripper — this
is noted because it is exactly the kind of "the tooling failed, not the source" error already found
once this week in `domestic_debt_objection_rates_gb.md`'s correction of the "compressed streams"
claim).

### Ofgem's own definitions (quoted)

> "A customer is in arrears if they have not paid a bill for longer than 91 days (13 weeks), and
> there is no formal arrangement to repay the debt. It excludes any charges for subsequent
> consumption."

> "A debt repayment arrangement is an arrangement to repay debts which lasts more than 91 days (13
> weeks)."

So **arrears** and **debt** are Ofgem's own mutually-exclusive labels for the SAME underlying thing
(a bill gone unpaid past 91 days) split by whether a formal repayment plan is now in place. Both are
**stock** measures — a snapshot at the end of the quarter — not a count of bills issued or missed in
that quarter.

### Established figures (two time points fetched this session)

| Quarter | In arrears, no arrangement — electricity | In arrears, no arrangement — gas | In debt (repayment arrangement) — electricity | In debt (repayment arrangement) — gas | Combined (arrears+debt), elec / gas |
|---|---|---|---|---|---|
| Q1 2025 | 1,064,138 (**3.6%**) | 864,918 (**3.6%**) | 840,630 (**2.9%**) | 699,869 (**2.9%**) | **6.5% / 6.5%** |
| Q2 2026 (latest available) | 1,187,788 (**4.0%**) | 954,966 (**3.9%**) | 888,824 (**2.9%**, +4% QoQ to this count) | 726,838 (**2.9%**) | **6.9% / 6.8%** |

Sources (both fetched directly, 200 OK):
- Live page, retrieved 2026-10-04: `https://www.ofgem.gov.uk/data/debt-and-arrears-indicators`
  (Q2 2026 figures; the page's own text: *"In Q2 2026, the number of customers in arrears rose by 5%
  for both electricity and gas, compared to the previous quarter, to 1,187,788 electricity customers
  (4.0% of customers) and 954,966 (3.9% of customers) of gas customers."* and *"increased by 4% for
  electricity accounts (to 888,824), and by 2% for gas accounts (to 726,838)... equates to 2.9% of
  all electricity and 2.9% of all gas domestic customers repaying a debt."*)
- Wayback snapshot, same URL, captured 2025-07-22 (content vintage Q1 2025 — the snapshot's embedded
  JSON-escaped text was decoded with `\uXXXX` and HTML-entity unescaping before tag-stripping — see
  method note above): *"In Q1 2025, the number of customers in arrears rose by 2% for electricity and
  fell by 0.2% for gas, compared to the previous quarter, to 1,064,138 electricity customers (3.6% of
  customers) and 864,918 (3.6% of customers) for gas."* and *"The total numbers increased to 840,630
  for electricity (2.9% of all customers) and to 699,869 for gas (2.9% of all customers)."*
  `http://web.archive.org/web/20250722082905/https://www.ofgem.gov.uk/data/debt-and-arrears-indicators`

**Direction, confirmed from the page's own narrative, not just these two points:** "the number of
domestic customers in arrears has trended upwards since 2024, although there was little change in
2025" and the pre-2023 history: "the number of customer accounts repaying an energy debt decreased
from the beginning of this time series in 2006, when nearly 5% of electricity customers and 4.7% of
gas customers were repaying a debt" (attributed to the shift toward monthly Direct Debit), with "a
sharp rise in accounts in arrears during Q2 2022" — consistent with, and now a primary-source
confirmation of, the already-filed `company_debt_management.md` figure ("Customers in electricity
arrears (Q4 2025): 1.15m, 3.9%").

**Confidence: H** — primary regulator source, direct quotes, methodology stated in the source's own
words, two independent fetches (live + Wayback) agreeing on definitions and showing a consistent
trend.

### What is still NOT established from this source

- **No payment-method split.** The page's text does not break "in arrears" or "in debt" down by
  Direct Debit / Standard Credit / PPM — the ONLY payment-method-specific series on this page is "the
  proportion of customers REPAYING a debt via PPM" (i.e. conditional on already being in the "in
  debt" bucket): 40% electricity / 36% gas in Q2 2026, "typically ranged between around 30% and 40%
  over the last 15 years." **This upgrades the prior note's "could not fetch" to "fetched directly,
  confirmed the breakdown is not published here either"** — a stronger, more useful finding than an
  unfetched page, because it closes the question rather than leaving it open.
- **No raw CSV/time-series export was reached.** The page's own text states "every chart includes...
  a feature to allow you to download chart images and raw data in .csv format" — that download is a
  client-side (JavaScript) action against a Highcharts render, keyed by an opaque per-chart ID (e.g.
  `field_highcharts_id: "gvS7WsWVw"`), and the underlying numeric series is not present in either the
  live HTML or the Wayback snapshot's embedded JSON-API payload (which carries chart METADATA —
  title, description, methodology text, source citation — but not chart DATA). **A full 2012-2026
  quarterly series exists and is downloadable by a human in a browser; it was not reached by this
  session's tooling.** This is the next concrete step if a longer series is wanted.
- **No decade-cumulative figure of any kind exists on this page or anywhere else found this
  session.** Ofgem publishes and defines only the STOCK quantities above. Nothing published converts
  "X% of accounts are in arrears right now" into "Y% of accounts were EVER in arrears across a
  10-year span" — that conversion needs a model of spell length and re-entry that this file declines
  to invent (see "The population check" below for why this matters and what a sanity bound, clearly
  labelled as derived, can and cannot say).

---

## The population check: can these figures validate or refute the simulation's two cited figures?

The task describes two numbers from the simulation (not read from `simulation/` code by this agent —
stated in the task itself, which is the only source for them used here): **about 132 of 176 supply
points (≈75%) miss at least one bill over a decade**, and **~47% of renewal decisions involve a
household with a bill >28 days unpaid**. Both are described as looking "far too high." Here is what
the figures above can and cannot say about that.

**They cannot be compared directly, and saying so plainly matters more than a number.** Both cited
sim figures are **cumulative/flow** quantities (definition 6 above); every Ofgem figure found is a
**stock** quantity (definitions 3-4) at a **91-day** threshold, while the sim's renewal figure uses a
**28-day** threshold (definition 5) — a different, lower bar that no published source quantifies at
all. Comparing a ~7% snapshot against a ~75%-over-a-decade or ~47%-of-renewals figure without
converting between stock and flow, and without reconciling the 28-day/91-day gap, is exactly the
"divide two numbers without saying what each counts" error this project has been burned by before.

**A derived sanity bound, clearly labelled as this file's own arithmetic and not a published
figure (confidence L):**

- If the combined "currently behind" stock (arrears + debt, ≈6.9% electricity / 6.8% gas, Q2 2026)
  is treated as if it were an **independent annual probability** applied identically every year for
  10 years with no persistence (a crude, almost certainly wrong simplifying assumption, used only to
  bound the question): cumulative incidence ≈ 1 − (1 − 0.069)¹⁰ ≈ **51-52%**. That is already well
  below the sim's cited ≈75%, which would require an annual-equivalent rate around **13%** under the
  same crude model (1 − (1 − p)¹⁰ = 0.75 ⟹ p ≈ 0.1294) — roughly **double** the current combined
  stock share.
- That pulls in the OPPOSITE direction from what the independent-trials model needs, once spell
  length is accounted for. If accounts that enter arrears tend to STAY there a long time (which the
  published record says they do: PPM debt repayment plans average **342-365 weeks — 6.6-7
  years** — per Ofgem's own current data, consistent with `company_debt_management.md`'s existing
  figure; and Energy UK's data shows aged (>12-month) arrears rose from 52% to 65% of the arrears
  stock 2023→2025), then the **stock is NOT 10 independent annual draws of fresh accounts** — it is
  dominated by a smaller number of accounts sitting in arrears for years at a time. Under that more
  realistic picture, the ANNUAL rate of accounts newly entering arrears is considerably LOWER than
  the stock/duration ratio would suggest for a short-spell population, and a 10-year cumulative
  incidence built from that lower annual-entry rate would plausibly land BELOW the crude 51-52%
  bound, not above it — pulling further away from, not toward, the sim's ≈75%.
- **Net read, stated as a bound and not a verdict:** nothing in the published record this session
  found supports an annual-equivalent incidence anywhere near the ~13% a 75% decade-cumulative figure
  would need, and the evidence on spell length (multi-year, not single-year) points the other way.
  **This is consistent with the task's own suspicion that 75% looks too high**, but it is a
  sanity bound built on a crude model, not a refutation — the right published quantity to refute or
  confirm it (an annual flow/entry-rate series, or a hazard model fitted to the stock+duration data)
  was not found and was not derivable without guessing a functional form for spell-length.
- **The 28-day/47%-of-renewals figure cannot be bounded this way at all.** No published source
  quantifies ANY incidence rate at the 28-day threshold — not a stock, not a flow, not a
  cross-section. The only thing establishable is that 28 days unpaid is a MUCH lower, more inclusive
  bar than Ofgem's 91-day arrears definition (it will catch routine Direct-Debit timing slippage,
  short postal delays, and genuinely transient lateness that cures before 91 days and never appears
  in any Ofgem arrears/debt count), so a materially higher share crossing it than the ~7% at 91 days
  is EXPECTED on structural grounds — but "higher" is not "47%", and nothing here supports or refutes
  that specific number.

**What would actually settle this** (not attempted here, named as the next step): a flow/hazard
series — the quarterly rate of accounts NEWLY crossing 91 days unpaid, which Ofgem's dashboard does
not publish (only the net stock, after that quarter's cures and new entries have both happened) — or
a practitioner's own account of what share of bills typically run past 28 days before being cured,
which is squarely the kind of thing CLAUDE.md names as "too obvious to anyone in the industry to be
written down anywhere" and a case for asking directly rather than further published-source search.

---

## What is ESTABLISHED vs NOT established — summary

| Question | Status | Confidence |
|---|---|---|
| (a) DD return/failure rate, energy or economy-wide, any year | **NOT established.** Pay.UK's "Unpaid debits" category (2.38-2.68% of DD volume, 2023-2025, rising) remains ambiguous and is declined as a failure-rate reading, now checked across 3 years instead of 1 | L (volumes H, the failure-rate READING explicitly rejected) |
| (b) DD/bill-failure rate segmented by income stress or vulnerability | **NOT established.** No new source found this session; stands as the pre-existing GAP (C1) | Gap |
| (c) Standard-credit bills unpaid by due date / within 28 days | **NOT established.** Two adjacent, already-sourced quantities (cost-allowance ratio; balance-age snapshot) explicitly do not answer this | Gap |
| (d) Share of domestic accounts in arrears (>91d, no arrangement), current | **ESTABLISHED.** 4.0% electricity / 3.9% gas, Q2 2026 | H |
| (d) Share of domestic accounts in debt (>91d, with arrangement), current | **ESTABLISHED.** 2.9% electricity / 2.9% gas, Q2 2026 | H |
| (d) Combined, current, and short trend | **ESTABLISHED for Q1 2025→Q2 2026** (6.5%/6.5% → 6.9%/6.8%, rising); **NOT established before Q1 2025 from this session's own fetch** (page's own narrative corroborates a 2006-2026 qualitative trend without giving the intervening annual figures in text) | H (two points) / M (qualitative trend prose) |
| (d) Split of arrears/debt stock by payment method (DD/SC/PPM) | **NOT established** — confirmed absent from the primary source itself (upgraded from "could not fetch" to "fetched, confirmed absent") | H (absence) |
| (d) Decade-cumulative "ever in arrears" incidence, any population | **NOT established anywhere.** Structurally a different (flow) quantity from every published (stock) figure; not derivable without an unpublished spell-length/hazard assumption | Gap |
| Sim's ≈75% (132/176) decade-cumulative miss-a-bill figure, against the above | **Cannot be confirmed or refuted directly.** A crude independent-trials bound off the current stock implies ≈51-52%, and multi-year spell-length evidence pulls further below that, not above — consistent with, but not proof of, the task's own suspicion that 75% is too high | L (derived, labelled as this file's own arithmetic) |
| Sim's ~47%-of-renewals, bill >28 days unpaid | **Cannot be assessed at all** — no published source quantifies anything at the 28-day threshold | Gap |

---

## Sources

- Pay.UK (wearepay.uk), *Bacs Processing Statistics* 2023, 2024, 2025 — fetched via Wayback Machine
  2026-10-04 (live domain 403s a scripted fetch):
  - `http://web.archive.org/web/20240417184513/https://www.wearepay.uk/wp-content/uploads/2024/03/Bacs_Annual-processing_stats_2023.pdf`
  - `http://web.archive.org/web/20260609212939/https://www.wearepay.uk/wp-content/uploads/2026/03/Bacs_Annual-processing_stats_2024.pdf`
  - `http://web.archive.org/web/20260609215606/https://www.wearepay.uk/wp-content/uploads/2026/03/Bacs_Annual-processing_stats_2025.pdf`
- Ofgem, *Debt and arrears indicators* — <https://www.ofgem.gov.uk/data/debt-and-arrears-indicators>,
  fetched live 2026-10-04 (200 OK); and Wayback snapshot captured 2025-07-22 (content vintage Q1
  2025): `http://web.archive.org/web/20250722082905/https://www.ofgem.gov.uk/data/debt-and-arrears-indicators`
- FCA, *Financial Lives* survey landing pages — <https://www.fca.org.uk/financial-lives>,
  <https://www.fca.org.uk/financial-lives/financial-lives-2024> — fetched live 2026-10-04 (200 OK,
  no energy/utility content found; guessed key-findings URL 404'd, not retried with a second guess).
- Attempted and not usable this session: `ukfinance.org.uk` UK Payment Markets reports (403 live, no
  Wayback capture of the specific report PDF URLs found); `gocardless.com`, `bacs.co.uk`,
  `ddmc.co.uk` guide pages on Direct Debit failure rates (404 on guessed URLs); ONS
  cost-of-living/public-opinion bulletins (502 on direct fetch, not retried via Wayback this
  session); Citizens Advice and StepChange policy/research landing pages (200 OK, no quantitative
  content on this specific question found on the pages fetched).
- Re-read, not re-fetched, as the basis for "do not repeat": `dd_failure_basis_and_live_arrears_provision_rates.md`,
  `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`, `company_debt_management.md`,
  `domestic_debt_objection_rates_gb.md` (all in this directory).

## How the simulation could check its own figures against this

1. **Age every arrears/collections observable in the sim's own book against two bars, not one**: a
   91-day/no-arrangement stock share (comparable to Ofgem's 4.0%/3.9% current figures) and, if the
   sim can compute it, an annual ENTRY rate into that state — the quantity this file could not find
   published and that would actually test the sim's flow dynamics rather than its snapshot.
2. **Do not compare the 28-day renewal-time figure to the 91-day Ofgem figures without a bridge.**
   If a bridge is wanted, the cheapest way to build one honestly is to read the sim's OWN cure rate
   between 28 and 91 days (what share of its own 28-day-late accounts are no longer late by day 91)
   — that is an internally-consistent check of the sim against itself, not against the world, but it
   at least tells whether 47% at 28 days and ~7% at 91 days (the real-world bar) are even in the same
   ballpark of CURE dynamics, which is the structural question the raw percentages cannot answer
   alone.
3. **The decade-cumulative 75% figure is the one place this file recommends asking a practitioner
   (CLAUDE.md's third leg of knowledge) rather than searching further** — Ofgem's own dashboard
   does not publish a flow/hazard series, and guessing a spell-length model to manufacture one would
   be inventing a number to fill a slot, the exact failure mode this research posture exists to
   prevent.
4. **If a longer Ofgem time series is wanted**, the concrete next step is reaching the per-chart raw
   CSV export (`field_highcharts_id` keys named above) rather than the page's narrative text — that
   export exists (the page states it does) and was not reached by this session's tooling.
