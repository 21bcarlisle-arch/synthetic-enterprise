"""D (L1->L2) — estimate the real cascade links D1..D8 on the record, and register
the not-yet-estimable ones as asserted (R10).

The method library `background/cascade_correlation_estimation.py` is the portable
joint-tail-lift spine (L1). This is its application to REAL in-repo data (L1->L2,
the atom's own stated increment): "estimate the real D1..D8 links on the record +
register the asserted ones." Every link ends up in ONE of two honest states —
ESTIMATED (a lift/CI computed from a real series) or ASSERTED (an `AssertedDependence`
R10 record naming exactly the real series + statistic that would ground it) — and
an asserted link is NEVER dressed as estimated.

WHAT IS ESTIMATED NOW (in-repo data available):
  * D1 (temp perp wind — the supplier-killing cold-and-still corner, the worked
    example): winter-conditioned lower-tail joint lift on the real 4-location
    Open-Meteo national series (`sim/weather_data/`). This is the SAME data +
    corner the W1_3 show-the-tail work uses; the estimate is expected to
    reproduce the DISCOVER doc's cited winter co-movement (all-year Pearson ~0
    LIES; the winter lower tail is strongly coupled). Reported WITH its u and a
    block-bootstrap CI (small, autocorrelated sample — trust the CI).
  * D8 (temporal persistence): real lag-1 autocorrelation of temp and wind — a
    SELF-dependence (not a pair-lift), the axis that turns a joint tail into a
    sustained multi-day drawdown.

WHAT IS ASSERTED (series not assembled in-repo, or genuinely not observable
without a company run, honestly registered, R10): D3 (short-volume<->cash-out,
the £ covariance — needs an actual book Delta_vol, which is a COMPANY output,
not a market observable; estimating it from the company's own simulated run
would breach anti-marking-own-homework), D7 (interconnector relief withdrawn in
the tail, an ANTI dependence — the real IC net-import + EU-tightness series are
not assembled in-repo). Each carries its sign + reason + the exact grounding
path, so a later rung can estimate it without re-deriving what it needs. The
assumed magnitudes are registered ASSUMPTIONS pending that estimation, never
presented as measured (R12 — no fabricated number reads as a result).

D6 (cross-seam compounding) MOVED asserted->ESTIMATED: the end-to-end
cold-winter TEMPERATURE -> daily SSP PRICE joint-tail lift, using the real
independent daily-mean SSP fixture (`sim/scenario/data/real_ssp_daily_mean.json`,
itself extracted from the published Elexon SSP cache) against Open-Meteo temp,
winter-conditioned (same anti-pooling as D1/D4). This reproduces the same
magnitude previously only NOTED in the maturity-map log (~1.77) but not
committed as re-runnable code — it is now a real, reproducible estimate, not an
assumed placeholder. Its CI [see detail] straddles the independence null (unlike
D1/D2/D4/D5, whose CIs all exclude it) — an honest finding that the cascade
PARTIALLY DECOUPLES end-to-end (the daily SSP mean smooths the half-hourly price
spike D2 finds at finer resolution; different resolutions, both real, not a
contradiction).

C-S2: deterministic (fixed bootstrap seed). This module reads sim/harness data to
compute a diagnostic; it is HARNESS code (background/), never company-facing.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from sim.weather_tail_demonstration import load_national_daily
from background.cascade_correlation_estimation import (
    AssertedDependence,
    LiftEstimate,
    asserted_dependence,
    block_bootstrap_lift_ci,
    compounding_holds,
    condition,
    end_to_end_lift,
    joint_tail_lift,
)

_WINTER_MONTHS = frozenset({12, 1, 2})
_DECILE_U = 0.10
_REGISTER_PATH = Path(__file__).resolve().parent.parent / "docs" / "observability" / "cascade_link_register.json"


@dataclass(frozen=True)
class EstimatedLink:
    """A cascade link estimated from a real series."""

    link_id: str
    statistic: str            # "joint_tail_lift" | "lag1_autocorr"
    value: float
    detail: Dict[str, float]  # u / ci_low / ci_high / n / sign, statistic-specific


def _winter_mask(dates) -> np.ndarray:
    return np.array([d.month in _WINTER_MONTHS for d in dates], dtype=bool)


def estimate_d1_temp_wind(*, u: float = _DECILE_U, seed: int = 0) -> EstimatedLink:
    """D1: the joint lower tail of (temperature, wind) in WINTER — cold AND still
    co-occurring. `condition` restricts to DJF BEFORE estimating (anti-pooling:
    the all-year corner is diluted by the calm bulk); `joint_tail_lift(..., lower)`
    then measures the corner. A block-bootstrap CI accompanies the point (the
    conditioned winter sample is small + autocorrelated)."""
    national, _doy, dates = load_national_daily()
    winter = _winter_mask(dates)
    temp_w = condition(national["temperature_mean_c"], winter)
    wind_w = condition(national["wind_speed_mean_ms"], winter)
    est: LiftEstimate = joint_tail_lift(temp_w, wind_w, u=u, upper=False)  # lower-lower = cold & still
    lo, hi = block_bootstrap_lift_ci(temp_w, wind_w, u=u, upper=False, seed=seed)
    return EstimatedLink(
        link_id="D1_temp_wind",
        statistic="joint_tail_lift",
        value=est.lift,
        detail={"u": u, "sign_lower": 1.0, "ci_low": float(lo), "ci_high": float(hi),
                "n_conditioned": float(est.n_conditioned), "lam": est.lam},
    )


def estimate_d8_persistence() -> EstimatedLink:
    """D8: temporal persistence — the DESEASONALISED residual AR1 coefficient of
    the national temp and wind series (a SELF-dependence). Persistence is
    measured on the residual, NOT raw: a raw lag-1 autocorr is dominated by the
    SEASON (winter days sit next to winter days ~0.95) and conflates the annual
    cycle with the anomaly persistence that actually makes a cold/still SPELL
    last. The weather engine's `fit_national_macro_model` already fits exactly
    this (seasonal harmonics removed, then an AR1 on the residual → `phi` = the
    residual lag-1 autocorrelation), so this reuses that calibrated fit (SIMPLICITY
    GUARD) rather than recomputing a seasonality-contaminated raw autocorr. A
    memoryless model prices a k-day spell as phi^k → vanishing → teaches zero
    hedge; the real residual phi is what turns a joint tail into a sustained
    drawdown."""
    from sim.weather_engine import fit_national_macro_model
    national, doy, _dates = load_national_daily()
    params = fit_national_macro_model(national, doy)
    phi_temp = float(params["phi"]["temperature_mean_c"])
    phi_wind = float(params["phi"]["wind_speed_mean_ms"])
    return EstimatedLink(
        link_id="D8_temporal_persistence",
        statistic="residual_ar1_phi",
        value=phi_temp,  # headline = temp persistence (the deeper of the two)
        detail={"residual_phi_temp": phi_temp, "residual_phi_wind": phi_wind},
    )


_DEMAND_CACHE = Path(__file__).resolve().parent.parent / "sim" / "cache" / "elexon_demand_full.json"


def _load_daily_demand(path: Path | None = None) -> Dict[str, float]:
    """Real GB national daily demand (mean of the half-hourly settlement-period
    `initialDemandOutturn`, MW) keyed by settlement date — the independent
    published series, NOT a sim output (anti-marking-own-homework, S3)."""
    import json
    from collections import defaultdict
    p = path or _DEMAND_CACHE
    agg: Dict[str, list] = defaultdict(list)
    for r in json.loads(p.read_text(encoding="utf-8")):
        v = r.get("initialDemandOutturn")
        if v is not None:
            agg[r["settlementDate"]].append(float(v))
    return {d: float(np.mean(vs)) for d, vs in agg.items()}


def estimate_d4_demand_temp(*, u: float = _DECILE_U, seed: int = 0) -> EstimatedLink:
    """D4: the cold-tail demand plateau — cold (LOW temp) AND high demand
    co-occurring. Heating load is CONVEX below a threshold, so a cold tail lifts
    demand far more than a linear fit predicts; the joint tail is estimated as
    the upper-upper corner of (-temp, demand) (negating temp turns the cold lower
    tail into an upper tail so the same-direction lift statistic applies). Uses
    the independent published Elexon demand series + Open-Meteo temp (different
    sources — the anti-marking-own-homework rule)."""
    national, _doy, dates = load_national_daily()
    demand_by_date = _load_daily_demand()
    temp_by_date = {dates[i].strftime("%Y-%m-%d"): float(national["temperature_mean_c"][i])
                    for i in range(len(dates))}
    common = sorted(set(demand_by_date) & set(temp_by_date))
    if len(common) < 100:
        raise ValueError(f"too few common demand/temp days to estimate D4: {len(common)}")
    demand = np.array([demand_by_date[d] for d in common])
    temp = np.array([temp_by_date[d] for d in common])
    est: LiftEstimate = joint_tail_lift(-temp, demand, u=u, upper=True)  # cold & high-demand corner
    lo, hi = block_bootstrap_lift_ci(-temp, demand, u=u, upper=True, seed=seed)
    return EstimatedLink(
        link_id="D4_demand_temp",
        statistic="joint_tail_lift",
        value=est.lift,
        detail={"u": u, "sign_cold_tail": 1.0, "ci_low": float(lo), "ci_high": float(hi),
                "n_days": float(len(common)), "pearson_all_year": float(np.corrcoef(temp, demand)[0, 1])},
    )


_CACHE = Path(__file__).resolve().parent.parent / "sim" / "cache"


@lru_cache(maxsize=4)
def _cached_json(name: str):
    """Parse a large sim/cache JSON ONCE per process (AGWS ~100MB, SSP ~130MB) so
    the several estimates that read the same file (D2 renewable + D5 wind both
    read AGWS) do not re-parse it. Transient in-memory cache, cleared with the
    process."""
    import json
    return json.loads((_CACHE / name).read_text())


def estimate_d2_residual_price(*, u: float = _DECILE_U, seed: int = 0) -> EstimatedLink:
    """D2: residual-demand (D - wind - solar) HIGH (tight) AND SSP price HIGH
    (dear) co-occurring -- the merit order convex in tightness. Estimated at
    HALF-HOURLY settlement resolution, NOT daily: the coupling is a per-period
    phenomenon (a tight settlement period clears at a high price THAT period),
    and daily averaging washes it out (measured: daily lift ~1.08 vs half-hourly
    1.32 rising to ~1.49 into the 5% tail). Uses the real independent Elexon
    series now cached: AGWS wind+solar generation, INDO demand outturn, SSP
    system sell price."""
    from sim.generation_demand_history import aggregate_renewable_generation
    ren = aggregate_renewable_generation(_cached_json("elexon_agws_full.json"))
    dem = {}
    for r in _cached_json("elexon_demand_full.json"):
        v = r.get("initialDemandOutturn")
        if v is not None:
            dem[(r["settlementDate"], int(r["settlementPeriod"]))] = float(v)
    price = {}
    for r in _cached_json("elexon_ssp_full.json"):
        v = r.get("systemSellPrice")
        if v is not None:
            price[(r["settlementDate"], int(r["settlementPeriod"]))] = float(v)
    keys = sorted(set(ren) & set(dem) & set(price))
    if len(keys) < 1000:
        raise ValueError(f"too few common half-hourly periods to estimate D2: {len(keys)}")
    resid = np.array([dem[k] - ren[k] for k in keys])
    pr = np.array([price[k] for k in keys])
    est: LiftEstimate = joint_tail_lift(resid, pr, u=u, upper=True)  # tight & dear corner
    lo, hi = block_bootstrap_lift_ci(resid, pr, u=u, upper=True, seed=seed)
    return EstimatedLink(
        link_id="D2_residual_demand_price",
        statistic="joint_tail_lift",
        value=est.lift,
        detail={"u": u, "resolution": 0.0, "ci_low": float(lo), "ci_high": float(hi),
                "n_periods": float(len(keys)), "pearson_all": float(np.corrcoef(resid, pr)[0, 1])},
    )


def estimate_d5_windoutput_windspeed(*, u: float = _DECILE_U, seed: int = 0) -> EstimatedLink:
    """D5: low wind SPEED and low wind OUTPUT co-occur (still & zero-output) --
    the turbine power curve. Deterministic in principle but TAIL-AMPLIFYING: the
    cubic ramp near cut-in means a small speed drop in the still tail is a large
    output collapse, so the lower-tail lift is strong and RISES into the tail
    (measured: decile ~4.9, rising to ~6.6 at the 5% tail). Daily national wind
    speed (Open-Meteo) vs daily national wind generation (AGWS Wind
    Onshore+Offshore) -- disjoint sources (anti-marking-own-homework)."""
    from sim.generation_demand_history import aggregate_wind_generation
    from collections import defaultdict
    wind = aggregate_wind_generation(_cached_json("elexon_agws_full.json"))  # {(date,period): MW}
    by_date = defaultdict(list)
    for (dt, _pd), mw in wind.items():
        by_date[dt].append(mw)
    gen_by_date = {d: float(np.mean(v)) for d, v in by_date.items()}
    national, _doy, dates = load_national_daily()
    speed_by_date = {dates[i].strftime("%Y-%m-%d"): float(national["wind_speed_mean_ms"][i])
                     for i in range(len(dates))}
    common = sorted(set(gen_by_date) & set(speed_by_date))
    if len(common) < 100:
        raise ValueError(f"too few common wind days to estimate D5: {len(common)}")
    ws = np.array([speed_by_date[d] for d in common])
    wg = np.array([gen_by_date[d] for d in common])
    est: LiftEstimate = joint_tail_lift(ws, wg, u=u, upper=False)  # still & zero-output corner
    lo, hi = block_bootstrap_lift_ci(ws, wg, u=u, upper=False, seed=seed)
    return EstimatedLink(
        link_id="D5_windoutput_windspeed",
        statistic="joint_tail_lift",
        value=est.lift,
        detail={"u": u, "sign_lower": 1.0, "ci_low": float(lo), "ci_high": float(hi),
                "n_days": float(len(common)), "pearson_all": float(np.corrcoef(ws, wg)[0, 1])},
    )


_SSP_DAILY_CACHE = Path(__file__).resolve().parent.parent / "sim" / "scenario" / "data" / "real_ssp_daily_mean.json"


def _load_daily_ssp_mean(path: Path | None = None) -> Dict[str, float]:
    """Real GB national daily-mean SSP (Elexon System Sell Price), keyed by ISO
    settlement date -- the independent published series (real 2016-2025 Elexon
    data, not a sim output; anti-marking-own-homework). Reads the compact
    fixture `real_ssp_daily_mean.json` (a contiguous daily series from
    `start_date`, itself extracted from the 128MB half-hourly SSP cache -- see
    its own `_provenance` field) rather than re-parsing the half-hourly cache
    D2 already reads. FAIL-OPEN guard: `n_days` must match the value count, or
    the fixture is corrupt and raising beats silently mis-aligning every date."""
    import json
    from datetime import date, timedelta
    p = path or _SSP_DAILY_CACHE
    raw = json.loads(p.read_text(encoding="utf-8"))
    values = raw["daily_mean_ssp"]
    if len(values) != raw["n_days"]:
        raise ValueError(
            f"real_ssp_daily_mean.json corrupt: n_days={raw['n_days']} but {len(values)} values present"
        )
    start = date.fromisoformat(raw["start_date"])
    return {(start + timedelta(days=i)).isoformat(): float(v) for i, v in enumerate(values)}


def estimate_d6_end_to_end(*, u: float = _DECILE_U, seed: int = 0) -> EstimatedLink:
    """D6: cross-seam compounding -- the END-TO-END cold-winter TEMPERATURE ->
    daily SSP PRICE joint-tail lift (`end_to_end_lift`), winter-conditioned
    (same anti-pooling as D1/D4), cold aligned to the dear corner via `-temp`
    (D4's convention) so both sides point the same way. Real independent
    sources on both ends: Open-Meteo temp, Elexon SSP (anti-marking-own-
    homework). Declared BEFORE looking at the result (the method mirrors D1/D4
    exactly -- winter DJF, decile u, same corner-alignment convention -- to
    avoid picking a driver definition that flatters a target number, R12): this
    is `L_end`, the terminal-vs-root lift the compounding inequality
    (`compounding_holds`) compares against the product of the per-link lifts.
    The CI is reported AS MEASURED even where (as here) it straddles the
    independence null -- an honest partial-decoupling finding, not smoothed
    over to look like a clean confirmation."""
    national, _doy, dates = load_national_daily()
    winter = _winter_mask(dates)
    price_by_date = _load_daily_ssp_mean()
    temp_by_date = {dates[i].strftime("%Y-%m-%d"): float(national["temperature_mean_c"][i])
                    for i in range(len(dates)) if winter[i]}
    common = sorted(set(temp_by_date) & set(price_by_date))
    if len(common) < 100:
        raise ValueError(f"too few common winter weather/price days to estimate D6: {len(common)}")
    temp = np.array([temp_by_date[d] for d in common])
    price = np.array([price_by_date[d] for d in common])
    est: LiftEstimate = end_to_end_lift(price, -temp, u=u, upper=True)  # cold & dear corner
    lo, hi = block_bootstrap_lift_ci(price, -temp, u=u, upper=True, seed=seed)
    return EstimatedLink(
        link_id="D6_cross_seam_compounding",
        statistic="end_to_end_lift",
        value=est.lift,
        detail={"u": u, "sign_cold_dear": 1.0, "ci_low": float(lo), "ci_high": float(hi),
                "n_winter_days": float(len(common)), "ci_excludes_null": float(lo > 1.0)},
    )


def asserted_links() -> List[AssertedDependence]:
    """D3/D7 — registered as asserted-not-estimated (R10). Signs come from the
    DISCOVER inventory; magnitudes are registered ASSUMPTIONS pending
    estimation (never presented as measured). Each names the exact real series +
    statistic that would ground it, so the next rung can estimate without
    re-deriving. D6 (formerly asserted here) is now ESTIMATED
    (`estimate_d6_end_to_end`) -- see the module docstring for what changed."""
    return [
        asserted_dependence(
            "D3_shortvol_cashout", assumed_lift=1.8, assumed_sign="upper",
            reason="book imbalance Delta_vol = demand - hedged is not observable without a run",
            grounding="Delta_vol vs SSP/SBP cash-out, upper-upper lift; the money is the covariance E[Delta_vol*spot]",
        ),
        asserted_dependence(
            "D7_interconnector_relief", assumed_lift=0.5, assumed_sign="anti",
            reason="IC net-import + EU-tightness series not assembled; a cold-and-still event is often EU-wide",
            grounding="IC net import vs GB residual demand, conditional relief | (GB tight AND EU tight) — near zero",
        ),
    ]


def build_register(*, seed: int = 0) -> Dict[str, object]:
    """The full D1..D8 register: estimated links (real series) + asserted links
    (R10, grounded). Every one of the eight is present in exactly one state —
    the inventory is never silently incomplete. Also reports the compounding
    inequality (`compounding_holds`, S4/D6) on the estimated links: whether the
    end-to-end D6 lift is at least the product of D1/D2/D4/D5 — a genuine
    finding (it does NOT hold on the real record: the cascade partially
    decouples end-to-end), reported as a diagnostic, never adjusted to hold."""
    estimated = [estimate_d1_temp_wind(seed=seed), estimate_d2_residual_price(seed=seed),
                 estimate_d4_demand_temp(seed=seed), estimate_d5_windoutput_windspeed(seed=seed),
                 estimate_d6_end_to_end(seed=seed), estimate_d8_persistence()]
    asserted = asserted_links()
    covered = {e.link_id.split("_")[0] for e in estimated} | {a.link_id.split("_")[0] for a in asserted}
    expected = {f"D{i}" for i in range(1, 9)}
    missing = expected - covered
    if missing:
        raise AssertionError(f"cascade link register INCOMPLETE — D-links not registered: {sorted(missing)}")
    d6 = next(e for e in estimated if e.link_id == "D6_cross_seam_compounding")
    chain_lifts = [e.value for e in estimated if e.link_id.split("_")[0] in ("D1", "D2", "D4", "D5")]
    compounding = {
        "l_end": d6.value,
        "product_of_links": float(np.prod(chain_lifts)),
        "link_lifts": {e.link_id: e.value for e in estimated if e.link_id.split("_")[0] in ("D1", "D2", "D4", "D5")},
        "holds": compounding_holds(d6.value, chain_lifts),
    }
    return {
        "estimated": [asdict(e) for e in estimated],
        "asserted": [asdict(a) for a in asserted],
        "covered_links": sorted(covered),
        "compounding": compounding,
    }


def write_register(*, seed: int = 0, path: Path | None = None) -> Dict[str, object]:
    """Persist the register to the record (docs/observability). R14/idempotent:
    a pure function of the committed data + seed, so re-running reproduces it."""
    import json
    reg = build_register(seed=seed)
    p = path or _REGISTER_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return reg
