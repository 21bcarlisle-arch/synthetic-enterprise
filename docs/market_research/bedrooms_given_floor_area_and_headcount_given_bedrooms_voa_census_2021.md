**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted`

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are anchored rows it will be built from; this declaration is replaced when the
page lands.

# Bedrooms given floor area, and headcount given bedrooms

**Read 2026-10-09** by the autonomous worker, for the claim
`headcount-given-dwelling-size-then-the-per-occupant-slope`. Raw counts are committed at
`sim/people/dwelling_size_counts.json` and rebuilt by `python3 tools/dwelling_size_joint.py --commit`.
The source files are cached outside the repo in `~/.cache/synthetic-enterprise/dwelling_size/`.

## 1. Bedrooms by property type and council tax band: VOA CTSOP3.0

**Source:** Valuation Office Agency, *Council Tax: stock of properties, 2025*, table CTSOP3.0,
England and Wales, at 31 March 2025, published 22 May 2026.
https://assets.publishing.service.gov.uk/media/6a0ee006f71ef78abbd59d69/2025_CT_SoP_Tables_3_4.ods.
VOA's property-type columns are split by bedrooms (1 to 6+, plus "Not known") within each band.

The share of the known-bedroom stock is 12.7% one-bed, 28.2% two, 42.9% three, 12.7% four, 2.5%
five and **0.9% six-plus**. By type, the six-plus share of all-band totals is 0.2% for bungalows,
0.6% for flats, 0.5% for terraces, 0.6% for semis and 3.1% for detached houses.

## 2. Household size by bedrooms: Census 2021 RM136

**Source:** ONS Census 2021, RM136 *Tenure by household size by number of bedrooms*, England and
Wales, all tenures, via nomis `NM_2236_1`. Households, both dimensions capped at 4+:

| People \ bedrooms | 1 | 2 | 3 | 4+ | Total |
|---|---|---|---|---|---|
| 1 | 2,103,189 | 2,584,556 | 2,205,958 | 588,085 | 7,481,788 |
| 2 | 602,910 | 2,675,616 | 3,533,763 | 1,639,112 | 8,451,401 |
| 3 | 82,563 | 918,985 | 1,979,246 | 974,378 | 3,955,172 |
| 4+ | 37,373 | 536,579 | 2,300,745 | 2,020,142 | 4,894,839 |

P(one person | one bedroom) = **0.744**. P(one person | 4+ bedrooms) = **0.113**.

## 3. Mean floor area by bedrooms: EHS 2012, an out-of-sample check

**Source:** MHCLG, *Floor Space in English Homes*, technical report figures and tables, Fig 2.5,
published 12 July 2018, from the EHS 2012 dwelling sample. Mean usable floor area (`floory`, new
definition): **47.0 m² for one bed, 70.9 for two, 94.7 for three and 158.4 for 4+.**

VOA's P(bedrooms | type, band), marginalised over NEED's council-tax mix within each type and
floor-area band, gives 53.2, 75.1, 97.3 and 139.0 m² at NEED's band midpoints. None of the three
inputs holds this relation, so the agreement tests the assumption that bedrooms are independent
of floor area given type and band.

## 4. Electricity by household type, per end use: HES 2012

**Source:** DEFRA/DECC/EST, *Household Electricity Survey*, Intertek report R66141, final report
issue 4, May 2012. Mean kWh/yr by household type:

| Table | Single pensioner | Single non-pensioner | Multiple pensioner | With children | Multiple, no children | All |
|---|---|---|---|---|---|---|
| 25 Lighting | 548 | 581 | 413 | 477 | 548 | -- |
| 26 Audiovisual | 465 | 453 | 441 | 603 | 630 | 553 |
| 29 Computer sites | 137 | 201 | 258 | 241 | -- | 240 |
| 1 Whole home | 3,427 | 3,853 | 3,812 | 3,672 | -- | -- |

Lighting shows no headcount gradient. Audiovisual is about +35% from one-person to multi-person
households. The cooking appliances (Table 23) are in
`what_a_cooking_appliance_uses_in_a_year_hes_2012.md`, and they are flat too.

**What is not established.** Every per-end-use HES table is flat or mild by household type, but
the whole-home gradients are steep: SERL 2022 gas no-PV gives 0.64 per occupant, and NEED 2023
Table A14 by adults gives 0.46. No published source read so far says which end use, or which
ownership pattern, carries the difference.
