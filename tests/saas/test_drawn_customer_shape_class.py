"""R10 CLASS CLOSURE — no company/saas consumer may KeyError on a DRAWN customer.

THE CLASS, and why an instance fix was not allowed to close it.

Activating the population draw (2026-08-13) put SYN-* customers into the book that
every downstream consumer iterates. A drawn record is saas-shaped but it is NOT the
static roster's shape: it carries `consumption_band`, `payment_method`,
`data_regime`, `acquisition_type`, `tariff_type`, and it does NOT carry the
hand-authored `home_type`, `epc_rating`, `bedrooms`, `contract_type`, `smart_meter`.

Any consumer that reads one of those five off a customer dict with `c["key"]` rather
than a guard raises KeyError the moment the draw is on. That failure does not look
like a wrong number — it kills the whole 10-year run. It killed ten tests in the
activation's first full-suite pass, all from ONE unguarded read in
`home_move_win_rate.build_home_move_win_rates` (`profile["epc_rating"]`), several
thousand settlement periods deep, long after the run looked healthy.

R10: an absurdity-class defect may not be closed with an instance fix. Patching that
one line closes the instance. THIS closes the class: it drives the real consumers
with the real ACTIVATED book and fails if any of them cannot cope. A consumer added
next month that reads `c["epc_rating"]` directly fails here, without anyone having
remembered this rule.

Deliberately BEHAVIOURAL rather than a static scan: `c["epc_rating"]` inside an
`if "epc_rating" in c:` branch is correct and a scan would have to model that, which
is how scans acquire false positives and then get muted.
"""

import pytest

from saas.customers import CUSTOMERS
from simulation.live_population import live_population

# The five fields the static roster authors and a drawn record does not carry.
STATIC_ONLY_FIELDS = {"home_type", "epc_rating", "bedrooms", "contract_type", "smart_meter"}


@pytest.fixture
def activated_book(monkeypatch):
    """The real drawn book, flag pinned ON so this does not depend on the curriculum."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    book = live_population()
    assert len(book) > len(CUSTOMERS), "fixture precondition: the draw must actually add customers"
    return book


@pytest.fixture
def drawn_only(activated_book):
    static_ids = {c["customer_id"] for c in CUSTOMERS}
    drawn = [c for c in activated_book if c["customer_id"] not in static_ids]
    assert drawn, "fixture precondition: there must be at least one drawn customer to test"
    return drawn


def test_the_premise_holds_drawn_records_really_do_lack_those_fields(drawn_only):
    """If this fails the class has dissolved (or the shape changed) and the rest of
    this file is testing nothing — the tautology guard for every test below."""
    for c in drawn_only:
        missing = STATIC_ONLY_FIELDS - set(c)
        assert missing == STATIC_ONLY_FIELDS, (
            f"{c['customer_id']} now carries {STATIC_ONLY_FIELDS - missing} — if the drawn "
            "shape gained these on purpose, this whole class guard needs rewriting, not muting"
        )


def test_property_model_builds_properties_for_the_activated_book(activated_book):
    # B12/KNIFE3 step 35 (2026-08-18): the builder moved world-side and no longer
    # guesses a drawn dwelling from `consumption_band`. The world's dwellings are
    # now a REQUIRED input, exactly as `run_phase2b` passes them, so this drives the
    # consumer the way the real caller does. The class this file guards is unchanged
    # -- no consumer may KeyError on a DRAWN customer's missing static fields -- and
    # the assertions below still fail if the builder reaches for one of them.
    from simulation.dwelling_records import build_properties
    from simulation.live_population import live_dwellings
    props = build_properties(activated_book, dwellings=live_dwellings())
    resi_elec = [c for c in activated_book
                 if c["segment"] == "resi" and c.get("commodity") == "electricity"]
    for c in resi_elec:
        assert c["customer_id"] in props, f"no property record for {c['customer_id']}"
        rec = props[c["customer_id"]]
        assert rec["epc_rating"] and rec["bedrooms"] and rec["property_type"]


def test_home_move_win_rates_cope_with_a_drawn_customer(activated_book):
    """THE ACTUAL 2026-08-13 KILLER, as a named control.

    `build_home_move_win_rates` read `profile["epc_rating"]` straight off the dict.
    Reverting that to a bare subscript fires this test by name.
    """
    from saas.home_move_win_rate import build_home_move_win_rates
    churn_risk = {
        c["customer_id"]: [{"renewal_period": 0, "churn_probability": 0.2}]
        for c in activated_book
    }
    out = build_home_move_win_rates(churn_risk, activated_book, price_differential_pct=0.0)
    for c in activated_book:
        assert c["customer_id"] in out
        for row in out[c["customer_id"]]:
            assert 0.0 <= row["win_probability"] <= 1.0


def test_a_home_move_win_on_a_drawn_property_can_be_cloned(drawn_only):
    """`register_acquired_point` clones the predecessor's dwelling fields. A drawn
    predecessor has none of them, and the run reaches this path whenever a home move
    is won on a drawn customer."""
    from company.interfaces.supply_book import register_acquired_point
    for c in drawn_only:
        rec = register_acquired_point(c["customer_id"] + "_clone", c, "2024-01-01")
        assert rec["home_type"] and rec["epc_rating"]
        assert rec["successor_of"] == c["customer_id"]
        assert rec["acquisition_type"] == "fresh_market"


def test_every_drawn_point_resolves_through_the_supply_book(activated_book):
    """Iterating a book the run cannot resolve by id is what handed `None` to the
    acquisition clone. Every point the seam serves must look up."""
    from company.interfaces.supply_book import registered_point
    unresolvable = [c["customer_id"] for c in activated_book
                    if registered_point(c["customer_id"]) is None]
    assert not unresolvable, f"seam serves points the book cannot resolve: {unresolvable}"


def test_settlement_input_projects_a_drawn_point(drawn_only):
    from company.interfaces.supply_book import settlement_input
    for c in drawn_only:
        si = settlement_input(c)
        assert si["customer_id"] == c["customer_id"]
        assert si["acquisition_date"] == c["acquisition_date"]


def test_the_shared_accessors_agree_with_the_property_derivation(drawn_only):
    """Two derivations of one customer's dwelling must not disagree.

    `_home_type_of` answers in the roster's vocabulary and `_derive_syn_property_fields`
    in the property vocabulary; if they drift, a drawn customer and its home-move
    successor describe different dwellings.
    """
    from saas.property_model import (
        _derive_syn_property_fields,
        _epc_rating_of,
        _home_type_of,
    )
    from simulation.dwelling_records import PROPERTY_TYPE_BY_HOME_TYPE
    for c in drawn_only:
        phys = _derive_syn_property_fields(c)
        assert PROPERTY_TYPE_BY_HOME_TYPE[_home_type_of(c)] == phys["property_type"], (
            f"{c['customer_id']}: home_type and property_type derivations disagree"
        )
        assert _epc_rating_of(c) == phys["epc_rating"]


def test_the_accessors_are_byte_identical_on_the_static_roster():
    """MUTATION (the other direction): the accessors must not have changed a single
    static customer's answer. If they had, activation would have silently moved the
    18 existing customers' properties too, which is not what 'additive' means."""
    from saas.property_model import _epc_rating_of, _home_type_of
    for c in CUSTOMERS:
        if "home_type" in c:
            assert _home_type_of(c) == c["home_type"]
        if "epc_rating" in c:
            assert _epc_rating_of(c) == c["epc_rating"]


# ═══════════════════════════════════════════════════════════════════════════
# THE SECOND SHAPE OF THE SAME CLASS (added 2026-08-13, after the first
# re-verification pass). The guards above catch a consumer that reads a FIELD a
# drawn record lacks. `cost_to_serve` failed a different way: it builds
# `{c["customer_id"]: ... for c in customers}` and then resolves SETTLEMENT
# RECORDS against it. A drawn customer settles from 2021, so if the roster handed
# in excludes the drawn book the lookup raises KeyError on the ID itself --
# nothing to do with which fields the record carries.
#
# The class is therefore wider than "missing field": it is "a consumer handed a
# roster that disagrees with the book the run actually settled". Same failure
# mode -- a dead run, thousands of settlement periods deep, not a wrong number.
# ═══════════════════════════════════════════════════════════════════════════

def test_cost_to_serve_resolves_a_drawn_customers_settlement_records(activated_book, drawn_only):
    """THE SECOND 2026-08-13 KILLER, as a named control.

    Feed `build_cost_to_serve` a settlement record for a DRAWN customer against
    the activated roster. Handing it a roster that omits the drawn book (which is
    what `annual_report` did) fires this by name.
    """
    from saas.cost_to_serve import build_cost_to_serve
    records = [
        {"customer_id": c["customer_id"], "revenue_gbp": 100.0,
         "margin_gbp": 10.0, "net_margin_gbp": 2.4, "commodity": "electricity"}
        for c in drawn_only
    ]
    out = build_cost_to_serve(records, activated_book)
    for c in drawn_only:
        assert c["customer_id"] in out["by_customer"], (
            f"{c['customer_id']} settled but has no cost-to-serve row"
        )


def test_the_reports_own_roster_covers_every_customer_that_can_settle():
    """The roster `annual_report` resolves records against must be a SUPERSET of
    the book the run settles. This is the invariant, stated once, rather than one
    test per call site -- a fifth registration book added later is covered."""
    import os

    import saas.customers as sc
    from simulation.live_population import live_population
    os.environ["SE_DRAW_POPULATION"] = "1"
    try:
        settleable = {c["customer_id"] for c in live_population()}
    finally:
        os.environ.pop("SE_DRAW_POPULATION", None)
    report_roster = {
        c["customer_id"] for c in
        sc.CUSTOMERS + sc.SUCCESSOR_CUSTOMERS + sc.ACQUIRED_CUSTOMERS + sc.DRAWN_CUSTOMERS
    }
    missing = settleable - report_roster
    assert not missing, (
        f"these customers can settle but the report's roster cannot resolve them: {missing} "
        "-- build_cost_to_serve raises KeyError on exactly this"
    )
