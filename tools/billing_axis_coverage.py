"""Does the demand sample span BILLING and COMMERCIAL complexity, per axis, measured.

REUSE: tools/billing_axis_coverage.py
CLASS: CUSTOM
INDEX: searched "billing", "commercial", "axis", "coverage", "payment", "meter", "tariff",
       "uncounted", "span".
       `tools/demand_vector_coverage.py` sizes the sample against the DEMAND vector and already
       enumerates what that N is blind to in `UNCOUNTED_AXES`. It is imported rather than copied,
       both for the population it generates and for that list -- this module adds no second
       enumeration of what is missing, because two lists of the same absence diverge inside a month.
       `tools/reduction_dimension.py` supplies `declare`, and the declaration below IS the finding
       in machine-readable form. `tools/demand_case_coverage.py` is the scalar predecessor and
       answers a different question. Nothing anywhere measures the BILLING axes against the sample.

WHY THIS EXISTS
---------------
`DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07`, section 4, verbatim:

    "A household is therefore more than usage and shape. It needs a meter type and read pattern, a
     payment method, a tariff with its dates, a move history and a credit position -- the things
     that make a bill right or wrong. And a sample sized against the demand vector may not be sized
     against billing complexity... Whether the demand sample spans that is an OPEN MEASUREMENT, NOT
     AN ASSUMPTION."

**The answer may be "no", and "no" is the deliverable.** The canon offers two acceptable outcomes --
spanned, or named as an uncounted dimension -- and the failure mode is neither of them: it is the
sample being sized on demand and read as if it were sized on billing.

WHAT THE ANSWER IS, TODAY
-------------------------
Four of the five axes are ABSENT from the drawn sample: no field carries them, so no figure about
them can be computed at any sample size. The fifth, payment method, is carried -- and is still not
spanned, for two independent reasons that the record states separately because they have different
remedies:

  * IT CARRIES TWO CATEGORIES AND THE WORLD HAS THREE. Direct debit is anchored (DESNZ QEP);
    the prepayment-versus-standard-credit split of the remainder is recorded in ASSUMPTIONS.md as
    NOT FOUND in the published commentary. A third category cannot be drawn from a share nobody
    published, and inventing it is the exact move this project keeps paying for.
  * ITS MARGIN AGREES WITH THE ANCHOR BY CONSTRUCTION. The sample draws payment method FROM
    `DD_SHARE_ELEC`, so the observed share matching the published one is arithmetic and not
    evidence. That is reported as `agrees_by_construction`, and a control refuses any reading of it
    as fidelity. A census that scored this as a pass would be a control that cannot fail.

So the honest per-axis answer is one CARRIED-BUT-NOT-SPANNED and four UNCOUNTED, and the N on the
demand page is a floor for a second reason on top of the one already published there.

WHY THE CANON DOCUMENT IS PARSED RATHER THAN TRANSCRIBED
--------------------------------------------------------
The axes are the canon's and are not this module's to invent or to freeze. A hand-typed copy of the
list is a copy that stays green on the day the director adds a sixth axis -- which is exactly the
day the census needs to go red. So `canon_named_axes` reads the sentence out of the document and
`axis_records` refuses when it names something no axis here covers. The refusal names the phrase.

WHAT THIS CANNOT DO, STATED SO IT IS NOT READ AS COVERAGE
----------------------------------------------------------
It measures the demand SAMPLE. The live book that the company actually serves carries a payment
method, a meter type and a tariff type on each drawn account (`simulation.population_draw`), and
those are a different population with a different owner. Whether the served book spans the axes is
a question this instrument does not answer and must not be quoted for.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import demand_vector_coverage as dvc  # noqa: E402  (after the path fix)
from tools.reduction_dimension import declare  # noqa: E402

#: The canon document this census answers to, and the three places a staged document lives across
#: its life. Resolved rather than pinned to `docs/staging/`: the staging protocol MOVES a document
#: to `done/` when it is worked, and a control that reads one directory goes green-by-absence on
#: the day the work it grades is filed. Absence is a REFUSAL here, never an empty answer.
CANON_DOCUMENT = "DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07.md"
_CANON_DIRECTORIES = ("docs/staging", "docs/staging/done", "docs/staging/in_progress")

#: The canon's own sentence, located by its opening words and terminated by the em-dash clause. The
#: list is English prose -- "A, B, C, D and E" -- so the comma split is done first and the LAST
#: comma-part is split once more on " and ". Splitting the whole string on " and " would cut
#: "meter type and read pattern" in half, which is one axis and not two.
_NEEDS_SENTENCE = re.compile(r"It needs (.+?)\s+—")
_ARTICLE = re.compile(r"^(a|an|the)\s+", re.I)


class UncoveredCanonAxis(ValueError):
    """The canon names a billing axis the census does not cover. The message names the phrase."""


class CanonDocumentMissing(FileNotFoundError):
    """The canon cannot be read, so the axis list cannot be established. Fails closed."""


@dataclass(frozen=True)
class BillingAxis:
    """One of the canon's five, and what would have to be true for the sample to span it."""

    key: str
    #: The canon's own words for it, and the join between this table and the parsed sentence.
    canon_phrase: str
    #: The field names in the generated population that would CARRY this axis. Probed against the
    #: population the sample is actually drawn as, never asserted -- a field list that says what
    #: ought to be there is a list that reads as coverage.
    sample_fields: tuple[str, ...]
    #: The entries of `dvc.UNCOUNTED_AXES` that stand for this axis when it is absent. There is one
    #: enumeration of the absence in this repository and it is that one.
    uncounted_as: tuple[str, ...]
    #: How many categories the PUBLISHED record establishes the world has. `None` where the record
    #: establishes no partition at all, which is a different answer from "we did not look".
    categories_in_the_world: Optional[int]
    #: The published population figure and where it is reached, or `None` with the reason named.
    population: Optional[Callable[[], dict]]
    #: True when the sample DRAWS this axis from the same published constant the census would score
    #: it against, so agreement is arithmetic. Named per axis rather than inferred.
    drawn_from_the_anchor: bool = False


def _direct_debit_share() -> dict:
    """The published direct-debit share, REACHED rather than copied.

    Reached through `simulation.population_draw.DD_SHARE_ELEC` -- the same constant the sample draws
    from -- so a change to the anchor moves both the sample and the figure it is scored against, and
    a test can perturb the source to prove this is a derivation and not a transcribed literal.
    """
    from simulation.population_draw import DD_SHARE_ELEC

    return {
        "category": "direct_debit",
        "share": float(DD_SHARE_ELEC),
        "source": ('DESNZ "Quarterly Energy Prices: June 2026", payment methods section '
                   "(end-March 2026): direct debit 72% of standard electricity customers, 75% of "
                   "gas; via docs/market_research/ASSUMPTIONS.md"),
        "reached_at": "simulation.population_draw.DD_SHARE_ELEC",
    }


#: The year the smart-meter penetration figure is read at. 2024 is the last OBSERVED point of the
#: DESNZ series `simulation.premise_population` interpolates; asking for a later year returns the
#: series held flat, which would publish an extrapolation as a measurement.
SMART_PENETRATION_YEAR = 2024


def _smart_meter_share() -> dict:
    """The published share of premises with a smart meter, reached through the world's own series."""
    from simulation.premise_population import smart_meter_penetration

    return {
        "category": "smart_meter_installed",
        "share": float(smart_meter_penetration(SMART_PENETRATION_YEAR)),
        "source": ("DESNZ Q4 2024 Smart Meters Statistics Table 5a: 10.6% (2016) to 68.9% (2024) "
                   f"of premises, read at {SMART_PENETRATION_YEAR}"),
        "reached_at": "simulation.premise_population.smart_meter_penetration",
    }


def _actively_chosen_tariff_share() -> dict:
    """The published share of households on an actively-chosen rather than a default tariff.

    ANCHORS THE CHOICE AND NOT THE DATES, and that half-answer is the point. Ofgem's stock split
    says what proportion of accounts sit on a tariff they chose; nothing published here establishes
    the distribution of tariff START DATES or term lengths, which is the other half of the canon's
    "a tariff with its dates". The record says so rather than letting one figure stand for both.
    """
    from simulation.household_segments import ENGAGEMENT_POPULATION_SHARE, EngagementLevel

    return {
        "category": "actively_chosen_tariff",
        "share": float(ENGAGEMENT_POPULATION_SHARE[EngagementLevel.ACTIVE]),
        "source": ("Ofgem Retail Market Indicators, October 2025 stock split: 45.1% of "
                   "non-prepayment domestic electricity accounts on actively-chosen tariffs, "
                   "54.9% on default; ratified as the archetype shares by director console "
                   "2026-07-22. Anchors the CHOICE margin only -- no published figure establishes "
                   "the distribution of tariff start dates or term lengths"),
        "reached_at": "simulation.household_segments.ENGAGEMENT_POPULATION_SHARE",
    }


#: THE SUBJECT VECTOR OF THIS CENSUS, and it is the canon's list rather than the demand vector. It
#: lives here rather than beside `DEMAND_VECTOR` in `reduction_dimension` because exactly one claim
#: in this repository is a claim about it; the argument for hoisting a vector is that several claims
#: would otherwise spell it differently, and there are not several.
CANON_AXES = (
    BillingAxis(
        key="meter_type_and_read_pattern",
        canon_phrase="meter type and read pattern",
        # `smart_meter` and `meter_type` are what the DRAWN BOOK calls it
        # (`simulation.population_draw.SyntheticCustomer.smart_meter`), so if the demand sample ever
        # gains the axis it will arrive under one of these names rather than a new one.
        sample_fields=("meter_type", "smart_meter", "read_pattern"),
        uncounted_as=("meter_read_pattern",),
        # Two, and the split is what a bill is computed FROM: a meter that settles half-hourly and
        # one read quarterly on an estimate are the canon's own example of two identical-consumption
        # households that are entirely different to bill.
        categories_in_the_world=2,
        population=_smart_meter_share,
    ),
    BillingAxis(
        key="payment_method",
        canon_phrase="payment method",
        sample_fields=("payment_method",),
        uncounted_as=("payment_method_third_category",),
        # THREE, AND THE THIRD IS WHY THIS AXIS IS NOT SPANNED DESPITE BEING CARRIED. Direct debit,
        # prepayment and standard credit are three different mechanics -- the published record
        # establishes that all three exist and gives the size of only the first.
        categories_in_the_world=3,
        population=_direct_debit_share,
        drawn_from_the_anchor=True,
    ),
    BillingAxis(
        key="tariff_and_dates",
        canon_phrase="tariff with its dates",
        sample_fields=("tariff_type", "tariff_start", "tariff_end"),
        uncounted_as=("tariff_and_dates",),
        categories_in_the_world=2,
        population=_actively_chosen_tariff_share,
    ),
    BillingAxis(
        key="move_history",
        canon_phrase="move history",
        sample_fields=("move_history", "moves", "occupancy_start"),
        uncounted_as=("move_history",),
        # NOT ESTABLISHED, and `None` is the honest entry rather than a plausible rate. Nothing in
        # ASSUMPTIONS.md or the commons establishes the distribution of domestic home moves per
        # account-year, so there is no partition to score the sample against even if it carried one.
        categories_in_the_world=None,
        population=None,
    ),
    BillingAxis(
        key="credit_position",
        canon_phrase="credit position",
        sample_fields=("credit_position", "arrears_balance_gbp", "credit_score"),
        uncounted_as=("arrears_position", "credit_position"),
        # NOT ESTABLISHED as a population partition. ASSUMPTIONS.md carries a directional context
        # figure -- about 75% of a GBP 4.43bn domestic debt stock sits with customers on no
        # repayment plan -- which is a share of MONEY and not a share of HOUSEHOLDS, and the two are
        # not the same quantity. Using it here would be dividing two numbers whose ratio is not one.
        categories_in_the_world=None,
        population=None,
    ),
)

#: The 95% two-sided normal deviate, for the interval a share of this sample size earns.
Z_95 = 1.96

#: The verdicts, and the set is closed. `SPANNED` is reachable and is not reached today; the tests
#: prove it can be, because a census whose only attainable answer is "no" is not a measurement.
VERDICTS = ("SPANNED", "CARRIED_NOT_SPANNED", "ABSENT")


def canon_path(root: Path | None = None) -> Path:
    """Where the canon document is, or a refusal naming every place that was asked."""
    root = root or PROJECT
    asked = []
    for directory in _CANON_DIRECTORIES:
        candidate = root / directory / CANON_DOCUMENT
        asked.append(str(candidate.relative_to(root)))
        if candidate.is_file():
            return candidate
    raise CanonDocumentMissing(
        f"{CANON_DOCUMENT} is in none of {asked}. The billing axes are the canon's list and this "
        f"census cannot establish them without it, so it refuses rather than reporting on a list "
        f"of its own.")


def canon_named_axes(text: str) -> tuple[str, ...]:
    """The billing axes the canon's section 4 sentence names, in its own words.

    A FLOOR ROW IN `substring_source_scan_baseline.json`, WITH ITS REASON HERE. The census that
    refuses a control reading Python source as TEXT flags this function and `axis_records`, because
    it fails closed when it cannot establish what a `read_text()` is reading. THE SUBJECT IS A
    MARKDOWN DOCUMENT -- the director's canon -- and there is no parse tree to route it through;
    `tools/python_code_text.py` is the remedy for Python and would be a category error here. That is
    the dismissal the baseline's own note names, recorded beside the code rather than only in the
    register, so the next reader can retire the row if the subject ever changes.
    """
    match = _NEEDS_SENTENCE.search(text)
    if not match:
        raise UncoveredCanonAxis(
            "the canon's \"It needs ...\" sentence was not found, so the axis list cannot be read "
            "from the document. A census that fell back on its own list here would be grading the "
            "canon against itself.")
    parts = [p.strip() for p in match.group(1).split(",")]
    tail = parts.pop().split(" and ")
    # "meter type and read pattern" is ONE axis: only the final comma-part carries the list's "and".
    parts.extend(t.strip() for t in tail)
    return tuple(_ARTICLE.sub("", p).strip() for p in parts if p.strip())


def _sample_carrier(population: dict, axis: BillingAxis) -> Optional[str]:
    """The field in the drawn population that carries this axis, or None. Probed, not declared."""
    for field in axis.sample_fields:
        if field in population:
            return field
    return None


def _share_interval(share: float, n: int) -> dict:
    """What a share of this sample size earns, and what size the tolerance would cost.

    `half_width_95` is the interval the sample's own n earns on the observed share.
    `n_for_tolerance` is the n at which that half-width falls to `dvc.DISTRIBUTION_TOLERANCE` --
    the same bar the demand measurement uses, so the two numbers are on one clock.
    """
    variance = share * (1.0 - share)
    return {
        "n": n,
        "half_width_95": (Z_95 * math.sqrt(variance / n)) if n > 0 else None,
        "n_for_tolerance": math.ceil((Z_95 / dvc.DISTRIBUTION_TOLERANCE) ** 2 * variance),
        "tolerance": dvc.DISTRIBUTION_TOLERANCE,
    }


def axis_records(population: dict, *, canon_text: str) -> list[dict]:
    """One record per canon axis: carried or not, against what figure, and what N it earns."""
    named = canon_named_axes(canon_text)
    covered = {a.canon_phrase for a in CANON_AXES}
    uncovered = [phrase for phrase in named if phrase not in covered]
    if uncovered:
        raise UncoveredCanonAxis(
            f"the canon names {uncovered} and no axis in CANON_AXES covers it. An axis added to the "
            f"canon and not to the census is the one thing this census must not survive: add the "
            f"axis, with the field that would carry it and the published figure or the named gap.")
    dropped = [a.canon_phrase for a in CANON_AXES if a.canon_phrase not in named]
    if dropped:
        raise UncoveredCanonAxis(
            f"the census covers {dropped}, which the canon's sentence no longer names. The list is "
            f"the canon's; reconcile against the document rather than keeping a private copy.")

    records = []
    for axis in CANON_AXES:
        carrier = _sample_carrier(population, axis)
        figure = axis.population() if axis.population else None
        record = {
            "axis": axis.key,
            "canon_phrase": axis.canon_phrase,
            "carried_by": carrier,
            "population_figure": figure,
            "categories_in_the_world": axis.categories_in_the_world,
            "categories_in_the_sample": None,
            "observed": None,
            "n_the_answer_earns": None,
            "agrees_by_construction": axis.drawn_from_the_anchor and carrier is not None,
            "uncounted_as": list(axis.uncounted_as),
            "why": None,
        }
        if carrier is None:
            record["verdict"] = "ABSENT"
            record["why"] = (
                f"no field of the drawn sample carries it (looked for {list(axis.sample_fields)}), "
                f"so no figure about it exists at any sample size. It is an UNCOUNTED DIMENSION of "
                f"the demand N, enumerated as {list(axis.uncounted_as)}.")
            if figure is None:
                record["why"] += (" No published figure establishes its distribution either, so "
                                  "the size of what is missing is itself unmeasured.")
            records.append(record)
            continue

        values = [str(v) for v in population[carrier]]
        categories = sorted(set(values))
        record["categories_in_the_sample"] = len(categories)
        record["observed"] = {c: values.count(c) / len(values) for c in categories}
        if figure is not None:
            record["n_the_answer_earns"] = _share_interval(figure["share"], len(values))

        reasons = []
        if axis.categories_in_the_world and len(categories) < axis.categories_in_the_world:
            reasons.append(
                f"the sample carries {len(categories)} categories and the published record "
                f"establishes that the world has {axis.categories_in_the_world}")
        if record["agrees_by_construction"]:
            reasons.append(
                "the sample draws this axis from the same published constant the census would "
                "score it against, so agreement on the margin is arithmetic and not evidence")
        if figure is None:
            reasons.append("no published figure establishes its distribution, so there is nothing "
                           "to score the sample against")
        record["verdict"] = "CARRIED_NOT_SPANNED" if reasons else "SPANNED"
        record["why"] = ("; ".join(reasons) if reasons else
                         "carried, and its categories and margin are established against the "
                         "published figure")
        records.append(record)
    return records


#: WHAT THIS CENSUS REDUCES OVER, and the declaration is the finding rather than a formality. One
#: of the five components is reduced over and four are blind -- so a reader who takes the demand N
#: as a size for the book has the refutation printed beside it.
REDUCES_OVER = declare(
    "whether the demand sample spans the billing and commercial axes",
    kind="coverage",
    of=tuple(a.key for a in CANON_AXES),
    reduces_over=("payment_method",),
    blind_to=("meter_type_and_read_pattern", "tariff_and_dates", "move_history",
              "credit_position"),
    joint=True,
)


def measurement(points: int = 20_000, seed: int = 0) -> dict:
    """The census: every canon axis against the drawn demand sample."""
    population = dvc.generated_population(points=points, seed=seed)
    canon = canon_path()
    records = axis_records(population, canon_text=canon.read_text())
    counts = {v: sum(1 for r in records if r["verdict"] == v) for v in VERDICTS}
    return {
        "subject": "the demand sample -- tools.demand_vector_coverage.generated_population",
        "sample": {"points": points, "seed": seed},
        "canon": {"document": str(canon.relative_to(PROJECT)),
                  "axes_named": list(canon_named_axes(canon.read_text()))},
        "declaration": REDUCES_OVER.banner(),
        "axes": records,
        "verdict_counts": counts,
        "uncounted_axes_of_the_demand_n": list(dvc.UNCOUNTED_AXES),
    }


#: The draw the daily line takes. Small on purpose: WHETHER a field is there does not depend on how
#: many households are drawn, and only the payment margin's bound does -- so the line reports the
#: verdicts, which are stable at any n, and points at the artefact for the figures. A daily note
#: that spent thirty seconds recomputing a bound nobody reads daily would be paid for every morning.
NOTE_POINTS = 200


def note_line() -> str:
    """One line for the daily self-note, and the thing that makes this census a TRIGGER.

    A census nobody runs is the arm without a trigger this project has shipped before. What this
    line has to survive is the day an axis quietly becomes uncounted again -- so it names the count
    and the axes rather than saying "unchanged", and it raises rather than returning a reassuring
    string when the canon cannot be read.
    """
    result = measurement(points=NOTE_POINTS)
    counts = result["verdict_counts"]
    absent = [r["axis"] for r in result["axes"] if r["verdict"] == "ABSENT"]
    return (f"billing axes vs the demand sample: {counts['SPANNED']} spanned, "
            f"{counts['CARRIED_NOT_SPANNED']} carried but not spanned, {counts['ABSENT']} absent "
            f"({', '.join(absent) if absent else 'none'}) — the absent ones are uncounted "
            f"dimensions of the published sample size")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true",
                    help="the per-axis census against the drawn demand sample")
    ap.add_argument("--points", type=int, default=20_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--json", type=Path, default=None,
                    help="also write the census to this path, for the reader-facing surface")
    args = ap.parse_args(argv)
    if args.measure:
        result = measurement(points=args.points, seed=args.seed)
        text = json.dumps(result, indent=2, default=str)
        if args.json:
            args.json.write_text(text + "\n")
        print(text)
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
