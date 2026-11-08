"""M1 -- Elexon settlement interface: receive and reconcile settlement statements.

The company receives half-hourly settlement statements from Elexon (BSC settlement).
Each statement records: period, volume settled (MWh), SSP/SBP price, net cost/credit.
The company reconciles these against its own billing records to detect imbalances.

Epistemic constraint: this module only sees what Elexon publishes (observable market
outcomes). It does not access simulation internals or forward curve parameters.
"""

from dataclasses import dataclass

IMBALANCE_FLAG_THRESHOLD_GBP = 10.0  # Flag imbalances above this value
IMBALANCE_REPORT_THRESHOLD_PCT = 5.0  # Flag when imbalance > 5% of settlement cost


@dataclass
class SettlementStatement:
    """A received Elexon BSC settlement statement for one half-hour period."""
    period: str               # ISO datetime of HH period start
    customer_id: str
    volume_kwh: float
    ssp_gbp_per_mwh: float    # System Sell Price (observable Elexon output)
    net_settlement_cost_gbp: float  # What we owe / are owed for this period
    hedge_pnl_gbp: float = 0.0     # Hedge gain/loss recorded against this period


def receive_settlement(
    period: str,
    customer_id: str,
    volume_kwh: float,
    ssp_gbp_per_mwh: float,
    net_settlement_cost_gbp: float,
    hedge_pnl_gbp: float = 0.0,
) -> SettlementStatement:
    """Create a SettlementStatement from Elexon data. Pure constructor."""
    return SettlementStatement(
        period=period,
        customer_id=customer_id,
        volume_kwh=volume_kwh,
        ssp_gbp_per_mwh=ssp_gbp_per_mwh,
        net_settlement_cost_gbp=net_settlement_cost_gbp,
        hedge_pnl_gbp=hedge_pnl_gbp,
    )


STATEMENT_INTEGRITY_TOLERANCE_PCT = 1.0   # volume x price vs stated cost
STATEMENT_INTEGRITY_TOLERANCE_GBP = 1.00  # absolute floor, for small periods


def _statement_integrity(statement: "SettlementStatement") -> tuple:
    """Check a statement against ITSELF: does volume x SSP tie to the stated cost?

    Returns (checked, consistent, implied_cost_gbp).

    `volume_kwh`, `ssp_gbp_per_mwh` and `hedge_pnl_gbp` were carried on every
    statement and read by NOTHING -- no function compared volume x price against
    `net_settlement_cost_gbp`. So the one input that makes a settlement statement
    PROVABLY wrong was invisible to the reconciliation that exists to catch it: a
    statement claiming 1,000 kWh at GBP 100/MWh while billing GBP 3 reconciled
    clean, and a period whose entire economics were a GBP 5,000 hedge loss looked
    identical to one with no hedge. Only a revenue gap could ever flag, which is
    a control that cannot fire on the corruption it is named for (R15).

    When the statement carries no internals (zero volume AND zero price -- the
    shape of a statement whose detail was never populated) there is nothing to
    tie out, so this returns checked=False rather than a passing verdict.
    """
    if statement.volume_kwh == 0 and statement.ssp_gbp_per_mwh == 0:
        return (False, None, None)
    implied = (statement.volume_kwh / 1000.0) * statement.ssp_gbp_per_mwh - statement.hedge_pnl_gbp
    gap = abs(implied - statement.net_settlement_cost_gbp)
    tolerance = max(
        STATEMENT_INTEGRITY_TOLERANCE_GBP,
        abs(implied) * STATEMENT_INTEGRITY_TOLERANCE_PCT / 100.0,
    )
    return (True, gap <= tolerance, implied)


def reconcile_against_bill(
    statement: SettlementStatement,
    billed_revenue_gbp: float,
    threshold_pct: float = IMBALANCE_REPORT_THRESHOLD_PCT,
) -> dict:
    """Reconcile a settlement statement against the company's billed revenue.

    Imbalance = billed_revenue - net_settlement_cost (positive = profitable).
    An imbalance beyond threshold_pct of settlement cost is flagged.
    """
    imbalance = billed_revenue_gbp - statement.net_settlement_cost_gbp
    pct = (abs(imbalance) / abs(statement.net_settlement_cost_gbp) * 100.0
           if abs(statement.net_settlement_cost_gbp) >= 0.01 else 0.0)
    checked, consistent, implied = _statement_integrity(statement)
    flagged = (pct > threshold_pct
               or abs(imbalance) > IMBALANCE_FLAG_THRESHOLD_GBP
               or consistent is False)
    return {
        "period": statement.period,
        "customer_id": statement.customer_id,
        "billed_revenue_gbp": round(billed_revenue_gbp, 2),
        "net_settlement_cost_gbp": round(statement.net_settlement_cost_gbp, 2),
        "imbalance_gbp": round(imbalance, 2),
        "imbalance_pct": round(pct, 1),
        "flagged": flagged,
        # Whether the statement was checked against ITSELF, and the result. An
        # unchecked statement reports checked=False / consistent=None rather than
        # a reassuring True: an unavailable check is not a passed check (R15).
        "statement_checked": checked,
        "statement_consistent": consistent,
        "implied_cost_gbp": None if implied is None else round(implied, 2),
    }


def reconcile_period_batch(
    statements: list[SettlementStatement],
    billed_revenues: dict[str, float],
    threshold_pct: float = IMBALANCE_REPORT_THRESHOLD_PCT,
) -> dict:
    """Batch reconciliation for a list of statements.

    billed_revenues: {customer_id: billed_revenue_gbp} for the period.
    Returns {results: list[dict], total_imbalance_gbp, flagged_count, checked}.
    """
    results = []
    total_imbalance = 0.0
    flagged = 0
    for stmt in statements:
        revenue = billed_revenues.get(stmt.customer_id, 0.0)
        rec = reconcile_against_bill(stmt, revenue, threshold_pct)
        results.append(rec)
        total_imbalance += rec["imbalance_gbp"]
        if rec["flagged"]:
            flagged += 1
    return {
        "results": results,
        "total_imbalance_gbp": round(total_imbalance, 2),
        "flagged_count": flagged,
        "checked": len(statements),
    }


def imbalance_summary(batch_result: dict) -> dict:
    """Summarise a batch reconciliation result for reporting."""
    results = batch_result.get("results", [])
    pos = [r["imbalance_gbp"] for r in results if r["imbalance_gbp"] > 0]
    neg = [r["imbalance_gbp"] for r in results if r["imbalance_gbp"] < 0]
    return {
        "total_imbalance_gbp": round(batch_result.get("total_imbalance_gbp", 0.0), 2),
        "favourable_count": len(pos),
        "unfavourable_count": len(neg),
        "flagged_count": batch_result.get("flagged_count", 0),
        "checked": batch_result.get("checked", 0),
        "net_position": "favourable" if batch_result.get("total_imbalance_gbp", 0) >= 0 else "unfavourable",
    }
