"""Tests for the credit-bureau epistemic-boundary adapter (acquisition funnel, PRIORITIES.md P1).

Verifies the Protocol, SyntheticBureauAdapter calibration/determinism, the factory,
and the epistemic guard that true_creditworthy never leaks into company/** code.
"""
import pytest
from pathlib import Path


class TestCreditBureauPortProtocol:
    def test_synthetic_adapter_satisfies_protocol(self):
        from tools.credit_bureau_port import CreditBureauPort
        from tools.credit_adapters.synthetic_bureau import SyntheticBureauAdapter
        assert isinstance(SyntheticBureauAdapter(), CreditBureauPort)

    def test_protocol_method_present(self):
        from tools.credit_bureau_port import CreditBureauPort
        assert hasattr(CreditBureauPort, "check_credit")

    def test_result_dataclass_fields(self):
        from tools.credit_bureau_port import CreditCheckResult
        r = CreditCheckResult(passed=True, score_band="prime", true_creditworthy=True)
        assert r.passed is True
        assert r.score_band == "prime"
        assert r.true_creditworthy is True


class TestSyntheticBureauAdapter:
    def _adapter(self):
        from tools.credit_adapters.synthetic_bureau import SyntheticBureauAdapter
        return SyntheticBureauAdapter()

    def test_determinism(self):
        a = self._adapter()
        r1 = a.check_credit("cust_A", "resi", "seed_1")
        r2 = a.check_credit("cust_A", "resi", "seed_1")
        assert r1 == r2

    def test_different_applicant_can_differ(self):
        a = self._adapter()
        results = {a.check_credit(f"cust_{i}", "resi", "seed_1") for i in range(50)}
        assert len(results) > 1

    def test_score_band_always_valid(self):
        a = self._adapter()
        for i in range(200):
            r = a.check_credit(f"cust_{i}", "resi", f"seed_{i}")
            assert r.score_band in {"decline", "sub_prime", "near_prime", "prime"}

    def test_decline_iff_not_passed(self):
        a = self._adapter()
        for i in range(500):
            r = a.check_credit(f"cust_{i}", "ic", f"seed_{i}")
            assert (r.score_band == "decline") == (not r.passed)

    def test_resi_pass_rate_in_calibrated_range(self):
        a = self._adapter()
        n = 6000
        passed = sum(a.check_credit(f"cust_{i}", "resi", f"seed_{i}").passed for i in range(n))
        rate = passed / n
        assert 0.90 <= rate <= 0.97, rate

    def test_ic_pass_rate_in_calibrated_range(self):
        a = self._adapter()
        n = 6000
        passed = sum(a.check_credit(f"cust_{i}", "ic", f"seed_{i}").passed for i in range(n))
        rate = passed / n
        assert 0.80 <= rate <= 0.92, rate

    def test_sme_alias_matches_ic(self):
        a = self._adapter()
        r_ic = a.check_credit("cust_A", "ic", "seed_1")
        r_sme = a.check_credit("cust_A", "sme", "seed_1")
        assert r_ic == r_sme

    def test_unknown_segment_falls_back_to_resi(self):
        a = self._adapter()
        r_unknown = a.check_credit("cust_A", "not_a_real_segment", "seed_1")
        r_resi = a.check_credit("cust_A", "resi", "seed_1")
        assert r_unknown == r_resi

    def test_genuine_disagreement_with_ground_truth(self):
        """Noise must produce real false-decline/false-accept divergence -- not a no-op."""
        a = self._adapter()
        n = 4000
        disagree = sum(
            a.check_credit(f"cust_{i}", "resi", f"seed_{i}").passed
            != a.check_credit(f"cust_{i}", "resi", f"seed_{i}").true_creditworthy
            for i in range(n)
        )
        rate = disagree / n
        assert 0.01 < rate < 0.30, rate


class TestCreditAdapterFactory:
    def test_default_returns_synthetic_bureau(self):
        from tools.credit_adapters import get_credit_bureau_adapter
        from tools.credit_adapters.synthetic_bureau import SyntheticBureauAdapter
        assert isinstance(get_credit_bureau_adapter(), SyntheticBureauAdapter)

    def test_explicit_source(self):
        from tools.credit_adapters import get_credit_bureau_adapter
        from tools.credit_adapters.synthetic_bureau import SyntheticBureauAdapter
        assert isinstance(get_credit_bureau_adapter("synthetic_bureau"), SyntheticBureauAdapter)

    def test_env_var_controls_selection(self, monkeypatch):
        from tools.credit_adapters import get_credit_bureau_adapter
        from tools.credit_adapters.synthetic_bureau import SyntheticBureauAdapter
        monkeypatch.setenv("CREDIT_ADAPTER_SOURCE", "synthetic_bureau")
        assert isinstance(get_credit_bureau_adapter(), SyntheticBureauAdapter)

    def test_unknown_source_raises_value_error(self):
        from tools.credit_adapters import get_credit_bureau_adapter
        with pytest.raises(ValueError, match="Unknown credit adapter source"):
            get_credit_bureau_adapter("bureau_v2")


class TestEpistemicGuard:
    def test_true_creditworthy_never_read_by_company_code(self):
        """SIM ground truth (true_creditworthy) must never leak into company/** decision code."""
        repo_root = Path(__file__).resolve().parents[2]
        company_dir = repo_root / "company"
        violations = []
        for path in company_dir.rglob("*.py"):
            if "test" in path.name:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "true_creditworthy" in text:
                violations.append(str(path))
        assert violations == [], f"true_creditworthy leaked into company code: {violations}"
