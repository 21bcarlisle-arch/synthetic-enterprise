import pytest
"""Phase 136: Renewal pricing engine tests."""

from company.billing.renewal_engine import generate_renewal_pack, RenewalPack


def _pack(segment="RESI", spot=22.0, consumption=3500.0):
    return generate_renewal_pack(
        customer_id="C1",
        segment=segment,
        spot_price_p_kwh=spot,
        annual_consumption_kwh=consumption,
        expiry_date="2024-06-30",
        days_to_expiry=42,
        quote_valid_until="2024-05-31",
    )


def test_returns_three_quotes():
    pack = _pack()
    assert len(pack.quotes) == 3


def test_fixed_1yr_cheapest_for_resi():
    pack = _pack()
    rates = {q.tariff_type: q.unit_rate_p_kwh for q in pack.quotes}
    assert rates["fixed_1yr"] < rates["fixed_2yr"] < rates["variable_svt"]


def test_recommended_is_fixed_1yr():
    pack = _pack()
    rec = pack.recommended
    assert rec is not None
    assert rec.tariff_type == "fixed_1yr"


def test_cheapest_is_fixed_1yr():
    pack = _pack()
    assert pack.cheapest.tariff_type == "fixed_1yr"


def test_unit_rate_includes_spot_and_margin():
    pack = _pack(spot=22.0)
    # fixed_1yr rate = spot + margin (2.5 for RESI) + 0.0 premium
    fixed = next(q for q in pack.quotes if q.tariff_type == "fixed_1yr")
    assert abs(fixed.unit_rate_p_kwh - 24.5) < 0.01


def test_annual_cost_positive():
    pack = _pack()
    for q in pack.quotes:
        assert q.annual_est_cost_gbp > 0


def test_ic_segment_lower_margin():
    pack_resi = _pack(segment="RESI", spot=22.0)
    pack_ic = _pack(segment="IC", spot=22.0)
    resi_rate = next(q.unit_rate_p_kwh for q in pack_resi.quotes if q.tariff_type == "fixed_1yr")
    ic_rate = next(q.unit_rate_p_kwh for q in pack_ic.quotes if q.tariff_type == "fixed_1yr")
    assert ic_rate < resi_rate  # I&C has 1.8p margin vs 2.5p


def test_term_label():
    pack = _pack()
    for q in pack.quotes:
        assert q.term_label != q.tariff_type  # label is human-readable


def test_pack_metadata():
    pack = _pack()
    assert pack.days_to_expiry == 42
    assert pack.spot_price_p_kwh == 22.0
    assert pack.expiry_date == "2024-06-30"


# --- Phase KU depth tests ---

def test_customer_id_in_pack():
    pack = _pack()
    assert pack.customer_id == 'C1'


def test_expiry_date_stored():
    pack = _pack()
    assert pack.expiry_date == '2024-06-30'


def test_days_to_expiry_stored():
    pack = _pack()
    assert pack.days_to_expiry == 42


def test_spot_price_stored():
    pack = _pack()
    assert pack.spot_price_p_kwh == pytest.approx(22.0)


def test_each_quote_has_customer_id():
    pack = _pack()
    for q in pack.quotes:
        assert q.customer_id == 'C1'


def test_each_quote_tariff_type_non_empty():
    pack = _pack()
    for q in pack.quotes:
        assert len(q.tariff_type) > 0


def test_unit_rate_positive_all_quotes():
    pack = _pack()
    for q in pack.quotes:
        assert q.unit_rate_p_kwh > 0.0


def test_standing_charge_positive_all_quotes():
    pack = _pack()
    for q in pack.quotes:
        assert q.standing_charge_p_day > 0.0


def test_recommended_flag_on_one_quote():
    pack = _pack()
    recommended = [q for q in pack.quotes if q.recommended]
    assert len(recommended) == 1


def test_sme_segment_higher_than_ic():
    pack_sme = _pack(segment='SME', spot=22.0)
    pack_ic = _pack(segment='IC', spot=22.0)
    sme_rate = next(q.unit_rate_p_kwh for q in pack_sme.quotes if q.tariff_type == 'fixed_1yr')
    ic_rate = next(q.unit_rate_p_kwh for q in pack_ic.quotes if q.tariff_type == 'fixed_1yr')
    assert sme_rate > ic_rate
