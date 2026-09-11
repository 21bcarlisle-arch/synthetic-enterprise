**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a52-the-supplier-holds-no-delivery-obligation

# FINDING: the supplier's non-delivery penalty was not money, and its status could only ever read FAILED

**Measured:** 2026-09-07, delivery seat, in an isolated worktree.
**Pre-registration:** `SEAT_PREREGISTRATION_WHAT_THE_SUPPLIER_DELIVERY_LEGS_COST_TO_REMOVE_2026-09-07.md`,
written before any suite was run against the change. **All five predictions held**; the two that
could have refuted the approach are marked below.

## What was drawn

a51 re-founded `company/regulatory/capacity_market.py`'s MONEY on the published Ofgem Annex 9 levy
and named, without touching, a category conflation beside it: `delivery_status`, `shortfall_kw`,
`penalty_gbp` and a `firm_capacity_kw` argument, modelling a capacity PROVIDER's obligation to
deliver at a System Stress Event on a party whose CM obligation is a payment. Delete, or move?

## The answer: DELETED, nothing moved

Not because the fields were unsourced — because the quantity is not a provider quantity in any
form, so no receiving home exists. Three things were wrong, and only the third is the kind a
re-founding could have fixed.

**1. The penalty was not money.** `(shortfall_kw / 1000) * (levy_gbp_per_mwh / 8)` is
MW × GBP/MWh = **GBP per hour**. A rate, in a field named `penalty_gbp`, added to nothing and
compared with nothing, so no consumer could have noticed. The `/ 8` carried no source and no unit.
Printed across the whole published record at 5 TWh of demand, before the deletion:

| obligation year | `annual_charge_gbp` | `penalty_gbp` | ratio |
|---|---|---|---|
| 2016 | £2,500,000 | £64.21 | 38,935× |
| 2020 | £29,300,000 | £752.57 | 38,935× |
| 2024 | £36,350,000 | £933.65 | 38,935× |

The constant ratio is the tell: the "penalty" was the charge divided by a fixed number, wearing a
delivery mechanism's name. Nothing about delivery entered it.

**2. The status was a constant.** `firm_capacity_kw` defaulted to `None → 0`, so `shortfall_kw` was
the whole obligation and `delivery_status` read `FAILED` for every year at every input a supplier
could actually present — the right-hand column above is `FAILED` nine times out of nine. DELIVERED
and PARTIAL were reachable only by handing the function a firm capacity a supplier does not have.
**Its own tests did exactly that**, including one written on 2026-09-07 to prove the partition was
reachable. That test was careful and correct about the code; it derived its fixture from the branch
definition specifically so as not to be fitted to its conclusion. All of that care went into proving
a partition over a quantity that should not exist. *A suite can be rigorous about reach and still
be measuring the wrong subject, because reach is a property of the code and subject is not.*

**3. The difference was not a shortfall.** `obligation_kw - firm_capacity_kw` subtracts a contracted
capacity from this module's estimate of the supplier's **own peak-period demand**. A provider's
shortfall is its agreed de-rated capacity less what it delivered at a stress event. Neither term of
that is a demand estimate — so before asking what the penalty rate should be, the subtraction names
a quantity nobody holds. *(CLAUDE.md: before dividing two numbers, say what each one counts. The
same test applied to a subtraction settles this one in a sentence.)*

## Why nothing moved rather than being relocated

`company/market/capacity_market.py` already holds the provider side and holds it correctly:
`CMUnit` with a de-rated capacity, `CMObligation.penalties_gbp`, `apply_penalty`, priced off the
auction actually held. Moving these fields there would have created a second and worse home for a
mechanism that is already built — the identical failure a51 had just finished undoing for the
clearing price, which had four homes.

Worth recording for whoever does build non-delivery properly: the real Capacity Market penalty is
assessed **per MWh of energy not delivered** at a System Stress Event and is capped monthly and
annually against the capacity payment. It is not a per-kW haircut on a capacity difference, so this
formula was not a mis-parameterised version of the real thing in the way a wrong rate would be.

## What replaces them: nothing, deliberately

A supplier *can* reduce this charge — by shifting customer demand out of the winter peak periods the
levy is assessed on, which moves the **volume** term. That is a real lever and it is a demand
mechanism. Inventing it here to fill the hole the deletion leaves would be the same move that
produced the 0.92.

## The controls, and the poison round

Two replace the six deleted, both keyed to the property rather than to the names:

* `test_a_supplier_result_carries_no_delivery_obligation_concept` — reads the live dataclass fields
  and the live signature, **not the module source**, which necessarily quotes all three deleted
  names in the docstring explaining their removal. A source-text control here would have been
  reading its own explanation. Matches a vocabulary wider than the four deleted names, so a
  re-introduction spelled `underdelivery` or `met_obligation` is caught too.
* `test_the_charge_a_supplier_pays_does_not_depend_on_any_capacity_it_holds` — the arity leg, which
  catches a successor argument named outside that vocabulary.

**Poison round run before trusting either.** The matcher is asserted to FIRE on the four deleted
names inside the test itself, because "found nothing" and "can never match" are indistinguishable
otherwise and this control's whole value is in the years when it correctly finds nothing. Then both
were mutation-proven against the module, each mutation asserting its target was present before
applying:

| mutation | result |
|---|---|
| re-add `delivery_status: str = "DELIVERED"` to `CMObligationResult` | **KILLED** |
| re-add a third parameter `own_generation_kw` to `compute_cm_obligation` | **KILLED** |

## Predictions, scored

1. Penalty is GBP/hour, not GBP — **held**. *(Refutation would have weakened the case for deleting
   rather than re-founding.)*
2. Blast radius zero outside the module's own test file — **held**. One importer in the tree.
3. No published figure moves — **held**. No site data, dashboard or report touched.
4. `annual_charge_gbp` and `cm_charge_per_mwh` bit-identical afterwards — **held**, diffed across
   all nine published years at 5 TWh. *(This was the stop condition: a single penny of movement
   would have meant a51's re-founding was misread.)*
5. Ratchets: I001 ≤ −1, E402 unchanged, orphan baseline unchanged — **held**; both files read 0/0,
   so nothing needed banking, and the module was already caller-less at HEAD so the deletion could
   not add an orphan.

## What is next, and it is NOT this atom

**The whole module has no production caller** — not just the delivery legs. `cm_charge_per_mwh` and
`compute_cm_obligation` are imported by nothing but their own tests, and the published levy reaches
production through `simulation/policy_costs.py` instead. So the company side reads Annex 9 and the
simulation side reads Annex 9, and only one of them is wired to anything.

That is a real question — should the supplier CM charge have a company-side home at all, and if so
what consumes it — and it is a *different* question from the one drawn here. Folding it into this
deletion would have repeated exactly the conflation a51 avoided by leaving the delivery legs alone.
Filed here so it is drawn deliberately or not at all.
