"""Phase 4b applied to the full Phase 2b portfolio — end-to-end run.

Every Phase 4b sub-phase summary (4b-1 through 4b-5) flags the same Open
Question: the customer value layer was built and tested against small
hand-written fixtures, but applying it to the full 9.5-year Phase 2b
settlement output (`simulation/run_phase2b.py`) was deferred to avoid a
second multi-hour simulation run within those increments. This script is
that follow-up: it runs the full Phase 2b simulation once, then feeds its
`all_records` settlement output through every 4b module in order —
cost-to-serve (4b-1), churn (4b-2), CLV (4b-3, via enterprise_value), home
move win rate (4b-4), and enterprise value (4b-5) — to produce portfolio-
level customer-value figures for the real 6-account portfolio.

`PRICE_DIFFERENTIAL_PCT = 0.0` (price parity with the market average) is
used for the home-move win rate input — per 4b-4/4b-5's Open Questions,
this is an external scalar this layer doesn't derive itself; 0.0 is the
neutral baseline.

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

from saas.churn_model import build_churn_risk
from saas.cost_to_serve import build_cost_to_serve
from saas.customers import CUSTOMERS
from saas.enterprise_value import build_enterprise_value
from simulation.run_phase2b import main as run_phase2b

PRICE_DIFFERENTIAL_PCT = 0.0


def main():
    phase2b_result = run_phase2b()
    all_records = phase2b_result["all_records"]

    cost_to_serve = build_cost_to_serve(all_records, CUSTOMERS)
    churn_risk = build_churn_risk(all_records, CUSTOMERS)
    enterprise_value = build_enterprise_value(
        churn_risk, cost_to_serve, CUSTOMERS, PRICE_DIFFERENTIAL_PCT
    )

    print("\n" + "=" * 60)
    print("=== Phase 4b customer value layer (full portfolio) ===")
    print("=" * 60)

    print(f"\nCost to serve (portfolio):       £{cost_to_serve['portfolio']['cost_to_serve_gbp']:>12.2f}")
    print(f"Margin (pre cost-to-serve):       £{cost_to_serve['portfolio']['margin_gbp']:>12.2f}")
    print(f"Net margin (post cost-to-serve):  £{cost_to_serve['portfolio']['net_margin_gbp']:>12.2f}")

    print(f"\n{'Account':<8} {'Renewals':>9} {'Lifetime':>10} {'AvgNetMargin£':>14} {'CLV£':>12}")
    for account_id, entry in enterprise_value["by_customer"].items():
        print(
            f"{account_id:<8} {len(churn_risk[account_id]):>9} "
            f"{entry['expected_lifetime_periods']:>10.2f} "
            f"{entry['avg_annual_net_margin_gbp']:>14.2f} "
            f"{entry['clv_gbp']:>12.2f}"
        )

    print(f"\nAccounts included:    {enterprise_value['portfolio']['account_count']}")
    print(f"Enterprise value (sum of CLV): £{enterprise_value['portfolio']['enterprise_value_gbp']:>12.2f}")

    return {
        "phase2b": phase2b_result,
        "cost_to_serve": cost_to_serve,
        "churn_risk": churn_risk,
        "enterprise_value": enterprise_value,
    }


if __name__ == "__main__":
    main()
