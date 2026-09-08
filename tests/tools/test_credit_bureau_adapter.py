"""Tests for the credit-bureau epistemic-boundary adapter (acquisition funnel, PRIORITIES.md P1).

Verifies the Protocol, SyntheticBureauAdapter calibration/determinism, the factory,
and the epistemic guard that true_creditworthy never leaks into company/** code.
"""
import pytest
from pathlib import Path

from tools.python_code_text import searchable


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
    @staticmethod
    def _company_modules_reading_ground_truth(root: Path) -> list[str]:
        """company/** modules that READ `true_creditworthy`, as opposed to naming it.

        TWO SUBSTRING BUGS LIVED HERE, both the same class: a spelling standing in for a
        structure.

        THE FILENAME FILTER. `"test" in path.name` excluded four production modules from an
        epistemic wall — `liquidity_stress_test.py`, `collateral_death_test.py`,
        `stress_test.py` and, because "attestation" contains "test",
        `annual_compliance_attestation_register.py`. Risk and compliance code is precisely where
        a creditworthiness leak would be worth having, and the wall could not see it. A test
        module is one pytest collects, which is a `test_` PREFIX, not the letters anywhere.

        THE BODY SCAN. `"true_creditworthy" in text` cannot tell a read from a comment saying
        the read is forbidden, so documenting the wall breached it. `searchable()` blanks
        comments and docstrings and leaves everything a running module could touch.
        """
        out = []
        for path in sorted(root.rglob("*.py")):
            if path.name.startswith("test_") or "/tests/" in path.as_posix():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "true_creditworthy" in searchable(text):
                out.append(str(path))
        return out

    def test_true_creditworthy_never_read_by_company_code(self):
        """SIM ground truth (true_creditworthy) must never leak into company/** decision code."""
        repo_root = Path(__file__).resolve().parents[2]
        company_dir = repo_root / "company"
        violations = self._company_modules_reading_ground_truth(company_dir)
        assert violations == [], f"true_creditworthy leaked into company code: {violations}"

    def test_the_wall_scan_has_a_subject(self):
        """FAIL-SILENT GUARD. The scan above passes on every input if it walks nothing, and a
        renamed root or a typo would do exactly that while reading like a clean wall."""
        repo_root = Path(__file__).resolve().parents[2]
        scanned = [p for p in (repo_root / "company").rglob("*.py")
                   if not p.name.startswith("test_")]
        assert len(scanned) > 50, f"company/ scan saw only {len(scanned)} modules — blind"

    def test_the_wall_catches_a_real_read(self, tmp_path):
        """REACHABILITY, asserted before anything is asserted about the tree. MUTATION: narrow
        the scan to nothing and this fires; without it the green above means nothing."""
        (tmp_path / "leaky.py").write_text("score = customer['true_creditworthy']\n")
        assert self._company_modules_reading_ground_truth(tmp_path) == [
            str(tmp_path / "leaky.py")]

    def test_a_module_named_for_a_stress_test_is_still_inside_the_wall(self, tmp_path):
        """The filename defect, pinned. MUTATION: restore `"test" in path.name` and this fires —
        four real company/risk and company/regulatory modules leave the wall with it."""
        (tmp_path / "liquidity_stress_test.py").write_text("x = true_creditworthy\n")
        (tmp_path / "annual_compliance_attestation_register.py").write_text(
            "y = true_creditworthy\n")
        assert len(self._company_modules_reading_ground_truth(tmp_path)) == 2

    def test_documenting_the_wall_does_not_breach_it(self, tmp_path):
        """THE OTHER DIRECTION. MUTATION: drop `searchable()` and this fires — a module that
        explains why it must not read ground truth is reported as reading it."""
        (tmp_path / "honest.py").write_text(
            '"""Scores from the bureau adapter only; true_creditworthy is SIM-side."""\n'
            "# never read true_creditworthy here -- it is ground truth\n"
            "score = bureau.score(account)\n"
        )
        assert self._company_modules_reading_ground_truth(tmp_path) == []
