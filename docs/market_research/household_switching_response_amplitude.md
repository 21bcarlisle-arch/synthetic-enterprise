# The household-level amplitude of switching response: what the two named sources establish, and what they do not

**Research completed: 2026-09-03, delivery seat.** Live sources fetched this pass: Ofgem Retail
Market Indicators data portal (HTTP 200, chart page); Ofgem/Ipsos **Consumer Survey 2021 —
Engagement report** (PDF fetched and `pdftotext`-parsed, 4,037 respondents). One further PDF was
fetched and discarded as off-subject: Ofgem's 2018 *Report on customer switching and disengaged
customers* is an ESP Consulting/VaasaETT review of **regulatory remedies** for disengaged customers
in other jurisdictions, and contains no switching-by-segment rate for GB.

**Opened by:** `docs/staging/SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`
§4 item 1, which named these two sources so the next attempt would start somewhere rather than in a
browser.

**This file is now the single home for this gap.** The two places that previously declared it
without pointing at each other — `docs/institutional/knowledge_map.md` (*Customer lifetime / churn*
row) and `docs/market_research/continuous_behavioural_engagement_w2_14.md` §4 item 6 — now both
point here and at each other.

---

## 0. The quantity actually wanted, stated before any source is read

`simulation/departure_level_anchor.py` carries a **per-year scalar**, bisected until the world's
whole-book departure rate equals the published rate. Replacing it with one constant leaves the
emergent level in band in 2 of 7 fitted years, and the miss is **compression**: emergent spread
9.1–19.6% against a record spread of 12.5–23.0%, roughly twofold and at both ends.

So the number the repair needs is:

> **By how much does an individual GB household's probability of leaving its supplier move between
> a low-switching year and a high-switching year — and how much of the market-level swing is
> carried by a few households moving a lot versus all households moving a little?**

That is a **within-household, across-year response amplitude**. Naming it precisely matters,
because the closest published things measure two *different* quantities that are easy to mistake
for it:

| quantity | what it is | is it what we need? |
|---|---|---|
| **A. market level, by year** | one switching rate per year for all GB | **no** — settled already; it is the thing to be explained, not the explanation |
| **B. between-group level, one year** | group A switches at 33%, group B at 17%, both in 2021 | **no** — a cross-sectional dispersion of *levels*, not a *response* |
| **C. within-household response to conditions** | this household's hazard in 2020 vs its hazard in 2022 | **yes** |

A published B does not become a C by being divided. This document's finding is that **the two named
sources supply A and B, and nothing published in either supplies C.**

---

## 1. Ofgem Retail Market Indicators — what it establishes

**Fetched:** `ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators`, 2026-09-03.
Chart: *"Number of domestic customers switching supplier by fuel type (GB)"*.

| month | domestic electricity switches | domestic gas switches |
|---|---|---|
| April 2026 | 243,754 | 183,180 |
| May 2026 | 237,988 | 181,733 |

**What this settles — the fuel-scope question, which was owed for a different reason.**
`docs/institutional/knowledge_map.md`'s *UK household switching volumes* row owes exactly this
reading, because ElectraLink's headline series (3.21m changes of supplier in 2024) could not be
reconciled to a fuel and its two readings differed by 1.8×. The per-fuel pair answers the ratio
directly:

- electricity / gas = **1.331** (April 2026), **1.310** (May 2026)
- electricity share of a both-fuel count = **57.1%** (April), **56.7%** (May)
- so a both-fuel numerator is **≈1.75×** its electricity leg

Applying the April share to ElectraLink's 2024 headline: read as **both fuels**, its electricity leg
is ~1.83m, or **6.5%** of a 28.0m electricity-account denominator; read as **electricity only**,
**11.5%**. The published band for 2024 is **12.5–16.1%**
(`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`). **Neither reading of
ElectraLink lands inside the band**, so the 1.8× ambiguity was never the only thing wrong with it,
and it stays an open cross-check rather than becoming the series. The 57.1% share is now the
established conversion factor, on one month, and is the thing to re-read across a full year before
it is used to move anything.

**What it does not establish — anything about dispersion.** The indicator is a **count of meter
points transferred**. No household attribute is attached to any unit; no denominator is published
beside it; there is no downloadable table, CSV or API endpoint on the page (Ofgem's own contact,
`marketmonitoring@ofgem.gov.uk`, is the route to the underlying data, and asking would be contacting
a real person — a reserved class, so not done here). The series is quantity **A** in §0, at higher
frequency and now split by fuel. It cannot be differenced into a household-level anything, because
it never had a household in it.

*Indicative only, and outside the 2016–2025 record:* 243,754 electricity switches × 12 over 28.0m
accounts annualises to **10.4%** for 2026. One month annualised across a seasonal series is a weak
reading and is recorded as a sanity check, not as a rate.

---

## 2. Ofgem Consumer Survey 2021 (Engagement report) — what it establishes

**Fetched and parsed 2026-09-03.** Ipsos for Ofgem, n = **4,037** GB energy consumers, **online**,
fieldwork **19 August – 17 September 2021, before the energy crisis**. This is the wave the
`continuous_behavioural_engagement_w2_14.md` §5 lead list named as "not located/fetched" — it is now
fetched, and the CMA 2016 Appendix 9.1 that stood in for it is no longer the only reading.

### 2.1 Self-reported supplier switching, by household attribute

Headline: **27%** of households report having **switched supplier in the past 12 months**
(*"P12M supplier switchers"*).

| cut | subgroup | switched supplier P12M | base |
|---|---|---|---|
| — | **total** | **27%** | 4,037 |
| age | 16–34 | 33% | 780 |
| age | 35–64 | 27% | 2,052 |
| age | 65+ | 24% | 1,205 |
| social grade | ABC1 | 32% | 3,055 |
| social grade | C2DE | 22% | 982 |
| tenure | owner-occupier | 31% | 2,853 |
| tenure | private tenant | 24% | 556 |
| tenure | social tenant | 17% | 585 |
| income | under £16k | 21% | 958 |
| income | £16k+ | 30% | 2,884 |
| financial | in financial difficulty | 23% | 652 |
| financial | not in financial difficulty | 29% | 2,939 |
| technology | low-carbon-technology adopter | 35% | — |

**The dispersion this actually bounds.** Widest ratio between any two published attribute groups:
**33% / 17% = 1.94×** (16–34 vs social tenants). Within a single axis: tenure **1.82×**, social
grade **1.45×**, income **1.43×**, age **1.38×**.

That is the honest published number for quantity **B**, and it is the largest one available. It is
**not** the amplitude the mechanism needs.

### 2.2 The self-report series beside the record

The survey publishes its own *"% P12M supplier switchers"* back to 2014 and prints it against
Ofgem's actual switching counts, captioned *"Levels of supplier switching reflect Ofgem's own
switching data"*:

| year | survey self-report | commons published band |
|---|---|---|
| 2014 | 14% | — |
| 2015 | 13% | — |
| 2016 | 15% | 17.0–17.6% |
| 2017 | 18% | 13.5–14.0% |
| 2018 | 18% | 19.5–20.0% |
| 2019 | 24% | 20.7–21.3% |
| 2020 | 31% | 22.5–23.0% |
| 2021 | 27% | 17.9–18.4% |

Measured against the band midpoints over the six overlapping years: **Spearman rho = +0.70
(n = 6, p = 0.125)** — suggestive, not established, on the same footing as the world's own emergent
ordering. Pearson r = +0.65 (p = 0.158). The survey's own spread is **15–31%**, a ratio of **2.07×**,
against the record's **13.75–22.75%** midpoints, a ratio of **1.65×**: **the self-report over-states
the swing**, in the opposite direction to the world's compression.

Two reasons that comparison cannot be used as a calibration, both from the survey's own footnotes:

1. **The mode changes in 2020**, face-to-face to online, and Ofgem states in terms that *"consumers
   who answer online surveys tend to be more engaged with the market and inclined to switch"* and
   that this *"is likely to explain a large part of the apparent increase between 2019 and 2020"*.
   The series is discontinuous at exactly the point where the swing is largest. Restricting to the
   face-to-face years 2016–2019 leaves n = 4 (rho = +0.63, p = 0.37), which establishes nothing.
2. **The level does not match.** 27% self-reported in 2021 against a published 17.9–18.4%: about
   1.5× over. Group levels in §2.1 therefore cannot be read as absolute annual hazards without a
   calibration the survey does not supply.

### 2.3 The definitional trap, and it is the most important thing in this document

The survey's *engagement* segmentation — the thing the finding hoped would carry a dispersion — is
**defined on the outcome**. Verbatim, from the report's own conventions page:

> *"P12M engaged — switched supplier, tariff, or compared in the past 12 months"*
> *"P12M disengaged — none of the above actions in the past 12 months"*

So a *disengaged* household's supplier-switching rate is **zero by construction**, and an
engaged-vs-disengaged switching ratio taken from this survey is **infinite and meaningless**. Any
multiplier read off the engaged/disengaged split — the exact shape of number a session under time
pressure would reach for, and the exact number the practitioner question in §4 asks about — would be
a **definitional artefact, not a measurement**. The survey's engaged/disengaged cross-breaks
(n = 2,638 / 1,399) are used throughout the report for *attitudes, confidence, barriers and risk
perceptions*, where they are informative, and are never used for switching rate, because there they
cannot be.

**This is the concrete content of "a segment-level dispersion is not a household-level one", and it
is worse than that phrase implies.** It is not merely that the segments are coarse. It is that the
one segmentation named *engagement* is the outcome variable wearing a different name.

### 2.4 The other cuts that look wide and are not usable

The widest spreads in the report are on **tariff type** (fixed **34%** vs standard variable **13%**,
2.6×) and **payment method** (direct debit **31%** vs prepayment **11%**, 2.8×). Both are
**outcome-defined or near-outcome-defined**: being on a fixed tariff in 2021 is very largely *the
result of* having switched, and payment method is entangled with tariff availability. Neither can be
used as a prior household attribute that generates switching. They are quantity **B** contaminated
by the outcome, and are recorded here so the next session does not reach for the biggest number on
the page.

*(The report's standard-credit column could not be read unambiguously from the extracted layout —
its four stacked values reconcile to 100% in more than one assignment — so no standard-credit figure
is quoted. Prepayment, 11%, reconciles uniquely and is quoted.)*

---

## 3. Verdict: the gap stands, with its reason named

**Neither source settles the household-level amplitude of switching response.**

| what was hoped for | what arrived |
|---|---|
| Retail Market Indicators would give a per-fuel series that constrains the household rate | It gives a per-fuel **count**, settles the 1.75× both-fuel conversion, and carries **no household in it at all** |
| The Consumer Survey would give switching by engagement segment, i.e. a dispersion | Its engagement segments are **defined on the switching outcome**, so the dispersion it appears to offer is a tautology |
| Failing that, attribute cuts would bound the dispersion | They do — at **1.94× between the extreme published groups** — but that is a between-group *level* ratio in one cross-section, not a within-household *response* to conditions |

**The strongest true statement available from published evidence:** in a single pre-crisis year,
self-reported annual supplier-switching propensity varied by at most about **1.9×** between the most
and least switch-prone published household groups, on a self-report that over-states the market
level by about 1.5× and over-states the year-to-year swing by about 1.25×.

**Why that does not close the repair.** The compression in §3 of the opening finding is a deficiency
in *spread across years* — the world moves 9.1→19.6 where the record moves 12.5→23.0. A
cross-sectional level ratio between household types says nothing about how far the whole
distribution travels between 2020 and 2022. Substituting the 1.94× into the mechanism as a response
amplitude would be **dividing two numbers whose ratio is not a quantity**, and publishing it would
make an artefact of survey design load-bearing in a figure the site prints.

**So: an honest gap, and the code keeps the per-year table.** `YEAR_LEVEL_ANCHOR` was not edited,
`fit_whole_book` was not touched, and no constant was chosen. The clamp stays visible and declared
rather than being replaced by an invented number, which is the trade CLAUDE.md's knowledge-first
rule makes explicitly.

**What would actually settle it, named so the next attempt does not repeat this one:**

1. A **longitudinal or panel** source that follows the same households across a switching-rate swing
   — not a repeated cross-section. Nothing located this pass does this for GB domestic energy.
2. **Supplier-level external loss rates** by book composition, which would let the between-book
   variance be decomposed. The knowledge map records these as unpublished, and this pass found
   nothing to overturn that.
3. The **practitioner** (§4) — this is the third side of the knowledge rule and it is the cheapest
   of the three.
4. **A structural route that removes the need for the constant**, recommended in §4.

---

## 4. The practitioner question, and the recommendation attached to it

**The question put to the director on NTFY, 2026-09-03:**

> How much more likely is an engaged household to switch supplier than a disengaged one in the same
> year — and does that gap *widen* in a high-switching year, or does the whole population shift
> together?

The second clause is the one that matters, and it is the one no published source above can reach:
it distinguishes a market swing carried by *more households becoming engaged* from one carried by
*already-engaged households acting more often*. The two produce the same market rate and completely
different individual mechanisms — and this project has been burned before by measuring one number
across two populations that turned out to be different experiences.

**The recommendation attached (a bare ask is a defect):**

1. **Do not invent the amplitude, and do not take it from the engaged/disengaged split** — §2.3
   shows that split is the outcome renamed, so a number from it would be false with a citation
   attached, which is worse than no number.
2. **Keep the per-year anchor in place meanwhile**, declared as a clamp with this file as its named
   reason, rather than swapping it for a constant. 2 of 7 in band with a named gap is the honest
   state and it is already recorded as such.
3. **If the trade knowledge is not there either, prefer the structural route to another search**:
   make the household's response amplitude a function of the **savings actually on offer to that
   household**, which the world can already observe, and let dispersion emerge from the price
   distribution rather than from a dispersion constant. That converts an unanchored scalar into a
   mechanism whose inputs are already sourced — and the one-constant sweep in the opening finding's
   §3 is the instrument that would grade it, unchanged.

---

## 5. Sources

- Ofgem, *Retail market indicators* data portal —
  https://www.ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators
  (fetched 2026-09-03; per-fuel monthly switch counts for April and May 2026)
- Ofgem / Ipsos, *Consumer Survey 2021 — Engagement report* —
  https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf
  (fetched and `pdftotext`-parsed 2026-09-03; n = 4,037, fieldwork 19 Aug – 17 Sep 2021)
- Ofgem / ESP Consulting & VaasaETT, *Report on customer switching and disengaged customers*, July
  2018 —
  https://www.ofgem.gov.uk/sites/default/files/docs/2018/07/retail_research_-_report_on_customer_switching_and_disengaged_customers_0.pdf
  (fetched 2026-09-03; **off-subject** — regulatory remedies, not GB switching rates by segment)

**In-repo, followed rather than re-derived:**
`docs/market_research/gb_switching_rate_denominators.md` (the denominator rules and the published
band), `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` (the commons
series), `docs/market_research/continuous_behavioural_engagement_w2_14.md` §3a and §4 item 6 (the
CMA 2016 engagement×price-sensitivity reading and the gap declaration this file now co-locates).
