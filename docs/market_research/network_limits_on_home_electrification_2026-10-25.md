# Network limits on household EVs, heat pumps, solar and batteries in GB: the rules, the home's own supply, the street and the time it takes

**Knowledge:** network-limits-on-home-electrification

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_NETWORK_LIMITS_ON_EVS_HEAT_PUMPS_PV_AND_BATTERIES_2026-10-25.md`
(director's chat, 25 Oct 06:44), one of two packs under the cover steer
`DIRECTOR_STEER_FLEX_AND_NETWORK_KNOWLEDGE_IS_THOROUGH_AND_THE_SIM_IS_LAYERED_2026-10-25.md`. The
steer's rule: knowledge is thorough whatever we build; the build is a minimum viable layer plus
optional layers, each with a trigger. **[derived]** is arithmetic on cited figures;
**[unverified]** is not a claim until sourced; the checks made on 2026-10-25 are in §7. Scope: GB
distribution networks at low and high voltage. Payments a DNO makes for local flexibility are on the
VPP and flexibility page; the home side of solar and batteries is on `solar-pv-and-home-batteries`.

## 0. What this project's world and company do today (read from code, not run)

- **Nothing models the network at the home.** No module in `simulation/`, `sim/` or `company/`
  holds a cut-out rating, a supply phase, a looped service, a maximum demand, the ENA
  notify-or-apply rule, a G98/G99/G100 decision or a DNO lead time (searched 2026-10-25 for
  looped, cut-out, G98, G99, ADMD; the only hit is a wind turbine's cut-out speed in
  `sim/price_engine.py:129`).
- **An EV arrives with a charger and no connection step.** `simulation/life_events.py:535-545` draws
  EV acquisition only for homes with a driveway, with a charger of 3.7, 7, 7 or 22 kW. **A 22 kW home
  charger needs a three-phase supply**, which most GB homes do not have (no published share; §2), so
  a quarter of the world's chargers are drawn at a rating few homes could connect without a chargeable
  upgrade.
- **Heat pumps and EVs install instantly.** There is no delay, refusal, upgrade cost or limiter, so
  the world cannot press back on an install offer the supplier makes.
- The company's network modules (`company/market/network_charges.py`, `llf_register.py`,
  `embedded_network_register.py`, `dso_flexibility_tender_register.py`) concern use-of-system
  charges, loss factors and flexibility tenders, not connection limits.

## 1. The process: notify or apply

### EV chargers and heat pumps (the common ENA form, v3.3)

Confirmed against the form itself (ENWL copy, accessed 2026-10-25):
https://www.enwl.co.uk/globalassets/evcp-and-hp-v3.3-ena-form.pdf

- **Connect and notify** — the installer fits the device and notifies the DNO within **28 days** — is
  allowed only if every condition holds: one additional device; a known cut-out rating; a metered
  supply; **not a looped service**; no safety concerns; maximum demand below the cut-out rating
  **and** below **13.8 kVA per phase (60 A)**, or the premises is CT-metered, or load-limited.
- Heat pumps also need a single controller, total heat-pump maximum demand **≤32 A** including boost,
  immersion and back-up heaters, and the model listed "Connect and Notify" in the ENA database.
- EV chargers on CT-metered premises: AC output ≤30% of maximum import capacity.
- V2G: total generation including PV and storage ≤**3.68 kW (16 A) per phase**, installed to G98.
- **Apply to connect** where 60 A < maximum demand ≤ 100 A: the DNO should confirm within
  **10 working days** of a complete form. Above 100 A, the guaranteed standards apply (quotation in 5
  working days for a single LV metered demand service, £20 a day late; ENWL GSoP note, Apr 2025).
- A combined heat pump and EV install, more than one device, a looped service, or generation over
  3.68 kW per phase forces an application (NGED flow-chart notes). **A bundle forces the slower route**
  **[derived from the rules]**.
- A fail-safe whole-premises load limiter holding the home at ≤60 A restores connect and notify
  (NGED).
- ENA Connect Direct (from May 2024): installer portal with instant approval for most routine
  applications; over 185,000 applications by 3 Oct 2025; covers PV, batteries and heat pumps by May
  2026. At one DNO it carried 40% of low-carbon applications by Nov 2024 (DESNZ).
- Precedents: UKPN Smart Connect approved ~57% of 1,720 EV applications instantly (2021-22); WPD
  moved to same- or next-day approval with remedials after connection (Oct 2021); SPEN aims to survey
  within 90 days, then design within 10 days, works free.

### Solar and batteries (EREC G98, G99, G100)

- **G98**: type-tested generation ≤16 A per phase (≈3.68 kW single-phase; ≈11 kW three-phase
  **[derived]**), notify within 28 days of commissioning (vendor guide citing G98 Issue 2; the 16 A
  per phase limit is confirmed on the ENA form).
- **G99**: above 16 A per phase, apply first; up to 45 working days (vendor); Fast Track at ENWL for
  ≤32 A design capacity and ≤60 A aggregate.
- **G100** export limitation: cut flow to the agreed limit typically within 15 s, at most 60 s, fail
  safe, settings locked; registered capacity follows the software limit; DC-coupled batteries count
  the inverter, AC-coupled count both (NGED).
- SPEN: PV plus storage with export locked to 3.68 kW per phase via Fast Track if total ≤7.36 kW.
- Plug-in solar up to 800 VA from 27 Aug 2026, still with a G98 notification for now (community FAQ,
  not primary).

### Customer-side installation

- IET Code of Practice for EV charging, 5th edition (12 Sep 2023), aligned to BS 7671:2018+A2:2022.
- BS 7671 Reg 722.411.4.1: a PME earth may serve an EV charger only if an open PEN cannot raise it
  above 70 V; otherwise open-PEN detection or a TT earth. This moves installer cost, not the DNO's
  decision **[derived]**.
- BS 7671 A4:2026 published 15 Jan 2026; A3:2024's prosumer and battery content **[unverified; still
  open]**.

## 2. Limits at the home

- Cut-outs: 30 A or 60 A in older homes, upgradable to 80 A (SPEN); new single-phase supplies 80 or
  100 A; SSEN treats ≤100 A per phase as typical.
- 60 A ≈ 13.8 kVA; 100 A ≈ 23 kVA; a 7 kW charger ≈ 32 A **[derived]**. A heat pump is 5-15 kW
  (~20-60 A) in ENWL's planning.
- Three-phase: most homes are single-phase; **no published GB share** (gap).
- **Looped services** (DESNZ, *Unlooping electricity network connections*, published 21 Jan 2026,
  confirmed 2026-10-25): central **3.9 million** (3.1-4.7m), **11-17%** of the housing stock, about
  14% of connections; 6-25% by anonymised DNO group; common on 1970s-80s estates, rural areas and
  terraces. This **supersedes** the older "up to 1.5m" figure, whose source was not found.
  https://assets.publishing.service.gov.uk/media/6949772372075a1d4a508a14/unlooping-electricity-network-connections-research-summary-report.pdf
- How DNOs treat a loop (same report): one DNO lets the first low-carbon device onto a 2-4 house loop
  without unlooping, which it says covers over 90% of cases; some use a load limiter and unloop
  later; three use no limiters and unloop instead.
- Cost of unlooping: industry median **£1,900** per property (Ofgem, in DESNZ); ENWL full £2,639,
  partial £943; complex jobs £10-15k. Standard unlooping is DNO-funded.
- Time: **3-12 weeks** uncomplicated; **6 months to a year** or more with neighbour disputes; the
  guaranteed standards do not apply to unlooping.
- Progress: **under 1%** of looped connections unlooped by Jan 2025; about **187,000** (~5%)
  projected by the end of ED2.
- Fuse and cut-out upgrades: free at most DNOs since Apr 2023; delays up to 30 days (UKPN) to 12 weeks
  (Octopus). **About 45% of Octopus heat pump customers needed a fuse upgrade** (Octopus written
  evidence to Parliament) **[source returned 403 on 2026-10-25; still open]**; WPD said about a
  third of homes could need upgrades (2022).
- Three-phase upgrade: ENWL average **£5,370**, chargeable; £3-7k typical (Regen/MCS); press reports
  to £15k.

## 3. Where constraints bite: the street and the substation

- After-diversity maximum demand per dwelling (NIE): detached 5.3 kVA alone, 3.0 at 100 homes;
  proposed +2.5 kVA for an EV charger and +2.5 for a heat pump. GB EV diversity: SSEN none to 20
  chargers then 0.5; WPD 0.5; UKPN 0.5 falling to 0.22 above 140; SPEN 2.5 kVA per 32 A charger.
- SPEN ADMD per home on a 300-home development: gas 1.5 kVA; gas + EV 4.8; heat pump 3.6; heat pump
  + EV 6.9; heat pump + smart EV 5.1 **[derived]**. Smart charging removed ~1.8 kVA per home.
- An LV substation costs £54k-148k; going from ~10% to 30% low-carbon devices at one site triggered a
  ~£7.5m HV substation (Scottish Government study).
- Electric Nation (673 drivers, >140,000 charges): plugged in over 12 hours on average, about three
  charges a week; at 40-70% EV uptake at least 32% of LV networks need intervention. UKPN Shift: only
  20% of plug-in time is needed.
- Regen/MCS (illustrative, not a forecast): 23% of primary substations at capacity by 2030 and 45% by
  2035 without investment. No GB count for secondary substations.
- ED2 (2023-28): £22.2bn totex, £3.2bn for low-carbon upgrades; uptake lags DFES and some secondary
  reinforcement allowances are barely used.
- Published capacity data: NGED (BSP and primary headroom only), UKPN secondary utilisation bands
  (login), SPEN per-secondary rating and peak utilisation (no headroom field), SSEN (fields not
  inspected).
- Export limits for PV and batteries are set per connection by study; no statistics on domestic
  export caps or refusals.

## 4. How DNOs manage instead of reinforcing

- Connect first, fix later (WPD 2021). Load limiters (the nearest thing to a domestic flexible
  connection). Supplier-delivered upgrades: Octopus doing UKPN fuse upgrades; an Octopus-NGED
  partnership including three-phase (2024).
- Local flexibility: NGED procured 9.8 GWh in 2024/25, 90% of registered assets domestic; delivery
  near 90%, about 6% of dispatches with no response.
- **Smart Charge Point Regulations 2021** (SI 2021/1467, confirmed against legislation.gov.uk on
  2026-10-25): charge points come with pre-set default charging hours outside peak hours, defined as
  **8am-11am and 4pm-10pm on weekdays**, which the owner may accept, remove or change; a random delay
  of up to **600 seconds** by default, capable of up to **1,800 seconds**, adjustable remotely and
  cancellable by the owner.
- Load-control licensing: Ofgem decision 7 Aug 2026; applications open 1 Mar 2027 with a 12-month
  transition; load controllers ≥300 MW enter the cyber regime; fee £1,100 or £1,650.
- LV visibility: SSEN ~19,000 LV monitors by 2027; ENWL aggregates smart-meter data by feeder with a
  minimum group of five.
- Connections reform (TMO4+) applies to generation and storage ≥1 MW, not homes.

## 5. What it means for a supplier selling EVs, heat pumps, PV and batteries

- **Cost to the household**: since 1 Apr 2023 (Access SCR) LV demand pays only extension assets, with
  a £1,720/kVA high-cost cap; generation pays reinforcement at the connection voltage, capped at
  £200/kW. In practice fuse, cut-out and unlooping work is free at most DNOs; three-phase is the main
  paid item (£3-7k).
- **Delay is the real cost**: notify, none; apply 60-100 A, ~10 working days; fuse upgrade up to 30
  days to 12 weeks; SPEN survey up to 90 days; unlooping 3-12 weeks or 6-12 months disputed; G99 up
  to 45 working days.
- Refusals for demand are rare; the outcome is "connect plus remedial work" or "connect with a
  limiter". For PV and batteries the risk is an export cap.
- Regional differences: looped share 6-25%; three-phase charging; survey lead times; first device on
  a loop; supplier-delegated fuse upgrades.

## (a) Process map

| Asset | Threshold | Process | Typical time / cost |
|---|---|---|---|
| EV charger | MD ≤60 A per phase, one device, known cut-out, not looped | notify within 28 days | none; free |
| EV charger | 60 A < MD ≤ 100 A | apply | DNO answer in 10 working days; fuse upgrade free at most DNOs |
| EV charger | MD >60 A held to ≤60 A by a fail-safe limiter | notify | limiter cost to the customer |
| Heat pump | ≤32 A incl. back-up, one controller, ENA-listed, MD ≤60 A | notify within 28 days | none |
| Heat pump | >32 A, unlisted, or MD >60 A | apply | 10 working days; upgrade up to 12 weeks |
| Heat pump + EV / >1 device | any | apply | as above |
| Any device on a looped service | looped | apply; unloop or limiter | 3-12 weeks (6-12 months disputed); £1,900 median, DNO-funded |
| Three-phase upgrade | needs >100 A single-phase | new connection quote | quote 5 working days; ~£5,370 (ENWL), £3-7k |
| PV / battery | ≤16 A per phase, type-tested | G98 notify within 28 days | none |
| PV + battery | export locked ≤3.68 kW per phase, total ≤7.36 kW (SPEN) | G99 Fast Track + G100 | ~20 business days (vendor) |
| PV / battery | >16 A per phase | full G99 | up to 45 working days; possible export cap |
| Plug-in solar | ≤800 VA | G98 notify (for now) | from 27 Aug 2026 |

## (b) Population checks for the world

1. Looped share 11-17% nationally (central ~14%), 6-25% by DNO group.
2. Under 1% unlooped by Jan 2025; ~5% by 2028.
3. About a third to 45% of heat pump installs need a supply upgrade (WPD; Octopus, the latter still
   open at source).
4. Instant approvals near UKPN's ~57% for EVs (2021-22) are plausible; 100% is not.
5. Fuse-upgrade delays with a tail to about 12 weeks; unlooping with a tail to 6-12 months.
6. ADMD ~1.5-3 kVA with gas heating, ~6-7 kVA with a heat pump and unmanaged EV, ~5 kVA with smart
   charging.
7. At 40-70% EV uptake, at least 32% of LV networks need intervention.
8. Reinforcement charged to domestic demand after Apr 2023 near zero except above £1,720/kVA.
9. EV charging needs ~20% of plug-in time.
10. Domestic flexibility delivery ~90%, ~6% no response.

## (c) What the world would need to hold, in layers

- **Minimum viable (L0)**: per home, DNO region, cut-out amps (30/60/80/100), phase, a looped flag
  and loop size; a deterministic notify-or-apply rule engine; delay and cost drawn from the published
  distributions. The supplier sees install lead time and conversion loss.
- **L2**: DNO-specific policies (first device on a loop, limiters, three-phase charging, supplier
  fuse upgrades) and G98/G99/G100 export logic.
- **L3**: a feeder and secondary-substation layer on ADMD, where street clustering drives remedial
  work and export caps follow voltage headroom.
- Flexibility markets and smart-charging defaults (L1, L4) and the DNO planning loop (L5) as in the
  cover steer.

## 7. Verification of the pack's [unverified] items (2026-10-25)

| Item | Outcome | Source |
|---|---|---|
| BS 7671 A3:2024 added prosumer and battery provisions | still open | IET/BSI content not read |

Counts: 1 item; 0 confirmed, 0 corrected, 1 still open. Figures the pack read through summaries or
vendors, re-read at primary source the same day: **confirmed** — every ENA form threshold above
(28 days, 60 A / 13.8 kVA, 32 A, 30% CT, 3.68 kW / 16 A per phase, 10 working days, looped service
excluded); the DESNZ unlooping figures (3.9m, 3.1-4.7m, 11-17%, £1,900, under 1%, ~187,000, 3-12
weeks, 6 months to a year, over 90% first device on a loop, three DNOs with no limiters); the Smart
Charge Point Regulations' peak hours and delays, with the nuance that the default hours are pre-set
and the owner may change them. **Still open** — Octopus's 45% fuse-upgrade share (parliament.uk
returned 403).

## Named gaps

1. GB share of homes on three-phase supply; distribution of cut-out ratings.
2. A national rate of EV or heat pump installs that trigger an upgrade (only Octopus 45% and WPD a
   third).
3. A GB count of secondary substations or LV feeders needing reinforcement by 2030 or 2035.
4. Statistics on domestic G99 export caps or refusals.
5. Original source of "up to 1.5m looped" (superseded by DESNZ's 3.9m).
6. Network findings of DESNZ Heat Pump Ready and UKPN Heat Street.
7. Electric Nation's per-EV diversified peak kW.
8. Any DNO right to interrupt domestic devices directly.
9. BS 7671 A3/A4 content; SSEN and NPg secondary datasets; NGED-Octopus partnership terms.
