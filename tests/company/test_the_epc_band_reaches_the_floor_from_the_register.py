"""The EPC band the health floor needs arrives from the REGISTER, and it arrives at all.

REUSE: tests/company/test_the_epc_band_reaches_the_floor_from_the_register.py
CLASS: CUSTOM
INDEX: searched "epc band", "health floor", "turn down", "certificate", "efficiency band",
       "couple_fabric certificate", "fabric gap ledger truth arm".
       `tests/company/test_turn_down_respects_the_health_floor.py` proves the FLOOR — that the rule
       refuses the right households and cannot be bought off. It knows nothing about where the band
       comes from, and it passed in full for thirteen days while no production caller passed one, so
       every real decision reached the fail-closed branch and the floor's ALLOW side was exercised by
       tests alone. `tests/tools/test_couple_fabric.py` proves the WALL at the same seam but asserts
       what must NOT cross; this asserts what must, and on what terms.
       `tests/company/pricing/test_thermal_inference.py` covers the certificate as an inference
       input — a different subject, and the band is deliberately not one.

THE DEFECT THIS EXISTS FOR
--------------------------
W2_34 sat at L1 with nine green controls because REACHABILITY, not correctness, was what was
missing: `decide(epc_band=...)` defaulted to `None` and nothing outside the floor's own tests ever
passed one. A measure can be in the book, proven over the whole band partition, and offered to
nobody — and every control on the rule itself stays green while that is true.

So these controls are about the CHAIN, not the rule: the band is a register fact rather than a
fabric one, it stops where the register stops, it reaches a real decision, and it reaches BOTH arms
of the gap ledger. That last one is the load-bearing leg and the least obvious: hand the truth arm a
band the company lacks and this codebase books a refusal that protects cold households as MONEY THE
COMPANY'S IGNORANCE COST THEM.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from background import fabric_gap_ledger as fgl  # noqa: E402
from company.pricing import fabric_intervention as fi  # noqa: E402
from company.pricing import thermal_inference as ti  # noqa: E402
from tools import couple_fabric as cf  # noqa: E402

#: Small enough to draw in a few seconds, large enough that the published band marginal
#: (EHS 2022-23 AT1_2 — A/B 3.3%, C 44.8%) puts several premises above the floor. It is a
#: sample size, never a target: nothing below asserts a COUNT.
_DRAW_N = 40


@pytest.fixture(scope="module")
def drawn():
    weather = cf.load_weather()
    population = cf.build_drawn_population(weather, n=_DRAW_N, seed=17, population_seed=17)
    observations, _detail, _no_belief = cf.observe(population, weather)
    return population, observations


def test_THE_FLOORS_ALLOW_BRANCH_IS_REACHED_BY_A_PRODUCTION_CALLER_not_only_by_a_test(drawn):
    """THE CONTROL W2_34 WAS MISSING, and the reason it stayed at L1.

    Every other control on the turn-down passes a band in by hand. This one asserts a band arrives
    from the drawn population, through the certificate, onto the observation, and into a decision
    that actually offers the measure — with nothing in this test supplying one.

    Keyed to the PROPERTY (`some household is offered it`), never to today's count: a control pinned
    to thirteen-of-thirty-nine would red when the world's band marginal is refreshed for fidelity,
    which is the wrong direction for a reachability claim.
    """
    _population, observations = drawn
    offered = [o.premise_id for o in observations if _production_decision(o).zero_capital_measure]
    assert offered, (
        "no premise in a drawn population was offered the zero-capital measure. The band is not "
        "reaching the health floor from production code, so `turn_down` is in the offer book and "
        "available to nobody — which is exactly the state this wiring was built to leave, and "
        "every control on the floor RULE stays green while it is true.")


def test_A_PREMISE_THE_REGISTER_HAS_NO_CERTIFICATE_FOR_CARRIES_NO_BAND(drawn):
    """A band is a fact ABOUT A CERTIFICATE. A premise the register never certified has none, and
    must not acquire one by the harness handing it round the seam.

    The second assertion is the one that matters: `_certificate_for` is offered a band AND a null
    lodgement together, which is the shape a future caller reaches by reading the band off the
    premise and forgetting the pairing."""
    population, _observations = drawn
    uncertificated = [entry for entry in population if entry[5] is None]
    assert uncertificated, (
        f"a {_DRAW_N}-premise draw produced no uncertificated premise, so the branch this test is "
        "about was never entered — EPC coverage is ~60% of the stock and this is not that")
    trace, household = uncertificated[0][2], uncertificated[0][1]
    assert cf._certificate_for(trace, household, None, "C") is None, (
        "a premise with no lodged certificate was handed a certificate anyway once a band was "
        "supplied beside it. The band would then establish a health floor the register cannot.")


def test_THE_BAND_IS_THE_REGISTERS_AND_IS_NOT_DERIVED_FROM_THE_FABRIC(drawn):
    """THE EPISTEMIC LEG. The two derivations available inside `_certificate_for` — the insulation
    string and the trace's true heat-loss coefficient, both in its own arguments — are the two the
    atom forbids, because either would put a constant nobody published into the one field a
    customer's advice turns on, and it would read as established.

    Both are testable without reading the seam's source. A band DERIVED from insulation is a
    FUNCTION of it, so some insulation level carrying two bands refutes that derivation outright. A
    band derived from the true HLC would be separable by a threshold on it, so overlapping HLC
    ranges between two bands refutes that one.

    EVERY BAND BELOW IS READ OFF THE CERTIFICATE THE SEAM BUILT, never off the population tuple it
    was built from. The first draft of this test read the tuple and a mutation that derived the
    band from insulation inside `_certificate_for` sailed through it: a control that pins the
    READER is blind to what the WRITER did.
    """
    population, observations = drawn
    kept = {o.premise_id for o in observations}
    bands_by_insulation: dict[str, set[str]] = {}
    hlc_by_band: dict[str, list[float]] = {}
    for premise_id, household, trace, _commodity, _cadence, lodged, drawn_band in population:
        if premise_id not in kept:
            continue
        certificate = cf._certificate_for(trace, household, lodged, drawn_band)
        if certificate is None or certificate.efficiency_band is None:
            continue
        assert certificate.efficiency_band == drawn_band, (
            f"{premise_id}: the certificate reports band {certificate.efficiency_band!r} where the "
            f"register drew {drawn_band!r}. The seam is computing a band rather than passing the "
            "published draw through, so whatever it computed it from is now an unpublished "
            "domain constant sitting in a customer-facing field")
        band = certificate.efficiency_band
        bands_by_insulation.setdefault(household.insulation.value, set()).add(band)
        hlc_by_band.setdefault(band, []).append(trace.fabric.heat_loss_coefficient_kw_per_k)

    assert any(len(v) > 1 for v in bands_by_insulation.values()), (
        f"every insulation level maps to exactly one band ({bands_by_insulation}), so the band is "
        "a function of the insulation string and the register is reporting the company's own "
        "assumption back to it")

    overlapping = [
        (a, b) for a in hlc_by_band for b in hlc_by_band if a < b
        and min(hlc_by_band[a]) <= max(hlc_by_band[b])
        and min(hlc_by_band[b]) <= max(hlc_by_band[a])
    ]
    assert overlapping, (
        f"no two bands overlap in true heat-loss coefficient ({hlc_by_band}), so a threshold on the "
        "SIM's hidden fabric reproduces the band exactly — which is the truth crossing the wall "
        "wearing a register field's name")


def test_THE_BAND_IS_NOT_READ_BY_THE_FABRIC_PRIOR_so_the_gap_did_not_move_under_it(drawn):
    """One change, one moved quantity. The band was added for the health floor, and `epc_prior`
    deliberately does not read it — so no belief in the measured gap moves in the commit that made
    one refusal reachable. Without this, a later gap result could be attributed to either.

    This is not a claim the band never belongs in the prior; it is a claim it is not there yet."""
    population, _observations = drawn
    certificated = next(e for e in population if e[5] is not None and e[6] is not None)
    _pid, household, trace, _commodity, _cadence, lodged, band = certificated
    with_band = cf._certificate_for(trace, household, lodged, band)
    without = cf._certificate_for(trace, household, lodged, None)
    # Only that one differs; whether it is the DRAWN band is the previous test's subject.
    assert with_band.efficiency_band is not None and without.efficiency_band is None
    a = ti.epc_prior(with_band, as_of=cf.AS_OF)
    b = ti.epc_prior(without, as_of=cf.AS_OF)
    assert a.hlc_kw_per_k == pytest.approx(b.hlc_kw_per_k), (
        "the fabric prior moved when the band was supplied, so this wiring changed every "
        "certificated premise's belief as well as its choice set")
    assert a.relative_sd == pytest.approx(b.relative_sd)


# ---------------------------------------------------------------------------
# THE TRUTH ARM — the leg that stops a safety refusal being published as lost money
# ---------------------------------------------------------------------------

#: A LOW-CONSUMPTION HOME, WHICH IS THE POPULATION THE WHOLE FINDING IS ABOUT. Every capital
#: measure destroys value here — £6,000 of insulation never pays back on 1,000 kWh a year — so
#: `turn_down` is not merely surfaced beside a winner, it IS the winner, and the choice set is
#: therefore what decides between RECOMMEND and DECLINE_NO_POSITIVE_VALUE. Printed across the real
#: range before this test was written: at 1,000 kWh and 7.4 p/kWh a band-C household is recommended
#: a turn-down and a bandless one is declined outright.
_LOW_USE_KWH = 1_000.0
_LOW_USE_HLC = 0.05


def _observation(premise_id: str, band: str | None) -> fgl.FabricObservation:
    """A premise whose belief IS the truth, so the ledger's only remaining input is the band.

    Zero belief error is the point: any forgone value this produces cannot be a wrong belief,
    because there is no wrong belief. It can only be the two arms being handed different rules.
    """
    return fgl.FabricObservation(
        premise_id=premise_id,
        actual_hlc_kw_per_k=_LOW_USE_HLC,
        epc_hlc_kw_per_k=_LOW_USE_HLC,
        inferred_hlc_kw_per_k=_LOW_USE_HLC,
        floor_area_m2=60.0,
        annual_heat_kwh=_LOW_USE_KWH,
        annual_degree_days_k_day=2_200.0,
        epc_relative_sd=0.02,
        inferred_relative_sd=0.02,
        epc_basis=ti.EvidenceBasis.METER_AND_EPC,
        inferred_basis=ti.EvidenceBasis.METER_AND_EPC,
        epc_band=band,
    )


def test_BOTH_LEDGER_ARMS_ARE_HANDED_THE_SAME_BAND_so_the_floor_is_never_booked_as_forgone_value():
    """THE LOAD-BEARING CONTROL OF THIS FILE.

    Perfect knowledge in the truth arm means perfect knowledge of the FABRIC — the one number the
    company does not have. The health floor is not a knowledge question at all: it is a rule about
    what may be recommended, read off the same public register in both arms. If the truth arm is
    given a band the company arm is not (or the reverse), the ledger books the difference, and the
    published figure reads *this is what the company's ignorance cost these customers* when what it
    actually measures is a floor protecting cold households.

    The test is a zero-belief-error population: every premise's belief IS its truth, so a non-zero
    forgone figure has no honest source left. It is run at a band that CLEARS the floor and a band
    that does not, because only one of those is a live risk and the file should not have to guess
    which — under `AB`/`C` the floor is silent in both arms; under `F` it removes the measure from
    both, and a one-sided band would leave the truth arm recommending where the company declines.
    """
    for band in ("C", "F", None):
        observations = [_observation(f"P-{i}", band) for i in range(5)]
        result = fgl.money_consequence(observations, unit_rate_p_per_kwh=7.4, belief="epc")
        assert result.forgone_lifetime_gbp == pytest.approx(0.0), (
            f"a population with NO belief error booked £{result.forgone_lifetime_gbp:,.2f} of "
            f"forgone value at band {band!r}. The only input left that can differ between the two "
            "arms is the health floor's band, so the ledger is publishing a safety refusal as "
            "money lost to ignorance.")
        assert result.misranked_premises == 0 and result.declined_where_value_existed == 0


def test_THE_FLOOR_CAN_CHANGE_THE_DECISION_AT_ALL_or_the_control_above_is_a_tautology():
    """A control that cannot fail proves nothing, and the one above would be exactly that if the
    band never reached a decision. This is its reachability leg, kept beside it on purpose.

    At the low-consumption inputs both use, the band is the whole difference between being
    recommended something free and being told nothing is worth doing."""
    common = dict(
        hlc_pessimistic_kw_per_k=_LOW_USE_HLC,
        actionable=True,
        annual_heat_kwh=_LOW_USE_KWH,
        annual_degree_days_k_day=2_200.0,
        unit_rate_p_per_kwh=7.4,
    )
    warm = fi.decide("P-warm", _LOW_USE_HLC, epc_band="C", **common)
    cold = fi.decide("P-cold", _LOW_USE_HLC, epc_band="F", **common)
    blind = fi.decide("P-blind", _LOW_USE_HLC, epc_band=None, **common)
    assert warm.decision is fi.Decision.RECOMMEND and warm.measure == "turn_down", (
        "the zero-capital measure does not win even where every capital measure destroys value, so "
        "the band cannot move a decision and the arms-agree control cannot fail")
    assert cold.decision is fi.Decision.DECLINE_NO_POSITIVE_VALUE
    assert blind.decision is fi.Decision.DECLINE_NO_POSITIVE_VALUE


def _production_decision(observation: fgl.FabricObservation) -> fi.Recommendation:
    """The company arm exactly as `fabric_gap_ledger._premise_forgone` runs it, on the register
    prior. Written out rather than called through `money_consequence` because this test needs the
    per-premise `Recommendation`, which the ledger folds into counts and money."""
    held, relative_sd, basis = observation.belief_arm("epc")
    lower, _upper = ti.log_normal_interval_95(held, relative_sd)
    return fi.decide(
        observation.premise_id,
        held,
        hlc_pessimistic_kw_per_k=lower,
        actionable=ti.is_actionable_belief(basis, relative_sd),
        annual_heat_kwh=observation.annual_heat_kwh,
        annual_degree_days_k_day=observation.annual_degree_days_k_day,
        unit_rate_p_per_kwh=cf.DEFAULT_UNIT_RATE_P_PER_KWH,
        epc_band=observation.epc_band,
    )
