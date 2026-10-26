# GB domestic payment-method migration rates, while staying with the same supplier (2016-2025)

**Knowledge:** debt-and-collections

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

## Addendum 2026-10-03: a channel change has two authors

**What the PB8 park conflates.** In the real trade, two different parties change a payment channel:

| route | who decides | what it needs |
|---|---|---|
| DD -> standard credit after repeated returned collections | **the supplier** stops presenting a mandate that keeps coming back | a collections policy acting on an observable it already holds |
| credit -> PPM through debt (warrant / remote switch) | **the supplier**, under SLC 28B and the 2024 restart conditions | the same, plus the code of practice |
| PPM -> credit on the annual SLC 28.1A reassessment | **the supplier** | the same |
| the household cancels its own mandate, or asks to go onto DD | **the household** | a behavioural rate. **This is the one nothing publishes.** |

The supplier-authored routes are company decisions. They do not need a world-side migration rate,
and drawing one in the world would be the wrong side of the epistemic wall. The rate they produce
should come out of the policy acting on the book, not go in as a number.

**What the tree does today (measured):**
- `simulation/household_segments.py::payment_channel_for_customer` gives each household and fuel a
  deterministic hash. Its channel is fixed for life.
- The world does return DDs (`simulation/arrears_engine.py` `_DD_FAILURE_PROB`, through
  `simulation/bacs_rails.py`), but every return carries ARUDD code 0, "refer to payer". No world
  household ever cancels its own mandate (code 1).
- The company already sees every return: `company/billing/dd_collections_desk.py::record_collection_outcome`
  and `DirectDebitBook.failed_attempts`.
- **No production path acts on those returns.** The only caller of `cancel_mandate(` is the portal's
  customer-request route (`company/portal/app.py:556`). A household whose DD bounces every month
  stays on DD forever.

**What follows.**
1. **Route 1 can be built now with no new rate.** It is a company collections rule ("stop
   presenting after N consecutive returns") reading an observable the company already holds. Its
   migration rate then falls out of the world's DD-failure draw. Two caveats: that draw is itself
   unsourced (the C1 GAP in `dd_failure_basis_and_live_arrears_provision_rates.md`), and the build
   lives in `company/billing/`, not PB8's `W2_customer_generator` scope. The world-side half
   is only the seam: the channel the household pays by has to follow the mandate.
2. **N is a practitioner question.** The mechanism (British Gas: 2 failed presentations, then the
   DD is stopped) has one supplier's help page behind it. Whether that is the industry norm, and
   whether "moved to another payment option" means standard credit or a fresh DD set-up, are things
   no published source will settle. Per CLAUDE.md's third side of knowledge, the director should
   confirm this before it is built. This one is reversible, so it is recorded here, not escalated.
3. **The household-authored route stays parked** on the published-rate gap, unchanged.

PB8's `block_reason` in the maturity map points here.

---

## Addendum 2026-10-11 — the full range of arrangements, who/why, and cap treatment (for a personal payment plan)

*Research pass, discovery agent, for the director's 2026-10-11 instruction on a personal payment
plan merged with debt management. Extends PB8 with the arrangement taxonomy, cap treatment, and
what is/is not known about take-up and choice.*

### 1. Taxonomy — ESTABLISHED: only three cap-recognised methods; everything else is a variant

DESNZ's *Quarterly Energy Prices* (Dec 2025, p.9): *"We track the three main payment methods...
prepayment, credit and direct debit."* PPM = pay-as-you-go against a topped-up balance. Standard
credit (SC) = pay on receipt of bill. DD = "a recurring payment based on an estimated usage which is
**revised based on actual usage**" — DESNZ's own definition makes review mechanics part of what DD
*is*. **There is no fourth cap category.** Variable DD, budget plans, seasonal/flexible DD and smart
PAYG are implementations of one of the three (variable DD is still DD; smart PAYG is PPM on a smart
meter). **Load-bearing for a plan: a "seasonal" or "flexible" product sits on top of a regulated
method's cost basis, it does not get one of its own.**

### 2. Who, and why — shares re-confirmed; WHY is thinner, and points toward non-choice

Shares: DD ~72–73% (Sept 2025); SC+PPM remainder ~27–28%; **the SC-vs-PPM split of that remainder is
still NOT ESTABLISHED** (JS-rendered Ofgem data portal, unchanged gap; QEP's XLSX tables 2.2–2.4 were
not pulled this session — concrete next step, not attempted here).

Ofgem's *Decision on adjusting standing charges for Prepayment Customers* (23 Feb 2024), citing its
own *Consumer Impacts of Market Conditions* survey (Wave 3 Dec 2022, Wave 4 Jul 2023), is the useful
find: *"the primary reason customers choose their payment methods, **noting that not all customers
are able to actively choose**."* On SC specifically: *"a doubling in the proportion of SC customers
falling behind in their energy bills"* between the two waves (7 months apart), plus **"low awareness
of the price differential between SC and DD"** — Ofgem's own conclusion that price differentials are
"an ineffective method of incentivising payment method choice" for this group.

**ESTABLISHED (H), qualitative, no numeric split:** PPM is frequently not actively chosen (debt
install/remote switch, landlord-fitted at move-in — consistent with PB8's route-2 research above); SC
shows rising arrears and low DD-price awareness, consistent with inertia/no-DD-access rather than
deliberate budgeting choice for a material share of its users. **GAP, stated explicitly:** the brief's
"control, budgeting, distrust of DD" as *positive* chosen reasons is not evidenced in anything read
this session — what is evidenced points the other way. No income/tenure/vulnerability crosstab
against method was reachable (survey data tables not pulled).

### 3. Cap treatment — ESTABLISHED, with an exact, recent magnitude

**PPM↔DD standing-charge levelisation (Phase 1) is real, dated, quantified.** Ofgem decision, 23 Feb
2024, effective 1 April 2024, reconciled between suppliers (REC R0147): *"The £52 benefit for PPM
customers comes at a cost of £10 per DD customer [/yr, inc. VAT]... net benefit of £112m... reductions
in total debt of £12.3m."* **Phase 2 (SC↔DD debt-cost levelisation), planned for April 2025, was
PAUSED** per Ofgem's Aug 2024 open letter — standard credit's premium over DD remains un-levelised.

**Current premium, DESNZ QEP Dec 2025 Chart 2.4, combined dual-fuel, 2025 averages:**

| method | 2025 avg annual bill | vs DD | vs 2024 |
|---|---:|---:|---|
| Credit (SC) | **£2,015** | **+£131** | +£47 / +2.4% |
| Direct debit | **£1,884** | — | −£1 / −0.1% |
| Prepayment | **£1,817** | **−£67** | +£65 / +3.7% |

**Striking, confirmed (not derived): prepayment is now the CHEAPEST method (£198 below credit),
reversing the historical PPM premium** (Ofgem 2014: ~£80/yr PPM premium over DD, down from ~£140 in
2009 — kept as pre-levelisation baseline only, superseded by the table above). **Standard credit,
untouched by levelisation, is the clear most-expensive method (£131–198/yr).** For a plan: moving an
SC household onto DD/PPM is a larger, sourced saving than anything achievable by adjusting within SC.

### 4. Migration — one addition to the existing gap list

The Phase 1 reconciliation mechanism (REC R0147) is itself evidence Ofgem expects ongoing PPM↔DD flow
— it exists to true up standing-charge revenue between suppliers as customers move. **Indirect (L)
evidence of continuing flow, not a rate**; none of the three gross-rate gaps already logged above are
closed by this addition.

### What this means for a personal payment plan

1. **Method is now a secondary lever to amount.** Since PPM is at parity-or-cheaper than DD, the
   biggest cap-driven saving is moving an SC household onto DD/PPM (£131–198/yr), not the collection
   pattern once there — price that move explicitly in any customer-level value model.
2. **"Not actively choosing" is the operative finding on PPM, plausibly SC too** — a plan proposing a
   method change is evidenced not to be fighting informed preference in a large share of cases, but no
   take-up rate for an offered switch is published; do not assume one.
3. **SC/DD debt-cost levelisation is paused, not delivered** — a plan relying on future parity there
   is building on a stalled policy; Ofgem's promised "Autumn 2024" debt-policy update was not found
   published as of this session.
4. **The SC/PPM split of the non-DD remainder and any income/tenure/vulnerability crosstab remain the
   two load-bearing gaps**, unchanged from PB8's prior verdict — next step is pulling the QEP XLSX
   tables and the Consumer Impacts Wave 3/4 data tables directly, not their policy-document summaries.

### Sources added this pass

- DESNZ, *Quarterly Energy Prices*, December 2025, pp.9–10 (Chart 2.4) — full PDF read, not only the
  commentary extract previously cited: <https://assets.publishing.service.gov.uk/media/6942cb008f4636fa2c547df5/quarterly-energy-prices-december-2025.pdf>. Retrieved 2026-10-11.
- Ofgem, *Levelling the cost of standing charges on prepayment meters* (workstream history: CfE Apr
  2023 → consultation Aug 2023 → statutory consultation Nov 2023 → decision Feb 2024) —
  <https://www.ofgem.gov.uk/consultation/levelling-cost-standing-charges-prepayment-meters>. Retrieved
  2026-10-11.
- Ofgem, *Decision on adjusting standing charges for Prepayment Customers*, 23 Feb 2024 (117pp; Exec
  Summary and §2 read directly) — <https://www.ofgem.gov.uk/sites/default/files/2024-02/Decision%20on%20adjusting%20standing%20charges%20for%20Prepayment%20Customers.pdf>. Retrieved 2026-10-11. Source
  of the £52/£10/£112m figures and the "not all customers are able to actively choose" / SC-awareness
  quotes.
- Ofgem, landing page carrying the Aug 2024 Phase 2 pause notice —
  <https://www.ofgem.gov.uk/decision/decision-adjusting-standing-charges-prepayment-customers>.
  Retrieved 2026-10-11.
- Ofgem, *Ofgem publishes analysis: price differences between payment methods* (pre-cap era) —
  <https://www.ofgem.gov.uk/press-release/ofgem-publishes-analysis-price-differences-between-payment-methods>. Retrieved 2026-10-11. Historical ~£80/yr (2014) vs ~£140/yr (2009) PPM premium, superseded
  by §3's current figures.

*Fetched live 2026-10-11. No figure in this addendum is simulation output.*

---

## The household's own payment-method acts: what the world does (2026-10-12)

**2026-10-12, the world lane, on the director's principles of 2026-10-11 and his ruling of
2026-10-12 ("mandate cancellation as its own act, the debt-to-prepayment route").** No new source
was read: the web-search budget for the session was spent, and the in-repo evidence was re-read.
The addendum of 2026-10-03 above splits channel changes by author; the supplier's routes stay
company decisions. This section is the household's side only, built in
`simulation/payment_method_dynamics.py`.

**The acts, defined first.** (1) *Cancelling a mandate for its own reasons*: the household tells
its bank to stop the DD with no bill shock behind it (distrust, wanting to control when money
leaves, closing or switching the account). The shock-driven cancellation is DD4b
(`what_bill_shock_is.md`). (2) *Paying by hand afterwards*: pay on receipt. (3) *Stopping paying*:
not a separate act in the world; a household paying on receipt that cannot pay fails at its own
tier's rate. (4) *Its answer on the prepayment route*: agreeing or not when offered a meter to
recover a debt; living with one fitted under warrant (the fitting is the supplier's act).

| Choice the world makes | Range or rule | Evidence | Mark |
|---|---|---|---|
| Own-reasons cancellation, per DD household-year, LOW stress | 0.005-0.02 (`method_own_reasons_cancel_share`), shipped 0 | none: "the one nothing publishes" (addendum 2026-10-03). DESNZ QEP: the DD share rose 3-4 points over 2020-25, a net figure that bounds no gross flow | ESTIMATE, labelled; both ends are choices said to be choices |
| A stretched household cancels more | x the world's stress relativity (4x, 11.7x), capped at 1 | Ofgem's Feb 2024 decision: many do not actively choose a method, and SC payers fall behind more; the direction, not a size. The relativity itself is unsourced (`arrears_engine._DD_TIER_RATIO_TO_LOW`), shared with DD4b so one scaling serves both | direction only |
| After cancelling it pays on receipt; the supplier sees an ARUDD 1 return that month and an ADDACS advice | reuses DD4b's book and wiring | Bacs scheme codes (already in `what_bill_shock_is.md`) | ESTABLISHED mechanism |
| Agreeing a prepayment meter offered for debt | 0.30-0.40 (`method_prepayment_offer_take_up_share`), shipped 0 | Ofgem indicators: 30-40% of customers repaying a debt repay through a PPM over 15 years (a stock of routes, read weakly as a choice share) | DERIVED, weak |
| Recovery once a meter is fitted for debt | GBP 6.01 a week electricity, 4.40 gas, from top-ups | Ofgem indicators, mean for new PPM-for-debt installs, calendar 2025 (`company_debt_management.md` s.2) | ESTABLISHED (a mean over new installs). *Not built (corrected 2026-10-12): first written into `payment_method_dynamics.py`, removed the same day because no meter is changed for debt in the run, so no live code reached it; it is built where the run first changes one.* |

**Shipped off, and what fires in the run.** The cancellation is drawn every billed month, the annual
share taken as a monthly hazard, before that month's collection is presented, when its share is on;
it is the only one of these acts the run can reach today. (First built at the annual review, it was
moved the same day: the run reaches a renewal review only about 20 times in 190 account-years on a
40-founder book, so a yearly share drawn there would have been an eighth of itself.) No supplier
in the run offers a prepayment meter or pursues a warrant, so the prepayment answers are the world's
side for the day one does.

**GAPs, carried rather than filled:**
- **the coupling of payment channel to income, tenure and vulnerability.** The research supports a
  direction (prepayment skews to low income, renters and debt) but no crosstab with a number was
  reachable: the SC/PPM split and any income/tenure crosstab are this page's two load-bearing gaps
  (s.4 of the 2026-10-11 addendum), and this session's web search was exhausted before EHS or the
  Consumer Impacts survey tables could be read. So the world's channel stays drawn once and
  uncoupled, and the first step is pulling the English Housing Survey energy tables and the Consumer
  Impacts Wave 3/4 tables, not a further search. Building a coupling on a direction alone would put
  an invented strength behind a published share;
- any published household-initiated cancellation rate (ADDACS code 1 volumes by sector are
  collected by Bacs and not published by energy supplier);
- re-mandating after a cancellation. *(Corrected 26 Oct: the world now answers the supplier's invitation
  at a labelled range, in the next section.)*
- a per-household self-disconnection rate on a meter fitted for debt (only stocks over all smart PPM
  customers are published: 564,191 electricity in Q2 2026);
- prepayment back to credit on the SLC 28.1A reassessment (a supplier act; no flow published).

## A take-up rate for an invitation back onto DD (2026-10-26)

**What is measured.** The probability that a household off DD signs the new mandate its supplier
invites it to, per invitation. It is not a yearly rate. The supplier decides when to ask
(`company/billing/dd_collections_desk.py`, `REMANDATE_OFFER_AFTER_PAID_BILLS`), and the household
decides whether to sign (`simulation/bacs_rails.py`, `REMANDATE_ACCEPTANCE_PROBABILITY`).

**No energy figure exists.** A fresh search (26 Oct) found no supplier, Ofgem or Citizens Advice
figure for the response to an invitation onto DD. Ofgem's letter trials (CMOL 2017, Active Choice
2018) measured switching tariff, not payment method. Two figures from elsewhere bound a belief:

| Source | What it counts | Figure | Fit |
|---|---|---|---|
| Medway Council with the Behavioural Insights Team, Test+Build RCT, Jan-Jun 2017 (LGA case study, <https://www.local.gov.uk/case-studies/using-behavioural-insights-convert-taxpayers-direct-debit-medway-council>) | council tax payers not on DD who set up a DD within a month of the annual bill, by letter insert | best insert ("loss aversion") 5%, "over 42%" above the no-insert control, so the control was about 3.5% | a single prompt to a non-DD stock; council tax rather than energy; the one-month window matches one invitation |
| Ofgem, *Customer Engagement with the Energy Market: Tracking Survey 2015*, OG19a/OG19c (electricity), <https://www.ofgem.gov.uk/sites/default/files/docs/2015/09/customerengagementreport2015_final_for_publication.pdf> | bill-payers who stayed with their supplier: 11% changed tariff or payment method; of those (n=184), 9% changed FROM pay-on-receipt | about 1% of non-switching bill-payers a year | a gross flow, to any method (DD or prepayment), prompted or not; n is about 17 respondents |
| DECC, *Quarterly Energy Prices*, Dec 2015, s.2.3, Chart 2.3.1, <https://assets.publishing.service.gov.uk/media/5a80c814e5274a2e87dbbc9b/QEP_final_Dec_15.pdf> | standard electricity customers by payment method, end-Sept 2015 | credit 26%, DD 57%, prepayment 17% | turns the row above into about 1%/26%, so at most about 4% of standard credit payers a year (lower if, as QEP says, SC payers switch supplier least) |

**The belief.** EVIDENCE RANGE 0.035-0.05 per invitation: Medway's control to its best insert. The
code ships **0.035**, the lower edge (F11). Two things are unmeasured, and both would make 0.05 an
overstatement:
1. whether a second ask after a decline pulls as well as the first. The desk asks again after
   every three on-time bills, so a household that keeps paying on time could be asked four times a
   year. At 0.035 that compounds to 13% a year, which already exceeds the published generic flow
   (≤4% a year). **GAP.**
2. how a household that recently left DD differs from a long-standing non-DD payer. One that
   cancelled at its bank chose to leave, and one the supplier stopped is now paying on time. No
   source gives the direction for either group. **GAP.**

**What it does in the run.** On the 40-household spell book (`tests/simulation/test_a_dd_stop_is_a_spell.py`),
over 8 seeds: 0 of 28 stopped households are back on DD by the end of the book's year with no rate, 1
at 0.035, and 3 at 0.05. This is within the generic flow. A resi payment outcome is drawn the same way
on either channel, so a re-mandate relabels bills and moves no payment outcome
(`test_a_re_mandate_moves_no_outcome`). The DD share of bills rises a little, and bad debt does not
move.

**What would replace it.** A supplier's own conversion figure for DD-invitation campaigns, or a
published SC-to-DD flow (QEP gives stocks only).

## What the drawn world is checked against (2026-10-19)

The direct-debit share above, stated as a claim the drawn founder book must bear.
`tools/world_claims.py` reads this block and measures the accounts the production draw makes at the
production founder count, pooled over eight seeds (about 3,000 accounts). It fails
`tests/tools/test_world_claims.py` outside the band. The band is DESNZ's 69% (Sept 2020) to 73%
(Sept 2025), widened by 3 sd of sampling noise at that pool size (about 2.5 points).

**GAP:** the founders open in 2016, and the published shares read here start in 2020. The 2016 to
2019 DD share was not read this session. QEP table 2.2 holds it, and it is the next thing to pull.
The prepayment-against-standard-credit split of the remainder is not checked, because it is not
established (row above) and the draw does not separate it: every non-DD founder is `other`.

```world-claims
- id: direct_debit_share_of_accounts
  measure: direct_debit_share_of_accounts
  band: [0.665, 0.755]
  source: "DESNZ Quarterly Energy Prices, Dec 2025 commentary, p.9: standard electricity DD 69% (Sept 2020) to 72% (Sept 2025), gas to 73%."
```
