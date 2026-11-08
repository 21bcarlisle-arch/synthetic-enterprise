"""EAC (Estimated Annual Consumption) calibration from actual billing history.

Real UK energy suppliers recalibrate EAC annually from meter reads.
This module computes calibrated annual kWh from the invoice DB so that
forward pricing and tariff comparison use actual rather than acquisition EAC.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from company.billing.invoice import _conn, create_schema, DEFAULT_DB_PATH


def calibrate_eac(
    account_id: str,
    db_path: Path = DEFAULT_DB_PATH,
    lookback_years: int = 2,
) -> float | None:
    """Return calibrated annual consumption (kWh) from billing history.

    Sums consumption_kwh from invoices within the lookback window and
    annualises based on total days covered. Returns None if no invoices found.
    """
    create_schema(db_path)
    with _conn(db_path) as conn:
        rows = conn.execute(
            "SELECT billing_period_start, billing_period_end, consumption_kwh, commodity "
            "FROM invoices WHERE account_id = ? ORDER BY billing_period_start",
            (account_id,),
        ).fetchall()

    if not rows:
        return None

    last_end = max(date.fromisoformat(r["billing_period_end"]) for r in rows)
    cutoff = date(last_end.year - lookback_years, last_end.month, last_end.day)

    window = [r for r in rows if date.fromisoformat(r["billing_period_end"]) >= cutoff]
    if not window:
        window = rows  # fall back to full history

    total_kwh = sum(r["consumption_kwh"] or 0.0 for r in window)
    start = date.fromisoformat(window[0]["billing_period_start"])
    end = date.fromisoformat(window[-1]["billing_period_end"])
    days = (end - start).days

    if days <= 0:
        return None

    return round(total_kwh / days * 365.25, 1)


def calibrate_all_customers(
    customer_ids: list[str],
    db_path: Path = DEFAULT_DB_PATH,
    lookback_years: int = 2,
) -> dict[str, float | None]:
    """Calibrate EAC for each customer. Returns {account_id: calibrated_eac_kwh}."""
    return {
        cid: calibrate_eac(cid, db_path, lookback_years)
        for cid in customer_ids
    }


def eac_drift(original_eac: float, calibrated_eac: float) -> dict:
    """Compute drift between original and calibrated EAC.

    Returns {original, calibrated, drift_pct, direction: "up"|"down"|"flat"}.
    """
    if original_eac <= 0:
        return {"original": original_eac, "calibrated": calibrated_eac,
                "drift_pct": 0.0, "direction": "flat"}
    drift_pct = (calibrated_eac - original_eac) / original_eac * 100
    direction = "up" if drift_pct > 0.5 else ("down" if drift_pct < -0.5 else "flat")
    return {
        "original": round(original_eac, 1),
        "calibrated": round(calibrated_eac, 1),
        "drift_pct": round(drift_pct, 1),
        "direction": direction,
    }
