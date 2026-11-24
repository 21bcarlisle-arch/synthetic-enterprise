**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: grading the weather-to-price chain on the 2016-2025 record, by regime (2026-11-24)

Written by the worker tick on 24 Nov 2026, before any run of the probe below. It answers the
director's steer of 24 Nov,
`docs/staging/advisor/DIRECTOR_STEER_GRADE_THE_WEATHER_TO_PRICE_CHAIN_ON_THE_RECORD_NOW_SO_FORWARD_YEARS_ARE_NOT_HELD_BY_IT_2026-11-24.md`,
items 1 and 2. This grades the chain on the record; it is not a forward run, so it is allowed
before the exit test (`docs/design/FORWARD_YEARS_RECOMMENDATION_2026-10-24.md` §8).

The subject is `sim/weather_price_chain.derive_price_on_record()`, the default path that the
forward-years design (§3) composes. The year-aware variant (W1_7) is reported beside it and decides
nothing.

The real side is the cached published Elexon SSP and the NBP gas series the chain is already fit to.

## The question, said before it is measured

The question: can forward years form price from this chain and have hedging and pricing judged on
it? A hedge book and a supplier's cost of supply are bought and judged at the month and season. So
the deciding scales are the demand-weighted monthly and quarterly mean prices, not the daily MAE.

The steer's frame then asks for three more checks: volatility at every scale, weather and price
moving together, and spells that last.

**Regimes**, fixed here by date and not chosen from any result:
- pre-crisis: 1 Jan 2016 to 30 Jun 2021;
- crisis: 1 Jul 2021 to 30 Jun 2023;
- post-crisis: 1 Jul 2023 to the end of the record.

## The acceptance bands

**Why no absolute band.** An absolute £ or % band would be a number picked to fill a slot.
Nothing in the knowledge layer establishes what monthly price error is tolerable for a
supplier's world. That is a **GAP**. So the bands are of two kinds, and neither is picked.

1. **Against a null (P1 monthly, P2 quarterly).** In each regime, the chain's median absolute
   percentage error on demand-weighted monthly (P1) and quarterly (P2) mean price must be lower
   than that of a gas-only null. The null is OLS of daily SSP on the NBP price, fit in-sample over
   the whole record, as the chain is. A chain that cannot beat price-follows-gas at the scale a
   hedge sees adds no value at that scale, whatever its weather coupling does elsewhere.
2. **Against the record's own sampling band.** For each statistic below, the chain's value must sit
   inside the 5th-95th percentile of the same statistic on real prices. That band comes from a
   month-block bootstrap within the regime: 1,000 draws for daily statistics and 300 for
   half-hourly, seed 20261124. The 90% level is a convention, stated as such.
   - Volatility: the standard deviation of daily, weekly, monthly and quarterly mean price. Daily
     1st and 99th percentiles. Half-hourly 0.1th and 99.9th percentiles, and the mean within-day
     standard deviation. The chain's half-hours come from `sim/scenario/intraday_shape.shape_day`,
     seed "grade-2026-11-24".
   - Weather and price together: the cold-and-still premium, using the chain's own
     `cold_still_tail_mask`, applied identically to both series. Also the correlation of the
     daily price anomaly with the temperature anomaly and with the wind-speed anomaly. An anomaly
     is the value minus its calendar-month mean.
   - Spells: lag-1 and lag-7 autocorrelation of the daily price anomaly, over pairs of days that
     fall in the same month.

**Verdict rule.** The chain is **fit for forward years on hedging and pricing** only if P1 and P2
pass in all three regimes and every volatility and coupling statistic passes in at least the
pre-crisis and post-crisis regimes. The crisis was a gas shock that a forward draw reproduces only
through its gas path.

If the chain fails, its errors are published beside every forward figure, as the §3 "known error",
until the largest cause is fixed (steer item 3).

**Cause diagnostics, recorded with the run:**
- daily error by gas-price quintile and by residual-demand quintile;
- error by year, which points at fleet change;
- default against year-aware, which isolates the fleet effect.

The steer's other candidates, interconnectors and outages, are not in the chain at all. If neither
gas nor residual demand nor year explains the error, they are the remainder.

## Predictions, filed before the run

- **P1 and P2:** the chain beats the null before and after the crisis, and **loses to it in the
  crisis**. In the crisis, price was gas, and the engine's convex scarcity tail mis-scales at
  £200+/MWh gas.
- **Daily volatility:** FAIL-low before and after the crisis. A degree-day demand and a
  mean-matched fleet under-disperse.
- **Cold-and-still premium:** FAIL-high before and after the crisis. The chain's whole-record
  ratio is 2.2x, and I expect the real ratio under the same mask to be nearer 1.3-1.6x.
- **Lag-1 autocorrelation:** FAIL-low. Real persistence also carries outages and gas, which the
  chain lacks.
- **Half-hourly 99.9th percentile:** FAIL-low, at least in the crisis. Real scarcity spikes exceed
  the intraday shape's capped lognormal.
- **Largest cause, if it fails:** the error concentrates in the top gas quintile, meaning the gas
  floor and the residual-to-price mapping at high gas, not the fleet.

## The probe

Run from the repo root, outside the repository's code roots. It is kept here so the run can be
repeated exactly.

```python
"""Grade sim/weather_price_chain on the 2016-2025 record, by regime (pre-registered 2026-11-24).
Run from the repo root: python3 /path/to/probe_chain_grade.py > result.json"""
import datetime as dt
import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, ".")
from sim.weather_price_chain import (_CACHE, cold_still_tail_mask, derive_price_on_record,  # noqa: E402
                                     load_daily_record)
from sim.scenario.intraday_shape import shape_day  # noqa: E402

REGIMES = {"pre": ("2016-01-01", "2021-06-30"), "crisis": ("2021-07-01", "2023-06-30"),
           "post": ("2023-07-01", "2099-12-31")}
B, B_HH, SEED, HH_SEED = 1000, 300, 20261124, "grade-2026-11-24"


def keys(dates, scale):
    if scale == "daily":
        return dates
    if scale == "weekly":
        return np.array(["%d-W%02d" % dt.date.fromisoformat(d).isocalendar()[:2] for d in dates])
    if scale == "monthly":
        return np.array([d[:7] for d in dates])
    return np.array([f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}" for d in dates])


def group_mean(x, k, w=None):
    w = np.ones_like(x) if w is None else w
    s, n = defaultdict(float), defaultdict(float)
    for xi, ki, wi in zip(x, k, w):
        s[ki] += xi * wi
        n[ki] += wi
    ks = sorted(s)
    return np.array([s[q] / n[q] for q in ks])


def anomaly(x, month_keys):
    m = defaultdict(list)
    for xi, k in zip(x, month_keys):
        m[k].append(xi)
    mu = {k: np.mean(v) for k, v in m.items()}
    return np.array([xi - mu[k] for xi, k in zip(x, month_keys)])


def paired_corr(a, b, blocks, lag=0):
    """corr over pairs (a[i], b[i+lag]) whose two days sit in the same calendar month."""
    i = np.arange(len(a) - lag)
    same = blocks[i] == blocks[i + lag]
    return float(np.corrcoef(a[i[same]], b[i[same] + lag])[0, 1])


def stats(price, temp, wind, dem, tail, mkeys):
    out = {}
    for sc in ("daily", "weekly", "monthly", "quarterly"):
        g = group_mean(price, keys_cache[sc], dem if sc in ("monthly", "quarterly") else None)
        out[f"std_{sc}"] = float(np.std(g))
    out["p99_daily"] = float(np.percentile(price, 99))
    out["p01_daily"] = float(np.percentile(price, 1))
    out["cold_still_ratio"] = float(price[tail].mean() / price[~tail].mean()) if tail.any() else None
    an = anomaly(price, mkeys)
    out["acf1"] = paired_corr(an, an, mkeys, 1)
    out["acf7"] = paired_corr(an, an, mkeys, 7)
    out["corr_temp"] = paired_corr(an, anomaly(temp, mkeys), mkeys)
    out["corr_wind"] = paired_corr(an, anomaly(wind, mkeys), mkeys)
    return out


def errors(model, real, dem, dates):
    out = {}
    for sc in ("daily", "weekly", "monthly", "quarterly"):
        k = keys(dates, sc)
        w = dem if sc in ("monthly", "quarterly") else None
        gm, gr = group_mean(model, k, w), group_mean(real, k, w)
        out[f"mae_{sc}"] = float(np.mean(np.abs(gm - gr)))
        out[f"median_ape_{sc}"] = float(np.median(np.abs(gm - gr) / np.abs(gr)))
        out[f"bias_{sc}"] = float(np.mean(gm - gr))
    return out


rec = load_daily_record()
d0, d1 = derive_price_on_record(), derive_price_on_record(year_aware=True)
dates, real, gas = d0["dates"], d0["real_ssp"], d0["gas_price"]
temp, wind, dem = d0["temperature_c"], d0["wind_speed_ms"], rec["demand_mw"]
X = np.column_stack([np.ones(len(gas)), gas])
null = X @ np.linalg.lstsq(X, real, rcond=None)[0]
tail_all = cold_still_tail_mask(d0)

hh = defaultdict(dict)
for r in json.loads((_CACHE / "elexon_ssp_full.json").read_text()):
    if r.get("systemSellPrice") is not None:
        hh[r["settlementDate"]][int(r["settlementPeriod"])] = float(r["systemSellPrice"])

rng = np.random.default_rng(SEED)
report = {"n_days": int(len(dates)), "regimes": {}}
for name, (a, b) in REGIMES.items():
    m = (dates >= a) & (dates <= b)
    ds = dates[m]
    keys_cache = {sc: keys(ds, sc) for sc in ("daily", "weekly", "monthly", "quarterly")}
    mk = keys_cache["monthly"]
    args = (temp[m], wind[m], dem[m], tail_all[m], mk)
    real_s = stats(real[m], *args)
    chain_s = stats(d0["derived_price"][m], *args)
    year_s = stats(d1["derived_price"][m], *args)
    # month-block bootstrap of the REAL statistics: the record's own sampling band
    months = sorted(set(mk))
    idx_by_month = {q: np.where(mk == q)[0] for q in months}
    boot = defaultdict(list)
    for _ in range(B):
        pick = rng.choice(len(months), len(months), replace=True)
        idx = np.concatenate([idx_by_month[months[j]] for j in pick])
        blocks = np.concatenate([np.full(len(idx_by_month[months[j]]), n) for n, j in enumerate(pick)]).astype(str)
        sub_dates = ds[idx]
        keys_cache = {"daily": np.char.add(blocks, sub_dates.astype(str)), "weekly": np.char.add(blocks, keys(sub_dates, "weekly")),
                      "monthly": blocks, "quarterly": np.char.add(np.array([str(int(x) // 3) for x in blocks]), "")}
        s = stats(real[m][idx], temp[m][idx], wind[m][idx], dem[m][idx], tail_all[m][idx], blocks)
        for k, v in s.items():
            if v is not None and np.isfinite(v):
                boot[k].append(v)
    keys_cache = {sc: keys(ds, sc) for sc in ("daily", "weekly", "monthly", "quarterly")}
    band = {k: (float(np.percentile(v, 5)), float(np.percentile(v, 95))) for k, v in boot.items()}

    def verdict(s):
        o = {}
        for k, v in s.items():
            if v is None or k not in band:
                o[k] = "n/a"
            else:
                lo, hi = band[k]
                o[k] = "PASS" if lo <= v <= hi else ("FAIL-low" if v < lo else "FAIL-high")
        return o

    # half-hourly leg: real HH SSP against shape_day(chain daily)
    real_hh, chain_hh, real_wd, chain_wd, hh_days = [], [], [], [], []
    for d, p in zip(ds, d0["derived_price"][m]):
        if len(hh.get(d, {})) >= 46:
            rv = [hh[d][k] for k in sorted(hh[d])]
            cv = shape_day(float(p), d, HH_SEED)
            real_hh.append(rv), chain_hh.append(cv)
            real_wd.append(np.std(rv)), chain_wd.append(np.std(cv)), hh_days.append(d[:7])
    hh_days = np.array(hh_days)
    hh_stats = lambda arrs, wd: {"hh_p999": float(np.percentile(np.concatenate(arrs), 99.9)),  # noqa: E731
                                 "hh_p001": float(np.percentile(np.concatenate(arrs), 0.1)),
                                 "hh_within_day_std": float(np.mean(wd))}
    real_h, chain_h = hh_stats(real_hh, real_wd), hh_stats(chain_hh, chain_wd)
    hb = defaultdict(list)
    hm = sorted(set(hh_days))
    hidx = {q: np.where(hh_days == q)[0] for q in hm}
    for _ in range(B_HH):
        idx = np.concatenate([hidx[hm[j]] for j in rng.choice(len(hm), len(hm), replace=True)])
        for k, v in hh_stats([real_hh[i] for i in idx], [real_wd[i] for i in idx]).items():
            hb[k].append(v)
    hband = {k: (float(np.percentile(v, 5)), float(np.percentile(v, 95))) for k, v in hb.items()}
    hverdict = {k: ("PASS" if hband[k][0] <= v <= hband[k][1] else ("FAIL-low" if v < hband[k][0] else "FAIL-high"))
                for k, v in chain_h.items()}

    e_chain, e_null, e_year = errors(d0["derived_price"][m], real[m], dem[m], ds), errors(null[m], real[m], dem[m], ds), \
        errors(d1["derived_price"][m], real[m], dem[m], ds)
    # diagnostics: where the daily error sits, by gas-price and residual-demand quintile
    err = d0["derived_price"][m] - real[m]
    diag = {}
    for nm, v in (("gas", gas[m]), ("residual_mw", d0["residual_mw"][m])):
        qs = np.percentile(v, [20, 40, 60, 80])
        bins = np.digitize(v, qs)
        diag[nm] = [{"quintile": int(q + 1), "mean_err": float(err[bins == q].mean()),
                     "mae": float(np.abs(err[bins == q]).mean())} for q in range(5)]
    by_year = {y: float(np.mean(np.abs(err[np.char.startswith(ds.astype(str), y)])))
               for y in sorted({d[:4] for d in ds})}
    report["regimes"][name] = {
        "n_days": int(m.sum()), "real_mean": float(real[m].mean()), "chain_mean": float(d0["derived_price"][m].mean()),
        "errors": {"chain": e_chain, "gas_only_null": e_null, "chain_year_aware": e_year},
        "P1_monthly_beats_null": e_chain["median_ape_monthly"] < e_null["median_ape_monthly"],
        "P2_quarterly_beats_null": e_chain["median_ape_quarterly"] < e_null["median_ape_quarterly"],
        "real": real_s, "chain": chain_s, "chain_year_aware": year_s, "band_90": band,
        "verdict_chain": verdict(chain_s), "verdict_year_aware": verdict(year_s),
        "hh": {"n_days": len(real_hh), "real": real_h, "chain": chain_h, "band_90": hband, "verdict": hverdict},
        "diagnostics": {"by_quintile": diag, "mae_by_year": by_year},
    }
print(json.dumps(report, indent=1))
```
