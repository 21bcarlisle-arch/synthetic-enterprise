**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas)

# FINDING — the same id mismatch is live at writer 3, so no gas renewal is ever repriced for unprofitability

Fixing the value arm's record filter (`observed_account_state`, landed today) closed ONE of two
sites in the renewal rate chain that read the settled book under the billing-account id. The other
is still open, and it is the same defect with the same cause:

```
company/pricing/renewal_rate_chain.py:303   renewal_unit_rate_uplift(account_id=billing_account, …)
company/crm/customer_profitability.py:305   compute_profitability_uplift(account_id, …)
company/crm/customer_profitability.py:156   if r.get("customer_id") == cid
```

`simulation/run_phase2b.py:1539` passes `household_of(cid)`; both settlement writers stamp the
SUPPLY POINT. Measured on a two-leg book whose gas leg is net-negative and whose electricity leg is
not:

```
estimate_prior_term_net_margin('C1g', …, commodity='gas')  -> -60.0   <- the leg's own book
estimate_prior_term_net_margin('C1',  …, commodity='gas')  -> None    <- what the chain asks
compute_profitability_uplift('C1',  …, commodity='gas')    ->   0.0   <- writer 3, every time
compute_profitability_uplift('C1g', …, commodity='gas')    ->   5.0
```

So writer 3 — the supplier's own policy of repricing net-negative accounts — has never fired on a
gas renewal and cannot, whatever the gas book says. It returns `0.0`, which is also its answer for
"this account is profitable", so the run output cannot tell the two apart. `NET_NEGATIVE_UPLIFT` is
a rate the supplier charges; a policy that is structurally unreachable on half the book is a
pricing claim we do not have.

## Why it was not landed with the value arm's fix

Attribution. Writer 3 runs BEFORE the value arm in the same chain and its uplift enters the
`locked_unit_rate` the arm then prices against, so fixing both in one pass would move the arm's
realised delta for two reasons at once and neither could be attributed. The arm's fix is being
measured one-variable right now against `value_cycle_ab_gas_admitted_2026-09-07.json` (world digest
`39a192ce04c1eda8`). Writer 3 needs its own pair, from whatever that run leaves as the new BEFORE.

## What the fix is, and what it is not

The same one line: match a record to the account the way the supplier BILLS it —
`_billing_account_id(r["customer_id"]) == cid` (`saas/customer_reaction.py`) — not by string
equality, and emphatically not by `simulation.household.household_of`, which is the world's fact
about the property and must stay free to disagree with the supplier's grouping.

Predicted before the run, kept here to be refuted: the count of `profitability_uplift` entries
rises from its electricity-only level, and the realised delta between arms moves by LESS than the
value arm's own fix did — writer 3 is a flat `NET_NEGATIVE_UPLIFT_GBP_PER_MWH` on a subset, not a
per-customer search. If the entry count does NOT rise, no gas leg in this world had a net-negative
prior term, and that is the finding instead.

## The control that would have caught it

`tests/company/pricing/test_value_arm_in_the_renewal_chain.py::test_every_commodity_the_arm_prices_can_reach_its_own_book_under_the_billing_account`
is the class control for the value arm's half. Writer 3 has no equivalent: nothing anywhere asserts
that a renewal the chain reprices can see the book it settled itself. The fix should bring one, over
the same `_WORLD_LEG_ID` map, so a third commodity cannot arrive uncovered.
