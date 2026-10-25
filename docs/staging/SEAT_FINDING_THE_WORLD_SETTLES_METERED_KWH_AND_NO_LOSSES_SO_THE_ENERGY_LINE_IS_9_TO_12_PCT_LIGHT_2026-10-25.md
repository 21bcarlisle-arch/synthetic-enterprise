**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 4 · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day`

# The world settles metered kWh with no losses, so the supplier's energy line is about 9–12% light against a cap that includes them

**What was found (25 Oct 2026, K8 page `regional-supply-cost`).** GB settlement scales a supplier's
metered volume up to what left the grid. It does this through Line Loss Factors, Transmission Loss
Multipliers (zonal since BSC P350, 1 Apr 2018) and GSP Group Correction. Ofgem's demand-weighted
transmission-and-distribution loss multiplier for a single-rate domestic customer had a median across
the 14 regions of **1.095 in 2016/17, rising to 1.121 in 2025/26**. The range across regions and years
is 1.03–1.17. Source: Annex 3 v1.25 `3b Losses`; full table in
`docs/market_research/regional_supply_cost_under_one_national_price_2026-10-25.md` §3b.

**No code applies any of it.** A grep on 2026-10-25 over `simulation/`, `sim/`, `company/` and `saas/`
for `LLF`, `TLM`, `GCF`, `line_loss` and `loss_multiplier` finds only `company/market/llf_register.py`.
That file is reached by its own test alone, and its docstring had the domestic LLF and the nature of
TLMs wrong (corrected in the same commit as the page).

**Why it flatters the company.** The cap's wholesale allowance (DF) is scaled by each region's loss
multiplier. The regional DF ratios equal the loss-multiplier ratios to four decimals (§1 of the note).
So the revenue and price anchors carry losses, and the world's cost of energy carries none. At the cap's
own allowances, losses are (1 − 1/LM) × DF per customer. For London that is about £13/yr in Apr–Sep
2016, about £134/yr annualised at the Jan–Mar 2023 peak, and about £44/yr in Apr–Jun 2025. That is an
estimate from the cap, **not a measurement of our book**.

**Prediction, written before any run.** Applying the GB-median multiplier per charging year to the
world's settled electricity volume raises the supplier's electricity commodity cost by about 9.5–12%
in every year. The largest £ effect falls in 2022/23. It lowers electricity gross margin by that cost
and changes no count: no customer, read or bill moves.

**What it would take.** This is a baseline-world fidelity fix (W7: world first), decided without
reference to company results. W3_3's file scope already holds the settlement cost path
(`simulation/hedged_settlement.py`, `simulation/policy_costs.py`). The national uplift needs no region
key. The regional spread (4–12pp) waits on an address-to-GSP-group mapping (note §5). Before a build:
pre-register the run, then run the one-variable version.

**Reversal:** the finding changes nothing. If it proves wrong, move it to `done/` with the measurement
that refuted it.
