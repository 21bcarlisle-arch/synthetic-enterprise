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

## (e) 2026-10-08: the four inputs behind the world's arrears being about four times the published level

**The need.** The world ledger shows about 10% of domestic electricity accounts more than 91 days in
arrears with no arrangement at Q4 2019. Ofgem's figure for that quarter is 694,191 accounts, about
**2.45%**, with a further 739,947 (about **2.6%**) repaying on an arrangement (§2.1 of
`debt_and_collections.md`). Four inputs are named GAPs in the code:
- `simulation/arrears_engine._DD_FAILURE_PROB` (C1, 3%/12%/35% by tier);
- `simulation/payment_behaviour_source.REPRESENTATION_SUCCESS_SHARE` (None);
- the rule in the same module that the half not repaid by 22 months is never repaid (its named
  gap 2);
- plan take-up (the world has no arrangements: its named gap 5).

Toggles: `dd_return_rate_first_presentation`, `dd_representation_success_share`,
`q3_debt_repaid_after_22_months_share`, and the existing `q3_plan_take_up_share`, in
`assumption_toggles.yaml`.

Method: no web search was available this pass. Pages were fetched directly. The Pay.UK "Unpaid
debits" line is **not** used, for the reason given in §(a).

### First, the comparator: the world's "no arrangement" is not Ofgem's

Ofgem's "in arrears" excludes accounts on an arrangement. The world has no arrangements, so every
world debtor is in the no-arrangement bucket. The fair comparator for a world without arrangements
is **arrears plus debt**: 2.45% + 2.6% = **about 5.1%** of electricity accounts at Q4 2019
(derived). Against that, the world is about **2x** high, not 4x. Plan take-up cannot close the
rest. It moves accounts between the two buckets; it does not shrink their sum, except by making
repayment faster.

### 1. DD return rate per collection attempt (first presentation): PARTIAL, by value, one supplier

- **No published rate by count.** No supplier report, Ofgem publication, Pay.UK page or survey read
  in this or earlier passes gives returns ÷ presentations for energy.
- **A derived bracket by value, from one supplier.** GoCardless's Octopus Energy case study
  (<https://gocardless.com/stories/octopus-energy>, retrieved 2026-10-08) is undated. It describes
  Octopus after the Bulb migration, so about 2024-25. It says:
  - *"£1 billion payments processed every month in the UK alone"*;
  - *"5.5 million customer accounts and £12 billion of annual payments"*;
  - *"£48M in failed payments recaptured across 12 months"* by Success+ retries.

  What follows from those figures (derived):
  - Recaptured is at most failed, so first-presentation failure by value is **at least £48m ÷
    £12bn = 0.40%**.
  - Failed value = recaptured ÷ the retry recovery share. With that share between 22% and 70% (item
    2), failed value is £69m-£218m. That is **0.57%-1.8% of collections by value**.
- **Caveats.**
  - The figures are by value, not by count. A household in difficulty can owe more than the
    average bill, or less.
  - This is one supplier.
  - The period is crisis-era, so 2016-2019 would plausibly be lower.
  - "Failed" may include cancelled mandates as well as unpaid returns.
  - The vendor is reporting its own product's results.
- **A survey bound, all payment methods.** Source: FCA *Financial Lives*.
  - Base: all UK adults.
  - Question K33: "Which ... domestic bills have you missed, or fallen behind on, in the last 6
    months".
  - Chart: "Types of payments fallen behind on, or missed, in the last 6 months (2020/2022/2024)", p.
    59 of
    <https://www.fca.org.uk/publication/financial-lives/fls-2024-vulnerability-financial-resilience.pdf>,
    retrieved 2026-10-08.
  - The bars were read from the PDF's text positions, in the order 2020, 2022, 2024.

  | Survey wave (fieldwork to) | Electricity | Gas | Any bill or credit commitment |
  |---|---|---|---|
  | 2020 (Feb 2020) | **2.2%** | 1.9% | 10% |
  | 2022 (May 2022) | 3.0% | 2.6% | 10% |
  | 2024 (May 2024) | 3.4% | 2.8% | 10% |

  These are adults, not accounts. A household has about two adults, so the share of households in
  2019-20 is between 2.2% and about 4% (derived). Where it falls depends on whether both adults
  report. The survey counts anyone who fell behind **at all** in six months, a much lower bar than
  Ofgem's 91 days. The world's 10% at 91 days is above even this.
- **Ofgem CIM Wave 5** (Jan-Feb 2024; §10.4 of `debt_and_collections.md`). 7.6% self-report being
  behind on energy bills. Ofgem's arrears plus debt at Q4 2023 was about 6.3%.

**Against the world.** The world's lowest tier fails 3% of DD presentations. The published bracket
is 0.57%-1.8% by value. Only the LOW tier is comparable, and it is already 1.7-5x too high.

### 2. Re-presentation success share: ESTIMATE, vendor figures only

| Figure | Population | Source (retrieved 2026-10-08) |
|---|---|---|
| "Success+ recovers **up to 70%** of failed payments" | All GoCardless merchants, all sectors; machine-timed retry; a ceiling ("up to") | <https://gocardless.com/solutions/recover-failed-payments> |
| "**22%** of failed payments recovered with Success+" | Jellyfish Energy, an SME (business) energy supplier | <https://gocardless.com/stories/jellyfish-energy> |
| "a **7% increase** in recapturing failed payments compared to just retrying" | A charity merchant | same page as the 70% |

- **No domestic-energy figure for a plain Bacs re-presentation was found.** The 7% line suggests a
  timed retry adds little over a plain retry. If so, a plain re-presentation recovers not much less
  than a timed one.
- **The two inputs are tied.** Octopus pins failure × recovery at about 0.40% of value, so a bracket
  run that moves one must move the other. 22% recovery goes with 1.8% failure; 70% goes with 0.57%.

### 3. What happens to unrepaid debt after about 22 months: PARTIAL; the world's "never" is not supported

- **No cohort repayment curve was found beyond Ofgem's 2013-15 objection cohort.**
  - The DRS impact assessment (Nov 2025, §3.10) gives only an average: *"more than 22 months"*.
  - The DRS working paper (Aug 2025) gives no age profile. Its §4.5 says 175,000 of about 195,000
    phase-1 customers are *"already engaged"* (paying something towards their ongoing usage). Its
    own counts do not add up: 175,000 + 50,000 ≠ 195,000.
- **Ofgem social obligations, 2018.** Source: "Debt Repayment 2018", pp. 2-3 of
  <https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/monitoring_social_obligations_-_2018_annual_data_report.pdf>,
  retrieved 2026-10-08. Average weeks to recover a non-PPM debt on an arrangement:

  | Supplier | Weeks |
  |---|---|
  | British Gas | 53 |
  | E.ON | 122 |
  | EDF | 76 |
  | npower | 88 |
  | SSE | 185 |
  | ScottishPower | 54 |

  **Weighted by entries, that is 95 weeks, about 22 months** (derived). It agrees with the DRS
  figure of 22 months.
- **Older debt keeps being repaid.**
  - Energy UK Fig. 5 gives "recovery rates" for debt more than 12 months old: 31% (2022-23), 15%
    (2023-24) and 9% (2024-25). The definition is undisclosed. Read here as a share per year (§C6(1)
    of `dd_failure_basis_and_live_arrears_provision_rates.md`).
  - Centrica provides **7.4%** against live DD balances more than 90 days old, and **50%** against
    pay-on-receipt balances of that age (2025, Note 17).
  - So the expected loss on old **live** arrears is 7%-50%. "Never repaid" implies 100%.
- **The world's rule, against this.** Half of unpaid bills are never repaid, even by a household
  that stays for ten years. The evidence supports continued repayment of roughly 9%-31% a year of
  what is still owed.

### 4. Repayment-plan take-up: no new denominator; one new flow

- **Still not published.** No source gives the number offered against the number accepted.
  `q3_plan_take_up_share` (0.32; 0.20-0.42) stands.
- **New flow, from the same Ofgem 2018 report.**
  - In 2018, **658,363** electricity and **540,246** gas customers entered a debt repayment
    arrangement. Two small suppliers' returns are missing.
  - The Q4 2018 stock on arrangements was 661,339 electricity and 543,540 gas.
  - By Little's law, entries equal to the stock mean an average stay of about **one year**
    (derived).
  - The planned recovery time is about 95 weeks. The gap suggests many arrangements end early,
    either broken or cleared. But the entries include arrangements shorter than 91 days, which the
    stock does not count.
  - **This is not a take-up rate.**

### What closes the gap (derived arithmetic, labelled as such)

Assume the stock is small and bills are drawn independently. Then the world's stock of never-repaid
arrears grows roughly in proportion to **f × (1 − r) × (1 − s)**:
- f is the DD failure rate;
- r is the re-presentation recovery;
- s is the share eventually repaid.

| Lever | World today | Published bracket | Factor on the stock (derived) |
|---|---|---|---|
| Comparator: arrears + debt rather than arrears alone | 2.45% | 5.1% | **about 2x** (the gap is about 2x, not 4x) |
| f, DD failure, LOW tier | 3% | 0.57%-1.8% (by value) | 1.7x-5.3x lower |
| (1 − r), re-presentation | 1 (r = None) | 0.30-0.78 | 1.3x-3.3x lower |
| f × (1 − r), joint (Octopus-tied) | 3% | 0.17% (r 70%, f 0.57%) to 1.40% (r 22%, f 1.8%) | **2.1x-17x lower** |
| s, after 22 months, over a 2016-19 window | 0 | 9%-31% a year | small: by Q4 2019 the debt is at most about 2 years past the 22-month mark |
| Plan take-up | none | 0.20-0.42 | **none on arrears + debt**; it only moves accounts between the two buckets |

Two ways close the remaining 2x:
- the comparator correction plus the low end of the joint DD lever; or
- the joint DD lever alone, at its central values.

**I cannot yet attribute the gap between the tiers.** That needs the world's tier mix, and MODERATE
(12%) and HIGH (35%) have no published counterpart at all.

**Prediction, filed before any run.** Scale every tier's net DD failure by 0.47 ÷ 3. That is the
central Octopus-tied f × (1 − r), 0.87% × 0.54, over the LOW tier's 3%, with the tiers' ratios
kept. The world's Q4 2019 arrears stock then falls by more than half.

### GAPs that are practitioner knowledge

- **DD returns by count, and first versus second presentation, for a domestic book.** Every
  supplier's collections team tracks this monthly; it is not published anywhere found.
- **The success share of a plain Bacs re-presentation**, as against a vendor's machine-timed retry.
- **What a supplier does with a stayer's debt that is two or more years old and has no plan.**
  Whether it keeps chasing, sells or writes off, and how much of it is paid.
- **Offered against accepted on arrangements.** The SOR template collects it; Ofgem publishes only
  stocks.

---

## (f) 2026-10-09: the repaid share of an ordinary failed bill, estimated from Ofgem's stock against its flow

**The need.** `simulation/payment_behaviour_source.LATER_SETTLEMENT_REPAID_SHARE` = 0.5 is the
share of debt-BLOCKED customers who had repaid (Ofgem IA July 2016 §1.39), applied to every failed
domestic bill (its named gap 8, SELECTION). The director (2026-10-09): *"I won't give a figure.
Estimate a range from Ofgem's published debt and arrears data (how arrears flow in compared with the
stock that remains), record it as a toggle with that basis, and show whether the arrears result
changes across the range."* Toggle: `q3_ordinary_failed_bill_repaid_share`.

**What is being estimated.** s = the share of failed domestic bills not collected on
re-presentation that the household eventually pays while still on supply. The world dates a repaid
bill at day 28 + 3 months (70% of them) or day 28 + 22 months (30%); the rest are never repaid and
stay outstanding until the account leaves. So a repaid bill spends on average **d_r = 0.55 years**
past day 91 (26 days or 605 days; computed from the module's own dating), and a never-repaid one
spends **T**, the time until its household leaves supply.

**The Ofgem stock and flow (electricity, 2018, the one year with both published).**

| Quantity | Value | Source |
|---|---|---|
| Stock past 91 days, no arrangement, Q4 2018 | 648,429 | Ofgem, *Debt and arrears indicators*, `debt_and_collections.md` §2.1 |
| Stock on an arrangement, Q4 2018 | 661,339 | same |
| **Pool S, Q4 2018** | **1,309,768** | sum |
| Customers entering a debt repayment arrangement, 2018 (two small suppliers missing) | **658,363** | Ofgem, *Monitoring social obligations: 2018 annual data report*, "Debt Repayment 2018", electricity total; already in §(e) item 4 |
| Pool, Q4 2016 / Q4 2019 | 1,189,544 / 1,434,138 | §2.1 table |

- **Time in the pool.** Little's law, taking entries to arrangements as the inflow: S / I =
  1,309,768 / 658,363 = **1.99 years** (derived). The pool grew 4% in 2018, so near-steady. It
  agrees with the DRS impact assessment's "more than 22 months" to recover (Nov 2025, §3.10) and
  the entry-weighted 95 weeks of §(e).
- **The stock that remains.** The pool grew by a mean of **81,531 accounts a year**, Q4 2016 to Q4
  2019, against 658,363 entries: at least **12.4%** of a year's inflow is still there a year on, if
  inflow was flat. So **s ≤ 0.876** even if a non-payer never left (derived).
- **The share.** With a fraction s staying d_r and 1 − s staying T:
  1.99 = s × 0.55 + (1 − s) × T, so **s = (T − 1.99) / (T − 0.55)**.

**T is the stay of a household that never repays, and Ofgem does not publish it.** It is bounded by
how often a debtor household leaves supply (T = 1/h):

| Exit hazard h | Basis | T (years) | s |
|---|---|---|---|
| 0.046 | social-rent move rate only (EHS 2023-24, `home_moves.md`), no switching | 21.7 | 0.93 → capped at **0.88** by stock growth |
| 0.073 | all-tenure move rate (EHS 2023-24, 1.8m of 24.7m), no switching | 13.7 | 0.89 |
| 0.175 | private-rent move rate (EHS 2023-24) | 5.7 | 0.72 |
| **0.273** | **all-tenure move 0.073 + switching away with debt 0.20** | **3.7** | **0.54** |
| 0.375 | private-rent move 0.175 + switching away with debt 0.20 | 2.7 | **0.32** |

Switching away with debt: Ofgem objections IA (2016) §1.35, "typically 430,000 a year" allowed to
switch with a debt, over the Q4 2016 stock of 2.16m electricity and gas accounts in arrears or debt
= **0.20 a year** (derived; 2013-15 figure, a comparable-data subset of suppliers, and a >28-day
debt population larger than the >91-day stock, so it is order-of-magnitude only).

**Range recorded: low 0.30, central 0.54, high 0.88.** The default stays the shipped **0.5**, which
lies inside it, as the director's instruction asks. Each end has a single basis: the low end is the
most mobile debtor household, the high end is the stock-growth bound.

**What the range does not cover, named.**
- **The 1.99 years is the weakest link.** Entries to arrangements include re-plans after a break,
  which overstates distinct inflow and understates the stay; they miss debtors never put on a plan
  (Ofgem 2015: about 40% of large-supplier debtors had no plan), which does the opposite. At T =
  3.7, a stay of 1.5 years gives s = 0.70 and 2.5 years gives 0.37. Widest defensible, if the stay
  is allowed 1.5-2.5 years as well: **about 0.1 to 0.88**.
- **Whether a written-off stayer leaves Ofgem's count** (a practitioner gap, filed 2026-10-09). If
  it does, T is shorter and s lower.
- The flow is electricity, 2018; the stock series is accounts per fuel, not households.
- The switching hazard is 2013-15. Domestic switching fell to near zero in 2022-23.

**Pre-registration (2026-10-09T17:40Z, written before any of the four runs finished).** Same
instrument as `SEAT_FINDING_THE_DD_FAILURE_CORRECTION_MOVED_MEASURED_FACTS_2026-10-09.md`: 2019
quarter-end electricity accounts with a bill unpaid more than 91 days, 400 founders, default seed,
`report_end` 2019-12-31, fuel split on the account id's `g` suffix, against Ofgem's matched **5.1%**;
MET if 5.1% lies inside the pooled Wilson 95% interval. Predictions: the never-repaid stock scales
with 1 − s. At 0.50 the reading reproduces 8.5% within a point. At 0.30 it is 10-13%, NOT MET,
HIGH. At 0.54 it is 7-9%, NOT MET, HIGH. At 0.88 it is 2.5-5%, and the verdict moves to MET or
NOT MET, LOW. **So the result changes across the range.**

### Result (2026-10-09T19:50Z): it changes. The high end of the range meets the comparator

Same instrument, origin 63f429536 plus this toggle, 400 founders, default seed. The share is set on
the module before the run (`/var/tmp/se-repaid-share-runs/run_at_share.py`, which runs the finding's
`arrears_like_for_like.py`; split by `arrears_slice.py`). Outputs:
`/var/tmp/se-repaid-share-runs/lfl_<share>.json`.

| s | 2019 pooled electricity, >91 days | Wilson 95% | Ratio to 5.1% | Q4 2019 alone | Verdict |
|---|---|---|---|---|---|
| 0.30 (low) | 108/1153 = **9.4%** | 7.8-11.2% | **1.84x** | 29/272 = 10.7% | NOT MET, HIGH |
| 0.50 (shipped) | 98/1153 = **8.5%** | 7.0-10.3% | **1.67x** | 28/272 = 10.3% | NOT MET, HIGH |
| 0.54 (central) | 98/1153 = **8.5%** | 7.0-10.3% | **1.67x** | 28/272 = 10.3% | NOT MET, HIGH |
| 0.88 (high) | 60/1153 = **5.2%** | 4.1-6.6% | **1.02x** | 17/272 = 6.3% | **MET** |

- **0.50 reproduces the finding exactly** (98/1153, 1.67x), so this tree measures on its
  instrument.
- **The verdict flips inside the range.** Between 0.50 and 0.88 the reading falls about 8.7 points
  per unit of s, so the pooled interval first reaches 5.1% near **s = 0.75** (linear
  interpolation, not measured).
- **Predictions.** 0.30 was predicted at 10-13% and read 9.4%: refuted on the low side. 0.88 was
  predicted at 2.5-5% and MET or LOW, and read 5.2%, MET: the reading is just above the predicted
  band, the verdict is as predicted. The response is weaker than 1 − s because the stock is
  counted per account and a chronic failer holds several bills, each drawn on its own (named gap
  4).
- **What holds the stock at each end** (2019 account-quarters behind): at 0.30, 100 of 108 hold a
  never-settled bill; at 0.50, 82 of 98; at 0.88, only 17 of 60. **At the high end 43 of the 60 are
  bills the world WILL repay, dated at the end of Ofgem's 22-month window** (named gap 2). So at
  the top of the range the result rests on the dating of the late repayers, not on the share.
- **0.54 reads the same electricity count as 0.50.** Each bill draws one uniform, so moving the
  threshold from 0.50 to 0.54 re-dates only bills drawn in that 4-point band, and none of them
  changed a 2019 electricity quarter-end count. The predicted 7-9% held.
- Gas, pooled 2019: 16/202 = 7.9% at 0.30 and 0.50, 12/202 = 5.9% at 0.54, 8/202 = 4.0%
  (2.0-7.6%) at 0.88.

---

### Scope, corrected the same day (2026-10-09, delivery seat)

The table above was measured on the world as it stood at 63f429536, where ONE share applied to
every failed bill. Before this section landed, 95c1193cb split the never-repaid share by payment
method from Centrica's provisions on live UK residential balances over 90 days old (ARA 2025
Note 17): Direct Debit 7.4% never repaid (92.6% repaid), standard credit 50.3% (49.7% repaid);
prepayment, which Centrica does not report, keeps this toggle. On that world it measured 4.3%
(Wilson 3.3-5.7%, 0.85x Ofgem's, MET) with the same instrument and book. *(Corrected 2026-10-10:
that interval was too narrow. On the account-clustered interval it is 2.4-6.7%. Three dice seeds
pooled read 6.1% (4.6-7.8%), 1.19x, MET, which is not established either way.)*

The two readings agree rather than compete. This range is for the WHOLE book; Centrica's split
is by method, and a mostly-DD book weighted by its split lands in the high part of the range,
which is where the measurements above put the flip to MET (about 0.75). Centrica's own note says
which way its figure errs: a provision is a stock rate by value, so it overstates never-repaid
per bill, which would push the book's repaid share higher still. What this toggle governs from
here is the methods the split has no row for; the range still bounds what the split adds up to.

## Sources

- Added 2026-10-08 for §(e), all retrieved 2026-10-08:
  - GoCardless, Octopus Energy case study: <https://gocardless.com/stories/octopus-energy>
  - GoCardless, Jellyfish Energy case study: <https://gocardless.com/stories/jellyfish-energy>
  - GoCardless, Success+: <https://gocardless.com/solutions/recover-failed-payments>
  - FCA, *Financial Lives 2024: vulnerability and financial resilience*, p. 59:
    <https://www.fca.org.uk/publication/financial-lives/fls-2024-vulnerability-financial-resilience.pdf>
  - Ofgem, *Monitoring social obligations: 2018 annual data report*, pp. 2-3:
    <https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/monitoring_social_obligations_-_2018_annual_data_report.pdf>
  - Ofgem, *DRS policy update working paper*, Aug 2025, §4.5:
    <https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf>

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
