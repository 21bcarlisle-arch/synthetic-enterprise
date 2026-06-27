"""Tests for the deterministic risk committee rule engine."""
import pytest
from sim.risk_committee_rules import (
    parse_handshake, should_escalate, apply_rules, decide, CRISIS_SIGMA_THRESHOLD,
)

# Sample handshake context (matches real file format)
SAMPLE_CONTEXT = """## Risk Committee Wake-Up -- 2019-06-15 period 1
Trigger: VaR_current £850.00 exceeds VaR_stressed £320.00 x 2.5 (ratio 2.66)
Treasury balance: £2500000.00 (12-month peak: £2550000.00, drawdown: 2.0%)
Portfolio gross margin YTD: £45000.00 | Net margin YTD: £12000.00
Capital costs YTD: £3500.00
VaR_current: £850.00 | VaR_stressed: £320.00 | Ratio: 2.66
Per-customer hedge_fraction: C1=0.80 C2=0.75 C3=0.90 C4=0.85
Per-customer collateral: C1: collateral=£100.00 coc=£0.80/mo C2: collateral=£80.00 coc=£0.65/mo
Rolling 12m SSP: sigma_recent = 0.950 | Forward price: £45.00/MWh
Regime: pre-2023 (sigma_stressed = 0.50)
Recommendation requested: adjust hedge_fraction for C1, C2
"""

CRISIS_CONTEXT = """## Risk Committee Wake-Up -- 2022-10-01 period 1
Trigger: VaR_current £5000.00 exceeds VaR_stressed £1200.00 x 2.5 (ratio 4.17)
Treasury balance: £1800000.00 (12-month peak: £2400000.00, drawdown: 25.0%)
VaR_current: £5000.00 | VaR_stressed: £1200.00 | Ratio: 4.17
Per-customer hedge_fraction: C1=0.70 C2=0.65
Per-customer collateral: C1: collateral=£500.00 coc=£4.00/mo
Rolling 12m SSP: sigma_recent = 1.800 | Forward price: £250.00/MWh
Regime: post-2023 (sigma_stressed = 1.50)
Recommendation requested: adjust hedge_fraction for C1, C2
"""

MAXED_CONTEXT = """## Risk Committee Wake-Up -- 2020-01-01 period 1
Trigger: VaR_current £900.00 exceeds VaR_stressed £350.00 x 2.5 (ratio 2.57)
VaR_current: £900.00 | VaR_stressed: £350.00 | Ratio: 2.57
Per-customer hedge_fraction: C1=1.00 C2=1.00
Per-customer collateral: C1: collateral=£200.00 coc=£1.60/mo
Rolling 12m SSP: sigma_recent = 0.800 | Forward price: £42.00/MWh
Recommendation requested: adjust hedge_fraction for C1, C2
"""


class TestParseHandshake:
    def test_hedge_fractions_parsed(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        assert parsed["hedge_fractions"]["C1"] == pytest.approx(0.80)
        assert parsed["hedge_fractions"]["C2"] == pytest.approx(0.75)
        assert parsed["hedge_fractions"]["C3"] == pytest.approx(0.90)

    def test_var_ratio_parsed(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        assert parsed["var_ratio"] == pytest.approx(2.66)

    def test_sigma_parsed(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        assert parsed["sigma_recent"] == pytest.approx(0.950)

    def test_triggered_customers_parsed(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        assert "C1" in parsed["triggered_customers"]
        assert "C2" in parsed["triggered_customers"]

    def test_crisis_sigma_parsed(self):
        parsed = parse_handshake(CRISIS_CONTEXT)
        assert parsed["sigma_recent"] == pytest.approx(1.800)

    def test_empty_context_safe(self):
        parsed = parse_handshake("")
        assert parsed["hedge_fractions"] == {}
        assert parsed["var_ratio"] == 0.0
        assert parsed["triggered_customers"] == []


class TestShouldEscalate:
    def test_no_escalate_routine(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        assert should_escalate(parsed) is False

    def test_escalate_crisis_sigma(self):
        parsed = parse_handshake(CRISIS_CONTEXT)
        assert should_escalate(parsed) is True

    def test_escalate_all_maxed(self):
        parsed = parse_handshake(MAXED_CONTEXT)
        assert should_escalate(parsed) is True

    def test_no_escalate_partial_maxed(self):
        # One maxed, one not — should not escalate
        context = SAMPLE_CONTEXT.replace(
            "Per-customer hedge_fraction: C1=0.80 C2=0.75 C3=0.90 C4=0.85",
            "Per-customer hedge_fraction: C1=1.00 C2=0.75 C3=0.90 C4=0.85"
        )
        parsed = parse_handshake(context)
        assert should_escalate(parsed) is False


class TestApplyRules:
    def test_adjusts_triggered_customers(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        result = apply_rules(parsed, {"C1": 0.80, "C2": 0.75, "C3": 0.90})
        assert "C1" in result
        assert "C2" in result
        assert result["C1"] > 0.80
        assert result["C2"] > 0.75

    def test_does_not_adjust_non_triggered(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        result = apply_rules(parsed, {"C1": 0.80, "C2": 0.75, "C3": 0.90})
        assert "C3" not in result

    def test_caps_at_1_0(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        result = apply_rules(parsed, {"C1": 0.95, "C2": 0.95})
        assert result.get("C1", 0.95) <= 1.0
        assert result.get("C2", 0.95) <= 1.0

    def test_step_severe_breach(self):
        # ratio >= 3.0 -> step 0.25
        context = SAMPLE_CONTEXT.replace("Ratio: 2.66", "Ratio: 3.10")
        parsed = parse_handshake(context)
        result = apply_rules(parsed, {"C1": 0.70, "C2": 0.70})
        assert result["C1"] == pytest.approx(0.95)

    def test_step_moderate_breach(self):
        # ratio 2.5-3.0 -> step 0.20
        parsed = parse_handshake(SAMPLE_CONTEXT)  # ratio 2.66
        result = apply_rules(parsed, {"C1": 0.70, "C2": 0.70})
        assert result["C1"] == pytest.approx(0.90)

    def test_step_mild_breach(self):
        # ratio < 2.5 -> step 0.15
        context = SAMPLE_CONTEXT.replace("Ratio: 2.66", "Ratio: 2.10")
        parsed = parse_handshake(context)
        result = apply_rules(parsed, {"C1": 0.70, "C2": 0.70})
        assert result["C1"] == pytest.approx(0.85)

    def test_no_adjustment_if_already_at_1(self):
        parsed = parse_handshake(SAMPLE_CONTEXT)
        result = apply_rules(parsed, {"C1": 1.0, "C2": 1.0})
        assert "C1" not in result
        assert "C2" not in result


class TestDecide:
    def test_routine_no_escalate(self):
        escalate, adjustments = decide(SAMPLE_CONTEXT, {"C1": 0.80, "C2": 0.75})
        assert escalate is False
        assert "C1" in adjustments

    def test_crisis_escalates(self):
        escalate, adjustments = decide(CRISIS_CONTEXT, {"C1": 0.70, "C2": 0.65})
        assert escalate is True
        assert adjustments == {}

    def test_maxed_escalates(self):
        escalate, adjustments = decide(MAXED_CONTEXT, {"C1": 1.0, "C2": 1.0})
        assert escalate is True

    def test_current_hf_overrides_parsed_hf(self):
        # If current_hf differs from what is in the context, current_hf wins
        escalate, adjustments = decide(SAMPLE_CONTEXT, {"C1": 0.95, "C2": 0.95})
        assert escalate is False
        # Both customers should cap at 1.0 from 0.95 + 0.20 = 1.0 (capped)
        assert adjustments.get("C1", 0.95) <= 1.0
