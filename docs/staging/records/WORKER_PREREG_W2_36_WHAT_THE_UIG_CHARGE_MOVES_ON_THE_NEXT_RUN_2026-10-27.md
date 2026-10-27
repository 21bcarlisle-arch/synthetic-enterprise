**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Prediction, filed before any run: what charging Unidentified Gas moves (2026-10-27)

**The change.** `simulation.gas_settlement.run_gas_term` now multiplies each gas day's wholesale cost
by (1 + the cap period's UIG allowance), `simulation.policy_costs.get_gas_uig_uplift`. The values
come from Ofgem's Annex 2 v1.30, rows 31 and 38: 2.00% to Mar 2022, then 1.82%, 1.83%, 1.92% and
1.86% for credit legs. A default-tariff leg priced as prepayment takes the PPM row: 5.34% in
Apr–Sep 2022 and 8.19% in Oct 2022–Sep 2023. Before 2019 the world uses a stated belief of 2.00%.
Knowledge: `docs/market_research/unbilled_energy_and_revenue_assurance.md`, "The cap's own UIG
allowance".

**Predictions, for the first fresh run whose base carries this commit, against the run before it:**

1. **P1, direct.** Each settled gas row's `gas_uig_cost_gbp` equals `wholesale_cost_gbp × u/(1+u)`.
   Summed over the run, gas wholesale cost rises by 1.8–2.1% in every calendar year except
   2022 and 2023. In those two years the prepayment default-tariff legs lift it to 2.0–3.0%.
   The upper bound assumes prepayment is at most 15% of gas kWh.
2. **P2, margin.** Gas gross margin falls by the summed UIG cost, to within the feedback in P3.
   Electricity's settled rows are byte-identical.
3. **P3, feedback: I cannot yet say its size.** Realised portfolio margin feeds the renewal
   rate chain (`company/interfaces/renewal_rate_chain.py`: the realised-margin recovery surcharge
   and the unprofitability uplift). Gas renewal rates may therefore rise a little, and churn and
   counts may move. To attribute anything beyond P1, run the one-variable arm: the same seed and
   base with `get_gas_uig_uplift` returning 0.
4. **P4, the cap tests.** No default-tariff rate moves past the cap because of this commit. The
   charge reaches cost, not the rate. The curtained validator's above-cap count is unchanged.

**What refutes it.** P1 outside 1.8–3.0% in any year, any electricity row changed, or a P4 breach.

**Reversal.** Revert the commit. The artefact and the knowledge section can stay: they are reads
of published data.
