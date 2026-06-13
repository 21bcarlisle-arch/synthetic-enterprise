"""Phase 4c applied to the full Phase 2b portfolio — end-to-end run.

Phase 4c-4 through 4c-6 (`saas/bill_generator.py`, `saas/payment_behaviour.py`,
`saas/contact_model.py`) were built and tested against small hand-written
settlement fixtures. This script is the follow-up flagged in
`docs/observability/PHASE_4c_SUMMARY.md`'s Open Questions: it runs the full
Phase 2b simulation once, groups its `all_records` settlement output into
monthly bills per customer (chronological, carrying `previous_bill_total_gbp`
for the bill-shock clarity penalty), then feeds those bills through 4c-5
(payment behaviour) and 4c-6 (contact/complaints) to produce portfolio-level
billing-experience figures for the real 10-account portfolio (6 electricity +
4 gas).

4c-2 (weather-driven demand shapes) and 4c-3 (weather->price sensitivity) are
NOT included here — both modify `simulation/settlement.py`'s inputs
(consumption shape, forward price) rather than consuming its output, so
wiring them in is a separate, larger re-run of `simulation/run_phase2b.py`
itself, not a downstream pass over its existing records. Flagged as a further
follow-up.

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

from saas.bill_generator import generate_bill
from saas.contact_model import build_contact_model
from saas.customers import CUSTOMERS, get_customer
from saas.payment_behaviour import build_payment_behaviour
from simulation.run_phase2b import main as run_phase2b


def _billing_month(settlement_date: str) -> str:
    """'YYYY-MM-DD' -> 'YYYY-MM'."""
    return settlement_date[:7]


def build_monthly_bills(all_records: list[dict]) -> list[dict]:
    """Group `all_records` (from `simulation.settlement.run_settlement`) into
    one bill per customer per calendar month, in chronological order, via
    `saas.bill_generator.generate_bill`.

    Each customer's bills carry `previous_bill_total_gbp` from their own
    prior month, enabling the bill-shock clarity penalty. `contract_type` is
    looked up per customer from `saas.customers.CUSTOMERS`.
    """
    by_customer_month: dict[str, dict[str, list[dict]]] = {}
    for record in all_records:
        customer_id = record["customer_id"]
        month = _billing_month(record["settlement_date"])
        by_customer_month.setdefault(customer_id, {}).setdefault(month, []).append(record)

    bills = []
    for customer_id, months in by_customer_month.items():
        contract_type = get_customer(customer_id)["contract_type"]
        previous_bill_total_gbp = None
        for month in sorted(months):
            bill = generate_bill(customer_id, months[month], contract_type, previous_bill_total_gbp)
            bills.append(bill)
            previous_bill_total_gbp = bill["total_amount_gbp"]

    return bills


def main():
    phase2b_result = run_phase2b()
    all_records = phase2b_result["all_records"]

    bills = build_monthly_bills(all_records)
    payment_behaviour = build_payment_behaviour(bills)
    contact_model = build_contact_model(bills)

    avg_clarity = sum(b["clarity_score"] for b in bills) / len(bills)
    shocked = [b for b in bills if b["bill_shock_pct"] is not None]
    avg_bill_shock = sum(b["bill_shock_pct"] for b in shocked) / len(shocked) if shocked else 0.0
    total_bad_debt = sum(
        record["bad_debt_provision_gbp"]
        for records in payment_behaviour.values()
        for record in records
    )

    print("\n" + "=" * 60)
    print("=== Phase 4c billing experience layer (full portfolio) ===")
    print("=" * 60)

    print(f"\nBills generated:                 {len(bills)}")
    print(f"Average clarity score:            {avg_clarity:>12.3f}")
    print(f"Average bill shock (where shown): {avg_bill_shock:>12.1%}")
    print(f"Total bad debt provision:        £{total_bad_debt:>12.2f}")
    print(f"Avg complaint probability:        {contact_model['portfolio']['avg_complaint_probability']:>12.3f}")
    print(f"Service quality score:            {contact_model['portfolio']['service_quality_score']:>12.3f}")

    print(f"\n{'Account':<8} {'Bills':>6} {'AvgClarity':>11} {'CreditRisk':>11} {'BadDebt£':>10}")
    for customer in CUSTOMERS:
        customer_id = customer["customer_id"]
        customer_bills = [b for b in bills if b["customer_id"] == customer_id]
        if not customer_bills:
            continue
        avg_customer_clarity = sum(b["clarity_score"] for b in customer_bills) / len(customer_bills)
        credit_risk = payment_behaviour[customer_id][0]["credit_risk"]
        bad_debt = sum(r["bad_debt_provision_gbp"] for r in payment_behaviour[customer_id])
        print(
            f"{customer_id:<8} {len(customer_bills):>6} {avg_customer_clarity:>11.3f} "
            f"{credit_risk:>11} {bad_debt:>10.2f}"
        )

    return {
        "phase2b": phase2b_result,
        "bills": bills,
        "payment_behaviour": payment_behaviour,
        "contact_model": contact_model,
    }


if __name__ == "__main__":
    main()
