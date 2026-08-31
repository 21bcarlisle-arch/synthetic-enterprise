"""The ladder page's renewal per-factor table must be a QUOTATION of the report, not a copy of it.

THE DEFECT THIS EXISTS TO CATCH, and it is not hypothetical -- it was live on the page for six
hours on 2026-08-31 and this control was written because of it.

`LADDER_APPLIED_TO_CHURN_2026-08-31.md` publishes the renewal route's per-factor table by hand.
Item 1 of the same page then made `sim_dissatisfaction_response` continuous, which is a change to
the WORLD, so every figure in that table was re-measured. The SVT table twelve lines below got its
superseded banner the same hour. The renewal table did not, and nothing could notice, because:

  * the ALONE column is INVARIANT to the change -- freezing every other factor at its population
    mean makes a factor's own ALONE score independent of what those other factors are made of, so
    three of the four ALONE figures still matched the live instrument exactly; and
  * the HELD OUT and CONTRIBUTION columns, which are not invariant, were the stale ones.

So the table read as "mostly right" to anyone spot-checking it, and the page ended up stating
**+0.0527** in the table and **+0.0539** eighty lines further down for the same quantity, both in
bold, both presented as measured. Two figures for one quantity on one page is the shape this
project has published wrongly before, and a reader has no way to tell which is the live one.

WHAT IS ASSERTED, AND WHY IT IS KEYED TO THE PROPERTY RATHER THAN TO TODAY'S ANSWER

Every figure the page quotes for the renewal route must equal the same field of
`docs/reports/ladder_churn_ceiling_vs_belief.json`, the artefact the page's own ceiling-vs-belief
section reads. Neither number is written into this file. When the world changes honestly, both
artefacts are regenerated and this stays green; when only one of them moves, it reds. That is the
opposite of a control pinned to 0.7400, which would go red the next time churn is repaired and
green the day the page rots.

FAIL CLOSED, because every plausible way this control could rot is a fail-open. A missing report,
an unparseable table, a table with no rows, or a factor present in the report and absent from the
page all RAISE rather than passing vacuously -- "we could not find the table" reading as "the table
agrees" is the exact failure this file is an instance of.

MUTATIONS PROVEN (2026-08-31), each against a green unmutated baseline, each firing on an assertion
and each mutation being one the page has actually suffered or could suffer tomorrow:
  1. page HELD OUT 0.6862 -> 0.6885 (the real stale value)  -> test_every_quoted_per_factor_figure_matches_the_report
  2. page contribution +0.0539 -> +0.0527 (ditto)           -> test_every_quoted_per_factor_figure_matches_the_report
  3. page ALONE 0.3806 -> 0.4672 (the bucketed value)       -> test_every_quoted_per_factor_figure_matches_the_report
  4. page distinct values 135 -> 3                          -> test_every_quoted_per_factor_figure_matches_the_report
  5. drop the `sim_action_propensity` row from the table    -> test_every_factor_in_the_report_is_quoted_on_the_page
  6. page route AUC 0.7400 -> 0.7412                        -> test_the_route_headline_matches_the_report
  7. page route null upper 0.6206 -> 0.6194                 -> test_the_route_headline_matches_the_report
  8. reword the renewal heading so the table cannot be found -> test_the_table_is_found_at_all + two others
  9. reword the SVT heading that bounds the slice            -> test_the_table_is_found_at_all + one other

AND 8 AND 9 FAILED THE FIRST TIME IN A WAY WORTH THE SPACE. The parse originally asserted inside
the `quoted_table` fixture, so an unfindable table raised during SETUP: pytest reported three
ERRORs and one FAILED, and an ERROR is neither a pass nor a failure -- every summary that counts
failures walks past it, which is the same fail-open shape as the defect this file exists to catch.
The fixture now RETURNS an empty table and the assertion lives in a test, so a table this control
can no longer read is a red with a message saying which part of the parse broke.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
PAGE = PROJECT / "docs" / "design" / "LADDER_APPLIED_TO_CHURN_2026-08-31.md"
REPORT = PROJECT / "docs" / "reports" / "ladder_churn_ceiling_vs_belief.json"

ROUTE = "renewal"

# The page quotes to four decimal places; the report carries full precision.
PLACES = 4

_HEADING = re.compile(
    r"\*\*Renewal route\s*—\s*(?P<decisions>[\d,]+) decisions,\s*(?P<departures>[\d,]+) departures\.\s*"
    r"AUC (?P<auc>[\d.]+), null \[(?P<low>[\d.]+), (?P<high>[\d.]+)\]\.\*\*"
)

_ROW_START = re.compile(r"^\|\s*`(?P<factor>sim_[a-z_]+)`\s*\|", re.MULTILINE)

# The page annotates cells freely -- `0.5925 *(inside null)*`, `**2.1%**`, `**−0.0012**`. Only the
# number is under test, so every cell is reduced to the first numeric token it contains.
_FIRST_NUMBER = re.compile(r"[+−-]?\d+(?:\.\d+)?")


def _number(cell: str) -> float:
    """The first number in a table cell, with the page's emphasis and typographic minus removed."""
    match = _FIRST_NUMBER.search(cell.replace("*", "").replace("−", "-"))
    assert match is not None, f"no number in the table cell {cell!r}"
    return float(match.group().replace("+", ""))


@pytest.fixture(scope="module")
def report() -> dict:
    if not REPORT.exists():
        raise AssertionError(
            f"{REPORT.relative_to(PROJECT)} is missing -- the page quotes an artefact that is not "
            "in the tree, so nothing can check what it says. Regenerate it with "
            "`python3 -m tools.measure_churn_heterogeneity`."
        )
    entry = json.loads(REPORT.read_text())["per_route"][ROUTE]
    assert entry["per_factor"], "the report carries no per-factor readings to check the page against"
    return entry


@pytest.fixture(scope="module")
def page_text() -> str:
    assert PAGE.exists(), f"{PAGE.relative_to(PROJECT)} is missing"
    return PAGE.read_text()


@pytest.fixture(scope="module")
def quoted_table(page_text: str) -> dict[str, dict[str, float]]:
    """The rows of the renewal per-factor table, as the page states them.

    The SVT table lives further down the same page and is deliberately excluded: it is marked
    SUPERSEDED and its figures are withdrawn, so it must NOT be held to agreement with the report.
    Slicing between the renewal heading and the SVT one is what keeps those two apart.
    """
    NOT_FOUND: dict[str, dict[str, float]] = {}

    start = _HEADING.search(page_text)
    if start is None:
        # Deliberately NOT an assertion. An assertion here raises during fixture SETUP, and a test
        # that errors at setup is neither a pass nor a failure -- pytest reports it as ERROR and
        # every summary that counts failures walks past it. `test_the_table_is_found_at_all` turns
        # this into a real red instead.
        return NOT_FOUND
    rest = page_text[start.end() :]
    end = rest.find("**SVT route")
    if end <= 0:
        return NOT_FOUND
    block = rest[:end]

    rows: dict[str, dict[str, float]] = {}
    for line in block.splitlines():
        start = _ROW_START.match(line)
        if start is None:
            continue
        cells = [c for c in line.strip().strip("|").split("|")]
        assert len(cells) == 6, (
            f"the renewal table row for `{start.group('factor')}` has {len(cells)} columns, not the "
            "six this control reads -- the table has been restructured and the parse is unsafe"
        )
        _, alone, held_out, contribution, ties, values = cells
        rows[start.group("factor")] = {
            "alone": _number(alone),
            "held_out": _number(held_out),
            "contribution": _number(contribution),
            "tie_pct": _number(ties),
            "distinct_values": _number(values),
        }
    return rows


def test_the_table_is_found_at_all(quoted_table):
    """A control that cannot find its subject must fail, never pass quietly.

    Every other assertion here iterates the parsed rows. If the parse silently returned nothing --
    the heading reworded, the table turned into prose, the columns reordered -- those loops would
    all pass over an empty collection and the page could say anything at all.
    """
    assert quoted_table, (
        "no per-factor rows were parsed out of the renewal section of "
        f"{PAGE.relative_to(PROJECT)}: either the `**Renewal route — N decisions, M departures. "
        "AUC x, null [a, b].**` heading is no longer in that form, or the `**SVT route` heading no "
        "longer follows it, or the table beneath is no longer a six-column markdown table. The "
        "page's figures are unchecked until this parse is repaired."
    )


def test_every_factor_in_the_report_is_quoted_on_the_page(report, quoted_table):
    """A factor dropped from the page is a figure that stops being checkable."""
    missing = sorted(set(report["per_factor"]) - set(quoted_table))
    assert not missing, (
        f"the report carries per-factor readings the page's renewal table does not quote: {missing}"
    )


def test_every_quoted_per_factor_figure_matches_the_report(report, quoted_table):
    """The page's numbers ARE the report's numbers, to the precision the page prints them."""
    disagreements = []
    for factor, quoted in sorted(quoted_table.items()):
        measured = report["per_factor"].get(factor)
        assert measured is not None, (
            f"the page quotes `{factor}` on the renewal route and the report has no such factor -- "
            "the page is quoting a measurement that no longer exists"
        )
        for field, page_value in quoted.items():
            # Each column is checked to the precision the PAGE prints it in. Holding a percentage
            # the page gives to one decimal to four would red on rounding alone, which is a control
            # that fails for a reason nobody can act on.
            if field == "distinct_values":
                live = float(measured["distinct_values"])
                if page_value != live:
                    disagreements.append(f"{factor}.{field}: page {page_value:.0f} vs report {live:.0f}")
            elif field == "tie_pct":
                live = float(measured["tie_fraction"]) * 100.0
                if round(page_value, 1) != round(live, 1):
                    disagreements.append(f"{factor}.tie_fraction: page {page_value}% vs report {live:.1f}%")
            else:
                live = float(measured[field])
                if round(page_value, PLACES) != round(live, PLACES):
                    disagreements.append(f"{factor}.{field}: page {page_value} vs report {live:.4f}")

    assert not disagreements, (
        "the ladder page and the report it quotes disagree, so one of them was regenerated and the "
        "other was not:\n  " + "\n  ".join(disagreements)
    )


def test_the_route_headline_matches_the_report(report, page_text):
    """The route's own AUC and null are quoted in prose above the table and rot the same way.

    This is where 0.7412 survived: the table was the visible defect and the heading carried the
    same stale capture one line higher.
    """
    heading = _HEADING.search(page_text)
    assert heading is not None, "the renewal route heading is not in the expected form"

    assert int(heading.group("decisions").replace(",", "")) == report["decisions"]
    assert int(heading.group("departures").replace(",", "")) == report["departures"]
    assert round(float(heading.group("auc")), PLACES) == round(report["oracle_auc"], PLACES), (
        f"the page states AUC {heading.group('auc')} and the report measures "
        f"{report['oracle_auc']:.4f}"
    )
    assert round(float(heading.group("low")), PLACES) == round(report["null"]["low"], PLACES)
    assert round(float(heading.group("high")), PLACES) == round(report["null"]["high"], PLACES)
