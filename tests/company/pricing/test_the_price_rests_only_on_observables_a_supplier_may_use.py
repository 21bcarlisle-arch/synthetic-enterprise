"""What the renewal price is allowed to rest on, and what it must never reach for.

THE QUESTION (director, 2026-09-23), asked of an arm whose advantage came partly from bad debt:

    "Declining on observable payment behaviour, credit position or arrears history is ordinary
     supplier practice. Using something a supplier shouldn't see, or shifting cost onto prepayment
     customers, isn't... I want to know which one is carrying a result before I believe it."

Two properties, and they fail in opposite directions.

**THE PERMITTED SET IS ORDINARY SUPPLIER PRACTICE.** `decide_margin` prices against consumption,
tenure, cost to serve, credit position, how late the account pays and what collections cost. Every
one is a supplier-side register a real retailer holds — a credit segment from its own checks, a
payment history from its own ledger. None is a world internal.

**AND PAYMENT METHOD IS NOT IN IT.** This is the cost-shift the director named, and it is refused by
CONSTRUCTION rather than by policy: `payment_method` is not a parameter of `decide_margin` and the
word appears nowhere in the pricing module, so a prepayment customer cannot be priced differently
from a direct-debit one for being a prepayment customer. It reaches the churn BELIEF through the
CIM engagement factor — which is a published, sourced reading — but the pricing path never passes
it, so the belief takes the published default.

WHY THIS IS A CONTROL AND NOT A COMMENT. The property is a negative one, and negative properties rot
silently: adding `payment_method=` to one call site would be a one-line change that no existing test
would notice, and the result would be a book that prices prepayment customers by their meter type.
The audit that answered the director's question was a `grep` run once by hand; this is that grep
with a reason attached and a failure message a reader can act on.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

from company.pricing import value_based_renewal as vbr

PRICING_MODULE = Path(inspect.getfile(vbr))

#: WHAT THE PRICE RESTS ON — facts about THIS ACCOUNT, each a register a real retailer holds about
#: its own customer rather than a fact about the world it could not have seen. The payment ones are
#: the director's "ordinary supplier practice" set, named explicitly because they are the ones an
#: arm earning on bad-debt avoidance would be resting on, and a reader is entitled to see them
#: listed rather than inferred:
#:
#:   credit_risk             the supplier's own credit segment
#:   behaviour_score         its own payment-behaviour analytics (EXCELLENT..CRITICAL)
#:   payment_delay_days      how late this account actually pays, off its own ledger
#:   collections_gbp_per_year what chasing it costs
ACCOUNT_OBSERVABLES = {
    "customer_id", "current_rate_gbp_per_mwh", "base_rate_gbp_per_mwh", "eac_kwh",
    "tenure_years", "cost_to_serve_gbp_per_year", "expected_periods", "segment", "fuel",
    "bill_shock_count", "satisfaction_score", "renewal_year", "annual_revenue_gbp",
    "credit_risk", "behaviour_score", "payment_delay_days", "collections_gbp_per_year",
    "fixed_revenue_gbp_per_year", "is_deemed_contract",
}

#: HOW THE SEARCH RUNS — not observables about anyone. Kept in a separate set on purpose: rolling
#: them in with the account facts is how a real observable would one day arrive disguised as a knob.
MECHANISM_PARAMETERS = {
    "arm", "candidates", "max_offered_rate_gbp_per_mwh", "book_general_margin_gbp_per_mwh",
    "ladder_multiplier", "flat_level_gbp_per_mwh",
}

PERMITTED_OBSERVABLES = ACCOUNT_OBSERVABLES | MECHANISM_PARAMETERS

#: The cost-shift, named. Not "discouraged" -- absent.
FORBIDDEN_TOKENS = ("payment_method", "prepay", "prepayment")


def test_the_price_rests_only_on_declared_supplier_observables():
    """A new input reaching the price is a decision, and it must be made deliberately.

    This fails on ADDITION as well as removal: an argument appearing here that nobody has argued is
    a supplier observable is exactly how a world internal would arrive -- one parameter at a time,
    each plausible on its own.
    """
    actual = set(inspect.signature(vbr.decide_margin).parameters)
    assert actual, "population floor: decide_margin has no parameters, so this control is blind"
    undeclared = actual - PERMITTED_OBSERVABLES
    assert not undeclared, (
        f"decide_margin now prices against {sorted(undeclared)}, which nothing here has argued is "
        "an observable a supplier holds. If it is one, add it with the argument; if it is not, the "
        "price is resting on something the company should not be able to see."
    )


def test_payment_method_cannot_reach_the_price_at_all():
    """The director's named cost-shift, refused by construction.

    Asserted over the whole module rather than the signature, because the leak that matters is a
    call site quietly threading it into the churn belief -- which would price prepayment customers
    differently without ever appearing as a parameter of `decide_margin`.
    """
    source = PRICING_MODULE.read_text()
    assert len(source) > 1000, "population floor: the pricing module read as near-empty"
    found = [t for t in FORBIDDEN_TOKENS if t in source.lower()]
    assert not found, (
        f"{PRICING_MODULE.name} now mentions {found}. Payment method reaching the pricing path is "
        "how a book comes to charge prepayment customers more for being prepayment customers -- the "
        "cost-shift the director named as the line between ordinary practice and not."
    )


def test_the_belief_still_hears_payment_method_and_that_is_a_different_thing():
    """The permitted half of the same fact, so this file cannot be read as banning the variable.

    A supplier's ESTIMATE of who shops may legitimately vary by channel -- Ofgem's CIM banner puts
    standard credit at 1.08x and traditional prepayment at 0.32x, and that is a published reading
    about engagement. What must not happen is that estimate becoming a PRICE keyed to the meter.
    """
    from company.crm.enriched_churn_estimate import derived_payment_method_engagement_factor

    unknown = derived_payment_method_engagement_factor(None, 2022)
    assert unknown > 0, "the published default must survive an unknown channel"
    # And the pricing module must not be the thing that calls it.
    assert "derived_payment_method_engagement_factor" not in PRICING_MODULE.read_text()


def test_the_declared_unheard_inputs_are_still_parameters_and_still_unheard():
    """`bill_shock_count` and `satisfaction_score` are ARGUMENTS the rule cannot act on.

    That is a published finding (`renewal_rule_price_response.json`'s `inputs_the_rule_cannot_hear`)
    and it is a defect, not a feature -- an accepted-but-ignored parameter lets a caller believe it
    is being heard. Pinned here so that fixing it is a deliberate act that updates this leg, and so
    that DELETING them silently -- which would also make the published finding stale -- is caught.
    """
    params = set(inspect.signature(vbr.decide_margin).parameters)
    for unheard in ("bill_shock_count", "satisfaction_score"):
        assert unheard in params, (
            f"{unheard} has been removed from decide_margin. It was documented as an observable "
            "the rule accepts and cannot hear; removing it may be right, but it makes "
            "renewal_rule_price_response.json's `inputs_the_rule_cannot_hear` stale."
        )


def test_no_simulation_internal_reaches_the_pricing_module():
    """The epistemic wall, at the one seam that sets a customer's price.

    Checked by IMPORT rather than by name: a pricing module that imports the world can read
    anything in it, and the guard has to be about reachability, not about which attribute today's
    code happens to touch.
    """
    tree = ast.parse(PRICING_MODULE.read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported, "population floor: the pricing module imports nothing, so this cannot see a leak"
    assert "simulation" not in imported and "sim" not in imported, (
        f"{PRICING_MODULE.name} imports the world ({sorted(imported & {'simulation', 'sim'})}). "
        "Everything the company prices against must come through its own registers."
    )


def test_the_payment_observables_the_director_named_are_actually_present():
    """"Ordinary supplier practice" has to be checkable, not asserted.

    If an arm's advantage comes from bad-debt avoidance, the question "on what did it select?" has a
    right answer only if these are reachable at the decision. Their ABSENCE would be the finding:
    an arm avoiding bad debt without any payment observable would be doing it by some other route,
    and that route would need explaining.
    """
    params = set(inspect.signature(vbr.decide_margin).parameters)
    for observable in ("credit_risk", "behaviour_score", "payment_delay_days",
                       "collections_gbp_per_year"):
        assert observable in params, (
            f"{observable} no longer reaches the price. An arm that still earns on bad debt is "
            "then selecting on something not in this list, and which it is becomes the question."
        )
