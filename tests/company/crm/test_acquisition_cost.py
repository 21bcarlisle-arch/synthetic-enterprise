"""Phase 123: Customer Acquisition Cost (CAC) model tests."""

from company.crm.acquisition_cost import get_cac, cac_summary, clv_vs_cac


def test_pcw_cac_2024():
    assert get_cac("pcw", 2024) == 50.0


def test_broker_highest_cac():
    broker = get_cac("broker", 2024)
    pcw = get_cac("pcw", 2024)
    assert broker > pcw


def test_referral_lowest_cac():
    referral = get_cac("referral", 2024)
    direct = get_cac("direct", 2024)
    assert referral < direct


def test_unknown_channel_returns_zero():
    assert get_cac("mystery_channel", 2024) == 0.0


def test_prior_year_clamped_to_2016():
    assert get_cac("pcw", 2010) == get_cac("pcw", 2016)


def test_future_year_clamped_to_2025():
    assert get_cac("direct", 2030) == get_cac("direct", 2025)


def test_cac_summary_has_all_channels():
    s = cac_summary(2024)
    for ch in ("pcw", "direct", "broker", "referral", "winback"):
        assert ch in s


def test_clv_vs_cac_healthy():
    result = clv_vs_cac(100.0, 5.0, "pcw", 2024)
    assert result["clv_gbp"] == 500.0
    assert result["status"] == "HEALTHY"


def test_clv_vs_cac_loss_making():
    result = clv_vs_cac(10.0, 1.0, "broker", 2024)
    assert result["status"] == "LOSS_MAKING"


def test_clv_cac_ratio_correct():
    result = clv_vs_cac(75.0, 4.0, "direct", 2024)
    expected_ratio = 300.0 / 30.0
    assert abs(result["clv_cac_ratio"] - expected_ratio) < 0.01
