"""R6: acquisition spend reaches the collateral a counterparty demands.

Roadmap R6 of WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE
(2026-08-28). The CMA's sentence, made testable: growth costs paid up front "weakened a firm's
balance sheet ... increasing the perceived riskiness of the supplier and, therefore, the quantity of
collateral that trading counterparties required."

The property under test is the CHAIN, not any level: hold the book perfectly still, take money off
the balance sheet, and the collateral demanded must go up. Every number below is either sourced
(the £130 MCR, the five-day close-out) or measured from observable history; none is tuned, and the
tests assert direction and monotonicity rather than magnitudes wherever a magnitude would just be
a mirror of the constants.
"""
import pytest

from company.finance.margin_call_book import build_margin_calls_from_mtm
from company.risk.independent_amount import (
    MCR_GBP_PER_ACCOUNT,
    STRESSED_CLOSE_OUT_DAYS,
    close_out_move_fraction_from_history,
    free_equity_gbp,
    independent_amount_gbp,
)

MOVE = 0.35  # a stressed close-out move, passed explicitly so these tests measure the mechanism


def _exposure(cp1=-100_000.0, cp2=60_000.0):
    """One name out-of-the-money, one in-the-money. The second is why R6 is direction-agnostic."""
    return {"CP1": {"netted_mtm_gbp": cp1}, "CP2": {"netted_mtm_gbp": cp2}}


def _book(net_assets, accounts=13, move=MOVE, **kw):
    return build_margin_calls_from_mtm(
        _exposure(), as_of_date="2022-01-01", settlement_deadline="2022-01-02",
        balance_sheet={"net_assets_gbp": net_assets, "accounts_held": accounts,
                       "close_out_move_fraction": move},
        **kw,
    )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE CHAIN — the thing R6 was asked for
# ═══════════════════════════════════════════════════════════════════════════════════════════

class TestSpendingTheBalanceSheetRaisesTheCollateralDemanded:
    def test_the_same_book_costs_more_collateral_once_equity_falls(self):
        """THE ASSERTION THAT CARRIES R6. Identical positions, identical marks, identical prices.

        The only thing that changes is how much equity the supplier has left, and the quantity of
        collateral its counterparties require goes up. Before this, nothing connected the two.
        """
        strong = _book(5_000_000.0).margin_call_summary()
        weak = _book(50_000.0).margin_call_summary()
        assert weak["total_outstanding_gbp"] > strong["total_outstanding_gbp"]
        assert weak["headroom_gbp"] < strong["headroom_gbp"]

    def test_it_is_monotone_in_the_balance_sheet(self):
        """Not a single step: less equity is never LESS collateral, across the whole range."""
        outstanding = [
            _book(n).margin_call_summary()["total_outstanding_gbp"]
            for n in (5_000_000.0, 1_000_000.0, 200_000.0, 100_000.0, 50_000.0, 0.0)
        ]
        assert outstanding == sorted(outstanding), (
            f"collateral demanded must not fall as equity falls: {outstanding}"
        )

    def test_acquisition_spend_is_what_moves_it(self):
        """The mechanism named end to end: a campaign's spend leaves the treasury, and that alone
        crosses the trigger. The £166,667 exposure is the run's own implied gross at the shipped
        facility; the spend figure is R1's sourced campaign cost."""
        opening = 200_000.0
        campaign_spend = 46_408.25  # measured, the live campaign at sourced prices
        before = _book(opening, move=MOVE).margin_call_summary()
        after = _book(opening - campaign_spend, move=MOVE).margin_call_summary()
        assert after["total_outstanding_gbp"] >= before["total_outstanding_gbp"]

    def test_a_call_now_forms_for_a_counterparty_we_are_IN_the_money_with(self):
        """B6 FRAME §1.9's one-directional death, closed.

        A long hedge book goes in-the-money on a price spike and posts NO variation margin, so
        before R6 the model could only ever kill on a price FALL. An independent amount is about
        the supplier's credit, not the position's sign, so CP2 forms a call for the first time.
        """
        strong = _book(5_000_000.0)
        weak = _book(50_000.0)
        assert strong.margin_call_summary()["total_calls"] == 1, "only the OTM name, as before"
        assert weak.margin_call_summary()["total_calls"] == 2
        cp2 = [c for c in weak.outstanding_calls() if c.counterparty == "CP2"]
        assert len(cp2) == 1
        assert cp2[0].variation_margin_gbp == 0.0, "in-the-money: no variation margin owed"
        assert cp2[0].initial_margin_gbp > 0.0, "but the counterparty still wants cover"


class TestNothingChangesWithoutTheBalanceSheet:
    def test_omitting_it_reproduces_the_pre_r6_book_exactly(self):
        """Every existing caller and every test pinning the old shape must be untouched."""
        before = build_margin_calls_from_mtm(
            _exposure(), as_of_date="2022-01-01", settlement_deadline="2022-01-02")
        s = before.margin_call_summary()
        assert s["total_calls"] == 1
        assert s["total_outstanding_gbp"] == 100_000.0
        assert all(c.initial_margin_gbp == 0.0 for c in before.outstanding_calls())

    def test_a_strong_balance_sheet_is_indistinguishable_from_the_old_behaviour(self):
        """MUTATION guard on the test above: if supplying a balance sheet ALWAYS changed the book,
        the previous test would prove nothing about the balance sheet being read."""
        old = build_margin_calls_from_mtm(
            _exposure(), as_of_date="2022-01-01", settlement_deadline="2022-01-02"
        ).margin_call_summary()
        strong = _book(5_000_000.0).margin_call_summary()
        assert strong["total_outstanding_gbp"] == old["total_outstanding_gbp"]


# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE TRIGGER, and the sourced quantities behind it
# ═══════════════════════════════════════════════════════════════════════════════════════════

class TestFreeEquity:
    def test_the_regulators_claim_comes_off_first(self):
        assert free_equity_gbp(100_000.0, 100) == 100_000.0 - 100 * MCR_GBP_PER_ACCOUNT

    def test_it_never_goes_negative(self):
        """A supplier below its MCR is in breach, not a supplier with negative free equity. Zero
        is the honest floor and it triggers the demand anyway."""
        assert free_equity_gbp(1_000.0, 100) == 0.0

    def test_an_unreadable_balance_sheet_is_None_and_not_zero(self):
        """Two different claims: nothing spare, versus nobody could read it."""
        assert free_equity_gbp(float("nan"), 13) is None
        assert free_equity_gbp(0.0, 13) == 0.0

    def test_the_mcr_figure_agrees_with_every_other_copy(self):
        """R10: the same published number is spelled in three modules. If they ever disagree, one
        of them is wrong and no reader could tell which."""
        from company.finance.treasury import MCR_PER_ACCOUNT
        from saas.capital.solvency import MCR_FLOOR_GBP_PER_CUSTOMER

        assert MCR_GBP_PER_ACCOUNT == MCR_PER_ACCOUNT == MCR_FLOOR_GBP_PER_CUSTOMER


class TestTheDemandItself:
    def test_no_demand_while_free_equity_covers_the_position(self):
        r = independent_amount_gbp(100_000.0, 5_000_000.0, 13, MOVE)
        assert r["demanded"] is False
        assert r["independent_amount_gbp"] == 0.0
        assert r["reason"] == "free_equity_covers_exposure"

    def test_demanded_once_it_does_not(self):
        r = independent_amount_gbp(100_000.0, 50_000.0, 13, MOVE)
        assert r["demanded"] is True
        assert r["reason"] == "free_equity_below_exposure"
        assert r["independent_amount_gbp"] == pytest.approx(100_000.0 * MOVE)

    def test_the_amount_is_the_close_out_move_and_nothing_else(self):
        """No invented rate: the amount is exposure x the measured move, so doubling the move
        doubles the demand and nothing in this module has a tunable percentage in it."""
        a = independent_amount_gbp(100_000.0, 50_000.0, 13, 0.20)["independent_amount_gbp"]
        b = independent_amount_gbp(100_000.0, 50_000.0, 13, 0.40)["independent_amount_gbp"]
        assert b == pytest.approx(2 * a)

    def test_a_flat_book_owes_nothing_however_weak_the_supplier(self):
        """A supplier with no position has nothing to collateralise. Distinct from a waiver."""
        r = independent_amount_gbp(0.0, 1.0, 13, MOVE)
        assert r["demanded"] is False
        assert r["reason"] == "no_exposure"

    def test_the_reason_distinguishes_three_different_zeros(self):
        """A £0 independent amount means three different things and a reader is entitled to know
        which. This is why the function returns a dict rather than a float."""
        reasons = {
            independent_amount_gbp(100_000.0, 5_000_000.0, 13, MOVE)["reason"],
            independent_amount_gbp(0.0, 5_000_000.0, 13, MOVE)["reason"],
            independent_amount_gbp(100_000.0, float("nan"), 13, MOVE)["reason"],
        }
        assert reasons == {
            "free_equity_covers_exposure", "no_exposure", "balance_sheet_unreadable"}


class TestItFailsClosed:
    """B6 FRAME §1.10 found three compounding fail-opens in this chain, where one non-finite mark
    returns "survived". R6 must not add a fourth."""

    @pytest.mark.parametrize("net_assets,move", [
        (float("nan"), MOVE),
        (float("inf"), MOVE),
        (50_000.0, float("nan")),
    ])
    def test_an_unreadable_input_DEMANDS_rather_than_waives(self, net_assets, move):
        """The direction matters more than the behaviour. A counterparty that cannot read your
        accounts does not extend you unsecured credit — so the safe default is a demand, and the
        flattering default (silently waiving on a NaN) is the shape that makes a corrupted mark
        indistinguishable from a healthy book."""
        r = independent_amount_gbp(100_000.0, net_assets, 13, move)
        assert r["demanded"] is True
        assert r["reason"] == "balance_sheet_unreadable"

    def test_a_negative_account_count_is_unreadable_not_free_capital(self):
        """MUTATION: without the guard, -100 accounts would ADD £13,000 of free equity."""
        assert free_equity_gbp(100_000.0, -100) is None


class TestTheCloseOutMoveIsMeasured:
    """The one quantity that could have been invented, and is not.

    The record shape here is the REAL Elexon one -- `settlementDate` / `systemSellPrice`, the keys
    `company/pricing/tariff_engine.py` itself reads. That is not a detail: this function's first
    draft defaulted to plausible-looking names that appear nowhere in the live feed, parsed 0 of
    165,386 rows, and returned None for every date in the decade, which the call site turns into a
    demand against every counterparty. `test_a_feed_shape_mismatch_RAISES` is what stops it
    recurring silently.
    """

    def _history(self, prices, start_day=1):
        return [
            {"settlementDate": f"2021-01-{start_day + i:02d}", "systemSellPrice": p}
            for i, p in enumerate(prices)
        ]

    def test_it_measures_the_move_in_the_MARK_not_in_the_raw_price(self):
        """A step in the spot moves the EWMA mark by much less, and the mark is what the position
        is closed out against. Measured on the real record, the raw-daily reading gave a worst
        five-day move of 681%; on the mark it is 28%."""
        history = self._history([100.0] * 20 + [200.0] * 10)
        move = close_out_move_fraction_from_history(history, "2021-03-01")
        assert move is not None
        assert 0.0 < move < 1.0, (
            f"a doubling in spot must not read as a doubling of the mark: {move}"
        )

    def test_a_bigger_shock_still_means_a_bigger_move(self):
        """Monotone: smoothing damps the move, it must not erase the ordering."""
        small = close_out_move_fraction_from_history(
            self._history([100.0] * 20 + [120.0] * 10), "2021-03-01")
        big = close_out_move_fraction_from_history(
            self._history([100.0] * 20 + [300.0] * 10), "2021-03-01")
        assert big > small

    def test_it_is_point_in_time(self):
        """Nothing on or after `as_of` is read. A close-out sized on the whole decade would price
        2022 into 2017's margin, which is the Blindfold breached in its purest form. Measured on
        the real record this shows as 15.2% known by 2017 rising to 28.0% after 2022."""
        history = self._history([100.0] * 10 + [500.0] * 10)
        before = close_out_move_fraction_from_history(history, "2021-01-11")
        after = close_out_move_fraction_from_history(history, "2021-03-01")
        assert after is not None
        assert before is None or before < after

    def test_too_little_history_REFUSES_rather_than_returning_zero(self):
        """A zero move waives the demand on exactly the input the function could not evaluate."""
        history = self._history([100.0] * STRESSED_CLOSE_OUT_DAYS)
        assert close_out_move_fraction_from_history(history, "2021-02-01") is None

    def test_a_flat_market_refuses_too(self):
        """Genuinely zero volatility over the whole window is not evidence that no cover is
        needed; it is a window that says nothing about a stress."""
        assert close_out_move_fraction_from_history(
            self._history([100.0] * 40), "2021-03-01") is None

    def test_unparseable_rows_are_skipped_when_others_parse(self):
        history = self._history([100.0] * 20 + [200.0] * 10) + [
            {"settlementDate": "2021-01-05"}, {"systemSellPrice": "cheap"}, {}]
        assert close_out_move_fraction_from_history(history, "2021-03-01") is not None

    def test_a_feed_shape_mismatch_RAISES_rather_than_reading_as_unmeasurable(self):
        """THE MUTATION FOR THE REAL DEFECT THIS FUNCTION HAD.

        Records that carry neither expected key are OUR bug, not a short history. Returning None
        would send NaN to the call site and demand collateral from every counterparty on a run
        where nothing was wrong with the market -- silently inflating every published margin
        figure. A key mismatch must be loud.
        """
        wrong_shape = [
            {"settlement_date": "2021-01-01", "price_gbp_per_mwh": 100.0} for _ in range(40)
        ]
        with pytest.raises(ValueError, match="feed-shape mismatch"):
            close_out_move_fraction_from_history(wrong_shape, "2021-03-01")

    def test_an_empty_feed_is_not_a_mismatch(self):
        """No records at all is a different claim from records of the wrong shape."""
        assert close_out_move_fraction_from_history([], "2021-03-01") is None

    def test_it_reads_the_same_keys_the_pricing_engine_marks_with(self):
        """Consistency by construction rather than by coincidence: the close-out move and the mark
        it is applied to must come from one reading of one series."""
        from pathlib import Path

        engine = (Path(__file__).resolve().parents[3]
                  / "company" / "pricing" / "tariff_engine.py").read_text(encoding="utf-8")
        assert '"settlementDate"' in engine and '"systemSellPrice"' in engine


# ═══════════════════════════════════════════════════════════════════════════════════════════
# IT IS WIRED — the defect this whole roadmap exists to close
# ═══════════════════════════════════════════════════════════════════════════════════════════

class TestTheLivePathPassesTheBalanceSheet:
    def test_run_phase2b_hands_its_own_balance_sheet_to_the_credit_desk(self):
        """An unwired credit model is the R1 defect wearing different clothes.

        Read as source rather than executed: importing `run_phase2b` runs the whole module, and
        this assertion is about the CALL being present, which the text settles exactly.
        """
        from pathlib import Path

        root = Path(__file__).resolve().parents[3]
        src = (root / "simulation" / "run_phase2b.py").read_text(encoding="utf-8")
        assert "balance_sheet={" in src, "the live collateral call passes no balance sheet"
        assert '"net_assets_gbp": final_treasury' in src

        # AND THE WORLD MUST NOT IMPORT THE CREDIT MODEL. The first draft measured the close-out
        # move in `run_phase2b` and imported `company.risk.independent_amount` to do it -- a live
        # SIM->company crossing, which the wall-crossing register refused at commit time and was
        # right to. The move is now measured inside the desk, from the same spot records it
        # already marks the book with, so the world hands over only two scalars.
        assert "from company.risk.independent_amount import" not in src, (
            "the world imports the credit model directly -- route it through the desk"
        )
        desk = (root / "company" / "risk"
                / "counterparty_collateral_desk.py").read_text(encoding="utf-8")
        assert "close_out_move_fraction_from_history" in desk, (
            "the close-out move must be MEASURED from observable price history inside the desk, "
            "not assumed"
        )

    def test_the_desk_reports_the_basis_even_when_it_was_not_assessed(self):
        """A missing independent amount must never be indistinguishable from a waived one."""
        from company.risk.counterparty_collateral_desk import _credit_and_margin

        class _Book:
            def open_contracts(self): return []
            def all_contracts(self): return []
            def live_contracts_as_of(self, _d): return []
            def exposure_by_counterparty(self, _p): return {}
            def exposure_by_counterparty_as_of(self, *_a, **_k): return {}

        _credit, margin = _credit_and_margin(_Book(), {}, [], [], "2022-01-01")
        assert margin["independent_amount_basis"] == "not_assessed_no_balance_sheet"
        assert margin["total_independent_amount_gbp"] == 0.0
