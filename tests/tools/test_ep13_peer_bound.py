"""R15 for `tools/ep13_peer_bound.py`.

WHAT THIS INSTRUMENT'S HEADLINE IS, and therefore what its controls have to be able to do.
Every previous EP13 bound reported a NEGATIVE — no headroom, retire the candidate — and the R15
danger there was an instrument that can only ever say "no headroom", which reports a CONSTANT
(R15's fourth shape). This one reports a POSITIVE: the target IS reproducible, the peer clears
the shipped model by 0.23 in 2024. The danger is exactly inverted, so the load-bearing test here
is `test_the_instrument_reports_a_LOW_peer_when_the_peer_IS_BAD` — a world where the publisher's
forecast carries no timing, requiring the instrument to say so.

The fixture is SYNTHETIC and does not read `sim/cache`, because a control that needs a 104,454
half-hour cache present is fail-silent the day the cache is absent. One test reads the COMMITTED
artefact to pin the published headline to the measurement, and it skips (loudly, with the reason)
when that file is missing rather than passing on its absence.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pytest

from sim import neso_carbon_intensity as neso
from tools import ep13_peer_bound as peer

YEAR = "2024"
DAYS = 60
PERIODS = 48


def _world(
    *,
    forecast_noise_g: float = 12.0,
    forecast_carries_timing: bool = True,
    seed: int = 7,
) -> tuple[dict, dict, dict, dict]:
    """(shipped, actual, forecast, demand) for one synthetic year.

    The SHIPPED baseline is a COMPETENT model, not a broken one: it gets the between-day level
    right and the within-day phase partly wrong, which is the real shape of what this atom ships
    (correlation 0.74 in 2024, day-level errors small). A fixture whose baseline is absurd makes
    its own bar meaningless -- every rung would clear a baseline of -1.
    """
    rng = random.Random(seed)
    actual: dict[tuple[str, int], float] = {}
    forecast: dict[tuple[str, int], float] = {}
    demand: dict[tuple[str, int], float] = {}
    shipped_g: dict[tuple[str, int], float] = {}
    for day in range(1, DAYS + 1):
        key_date = f"{YEAR}-03-{day:02d}" if day <= 31 else f"{YEAR}-04-{day - 31:02d}"
        level = 200.0 + 40.0 * math.sin(2 * math.pi * day / 29.0)
        for period in range(1, PERIODS + 1):
            phase = 2 * math.pi * period / PERIODS
            within = 60.0 * math.sin(phase) + 20.0 * math.sin(2 * phase)
            key = (key_date, period)
            actual[key] = level + within + rng.gauss(0.0, 4.0)
            demand[key] = 30000.0 + 8000.0 * math.sin(phase - 0.6)
            # The shipped model: right about the day, wrong about the ordering inside it.
            shipped_g[key] = level + 0.45 * within + 25.0 * math.sin(phase + 2.2)
            if forecast_carries_timing:
                forecast[key] = actual[key] + rng.gauss(0.0, forecast_noise_g)
            else:
                forecast[key] = level + rng.gauss(0.0, forecast_noise_g)
    shipped = neso.published_shape(shipped_g, demand)
    return shipped, actual, forecast, demand


def _row(**kwargs):
    shipped, actual, forecast, demand = _world(**kwargs)
    row = peer.measure_year(
        YEAR, shipped=shipped, actual=actual, forecast=forecast, demand=demand
    )
    row["controls"] = peer.verdicts(row)
    return row


@pytest.fixture(scope="module")
def row():
    return _row()


def test_the_fixture_is_a_population_and_the_baseline_is_competent(row):
    """POPULATION FIRST. A correlation over a handful of half hours is noise wearing a statistic's
    clothes, and a bar cleared by an absurd baseline measures nothing."""
    assert row["control_scored_half_hours"] >= peer.MIN_SCORED_HALF_HOURS
    assert row["control_scored_half_hours"] >= 1000
    assert 0.55 < row["baseline"]["correlation"] < 0.95


def test_the_instrument_reports_a_LOW_peer_when_the_peer_IS_BAD():
    """THE LOAD-BEARING TEST. This instrument's finding is a POSITIVE, so an instrument that reports
    a high peer on any input reports a CONSTANT and its headline is worthless.

    The bad world is not noise-vs-noise: the forecast still knows the day's LEVEL exactly and has
    lost only the within-day ordering, which is the specific claim under measurement. Asserted by
    ATTAINMENT -- the peer must fall BELOW the shipped baseline and its own within-day control must
    go False -- and not merely by "it went down".
    """
    bad = _row(forecast_carries_timing=False)
    assert bad["peer_forecast"]["correlation"] < bad["baseline"]["correlation"]
    assert bad["controls"]["peer_exceeds_baseline"] is False
    assert bad["controls"]["peer_beats_its_own_day_mean"] is False
    # And the ladder, which is a property of the TARGET and not of the forecast, is unmoved.
    assert bad["persistence_lag_1"]["correlation"] > 0.9


def test_a_BACKFILLED_forecast_is_caught_by_the_tautology_control(row):
    """MUTATION: forecast := actual. The R15 first killer -- a series compared with itself.

    Without this control the instrument would report a perfect peer and the atom would conclude
    the target is trivially reproducible from a field that is the target.
    """
    assert row["controls"]["peer_is_not_a_backfill"] is True

    shipped, actual, _forecast, demand = _world()
    backfilled = peer.measure_year(
        YEAR, shipped=shipped, actual=actual, forecast=dict(actual), demand=demand
    )
    verdicts = peer.verdicts(backfilled)
    assert backfilled["control_peer_identical_share"] == 1.0
    assert backfilled["control_peer_mean_abs_error_g"] == 0.0
    assert verdicts["peer_is_not_a_backfill"] is False
    assert backfilled["peer_forecast"]["correlation"] == pytest.approx(1.0, abs=1e-9)


def test_the_within_day_control_fires_when_the_peer_is_its_own_day_mean():
    """MUTATION: forecast := its own day mean. The peer keeps every between-day fact and loses
    every within-day one, so a control that still passes is not reading the axis it names.

    THIS MUTATION SURVIVED THE FIRST BATTERY AND THE CONTROL WAS THE FAULT. Written as the obvious
    `peer > peer_day_mean`, it PASSED under its own defect: the day mean of an already-flat series
    equals that series, and the two correlations differed by 1.1e-16 of floating point, which a
    strict inequality reads as an advantage. A control comparing two quantities the defect makes
    IDENTICAL is fail-open without a materiality margin -- it reports rounding noise as a finding.
    Hence `MIN_WITHIN_DAY_ADVANTAGE`, and hence this test asserts the margin BINDS: the gap under
    the mutation is real-but-negligible, not negative, so a margin of zero would still pass.
    """
    shipped, actual, forecast, demand = _world()
    flattened = peer.day_mean(forecast)
    row = peer.measure_year(
        YEAR, shipped=shipped, actual=actual, forecast=flattened, demand=demand
    )
    gap = row["peer_forecast"]["correlation"] - row["peer_forecast_day_mean"]["correlation"]
    assert abs(gap) < 1e-9, "the mutation must make the two sides equal, or it tests something else"
    assert peer.verdicts(row)["peer_beats_its_own_day_mean"] is False


def test_the_within_day_margin_is_far_below_the_measured_signal(row):
    """The margin must not be doing the work. A bar the real data only just clears is a bar chosen
    to be cleared; this one sits more than an order of magnitude below the measured gap."""
    gap = row["peer_forecast"]["correlation"] - row["peer_forecast_day_mean"]["correlation"]
    assert gap > 10 * peer.MIN_WITHIN_DAY_ADVANTAGE
    assert row["controls"]["peer_beats_its_own_day_mean"] is True


def test_day_mean_actually_flattens_the_within_day_axis():
    """The control above is only as good as `day_mean`. A `day_mean` that returned its input would
    make `peer_beats_its_own_day_mean` compare a series with itself and pass by tautology."""
    _shipped, actual, _forecast, _demand = _world()
    flat = peer.day_mean(actual)
    assert len(flat) == len(actual)
    per_day = {}
    for (day, _period), value in flat.items():
        per_day.setdefault(day, set()).add(round(value, 9))
    assert all(len(values) == 1 for values in per_day.values())
    assert len({tuple(v)[0] for v in per_day.values()}) > 1  # days still differ from each other


def test_the_NULL_rung_collapses_and_the_control_fires_when_it_does_not(row):
    """MUTATION: `shuffled` returns its input, i.e. the null is not a null. A null rung that is
    silently the treatment is R15 fail-silent -- the control would pass on a broken null."""
    assert row["controls"]["null_collapses"] is True
    assert abs(row["peer_forecast_shuffled"]["correlation"]) < 0.1

    unshuffled = dict(row)
    unshuffled["peer_forecast_shuffled"] = row["peer_forecast"]
    assert peer.verdicts(unshuffled)["null_collapses"] is False


def test_shuffled_preserves_the_VALUES_and_destroys_only_the_TIMING():
    """A null that changed the distribution would test the scale of the numbers, not the axis."""
    _shipped, _actual, forecast, _demand = _world()
    keys = sorted(forecast)
    out = peer.shuffled(forecast, keys)
    assert sorted(out.values()) == pytest.approx(sorted(forecast[k] for k in keys))
    assert any(abs(out[k] - forecast[k]) > 1e-9 for k in keys)


def test_a_ONE_SIDED_ladder_fails_the_bracket_control(row):
    """MUTATION: drop the rungs above the peer, leaving a ladder that only bounds it from below.

    A one-sided containment check passes by being WIDE, which is why the mutation here is a
    NARROWING of the ladder rather than a move of the peer: the surviving rungs still 'contain'
    the peer in the loose sense, and only a bracket requirement can tell the difference.
    """
    assert row["controls"]["ladder_brackets_the_peer"] is True
    assert row["peer_equivalent_lag_half_hours"] is not None

    one_sided = {k: v for k, v in row.items() if k not in ("persistence_lag_1", "persistence_lag_2")}
    one_sided["peer_equivalent_lag_half_hours"] = peer.peer_equivalent_lag(
        row["peer_forecast"]["correlation"],
        {
            name: row[name]["correlation"]
            for name in ("persistence_lag_4", "persistence_lag_48")
        },
        lags=(4, 48),
    )
    assert one_sided["peer_equivalent_lag_half_hours"] is None
    assert peer.verdicts(one_sided, lags=(4, 48))["ladder_brackets_the_peer"] is False


def test_peer_equivalent_lag_interpolates_inside_the_bracket_it_found():
    ladder = {"persistence_lag_1": 0.99, "persistence_lag_2": 0.97, "persistence_lag_4": 0.93}
    assert peer.peer_equivalent_lag(0.98, ladder, (1, 2, 4)) == pytest.approx(1.5)
    assert peer.peer_equivalent_lag(0.99, ladder, (1, 2, 4)) == pytest.approx(1.0)
    assert peer.peer_equivalent_lag(0.995, ladder, (1, 2, 4)) is None  # above every rung


def test_an_unphysical_reading_is_refused_on_BOTH_sides_of_the_comparison():
    """A filter applied to one side of a comparison measures the filter.

    NESO's forecast field carries readings that are not a grid -- 13,579 gCO2/kWh among them. The
    half hour has to leave the OUTTURN series too, or the two rungs are scored over different
    populations and the refusal flatters whichever side kept it.
    """
    series = {
        ("2024-03-02", 1): {"actual": 200.0, "forecast": 210.0},
        ("2024-03-02", 2): {"actual": 190.0, "forecast": 13579.0},
        ("2024-03-02", 3): {"actual": 9999.0, "forecast": 205.0},
        ("2024-03-02", 4): {"actual": 180.0},
    }
    actual, forecast, refused = peer.refuse_unphysical(series, 937.0)
    assert set(actual) == set(forecast) == {("2024-03-02", 1)}
    assert refused == 3


def test_lagged_key_rolls_back_over_midnight():
    assert peer.lagged_key(("2024-03-02", 5), 4) == ("2024-03-02", 1)
    assert peer.lagged_key(("2024-03-02", 2), 4) == ("2024-03-01", 46)
    assert peer.lagged_key(("2024-03-01", 1), 48) == ("2024-02-29", 1)


def test_a_year_too_thin_to_measure_is_REFUSED_not_reported():
    """R15 fail-open: a year with a fortnight of cache must not report a correlation as if it were
    a year. The refusal is an exception the caller skips on, not a quietly smaller n."""
    shipped, actual, forecast, demand = _world()
    keep = {k for k in actual if int(k[0][8:10]) <= 4}
    with pytest.raises(neso.NesoIntensityUnavailable):
        peer.measure_year(
            YEAR,
            shipped={k: v for k, v in shipped.items() if k in keep},
            actual={k: v for k, v in actual.items() if k in keep},
            forecast={k: v for k, v in forecast.items() if k in keep},
            demand=demand,
        )


def test_the_peer_series_cannot_reach_the_published_feed():
    """STRUCTURAL, not a promise. Republishing NESO's forecast as this world's carbon series would
    make the reconstruction pointless and import NESO's arithmetic wholesale."""
    assert peer.peer_is_unreachable_from(peer._published_feed_source()) is True
    assert peer.peer_is_unreachable_from("from tools.ep13_peer_bound import measure") is False
    assert peer.peer_is_unreachable_from("import tools.ep13_peer_bound") is False
    assert peer.peer_is_unreachable_from("# tools.ep13_peer_bound is mentioned only here") is True


def test_the_committed_artefact_carries_the_numbers_the_frame_doc_quotes():
    """R11-flavoured: the doc's sentence is pinned to the artefact, because this project has twice
    been caught publishing a recollection written in the grammar of a measurement."""
    path = Path(peer.OUT_PATH)
    if not path.exists():
        pytest.skip(f"{path} not generated -- run `python3 -m tools.ep13_peer_bound`")
    data = json.loads(path.read_text(encoding="utf-8"))
    years = data["years"]
    assert set(years) >= {"2019", "2020", "2021", "2022", "2023", "2024"}
    for year, r in years.items():
        assert all(r["controls"].values()), f"{year} published a failed control"
        assert 0.95 < r["peer_forecast"]["correlation"] < 0.99
        assert r["persistence_lag_1"]["correlation"] > r["peer_forecast"]["correlation"]
        assert r["persistence_lag_48"]["correlation"] < r["peer_forecast"]["correlation"]
        assert 1.5 < r["peer_equivalent_lag_half_hours"] < 3.0
    assert years["2024"]["baseline"]["correlation"] == pytest.approx(0.7425, abs=0.002)
    assert years["2024"]["peer_over_baseline"] == pytest.approx(0.229, abs=0.005)
    assert data["peer_reaches_the_published_feed"] is False
