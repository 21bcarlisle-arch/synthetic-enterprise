# How often does a losing supplier object to an indebted domestic customer's switch, and how often does the objection actually stop it?

**Knowledge:** acquisition-and-retention-economics

Research pass, 2026-10-03, discovery agent. Opened by
`docs/staging/SEAT_FINDING_THE_WORLD_LETS_A_DEBTOR_SWITCH_AWAY_BECAUSE_THE_DOMESTIC_DEBT_OBJECTION_IS_UNMODELLED_2026-10-03.md`,
which recorded that both source PDFs had previously "returned compressed streams". They do not —
`pdftotext -layout` (already installed at `/usr/bin/pdftotext`) extracts both cleanly. This file is
the first full reading of their tables. `svt_drift_by_payment_behaviour.md` §"The magnitude: NOT
ESTABLISHED" is the prior attempt; its verdict is now substantially upgraded for the 2016 cross-
section and left unchanged for 2017-2025.

**Both source documents are the same regulatory review. Nothing later, more granular, or
dated after July 2016 was found** despite search attempts covering CSS go-live (18 July 2022)
and the years either side of it — see "What was searched and did not surface a figure" below.
Every number in this file is 2013-2016 vintage. Treat the magnitude as the best-evidenced snapshot
available, not as a 2016-2025 time series.

**Added 2026-10-08: the rest of the objection family.** `a_save_offer_against_the_switching_rules_and_the_seam.md`
§5 reads the Switching Programme's 2016 RFI (Ofgem IA assumptions log, Sept 2017). It finds Customer
Requested Objections at **1.28% of domestic switches** (or ~0.4%: two Ofgem papers on the same RFI
disagree), registration withdrawals at 3.2%, rejections and ETs. It also corrects how the 2014
consultation figure is read: "around 7% of domestic … gas transfers and 14% of electricity
transfers" are blocked, and **the 14% covers domestic and non-domestic electricity together**. It
finds no CSS-era (post-18 July 2022) objection rate, which is consistent with the gap recorded below.

## The quantity, defined before it is measured

Three different things are each called "the objection rate" somewhere in the literature, and they
have three different denominators. Conflating them is the error this file exists to prevent.

1. **The published SLC 14 objection rate** — all objections, any permitted ground (debt,
   erroneous transfer, no contract in place, or unmatched Related Meter Points), over **all
   attempted domestic transfers** (switchers and non-switchers, indebted and not). This is what
   Ofgem's annual retail market indicators publish and what the decision letter quotes: "a total
   objection rate of 6% for domestic electricity customer transfers and 5% for domestic gas
   transfers" (March 2016). Over 90% of this is debt objections specifically (IA p.4, "The vast
   majority of objections (well over 90%) in the domestic market occur because a customer is in
   debt. Erroneous transfers make up most of the rest.") — so the debt-specific objection rate as a
   share of **all** attempted transfers is roughly 5.4-6.3%, call it **~6%**.

2. **The conditional the question actually asks: given a domestic credit customer is in debt and
   attempts to switch, how often is the attempt objected to?** This denominator is "indebted
   customers who attempt to switch", not "all attempted transfers" — a much smaller, selected
   population, and the right one to condition a simulation's departure draw on. Ofgem's own
   figure, in the decision letter and IA §1.35 verbatim: *"2-3 times as many customers are allowed
   to switch with a debt (typically 430,000 a year) than are blocked through debt objection
   (typically around 170,000 a year). In other words, over 70% of indebted customers who want to
   switch are allowed to by their current suppliers."* **That makes the conditional objection rate
   ≈ 170,000 / (430,000 + 170,000) ≈ 28%**, i.e. **roughly 1 in 4 indebted domestic customers who
   attempt to switch are blocked**, not 6%. The two figures are not alternative estimates of the
   same thing; (1) is diluted by the ~95%+ of transfer attempts that carry no debt at all, (2) is
   not.

3. **Given an objection happens, how often does it actually stop the switch (the customer stays)
   rather than merely delaying it?** This is the question's second half and the IA answers it only
   indirectly, by tracking a cohort of blocked customers forward in time rather than publishing a
   single "stayed" percentage — see "Outcome of a block" below. There is no single published number
   for this; there is a chain of conditional probabilities that has to be multiplied together, and
   each link is dated and has its own base.

## Established figures, with exact wording and location

All page/paragraph references are to the PDFs fetched 2026-10-03:
- `https://www.ofgem.gov.uk/sites/default/files/docs/2016/07/decision_on_review_of_domestic_objections.pdf`
  ("the decision letter", 25 July 2016, 6 pages, signed Anthony Pygram)
- `https://www.ofgem.gov.uk/sites/default/files/docs/2016/07/impact_assessment_on_review_of_domestic_objections.pdf`
  ("the IA", published 28 July 2016, 34 pages)

| # | Quantity | Value | Denominator / population | Source |
|---|---|---|---|---|
| 1 | Published SLC 14 objection rate, all grounds, March 2016 | **6% electricity, 5% gas** of all domestic transfer attempts (both down 1pp on March 2015) | all attempted domestic transfers, any payment method, any ground | Decision letter p.2; IA Executive Summary p.3 |
| 2 | Same rate, RFI data Jan 2013 - Sep 2015 | "broadly stable ... at 6-7% of all transfers" | same | Decision letter p.2; IA §1.26 |
| 3 | Longer baseline, since the 2006/7 Supply Licence Review | objections "typically represented 6-7% of domestic customer transfers" | same | IA §1.5 |
| 4 | Share of objections that are debt-grounded | **"well over 90%"**; "erroneous transfers make up most of the rest" | all objections, any ground | IA p.4 Context; IA Exec. Summary p.3 ("Debt objections account for over 90% of these objections") |
| 5 | Erroneous-objection rate | **NOT separately quantified** — only "most of the rest" of the <10% non-debt remainder | — | IA p.4, §3.3 |
| 6 | Total debt objections raised (industry, suppliers covering 98% of domestic customers) | **374,463 (2013); 285,697 (2014), a 24% fall; 284,323 (Jan-Sep 2015)** | count of objections (not customers — see row 8) | IA §1.24-1.25 |
| 7 | Individual customers experiencing a debt objection (de-duplicated across multiple attempts/fuels) | **≈187,232 (2013); 142,848 (2014); 142,162 (Jan-Sep 2015)** | domestic customers, after removing dual-fuel double-counting and repeat attempts at the same transfer | IA §1.25 |
| 8 | Why objections > customers | "around half the number of objections raised" are individual customers, "partly because of dual fuel customers ... and partly because some suppliers try more than once" | — | Decision letter p.2 |
| 9 | **Customers allowed to switch despite debt, vs blocked** | **"typically 430,000 a year" allowed vs "typically around 170,000 a year" blocked, i.e. "2-3 times as many ... allowed ... than are blocked"** → **≈70-72% allowed / ≈28-30% blocked**, conditional on being indebted and attempting to switch | indebted domestic customers attempting to switch (comparable-data subset of suppliers, incl. 4 of the 6 largest) | Decision letter p.3; IA §1.30-1.35 (footnote 9: "four of the six large domestic suppliers") |
| 10 | Payment-method mix of debt objections | over 80% of debt objections are credit or prepayment; **credit 46-48%, direct debit 11-12%, prepayment 32-36%** | all debt objections, 2013-2015 | IA §1.27 |
| 11 | DAP usage by PPM customers in this period | "actual switching using this mechanism remained very low over the period" | PPM customers with debt <£500 | IA §1.27 |
| 12 | Average debt of blocked customers, by year | **£268 (2013) → £377 (2014) → £418 (2015)** | customers whose transfer was objected to on debt grounds (suppliers covering 63-67% of domestic customers) | Decision letter p.2; IA §1.28, footnote 7 |
| 13 | Debt level at which "blocked" overtakes "not blocked" (the crossover point) | **2013: ~£200-250. 2014: equal at £600-650, but blocked did not clearly exceed not-blocked until over £1,000 (data limitation, see row 14). Jan-Sep 2015: ~£350-400.** | comparable sub-sample, 4 of 6 largest suppliers | IA §1.32-1.34, Figure 1 |
| 14 | Known distortion in the 2014 figure | one large supplier in the comparable sample "did not object to any customers switching while it was updating its billing system" in 2014 | same sub-sample | IA §1.33 |
| 15 | "More likely than not to switch" debt level, 2015 | **£300-350** | same | Decision letter p.3; IA §1.35 |
| 16 | Informal supplier de-minimis thresholds | "ranging up to £200 per fuel, sometimes varying by payment type", below which many suppliers allow the transfer regardless | supplier policy, not a licence rule | Decision letter p.3; IA §1.29 |
| 17 | Statutory debt-age threshold before an objection may be raised | **28 days** outstanding since written notice to the customer, and the supplier must have notified the customer of the charge in writing first; "a supplier cannot object for an outstanding amount 'on their system' (whatever the amount) if they have not previously informed the customer about it and the debt has not been outstanding for 28 days" | SLC 14; decision letter p.1; IA Context p.4 |
| 18 | Objection window length (pre-CSS, as switching ran via gas/electricity industry flows, not CSS) | electricity (MRA): **5 working days**. Gas (UNC): variable, "as low as two working days" to make a 3-week switch achievable | pre-Faster-Switching switching process | IA §1.1, footnote 1 |
| 19 | DAP debt threshold for PPM | originally raised to **£200** (date of that rise not given beyond "we also doubled" in the 2006/7 review); **"has since been raised to £500"** as of 2016 | PPM customers only; supplier agreement to accept the debt transfer is still required | Decision letter footnote 1, p.1; IA §1.9 |
| 20 | Internal switching (tariff switch with existing supplier) by blocked customers, by year | **16,850 (2013) = 9.00%; 4,968 (2014) = 3.48%; 6,569 (2015) = 4.62%** of that year's estimated blocked-customer count | 14 suppliers = 95% of domestic gas+electricity market; 11 of those 14 actually offer alternative contracts and object for debt | IA Table 1, §1.36-1.37 |
| 21 | Headline restatement of row 20 | "only around 5% of the customers who have been prevented from switching supplier on grounds of debt switch tariffs with their current supplier" → **"around 95% of debt blocked customers are potentially missing out" on cheaper own-supplier tariffs** | same | Decision letter p.4; IA §1.37 |
| 22 | Debt repayment rate for blocked customers (two snapshot months, Nov 2013 & Apr 2014, measured as of Sept 2015) | **"just over half"** had repaid the debt by the time of reporting; of those, **~70%** repaid within 3 months; PPM customers took longest | Decision letter p.3; IA §1.38-1.39 |
| 23 | Switch-away rate among repaying blocked customers, within a year | **27-39%** within a year of being blocked (method 1 — time since objection) or **41-60%** within a year of repaying the debt (method 2 — time since repayment), varying by month/payment method; DD and credit customers switched away more than PPM | Decision letter p.3; IA §1.40-1.41 |

## What "the customer stays" means — a chain, not a single number

The question's second half ("how often does an objection actually stop the switch, customer stays")
has no single published answer because Ofgem measured a **cohort over time**, not a yes/no outcome.
Multiplying the published links gives a bound, not a quoted figure — **this derivation is mine, not
Ofgem's, and must be labelled as such wherever it is used**:

- Starting population: domestic customers objected to on debt grounds in one of two snapshot months
  (Nov 2013, Apr 2014).
- **≈50%** had NOT repaid the debt by the time of reporting (row 22) — these customers cannot
  complete a switch while the debt remains outstanding and the objection stands, so within the
  observed window they stayed by construction.
- Of the **≈50%** who HAD repaid: **27-39%** (method 1) had switched supplier within a year of the
  original block. That means **61-73% of repayers had NOT switched within a year**, despite being
  free to.
- Chaining: stayed-within-a-year ≈ 50% (never repaid) + 50% × (61% to 73%) (repaid but didn't switch)
  **≈ 80% to 87%** of blocked customers had not switched supplier within a year of the block.
  Correspondingly **≈13% to 20%** had switched away within that year despite having once been
  blocked. Internal (own-supplier) switching adds only ~3-9% more (row 20) on top of whichever of
  these two outcomes applied, so it does not materially change the "stayed on the same deal" share.

This is consistent with, and sharpens, the decision letter's own framing that objections "stop"
rather than merely "delay" most attempted debt-motivated switches for the customers they catch —
but note the base population here is **already-blocked** customers, not **all** indebted customers
who tried to switch (that split is row 9, ~70/30 allowed/blocked). The two have to be composed, not
substituted for each other, to get from "indebted customer attempts to switch" to "customer is still
with the same supplier a year later":

```
P(still with same supplier, 1yr | indebted & attempted switch)
  ≈ P(blocked | indebted & attempted switch) × P(stays | blocked, 1yr)
  ≈ 0.28-0.30  ×  0.80-0.87
  ≈ 0.22-0.26
```

plus whatever share of the ~70-72% who were ALLOWED to switch chose not to for unrelated reasons —
which this review does not measure and which is a different (general inertia) question. **Do not
read 0.22-0.26 as "a quarter of indebted switch-attempters end up staying" without the composition
being visible**: it already nets out the ~72% who were simply never blocked and would need a
separate churn-hazard treatment, not this file's figures.

## What is ESTABLISHED vs NOT established

| What | Status | Confidence |
|---|---|---|
| Overall SLC 14 objection rate ≈6% (elec) / 5% (gas) of all domestic transfer attempts, 2015-2016 | **Established** | H — primary regulator source, multiple consistent restatements across both documents |
| >90% of objections are debt-grounded; erroneous transfers are "most of the rest" | **Established** (direction and rough share) | H for ">90%"; the erroneous-only rate is NOT separately published (gap) |
| Conditional block rate given indebted + attempting to switch ≈ 28-30% (≈70-72% allowed) | **Established for 2015** (and roughly stable 2013-2015 per the RFI) | H — this is Ofgem's own stated ratio, not a derived one |
| Debt-age threshold = 28 days (statutory, SLC 14) | **Established** | H |
| PPM DAP threshold = £500 (as of 2016; raised from £200) | **Established as of 2016.** NOT re-verified for any later year this session, though `gb_payment_method_migration_rates.md` and this repo's other files already independently cite £500 as the figure still current through the 2023 reforms | H for 2016; the repo's other citations imply continuity to 2023 but none of them is this session's own check |
| Average debt of blocked customers rises £268→£377→£418, 2013-2015 | **Established** | H |
| Debt-level "crossover" where blocked customers outnumber allowed ones moves up over time (≈£200-250 in 2013 to ≈£350-400 in 2015) | **Established, with a named data quality caveat for 2014** (one supplier's system migration distorts that year) | M — real suppliers, real data, but the three years are not on a consistent footing and the sub-sample is 4 of 6 large suppliers, not the whole market |
| ~50% of blocked customers had repaid by time of reporting; ~70% of repayers did so within 3 months | **Established** | H |
| 27-39% (method 1) / 41-60% (method 2) of repaying blocked customers switch away within a year | **Established**, but the method 1/2 split and the month-to-month variation mean this is a range, not a point estimate | H for the range as published; M for picking any single number inside it |
| Only ~5% of blocked customers switch tariff with their existing supplier instead | **Established** | H |
| A single number for "P(objection stops the switch, customer stays)" | **NOT established as a single published figure.** The ≈80-87%/≈13-20% split above is **derived by this file**, composing three of Ofgem's own published rates, not quoted from the source | L for the composite (derived); H for each input rate individually |
| Any objection-rate or outcome figure for 2016-2021 | **NOT established.** No later Ofgem publication on this specific topic was found | Gap |
| Any objection-rate or outcome figure for the CSS era (go-live 18 July 2022) onward | **NOT established.** See search log below | Gap |
| Whether SLC 14's debt-objection regime itself changed when switching moved to CSS | **NOT established either way this session.** The decision letter (2016) explicitly flags that "the upcoming programme of changes to move towards faster and more reliable switching" might prompt "a separate impact assessment" of objections, but no such later document was located; `ADVISOR_SCOPE_BRIEF_INDUSTRY_BOUNDARY_2026-08-04.md` (secondary, in-repo) only states CSS "carries objections" as a registration function, which is consistent with continuity but does not confirm the licence condition's wording or the 28-day/£500 thresholds are unchanged post-2022 | Gap |
| REC Schedule 23 (CSS registration services) wording on the objection window | **NOT established.** Not located in `docs/domain_artefact_library/` (no Schedule 23 text present) and not successfully fetched this session (see below) | Gap |
| The within-band structure Ofgem's own data implies (e.g. a smooth block-probability curve by exact debt amount) | **Partially established as a qualitative shape** (Figure 1, §1.31-1.34: block probability rises monotonically with debt, roughly — subject to the 2014 distortion) **but no supplier-level or industry-average numeric curve was published**, only the three single-year crossover points in row 13 | M — shape is real, no formula or table of probabilities by £-band exists |

## What was searched and did not surface a figure (so the gap above is a finding, not an omission)

- **Ofgem's Retail Market Indicators data portal** (`ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators`) — fetched live 2026-10-03, 326KB of HTML with zero occurrences of the word "objection" anywhere in the static document and no linked `.csv`/`.xlsx`/API endpoint found. This is JS-rendered, consistent with the pre-existing finding in `gb_payment_method_migration_rates.md` about the same page's debt-and-arrears indicators. **The page likely still carries a current objection-rate series — it is simply not fetchable by a scripted read.**
- Web search (DuckDuckGo HTML endpoint, then Bing) for later Ofgem publications combining "domestic debt objection" with 2021/2022/2023/2024 and with "Faster Switching"/CSS: no later Ofgem decision, consultation or impact assessment on domestic debt objections specifically was surfaced; search access was rate-limited partway through this session (empty/bot-check responses from DuckDuckGo after the first few queries), so **absence of a result here is weaker evidence than the primary-document reading above** and should not be treated as a confirmed "nothing exists" — only as "nothing was found this session".
- Attempted a direct guess at the Ofgem consolidated Standard Licence Conditions PDF URL to read the current SLC 14 text verbatim: wrong guess, returned a 194KB HTML error/redirect page, not retried with a second guess given time spent.
- `docs/domain_artefact_library/` (the regulation commons) has no file naming SLC 14 or REC Schedule 23 specifically; the only existing hits are indirect (the scope brief, and an unrelated CEDA data URL that happens to contain the substring "dap").

## How a simulation could use this (without inventing a number to fill the remaining gaps)

1. **The conditional to draw on is row 9, not row 1.** A household's departure draw, if it is to
   respect the debt-objection right at all, should condition P(blocked) on "is this account in
   debt and attempting to switch", not on "is this account attempting to switch" — using the ~6%
   overall SLC 14 rate here would understate the effect by roughly 5x, because it is diluted by the
   ~95%+ of attempts that carry no debt.
2. **A usable single-point estimate for 2013-2015, with its caveats attached:** P(blocked | in debt,
   attempts to switch) ≈ **0.28-0.30**, rising with debt level per the crossover points in row 13 (a
   household at the then-informal ~£200 de-minimis level is overwhelmingly likely to be ALLOWED to
   switch; a household at £350-400+ debt in 2015 was roughly at 50/50, and above that more likely to
   be blocked than not). **This is a 2013-2015 snapshot carried forward with no evidence it still
   holds** — see the gap rows above — so any simulation using it for 2016-2025 is extrapolating a
   stale regulatory snapshot across a decade that includes the 2022 energy crisis, mass supplier
   failure, and the CSS go-live, none of which this file's source documents could have seen.
3. **If a departure-blocking mechanism is built, it should carry the 28-day debt-age threshold
   as a hard gate** (row 17) before any probability is even evaluated — a debt notified and unpaid
   for under 28 days cannot legally be grounds for an objection at all, regardless of amount.
4. **The "stays" outcome is not an indefinite block.** A blocked household is not stuck forever: the
   composed estimate in "What 'the customer stays' means" above (≈80-87% still with the same
   supplier after a year) implies a release mechanism is needed — either the debt gets repaid and the
   household later switches (the dominant repair route per row 23), or it does not repay and remains
   with the original supplier, continuing to accrue the arrears the existing `arrears_engine`
   already tracks. **Do not model an objection as a permanent flag**; model it as a hazard that
   resolves on the household's own repayment trajectory, which this repo's own debt/arrears modules
   should already be computing for the account.
5. **PPM accounts should route through a different mechanism (DAP), not this one** — a PPM customer
   below the £500 threshold (2016 figure; not re-verified for later years) can switch supplier with
   the debt moving to the new supplier, which is a materially different outcome (the household DOES
   leave, the debt follows it) from a credit-meter objection (the household does NOT leave, the debt
   stays with the incumbent). Conflating the two payment methods under one "debt blocks switching"
   rule would misrepresent roughly a third of the debt-objection population (row 10: prepayment is
   32-36% of debt objections even though PPM customers have a nominal escape route the credit
   population does not).
6. **Do not build a numeric probability curve by exact £-band.** Row 13's three crossover points are
   real but are not a published formula, and the 2014 data point is known-distorted by one supplier's
   system migration. A simulation that needs finer granularity than "below an informal ~£200-350
   threshold, mostly allowed; above it, increasingly likely to be blocked" would be inventing the
   curve's shape between the three anchors, which this file's evidence does not support doing.

## Files this reasoning should update, once a decision is made to build the mechanism

This file is gather-only (R12/R13 posture) and makes no change to `simulation/` or `company/`. The
staging finding that opened this research
(`docs/staging/SEAT_FINDING_THE_WORLD_LETS_A_DEBTOR_SWITCH_AWAY_BECAUSE_THE_DOMESTIC_DEBT_OBJECTION_IS_UNMODELLED_2026-10-03.md`)
asked specifically for "the objection rate by debt age or amount" before closing — item 1 of its
"What closing it needs" list is now answered, to the extent the published record answers it at all
(row 9 and row 13 above); items 2 and 3 of that list (who it applies to, and the world-side draw
itself) are unchanged by this file and remain for whoever picks that atom up.
