"""The stock's EPC association, measured from DESNZ NEED rather than asserted.

REUSE: tools/need_stock_joint.py
CLASS: CUSTOM
INDEX: searched "need", "stock", "joint", "epc", "tilt", "association", "cross-tab".
       `simulation/premise_population.py` owns the joint and is the consumer; it held the tilt
       tables this replaces. `tools/weather_cell_weights.py` fits a different joint (households to
       cells) from different sources. Nothing else reads NEED.

WHY THIS EXISTS
---------------
`W2_21`, from the housing ruling section 3.1: *"the fitted joint of the quantities that carry the
variance, WITH THEIR PUBLISHED CORRELATIONS"*, and its named failure mode: *"an invented correlation
matrix where a published cross-tab exists -- the ruling forbids it and the small-area data is what
makes it unnecessary."*

`premise_population` built its seed joint as the independent product times two hand-written tilt
tables, and said so plainly: *"THE TILT MAGNITUDES ARE NOT ANCHORED. Only their direction is."* NEED
carries `PROP_TYPE x PROP_AGE_BAND x EPC` on one row per dwelling for 34,914 rated dwellings, so the
magnitudes are measurable and one of the directions turns out to be wrong.

WHAT THE MEASUREMENT FOUND
--------------------------
Lift is observed / (row x column) -- 1.00 means no association. Against the hand tilts:

    PRE-1930   band F/G   hand 5.0 and 8.0   measured 2.78     up to 2.9x too harsh
    PRE-1930   band C     hand 0.30          measured 0.59     2.0x too harsh
    POST-2000  band C     hand 1.90          measured 1.00     post-2000 is exactly average
    DETACHED   band A/B   hand 0.90          measured 1.21     THE DIRECTION IS WRONG

The last one is the finding. The hand table had detached homes slightly LESS likely to be A/B; they
are 1.21x MORE likely, because detached is bimodal -- old draughty rectories and new large efficient
houses sit in the same category. A tilt table whose only claim was its direction had a direction
wrong, and nothing could have caught it without the cross-tab.

THE ERA MAPPING IS ARITHMETIC ON PUBLISHED BOUNDARIES, NOT A JUDGEMENT
----------------------------------------------------------------------
NEED's `PROP_AGE_BAND` is coarser than this project's six eras: **1 = before 1930, 2 = 1930-1972,
3 = 1973-1999, 4 = 2000 or later** (DESNZ's own metadata). Three of the six eras sit inside one band;
three straddle a boundary. A straddling era takes the YEAR-WEIGHTED AVERAGE of the bands it spans --
1919-1944 is eleven years in band 1 and fifteen in band 2 -- which is arithmetic on the published
boundaries rather than a choice about which band it "really" is.

THE RESIDUAL, AND IT IS NOT SMALL
----------------------------------
**30.2% of NEED's dwellings have no EPC, and they are not missing at random.** Flats are 29.2% of
rated dwellings and 11.4% of unrated ones; post-2000 homes are 24.5% against 5.9%. An EPC exists
because a home was sold, let or newly built.

What that does and does not damage: the lifts here are CONDITIONAL structure, and the joint they seed
is raked onto the published marginals afterwards, so a biased marginal composition washes out. What
would not wash out is a home's EPC being systematically better or worse than an unrated home of the
SAME type and age -- and NEED cannot answer that, because an unrated home has no rating. Stated as
the residual rather than absorbed.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

NEED_CSV = Path.home() / ".cache" / "synthetic-enterprise" / "need_2026" / "anon2026_50k.csv"

#: NEED's six property types onto this project's four. Bungalow folds into DETACHED, which is the
#: fold `premise_population` already declares and for the reason it gives (a bungalow's thermal
#: signature -- large roof and ground floor for its floor area -- is nearest detached).
PROPERTY_TYPE = {
    "Detached": "DETACHED", "Bungalow": "DETACHED", "Semi detached": "SEMI_DETACHED",
    "End terrace": "TERRACED", "Mid terrace": "TERRACED", "Flat": "FLAT",
}

#: NEED reports A/B and F/G as pairs; this project bands them separately. A pair's lift applies to
#: both its members -- the alternative is to invent a split inside a bracket the source does not
#: resolve, which is the failure mode the ruling names.
EPC_CLASS = {"A/B": ("AB",), "C": ("C",), "D": ("D",), "E": ("E",), "F/G": ("F", "G")}

#: DESNZ metadata, verbatim: 1 = before 1930; 2 = 1930-1972; 3 = 1973-1999; 4 = 2000 or later.
AGE_BAND_YEARS = {"1": (1800, 1929), "2": (1930, 1972), "3": (1973, 1999), "4": (2000, 2030)}

#: This project's eras, as year spans, so the overlap with NEED's bands is computed and not chosen.
ERA_YEARS = {
    "PRE_1919": (1800, 1918), "ERA_1919_1944": (1919, 1944), "ERA_1945_1964": (1945, 1964),
    "ERA_1965_1980": (1965, 1980), "ERA_1981_2000": (1981, 2000), "POST_2000": (2001, 2030),
}


def _rows() -> list[dict]:
    if not NEED_CSV.is_file():
        raise FileNotFoundError(
            f"{NEED_CSV} is absent. The stock association is measured from DESNZ NEED and the "
            "alternative is a hand-written tilt table, which is what this replaced.")
    with NEED_CSV.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def era_band_weights() -> dict[str, dict[str, float]]:
    """{era: {NEED age band: share of the era's years in that band}}.

    Arithmetic on two published sets of boundaries. An era inside one band gets `{band: 1.0}`; one
    that straddles gets its years split, which is the only rule that needs no opinion about where a
    1919-1944 house "really" belongs.
    """
    out: dict[str, dict[str, float]] = {}
    for era, (elo, ehi) in ERA_YEARS.items():
        span = ehi - elo + 1
        weights = {}
        for band, (blo, bhi) in AGE_BAND_YEARS.items():
            overlap = max(0, min(ehi, bhi) - max(elo, blo) + 1)
            if overlap:
                weights[band] = overlap / span
        out[era] = weights
    return out


def measured_lifts(rows: list[dict] | None = None) -> dict:
    """Lift of each EPC band over independence, by age band and by property type.

    LIFT, NOT SHARE, because the seed is multiplied by the published marginals and then raked onto
    them. A share would double-count the marginal; a lift carries only the association, which is
    the part NEED knows and the published marginals do not.
    """
    rows = rows if rows is not None else _rows()
    rated = [r for r in rows if r["EPC"] in EPC_CLASS]
    n = len(rated)
    if n < 10_000:
        raise ValueError(f"only {n} rated dwellings in NEED; the lifts would be noise")

    by_age = collections.Counter(r["PROP_AGE_BAND"] for r in rated)
    by_type = collections.Counter(PROPERTY_TYPE[r["PROP_TYPE"]] for r in rated)
    by_epc = collections.Counter(r["EPC"] for r in rated)
    age_epc = collections.Counter((r["PROP_AGE_BAND"], r["EPC"]) for r in rated)
    type_epc = collections.Counter((PROPERTY_TYPE[r["PROP_TYPE"]], r["EPC"]) for r in rated)

    def lift(joint, row_counts, key):
        out = {}
        for epc_class, bands in EPC_CLASS.items():
            expected = (row_counts[key] / n) * (by_epc[epc_class] / n)
            value = (joint[(key, epc_class)] / n) / expected if expected else 0.0
            for band in bands:
                out[band] = round(value, 4)
        return out

    per_band = {age: lift(age_epc, by_age, age) for age in sorted(by_age)}
    weights = era_band_weights()
    by_era = {}
    for era, bands in weights.items():
        merged: dict[str, float] = collections.defaultdict(float)
        for band, share in bands.items():
            for epc, value in per_band[band].items():
                merged[epc] += share * value
        by_era[era] = {k: round(v, 4) for k, v in merged.items()}

    unrated = [r for r in rows if r["EPC"] == "No EPC"]
    return {
        "source": "DESNZ NEED anonymised 2026 sample, 50,000 dwellings",
        "rated_dwellings": n,
        "unrated_dwellings": len(unrated),
        "unrated_share": round(len(unrated) / len(rows), 4),
        "by_age_band": per_band,
        "by_era": by_era,
        "by_property_type": {t: lift(type_epc, by_type, t) for t in sorted(by_type)},
        "era_band_weights": weights,
        "unrated_composition_ratio": _unrated_ratio(rated, unrated),
    }


def _unrated_ratio(rated: list[dict], unrated: list[dict]) -> dict:
    """How the unrated 30% differ in composition -- the residual, quantified.

    Published because "30% have no EPC" is a caveat and "flats are 2.6x under-represented among
    them" is a bound. A reader can decide whether the association below is usable; they cannot
    decide that from a percentage.
    """
    out: dict[str, dict[str, float]] = {}
    for column, label in (("PROP_TYPE", "property_type"), ("PROP_AGE_BAND", "age_band")):
        a = collections.Counter(r[column] for r in rated)
        b = collections.Counter(r[column] for r in unrated)
        out[label] = {
            k: round((b[k] / len(unrated)) / (a[k] / len(rated)), 3)
            for k in sorted(set(a) | set(b)) if a[k]
        }
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lifts", action="store_true", help="print the measured association")
    args = ap.parse_args(argv)
    if args.lifts:
        print(json.dumps(measured_lifts(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
