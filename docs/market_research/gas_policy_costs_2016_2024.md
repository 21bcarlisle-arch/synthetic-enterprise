# Gas Policy Costs — Derivation and Sources (2016–2024)

**Phase 30b Research** | June 2026

Covers three gas-side obligation year (OY) charge streams that are distinct from
the electricity-side policy stack (RO, CfD, CM, FiT, CCL-electricity). All use
the same April-to-March obligation year convention.

---

## 1. Gas Climate Change Levy (CCL)

### Scope
Applies to non-domestic gas supply only. **Domestic (resi) gas is CCL-exempt** — this
is the key difference from electricity CCL which has no domestic exemption.

### Source
HMRC Environmental Taxes Bulletin, Table 1 — "Climate Change Levy rates"
(published annually). Primary authoritative source, H confidence.

### Rate Schedule

| OY start | Rate (£/MWh) | Rate (p/kWh) | Note |
|----------|-------------|-------------|------|
| 2016/17  | 1.95        | 0.195       | HMRC Table 1 |
| 2017/18  | 1.98        | 0.198       | |
| 2018/19  | 2.03        | 0.203       | |
| 2019/20  | 3.39        | 0.339       | **Budget 2016 rebalancing begins** — large step |
| 2020/21  | 4.06        | 0.406       | |
| 2021/22  | 4.65        | 0.465       | |
| 2022/23  | 5.68        | 0.568       | |
| 2023/24  | 6.72        | 0.672       | |
| 2024/25  | 7.75        | 0.775       | **Parity with electricity CCL** |

### Key policy note: the 2019 step-change
The large increase from £2.03 to £3.39/MWh in 2019 was announced in **Budget 2016**,
not Budget 2019. The policy rationale: electricity CCL was being raised faster than
gas CCL, creating incentive distortions for gas over electricity in commercial
heating decisions. HMRC announced a schedule to bring gas and electricity CCL rates
to parity by 2024/25 — which is exactly what the table shows.

### Implementation in sim
`get_gas_ccl_per_mwh(date_str, segment)` — returns 0.0 for segment="resi", looks up
by OY start year for all other segments. Clamps to 2016 floor and 2024 ceiling.

---

## 2. Gas Network Charges (GDN + NTS)

### Scope
Gas Distribution Network (GDN) and National Transmission System (NTS) charges.
Applies to **all segments** (domestic and non-domestic). No per-meter standing charge
component here — all on unit rate convention (unlike electricity which has standing
charges).

### Source
Derived from Ofgem price cap network percentage share × cap unit rates (all-inclusive
p/kWh). **M confidence** — not directly from Ofgem Annex 9 (gas network annex is
Excel-only, not HTML-navigable). Cross-checked against published Ofgem cap breakdowns.

RIIO-GD2 (Ofgem's gas distribution price control 2021-2026) and the SOLR cost
socialisation in 2022 both appear in the rate trajectory.

### Rate Schedule

| OY start | Rate (£/MWh) | Note |
|----------|-------------|------|
| 2016/17  | 9.9         | ~26% of typical 3.8 p/kWh gas cap |
| 2017/18  | 9.9         | stable |
| 2018/19  | 9.6         | slight decrease |
| 2019/20  | 10.0        | |
| 2020/21  | 9.0         | low wholesale prices → low cap unit rate → lower implied network |
| 2021/22  | 10.3        | RIIO-GD2 commences |
| 2022/23  | 11.0        | SOLR cost socialisation begins |
| 2023/24  | 17.6        | **large step** — RIIO-GD2 year 2 upward reset + full SOLR pass-through |
| 2024/25  | 14.3        | partial reversal as SOLR costs normalise |

### Key note: 2023 step-up
The £17.6/MWh peak in 2023/24 reflects two simultaneous factors:
1. RIIO-GD2 allowed revenue upward reset (Ofgem's December 2022 redetermination)
2. Full pass-through of 2021/22 SOLR (Supplier of Last Resort) costs being
   socialised across the distribution network charge base

### Implementation in sim
`get_gas_network_cost_per_mwh(date_str)` — no segment exemption. Clamps to
2016 floor and 2024 ceiling.

---

## 3. Green Gas Levy (GGL)

### Scope
Applies to **all segments** (domestic and non-domestic). This is a per-meter
(MPRN) charge per day — **not a per-kWh charge** — introduced to fund the
Green Gas Support Scheme (GGSS), the successor to Renewable Heat Incentive (RHI).

### Source
DESNZ (Department for Energy Security and Net Zero) GOV.UK guidance:
"Green Gas Levy rates". **H confidence** — primary government source.

### Levy Start Date
**30 November 2021** — GGL first collected by HMRC. Before this date, GGL = 0
for all customers and dates.

### Rate Schedule (per MPRN per day, in pence)

| OY       | p/meter/day | £/meter/year | Note |
|----------|------------|-------------|------|
| 2021/22  | 0.576      | 2.10        | Nov 2021 start; OY 2021 rate also applies 2022/23 |
| 2022/23  | 0.576      | 2.10        | same rate (same tranche of GGSS spend) |
| 2023/24  | 0.122      | 0.45        | **sharp drop** — fewer GGSS projects commissioned than expected |
| 2024/25  | 0.105      | 0.38        | continued decline |

### Normalisation to £/MWh
Because GGL is per meter per day (not per kWh), it must be normalised using
the customer's annual quantity (AQ):

```
ggl_per_mwh = annual_rate_per_meter / (aq_kwh / 1000)
```

This gives:
- `ggl_per_mwh × daily_mwh = annual_rate_per_meter / 365`

which is correct — each day contributes exactly 1/365th of the annual meter levy,
regardless of daily consumption (the meter charge doesn't scale with kWh consumed).

### Why the 2023/24 drop?
The GGSS (Green Gas Support Scheme) attracted fewer biomethane injection projects
than BEIS modelled when setting the 2022 levy rate. Lower committed spend →
lower levy required to fund it. DESNZ publishes updated rates annually as part
of GGSS budget reconciliation.

### GGL vs RHI
The RHI (Renewable Heat Incentive, 2014-2022) was funded differently — from
general taxation, not a gas levy. GGL is specifically a gas bill levy, collected
by the HMRC through gas suppliers.

### Implementation in sim
`get_ggl_per_mwh(date_str, aq_kwh)`:
- Returns 0.0 if `date_str < "2021-11-30"`
- Returns 0.0 if `aq_kwh <= 0`
- Looks up OY by year; returns 0.0 for OYs with no GGSS spend (post-2024 TBD)
- Normalises daily rate: `annual_rate_per_meter / (aq_kwh / 1000)`

---

## Policy Cost Stack Summary

For a resi dual-fuel customer in 2023/24:

| Charge | £/MWh | Applies to resi? |
|--------|-------|-----------------|
| Gas CCL | 0.0 | No — domestic exempt |
| Gas network | 17.6 | Yes |
| GGL (at 11,500 kWh AQ) | 0.039 | Yes |
| **Total gas policy** | **~17.64** | |

For a non-domestic (SME) gas customer in 2023/24 (15,000 kWh AQ):

| Charge | £/MWh | Note |
|--------|-------|------|
| Gas CCL | 6.72 | Non-domestic pays |
| Gas network | 17.6 | All segments |
| GGL (at 15,000 kWh AQ) | 0.030 | All segments |
| **Total gas policy** | **~24.35** | |

---

## Implementation Reference

| Function | File | Returns |
|----------|------|---------|
| `get_gas_ccl_per_mwh(date_str, segment)` | `simulation/policy_costs.py` | 0.0 for resi; OY rate for SME/I&C |
| `get_gas_network_cost_per_mwh(date_str)` | `simulation/policy_costs.py` | OY network rate for all segments |
| `get_ggl_per_mwh(date_str, aq_kwh)` | `simulation/policy_costs.py` | Normalised £/MWh; 0 before Nov 2021 |

Gas settlement records (`simulation/gas_settlement.py`) include:
- `gas_ccl_gbp` — per day gas CCL cost (0 for resi)
- `ggl_gbp` — per day GGL levy
- `gas_policy_cost_gbp` = CCL + GGL
- `gas_network_cost_gbp` — per day network charge
- `net_margin_gbp` deducts `gas_policy_cost_gbp + gas_network_cost_gbp` from gross margin
