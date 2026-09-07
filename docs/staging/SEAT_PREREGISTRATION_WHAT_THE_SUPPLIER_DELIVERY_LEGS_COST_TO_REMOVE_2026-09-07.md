**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a52-the-supplier-holds-no-delivery-obligation

# PRE-REGISTRATION: what removing the supplier-side delivery legs will and will not move

**Written:** 2026-09-07, delivery seat, claim `a52-the-supplier-holds-no-delivery-obligation`,
BEFORE running any suite or gate against the change.

## The decision this fixes in advance

`company/regulatory/capacity_market.py` carries `delivery_status`, `shortfall_kw`, `penalty_gbp`
and a `firm_capacity_kw` argument. The a51 pass named them a category conflation in the docstring
and deliberately did not touch them. The drawn item asks: delete, or move to whatever holds a
provider agreement?

**I am recording my answer before I measure: DELETE, with nothing moved.** The reason is that the
quantity is not a provider quantity in any form, so there is no receiving home for it:

* `shortfall_kw = obligation_kw - firm_capacity_kw` differences a SUPPLIER's estimated peak-period
  demand against a contracted capacity. A capacity provider's shortfall is measured against its
  own agreed de-rated capacity at a System Stress Event, not against somebody's demand.
* `company/market/capacity_market.py` already holds the provider side properly —
  `CMObligation.penalties_gbp` and `apply_penalty`, hung off a `CMUnit` with a de-rated capacity
  and a delivery year. A move would be a second, worse home for a mechanism that exists.

## The predictions, each refutable

1. **Dimensional.** `penalty_gbp` is not money. `(shortfall_kw / 1000) * (levy_gbp_per_mwh / 8)` is
   MW × GBP/MWh = **GBP per hour**. If I have this wrong the field is merely mis-sourced rather
   than mis-typed, and that would weaken the case for deleting rather than re-founding it.
2. **Blast radius: zero outside the module's own test file.** The census run before writing this
   found exactly one importer of `company.regulatory.capacity_market` in the whole tree, and it is
   `tests/company/regulatory/test_capacity_market.py`. No production caller exists — not for the
   delivery legs and not for `cm_charge_per_mwh` either.
3. **No published figure moves.** No site data file, no dashboard basis, no annual report should
   change, and I predict the site lane's gates go green without any page edit. This follows from
   (2) and is stated separately because it is the one that would actually cost something if wrong.
4. **`annual_charge_gbp` and `cm_charge_per_mwh` are bit-identical afterwards.** Neither reads the
   delivery legs today; removing them is not allowed to perturb the money. If any published levy
   figure moves by a single penny, my read of the a51 re-founding is wrong and I stop.
5. **Ratchets.** I expect `I001` to move by at most -1 (the test file's import block shrinks) and
   `E402` not to move at all. The orphan baseline should not move: the module was ALREADY caller-less
   at HEAD, so this deletion cannot add an orphan that was not there.

## What would refute the whole approach

A production caller reading `delivery_status` that the census missed because it reaches the module
by a route a `grep` of import statements cannot see — a registry, a `getattr`, a JSON-driven
dispatch. I will run the module's suite and the architecture suites and read the reds rather than
assuming the grep was complete.

## Recorded but NOT actioned this turn

The whole module has **no production caller**, not just the delivery legs. The published levy it
reads reaches production through `simulation/policy_costs.py` instead. That is a separate question
from the one drawn — whether the supplier-side charge should have a company-side home at all — and
conflating it with this deletion would repeat exactly the mistake a51 avoided.
