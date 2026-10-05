# EV, solar and batteries as products: what a GB supplier gains, loses and can see

**Knowledge:** ev-solar-and-batteries-as-products

*Written 2026-10-05 for step 1 of the director's priority canon
(`docs/staging/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`). That canon places this area in
step 5 and describes it as "converting customers, avoiding losses when they get the kit,
generating leads for it, and giving them the ROI case". Every figure below is either cited or
marked **GAP**. The sources were read on 2026-10-05.*

**How the sources are graded.** **[P]** means I read the figure in the primary publication.
**[S]** means it came from a secondary report or a search summary that quotes the primary, which
I did not open myself because the fetch was refused or I did not attempt it. An [S] figure is
evidence, not an anchor. Before any constant cites one, someone has to open the primary.

---

## 1. Definitions and relationships, before any split

### 1.1 The three products are three different physical things

| Product | What it does to the meter | What it does to the half-hourly shape |
|---|---|---|
| **EV** (with or without an EV tariff or smart charging) | Adds import. Nothing is exported unless the household has vehicle-to-grid, which is negligible in 2016–2025. | Adds a large block that can be moved. Where it lands depends on the **tariff and the charger, not on owning the car** (see §2.1). |
| **Rooftop solar PV** (export paid under the FiT before April 2019, and under the SEG from January 2020) | Cuts import by the self-consumed share and creates **export** through a separate export registration. | Removes daytime import and creates midday export. The household cannot move it in time. |
| **Home battery** | Is not a source of energy in its own right. It moves energy in time, from solar or from the grid. | Moves import from the peak into stored solar or off-peak grid charging. With the right tariff it can also move export. |

The three get bundled together, and they should not be. **An EV adds import and solar removes
it.** A battery is a time-shifter whose value depends wholly on the tariff. A supplier relationship
that is good for one product can be bad for another.

### 1.2 The supplier relationships (one row each, per product)

| Relationship | EV | Solar | Battery |
|---|---|---|---|
| **R-a: the customer adopts on their own; the supplier just supplies** | The supplier **gains** import volume, mostly at the evening peak if the customer stays on a flat tariff (§2.1). | The supplier **loses** import volume, mainly in daytime hours. If it is the export supplier it gains export to buy, and the export registration can sit with a different supplier. | The supplier loses import at the peak, and the net effect on its book depends on the tariff. |
| **R-b: the supplier sells, installs, or takes a lead fee** | Charger sale or install, or a car lease bundle (for example a salary-sacrifice and tariff pack). | Panel sale or install, or a referral to an installer. | Battery sale or install, often alongside solar. |
| **R-c: the supplier offers a tariff that monetises the kit** | An EV tariff: a cheap overnight window, or smart dispatch of the charger. | An export tariff (SEG): **tied** (only for its own import customers) or **untied**. | A ToU import tariff with a ToU export tariff, so the battery can arbitrage. |

**R-a is a cost the supplier did not choose.** R-b is a product line with its own capital and
margin. **R-c is the only one of the three that uses a supply licence**, so it is the only one
Poesys as a supplier can do natively.

### 1.3 Who can adopt is not the same as who has the kit

Tenure and the physical house limit adoption before preference does.

- **Solar by tenure (England, English Housing Survey 2023-24) [S]:** about 1.5 million dwellings
  (6%) had PV. By tenure, **7% of owner-occupied, 5% of social-rented and 2% of private-rented**
  dwellings had it. In 2015 it was 4% overall, split 5% owner, 3% social and 1% private.
  Social-rented homes are much closer to owner-occupied than private-rented ones are, because
  housing associations installed PV at scale under the FiT ("rent-a-roof").
- **EV charging access:** around **30–35% of households have no off-street parking** (RAC
  Foundation and EHS, via Energy Systems Catapult) [S]. About one EV driver in five has no home
  charger [S]. Without a home charger, an EV adds nothing to the supplier's import, so for the
  supplier that household is not an EV household.
- **Batteries** do not need a roof, but in 2016–2025 almost all of them were installed alongside
  or after solar (§2.3).

**Definition used throughout:** an "EV household" for a supplier means **a household that charges
a plug-in vehicle through its own meter**. That is not the same thing as a privately registered
EV. A company car charged at home on salary sacrifice counts. A private EV with no driveway does
not.

---

## 2. Scale, product by product

### 2.1 EV

| Quantity | Value | Source |
|---|---|---|
| New BEV registrations | 2024: **381,970 (19.6% of the market)**. 2025: **473,348 (23.4%)**. | SMMT annual releases [S, quoting SMMT] |
| Private buyers' share of new BEVs | **24.5%**, so fleet and business buyers dominate | SMMT ("Record EV market share but weak private demand") [S] |
| BEVs in the licensed car parc | **about 4% of cars at end-2024** | DfT Vehicle Licensing Statistics 2024, as quoted by Milliman [S]. The primary table is DfT `VEH0142` (plug-in cars by keepership: private or company). |
| Plug-in cars, August 2026 | about 3.36M, of which about 2.18M BEV and about 1.16M PHEV | Zapmap [S] |
| **Households with an EV, by year** | **GAP**: DfT does not publish it. VEH0142 gives cars by keepership, not households, and company-kept cars can charge at home. | — |
| Annual home charging energy | **1,800–1,900 kWh/yr for cars with 0–25 kWh batteries and about 3,500 kWh/yr for cars over 35 kWh** | Electric Nation (WPD/EA Technology, 2017–19, about 700 participants) [S] |
| When unmanaged home charging happens | Plug-in peaks at **17:00–19:00 on weekdays**. Charging peaks at about 25% of cars at 19:00 and is typically 15–20% from **19:00 to 22:00**. | Electric Nation [S] |
| Share of charging done at home | about 80% | various, secondary [S] |
| Customers on a smart ToU **EV** tariff | 243k (Jan 2024), then **502k (Jan 2025)**, then **653k (Jul 2025)**. All smart ToU: 395k, then 664k, then 835k (**2.8% of the domestic market**). | Ofgem *State of the market* (Apr 2025 and Jan 2026) [S, quoting Ofgem] |
| Intelligent Octopus Go | **156k EVs at FY24 and 278k at FY25** (April year end) | Octopus Energy Group Annual Report FY25 [S] |
| EV owners on standard (flat) rates for home charging | 46% (survey of about 300 owners) | Smart Home Charge survey via EV Powered [S, small sample] |
| Smart Charge Points Regulations 2021 | Since 30 June 2022, new home chargers ship **with default** charging outside 08:00–11:00 and 16:00–22:00 on weekdays, plus a randomised delay. **The owner can override the default.** | SI 2021/1467 [P from prior knowledge; the statutory text was not re-read in this pass] |

**What this establishes.** **Whether EV load sits at the evening peak or overnight depends on the
tariff and the charger, not on owning the car.** Unmanaged, it peaks between 19:00 and 22:00.
On an EV tariff with smart dispatch, it moves overnight. Ofgem's 653k EV-tariff customers, against
a fleet of roughly 1.5–2M plug-in cars charged at home, put tariff take-up among EV households at
about **a third to a half**. That is an order-of-magnitude reading, not a figure, because the
denominator above is a GAP. This answers the open question on the knowledge map's "EV smart
charging bifurcation" row.

**GAP:** the share of EV kWh that lands off-peak on an EV tariff. No published per-tariff figure
was found. Electric Nation shows that a ToU price plus app-based smart charging moves "most" of
it, without giving a number.

### 2.2 Rooftop solar

| Quantity | Value | Source |
|---|---|---|
| UK solar PV sites at year end (all sizes) | 2016: 877,422. 2017: 922,377. 2018: 992,958. 2019: 1,036,759. 2020: 1,072,261. | DESNZ solar deployment, via Statista and Wikipedia [S] |
| New installations per year (all sizes) | 2017: about **45k**. 2018: about 71k (a rush before the FiT closed). 2019: about 44k. 2020: about 36k. 2023: about **197k**. 2024: about **191k**. 2025: about **255k** (+37%). | Year-on-year differences in DESNZ site counts. 2023–25 from DESNZ via pv-magazine and Solar Power Portal [S]. |
| MCS-certified solar installs | 2024: **184,462**. 2025: **267,032**, which beat the 2011 FiT-boom record by 31%. | MCS annual statements [S, quoting MCS] |
| Domestic installations | about 1.55M of about 1.80M total (May 2025), which is about 30% of capacity | DESNZ via Solar Power Portal [S] |
| All installations, March 2026 | about 2.0M | DESNZ [S] |
| Installed cost, 0–4 kW, median per kW (DNC basis) | 2019/20: **£1,481**. 2020/21: £1,500. 2021/22: £1,732. 2022/23: **£2,250**. 2023/24: £2,263. 2024/25: £1,884. 2025/26: **£1,780**, which DESNZ says is the lowest on record in real terms. | DESNZ *Solar PV cost data* (from the MCS Installation Database), via solar4good [S] |
| VAT | 0% on residential solar and batteries from 1 Apr 2022 (to 31 Mar 2027). Batteries retrofitted on their own were zero-rated from 1 Feb 2024. | HMRC [P from prior knowledge; not re-read] |
| **Self-consumption, measured** | **45% of generation (855 kWh/yr) across 302 PV homes.** Regression for a 4,000 kWh/yr home with 2.9 kWp: **966 ± 38 kWh/yr self-consumed, cutting grid import by 24%**. | McKenna, Pless & Darby (2018), *Energy Policy* 118:482–491 [S, abstract read] |
| Self-consumption, as advice assumes | 35% without a battery and 70% with one (an EST-style assumption) | Octopus "Solar savings explained" [S] |
| FiT (pre-2019) export | Unmetered generators are *deemed* to export **50%** and are paid on that. The scheme closed to new applicants on **31 Mar 2019**. | Ofgem FiT [P from prior knowledge] |
| SEG Year 5 (Apr 2024–Mar 2025) | **270,395 installations registered (99.98% PV), 1,585 MW, 443.1 GWh exported, £56.97M paid, 11 licensees, 50 tariffs** (21 open to all, 29 restricted). Year 4: 166,022 installations, 283.1 GWh, £30.75M. | **Ofgem SEG Annual Report Year 5 [P]** |
| SEG average rates, Year 5 | offered average 10.80p/kWh. **Tied tariffs 15.39p, untied 4.47p.** Top rate 40p. | Ofgem via Solar Power Portal [S; these averages were not in the primary text I fetched] |
| SEG, implied average paid | **£56.97M ÷ 443.1 GWh = 12.9p/kWh** (Year 4: 10.9p) | Arithmetic on [P] figures. **Both are totals over every SEG generator, so this is a genuine average price.** |
| SEG export per *domestic* installation | **Cannot be divided out.** The 443 GWh includes non-domestic generators up to 5 MW. The average registered capacity is 5.9 kW, which is above a typical 3.5–4 kW home. | — |
| SEG rules | From 1 Jan 2020, licensees with 150,000 or more domestic customers must offer an export tariff, with a rate **above zero at all times**. It covers installations up to 5 MW (MCS-certified for PV) and needs metered export, in practice a smart meter. | SEG Order 2019 and Ofgem SEG guidance [P from prior knowledge] |

**Pattern 2016–2025:** a FiT-subsidy tail (2016–2019) gave way to a **trough of about 35–45k a
year** (2019–2021). Then the **crisis step-change** came: about 190–200k a year in 2023–24 and
about 255–267k in 2025. That step was driven by bill levels, not subsidy. Because the SEG
replaced the FiT, export income became something the market sets. Retailers now compete on it,
and tied export tariffs pay three times what untied ones do.

### 2.3 Home batteries

| Quantity | Value | Source |
|---|---|---|
| MCS-certified battery installs | 2022: **269**. 2023: about **5,000**. 2024: **17,551–20,550** (sources differ). 2025: **about 41,000**. | MCS via pv-magazine, Solar Power Portal and UKEM [S] |
| DESNZ battery count | more than 22,000 domestic batteries Apr 2024–Mar 2025, total domestic capacity above 400 MWh | DESNZ via Solar Power Portal [S] |
| Attach rate to new solar | estimates run from **"over 30%" to about 94%** | Solar Power Portal "attachment rate far greater than thought" and installer commentary [S]. **These cannot both be true.** |
| Installed cost | adding a battery costs about £2,000–4,000 extra | Octopus and EST-style advice [S] |
| **Stock of home batteries, by year** | **GAP.** Batteries did not need MCS certification for the SEG until recently, so MCS counts before 2023 are a floor, not a measure. | — |
| How batteries operate | **GAP (published).** No GB-wide measured split between solar-only charging and grid charging on ToU was found. | — |

### 2.4 Heat pumps

Heat pumps are out of scope for this page. The code bundles them with EVs (§6), but heat pumps
belong with heating.

---

## 3. The ROI case

| Case | Payback | Source and what it is sensitive to |
|---|---|---|
| Solar only, EST | **9–13 years**, depending on location and daytime occupancy | EST solar guide (July 2023) [S] |
| Solar only, 2026 secondary estimates | 6–9 years. Example: a £6,500 4 kW system returning £900–1,100 a year. | Secondary aggregators [S, low grade] |
| Solar plus a 9.5 kWh battery | 8–9 years on a £10,300 system | Secondary [S, low grade] |
| EST annual savings with SEG | London £900–930, Manchester £740–810, Stirling £680–740. Without SEG: £200–330, £190–310 and £180–290. | EST via search summary [S]. **Suspect:** the gap between the two implies export income of about £500–600 a year, which at about 12p/kWh means 4,500+ kWh exported. A 3.5–4 kW home cannot do that. **Do not use these figures until the primary has been read.** |

**What the payback is sensitive to (structural; follows from the definitions):**

1. **The import unit rate**, because each self-consumed kWh saves the full retail rate. The
   2022–23 crisis roughly doubled the value of self-consumption, which is consistent with the
   installation step-change in §2.2.
2. **The export rate.** On the Year 5 averages, tied pays 15.39p and untied 4.47p, a factor of
   3.4. For a home that exports about 55% of its generation, the export rate decides a large share
   of the return. **The household's export rate is a choice of supplier**, and that is where the
   supplier enters the household's ROI.
3. **Self-consumption**, measured at 45% (McKenna 2018). It is higher with daytime occupancy and
   with a battery.
4. **Install cost**, which was flat in nominal terms from 2019/20 to 2020/21, peaked in 2022/23
   to 2023/24, and has fallen since.

**GAP:** published sensitivity curves, meaning payback as a function of the export rate and the
self-consumption share from one consistent source. Which? publishes calculators but no stated
table was found.

---

## 4. What a supplier loses, and what it can recover

**Solar, under R-a.** The supplier loses about **24% of a typical PV home's import**, roughly
900–1,000 kWh a year (McKenna 2018), and that loss is concentrated in daytime hours. **The
standing charge is not lost.** Under the cap, the supplier's margin on a kWh is the EBIT
allowance, a small percentage of the bill (see `what-a-customer-is-worth` and the cap pages). So
**the margin lost on the volume is small, of the order of pounds per year.** That is an
inference from the cap structure, not a published figure. **The real exposure is the customer
leaving:** 29 of the 50 SEG tariffs in Year 5 were restricted, and tied tariffs average 3.4 times
untied ones. So **a solar household is a target for competitors' tied export tariffs.** "Avoiding
losses when they get the kit" is mainly a **retention** problem, not a volume problem.

**Solar, what can be recovered.** The supplier can recover value in two ways. It can be the
export supplier, buying export at the SEG rate and receiving that energy into its own settlement
position, where it is worth the midday wholesale price. Or it can offer a tied SEG tariff as a
retention lever. **The net cost of SEG is (SEG rate − the wholesale value of midday export).** It
is not the gross SEG payment, so an untied 4.47p tariff can be cash-positive for the supplier. A
tied 15.39p tariff transfers value to the customer and is paid for out of import margin. Under
the mission's first rule, that is a transfer, not value created, unless it keeps a customer who
would otherwise leave.

**EV, under R-a.** The supplier **gains** about 1,800–3,500 kWh a year (Electric Nation). On a
flat tariff that volume lands mostly 19:00–22:00, so the supplier buys it at peak wholesale and
peak network cost and sells it at the flat rate. The **margin per kWh on peak EV load can be
negative** against a flat retail price. *(Direction is inferred from the price shape. The size
of this is a GAP to be measured on the project's own Elexon panel.)*

**EV, under R-c.** The EV tariff creates value by moving 19:00–22:00 load overnight. The value is
**the wholesale and network peak/off-peak spread multiplied by the kWh moved**, plus any
flexibility revenue (Octopus reports 1 GW of EV batteries under smart dispatch in 2024 [S]). That
is value **created**, and the tariff discount is the **sharing** of it. This is the cleanest
"create, then share" case in the whole area.

**Battery.** On a solar-only dispatch it cuts peak import (a loss of peak volume) and export
(less SEG to pay). On ToU grid charging it moves import into off-peak periods, which is value
created by the same mechanism as the EV tariff.

**GAPS:**
- What a supplier earns from an installation lead fee or a referral. No published rate was found.
- Margins on supplier-installed kit (R-b). Supplier annual reports do not break them out, at
  least in the documents searched.
- Churn rates of kit owners against non-owners. None published.

---

## 5. What a real supplier can see, and what it cannot

| Observable | Seen? | How |
|---|---|---|
| An export MPAN and export registration | **Yes**, when the customer registers for export with this supplier | The DNO issues a separate export MPAN. Export can be registered with a **different** supplier from import. |
| Export reads, half-hourly | **Yes**, once SEG-registered with a smart meter | Smart meter export register via the DCC. Export MPANs settle half-hourly. |
| MCS certificate (kWp, install date) | **Yes**, at SEG application | Required evidence for SEG eligibility |
| FiT generation-meter reads | **Yes**, if the supplier is that installation's FiT licensee | FiT quarterly generation reads |
| Solar *generation* and self-consumption for a SEG-only or unregistered home | **No.** It sits behind the meter, so only net import and export are seen. | Can only be inferred from the half-hourly import shape (a daytime dip on sunny days) |
| PV on the house, before any registration | **Partly.** The public EPC register records PV, but an EPC is only made at sale, letting or a measure. | Public EPC register (company-knowable) |
| EV ownership | **No direct signal.** It is seen if the customer declares it at EV-tariff signup or the charger or car is integrated for smart dispatch. | Otherwise inferred from half-hourly import (3.7–7 kW evening or overnight blocks) |
| Charger installation | **No.** Notification goes to the DNO, not to the supplier. | — |
| Battery | **No.** A G98/G99 notification goes to the DNO. | Seen only as a changed import/export shape, or by integration |
| Tenure, roof orientation, off-street parking | **No.** Partly inferable from public data (EPC built form, OS/aerial data), all at the property, not the household. | — |

**Before any of this crosses the seam:** export registration and export reads are the **only
first-class observables** in this whole area. Every other signal is an inference from the import
shape, which the company is allowed to get wrong.

---

## 6. What our code does (discovery, 2026-10-05)

### The world (`simulation/`, `sim/`)

- **Adoption is generated by life events.** `simulation/life_events.py` draws Bernoulli trials
  each year:
  - `solar_install`, using `_SOLAR_INSTALL_PROB_BY_YEAR` (0.23–0.40%/yr) and a kWp drawn from
    U(2.5, 4.5).
  - `battery_installed`, only for homes that already have solar, using
    `_BATTERY_INSTALL_PROB_WITH_SOLAR_BY_YEAR` (0.2% in 2016 rising to 4.5% in 2025), sized
    U(4, 13.5) kWh.
  - `ev_acquired` (0.1% to 1.6%/yr).
  - `heat_pump_installed`.

  Two eligibility rules apply. Solar is restricted to non-flat homes whose roof does not face
  north. Tenure multipliers (`population_draw.low_carbon_adoption_eligibility_multiplier`;
  director-asserted private_rent 0.1 and social_rent 0.25 for solar) scale the rates. The
  initial stock is deterministic: **every `rural_detached` home has solar and no other home
  does** (`simulation/household.py:409-412`).
- **`simulation/adoption_geography.py`** fits logistic S-curves for EVs and heat pumps (EV anchors
  0.3% in 2016 to 6% in 2024, ceiling 0.90) and a regional tilt. **It has no production
  importer. Only its own tests import it.**
- **Solar in the demand shape** is in `simulation/run_phase2b.py:507-568` and
  `simulation/demand_model.py:1015-1140`. Generation is irradiance (from
  `sim.weather_engine.half_hourly_solar_irradiance`, keyed on latitude and cloud) × **a fixed
  `SOLAR_KWP = 3.5`** × 0.85. **That ignores the household's own drawn kWp.** Import is then
  `max(0, load − generation)`. **Export is floored away. The world generates no export volume,
  no export MPAN and no export registration** (the docstring says "export is out of scope for this
  sub-phase").
- **The battery** (`_battery_daily_dispatch`, `run_phase2b.py:463`) charges only from excess solar
  and discharges at 16:00–20:00, with 90% round-trip efficiency. **It never charges from the grid,
  whatever the tariff.**
- **EV load is counted twice.** When `has_ev` is true, `dynamic_assets` sets `assets["ev"]`. Then
  `build_demand_shape` adds `EV_CHARGING_KWH_PER_NIGHT = 8.0` kWh across 00:00–04:00, which is
  **2,922 kWh/yr**. After that, the "Phase P" block in `run_phase2b.py:590-599` adds
  `household.ev_annual_kwh()` = 7,500/3.5 = **2,143 kWh/yr** on top, 90% of it overnight. **The
  total is 5,065 kWh/yr per EV household. Measured 2026-10-05 by calling `build_demand_shape`
  with `ev` set false and then true (+8.0 kWh/day), and reading `ev_annual_kwh`.** The published
  range is 1,800–3,500 (§2.1). The `build_demand_shape` block is also multiplied by the EPC
  multiplier, which scales a car's charging by how well the house is insulated.
- **EV timing ignores the tariff.** Both blocks put about 90–100% of EV energy overnight for
  **every** EV, citing the Smart Charge Points Regulations. Those regulations set a default the
  owner can override, and the observed unmanaged peak is 19:00–22:00 (§2.1). **So the world hands
  every EV household the off-peak shift that only an EV tariff earns in reality.**
- **Demand response** (`simulation/demand_response.py`) applies only to customers on ToU: a 15%
  peak-to-off-peak shift, +12% with an EV and +8% with a heat pump, read from the **static**
  property `assets`, not from the dynamic life-event EV flag.

### The company (`company/`, `saas/`)

- **The ToU offer is live:** `company/pricing/tou_desk.py` → `company/interfaces/tou_offer.py` →
  `run_phase2b.py:3415`. **Every customer with a smart or HH meter is put on ToU, with no choice
  step.** The pair is fixed at 1.5× peak and 0.786× off-peak (a 1.91:1 ratio, from
  `saas/tariff_pricing.py:111`), with peak at 07:00–11:00 and 16:00–20:00. For comparison, real
  smart ToU take-up was 2.8% in July 2025, and real EV tariffs run about 3:1 or more.
- **There is no EV tariff, export tariff or battery tariff.**
  `company/crm/ancillary_products.py` lists `EV_TARIFF` at £0/month and `SOLAR_MONITORING` at
  £4/month. **Nothing reaches it.**
- **The SEG and export stack is complete and unreached.** These modules have **zero production
  importers** (checked by grep 2026-10-05; only tests import them):
  - `company/regulatory/seg_book.py`
  - `company/regulatory/seg_export_estimator.py` (W1_28's banded PV yield lives here)
  - `company/billing/seg_portfolio.py`
  - `company/billing/smart_export.py`
  - `company/market/prosumer_balance_register.py`
  - `company/market/ev_demand_forecast.py`
  - `company/crm/decarb_recommender.py`

  `company/billing/seg_register.py` is imported only by `company/billing/fit_legacy_register.py`,
  which is itself unreached.
- **One subject has three SEG rate tables that disagree.** For 2024:
  - `seg_book` says **4.8p**
  - `smart_export` says **8.5p**
  - `seg_portfolio` says **12.0p**

  The published Year 5 averages are 10.80p offered and 12.9p paid, with untied at 4.47p and tied
  at 15.39p. `seg_book`'s docstring calls SEG "a direct cost on the supplier's P&L". That ignores
  the wholesale value of the exported energy the supplier receives (§4).
- **One subject has four EV kWh figures:**
  - 2,143 (`simulation/household.py`)
  - 2,922 (`simulation/demand_model.py`)
  - 5,065 (what the run actually applies)
  - 3,500–4,000 (`company/market/ev_demand_forecast.py`, unreached)
- **One subject has two self-consumption figures:** 0.50 without a battery and 0.70 with one
  (`seg_export_estimator`, citing a "BEIS 2022 UK Household Solar Report" that this pass did not
  find), against 45% measured (McKenna 2018).
- **Discovery of kit:** `company/crm/property_discovery.apply_tariff_registration` (EV or solar
  revealed at tariff signup) is reached only through `home_registry.record_tariff_registration`,
  and **nothing calls that**.
- **ROI:** `decarb_recommender` has solar at £5,500 with savings of £370/yr (a 14.9-year payback)
  and a battery at £4,500 with savings of £200/yr. These are single constants with no tariff,
  export-rate or self-consumption dependence, and the module is unreached.
- **ToU instruments:** `tools/tou_sharing_ceiling.py` and `tools/tou_extreme_day_concentration.py`
  bound the value of a generic load-shifting ToU from the Elexon panel. They are the right
  measuring stick for an EV tariff's value created, but neither has an EV-specific load block.

### How the code's adoption rates compare with the published record

Imputed national installs = the code's annual probability × 28.4M × the non-solar share. This is
an upper bound for the code, because the code applies the rate to eligible homes only.

| Year | Code (upper bound) | Published new installs | Published ÷ code |
|---|---|---|---|
| 2017 | about 76k | about 45k | 0.59 |
| 2018 | 68k | 71k | 1.04 |
| 2019 | 62k | 44k | 0.70 |
| 2020 | 68k | 36k | 0.53 |
| 2023 | 107k | 197k | **1.83** |
| 2024 | 102k | 191k | **1.87** |
| 2025 | 94k | 255k | **2.72** |

The published counts include non-domestic sites, which are about 10% by count. With that caveat,
**the shape is inverted in the period that matters.** The code has solar adoption *falling*
from 2023 to 2025, while the real market rose by about 37% in 2025, and it puts the post-crisis
level at roughly half of reality.

---

## 7. Gaps, in rank order

1. **EV load is counted twice and is the same for every tariff in the world.** This is a defect,
   not a knowledge gap. Removing the double count needs one choice of kWh from the published
   1,800–3,500 range, not a new number.
2. **The world has no export.** There is no export volume, no export MPAN and no registration
   event, so the company's whole SEG stack has nothing to read and stays unreached.
3. **The world's solar adoption is the wrong shape after 2022** (§6 table). The battery
   install rate cannot be checked because no published battery stock exists before 2023.
4. **Tenure factors.** The asserted social_rent factor of 0.25 for solar sits against EHS stock
   shares of 5% social and 7% owner, a ratio of about 0.7. *A stock ratio is not an adoption-rate
   ratio, so this argues against the 0.25 without replacing it.*
5. **The ToU shift fraction** in `demand_response.py` is 15% base for every smart-meter customer.
   The knowledge layer's settled Arcturus opt-out function gives about 1–2% at the code's own
   1.91:1 ratio (`docs/market_research/domestic_shift_response_arc.json`). Two parts of the
   tree disagree here, and nothing links them.
6. **Published gaps:** households with an EV by year; the off-peak share of EV kWh on an EV tariff;
   how batteries operate; lead-fee and referral rates; how kit owners churn; the EST savings
   figures (suspect, §3).

---

## 8. What this says about the order of work

The canon invites proposals backed by evidence. There are three. None of them reorders the
steps; each puts something inside an earlier step.

1. **Fix the EV double count inside step 2 (billing accuracy), not in step 5.** Every EV household
   in the world consumes about 5,065 kWh/yr of EV load against a published 1,800–3,500, so the
   world over-generates and the company bills energy that would not have been used. Step 2's
   premise is that the world generates what is billed the way it arises in reality. Step 3
   (forward CLV) would learn from these inflated EV volumes. It is a one-module world-fidelity
   repair with no company-results input, so it is legal under the baseline/curriculum split.
   *Evidence: §6, measured 2026-10-05.*
2. **Within step 5, EV, solar and batteries rank last, and the step needs world work first.**
   Against the canon's test "whether the world contains what it needs yet", it does not:
   - there is no export to buy or settle;
   - EV timing is the same whatever the tariff, so an EV tariff can create no value the world does
     not already grant for free;
   - batteries cannot arbitrage;
   - nothing crosses the seam to reveal that a customer has kit.

   Three world pieces are needed:
   - export generation with an export registration observable;
   - EV charging timing that depends on tariff and charger;
   - battery dispatch that depends on tariff.

   **The EV-timing piece should come before any further work on the live ToU desk**, because
   today's ToU book is credited with an EV shift the world hands over without a tariff.
3. **Step 6 (forward simulation) already depends on this area.** The canon names "adoption that
   builds over years" as the reason forward runs could add value. `life_events._annual_prob`
   clamps to the 2025 rate forever, while the S-curve module (`adoption_geography`) that would
   carry adoption forward is unwired. Under "build nothing that forecloses forward simulation",
   when the adoption tables are re-anchored (gap 3), they should be fitted to a curve that can
   extrapolate, not extended as a lookup table.

One more point is about framing, not order. **"Avoiding losses when they get the kit" is mostly a
retention problem, not a volume problem** (§4). That puts its lever next to the per-customer
retention decisions of step 4. Its evidence is the ratio of tied to untied SEG rates and the 29
restricted tariffs.

---

## Sources

- Ofgem, *Smart Export Guarantee Annual Report, April 2024–March 2025*:
  https://www.ofgem.gov.uk/transparency-document/smart-export-guarantee-annual-report-april-2024-march-2025 [P]
- Solar Power Portal on the Ofgem SEG Year 5 tied/untied averages:
  https://www.solarpowerportal.co.uk/solar-pv/300-increase-in-support-for-small-renewable-generators-under-smart-export-guarantee-ofgem-says [S]
- Ofgem, *State of the market report* (April 2025):
  https://www.ofgem.gov.uk/sites/default/files/2025-04/OFG2296_State%20of%20the%20Market%20Report.pdf ;
  (January 2026): https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf [S via summaries]
- Octopus Energy Group, *Annual Report FY25*:
  https://octopusenergy.group/static/documents/OEGL_Financial_statements_Annual_Report_FY25.pdf [S]
- SMMT, 2025 full-year market release:
  https://www.smmt.co.uk/uk-new-car-market-breaches-two-million-as-almost-one-in-four-buyers-go-electric/ ;
  private demand: https://www.smmt.co.uk/record-ev-market-share-but-weak-private-demand-frustrates-ambition/ [S]
- DfT, *Vehicle licensing statistics data tables* (VEH0142):
  https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables ;
  the 4% BEV-share quote: https://uk.milliman.com/en-GB/insight/electric-vehicles-risk-and-opportunity-uk-insurers [S]
- Zapmap EV market statistics: https://www.zapmap.com/ev-stats/ev-market [S]
- Electric Nation (WPD / National Grid), *The real-world smart charging trial*:
  https://commercial.nationalgrid.co.uk/downloads-view-reciteme/34180 ; electrive summary:
  https://www.electrive.com/2019/07/29/electric-nation-smart-charging-research-grid-is-fine/ [S]
- EV Powered / Smart Home Charge survey:
  https://evpowered.co.uk/news/survey-finds-almost-half-of-ev-owners-miss-out-on-off-peak-charging-rates/ [S]
- Energy Systems Catapult, on-street parking and EVs:
  https://es.catapult.org.uk/report/on-street-parking-and-electric-vehicles/ [S]
- DESNZ, *Solar photovoltaics deployment*:
  https://www.gov.uk/government/statistics/solar-photovoltaics-deployment ; site counts as
  quoted at https://en.wikipedia.org/wiki/Solar_power_in_the_United_Kingdom ; 2025 total:
  https://www.solarpowerportal.co.uk/energy-policy/uk-solar-capacity-approaches-19-gw-milestone [S]
- DESNZ solar cost data, as quoted at
  https://solar4good.co.uk/blogs/solar-panel-costs-uk-government-data-2026/ [S]
- MCS: https://mcscertified.com/uk-rooftop-solar-installations-hit-record-high/ ;
  pv-magazine: https://www.pv-magazine.com/2025/06/18/uk-rooftop-solar-installations-surge-new-battery-storage-record-set/ [S]
- Batteries: https://www.solarpowerportal.co.uk/energy-storage/desnz-over-22-000-domestic-batteries-installed-in-past-year ;
  https://www.solarpowerportal.co.uk/battery-storage/uk-battery-attachment-rate-far-greater-than-previously-thought- ;
  https://www.ukem.co.uk/solar-battery-storage/news/uk-home-battery-installations-record/ [S]
- McKenna, Pless & Darby (2018), "Solar photovoltaic self-consumption in the UK residential
  sector", *Energy Policy* 118:482–491:
  https://discovery.ucl.ac.uk/id/eprint/10047969/1/McKenna%20PV%20self-consumption%20in%20UK%202018%2005%2008.pdf [S, abstract]
- English Housing Survey energy reports (PV by tenure):
  https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1091144/Energy_Report_2020_revised.pdf [S]
- Energy Saving Trust, solar guide: https://energysavingtrust.org.uk/advice/solar-panels/
  (fetch refused, 403) [S]
- Octopus, "Solar savings explained": https://octopus.energy/blog/solar-savings/ [S]
