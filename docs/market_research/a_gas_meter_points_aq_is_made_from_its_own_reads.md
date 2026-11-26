# A gas meter point's AQ is made from that meter's own reads

**Knowledge:** metering-and-reads

Written 25 Nov 2026 by the delivery seat, before the world build that makes it so (K8). The gas twin of
the electricity rule in `simulation/fabric_demand_path.registry_eac_from_own_reads` (BSCP504
s3.2.6.51, since 4 Nov).

**How figures are marked.** **[H]** quoted from a primary source already held in this repository.
**[L]** a well-known industry arrangement **not re-read this session**: practitioner background, not a
cited claim. **GAP** means not established.

## 1. What the rules say

- **The AQ is the meter's own use, weather-corrected.** "AQ is based on the consumption between two
  meter readings [9-36 months apart]. The calculation is adjusted for the impact of the actual weather
  experienced in that period. It's then converted to a 12-month estimate." (Xoserve, *Annual Quantity
  (AQ)* help page, quoted in `unbilled_energy_and_revenue_assurance.md` K2.) [H] It is expressed on
  seasonal-normal weather and spread by the EUC's Annual Load Profile. [H] (same page)
- **The AQ belongs to the supply meter point, not the supplier.** It is held on UK Link and handed to
  the gaining supplier on registration (`what_a_supplier_holds_to_size_a_direct_debit.md`, row 2). [H]
  So a switching home arrives with the AQ its own meter made, not a class value.
- **Rolling AQ.** Since Project Nexus (June 2017) the AQ is recalculated monthly from the latest read
  pair that meets the 9-36 month rule (UNC TPD Section G). Before that it was recalculated in an annual
  AQ review. [L] Under both regimes the AQ is made from the meter point's own reads. Only how often it
  is revised changes.
- **A class value is for a meter with no history.** For a new meter point the AQ is set from the EUC
  or the shipper's nomination until reads exist. [L] Every gas premise this world draws is an existing,
  settled dwelling, so that case does not arise at registration.

## 2. What the world did before this build

Each drawn gas premise carries one `aq_kwh`. The world uses it twice:

1. **Demand.** `aq_kwh x HouseholdDemandRegister.gas_eac_multiplier_for_date(...)` is the level the
   gas term settles on. The multiplier is 0.12 for a heat-pump home (cooking only), the EPC multiplier
   for a gas-heated home, and 1.0 otherwise. Real HDD moves the daily shape, not the annual level
   (`heating_fraction_for`).
2. **Registry.** The same unmultiplied `aq_kwh` is the AQ the company is handed. It holds that AQ on
   the bill estimate until its own reads span long enough.

So the registry AQ was the drawn band, not the meter's use. **Census (25 Nov, 503 drawn gas premises,
prereg `docs/staging/records/SEAT_PREREG_THE_GAS_AQ_AGAINST_ITS_OWN_METER_CENSUS_2026-11-25.md`).** This is per
premise and uses no billed days, so voids cannot enter it.

| Own use / registry AQ | Premises |
|---|---|
| 0.12 (heat pump: registry 8.3x the meter) | 3 |
| 0.34 to 0.8 | 14 |
| 0.8 to 1.25 (within 10%: 247) | 247 |
| 1.25 to 2.2 (registry *under* the meter; 36 at 1.5x or more) | 239 |

The breach that surfaced it, PROS-2021-0100 (registry 9,542.5 kWh, meter ~1,150 kWh), is one of the
three heat-pump homes. The larger class by count is the other direction: about half of the gas book
was handed an AQ below its own use. That errs in the supplier's favour on paper and under-collects in
practice.

## 3. What the build does, and why

- **Registry AQ = the meter's own weather-normal use over the year before acquisition.** That is the
  drawn level times the mean of the household's gas multiplier over the 365 days before acquisition.
  For an acquisition before the run's first year is complete, the window is the run's first year,
  which is the electricity rule's `OWN_READS_FIRST_YEAR`. The world's level has no weather in it, so
  this figure is weather-normal by construction, as Xoserve's is after its correction.
  **Correction (26 Nov 2026):** it is weather-normal on the *national* 1991-2020 England & Wales
  normal (`REFERENCE_MONTHLY_HDD`), not on the meter's own weather. On the 001e4f680a book the
  premise cells' HDD is median 0.911 of that normal, and a premise's first year of true use is
  0.930 of its registered AQ. The world's demand is exactly `aq x multiplier x weather`
  (measured / predicted 1.000). The AQ handed over is therefore ~7-8% above the meter's own year.
  See GAP 4 and
  `docs/staging/done/SEAT_FINDING_IS_A_GAS_PREMISES_REGISTERED_AQ_ITS_FIRST_YEAR_OF_TRUE_USE_2026-11-26.md`.
- **Demand does not move.** The drawn level moves to `_WORLD_BASE_AQ_KWH`, and every world-side reader
  of the household's gas level reads it from there. Only what the registry hands the supplier changes.
- **A lag-only model with zero read error**, as for electricity. A real AQ carries read and
  weather-correction error. Nothing published sizes that error, so none is invented.

## 4. GAPs

- **GAP 1: the AQ is not revised after acquisition.** A real rolling AQ would follow a heat pump
  fitted mid-supply within months. Here the company's own reads take over after its hold
  (`MIN_ADVANCE_DAYS` / `GAS_AQ_MIN_ADVANCE_DAYS`). That is the supplier's own estimate, not the
  registry's.
- **GAP 2: the size of the AQ's own error** (read error, weather-correction error, a 9-month read pair
  in an atypical year) is not published. It is carried as zero, which is the one value we know is
  wrong (K2), so it is named here and not hidden.
- **GAP 4 (narrowed 26 Nov 2026, see s5): which seasonal normal the AQ is put on.** Read: it is per
  LDZ, at one primary weather station per LDZ, climate-projected forward over the five gas years it
  serves, and revised every five years. Still open: the SNCWV values themselves (UK Link secure area),
  so how far each basis in force over 2016-2025 sat from the 1991-2020 E&W normal is not sized.
- **GAP 3: UNC TPD Section G was not re-read this session.** The rolling-AQ arrangement in s1 is marked
  [L] for that reason. The design rests only on the [H] Xoserve line: the AQ is the meter's own use.

## 5. The seasonal normal the AQ is put on (read 26 Nov 2026)

Sources, all read this session as PDF text: Xoserve, *Seasonal Normal Composite Weather Variable*
(Demand Estimation, Sept 2026, `xoserve.com/media/qfehz3t3/seasonal-normal-composite-weather-variable_sept26.pdf`,
SHA-256 f8fd0913...1121) **[SN26]**; Xoserve/Met Office, *Seasonal Normal Weather Review 2025*
(`xoserve.com/media/gv0jo4ib/xo-met-off-snwr-2025.pdf`, dfe2176b...98fe1) **[MO25]**; Xoserve,
*Seasonal Normal Review 2025* (DESC, Oct 2025, `gasgovernance.co.uk/.../2025-10/Seasonal Normal Review 2025.pdf`,
4286a02d...ea45) **[SNR25]**; Xoserve, *Seasonal Normal Review Update* 18 Dec 2019
(`xoserve.com/media/7862/...`, 5f72b082...9eba) **[U19]** and Sept 2020 (`xoserve.com/media/40682/...`,
3290c32f...74fd) **[U20]**.

- **The AQ formula weather-corrects only the read window's anomaly.** "AQ = AQMQ * 365 / (Σ (ALP *
  (1 + (DAF x WCF)))", where AQMQ is "the actual consumption between two meter reads" and "WCF𝑡 =
  CWV𝑡 - SNCWV𝑡". CWV and SNCWV are each "for the LDZ for day 't'". [SN26 slides 3-4] [H]
- **Per LDZ, one station each.** The review "is performed for each of the 13 Local Distribution Zones
  (LDZs) and associated weather stations" [MO25 p.1]. The SNCWV "remains a single value per LDZ per
  Gas Day" [SNR25 Summary]. From Oct 2020 "Yeovilton Weather Station will be the primary source of all
  weather observations ... for the South West (SW) LDZ" [U20]. [H]
- **The CWV** is fitted per LDZ to aggregate NDM demand, using "temperature, wind speed and solar
  radiation" [MO25 p.1]; solar was added from 1 Oct 2020 [U20]. The 2025 parameters were fitted on
  "8 Gas Years ... 2015/16 to 2022/23" and are tabled per LDZ [SNR25 CWV slides]. [H]
- **The normal is climate-projected forward, not a fixed 30-year average.** The SNCWV "represents a
  benchmark of climatological 'normal' weather ... for each LDZ", set "at a minimum once every 5
  years" to be "reflective of the latest view of longer-term climate change phenomenon such as global
  warming" [SN26 slide 2]. [H]
  - **Basis from 1 Oct 2025 (to 30 Sep 2030):** "derived purely from the CCM projections". These are
    Met Office UKCP18 projections for "01/10/2025 05:00 to 01/10/2030 04:00", passed through the CWV
    and averaged "across the 5 Gas Years" [SNR25 Calculation of SNCWV]. "Across all LDZs, SNCWV
    profiles have generally increased across all months" (warmer). For LDZ NO the change is +0.28 to
    +0.97 CWV by month [SNR25 SNCWV Profiles]. "This warming will result in a reduction in AQs,
    especially for ... the domestic sector" (Xoserve news, 11 Jun 2025). [H]
  - **Basis from 1 Oct 2020 (to 30 Sep 2025):** built on a CWV history from 1960/61 adjusted for
    climate change ("older years have been adjusted more"), using the 2013 Met Office work that
    "produced predictions of expected average weather as far as 2025" [U19]. [H] How that adjusted
    history was reduced to the daily normal is in the secure area and was not read: **GAP**.
  - **Basis from 1 Oct 2015:** "the last review of Seasonal Normal in 2014", on the same 2013 Met Office
    output [U19]. [H] Its construction is not read: **GAP**.
- **A basis change moves every AQ at once.** At each change, AQs not recalculated in September get an
  EUC "Seasonal Normal Ratio" "to ensure all Live Supply Meter Points ... will be on the same Seasonal
  Normal weather basis" [SNR25 Implementation; U20]. Billing AQs follow from April 2026 [SNR25
  Summary]. [H] The ratios' values are secure-area: **GAP**.

**What this means for the world's registry AQ** (inference from the [H] lines above, not a quoted claim):

1. **A meter's local climate is inside its real AQ.** The AQMQ is the meter's actual consumption. The
   correction divides out only how far its *LDZ station's* weather departed from the *LDZ's* normal in
   the read window. A home warmer than its LDZ station (an urban cell) meters less gas in every year,
   and nothing in the formula adds that back. So the real AQ is about the meter's own use in a year when
   its LDZ's weather is normal. The world's AQ puts every meter on the national normal, which strips
   out that local offset. That part of the 9% (the urban cells) is the world's error, not something a
   real supplier carries.
2. **The normal leans warm.** Each basis is built to represent the five gas years it serves, using
   climate projections. A backward 1991-2020 average therefore sits colder than any basis in force over
   2016-2025. That part of the 9% (2016-25 warmer than 1991-2020) is also mostly absent from a real AQ.
   How much is left over is not sized: the SNCWV values are secure-area.
3. **What a real supplier does carry** is the read window's LDZ-versus-meter mismatch and the year's
   departure from the projected normal. These are year-to-year noise around 1, not a standing 7-8% bias.

**Decision (delivery seat, 26 Nov 2026).** `register_gas_premises_on_their_own_reads` should hand over
the meter's own weather-normal year **at its own cell**, not at the national normal. It should take
the meter's own use over the read year (the 365 days before acquisition, at its cell's weather). Then
it should divide out only that year's departure from a normal, the way the AQMQ/WAALP formula does. The
world has no LDZ CWV and no SNCWV values, so which normal it uses for that departure is the one open
choice. It is handed on as a build item with that choice named (`docs/staging/SEAT_FINDING_A_GAS_AQS_SEASONAL_NORMAL_IS_PER_LDZ_PROJECTED_FORWARD_AND_KEEPS_THE_METERS_OWN_CLIMATE_2026-11-26.md`),
not picked here. Until the build lands, the registry AQ's national-normal basis is a named defect,
not the record.
