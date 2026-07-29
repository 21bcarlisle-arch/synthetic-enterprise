# Continuous Behavioural Engagement — Market Research (W2_14)

**Scope note (epistemic-wall boundary):** This document is the DISCOVER input for
`W2_14_continuous_behavioural_engagement_model`. It concerns ONLY the real-world shape of, and
transitions in, UK domestic energy-consumer engagement/switching propensity — external published
evidence, read blind to `simulation/**`. `simulation/household_segments.py` was **not read** to
produce this document; everything said about it comes from the task brief supplied to this
agent, not from inspecting the code. The director-R13-ratified population shares
(ACTIVE 0.45 / PASSIVE 0.35 / DISENGAGED 0.20) are **not re-examined or challenged** here — per
the brief, that ruling stands. This document addresses the three separate questions the brief
asks: (1) is engagement a distribution or three boxes, (2) can households move between states and
by how much, (3) do the two registered fusion hypotheses (engagement×price-sensitivity,
U-shape-by-affluence) hold up against real data. Any code-seam / build-time decision belongs to a
separate agent authorized to read `simulation/**` and write `docs/design/**`.

**Method note on this session's search environment:** Ofgem's own website
(`ofgem.gov.uk/energy-data-and-research/data-portal/retail-market-indicators`) renders its
switching-rate and stock-share charts client-side via JavaScript (everviz/Highcharts embeds with
no discoverable static JSON/CSV endpoint in the served HTML) — this session's tool access is
`curl`/`pdftotext` only, no headless browser, so the interactive switching-rate time series could
**not** be fetched this session despite several attempts (direct fetch, search-engine routes, a
House of Commons Library briefing route — Cloudflare-challenge-blocked). This is stated plainly
rather than papered over; see §5 UNFETCHED LEADS. What COULD be fetched — and turned out to be
unusually rich — was the CMA Energy Market Investigation's own primary survey and final-report
text, downloaded and parsed directly with `pdftotext`/`pdftoppm` this session (not a secondary
citation of the CMA report).

---

## §1 Is engagement a DISTRIBUTION or three boxes?

**domain**: churn
**assumption_tested**: Does published UK evidence describe consumer engagement as a small number
of discrete boxes (as the SIM's ACTIVE/PASSIVE/DISENGAGED archetype does), or as a continuous
spectrum / a published multi-segment (>3-bin) typology?
**benchmark_value**: The CMA Energy Market Investigation **Final Report** (24 June 2016), §9.126–
9.131 and **Figure 9.6 "Stages of engagement and barriers to engagement in domestic retail energy
markets"**, publishes an explicit **4-STAGE FUNNEL**, fetched and visually confirmed this session
(page 480 of the report, rendered to PNG and read directly):
  - **Stage 1** — Awareness of ability to switch / Consider switching (barrier: fundamental
    characteristics of energy consumption — homogeneity, traditional meters)
  - **Stage 2** — Access information / Assess information (barrier: non-use of internet,
    complexity, non-use of PCWs/third-party intermediaries)
  - **Stage 3** — Act on information (barrier: actual and perceived barriers to switching)
  - **Stage 4** — Fully engaged (no further barrier listed — end state)

  Population sizes are given for Stage 1 only, not for stages 2–4 individually: **34%** of
  respondents "had never considered switching supplier"; **36%** "either did not think it was
  possible or did not know if it was possible" to change tariff/payment method/supplier; **56%**
  "had either never switched supplier, did not know it was possible, or did not know if they had
  done so" (CMA Final Report §9.128, quoting Appendix 9.1's own survey results). The underlying
  survey (**Appendix 9.1: CMA domestic customer survey results**, GfK NOP telephone survey,
  n=6,999, fieldwork 2014/15) reports a **graded funnel of continuous, non-identical engagement
  measures**, not a clean 3-way split: 89% aware switching is possible → 66% have considered
  switching → 40% have shopped around ever (36% in last 3yrs) → 44% have switched ever (25% in
  last 3yrs, 13% in last yr) → 45% likely to switch in next 3yrs. A direct text search of this
  session's three fetched CMA documents (final report, Appendix 9.1, Appendix 9.2) for "segment",
  "typology", "index of engagement" and "engagement score" returned **zero matches** — no
  composite continuous engagement INDEX and no named multi-segment population TYPOLOGY (beyond
  the qualitative 4-stage funnel above) was found in these primary sources.
**confidence**: H for the funnel's existence and the Stage-1 percentages (quoted directly from
the primary CMA PDF, fetched and rendered this session); M for the absence-of-index/typology
claim (a real, direct text search across the three fetched CMA PDFs found nothing, but this is
absence-of-evidence within this session's specific fetched document set, not an exhaustive
literature search of every CMA/Ofgem publication since 2016).
**source**: CMA "Energy Market Investigation: Final Report" (24 June 2016),
`final-report-energy-market-investigation.pdf`, §9.126–9.131 and Figure 9.6 (p.480),
assets.publishing.service.gov.uk/media/5773de34e5274a0da3000113, fetched and `pdftotext`/
`pdftoppm`-rendered live 2026-07-29; CMA "Appendix 9.1: CMA domestic customer survey results",
assets.publishing.service.gov.uk/media/576bcbbc40f0b652dd0000b0, same fetch date.
**date**: 2026-07-29
**finding**: Real UK regulatory evidence supports a **published, official, ANCHORED >3-bin
framework** — a 4-stage engagement funnel — which directly confirms the brief's premise that a
finer-grained typology than 3 boxes exists in the literature. But it does NOT support treating
engagement as a single continuous scalar index either: CMA's own operationalisation is a set of
**five-plus correlated but non-identical binary/ordinal measures** (awareness, consideration,
shopping, switching-ever, switching-recently, switching-intent), each with its own population
share, not one number per household. **ANCHORED, qualified.** For the SIM's 3-archetype model:
the existing hard **DISENGAGED=0.20** tail sits close in both direction and rough size to CMA's
own Stage-1 "never considered switching" 34% and the stricter "never switched, never switched
tariff, unlikely to switch in next 3yrs" 22% triple-negative measure found separately in Appendix
9.1 (see §1a below) — i.e. **a genuinely hard-disengaged tail of ~20-25% of the population is a
real, twice-independently-observed feature of the GB market, not an artefact of the SIM's own
design.** What the CMA data does NOT support is a clean binary split of the REMAINING ~75-80% into
two further boxes (ACTIVE vs PASSIVE) — that remainder is graded/funnel-shaped (66% "considered"
→ 40% "shopped" → 25% "switched in 3yrs" → 13% "switched in 1yr"), i.e. the ACTIVE/PASSIVE boundary
in the SIM is a reasonable coarse discretisation of a genuinely continuous funnel, not itself a
directly-observed natural break in the data.

### §1a Independent cross-validation of the ~20% hard-disengaged tail (unplanned but load-bearing finding)

**domain**: churn
**assumption_tested**: Is the R13-ratified DISENGAGED share of 0.20 (anchored to Ofgem RMI
October-2025 stock data — 20.3% held on default tariff 3+ years) corroborated by any
INDEPENDENT, methodologically-unrelated source measured at a different point in time?
**benchmark_value**: CMA Appendix 9.1 (survey wave 2014/15, GfK NOP telephone survey n=6,999),
paragraph 5(h): **"22% of respondents have never switched supplier, never switched tariff with
their existing supplier and are unlikely to consider switching in the next three years"** — a
triple-negative "hard disengaged" definition, constructed from self-reported survey behaviour,
9+ years before and via a completely different method (survey self-report vs Ofgem's own
administrative account-tenure billing data) from the Ofgem RMI Oct-2025 20.3% figure already
cited in `ASSUMPTIONS.md`.
**confidence**: M — two independent methods (self-report survey vs administrative tenure data),
two different points in time (2014/15 vs 2025), same rough magnitude (22% vs 20.3%); not
H because the two definitions are not identical (CMA's is a 3-way behavioural AND, Ofgem's is a
single tenure-length threshold) and no formal statistical reconciliation was attempted.
**source**: CMA Appendix 9.1, paragraph 5(h), p.A9.1-3, fetched 2026-07-29 (see §1 for full
citation); cross-referenced against `ASSUMPTIONS.md`'s existing Ofgem RMI Oct-2025 row (fetched
2026-07-08/2026-07-22, already in the repo, not re-fetched this session).
**date**: 2026-07-29
**finding**: This is **corroborating, not new, evidence for the ALREADY-RATIFIED 0.20 share** —
per the brief, this document does not propose changing it. It is recorded because it is a
genuinely independent second data point (a different survey house, a different decade, a
different measurement method) landing within ~2 percentage points of the ratified figure, which
is a materially stronger form of validation than a single source repeated. **No action
recommended — R13 stands.**

---

## §2 Transitions — can a household move between engagement states, and by how much?

### §2a Price shock (2021-22 crisis) — switching-rate collapse and post-crisis persistence

**domain**: churn
**assumption_tested**: Did the published UK domestic switching-rate series show a collapse during
the 2021-22 energy crisis and a recovery in 2023-2025, and — critically — did households forced
onto SVT in 2022 disproportionately STAY there once fixed deals returned (a "scarring"/persistent
disengagement effect), or did they return to shopping around at pre-crisis rates?
**benchmark_value**: **NOT FETCHED this session at the annual-series level.** Ofgem's own
"Retail market indicators" data portal (the primary, most authoritative source for this exact
series) renders its switching charts via client-side JavaScript with no discoverable static
data endpoint in the served HTML (confirmed by direct inspection of the fetched page source,
2026-07-29) — this session's tooling (`curl`, no headless browser) cannot execute that
JavaScript. A House of Commons Library briefing that likely compiles this exact series
(`commonslibrary.parliament.uk`) returned a Cloudflare bot-challenge page on every attempted
route (direct fetch and a Wayback Machine mirror attempt, the latter also landing on an
unrelated cached briefing). General web search (DuckDuckGo, Bing) returned JS-shell pages with
no usable result links via plain `curl`. What IS anchored, and is directly relevant background
even though it is not the switching-rate series itself: the **SUPPLY-SIDE mechanism** for the
2022 collapse is independently well-evidenced in this repo's own prior research
(`docs/market_research/scenario_spine_and_friction_anchors_2026-07-23.md`, Ofgem price-cap letter
26 Aug 2022 fetched live: wholesale-cost cap component +80% in a single quarterly reset) — the
market's own fixed-tariff withdrawal in 2022 (well documented qualitatively in the general press
and in this repo's existing NBP/SSP crisis anchors) is a supply-side collapse of what there was
TO switch to, structurally distinct from a demand-side fall in household willingness to shop —
exactly the distinction the brief asks to be kept honest. **This distinction is stated but not
independently re-quantified this session.**
**confidence**: n/a — explicit non-finding at the quantitative annual-series level.
**source**: Attempted `ofgem.gov.uk/energy-data-and-research/data-portal/retail-market-indicators`
(JS-rendered, no static data found), `commonslibrary.parliament.uk/research-briefings/cbp-8462/`
(wrong briefing number, and separately Cloudflare-blocked on retry), `html.duckduckgo.com`,
`www.bing.com` (both returned non-content JS shells to a plain `curl` fetch) — all attempted live
2026-07-29.
**date**: 2026-07-29
**finding**: **Gap, not invented.** The single highest-value figure the brief asks for — the
magnitude of post-2022 "scarring" (persistent SVT residency after fixed deals returned in
2023-24 vs a return to pre-crisis shopping rates) — is **UNFETCHED and must be sampled from a
distribution (R10), not fixed as a point estimate**, pending a future session with browser-level
fetch capability against the Ofgem RMI portal, or a direct data-request/FOI-style approach to
Ofgem's underlying switching dataset. Named follow-up leads in §5.

### §2b Bad service episode / complaint → subsequent switching propensity

**domain**: churn
**assumption_tested**: Is there UK evidence linking a complaint or service-failure episode to a
subsequent rise in switching propensity for the affected household?
**benchmark_value**: **NOT FOUND this session.** Citizens Advice's own site returned a 404 for a
guessed URL and an empty result set for a site search on "energy switching complaint"; no other
source was attempted this session for this specific sub-question given time constraints.
**confidence**: n/a — explicit non-finding.
**source**: `citizensadvice.org.uk` (404 + empty search, attempted live 2026-07-29).
**date**: 2026-07-29
**finding**: **Gap.** UNANCHORED — must be sampled from a distribution if built. Named follow-up
leads (Ofgem complaints-data publications, Citizens Advice supplier star ratings methodology
page, Ombudsman Services energy annual report) in §5 — none of these three specific documents
were located or fetched this session, this is a genuinely unexplored lead, not a checked-and-
empty result for those particular publications.

### §2c Home move as an engagement/switching trigger

**domain**: churn
**assumption_tested**: Does CMA/Ofgem evidence support "home movers" as a distinct
switching/engagement trigger population?
**benchmark_value**: **Qualitatively confirmed, quantitatively redacted.** CMA Final Report
Tables 8.5 and 8.6 (domestic customer acquisitions by channel, Jan 2014–Jun 2015) list **"Home
movers"** as an explicit, named, standalone acquisition channel alongside face-to-face,
telesales, own website, PCWs, cashback websites, collective switches, white-labels/partnerships
and win-back/recovery — for each of the Six Large Energy Firms. However, every cell in both
tables is redacted (`[]`) as confidential commercial data; no numeric percentage for the
home-movers channel, for any supplier, survived to the published version. §8.161's footnote
additionally confirms E.ON's home-moves channel specifically included acquisitions from
relationships with letting agents, i.e. the industry itself treats a home move as a distinct,
actively-targeted acquisition moment.
**confidence**: L — the CHANNEL's existence and industry recognition is H (directly quoted from
primary source, table structure + explicit footnote), but the MAGNITUDE (what fraction of
acquisitions, or what elevated switching probability, home-moving confers) is entirely redacted
in the only primary source located this session, so the quantitative claim is L/unanchored.
**source**: CMA Final Report, Tables 8.5 and 8.6, §8.160–8.161, p.389-390, fetched and
`pdftotext`-parsed live 2026-07-29 (same PDF as §1).
**date**: 2026-07-29
**finding**: A real UK regulator's own market-investigation data structure treats home-moving as
a genuine, distinct trigger channel — directionally supports the brief's causal-sketch premise —
but the actual elevated-engagement magnitude is **UNANCHORED (R10)**; no substitute unredacted
source was located this session (see §5 for a named follow-up: Ofgem's deemed-contract price
publications, which set punitively high deemed rates specifically to discourage prolonged
non-engagement after a move, is an adjacent regulatory-design signal that a move DOES typically
trigger rapid re-engagement, but this is an inferred policy-design rationale, not a directly
measured switching-rate uplift).

### §2d Supplier failure / SoLR involuntary transfer → subsequent engagement

**domain**: churn
**assumption_tested**: How many domestic customers were involuntarily moved via the Supplier of
Last Resort (SoLR) process during the 2021-22 supplier-failure wave, and did that forced move
make them more or less engaged afterwards?
**benchmark_value**: **Headcount ANCHORED, post-move engagement effect UNFETCHED.** National
Audit Office, "The energy supplier market" (March 2022), §1.13/2.3: **"Since July 2021, Ofgem has
transferred nearly 2.4 million customers of 28 failed energy suppliers to alternative providers
through the SOLR process, without any interruption to their energy supply"** — for one failed
supplier alone (Bulb Energy) this covered ~1.6 million customers, moved instead via a Special
Administration Regime rather than a standard SoLR. This 2.4m figure directly corroborates the
brief's stated "~2.4m customers" premise from a primary, fetched source (not merely re-asserting
the brief's own number back). The NAO report was searched directly for any subsequent-engagement
language ("after transfer", "switch away", "remained with", "stayed with") — **zero matches** —
the report covers cost/process/governance of the SoLR mechanism, not the transferred customers'
subsequent switching behaviour.
**confidence**: H for the 2.4m headcount (primary NAO source, direct quote); n/a (explicit
non-finding) for the post-transfer engagement DIRECTION and magnitude.
**source**: National Audit Office, "The energy supplier market" (HC 1112, March 2022),
nao.org.uk/wp-content/uploads/2022/03/The-energy-supplier-market.pdf, §1.13/2.3, fetched and
`pdftotext`-parsed live 2026-07-29.
**date**: 2026-07-29
**finding**: The headcount is now H-confidence ANCHORED (previously the brief's own stated
figure, now independently confirmed against a primary NAO source rather than taken on trust).
The DIRECTION of the post-transfer engagement effect (did being auto-moved onto a SoLR's
"deemed"/default-equivalent tariff make people MORE likely to then actively shop, having been
forced to notice their supplier situation — or did it just add another population to the
already-large SVT/default stock, indistinguishable from ordinary disengagement) is **genuinely
unfetched and unresolved this session — R10, must be sampled from a distribution if a build wants
this as a distinct transition trigger**, not asserted in either direction. Named follow-up in §5.

---

## §3 The two registered fusion hypotheses

### §3a engagement × price_sensitivity

**domain**: churn
**assumption_tested**: Is a more-engaged household also more price-elastic (i.e. does published
UK evidence support a positive correlation between engagement and price-sensitivity, as the SIM's
registered coupling hypothesises)?
**benchmark_value**: CMA Appendix 9.1, paragraphs 18(a) and 21-22: price/cost/tariff/rate is
cited as important by **81%** of ALL respondents (the population baseline), but rises to **93%**
among those who have shopped around in the last year and **93%** among those who switched in the
last year — i.e. the MORE engaged subgroup is measurably MORE likely to name price as their
driver (81% → 93%, a 12-percentage-point gap between the whole population and its most-engaged
tail). Separately, of those who DID switch in the last three years, 83% cited cost/tariff-related
reasons for going ahead (73% specifically "cheaper tariff"). CMA final-report §9.142-9.143
independently frames this as a structural feature of the market: "product homogeneity means that
price should be the most important consideration" — engagement and price-sensitivity are treated
by the CMA as causally LINKED through the homogeneous-good mechanism, not independent traits.
**confidence**: M — the 81%→93% gap is a direct, quoted, primary-source finding (H for the raw
numbers); the causal LINK (does engagement CAUSE price-sensitivity, or does the underlying trait
generate both, as CMA's own homogeneous-good argument implies) is the CMA's own interpretive
argument, not an experimentally isolated effect, hence M overall.
**source**: CMA Appendix 9.1, §18(a) and §21-22, p.A9.1-5/6; CMA Final Report §9.142-9.143,
p.484-485, both fetched and `pdftotext`-parsed live 2026-07-29 (same PDFs as §1/§2).
**date**: 2026-07-29
**finding**: **SUPPORTED, direction confirmed.** Real UK evidence backs a positive
engagement↔price-sensitivity coupling — more-engaged households are measurably (not just
plausibly) more likely to name price as their driver and their reason for acting. This is a
reasonable coupling to keep if/when built, magnitude R10 (the 81%→93% gap is real but is a
"% citing price as important" measure, not a calibrated price-elasticity coefficient — converting
it into an actual elasticity multiplier is a build-time modelling choice with no direct anchor).

### §3b U-shape by affluence

**domain**: churn
**assumption_tested**: Is engagement LOW at both ends of the income/affluence distribution
(low-income: access/capacity/digital-exclusion barriers; high-income: low salience/doesn't care)
and HIGHEST in the middle, as the registered fusion hypothesis proposes?
**benchmark_value**: CMA Appendix 9.1 gives extensive income cross-tabs (income bands: under
£18,000 / £18,000–£36,000 / over £36,000, the CMA's own banding, self-reported, n=6,999). Findings
across multiple independent measures, all pointing the same direction:
  - §7(a)/§815: household incomes **under £18,000** are named as one of the characteristic groups
    MORE likely to have never considered switching, less likely to have shopped around/switched,
    less likely to consider switching in future — **LOW-INCOME arm supports the hypothesis
    (lower engagement).**
  - §272/§5522 ("Respondents with independent suppliers"): the ~7.5% of respondents with an
    INDEPENDENT (non-Six-Large-Firm) supplier — CMA's own proxy for an engaged/switched
    population — are **"more likely to... be on a higher household income; be younger"** than
    those who are not. This is the opposite of the hypothesis at the top end: the most-engaged
    subgroup skews HIGHER income, not middle-income.
  - §6143 and §6259: on the specific attitude statements "there are no real price differences
    between suppliers" and "I worry switching would go wrong" — respondents with **incomes above
    £36,000/yr are LESS likely to agree** with both disengagement-coded statements (43% vs a
    higher rate for lower bands; 39% vs 61% for under-£18,000) — i.e. engagement/confidence rises
    monotonically with income through the CMA's own top-measured band.
  - Age is a SEPARATE demographic axis in the same data, also correlated with lower engagement at
    65+ (§7(a), §24: 65+ over-represented among those satisfied-without-shopping, no-internet-
    access, PSR-registered) — but age and income move in the SAME direction here (both push
    toward disengagement at the "older/lower-income" end), they do NOT form two opposite arms of
    a single affluence U-shape. There is no independent evidence in this survey of a downturn in
    engagement specifically AT THE TOP of the income scale.
**confidence**: M — multiple independent cross-tabs within one primary, large-sample (n=6,999)
survey all point the same way (H for each individual quoted figure), but the CMA's own top income
band is "£36,000 or more" (a 2014/15-era band, not further disaggregated) — genuinely
ultra-high-income/high-net-worth engagement is **UNTESTED** in this data, so "REFUTED at the very
top of the real distribution" cannot be claimed with full confidence, only "refuted within the
measured range."
**source**: CMA Appendix 9.1, §7(a)/§815 (p.A9.1-3), §272/§5522 (p.A9.1-101), §6143/§6259
(p.A9.1-114), fetched and `pdftotext`-parsed live 2026-07-29 (same PDF as §1/§2).
**date**: 2026-07-29
**finding**: **NOT SUPPORTED as a U-shape within the CMA's measured income range — REFUTED at the
stated form.** The real relationship in this primary source is **monotonically increasing
engagement with income** (low-income → less engaged; high-income → more engaged, all the way to
the top surveyed band), not U-shaped. The LOW-income arm of the hypothesis is directionally
correct (low-income households ARE less engaged — access/capacity/digital-exclusion barriers are
directly evidenced: no-internet-access, PSR registration, social-rented housing, disability all
independently correlate with lower engagement in the same direction as low income). The
HIGH-income arm is directionally WRONG in this data — there is no "doesn't care enough to
bother" salience effect visible at £36,000+; if anything the opposite (higher income correlates
with MORE engagement, plausibly via correlated traits — higher education, home ownership,
younger age, higher digital confidence — that CMA's own cross-tabs show cluster together). **A
build should NOT bake in a symmetric U-shape by income/affluence on this evidence** — the
honest real-world shape (within the measured £0–£36,000+ range) is monotonic, with a genuinely
untested possibility of a downturn recurring only at incomes far above what this 2014/15 survey's
top band captured (a plausible but entirely UNTESTED extension, **UNANCHORED, R10** if a build
wants to represent it).

---

## §4 What stays R10

Every quantity below has **no published anchor found this session** and must be sampled from a
distribution rather than fixed as a point estimate in any future build, per R10:

1. **The exact per-year magnitude of the 2022 switching-rate collapse** and the 2023-2025
   recovery trajectory (annual switching-rate series, §2a) — genuinely unfetched, not merely
   unconfirmed.
2. **The persistence/"scarring" rate**: what fraction of households forced onto SVT/default in
   2022 remained there through 2023-24 once fixed deals returned, vs the fraction that resumed
   pre-crisis-rate shopping — the single highest-value unanchored number in this brief.
3. **Complaint/service-failure → switching-propensity uplift** (§2b) — no source found at all
   this session, direction and magnitude both unanchored.
4. **Home-move → switching-propensity uplift magnitude** (§2c) — channel existence is real
   (CMA-confirmed), the magnitude is redacted in the only source found.
5. **SoLR-transfer → subsequent engagement direction and magnitude** (§2d) — the 2.4m headcount is
   anchored; what happens to those customers' engagement AFTER the forced move is not.
6. **Engagement × price-sensitivity as a calibrated ELASTICITY multiplier** (§3a) — the
   directional coupling is supported (81%→93%), but converting "% citing price as important" into
   an elasticity coefficient is an unanchored modelling choice.
7. **Any engagement effect at incomes materially above the CMA's ~2014/15 "£36,000+" top band**
   (§3b) — genuinely untested territory, not evidenced either for or against a downturn.
8. **Per-stage (2/3/4) population shares in the CMA's own 4-stage funnel** (§1) — only Stage 1's
   share is published; Stages 2-4's relative sizes are not quantified anywhere located this
   session.

---

## §5 Unfetched leads (named, for a future pass)

- **Ofgem "Retail market indicators" switching-rate chart** — JS-rendered, needs a headless
  browser (Playwright) or a direct Ofgem data-request, not a plain `curl` fetch.
- **House of Commons Library briefing on domestic energy switching statistics** — attempted
  `commonslibrary.parliament.uk/research-briefings/cbp-8462/` (wrong document — turned out to be
  an unrelated unemployment-benefits briefing per its cached title) and hit a live Cloudflare
  bot-challenge on retry; the CORRECT briefing number was not identified this session. A DESNZ
  Public Attitudes Tracker footnote (Summer 2025 wave, "Energy Bills and Tariffs" report, fetched
  this session) cites `commonslibrary.parliament.uk/research-briefings/cbp-9491/` as its own
  domestic-energy-price-changes reference — a real, fetched citation, worth trying first in a
  future pass (not yet itself fetched this session).
- **Ofgem Consumer Survey (annual, 2017-2025 waves)** — not located/fetched this session; the CMA
  2016 survey (Appendix 9.1) was used instead as it was directly reachable, but it predates the
  2021-22 crisis entirely and is now a 2014/15-vintage data point.
- **Citizens Advice supplier star ratings / switching-after-complaint research** — site returned
  404/empty search this session; not found via the routes tried.
- **Ombudsman Services energy annual report** — not attempted this session (named as a lead only).
- **DESNZ Public Attitudes Tracker "Energy Bills and Tariffs" wave-on-wave time series** (the
  underlying `.xlsx` time-series file linked from the Summer-2025 wave page was identified but not
  downloaded/parsed this session — it may contain a switching-intent or tariff-shopping question
  tracked over multiple waves 2022-2025, which would directly speak to §2a; genuinely unexplored,
  not checked-and-empty).
- **Ofgem deemed-contract price-setting rationale documents** — an adjacent regulatory-design
  signal for §2c (home movers), not itself fetched this session.

**No simulation code was read or touched to produce this document.**
