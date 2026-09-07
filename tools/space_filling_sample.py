"""Draw for difference: a candidate house is rejected when one already drawn behaves the same.

REUSE: tools/space_filling_sample.py
CLASS: CUSTOM
INDEX: searched "sample", "space filling", "maximin", "coverage", "corner", "reject", "diversity".
       `tools/demand_case_coverage.py` answers HOW MANY cases are needed and is imported for its
       population and its demand model -- it does not choose them. `tools/weather_cell_derivation.py`
       partitions the WEATHER drivers. `simulation/population_draw.py` draws for PROPORTION, raked
       onto published marginals, which is the thing this is the opposite of and does not replace.
       Nothing selects a set of houses by how differently they behave.

WHY THIS EXISTS
---------------
Housing ruling, sections 1 and 3.2, the director's words:

    "Draw for DIFFERENCE, not for proportion. Two London terraces on one street teach the world
     nothing the first did not... a candidate is rejected if a house already drawn would behave the
     same. 'Behave the same' is judged on OUTPUTS, not inputs: usage level, shape and weather
     gradient, and the technical ceiling on each value lever. Not on type/age/size labels."

And the failure mode it names, section 6(a): *"the similarity test run on inputs instead of outputs,
producing a sample that matches every marginal and misses the joint corners."*

WHAT THE OUTPUT SPACE IS, AND WHAT IS HONESTLY MISSING FROM IT
--------------------------------------------------------------
Five axes, each computed for every (weather cell x house case) pair in the England-and-Wales
population, from the same validated closed form `demand_case_coverage` uses:

    annual_kwh                 the level
    kwh_per_degree_day         the weather gradient
    solar_offset_share         the share of gross heat loss the sun already removes
    insulation_ceiling_kwh     what retrofitting this fabric to FULL would save, in kWh
    turndown_ceiling_kwh       what one degree off the set-point would save, in kWh

THE RULING ALSO NAMES **SHAPE**, AND SHAPE IS NOT HERE. The closed form is annual and carries no
half-hourly or intra-year profile, so a shape axis computed from it would be a function of the two
axes above wearing a third axis's name -- which is exactly the "invented number filling a slot"
this project keeps paying for. It is a named gap with a stated consequence: the sample below is
space-filling in LEVEL, GRADIENT and TWO CEILINGS, and two houses it calls different by nothing
else may still share a profile. `W2_23`'s observation layer is where a shape axis becomes payable.

**Five of the seven phase-1 levers are also absent** for the same reason and it is the same
sentence: PV, battery, EV and flow-temperature ceilings need roof geometry, parking and a heating
circuit the premise joint does not yet carry, and the ruling itself expects roof geometry to be a
gap (section 4). Insulation and turn-down are the two that are computable today from published
fabric physics, and they are the two that are here.

WHY A MAXIMIN DRAW AND NOT A CLUSTERING
----------------------------------------
`demand_case_coverage.coverage` uses k-means, which finds the BEST partition into k cases. That is
the right tool for "how many are needed" and the wrong one for "which ones do I draw": k-means puts
its centres where the mass is, and the ruling's whole point is that the mass is not where the money
is. A greedy maximin draw takes, at each step, the candidate FARTHEST from everything already
drawn, which is the same sentence as "reject a candidate a drawn house would behave like" read from
the other end.

The two are reported together on purpose. K-means is the CEILING on variance covered at each N; the
gap between them is the price of drawing for difference, and the tail curve is what that price buys.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

AXES = ("annual_kwh", "kwh_per_degree_day", "solar_offset_share",
        "insulation_ceiling_kwh", "turndown_ceiling_kwh")

#: One degree off the thermostat. The turn-down ceiling is stated per degree because that is how the
#: published trials state it and because the ladder of behavioural rungs the ruling asks for is
#: built out of single degrees, not out of a chosen total.
TURNDOWN_C = 1.0

#: What "the tail" means here: the household-weighted top 1% of the population on an axis, which is
#: the coverage target the ruling sets ("99% of variance, INCLUDING TAILS") read as a population
#: share rather than as a variance share.
TAIL_QUANTILE = 0.99

#: An extreme, for the corner ledger: the top or bottom 5% of the population on one axis. Wider than
#: the tail above because a CORNER is a conjunction -- a point extreme on two axes at once -- and at
#: 1% per axis most conjunctions are empty for arithmetic reasons rather than physical ones.
CORNER_QUANTILE = 0.05

#: Equal-mass bands the tail is cut into. Ten, so a band is a tenth of one per cent of the
#: population -- fine enough that a draw cannot cover a tail by sitting at one end of it, coarse
#: enough that a 200,000-point sample still puts two hundred points in the smallest band.
TAIL_BANDS = 10

#: How much of a tail a draw must reach before the tail counts as covered. The
#: ruling sets 99% of variance "including tails" and does not set a separate tail number; 90% is a
#: CHOICE, stated as one, and the curve below is published so a different one can be read off it
#: rather than requiring a re-run.
TAIL_TARGET = 0.90

#: Sizes the draw is reported at. Geometric, because the interesting behaviour is at the low end and
#: an arithmetic ladder spends its resolution where the curve is flat.
NS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584)

#: Where the k-means comparison stops. It is a CEILING on the draw, not a rival sample, and past
#: this size it costs minutes per point to re-confirm a curve that flattened at 55.
KMEANS_CEILING_MAX = 377

LEDGER = PROJECT / "docs" / "design" / "visited_corner_ledger.json"


def output_space(grid=None, sample: int = 200_000, seed: int = 0) -> dict:
    """A household-weighted sample of the population in the five-axis output space.

    SAMPLED FOR THE SAME REASON THE COVERAGE CURVE IS: the full grid is 39.3 million (cell, house)
    pairs and a greedy maximin draw is quadratic in the candidate set. The sample is drawn WITH
    household weight, so a corner that one household in Britain occupies is one draw away from
    never being a candidate. That is a real limit of this method and it is a limit in the SAMPLING,
    not in the draw: `corners()` is computed on this same sample, so a conjunction rarer than one in
    two hundred thousand households reads as empty here whether or not Britain contains it.
    """
    import numpy as np

    from tools import demand_case_coverage as dcc

    grid = grid if grid is not None else dcc.demand_grid()
    params = np.asarray(grid["case_params"])
    hdd = np.asarray(grid["cell_hdd"])
    wind = np.asarray(grid["cell_wind"])
    solar_index = np.asarray(grid["cell_solar_index"])
    demand = np.asarray(grid["demand"])
    sensitivity = np.asarray(grid["sensitivity"])

    from simulation import fabric_physics as fp

    reference_solar = dcc._reference_solar_kwh_per_m2()
    hours = len(dcc.DOYS) * 24.0

    # THE RETROFIT LEG, from the same Household construction rather than a second one -- see
    # `house_cases(insulation_override=...)`. The ceiling is then a difference between two fabric
    # states of one model, which is the only reading under which it is a ceiling at all.
    _, full_params, _, _ = dcc.house_cases(insulation_override="FULL")
    full_params = np.asarray(full_params)

    # The turn-down leg is a difference in degree-days at one degree lower, so it needs the cell's
    # heating season re-integrated rather than a fraction of the level.
    winter_hdd_down = dcc._seasonal_hdd(
        _winter_temp_from_hdd(hdd), setpoint_c=dcc.SETPOINT_C - TURNDOWN_C)

    gross = sensitivity * hdd[:, None]
    solar = params[None, :, 3] * reference_solar * solar_index[:, None]
    internal = params[None, :, 4] * hours
    with np.errstate(divide="ignore", invalid="ignore"):
        offset_share = np.where(gross > 0.0, solar / np.maximum(gross, 1e-9), 0.0)

    retro = np.empty_like(demand)
    for i in range(full_params.shape[0]):
        fabric, raw_ach, volume, aperture, internal_kw = full_params[i]
        ach = np.maximum(raw_ach * (wind / fp.SAP_REFERENCE_WIND_MS), fp._MINIMUM_VENTILATION_ACH)
        hlc = (fabric + 0.33 * ach * volume) / 1000.0
        retro[:, i] = np.maximum(
            0.0, hlc * hdd * 24.0 - aperture * reference_solar * solar_index - internal_kw * hours)

    turndown = np.maximum(
        0.0, demand - np.maximum(0.0, sensitivity * winter_hdd_down[:, None] - solar - internal))

    values = np.stack([
        demand.ravel(),
        sensitivity.ravel(),
        offset_share.ravel(),
        np.maximum(0.0, demand - retro).ravel(),
        turndown.ravel(),
    ], axis=1)
    weights = np.asarray(grid["weights"]).ravel()

    keep = np.flatnonzero(weights > 0)
    values, weights = values[keep], weights[keep]
    rng = np.random.default_rng(seed)
    index = keep
    if len(values) > sample:
        pick = rng.choice(len(values), size=sample, replace=True, p=weights / weights.sum())
        values, weights, index = values[pick], np.ones(sample), keep[pick]
    return {"values": values, "weights": weights, "axes": AXES, "index": index,
            "n_cases": int(params.shape[0]), "case_params": params,
            "cell_hdd": hdd, "cell_wind": wind, "cell_solar_index": solar_index}


def input_space(space) -> dict:
    """The same sampled households, described by their INPUTS instead of by their behaviour.

    BUILT FROM THE SAMPLE'S OWN INDICES, not re-sampled, so the two descriptions are of exactly the
    same set of households -- a comparison between an input draw and an output draw made on two
    different samples would measure the sampling.

    Eight columns: the five fabric parameters of the house and the three drivers of its cell. That
    is the whole of what the world knows about a premise before it computes anything, which is what
    makes it the fair opponent for the output space rather than a straw one.
    """
    import numpy as np

    index = np.asarray(space["index"])
    cell = index // space["n_cases"]
    case = index % space["n_cases"]
    params = np.asarray(space["case_params"])[case]
    drivers = np.stack([np.asarray(space["cell_hdd"])[cell],
                        np.asarray(space["cell_wind"])[cell],
                        np.asarray(space["cell_solar_index"])[cell]], axis=1)
    return {"values": np.concatenate([params, drivers], axis=1), "weights": space["weights"],
            "axes": ("fabric_w_per_k", "raw_infiltration_ach", "volume_m3", "solar_aperture_m2",
                     "internal_gain_kw", "cell_degree_days", "cell_wind_ms", "cell_solar_index")}


def _winter_temp_from_hdd(hdd):
    """Invert `_seasonal_hdd` numerically, so the turn-down leg is integrated over the SAME cells.

    The grid hands back degree-days rather than the winter temperature they came from. Re-deriving
    the temperature by a monotone search costs nothing and keeps this function honest about what it
    needs; carrying a second copy of the cell temperatures would let the two legs of a difference
    come from different cells, which is the defect this whole atom is built to avoid.
    """
    import numpy as np

    from tools import demand_case_coverage as dcc

    probe = np.linspace(-5.0, 15.0, 401)
    table = dcc._seasonal_hdd(probe)
    order = np.argsort(table)
    return np.interp(np.asarray(hdd), table[order], probe[order])


def _standardise(values, weights):
    import numpy as np

    mean = np.average(values, axis=0, weights=weights)
    sd = np.sqrt(np.average((values - mean) ** 2, axis=0, weights=weights))
    return (values - mean) / np.where(sd == 0, 1.0, sd)


def select(z, n: int, seed: int = 0):
    """Greedy maximin: indices of `n` points, each the farthest from everything already drawn.

    THE REJECTION IS THE SELECTION, read from the other end. "Reject a candidate when a drawn house
    would behave the same" and "take the candidate least like anything drawn" pick out the same set;
    stating it as a maximum makes the stopping rule a COVERAGE question rather than a tolerance
    somebody chose.

    Seeded from a random point rather than from the centroid, because the ruling requires a fresh
    draw per life and a deterministic start would make every life's first houses identical.
    """
    import numpy as np

    rng = np.random.default_rng(seed)
    first = int(rng.integers(len(z)))
    chosen = [first]
    nearest = np.sum((z - z[first]) ** 2, axis=1)
    while len(chosen) < n:
        pick = int(np.argmax(nearest))
        if nearest[pick] <= 0.0:
            break
        chosen.append(pick)
        nearest = np.minimum(nearest, np.sum((z - z[pick]) ** 2, axis=1))
    return np.array(chosen)


def fill_radius(z, drawn) -> float:
    """The worst-covered point's distance to its nearest drawn point, in standardised units.

    THE QUANTITY THE DRAW ACTUALLY MAXIMISES, and it is not variance covered. Greedy maximin
    minimises this radius; k-means minimises within-cluster variance. Reporting the draw against
    the variance curve alone reads as maximin doing badly at its own job, when it is doing well at
    a different one -- so both are published. A radius of r means no household in Britain is more
    than r standardised units of behaviour away from a house the sample contains.
    """
    import numpy as np

    best = None
    for i in drawn:
        d = np.sum((z - z[i]) ** 2, axis=1)
        best = d if best is None else np.minimum(best, d)
    return round(float(np.sqrt(best.max())), 4)



def _variance_covered(z, weights, centres) -> float:
    import numpy as np

    total = float(np.sum(weights[:, None] * (z - np.average(z, axis=0, weights=weights)) ** 2))
    best = None
    for c in centres:
        d = np.sum((z - c) ** 2, axis=1)
        best = d if best is None else np.minimum(best, d)
    return round(1.0 - float(np.sum(weights * best)) / total, 4) + 0.0


def tail_coverage(values, weights, drawn) -> dict:
    """Per axis: the share of the population's top 1% that a drawn house actually sits in.

    THE TAIL IS CUT INTO TEN EQUAL-MASS BANDS and a band counts as represented when at least one
    drawn house falls in it. Zero when no house is in the tail at all; one when the draw has a house
    in every tenth of it. Monotone under a nested draw, bounded, and the same sentence the ruling
    uses -- "the share of the population's top 1% on each output represented".

    THREE READINGS WERE TRIED AND TWO WERE WRONG, and both are worth naming because each looked
    right and neither is fail-open.

    "Some drawn house is NEAREST to it" is fail-open: a mid-range house is nearest to every tail
    household when the draw contains no tail house at all, so the tail reads covered by nothing.

    "The share of tail mass whose nearest drawn house is ITSELF in the tail" fixes that and is NOT
    MONOTONE -- an ordinary house can take nearest-ness away from a tail house, so the figure falls
    as the draw grows. On the real population it went 0.997 at five houses to 0.025 at fifty-five,
    and the rule reading N off it reported five.

    "The share of the tail's own VARIANCE captured by drawn tail houses" is monotone and has a worse
    problem: with one centre at the edge of a tail, within-tail scatter exceeds the tail's variance
    about its own mean, so the figure goes NEGATIVE -- and a draw with a badly placed tail house
    then scores BELOW a draw with no tail house at all, which sorts the two states backwards.
    """
    import numpy as np

    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    out = {}
    for j, axis in enumerate(AXES):
        cut = _weighted_quantile(values[:, j], weights, TAIL_QUANTILE)
        in_tail = values[:, j] >= cut
        if not in_tail.any():
            out[axis] = None
            continue
        edges = [_weighted_quantile(values[in_tail, j], weights[in_tail], q)
                 for q in np.linspace(0.0, 1.0, TAIL_BANDS + 1)]
        band_mass = np.zeros(TAIL_BANDS)
        hit = np.zeros(TAIL_BANDS, dtype=bool)
        for b in range(TAIL_BANDS):
            lo, hi = edges[b], edges[b + 1]
            last = b == TAIL_BANDS - 1
            band = in_tail & (values[:, j] >= lo) & (
                (values[:, j] <= hi) if last else (values[:, j] < hi))
            band_mass[b] = weights[band].sum()
            hit[b] = bool(band[drawn].any())
        total = band_mass.sum()
        out[axis] = round(float(band_mass[hit].sum()) / float(total), 4) + 0.0 if total > 0 else None
    return out


def _weighted_quantile(values, weights, q: float) -> float:
    import numpy as np

    order = np.argsort(values)
    v, w = np.asarray(values)[order], np.asarray(weights)[order]
    cumulative = np.cumsum(w) / w.sum()
    return float(v[np.searchsorted(cumulative, q, side="left").clip(0, len(v) - 1)])


def corners(values, weights) -> dict:
    """Which conjunctions of extremes Britain actually contains, and how much mass each holds.

    A CORNER is a point in the top or bottom 5% on TWO OR MORE axes at once. Most of the 45 possible
    pairs are empty, and which ones are empty is the finding: an output space of five axes is not a
    five-dimensional box, it is a thin surface inside one, and a sample that tried to fill the box
    would spend most of its draws on houses that do not exist.
    """
    import collections

    import numpy as np

    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    flags = {}
    for j, axis in enumerate(AXES):
        high = values[:, j] >= _weighted_quantile(values[:, j], weights, 1.0 - CORNER_QUANTILE)
        low = values[:, j] <= _weighted_quantile(values[:, j], weights, CORNER_QUANTILE)
        flags[f"{axis}+"] = high
        flags[f"{axis}-"] = low

    names = list(flags)
    mass: dict = collections.Counter()
    total = float(weights.sum())
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            if names[a].rstrip("+-") == names[b].rstrip("+-"):
                continue
            both = flags[names[a]] & flags[names[b]]
            share = float(weights[both].sum()) / total
            if share > 0.0:
                mass[f"{names[a]} & {names[b]}"] = round(share, 6)
    return {"occupied": dict(mass.most_common()),
            "possible_pairs": len(names) * (len(names) - 2) // 2,
            "occupied_pairs": len(mass)}


def visited(drawn_values, drawn_weights, population_values, population_weights) -> list[str]:
    """The corner labels a drawn set actually occupies -- one run's entry in the ledger.

    Keyed to the POPULATION's cut points, not the draw's, or every draw visits its own corners by
    construction and the ledger becomes a tautology that always reads full.
    """
    import numpy as np

    population_values = np.asarray(population_values, dtype=float)
    drawn_values = np.asarray(drawn_values, dtype=float)
    flags = {}
    for j, axis in enumerate(AXES):
        hi = _weighted_quantile(population_values[:, j], population_weights, 1.0 - CORNER_QUANTILE)
        lo = _weighted_quantile(population_values[:, j], population_weights, CORNER_QUANTILE)
        flags[f"{axis}+"] = drawn_values[:, j] >= hi
        flags[f"{axis}-"] = drawn_values[:, j] <= lo
    names = list(flags)
    out = []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            if names[a].rstrip("+-") == names[b].rstrip("+-"):
                continue
            if bool((flags[names[a]] & flags[names[b]]).any()):
                out.append(f"{names[a]} & {names[b]}")
    return sorted(out)


def record_visit(labels: list[str], path: Path = LEDGER) -> dict:
    """Add one run's visited corners to the across-runs ledger and return it.

    THE LEDGER IS THE ONLY PART OF THIS THAT IS NOT A MEASUREMENT. The ruling is explicit that
    coverage is a property of the ENSEMBLE of runs and that the director does not want every house
    in every geography in one run, so what a run owes is its corners, and what steers the next run
    is which corners are still at zero.
    """
    ledger = {"visits": {}, "runs": 0}
    if path.is_file():
        ledger = json.loads(path.read_text(encoding="utf-8"))
    for label in labels:
        ledger["visits"][label] = ledger["visits"].get(label, 0) + 1
    ledger["runs"] = int(ledger.get("runs", 0)) + 1
    ledger["visits"] = dict(sorted(ledger["visits"].items()))
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ledger


def measurement(space=None, ns=NS, seed: int = 0) -> dict:
    """The two curves the ruling asks for, and therefore N.

    Curve one is variance covered against distinct houses drawn, reported for the maximin draw AND
    for the k-means ceiling at the same N. Curve two is tail coverage per axis. N is REPORTED --
    where both clear their target -- rather than chosen.
    """
    from tools import demand_case_coverage as dcc

    space = space if space is not None else output_space(seed=seed)
    values, weights = space["values"], space["weights"]
    z = _standardise(values, weights)

    drawn = select(z, max(ns), seed=seed)
    curve, tails, radius = {}, {}, {}
    for n in ns:
        if n > len(drawn):
            continue
        take = drawn[:n]
        curve[n] = _variance_covered(z, weights, z[take])
        radius[n] = fill_radius(z, take)
        tails[n] = tail_coverage(values, weights, take)

    # The k-means ceiling stops at KMEANS_CEILING_MAX. Beyond it the comparison costs more than it
    # tells: the optimal partition has already passed 99% by 55 and the interesting question above
    # that size is the TAIL, which k-means is not competing for. Said here rather than left as a
    # ragged column, because a curve that silently stops is read as a curve that ended.
    ceiling = dcc.coverage(values, weights,
                           [n for n in ns if n <= min(len(drawn), KMEANS_CEILING_MAX)],
                           seed=seed, sample=len(values))

    # THE RULING'S PREMISE, MEASURED ON BRITAIN RATHER THAN ASSERTED. The same algorithm, the same
    # households, the same size -- the only difference is whether the distance is computed on what
    # a house IS or on what it DOES. What this costs is allowed to come out smaller than the ruling
    # assumes; that is the point of measuring it.
    inputs = input_space(space)
    zi = _standardise(inputs["values"], weights)
    at = min(len(drawn), 233)
    on_inputs = select(zi, at, seed=seed)
    drawn_on_inputs = {
        "n": at,
        "output_variance_covered": _variance_covered(z, weights, z[on_inputs]),
        "output_fill_radius": fill_radius(z, on_inputs),
        "tail_covered": tail_coverage(values, weights, on_inputs),
        "corners_visited": len(visited(values[on_inputs], weights[on_inputs], values, weights)),
    }

    def first(predicate):
        return next((n for n in sorted(curve) if predicate(n)), None)

    n_variance = first(lambda n: curve[n] >= 0.99)
    n_tails = first(lambda n: all(v is not None and v >= TAIL_TARGET for v in tails[n].values()))
    reported = max(x for x in (n_variance, n_tails) if x is not None)
    return {
        "axes": list(AXES),
        "population_points": int(len(values)),
        "variance_covered": curve,
        "fill_radius": radius,
        "variance_covered_kmeans_ceiling": ceiling,
        "tail_covered": tails,
        "n_for_99pc_variance": n_variance,
        "n_for_90pc_of_every_tail": n_tails,
        "n_reported": reported,
        "corners": corners(values, weights),
        "drawn_on_inputs_instead": drawn_on_inputs,
        "drawn_on_outputs_at_same_n": {
            "n": at,
            "output_variance_covered": curve.get(at),
            "output_fill_radius": radius.get(at),
            "tail_covered": tails.get(at),
            "corners_visited": len(visited(values[drawn[:at]], weights[drawn[:at]],
                                           values, weights)),
        },
        "visited_by_this_draw": visited(values[drawn[:reported]], weights[drawn[:reported]],
                                        values, weights),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true", help="the two curves and N")
    ap.add_argument("--corners", action="store_true", help="which conjunctions of extremes exist")
    ap.add_argument("--record", action="store_true", help="add this draw's corners to the ledger")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    if args.measure:
        result = measurement(seed=args.seed)
        print(json.dumps(result, indent=2, default=str))
        if args.record:
            record_visit(result["visited_by_this_draw"])
        return 0
    if args.corners:
        space = output_space(seed=args.seed)
        print(json.dumps(corners(space["values"], space["weights"]), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
