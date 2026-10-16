"""Writer 1 reads the unit-rate margin against what its own strike priced for, and the save takes
writer 1's floor (2026-10-14).

The defect each test names: the portfolio premium learned from a margin that counted the standing
charge as profit, against an 8% literal, so it took the full -5% off a book priced at cost
(`docs/staging/SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_AND_THE_PREMIUM_READS_THE_STANDING_CHARGE_AS_MARGIN_2026-10-14.md`);
and the save floored at forward + the two locked costs while writer 1 floored at that plus capital.
"""
import pytest

from company.pricing.renewal_desk import pre_margin_unit_rate
from company.pricing.renewal_rate_chain import PortfolioMarginBook, portfolio_position
from company.pricing.tariff_engine import PORTFOLIO_PREMIUM_MIN
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

# A 2024-25 electricity term at real inputs (the finding's row 433): 3.1 MWh at GBP 198.62/MWh,
# standing charge 57.11p/day.
MWH, RATE, SC = 3.1, 198.62, 57.11 * 365 / 100


def _book_after(unit_margin_per_mwh, *, sc=SC, mwh=MWH):
    book = PortfolioMarginBook()
    unit_revenue = RATE * mwh
    book.term_ended(billing_account="A", commodity="electricity", last_settled_day="2024-09-30",
                    net_margin=unit_margin_per_mwh * mwh + sc, revenue=unit_revenue + sc,
                    standing_charge_revenue=sc, volume_mwh=mwh, held_on_a_save=False,
                    tariff_type="fixed")
    book.as_of("2024-10-01")
    return book


def test_a_term_that_earned_what_its_strike_priced_for_moves_no_rate():
    # Defect: the standing charge read as margin put this term at 26% against 8%, and -5% followed.
    book = _book_after(TARGET_MARGIN_GBP_PER_MWH)
    pos = portfolio_position(book.rates("electricity"), book.priced_for("electricity"))
    assert pos["mean_recent_margin_rate"] == pytest.approx(pos["target_margin_rate"], abs=1e-4)
    assert pos["portfolio_premium_fraction"] == pytest.approx(0.0, abs=1e-6)
    # The control: the same term read on the old basis, against the literal, takes the full cut.
    bill_basis = (TARGET_MARGIN_GBP_PER_MWH * MWH + SC) / (RATE * MWH + SC)
    assert portfolio_position([bill_basis])["portfolio_premium_fraction"] == PORTFOLIO_PREMIUM_MIN


def test_the_standing_charge_moves_neither_the_reading_nor_the_premium():
    # Defect: a bigger standing charge read as a fatter margin, so a deeper discount.
    small, large = _book_after(-5.0, sc=50.0), _book_after(-5.0, sc=400.0)
    assert small.rates("electricity") == pytest.approx(large.rates("electricity"))
    assert small.priced_for("electricity") == pytest.approx(large.priced_for("electricity"))


def test_a_unit_rate_that_lost_money_is_surcharged_and_one_that_beat_its_price_is_cut():
    # The partition in one control, so a premium stuck at either sign fails: a loss raises the
    # next rate, an over-earning lowers it, and the priced-for margin is the line between them.
    lost = _book_after(-5.0)
    beat = _book_after(TARGET_MARGIN_GBP_PER_MWH + 10.0)
    p_lost = portfolio_position(lost.rates("electricity"), lost.priced_for("electricity"))
    p_beat = portfolio_position(beat.rates("electricity"), beat.priced_for("electricity"))
    assert p_lost["portfolio_premium_fraction"] > 0 > p_beat["portfolio_premium_fraction"]
    assert p_lost["target_margin_rate"] == pytest.approx(TARGET_MARGIN_GBP_PER_MWH / RATE, abs=1e-4)


def test_a_history_that_does_not_state_its_priced_for_rate_falls_back_to_the_literal_named():
    # The fallback branch is reachable and says so: no target is recorded where none was stated,
    # and a window with ANY unstated term is not averaged over the ones that state it.
    assert portfolio_position([0.02])["target_margin_rate"] is None
    assert portfolio_position([0.02, 0.02], [None, 0.01])["target_margin_rate"] is None
    assert portfolio_position([0.02, 0.02], [0.01, 0.01])["target_margin_rate"] == 0.01


@pytest.mark.parametrize("fuel, day, fwd, policy, network", [
    ("electricity", "2024-09-17", 66.89, 58.26, 69.00),
    ("gas", "2024-07-05", 27.66, 0.04, 14.30),
])
def test_the_save_and_the_renewal_cut_floor_where_writer_one_does(fuel, day, fwd, policy, network):
    # Defect: the save's floor was fwd + policy + network, GBP 2.2-4.5/MWh under writer 1's.
    from simulation.run_phase2b import _price_match_inputs

    inputs = _price_match_inputs({"locked_policy_cost_gbp_per_mwh": policy,
                                  "locked_network_cost_gbp_per_mwh": network}, fuel, day, fwd)
    assert inputs["cost_floor"] == pre_margin_unit_rate(fwd, day, policy, network)
    assert inputs["cost_floor"] > fwd + policy + network
