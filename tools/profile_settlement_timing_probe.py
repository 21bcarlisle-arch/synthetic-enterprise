#!/usr/bin/env python3
"""What settling each home's OWN half hours costs against settling its annual volume x the published
Profile Class shape -- which is what 2016-2025 non-half-hourly domestic settlement actually did.

Pre-registration and result:
docs/staging/records/SEAT_PREREGISTRATION_WHAT_SETTLING_EACH_HOMES_OWN_SHAPE_IS_WORTH_AGAINST_THE_PROFILE_2026-10-22.md
docs/staging/records/SEAT_RESULT_SETTLING_EACH_HOMES_OWN_SHAPE_AGAINST_THE_PROFILE_IS_NEAR_ZERO_FOR_THE_BOOK_AND_TENS_OF_POUNDS_FOR_AN_ELECTRICALLY_HEATED_HOME_2026-10-22.md

The shapes come from the run's own builders, wired as `run_phase2b.main` wires them. That setup
lives inside `main()`, so it is copied here in the same order rather than imported. If `main`
changes how a premise's shape is built, this copy has to follow it.

THE PROFILE CLASS IS THE TRAP. Read against PC1, a storage-heated home shows about -£90 a year of
"timing value", and that is entirely the wrong profile. Since 2026-10-22 each home is graded on the
class `run_phase2b.registered_profile_class` registers it on (PC2 for a drawn storage-heated home).
`--pc2-csv` still grades every electrically heated fabric home against PC2 as well, whatever it is
registered on; it defaults to the tree's own table, `sim/data/profile_class_2_gad.csv`.

DELIBERATELY DORMANT (orphan_baseline.json): a one-off measurement taken by hand. It takes about
12 minutes over the full book.

    python3 -m tools.profile_settlement_timing_probe --json out.json [--limit N] [--pc2-csv PATH]
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import date
from functools import lru_cache

from sim.profile_class_2 import CSV_PATH as PC2_CSV

#: Settlement periods 1-14, 00:00-07:00: the overnight window used to tell a storage/E7-shaped home
#: from a day-heated one. Descriptive only -- it splits the report and gates nothing.
_OVERNIGHT_PERIODS = slice(0, 14)


def year_delta(shape, profile, prices, dates):
    """(own kWh, own cost £, profiled cost £) for one home over `dates`, or None if nothing settled.

    The profile carries the home's OWN volume over the same priced periods -- the annual true-up
    reconciliation performed -- so the difference is timing alone.
    """
    own, prof = [], []
    for d in dates:
        s, p = shape(d), profile(d)
        for i in range(48):
            px = prices.get((d, i + 1))
            if px is not None:
                own.append((s[i], px))
                prof.append((p[i], px))
    own_kwh = sum(q for q, _ in own)
    prof_kwh = sum(q for q, _ in prof)
    if own_kwh <= 0 or prof_kwh <= 0:
        return None
    k = own_kwh / prof_kwh
    return (own_kwh, sum(q * px for q, px in own) / 1000.0,
            sum(q * k * px for q, px in prof) / 1000.0)


def overnight_share(shape, dates) -> float:
    total = night = 0.0
    for d in dates:
        s = shape(d)
        total += sum(s)
        night += sum(s[_OVERNIGHT_PERIODS])
    return night / total if total else 0.0


def _book_shapes(r, limit):
    customers = r.ELEC_CUSTOMERS + r.SUCCESSOR_ELEC_CUSTOMERS
    if limit:
        customers = customers[:limit]
    properties = r.build_properties(r.CUSTOMERS, dwellings=r.live_dwellings())
    register = r.HouseholdDemandRegister(r.CUSTOMERS, drawn_households=r.live_drawn_households())
    source = r.WeatherWorldSource.load()
    world = source.world
    end = min(r.REPORT_END, world.record_end())
    r.adopt_shared_world(world)
    r.adopt_book(r.ELEC_CUSTOMERS + r.GAS_CUSTOMERS + r.SUCCESSOR_ELEC_CUSTOMERS)
    weather = {c["customer_id"]: r.weather_means_for_customer(c, world) for c in customers}
    cloud = {c["customer_id"]: r.cloud_cover_for_customer(c, world) for c in customers}
    fabric, _verdicts = r.fabric_providers_for_book(
        customers=customers,
        household_at_date=register.household_at_date,
        is_half_hourly_metered=r.is_hh_customer,
        weather_site_for=source.site_for,
        weather_available=source.available,
        latitude_for=lambda c: c.get("location", {}).get("lat") or r.DEFAULT_LATITUDE_DEG,
        start=date.fromisoformat(r.REPORT_START),
        end=date.fromisoformat(end),
        weather_days_for=source.days,
    )

    def battery_for(cid):
        def dispatch(gross, generation, date_str):
            dyn = register.dynamic_assets(cid, date_str) or {}
            kwh = dyn.get("battery_kwh", 0.0) if dyn.get("battery") else 0.0
            if not kwh:
                return [g - p for g, p in zip(gross, generation)]
            return r._battery_daily_dispatch(gross, generation, kwh)
        return dispatch

    for c in customers:
        cid = c["customer_id"]
        if r.is_hh_customer(c):
            continue  # elective HH settlement was real for these
        pc = r.registered_profile_class(
            c, register, max(c.get("acquisition_date") or r.REPORT_START, r.REPORT_START))
        if cid in fabric:
            series = fabric[cid]
            shape = r.fabric_shape_fn(series, "electricity", battery_dispatch=battery_for(cid))
            group = f"fabric_{series.heating_commodity}_heated"
        else:
            shape = r._weather_adjusted_shape_fn(
                r.SHAPE_LOADERS[pc], weather[cid], properties.get(cid, r.DEFAULT_PROPERTY),
                cloud_cover_means=cloud.get(cid), latitude_deg=c.get("location", {}).get("lat"),
                household_register=register, customer_id=cid, eac_kwh=r._base_profile_eac(c),
            )
            group = f"legacy_pc{pc}"
        yield c, pc, group, lru_cache(maxsize=None)(shape), end


def through_settlement(shape, profile, records, dates):
    """(gross wholesale cost on the profile minus on the own shape, max |revenue difference|) from
    `hedged_settlement.run_deemed_term` itself over `dates` -- the run's own writer, so P15a of
    SEAT_PREREGISTRATION_A_PROFILED_HOME_SETTLES_ITS_OWN_VOLUME_ON_ITS_REGISTERED_PROFILE_2026-10-22
    grades the build rather than this file's arithmetic."""
    from simulation.hedged_settlement import run_deemed_term
    end = date.fromordinal(date.fromisoformat(dates[-1]).toordinal() + 1).isoformat()
    a = run_deemed_term("probe", dates[0], end, 0.0, shape, records)
    b = run_deemed_term("probe", dates[0], end, 0.0, shape, records, settled_shape=profile)
    cost = sum(x["wholesale_cost_gbp"] for x in b) - sum(x["wholesale_cost_gbp"] for x in a)
    return cost, max((abs(x["revenue_gbp"] - y["revenue_gbp"]) for x, y in zip(a, b)), default=0.0)


def measure(limit=None, pc2_csv=None, settle=False):
    import simulation.run_phase2b as r
    from sim.profile_class_1 import load_pc1_shape

    pc2 = lru_cache(maxsize=None)(lambda d: load_pc1_shape(d, pc2_csv)) if pc2_csv else None
    records = r.get_cached_prices(r.SSP_RECORD_START, r.REPORT_END)
    prices = {(x["settlementDate"], x["settlementPeriod"]): x["systemSellPrice"] for x in records}
    records_by_year = defaultdict(list)
    for x in records:
        records_by_year[x["settlementDate"][:4]].append(x)
    rows = []
    for c, pc, group, shape, end in _book_shapes(r, limit):
        profile = lru_cache(maxsize=None)(r.SHAPE_LOADERS[pc])
        by_year = defaultdict(list)
        d0 = date.fromisoformat(max(c["acquisition_date"], r.REPORT_START))
        for o in range((date.fromisoformat(end) - d0).days):
            d = date.fromordinal(d0.toordinal() + o).isoformat()
            by_year[d[:4]].append(d)
        all_dates = [d for ds in by_year.values() for d in ds]
        night = overnight_share(shape, all_dates)
        for year, dates in sorted(by_year.items()):
            got = year_delta(shape, profile, prices, dates)
            if got is None:
                continue
            kwh, own, prof = got
            row = {"customer_id": c["customer_id"], "group": group, "pc": pc, "year": year,
                   "days": len(dates), "overnight_share": night, "kwh": kwh,
                   "own_cost": own, "prof_cost": prof, "delta": own - prof}
            if settle and group.startswith("fabric_"):
                row["settled_cost_move"], row["revenue_moved"] = through_settlement(
                    shape, profile, records_by_year[year], dates)
            if pc2 and group == "fabric_electricity_heated":
                alt = year_delta(shape, pc2, prices, dates)
                row["delta_pc2"] = alt[1] - alt[2]
            rows.append(row)
    return rows


def report(rows):
    def line(sel, label, key="delta"):
        if not sel:
            return
        full = [x[key] for x in sel if x["days"] >= 365]
        own = sum(x["own_cost"] for x in sel)
        dl = sum(x[key] for x in sel)
        out = (f"{label:34s} homes={len({x['customer_id'] for x in sel}):4d} home-years={len(sel):5d} "
               f"own=£{own:,.0f} Δ=£{dl:,.0f} ({100 * dl / own:+.2f}%)")
        if full:
            out += (f" | full-yr mean £{statistics.mean(full):+.1f} median "
                    f"£{statistics.median(full):+.1f} mean|Δ| £{statistics.mean(abs(v) for v in full):.1f}")
        print(out)

    for g in sorted({x["group"] for x in rows}):
        line([x for x in rows if x["group"] == g], g)
    line(rows, "BOOK (every home on its registered class)")
    eh = [x for x in rows if "delta_pc2" in x]
    for label, keep in (("night-heavy (>=38% overnight)", lambda s: s >= 0.38),
                        ("day-heated (<30% overnight)", lambda s: s < 0.30)):
        sel = [x for x in eh if keep(x["overnight_share"])]
        line(sel, f"  elec-heated {label} vs PC1")
        line(sel, f"  elec-heated {label} vs PC2", "delta_pc2")
    st = [x for x in rows if "settled_cost_move" in x]
    if st:
        worst = max(abs(x["settled_cost_move"] + x["delta"]) for x in st)
        print(f"THROUGH run_deemed_term: {len(st)} fabric home-years, max |move + Δ| £{worst:.4f}, "
              f"max |revenue moved| £{max(x['revenue_moved'] for x in st):.6f}")
        for g in sorted({x["group"] for x in st}):
            sel = [x for x in st if x["group"] == g]
            full = [x["settled_cost_move"] for x in sel if x["days"] >= 365]
            print(f"  {g:34s} cost move £{sum(x['settled_cost_move'] for x in sel):,.0f}"
                  + (f" | full-yr mean £{statistics.mean(full):+.1f}" if full else ""))
        for label, keep in (("night-heavy (>=38% overnight)", lambda s: s >= 0.38),
                            ("day-heated (<30% overnight)", lambda s: s < 0.30)):
            full = [x["settled_cost_move"] for x in st if x["group"] == "fabric_electricity_heated"
                    and keep(x["overnight_share"]) and x["days"] >= 365]
            if full:
                print(f"  elec-heated {label:30s} full-yr mean cost move £{statistics.mean(full):+.1f}")
    if eh:
        swap = sum(x["delta_pc2"] - x["delta"] for x in eh if x["overnight_share"] >= 0.38)
        own = sum(x["own_cost"] for x in rows)
        dl = sum(x["delta"] for x in rows) + swap
        print(f"BOOK with night-heavy homes on PC2: Δ=£{dl:,.0f} ({100 * dl / own:+.2f}%)")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--json")
    ap.add_argument("--pc2-csv", default=PC2_CSV, help="a PC2 GAD table (default: the tree's)")
    ap.add_argument("--through-settlement", action="store_true",
                    help="also settle each fabric home-year through run_deemed_term (P15a/b)")
    a = ap.parse_args(argv)
    rows = measure(a.limit, a.pc2_csv, settle=a.through_settlement)
    report(rows)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(rows, f)


if __name__ == "__main__":
    main()
