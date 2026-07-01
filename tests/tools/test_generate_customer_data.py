"""Tests for tools/generate_customer_data.py pure helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_customer_data import _tariff, _meter, _base_id


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
