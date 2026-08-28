"""EP13: THE PEER BOUND — what correlation the PUBLISHER's own forecast reaches on its own outturn.

REUSE: tools/ep13_peer_bound.py
CLASS: CUSTOM
INDEX: searched "peer", "bound", "ceiling", "oracle", "forecast", "persistence", "autocorrelation",
       "correlation", "within-day". The two nearest organs are `tools/ep13_input_ceiling.py` and
       `tools/ep13_embedded_generation_bound.py`, and this is DELIBERATELY NOT either of them.
       Both of those bound a MODEL CLASS by fitting something to the target; the fit is why they
       cost 85 minutes and why their treatments may never be published. This one fits NOTHING. It
       reads two series NESO already publishes side by side in the same cache and scores them
       against each other with the same `neso.compare_shapes`, which is why it runs in seconds.
       It is a separate file from `sim/neso_carbon_intensity.forecast_skill` for the opposite
       reason to the usual one: that function answers a CUSTOMER question (what fraction of an
       achievable within-day saving a forecast-led shift captures) and returns annual aggregates
       only, deliberately un-joinable back to a half hour. This answers an ATOM question on the
       atom's own axis, and it needs the reconstruction beside it, so it lives in tools/ with the
       other bounds rather than widening a sim module's surface.

WHY THIS EXISTS
---------------
`docs/design/maturity_map.yaml` has held EP13 at L2 through eight passes on ONE axis: correlation
against NESO's published series, 0.746 in 2024. Four candidate inputs have now been retired by
measuring their ceiling before building them — the biomass outage model, the merit-order
programme, the within-day axis via recalibration, and embedded generation. Every one of those
measurements came back NEGATIVE, and a programme that has heard "no headroom" four times in a row
has to ask a question it has never asked:

    IS THE TARGET REPRODUCIBLE AT ALL?

`ep13_input_ceiling` bounds the best function of THE MODEL'S OWN INPUTS. It cannot distinguish
"the information is not in these inputs" from "the information is not anywhere" — and those two
have opposite consequences for L3. The first says find a new input. The second says the axis is
measuring the counterparty's own noise and no build of any kind can move it.

The discriminator is free and it has been sitting in the cache the whole time. NESO publishes a
FORECAST on every half hour it publishes an outturn for. Score the publisher's own forecast
against the publisher's own outturn, on the same held-out half hours, with the same function, and
the answer is a fact about the TARGET rather than about us.

WHAT A PEER BOUND IS, AND THE TWO THINGS IT IS NOT
--------------------------------------------------
It is not an ORACLE bound. An oracle holds the true value of an input and bounds every model that
could be built on it; §10 and the embedded pass both used one. This holds no truth: it is another
party's ex-ante estimate, and it can be beaten.

It is not an INDEPENDENT bound either, and this is the caveat that governs how the number may be
read. NESO's "actual" is itself a MODEL — a metered fuel mix put through NESO's own factor table,
NESO's own embedded-generation estimate and NESO's own loss correction — and NESO's forecast is
built from the same three. A forecast that shares its target's methodology scores higher than an
outside modeller with the same physical knowledge would, because the common-mode part cancels. So
this is an OPTIMISTIC bound on what an outside reconstruction can reach.

The optimism is in the SAFE direction and that is the whole reason it is worth measuring. A LOW
peer number would have proved the axis exhausted and closed the atom's whole remaining programme.
A HIGH one proves only that the target is reproducible — it promises no build succeeds. As with
every ceiling on this atom, one direction is load-bearing and the other is not, and it is stated
here so that a later reader cannot take the high number as a promise.

THE PERSISTENCE LADDER, which is what makes the peer number READABLE
--------------------------------------------------------------------
A correlation of 0.97 against a smoothly varying series means nothing on its own, because carbon
intensity is heavily autocorrelated and "0.97" may be what a copy of half an hour ago scores. So
every run publishes a LADDER: the outturn itself, lagged 1, 2, 4 and 48 half hours, scored by the
same function on the same keys. Each rung is a model any reader can build, and together they price
the axis.

The ladder must BRACKET the peer — some rung above it, some rung below — or it has not located it.
A one-sided ladder is a containment check, and a containment check on a published range is
fail-open (it passes by being wide). `ladder_brackets_the_peer` is a verdict for that reason, and
`peer_equivalent_lag` reports where on the ladder the peer actually falls.

THE TAUTOLOGY GUARD, which is the first thing a reader should check
--------------------------------------------------------------------
If NESO's `forecast` field were back-filled from the outturn for settled half hours, this entire
measurement would be a series compared with itself and would report ~1.0 by construction — R15's
first killer, exactly. `peer_is_not_a_backfill` is therefore computed and published: the share of
half hours where forecast and actual are bit-identical, and the mean absolute difference in grams.
A copy scores 1.0 and 0 g. The measured values are 0.041 and 9.8 g.

BOTH SIDES ARE FILTERED BY THE SAME PHYSICAL CEILING. NESO's forecast field carries a handful of
readings that are not a grid (13,579 gCO2/kWh among them, found by `forecast_skill` in 2019), and
the outturn carries published zeroes. A filter applied to one side of a comparison measures the
filter, so both sides are refused together at
`neso_carbon_intensity._physical_ceiling_g_co2_per_kwh()` — NESO's own published coal factor, the
dirtiest grid GB could physically be — and the count refused is published.

R12. Every number here is a DIAGNOSTIC. In particular the finding that this instrument produces
about the ATOM'S OWN EXIT AXIS is the kind of finding an agent grading itself must handle at
arm's length: see `docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` §13. Nothing in this file
moves a level, changes an exit test, or is read by the published feed.

Reproduce: `python3 -m tools.ep13_peer_bound` -> `docs/observability/ep13_peer_bound.json`.
"""

from __future__ import annotations

import ast
import json
import random
from datetime import date as date_cls
from datetime import timedelta
from pathlib import Path
from typing import Mapping, Sequence

from sim import grid_carbon_intensity as gci
from sim import neso_carbon_intensity as neso

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "ep13_peer_bound.json"

#: Half-hour lags for the persistence ladder. 1 and 2 sit either side of any plausible operational
#: forecast horizon, 4 is two hours, and 48 is the same period yesterday -- the rung that shows the
#: ladder is measuring lead time and not merely smoothness, because it COLLAPSES.
LADDER_LAGS = (1, 2, 4, 48)

#: The shuffle seed for the null rung. Fixed so the null is reproducible; its job is to collapse.
NULL_SEED = 20260828

#: A year needs this many scored half hours before it is measured at all. Roughly two weeks. The
#: bar exists so a year with a fortnight of cache cannot report a correlation as if it were a year.
MIN_SCORED_HALF_HOURS = 600

#: `peer_is_not_a_backfill` fails above this share of bit-identical (forecast, actual) pairs. A
#: back-filled field would sit near 1.0; a genuine forecast collides with its outturn sometimes,
#: because both are published as whole grams.
MAX_IDENTICAL_SHARE = 0.10

#: How much the peer must beat its own day mean by before that counts as a within-day advantage.
#: FOUND BY A MUTATION RATHER THAN CHOSEN IN ADVANCE, and it is R15's fail-open shape in its most
#: embarrassing form: `peer > peer_day_mean` written as a strict inequality PASSES when the
#: mutation makes the two sides equal by construction, because the day mean of an
#: already-flat series differs from itself by 1e-16 of floating point. A control comparing two
#: quantities a defect makes IDENTICAL needs a materiality margin or it reports rounding noise as
#: a finding. A hundredth of a correlation is not an advantage; the measured gap is 0.13-0.15,
#: more than ten times this, so the bar is nowhere near the data and cannot be read as tuned to it.
MIN_WITHIN_DAY_ADVANTAGE = 0.01


def held_out(date: str) -> bool:
    """EVEN days of the month are scored, ODD days are not.

    IDENTICAL to `ep13_input_ceiling.held_out`, and duplicated rather than imported ON PURPOSE:
    this module fits nothing, so it has no fit side and no leakage to prevent. It scores on even
    days for ONE reason — so that its baseline column is the same population as that instrument's,
    and the two artefacts can be read in one table. Importing it would say the split is shared
    machinery; it is a shared CONVENTION, and if that file's split ever changes for a fitting
    reason this one must not silently follow.
    """
    return int(date[8:10]) % 2 == 0


def lagged_key(key: tuple[str, int], half_hours: int) -> tuple[str, int]:
    """The settlement key `half_hours` earlier, rolling back over midnight.

    Uses a 48-period day rather than the true 46/50 of the clock-change days. Those two days a year
    shift a handful of ladder rungs by one period; they cannot move a correlation over 8,000 half
    hours, and reaching for the real period count would put a DST model inside a reference rung
    whose whole value is that a reader can rebuild it in three lines.
    """
    day, period = date_cls.fromisoformat(key[0]), key[1] - half_hours
    while period < 1:
        day -= timedelta(days=1)
        period += 48
    while period > 48:
        day += timedelta(days=1)
        period -= 48
    return (day.isoformat(), period)


def day_mean(series: Mapping[tuple[str, int], float]) -> dict[tuple[str, int], float]:
    """Every half hour replaced by its own DAY's mean — the within-day axis deleted, nothing else.

    This is the placebo that separates the two axes the atom is scored on. A rung that keeps its
    correlation under this substitution was never carrying within-day information; the between-day
    ordering alone was doing the work.
    """
    totals: dict[str, list[float]] = {}
    for key, value in series.items():
        acc = totals.setdefault(key[0], [0.0, 0.0])
        acc[0] += float(value)
        acc[1] += 1.0
    return {key: totals[key[0]][0] / totals[key[0]][1] for key in series}


def shuffled(
    series: Mapping[tuple[str, int], float],
    keys: Sequence[tuple[str, int]],
    seed: int = NULL_SEED,
) -> dict[tuple[str, int], float]:
    """The same values dealt to different half hours. The VALUE DISTRIBUTION is preserved exactly
    and only the TIMING is destroyed, so the null tests the axis under measurement rather than the
    scale of the numbers."""
    ordered = sorted(keys)
    values = [float(series[k]) for k in ordered]
    random.Random(seed).shuffle(values)
    return dict(zip(ordered, values))


def refuse_unphysical(
    series: Mapping[tuple[str, int], Mapping[str, float]], ceiling: float
) -> tuple[dict[tuple[str, int], float], dict[tuple[str, int], float], int]:
    """(actual, forecast, refused) — a half hour survives only if BOTH sides are under `ceiling`.

    BOTH, jointly, because a filter on one side of a comparison measures the filter. A half hour
    whose forecast is 13,579 gCO2/kWh is dropped from the outturn series too, so the two rungs are
    scored over identical keys and the refusal cannot flatter either of them.
    """
    actual: dict[tuple[str, int], float] = {}
    forecast: dict[tuple[str, int], float] = {}
    refused = 0
    for key, entry in series.items():
        a, f = entry.get("actual"), entry.get("forecast")
        if a is None or f is None:
            refused += 1
            continue
        if float(a) > ceiling or float(f) > ceiling:
            refused += 1
            continue
        actual[key] = float(a)
        forecast[key] = float(f)
    return actual, forecast, refused


def _published_feed_source() -> str:
    return (PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(encoding="utf-8")


def peer_is_unreachable_from(source: str) -> bool:
    """True when nothing in `source` imports this module — an AST walk, not a substring search.

    Same walk and same reason as `ep13_input_ceiling.ceiling_is_unreachable_from`. Republishing
    NESO's forecast as this world's carbon series would make the reconstruction pointless and
    import NESO's arithmetic wholesale; that it cannot happen is a structural check here rather
    than a sentence in a docstring.
    """
    tree = ast.parse(source)
    mine = Path(__file__).stem
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[-1] == mine for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[-1] == mine:
                return False
            if any(alias.name == mine for alias in node.names):
                return False
    return True


def peer_equivalent_lag(
    peer: float, ladder: Mapping[str, float], lags: Sequence[int] = LADDER_LAGS
) -> float | None:
    """Where the peer forecast falls on the persistence ladder, in half hours, interpolated.

    `None` when the ladder does not bracket it — an unbracketed peer has been located on one side
    only, which is the fail-open shape this function refuses to paper over by extrapolating.
    """
    points = [(lag, ladder[f"persistence_lag_{lag}"]) for lag in lags if f"persistence_lag_{lag}" in ladder]
    points.sort(key=lambda p: p[0])
    for (lo_lag, lo_r), (hi_lag, hi_r) in zip(points, points[1:]):
        # Correlation FALLS as the lag grows, so the bracket is lo_r >= peer >= hi_r.
        if lo_r >= peer >= hi_r:
            if lo_r == hi_r:
                return float(lo_lag)
            span = (lo_r - peer) / (lo_r - hi_r)
            return float(lo_lag) + span * (hi_lag - lo_lag)
    return None


def measure_year(
    year: str,
    *,
    shipped: Mapping[tuple[str, int], float],
    actual: Mapping[tuple[str, int], float],
    forecast: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    lags: Sequence[int] = LADDER_LAGS,
) -> dict:
    """Every rung for one year, on the held-out half hours only.

    Every rung is SHAPED by `neso.published_shape` before scoring, because the reconstruction is a
    dimensionless shape and a gram-valued series compared against it would measure the units.
    """
    published = neso.published_shape(actual, demand)
    score_keys = [
        k
        for k in shipped
        if k[0][:4] == year
        and k in published
        and held_out(k[0])
        and float(demand.get(k) or 0.0) > 0.0
    ]
    if len(score_keys) < MIN_SCORED_HALF_HOURS:
        raise neso.NesoIntensityUnavailable(
            f"{year} has {len(score_keys)} scored half hours, under the {MIN_SCORED_HALF_HOURS} bar"
        )

    peer = neso.published_shape(forecast, demand)
    rungs: dict[str, Mapping[tuple[str, int], float]] = {
        "baseline": shipped,
        "peer_forecast": peer,
        "peer_forecast_day_mean": day_mean(peer),
        "peer_forecast_shuffled": neso.published_shape(
            shuffled(forecast, sorted(k for k in forecast if k[0][:4] == year)), demand
        ),
        "target_day_mean": day_mean(published),
    }
    for lag in lags:
        rungs[f"persistence_lag_{lag}"] = neso.published_shape(
            {
                key: actual[lagged_key(key, lag)]
                for key in actual
                if lagged_key(key, lag) in actual
            },
            demand,
        )

    row: dict[str, object] = {}
    for name, series in rungs.items():
        present = {k: series[k] for k in score_keys if k in series}
        if len(present) < MIN_SCORED_HALF_HOURS:
            continue
        row[name] = neso.compare_shapes(present, published, demand, year)

    identical = sum(1 for k in score_keys if abs(forecast[k] - actual[k]) < 1e-9)
    row["control_scored_half_hours"] = float(len(score_keys))
    row["control_peer_identical_share"] = identical / len(score_keys)
    row["control_peer_mean_abs_error_g"] = sum(
        abs(forecast[k] - actual[k]) for k in score_keys
    ) / len(score_keys)
    correlations = {
        name: float(value["correlation"])
        for name, value in row.items()
        if isinstance(value, dict) and value.get("correlation") is not None
    }
    row["peer_equivalent_lag_half_hours"] = peer_equivalent_lag(
        correlations["peer_forecast"], correlations, lags
    )
    row["peer_over_baseline"] = (
        correlations["peer_forecast"] - correlations["baseline"]
    )
    return row


def verdicts(row: Mapping[str, object], lags: Sequence[int] = LADDER_LAGS) -> dict[str, bool]:
    """The controls, computed from the row that was just published rather than only asserted in a
    test — a verdict that lives only in another process is one a reader has to take on trust."""
    def corr(name: str) -> float:
        return float(row[name]["correlation"])  # type: ignore[index]

    peer = corr("peer_forecast")
    ladder = [corr(f"persistence_lag_{lag}") for lag in lags if f"persistence_lag_{lag}" in row]
    return {
        # CONTROL 1, TAUTOLOGY. If the published forecast were back-filled from the outturn this
        # whole measurement would be a series against itself. The one control a reader should
        # check before any other, because if it fails every number below is 1.0 by construction.
        "peer_is_not_a_backfill": (
            float(row["control_peer_identical_share"]) < MAX_IDENTICAL_SHARE  # type: ignore[arg-type]
            and float(row["control_peer_mean_abs_error_g"]) > 1.0  # type: ignore[arg-type]
        ),
        # CONTROL 2, the peer's advantage is WITHIN-DAY. Deleting the within-day variation from
        # the peer must cost it MATERIALLY; if it does not, the between-day ordering was doing the
        # work and the number says nothing about the axis holding the level. See
        # MIN_WITHIN_DAY_ADVANTAGE for why this is not a strict inequality.
        "peer_beats_its_own_day_mean": peer - corr("peer_forecast_day_mean")
        > MIN_WITHIN_DAY_ADVANTAGE,
        # CONTROL 3, the NULL must collapse. The peer takes one value per scored half hour, so the
        # effective sample behind a shuffled correlation is the half-hour count and the threshold
        # is derived from it rather than chosen.
        "null_collapses": abs(corr("peer_forecast_shuffled"))
        < 3.0 / (float(row["control_scored_half_hours"]) ** 0.5),  # type: ignore[arg-type]
        # CONTROL 4, the ladder must BRACKET the peer. A ladder entirely below it bounds the peer
        # on one side only and would pass by being short — the fail-open shape of every one-sided
        # containment check. Bracketing is what turns the ladder from a bound into a LOCATION.
        "ladder_brackets_the_peer": bool(ladder)
        and max(ladder) >= peer >= min(ladder)
        and row["peer_equivalent_lag_half_hours"] is not None,
        # REPORTED, not a control: whether the publisher's own forecast clears the shipped
        # reconstruction on the atom's own axis.
        "peer_exceeds_baseline": peer > corr("baseline"),
    }


def measure() -> dict:
    """Every year the two series share. Loads the real caches; fits nothing."""
    from tools.generate_grid_intensity_feed import (
        AGWS_CACHE,
        DEMAND_CACHE,
        aggregate_demand,
        aggregate_renewable_generation,
        fuel_mix,
    )

    demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text(encoding="utf-8")))
    renewables = aggregate_renewable_generation(
        json.loads(Path(AGWS_CACHE).read_text(encoding="utf-8"))
    )
    (imports, coal_capacity, _coverage, thermal_floors, must_run, _mrc, _envelope) = fuel_mix()

    # THE BASELINE IS RE-MEASURED HERE AND NOT QUOTED from `ep13_input_ceiling.json`, though the
    # two agree to 1e-4. A cited baseline can come from a different run than the one it is being
    # compared against, and the whole value of this artefact is that its columns are one process.
    shipped = gci.build_shape(
        demand,
        renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year={y: r["floor_mw"] for y, r in thermal_floors.items()},
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=None,
    )

    ceiling = neso._physical_ceiling_g_co2_per_kwh()
    parsed = neso.to_settlement_periods(neso.load_cached())
    actual, forecast, refused = refuse_unphysical(parsed, ceiling)

    years = sorted({k[0][:4] for k in actual} & {k[0][:4] for k in shipped})
    rows: dict[str, dict] = {}
    for year in years:
        try:
            row = measure_year(
                year, shipped=shipped, actual=actual, forecast=forecast, demand=demand
            )
        except (neso.NesoIntensityUnavailable, ValueError, KeyError):
            continue
        row["controls"] = verdicts(row)
        rows[year] = row

    return {
        "measured_from": "sim/cache (NESO Carbon Intensity forecast+actual, Elexon FUELHH + demand + AGWS)",
        "basis": neso.PUBLISHED_BASIS,
        "split": "scored on EVEN days of the month -- the same population ep13_input_ceiling scores",
        "physical_ceiling_g_co2_per_kwh": ceiling,
        "half_hours_refused_as_unphysical": float(refused),
        "rungs": {
            "baseline": "build_shape as shipped -- where the atom is",
            "peer_forecast": "NESO's OWN published forecast against NESO's OWN outturn",
            "peer_forecast_day_mean": "the peer with its within-day variation deleted -- CONTROL",
            "peer_forecast_shuffled": "the peer dealt to other half hours -- NULL, must collapse",
            "target_day_mean": "the outturn's own day mean -- hindsight, between-day axis only",
            "persistence_lag_N": "the outturn copied from N half hours earlier -- the LADDER",
        },
        "what_this_bound_is_not": (
            "NOT an oracle: it holds no truth and can be beaten. NOT independent: NESO's actual is "
            "itself a model built from the same factor table, embedded estimate and loss "
            "correction as its forecast, so common-mode cancels and this OVERSTATES what an "
            "outside reconstruction can reach. The optimism is in the safe direction -- a LOW peer "
            "would have closed the axis; a HIGH one promises no build succeeds."
        ),
        "peer_reaches_the_published_feed": not peer_is_unreachable_from(_published_feed_source()),
        "years": rows,
    }


def main(argv: list[str] | None = None) -> int:
    data = measure()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=1, default=str) + "\n", encoding="utf-8")
    print("year   n   baseline    PEER  peer_daymean   null   lag1   lag2   lag4  lag48  ~lag")
    for year, row in sorted(data["years"].items()):
        c = row["controls"]
        lag = row["peer_equivalent_lag_half_hours"]
        print(
            f"{year} {int(row['control_scored_half_hours']):5d} "
            f"{row['baseline']['correlation']:8.4f} "
            f"{row['peer_forecast']['correlation']:7.4f} "
            f"{row['peer_forecast_day_mean']['correlation']:12.4f} "
            f"{row['peer_forecast_shuffled']['correlation']:6.3f} "
            + " ".join(
                f"{row[f'persistence_lag_{lag_n}']['correlation']:6.4f}" for lag_n in LADDER_LAGS
            )
            + (f" {lag:5.2f}" if lag is not None else "     -")
            + "  | backfill_ok=" + ("Y" if c["peer_is_not_a_backfill"] else "N")
            + " within_day=" + ("Y" if c["peer_beats_its_own_day_mean"] else "N")
            + " null=" + ("Y" if c["null_collapses"] else "N")
            + " bracket=" + ("Y" if c["ladder_brackets_the_peer"] else "N")
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
