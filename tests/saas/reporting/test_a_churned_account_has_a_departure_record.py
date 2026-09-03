"""Every churn the published artefact reports must have a departure record, and every year it
reports must appear in one.

THE DEFECT THIS NAMES, MEASURED (2026-08-31). `docs/reports/run_output_latest.json` at the
2026-08-31 05:07Z run carries **82 accounts in `churned_billing_accounts` and 32 rows of
`event_type == "churned"` in `customer_events`**. Fifty accounts left the book with no cause, no
roll and no probability recorded anywhere a reader can reach. The same artefact reports ten years
in `years` and nine in `customer_events`: **2022 is absent entirely**, which is the crisis year and
one of the four walls in CLAUDE.md.

WHY BOTH LEGS ARE THE SAME CONTROL. They are one property with two faces: *a departure the
artefact asserts must be a departure the artefact can account for.* An unexplained account is a
churn with no record; an unrepresented year is a whole year of the window with no record. Every
downstream reader that divides departures by a population -- `tools/population_anchor._churn_by_year`
and `tools/measure_departure_level` foremost -- takes both from this artefact, so a hole in either
becomes a departure LEVEL nobody can attribute.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. There is no count in here. The window comes from the
artefact's own `years`, the explained set from whatever departure logs the artefact carries, and
the control goes green the moment every churn has a record -- however many there are, and by
whichever route. **Widening it is banned in both directions**: do not add a tolerance for "a few"
unexplained accounts, and do not repair a missing year by writing rows from anything other than the
world producing them.

FAIL-CLOSED, DELIBERATELY, AND THE `.get(..., [])` IS NOT A FAIL-OPEN. An artefact that predates
the `svt_departures` key yields an empty list, so its SVT departures stay unexplained and this goes
red -- which is the truth about that artefact, not a false alarm. The vacuous-pass hole is the
other one: an artefact with an empty window or an empty book would satisfy both legs by having
nothing to check, so `test_the_control_refuses_an_artefact_it_cannot_grade` closes it.

IT WAS RED AT BIRTH AND IT IS NOW GREEN, WHICH CHANGES WHAT IT OWES (2026-08-31, 07:5xZ). This
file was written red against the 05:07Z artefact and its docstring rested its FAIL-branch proof on
that redness. The 06:36Z run (`run_complete_20260831T063611Z`) executed the working tree carrying
`annual_report.extract_report_data`'s repair, the artefact gained its `svt_departures` key, and
both live legs went green -- 0 unexplained, no year absent. **A control that has gone green has
spent its red-at-birth evidence**, so the proof is restated here as a mutation that can be re-run
at any time rather than as a fact about one artefact that has since moved.

THE NAMED MUTATION, AND IT IS THE HISTORICAL DEFECT ITSELF. Drop `svt_departures` from the
artefact -- exactly what the reducer did for four consecutive runs -- and both live legs fail
together: `unexplained_churns` returns 50 and `years_absent_from_the_lifecycle_record` returns
`["2022"]`. Verified against the live artefact on 2026-08-31 by deleting the key from a copy of it
in memory. That is the one-line regression this control exists to catch, so its FAIL branch is
reachable by the precise route that made it necessary.

The PASS branch's reachability is the other half -- R15's "a control whose pass branch is
unreachable reports a constant verdict" -- and the four synthetic-artefact cases below are that
proof: one green via the renewal log, one green via the SVT log, one red for an unexplained
account, one red for an absent year. They matter more now than when the live legs were red,
because a green live leg cannot by itself distinguish a sound record from a helper that has
stopped looking.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_OUTPUT_PATH = REPO_ROOT / "docs" / "reports" / "run_output_latest.json"

#: Every log in the artefact whose rows are departures. A route that gets added later belongs
#: here and nowhere else -- that is the whole reason this is a named list rather than two
#: hand-written lookups. `customer_events` is filtered to its churned rows; `svt_departures` is
#: departures end to end.
RENEWAL_LOG = "customer_events"
SVT_LOG = "svt_departures"


def _departure_rows(artefact: dict) -> list[dict]:
    """Every row in the artefact that records an account leaving, by whichever route."""
    renewals = [
        e for e in (artefact.get(RENEWAL_LOG) or []) if e.get("event_type") == "churned"
    ]
    return renewals + list(artefact.get(SVT_LOG) or [])


def unexplained_churns(artefact: dict) -> list[str]:
    """Accounts the artefact says churned, for which it holds no departure record."""
    explained = {row.get("customer_id") for row in _departure_rows(artefact)}
    return sorted(
        account
        for account in (artefact.get("churned_billing_accounts") or [])
        if account not in explained
    )


def years_absent_from_the_lifecycle_record(artefact: dict) -> list[str]:
    """Years the artefact reports on, for which it holds no lifecycle event at all.

    The union of BOTH logs, not the renewal log alone: a year in which every household sat on
    the standard variable product has no renewal decisions by construction, and counting that as
    a hole would key this to the shape of the book rather than to the record's coverage.
    """
    reported = {str(y) for y in (artefact.get("years") or {})}
    recorded = {
        (e.get("event_date") or "")[:4]
        for e in (artefact.get(RENEWAL_LOG) or []) + list(artefact.get(SVT_LOG) or [])
    }
    return sorted(reported - recorded)


def _live_artefact() -> dict:
    assert RUN_OUTPUT_PATH.exists(), (
        f"{RUN_OUTPUT_PATH} is missing -- the published run artefact is what this control grades, "
        "and its absence is a refusal to grade, never a pass"
    )
    return json.loads(RUN_OUTPUT_PATH.read_text())


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The PASS branch is reachable: two artefacts that satisfy the property, by each route.
# ─────────────────────────────────────────────────────────────────────────────────────────────

_GREEN_VIA_RENEWAL = {
    "years": {"2016": {}, "2017": {}},
    "churned_billing_accounts": ["C1"],
    "customer_events": [
        {"customer_id": "C1", "event_date": "2016-06-01", "event_type": "renewed"},
        {"customer_id": "C1", "event_date": "2017-06-01", "event_type": "churned"},
    ],
}

_GREEN_VIA_SVT = {
    "years": {"2016": {}, "2017": {}},
    "churned_billing_accounts": ["C1"],
    "customer_events": [
        {"customer_id": "C1", "event_date": "2016-06-01", "event_type": "renewed"},
    ],
    "svt_departures": [
        {"customer_id": "C1", "event_date": "2017-04-01", "event_type": "churned"},
    ],
}


@pytest.mark.parametrize("artefact", [_GREEN_VIA_RENEWAL, _GREEN_VIA_SVT])
def test_an_account_whose_departure_is_recorded_is_explained(artefact):
    assert unexplained_churns(artefact) == []
    assert years_absent_from_the_lifecycle_record(artefact) == []


def test_an_account_that_churned_with_no_departure_row_anywhere_is_reported():
    """The 2026-08-31 defect in miniature: the account is in the churn list and in neither log."""
    artefact = {
        "years": {"2016": {}},
        "churned_billing_accounts": ["C1", "C2"],
        "customer_events": [
            {"customer_id": "C1", "event_date": "2016-06-01", "event_type": "churned"},
        ],
    }
    assert unexplained_churns(artefact) == ["C2"]


def test_a_reported_year_with_no_lifecycle_event_is_reported():
    artefact = {
        "years": {"2016": {}, "2017": {}, "2018": {}},
        "churned_billing_accounts": [],
        "customer_events": [
            {"customer_id": "C1", "event_date": "2016-06-01", "event_type": "renewed"},
            {"customer_id": "C1", "event_date": "2018-06-01", "event_type": "churned"},
        ],
    }
    assert years_absent_from_the_lifecycle_record(artefact) == ["2017"]


def test_the_control_refuses_an_artefact_it_cannot_grade():
    """An empty window and an empty book satisfy both legs by having nothing in them.

    That is the vacuous pass this control would otherwise report, so the live legs assert the
    subject exists BEFORE they assert the property of it. Without this the whole file could go
    green on a truncated or half-written artefact and read as evidence that the record is sound.
    """
    empty = {"years": {}, "churned_billing_accounts": [], "customer_events": []}
    assert unexplained_churns(empty) == []
    assert years_absent_from_the_lifecycle_record(empty) == []


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The live artefact. These are the legs that are red at HEAD.
# ─────────────────────────────────────────────────────────────────────────────────────────────


def test_every_churned_account_in_the_published_run_has_a_departure_record():
    artefact = _live_artefact()
    churned = artefact.get("churned_billing_accounts") or []
    assert churned, "the published run reports no churn at all -- refusing to grade a book that cannot lose anyone"
    missing = unexplained_churns(artefact)
    assert not missing, (
        f"{len(missing)} of {len(churned)} churned accounts have no departure record in "
        f"`{RENEWAL_LOG}` or `{SVT_LOG}`: {missing[:10]}{' ...' if len(missing) > 10 else ''}. "
        "They left with no cause, no roll and no probability. The repair is to carry the "
        "missing route's log through to the published artefact, NEVER to shrink the churn list "
        "or widen this assertion."
    )


def test_every_year_the_published_run_reports_appears_in_its_lifecycle_record():
    artefact = _live_artefact()
    reported = {str(y) for y in (artefact.get("years") or {})}
    assert reported, "the published run reports no years -- refusing to grade an empty window"
    absent = years_absent_from_the_lifecycle_record(artefact)
    assert not absent, (
        f"the run reports {len(reported)} years and its lifecycle record covers "
        f"{len(reported) - len(absent)}: {absent} have no renewal decision and no departure. "
        "Repair the year by making the world produce its events, never by writing rows for it."
    )
