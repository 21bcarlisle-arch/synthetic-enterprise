"""The final-year CLV snapshot was empty, and the report published it as a £3.3m fall.

`WORKER_FINDING_THE_FINAL_YEAR_CLV_SNAPSHOT_IS_EMPTY_AND_THE_REPORT_PUBLISHES_IT_AS_A_THREE_MILLION_FALL_2026-08-17`
(BLOCKING, lane B_commercial). Two defects, one cause and one consequence:

  CAUSE      `_build_clv_snapshots` passed the CALENDAR year end as the cessation
             cutoff. With the newest settlement anywhere at 2025-06-07, every account
             read as ceased 35 days later and the 2025 snapshot came out EMPTY --
             while the same run reported eleven accounts settling in 2025.
  CONSEQUENCE `_section_clv_evolution` ranked that empty year against full ones and
             published "Earliest/lowest: 2025 (£0)" and "Largest YoY fall: 2025
             (£-3,255,946)". The largest movement the series reported was an artefact
             of its own cutoff, and it is the figure a reader's eye goes to.

R15 -- every test here is written to FAIL on the pre-repair code, and the two
anti-fail-open directions are written to fail on the cheapest wrong repair (deleting
the cessation logic, or blanking the section whenever anything looks partial).

R10 -- the invariant is the CLASS, not the row: *no derived headline (extremum, Δ,
ranking) may be computed over a period the run does not fully cover.*
"""
from datetime import date, timedelta

from saas.reporting.annual_report import (
    _build_clv_snapshots,
    _covers_full_year,
    _section_clv_evolution,
    _snapshot_observation_edge,
)

# --------------------------------------------------------------------------
# A run that STOPS MID-YEAR -- the shape that produced the published defect.
# C1 and C2 both settle daily from 2023-01-01 to 2025-06-07 and neither ever
# leaves. Any reading that says the book emptied in 2025 is reading the cutoff.
# --------------------------------------------------------------------------
_LAST_SETTLEMENT = "2025-06-07"


def _settled_days(customer_id: str, start: str, end: str) -> list[dict]:
    day, last = date.fromisoformat(start), date.fromisoformat(end)
    out = []
    while day <= last:
        out.append({
            "customer_id": customer_id,
            "settlement_date": day.isoformat(),
            "revenue_gbp": 2.0,
            "margin_gbp": 1.0,
            # Below the gross margin, as in the real book: the CLV these
            # snapshots carry is valued on this line, not the one above
            # (2026-08-17 margin-basis finding).
            "net_margin_gbp": 0.24,
        })
        day += timedelta(days=1)
    return out


_MIDYEAR_RECORDS = (
    _settled_days("C1", "2023-01-01", _LAST_SETTLEMENT)
    + _settled_days("C2", "2023-01-01", _LAST_SETTLEMENT)
)
_MIDYEAR_CHURN_RISK = {
    "C1": [
        {"renewal_period": "2023-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2024-01", "bill_shock_count": 0, "churn_probability": 0.06},
    ],
    "C2": [
        {"renewal_period": "2023-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2024-01", "bill_shock_count": 1, "churn_probability": 0.07},
    ],
}
_MIDYEAR_YEARS = ["2023", "2024", "2025"]


def _snapshots() -> dict:
    return _build_clv_snapshots(_MIDYEAR_RECORDS, _MIDYEAR_CHURN_RISK, _MIDYEAR_YEARS)


def _as_of_map() -> dict:
    return {
        yr: _snapshot_observation_edge(_MIDYEAR_RECORDS, as_of=f"{yr}-12-31")
        for yr in _MIDYEAR_YEARS
    }


def _section() -> str:
    return _section_clv_evolution(
        {"clv_snapshots": _snapshots(), "clv_snapshot_as_of": _as_of_map()}
    )


# --------------------------------------------------------------------------
# CAUSE: the snapshot must be taken at the observation edge, not the calendar
# year end.
# --------------------------------------------------------------------------


def test_the_final_partial_year_still_values_the_book():
    """THE DEFECT ITSELF. Two accounts are settling right up to the run's last day.
    On the pre-repair code (`as_of=cutoff`) this snapshot is `{}` -- every account
    read as ceased because 2025-12-31 is 207 days past the last settlement anywhere.
    """
    snapshots = _snapshots()
    assert snapshots["2025"], (
        "the final-year snapshot is empty while both accounts were still settling -- "
        "the cessation cutoff is being measured against a date the run never reached"
    )
    assert set(snapshots["2025"]) == {"C1", "C2"}
    assert all(v > 0 for v in snapshots["2025"].values())


def test_the_observation_edge_is_the_last_settlement_not_the_year_end():
    assert _snapshot_observation_edge(_MIDYEAR_RECORDS, as_of="2025-12-31") == _LAST_SETTLEMENT
    # And it is bounded: a cutoff mid-run never sees past itself.
    assert _snapshot_observation_edge(_MIDYEAR_RECORDS, as_of="2024-03-31") == "2024-03-31"
    assert _snapshot_observation_edge(_MIDYEAR_RECORDS, as_of="2019-01-01") is None


def test_a_genuinely_departed_account_is_still_excluded_at_a_midyear_edge():
    """ANTI-FAIL-OPEN, direction two -- named in the finding.

    The cheapest way to pass the test above is to stop excluding ceased accounts at
    all. C3 stops settling in 2024 and must be ABSENT from the 2025 snapshot even
    though that snapshot is now taken at a mid-year edge. If this goes green while
    the clamp is removed, the clamp is doing nothing; if it goes red, the repair has
    disabled the cessation logic instead of re-dating it.
    """
    records = _MIDYEAR_RECORDS + _settled_days("C3", "2023-01-01", "2024-02-01")
    churn = dict(_MIDYEAR_CHURN_RISK)
    churn["C3"] = [
        {"renewal_period": "2023-01", "bill_shock_count": 0, "churn_probability": 0.05},
    ]
    snapshots = _build_clv_snapshots(records, churn, _MIDYEAR_YEARS)
    assert "C3" in snapshots["2023"], "C3 was on supply through 2023 and must be valued there"
    assert "C3" not in snapshots["2025"], (
        "C3 last settled 2024-02-01, 16 months before the 2025 edge -- it must read as ceased"
    )


def test_the_exclusion_is_not_retrospective():
    """Point-in-Time, the other way: a departure must not be back-dated into a year
    the supplier had not yet observed it in."""
    records = _MIDYEAR_RECORDS + _settled_days("C3", "2023-01-01", "2024-02-01")
    churn = dict(_MIDYEAR_CHURN_RISK)
    churn["C3"] = [
        {"renewal_period": "2023-01", "bill_shock_count": 0, "churn_probability": 0.05},
    ]
    snapshots = _build_clv_snapshots(records, churn, _MIDYEAR_YEARS)
    assert snapshots["2023"]["C3"] > 0


# --------------------------------------------------------------------------
# CONSEQUENCE: the derived-headline guard (R10 class invariant).
# --------------------------------------------------------------------------


def test_the_truncated_year_is_not_named_as_the_largest_yoy_fall():
    """THE PUBLISHED SYMPTOM, as a control. The finding's own named mutation:
    truncate the run to mid-year and the section must NOT name the truncated year as
    the largest fall. Pre-repair this printed `Largest YoY fall: 2025 (£-...)`.
    """
    result = _section()
    for line in result.splitlines():
        if "Largest YoY fall" in line or "Lowest:" in line or "Earliest/lowest" in line:
            assert "2025" not in line, (
                f"a period the run does not cover is being ranked against full years: {line}"
            )


def test_an_empty_final_year_is_excluded_even_with_no_as_of_map():
    """The guard must hold on a run output that predates the as-of map -- which is
    the artefact this defect was actually found in. The empty population is the
    detectable shape on its own.
    """
    result = _section_clv_evolution({
        "clv_snapshots": {
            "2023": {"C1": 1000.0},
            "2024": {"C1": 3000.0},
            "2025": {},
        }
    })
    assert "Largest YoY fall" not in result, (
        "an empty year was ranked as a fall with no coverage evidence to excuse it"
    )
    assert "2024" in result


def test_the_partial_year_is_still_shown_as_its_own_reading():
    """ANTI-FAIL-OPEN, direction one: the cheapest way to pass the guard above is to
    drop the partial year, or the whole section, entirely. A partial year is a real
    reading of a shorter period and must still render -- labelled, with its own
    as-of date, and with its Δ withheld.
    """
    result = _section()
    assert "2025 *" in result, "the partial year must still appear as a row"
    assert _LAST_SETTLEMENT in result, "the partial row must carry its own as-of date"
    assert "Partial period" in result
    # ...and the full years keep their headlines rather than the section going dark.
    assert "Peak portfolio CLV" in result
    assert "2024" in result


def test_the_partial_years_delta_is_withheld():
    """A mid-year reading minus a year-end reading is not a YoY move. The Δ cell for
    the partial year must be the em-dash, not an arithmetic difference."""
    result = _section()
    row = [ln for ln in result.splitlines() if ln.startswith("| 2025 *")]
    assert row, "expected a 2025 row"
    assert row[0].rstrip().endswith("— |"), (
        f"the partial year published a like-for-like Δ against a full year: {row[0]}"
    )


def test_covers_full_year_predicate_both_directions():
    """The R10 predicate itself, pinned independently of its callers."""
    assert _covers_full_year("2024", "2024-12-31")
    assert _covers_full_year("2024", "2025-06-07")
    assert not _covers_full_year("2025", "2025-06-07")
    assert not _covers_full_year("2025", None), "no observation is not full coverage"
