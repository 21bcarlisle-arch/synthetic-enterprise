"""The cash hole H each stylised 2021-22 supplier strategy takes in the world, Jul 2021 to Mar 2022.

Step (d) of the director's steer of 18 Nov 2026 ("the world must rank real 2021-22 supplier
strategies in the order reality did"). The test, its quantity and its pass rule are pre-registered
in `docs/staging/records/SEAT_PREREG_THE_WORLD_PUTS_A_BIGGER_CASH_HOLE_IN_THE_FAILED_STRATEGIES_
THAN_IN_THE_CAP_TRACKING_SURVIVOR_2026-11-18.md`; every strategy parameter comes from
`docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md`. This module only composes.

A HARNESS INSTRUMENT, NOT THE COMPANY (W7, R13). It reads `sim/`, `simulation/` and published
artefacts, never `company/` or `saas/`, and nothing in the company reads it or its output.

WHY REVENUE IS THE CAP'S COMMODITY ALLOWANCE, NOT THE WHOLE UNIT RATE. The pre-registration's flow
is "revenue - cost + change in credit balances", with cost the wholesale energy. Read literally on
the full cap unit rate, every strategy would book the network, policy and operating allowances as
profit, which they are not: those pass through at the same rate whatever the hedge. So both sides
are taken on ONE basis, the cap's own commodity allowance (DF + CM, `ofgem_cap_unit_rate_composition
.json`, GB median, ex-VAT), and every wholesale price is put on that basis by the cap's own uplift
from its index to its allowance (`uplift`, measured, not chosen). That removes a term identical
across strategies; it cannot move the ranking, and it does mean the "cap's operating allowances"
part of the pre-registration's predicted S5 residual is out by construction (said in the result).

TWO READINGS OF A DISCLOSED HEDGE. "Hedged 20% three months out, 15% nine months out" is a snapshot
of cover held at disclosure (`static`: the book at 1 Jul 2021, cover bought before it), or a policy
every delivery month passes through (`rolling`: the last tranche bought three months out at that
week's forward). The pre-registration's predicted mechanism for S4 ("the unhedged SVT after Oct-21")
is the static reading, so static is primary. Rolling is reported beside it as a sensitivity the
pre-registration did not name; it is not part of the pre-registered verdict.

Run: `python3 -m tools.strategy_cash_hole_2021_22` (prints the tables and the verdict);
`--json PATH` also writes the full result.
"""

from __future__ import annotations

import argparse
import json
from calendar import monthrange
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from statistics import mean

from sim.gas_prices_history import load_nbp_history
from sim.profile_class_1 import load_pc1_shape
from sim.weather_hdd import REFERENCE_MONTHLY_HDD
from simulation.gas_settlement import resi_daily_gas_kwh
from simulation.market_switching_propensity import market_departure_rate
from simulation.price_cap_enforcement import ofgem_cap_unit_rate_gbp_per_mwh_inc_vat

ROOT = Path(__file__).resolve().parents[1]
_COMPOSITION = ROOT / "docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json"
_FORWARD_AXIS = ROOT / "docs/market_research/ofgem_forward_weekly_with_delivery_start_2021_2026.json"
_MID = ROOT / "sim/cache/elexon_mid_2021_2023.json"

FUELS = ("electricity", "gas")
#: The window the pre-registration names: 1 Jul 2021 to 31 Mar 2022, monthly.
MONTHS = [(2021, m) for m in range(7, 13)] + [(2022, m) for m in range(1, 4)]
START = date(2021, 7, 1)

#: The F grid the pre-registration fixes: £0 to £400 per customer in £25 steps.
F_GRID = list(range(0, 401, 25))

#: Fixed-tariff share swept, NAO 3.22 ("more than half"), pre-registered set.
FIXED_SHARES = (0.5, 0.75, 1.0)
#: Credit balances, NERA for Ofgem (Jun 2022) p.80: the Sep-Dec 2021 average net of unbilled,
#: £65 (large) and £80 (small) per customer. Pre-registered as the two ends of the sweep.
CREDIT_BALANCE_SEP_DEC_GBP = (65.0, 80.0)

# ---------------------------------------------------------------- strategies (page table, no others)
# Each ladder maps months-of-lead -> cover. "3m/9m" disclosures interpolate linearly between the two
# leads and hold the 3m figure inside three months (nothing shorter is published).
STRATEGIES = {
    "S1": {"what": "Unhedged timing entrant (Green Supplier)", "fixed": [(3, 0.0, 0.0)], "svt": "same"},
    "S2": {"what": "Short-hedged growth book (Avro)", "fixed": [(3, 0.20, 0.15)], "svt": "same"},
    # PFP 91% / c.70%, Together 87% / 95%: both published pairs, swept as two points.
    "S3": {"what": "Well hedged on negative equity (PFP, Together)",
           "fixed": [(3, 0.91, 0.70), (3, 0.87, 0.95)], "svt": "together_ladder"},
    "S4": {"what": "Fixed fully hedged, SVT unhedged beyond 3m (Pure Planet)",
           "fixed": [(3, 1.0, 1.0)], "svt": "pure_planet"},
    "S5": {"what": "Hedged to the cap's own 6-2-12 reference profile", "fixed": [(3, 1.0, 1.0)],
           "svt": "cap_6_2_12"},
}


def _interp(c3: float, c9: float, lead: int) -> float:
    if lead <= 3:
        return c3
    if lead >= 9:
        return c9
    return c3 + (c9 - c3) * (lead - 3) / 6.0


def svt_cover(kind: str, pair: tuple, lead: int) -> float:
    """Cover on the SVT book for a month `lead` months after the hedge reading date."""
    if kind == "same":
        return _interp(pair[1], pair[2], lead)
    if kind == "together_ladder":
        # Together (Oxera p.109): "100% of SVT volume hedged in the month ahead, to 20% in month 6".
        # Month 1 = lead 0. Beyond month 6 nothing is said; the last step (20%) is held, which is the
        # direction against our own thesis (more cover in a rising market shrinks S3's hole), F11.
        step = min(lead, 5)
        return 1.0 - 0.16 * step
    if kind == "pure_planet":
        return 1.0 if lead < 3 else 0.0
    raise ValueError(kind)


# ------------------------------------------------------------------------------------- world inputs
@lru_cache(maxsize=None)
def _composition() -> dict:
    return json.loads(_COMPOSITION.read_text())


def _period_row(fuel: str, d: date) -> dict:
    key = "by_payment_method" if fuel == "electricity" else "gas_by_payment_method"
    rows = sorted(_composition()[key]["direct_debit"]["periods"], key=lambda r: r["starts"])
    chosen = None
    for r in rows:
        if date.fromisoformat(r["starts"]) <= d:
            chosen = r
    if chosen is None:
        raise LookupError(f"no cap period for {fuel} on {d}")
    return chosen


def cap_commodity_allowance(fuel: str, d: date) -> float:
    """The cap's commodity (DF+CM) allowance on the unit rate, £/MWh ex-VAT, GB median, DD."""
    r = _period_row(fuel, d)
    return r["unit_rate_p_per_kwh_ex_vat"] * r["commodity_share_of_unit_rate"] * 10.0


def _benchmark_kwh(fuel: str) -> float:
    return float(_period_row(fuel, START)["benchmark_kwh"])


@lru_cache(maxsize=None)
def _forward_rows(fuel: str) -> list[dict]:
    rows = json.loads(_FORWARD_AXIS.read_text())["rows"]
    return sorted((r for r in rows if r["fuel"] == fuel), key=lambda r: r["trade_week_start"])


def forward_mean(fuel: str, trade_from: date, trade_to: date) -> float:
    """Mean 12-month basket forward over trade weeks wholly published in [trade_from, trade_to].

    Point-in-time: a row is read from its trade_week_end. Before the first published week (1 Feb
    2021) there is no forward at all; the first published week stands in and the caller says so.
    """
    rows = _forward_rows(fuel)
    first = date.fromisoformat(rows[0]["trade_week_start"])
    if trade_to < first:
        return rows[0]["price_gbp_per_mwh"]
    pick = [r["price_gbp_per_mwh"] for r in rows
            if trade_from <= date.fromisoformat(r["trade_week_start"])
            and date.fromisoformat(r["trade_week_end"]) <= trade_to]
    if not pick:
        raise LookupError(f"no {fuel} forward traded {trade_from}..{trade_to}")
    return mean(pick)


@lru_cache(maxsize=None)
def uplift(fuel: str) -> dict:
    """The cap's own ratio of commodity allowance to its 6-2-12 index, Oct-21 period.

    The Oct-21 cap's observation window (window 0, delivery from 1 Oct 2021) is wholly inside the
    published forward, so this is the one period where both the index and the allowance are read,
    not inferred. It carries shape, losses, CM and (gas) UIG. It is applied to every wholesale price
    so cost and revenue sit on one basis.
    """
    idx = mean(r["price_gbp_per_mwh"] for r in _forward_rows(fuel)
               if r["delivery_start"] == "2021-10-01" and r.get("window") == 0)
    allow = cap_commodity_allowance(fuel, date(2021, 10, 1))
    return {"index_gbp_per_mwh": idx, "allowance_gbp_per_mwh": allow, "k": allow / idx}


@lru_cache(maxsize=None)
def _mid_monthly() -> dict:
    raw = json.loads(_MID.read_text())
    acc: dict = {}
    for r in raw:
        if r.get("dataProvider") != "APXMIDP" or not r.get("volume"):
            continue
        ym = tuple(int(x) for x in r["settlementDate"][:7].split("-"))
        acc.setdefault(ym, []).append(r["price"])
    return {k: mean(v) for k, v in acc.items()}


@lru_cache(maxsize=None)
def _gas_monthly() -> dict:
    acc: dict = {}
    for r in load_nbp_history(str(ROOT / "sim/gas_data/nbp_sap.csv")):
        d = r["settlementDate"]
        ym = (int(d[:4]), int(d[5:7]))
        acc.setdefault(ym, []).append(float(r["systemSellPrice"]))
    return {k: mean(v) for k, v in acc.items()}


def spot_raw(fuel: str, ym: tuple) -> float:
    """Baseload monthly spot, £/MWh: Elexon MID (APX) for electricity, the TTF monthly proxy for gas.

    Baseload, like the forward basket, so the cap's uplift applies to both alike."""
    src = _mid_monthly() if fuel == "electricity" else _gas_monthly()
    if ym not in src:
        raise LookupError(f"no {fuel} spot for {ym}")
    return src[ym]


@lru_cache(maxsize=None)
def monthly_volume_mwh(fuel: str) -> dict:
    """One typical dual-fuel customer's volume per month at Ofgem's benchmark annual consumption.

    Electricity: Elexon Profile Class 1 daily totals, scaled so a calendar year sums to the
    benchmark. Gas: the world's own two-term daily form at 1991-2020 normal HDD. Weather is normal:
    the 2021-22 weather deviation (Together's "demand uncertainties") is not tested here.
    """
    bench = _benchmark_kwh(fuel)
    if fuel == "electricity":
        year = [date(2021, 1, 1) + timedelta(days=i) for i in range(365)]
        daily = {d: sum(load_pc1_shape(d)) for d in year}
        scale = bench / sum(daily.values())
        out = {}
        for y, m in MONTHS:
            days = [date(y, m, i) for i in range(1, monthrange(y, m)[1] + 1)]
            out[(y, m)] = sum(sum(load_pc1_shape(d)) for d in days) * scale / 1000.0
        return out
    out = {}
    for y, m in MONTHS:
        n = monthrange(y, m)[1]
        hdd_day = REFERENCE_MONTHLY_HDD[m] / n
        out[(y, m)] = n * resi_daily_gas_kwh(bench, hdd_day) / 1000.0
    return out


def svt_survival(ym: tuple) -> float:
    """Share of the 1 Jul 2021 SVT book still on supply in month `ym` (mid-month), at the world's
    annual departure rate. GAP: the within-2021 collapse in switching after Sep-21 is not resolved."""
    surv, cursor = 1.0, START
    y, m = ym
    mid = date(y, m, 15)
    while cursor < mid:
        rate = market_departure_rate(cursor.year)
        step_end = min(mid, date(cursor.year + 1, 1, 1))
        surv *= (1.0 - rate) ** ((step_end - cursor).days / 365.0)
        cursor = step_end
    return surv


def _lead(ym: tuple) -> int:
    return (ym[0] - START.year) * 12 + ym[1] - START.month


def _month_start(ym: tuple, back: int) -> date:
    y, m = ym
    m -= back
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1)


# -------------------------------------------------------------------------------- the strategy flow
def _strike(fuel: str) -> float:
    """Fixed rates and fixed-book hedges: struck at the Jul-21 forward (pre-registration §2)."""
    return forward_mean(fuel, date(2021, 7, 1), date(2021, 7, 31))


def _svt_hedge_price(fuel: str, kind: str, ym: tuple, reading: str, cover: float, c9: float) -> float:
    """Raw (pre-uplift) price paid for the SVT cover on delivery month `ym`."""
    if kind == "cap_6_2_12":
        # By definition the cap's own index for the period the month falls in. For the Apr-21 cap
        # (Jul-Sep 21) the window (Aug-20..Jan-21) predates the published forward, so the index is
        # read back from the allowance through the measured uplift.
        return cap_commodity_allowance(fuel, date(*ym, 1)) / uplift(fuel)["k"]
    if reading == "static":
        # Cover held on 1 Jul 2021, bought in the published months before it.
        return forward_mean(fuel, date(2021, 2, 1), date(2021, 6, 30))
    # rolling: the long tranche at nine months out, the rest at three (Together's ladder and Pure
    # Planet's 3m cover: bought at the shortest lead that still carries it).
    if kind == "together_ladder":
        lead_months = 6
    elif kind == "pure_planet":
        lead_months = 3
    else:
        lead_months = 3
    def at(back: int) -> float:
        t0 = _month_start(ym, back)
        return forward_mean(fuel, t0, t0 + timedelta(days=30))
    if kind == "same" and cover > 0:
        long_part = min(c9, cover)
        return (long_part * at(9) + (cover - long_part) * at(3)) / cover
    return at(lead_months)


def strategy_path(name: str, fixed_share: float, pair: tuple, reading: str) -> dict:
    """Monthly commodity-basis cash flow, per opening customer, both fuels, before credit balances."""
    spec = STRATEGIES[name]
    kind = spec["svt"]
    rows = []
    for ym in MONTHS:
        lead = _lead(ym)
        flow = 0.0
        for fuel in FUELS:
            k = uplift(fuel)["k"]
            vol = monthly_volume_mwh(fuel)[ym]
            spot = spot_raw(fuel, ym) * k
            strike = _strike(fuel) * k
            # Fixed book: 12-month contracts, no leavers inside the window, revenue at strike.
            c_fix = _interp(pair[1], pair[2], lead)
            fix_vol = fixed_share * vol
            flow += fix_vol * (strike - (c_fix * strike + (1 - c_fix) * spot))
            # SVT book: revenue at the cap's commodity allowance on the volume still on supply;
            # cover sized on the opening book, so leavers' cover is sold back at spot.
            svt_open = (1 - fixed_share) * vol
            if svt_open == 0:
                continue
            c_svt = 1.0 if kind == "cap_6_2_12" else svt_cover(kind, pair, lead)
            surv = svt_survival(ym)
            on_supply = svt_open * surv
            hedge_vol = c_svt * svt_open
            hedge_px = _svt_hedge_price(fuel, kind, ym, reading, c_svt, pair[2]) * k
            revenue = on_supply * cap_commodity_allowance(fuel, date(*ym, 1))
            bought = hedge_vol * hedge_px + max(on_supply - hedge_vol, 0.0) * spot
            sold_back = max(hedge_vol - on_supply, 0.0) * spot
            flow += revenue - bought + sold_back
        rows.append({"month": f"{ym[0]}-{ym[1]:02d}", "flow_gbp": flow})
    return {"rows": rows}


@lru_cache(maxsize=None)
def credit_balance_path(sep_dec_avg: float) -> dict:
    """Per-customer credit balance at each month end, Jun-21 .. Mar-22, £.

    Shape from the world: a flat direct debit against the seasonal bill at the cap's full unit rates
    (benchmark volumes, the months above, the year Apr-21..Mar-22 balancing to zero). Level: shifted
    so the Sep-Dec 2021 average equals NERA's figure. Standing charges are flat and cancel out of the
    shape; they are left out.
    """
    year = [(2021, m) for m in range(4, 13)] + [(2022, m) for m in range(1, 4)]
    bill = {}
    for ym in year:
        total = 0.0
        for fuel in FUELS:
            if ym in monthly_volume_mwh(fuel):
                vol = monthly_volume_mwh(fuel)[ym]
            else:  # Apr-Jun 21: same shape functions, outside MONTHS
                vol = _volume_outside(fuel, ym)
            total += vol * ofgem_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, date(*ym, 15))
        bill[ym] = total
    dd = sum(bill.values()) / 12.0
    bal, path = 0.0, {}
    for ym in year:
        bal += dd - bill[ym]
        path[ym] = bal
    level = mean(path[(2021, m)] for m in (9, 10, 11, 12))
    shift = sep_dec_avg - level
    return {f"{y}-{m:02d}": v + shift for (y, m), v in path.items()}


def _volume_outside(fuel: str, ym: tuple) -> float:
    y, m = ym
    bench = _benchmark_kwh(fuel)
    n = monthrange(y, m)[1]
    if fuel == "electricity":
        year = [date(2021, 1, 1) + timedelta(days=i) for i in range(365)]
        scale = bench / sum(sum(load_pc1_shape(d)) for d in year)
        return sum(sum(load_pc1_shape(date(y, m, i))) for i in range(1, n + 1)) * scale / 1000.0
    return n * resi_daily_gas_kwh(bench, REFERENCE_MONTHLY_HDD[m] / n) / 1000.0


def hole(name: str, fixed_share: float, pair: tuple, credit: float, reading: str) -> dict:
    path = strategy_path(name, fixed_share, pair, reading)["rows"]
    bal = credit_balance_path(credit)
    opening = bal["2021-06"]
    cum, worst, worst_month, series = 0.0, 0.0, None, []
    for r in path:
        cum += r["flow_gbp"]
        held = bal[r["month"]] - opening
        point = cum + held
        series.append({"month": r["month"], "wholesale_cum_gbp": round(cum, 2),
                       "credit_change_gbp": round(held, 2), "cash_gbp": round(point, 2)})
        if point < worst:
            worst, worst_month = point, r["month"]
    return {"H_gbp": round(worst, 2), "trough": worst_month, "series": series}


def run(reading: str) -> dict:
    points = []
    for name, spec in STRATEGIES.items():
        for pair in spec["fixed"]:
            for fs in FIXED_SHARES:
                for cb in CREDIT_BALANCE_SEP_DEC_GBP:
                    h = hole(name, fs, pair, cb, reading)
                    points.append({"strategy": name, "fixed_share": fs, "cover_3m_9m": list(pair[1:]),
                                   "credit_sep_dec_gbp": cb, **h})
    return {"reading": reading, "points": points, "verdict": verdict(points),
            # NOT the pre-registered verdict. At fixed share 1.0 there is no SVT book, so S4 and S5
            # are the same strategy (fixed fully hedged at strike) and tie exactly; the pre-registered
            # rule fails there by definition. This is the verdict with that point removed, filed
            # after the answer was known and labelled so.
            "post_hoc_verdict_without_fixed_share_1": verdict(
                [p for p in points if p["fixed_share"] < 1.0])}


def verdict(points: list[dict]) -> dict:
    """Pre-registration §4.1. Pass iff a band of F holds H_S5 > -F and every S1-S4 hole below -F at
    EVERY sweep point; fail if no band, or if any S1-S4 hole is smaller than S5's at any sweep point."""
    s5 = [p for p in points if p["strategy"] == "S5"]
    s5_worst = max(-p["H_gbp"] for p in s5)  # biggest S5 hole, £ positive
    failed_tier = [p for p in points if p["strategy"] != "S5"]
    tier_least = min(-p["H_gbp"] for p in failed_tier)  # smallest S1-S4 hole
    # Per sweep point: same fixed share and credit balance.
    inversions = []
    for p in failed_tier:
        twin = next(q for q in s5 if q["fixed_share"] == p["fixed_share"]
                    and q["credit_sep_dec_gbp"] == p["credit_sep_dec_gbp"])
        if -p["H_gbp"] < -twin["H_gbp"]:
            inversions.append({k: p[k] for k in ("strategy", "fixed_share", "cover_3m_9m",
                                                 "credit_sep_dec_gbp", "H_gbp")})
    grid = [f for f in F_GRID if s5_worst < f < tier_least]
    by_strategy = {}
    for name in STRATEGIES:
        hs = [p["H_gbp"] for p in points if p["strategy"] == name]
        by_strategy[name] = {"deepest": min(hs), "shallowest": max(hs)}
    return {
        "passes": bool(grid) and not inversions,
        "band_gbp_per_customer": [round(s5_worst, 2), round(tier_least, 2)] if tier_least > s5_worst else None,
        "band_width_gbp": round(max(tier_least - s5_worst, 0.0), 2),
        "F_grid_points_in_band": grid,
        "inversions": inversions,
        "by_strategy": by_strategy,
    }


def _inputs_table() -> dict:
    out = {}
    for fuel in FUELS:
        u = uplift(fuel)
        out[fuel] = {
            "uplift": {k: round(v, 4) for k, v in u.items()},
            "strike_jul21_raw": round(_strike(fuel), 2),
            "svt_static_hedge_raw_feb_jun21": round(forward_mean(fuel, date(2021, 2, 1), date(2021, 6, 30)), 2),
            "months": [{"month": f"{y}-{m:02d}", "volume_mwh": round(monthly_volume_mwh(fuel)[(y, m)], 4),
                        "spot_raw": round(spot_raw(fuel, (y, m)), 2),
                        "cap_commodity_allowance": round(cap_commodity_allowance(fuel, date(y, m, 1)), 2),
                        "svt_survival": round(svt_survival((y, m)), 4)} for y, m in MONTHS],
        }
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)
    result = {"inputs": _inputs_table(),
              "credit_balance_paths": {str(c): credit_balance_path(c) for c in CREDIT_BALANCE_SEP_DEC_GBP},
              "static": run("static"), "rolling": run("rolling")}
    for fuel, t in result["inputs"].items():
        print(f"\n{fuel}: uplift {t['uplift']}  strike(Jul-21) {t['strike_jul21_raw']}"
              f"  static SVT hedge {t['svt_static_hedge_raw_feb_jun21']}")
        for r in t["months"]:
            print("  ", r)
    for reading in ("static", "rolling"):
        res = result[reading]
        print(f"\n=== reading: {reading}")
        for p in res["points"]:
            print(f"  {p['strategy']} fixed={p['fixed_share']:.2f} cover={p['cover_3m_9m']} "
                  f"credit={p['credit_sep_dec_gbp']:.0f}  H={p['H_gbp']:9.2f}  trough={p['trough']}")
        print("  pre-registered verdict:", json.dumps(res["verdict"]))
        print("  post-hoc, fixed share 1.0 removed:", json.dumps(res["post_hoc_verdict_without_fixed_share_1"]))
    if args.json:
        args.json.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
