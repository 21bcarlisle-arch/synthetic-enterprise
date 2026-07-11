"""Tests for tools/generate_customer_data.py pure helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

import json

from tools.generate_customer_data import (
    _tariff, _meter, _base_id, _mpan, _mprn, _mpan_check_digit, _timeline,
    _forecast_cashflow, generate,
)
import tools.generate_customer_data as gcd_module


def test_tariff_ic_segment():
    assert _tariff("I&C", "electricity") == "Half-Hourly Industrial and Commercial"


def test_tariff_resi_electricity():
    assert _tariff("resi", "electricity") == "Standard Variable (Electricity)"


def test_tariff_resi_gas():
    assert _tariff("resi", "gas") == "Standard Variable (Gas)"


def test_tariff_sme():
    assert _tariff("SME", "electricity") == "Standard Variable (Electricity)"


def test_meter_ic_is_hh():
    assert _meter("C_IC1", "I&C") == "HH"


def test_meter_reflects_real_smart_meter_status():
    """Was a hardcoded "always Smart" placeholder for every non-I&C
    customer (Rich-flagged 2026-07-09: let C1 show "Smart" on the site while
    its actual meter-read data behaved like a traditional meter). Now
    resolves the real per-customer status via saas.customers +
    simulation.meter_reads.meter_type_for_customer -- C1 is genuinely smart,
    C3 genuinely is not (saas/property_model.py's ASSET_PROFILE_BY_CUSTOMER)."""
    assert _meter("C1", "resi") == "Smart"
    assert _meter("C3", "resi") == "Traditional"


def test_meter_gas_twin_inherits_electricity_siblings_status():
    assert _meter("C1g", "resi") == "Smart"
    assert _meter("C3g", "resi") == "Traditional"


def test_meter_sme_without_known_profile_defaults_traditional():
    # C5/C6 (SME) have no ASSET_PROFILE_BY_CUSTOMER entry and no explicit
    # smart_meter/metering flag -- meter_type_for_customer's own documented
    # default applies.
    assert _meter("C5", "SME") == "Traditional"


def test_base_id_strips_gas_suffix():
    assert _base_id("C1g") == "C1"


def test_base_id_strips_ic_gas_suffix():
    assert _base_id("C_IC3g") == "C_IC3"


def test_base_id_no_suffix():
    assert _base_id("C1") == "C1"


def test_base_id_single_char():
    assert _base_id("g") == "g"


def test_tariff_unknown_segment_defaults_to_resi():
    result = _tariff("unknown", "electricity")
    assert isinstance(result, str)
    assert len(result) > 0


def test_meter_unknown_customer_defaults_to_traditional():
    result = _meter("unknown_customer_id", "resi")
    assert result == "Traditional"


def test_base_id_strips_trailing_g_only():
    assert _base_id("Cgg") == "Cg"


def test_mpan_bottom_line_is_11_digits():
    m = _mpan("C1", "resi")
    assert len(m["bottom_line"]) == 11
    assert m["bottom_line"].isdigit()


def test_mpan_top_line_is_7_digits():
    m = _mpan("C1", "resi")
    assert len(m["top_line"]) == 7


def test_mpan_deterministic():
    assert _mpan("C1", "resi") == _mpan("C1", "resi")


def test_mpan_differs_by_account():
    assert _mpan("C1", "resi") != _mpan("C2", "resi")


def test_mpan_ic_uses_profile_class_05():
    m = _mpan("C_IC1", "I&C")
    assert m["top_line"][:2] == "05"


def test_mpan_resi_uses_profile_class_01():
    m = _mpan("C1", "resi")
    assert m["top_line"][:2] == "01"


def test_mpan_check_digit_matches_published_algorithm():
    core = "00012345"
    weights = [3, 5, 7, 13, 17, 19, 23, 29]
    expected = str((sum(int(d) * w for d, w in zip(core, weights)) % 11) % 10)
    assert _mpan_check_digit(core) == expected


def test_mprn_is_8_digits():
    assert len(_mprn("C1g")) == 8
    assert _mprn("C1g").isdigit()


def test_mprn_deterministic():
    assert _mprn("C1g") == _mprn("C1g")


def test_timeline_merges_and_sorts_by_date():
    run = {
        "customer_events": [
            {"customer_id": "C1", "event_date": "2018-01-01", "commodity": "electricity",
             "event_type": "renewed", "unit_rate_gbp_per_mwh": 100.0},
            {"customer_id": "C1", "event_date": "2016-01-01", "commodity": "electricity",
             "event_type": "renewed", "unit_rate_gbp_per_mwh": 90.0},
        ],
        "per_customer_behavioral": {
            "C1": {"life_event_history": [{"date": "2017-01-01", "event_type": "new_baby"}]},
        },
    }
    tl = _timeline(run, "C1")
    assert [e["date"] for e in tl] == ["2016-01-01", "2017-01-01", "2018-01-01"]
    assert tl[1]["type"] == "life_event"
    assert tl[1]["detail"] == "New baby"


def test_timeline_includes_gas_twin_events():
    run = {
        "customer_events": [
            {"customer_id": "C1g", "event_date": "2019-01-01", "commodity": "gas",
             "event_type": "churned"},
        ],
        "per_customer_behavioral": {},
    }
    tl = _timeline(run, "C1")
    assert len(tl) == 1
    assert tl[0]["commodity"] == "gas"


def test_timeline_empty_when_no_data():
    assert _timeline({}, "C1") == []


class TestForecastCashflow:
    def test_zero_margin_returns_empty(self):
        assert _forecast_cashflow(0, 5.0, 0.10) == []

    def test_zero_lifetime_returns_empty(self):
        assert _forecast_cashflow(1000.0, 0, 0.10) == []

    def test_negative_lifetime_returns_empty(self):
        assert _forecast_cashflow(1000.0, -1.0, 0.10) == []

    def test_whole_year_lifetime_row_count(self):
        rows = _forecast_cashflow(1000.0, 3.0, 0.10)
        assert len(rows) == 3
        assert [r["year_offset"] for r in rows] == [1, 2, 3]

    def test_fractional_lifetime_rounds_up_row_count(self):
        rows = _forecast_cashflow(1000.0, 2.5, 0.10)
        assert len(rows) == 3

    def test_fractional_final_year_is_partial_weight(self):
        rows = _forecast_cashflow(1000.0, 2.5, 0.10)
        assert rows[0]["undiscounted_gbp"] == pytest.approx(1000.0)
        assert rows[1]["undiscounted_gbp"] == pytest.approx(1000.0)
        assert rows[2]["undiscounted_gbp"] == pytest.approx(500.0)

    def test_capped_at_ten_years(self):
        rows = _forecast_cashflow(1000.0, 25.0, 0.10)
        assert len(rows) == 10

    def test_discounted_less_than_undiscounted_for_positive_rate(self):
        rows = _forecast_cashflow(1000.0, 3.0, 0.10)
        for r in rows:
            assert r["discounted_gbp"] < r["undiscounted_gbp"]

    def test_discounted_sum_reconciles_with_clv_annuity(self):
        # Same math as saas/clv_model.py's annuity_factor -- the discounted
        # sum here should equal avg_annual_margin * annuity_factor(lifetime, rate).
        avg_margin = 1000.0
        lifetime = 4.0
        rate = 0.10
        rows = _forecast_cashflow(avg_margin, lifetime, rate)
        total_discounted = sum(r["discounted_gbp"] for r in rows)
        whole = int(lifetime)
        expected = sum(avg_margin / (1.0 + rate) ** k for k in range(1, whole + 1))
        assert total_discounted == pytest.approx(expected, abs=0.01)

    def test_later_years_discounted_less_than_earlier(self):
        rows = _forecast_cashflow(1000.0, 5.0, 0.10)
        discounted = [r["discounted_gbp"] for r in rows]
        assert discounted == sorted(discounted, reverse=True)


class TestAvgHedgeFractionThreadedIntoOutput:
    """2026-07-11, HARDEN sweep (harden_sweep:live_site:B3_hedge_tariff_alignment):
    avg_hedge_fraction was computed in per_customer_lifetime but never reached
    a per-customer site JSON file -- this proves the full thread."""

    def test_field_present_and_correct_when_computed(self, tmp_path, monkeypatch):
        run = {
            "per_customer_lifetime": {
                "C1": {
                    "segment": "resi", "commodity": "electricity",
                    "acquisition_date": "2016-01-01",
                    "revenue_gbp": 100.0, "gross_gbp": 20.0, "net_gbp": 15.0,
                    "cost_to_serve_gbp": 5.0, "pricing_action": "NONE",
                    "avg_hedge_fraction": 0.6667,
                },
            },
            "by_billing_account": {}, "per_cid_comm_pnl": {},
        }
        run_path = tmp_path / "run.json"
        run_path.write_text(json.dumps(run))
        out_dir = tmp_path / "out"
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        generate(run_json_path=run_path)

        obj = json.loads((out_dir / "C1.json").read_text())
        assert obj["avg_hedge_fraction"] == 0.6667

    def test_field_none_when_not_computed(self, tmp_path, monkeypatch):
        run = {
            "per_customer_lifetime": {
                "C1": {
                    "segment": "resi", "commodity": "electricity",
                    "acquisition_date": "2016-01-01",
                    "revenue_gbp": 100.0, "gross_gbp": 20.0, "net_gbp": 15.0,
                    "cost_to_serve_gbp": 5.0, "pricing_action": "NONE",
                    "avg_hedge_fraction": None,
                },
            },
            "by_billing_account": {}, "per_cid_comm_pnl": {},
        }
        run_path = tmp_path / "run.json"
        run_path.write_text(json.dumps(run))
        out_dir = tmp_path / "out"
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        generate(run_json_path=run_path)

        obj = json.loads((out_dir / "C1.json").read_text())
        assert obj["avg_hedge_fraction"] is None
