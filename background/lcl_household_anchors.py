"""EXTERNAL ANCHORS for the two-level test, derived from a real household panel.

Serves `H_GAP_fabric_belief_truth_gap` L2->L3, against the three cells that
`background/fabric_gap_ledger.py` has carried as UNVALIDATED since it was built
(`docs/design/PREMISE_TWO_LEVEL_TEST_HARNESS_SPEC.md` L1.4 and L2.4, both filed
`AnchorStatus.NEED`).

ONE OF THE TWO ANCHORS IS IN USE. READ THIS BEFORE REUSING THE OTHER.
=====================================================================
`LCL_SCALE_SPREAD_P90_P10_FLOOR` (L2.4) is live: it fires on the real generator
and it is reachable, both proven in `tests/harness/test_premise_two_level.py`.

`LCL_WEEKDAY_WEEKEND_TV_FLOOR` (L1.4) is derived here and DELIBERATELY NOT WIRED
INTO A BAND. It was, for about an hour on 2026-08-09, and its own R15 mutation
took it back out: relabelling the day-type calendar at random — the mutation the
spec names for this cell — left NOT ONE of 600 home-permutation samples below the
floor (null median 0.0715, null minimum 0.0378, floor 0.0262). The statistic is
biased upward at the coupled run's 120-day window, where 35 weekend days and 85
weekday days are small enough that two arbitrary subsets of the SAME home differ
by about as much as a real household's weekday differs from its weekend over a
full year. The anchor is sound; applying it across window lengths is not. The
derivation is kept, un-wired, because the fix is to null-correct the STATISTIC
(separation minus the median of k randomised relabellings) and this number is
half of what that build needs.

PURPOSE, GUARANTEES, WHY — stated first (OPS1 standard) or the mechanism is deleted
====================================================================================

**Purpose.** Turn two MEASURED-BUT-NOT-JUDGED cells into JUDGED ones, by deriving
their bands from a real panel of individual UK households rather than from an
invented number.

**Guarantee.** Every threshold this module exports is a function of
`data/lake/lcl_household_load_shapes_2013/household_shapes_and_archetype_2013.csv`
and of nothing else — no simulation output, no company belief, no generator
parameter is an input to any band here. `tests/harness/test_lcl_household_anchors.py`
RE-DERIVES each exported constant from the raw CSV with independent inline
arithmetic (not by calling the functions below) and fails if they disagree, so the
constants are auditable facts rather than asserted ones.

**Why it is needed, and why now.** `observed-in-code`: the two cells' band notes
say, in their own words, that giving them an invented threshold "would make the
suite look rigorous while being unfalsifiable". That refusal was right and it had a
price — an unanchored cell is reported and never judged, so a generator can be
arbitrarily wrong on it and the suite still reads green. The atom's own L2 residual
named the missing anchors as an L3 blocker. The panel below was already in the
repo, fetched and documented for a different workload
(`docs/market_research/hh_load_shape_clustering_2026.md`), and it measures exactly
the two quantities the cells needed.

THE PANEL, AND WHAT IT IS NOT
-----------------------------
Low Carbon London (UK Power Networks, published via the London Datastore under
CC-BY; dataset page cited in the research doc above). 304 households with >= 85%
half-hourly coverage of calendar year 2013, real metered electricity. Per household
the derived file carries `mean_daily_kwh` and two normalised 48-vectors — the mean
weekday shape (`wd_0..wd_47`) and the mean weekend shape (`we_0..we_47`).

Stated so a future reader can supersede these anchors rather than inherit them
silently. This panel is:

* **London-only, 2013, electricity-only.** The registered NEED for L2.4 was the
  DESNZ National Energy Efficiency Data-Framework (EPC-linked metered annual
  consumption, stratified by property type and floor-area band) and for L1.4 was
  SERL. This is neither. It is a real measurement of the same two quantities, and
  a stratified national source should REPLACE it when one is fetched.
* **not property-type stratified**, so it cannot say whether the model's spread is
  wrong in the right places — only whether it is the right size overall.
* **estimated with a different normalisation than the model's.** The panel averages
  each household's half-hourly kWh over all 2013 weekdays and then normalises the
  mean to sum to 1; `fabric_gap_ledger.weekday_weekend_separation` normalises each
  DAY and then averages the normalised days. Both estimate the same shape; they are
  not identical estimators, and they differ most for a household whose daily total
  swings hard. This is why the L1.4 floor is taken from the panel's LOW TAIL rather
  than near its centre — the loose direction, chosen deliberately.
* **a full year against the model's 120-day window** (the coupled run measures
  2022-01-01..04-30). For L2.4 this cuts the CONSERVATIVE way: a winter-weighted
  window amplifies heating-driven differences between homes, so if anything the
  model's window should be MORE dispersed than the panel's, not less.

HOW A THRESHOLD IS CHOSEN — the rule, stated before the numbers (R12)
---------------------------------------------------------------------
Not "whatever the model happens to clear". The rule is fixed and mechanical:

* a **population-level** statistic (L2.4) gets the 5th percentile of a
  seeded bootstrap over the panel — i.e. the model must be at least as dispersed as
  the low end of what this panel's own sampling error admits. Sampling uncertainty
  is a real reason to loosen a band; the model's convenience is not.
* a **per-home floor** (L1.4) is taken at the panel's own low tail (its 5th
  percentile, bootstrapped the same way), and the population violation RATE the
  cell tolerates is then set to 10% — double the 5% that the anchor itself implies,
  because by construction 5% of REAL homes sit below their own panel's P05 and a
  band that fails a generator for reproducing that would be measuring nothing.

The live threshold is not knife-edge against the current generator, and that is
stated rather than hoped: on the drawn n=200 population the model reads 1.80
against the L2.4 threshold of 4.88 — a factor of 2.7, so every tolerance the rule
above admits lands on the same verdict. A band whose verdict flips under a
defensible change of tolerance would be a tuned band, and R4 — diagnose the
mechanism — would apply instead of a threshold move.

WHAT THIS EPISODE IS WORTH KEEPING FOR (the generalisable half)
---------------------------------------------------------------
An anchor is a number AND a window. Both bands here came off the same panel, by
the same rule, on the same day; one is live and one is fail-open, and the only
difference is that the L2.4 statistic (a ratio between homes) is insensitive to
how many days each home was watched for, while the L1.4 statistic (a distance
between two subsets of one home's days) is not. Nothing in the anchor's own
provenance says which kind you have. The mutation says.
"""

from __future__ import annotations

import csv
import math
import random
from functools import lru_cache
from pathlib import Path
from typing import Sequence

PROJECT_DIR = Path(__file__).resolve().parents[1]
LCL_PANEL_PATH = (
    PROJECT_DIR
    / "data"
    / "lake"
    / "lcl_household_load_shapes_2013"
    / "household_shapes_and_archetype_2013.csv"
)

PERIODS_PER_DAY = 48

#: Provenance carried WITH the numbers, so a band printed in a ledger row can be
#: traced without opening this file.
ANCHOR_SOURCE = (
    "Low Carbon London (UK Power Networks, London Datastore, CC-BY): 304 real "
    "households, >=85% half-hourly coverage of calendar 2013, electricity. Derived "
    "panel data/lake/lcl_household_load_shapes_2013/"
    "household_shapes_and_archetype_2013.csv; method "
    "docs/market_research/hh_load_shape_clustering_2026.md"
)

#: Bootstrap settings. Fixed, named and exported because a threshold derived from a
#: resample is only reproducible if the resampling is (C-S2: a named seeded stream).
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260809
BOOTSTRAP_QUANTILE = 0.05


class AnchorUnavailable(RuntimeError):
    """The panel could not be read. An unavailable check is a FAILED check (R15),
    so this RAISES rather than returning a default that would silently become the
    band."""


def _quantile(values: Sequence[float], q: float) -> float:
    """Linear-interpolation quantile — the SAME convention as
    `fabric_gap_ledger.scale_spread`, because two quantile conventions across a
    band and the statistic it judges is a difference nobody would ever see."""
    ordered = sorted(values)
    if not ordered:
        raise AnchorUnavailable("no values to take a quantile of")
    pos = q * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


@lru_cache(maxsize=1)
def load_panel(path: str | None = None) -> tuple[dict[str, object], ...]:
    """The panel, as rows. Cached because every anchor below reads the same file.

    Every failure mode RAISES. A panel that is missing, empty, short of the columns
    the anchors need, or carrying a non-finite consumption figure cannot produce a
    band, and returning something anyway would put an unfounded number into a
    control's threshold — the fail-open direction.
    """
    p = Path(path) if path else LCL_PANEL_PATH
    if not p.exists():
        raise AnchorUnavailable(f"the LCL anchor panel is not on disk at {p}")
    with p.open() as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise AnchorUnavailable(f"{p} has no households in it")
    required = ["mean_daily_kwh"] + [f"wd_{i}" for i in range(PERIODS_PER_DAY)] + [
        f"we_{i}" for i in range(PERIODS_PER_DAY)
    ]
    missing = [c for c in required if c not in rows[0]]
    if missing:
        raise AnchorUnavailable(
            f"{p} is missing {len(missing)} column(s) the anchors need, "
            f"first {missing[0]!r}"
        )
    return tuple(rows)  # type: ignore[arg-type]


def panel_daily_kwh(path: str | None = None) -> tuple[float, ...]:
    """Each household's mean daily electricity consumption."""
    values = []
    for row in load_panel(path):
        v = float(row["mean_daily_kwh"])  # type: ignore[arg-type]
        if not math.isfinite(v) or v <= 0.0:
            raise AnchorUnavailable(
                f"household {row.get('LCLid')!r} has a non-positive or non-finite "
                "daily consumption; a panel that cannot be trusted cannot set a band"
            )
        values.append(v)
    return tuple(values)


def panel_weekday_weekend_separation(path: str | None = None) -> tuple[float, ...]:
    """Each household's weekday-vs-weekend total-variation distance.

    The SAME statistic as `fabric_gap_ledger.weekday_weekend_separation` —
    0.5 * sum|weekday_shape - weekend_shape| over two normalised 48-vectors — so
    the band and the thing it judges are the same measurement. The two estimators
    of the underlying shapes differ, and that difference is declared in this
    module's docstring rather than hidden here.
    """
    out = []
    for row in load_panel(path):
        wd = [float(row[f"wd_{i}"]) for i in range(PERIODS_PER_DAY)]  # type: ignore[arg-type]
        we = [float(row[f"we_{i}"]) for i in range(PERIODS_PER_DAY)]  # type: ignore[arg-type]
        for vec, name in ((wd, "weekday"), (we, "weekend")):
            if not all(math.isfinite(x) for x in vec):
                raise AnchorUnavailable(
                    f"household {row.get('LCLid')!r} has a non-finite {name} shape"
                )
            if abs(sum(vec) - 1.0) > 1e-6:
                raise AnchorUnavailable(
                    f"household {row.get('LCLid')!r}'s {name} shape sums to "
                    f"{sum(vec):.6f}, not 1.0 — this file is supposed to be normalised, "
                    "and a total-variation distance between un-normalised vectors is "
                    "not the statistic the band judges"
                )
        out.append(0.5 * sum(abs(a - b) for a, b in zip(wd, we)))
    return tuple(out)


def bootstrap_low_quantile(
    values: Sequence[float],
    statistic,
    *,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
    quantile: float = BOOTSTRAP_QUANTILE,
) -> float:
    """The low end of what this panel's own sampling error admits for `statistic`.

    `statistic` maps a resampled panel to one number. Deterministic given `seed`
    (C-S2), and the seed is a named constant rather than a literal at the call site
    so a threshold cannot be shifted by quietly reseeding.
    """
    if len(values) < 2:
        raise AnchorUnavailable("a bootstrap over fewer than two households is theatre")
    rnd = random.Random(seed)
    n = len(values)
    draws = [statistic([rnd.choice(values) for _ in range(n)]) for _ in range(resamples)]
    return _quantile(draws, quantile)


def _p90_over_p10(values: Sequence[float]) -> float:
    return _quantile(values, 0.90) / _quantile(values, 0.10)


def derive_scale_spread_floor(path: str | None = None) -> float:
    """L2.4's band: how far apart real homes' consumption levels are."""
    return bootstrap_low_quantile(panel_daily_kwh(path), _p90_over_p10)


def derive_weekday_weekend_floor(path: str | None = None) -> float:
    """L1.4's per-home band: how alike a real home's weekday and weekend can be."""
    return bootstrap_low_quantile(
        panel_weekday_weekend_separation(path),
        lambda s: _quantile(s, BOOTSTRAP_QUANTILE),
    )


# ---------------------------------------------------------------------------
# THE FROZEN CONSTANTS
# ---------------------------------------------------------------------------
#
# Frozen rather than derived at import, for two reasons and neither is speed alone:
# a band that recomputes itself from a file every import is a band that CHANGES
# when the file does, silently, and the resulting ledger row would carry a
# threshold nobody chose. Freezing makes the number a decision with a date on it.
# `tests/harness/test_lcl_household_anchors.py` re-derives both from the raw CSV
# with independent inline arithmetic and fails on any drift, so freezing costs no
# auditability.
#
# Derived 2026-08-09 from the panel above, at BOOTSTRAP_SEED/BOOTSTRAP_RESAMPLES.

#: L2.4 — P90/P10 of household consumption. Panel point estimate 5.3769
#: (IQR ratio 2.4566); this is the bootstrap P05 of that ratio.
LCL_SCALE_SPREAD_P90_P10_FLOOR = 4.8807

#: L1.4 — per-home weekday/weekend total-variation distance. Panel median 0.0724,
#: P05 0.0279; this is the bootstrap P05 of that P05.
LCL_WEEKDAY_WEEKEND_TV_FLOOR = 0.0262

#: The population violation rate the L1.4 floor tolerates — see the rule in the
#: module docstring. 5% of the anchor panel's own households sit below its P05.
LCL_WEEKDAY_WEEKEND_VIOLATION_RATE = 0.10
