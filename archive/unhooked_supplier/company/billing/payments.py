"""C3 — Payment processing, reconciliation, and debt aging.

Links payment_received_event records from the ledger to invoice records.
Reconciles payments to invoices by customer_id + billing_period_end.
Ages outstanding debt; flags overdue invoices as bad_debt after 90 days.
"""

from datetime import date, timedelta
from pathlib import Path

from company.billing.invoice import _conn, create_schema, update_payment_status

BAD_DEBT_DAYS = 90


def reconcile_payment(
    payment_event: dict,
    db_path: Path,
) -> str:
    """Apply one payment event to the matching invoice.

    Returns the new payment_status ('paid', 'partially_paid', 'no_match').
    """
    cid = payment_event.get('customer_id', '')
    period_end = payment_event.get('bill_period_end', '')
    amount = payment_event.get('amount_gbp', 0.0)

    create_schema(db_path)
    with _conn(db_path) as conn:
        row = conn.execute(
            'SELECT invoice_number, total_gbp, payment_status FROM invoices '
            'WHERE account_id = ? AND billing_period_end = ? '
            'ORDER BY invoice_number LIMIT 1',
            (cid, period_end),
        ).fetchone()
        if row is None:
            return 'no_match'
        inv_num = row['invoice_number']
        total = row['total_gbp']
        current_status = row['payment_status']
        if current_status in ('paid', 'bad_debt'):
            return current_status
        new_status = 'paid' if amount >= total * 0.999 else 'partially_paid'
        conn.execute(
            'UPDATE invoices SET payment_status = ? WHERE invoice_number = ?',
            (new_status, inv_num),
        )
        return new_status


def reconcile_payments(
    payment_events: list,
    db_path: Path,
) -> dict:
    """Reconcile all payment events against the invoice DB.

    Returns {paid: int, partially_paid: int, no_match: int}.
    """
    counts = {'paid': 0, 'partially_paid': 0, 'no_match': 0}
    for event in payment_events:
        if event.get('event_type') != 'payment_received_event':
            continue
        result = reconcile_payment(event, db_path)
        if result in counts:
            counts[result] += 1
    return counts


def age_debt(
    db_path: Path,
    as_of_date: str,
) -> list:
    """Flag invoices unpaid past BAD_DEBT_DAYS as bad_debt.

    Returns list of {invoice_number, account_id, days_outstanding, new_status}.
    """
    as_of = date.fromisoformat(as_of_date)
    updated = []
    create_schema(db_path)
    with _conn(db_path) as conn:
        rows = conn.execute(
            "SELECT invoice_number, account_id, due_date, payment_status "
            "FROM invoices WHERE payment_status IN ('unpaid', 'partially_paid')"
        ).fetchall()
        for row in rows:
            try:
                due = date.fromisoformat(row['due_date'])
            except (ValueError, TypeError):
                continue
            days = (as_of - due).days
            new_status = row['payment_status']
            if days > BAD_DEBT_DAYS:
                new_status = 'bad_debt'
                conn.execute(
                    'UPDATE invoices SET payment_status = ? WHERE invoice_number = ?',
                    ('bad_debt', row['invoice_number']),
                )
            updated.append({
                'invoice_number': row['invoice_number'],
                'account_id': row['account_id'],
                'days_outstanding': days,
                'new_status': new_status,
            })
    return updated


def debt_aging_summary(
    db_path: Path,
    as_of_date: str,
) -> dict:
    """Return aging buckets for outstanding (unpaid + partially_paid) invoices.

    Buckets: current (0-30d), late (31-60d), overdue (61-90d), bad_debt (90+d or status=bad_debt).
    Returns {bucket: {count, amount_gbp}} for each bucket.
    """
    as_of = date.fromisoformat(as_of_date)
    buckets = {
        'current': {'count': 0, 'amount_gbp': 0.0},
        'late': {'count': 0, 'amount_gbp': 0.0},
        'overdue': {'count': 0, 'amount_gbp': 0.0},
        'bad_debt': {'count': 0, 'amount_gbp': 0.0},
    }
    create_schema(db_path)
    with _conn(db_path) as conn:
        rows = conn.execute(
            "SELECT invoice_number, due_date, total_gbp, payment_status "
            "FROM invoices WHERE payment_status != 'paid'"
        ).fetchall()
        for row in rows:
            if row['payment_status'] == 'bad_debt':
                buckets['bad_debt']['count'] += 1
                buckets['bad_debt']['amount_gbp'] += row['total_gbp']
                continue
            try:
                due = date.fromisoformat(row['due_date'])
            except (ValueError, TypeError):
                continue
            days = (as_of - due).days
            if days > BAD_DEBT_DAYS:
                bucket = 'bad_debt'
            elif days > 60:
                bucket = 'overdue'
            elif days > 30:
                bucket = 'late'
            else:
                bucket = 'current'
            buckets[bucket]['count'] += 1
            buckets[bucket]['amount_gbp'] += row['total_gbp']
    for b in buckets.values():
        b['amount_gbp'] = round(b['amount_gbp'], 2)
    return buckets
