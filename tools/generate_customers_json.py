import datetime
import json
import pathlib

PROJECT = pathlib.Path(__file__).resolve().parent.parent


def _base_id(cid: str) -> str:
    if cid.endswith("g") and len(cid) > 1:
        return cid[:-1]
    return cid


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = PROJECT / "docs" / "reports" / "run_output_latest.json"
    if out_path is None:
        out_path = PROJECT / "site" / "data" / "customers.json"

    data = json.loads(pathlib.Path(run_json_path).read_text())
    pcl = data.get("per_customer_lifetime", {})
    bills = data.get("bills", [])

    # ── TWO RATES, EACH NAMED FOR WHAT IT IS (2026-08-31) ───────────────────────────────────────
    # `avg_rate_gbp_per_mwh` used to be published here and it was the COMMODITY leg alone --
    # `average_unit_rate_gbp_per_mwh` is `commodity_amount / MWh` in `saas/bill_generator`, the
    # wholesale energy and nothing else. The name did not say so, and the field was read as the
    # price the customer pays. Measured over the whole book on the day this changed:
    #
    #     commodity leg   102.57 GBP/MWh     effective   156.42 GBP/MWh     1.53x understated
    #     per account: median ratio 1.59x, worst 4.17x
    #
    # It was not a hypothetical misreading. `tools/couple_value_based_pricing.compare` took this
    # field as `current_rate_gbp_per_mwh` -- "what this customer currently pays" -- and derived
    # `base_rate = current_rate - TARGET_MARGIN` from it, so the entire value-based pricing arm was
    # anchored on roughly two thirds of the real price.
    #
    # A bill legitimately HAS a commodity rate and an effective rate and both are worth publishing.
    # What was missing was anything saying which one a field is, so both are published, both named.
    #
    # CATCH-UP BILLS ARE EXCLUDED FROM THE EFFECTIVE RATE, AND THE COUNT IS PUBLISHED. A catch-up
    # bill reconciles earlier estimated reads: its MONEY spans up to thirteen periods while its
    # VOLUME spans one, so total/volume on such a row is not a rate at all. 959 of 11,167 bills
    # carry one, and **178 of them have a negative GBP/MWh** -- the sign is the only reason the
    # defect is ever visible. Excluding them costs no account (251 before, 251 after, so no
    # household silently loses its rate) and pulls the worst account from 720.24 to 437.41.
    #
    # The commodity rate keeps every bill: `commodity_amount_gbp` is for THIS period's volume on a
    # catch-up bill too -- the adjustment is a separate term. Different exclusions for different
    # legs is correct here and is exactly why each leg has to say what it counts.
    bill_agg = {}
    for bill in bills:
        cid = bill["customer_id"]
        kwh = bill.get("total_consumption_kwh", 0) or 0
        rate = bill.get("average_unit_rate_gbp_per_mwh", 0) or 0
        if cid not in bill_agg:
            bill_agg[cid] = {"total_kwh": 0.0, "bill_count": 0, "rate_x_kwh": 0.0,
                             "effective_kwh": 0.0, "effective_gbp": 0.0, "catchup_bills": 0}
        bill_agg[cid]["total_kwh"] += kwh
        bill_agg[cid]["bill_count"] += 1
        bill_agg[cid]["rate_x_kwh"] += rate * kwh
        if bill.get("catchup_applied"):
            bill_agg[cid]["catchup_bills"] += 1
        else:
            bill_agg[cid]["effective_kwh"] += kwh
            bill_agg[cid]["effective_gbp"] += bill.get("total_amount_gbp", 0) or 0

    groups = {}
    for cid, lifetime in pcl.items():
        base = _base_id(cid)
        if base not in groups:
            groups[base] = {}
        commodity = lifetime.get("commodity", "electricity")
        agg = bill_agg.get(cid, {})
        total_kwh = agg.get("total_kwh", 0.0)
        rate_x_kwh = agg.get("rate_x_kwh", 0.0)
        groups[base][commodity] = {
            "cid": cid,
            "commodity": commodity,
            "segment": lifetime.get("segment", "unknown"),
            "acquisition_date": lifetime.get("acquisition_date", ""),
            "revenue_gbp": round(lifetime.get("revenue_gbp", 0), 2),
            "gross_gbp": round(lifetime.get("gross_gbp", 0), 2),
            "capital_gbp": round(lifetime.get("capital_gbp", 0), 2),
            "net_gbp": round(lifetime.get("net_gbp", 0), 2),
            "cost_to_serve_gbp": round(lifetime.get("cost_to_serve_gbp", 0), 2),
            "total_kwh": round(total_kwh, 0),
            # THE WHOLESALE ENERGY LEG ONLY -- not what the household pays. See the note above.
            "avg_commodity_rate_gbp_per_mwh": round(
                rate_x_kwh / total_kwh if total_kwh > 0 else 0, 2),
            # WHAT THE HOUSEHOLD ACTUALLY PAID per MWh: every term of the bill over the volume
            # those same bills covered, catch-up bills excluded on both legs together.
            "avg_effective_rate_gbp_per_mwh": round(
                (agg.get("effective_gbp", 0.0) / (agg.get("effective_kwh", 0.0) / 1000))
                if agg.get("effective_kwh", 0.0) > 0 else 0, 2),
            # THE DECLARED DENOMINATOR. A rate published without saying what it left out is the
            # shape this whole change exists to stop; a reader can now see the exclusion is small
            # and can tell an account that has NO clean bills from one that happens to read zero.
            "effective_rate_bills_excluded": agg.get("catchup_bills", 0),
            "bill_count": agg.get("bill_count", 0),
        }

    customers = []
    for base_id in sorted(groups.keys()):
        legs = groups[base_id]
        first = next(iter(legs.values()))
        combined = {
            "revenue_gbp": round(sum(l["revenue_gbp"] for l in legs.values()), 2),
            "gross_gbp": round(sum(l["gross_gbp"] for l in legs.values()), 2),
            "capital_gbp": round(sum(l["capital_gbp"] for l in legs.values()), 2),
            "net_gbp": round(sum(l["net_gbp"] for l in legs.values()), 2),
            "cost_to_serve_gbp": round(sum(l["cost_to_serve_gbp"] for l in legs.values()), 2),
            "total_kwh": round(sum(l["total_kwh"] for l in legs.values()), 0),
        }
        customers.append({
            "customer_group": base_id,
            "segment": first["segment"],
            "acquisition_date": first["acquisition_date"],
            "fuels": sorted(legs.keys()),
            "legs": legs,
            "combined": combined,
        })

    result = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "customer_count": len(customers),
        "customers": customers,
    }

    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    generate()
