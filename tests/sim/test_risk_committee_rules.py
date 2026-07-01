"""Tests for sim/risk_committee_rules.py -- deterministic rule engine."""

import pytest

from sim.risk_committee_rules import (
    CRISIS_SIGMA_THRESHOLD,
    _adjustment_step,
    apply_rules,
    decide,
    parse_handshake,
    should_escalate,
)


def _context(hf_str="C1=0.70 C2=0.80", ratio=2.6, sigma=1.2, triggered="C1, C2"):
    return (
        f"Per-customer hedge_fraction: {hf_str}\n"
        f"Ratio: {ratio}\n"
        f"Rolling 12m SSP: \u03c3_recent = {sigma}\n"
        f"Recommendation requested: adjust hedge_fraction for {triggered}"
    )


# --- parse_handshake ---

def test_parse_handshake_hedge_fractions():
    parsed = parse_handshake(_context(hf_str="C1=0.70 C2=0.80"))
    assert parsed["hedge_fractions"]["C1"] == pytest.approx(0.70)
    assert parsed["hedge_fractions"]["C2"] == pytest.approx(0.80)


def test_parse_handshake_var_ratio():
    parsed = parse_handshake(_context(ratio=2.6))
    assert parsed["var_ratio"] == pytest.approx(2.6)


def test_parse_handshake_sigma_recent():
    parsed = parse_handshake(_context(sigma=1.316))
    assert parsed["sigma_recent"] == pytest.approx(1.316)


def test_parse_handshake_triggered_customers():
    parsed = parse_handshake(_context(triggered="C1, C5, C7"))
    assert "C1" in parsed["triggered_customers"]
    assert "C5" in parsed["triggered_customers"]
    assert "C7" in parsed["triggered_customers"]


def test_parse_handshake_empty_context_defaults():
    parsed = parse_handshake("no fields here")
    assert parsed["var_ratio"] == 0.0
    assert parsed["sigma_recent"] == 0.0
    assert parsed["triggered_customers"] == []


# --- should_escalate ---

def test_should_escalate_high_sigma():
    parsed = {"sigma_recent": CRISIS_SIGMA_THRESHOLD + 0.1, "triggered_customers": ["C1"], "hedge_fractions": {"C1": 0.5}}
    assert should_escalate(parsed) is True


def test_should_escalate_all_at_max():
    parsed = {"sigma_recent": 0.5, "triggered_customers": ["C1", "C2"], "hedge_fractions": {"C1": 1.0, "C2": 1.0}}
    assert should_escalate(parsed) is True


def test_should_not_escalate_normal():
    parsed = {"sigma_recent": 1.0, "triggered_customers": ["C1"], "hedge_fractions": {"C1": 0.7}}
    assert should_escalate(parsed) is False


# --- _adjustment_step ---

def test_adjustment_step_severe():
    assert _adjustment_step(3.0) == pytest.approx(0.25)


def test_adjustment_step_moderate():
    assert _adjustment_step(2.5) == pytest.approx(0.20)


def test_adjustment_step_mild():
    assert _adjustment_step(2.0) == pytest.approx(0.15)


# --- apply_rules ---

def test_apply_rules_increments_hf():
    parsed = {"triggered_customers": ["C1"], "var_ratio": 2.6, "hedge_fractions": {"C1": 0.70}}
    result = apply_rules(parsed, {"C1": 0.70})
    assert "C1" in result
    assert result["C1"] > 0.70


def test_apply_rules_caps_at_one():
    parsed = {"triggered_customers": ["C1"], "var_ratio": 3.5, "hedge_fractions": {"C1": 0.90}}
    result = apply_rules(parsed, {"C1": 0.90})
    assert result["C1"] <= 1.0


def test_apply_rules_already_at_max_no_change():
    parsed = {"triggered_customers": ["C1"], "var_ratio": 2.6, "hedge_fractions": {"C1": 1.0}}
    result = apply_rules(parsed, {"C1": 1.0})
    assert "C1" not in result


# --- decide ---

def test_decide_normal_no_escalate():
    ctx = _context(sigma=1.0, ratio=2.6)
    escalate, _ = decide(ctx, {"C1": 0.70, "C2": 0.80})
    assert escalate is False


def test_decide_crisis_sigma_escalates():
    ctx = _context(sigma=1.8, ratio=2.6)
    escalate, _ = decide(ctx, {"C1": 0.70})
    assert escalate is True
