"""COUPLED-TRIAD runner for the household-shape and weather pairs of D48 billing accuracy.

HARNESS code, outside the wall: it holds the world's metered use (`meter_read_log[].true_consumption_kwh`)
beside what the company billed and the shape it billed on. Nothing here is imported by `company/`.

Two readings, one book:

1. BILLED MINUS METERED, BY READ TYPE, per account-month. Read type is the bill's own basis: `actual`
   (traditional meter read), `smart` (smart read), `estimated` (no read; either meter), and
   prepayment split by whether the world's read was actual. Mean |billed - metered| and mean signed,
   each with an account-clustered bootstrap 95% interval. This is where any billing gap sits.

2. W2_30 <-> D48: THE SEASONAL SHAPE. The company estimates an unread month as its trailing reads
   spread on a published monthly share of annual use (`company.billing.unread_month_estimate`). That
   share IS its belief about how a household's year is shaped. Per account-year with twelve monthly
   bills, truth = each month's share of the year's metered use; belief = the published share over the
   same days (PC2 registers summed for an Economy 7 meter); no-skill = share by days, the flat
   pro-rata the estimator's own docstring names as its control. gap = sum|belief - truth| /
   sum|no-skill - truth|. Shares, not kWh, so the estimator's level error (what the trailing window
   got wrong about the year) does not enter: this grades the shape alone. It is still the shape the
   world produced in a given year, weather included, and it says so.

W1_14 <-> D48 is NOT given a gap. The company holds no weather belief for billing (the estimator's own
docstring: "the company holds no weather feed for billing"), so there is no belief to grade against
the cell's weather, and a ratio of zero-belief to zero-baseline would be 1.0 by construction, not by
measurement. Its row carries what IS measured: the size of the year-specific part of the true shape
(each account-month's share less that account's mean share for the calendar month), the error a
weather-blind estimate cannot avoid. The pair closes when the company carries a weather-corrected
estimate, a capability, not a measurement.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

from background.gap_metric import GAP_LEDGER_PATH, _normalise, _substream_seed, write_gap_entry
from background.live_ledger_guard import guard_live_ledger_write
from company.billing.unread_month_estimate import (
    ECONOMY_7_REGISTERS,
    profile_weight,
    register_profile_weight,
)

TWIN = "D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used"
W2_30 = "W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape"
W1_14 = "W1_14_weather_cells_for_household_heat_load"
N_RESAMPLES = 2000
WINTER = (11, 12, 1, 2, 3)


def _read_type(bill: dict, read: dict) -> str:
    basis = bill.get("billing_basis")
    if basis == "estimated":
        return "estimated"
    if basis == "prepayment_meter":
        return "prepayment_" + ("actual" if read["status"] == "actual" else "estimated")
    return "smart" if bill.get("meter_type") == "smart" else "actual"


def _clustered(per_account: list, substream: str):
    """Mean over all items with an account-clustered bootstrap 95% interval."""
    s = np.array([a.sum() for a in per_account])
    n = np.array([a.size for a in per_account])
    rng = np.random.default_rng(_substream_seed(substream))
    boots = []
    for _ in range(N_RESAMPLES):
        i = rng.integers(0, s.size, s.size)
        boots.append(s[i].sum() / n[i].sum())
    boots.sort()
    return float(s.sum() / n.sum()), [round(float(boots[int(0.025 * N_RESAMPLES)]), 4),
                                      round(float(boots[int(0.975 * N_RESAMPLES) - 1]), 4)]


def _ratio_ci(num: list, den: list, substream: str):
    """sum(num)/sum(den) with an account-clustered bootstrap 95% interval."""
    a = np.array([x.sum() for x in num])
    b = np.array([x.sum() for x in den])
    rng = np.random.default_rng(_substream_seed(substream))
    boots = []
    for _ in range(N_RESAMPLES):
        i = rng.integers(0, a.size, a.size)
        if b[i].sum() > 0:
            boots.append(a[i].sum() / b[i].sum())
    boots.sort()
    return float(a.sum() / b.sum()), [round(float(boots[int(0.025 * len(boots))]), 4),
                                      round(float(boots[int(0.975 * len(boots)) - 1]), 4)]


def _joined(book: dict):
    reads = {(r["customer_id"], r["period_end"]): r for r in book["meter_read_log"]}
    for b in book["bills"]:
        r = reads.get((b["customer_id"], b["period_end"]))
        if r is None or r.get("true_consumption_kwh") is None:
            continue
        yield b, r


def read_type_split(book: dict) -> dict:
    groups: dict = defaultdict(lambda: defaultdict(list))
    for b, r in _joined(book):
        d = b["total_consumption_kwh"] - r["true_consumption_kwh"]
        season = "winter" if int(b["period_end"][5:7]) in WINTER else "summer"
        rt = _read_type(b, r)
        for key in (rt, f"{rt}|{b['commodity']}", f"{rt}|{b['commodity']}|{season}"):
            groups[key][b["customer_id"]].append(d)
    out = {}
    for key in sorted(groups):
        accs = [np.array(v) for v in groups[key].values()]
        mae, mae_ci = _clustered([np.abs(a) for a in accs], f"D48_rt_abs_{key}")
        bias, bias_ci = _clustered(accs, f"D48_rt_signed_{key}")
        out[key] = {"n_account_months": int(sum(a.size for a in accs)), "n_accounts": len(accs),
                    "mean_abs_kwh": round(mae, 2), "mean_abs_ci95": mae_ci,
                    "mean_signed_kwh": round(bias, 2), "mean_signed_ci95": bias_ci}
    return out


def annual_billed_vs_metered(book: dict) -> dict:
    yr: dict = defaultdict(lambda: [0.0, 0.0])
    for b, r in _joined(book):
        k = f"{b['period_end'][:4]}|{b['commodity']}"
        yr[k][0] += b["total_consumption_kwh"]
        yr[k][1] += r["true_consumption_kwh"]
    return {k: {"billed_kwh": round(v[0], 1), "metered_kwh": round(v[1], 1),
                "billed_over_metered_pct": round((v[0] - v[1]) / v[1] * 100, 2)}
            for k, v in sorted(yr.items())}


def _company_weight(fuel: str, profile_class, start: date, end: date) -> float:
    if fuel == "electricity" and profile_class == 2:
        return sum(register_profile_weight(reg, start, end) for reg in ECONOMY_7_REGISTERS)
    return profile_weight(fuel, start, end)


def shape_rows(book: dict) -> list:
    """(account, fuel, month, year, truth_share, belief_share, flat_share) for account-years with
    twelve monthly bills inside one calendar year and positive metered use."""
    by_year: dict = defaultdict(list)
    for b, r in _joined(book):
        s, e = date.fromisoformat(b["period_start"]), date.fromisoformat(b["period_end"])
        if (s.year, s.month) != (e.year, e.month) or s.day != 1:
            continue
        by_year[(b["customer_id"], b["commodity"], e.year)].append((e.month, s, e, b, r))
    rows = []
    for (acct, fuel, yr), months in by_year.items():
        if len({m for m, *_ in months}) != 12 or len(months) != 12:
            continue
        true = np.array([r["true_consumption_kwh"] for *_, r in months])
        if true.sum() <= 0:
            continue
        belief = np.array([_company_weight(fuel, b.get("profile_class"), s, e)
                           for _, s, e, b, _ in months])
        flat = np.array([(e - s).days + 1 for _, s, e, _, _ in months], dtype=float)
        for i, (m, *_rest) in enumerate(months):
            rows.append((acct, fuel, m, yr, true[i] / true.sum(), belief[i] / belief.sum(),
                         flat[i] / flat.sum()))
    return rows


def shape_gap(rows: list, label: str) -> dict:
    num, den = defaultdict(list), defaultdict(list)
    signed = defaultdict(lambda: defaultdict(list))
    for acct, fuel, m, _yr, t, b, f in rows:
        num[acct].append(abs(b - t))
        den[acct].append(abs(f - t))
        signed["winter" if m in WINTER else "summer"][acct].append(b - t)
    accts = sorted(num)
    gap, ci = _ratio_ci([np.array(num[a]) for a in accts], [np.array(den[a]) for a in accts],
                        f"W2_30_D48_{label}")
    out = {"gap": round(gap, 4), "gap_ci95": ci, "n_account_months": len(rows),
           "n_accounts": len(accts), "n_account_years": len(rows) // 12,
           "mae_belief_share": round(sum(map(sum, num.values())) / len(rows), 5),
           "mae_flat_share": round(sum(map(sum, den.values())) / len(rows), 5)}
    for season, per in signed.items():
        mean, sci = _clustered([np.array(v) for v in per.values()], f"W2_30_D48_{label}_{season}")
        out[f"belief_minus_truth_share_{season}"] = round(mean, 5)
        out[f"belief_minus_truth_share_{season}_ci95"] = sci
    return out


def year_specific_share(rows: list) -> dict:
    """Mean |share - the account's own mean share for that calendar month| over account-months whose
    account has at least two years of that month: the part of the true shape no seasonal-normal
    estimate can know."""
    cell = defaultdict(list)
    for acct, fuel, m, _yr, t, *_ in rows:
        cell[(acct, fuel, m)].append(t)
    out = {}
    for fuel in ("electricity", "gas"):
        dev = defaultdict(list)
        for (acct, f, _m), ts in cell.items():
            if f == fuel and len(ts) >= 2:
                mu = sum(ts) / len(ts)
                dev[acct].extend(abs(t - mu) for t in ts)
        if dev:
            mean, ci = _clustered([np.array(v) for v in dev.values()], f"W1_14_D48_{fuel}")
            out[fuel] = {"mean_abs_share_deviation": round(mean, 5), "ci95": ci,
                         "n_account_months": sum(map(len, dev.values())), "n_accounts": len(dev)}
    return out


def measure(book: dict):
    rows = shape_rows(book)
    by_fuel = {fuel: shape_gap([r for r in rows if r[1] == fuel], fuel)
               for fuel in ("electricity", "gas")}
    pooled = shape_gap(rows, "all")
    split = read_type_split(book)
    commit = (book.get("producing_commit") or {}).get("commit")
    w2_30 = _normalise(
        pooled["mae_belief_share"], pooled["mae_flat_share"],
        ("no-skill = each month's share of the account-year by days (flat pro-rata, the estimator's "
         f"own named control); MAE_noskill={pooled['mae_flat_share']:.5f} of annual use per month"),
        "prediction",
        components={
            "definition": ("per account-year with twelve monthly bills: truth = each month's share of "
                           "the year's metered use (grader side); belief = the published monthly "
                           "share the company estimates unread months on (PC1/EUC01B proxy; PC2 "
                           "registers summed for Economy 7); gap = sum|belief-truth| / "
                           "sum|flat-truth|. Shares, so the estimator's level error is excluded."),
            "pooled": pooled, "by_fuel": by_fuel,
            "billed_minus_metered_by_read_type": split,
            "annual_billed_vs_metered": annual_billed_vs_metered(book),
            "book_producing_commit": commit,
            "reads_with_it": ("the truth share includes each year's weather, so this grades the "
                              "company's seasonal-normal shape against the shape the world produced "
                              "in that year, not against a weather-normal truth"),
        },
        note=("how far the company's seasonal shape for an unread month sits from the household's "
              "metered year, against a supplier that spreads by days. Billing gaps sit only on "
              "estimated bills: actual, smart and prepayment reads bill what was metered."),
    )
    w1_14 = {
        "twin_atom_id": TWIN, "gap": None, "metric": "prediction", "raw_gap": None, "g0": None,
        "baseline": "none: the company holds no belief to grade",
        "normalisation": "", "normalisation_reason": "", "raw_gap_is": "",
        "components": {"year_specific_share_of_true_shape": year_specific_share(rows),
                       "book_producing_commit": commit},
        "note": ("UNDEFINED, not unmeasured: the company's unread-month estimate is seasonal normal "
                 "and 'holds no weather feed for billing' (company/billing/unread_month_estimate.py), "
                 "so there is no weather belief to set against the cell's weather and any ratio "
                 "would be 1.0 by construction. Measured instead: the year-specific part of the "
                 "true shape, the error a weather-blind estimate cannot avoid. Closes when the "
                 "company carries a weather-corrected estimate (a capability), then graded here."),
    }
    return w2_30, w1_14


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", required=True)
    ap.add_argument("--write-ledger", action="store_true")
    args = ap.parse_args()
    book = json.loads(Path(args.book).read_text(encoding="utf-8"))
    w2_30, w1_14 = measure(book)
    c = w2_30.components
    print(json.dumps({"W2_30_gap": w2_30.gap, "pooled": c["pooled"], "by_fuel": c["by_fuel"],
                      "W1_14": w1_14["components"]}, indent=1))
    for key in ("actual", "smart", "estimated", "prepayment_actual", "prepayment_estimated"):
        print(key, c["billed_minus_metered_by_read_type"].get(key))
    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        write_gap_entry(W2_30, TWIN, w2_30, measured_at=measured_at, run_git_commit=commit)
        guard_live_ledger_write(GAP_LEDGER_PATH, writer="couple_d48_billing_gap")
        ledger = json.loads(GAP_LEDGER_PATH.read_text(encoding="utf-8"))
        ledger[W1_14] = dict(w1_14, measured_at=measured_at, run_git_commit=commit)
        GAP_LEDGER_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n",
                                   encoding="utf-8")
        print(f"ledger written: {W2_30} gap={w2_30.gap:.4f}; {W1_14} gap None (named reason)")


if __name__ == "__main__":
    main()
