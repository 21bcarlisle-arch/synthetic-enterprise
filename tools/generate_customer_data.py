#!/usr/bin/env python3
"""Generate per-customer site data with dual-fuel combined views and enriched metrics."""
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from company.crm.customer_registry import mpan_core, mprn, predecessors, supply_point_of
from saas.clv_model import DISCOUNT_RATE_ANNUAL

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_DIR = PROJECT / "site" / "data" / "customers"



def _retire_departed_artefacts(index):
    """Delete per-account artefacts for accounts no longer in the population.

    WORKER_FINDING_THE_PRINTED_FOOTING_CONTROL_RUNS_ON_A_SMALLER_POPULATION_THAN_THE_PAGE
    (2026-08-12): this generator wrote a file per account in the run and never removed
    the file of an account that LEFT. The successor accounts C1_2/C2_2/C5_2
    (saas/customers.py::SUCCESSOR_CUSTOMERS -- activated only when the predecessor
    churns and we win the home-mover competition) activated in earlier runs and not in
    this one, so their artefacts sat on the publish path unrefreshed for 33-35 days and
    stayed FETCHABLE on poesys.net, still carrying invoice amounts from the pre-RJ era
    when generate_invoice_data fabricated them by splitting lifetime revenue. That
    fabricator rounded components and total independently, so 30 of those invoices did
    not foot -- the entire observed footing-defect population, in the one place no
    control could see it.

    Fails CLOSED on an empty population: an empty `index` means the run produced no
    customers, which is a broken run, not an instruction to wipe the publish path.
    Only files this generator's own naming owns (`<account_id>.json`) are candidates,
    so `_index.json` and any hand-added artefact are never touched.
    """
    if not index:
        return []
    keep = set(index)
    retired = []
    for path in sorted(OUT_DIR.glob("*.json")):
        if path.name == "_index.json":
            continue
        if path.stem not in keep:
            path.unlink()
            retired.append(path.stem)
    return retired


def _digest_int(seed, n):
    """First n digits of a deterministic hash of seed -- a display identifier,
    not a claim about simulation internals (same status as account_id itself)."""
    h = hashlib.sha256(seed.encode()).hexdigest()
    return str(int(h, 16))[:n].zfill(n)


def _mpan(supply_point, segment, billed_profile_class=None):
    """MPAN bottom line, the 13-digit core (`customer_registry.mpan_core`, the one home the ledger
    reads too), plus a top line of profile class(2) + meter timeswitch(2) + line loss factor(3).
    Pass the supply point (`supply_point_of`), not the account. A domestic meter's class is the one
    its bills carry (`profile_classes_billed`); "01" only where no bill names one."""
    profile_class = "05" if segment == "I&C" else "%02d" % (billed_profile_class or 1)
    meter_timeswitch = "00"
    line_loss_factor = _digest_int(supply_point + "-llf", 3)
    return {
        "top_line": profile_class + meter_timeswitch + line_loss_factor,
        "bottom_line": mpan_core(supply_point),
    }


_mprn = mprn


def _tariff(segment, commodity):
    if segment == "I&C":
        return "Half-Hourly Industrial and Commercial"
    return "Standard Variable (" + commodity.capitalize() + ")"


def meter_types_billed(run):
    """account -> the meter type its LATEST read was taken on, from the run's own `meter_read_log`.

    This is the one home for the meter type a household page prints. The bills were cut on these
    reads, so a label from anywhere else can contradict the bills printed under it. That happened:
    the label used to come from `saas.customers` at page-build time. That book does not hold the
    smart flag the run stamped on a drawn household at acquisition. So on the 129e7de698 book,
    273 of 1,293 accounts were billed on smart reads and labelled "Traditional"
    (SEAT_FINDING_THE_THIRD_COLD_READ_FINDS_THE_METER_TYPE_PRINTED_FROM_TWO_RECORDS_THAT_DISAGREE).
    It is the latest read and not the commonest, because after a meter exchange the meter now on
    the wall is the one the next read comes from.
    """
    latest = {}
    for read in run.get("meter_read_log") or []:
        cid, when = read.get("customer_id"), str(read.get("period_end") or "")
        if cid and read.get("meter_type") and when >= latest.get(cid, ("",))[0]:
            latest[cid] = (when, read["meter_type"])
    return {cid: meter for cid, (_, meter) in latest.items()}


def profile_classes_billed(run):
    """account -> the profile class its LATEST bill carries, from the run's own `bills`.

    The cast's storage-heating slot reads `profile_class` from the page, and the page never wrote
    it, so the slot stood empty on "the record names no profile class 2 meter" while 31+ accounts on
    the cd4fc5b8d8 book were billed as PC2. The latest bill, for the reason `meter_types_billed` gives.
    """
    latest = {}
    for bill in run.get("bills") or []:
        cid, when = bill.get("customer_id"), str(bill.get("period_end") or "")
        if cid and bill.get("profile_class") is not None and when >= latest.get(cid, ("",))[0]:
            latest[cid] = (when, bill["profile_class"])
    return {cid: pc for cid, (_, pc) in latest.items()}


def _meter(segment, billed_meter_type):
    """Customer-facing meter type label, from `meter_types_billed` (its docstring says why there).

    None where the run took no read for the account: we cannot tell, and the page prints "—"
    rather than defaulting to "Traditional", which is the default that produced the finding.
    """
    if segment == "I&C":
        return "HH"
    return {"smart": "Smart", "traditional": "Traditional"}.get(billed_meter_type)


def _base_id(cid):
    """Strip gas suffix: C1g -> C1, C_IC3g -> C_IC3."""
    if cid.endswith("g") and len(cid) > 1:
        candidate = cid[:-1]
        if candidate:
            return candidate
    return cid


_EVENT_LABELS = {
    "renewed": "Tariff renewed",
    "churned": "Churned",
}


def _timeline(run, base):
    """Household-level timeline: real renewal/churn events (customer_events,
    electricity-metered) + real life events (per_customer_behavioral) that fall
    inside a supply window of either fuel, merged and sorted. No fabrication --
    both sources already exist in the run artifact; this just assembles them
    per household for display."""
    events = []
    ce = run.get("customer_events", [])
    for e in ce:
        if e.get("customer_id") not in (base, base + "g"):
            continue
        etype = e.get("event_type")
        label = _EVENT_LABELS.get(etype, etype)
        rate = e.get("unit_rate_gbp_per_mwh")
        detail = label
        if etype == "renewed" and rate is not None:
            detail = label + " at " + str(round(rate, 0)) + " £/MWh"
        events.append({
            "date": e.get("event_date"),
            "type": etype,
            "commodity": e.get("commodity"),
            "detail": detail,
        })
    events.extend(_life_events(run, base)[0])
    events.sort(key=lambda e: e.get("date") or "")
    return events


def _supply_windows(run, base):
    """The (first day, last day) we supplied each of the household's legs, from the supplier's own
    record: the leg's acquisition date, its first churn or move-out, and the last month it was
    billed. A leg never billed has no window."""
    pcl = run.get("per_customer_lifetime", {})
    exits = {}
    for e in run.get("customer_events", []):
        if e.get("event_type") == "churned" and e.get("event_date"):
            exits.setdefault(e.get("customer_id"), []).append(e["event_date"])
    for m in run.get("home_move_outs") or []:
        if m.get("move_date"):
            exits.setdefault(m.get("customer_id"), []).append(m["move_date"])
    windows = []
    for cid in (base, base + "g"):
        if cid not in pcl:
            continue
        billed = [mo for ydata in run.get("years", {}).values()
                  for mo in (ydata.get("per_customer_monthly", {}).get(cid) or {})]
        if not billed:
            continue
        end = min([max(billed) + "-31"] + exits.get(cid, []))
        windows.append((pcl[cid].get("acquisition_date") or min(billed) + "-01", end))
    return windows


def _life_events(run, base):
    """The world's life events for this household, split into those that fall while we supplied
    either fuel and those that do not. Only the first go on the supplier's timeline: a supplier
    has no way to know of a former customer's car, or of a baby born before the home joined it.
    The second are published apart, labelled as the world's.

    Those kept are the world's too: no route in the run tells the supplier of a birth, a job lost or
    a car bought, and it can only see their effect on the meter, later. Each carries `seen_by`, so a
    reader of the timeline can tell them from the account events the supplier recorded."""
    windows = _supply_windows(run, base)
    inside, outside = [], []
    pcb = run.get("per_customer_behavioral", {})
    for life in pcb.get(base, {}).get("life_event_history", []):
        date = life.get("date")
        e = {
            "date": date,
            "type": "life_event",
            "commodity": None,
            "detail": life.get("event_type", "").replace("_", " ").capitalize(),
            "seen_by": "world",
        }
        held = bool(date) and any(lo <= date <= hi for lo, hi in windows)
        (inside if held else outside).append(e)
    return inside, outside


def _per_year_data(run, cid):
    """Collect per-year net/gross/revenue for a single customer."""
    years_out = []
    for yr in sorted(run.get("years", {}).keys()):
        ydata = run["years"][yr]
        per_cust = ydata.get("per_customer", {})
        cdata = per_cust.get(cid, {})
        if cdata:
            years_out.append({
                "year": int(yr),
                "revenue_gbp": round(cdata.get("revenue_gbp", 0), 2),
                "gross_gbp": round(cdata.get("gross_gbp", 0), 2),
                "net_gbp": round(cdata.get("net_gbp", 0), 2),
                "tariff_min": round(cdata.get("tariff_min_gbp_per_mwh", 0), 2),
                "tariff_max": round(cdata.get("tariff_max_gbp_per_mwh", 0), 2),
            })
    return years_out


def _round_or_none(value, ndigits):
    """Round a figure, passing a NEVER-POPULATED field through as None.

    The whole point of the attribution fix below: `round(x or 0, n)` and
    `round(d.get(k, 0), n)` both turn "no value was computed" into the number 0,
    and 0 is a value a reader takes as the company's belief.
    """
    return None if value is None else round(value, ndigits)


# Where a record's forward-looking figures are carried. See _forward_looking_basis.
BASIS_ACCOUNT = "account"
BASIS_BILLING_ACCOUNT = "billing_account"
BASIS_NO_BILLING_ACCOUNT = "no_billing_account"


def _forward_looking_basis(cid, base, by_billing_account):
    """Resolve WHERE this record's forward-looking figures are carried, and return
    the billing-account row they come from (None when this record carries none).

    CLV and churn are BILLING-ACCOUNT quantities, not per-commodity ones:
    `saas.clv_model.build_clv` sums both dual-fuel legs' net margin under
    `saas.customer_reaction._billing_account_id` ("C1g" bills under "C1", because
    the household gets one combined dual-fuel bill) and projects a single figure
    for the household. So a gas leg's lifetime value is neither zero nor missing --
    it is ALREADY INSIDE its electricity sibling's figure. Publishing 0 for it
    stated a company belief the company does not hold, on half of every dual-fuel
    household, and left C1's two legs disagreeing about whether the household still
    existed (site/customers/index.html, cold-eyes 2026-08-12, names this the DATA
    half of that finding).

    Three distinct states were all published as the number 0:

      * this leg is not the account of record (every gas leg) -> BASIS_BILLING_ACCOUNT
      * it IS the account of record and build_clv produced a
        value                                                 -> BASIS_ACCOUNT
      * no billing-account row exists for this id at all
        (e.g. SYN-2021-001)                              -> BASIS_NO_BILLING_ACCOUNT

    A row under BASIS_ACCOUNT may still carry `clv_gbp: null` -- build_clv excludes
    accounts with no renewal points, and accounts the caller reports as no longer
    supplied, while still recording their churn belief. That is a real and separate
    state: the account of record, whose lifetime value was not modelled but whose
    churn belief was. It is now visible as a null CLV beside a present churn figure
    rather than as two indistinguishable zeros.

    A genuine COMPUTED zero returns the row under BASIS_ACCOUNT and stays 0.0 -- the
    distinction this function exists to preserve runs in both directions.
    """
    if cid != base:
        # A gas leg. Its value is carried on `base`, whether or not `base` itself
        # was valued -- the attribution statement is true either way.
        return None, BASIS_BILLING_ACCOUNT
    row = by_billing_account.get(base)
    if row is None:
        return None, BASIS_NO_BILLING_ACCOUNT
    return row, BASIS_ACCOUNT


def _forecast_cashflow(avg_annual_net_margin_gbp, expected_lifetime_periods, discount_rate):
    """Forward-looking per-year net cash contribution forecast (director page
    comment, /customers/, 2026-07-11: "expose forecast profit and cashflow").

    Uses the SAME inputs and discounting convention already driving clv_gbp
    (saas/clv_model.py::build_clv) rather than inventing a new methodology --
    avg_annual_net_margin_gbp is this account's historical average annual net
    margin, treated as the forecast for each remaining year of its expected
    lifetime. Capped at 10 years for display (a longer projection is not more
    informative, just more speculative for a Bayesian-survival-model lifetime
    estimate). The sum of discounted_gbp reconciles with clv_gbp by
    construction (same annuity_factor math, same discount rate).
    """
    if not avg_annual_net_margin_gbp or not expected_lifetime_periods:
        return []
    if expected_lifetime_periods <= 0:
        return []
    n_years = min(10, math.ceil(expected_lifetime_periods))
    rows = []
    for year_offset in range(1, n_years + 1):
        # Final partial year gets a fractional weight if the lifetime isn't a whole number.
        weight = min(1.0, expected_lifetime_periods - (year_offset - 1))
        undiscounted = avg_annual_net_margin_gbp * weight
        discounted = undiscounted / (1.0 + discount_rate) ** year_offset
        rows.append({
            "year_offset": year_offset,
            "undiscounted_gbp": round(undiscounted, 2),
            "discounted_gbp": round(discounted, 2),
        })
    return rows


def generate(run_json_path=None):
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    run = json.loads(path.read_text())
    pcl = run.get("per_customer_lifetime", {})
    bba = run.get("by_billing_account", {})
    comm_pnl = run.get("per_cid_comm_pnl", {})
    predecessor_of = predecessors(run.get("occupier_successions"))
    billed_meter = meter_types_billed(run)
    billed_profile_class = profile_classes_billed(run)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for cid, cdata in pcl.items():
        segment = cdata.get("segment", "resi")
        commodity = cdata.get("commodity", "electricity")
        base = _base_id(cid)
        is_gas = cid.endswith("g") and cid != base

        # CLV / churn are BILLING-ACCOUNT quantities -- resolve which account carries
        # this record's, and publish null (never 0) where this record carries none.
        clv_row, fwd_basis = _forward_looking_basis(cid, base, bba)
        clv_data = clv_row or {}
        clv_gbp = _round_or_none(clv_data.get("clv_gbp"), 2)
        churn_p = _round_or_none(clv_data.get("latest_churn_probability"), 3)

        # Commodity-level P&L split
        comm = comm_pnl.get(cid, {})
        elec_comm = comm.get("electricity", {})
        gas_comm = comm.get("gas", {})

        # Dual-fuel companion account
        gas_id = base + "g"
        has_dual_fuel = (gas_id in pcl) and (not is_gas)
        gas_lifetime = pcl.get(gas_id, {}) if has_dual_fuel else None

        obj = dict(
            account_id=cid,
            base_account_id=base,
            segment=segment,
            commodity=commodity,
            is_dual_fuel=has_dual_fuel,
            acquisition_date=cdata.get("acquisition_date", "2016-01-01"),
            tariff_name=_tariff(segment, commodity),
            meter_type=_meter(segment, billed_meter.get(cid)),
            profile_class=billed_profile_class.get(cid) if commodity == "electricity" else None,
            mpan=(_mpan(supply_point_of(cid, predecessor_of), segment, billed_profile_class.get(cid))
                  if commodity == "electricity" else None),
            mprn=(_mprn(supply_point_of(cid, predecessor_of)) if commodity == "gas" else None),
            lifetime_revenue_gbp=round(cdata.get("revenue_gbp", 0), 2),
            lifetime_gross_gbp=round(cdata.get("gross_gbp", 0), 2),
            lifetime_net_gbp=round(cdata.get("net_gbp", 0), 2),
            lifetime_net_after_cts_gbp=round(
                cdata.get("net_margin_after_cost_to_serve_gbp", 0), 2),
            cost_to_serve_gbp=round(cdata.get("cost_to_serve_gbp", 0), 2),
            pricing_action=cdata.get("pricing_action", "NONE"),
            avg_hedge_fraction=(
                round(cdata["avg_hedge_fraction"], 4)
                if cdata.get("avg_hedge_fraction") is not None else None
            ),
            clv_gbp=clv_gbp,
            churn_probability=churn_p,
            expected_lifetime_periods=_round_or_none(
                clv_data.get("expected_lifetime_periods"), 2),
            forecast_annual_profit_gbp=_round_or_none(
                clv_data.get("avg_annual_net_margin_gbp"), 2),
            forecast_cashflow=_forecast_cashflow(
                clv_data.get("avg_annual_net_margin_gbp"),
                clv_data.get("expected_lifetime_periods"),
                DISCOUNT_RATE_ANNUAL,
            ),
            # Which account the four fields above belong to, so a reader can tell a
            # measured zero from a figure carried on the household's other leg.
            forward_looking_basis=fwd_basis,
            forward_looking_account_id=base,
            commodity_split={
                "electricity": {
                    "net_gbp": round(elec_comm.get("net", 0), 2),
                    "revenue_gbp": round(elec_comm.get("revenue", 0), 2),
                } if elec_comm else None,
                "gas": {
                    "net_gbp": round(gas_comm.get("net", 0), 2),
                    "revenue_gbp": round(gas_comm.get("revenue", 0), 2),
                } if gas_comm else None,
            },
            dual_fuel_combined=(
                {
                    "gas_account_id": gas_id,
                    "gas_lifetime_net_gbp": round(gas_lifetime.get("net_gbp", 0), 2),
                    "gas_lifetime_revenue_gbp": round(gas_lifetime.get("revenue_gbp", 0), 2),
                    "combined_net_gbp": round(
                        cdata.get("net_gbp", 0) + gas_lifetime.get("net_gbp", 0), 2
                    ),
                    "combined_revenue_gbp": round(
                        cdata.get("revenue_gbp", 0) + gas_lifetime.get("revenue_gbp", 0), 2
                    ),
                }
                if (has_dual_fuel and gas_lifetime)
                else None
            ),
            annual_pnl=_per_year_data(run, cid),
            timeline=_timeline(run, base),
            # Not the supplier's: the world's events from before we supplied the home or after it
            # left. Kept so the simulation's record stays whole, never read as something we knew.
            world_life_events_outside_supply=_life_events(run, base)[1],
            invoices=[],
        )
        (OUT_DIR / (cid + ".json")).write_text(json.dumps(obj, indent=2))
        written.append(cid)

    index = sorted(pcl.keys())
    (OUT_DIR / "_index.json").write_text(json.dumps(index))
    retired = _retire_departed_artefacts(index)
    print("Generated", len(written), "customer files in", str(OUT_DIR))
    if retired:
        print("Retired", len(retired), "departed customer files:", ", ".join(retired))
    return index


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
