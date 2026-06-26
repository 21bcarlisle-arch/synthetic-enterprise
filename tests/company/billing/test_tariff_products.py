"""Phase 142: Green tariff product catalogue tests."""
import pytest
from company.billing.tariff_products import TariffProduct, TariffCatalogue


# --- TariffProduct construction ---

def test_tariff_product_fields():
    p = TariffCatalogue.get_by_code("GREEN_FIX_1YR")
    assert p is not None
    assert p.code == "GREEN_FIX_1YR"
    assert p.name == "Green Fix 1 Year"
    assert p.commodity == "electricity"
    assert p.segment == "resi"
    assert p.term == "fixed_1yr"
    assert p.is_green is True
    assert p.rego_required_pct == 1.0
    assert p.unit_rate_premium_pct == 0.015
    assert p.launch_date == "2018-04-01"
    assert p.withdrawal_date is None


def test_product_is_immutable():
    p = TariffCatalogue.get_by_code("STD_FIX_1YR")
    with pytest.raises((AttributeError, TypeError)):
        p.is_green = True  # frozen=True must prevent mutation


# --- active_products() ---

def test_active_products_no_date_excludes_withdrawn():
    active = TariffCatalogue.active_products()
    codes = [p.code for p in active]
    assert "IC_GREEN_CERT" not in codes  # withdrawn 2023-12-31


def test_active_products_before_launch_excluded():
    # GREEN_FIX_1YR launched 2018-04-01
    active = TariffCatalogue.active_products("2017-12-31")
    codes = [p.code for p in active]
    assert "GREEN_FIX_1YR" not in codes
    assert "STD_FIX_1YR" in codes


def test_active_products_after_withdrawal_excluded():
    # IC_GREEN_CERT withdrawn 2023-12-31
    active = TariffCatalogue.active_products("2024-01-01")
    codes = [p.code for p in active]
    assert "IC_GREEN_CERT" not in codes


def test_active_products_within_window_included():
    # IC_GREEN_CERT: launched 2020-01-01, withdrawn 2023-12-31
    active = TariffCatalogue.active_products("2022-06-01")
    codes = [p.code for p in active]
    assert "IC_GREEN_CERT" in codes


# --- products_for_segment() ---

def test_products_for_resi():
    products = TariffCatalogue.products_for_segment("resi", "2020-01-01")
    for p in products:
        assert p.segment in ("resi", "all")
    codes = [p.code for p in products]
    assert "STD_FIX_1YR" in codes
    assert "GREEN_FIX_1YR" in codes
    assert "SME_FIXED" not in codes
    assert "IC_BASELOAD" not in codes


def test_products_for_sme():
    products = TariffCatalogue.products_for_segment("sme", "2020-01-01")
    codes = [p.code for p in products]
    assert "SME_FIXED" in codes
    assert "STD_FIX_1YR" not in codes


def test_products_for_ic():
    products = TariffCatalogue.products_for_segment("ic", "2022-06-01")
    codes = [p.code for p in products]
    assert "IC_BASELOAD" in codes
    assert "IC_GREEN_CERT" in codes  # within window 2020-01-01 to 2023-12-31
    assert "SME_FIXED" not in codes


# --- green_products() ---

def test_green_products_all_are_green():
    green = TariffCatalogue.green_products("2020-01-01")
    assert len(green) > 0
    for p in green:
        assert p.is_green is True


def test_green_products_non_green_excluded():
    green = TariffCatalogue.green_products("2020-01-01")
    codes = [p.code for p in green]
    assert "STD_FIX_1YR" not in codes
    assert "STD_VAR" not in codes
    assert "SME_FIXED" not in codes


# --- get_by_code() ---

def test_get_by_code_found():
    p = TariffCatalogue.get_by_code("SME_GREEN")
    assert p is not None
    assert p.segment == "sme"
    assert p.is_green is True


def test_get_by_code_not_found():
    p = TariffCatalogue.get_by_code("NONEXISTENT_CODE")
    assert p is None


# --- rego_requirement_mwh() ---

def test_rego_requirement_green_product_100pct():
    # GREEN_FIX_1YR: 100% REGO; 3500 kWh = 3.5 MWh required
    req = TariffCatalogue.rego_requirement_mwh(3500.0, "GREEN_FIX_1YR")
    assert abs(req - 3.5) < 0.0001


def test_rego_requirement_green_product_50pct():
    # IC_GREEN_CERT: 50% REGO; 2000000 kWh = 2000 MWh * 0.5 = 1000 MWh
    req = TariffCatalogue.rego_requirement_mwh(2_000_000.0, "IC_GREEN_CERT")
    assert abs(req - 1000.0) < 0.001


def test_rego_requirement_non_green_is_zero():
    req = TariffCatalogue.rego_requirement_mwh(3500.0, "STD_FIX_1YR")
    assert req == 0.0


def test_rego_requirement_unknown_code_is_zero():
    req = TariffCatalogue.rego_requirement_mwh(3500.0, "NO_SUCH_PRODUCT")
    assert req == 0.0


# --- summary() ---

def test_summary_structure():
    s = TariffCatalogue.summary("2020-01-01")
    assert "active_count" in s
    assert "green_count" in s
    assert "by_segment" in s
    assert s["active_count"] >= s["green_count"]
    assert s["green_count"] > 0


def test_summary_green_count_matches_green_products():
    date = "2022-06-01"
    s = TariffCatalogue.summary(date)
    green = TariffCatalogue.green_products(date)
    assert s["green_count"] == len(green)


def test_summary_segment_counts_add_up():
    date = "2020-01-01"
    s = TariffCatalogue.summary(date)
    total_in_segments = sum(s["by_segment"].values())
    assert total_in_segments == s["active_count"]
