# How far a settled domestic EAC sits from the next year's use, and two neighbouring questions

**Knowledge:** metering-and-reads

**Asked by** claim `size-the-registry-eac-read-error-from-the-published-record` (2026-10-01). The
world currently gives a fabric premise's registry EAC **zero read error**
(`SEAT_FINDING_A_FABRIC_PREMISES_REGISTRY_EAC_IS_NOW_ITS_OWN_READS_..._2026-10-01.md`), and that
assumption alone now sets year-one bill shock. This document is knowledge only: **no world
change follows from it here.** Any change is a separate item with its own pre-registration.

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
