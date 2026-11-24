"""A world hedge executes at the market's published forward where one exists (G15, 2026-11-23).

Defect this catches: a hedge booked at the world's spot-EWMA model, which sat 0.51x the dealable
price in summer 2022, or a quote read before Ofgem's week had closed (hedging on a price not yet
published), or an old row served after the series ended.
"""
import ast
from pathlib import Path

from sim.forward_curve import published_forward_quote

ROOT = Path(__file__).resolve().parents[2]


def test_the_quote_is_point_in_time_and_can_be_absent_on_both_sides():
    # Both legs can be taken: a price inside the series, None before it and after it.
    assert published_forward_quote("2021-02-07") is None          # week of 1 Feb not yet closed
    assert published_forward_quote("2021-02-08") == 53.08          # readable the Monday after
    assert published_forward_quote("2022-07-31") != 413.59         # week of 25 Jul still trading
    assert published_forward_quote("2022-08-01") == 413.59
    assert published_forward_quote("2026-07-06") is not None
    assert published_forward_quote("2026-07-13") is None           # series ended: no stale price
    gas = published_forward_quote("2022-08-01", "gas")
    assert gas is not None and 100 < gas < 200                     # p/therm converted to GBP/MWh


def test_the_run_books_its_hedges_at_the_published_quote():
    """Both fuels' hedge legs in the run read `published_forward_quote`; removing either reds this."""
    tree = ast.parse((ROOT / "simulation" / "run_phase2b.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "published_forward_quote"]
    fuels = {n.args[1].value for n in calls if len(n.args) > 1 and isinstance(n.args[1], ast.Constant)}
    assert fuels == {"electricity", "gas"}
    # The company's trading book is opened at the executed price, not the synthetic estimate.
    agreed = [k.value.id for n in ast.walk(tree) if isinstance(n, ast.Call)
              and getattr(n.func, "attr", None) == "open_term_hedge"
              for k in n.keywords if k.arg == "forward_price_gbp_per_mwh" and isinstance(k.value, ast.Name)]
    assert agreed == ["hedge_price"]
