"""THE DEFECT: an explanation of a household's year that NARRATES instead of RECONCILING.

`tools/explain_premise_year.py` answers the director's phase-one ask -- *"look at a household's
half-hourly gas and electricity for a year and believe it, and be able to say why it looks like
that -- this fabric, this weather, these people, this heating pattern."* A tool that prints four
plausible paragraphs satisfies that sentence and establishes nothing: every total is plausible for
some combination of causes, so prose about a house is not evidence the house was modelled. The only
thing that cannot be faked is an ARITHMETIC IDENTITY between the causes and the fuel, which is why
`explain()` returns a `reconciliation` block and why this control asserts it CLOSES rather than
asserting any figure in it.

WHY THE TWO YEARS ARE IN ONE TEST AND NOT TWO. A reconciliation that closes tells you the arithmetic
is consistent; it does NOT tell you the weather leg read any weather. Until 2026-09-21 ten of the
book's eighteen premises resolved their sky by a string rule over four filenames, missed, and got
`REFERENCE_MONTHLY_HDD` -- the 1991-2020 monthly normal -- which is THE SAME NUMBER IN EVERY YEAR. A
degree-day total computed off a normal closes its identity perfectly and is still climatology. So
the discriminating assertion is that 2018 and 2022 DISAGREE, and it has to sit beside the identity
rather than in a test of its own: separately, each passes against a normal.
(`W1_14` step 3, `a2145439a`; the finding is
`docs/staging/done/WORKER_FINDING_THE_HDD_LEG_IS_A_THIRD_RESOLVER_AND_TEN_OF_EIGHTEEN_PREMISES_GET_A_CLIMATE_NORMAL_INSTEAD_OF_WEATHER_2026-09-21.md`.)

Both years are real GB record and neither is a scenario: 2018 held a cold late winter, 2022 was the
warmest year in the series.
"""

import pytest

from tools.explain_premise_year import explain, render

#: A premise the per-cell weather store holds a cell for, so both years resolve to real days.
PREMISE = "C1"

#: Two years the real record puts far apart. A climate normal returns one answer for both.
COLD_YEAR = 2018
WARM_YEAR = 2022

#: The identity is in kWh over a whole year, so it closes to the rounding in `explain()`'s own
#: output (one decimal place per term, three terms). A tolerance of 1 kWh on an ~8,000 kWh gross is
#: the rounding and nothing else -- it is deliberately far too tight to absorb a real modelling gap.
CLOSES_WITHIN_KWH = 1.0


@pytest.fixture(scope="module")
def reports():
    """Both years, once. `explain()` is ~0.8 s per year and neither call writes anything."""
    return {year: explain(PREMISE, year) for year in (COLD_YEAR, WARM_YEAR)}


def test_the_reconciliation_closes_and_the_two_years_disagree(reports):
    """The four causes must ADD UP to the fuel, and the weather must be a year rather than a normal.

    POPULATION FLOOR FIRST. Every assertion below is indexed by year, so a fixture that returned an
    empty mapping -- or `explain()` restructured to return a stub -- would leave this control
    reporting the chain clean while reading nothing.
    """
    assert set(reports) == {COLD_YEAR, WARM_YEAR}, (
        "both years must be present or the disagreement leg below reads nothing: "
        "{}".format(sorted(reports))
    )

    for year, report in reports.items():
        rec = report["reconciliation"]
        weather = report["weather"]

        assert weather["days"] > 350, (
            "{} resolved only {} days, so its degree-day total is not a year".format(
                year, weather["days"]))

        # THE IDENTITY. Gross fabric loss, less what the gains covered, IS the heat delivered.
        # Keyed to the closure, never to a figure: a more faithful fabric model must move every
        # term here and still pass, and that is the whole point of writing it this way.
        residual = (
            rec["gross_fabric_loss_kwh"]
            - rec["covered_by_gains_kwh"]
            - rec["heat_delivered_kwh"]
        )
        assert abs(residual) <= CLOSES_WITHIN_KWH, (
            "{}: HLC x degree-days x 24 h, less gains, does not land on the heat delivered -- "
            "residual {:.1f} kWh (gross {:.1f}, gains {:.1f}, delivered {:.1f})".format(
                year, residual, rec["gross_fabric_loss_kwh"], rec["covered_by_gains_kwh"],
                rec["heat_delivered_kwh"]))

        # And the delivered heat is the gas burnt times the boiler's efficiency, so the fuel side
        # of the identity is bound too and not merely reported next to it.
        heat_fuel = report["year_totals"]["space_heat_fuel_kwh"]
        assert heat_fuel > 0.0, "{}: no space-heat fuel at all".format(year)
        implied = rec["heat_delivered_kwh"] / heat_fuel
        assert implied == pytest.approx(rec["boiler_efficiency_implied"], abs=1e-3), (
            "{}: the published boiler efficiency {} is not delivered/fuel ({:.4f})".format(
                year, rec["boiler_efficiency_implied"], implied))

    # THE DISCRIMINATING LEG: a normal cannot see a winter. Before the step-3 repair this premise's
    # sibling C7 returned annual HDD 2086.1 in BOTH 2018 and 2022. Equal degree-days here means the
    # weather leg has stopped reading the world, whatever the identity says.
    cold_dd = reports[COLD_YEAR]["weather"]["degree_days_at_own_setpoint"]
    warm_dd = reports[WARM_YEAR]["weather"]["degree_days_at_own_setpoint"]
    assert cold_dd != warm_dd, (
        "{} and {} produced the SAME degree-day total ({}), which is what a climate normal does "
        "and what W1_14 step 3 exists to stop".format(COLD_YEAR, WARM_YEAR, cold_dd))
    assert cold_dd > warm_dd, (
        "the colder year must demand more heating: {} gave {} degree-days against {}'s {}".format(
            COLD_YEAR, cold_dd, WARM_YEAR, warm_dd))


def test_the_rendering_carries_every_cause_it_claims_to_explain(reports):
    """The prose is the deliverable, so a section silently dropped from it is the defect.

    Not a spelling test: each heading corresponds to one of the four causes the director's sentence
    names, and a renderer that omits one still prints a confident-looking explanation.
    """
    text = render(reports[WARM_YEAR])
    for heading in ("THIS FABRIC", "THIS WEATHER", "THESE PEOPLE", "THIS HEATING PATTERN",
                    "AND THE ARITHMETIC CLOSES"):
        assert heading in text, "the rendering dropped {!r}".format(heading)
