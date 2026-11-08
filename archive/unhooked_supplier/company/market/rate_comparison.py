"""Market rate comparison — compares forward market estimate vs customer invoice rate.

Uses published price feed (company/market/price_feed.py) as market source.
Derives customer contracted rate from most recent invoice (p/kWh).
"""

from __future__ import annotations
from pathlib import Path
import sqlite3
from contextlib import contextmanager

from company.market.price_feed import PriceFeed, DEFAULT_FEED_PATH
from company.billing.invoice import DEFAULT_DB_PATH, create_schema


@contextmanager
def _conn(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _effective_rate_p_per_kwh(account_id: str, db_path: Path) -> float | None:
    """Derive effective unit rate from most recent invoice with consumption."""
    create_schema(db_path)
    with _conn(db_path) as conn:
        row = conn.execute(
            """SELECT total_gbp, consumption_kwh FROM invoices
               WHERE account_id=? AND consumption_kwh > 0
               ORDER BY billing_period_end DESC LIMIT 1""",
            (account_id,),
        ).fetchone()
    if row is None or row["consumption_kwh"] <= 0:
        return None
    return round(row["total_gbp"] / row["consumption_kwh"] * 100.0, 2)


def market_rate_comparison(
    account_id: str,
    db_path: Path = DEFAULT_DB_PATH,
    feed_path: Path = DEFAULT_FEED_PATH,
) -> dict | None:
    """Compare forward market rate vs customer effective contracted rate.

    Returns None if either rate cannot be determined.
    market_p: forward estimate in p/kWh (£/MWh * 10)
    contracted_p: effective rate from last invoice
    """
    feed = PriceFeed(feed_path)
    if not feed.is_available():
        return None
    fwd_mwh = feed.get_forward_price_estimate()
    if fwd_mwh is None:
        return None
    market_p = round(fwd_mwh / 10.0, 2)  # £/MWh -> p/kWh
    contracted_p = _effective_rate_p_per_kwh(account_id, db_path)
    if contracted_p is None:
        return {"market_p": market_p, "contracted_p": None, "delta_p": None,
                "protected": None, "message": "No invoice data to compare"}
    delta = round(market_p - contracted_p, 2)
    protected = contracted_p < market_p
    if abs(delta) < 0.5:
        msg = "Your rate is in line with the current market."
    elif protected:
        msg = f"Your fixed contract is {abs(delta):.1f}p/kWh below the market — you are protected."
    else:
        msg = f"Market rate is {abs(delta):.1f}p/kWh below your contracted rate."
    return {
        "market_p": market_p,
        "contracted_p": contracted_p,
        "delta_p": delta,
        "protected": protected,
        "message": msg,
    }
