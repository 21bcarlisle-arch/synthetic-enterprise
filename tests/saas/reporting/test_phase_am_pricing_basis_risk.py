"""Phase AM: Pricing Basis Risk Attribution section tests."""
import pytest
from saas.reporting.annual_report import _section_pricing_basis_risk


def _brt(cid, term_start, co_fwd, sim_fwd, commodity="electricity"):
    error = (co_fwd - sim_fwd) / sim_fwd if sim_fwd else 0.0
    return {
        "customer_id": cid,
        "commodity": commodity,
        "term_start": term_start,
        "company_fwd_gbp_per_mwh": co_fwd,
        "sim_fwd_gbp_per_mwh": sim_fwd,
        "tariff_error_pct": error,
    }


def _data(brt_entries):
    return {"basis_risk_terms": brt_entries}


# ── 1. Empty basis_risk_terms returns empty ───────────────────────────────────

def test_empty_returns_empty():
    assert _section_pricing_basis_risk({}) == ""
    assert _section_pricing_basis_risk({"basis_risk_terms": []}) == ""


# ── 2. Header present ────────────────────────────────────────────────────────

def test_header_present():
    data = _data([_brt("C1", "2021-01-01", 50.0, 45.0)])
    result = _section_pricing_basis_risk(data)
    assert "## Pricing Basis Risk Attribution" in result


# ── 3. Year shown in table ───────────────────────────────────────────────────

def test_year_in_table():
    data = _data([_brt("C1", "2021-06-30", 50.0, 45.0)])
    result = _section_pricing_basis_risk(data)
    assert "2021" in result


# ── 4. Mean error computed correctly ─────────────────────────────────────────

def test_mean_error_computed():
    # (50-45)/45 = 11.1% over-price
    data = _data([_brt("C1", "2021-01-01", 50.0, 45.0)])
    result = _section_pricing_basis_risk(data)
    assert "+11.1%" in result


# ── 5. Over-pricing year (mean > 15%) flagged HIGH OVER-PRICE ─────────────────

def test_high_over_price_flagged():
    # 3 contracts all +20% → mean = +20%
    entries = [_brt(f"C{i}", "2023-01-01", 60.0, 50.0) for i in range(3)]
    data = _data(entries)
    result = _section_pricing_basis_risk(data)
    assert "HIGH OVER-PRICE" in result


# ── 6. Under-pricing year (mean < -5%) flagged UNDER-PRICE ────────────────────

def test_under_price_flagged():
    # company_fwd=40 < sim_fwd=50 → -20% error
    entries = [_brt(f"C{i}", "2018-01-01", 40.0, 50.0) for i in range(3)]
    data = _data(entries)
    result = _section_pricing_basis_risk(data)
    assert "UNDER-PRICE" in result


# ── 7. On target (mean between -5% and +5%) labelled correctly ────────────────

def test_on_target_labelled():
    # 2% error → on target
    entries = [_brt(f"C{i}", "2020-01-01", 51.0, 50.0) for i in range(3)]
    data = _data(entries)
    result = _section_pricing_basis_risk(data)
    assert "on target" in result


# ── 8. Portfolio-wide mean error shown ───────────────────────────────────────

def test_portfolio_mean_shown():
    data = _data([_brt("C1", "2021-01-01", 50.0, 45.0)])
    result = _section_pricing_basis_risk(data)
    assert "Portfolio-wide mean error" in result or "Portfolio mean" in result


# ── 9. Worst over-pricing year identified in summary ─────────────────────────

def test_worst_over_pricing_year_in_summary():
    entries = [
        _brt("C1", "2023-01-01", 60.0, 50.0),  # +20%
        _brt("C2", "2024-01-01", 55.0, 50.0),  # +10%
    ]
    data = _data(entries)
    result = _section_pricing_basis_risk(data)
    assert "2023" in result
    assert "Worst over-pricing" in result


# ── 10. Multiple years shown in table ────────────────────────────────────────

def test_multiple_years_in_table():
    entries = [
        _brt("C1", "2021-01-01", 50.0, 45.0),
        _brt("C2", "2022-01-01", 52.0, 48.0),
        _brt("C3", "2023-01-01", 60.0, 50.0),
    ]
    data = _data(entries)
    result = _section_pricing_basis_risk(data)
    assert "2021" in result
    assert "2022" in result
    assert "2023" in result


# ── 11. Post-crisis over-pricing note when high years exist ─────────────────

def test_post_crisis_over_pricing_note():
    entries = [_brt(f"C{i}", "2023-06-30", 70.0, 50.0) for i in range(4)]
    data = _data(entries)
    result = _section_pricing_basis_risk(data)
    assert "crisis" in result.lower() or "normalised" in result.lower()


# ── 12. Under-priced years listed in summary ─────────────────────────────────

def test_under_priced_years_in_summary():
    entries = [_brt(f"C{i}", "2018-01-01", 40.0, 50.0) for i in range(4)]
    data = _data(entries)
    result = _section_pricing_basis_risk(data)
    assert "Under-pricing" in result or "under-pric" in result.lower()
    assert "2018" in result
