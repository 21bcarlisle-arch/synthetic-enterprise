import pytest
from unittest.mock import MagicMock, patch
from simulation.household_demand import HouseholdDemandRegister
from simulation.household import IncomeStress


class TestIncomeStressTrajectory:
    def test_returns_list_of_year_stress_dicts(self):
        hdr = HouseholdDemandRegister([])
        with patch.object(hdr, "income_stress_at_date", return_value=IncomeStress.LOW):
            result = hdr.income_stress_trajectory("C1", [2020, 2021])
        assert len(result) == 2
        assert result[0] == {"year": 2020, "stress": "low"}
        assert result[1] == {"year": 2021, "stress": "low"}

    def test_uses_dec31_as_snapshot_date(self):
        hdr = HouseholdDemandRegister([])
        seen = []

        def mock_stress(cid, date):
            seen.append(date)
            return IncomeStress.MODERATE

        with patch.object(hdr, "income_stress_at_date", side_effect=mock_stress):
            hdr.income_stress_trajectory("C1", [2020, 2021])
        assert seen == ["2020-12-31", "2021-12-31"]

    def test_moderate_stress_value(self):
        hdr = HouseholdDemandRegister([])
        with patch.object(hdr, "income_stress_at_date", return_value=IncomeStress.MODERATE):
            result = hdr.income_stress_trajectory("C1", [2022])
        assert result[0]["stress"] == "moderate"

    def test_high_stress_value(self):
        hdr = HouseholdDemandRegister([])
        with patch.object(hdr, "income_stress_at_date", return_value=IncomeStress.HIGH):
            result = hdr.income_stress_trajectory("C1", [2022])
        assert result[0]["stress"] == "high"

    def test_none_stress_defaults_to_low(self):
        hdr = HouseholdDemandRegister([])
        with patch.object(hdr, "income_stress_at_date", return_value=None):
            result = hdr.income_stress_trajectory("C1", [2022])
        assert result[0]["stress"] == "low"

    def test_empty_years_returns_empty(self):
        hdr = HouseholdDemandRegister([])
        with patch.object(hdr, "income_stress_at_date", return_value=IncomeStress.LOW):
            result = hdr.income_stress_trajectory("C1", [])
        assert result == []

    def test_multiple_years_ordered(self):
        hdr = HouseholdDemandRegister([])
        stresses = [IncomeStress.LOW, IncomeStress.MODERATE, IncomeStress.HIGH]
        call_count = [0]

        def mock_stress(cid, date):
            idx = call_count[0]
            call_count[0] += 1
            return stresses[idx]

        with patch.object(hdr, "income_stress_at_date", side_effect=mock_stress):
            result = hdr.income_stress_trajectory("C1", [2020, 2021, 2022])
        assert [r["stress"] for r in result] == ["low", "moderate", "high"]


class TestLifeEventHistory:
    def _make_event(self, cid, date, event_type):
        e = MagicMock()
        e.customer_id = cid
        e.event_date = date
        e.event_type = event_type
        return e

    def test_returns_list_of_dicts(self):
        hdr = HouseholdDemandRegister([])
        e = self._make_event("C1", "2020-03-15", "job_loss")
        hdr._events = {"C1": [e]}
        result = hdr.life_event_history("C1")
        assert len(result) == 1
        assert result[0] == {"date": "2020-03-15", "event_type": "job_loss"}

    def test_empty_if_no_events(self):
        hdr = HouseholdDemandRegister([])
        result = hdr.life_event_history("C_UNKNOWN")
        assert result == []

    def test_multiple_events_preserved(self):
        hdr = HouseholdDemandRegister([])
        e1 = self._make_event("C1", "2020-03-15", "job_loss")
        e2 = self._make_event("C1", "2021-06-01", "income_recovery")
        hdr._events = {"C1": [e1, e2]}
        result = hdr.life_event_history("C1")
        assert len(result) == 2
        assert result[0]["event_type"] == "job_loss"
        assert result[1]["event_type"] == "income_recovery"

    def test_isolates_to_customer(self):
        hdr = HouseholdDemandRegister([])
        e1 = self._make_event("C1", "2020-03-15", "job_loss")
        e2 = self._make_event("C2", "2021-06-01", "new_baby")
        hdr._events = {"C1": [e1], "C2": [e2]}
        result = hdr.life_event_history("C1")
        assert len(result) == 1
        assert result[0]["event_type"] == "job_loss"


class TestGenerateCustomerSampleBehavioral:
    def test_behavioral_fields_populated_from_run(self, tmp_path):
        import json
        from tools.generate_customer_sample import generate

        run_data = {
            "per_customer_lifetime": {
                "C1": {
                    "segment": "resi", "commodity": "electricity",
                    "revenue_gbp": 1000, "gross_gbp": 200, "net_gbp": 100,
                    "cost_to_serve_gbp": 50, "net_margin_after_cost_to_serve_gbp": 50,
                    "acquisition_date": "2016-01-01",
                },
            },
            "by_billing_account": {},
            "customer_events": [],
            "basis_risk_terms": [],
            "churn_basis_risk": [],
            "per_customer_behavioral": {
                "C1": {
                    "income_stress_trajectory": [{"year": 2020, "stress": "moderate"}],
                    "life_event_history": [{"date": "2020-03-15", "event_type": "job_loss"}],
                    "payment_behaviour_score": "GOOD",
                    "payment_behaviour_metrics": {
                        "on_time_rate": 0.85,
                        "late_rate": 0.10,
                        "dd_fail_rate": 0.02,
                    },
                    "company_satisfaction_score": 0.72,
                    "satisfaction_score_trajectory": [
                        {"year": 2019, "satisfaction_score": 0.70},
                        {"year": 2020, "satisfaction_score": 0.65},
                    ],
                    "payment_miss_trajectory": [
                        {"year": 2020, "late": 1, "dd_failed": 0, "total": 3},
                    ],
                    "bill_shock_history": ["2020-01-15"],
                },
            },
        }
        run_json = tmp_path / "run.json"
        run_json.write_text(json.dumps(run_data))
        out_path = tmp_path / "sample.json"

        import unittest.mock as mock
        with mock.patch("tools.generate_customer_sample.OUT_PATH", out_path), \
             mock.patch("tools.generate_customer_sample.PROJECT", tmp_path):
            (tmp_path / "site" / "state").mkdir(parents=True, exist_ok=True)
            generate(str(run_json))

        result = json.loads(out_path.read_text())
        c1 = result["customers"]["C1"]
        assert c1["income_stress_trajectory"] == [{"year": 2020, "stress": "moderate"}]
        assert c1["life_event_history"] == [{"date": "2020-03-15", "event_type": "job_loss"}]
        assert c1["payment_behaviour_analytics"]["score"] == "GOOD"
        assert c1["data_status"]["income_stress_trajectory"] == "complete"
        assert c1["satisfaction_score_trajectory"] == [
            {"year": 2019, "satisfaction_score": 0.70},
            {"year": 2020, "satisfaction_score": 0.65},
        ]
        assert c1["data_status"]["satisfaction_score_trajectory"] == "complete"
        assert c1["payment_miss_trajectory"] == [
            {"year": 2020, "late": 1, "dd_failed": 0, "total": 3},
        ]
        assert c1["data_status"]["payment_miss_trajectory"] == "complete"
        assert c1["bill_shock_history"] == ["2020-01-15"]
        assert c1["data_status"]["bill_shock_history"] == "complete"
        assert c1["data_status"]["complaint_history"] == "not_simulated"

    def test_behavioral_absent_gives_pending_status(self, tmp_path):
        import json
        from tools.generate_customer_sample import generate

        run_data = {
            "per_customer_lifetime": {
                "C1": {
                    "segment": "resi", "commodity": "electricity",
                    "revenue_gbp": 1000, "gross_gbp": 200, "net_gbp": 100,
                    "cost_to_serve_gbp": 50, "net_margin_after_cost_to_serve_gbp": 50,
                    "acquisition_date": "2016-01-01",
                },
            },
            "by_billing_account": {},
            "customer_events": [],
            "basis_risk_terms": [],
            "churn_basis_risk": [],
        }
        run_json = tmp_path / "run.json"
        run_json.write_text(json.dumps(run_data))
        out_path = tmp_path / "sample.json"

        import unittest.mock as mock
        with mock.patch("tools.generate_customer_sample.OUT_PATH", out_path), \
             mock.patch("tools.generate_customer_sample.PROJECT", tmp_path):
            (tmp_path / "site" / "state").mkdir(parents=True, exist_ok=True)
            generate(str(run_json))

        result = json.loads(out_path.read_text())
        c1 = result["customers"]["C1"]
        assert c1["income_stress_trajectory"] is None
        assert c1["data_status"]["income_stress_trajectory"] == "pending_sim_emission"
        assert c1["payment_behaviour_analytics"] is None
        assert c1["satisfaction_score_trajectory"] is None
        assert c1["data_status"]["satisfaction_score_trajectory"] == "pending_sim_emission"
        assert c1["payment_miss_trajectory"] == []
        assert c1["bill_shock_history"] == []
        assert c1["data_status"]["complaint_history"] == "not_simulated"
