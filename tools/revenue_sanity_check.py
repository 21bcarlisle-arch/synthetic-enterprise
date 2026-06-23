"""
Revenue and margin sanity check — runs after every full sim.

Usage:
    python3 -m tools.revenue_sanity_check [path/to/run_output.json]

If no path given, uses docs/reports/run_output_latest.json (symlink).

Exit codes:
    0  — all checks pass (within thresholds)
    1  — one or more anomalies flagged

Output: markdown-formatted report for NTFY / annual report appendage.
"""
import json
import sys
from pathlib import Path

# Industry benchmarks: (min_net_pct, max_net_pct, label)
SEGMENT_BENCHMARKS = {
    "resi/elec":  (-2.0, 8.0,  "Ofgem CMA 2-5%"),
    "resi/gas":   (-2.0, 6.0,  "Ofgem CMA 2-4%"),
    "SME/elec":   (-5.0, 12.0, "CMA 3-8%"),
    "I&C/elec":   (-20.0, 15.0, "large spread -20% to +15% (crisis)"),
    "I&C/gas":    (-10.0, 10.0, "commodity 2-6%, pass-through ≈0"),
}

CUSTOMER_MAX_NET_PCT = 40.0    # flag individual customer net > 40%
CUSTOMER_MIN_NET_PCT = -80.0   # flag individual customer net < -80%


def _load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def run_check(data: dict) -> tuple[bool, str]:
    """Return (passed, markdown_report)."""
    from saas.customers import CUSTOMERS

    pcp = data.get("per_cid_pnl", {})
    run_commit = data.get("meta", {}).get("git_commit", "unknown") if "meta" in data else "?"

    # Build segment aggregates
    segs: dict[str, dict] = {}
    customer_rows: list[dict] = []
    for c in CUSTOMERS:
        cid = c["customer_id"]
        seg_key = f"{c.get('segment', 'resi')}/{c.get('commodity', 'electricity')[:4]}"
        pnl = pcp.get(cid, {})
        rev = pnl.get("revenue", 0.0)
        gross = pnl.get("gross", 0.0)
        net = pnl.get("net", 0.0)
        if seg_key not in segs:
            segs[seg_key] = {"rev": 0.0, "gross": 0.0, "net": 0.0}
        segs[seg_key]["rev"] += rev
        segs[seg_key]["gross"] += gross
        segs[seg_key]["net"] += net
        customer_rows.append({"cid": cid, "seg": seg_key, "rev": rev, "gross": gross, "net": net})

    lines: list[str] = ["## Revenue & Margin Sanity Check", ""]
    lines.append("### Portfolio P&L Waterfall")
    total_rev = data.get("total_revenue_gbp", 0.0)
    total_gross = data.get("total_gross_gbp", 0.0)
    total_net = data.get("total_net_gbp", 0.0)
    total_cap = data.get("total_capital_gbp", 0.0)
    policy_and_network = total_gross - total_net - total_cap
    wholesale = total_rev - total_gross
    lines += [
        f"| Line | £ | % Revenue |",
        f"|------|---|-----------|",
        f"| Supply Revenue (ex-VAT, ex-policy passthrough) | £{total_rev:,.0f} | 100.0% |",
        f"| Wholesale cost | -£{wholesale:,.0f} | {100*wholesale/total_rev:.1f}% |",
        f"| **Gross supply margin** | **£{total_gross:,.0f}** | **{100*total_gross/total_rev:.1f}%** |",
        f"| Policy + Network costs | -£{policy_and_network:,.0f} | {100*policy_and_network/total_rev:.1f}% |",
        f"| Capital cost | -£{total_cap:,.0f} | {100*total_cap/total_rev:.1f}% |",
        f"| **Net supply margin** | **£{total_net:,.0f}** | **{100*total_net/total_rev:.1f}%** |",
        "",
        "> *The ledger's `net_margin_gbp` (£{:,.0f}) is gross − capital only, not final net.*".format(
            data.get("_ledger_headline", {}).get("net_margin_gbp", 0)
        ),
        "",
    ]

    # Segment table
    lines.append("### Segment Net Margin vs Benchmark")
    lines += [
        "| Segment | Revenue | Gross% | Net% | Benchmark | Status |",
        "|---------|---------|--------|------|-----------|--------|",
    ]
    anomalies: list[str] = []
    for seg_key, totals in sorted(segs.items()):
        rev = totals["rev"]
        gross = totals["gross"]
        net = totals["net"]
        if rev <= 0:
            continue
        net_pct = 100.0 * net / rev
        gross_pct = 100.0 * gross / rev
        bench = SEGMENT_BENCHMARKS.get(seg_key, None)
        if bench:
            lo, hi, label = bench
            ok = lo <= net_pct <= hi
            status = "✓" if ok else "⚠ ANOMALY"
            if not ok:
                anomalies.append(f"{seg_key} net {net_pct:.1f}% (benchmark {label})")
        else:
            status = "—"
            label = "no benchmark"
        lines.append(
            f"| {seg_key} | £{rev:,.0f} | {gross_pct:.1f}% | {net_pct:.1f}% | {label} | {status} |"
        )
    lines.append("")

    # Per-customer table (flag outliers)
    lines.append("### Per-Customer Net Margin Flags")
    flagged_customers: list[str] = []
    for row in sorted(customer_rows, key=lambda r: r["net"] / r["rev"] if r["rev"] > 0 else 0, reverse=True):
        if row["rev"] <= 0:
            continue
        net_pct = 100.0 * row["net"] / row["rev"]
        if net_pct > CUSTOMER_MAX_NET_PCT or net_pct < CUSTOMER_MIN_NET_PCT:
            lines.append(f"- **{row['cid']}** ({row['seg']}): net {net_pct:.1f}% — rev £{row['rev']:,.0f}, net £{row['net']:,.0f}")
            flagged_customers.append(row["cid"])

    if not flagged_customers:
        lines.append("No individual customers outside ±{}/{} thresholds.".format(
            CUSTOMER_MAX_NET_PCT, abs(CUSTOMER_MIN_NET_PCT)
        ))
    lines.append("")

    # Summary
    passed = len(anomalies) == 0 and len(flagged_customers) == 0
    if passed:
        lines.append("**SANITY CHECK: PASS** — all segments within benchmarks.")
    else:
        lines.append("**SANITY CHECK: ANOMALIES DETECTED**")
        for a in anomalies:
            lines.append(f"- Segment {a}")
        for c in flagged_customers:
            lines.append(f"- Customer {c} outside net% bounds")

    return passed, "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/run_output_latest.json"
    data = _load(path)
    passed, report = run_check(data)
    print(report)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
