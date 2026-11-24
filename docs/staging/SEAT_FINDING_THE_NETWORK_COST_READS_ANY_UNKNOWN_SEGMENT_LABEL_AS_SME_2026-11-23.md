**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome`

# The network cost reads any unknown segment label as SME, silently

`simulation.policy_costs.get_electricity_network_cost_per_mwh(date, segment)` checks `segment ==
"resi"` and `segment == "I&C"`, and sends **every other string** to the SME volume table. It never
passes through `simulation.segment_vocabulary.normalise_segment`, which knows `"domestic"`,
`"residential"`, `"sme"` and `"ic"`, and raises on anything it does not know.

**What it has already cost.** The hedge-cost probe behind 059b3632ee passed `"domestic"`. That
priced a residential strike on 75 £/MWh of network cost where the cap allowance is 42.4 (2023-07),
or 69 against 29.0 (2024-07). The result was a published ±3.2% match between a six-month ladder and
the market's cheapest fix, which was false. It is corrected in db2f502b2, on the knowledge page
(`cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §7).

**Live risk, not measured.** The production callers pass a variable segment:
`simulation/renewals.py:311`, `simulation/hedged_settlement.py` (three sites),
`simulation/competitor_reference.py:293` and `simulation/live_population.py:1170`. If any of them is
ever handed a lower-case alias (`"ic"`) or a company-book label (`"iandc"`, a `CompanyBookLabel`),
it reads SME's network cost with no error. Whether any run reaches that today **I cannot yet say**.

**Proposed fix.** Canonicalise at the top of the function with `normalise_segment(segment)`. That
fails closed: a book label raises, an unknown label raises, and `"domestic"` reads residential. Do
the same in the sibling readers in `policy_costs.py` that branch on segment. First run one
2016–2018 whole run under the change, to establish no caller passes a label that would now raise.
