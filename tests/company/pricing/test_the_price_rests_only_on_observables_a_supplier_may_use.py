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

**AND PAYMENT METHOD MAY NOT MOVE A CLEAN ACCOUNT'S PRICE.** This is the cost-shift the director
named. Until 2026-10-03 it was refused by a word ban: `payment_method` was not a parameter and the
word appeared nowhere in the module. `e0370bf94` made the method a parameter on purpose -- money a
household already owes is provisioned on the published row for how it pays -- and the ban went red
while a clean prepayment household was priced GBP 2.00-2.75/MWh above a clean DD one. The ban could
not tell the two apart. The PROPERTY can: method may price DEBT (which row an unpaid bill is
provisioned on), and may never price a household with none
(`test_a_clean_account_is_not_priced_for_how_it_pays`).

WHY THIS IS A CONTROL AND NOT A COMMENT. The property is a negative one, and negative properties rot
silently: a channel-keyed term anywhere on the pricing path would be a one-line change that no
other test would notice, and the result would be a book that prices prepayment customers by their
meter type.
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
#:   arrears_state           where this account stands on its own accounts receivable
#:
#: `arrears_state` IS THE DIRECTOR'S OWN THIRD ITEM, ADDED DELIBERATELY (2026-09-25). The question
#: at the head of this file names three things as ordinary supplier practice -- "observable payment
#: behaviour, credit position or arrears HISTORY" -- and the first two were already here while the
#: third had no way to reach the price at all. It is a state on the company's own ledger
#: (`churn_model.ARREARS_STATES`, read by `arrears_state_from_collections` off
#: `arrears_engine.collections_snapshot`), carrying Ofgem CIM w6 Table 56's published pair: 1.28x
#: the population switching rate for a household whose arrears are getting harder, 0.79x for one
#: with no debt. It is NOT the cost-shift the same question refuses: it prices a household by what
#: this supplier's own books say it is owed, not by the meter type it pays through, and it moves
#: the price DOWN as readily as up -- 0.79x is the larger half of what Table 56 measured.
ACCOUNT_OBSERVABLES = {
    "customer_id", "current_rate_gbp_per_mwh", "base_rate_gbp_per_mwh", "eac_kwh",
    "tenure_years", "cost_to_serve_gbp_per_year", "expected_periods", "segment", "fuel",
    "bill_shock_count", "satisfaction_score", "renewal_year", "annual_revenue_gbp",
    "credit_risk", "behaviour_score", "payment_delay_days", "collections_gbp_per_year",
    "fixed_revenue_gbp_per_year", "is_deemed_contract", "arrears_state",
    # THE ACCOUNT'S OWN LEDGER (2026-10-03, `e0370bf94`): every unpaid bill with its age, and what
    # was billed in the 365 days to the renewal. Both read off the company's own receivable.
    "unpaid_bills_by_age", "billed_last_year_gbp",
    # The company's own mandate register: how this account pays it. Admitted to price DEBT (which
    # published provision row an unpaid bill sits on) and never a clean account -- the property
    # `test_a_clean_account_is_not_priced_for_how_it_pays` holds that line.
    "payment_method",
    # The bad-debt charge per GBP billed the company has booked on its OWN accounts in this arrears
    # state, learned from outcomes dated before the renewal (`company/pricing/default_belief.py`).
    # Learned by arrears state only: the account's payment method cannot move it.
    "default_belief_rate",
}

#: HOW THE SEARCH RUNS — not observables about anyone. Kept in a separate set on purpose: rolling
#: them in with the account facts is how a real observable would one day arrive disguised as a knob.
MECHANISM_PARAMETERS = {
    "arm", "candidates", "max_offered_rate_gbp_per_mwh", "book_general_margin_gbp_per_mwh",
    "ladder_multiplier", "flat_level_gbp_per_mwh",
}

#: WHAT THE PRICE RESTS ON THAT IS NOT ABOUT THIS ACCOUNT — published market facts, readable by
#: every supplier and every household on the day. Separate from the account set because the test of
#: admission is different: not "does the supplier hold this register about its customer" but "was it
#: published before the decision".
#:
#:   published_default_rate_gbp_per_mwh  Ofgem's default tariff cap unit rate for this fuel on the
#:       renewal date, EPG-net, ex-VAT -- `renewal_rate_chain.cap_ceiling_ex_vat`, the same
#:       published lookup writer 4 already clamps with. The churn belief reads the offer's gap to
#:       it (2026-10-02: the move from the account's own last price ranked churn at r = -0.12).
#:   stayer_default_rate_gbp_per_mwh  the company's OWN default tariff for this fuel on the day,
#:       ex-VAT: what a household that refuses the fix is billed (SLC 22C.7/22C.8). Published by the
#:       company itself, so it is the most observable number on the page.
MARKET_OBSERVABLES = {"published_default_rate_gbp_per_mwh", "stayer_default_rate_gbp_per_mwh"}

PERMITTED_OBSERVABLES = ACCOUNT_OBSERVABLES | MARKET_OBSERVABLES | MECHANISM_PARAMETERS



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


METHODS = ("direct_debit", "standard_credit", "prepayment")

#: Real renewal inputs (2,700 kWh is Ofgem's TDCV for electricity; GBP 99 a year is a standing
#: charge on the 2022-23 cap's scale), across the rates the book has seen. The first two are the
#: inputs the cost-shift was MEASURED at (finding of 2026-10-03, 106.50 vs 108.50), uncapped; the
#: rest are capped at the published default, where most real renewals sit.
_CASES = [
    dict(current_rate_gbp_per_mwh=215.0, base_rate_gbp_per_mwh=205.0),
    dict(current_rate_gbp_per_mwh=300.0, base_rate_gbp_per_mwh=280.0),
    dict(current_rate_gbp_per_mwh=215.0, base_rate_gbp_per_mwh=180.0,
         max_offered_rate_gbp_per_mwh=240.0, published_default_rate_gbp_per_mwh=240.0),
    dict(current_rate_gbp_per_mwh=300.0, base_rate_gbp_per_mwh=250.0,
         max_offered_rate_gbp_per_mwh=330.0, published_default_rate_gbp_per_mwh=330.0),
]
_EACS = (1800.0, 2700.0, 4200.0)
#: Before, during and after the crisis. 2022's market pressure makes the belief so flat that the
#: uncapped cases go to the top candidate, where no cost can move a margin; the other two years
#: price in the interior, which is where the cost-shift was measured.
_YEARS = (2019, 2022, 2023)
#: The two settings of `DecisionPolicy.renewal_default_belief`, as `decide_margin` receives them:
#: the rate chain passes the book's rate only under `own_book` and `None` otherwise.
_DEFAULT_BELIEF = {"segment_table": None, "own_book": 0.02}


def _book_that_tells_the_channels_apart():
    """A run's pressure ledger in which the channels have taught the company DIFFERENT things:
    DD shops ~4x as often as prepayment (engagement ~1.54 vs ~0.35), and only DD has closed renewals
    from which a price response could be learned. Outside a run every channel reads the same
    prior, so a check without this would pass whatever the pricing did with the method."""
    from company.crm.competitive_pressure import CompetitivePressureLedger
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    for year in (2019, 2020, 2021):
        for method, losses in (("direct_debit", 60), ("prepayment", 10)):
            for _ in range(400):
                ledger.observe_renewal_decision(year, 0.05, payment_method=method)
            for _ in range(losses):
                ledger.observe_competitive_loss(year, payment_method=method)
        for i, (move, left) in enumerate([(0.4, True)] * 6 + [(0.3, True)] * 4
                                         + [(-0.1, False)] * 10):
            account = f"D{year}-{i}"
            ledger.observe_price_response(year, "direct_debit", "electricity", account, move, 0.2)
            if left:
                ledger.observe_competitive_loss(year, payment_method="direct_debit",
                                                account_id=account)
    return ledger


def _margins_by_method(*, learn: bool, unpaid=()) -> dict:
    """`{(scope, belief, case, eac, year): {method: margin}}` over the whole grid."""
    import dataclasses

    from company.crm.competitive_pressure import pressure_ledger_scope
    from company.policy.decision_policy import VALUE_ARM_POLICY, policy_scope

    out = {}
    policy = dataclasses.replace(VALUE_ARM_POLICY, learn_price_response=learn)
    # BOTH SCOPES, because each hides what the other shows: outside a run every channel reads the
    # same belief and the arm prices in the interior, where a channel-keyed COST moves the margin;
    # in a run the book teaches channel-keyed BELIEFS, and that same belief is flat enough to send
    # the uncapped cases to the top candidate.
    for scope, ledger in (("no_run", None), ("run", _book_that_tells_the_channels_apart())):
        with pressure_ledger_scope(ledger), policy_scope(policy):
            for belief, rate in _DEFAULT_BELIEF.items():
                for n, case in enumerate(_CASES):
                    for eac in _EACS:
                        for year in _YEARS:
                            out[(scope, belief, n, eac, year)] = {m: vbr.decide_margin(
                                customer_id="X", arm="value_based", eac_kwh=eac, tenure_years=2.0,
                                cost_to_serve_gbp_per_year=60.0, fixed_revenue_gbp_per_year=99.0,
                                renewal_year=year, fuel="electricity", unpaid_bills_by_age=unpaid,
                                billed_last_year_gbp=case["current_rate_gbp_per_mwh"] * eac / 1000.0,
                                payment_method=m, default_belief_rate=rate, **case,
                            ).margin_gbp_per_mwh for m in METHODS}
    return out


def test_a_clean_account_is_not_priced_for_how_it_pays():
    """The director's named cost-shift, as a property of the price rather than a word in a file.

    A household that owes nothing is priced the same whether it pays by direct debit, on receipt or
    through a prepayment meter -- on both settings of `renewal_default_belief`, in a run whose book
    has taught the company that the channels shop differently. Method may still price DEBT; the
    control below shows that branch is reachable, so this one is not passing because the method
    reaches nothing.

    MUTATION (must fire): in `observed_non_payment_provision_rate`, move the clean-year return
    back below the live-row lookup -- the segment-table path then prices clean prepayment at the
    2% prior and the first two cases diverge by GBP 2.00-2.75/MWh.
    """
    grid = _margins_by_method(learn=False)
    assert len(grid) == 2 * len(_DEFAULT_BELIEF) * len(_CASES) * len(_EACS) * len(_YEARS)
    interior = [k for k, row in grid.items()
                if 0 < row["direct_debit"] < max(vbr.CANDIDATE_MARGINS_GBP_PER_MWH)
                and k[2] < 2]
    assert interior, ("population floor: every uncapped cell priced at the top candidate, so no "
                      "channel-keyed cost could have moved a margin and this check is blind")
    shifted = {k: row for k, row in grid.items() if len(set(row.values())) != 1}
    assert not shifted, (
        f"a clean account's price depends on how it pays in {len(shifted)} cell(s), e.g. "
        f"{next(iter(shifted.items()))}. That is the cost-shift onto prepayment the director ruled "
        "out on 2026-09-23: payment method may price debt, never a household that has none.")


def test_the_method_still_prices_debt_so_the_clean_check_is_not_vacuous():
    """The rare branch, shown reachable: a household owing money IS priced on its method's
    published provision row (Centrica Note 17 publishes DD and pay-on-receipt rows, and none for
    prepayment). If the method stopped reaching the price altogether, the property above would pass
    for the wrong reason."""
    grid = _margins_by_method(learn=False, unpaid=((150.0, 45), (150.0, 15)))
    assert any(len(set(row.values())) > 1 for row in grid.values()), (
        "no debtor's price moved with its payment method anywhere on the grid, so the clean-account "
        "property can no longer distinguish 'method is ignored for clean accounts' from 'method "
        "reaches nothing'")


def test_a_clean_account_is_not_priced_for_how_it_pays_when_the_price_response_is_learned():
    """The same property with B8 on, where the response is learned PER CHANNEL: in this book only
    DD has closed renewals, so a per-channel slope prices a clean DD household below a clean
    prepayment one (measured 2026-10-03: up to GBP 2.75/MWh at 215/180 capped at 240). The price
    reads the slope pooled over every channel instead.

    And the learning must still REACH the price, or channel-blind would have been bought by
    switching B8 off. MUTATION (must fire): `channel_blind` passing `payment_method` through to
    `learned_correction` reds the first assert; passing `None` reds the second.
    """
    learned = _margins_by_method(learn=True)
    shifted = {k: row for k, row in learned.items() if len(set(row.values())) != 1}
    assert not shifted, (
        f"with the price response learned, a clean account's price depends on how it pays in "
        f"{len(shifted)} cell(s), e.g. {next(iter(shifted.items()))}")
    unlearned = _margins_by_method(learn=False)
    assert any(learned[k] != unlearned[k] for k in learned if k[0] == "run"), (
        "B8's learned response moved no price anywhere on the grid, so the property above holds "
        "because the learning never reaches the price, not because it reaches it channel-blind")


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
