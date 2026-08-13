"""R15 control for the TIME-OF-USE OFFER seam (KNIFE pass 3, `A_composition_lift`
step 25, register §3t).

WHAT THIS SUITE IS FOR — the properties nothing else in the tree can see
------------------------------------------------------------------------
`simulation/run_phase2b.py` held two crossings and, worse, the COMPOSITION of them:
it asked `saas.smart_meter_rollout.is_tou_eligible` whether the supplier would offer
a ToU product, then built the pair inline as `(rate * TOU_PEAK_MULTIPLIER,
rate * TOU_OFFPEAK_MULTIPLIER)` from the supplier's own multipliers. Four properties
that cut rests on are invisible to every instrument already watching:

  1. NO NUMBER MOVES. The pair and the eligibility verdict must be identical to the
     pre-cut world's, for the customers who are offered ToU AND for those who are
     not — an eligibility rule copied slightly wrong shows up nowhere else, because
     an ineligible customer simply gets no ToU log line and no test counts absences.

  2. THE SPLIT EXISTED TWICE AND NOW EXISTS ONCE. `saas.tariff_pricing.
     price_tou_tariff` applied the same two multipliers to a flat rate it struck
     itself. Nothing compared them. A supplier that moves its peak multiplier in one
     of two places is quoting two different products.

  3. THE PAIR IS REVENUE-NEUTRAL AT THE ASSUMED 30/70 SPLIT — that is the whole
     design of the off-peak multiplier, and it is an arithmetic property of the two
     numbers together that neither multiplier's own value asserts.

  4. THE DOOR MUST NOT HAND BACK THE PREDICATE. Re-exporting `is_tou_eligible`
     would let the world ask "would this customer be eligible" separately from
     "what are you offering them", restoring the composition it just gave up —
     and the epistemic ratchet would stay GREEN, because the world's import would
     still terminate on the exempt seam package.

Every control below is mutation-proven by PERFORMING the defect on a copy of the
real source, never by asserting it impossible.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

import pytest

import company.interfaces.tou_offer as seam
from company.interfaces.tou_offer import TouOffer, request_tou_offer

REPO_ROOT = Path(__file__).resolve().parents[3]
SEAM_SOURCE = REPO_ROOT / "company" / "interfaces" / "tou_offer.py"
DESK_SOURCE = REPO_ROOT / "company" / "pricing" / "tou_desk.py"

# The company machinery a caller must not be able to reach through the door.
FORBIDDEN_AT_THE_DOOR = (
    "is_tou_eligible",
    "split_flat_rate_to_tou",
    "price_tou_tariff",
    "TOU_PEAK_MULTIPLIER",
    "TOU_OFFPEAK_MULTIPLIER",
    "decide_tou_offer",
)

# The customers the world actually carries, by the two metering facts the rollout
# stamps. Both eligible paths and both ineligible ones — identity is claimed for
# the renewals that DO NOT fire as well as the one that does.
_CUSTOMERS = {
    "hh_metered": {"metering": "HH"},
    "nhh_with_smart_meter": {"metering": "NHH", "smart_meter": True},
    "nhh_no_smart_meter": {"metering": "NHH", "smart_meter": False},
    "nhh_field_absent": {"metering": "NHH"},
    "hh_and_smart": {"metering": "HH", "smart_meter": True},
    "empty_record": {},
}
_RATES = (0.0, 62.4, 140.0, 310.0)


class _Mutant:
    """Perform a defect on the REAL source file, load THAT file as a throwaway
    module, restore byte-for-byte and verify the restoration.

    Registered under a throwaway name while it executes because `@dataclass`
    resolves annotations through `sys.modules[cls.__module__]`; loading it
    unregistered fails inside `dataclasses` rather than in the assertion, which
    would make the mutation UNAVAILABLE — and an unavailable check is a FAILED
    check, never a skip (R15 FAIL-SILENT).
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


# ---------------------------------------------------------------------------
# The pre-cut world, transcribed from `simulation/run_phase2b.py` as it stood at
# 880ab94e2 — the commit BEFORE the cut. Never from the module under test:
# deriving the expectation from the subject is the R15 TAUTOLOGY pattern.
# ---------------------------------------------------------------------------


def _drive_pre_cut(customer: dict, unit_rate: float):
    from saas.smart_meter_rollout import is_tou_eligible
    from saas.tariff_pricing import TOU_OFFPEAK_MULTIPLIER, TOU_PEAK_MULTIPLIER

    tou_rates = None
    if is_tou_eligible(customer):
        tou_rates = (unit_rate * TOU_PEAK_MULTIPLIER, unit_rate * TOU_OFFPEAK_MULTIPLIER)
    return tou_rates


def _drive_door(customer: dict, unit_rate: float, module=seam):
    offer = module.request_tou_offer(
        customer=customer, flat_unit_rate_gbp_per_mwh=unit_rate,
    )
    if offer is None:
        return None
    return (offer.peak_rate_gbp_per_mwh, offer.offpeak_rate_gbp_per_mwh)


# ── VACUITY — the fixture must be able to fail the controls that read it ────


def test_the_fixture_covers_both_verdicts():
    """If every fixture customer were eligible, deleting the eligibility rule
    would pass every identity assertion below."""
    verdicts = {k: _drive_door(c, 140.0) is not None for k, c in _CUSTOMERS.items()}
    assert set(verdicts.values()) == {True, False}, verdicts
    assert sum(verdicts.values()) == 3, verdicts


# ── 1. NO NUMBER MOVES ──────────────────────────────────────────────────────


@pytest.mark.parametrize("name", sorted(_CUSTOMERS))
@pytest.mark.parametrize("rate", _RATES)
def test_the_door_reproduces_the_pre_cut_offer_exactly(name, rate):
    assert _drive_door(_CUSTOMERS[name], rate) == _drive_pre_cut(_CUSTOMERS[name], rate)


def test_mutation_widening_the_eligibility_rule_is_caught_by_the_same_comparison():
    """Perform the defect: offer ToU to everyone. The eligible customers are
    unaffected — which is exactly why the ineligible ones had to be in the
    comparison at all."""
    with _Mutant(
        DESK_SOURCE,
        "    if not is_tou_eligible(customer):\n        return None",
        "    if False:  # MUTATION\n        return None",
        "mutant_tou_desk_eligibility",
    ) as mutated:
        got = mutated.decide_tou_offer(
            customer=_CUSTOMERS["nhh_no_smart_meter"], flat_unit_rate_gbp_per_mwh=140.0,
        )
        assert got is not None, "the mutation did not take"
        with pytest.raises(AssertionError):
            assert (got.peak_rate_gbp_per_mwh, got.offpeak_rate_gbp_per_mwh) == \
                _drive_pre_cut(_CUSTOMERS["nhh_no_smart_meter"], 140.0)
    # The live door still agrees with the pre-cut world.
    assert _drive_door(_CUSTOMERS["nhh_no_smart_meter"], 140.0) is None


# ── 2. ONE SPLIT, NOT TWO ───────────────────────────────────────────────────


def test_the_split_the_door_uses_is_the_split_price_tou_tariff_uses():
    """The two sites are now the same function, checked on the VALUES rather
    than by reading the imports: `price_tou_tariff` strikes its own flat rate,
    so the pair it returns must be that flat rate put through the same split the
    door applies to a contracted one."""
    from saas.tariff_pricing import price_fixed_tariff, price_tou_tariff

    flat = price_fixed_tariff(62.4, 14000, "2019-04-01")
    assert price_tou_tariff(62.4, 14000, "2019-04-01") == _drive_door(
        _CUSTOMERS["hh_metered"], flat,
    )


def test_mutation_a_second_copy_of_the_split_is_caught():
    """Perform the defect that was live until this step: the desk applies its own
    multipliers instead of the shared split. Same values today — so the control
    is written against a CHANGED multiplier, which is the actual failure mode
    (one site edited, the other not)."""
    with _Mutant(
        DESK_SOURCE,
        "    peak, offpeak = split_flat_rate_to_tou(flat_unit_rate_gbp_per_mwh)",
        "    peak, offpeak = (  # MUTATION: a private second copy of the split\n"
        "        flat_unit_rate_gbp_per_mwh * 1.60,\n"
        "        flat_unit_rate_gbp_per_mwh * 0.74,\n"
        "    )",
        "mutant_tou_desk_split",
    ) as mutated:
        from saas.tariff_pricing import price_fixed_tariff, price_tou_tariff

        flat = price_fixed_tariff(62.4, 14000, "2019-04-01")
        got = mutated.decide_tou_offer(
            customer=_CUSTOMERS["hh_metered"], flat_unit_rate_gbp_per_mwh=flat,
        )
        with pytest.raises(AssertionError):
            assert price_tou_tariff(62.4, 14000, "2019-04-01") == (
                got.peak_rate_gbp_per_mwh, got.offpeak_rate_gbp_per_mwh,
            )


# ── 3. THE PAIR IS REVENUE-NEUTRAL AT THE ASSUMED SPLIT ─────────────────────


@pytest.mark.parametrize("rate", [r for r in _RATES if r > 0])
def test_the_pair_is_revenue_neutral_at_the_thirty_seventy_assumption(rate):
    """0.30*peak + 0.70*off-peak == the flat rate. This is the property the
    off-peak multiplier is DEFINED by, and it is the one a swapped pair breaks:
    swap them and a 30/70 customer pays ~29% more for the same energy."""
    peak, offpeak = _drive_door(_CUSTOMERS["hh_metered"], rate)
    assert 0.30 * peak + 0.70 * offpeak == pytest.approx(rate, rel=1e-12)
    assert 0.30 * offpeak + 0.70 * peak != pytest.approx(rate, rel=1e-6), (
        "the pair is symmetric on this fixture — the swap this control exists to "
        "catch would be invisible"
    )


def test_mutation_swapping_the_pair_reds_the_neutrality_control():
    with _Mutant(
        DESK_SOURCE,
        "    return TouOffer(peak, offpeak)",
        "    return TouOffer(offpeak, peak)  # MUTATION",
        "mutant_tou_desk_swap",
    ) as mutated:
        got = mutated.decide_tou_offer(
            customer=_CUSTOMERS["hh_metered"], flat_unit_rate_gbp_per_mwh=140.0,
        )
        with pytest.raises(AssertionError):
            assert 0.30 * got.peak_rate_gbp_per_mwh + 0.70 * got.offpeak_rate_gbp_per_mwh \
                == pytest.approx(140.0, rel=1e-12)


# ── 4. The door hands back an offer, not the machinery ──────────────────────


def test_the_door_exposes_only_the_offer_and_the_request():
    assert seam.__all__ == ("TouOffer", "request_tou_offer")
    reachable = [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(seam, n)]
    assert reachable == [], (
        "the ToU door hands the world back the supplier's own eligibility rule or "
        "multipliers: " + ", ".join(reachable) + ". The epistemic ratchet cannot "
        "see this — the SIM's import still terminates on the exempt seam package."
    )


@pytest.mark.parametrize(
    "old,new,leaked",
    [
        (
            "from company.pricing.tou_desk import TouOffer",
            "from company.pricing.tou_desk import TouOffer\n"
            "from saas.smart_meter_rollout import is_tou_eligible  # MUTATION",
            "is_tou_eligible",
        ),
        (
            "from company.pricing.tou_desk import TouOffer",
            "from company.pricing.tou_desk import TouOffer, decide_tou_offer",
            "decide_tou_offer",
        ),
    ],
)
def test_mutation_widening_the_door_reds_the_door_control(old, new, leaked):
    """Re-export the predicate, and re-export the desk entry point. Neither
    moves a wall edge, and re-exporting the predicate is the specific widening
    that would give the world back the composition."""
    with _Mutant(SEAM_SOURCE, old, new, "mutant_tou_offer") as mutated:
        assert hasattr(mutated, leaked), "mutation did not take"
        with pytest.raises(AssertionError):
            reachable = [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(mutated, n)]
            assert reachable == []
    assert [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(seam, n)] == []


def test_no_parameter_of_the_door_can_carry_the_companys_machinery():
    for name, param in inspect.signature(request_tou_offer).parameters.items():
        assert param.kind is inspect.Parameter.KEYWORD_ONLY, (
            f"{name} is positional — a customer record and a rate are both 'the "
            "obvious first argument', and a swap would read as a plausible number"
        )
        assert param.default is inspect.Parameter.empty, (
            f"{name} carries a default; a defaulted parameter is where a company "
            "object re-enters the signature without any caller asking for it"
        )
        assert not any(
            bad in str(param.annotation) for bad in FORBIDDEN_AT_THE_DOOR
        ), f"{name} is annotated {param.annotation!r}"


def test_the_offer_carries_values_only():
    offer = request_tou_offer(
        customer=_CUSTOMERS["hh_metered"], flat_unit_rate_gbp_per_mwh=140.0,
    )
    assert isinstance(offer, TouOffer)
    for value in (offer.peak_rate_gbp_per_mwh, offer.offpeak_rate_gbp_per_mwh):
        assert isinstance(value, (int, float))
    with pytest.raises(Exception):
        offer.peak_rate_gbp_per_mwh = 1.0  # frozen: the world cannot rewrite the quote


def test_a_term_with_no_tou_offer_is_none_not_an_offer_of_nulls():
    """A `TouOffer(None, None)` would be billable against by a caller that only
    checks the object exists."""
    assert request_tou_offer(
        customer=_CUSTOMERS["nhh_no_smart_meter"], flat_unit_rate_gbp_per_mwh=140.0,
    ) is None
