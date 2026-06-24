"""Phase 47b — Cap-aware acquisition gate tests.

The gate prevents resi electricity acquisition when the Ofgem cap
is below the company's forward cost (selling below wholesale cost is irrational).
"""

import pytest
from saas.growth_mandate import should_attempt_acquisition


class TestShouldAttemptAcquisition:
    def test_gate_fires_when_cap_below_fwd(self):
        """2022 crisis: cap=305, fwd=350 → gate fires (cap below wholesale)."""
        ok, reason = should_attempt_acquisition("resi", "electricity", 350.0, "2022-06-01")
        assert not ok
        assert reason is not None
        assert "cap_constrained" in reason

    def test_gate_passes_when_cap_above_fwd(self):
        """2017 normal: cap=None (pre-cap era) → no gate."""
        ok, reason = should_attempt_acquisition("resi", "electricity", 120.0, "2017-06-01")
        assert ok
        assert reason is None

    def test_gate_does_not_fire_for_ic_segment(self):
        """I&C customers are not subject to the domestic price cap."""
        ok, reason = should_attempt_acquisition("I&C", "electricity", 400.0, "2022-06-01")
        assert ok
        assert reason is None

    def test_gate_does_not_fire_for_sme_segment(self):
        """SME customers are not subject to the domestic price cap."""
        ok, reason = should_attempt_acquisition("SME", "electricity", 400.0, "2022-06-01")
        assert ok
        assert reason is None

    def test_gate_does_not_fire_for_gas(self):
        """Gas acquisition is not gated by the electricity cap."""
        ok, reason = should_attempt_acquisition("resi", "gas", 400.0, "2022-06-01")
        assert ok
        assert reason is None

    def test_gate_passes_pre_cap_era(self):
        """Pre-2019 (no cap) → always proceed."""
        ok, reason = should_attempt_acquisition("resi", "electricity", 300.0, "2018-01-01")
        assert ok
        assert reason is None

    def test_gate_passes_when_cap_exactly_equals_fwd(self):
        """Cap == fwd: still profitable (zero margin, but not loss-making). Gate should NOT fire."""
        # get_cap_unit_rate_gbp_per_mwh("electricity", 2022) = 305.0
        ok, reason = should_attempt_acquisition("resi", "electricity", 305.0, "2022-06-01")
        assert ok  # cap >= fwd → not loss-making

    def test_gate_reason_contains_both_values(self):
        """gate_reason string includes both cap and fwd values for auditability."""
        ok, reason = should_attempt_acquisition("resi", "electricity", 350.0, "2022-06-01")
        assert not ok
        assert "305" in reason  # cap value
        assert "350" in reason  # fwd value


class TestAcquisitionGateIntegration:
    """Verify gate fires at module level using 2022 acquisition conditions."""

    def test_resi_not_in_gate_2017(self):
        """2017 is pre-cap era — gate never fires regardless of fwd."""
        ok, _ = should_attempt_acquisition("resi", "electricity", 200.0, "2017-01-01")
        assert ok

    def test_high_fwd_triggers_gate_2022(self):
        """When wholesale spikes above cap in crisis years, gate protects company."""
        ok, reason = should_attempt_acquisition("resi", "electricity", 400.0, "2022-09-01")
        assert not ok
        assert reason is not None
