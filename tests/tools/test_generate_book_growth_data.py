"""The growth curve must say WHICH constraint gave it its shape.

Director, 2026-08-24 console: *"if our own code binds growth rather than the simulated economics,
say so on the site and fix it if it's cheap. A growth curve that's an artefact of our engine is an
inconsistency, not a result."*

WHAT IS UNDER TEST is the DISCRIMINATION, not the numbers. A flat year has four possible causes --
the supplier could not afford to quote, the supplier chose not to grow, almost nobody was
switching, or our settlement engine refused to settle the wins -- and exactly one of those is a
defect in us rather than a fact about the company. A file that rendered the curve without that
distinction would be worse than no file: it would publish our own machine limit as a commercial
result.

R15: every control below is paired with the mutation that injects the defect it guards.
"""
from __future__ import annotations

import json

import pytest

from tools import generate_book_growth_data as gb


def _campaign(*bindings, **kw):
    """A campaign record whose years carry the given binding reasons, in order."""
    return {
        "by_year": [
            {"year": 2016 + i, "quotes_issued": 10 * (i + 1), "wins": 3, "accounts_after": 20 + i,
             "spend_gbp": 100.0, "binding": b, "homes_in_market": 400,
             "switching_multiplier": 1.0, "believed_win_rate": 0.2,
             "realised_win_rate_used": None, "planning_on": "belief"}
            for i, b in enumerate(bindings)
        ],
        "notes": kw.get("notes", []),
        "quotes": 100, "wins": 9, "spend_gbp": 1000.0,
        "customer_years_committed": 590.0, "customer_year_budget": 600.0,
    }


def test_a_year_our_engine_stopped_is_flagged_as_OUR_artefact():
    """THE ASSERTION THAT CARRIES THE FILE. settlement_engine is the one binding reason that is a
    fact about us rather than about the company."""
    out = gb.build(_campaign("settlement_engine"))
    year = out["years"][0]

    assert year["binding_is_our_artefact"] is True
    assert year["binding_label"] == "Our settlement engine"
    assert out["engine_bound_years"] == [2016]
    assert "artefact of the simulation" in out["engine_bound_statement"]


@pytest.mark.parametrize("binding", ["capital", "growth_rate", "market", "mandate"])
def test_MUTATION_every_COMMERCIAL_reason_is_NOT_flagged_as_our_artefact(binding):
    """R15 null control. If everything were flagged, the flag would carry no information and the
    test above would pass on a file that simply always said 'artefact'. A thin market in 2022 is a
    real feature of GB retail and must NOT be published as a defect in us."""
    out = gb.build(_campaign(binding))

    assert out["years"][0]["binding_is_our_artefact"] is False
    assert out["engine_bound_years"] == []
    assert "No year was bound by our settlement engine" in out["engine_bound_statement"]


def test_the_statement_counts_only_the_engine_bound_years():
    """Mixed run: the headline must name the artefact years and only those."""
    out = gb.build(_campaign("capital", "settlement_engine", "market", "settlement_engine"))

    assert out["engine_bound_years"] == [2017, 2019]
    assert "2 of 4 years" in out["engine_bound_statement"]
    assert "2017, 2019" in out["engine_bound_statement"]


def test_an_unrecognised_binding_is_shown_VERBATIM_and_never_guessed():
    """A binding reason this file has not been taught is a gap in this file, not a licence to
    classify. It must not silently become 'not our artefact' with a confident label."""
    out = gb.build(_campaign("some_new_reason"))
    year = out["years"][0]

    assert year["binding"] == "some_new_reason"
    assert year["binding_label"] == "some_new_reason"
    assert "Unrecognised" in year["binding_meaning"]


def test_a_missing_record_publishes_UNAVAILABLE_and_never_a_curve_of_zeroes():
    """FAIL-OPEN GUARD (R15). A zeroed curve is a CLAIM -- that the supplier won nothing -- and it
    is indistinguishable on a chart from a real collapse. Absence of a record is not evidence of
    absence of growth."""
    for empty in (None, {}, {"by_year": []}):
        out = gb.build(empty)
        assert out["available"] is False
        assert out["years"] == []
        assert "no campaign record" in out["reason"]
        assert "engine_bound_statement" not in out, (
            "an absent record must not produce a headline about what bound the book"
        )


def test_every_published_money_figure_carries_its_clock():
    """R14: no financial figure without its basis."""
    out = gb.build(_campaign("capital", "settlement_engine"))

    assert out["totals"]["clock"] == "settled"
    for year in out["years"]:
        assert year["spend_gbp"] is not None
        assert year["clock"] == "settled"


def test_the_generator_writes_the_file_and_survives_an_unreadable_record(tmp_path):
    """End-to-end, including the branch that matters operationally: a corrupt or absent source
    must still produce a readable file rather than leaving the previous run's curve live under a
    fresh timestamp."""
    out_path = tmp_path / "book_growth.json"

    src = tmp_path / "campaign.json"
    src.write_text(json.dumps(_campaign("settlement_engine")), encoding="utf-8")
    gb.generate(out_path=out_path, campaign_path=src)
    assert json.loads(out_path.read_text())["engine_bound_years"] == [2016]

    src.write_text("{not json", encoding="utf-8")
    gb.generate(out_path=out_path, campaign_path=src)
    written = json.loads(out_path.read_text())
    assert written["available"] is False, "a corrupt record must not leave a stale curve claiming to be current"


def test_the_generator_is_WIRED_into_the_publish_cycle():
    """The class this project keeps finding: a generator with no caller. The campaign record it
    reads was itself written every run for a reader that did not exist, which is the whole reason
    this file was needed -- so assert the caller, not just the callee."""
    from pathlib import Path

    src = Path(gb.__file__).resolve().parent.parent / "background" / "process_run_complete.py"
    text = src.read_text(encoding="utf-8")
    assert "from tools.generate_book_growth_data import generate" in text
    assert "gen_growth()" in text
