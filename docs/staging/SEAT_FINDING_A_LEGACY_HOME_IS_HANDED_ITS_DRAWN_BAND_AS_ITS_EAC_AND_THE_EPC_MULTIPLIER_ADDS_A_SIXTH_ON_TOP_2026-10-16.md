**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`
**Knowledge:** unbilled-energy-and-revenue-assurance

# A legacy home's EAC is its drawn band, and the EPC multiplier adds a sixth on top of it. Separately, C7's missing EAC is what HH settlement looks like, but HH settlement with no HH data is not (2026-10-16)

**Fate (2026-10-16):** BUILD AFTER THE 2026-10-19 PUBLISH. This is a diagnosis only, and no world behaviour changed. It answers claim `legacy-pc1-homes-use-a-fifth-more-than-their-own-eac`, which comes from
`WORKER_FINDING_D48_ELECTRICITYS_PRE_2020_UNDER_BILL_IS_ONE_UNREAD_EV_HOME_BILLED_ON_THE_TDCV_FALLBACK_2026-10-16.md` §1.
The pre-registration is `records/SEAT_PREREG_WHICH_LAYER_LIFTS_A_LEGACY_HOME_ABOVE_ITS_OWN_EAC_2026-10-16.md`,
written before any layer was integrated. It is graded below. One edit was made after the measurement: at landing, its header atom was repointed from D48 to W2_36, the world-lane atom this subject serves. Its predictions are untouched.

*Run `run_output_2248e3baf_20261013T134447Z` (the one the Expert Hour graded). The probe rebuilds
`run_phase2b._weather_adjusted_shape_fn` one layer at a time for every `legacy_pc1_rescaled` home
that is in the module book: 232 of the run's 291. The other 59 were won mid-run. It integrates every
calendar year from 2016 to 2024 at the run's own inputs: `build_properties(CUSTOMERS, live_dwellings())`,
`HouseholdDemandRegister(CUSTOMERS, ...)` and the per-cell weather store. On the 15th of every month
the probe's full chain was checked against the real function, and **0 days mismatched**. One mistake
of my own was caught and corrected. The first pass built properties from the electricity homes alone,
so no gas twin was visible and every home read `electric_storage`. The table below comes from the
corrected pass.*

## 1. Which layer it is

**The cause is the registry, not the scaler.** `eac_scaled_shape_fn` does its job: every year
integrates to the EAC to within 0.000%. Two things combine to produce the gap:

1. **The overlays sit on top of the EAC by design** (`eac_scaled_shape_fn`'s docstring says "a
   household's settled total therefore need not equal its EAC"). The largest overlay is
   **`HouseholdDemandRegister.epc_multiplier`**. It is centred on band C (A/B 0.75, C 1.00, D 1.25,
   E 1.55, F 1.85, G 2.20), so its book mean is 1.156, not 1. It also multiplies the whole
   electricity shape of every home, including the 76 gas-heated ones, whose electricity is mostly
   not heating.
2. **A legacy home's registry EAC is still the drawn TDCV band**, which is the number the base profile
   is levelled to. Fabric homes have been handed their own reads since 2026-10-01
   (`run_phase2b` ~l.1912, `registry_eac_from_own_reads`, BSCP504 s3.2.6.51). That loop iterates
   `fabric_series_by_customer` only. **That is why fabric homes sit at -2% (lag) and legacy homes sit
   at +21%.** It is the same defect the 2026-10-01 fix closed, still open on the other provider.

**Annual integral against the EAC, cumulative and per step, 2016-2024 pooled by kWh:**

| layer (in the order the code applies it) | 2016 cohort cum | step | later cum | step | all 232 cum | step |
|---|---|---|---|---|---|---|
| `eac_scaled_shape_fn` | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |
| + HDD electric heating | +2.73% | +2.73% | +0.00% | +0.00% | +1.77% | +1.77% |
| + CDD cooling | +2.73% | +0.00% | +0.01% | +0.01% | +1.77% | +0.00% |
| x occupancy shape | +3.01% | +0.27% | -0.12% | -0.12% | +1.91% | +0.13% |
| x occupancy volume | +2.33% | -0.65% | +0.02% | +0.14% | +1.52% | -0.38% |
| solar / battery | +2.33% | +0.00% | +0.02% | +0.00% | +1.52% | +0.00% |
| **x EPC multiplier** | **+18.32%** | **+15.62%** | **+15.11%** | **+15.09%** | **+17.19%** | **+15.44%** |
| + ASHP 5,500 kWh/yr | +21.26% | +2.49% | +17.77% | +2.31% | +20.04% | +2.43% |
| + EV 2,143 kWh/yr | +22.23% | +0.79% | +18.79% | +0.86% | +21.02% | +0.82% |

Every year from 2016 to 2024 lands between +20.8% and +21.5%, so this is a level, not a season.

**The probe reproduces the bills.** Over the same homes and billed days, true kWh against the registry
EAC is +20.9% for the 2016 cohort and +27.8% for the in-book later homes. The probe gives +21.4% and
+27.3%. The D48 cohort figures were +21.9% and +10.6% (+21.1% and +11.3% recut here). The later
cohort's +11.3% is lower because 59 of its homes are mid-run wins outside the module book. Whether
those wins carry a different registry EAC **I cannot yet say**. It is the first thing the build
should print.

**Two homes carry +191% heating load.** Of the 232 homes, 156 are `electric_storage`
(`DEFAULT_HEATING_SYSTEM` applies whenever no `<cid>g` gas twin exists). The HDD layer bites only
in the 2 storage homes that have a weather cell, because the other legacy homes are legacy precisely
*because* they have no cell. So **extending the weather store to these cells (W1_14) would add
~3 kWh/DD of storage heating on top of a TDCV band in up to 154 homes.** Whether those homes really
are electrically heated is a separate W2 question about the default. It is named here so that the
weather extension does not land into it blind.

### The predictions, graded

| | Prediction | Result |
|---|---|---|
| P1 | The scaler integrates to the EAC within +-0.5% every year | **Held** (0.000%) |
| P2 | The EPC multiplier is the largest lift; its book mean is >= 1.12 | **Held** (step +15.4%, mean 1.156) |
| P3 | The occupancy volume book mean is within +-3% of 1 | **Held** (-0.38%) |
| P4 | CDD under 1%; HDD under 3% book-wide | **Held** (0.00%, +1.77%) |
| P5 | EV + ASHP under 5% | **Held** (+3.3%) |
| P6 | Removing EPC alone brings the book within +-5% | **Refuted, narrowly.** It comes to +5.3% (2016 +6.2%, later +3.7%). ASHP, EV and the two heated homes carry the rest. That is why the fix below is the registry and not the multiplier |

## 2. The fix, for a build after the publish

**F1, the D48 fix (recommended).** Hand every legacy premise its own reads as its registry EAC, by the
same rule fabric premises already follow. Call `registry_eac_from_own_reads` over the legacy
`shape_fn`, across the window up to `acquisition_date`, in the loop at `run_phase2b` ~l.1923. A
legacy home has a shape for every date, so it can never fall short of 365 days.
**Trap:** `_base_profile_eac` reads `customer["eac_kwh"]`, and the loop overwrites that field. Unless
the base level reads a preserved drawn band, the per-term `shape_fn` at ~l.4320 would re-level to
the overwritten figure and stack the overlays again, putting another fifth onto **world volume**.
Keep the drawn band in its own field and level on that. F1 changes what the supplier is handed and
leaves no world kWh moving. Add a control that asserts both together: the settled volume per legacy
home is byte-identical, and the registry EAC changes.

**F2, a fidelity question (not this build; K8 page first).** The EPC multiplier is centred on C and
applied to all electricity, including that of gas-heated homes. It needs a knowledge page saying what
EPC band predicts about non-heating electricity, and it may be near nothing. Until that page exists it
stays a GAP. It does not block F1.

### Pre-registered effect of F1 (graded on the first post-publish run of the same seed and book)

| | Prediction |
|---|---|
| Q1 | Legacy realised/registry moves from +21.1% (2016) / +11.3% (later) into **[-4%, +1%]** for both, the fabric band (fabric is -2.0% / -2.4% today) |
| Q2 | Estimated electricity bills on the opening path (no actual read yet), legacy: (true-est)/true moves from **+12.6%** into **[-6%, 0%]** |
| Q3 | The same over the whole book excluding C7 moves from **+2.9%** into **[-6%, -1%]** |
| Q4 | The trailing path is unchanged within **+-0.5 pt** (-0.5% today). It already estimates from the home's own reads |
| Q5 | K1 electricity excluding C7 moves down at month ends where legacy opening runs are open: **2016-06 from +2.2% into [-4%, 0%]**; from 2017-01 onward, \|change\| <= 1.5 pt at every month end |
| Q6 | Settled electricity kWh per legacy home is unchanged (F1 is a registry change, not a volume change). Any movement refutes the build, not the prediction |

So the "fifth" lives almost entirely on the **opening path**. Once a home has been read, the company
estimates from its reads and is right to within half a point. The registry defect costs the company
its first-year estimates, first-year DD, quote and hedge for legacy homes. It does not cost the
trailing grade.

## 3. C7: is a half-hourly account with no EAC something the industry flow could produce?

**Ruling: the missing EAC is producible. HH settlement with no HH data reaching the supplier is not,
and C7 is drawn as both.**

- The commons place the EAC entirely on the **non-half-hourly** side. It is "held by the
  Non-Half-Hourly Data Collector and communicated on the **D0019** data flow, derived from the latest
  **D0010** meter reading" (`docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md` §2,
  rank 2). DESNZ describes AA/EAC as the "NHH data" (`how_far_a_settled_eac_sits_from_next_years_use.md`
  §1). An account settled half-hourly is outside the D0019 flow, so **no EAC being handed to the
  gaining supplier is what an HH-settled account looks like**, not a defect.
- HH settlement presupposes the HH data. "In order to settle customers half-hourly, suppliers need
  access to their customers' half-hourly consumption data from their smart meter", and before MHHS
  that required the domestic customer's opt-in (Ofgem decision, 25 June 2019,
  `smart_meter_hh_data_consent_2026.md` §(b)). C7 is `metering: "HH"` (`saas/customers.py`), but
  `simulation.meter_reads` draws `is_not_in_smart_mode` and `is_hard_to_read` from the id alone,
  without reading `metering`. So C7 is settled on a meter the supplier cannot read for 50 months.
  **That combination has no industry route.** An account like that is either NHH-settled, in which
  case it has a D0019 EAC, or HH-settled with the data arriving.
- **GAP, not filled.** What happens to a domestic HH-settled MPAN whose meter stops communicating:
  whether the HH data collector estimates and how long it may, and whether it reverts to NHH. That is
  BSCP502 / the HH data flows, which are not in the commons. It is named for the next reader and was
  not read here. Separately, SLC 21B's one-read-a-year duty is unanswered for any 50-month estimate
  run (D48 finding §4).

**Fix (W2, after the publish):** in `meter_reads`, a `metering == "HH"` account is a communicating
smart meter and is exempt from both persistent draws. C7, C8 and C9 are authored HH with real HH
series. The other legitimate shape, NHH with a D0019 EAC, would mean un-authoring them.
**Prediction R1:** C7's 50 estimated bills become actual, and K1 electricity from 2016-07 to 2020-02
falls onto the D48 finding's ex-C7 series (within +-4% at every month end; already shown by its P5).
**R2:** C8 and C9 move by under 1 point, because neither draws out of smart mode.
