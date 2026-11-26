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
  `docs/staging/SEAT_FINDING_IS_A_GAS_PREMISES_REGISTERED_AQ_ITS_FIRST_YEAR_OF_TRUE_USE_2026-11-26.md`.
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
- **GAP 4: which seasonal normal the AQ is put on.** Xoserve expresses the AQ on seasonal-normal
  weather [H]. Not established: whether that normal is per LDZ, how it is built (the Seasonal Normal
  Composite Weather Variable and its review cycle), and whether it is climate-adjusted toward recent
  years. The build uses the national 1991-2020 normal, which is warmer-blind at an urban 1 km cell.
  Until this is read, the registry AQ's weather basis is the build's choice, not the record's.
- **GAP 3: UNC TPD Section G was not re-read this session.** The rolling-AQ arrangement in s1 is marked
  [L] for that reason. The design rests only on the [H] Xoserve line: the AQ is the meter's own use.
