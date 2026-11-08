# ARCHIVED LEGS of tests/company/risk/test_independent_amount.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/risk/test_independent_amount.py.
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





# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE TRIGGER, and the sourced quantities behind it
# ═══════════════════════════════════════════════════════════════════════════════════════════

class TestFreeEquity:



    def test_the_mcr_figure_agrees_with_every_other_copy(self):
        """R10: the same published number is spelled in four modules. If they ever disagree, one
        of them is wrong and no reader could tell which."""
        from company.finance.treasury import MCR_PER_ACCOUNT
        from saas.capital.solvency import MCR_FLOOR_GBP_PER_CUSTOMER
        from saas.growth_mandate import CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT

        assert (
            MCR_GBP_PER_ACCOUNT
            == MCR_PER_ACCOUNT
            == MCR_FLOOR_GBP_PER_CUSTOMER
            == CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT
        )








# ═══════════════════════════════════════════════════════════════════════════════════════════
# IT IS WIRED — the defect this whole roadmap exists to close
# ═══════════════════════════════════════════════════════════════════════════════════════════

