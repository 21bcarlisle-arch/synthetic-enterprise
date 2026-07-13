"""C10_self_rationing_detection -- unit + coupled-gap wiring tests.

Three layers:
  1. The detector reads OBSERVABLES only and separates a self-rationer (a DROP
     below floor) from a genuinely-low-need home (below floor but NO drop) -- the
     confound it must not fail -- plus the honest blind spots (no baseline,
     arrears, above floor) (unit tests).
  2. Wall + drift discipline: the detector imports nothing from `simulation.*`
     and its TDCV floor tracks the company-side source of truth.
  3. The W2_8 <-> C10 coupled gap wiring is REAL, not theatre: MUTATION tests
     prove the detection-gap fires on its named defects -- a perfect detector
     drives the gap to 0, a blind (flag-nobody) detector to 1, and the harm
     weighting is load-bearing. The scenario is deterministic (C-S2) and the
     ledger write is read-merge-write (preserves siblings). Per CLAUDE.md R15: a
     control that cannot fail is worse than none.
"""

import datetime as dt
import json

import pytest

from company.compliance.domain_invariants import TDCV_ELEC_LOW, TDCV_GAS_LOW
from company.crm.self_rationing_detector import (
    SelfRationingDetector,
    SelfRationingObservation,
    TDCV_LOW_FLOOR_KWH,
    _MATERIAL_DROP_FRACTION,
)
from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRegister

from background.gap_metric import detection_gap, write_gap_entry

import tools.couple_w2_8_c10 as couple


# --------------------------------------------------------------------------
# 1. detector unit behaviour -- the rationer vs low-need discrimination
# --------------------------------------------------------------------------

FLOOR_E = TDCV_ELEC_LOW.low   # 1400


def _obs(**kw):
    base = dict(customer_id="C1", commodity="electricity")
    base.update(kw)
    return SelfRationingObservation(**base)


def test_self_rationer_flagged():
    """A DROP from a normal baseline down below the floor, clean payments,
    baseline present -> flagged, PPM_SELF_DISCONNECTED raised."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1200.0))
    assert r.self_rationing_suspected is True
    assert r.vulnerability_flags == (VulnerabilityFlag.PPM_SELF_DISCONNECTED,)
    assert r.confidence > 0.5
    assert r.signals["below_floor"] is True
    assert r.signals["material_drop"] is True


def test_low_need_home_not_flagged_the_confound():
    """A genuinely-low-need home: below floor but NO drop (observed == baseline).
    This is THE confound -- it must NOT be flagged even though it is below the
    floor with a clean record."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=1050.0, observed_annual_kwh=1050.0))
    assert r.self_rationing_suspected is False
    assert r.vulnerability_flags == ()
    assert r.signals["below_floor"] is True
    assert r.signals["material_drop"] is False
    assert "low-need" in r.signals["not_flagged_reason"]


def test_below_floor_alone_never_flags_without_a_drop():
    """A detector that flags everyone below floor is naive/leaking. A slightly-
    below-floor home with only a trivial (sub-threshold) drop is NOT flagged."""
    det = SelfRationingDetector()
    # 5% drop -- below the 20% material threshold.
    r = det.detect(_obs(baseline_annual_kwh=1300.0, observed_annual_kwh=1235.0))
    assert r.self_rationing_suspected is False


def test_no_baseline_is_the_blind_spot():
    """No usable baseline (traditional meter / switched-in) -> the drop is
    unobservable -> NOT flagged, even though below floor. The detector does NOT
    fall back to below-floor-alone."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=None, observed_annual_kwh=1100.0))
    assert r.self_rationing_suspected is False
    assert r.signals["has_usable_baseline"] is False
    assert "NO usable baseline" in r.signals["not_flagged_reason"]


def test_arrears_deferred_to_collections():
    """A textbook rationing signature BUT arrears open -> the collections channel
    owns it; this silent-hardship flag defers rather than double-flag."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1200.0,
                        arrears_open=True))
    assert r.self_rationing_suspected is False
    assert "collections" in r.signals["not_flagged_reason"]


def test_missed_payment_deferred():
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1200.0,
                        missed_payments=1))
    assert r.self_rationing_suspected is False


def test_drop_but_above_floor_not_flagged():
    """A big cut that still leaves the home above the plausible-living floor is
    belt-tightening, not the below-floor hardship signature."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=4200.0, observed_annual_kwh=1800.0))
    assert r.signals["below_floor"] is False
    assert r.self_rationing_suspected is False


def test_weather_normalisation_masks_a_mild_year():
    """If the whole drop is explained by a much milder period (weather factor),
    the residual cut is below threshold -> NOT flagged (a warm year is not a
    ration). This is an honest observational limit, not a bug."""
    det = SelfRationingDetector()
    # baseline 1700, observed 1300 -> raw drop ~24%. But a mild year (factor
    # 0.80) makes weather-expected 1360, residual drop only ~4% -> not material.
    r = det.detect(_obs(baseline_annual_kwh=1700.0, observed_annual_kwh=1300.0,
                        weather_normalisation_factor=0.80))
    assert r.self_rationing_suspected is False
    assert r.signals["material_drop"] is False


def test_weather_normalisation_still_catches_a_real_cut():
    """A cut BEYOND what a mild year explains is still flagged."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1100.0,
                        weather_normalisation_factor=0.95))
    assert r.self_rationing_suspected is True


def test_confidence_deeper_cut_higher():
    det = SelfRationingDetector()
    shallow = det.detect(_obs(baseline_annual_kwh=1800.0, observed_annual_kwh=1390.0))
    deep = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=700.0))
    assert deep.confidence > shallow.confidence


def test_gas_commodity_floor():
    det = SelfRationingDetector()
    r = det.detect(_obs(commodity="gas", baseline_annual_kwh=11000.0,
                        observed_annual_kwh=4800.0))
    assert r.signals["floor_kwh"] == TDCV_GAS_LOW.low
    assert r.self_rationing_suspected is True


def test_apply_to_register_raises_ppm_flag_with_actions():
    det = SelfRationingDetector()
    reg = VulnerabilityRegister()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1100.0))
    det.apply_to_register(reg, r, dt.date(2024, 1, 1))
    rec = reg.get("C1")
    assert rec is not None
    assert VulnerabilityFlag.PPM_SELF_DISCONNECTED in rec.flags
    # The orphaned flag now drives a real support response.
    assert "offer_emergency_credit" in rec.required_actions
    assert "debt_referral" in rec.required_actions


def test_apply_to_register_no_detection_is_noop():
    det = SelfRationingDetector()
    reg = VulnerabilityRegister()
    r = det.detect(_obs(baseline_annual_kwh=1050.0, observed_annual_kwh=1050.0))
    det.apply_to_register(reg, r, dt.date(2024, 1, 1))
    assert reg.get("C1") is None


# --------------------------------------------------------------------------
# 2. wall + drift discipline
# --------------------------------------------------------------------------

def test_detector_imports_no_simulation():
    import company.crm.self_rationing_detector as mod
    import inspect
    src = inspect.getsource(mod)
    assert "import simulation" not in src
    assert "from simulation" not in src


def test_floor_tracks_company_source_of_truth():
    """The detector floor is the domain_invariants source (regulation commons),
    not a re-derived threshold -- drift guard."""
    assert TDCV_LOW_FLOOR_KWH["electricity"] == TDCV_ELEC_LOW.low
    assert TDCV_LOW_FLOOR_KWH["gas"] == TDCV_GAS_LOW.low


def test_material_threshold_independent_of_sim_severity():
    """R15: the company's drop threshold is NOT the SIM's severity band. W2_8's
    minimum severity is 0.30; the detector's threshold is a lower, independently
    chosen 0.20 (so it is not reading the SIM's number)."""
    from simulation.self_rationing import _SEVERITY_RANGE
    assert _MATERIAL_DROP_FRACTION < _SEVERITY_RANGE[0]


# --------------------------------------------------------------------------
# 3. coupled-gap wiring -- MUTATION tests (the gap must be able to FAIL)
# --------------------------------------------------------------------------

def test_coupled_scenario_gap_is_non_degenerate():
    result, stats = couple.measure(n_customers=2500)
    assert stats["n_truth_detectable"] > 30, "need a real truth set"
    assert stats["n_low_need_below_floor"] > 0, "the confound must be present"
    # A real, honest gap: not perfect (blind spot), not blind (some recovery).
    assert 0.0 < result.gap < 1.0
    # The detector is NOT naive: it excludes the low-need confounds cleanly.
    assert stats["false_positive_rate"] < 0.05


def test_missed_are_the_no_baseline_blind_spot():
    """Every truth account the detector missed is a coverage blind spot, not a
    logic error: with a baseline the rationer is separable by construction."""
    result, stats = couple.measure(n_customers=2500)
    missed = result.components["missed"]
    # All (or essentially all) misses are the no-baseline population.
    assert stats["missed_because_no_baseline"] == missed


def test_scenario_deterministic():
    a, _ = couple.measure(n_customers=1500)
    b, _ = couple.measure(n_customers=1500)
    assert a.gap == b.gap
    assert a.raw_gap == b.raw_gap


def test_mutation_perfect_detector_drives_gap_to_zero():
    """A detector that flags exactly the truth set has gap 0 -- proving the gap
    is not stuck high (a control that can never pass is also broken)."""
    truth, _flagged, harm, _stats = couple.build_scenario(1500)
    perfect = detection_gap(truth, truth, harm=harm)
    assert perfect.gap == 0.0


def test_mutation_blind_detector_drives_gap_to_one():
    """Flag nobody -> the whole detectable harm is missed -> gap == 1."""
    truth, _flagged, harm, _stats = couple.build_scenario(1500)
    blind = detection_gap(truth, set(), harm=harm)
    assert blind.gap == 1.0


def test_mutation_harm_weighting_is_load_bearing():
    """Missing a HIGH-harm account costs more than missing a low-harm one -- the
    harm weighting is real, not decorative."""
    truth = {"a", "b"}
    harm = {"a": 10.0, "b": 1.0}
    miss_high = detection_gap(truth, {"b"}, harm=harm)   # missed a (harm 10)
    miss_low = detection_gap(truth, {"a"}, harm=harm)    # missed b (harm 1)
    assert miss_high.gap > miss_low.gap


def test_ledger_write_is_read_merge_write(tmp_path):
    """Writing the W2_8<->C10 entry preserves existing sibling entries."""
    ledger = tmp_path / "coupled_gap_ledger.json"
    ledger.write_text(json.dumps({
        "W2_5_life_event_stream": {"twin_atom_id": "C7", "gap": 0.4}
    }))
    result, _ = couple.measure(n_customers=800)
    merged = write_gap_entry(
        couple.WORLD_ATOM_ID, couple.TWIN_ATOM_ID, result,
        measured_at="2026-07-13T00:00:00+00:00", run_git_commit="deadbeef",
        ledger_path=ledger,
    )
    assert "W2_5_life_event_stream" in merged   # sibling preserved
    assert "W2_8_self_rationing" in merged
    assert merged["W2_8_self_rationing"]["twin_atom_id"] == "C10_self_rationing_detection"
    assert merged["W2_8_self_rationing"]["metric"] == "detection"
