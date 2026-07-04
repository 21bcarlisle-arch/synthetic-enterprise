"""Phase PY: Statistical Equivalence Gate -- tests for tools/synthetic_validation.py.

Validates that the gate module correctly checks 10 statistical properties of the
CorrelatedGeneratorAdapter against 2016-2025 UK energy market benchmarks.
"""
import json
import math
import os
import tempfile
import pytest


class TestModuleStructure:
    def test_module_imports_cleanly(self):
        import tools.synthetic_validation as sv
        assert hasattr(sv, "run_gate")
        assert hasattr(sv, "write_gate_json")
        assert hasattr(sv, "HISTORICAL_BENCHMARKS")

    def test_historical_benchmarks_has_required_keys(self):
        from tools.synthetic_validation import HISTORICAL_BENCHMARKS
        required = {
            "gas_long_run_mean_gbp_per_mwh",
            "elec_long_run_mean_gbp_per_mwh",
            "gas_return_vol_annual_lo",
            "gas_return_vol_annual_hi",
            "elec_return_vol_annual_lo",
            "elec_return_vol_annual_hi",
            "elec_gas_corr_lo",
            "elec_gas_corr_hi",
            "crisis_freq_lo",
            "crisis_freq_hi",
        }
        assert required <= set(HISTORICAL_BENCHMARKS.keys())

    def test_equivalence_check_is_dataclass(self):
        from tools.synthetic_validation import EquivalenceCheck
        import dataclasses
        assert dataclasses.is_dataclass(EquivalenceCheck)
        fields = {f.name for f in dataclasses.fields(EquivalenceCheck)}
        assert {"name", "passed", "value", "benchmark", "message"} <= fields

    def test_equivalence_gate_is_dataclass(self):
        from tools.synthetic_validation import EquivalenceGate
        import dataclasses
        assert dataclasses.is_dataclass(EquivalenceGate)
        fields = {f.name for f in dataclasses.fields(EquivalenceGate)}
        assert {"overall_pass", "checks", "model_params", "n_steps", "timestamp"} <= fields


class TestRunGate:
    def _gate(self):
        from tools.synthetic_validation import run_gate
        return run_gate(seed=0, n_steps=5000)

    def test_run_gate_returns_equivalence_gate(self):
        from tools.synthetic_validation import EquivalenceGate
        gate = self._gate()
        assert isinstance(gate, EquivalenceGate)

    def test_run_gate_passes_with_calibrated_generator(self):
        gate = self._gate()
        assert gate.overall_pass is True, (
            "Gate FAILED. Failed checks: " +
            ", ".join(c.name for c in gate.checks if not c.passed)
        )

    def test_gate_has_ten_checks(self):
        gate = self._gate()
        assert len(gate.checks) == 10

    def test_gate_n_steps_recorded(self):
        gate = self._gate()
        assert gate.n_steps == 5000

    def test_gate_has_timestamp(self):
        gate = self._gate()
        assert gate.timestamp and "T" in gate.timestamp

    def test_gate_model_params_present(self):
        gate = self._gate()
        assert "gas_mu" in gate.model_params
        assert "corr" in gate.model_params
        assert "crisis_prob" in gate.model_params


class TestIndividualChecks:
    def _checks(self):
        from tools.synthetic_validation import run_gate
        gate = run_gate(seed=0, n_steps=5000)
        return {c.name: c for c in gate.checks}

    def test_gas_long_run_mean_passes(self):
        c = self._checks()["gas_long_run_mean"]
        assert c.passed, "gas mean check failed: %s" % c.message

    def test_elec_long_run_mean_passes(self):
        c = self._checks()["elec_long_run_mean"]
        assert c.passed, "elec mean check failed: %s" % c.message

    def test_gas_return_vol_passes(self):
        c = self._checks()["gas_return_vol"]
        assert c.passed, "gas vol check failed: %s" % c.message

    def test_elec_return_vol_passes(self):
        c = self._checks()["elec_return_vol"]
        assert c.passed, "elec vol check failed: %s" % c.message

    def test_elec_gas_correlation_passes(self):
        c = self._checks()["elec_gas_correlation"]
        assert c.passed, "correlation check failed: %s" % c.message

    def test_crisis_freq_passes(self):
        c = self._checks()["crisis_freq"]
        assert c.passed, "crisis_freq check failed: %s" % c.message

    def test_gas_mean_reversion_passes(self):
        c = self._checks()["gas_mean_reversion"]
        assert c.passed, "gas mean reversion check failed: %s" % c.message
        assert c.value < 0.0

    def test_elec_mean_reversion_passes(self):
        c = self._checks()["elec_mean_reversion"]
        assert c.passed, "elec mean reversion check failed: %s" % c.message
        assert c.value < 0.0

    def test_gas_fat_tails_passes(self):
        c = self._checks()["gas_fat_tails"]
        assert c.passed, "gas fat tails check failed: %s" % c.message
        assert c.value > 0.0

    def test_elec_fat_tails_passes(self):
        c = self._checks()["elec_fat_tails"]
        assert c.passed, "elec fat tails check failed: %s" % c.message
        assert c.value > 0.0


class TestGateOutput:
    def test_gate_json_serializable(self):
        from tools.synthetic_validation import run_gate
        import dataclasses
        gate = run_gate(seed=0, n_steps=200)
        data = dataclasses.asdict(gate)
        serialized = json.dumps(data)
        parsed = json.loads(serialized)
        assert "overall_pass" in parsed

    def test_write_gate_json_writes_file(self):
        from tools.synthetic_validation import run_gate, write_gate_json
        gate = run_gate(seed=0, n_steps=200)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name
        try:
            out = write_gate_json(gate, path=tmp_path)
            assert out == tmp_path
            with open(tmp_path) as f:
                data = json.load(f)
            assert "overall_pass" in data
            assert "checks" in data
            assert "model_params" in data
        finally:
            os.unlink(tmp_path)
