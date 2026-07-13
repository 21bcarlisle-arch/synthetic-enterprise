"""Unit tests for C6_affordability_inference -- the company-side ability-to-pay
twin. Observable-only inference, deterministic, allowed to be wrong. These tests
assert BEHAVIOUR on observables, never that the inference matches hidden truth
(that is the coupling harness's job -- tests/tools/test_couple_w2_4_c6.py)."""

from __future__ import annotations

import ast
import inspect

import company.crm.affordability_inference as ai_mod
from company.crm.affordability_inference import (
    AffordabilityBand,
    AffordabilityInference,
    AffordabilityObservation,
    BAND_ORDER,
    composition_of,
    composition_vector,
)


def _pay(result: str) -> dict:
    return {"result": result, "days_late": 0}


def _payments(on_time: int, late: int, dd_failed: int) -> list:
    return (
        [_pay("ON_TIME")] * on_time
        + [_pay("LATE")] * late
        + [_pay("DD_FAILED")] * dd_failed
    )


# ---------------------------------------------------------------------------
# Wall: the company twin imports nothing from simulation.*
# ---------------------------------------------------------------------------

def _imported_modules(module) -> set:
    """The set of module names actually IMPORTED by a module (AST-level, so a
    mention in a docstring/comment does not count)."""
    tree = ast.parse(inspect.getsource(module))
    names: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
    return names


def test_no_simulation_import():
    # The wall check that matters: no ACTUAL import from simulation.* (the
    # docstring legitimately names the hidden modules it must never read).
    for mod in _imported_modules(ai_mod):
        assert not mod.startswith("simulation"), mod


# ---------------------------------------------------------------------------
# Band inference from observables
# ---------------------------------------------------------------------------

def test_clean_payer_defaults_managing():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c1", recent_payments=_payments(12, 0, 0),
        annual_consumption_kwh=2900.0,
    )
    a = inf.infer_band(obs)
    assert a.band == AffordabilityBand.MANAGING


def test_high_consumption_clean_payer_comfortable():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c2", recent_payments=_payments(12, 0, 0),
        annual_consumption_kwh=2900.0 * 1.5,  # well above median
    )
    assert inf.infer_band(obs).band == AffordabilityBand.COMFORTABLE


def test_severe_bad_rate_negative():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c3", recent_payments=_payments(4, 2, 6),  # 8/12 bad
    )
    assert inf.infer_band(obs).band == AffordabilityBand.NEGATIVE


def test_moderate_bad_rate_stretched():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c4", recent_payments=_payments(9, 2, 1),  # 3/12 bad ~0.25
    )
    assert inf.infer_band(obs).band == AffordabilityBand.STRETCHED


def test_escalated_arrears_is_negative_even_if_payments_missing():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c5", recent_payments=(), arrears_open=True,
        arrears_stage="second_notice",
    )
    assert inf.infer_band(obs).band == AffordabilityBand.NEGATIVE


def test_open_arrears_first_notice_is_stretched():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c6", recent_payments=_payments(11, 1, 0),
        arrears_open=True, arrears_stage="first_notice",
    )
    assert inf.infer_band(obs).band == AffordabilityBand.STRETCHED


def test_hardship_contact_with_moderate_strain_reads_negative():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c7", recent_payments=_payments(9, 2, 1),  # ~0.25 bad
        inbound_hardship_contacts=1,
    )
    assert inf.infer_band(obs).band == AffordabilityBand.NEGATIVE


# ---------------------------------------------------------------------------
# C-S1 partial observation / C-S2 determinism
# ---------------------------------------------------------------------------

def test_empty_observation_gives_low_confidence_managing():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(customer_id="c8")  # nothing observed
    a = inf.infer_band(obs)
    # No opinion => defaults to MANAGING with the lowest confidence (not a
    # confident comfortable, not a false hardship flag).
    assert a.band == AffordabilityBand.MANAGING
    assert a.confidence <= 0.4


def test_deterministic():
    inf = AffordabilityInference()
    obs = AffordabilityObservation(
        customer_id="c9", recent_payments=_payments(8, 3, 1),
        annual_consumption_kwh=3100.0,
    )
    assert inf.infer_band(obs).band == inf.infer_band(obs).band
    assert inf.infer_band(obs).confidence == inf.infer_band(obs).confidence


# ---------------------------------------------------------------------------
# Book composition
# ---------------------------------------------------------------------------

def test_composition_sums_to_one():
    bands = [AffordabilityBand.NEGATIVE, AffordabilityBand.MANAGING,
             AffordabilityBand.MANAGING, AffordabilityBand.COMFORTABLE]
    dist = composition_of(bands)
    assert abs(sum(dist.values()) - 1.0) < 1e-9
    assert dist[AffordabilityBand.MANAGING] == 0.5


def test_empty_book_is_uniform():
    dist = composition_of([])
    assert all(abs(v - 0.25) < 1e-9 for v in dist.values())


def test_composition_vector_is_in_band_order():
    dist = {AffordabilityBand.NEGATIVE: 0.1, AffordabilityBand.STRETCHED: 0.2,
            AffordabilityBand.MANAGING: 0.3, AffordabilityBand.COMFORTABLE: 0.4}
    assert composition_vector(dist) == [0.1, 0.2, 0.3, 0.4]
    assert list(BAND_ORDER)[0] == AffordabilityBand.NEGATIVE


def test_book_composition_from_observations():
    inf = AffordabilityInference()
    obs = [
        AffordabilityObservation(customer_id="a", recent_payments=_payments(12, 0, 0),
                                 annual_consumption_kwh=2900.0),          # managing
        AffordabilityObservation(customer_id="b", recent_payments=_payments(2, 4, 6),  # negative
                                 ),
    ]
    dist = inf.book_composition(obs)
    assert abs(sum(dist.values()) - 1.0) < 1e-9
    assert dist[AffordabilityBand.NEGATIVE] == 0.5
    assert dist[AffordabilityBand.MANAGING] == 0.5
