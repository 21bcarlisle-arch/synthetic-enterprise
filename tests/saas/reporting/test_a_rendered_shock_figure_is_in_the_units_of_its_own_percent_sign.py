"""Every bill-shock figure this report renders is in the units of the `%` beside it.

THE DEFECT THIS EXISTS TO CATCH, in the words of the artefact that had it: `docs/reports/
ANNUAL_REPORT.md` published `Worst bill shock: **2022** (0.58%)` and `| 2022 | 57.5% | ... |`
about one stored field, 1,166 lines apart, in one document under this company's name. The field
(`years[yr]["avg_bill_shock_pct"]`) is a FRACTION carrying a `_pct` name -- the served
`site/data/dashboard.json` says so in its own sibling note -- and one renderer scaled it while the
other did not.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts that 2022 is the worst year,
that the mean is 45.7%, or that any particular year is banded HIGH. Every check below is of the
form "whatever the numbers are, these two renderings of them agree" or "an unmeasured cell says
so". A control pinned to the current figures goes red when the model becomes more honest and stays
green when the claim rots, which is exactly backwards.

Each test names the defect it would catch, and each was mutation-proven against the fix it guards
(see the module's own commit message for the surviving/killed list).
"""
import re

import pytest

from saas.reporting.annual_report import (
    SHOCK_NOT_MEASURED,
    _bill_shock_populations,
    _fmt_shock_pct,
    _section_bill_shock_analysis,
    _section_service_quality,
    _shock_band,
    _shock_definition_population,
    _worst_defined_shock_year,
)

# A percentage as this report prints one: "43.5%", "0.1%", "1360.0%".
_RENDERED_PCT = re.compile(r"(\d+\.\d)%")


def _bill(period_end, pct, population, customer="C1"):
    return {
        "customer_id": customer,
        "period_end": period_end,
        "bill_shock_pct": pct,
        "bill_shock_population": population,
        "payment_channel": None,
    }


def _data(bills, *, years=("2022",)):
    """A report `data` dict carrying exactly `bills`, reduced the way the real one is."""
    ydata = {}
    for yr in years:
        yr_bills = [b for b in bills if b["period_end"].startswith(yr)]
        flagged = [b for b in yr_bills if b["bill_shock_pct"] >= 0.20]
        ydata[yr] = {
            "avg_bill_shock_pct": (
                sum(b["bill_shock_pct"] for b in yr_bills) / len(yr_bills) if yr_bills else None
            ),
            "bill_shock_events": flagged,
            "bills_count": len(yr_bills),
            "avg_clarity": 0.90,
            "avg_complaint_probability": 0.03,
        }
    return {"years": ydata, "bills": bills}


# ---------------------------------------------------------------------------
# THE UNITS PROPERTY
# ---------------------------------------------------------------------------

def test_one_stored_fraction_is_never_rendered_both_scaled_and_unscaled():
    """DEFECT: the hundredfold disagreement. A 0.42 fraction printed as both "42.0%" and "0.42%".

    Constructed so the two renderings are TELLABLE APART: a mean of 0.42 renders as "42.0%" if
    scaled once and "0.4%" if not, and only one of those may appear.
    """
    bills = [_bill("2022-01-31", 0.42, "bill"), _bill("2022-02-28", 0.42, "bill")]
    rendered = _section_bill_shock_analysis(_data(bills)) + _section_service_quality(_data(bills))
    assert "42.0%" in rendered, "the mean was not rendered in percent at all"
    # The unscaled rendering of the SAME quantity must appear nowhere.
    assert "0.4%" not in rendered, (
        "a bill-shock figure was rendered without scaling a fraction to percent -- "
        "this is the 0.58%-vs-57.5% defect"
    )


def test_no_rendered_shock_percentage_is_small_enough_to_be_an_unscaled_fraction():
    """DEFECT: a NEW reader added later that forgets the scaling.

    Scope note (R15): this is deliberately a property over the whole rendered section rather than
    over the call sites known today, because the defect was that a second call site existed and
    disagreed. Bills are built so every real figure is comfortably above 1%, making any sub-1%
    percentage a scaling error rather than a small true value.
    """
    bills = [
        _bill("2022-01-31", 0.42, "bill"),
        _bill("2022-02-28", 0.55, "bill"),
        _bill("2022-03-31", 0.61, "payment"),
        _bill("2022-04-30", 0.48, "payment"),
    ]
    rendered = _section_bill_shock_analysis(_data(bills))
    small = [m for m in _RENDERED_PCT.findall(rendered) if float(m) < 1.0]
    assert not small, (
        f"rendered percentages below 1% ({small}) when every input shock was >=42% -- "
        "a fraction reached a '%' without being scaled"
    )


def test_the_renderer_does_not_scale_what_is_already_a_percentage():
    """DEFECT: over-correction. Fixing the missing x100 by adding a second one."""
    assert _fmt_shock_pct(43.5) == "43.5%"
    assert _fmt_shock_pct(0.1) == "0.1%"


# ---------------------------------------------------------------------------
# THE FAIL-CLOSED PROPERTY
# ---------------------------------------------------------------------------

def test_an_unmeasured_population_is_not_published_as_a_measured_zero():
    """DEFECT: `avg = yd.get("avg_bill_shock_pct") or 0.0`.

    An n=0 cell used to become 0.0, which then fell below the 20% band edge and was published
    as an unflagged, apparently-fine year. On the real ten-year book that was fifteen cells.
    """
    bills = [_bill("2022-01-31", 0.42, "bill")]  # nothing in `payment` or `out_of_scope`
    rendered = _section_bill_shock_analysis(_data(bills))
    assert SHOCK_NOT_MEASURED in rendered
    assert "| 2022 | out of scope | 0 | " + SHOCK_NOT_MEASURED in rendered, (
        "an empty population was rendered as a measured value"
    )


def test_an_unmeasured_population_is_none_in_the_data_layer_not_only_in_the_render():
    """The SAME fail-closed property one layer down, and it needs its own leg.

    ESTABLISHED BY A MUTATION THAT DID NOT FIRE, which is either a missing test or an
    equivalence and must never be left as whichever is flattering. Making `_shock_stats`
    return `avg_pct=0.0` for an empty sample -- the exact pre-split defect -- left
    `test_an_unmeasured_population_is_not_published_as_a_measured_zero` GREEN. That test is
    an equivalence at the render layer: `_section_bill_shock_analysis` short-circuits on
    `if not stats.get("n")` and prints the refusal without ever reading `avg_pct`, so it
    cannot see a measured zero underneath it.

    The only control that DID fire was the coupling one -- the two split implementations
    agreeing bill for bill. That is agreement with `tools/generate_dashboard_data.py`, not
    the property itself, and it is primed to stop holding: the repair filed in
    `docs/staging/FINDING_THE_BILL_SHOCK_SPLIT_HAS_ONE_IMPLEMENTATION_AND_IT_IS_IN_THE_WRONG_LAYER_2026-09-02.md`
    unifies the two copies into one, at which point the coupling check compares a thing to
    itself and this property has no holder at all. This leg is what makes that repair safe
    to land.
    """
    pops = _bill_shock_populations(_data([_bill("2022-01-31", 0.42, "bill")]))
    empty = pops["2022"]["out_of_scope"]
    assert empty["n"] == 0
    for field in ("avg_pct", "median_pct", "max_pct", "ci95_low", "ci95_high"):
        assert empty[field] is None, (
            f"an unmeasured population published {field}={empty[field]!r}; a population with no "
            "bill in a year has not been measured at zero shock, it has not been measured"
        )


def test_an_unmeasured_band_refuses_rather_than_reporting_the_best_branch():
    """DEFECT: a None/absent mean banding as 'within band' -- fail-open in a verdict."""
    assert _shock_band(None) == SHOCK_NOT_MEASURED
    assert _shock_band(0.0) != SHOCK_NOT_MEASURED  # a genuine measured zero is NOT a refusal


def test_no_worst_year_is_named_when_no_year_was_measured():
    """DEFECT: `worst_shock = 0.0` seeded a comparison every real year beat.

    With no measured year at all the old shape still crowned one. It must return None, and the
    report must say so rather than printing a year.
    """
    empty = {"2022": {"bill": {"n": 0, "avg_pct": None}}}
    assert _worst_defined_shock_year(empty, ["2022"]) is None


# ---------------------------------------------------------------------------
# THE DEFINITION PROPERTY
# ---------------------------------------------------------------------------

def test_the_band_is_applied_only_to_the_population_whose_figure_is_a_shock():
    """DEFECT: banding the direct-debit row.

    Its bill-to-bill difference is not a quantity that household experienced, so a verdict on it
    asserts a harm nobody had. The band must appear on the standard-credit row and `n/a` on the
    direct-debit row of the SAME year.
    """
    bills = [
        _bill("2022-01-31", 0.42, "bill"),
        _bill("2022-02-28", 0.42, "payment"),
    ]
    rendered = _section_bill_shock_analysis(_data(bills))
    bill_row = next(ln for ln in rendered.splitlines() if "| standard credit |" in ln)
    dd_row = next(ln for ln in rendered.splitlines() if "| direct debit |" in ln)
    assert bill_row.rstrip().endswith("**HIGH** |"), bill_row
    assert dd_row.rstrip().endswith("n/a |"), dd_row


def test_the_defined_population_matches_the_dashboards_own_constant():
    """DEFECT: this report and `site/data/dashboard.json` coming to disagree about which column
    means what.

    THE REPORT KEEPS ITS OWN COPY ON PURPOSE and this is what makes that safe. Importing the
    dashboard generator from `saas/reporting/annual_report.py` reaches `simulation.*` and
    `tools.wall_crossing_dispositions` refuses the commit -- correctly; that route is a wall, not
    a trade-off. A TEST may make the crossing the module may not, so the coupling is asserted here
    instead of assumed there.
    """
    from tools.generate_dashboard_data import SHOCK_DEFINITION_POPULATION

    assert _shock_definition_population() == SHOCK_DEFINITION_POPULATION


def test_the_report_and_the_dashboard_split_the_same_bills_the_same_way():
    """DEFECT: the two copies of the population split drifting apart.

    This is the control the constant check alone would not give: it compares the whole computed
    block -- every n, mean, median, max and both interval bounds, for every population including
    the mixed total -- against the dashboard's implementation on ONE input. A changed bootstrap
    seed, resample count, rounding, tail, or population key reds it.

    Keyed to AGREEMENT, not to values: nothing here asserts what any figure is, so it stays green
    when the model changes and goes red only when the two artefacts would disagree.
    """
    from tools.generate_dashboard_data import _annual_shock_by_population

    # THE FIXTURE HAS TO BE BIG ENOUGH AND ODD ENOUGH FOR THE MUTATIONS TO BITE. A first version
    # used six round values and two of five drift mutations SURVIVED -- resample count and
    # rounding precision -- because at n=2 with values like 0.42 the bootstrap percentiles and
    # the 1-vs-2-decimal rounding both landed on the same number by luck. That was a weak fixture,
    # not an equivalence, and recording which is which is the rule. These values are irrational-
    # ish to three places and there are enough of them per population that both now red.
    bills = [
        _bill(f"2022-{m:02d}-28", pct, pop, customer=f"C{i}")
        for i, (m, pct, pop) in enumerate([
            (1, 0.4237, "bill"), (2, 0.1319, "bill"), (3, 0.8861, "bill"),
            (4, 0.0733, "bill"), (5, 0.5107, "bill"), (6, 0.2949, "bill"),
            (7, 0.6151, "payment"), (8, 0.0787, "payment"), (9, 0.3313, "payment"),
            (10, 0.9377, "payment"), (11, 0.1471, "payment"), (12, 0.2237, None),
        ])
    ] + [
        _bill(f"2023-{m:02d}-28", pct, pop, customer=f"D{i}")
        for i, (m, pct, pop) in enumerate([
            (1, 0.5573, "bill"), (2, 0.2129, "bill"), (3, 0.7691, "payment"),
            (4, 0.0419, "payment"), (5, 0.3847, "bill"), (6, 0.6203, "payment"),
        ])
    ]
    d = _data(bills, years=("2022", "2023"))
    mine = _bill_shock_populations(d)
    theirs = _annual_shock_by_population(d, ["2022", "2023"])
    assert mine == theirs


def test_the_report_publishes_each_populations_own_n():
    """DEFECT: a mean published without the bound its sample size earns.

    The pre-split field carried no n at all, so no reader could tell a mean of 252 bills from a
    mean of 2.
    """
    bills = [_bill(f"2022-0{i}-28", 0.42, "bill", customer=f"C{i}") for i in range(1, 4)]
    rendered = _section_bill_shock_analysis(_data(bills))
    assert "| 2022 | standard credit | 3 |" in rendered


# ---------------------------------------------------------------------------
# THE ATTRIBUTION PROPERTY
# ---------------------------------------------------------------------------

def test_the_band_is_not_attributed_to_a_regulator():
    """DEFECT: 'Ofgem benchmarks: ... bill shock <0.20% (GREEN)...' and 'Ofgem monitors bill shock
    as a consumer harm indicator', both published for months.

    `docs/market_research/BILL_SHOCK_EVENT_TYPES_ANCHORS.md` section 3 searched for exactly this
    and recorded 'Confirmed: no' -- no Ofgem definition of bill shock as a term, threshold or
    comparison basis. The refusal must be ON the page, naming its reason; asserting only the
    absence of the word 'Ofgem' would pass on a silent deletion.
    """
    bills = [_bill("2022-01-31", 0.42, "bill")]
    rendered = _section_bill_shock_analysis(_data(bills))
    assert "NOT a regulator's" in rendered
    assert "BILL_SHOCK_EVENT_TYPES_ANCHORS" in rendered
    assert "Ofgem monitors bill shock" not in rendered


def test_the_withdrawn_column_is_withdrawn_out_loud():
    """DEFECT: a silent deletion. A column that vanishes between two editions is
    indistinguishable from a rendering bug unless the report says it went and why."""
    bills = [_bill("2022-01-31", 0.42, "bill")]
    rendered = _section_service_quality(_data(bills))
    assert "Withdrawn from this table" in rendered
    assert "Shock%" in rendered, "the withdrawal note must name the column it withdrew"


def test_the_service_quality_rag_says_so_when_it_has_only_one_reachable_value():
    """DEFECT: swapping a constant-RED verdict for a constant-GREEN one.

    The shock leg was RED in all ten years of the real book, so its other branches were
    unreachable and the column carried no information. Removing it must not simply move the
    problem: when the remaining legs are also single-valued across the years shown, the page has
    to say the verdict is untested rather than passed.
    """
    bills = [_bill("2022-01-31", 0.42, "bill")]
    rendered = _section_service_quality(_data(bills))
    assert "carries no information about this book" in rendered


def test_the_constant_verdict_note_is_absent_when_the_rag_actually_moves():
    """THE OTHER DIRECTION -- without this the test above passes on a hardcoded sentence.

    A book whose clarity crosses the 0.80 edge in one year and not another produces two distinct
    verdicts, and the 'carries no information' note must then NOT appear.
    """
    bills = [_bill("2021-01-31", 0.42, "bill"), _bill("2022-01-31", 0.42, "bill")]
    d = _data(bills, years=("2021", "2022"))
    d["years"]["2021"]["avg_clarity"] = 0.95   # GREEN
    d["years"]["2022"]["avg_clarity"] = 0.50   # RED
    rendered = _section_service_quality(d)
    assert "carries no information about this book" not in rendered
    assert "RED years: 2022" in rendered


# ---------------------------------------------------------------------------
# THE MAGNITUDE-VS-INCIDENCE PROPERTY
# ---------------------------------------------------------------------------

def test_incidence_divides_flagged_bills_by_computable_bills_not_by_every_bill():
    """DEFECT: 'Shock Rate' = events / bills_count.

    A bill with no prior bill has no computable change and CANNOT be flagged, so counting it in
    the denominator understates incidence. Here: 4 computable bills in `bill`, 2 of them flagged,
    plus 6 uncomputable bills inflating `bills_count` to 10. The honest figure is 50%, and the
    old denominator gives 20%.
    """
    bills = [
        _bill("2022-01-31", 0.42, "bill", customer="C1"),
        _bill("2022-02-28", 0.42, "bill", customer="C2"),
        _bill("2022-03-31", 0.05, "bill", customer="C3"),
        _bill("2022-04-30", 0.05, "bill", customer="C4"),
    ]
    d = _data(bills)
    d["years"]["2022"]["bills_count"] = 10  # six bills had no prior bill to difference
    rendered = _section_bill_shock_analysis(d)
    row = next(ln for ln in rendered.splitlines() if ln.startswith("| 2022 | standard credit | 2 | 4 |"))
    assert row.rstrip().endswith("50% |"), row


def test_magnitude_and_incidence_are_not_in_one_table():
    """DEFECT: a mean banded against a threshold whose wording read as an incidence, published
    in the same row as an actual incidence. They are separate headings now."""
    bills = [_bill("2022-01-31", 0.42, "bill")]
    rendered = _section_bill_shock_analysis(_data(bills))
    assert "### Magnitude" in rendered
    assert "### Incidence" in rendered
    assert rendered.index("### Magnitude") < rendered.index("### Incidence")


# ---------------------------------------------------------------------------
# THE SUPERSEDED TOTAL IS KEPT, AND LABELLED
# ---------------------------------------------------------------------------

def test_the_mixed_mean_is_published_but_never_as_a_bill_shock_rate():
    """DEFECT: deleting the pre-split figure, which would make the re-partition unreconcilable
    from the artefacts alone -- or keeping it under its old name, which is the original defect."""
    bills = [_bill("2022-01-31", 0.42, "bill"), _bill("2022-02-28", 0.60, "payment")]
    rendered = _section_bill_shock_analysis(_data(bills))
    assert "### The superseded total" in rendered
    assert "not a bill shock rate and should not be cited" in rendered


@pytest.mark.parametrize("section", [_section_bill_shock_analysis, _section_service_quality])
def test_sections_survive_a_book_with_no_bills_at_all(section):
    """DEFECT: the fail-closed repair crashing instead of refusing. A refusal that raises is not
    a refusal."""
    assert section({}) == ""
