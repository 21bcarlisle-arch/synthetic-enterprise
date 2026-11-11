# Reading log, part two: published research against our gaps

The second part of `reading_log.md`. Part one covers how Poesys is built. This part covers the
domain: each open GAP is treated as a search question, and the candidates and verdicts are kept
against it. Detailed findings go on the knowledge page that uses them. Themed syntheses become
knowledge-layer pages. This file holds the lists, the verdicts and the absences.

Set up on the director's two steers of 11 Nov
(`docs/staging/advisor/done/DIRECTOR_STEER_GAP_DRIVEN_LITERATURE_SEARCH_AT_TWO_DEPTHS_2026-11-11.md`,
`docs/staging/advisor/done/DIRECTOR_STEER_RECORD_WHERE_RESEARCH_IS_ABSENT_AND_SEARCH_BEYOND_THE_UK_2026-11-11.md`).

## How a gap is worked

**Depth.** There are two, following the director's distinction:
- **Detailed** applies to a gap that sets a constant, a mode share or a world response. The top two or
  three papers are read in full, and their findings, ranges and caveats go on the knowledge page.
- **Aggregated** applies to a theme that only informs our thinking. It is read at abstract level and
  summarised as one short synthesis per theme. An aggregated synthesis says "abstract-level" at the
  top and never sets a constant.

**Just in time.** Candidates are listed for every gap now, because listing is cheap. A gap is read
when its build comes up.

**Evidence grade, by study type and never by citations.** From strongest to weakest:
meta-analysis or randomised trial (RCT), then large observational study (OBS), then modelling
(MOD), then review or opinion (REV / OP). A narrative review is graded REV. A systematic review is
graded as the strongest type it pools.

**Transferability, graded apart from evidence.** Every non-UK source gets a note:
- **P, physics** (yield, heat loss, battery and EV behaviour): transfers fully once climate and stock
  are adjusted for.
- **B, behaviour** (adoption, price response, effort tolerance): transfers partly. Say what differs:
  market design, regulation, climate, housing, income or culture.
- **R, rules, prices, market structure:** UK-specific. A foreign source is an analogue only.

**A non-UK source never sets a GB value** unless its transferability note and the stated adjustment
are given beside it.

**An absence is a finding.** When a search finds little or nothing, the result is recorded as a
finding, not as a failed search. It says what was searched, where, what came closest and why that
falls short (wrong country, period or population; a model rather than evidence; or nothing). This
confirms the gap so the code can carry it as a ranged `None` (K2). It marks where the practitioner
is the only source (K4). And it shows where Poesys could add something nobody has published (M4).

**Where the search runs.** UK sources are searched first: CREDS, UKERC (including its systematic
reviews), SERL, the Energy Systems Catapult, Behavioural Insights Team trials, Ofgem and Citizens
Advice. UK first is where the search starts, not a limit on it. For the scholarly side we use
OpenAlex (`api.openalex.org/works`, which needs no key). We run each query twice: once restricted to
UK-affiliated authors (`authorships.countries:GB`) and once unrestricted, both from 2012 onwards.
Semantic Scholar refused unkeyed requests on 11 Nov (HTTP 429), so it is not used yet. The fetched
lists are documentation only and are never a runtime input (W6).

**Limits of a candidate list.** OpenAlex does not index most grey literature: SERL reports, Ofgem
consumer surveys, Catapult trial reports and BIT write-ups. Until those UK seeds have been searched
directly, any absence below is **provisional**.

## First in line (11 Nov): operating modes, adoption and hassle, carbon definitions

The verdict codes are LISTED (not yet read), ABSTRACT (read at abstract level; claims are
abstract-level) and READ (read in full). Each candidate is given as ID · year · authors' countries ·
grade from the abstract · transferability.

### G1. Operating-mode shares of home batteries, EV charging and heat pumps (depth: detailed, held)

This is the 10 Nov asset steer: "the shares of each mode... are knowledge to establish first". The
build waits behind the exit test, so this gap is listed, not read.

| Candidate | Year · countries | Grade · transferability | Verdict | What it bears on |
|---|---|---|---|---|
| Empirical field evaluation of self-consumption regulation of household batteries (*Energy Policy*, 10.1016/j.enpol.2024.114343) | 2024 · DE | OBS, 947 systems for one year · B/R: the operating mode follows German self-consumption rules | ABSTRACT | The closest thing to a measured mode mix. It shows the mix is set by regulation, so it does not carry to GB as a number |
| Private vs public value of US residential batteries operated for self-consumption (*iScience*, 10.1016/j.isci.2022.104714) | 2022 · US | OBS, metered data on 1,800 customers at 6 utilities · B/R | ABSTRACT | Self-consumption batteries "largely sitting idle on peak days". The mode decides grid value |
| Time-of-use and time-of-export tariffs for home batteries: LV network effects (W2809036477) | 2018 · GB | MOD · UK | LISTED | Tariff-driven mode, modelled rather than observed |
| Evaluation of residential DR trials with smart heat pumps and batteries, Barnsley (*J. Cleaner Prod.*, 10.1016/j.jclepro.2023.136760) | 2023 · GB | OBS, but only 14 dwellings with automated control · UK | ABSTRACT | Automated-control mode in a trial setting. Too small to give a share |
| Demand response with heat pumps: three control options in practice (*BSERT*, 10.1177/01436244221145871) | 2022 · GB | OBS, 3 cases · UK | ABSTRACT | The control options themselves (setpoint lowering and others), not their shares |
| The proof of the pudding is in the heating: field experiment on heat pump flexibility (*Energy Econ.*, 10.1016/j.eneco.2025.108565) | 2025 · BE | RCT, a field experiment (no abstract in OpenAlex) · B | LISTED | Engagement with heat pump flexibility. A read candidate when G1 is built |
| On the ease of being green: the inconvenience of EV charging (*Applied Energy*, 10.1016/j.apenergy.2019.114090) | 2019 · DK, GB | type not known (no abstract) · B | LISTED | The effort cost of charging behaviour. Also bears on G3 |
| The economics of smart EV charging at home: review and agenda (*npj Sust. Mobility*, 10.1038/s44333-026-00105-4) | 2026 · CH | REV, narrative · — | ABSTRACT | Three optimisation logics: market-driven, grid-conscious and prosumer. A frame for the mode list, not shares |
| Addition of heat pump load profiles to GB demand: field trial (W2739454010) | 2017 · GB | OBS, field trial · UK | LISTED | How heat pumps are run in practice (the RHPP data) |

**ABSENCE (provisional): no published measurement of GB operating-mode shares for home batteries.**
- *Searched:* OpenAlex, two battery queries, UK-only and unrestricted, 2012 onwards.
- *Closest:* the German 947-system field study and the US 1,800-customer metered study.
- *Why they fall short:* wrong country, and in both the mode mix follows the local regulation (German
  self-consumption rules, US net metering), so it cannot be carried over as a GB share.
- *Still to search:* SERL, Catapult and Ofgem grey literature, and supplier-published fleet data.
- *If it holds:* the shares stay a ranged GAP, and the question goes to the practitioner with a
  recommendation.

EV charging and heat pump modes have UK field-trial data (Electric Nation, RHPP), but none of it was
found as a mode share.

### G2. Adoption response to advice and support (depth: detailed, held)

This is the 10 Nov persuasion steer, ranked after G1.

| Candidate | Year · countries | Grade · transferability | Verdict | What it bears on |
|---|---|---|---|---|
| The appeal of the Green Deal: homeowners before and after launch (*Energy Policy*, 10.1016/j.enpol.2015.01.015) | 2015 · GB | OBS, repeated measures · UK | ABSTRACT | Whether a support scheme moved awareness and intention among homeowners already considering renovating |
| Energy coaching and "fix team" retrofitting against energy poverty (*ERSS*, 10.1016/j.erss.2024.103807) | 2024 · NL | OBS, ex-post · B: Dutch municipal schemes | ABSTRACT | Advice compared with doing the work. The nearest test of "advice alone" |
| Value-based testimonials as citizen activation (*TCW*, 10.5117/tcw2026.3.003.klos) | 2026 · NL | RCT, online field experiment, n=959 · B | ABSTRACT | **No effect** of value framing, but the outcome was intention to visit a website, not adoption |
| The economic determinants of heat pump adoption (NBER w31344) | 2023 · US | OBS, nationally representative · B/R | ABSTRACT | US heat pump adoption is nearly flat across income, unlike solar and EVs |
| Household heat pump adoption and user behaviours: systematic review (10.1080/14786451.2025.2488174) | 2025 · NL | REV, systematic, 16 studies · B | ABSTRACT | Mixed findings. Expected comfort and performance hinder adoption alongside cost |
| Increasing heat pump adoption: preparing homes in the UK (W4395083941) | 2024 · GB | type not known · UK | LISTED | |
| The economics of heat pumps and the consequences of government policy (*Energy Policy*, 10.1016/j.enpol.2019.111198) | 2019 · GB | type not known (no abstract) · UK | LISTED | RHI-era support |
| Solar rebound: the unintended consequences of subsidies (W2915786677) | 2021 · BE, ES | type not known · B/R | LISTED | |

**ABSENCE (provisional): no GB randomised evidence on whether a supplier's advice changes what a
household adopts.**
- *Searched:* OpenAlex, two advice queries.
- *Closest:* the Dutch ex-post coaching study (observational) and the Dutch online experiment (an
  RCT, but its outcome is intention, not adoption).
- *Why they fall short:* wrong country, and either not randomised or measuring the wrong outcome.
- *Still to search:* BIT and Catapult trials, and Ofgem's evaluations of supplier obligation
  schemes (ECO).

### G3. Hassle tolerance: household effort as a barrier (depth: detailed, held)

M3 measures time "in household minutes per kind of activity", so this gap needs a quantity, not a
narrative.

| Candidate | Year · countries | Grade · transferability | Verdict | What it bears on |
|---|---|---|---|---|
| The Hassle Factor as a psychological barrier to a green home (*J. Consumer Policy*, 10.1007/s10603-019-09410-7) | 2019 · NL | OP / conceptual · B | ABSTRACT | Hassle arises at three journey stages (awareness, consideration, decision), and avoiding it causes delay |
| Maybe tomorrow: how burdens and biases impede energy-efficiency investments (*ERSS*, 10.1016/j.erss.2021.102154) | 2021 · IE | MOD, a theory model and simulation · B | ABSTRACT | Administrative burden "can strongly reduce" grant uptake. Shown with a model, not measured |
| Householders' retrofit decisions: review of the evidence (*J. Building Eng.*, 10.1016/j.jobe.2025.113838) | 2025 · GB, IE | REV, critical review of 164 studies · UK | ABSTRACT | **First to read for G3.** It critiques the evidence base factor by factor |
| Why do homeowners renovate energy efficiently? (*ERSS*, 10.1016/j.erss.2015.03.002) | 2015 · GB | REV · UK | ABSTRACT | Renovation is a home improvement first and an energy decision second |
| Specific barriers and drivers at different stages of upgrade decisions (W2515857616) | 2016 · NO | type not known · B | LISTED | Stage-specific barriers |
| Stop procrastinating, start renovating! (W4401837312) | 2024 · DK | type not known · B | LISTED | Delay as the behaviour |
| Assessing the energy-efficiency gap (Gerarden, Newell and Stavins; W3121579204) | 2017 · US | REV · B | LISTED | The economics framing of hidden costs |

**ABSENCE (provisional): no published measure of hassle as a quantity.**
- *What is missing:* minutes of household effort, or a stated tolerance, per measure.
- *Searched:* OpenAlex, three queries. A demand-response "fatigue" query returned off-topic results
  (occupational fatigue).
- *Closest:* hassle is conceptual in the Dutch paper and modelled in the Irish one.
- *Why they fall short:* no unit and no measurement.
- *Where Poesys could add something:* M3's minutes may be the first quantity anyone defines here (M4).

### G4. Carbon definitions: average or marginal, direct or lifecycle, and how imports count (depth: aggregated, plus the carbon steer)

The carbon steer of 11 Nov asks for "the published debate summarised, not hidden". These candidates
feed that summary. The Ember check and the Electricity Maps reading are the steer's own items, logged
here on 11 Nov with their verdicts.

| Candidate | Year · countries | Grade · transferability | Verdict | What it bears on |
|---|---|---|---|---|
| Marginal GHG displacement of wind power in Great Britain (*Energy Policy*, 10.1016/j.enpol.2016.11.012) | 2016 · GB | OBS, empirical, 2009–2014 · UK | ABSTRACT | Displacement is "approximated as the average... despite an acknowledgement that wind will actually displace only the generators operating on the margin". GB marginal factors from historical data |
| Long-run marginal CO2 emissions factors in national electricity systems (Hawkes; *Applied Energy*, 10.1016/j.apenergy.2014.03.060) | 2014 · GB | MOD · UK | ABSTRACT | Short-run and long-run marginal factors differ, and an intervention's effect depends on which is meant |
| Real-time carbon accounting for European electricity markets (*Energy Strategy Rev.*, 10.1016/j.esr.2019.100367) | 2019 · 27 European countries incl. GB | MOD on real 2017 hourly data (flow tracing) · P | READ (supp. Tables 4–5, 11 Nov) | GB 346 produced against 349 consumed kgCO2eq/MWh, **+0.9%**. Import factors from France run 9% below its average and from the Netherlands 19% above. That settles item 3 of the carbon steer as "small": household_carbon §1a |
| Ember yearly electricity data and *Methodology v1.6* (ember-energy.org/data/yearly-electricity-data/), CC-BY-4.0 | 2026 release · UK | Published statistics, lifecycle CO2e, gross, generation-only · UK | READ, and checked by year | **A second independent view: the check, not a feed.** On a matched basis it agrees within a few percent in 2016–18, and runs 9–25% above ours by 2023–25. The leading cause is about 43 TWh a year of thermal generation NESO's mix does not count. household_carbon §1b |
| Electricity Maps: methodology, `electricitymaps-contrib` (AGPL-3.0), and the marginal publications | 2018–2025 · global | Practitioner method · P | READ (pages; their API terms returned 403) | **Verdict: learn from the method; no data feed.** It is consumption-based, flow-traced and lifecycle-by-default, and validated against Ember, the IEA and Eurostat. The marginal withdrawal is **verified**: "marginal signals come with major limitations, such as the incompatibility with regulation, which is why we no longer offer marginal signals" ("Our latest research on Marginal emission factors", 13 May 2024, updated 14 Jan 2025). Paid plans start at €2,500 a year per country. What the free tier allows was not established. Their forecast method is not published |
| Carbon intensity of electricity produced and used in Europe (*Applied Energy*, 10.1016/j.apenergy.2021.117901) | 2021 · BE, DE, IT, NL | MOD · P/R | ABSTRACT | Produced versus used intensity by country |
| Price-based demand response and carbon emissions in European markets (*Applied Energy*, 10.1016/j.apenergy.2021.117040) | 2021 · DE, IE, US | MOD, merit-order MEFs for 20 countries · P/R | ABSTRACT | Marginal and average factors can give opposite signs for the same load shift |
| Accounting carbon emissions from electricity generation: review of emission-factor methods (*Applied Energy*, 10.1016/j.apenergy.2025.125992) | 2025 · IT | REV with an empirical comparison · R | ABSTRACT | The choice of method changes the CO2 estimate "significantly" |
| Spatial and temporal heterogeneity of marginal emissions (Graff Zivin et al.; W3123846525) | 2014 · US | OBS · P/R | LISTED | The classic US marginal-factor paper |

**Not an absence.** This literature is rich. The open question is which definition the customer's
figure uses and why, and that is a choice to state, not a fact to find. One point runs against our
own thesis (F11): the GB evidence that wind displaces the marginal plant rather than the average
says that "carbon saved by shifting", measured on average intensity, is a definition that needs
defending, not a neutral default.

## The steer's GLM question: do our world checks test against data held back from fitting?

First pass, 11 Nov. It is mixed, and this is not yet a census of every world check.

- **Held out:**
  - The grid-carbon future (`sim/grid_carbon_future.py`, `HELD_OUT_YEAR = 2025`) chose its model and
    regime rule by fitting on earlier years and grading on 2025.
  - The price engine's residual-demand axis was chosen by year-held-out error (the comment at
    `sim/price_engine.py:206`).
- **In-sample, by construction:**
  - The world's departure level is fitted to the published switching band
    (`tools/fit_year_level_anchor.py`).
  - Its acceptance test,
    `tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band`,
    grades it against that same band.
  - That is legitimate as calibration, because inside 2016–2025 the level is ground truth (the third
    wall). It is not validation, and the knowledge map's own row says so ("in band in 6 of 8 IS NOT
    A VALIDATION RESULT").
- **Still to do:** a census of every fitted world quantity and the data it is graded against, with
  each marked held-out, in-sample or ungraded. It is listed here, not built.

## The queue: gaps with no candidates listed yet

These GAPs are stated on the published knowledge pages (`site/data/knowledge_topics.json`) and in
`knowledge_map.md`. Each needs its search question and candidate list. Most are GB rules or
supplier operations (grade R), where scholarly search will find little, and the absence should be
recorded as such.

- acquisition and retention economics: whether a retention offer below cost pays for itself; what
  the standing charge costs to serve
- what a customer is worth: the discount rate (a placeholder of 8%)
- who lives where: the direct-debit payment gap (selection or cause)
- the first-year blind spot: the split between fixed and variable direct debit
- payments and direct debit: refund speed (the licence names no number of days)
- the customer-needs framework: willingness to pay by band
- unbilled energy, back-billing and payments: the reaction GAPs in each pain-point table
- knowledge map: operational carbon (E5), bad-debt write-off against recovery, and the 2016–2018
  active-renewal split

The **Z.ai entry** (11 Nov) is software practice, so it is in part one.
