**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `front-door-proof-strip-stories-and-no-js-render`

# The opex ledger counts 165 households where the final-year book holds 227

*Delivery seat, 2026-10-22, choosing the household figure for the front door's proof strip.*

**What was measured.** On the 19 Oct publish run (`run_output_8b6fea024_20261019T033010Z.json`, the
shared tree's `docs/reports/`), `_final_year_active_ids` returns 392 fuel accounts. 165 of them end in
`g`. With the `g` suffix stripped (`saas.opex_ledger._household_base_id`) they come to **227 distinct
households**, so every gas account in 2025 sits in a home whose electricity account is also on the book.
The published `site/data/dashboard.json` `opex_ledger.household_count` reads **165**, and
`book_annual[-1]` reads 227 electricity and 165 gas accounts.

**Why it matters.** `benchmark_opex_per_household_gbp` (£307.10) and `true_opex_per_household_gbp` are
divided by that count. If 227 is right, both are overstated by 227/165, about 1.38 times. No served page
renders `opex_ledger` today (a grep of `site/**/*.html` and `*.js` finds no reader), so this is LATENT,
not a false public claim.

**Why `_check_population_consistency` stays green.** Its assertion (2) compares `household_count` with
`_resi_household_ids_from_active(active_ids)`, and both sides go through the same
`saas.customers.get_customer(cid)` resi filter. A filter that drops a set of ids drops them from both
sides, so the check cannot see it. The new proof strip counts resi from the run's own
`customers.lifetime[cid].segment` instead, and gets 227.

**I cannot yet say which ids drop out.** The candidates, unranked: `get_customer` does not resolve the
campaign wins (`OCC-*`) or successor occupants, or it resolves only one leg of a drawn household. Note
that 165 equals the gas-leg count exactly, which may or may not be a coincidence. The one-variable test:
run `_resi_household_ids_from_active` on this run's active ids with `SE_DRAW_POPULATION=1`, and list
every id for which `get_customer` returns `None` or a non-`resi` segment.
