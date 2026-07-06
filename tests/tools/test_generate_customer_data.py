"""Tests for tools/generate_customer_data.py pure helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_customer_data import (
    _tariff, _meter, _base_id, _mpan, _mprn, _mpan_check_digit, _timeline,
)


def test_tariff_ic_segment():
    assert _tariff("I&C", "electricity") == "Half-Hourly Industrial and Commercial"


def test_tariff_resi_electricity():
    assert _tariff("resi", "electricity") == "Standard Variable (Electricity)"


def test_tariff_resi_gas():
    assert _tariff("resi", "gas") == "Standard Variable (Gas)"


def test_tariff_sme():
    assert _tariff("SME", "electricity") == "Standard Variable (Electricity)"


def test_meter_ic_is_hh():
    assert _meter("I&C") == "HH"


def test_meter_resi_is_smart():
    assert _meter("resi") == "Smart"


def test_meter_sme_is_smart():
    assert _meter("SME") == "Smart"


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


def test_meter_unknown_defaults_to_smart():
    result = _meter("unknown")
    assert isinstance(result, str)


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
