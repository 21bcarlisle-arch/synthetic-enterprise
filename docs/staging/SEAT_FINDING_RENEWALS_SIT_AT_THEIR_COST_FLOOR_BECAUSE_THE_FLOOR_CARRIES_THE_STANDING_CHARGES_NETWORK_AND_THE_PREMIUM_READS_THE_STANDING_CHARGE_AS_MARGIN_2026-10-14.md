**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** acquisition-and-retention-economics -- the published basis is Ofgem's cap construction as the commons already holds it (`docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json`, `ofgem_cap_standing_charges.json`; knowledge map rows "Cap formula" and "Network charges (electricity)")

# Renewals sit at their cost floor because the floor carries the network cost the standing charge recovers, and the portfolio premium reads the standing charge as margin (2026-10-14)

**Fate (2026-10-14):** ATOM -- fix 1 is `B12_writer_one_reads_its_margin_on_the_unit_rate_so_a_renewal_floor_is_its_true_unit_cost` and fix 2 is `W3_3_the_network_charge_splits_per_unit_and_per_day`, both minted at L0 build; the save is re-graded after B12. The save-offer page §8 is rewritten on this frame.

**Decision: (b), a definitional defect, not (a).** The renewal price is not loss-making in the world. A renewal at its floor still collects the standing charge, about GBP 187 a year ex-VAT in 2025, and nothing in the floor counts that. Two definitions are wrong, and together they put the price on the floor:

1. **The floor counts the network cost the standing charge already recovers.** The electricity floor is `company_fwd + locked_policy + locked_network` (`run_phase2b._price_match_inputs`, the save's floor and the competitive ceiling's). `locked_network` is `simulation.policy_costs._NETWORK_COST_RESI_SME_BY_YEAR`, which is Ofgem's whole per-customer network allowance divided by 3.1 MWh ("£/customer/yr ÷ 3.1 MWh", per the table's own comment). That is GBP 69/MWh in 2024-25. By Ofgem's construction the cap splits each cost into a nil-consumption allowance (the standing charge) and a per-kWh allowance (the unit rate). The fixed network share, including the TNUoS residual moved to fixed charges by the TCR in April 2023, sits in the standing charge. The company bills that standing charge too: `_ELEC_SC_PENCE_PER_DAY_BY_YEAR` reproduces Ofgem's nil-consumption total to the penny.
2. **Writer 1 learns from a margin that counts the standing charge as profit.** `hedged_settlement` adds `sc_per_period` to both revenue and margin. The term's `net_margin_gbp` deducts no cost to serve. So the portfolio book reads a realised margin rate of 18-20% (median) against its 8% target (`PORTFOLIO_TARGET_MARGIN_RATE`). It then takes the full -5% (`PORTFOLIO_PREMIUM_MIN`) off nearly every renewal. That cut is larger than the strike's headroom over the floor (GBP 2 margin plus a capital charge of 2.2-4.5), so `_floor_a_discount` stops each renewal on the floor.

The competitive ceiling (SVT x 0.97-1.02) **never binds** on these rows. It sits GBP 20-60/MWh above the floor.

## The table, at real inputs

Seed 61109 is printed below. The artefacts are `/var/tmp/floor-recount-out/sv-k1-611{09,10,11,12}.json` at d55598dd6, the last per-renewal log for these seeds. The regrade3 artefacts at 5e5358092 (`/var/tmp/regrade3/out/rc-*`) keep totals only, so the held rows cannot be read from them. The script is at the foot of this file. Units are GBP/MWh ex-VAT. `strike` = fwd + capital + 2 + policy + network (`price_fixed_tariff`). `w1 -5%` = the strike after writer 1's full discount. The default is `cap_ceiling_ex_vat`. The best deal is the default x (1 - the published gap). The cap's non-commodity figure is the unit rate x (1 - the commodity share), from Ofgem's own model (direct debit). SC is pence per day.

| cust | fuel | start | renewal | fwd | capital | policy | network | floor | strike | w1 -5% | comp. ceiling | default | best deal | cap unit | cap non-commodity | SC co / cap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 326 | gas | 2024-07-05 | 42.77 | 27.66 | 1.02 | 0.04 | 14.30 | 42.00 | 45.02 | 42.77 | - | 52.19 | 50.26 | - | - | 28.57 / - |
| 433 | elec | 2024-09-17 | **194.15** | 66.89 | 2.48 | 58.26 | 69.00 | **194.15** | 198.62 | 188.69 | 228.07 | 212.95 | 205.07 | 213.08 | **109.01** | 57.11 / 58.62 |
| 038 | elec | 2025-02-05 | **238.30** | 111.04 | 4.11 | 58.26 | 69.00 | **238.30** | 244.41 | 232.19 | 253.19 | 236.76 | 221.85 | 236.72 | **114.97** | 51.23 / 59.57 |
| 045 | gas | 2025-02-08 | 62.14 | 49.29 | 1.82 | 0.02 | 14.30 | 63.61 | 67.44 | 64.07 | - | 60.38 | 56.58 | - | - | 29.58 / - |
| 128 | elec | 2025-03-13 | **213.05** | 85.79 | 3.18 | 58.26 | 69.00 | **213.05** | 218.23 | 207.32 | 253.19 | 236.76 | 221.85 | 236.72 | **114.97** | 51.23 / 59.57 |
| 179 | gas | 2025-04-11 | 63.23 | 54.04 | 2.00 | 0.00 | 14.30 | 68.34 | 72.35 | 68.73 | - | 66.57 | 57.25 | - | - | 29.58 / - |
| 227 | elec | 2025-05-12 | **251.06** | 120.89 | 4.47 | 61.17 | 69.00 | **251.06** | 257.54 | 244.66 | 275.30 | 257.43 | 221.39 | 257.42 | **123.36** | 51.23 / 49.63 |
| 264 | elec | 2025-05-28 | **211.90** | 81.73 | 3.03 | 61.17 | 69.00 | **211.90** | 216.92 | 206.08 | 275.30 | 257.43 | 221.39 | 257.42 | **123.36** | 51.23 / 49.63 |

`fwd` is the floor minus the two published locks the world hands the desk (`renewals.py`), so it is derived, not logged. **On all four seeds: 21 of 21 held electricity renewals sit at the floor to the penny**, and on every one `w1 -5%` is below the floor. The 7 gas rows are not on the floor. Three sit below it: the unfloored risk-tier cut, which `5c137eb5b` has since floored. Gas has no competitive ceiling and no standing-charge-shaped network split here: `get_gas_network_cost_per_mwh` is unit-only.

**The number that decides (b) over (a).** The floor's policy plus network is GBP 127.3-130.2/MWh. Ofgem's cap unit rate carries only 109.0-123.4 of non-commodity cost in total, and that already includes the cap's per-kWh share of opex, EBIT and headroom. Measured the same way, the floor's non-commodity could not exceed the whole cap allowance, and here it exceeds it by 6.8-18.3. **On 12 of the 21 rows, the market's best published deal sits below the company's floor.** In 2025-Q1 the best deal was GBP 221.85 against a floor of 238.30. A floor that the cheapest suppliers in the market were beating is not counting a variable cost. It is counting a fixed cost on volume.

## What a floor counts, from published evidence first

- **No rule sets a renewal floor.** SLC 22B and the Ofgem decisions in `a_save_offer_against_the_switching_rules_and_the_seam.md` §7 name "no price formula, no floor, no ceiling". The financial-resilience rules (capital floor, adjusted net assets) bind the balance sheet, not a tariff's price. A floor is the supplier's own commercial rule, and its content is a definition.
- **The published definition of which cost the unit rate carries is the cap's construction.** For each component, the per-kWh allowance is the benchmark-consumption allowance minus the nil-consumption allowance, and the nil column *is* the standing charge (Ofgem's Default Tariff Cap level model v1.31, as read into the commons). The knowledge map states the consequence: "The standing charge carries the network residual the unit rate then does not." Its "Network charges" row already lists the TCR 2023 shift as "not fully modelled".
- So the floor of a unit rate is the per-kWh cost: commodity at the term's hedge, per-kWh policy and per-kWh network. The fixed network share is recovered once, through the standing charge.

## Where the defect lives: both sides of the wall

- **World (fidelity, decided blind to company results):** `hedged_settlement` charges `get_electricity_network_cost_per_mwh x consumption`, the whole allowance on volume, and adds a cap-sized standing charge as revenue. For a 3.1 MWh household the network total is about right. For any other household it is wrong, and the fixed share is charged on volume. This is a world finding for the sim lane. It is not the company's to fix, and it moves settlement.
- **Company:** (i) the floor follows the world's per-MWh lock, because that is what the published network schedule hands it. Once the world splits the schedule, the floor follows by construction. (ii) **Writer 1's margin rate counts the standing charge with no cost to serve against it.** That is the company's own definition and is fixable now: a margin compared with a target margin must be measured after the cost the standing charge exists to recover. Otherwise every book with a standing charge reads as over-earning, and the premium will discount to the floor whatever the floor is.

## Interconnection: on origin the save and writer 1 now read two different floors

Since `2026-10-13` (the capital-inclusive floor, which 5e5358092 carries), writer 1 stops at `pre_margin_unit_rate` = fwd + capital + policy + network. `_price_match_inputs` still hands the save fwd + policy + network. **Prediction, filed before any run and not measured here:** at origin, held electricity renewals sit GBP 2.2-4.5 above the save's floor, not on it. Where the best deal is below the floor (12 of 21 rows above), the match offers the save's floor. So on a re-run of seed 61109 at origin HEAD, the save makes at least 1 offer, where it made 0 at d55598dd6. If it is still 0, this account of the mechanism is incomplete. Either way, one supplier with two floors is the shape this project has paid for before. The fix gives the save the same floor as writer 1.

## The fix this implies, in order (not built here)

1. **Company, now:** writer 1's realised margin rate is measured on the unit-rate margin, with standing-charge revenue counted net of the cost to serve it recovers, or it is compared with a target defined on the same basis. Knowledge page first (K8): what the 8% target counts against the cap's EBIT allowance (`price_cap_ebit_allowance.md`). Then the save takes `pre_margin_unit_rate`, one floor.
2. **World, separately:** the electricity network schedule is split into the per-kWh allowance and the nil-consumption allowance, following Ofgem's model and the TCR in April 2023. Settlement charges the fixed share per supply point per day. The renewal floor then follows by construction. This needs its own knowledge page and pre-registration. It moves every settled figure, so it is not bundled with (1).
3. The save is re-graded only after (1). Until then, its inertness says nothing about the save's design.

## Script

```
PYTHONPATH=. python3 /var/tmp/floor-recount-out/floor_table.py /var/tmp/floor-recount-out/sv-k1-61109.json
```
It reads each held row's `price_match_inputs`. It recomputes policy and network from `simulation.policy_costs` at the term start (the same published calls `renewals.py` hands the desk), takes fwd = floor - policy - network, and reprices the strike through `saas.tariff_pricing.price_fixed_tariff` with `renewal_desk.NAKED_FRACTION`. It reads the ceiling from `renewal_desk._competitive_ceiling_gbp_per_mwh`, and the default and gap from `save_offer`. A copy of the script is kept beside the artefacts at `/var/tmp/floor-recount-out/floor_table.py`.
