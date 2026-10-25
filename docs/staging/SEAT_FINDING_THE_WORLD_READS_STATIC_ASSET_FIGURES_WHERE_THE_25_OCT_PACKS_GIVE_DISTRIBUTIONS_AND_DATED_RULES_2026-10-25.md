# The world reads static asset figures where the 25 Oct packs give distributions and dated rules

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

*Delivery seat, 2026-10-25, from drafting the 21 Knowledge pages behind the director's asset and
advice-roadmap steers. Read from code, not run. The full code reads, with file and line, are on each
page's research note; `docs/design/PERSONALISED_ASSET_WORLD.md` §10 lists the asset ones.*

## The four "now" items in the advice-roadmap steer, and where each stands

1. **Gas typical consumption (TDCV).** Ofgem's medium gas value fell from 11,500 to 9,500 kWh on
   1 Jul 2026 (confirmed at source, 25 Oct). A dated table already exists:
   `company/billing/annual_consumption_estimate.py::TDCV_BY_DATE`. Some places still read a single
   value. `company/market/market_report.py:107-108` uses 3,100 kWh electricity and 11,500 kWh gas
   for every year, which is the 2015 electricity value beside the 2023 gas value.
   `simulation/competitor_reference.py:156` (`TDCV_DUAL_FUEL_MWH = 14.2`) and
   `company/finance/bad_debt_provision.py:145` (`CAP_LEVEL_KWH`) each say why they use one basis.
   The volatility and cost fork reports that the 2026 bands are applied to 2016-25 in three places.
   Dating them is a fidelity fix, and it is not done here.
2. **EV uplift.** The director's 06:03 steer replaces this item. The +8% is a symptom, not a number
   to correct. The world adds a fixed 2,143 kWh a year per EV (7,500 miles at 3.5 mi/kWh,
   `simulation/household.py:283`). The company assumes 2,500 (`company/crm/property_model.py:128`).
   "Driveway" means detached or semi-detached (`household.py:431`). Explore's +8% comes from
   `tools/generate_customer_reaction_chain.py:57`, which compares three months before with three
   after. **I cannot yet say** why that reads +8% when both paths add about 180 kWh a month. The fix
   is the generative EV in the design note, step 8. Patching the constant to a band would not fix it.
3. **Economy 7.** There are no two-rate meters in the run. Restricted meters were 14-17% of
   electricity accounts in 2015-20, and the multi-rate TDCV is now dated on the knowledge layer. The
   steer keeps this item under the same rule: a two-rate meter is an attribute of a home with
   storage or other off-peak load, and the share is the population check. Not built here.
4. **Dated rules in the forward years.** Zero VAT on GB domestic electricity runs from 1 Oct 2026
   to 31 Mar 2027, confirmed at HMRC (Revenue and Customs Brief 10 (2026)) on 25 Oct.
   `company/compliance/domain_invariants.py:1238` `vat_rate_for_segment` returns 5% for all
   domestic supply, with no date and no fuel. The volatility fork reads `renewal_rate_chain` as
   understating the ex-VAT electricity cap by about 4.8% from 1 Oct 2026. That date lies outside
   2016-25, so no current run is wrong, but every forward year is. The commons amendment (a dated
   exception in `uk_vat_rates.json`) is drafted in `/var/tmp/kdrafts/gap_closure/amendments.md` A6
   and not yet landed.

## Other static figures the packs show are wrong in kind

- **Heat pumps.** Every heat-pump home gets a fixed 5,500 kWh in settlement
  (`simulation/household.py:84`), while the physics derives its own figure.
- **Heating schedule.** Once-a-day heating is given a 6-8.5 h block (`fabric_physics.py:1127`),
  but the survey median is 15 h.
- **Boilers.** The boiler has no flow temperature, and a new boiler runs at 0.90 efficiency, above
  every in-home measurement.
- **Setpoint.** It never moves after 2022: the 2022 response scales whole-fuel use instead of
  turning the thermostat down.
- **Solar PV.** Output uses a fixed 3.5 kWp (`simulation/demand_model.py:1017`), whatever size was
  drawn. Every non-flat roof is labelled east_west.
- **Batteries.** They charge only from solar surplus.
- **The world's "NBP" gas price.** It is a monthly TTF proxy at a fixed 1.28 $/£, and it moves on
  116 of 3,538 days. It has no daily or weekly volatility, which the forward-years volatility steer
  needs.
- **Fuel and capex prices.** There is no petrol or diesel price series anywhere. Retrofit capex is
  four fixed figures in every year.
- **Company advice copy.** It claims a smart thermostat saves 10-15%, where measured savings are
  0-6%. It prices insulation at 30% of fabric heat, above every measured median.

## What closes it

Most of these items are step 8 (the personalised asset world) in `docs/direction/priority_order.yaml`.
That step comes after the basics and the forward years, and nothing here jumps the order. Three
items are fidelity defects in the world as it stands today:

- the NBP proxy's missing daily volatility, which step 6 (forward years) needs;
- the undated VAT reader;
- the market report's mixed-basis TDCV.

Each of these three should be drawn on its own as a fix.

## Status, 2026-10-25 (delivery lane `three-dated-rule-fidelity-fixes-from-the-25-oct-packs`)

- **VAT:** the commons now carries amendment A6 (`dated_exceptions`, with `rate_band` added so a
  reader can price it). `vat_rate_for_segment(segment, fuel=, on=)` honours it, and
  `cap_ceiling_ex_vat` passes both. The remaining undated readers are filed in
  `SEAT_FINDING_SIX_VAT_READERS_STILL_ASK_NO_DATE_AND_THE_WORLDS_OWN_IS_UNDATED_2026-10-25.md`.
- **TDCV:** `market_benchmark` reads `tdcv_kwh(..., "MEDIUM", 1 July of the year)`.
- **NBP:** recorded, with the 116-of-3,538 count measured, in
  `SEAT_FINDING_THE_WORLDS_NBP_IS_A_MONTHLY_TTF_PROXY_SO_EP16_CANNOT_FIT_DAILY_GAS_VOLATILITY_2026-10-25.md`.

Everything else here is step 8 and stays open.
