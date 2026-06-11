"""Phase 3a — Experience Observability Depth.

Runs the Phase 2b dual-fuel simulation to get a full set of settled
records, then scores each customer's per-billing-period experience
signals (bill shock, cumulative exposure, expectation gap) via
saas.customer_reaction.score_experience_signals, and reports:
  - which customers had the most bill-shock events in 2016
  - which customers had the most bill-shock events in 2021-2022
  - whether bill-shock frequency differs by location or home type

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

from collections import defaultdict

from saas.customer_reaction import score_experience_signals
from saas.customers import CUSTOMERS
from simulation.run_phase2b import main as run_phase2b


def _bill_shock_events(signals, year_prefixes):
    """Count bill_shock_triggered=True periods per customer whose
    billing_period starts with one of year_prefixes (e.g. "2016" or
    "2021"/"2022")."""
    counts = {}
    for customer_id, periods in signals.items():
        counts[customer_id] = sum(
            1 for p in periods
            if p["bill_shock_triggered"] and p["billing_period"][:4] in year_prefixes
        )
    return counts


def main():
    print("=== Phase 3a — Experience Observability Depth ===\n")
    print("--- Running Phase 2b simulation for settlement records ---\n")
    result = run_phase2b()
    all_records = result["all_records"]

    print("\n=== Scoring experience signals ===\n")
    signals = score_experience_signals(all_records)

    shocks_2016 = _bill_shock_events(signals, {"2016"})
    shocks_crisis = _bill_shock_events(signals, {"2021", "2022"})

    print(f"{'Customer':<8} {'Region':<12} {'Home type':<16} {'2016 shocks':>12} {'2021-22 shocks':>15}")
    for c in CUSTOMERS:
        cid = c["customer_id"]
        if cid not in signals:
            continue
        region = c["location"]["region"]
        home_type = c["home_type"]
        print(f"{cid:<8} {region:<12} {home_type:<16} {shocks_2016.get(cid, 0):>12} {shocks_crisis.get(cid, 0):>15}")

    print("\n=== By region ===")
    by_region_2016 = defaultdict(int)
    by_region_crisis = defaultdict(int)
    for c in CUSTOMERS:
        cid = c["customer_id"]
        if cid not in signals:
            continue
        region = c["location"]["region"]
        by_region_2016[region] += shocks_2016.get(cid, 0)
        by_region_crisis[region] += shocks_crisis.get(cid, 0)
    for region in sorted(by_region_2016):
        print(f"  {region:<12} 2016={by_region_2016[region]:>3}  2021-22={by_region_crisis[region]:>3}")

    print("\n=== By home type ===")
    by_home_2016 = defaultdict(int)
    by_home_crisis = defaultdict(int)
    for c in CUSTOMERS:
        cid = c["customer_id"]
        if cid not in signals:
            continue
        home_type = c["home_type"]
        by_home_2016[home_type] += shocks_2016.get(cid, 0)
        by_home_crisis[home_type] += shocks_crisis.get(cid, 0)
    for home_type in sorted(by_home_2016):
        print(f"  {home_type:<16} 2016={by_home_2016[home_type]:>3}  2021-22={by_home_crisis[home_type]:>3}")

    return {
        "signals": signals,
        "shocks_2016": shocks_2016,
        "shocks_crisis": shocks_crisis,
    }


if __name__ == "__main__":
    main()
