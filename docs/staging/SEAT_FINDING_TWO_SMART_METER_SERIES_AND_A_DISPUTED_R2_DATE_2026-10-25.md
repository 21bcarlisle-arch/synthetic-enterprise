**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** 2 · **Atom:** `EP5_settlement_true_ups`
**Knowledge:** `smart-meters-and-half-hourly-settlement` -- `docs/market_research/smart_meters_and_half_hourly_settlement_2026-10-25.md` §0

# Two smart-meter series disagree, two Elexon sources disagree on R2, and two uncalled company rules hold dates and windows the record does not

Found while turning the tariffs and smart-meter packs into Knowledge pages (seat, 25 Oct). Read from
code, not run.

1. **Smart-meter share, two homes.** `simulation/premise_population.smart_meter_penetration` (DESNZ
   Table 5a, linear 10.6% → 68.9%) is within about 5 points of the published domestic share in any
   mode (~37%, 50%, 55%, 66% and 71% at end 2019, 2021, 2022, 2024 and 2025). The second copy,
   `saas/smart_meter_rollout._PENETRATION_BY_YEAR["resi"]` (0.47, 0.60, 0.65, 0.72, 0.75 in the same
   years), is 4-10 points above the record. It is drawn by `saas/property_model.get_smart_meter_status`
   and gates `company/pricing/tou_desk.offers_tou`. Its docstring gets about 72% by dividing 34.5m
   meters (electricity and gas) by 29m households, which is not a share of anything. **Proposal:** one
   home, the world's series, read by the gate. Measure how many time-of-use offers move before
   ruling.
2. **R2 at 4 or 5 months.** `simulation/settlement_timetable.R2_MONTHS = 4` follows Elexon's 2014
   slides (`elexon_settlement_run_timetable_verified.md`). Elexon's current glossary says "5 months
   after the Settlement Period". **I cannot yet say which is current.** The SVAA calendar for a 2016-25
   year would settle it. If 5 is right, the world publishes R2 a month early. The shares and RF are
   unchanged.
3. **`company/market/mhhs_tracker.py`** holds a go-live of 5 June 2025 and shadow running from
   1 November 2024. The record: M10 on 22-24 Sep 2025, M11 on 22 Oct 2025, completion on 7 May 2027.
4. **`company/billing/exit_fee.py`** (uncalled) waives within 42 days of a fix's end. The licence
   window the tariffs pack cites is the final 49 days. It prices the fee per kWh, where every
   published fee is flat per fuel.

None of these moves a published figure today: 3 and 4 are read by no run, and 1 changes who is
offered time-of-use, not the settled volumes.
