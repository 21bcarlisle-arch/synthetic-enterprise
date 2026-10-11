**Knowledge:** home-moves

# How far a GB household moves, and what its new home uses

*Written 2026-10-10 to support a "move with us" supplier offer: to honestly supply a departing
customer at their destination, the world needs a destination region (for the regional tariff and
the weather cell) and a destination demand. Read-only market research; nothing here touches
`sim/`, `simulation/`, `company/` or `saas/`. Companion to `docs/market_research/home_moves.md`,
which this page does not repeat (move rates by tenure, the deemed-contract mechanics, the licence
clock). `**Knowledge:** home-moves` matches that page's topic.*

---

## 1. The three shares: same local authority, same region, cross region

**The two published series answer different questions, and neither alone answers all three parts
of the question.**

### 1a. Same local authority — NOT ESTABLISHED at GB level

ONS's internal migration series (the only GB-wide administrative series on this) **excludes moves
within a single local authority by definition**: "Internal migration is defined as residential
moves between local authorities and regions in England and Wales... It excludes moves within a
single local authority" (ONS, *Internal migration by local authorities in England and Wales, year
ending June 2015* — the series' last narrative bulletin; the within-LA exclusion is stated as a
standing methodological choice, not specific to that year). No GB administrative series was found
in this pass that sizes the same-LA share of all moves directly. **This is a genuine gap, not a
number to infer confidently**; §1c gives the one bound that does follow logically.

### 1b/1c. Same region vs cross region, among moves that change local authority — DERIVED, ESTABLISHED inputs

ONS publishes, alongside the internal migration series, annual origin-destination matrices at both
local-authority and region level: *Internal migration between English and Welsh local authorities,
Scotland and Northern Ireland, square matrix* (dataset `IM...-T7`) and *Internal migration between
English regions, Wales, Scotland and Northern Ireland, square matrix* (dataset `IM...-T8`), both
released 25 June 2021 for the year ending June 2020 (the last published matrix edition found; the
series ran YE2012–YE2020). "Region" here means the 9 English Government Office Regions plus Wales,
Scotland and Northern Ireland as whole units — **12 areas, not the 14 GB electricity distribution
regions** (§2).

Reading the two matrices for year ending June 2020 (own computation from the published cell
values, cross-checked against the workbook's own row/column totals):

| Quantity | Value | Source |
|---|---|---|
| Total moves between different local authorities, UK-wide (Scotland/NI as single units) | **3,093,603** | `IM2020-T7b`, grand total cell |
| Of which, moves that also cross a region boundary | **1,488,323** (48.1%) | `IM2020-T8`, sum of all off-diagonal region cells, cross-checked against the table's own printed row totals (sums to 1,488,329, a 6-move rounding difference) |
| Of which, moves that stay within the same region but change local authority | **1,605,280** (51.9%) | derived: 3,093,603 − 1,488,323 |

**So among GB residents who move house and change local authority, just over half (DERIVED,
51.9%, YE June 2020) stay within the same one of the 12 ONS regions, and just under half (48.1%)
cross a regional boundary.** This is one year; the method and the shape (an only-just majority
staying in-region) is plausible as stable given the regions are large (each covers many LAs), but
no multi-year series was pulled to confirm stability across 2016–2025, so treat the exact split as
year-specific and the shape as the more durable fact. **Status: DERIVED** (arithmetic on two
ESTABLISHED, exactly-sourced ONS tables).

### The one honest bound across all three

Every local authority sits inside exactly one region, so a move that stays within the same LA is
*necessarily* also within the same region. That means:

> **share of ALL moves staying within-region ≥ 51.9%** (DERIVED lower bound; the true figure is
> higher by however many moves stay within the same LA, which is NOT ESTABLISHED, so no upper
> bound is available either).

A simulation cannot honestly assume "most moves stay local" means "most moves stay in the same
LA" — that specific share is unmeasured. It CAN honestly assume "a majority of moves stay within
the same broad (12-area) region", because that is true even restricted to the harder sub-population
(LA-changers) and only gets truer once same-LA moves are added back in.

---

## 2. The region definition does not match the tariff/DNO region — a mapping is needed, not a blocker

ONS's "region" (§1) is the 12-area Government Office Region / country split, and ONS publishes a
maintained lookup for it: *England and Wales local authority to region lookup* (ONS dataset,
released 25 June 2021, "a lookup table listing each local authority in England and Wales, the
region it is located within, its local authority code and region code").

**GB electricity distribution/tariff regions are a different, finer partition**: 14 Grid Supply
Point (GSP) groups / DNO licence areas (the task brief's own framing, consistent with the standard
industry count — e.g. London is one DNO area entirely inside ONS's "London" region, but ONS's
"South East" region is split across two DNO areas, and ONS's "Wales" region is split between one
DNO area that also covers Merseyside/Cheshire in England and one that does not). **No single ONS
table gives LA-to-DNO-region directly**; that mapping runs through postcode area (every GB postcode
area has one GSP group / distributor id, published by Elexon/MPAS) rather than through the ONS
local-authority geography. This pass did not pull that postcode-to-GSP-group table; it exists and
is public, so the mapping is **derivable, not a gap**, but it is a second lookup, not a relabelling
of the ONS one. **GAP for this pass: the LA→GSP-group table itself was not fetched or checked in.**

---

## 3. By tenure: distance moved (a proxy, not the same measure)

English Housing Survey 2021–22, *Household moves — fact sheet* (DLUHC, published 13 July 2023,
Annex Table 1.5; England only, base: households resident in current home less than 3 years).
**ESTABLISHED, exact figures, by tenure:**

| Tenure | Moved within 5 miles of previous home |
|---|---|
| Social renters | **70%** |
| Owner occupiers | **51%** |
| Private renters | **45%** |

Age cuts the owner-occupier figure further: younger owners (HRP 16–54) 53% within 5 miles vs older
owners (55+) 44%; older owners are three times as likely to move 50+ miles (21% vs 7% younger).

**This is a distance-band measure, not a same-LA or same-region flag**, and the two should not be
treated as interchangeable: English LAs vary hugely in area (a 5-mile move can cross two or three
London borough boundaries, or stay inside one large rural district), so "70% within 5 miles" is
not "70% within the same LA". It is nonetheless the only tenure-split distance evidence found, and
it is directionally consistent with §1: social renters (the tenure usually allocated by a single
local authority or housing association, consistent with `home_moves.md` §1's framing) move the
shortest distances; private renters — the tenure that moves most often (`home_moves.md` §2.1,
~18–21%/yr) — move the furthest and least locally of the three. **A "move with us" offer therefore
has to reach furthest, and cross a tariff region most often, for exactly the tenure that generates
most of the moves.**

No published source combining tenure with an exact same-LA or same-region flag (rather than a
mileage band) was found in this pass. **GAP.**

---

## 4. What is known about consumption after a move

**No panel study tracking the same GB household's metered consumption immediately before and after
a move to a different dwelling was found in this pass.** DESNZ's National Energy Efficiency
Data-Framework (NEED) links meter consumption to dwelling EPC data by address over time and is the
natural source for such a study, but the NEED summary-of-analysis reports read in this pass (2026
edition) are about the impact of efficiency *measures*, not movers, and no mover-specific cut was
located. **GAP.**

What IS established, from a different angle — **does the dwelling or the household explain more of
a home's energy consumption?** — is directly relevant, because it bears on which side of a move
(the vacated dwelling's history, or the new dwelling's own characteristics) a supplier should trust
more:

> Huebner, Hamilton, Chalabi, Shipworth & Oreszczyn, *"Explaining domestic energy consumption – the
> comparative contribution of building factors, socio-demographics, behaviours and attitudes"*,
> Applied Energy 159 (2015) 589–600 (924 English households, fieldwork 2011/12; open access,
> CC BY). Four separate regression models: **building characteristics (dwelling size and type)
> alone explained ~39% of the variance in annualised energy consumption; socio-demographics 24%;
> heating behaviour 14%; attitudes and other self-reported behaviours only 5%.** A combined model
> with all predictors explained 44% (multicollinearity between the groups eats most of the gain
> over building factors alone), and after correcting for that, **"building variables predominantly
> remained as significant predictors of energy consumption, in particular the dwelling's size and
> type"**; of the socio-demographic predictors only household size remained significant. The paper's
> own framing: "whilst people use energy, it is physical building characteristics that largely
> determine how much is used."

**Status: ESTABLISHED** (a single peer-reviewed, open-access study; cross-sectional across
households, not a before/after panel on movers specifically, so it shows *dwellings predict
consumption better than occupants do* across the population, not *how fast a given mover's usage
converges to the new dwelling's level* — that convergence question is the GAP above). It is the
best available evidence on the mechanism the question asks about, and it points the same way as
the structural fact already recorded in `home_moves.md` §3: a settlement EAC belongs to the
*metering point*, not the household, which only makes sense as an industry practice if
dwelling-level consumption is reasonably persistent across an occupier change **at the same
address** — consistent with, not a repeat of, the Huebner finding.

---

## 5. What a simulation may honestly assume

**Destination region.** A "move with us" world should not assume the destination is always the
origin's region (§1 shows a near-even split among LA-changing moves, and over half of ALL moves,
by the bound in §1, stay in-region) and should not draw it uniformly across all 14 tariff regions
either (the real distribution is far from uniform — London/South East/East dominate the ONS
region-to-region flows in the raw YE2020 matrix). Two honest options, in order of fidelity:
1. Draw the destination's **ONS region** from the published region-to-region flow matrix
   (`IM...-T8`, conditional on the origin region), then map that region to a GB tariff/DNO region
   via the postcode/GSP-group lookup (§2, not yet pulled into this repo).
2. As a coarser, still-sourced fallback: with probability ≈0.52 (the DERIVED YE2020 figure, §1,
   stated as a point estimate with no multi-year confirmation) keep the same ONS region as the
   origin; otherwise draw another region from the matrix's marginal flow shares. **A single
   national "p(stays in region)" constant used this way must carry this exact derivation and year
   as its origin — it is not an Ofgem or DESNZ published rate, it is two ONS tables combined.**

Either way, "same region" must be read as the ONS 12-area region, converted to a tariff region
through a second lookup — never silently treated as the same partition.

**Destination demand.** The new premises' own characteristics (EPC band, floor area/property type,
build era — the same marginals `simulation/premise_population.py` already draws from, per
`ASSUMPTIONS.md`'s Household Physical Property Attributes rows) should drive the redrawn EAC, not
the mover's consumption at the old address. §4's variance-decomposition evidence is the best
available support for that: building factors outweigh household behaviour roughly 2.5:1 in
explaining consumption, so inheriting a new dwelling's own characteristics is better-supported than
carrying the old household's usage level forward. A modest household-level adjustment (the 24%
socio-demographic share, dominated by household size, which the world already carries) is
defensible as a secondary term, never as the primary driver. No published source gives the
*speed* of convergence after a move, so a simulation that makes consumption snap immediately and
fully to the new dwelling's draw is making an unforced, undocumented choice about timing (even if
the long-run level is well supported) — that choice should be named as an assumption, not presented
as sourced.

**By tenure.** If the mover-retention offer targets private renters specifically (the tenure that
moves most often, `home_moves.md` §2.1), §3 says those are also the movers least likely to stay
local (45% within 5 miles, the lowest of the three tenures) — so the destination-region draw matters
more, not less, for exactly the population a retention offer is likely to reach first.

---

## Sources

- ONS, *Internal migration by local authorities in England and Wales, year ending June 2015*
  (last narrative bulletin in this series), https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/migrationwithintheuk/bulletins/internalmigrationbylocalauthoritiesinenglandandwales/yearendingjune2015
  (fetched 2026-10-10) — definitional exclusion of within-LA moves (§1a).
- ONS, *Internal migration moves: LA and region totals, by sex and single year of age* and
  *Matrices of internal migration moves between local authorities and regions, including the
  countries of Wales, Scotland and Northern Ireland*, both released 25 June 2021, year ending June
  2020 editions: `laandregionalsquarematrices2020newboundaries.xlsx` (tables IM2020-T7b, IM2020-T8),
  https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/migrationwithintheuk/datasets/matricesofinternalmigrationmovesbetweenlocalauthoritiesandregionsincludingthecountriesofwalesscotlandandnorthernireland
  (downloaded and read directly 2026-10-10; §1b/1c figures are this pass's own arithmetic on the
  published cells).
- ONS, *England and Wales local authority to region lookup*, released 25 June 2021,
  https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/migrationwithintheuk/datasets/userinformationenglandandwaleslocalauthoritytoregionlookup
  (fetched 2026-10-10; existence confirmed, not downloaded) — §2.
- DLUHC, *English Housing Survey 2021 to 2022: household moves — fact sheet*, published 13 July
  2023, items 4–5 (Annex Table 1.5),
  https://www.gov.uk/government/statistics/english-housing-survey-2021-to-2022-household-moves-fact-sheet/english-housing-survey-2021-to-2022-household-moves-fact-sheet
  (fetched 2026-10-10) — §3.
- Huebner, G.M., Hamilton, I., Chalabi, Z., Shipworth, D., Oreszczyn, T., *"Explaining domestic
  energy consumption – the comparative contribution of building factors, socio-demographics,
  behaviours and attitudes"*, Applied Energy 159 (2015) 589–600, open-access copy
  https://discovery.ucl.ac.uk/1473481/1/1-s2.0-S0306261915010983-main.pdf (downloaded and read
  2026-10-10) — §4.
- DESNZ, *National Energy Efficiency Data-Framework (NEED) report: summary of analysis 2026*
  (accessible webpage), https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026-accessible-webpage
  (fetched 2026-10-10; checked for a mover-specific cut, none found — §4 gap).
- `docs/market_research/home_moves.md` (this repo) — move rates by tenure (§2.1 there), the
  deemed-contract and EAC-inheritance mechanics (§3 there), cited rather than repeated.
