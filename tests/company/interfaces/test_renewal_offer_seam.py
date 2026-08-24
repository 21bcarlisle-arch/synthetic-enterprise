"""R15 control for the RENEWAL-OFFER seam (KNIFE pass 3, B7).

WHAT THIS SUITE IS FOR — the properties NO other instrument in the tree can see
-------------------------------------------------------------------------------
`B7_renewal_is_a_company_decision` moved the renewal pricing decision and its
governance routing out of `simulation/renewals.py` into
`company/pricing/renewal_desk.py`, reached through
`company/interfaces/renewal_offer.py`. Four properties that cut rests on are
invisible to everything already watching, and each is mutation-proven below by
PERFORMING the defect rather than asserting it impossible.

  1. THE DOOR COULD BE WIDENED WITHOUT MOVING A SINGLE WALL EDGE. Re-exporting
     `price_fixed_tariff`, or accepting an `engine=`/`desk=` convenience argument,
     would hand the world back the company's pricing machinery — and the epistemic
     ratchet would stay green, because the SIM's import still terminates on the
     exempt seam package. The ratchet is blind to this by construction; tests 1 and
     2 are what is not.

  2. THE GOVERNANCE ROUTING COULD GO QUIET FOR A WHOLE PRODUCT. The decision log is
     what the board's approval surfaces read. A desk that skipped routing for, say,
     pass-through terms would move no rate, break no schedule, and turn a governed
     decision into an ungoverned one silently — FAIL-SILENT. Test 3 counts the
     events against the offers.

  3. THE COLD-START FALLBACK COULD BE DROPPED. When the company's notice-date
     lookback window is empty its engine raises, and the pre-cut code fell back to
     the forward the world hands in. A fallback that quietly became 0.0 (or the
     spot price, or anything else) would misprice exactly the customers whose
     first term opens at the start of history, and every test that does not force
     an empty window would stay green. Test 4 forces one, and carries a vacuity
     guard proving the engine really raised.

Mutations here run on the module's SOURCE TEXT, are loaded as a throwaway module
rather than by reloading the live one, and restore in a `finally` whose result is
verified byte-equal — so no restoration step can be forgotten and leave the tree
dirty, and no mutation can leak into the suite it is protecting.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

import company.interfaces.renewal_offer as seam
import company.pricing.renewal_desk as desk
from company.governance.decision_rights import get_decision_log, reset_decision_log
from company.interfaces.renewal_offer import RenewalOffer, request_renewal_offer

REPO_ROOT = Path(__file__).resolve().parents[3]
SEAM_SOURCE = REPO_ROOT / "company" / "interfaces" / "renewal_offer.py"
DESK_SOURCE = REPO_ROOT / "company" / "pricing" / "renewal_desk.py"

# The company machinery a caller must not be able to reach through the door.
FORBIDDEN_AT_THE_DOOR = (
    "CompanyTariffEngine",
    "price_fixed_tariff",
    "DecisionClass",
    "get_decision_log",
    "log_decision_event",
    "request_governance_approval",
    "record_governance_decision",
    "quote_renewal",
    "_COMPANY_ENGINE",
)


@pytest.fixture(autouse=True)
def _fresh_log():
    reset_decision_log()
    yield
    reset_decision_log()


def _records(start: str, end: str, price: float = 60.0) -> list[dict]:
    s, e = date.fromisoformat(start), date.fromisoformat(end)
    out, cur = [], s
    while cur <= e:
        out.append({"settlementDate": cur.isoformat(), "systemSellPrice": price})
        cur += timedelta(days=1)
    return out


def _ask(tariff_type="fixed", term_start="2017-01-01", records=None,
         prior=None, fallback=99.0, segment="resi", eac_kwh=2800,
         customer_id="C_SEAM", svt=None, switching_multiplier=1.0):
    ts = date.fromisoformat(term_start)
    return request_renewal_offer(
        customer_id=customer_id,
        term_start=ts,
        notice_date=ts - timedelta(days=42),
        tariff_type=tariff_type,
        segment=segment,
        eac_kwh=eac_kwh,
        observable_price_records=records if records is not None
        else _records("2015-01-01", "2018-01-01"),
        published_policy_cost_per_mwh=25.0,
        published_network_cost_per_mwh=40.0,
        prior_fixed_unit_rate=prior,
        fallback_forward_price_gbp_per_mwh=fallback,
        # B4_competitor_field (2026-08-24): svt=None keeps this seam-door
        # suite's fixtures behaviourally identical to before the atom landed
        # -- the ceiling never binds with no published SVT. The ceiling's own
        # behaviour is covered by tests/company/pricing/test_renewal_desk.py.
        published_svt_gbp_per_mwh=svt,
        published_market_switching_multiplier=switching_multiplier,
    )


class _Mutant:
    """Perform a defect on the REAL source file, load THAT file as a throwaway
    module, then restore byte-for-byte and verify the restoration.

    The mutated code is loaded under a fresh module name rather than by reloading
    the live module: `importlib.reload` updates a namespace in place and never
    removes names, so a re-export mutation would survive its own restoration and
    the identity of `RenewalOffer` would change under every other test in the file.
    That is a mutation harness that damages the suite it is meant to protect.
    """

    def __init__(self, path: Path, old: str, new: str, name: str):
        self.path, self.name = path, name
        self.original = path.read_text()
        assert old in self.original, "mutation target absent — the mutation is vacuous"
        self.mutated_text = self.original.replace(old, new, 1)
        assert self.mutated_text != self.original

    def __enter__(self):
        self.path.write_text(self.mutated_text)
        try:
            spec = importlib.util.spec_from_file_location(self.name, self.path)
            module = importlib.util.module_from_spec(spec)
            # `@dataclass` resolves annotations through `sys.modules[cls.__module__]`,
            # so a throwaway module must be registered under its throwaway name while
            # it executes. Removed again below: the live modules keep their own slots
            # throughout and are never displaced.
            sys.modules[self.name] = module
            spec.loader.exec_module(module)
        finally:
            self.path.write_text(self.original)
        return module

    def __exit__(self, *exc):
        sys.modules.pop(self.name, None)
        self.path.write_text(self.original)
        assert self.path.read_text() == self.original, "restoration left the tree dirty"
        return False


# ── 1. The door exposes the offer and nothing else ──────────────────────────


def test_the_door_exposes_only_the_offer_and_the_request():
    # KNIFE step 24 (§3s) added `request_company_forward_estimate`: the gas
    # renewal schedule in `run_phase2b.py` needed the same notice-date forward
    # view electricity has asked this door for since B7, and was holding its
    # own `CompanyTariffEngine()` to get it.
    # KNIFE step 25 (§3t) added `request_fixed_unit_rate` and the
    # `FixedRateStrike` it returns: the same gas schedule was also deciding WHICH
    # published components a pass-through product locks, reading the company's own
    # naked fraction back to it, and calling `price_fixed_tariff` itself.
    assert seam.__all__ == (
        "FixedRateStrike",
        "RenewalOffer",
        "request_company_forward_estimate",
        "request_fixed_unit_rate",
        "request_renewal_offer",
    )
    reachable = [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(seam, n)]
    assert reachable == [], (
        "the renewal-offer door hands the world back the company's own pricing/"
        "governance machinery: " + ", ".join(reachable) + ". The epistemic ratchet "
        "cannot see this — the SIM's import still terminates on the exempt seam "
        "package — so the widening would be silent."
    )


@pytest.mark.parametrize(
    "old,new,leaked",
    [
        (
            "from company.pricing.renewal_desk import FixedRateStrike, RenewalOffer",
            "from company.pricing.renewal_desk import FixedRateStrike, RenewalOffer\n"
            "from saas.tariff_pricing import price_fixed_tariff  # MUTATION",
            "price_fixed_tariff",
        ),
        (
            "from company.pricing.renewal_desk import FixedRateStrike, RenewalOffer",
            "from company.pricing.renewal_desk import FixedRateStrike, RenewalOffer, quote_renewal",
            "quote_renewal",
        ),
    ],
)
def test_mutation_widening_the_door_reds_the_door_control(old, new, leaked):
    """Perform the widening two ways: re-export the company's pricing function,
    and re-export the desk's own entry point so a caller can step past this
    door's narrow signature. Neither moves a wall edge."""
    with _Mutant(SEAM_SOURCE, old, new, "mutant_renewal_offer") as mutated:
        assert hasattr(mutated, leaked), "mutation did not take"
        with pytest.raises(AssertionError):
            reachable = [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(mutated, n)]
            assert reachable == []
    # The live door is untouched by the mutation and still exposes nothing.
    assert [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(seam, n)] == []


# ── 2. No parameter can carry the machinery in ──────────────────────────────


def test_no_parameter_of_the_door_can_carry_the_companys_machinery():
    """Every parameter is keyword-only, defaulted nowhere, and annotated as a
    plain value. A `desk=quote_renewal` or `engine=_COMPANY_ENGINE` default is
    how the removed dependency comes back without a wall edge: the caller never
    passes it, so nothing looks different at the call site."""
    sig = inspect.signature(request_renewal_offer)
    for name, param in sig.parameters.items():
        assert param.kind is inspect.Parameter.KEYWORD_ONLY, (
            f"{name} is positional — eleven positional observables across a wall "
            "is how the wrong one gets passed unnoticed"
        )
        assert param.default is inspect.Parameter.empty, (
            f"{name} carries a default; a defaulted parameter is where a company "
            "object re-enters the signature without any caller asking for it"
        )
        annotation = str(param.annotation)
        assert not any(bad in annotation for bad in FORBIDDEN_AT_THE_DOOR), (
            f"{name} is annotated {annotation!r} — the door accepts a company "
            "decision object"
        )


def test_mutation_a_defaulted_desk_parameter_reds_the_signature_control():
    """Perform it: give the door an `engine=` convenience default."""
    with _Mutant(
        SEAM_SOURCE,
        "    published_market_switching_multiplier: float,\n) -> RenewalOffer:",
        "    published_market_switching_multiplier: float,\n"
        "    engine: object = None,  # MUTATION\n) -> RenewalOffer:",
        "mutant_renewal_offer_sig",
    ) as mutated:
        params = inspect.signature(mutated.request_renewal_offer).parameters
        assert "engine" in params, "mutation did not take"
        with pytest.raises(AssertionError):
            for name, param in params.items():
                assert param.default is inspect.Parameter.empty, name


# ── 3. Every priced term is a GOVERNED term ─────────────────────────────────


def _pricing_moves(customer_id: str) -> list:
    return [
        r.value
        for r in get_decision_log().all_records()
        if r.entity_id == customer_id and r.fact_type == "decision_event:pricing_move"
    ]


@pytest.mark.parametrize("tariff_type", ["fixed", "pass_through", "flex"])
def test_a_priced_term_is_a_governed_term_and_an_unpriced_one_is_not(tariff_type):
    """The invariant that survives a product being added: an offer that quotes a
    rate leaves a PRICING_MOVE decision behind; an offer that quotes no rate
    (flex commits only a markup) leaves none. Counted against the offer, not
    against a list of product names, so a fourth tariff type cannot slip through
    ungoverned."""
    cid = f"C_GOV_{tariff_type}"
    offer = _ask(tariff_type=tariff_type, customer_id=cid)
    moves = _pricing_moves(cid)
    if offer.unit_rate_gbp_per_mwh is None:
        assert moves == [], f"{tariff_type} quoted no rate but logged a decision"
    else:
        assert len(moves) == 1, (
            f"{tariff_type} quoted {offer.unit_rate_gbp_per_mwh} but left "
            f"{len(moves)} governed decisions — a priced move that no one governs "
            "is invisible on every approval surface the board reads"
        )
        assert moves[0].decision == {
            "unit_rate_gbp_per_mwh": offer.unit_rate_gbp_per_mwh
        }


def test_mutation_skipping_the_routing_for_one_product_reds_the_governance_control():
    """Perform the fail-silent defect: leave pass-through terms priced but
    ungoverned. No rate moves, no schedule breaks, no wall edge appears."""
    with _Mutant(
        DESK_SOURCE,
        '    request = {\n        "term_start": term_start_str,',
        '    if tariff_type == "pass_through":  # MUTATION\n        return\n'
        '    request = {\n        "term_start": term_start_str,',
        "mutant_renewal_desk_gov",
    ) as mutated:
        reset_decision_log()
        ts = date.fromisoformat("2017-01-01")
        offer = mutated.quote_renewal(
            customer_id="C_MUT",
            term_start=ts,
            notice_date=ts - timedelta(days=42),
            tariff_type="pass_through",
            segment="resi",
            eac_kwh=2800,
            observable_price_records=_records("2015-01-01", "2018-01-01"),
            published_policy_cost_per_mwh=25.0,
            published_network_cost_per_mwh=40.0,
            prior_fixed_unit_rate=None,
            fallback_forward_price_gbp_per_mwh=99.0,
            published_svt_gbp_per_mwh=None,
            published_market_switching_multiplier=1.0,
        )
        # The defect is silent on every other axis: a rate was still quoted.
        assert offer.unit_rate_gbp_per_mwh is not None
        with pytest.raises(AssertionError):
            assert len(_pricing_moves("C_MUT")) == 1


# ── 4. The cold-start fallback is the number the world handed in ────────────


def _cold_start_records(term_start: str) -> list[dict]:
    """Records that stop BEFORE the notice date, so the company's own lookback
    window is empty and its engine raises."""
    ts = date.fromisoformat(term_start)
    return _records((ts - timedelta(days=30)).isoformat(), ts.isoformat())


def test_the_cold_start_forward_is_exactly_the_fallback_the_world_handed_in():
    term_start = "2017-01-01"
    records = _cold_start_records(term_start)

    # Vacuity guard: the engine MUST actually raise on this fixture, else this
    # test passes against the ordinary path and proves nothing about cold start.
    with pytest.raises(ValueError):
        desk._COMPANY_ENGINE.get_forward_price(
            "electricity",
            (date.fromisoformat(term_start) - timedelta(days=42)).isoformat(),
            records,
        )

    offer = _ask(term_start=term_start, records=records, fallback=123.456,
                 customer_id="C_COLD")
    assert offer.company_forward_price_gbp_per_mwh == 123.456, (
        "the cold-start forward is not the value the world handed in — a dropped "
        "or altered fallback misprices exactly the customers whose first term "
        "opens at the start of history, silently"
    )


def test_mutation_dropping_the_cold_start_fallback_reds_the_control():
    """Perform it: the cold-start branch silently answers 0.0 instead of the
    forward the world handed in."""
    with _Mutant(
        DESK_SOURCE,
        "        company_fwd = fallback_forward_price_gbp_per_mwh",
        "        company_fwd = 0.0  # MUTATION",
        "mutant_renewal_desk_cold",
    ) as mutated:
        ts = date.fromisoformat("2017-01-01")
        offer = mutated.quote_renewal(
            customer_id="C_COLDMUT",
            term_start=ts,
            notice_date=ts - timedelta(days=42),
            tariff_type="fixed",
            segment="resi",
            eac_kwh=2800,
            observable_price_records=_cold_start_records("2017-01-01"),
            published_policy_cost_per_mwh=25.0,
            published_network_cost_per_mwh=40.0,
            prior_fixed_unit_rate=None,
            fallback_forward_price_gbp_per_mwh=123.456,
            published_svt_gbp_per_mwh=None,
            published_market_switching_multiplier=1.0,
        )
        with pytest.raises(AssertionError):
            assert offer.company_forward_price_gbp_per_mwh == 123.456


# ── The offer is a value, not a handle ──────────────────────────────────────


def test_the_offer_carries_values_only():
    offer = _ask()
    assert isinstance(offer, RenewalOffer)
    for field_value in (
        offer.unit_rate_gbp_per_mwh,
        offer.company_forward_price_gbp_per_mwh,
        offer.locked_policy_cost_gbp_per_mwh,
        offer.locked_network_cost_gbp_per_mwh,
    ):
        assert field_value is None or isinstance(field_value, (int, float))
    with pytest.raises(Exception):
        offer.unit_rate_gbp_per_mwh = 1.0  # frozen: the world cannot rewrite the quote


# ═══════════════════════════════════════════════════════════════════════════
# KNIFE step 25 (§3t) — THE GAS STRIKE. `simulation/run_phase2b.py::
# _build_gas_renewal_schedule` ran the lock decision, fetched the company's own
# naked fraction and called `price_fixed_tariff` itself. These controls are
# about the COMPOSITION — which components are locked, on what fraction, in what
# order — not about the pricing arithmetic, which is unchanged and shared.
# ═══════════════════════════════════════════════════════════════════════════

# The world's block EXACTLY as it stood at 880ab94e2, the commit BEFORE the cut.
# Transcribed from `simulation/run_phase2b.py`, never from the module under test:
# deriving the expectation from the subject is the R15 TAUTOLOGY pattern.
def _drive_pre_cut_gas_strike(
    *, tariff_type: str, company_fwd: float, aq_kwh: int, term_start: str,
    gas_policy: float, gas_network: float,
) -> tuple[float, float, float]:
    from company.interfaces.hedge_desk import hedge_mandate
    from saas.tariff_pricing import price_fixed_tariff

    # Phase 40b: pass-through tariffs lock only wholesale+margin at term start.
    if tariff_type == "pass_through":
        locked_gas_policy = 0.0
        locked_gas_network = 0.0
    else:
        locked_gas_policy = gas_policy
        locked_gas_network = gas_network
    unit_rate = price_fixed_tariff(
        company_fwd, aq_kwh, term_start,
        naked_fraction=hedge_mandate().naked_fraction,
        policy_cost_per_mwh=locked_gas_policy,
        network_cost_per_mwh=locked_gas_network,
    )
    return unit_rate, locked_gas_policy, locked_gas_network


_GAS_CASES = [
    # (tariff_type, company_fwd, aq_kwh, term_start, gas_policy, gas_network)
    ("fixed", 62.4, 14000, "2019-04-01", 5.6, 12.3),
    ("pass_through", 62.4, 14000, "2019-04-01", 5.6, 12.3),
    # The GGL only applies from Nov 2021, so a zero policy cost is a real case
    # and not a degenerate one — it must still be told apart from a locked zero.
    ("fixed", 180.0, 32000, "2021-01-01", 0.0, 9.1),
    ("pass_through", 180.0, 32000, "2021-01-01", 0.0, 9.1),
    # A crisis-era I&C-sized term, where the naked fraction moves the rate most.
    ("fixed", 310.0, 900000, "2022-10-01", 6.4, 3.9),
]


@pytest.mark.parametrize("case", _GAS_CASES, ids=[f"{c[0]}@{c[3]}" for c in _GAS_CASES])
def test_the_door_reproduces_the_pre_cut_gas_strike_exactly(case):
    """NO NUMBER MOVES, measured rather than asserted — over both products and
    three price regimes, rate AND both locked components."""
    tariff_type, fwd, aq, ts, policy, network = case
    want = _drive_pre_cut_gas_strike(
        tariff_type=tariff_type, company_fwd=fwd, aq_kwh=aq, term_start=ts,
        gas_policy=policy, gas_network=network,
    )
    strike = seam.request_fixed_unit_rate(
        tariff_type=tariff_type,
        company_forward_price_gbp_per_mwh=fwd,
        eac_kwh=aq,
        term_start=ts,
        published_policy_cost_per_mwh=policy,
        published_network_cost_per_mwh=network,
    )
    assert (
        strike.unit_rate_gbp_per_mwh,
        strike.locked_policy_cost_gbp_per_mwh,
        strike.locked_network_cost_gbp_per_mwh,
    ) == want


def test_the_fixed_and_pass_through_cases_are_not_the_same_number():
    """VACUITY: if the two products priced identically on this fixture, every
    identity assertion above would pass with the lock decision deleted."""
    fixed = seam.request_fixed_unit_rate(
        tariff_type="fixed", company_forward_price_gbp_per_mwh=62.4, eac_kwh=14000,
        term_start="2019-04-01", published_policy_cost_per_mwh=5.6,
        published_network_cost_per_mwh=12.3,
    )
    passthru = seam.request_fixed_unit_rate(
        tariff_type="pass_through", company_forward_price_gbp_per_mwh=62.4,
        eac_kwh=14000, term_start="2019-04-01", published_policy_cost_per_mwh=5.6,
        published_network_cost_per_mwh=12.3,
    )
    assert fixed.unit_rate_gbp_per_mwh > passthru.unit_rate_gbp_per_mwh


def test_the_naked_fraction_the_world_used_to_hand_over_is_the_desks_own():
    """The argument stopped crossing the wall. That is only a no-op because the
    two constants are equal TODAY — checked here, so the day they diverge this
    control reds instead of the gas book silently repricing."""
    from company.interfaces.hedge_desk import hedge_mandate

    assert desk.NAKED_FRACTION == hedge_mandate().naked_fraction


def test_the_order_is_a_signature_lock_first_then_strike():
    """Perform the reorder on a copy of the real desk: strike against the
    PUBLISHED components, then zero them. A pass-through product priced that way
    sells a rate with levies baked in that it bills again at settlement — and
    nothing in the pre-cut code could have caught it, because the two steps were
    four lines apart in the world with nothing asserting the sequence."""
    original = DESK_SOURCE.read_text()
    anchor = """    if tariff_type == "flex":
        return FixedRateStrike(None, locked_policy, locked_network)
"""
    assert anchor in original, "anchor moved — this mutation is no longer the defect"
    mutated_text = original.replace(
        anchor,
        anchor
        + """
    locked_policy, locked_network = (  # MUTATION: strike before the lock decision
        published_policy_cost_per_mwh, published_network_cost_per_mwh,
    )
    _late = price_fixed_tariff(
        company_forward_price_gbp_per_mwh, eac_kwh, term_start,
        naked_fraction=NAKED_FRACTION,
        policy_cost_per_mwh=locked_policy,
        network_cost_per_mwh=locked_network,
    )
    if tariff_type == "pass_through":
        return FixedRateStrike(_late, 0.0, 0.0)
""",
        1,
    )
    with _Mutant(DESK_SOURCE, original, mutated_text, "mutant_desk_strike_order") as m:
        got = m.strike_fixed_unit_rate(
            tariff_type="pass_through", company_forward_price_gbp_per_mwh=62.4,
            eac_kwh=14000, term_start="2019-04-01",
            published_policy_cost_per_mwh=5.6, published_network_cost_per_mwh=12.3,
        )
        want = _drive_pre_cut_gas_strike(
            tariff_type="pass_through", company_fwd=62.4, aq_kwh=14000,
            term_start="2019-04-01", gas_policy=5.6, gas_network=12.3,
        )
        assert got.unit_rate_gbp_per_mwh != want[0], "the mutation did not take"
    # The live desk is untouched and still agrees with the pre-cut world.
    assert DESK_SOURCE.read_text() == original
    assert seam.request_fixed_unit_rate(
        tariff_type="pass_through", company_forward_price_gbp_per_mwh=62.4,
        eac_kwh=14000, term_start="2019-04-01", published_policy_cost_per_mwh=5.6,
        published_network_cost_per_mwh=12.3,
    ).unit_rate_gbp_per_mwh == _drive_pre_cut_gas_strike(
        tariff_type="pass_through", company_fwd=62.4, aq_kwh=14000,
        term_start="2019-04-01", gas_policy=5.6, gas_network=12.3,
    )[0]


def test_a_flex_gas_term_is_the_one_case_that_deliberately_diverges():
    """NAMED, not smoothed over. The world's gas block only zeroed for
    `pass_through`, so a flex gas term would have been quoted a locked rate; the
    desk answers None, which is the product rule electricity has always used.
    The divergence is unreachable on today's tree — pinned here — and it is a
    CORRECTION, so it is recorded rather than hidden behind 'no number moves'."""
    from simulation.run_phase2b import GAS_CUSTOMERS

    assert {c.get("tariff_type", "fixed") for c in GAS_CUSTOMERS} == {
        "fixed", "pass_through",
    }, "a flex gas customer now exists — the divergence above is live, re-rule it"
    strike = seam.request_fixed_unit_rate(
        tariff_type="flex", company_forward_price_gbp_per_mwh=62.4, eac_kwh=14000,
        term_start="2019-04-01", published_policy_cost_per_mwh=5.6,
        published_network_cost_per_mwh=12.3,
    )
    assert strike.unit_rate_gbp_per_mwh is None
    assert (strike.locked_policy_cost_gbp_per_mwh,
            strike.locked_network_cost_gbp_per_mwh) == (0.0, 0.0)
