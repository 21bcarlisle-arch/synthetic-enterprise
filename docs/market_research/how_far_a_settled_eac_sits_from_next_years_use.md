# How far a settled domestic EAC sits from the next year's use, and two neighbouring questions

**Knowledge:** metering-and-reads

**Asked by** claim `size-the-registry-eac-read-error-from-the-published-record` (2026-10-01). The
world currently gives a fabric premise's registry EAC **zero read error**
(`SEAT_FINDING_A_FABRIC_PREMISES_REGISTRY_EAC_IS_NOW_ITS_OWN_READS_..._2026-10-01.md`), and that
assumption alone now sets year-one bill shock. Sections 1-3 are knowledge only: **no world
change follows from them here.** §4 (4 Nov 2026) records the one that did, and why.
§5 (7 Nov 2026) records what a domestic bill's ceiling check compares against, and the company change that followed.

There are three questions:
1. How far does a settled EAC sit from next year's actual use, by meter type?
2. Does the cap bind a ToU tariff at a benchmark split, or at the household's realised rate?
3. Is 28–41 MWh/yr plausible for a GB direct-electric home?

---

## 1. Registry EAC against next year's use

### What the industry figure is (DESNZ, *Subnational methodology and guidance booklet*, 2026)

> "For the NHH data, annualised estimates are based on either an Annualised Advance (AA) or
> Estimated Annual Consumption (EAC). The AA is an estimate of annualised consumption based on
> consumption recorded between two meter readings at least 6 months apart … an EAC is used where
> two such meter readings are not available and an estimate of annualised consumption is produced
> … using historical information and the profile information relating to the meter."

> "The MPAN data used in this analysis consists of approximately **80 per cent actual ('Annual
> Advance') readings and 20 per cent estimated readings ('Estimated Annual Consumption')** … From
> year-to-year some meter readings … change from actual to estimated readings and vice-versa, which
> can cause extreme values to be created when an estimate is corrected."

The NEED electricity field `Econs<year>` is built from these same MPAN figures. So for one
dwelling, **the ratio of two consecutive NEED years is the ratio of two consecutive industry
annual figures for that meter.** That is the closest published thing to "the EAC a gaining
supplier is handed against the use it then bills."

### Measured: NEED 2026 anonymised 50k sample, consecutive-year pairs 2016→2024

Method: r = E(t+1)/E(t), both years flagged `V`, dwellings flagged `PV_FLAG` excluded (export
netting). Pairs are pooled across years. Pre-registered before the run in
`docs/staging/records/WORKER_PREREGISTRATION_YEAR_ON_YEAR_DOMESTIC_ELECTRICITY_CHANGE_IN_NEED_AS_THE_EAC_ERROR_FLOOR_2026-10-01.md`.

| class | pairs | median r | p10 r | p90 r | median \|r−1\| | p75 | p90 | p95 | share \|r−1\|>0.25 | >0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gas-heated | 273,417 | 1.000 | 0.682 | 1.392 | **0.143** | 0.290 | 0.550 | 0.800 | 0.290 | 0.113 |
| gas not main heating fuel | 57,467 | 1.000 | 0.612 | 1.577 | **0.179** | 0.377 | 0.714 | 1.125 | 0.377 | 0.171 |
| … of those, ≥8 MWh in year t | 9,959 | 0.915 | 0.466 | 1.214 | 0.167 | — | 0.589 | — | 0.357 | — |
| all | 330,884 | 1.000 | 0.667 | 1.419 | 0.147 | 0.304 | 0.580 | 0.842 | 0.305 | 0.123 |
| all, 2021→2022 (price shock) | 41,989 | 0.923 | 0.611 | 1.364 | 0.167 | 0.324 | 0.591 | 0.829 | 0.335 | 0.130 |

**What the distribution is.** It is centred on 1 (no bias), and its spread is wide: half of
homes move by more than 14% from one industry year to the next, and one in eight moves by more
than 50%. That fits Elexon's own finding on the bias. Its Issue 23 group (final report
2006-10-12) concluded "there may be an issue regarding the estimation of consumption, but that
**EACs are not systematically underestimating consumption**."

**What it bundles, stated rather than separated.** The spread contains four things:
- real household change: weather, occupancy, appliances;
- **change of occupier**: NEED follows the dwelling, not the household;
- EAC↔AA transitions, which DESNZ itself names as a source of extreme values;
- the rounding to 100 kWh.

A switching customer keeps their own history. A move-in inherits the previous occupier's EAC. The
two populations would have different error distributions, and NEED cannot split them.

### By meter type: what is and is not published

| meter | what the record gives | status |
|---|---|---|
| smart (read monthly or more often) | Nothing published by meter type. Frequent reads make the AA the trailing actual year, so the error approaches the household-change component above. | **GAP** |
| traditional credit (read ≤2×/yr, some estimated) | DESNZ: ~20% of MPAN-years carry an EAC rather than an AA, and corrections produce extreme values. No distribution of the error is published. | **GAP**, partly bounded by the table |
| E7 / storage (profile class 2) | NEED exposes no profile class. "Gas not main heating fuel" is the nearest proxy, and it is **wider** (p90 0.71 against 0.55). It also mixes in oil, LPG and solid-fuel homes. | **GAP** |

**Practitioner question (put to the director):** at a change of supply, what share of the EACs a
supplier receives are AA-backed and what share are estimate-backed, for smart and for traditional
meters? And in practice, how far is a first-year direct debit off for each? A practitioner will
know the second answer; no published source gives it.

**What this does and does not license.** The table is a sourced distribution of *how far one
industry annual figure sits from the next*. It is not a distribution of read error alone. It
must not be read as a calibration target for the world's read-error term without first deciding
which of the four components the world already produces. The world already varies weather and
does not vary occupancy. **That decision belongs to the separate pre-registered world item.**

---

## 2. Does the cap bind a ToU tariff at a benchmark split or at the realised rate?

**At an assumed split, not at the household's realised average rate.** Source: Ofgem, *draft
electricity licence condition 28AD* (June 2018). The in-force text was not read here because the
consolidated-conditions URL redirected. Read the in-force paragraph before anything is keyed to
the wording.

> **28AD.4** "For all Multi-Register Tariffs, compliance with the Charge Restriction will be
> assessed against the Relevant Maximum Charge determined on the basis of the Benchmark Metering
> Arrangement values for **Economy 7 Metering Arrangements**."
>
> **28AD.29** "… in calculating the aggregate amount of all Charges for Supply Activities,
> consumption in different periods will be weighted using an **Assumed Consumption Split** …"
>
> **28AD.31(a)** for each Economy 7 Tariff, "off-peak and peak consumption levels of **42% and
> 58%**, respectively"; **(b)** for any other Multi-Register Tariff, "based on historic
> consumption data or, in the absence of historic data, on a reasonable estimate of the average
> consumption split", notified to the Authority (28AD.32).
>
> **28AD.34** the Authority may direct a rebate if, because the forecast and actual average splits
> differ, customers "either individually or collectively incurred Charges … materially in excess of
> the Relevant Maximum Charge."

**Consequences for the five ToU first bills above the flat ex-VAT cap:**
1. A household whose realised rate is above the flat cap is **not, by that fact, in breach.**
2. The legal test is made against the **Economy 7 benchmark**, not the single-rate one, and at the
   tariff's assumed split. The world's flat ex-VAT cap is therefore the wrong comparator for a
   multi-register SVT.
3. For a non-E7 ToU tariff the split is the **supplier's own declared historic average.** An
   assumed 30% peak is lawful only if it is that tariff's real average. 28AD.34 is the backstop
   that catches a split chosen to fit.

---

## 3. Is 28–41 MWh/yr plausible for a GB direct-electric home?

The world drew both accounts as **detached, pre-1919, 6 bed, 151–200 m², direct electric, poor
insulation, no mains gas.** PROS-2016-0098 has EPC F; PROS-2024-0082 has EPC E and a smart meter
from 2022.

**From the published electricity record** (`need_domestic_electricity_high_tail.md`):
- DESNZ suppresses domestic electricity above 25,000 kWh, so **no published percentile reaches
  28 MWh.**
- The censored share is not small: 5.93% of "detached, pre-1930, 151–200 m², gas not main
  heating fuel" sits above 25 MWh. That class includes oil and LPG homes, so the direct-electric
  share above the cut is larger.
- The subnational methodology keeps profile-class 1–2 meters as domestic up to 100,000 kWh, and
  reallocates them between 50 and 100 MWh only if the address shows a business. So the
  statistics themselves treat 28–41 MWh as within domestic range.

**A cross-check from the same dwelling class heated by gas** (NEED 2026, gas-heated, detached,
pre-1930, 151–200 m², gas kWh):

| year | n | p50 | p90 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| 2019 | 136 | 26,900 | 40,200 | 45,800 | 48,300 |
| 2024 | 143 | 21,500 | 34,200 | 39,900 | 45,600 |

A boiler delivers less heat than the gas it burns, and resistive heating delivers all of it. So
the *heat demand* of this class sits at or below these gas figures, and the class's own
appliance use adds to it.
- **On that reading, 28 MWh is about the median of a home heated to a gas home's standard.**
- **41 MWh is about that class's p90–p95.**

**What the record does not settle, and this is the open question.** NEED's non-gas homes in the
class have a median electricity use of **4,500 kWh**, not ~25,000. That is consistent with
electric-heated homes heating far less than gas-heated ones because of the price, but the mixing
with oil-heated homes means NEED cannot show it. If that is right, a world that heats a
direct-electric home to the gas class's level has its tail in the right place and its centre too
high.

**Verdict:**
- **28 MWh is plausible.** It is inside a measured, unsized domestic tail.
- **41 MWh is not refuted, but no published distribution reaches it.** That is a gap.

**Practitioner question (put to the director):** does a large, old, poorly insulated
direct-electric home on Economy 7 or storage heaters really draw 30–40 MWh a year? Or do such
households ration heat so hard that 15–20 MWh is the realistic top? Put plainly: does the world
heat electric homes as if electricity cost what gas costs?

---

## 4. What an electrically heated home meters, and what its registry EAC should be (added 4 Nov 2026)

**Asked by** the drawn item `electric-heated-homes-eac-double-count-and-the-fresh-grade`. On the a6b7a0fd47
book, 19 of the 54 INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER breaches are on homes the world drew
storage- or direct-electric-heated. Those homes meter 5-10 MWh a year, with a tail at 13-23 MWh (large
or E/F-rated homes), against registry EACs of 1,400-4,000 kWh. Two questions were asked: is the drawn
band already heating-inclusive (a double count), and does a real EAC follow the reads? Researched
first-hand unless marked REPO (quoted from an earlier page).

**What is published (FH):**
- **Every Economy 7 meter, metered** (DESNZ sub-national statistics, GB). The median was 4,102 kWh in 2016,
  3,918 in 2019 and 3,344 in 2024; the 2024 mean was 4,664. That is every PC2 meter, with or without storage
  heating. Ofgem records a stakeholder claim that about half of E7 users have storage heating and use
  "significantly" more (TDCV decision, 25 May 2023, para 2.21). That is an assertion, not a finding.
- **A storage-heated home, modelled to a heating standard** (BEIS/Element Energy, Research Paper 2019/021,
  Tables 7-1, 7-4, 7-10). A 73 m² solid-wall terrace uses **12.8 MWh** a year (9.7 MWh with loft and wall
  insulation). A 174 m² un-insulated detached house uses **21.9 MWh** (16.0 MWh insulated). Hot water is
  included. These are demand models, not meters.
- **NEED 2026, gas not the main heating fuel** (2024 year; our own percentiles from the published 50k file).
  Median 3,200 kWh, p75 6,000, p90 9,600. Homes over 200 m²: median 6,000, p90 15,900. The class mixes in
  oil, LPG and communal heat, and has no electric-heating field.
- **The TDCVs are defined by meter class, not by heating.** PC1's quartiles are those of every single-rate
  meter (decision para 2.15). PC2 (2,200/3,900/6,700 from Oct 2023) includes storage and non-storage homes
  (para 2.12), and Ofgem says it is "bound to be below [its] actual value". Neither is a figure for an
  electrically heated home. Ofgem's own advice is to use the consumer's figures.
- **A real EAC follows the reads.** BSC Annex S-2 §4.3.7 (P40 legal text, FH): every valid advance gives a
  new EAC, EAC_new = w × AA + (1 − w) × EAC_previous, with w = min(FYC × SPAR, 1). BSCP504 v53.0 §4.9 sets
  no minimum read interval. The "6 months apart" is DESNZ's statistical definition of an AA, not a BSC
  rule. A gaining supplier is handed the latest EAC (§3.2.6.51, REPO).

**Not established (GAP):** a metered annual figure for storage-heated or direct-electric homes; how far such
homes ration heat; SPAR's value (Market Domain Data, behind a login); the lag from a read to its D0019; and
whether a supplier's billing estimate in its first months follows the D0019 EAC, its own reads, or a blend
(Citizens Advice, FH, implies its own earlier pattern but gives no weighting).

**What the design does, and why:**
1. **No double count to remove.** The drawn band is a PC1 quartile range, drawn blind to the dwelling. On
   an electric-heated home it acts as the appliance base, and the legacy shape adds the heating to it. The
   world's resulting 5-10 MWh, with its 13-23 MWh tail on large poorly rated homes, sits inside the BEIS
   modelled range (9.7-21.9 MWh) and above the E7 population, which is where a heated home should sit.
   `demand_model.ELEC_HEATING_KWH_PER_DEGREE_DAY` (3 kWh/HDD) is therefore **not changed**. Nothing published
   refutes it, and nothing published licenses a better number. SYN-2016-201 (a two-bed EPC E flat at
   13-15 MWh) sits above the 73 m² terrace's 12.8 MWh, and is the case to watch.
2. **The defect is the registry, not the meter.** The own-reads rule of 1 Oct reached the fabric premises
   only. On the a6b7a0fd47 book, **all 15** breaching electric-heated homes were legacy premises still
   registered at their drawn band. The 10 electric-heated fabric premises, registered on their own reads,
   breach none. From 4 Nov a domestic legacy premise is registered on its own first-year import, as a fabric
   premise is (`run_phase2b.register_legacy_premises_on_their_own_reads`). The band stays the world's demand
   level, so the meter does not move; only what the registry hands the supplier does.
3. **The supplier's first-year estimate rule is not changed.** Whether to re-estimate from the first reads
   is a GAP above. With the registry carrying the home's use, the case behind it (an estimate held at the
   registry figure after a large read) loses its cause. If the next book still shows it, that becomes the
   question.

## 5. What a domestic bill's ceiling check compares against (added 7 Nov 2026)

**Asked by** the drawn item `the-billing-gate-scales-a-homes-electricity-by-its-own-meter`. On the
fd91027799 book the exception queue holds 16 winter estimates on three listed, storage-heated homes
(SYN-2016-175, SYN-2016-355, PROS-2017-0233; EACs 18.7-23.7 MWh). The company's pre-bill gate reads each
one as a business: it compares the bill with a flat 2,100 kWh a month, a figure sourced as "observed sim
population + headroom". Each held estimate is 0.91-1.18 times its own EAC spread by the PC1 shape, and
exactly its EAC on the meter's PC2 register split. The holds are the whole cause of the carbon row's
exception. Researched first-hand (FH) by a discovery pass on 7 Nov unless marked.

**What is published (FH):**
- **Electricity read validation is per meter, at twice the expected advance.** BSCP504 (NHH data
  collection, effective 22 Sep 2025), "Validate" appendix (4.2, as extracted), step 5: "Check
  consumption/generation does not exceed twice the expected advance. (using the EAC times the Profile
  Coefficient, or some other equivalent method.)" A read over it fails validation, "except where it is
  caused by a seasonal register Time Pattern Regime", and the data collector may set it valid "where good
  reason exists". With no prior valid read, the expected advance may be the class-average EAC times the
  coefficient, or an AA from reads either side. The per-class EAC/AA tolerances are in Market Domain Data,
  behind a login. **GAP** for those numbers.
- **Gas read validation is tolerance-banded against the meter, but the numbers are not found.** UNC TPD
  Section M v6.24 §5.3.2-5.3.5: an inner band the user can override and an outer band it cannot, for
  Class 2-4 meters checked by the user and then the CDSP. The values sit in the UNC Validation Rules
  document (§5.3.3), not located. **GAP.**
- **VAT follows the premise, not the volume.** HMRC Notice 701/19 §3.2.1: fuel for "genuine domestic use"
  at a dwelling takes the reduced rate; the notice sets no volume limit on it (read from its absence). The
  1,000 kWh a month (33 a day) electricity and 4,397 kWh a month (145 a day) gas thresholds of §5.2 and
  §4.2 are the de minimis for business use only. (Also found: a temporary 0% rate on domestic electricity
  in GB from 1 Oct 2026 to 30 Jun 2027. That is outside the 2016-2025 record and changes nothing here.)
- **Not found:** any Ofgem, Citizens Advice or Energy UK statement of what a supplier's bill exception
  queue compares a domestic bill against. **GAP.** The BSCP504 check is the industry's only published
  per-meter comparison, and it is the data collector's, applied to reads.
- **What storage-heated and direct-electric homes meter in a month: still GAP.** §4 holds the annual
  evidence (BEIS/Element Energy modelled 9.7-21.9 MWh). No metered monthly peak share for electric heating
  was found; the PC2 profile coefficients are the published shape.

**What the design does, and why:**
1. **The meter's registered EAC lifts the ceiling to BSCP504's rule.** For electricity the ceiling is the
   larger of the population screen and twice the registry figure's share of the bill's days (the larger of
   the PC1 shape and the PC2 register split, as §4f of `unbilled_energy_and_revenue_assurance.md` already
   computes it). `company/compliance/domain_invariants.domestic_bill_ceiling_kwh`,
   `READ_VALIDATION_EXPECTED_ADVANCE_THRESHOLD = 2.0`. Applying a data collector's read check to a
   supplier's bill is our choice: it is the one published per-meter comparison.
2. **It lifts and never lowers.** A real collector compares against the current EAC, which every advance
   moves (§4). The company holds only the EAC it was handed at registration. Measured on the fd91027799
   book: lowering the screen to 2x that figure would newly flag 46 electricity bills, all on two homes
   (SYN-2016-050, SYN-2016-487) whose use has doubled since 2016. So the flat screen stays as the floor,
   now labelled a named simplification. The error runs lenient for a meter registered light whose use has
   grown.
3. **The VAT half lifts only on a listed dwelling.** On the council tax list the premise is a dwelling, and
   §3.2.1 gives it the reduced rate at any volume. Off the list, a business premise on a domestic label
   has a business-sized registry figure, so lifting there would hide the C6 class. The screen stays.
4. **Gas is unchanged.** No tolerance is published to us. 2x on the AQ would newly flag 202 gas bills on
   the same book, mostly short spring reads, which is a reason not to borrow electricity's number.
5. **Answers §4f's open question for electricity.** "Whether the registry should also answer there" (after
   a read too short to replace it): yes, because BSCP504's expected advance is the EAC times the profile
   whatever the read history. SYN-2016-175 is that case: one 23-day April read, then winter estimates at
   its registry share, each above the spring rate §4d compared them with.

**Sources (§5):** Elexon, BSCP504 *Non Half Hourly Data Collection for SVA Metering Systems Registered
in SMRS*, effective 22 Sep 2025:
https://bscdocs.elexon.co.uk/bsc-procedures/bscp504-non-half-hourly-data-collection-for-sva-metering-systems-registered-in-smrs
· Joint Office, UNC TPD Section M v6.24 (18 May 2026):
https://www.gasgovernance.co.uk/sites/default/files/related-files/2026-05/15%20TPD%20Section%20M%20-%20Supply%20Point%20Metering.pdf
· HMRC, *VAT on fuel and power (Notice 701/19)*: https://www.gov.uk/guidance/vat-on-fuel-and-power-notice-70119

## Sources
- DESNZ, *Subnational methodology and guidance booklet* (2026), §3.1.3 and "Annualised
  MPAN-level electricity consumption data":
  https://assets.publishing.service.gov.uk/media/6a68b45b83f71b8684d02105/Subnational-methodology-and-guidance-booklet.pdf
- DESNZ, NEED 2026 anonymised dataset `anon2026_50k.csv` (local cache
  `~/.cache/synthetic-enterprise/need_2026/`), as in `need_domestic_electricity_high_tail.md`
- Elexon, *Issue 23: Apparent Tendency for EAC Values to Under-Estimate Consumption*:
  https://www.elexon.co.uk/smg-issue/issue-23-apparent-tendency-for-eac-values-to-under-estimate-consumption/
- Ofgem, *Draft electricity licence condition — default tariff cap — 28AD v1.0* (June 2018):
  https://www.ofgem.gov.uk/sites/default/files/docs/2018/06/draft_electricity_licence_condition_default_tariff_cap_-_28ad_v1.0.pdf
- Not read, named for the next reader: BSCP504 (EAC/AA calculation) and the in-force SLC 28AD
  text.
- §4 (4 Nov 2026): Ofgem, *Decision on revised TDCVs and Economy 7 consumption split*, 25 May 2023:
  https://www.ofgem.gov.uk/sites/default/files/2023-05/TDCV%202023%20Decision%20Letter.pdf · DESNZ,
  *Subnational electricity consumption statistics 2005-2024* (18 Dec 2025):
  https://assets.publishing.service.gov.uk/media/69426e905431f4f94d7f0b5e/Subnational_electricity_consumption_statistics_2005-2024.xlsx
  · BEIS/Element Energy, *Evidence gathering for electric heating options in off gas grid homes* (2019/021):
  https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/831079/Electric_heating_options_in_off-gas_grid_homes.pdf
  · Elexon, *P40 Modification Report* v0.3 (Annex S-2 §4.3.7):
  https://assets.elexon.co.uk/wp-content/uploads/sites/11/2012/02/28170318/p40_mr_v0.3.pdf · Elexon, BSCP504
  v53.0 §4.9 (as above) · Citizens Advice, *If you think you've been charged too much for your energy*
  (retrieved 4 Nov 2026).
