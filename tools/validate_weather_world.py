"""Measure whether `sim/weather_world/` is what committed code would produce.

REUSE: tools/validate_weather_world.py
CLASS: CUSTOM
INDEX: searched "validate weather", "weather world check", "store consistency", "reproduce
       artefact", "haduk check". `tools/build_weather_world.py` WRITES the store and its pure
       decomposition helpers (`level_of`, `extract_temperature`) are imported here rather than
       re-implemented -- a validator that re-derives the formula it is checking cannot fail.
       `simulation/weather_cell_siting.py` asks whether two PLACES may substitute for each other
       on heat-load drivers; it does not read this store. `tools/canon_drift_check.py` compares a
       published page to code, not an artefact to its producer. Nothing else re-derives a
       committed data artefact from its sources.

WHY THIS EXISTS
---------------
Both `sim/weather_world.py` and `tools/build_weather_world.py` cited this path for eight days
before it existed. A path in a prose comment is a reachability edge, so the store's only claimed
control was a file nothing could run -- and the store's real state was worse than either docstring
knew: the writer in the tree and the bytes on disk had different SHAPES, so re-running the builder
would have corrupted the artefact rather than rebuilt it.

The question this answers is the one that decides whether 7.9 MB of derived data may be committed
at all: **would running the committed code again produce these bytes?** An artefact nobody can
regenerate is the defect `simulation/weather_cell_siting.py` already devotes three paragraphs to,
and committing a larger one would be re-buying it at scale.

WHAT IT CAN AND CANNOT ESTABLISH
---------------------------------
The store has two halves and only one of them is checkable offline.

  * TEMPERATURE comes from the HadUK 1 km daily grids under `~/.cache/`, so it is re-derived here
    from those grids and diffed value by value. This half is genuinely falsifiable.
  * WIND, CLOUD and PRECIPITATION come from the Open-Meteo ERA5 archive over the network. Re-
    pulling 156 cells to check them would take about an hour and would compare today's archive to
    a pull made on another day. Those columns are checked for PRESENCE and internal consistency
    only, and this module says so rather than implying a coverage it does not have.

A leg that cannot run says so and does not pass. `--require-temperature` turns an absent HadUK
cache from "skipped" into a refusal, which is what a gate wants and what an exploratory run does
not.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import statistics
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from sim.weather_world import (  # noqa: E402
    CELLS_PATH,
    REGIMES_PATH,
    SERIES_PATH,
)
from tools.build_weather_world import (  # noqa: E402
    END_DATE,
    ERA5_FIELDS,
    HADUK_DAY,
    LEVELLED,
    START_DATE,
    extract_temperature,
    level_of,
)
from tools.reduction_dimension import declare  # noqa: E402

#: The store rounds to three decimals, so two derivations of the same value may differ by half a
#: unit in the last place from each side. Anything above this is a real disagreement, not rounding.
TOLERANCE_C = 0.001

#: WHAT `check_era5_coverage` REDUCES OVER, per the demand-vector canon's rule that a coverage claim
#: names the axes it varies over and accounts for every component of its subject as reduced or
#: explicitly blind. Enforced by `tests/architecture/test_a_coverage_claim_declares_what_it_reduces
#: _over.py`, which had been red at `origin/main` on this module with no commit's gate selection able
#: to reach it.
#:
#: THE DECLARATION IS WHERE A CONFLATION BECOMES VISIBLE, and writing this one surfaced a real one
#: rather than tidying a red away. The leg is NAMED "every cell carries the ERA5 columns" and what it
#: computes is `any(field non-empty, over any row, over any field)`, so:
#:
#:   * THE FIELD COLLAPSE. A cell holding wind and NO cloud is not counted bare, and the leg passes
#:     it -- while this module's own header says the fabric path reads cloud cover and "a cell with
#:     temperature and no cloud cannot drive it". Declared as `any_era5_column_present`, derived from
#:     all three fields, so `Declaration.collapsed` states it in the banner as arithmetic on the
#:     declaration rather than as a confession somebody has to remember to write.
#:   * THE TIME COLLAPSE. One non-empty row passes the whole cell, so how MUCH of a cell's series
#:     carries the columns is not in the figure at all. `within_cell_time_coverage`, blind.
#:
#: WHETHER `any` SHOULD BE `all` IS NOT DECIDED HERE, and that is deliberate. It is a question about
#: what partial ERA5 coverage means for the fabric path, the weather lane owns it, and changing a
#: world-fidelity verdict inside a commit whose subject is clearing reds is how one lane's judgement
#: gets made by another lane's tidying. Filed as a finding instead. The canon's own sentence about
#: this class applies exactly: it "flatters in a consistent direction -- always making the sample
#: look smaller and the coverage look better -- which is why it must be looked for rather than
#: waited for".
REDUCES_OVER = (
    declare(
        "the share of store cells holding any ERA5 archive column at all",
        kind="coverage",
        of=ERA5_FIELDS,
        reduces_over=("any_era5_column_present",),
        derived_from={"any_era5_column_present": ERA5_FIELDS},
        blind_to=("within_cell_time_coverage",),
        joint=True,
    ),
)


class Leg:
    """One check, its verdict, and the evidence for it.

    A leg has THREE outcomes, not two. `None` means the leg could not run -- an absent HadUK
    cache, an absent store -- and it is kept distinct from `True` on purpose: a validator that
    reports a skipped leg as a pass is the fail-open this module exists to prevent.
    """

    def __init__(self, name: str, passed: bool | None, detail: str):
        self.name, self.passed, self.detail = name, passed, detail

    @property
    def mark(self) -> str:
        return {True: "PASS", False: "FAIL", None: "COULD NOT RUN"}[self.passed]

    def __repr__(self) -> str:
        return f"{self.mark:<13} {self.name}: {self.detail}"


def load_store() -> tuple[dict, dict, dict[str, list[dict]]]:
    """The three artefacts, with the series still keyed by REGIME and still in anomaly terms."""
    cells = json.loads(CELLS_PATH.read_text(encoding="utf-8"))
    regimes = json.loads(REGIMES_PATH.read_text(encoding="utf-8")) if REGIMES_PATH.is_file() else {
        "k": 0, "regime_of_cell": {}}
    series: dict[str, list[dict]] = {}
    with gzip.open(SERIES_PATH, "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            series.setdefault(row["cell_id"], []).append(row)
    return cells, regimes, series


def check_artefacts_agree(cells: dict, regimes: dict, series: dict) -> Leg:
    """Every key in each of the three files is known to the other two.

    THE DEFECT THIS CATCHES IS THE ONE THAT WAS LIVE: a series keyed by regime and a reader keyed
    by cell agree on nothing, and a rewrite carries both keyings in one column.
    """
    regime_of_cell = regimes.get("regime_of_cell", {})
    cell_of_regime = {r: c for c, r in regime_of_cell.items()}
    faults = []

    unmapped = sorted(set(series) - set(cell_of_regime))
    if unmapped:
        faults.append(f"{len(unmapped)} series key(s) absent from regimes.json ({unmapped[:4]})")
    uncelled = sorted({cell_of_regime[r] for r in series if r in cell_of_regime}
                      - set(cells["cells"]))
    if uncelled:
        faults.append(f"{len(uncelled)} mapped cell(s) absent from cells.json ({uncelled[:4]})")
    seriesless = sorted(set(regime_of_cell.values()) - set(series))
    if seriesless:
        faults.append(f"{len(seriesless)} regime(s) with no rows ({seriesless[:4]})")
    if regimes.get("k") != len(regime_of_cell):
        faults.append(f"k={regimes.get('k')} but the map holds {len(regime_of_cell)}")

    if faults:
        return Leg("the three artefacts agree", False, "; ".join(faults))
    return Leg("the three artefacts agree", True,
               f"{len(cells['cells'])} cells, {len(regime_of_cell)} regimes, "
               f"{sum(len(v) for v in series.values())} rows, every key known to all three")


def check_decomposition(cells: dict, regimes: dict, series: dict) -> Leg:
    """The stored temperature really is an ANOMALY: each regime's mean is zero.

    WHAT THIS LEG CANNOT ESTABLISH, SAID OUT LOUD. The obvious question -- "is `level_c` the mean
    of the cell's own raw series?" -- CANNOT BE ASKED HERE, and the first draft of this function
    asked it anyway and was a tautology. The only raw series available inside the store is
    reconstructed as `stored + level_c`, so its mean is `mean(stored) + level_c` and comparing
    that back to `level_c` tests nothing about `level_c` at all: it passes for any value
    whatsoever. `test_the_decomposition_leg_refuses_a_level_that_is_not_the_cells_mean` caught it
    by shifting a level 3 C and watching the leg stay green.

    Whether `level_c` is the RIGHT number is a question about the HadUK grids, so it belongs to
    `check_temperature_reproduces` and is asked there -- a shifted level puts every one of that
    cell's values 3 C from its source.

    What IS checkable here, and is not circular, is the property the reader depends on: the stored
    columns are centred on zero. That is what makes `for_cell` adding `level_c` back correct, and
    it goes red the moment a writer stores the raw series instead -- which would hand every caller
    a temperature about eleven degrees wrong and entirely plausible.
    """
    regime_of_cell = regimes.get("regime_of_cell", {})
    # -1.0, not 0.0, so the first cell always claims the slot. Starting at 0.0 left `worst_cell`
    # as None on a store where every cell is exact -- the report then named no cell precisely when
    # the news was good, which reads like the leg found nothing to look at.
    worst, worst_cell, checked = -1.0, None, 0
    for cell in cells["cells"]:
        rows = series.get(regime_of_cell.get(cell, cell))
        if not rows:
            continue
        anomaly = [float(r["temperature_mean_c"]) for r in rows
                   if r["temperature_mean_c"] not in ("", None)]
        if not anomaly:
            continue
        # `level_of` is the writer's own function, so the two cannot drift apart.
        gap = abs(level_of([{"temperature_mean_c": v} for v in anomaly]))
        checked += 1
        if gap > worst:
            worst, worst_cell = gap, cell
    if not checked:
        return Leg("the stored temperature is an anomaly", None, "no cell carries temperature")
    if worst > TOLERANCE_C:
        return Leg("the stored temperature is an anomaly", False,
                   f"{worst_cell}'s stored mean is {worst:.4f} C, not zero -- the series is raw, "
                   f"or its level was taken over a different population ({checked} cell(s))")
    return Leg("the stored temperature is an anomaly", True,
               f"{checked} cell(s) centred on zero, worst |mean| {worst:.5f} C at {worst_cell}")


def check_window(series: dict) -> Leg:
    """Every regime spans the declared window, day for day, with no gap and no duplicate."""
    from datetime import date

    start = date.fromisoformat(START_DATE)
    end = date.fromisoformat(END_DATE)
    want = (end - start).days + 1
    faults = []
    for regime, rows in sorted(series.items()):
        dates = [r["date"] for r in rows]
        if len(set(dates)) != len(dates):
            faults.append(f"{regime} has duplicate dates")
        elif len(dates) != want:
            faults.append(f"{regime} has {len(dates)} day(s), not {want}")
        elif min(dates) != START_DATE or max(dates) != END_DATE:
            faults.append(f"{regime} spans {min(dates)}..{max(dates)}")
        if len(faults) >= 4:
            break
    if faults:
        return Leg("every regime spans the window", False, "; ".join(faults))
    return Leg("every regime spans the window", True,
               f"{len(series)} regime(s) x {want} days, {START_DATE}..{END_DATE}, no gaps")


def check_era5_coverage(cells: dict, regimes: dict, series: dict) -> Leg:
    """WHICH cells carry the archive columns. Reported, and reported as a FAIL when any do not.

    This is not a nicety. The fabric path reads cloud cover, so a cell with temperature and no
    cloud cannot drive it even once the store is wired -- and a store that is 88% pulled looks
    complete to every consumer that only asks for temperature.
    """
    regime_of_cell = regimes.get("regime_of_cell", {})
    bare = sorted(
        cell for cell in cells["cells"]
        if not any(r.get(f) not in ("", None)
                   for r in series.get(regime_of_cell.get(cell, cell), [])
                   for f in ERA5_FIELDS))
    if bare:
        return Leg("every cell carries the ERA5 columns", False,
                   f"{len(bare)} of {len(cells['cells'])} cell(s) hold temperature only "
                   f"({', '.join(bare[:4])}{'...' if len(bare) > 4 else ''}) -- "
                   f"{len(bare) * len(series.get(next(iter(series)), []))} rows with no "
                   f"wind, cloud or precipitation")
    return Leg("every cell carries the ERA5 columns", True,
               f"all {len(cells['cells'])} cell(s) carry {', '.join(ERA5_FIELDS)}")


def check_temperature_reproduces(cells: dict, regimes: dict, series: dict,
                                 progress=print) -> Leg:
    """Re-derive temperature from the HadUK grids and diff it against the bytes on disk.

    THE ONLY LEG THAT ANSWERS THE QUESTION THE STORE IS COMMITTED ON. Everything else here checks
    that the artefact is consistent with ITSELF, which a fabricated file would also be.
    """
    if not HADUK_DAY.is_dir():
        return Leg("temperature re-derives from HadUK", None,
                   f"{HADUK_DAY} is absent -- the 1 km grids are not on this machine")

    regime_of_cell = regimes.get("regime_of_cell", {})
    derived = extract_temperature(cells["cells"], progress=progress)

    diffs: dict[str, list[float]] = {f: [] for f in LEVELLED}
    absent = 0
    for cell, meta in cells["cells"].items():
        rows = series.get(regime_of_cell.get(cell, cell), [])
        level = float(meta.get("level_c", 0.0) or 0.0)
        got = derived.get(cell, {})
        for row in rows:
            day = got.get(row["date"])
            if day is None:
                absent += 1
                continue
            for field in LEVELLED:
                if row[field] in ("", None) or field not in day:
                    continue
                diffs[field].append((float(row[field]) + level) - day[field])

    compared = sum(len(v) for v in diffs.values())
    if not compared:
        return Leg("temperature re-derives from HadUK", None,
                   "the grids yielded no cell-day the store also holds")

    worst = max(max((abs(x) for x in v), default=0.0) for v in diffs.values())
    agreeing = sum(1 for v in diffs.values() for x in v if abs(x) <= TOLERANCE_C)
    detail = (f"{compared} value(s) compared, {agreeing / compared:.4%} within {TOLERANCE_C} C, "
              f"worst |diff| {worst:.4f} C"
              + (f", {absent} stored cell-day(s) the grids do not cover" if absent else ""))
    for field in LEVELLED:
        if diffs[field]:
            detail += (f"; {field} mean {statistics.fmean(diffs[field]):+.5f}")
    return Leg("temperature re-derives from HadUK", worst <= TOLERANCE_C and not absent, detail)


def validate(temperature: bool = True, progress=print) -> list[Leg]:
    """Every leg, in cost order -- the cheap consistency checks before the five-minute re-derive."""
    if not CELLS_PATH.is_file() or not SERIES_PATH.is_file():
        return [Leg("the store exists", False,
                    f"{CELLS_PATH.parent} does not hold both cells.json and daily.csv.gz. "
                    "Build it with `python3 -m tools.build_weather_world --build`.")]
    cells, regimes, series = load_store()
    legs = [
        check_artefacts_agree(cells, regimes, series),
        check_window(series),
        check_decomposition(cells, regimes, series),
        check_era5_coverage(cells, regimes, series),
    ]
    if temperature:
        legs.append(check_temperature_reproduces(cells, regimes, series, progress=progress))
    else:
        legs.append(Leg("temperature re-derives from HadUK", None, "not asked for"))
    return legs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-temperature", action="store_true",
                        help="skip the HadUK re-derive (it opens 360 monthly grids)")
    parser.add_argument("--require-temperature", action="store_true",
                        help="treat an absent HadUK cache as a refusal, not a skip")
    args = parser.parse_args(argv)

    legs = validate(temperature=not args.no_temperature)
    for leg in legs:
        print(leg)

    failed = [leg for leg in legs if leg.passed is False]
    skipped = [leg for leg in legs if leg.passed is None]
    # FAIL CLOSED, AND SAY SO ON THE SURFACE. A skipped leg is printed as a skip and counted as
    # one; it is never folded into the pass count.
    print(f"\n{sum(1 for x in legs if x.passed is True)} passed, {len(failed)} failed, "
          f"{len(skipped)} could not run")
    if failed:
        return 1
    if skipped and args.require_temperature:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
