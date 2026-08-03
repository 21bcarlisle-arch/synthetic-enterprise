"""SITE_EH2 -- the predictions ledger MUST be able to record a MISS.

WHY THIS FILE EXISTS. A cold-eyes Expert Hour found this project's own R15 breach
on its most load-bearing public surface: on the door billed as "the page an expert
checks first", NO prediction could ever be wrong. Every failure routed to an
unfalsifiable escape hatch -- a renewal miss was recorded "inconclusive" with the
note "not counted as a miss", 25 of 26 hedge calls were "ungraded -- market data
has not advanced", one C9 prediction logged four times was counted as four, and
the headline was a log-line count that read as a track record.

A ledger whose worst possible verdict is "inconclusive" is not evidence. This file
is the control that proves the new ledger CAN return a bad verdict, and that it
does so for the right reason.

WHAT IS ASSERTED, and how each maps to R15's three killer patterns:

  MUTATION (the exit criterion). A prediction that is demonstrably wrong against
  the INDEPENDENTLY observed outcome renders as MISS on the surface -- and the
  same machinery with a correct prediction renders ON TARGET, so the MISS is
  caused by the wrongness and not by the harness.

  TAUTOLOGY. The prediction is read from the pre-registered decision log
  (track_record_scorecard.json) and the outcome from a different file with a
  different writer (live_portfolio.json). Two tests move ONE source at a time and
  assert the verdict follows each independently -- neither value is derived from
  the other.

  FAIL-OPEN. Missing, zero, empty, non-finite and malformed outcome data must
  grade UNGRADEABLE -- never ON TARGET, and never AWAITING-forever. An unbounded
  wait is itself the fail-open this atom was minted for, so the horizon is tested
  from both sides: inside it AWAITING, past it UNGRADEABLE.

  FAIL-SILENT. If the outcome source or the ledger source is unavailable, the
  surface must SAY the check failed. A blank panel that reads as a clean record is
  the failure mode.

  R10 (the class, not the instance). _ledger_integrity re-derives the closed
  verdict vocabulary and the bounded-wait guarantee over the finished rows, and a
  violation is rendered loudly. A test mutates a row into the exact old defect
  (permanently parked) and proves the integrity check FIRES.

R11 throughout: assertions are on the RENDERED pixel produced by the page's own
inline JavaScript via the Node/vm door harness, not on the generator's return
value alone. R12: no assertion here rewards a better-looking track record -- the
live expectation is "0 of 2 graded", and that is what ships.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_door_harness.mjs"
DATA = HERE.parent / "data" / "proof.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _gpd():
    if str(PROJECT) not in sys.path:
        sys.path.insert(0, str(PROJECT))
    import tools.generate_proof_data as gpd

    return gpd


def _render(predictions=None) -> dict:
    """Render the whole door, optionally with an injected predictions payload."""
    data = json.loads(DATA.read_text())
    if predictions is not None:
        data["predictions"] = predictions
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data), capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _surface(out: dict) -> str:
    return out["pred-body"]["innerHTML"] + out["pred-intro"]["innerHTML"] + \
        out["pred-kpis"]["innerHTML"] + out["pred-intro"]["textContent"] + \
        out["pred-body"]["textContent"]


# --------------------------------------------------------------------------- #
# Fixtures: a synthetic pre-registered log + a synthetic observed portfolio.
# The two are SEPARATE inputs on purpose -- that separation is the independence
# the TAUTOLOGY tests below exercise.
# --------------------------------------------------------------------------- #
OBSERVED_C9_RATE = 210.0
DEFAULT_PORTFOLIO = {
    "generated_at": "2026-07-09T00:00:00Z",
    "source_year": 2025,
    "customers": [
        {"cid": "C9", "commodity": "electricity",
         "current_rate_gbp_per_mwh": OBSERVED_C9_RATE,
         "last_renewal_date": "2024-06-29"},
    ],
}
MISSING = object()  # the file does not exist at all


def _entry(day="2026-07-08", cid="C9", renewal_date="2024-01-01", rate=OBSERVED_C9_RATE):
    """One pre-registered renewal-price flag log LINE.

    renewal_date defaults to a date the observed snapshot has already passed, so
    the entry is genuinely gradeable and a wrong rate must land as a MISS.
    """
    return {"decision_run_at": day, "cid": cid, "renewal_date": renewal_date,
            "proposed_rate_gbp_per_mwh": rate,
            "outcome": "no_renewal_detected_yet", "graded": False}


def _scorecard(renewal=(), hedge=(), today="2026-07-10", tol=0.02,
               upstream_graded=0, log_entry_count=None):
    return {
        "generated_at": today + "T00:00:00Z",
        "wall_clock_today": today,
        "clock_started": "2026-07-04",
        "log_entry_count": len(renewal) + len(hedge)
        if log_entry_count is None else log_entry_count,
        "renewal_tolerance_pct": tol,
        "renewal_grading": {"graded": [], "pending": [],
                            "inconclusive": list(renewal),
                            "graded_count": upstream_graded,
                            "inconclusive_count": len(renewal)},
        "hedge_grading": {"entries": list(hedge), "graded_count": 0,
                          "ungraded_count": len(hedge),
                          "current_market_data_stale_days": 1},
        "retention_ev_log": {"logged_count": 0, "graded_count": 0,
                             "note": "no realized-value join exists yet",
                             "entries": []},
    }


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    gpd = _gpd()
    counter = {"n": 0}

    def build(scorecard, portfolio=DEFAULT_PORTFOLIO):
        counter["n"] += 1
        n = counter["n"]
        sc_path = tmp_path / f"scorecard_{n}.json"
        if scorecard is MISSING:
            sc_path = tmp_path / f"absent_scorecard_{n}.json"
        elif isinstance(scorecard, str):
            sc_path.write_text(scorecard)
        else:
            sc_path.write_text(json.dumps(scorecard))
        monkeypatch.setattr(gpd, "SCORECARD_PATH", sc_path)

        pf_path = tmp_path / f"portfolio_{n}.json"
        if portfolio is MISSING:
            pf_path = tmp_path / f"absent_portfolio_{n}.json"
        elif isinstance(portfolio, str):
            pf_path.write_text(portfolio)
        else:
            pf_path.write_text(json.dumps(portfolio))
        monkeypatch.setattr(gpd, "LIVE_PORTFOLIO_PATH", pf_path)
        return gpd._predictions_ledger()

    return build


def _only_row(led):
    rows = led["renewal"]["rows"]
    assert len(rows) == 1, f"expected one distinct renewal prediction, got {len(rows)}"
    return rows[0]


# =========================================================================== #
# R15 MUTATION -- THE EXIT CRITERION. A wrong prediction renders as a MISS.
# =========================================================================== #
def test_deliberately_wrong_prediction_renders_as_a_miss(ledger):
    # The observed outcome is 210.00 GBP/MWh. The pre-registered prediction says
    # 100.00 -- wrong by -52%, far outside the 2% tolerance. This MUST be a MISS,
    # on the rendered surface, not merely in the generator's return value.
    led = ledger(_scorecard(renewal=[_entry(rate=100.0)]))
    row = _only_row(led)
    assert row["verdict"] == "MISS", row
    assert row["observed_rate_gbp_per_mwh"] == OBSERVED_C9_RATE
    assert row["delta_pct"] == 110.0, row["delta_pct"]
    assert led["missed"] == 1 and led["graded"] == 1 and led["on_target"] == 0

    out = _render(led)
    body = out["pred-body"]["innerHTML"]
    assert '<span class="o-miss">MISS</span>' in body, body
    assert "MISS: C9 renewed on 2024-06-29 at 210.00 GBP/MWh against 100.00 predicted" \
        in body, body
    # the headline states the miss rather than burying it
    assert "1 of 1 distinct predictions graded (0 on target, 1 MISSED)" in body, body
    # ...and the KPI row flags it as an alarm, not a neutral tile
    assert '<div class="kpi alarm"><div class="kpi-l">Missed</div><div class="kpi-v">1</div>' \
        in out["pred-kpis"]["innerHTML"], out["pred-kpis"]["innerHTML"]


def test_correct_prediction_renders_as_on_target(ledger):
    # The CONTROL for the mutation above: identical machinery, identical sources,
    # only the predicted rate is now right. If this also rendered MISS the test
    # above would prove nothing (a constant verdict is not a grade).
    led = ledger(_scorecard(renewal=[_entry(rate=OBSERVED_C9_RATE)]))
    row = _only_row(led)
    assert row["verdict"] == "ON TARGET", row
    assert led["on_target"] == 1 and led["missed"] == 0 and led["graded"] == 1

    body = _render(led)["pred-body"]["innerHTML"]
    assert '<span class="o-target">ON TARGET</span>' in body, body
    assert "MISS" not in body.replace("MISSED", ""), body


def test_the_grade_boundary_is_the_stated_tolerance(ledger):
    # The tolerance is a published number, so it must actually bind: 1.9% inside
    # the 2% band is ON TARGET, 2.1% outside it is a MISS. (Not a target-seeking
    # assertion -- it pins that the band the surface PRINTS is the band applied.)
    inside = ledger(_scorecard(renewal=[_entry(rate=OBSERVED_C9_RATE / 1.019)]))
    outside = ledger(_scorecard(renewal=[_entry(rate=OBSERVED_C9_RATE / 1.021)]))
    assert _only_row(inside)["verdict"] == "ON TARGET"
    assert _only_row(outside)["verdict"] == "MISS"


# =========================================================================== #
# KILLER PATTERN 1 -- TAUTOLOGY. The prediction and the outcome are independent.
# Move exactly one source at a time; the verdict must follow each on its own.
# =========================================================================== #
def test_verdict_follows_the_outcome_source_alone(ledger):
    # Prediction held constant at 210.0; only live_portfolio.json moves.
    sc = _scorecard(renewal=[_entry(rate=OBSERVED_C9_RATE)])
    matching = ledger(sc, DEFAULT_PORTFOLIO)
    moved = json.loads(json.dumps(DEFAULT_PORTFOLIO))
    moved["customers"][0]["current_rate_gbp_per_mwh"] = 999.0
    diverged = ledger(sc, moved)
    assert _only_row(matching)["verdict"] == "ON TARGET"
    assert _only_row(diverged)["verdict"] == "MISS", \
        "the verdict ignored the observed source -- the grade is a tautology"
    # and the moved observed value reaches the pixel, not just the verdict
    assert "999" in _render(diverged)["pred-body"]["innerHTML"]


def test_verdict_follows_the_prediction_alone(ledger):
    # Outcome held constant at 210.0; only the pre-registered prediction moves.
    right = ledger(_scorecard(renewal=[_entry(rate=OBSERVED_C9_RATE)]))
    wrong = ledger(_scorecard(renewal=[_entry(rate=42.0)]))
    assert _only_row(right)["verdict"] == "ON TARGET"
    assert _only_row(wrong)["verdict"] == "MISS", \
        "the verdict ignored the pre-registered prediction -- the grade is a tautology"


# =========================================================================== #
# KILLER PATTERN 2 -- FAIL-OPEN. Missing / zero / empty / non-finite / malformed
# outcome data must never become a pass, and never an indefinite wait.
# =========================================================================== #
@pytest.mark.parametrize("observed_rate", [None, float("nan"), float("inf"), "210", {}])
def test_malformed_observed_rate_is_ungradeable_not_a_pass(ledger, observed_rate):
    pf = json.loads(json.dumps(DEFAULT_PORTFOLIO))
    # json can't carry NaN/Inf faithfully through the file, so inject via a raw
    # JSON text body for the non-finite cases (Python's json emits NaN/Infinity
    # literals, which its own loader accepts -- exactly the malformed input a real
    # broken writer would leave behind).
    pf["customers"][0]["current_rate_gbp_per_mwh"] = observed_rate
    led = ledger(_scorecard(renewal=[_entry(rate=OBSERVED_C9_RATE)]),
                 json.dumps(pf))
    row = _only_row(led)
    assert row["verdict"] == "UNGRADEABLE", (observed_rate, row)
    assert led["on_target"] == 0 and led["graded"] == 0, \
        f"malformed observed rate {observed_rate!r} produced a grade"
    assert row["blocker"], "an undecided row must name its blocker"
    body = _render(led)["pred-body"]["innerHTML"]
    assert "UNGRADEABLE" in body and "missing, zero or non-finite" in body, body


def test_zero_predicted_rate_is_ungradeable_not_a_pass(ledger):
    # A zero predicted rate makes the tolerance band zero-wide; a naive
    # implementation would call an exact-match "on target" or divide by zero.
    led = ledger(_scorecard(renewal=[_entry(rate=0.0)]))
    row = _only_row(led)
    assert row["verdict"] == "UNGRADEABLE", row
    assert led["on_target"] == 0


def test_empty_portfolio_snapshot_is_ungradeable_not_a_pass(ledger):
    led = ledger(_scorecard(renewal=[_entry()]), {"generated_at": "2026-07-09T00:00:00Z",
                                                  "customers": []})
    row = _only_row(led)
    assert row["verdict"] == "UNGRADEABLE", row
    assert led["outcome_source_available"] is False
    assert "ZERO identified accounts" in (led["outcome_source_detail"] or "")
    assert led["graded"] == 0


def test_absent_account_is_ungradeable_not_a_pass(ledger):
    led = ledger(_scorecard(renewal=[_entry(cid="C_NOT_THERE")]))
    row = _only_row(led)
    assert row["verdict"] == "UNGRADEABLE", row
    assert "absent from the observed portfolio snapshot" in row["blocker"]["detail"]
    assert led["graded"] == 0


def test_malformed_portfolio_payload_is_ungradeable_not_a_pass(ledger):
    led = ledger(_scorecard(renewal=[_entry()]), "{ this is not json")
    assert _only_row(led)["verdict"] == "UNGRADEABLE"
    assert led["outcome_source_available"] is False
    assert led["graded"] == 0


def test_prediction_with_no_renewal_date_is_ungradeable_not_a_pass(ledger):
    led = ledger(_scorecard(renewal=[_entry(renewal_date=None)]))
    row = _only_row(led)
    assert row["verdict"] == "UNGRADEABLE", row
    assert "malformed" in row["verdict_reason"].lower()


# =========================================================================== #
# KILLER PATTERN 3 -- FAIL-SILENT. An unavailable check is a FAILED check; the
# surface must say so rather than render a clean (or blank) record.
# =========================================================================== #
def test_unavailable_outcome_source_is_a_failed_check_not_a_clean_record(ledger):
    led = ledger(_scorecard(renewal=[_entry()]), MISSING)
    row = _only_row(led)
    assert row["verdict"] == "UNGRADEABLE", row
    assert "unavailable check is a FAILED check" in row["verdict_reason"]
    assert led["graded"] == 0 and led["awaiting"] == 0, \
        "an unavailable grader must not leave entries quietly waiting"
    body = _render(led)["pred-body"]["innerHTML"]
    assert "is unavailable" in body, body
    assert "FAILED check" in body, body


def test_unavailable_ledger_source_renders_a_loud_failure(ledger):
    led = ledger(MISSING)
    assert led["available"] is False
    assert "LEDGER SOURCE UNAVAILABLE" in led["headline"]
    out = _render(led)
    body = out["pred-body"]["innerHTML"]
    # NOT a blank panel: the failure is on the pixel, in the failure style.
    assert 'class="pred-fail"' in body, body
    assert "LEDGER SOURCE UNAVAILABLE" in body, body
    assert "NOTHING on this door has been graded" in body, body
    assert "FAILED check" in body, body


# =========================================================================== #
# G3 BOUNDED UNDECIDEDNESS -- tested from BOTH sides. An unbounded "inconclusive"
# was the fail-open; the bound only counts if it actually flips.
# =========================================================================== #
def _pending_scorecard(today, first="2026-07-08"):
    # renewal_date far in the future of the snapshot's clock => genuinely undecided
    return _scorecard(renewal=[_entry(day=first, renewal_date="2030-01-01")],
                      today=today)


def test_awaiting_inside_the_horizon_becomes_ungradeable_past_it(ledger):
    gpd = _gpd()
    horizon = gpd.INCONCLUSIVE_HORIZON_DAYS
    inside = ledger(_pending_scorecard(today="2026-07-15"))   # 7 days old
    edge = ledger(_pending_scorecard(today="2026-07-22"))     # exactly `horizon`
    past = ledger(_pending_scorecard(today="2026-08-30"))     # 53 days old

    ri, re_, rp = _only_row(inside), _only_row(edge), _only_row(past)
    assert ri["verdict"] == "AWAITING OUTCOME", ri
    assert ri["days_since_first_logged"] == 7
    assert ri["horizon_deadline"] == "2026-07-22"
    assert re_["verdict"] == "AWAITING OUTCOME", "the horizon must be inclusive at the edge"
    assert re_["days_since_first_logged"] == horizon
    assert rp["verdict"] == "UNGRADEABLE", \
        "an entry past the horizon is still parked -- the escape hatch is unbounded"
    assert "struck from the track record" in rp["verdict_reason"]
    assert "is not a pass, and it is not still waiting" in rp["verdict_reason"]

    # ...and the flip is visible on the surface, with the horizon stated.
    body_in = _render(inside)["pred-body"]["innerHTML"]
    body_out = _render(past)["pred-body"]["innerHTML"]
    assert '<span class="o-awaiting">AWAITING OUTCOME</span>' in body_in, body_in
    assert "not cleared by 2026-07-22 this entry is declared UNGRADEABLE" in body_in, body_in
    assert '<span class="o-ungradeable">UNGRADEABLE</span>' in body_out, body_out


def test_undecided_entry_names_its_blocker_and_the_blockers_age(ledger):
    # "Inconclusive" with no named cause is the unfalsifiable state. An undecided
    # entry must name the snapshot, its stamp and its AGE.
    led = ledger(_pending_scorecard(today="2026-07-15"))
    blk = _only_row(led)["blocker"]
    assert blk, "an undecided entry with no named blocker IS the unfalsifiable state"
    assert blk["source"].endswith("live_portfolio.json"), blk
    assert blk["stamp"] == "2026-07-09T00:00:00Z", blk
    assert blk["age_days"] == 6, blk
    assert "has not advanced past the flagged date" in blk["detail"], blk
    body = _render(led)["pred-body"]["innerHTML"]
    assert "Blocked on" in body and "live_portfolio.json" in body, body
    assert "6 day(s) old" in body, body


def test_malformed_log_date_is_ungradeable_not_an_unbounded_wait(ledger):
    # If the log date is unparseable the wait CANNOT be proven bounded, so the
    # entry must be struck rather than parked. (Fail closed, not fail open.)
    led = ledger(_scorecard(renewal=[_entry(day="not-a-date",
                                            renewal_date="2030-01-01")]))
    row = _only_row(led)
    assert row["verdict"] == "UNGRADEABLE", row
    assert "cannot be bounded" in row["verdict_reason"], row["verdict_reason"]
    assert "unbounded wait is the fail-open" in row["verdict_reason"]


def test_hedge_stance_is_bounded_and_never_invented_a_grade(ledger):
    # No outcome source for a hedge stance exists in this codebase. The correct
    # output is UNGRADEABLE with the missing signal named -- NOT an invented grade,
    # and NOT a permanent "ungraded -- market data has not advanced".
    hedge = [{"decision_run_at": "2026-07-04", "hedge_recommendation": "INCREASE",
              "outcome": "ungraded -- market data has not advanced"}]
    led = ledger(_scorecard(hedge=hedge, today="2026-08-30"))
    row = led["hedge"]["rows"][0]
    assert row["verdict"] == "UNGRADEABLE", row
    assert row["blocker"]["detail"].startswith("no outcome source exists"), row
    assert led["on_target"] == 0 and led["graded"] == 0
    body = _render(led)["pred-body"]["innerHTML"]
    assert "nothing in this codebase joins a hedge stance to the realised cost" in body


# =========================================================================== #
# G1 DE-DUPLICATION and the honest headline.
# =========================================================================== #
def test_a_reglogged_prediction_is_one_row_with_a_relog_count(ledger):
    days = ["2026-07-04", "2026-07-05", "2026-07-06", "2026-07-07"]
    led = ledger(_scorecard(renewal=[_entry(day=d, renewal_date="2030-01-01")
                                     for d in days], today="2026-07-10"))
    row = _only_row(led)
    assert row["relog_count"] == 4
    assert row["first_logged_at"] == "2026-07-04"
    assert row["last_logged_at"] == "2026-07-07"
    assert led["log_lines"] == 4 and led["distinct_predictions"] == 1
    body = _render(led)["pred-body"]["innerHTML"]
    assert body.count('class="lg-pred"') == 1, "the same prediction rendered twice"
    assert "re-logged 4&times;" in body and "counted once" in body, body
    assert "4 log line(s) de-duplicate to 1 distinct prediction(s)" in body, body


def test_genuinely_different_predictions_are_not_collapsed(ledger):
    # The de-dup must not swallow real predictions: a different price on the same
    # account/date is a DIFFERENT prediction and gets its own row.
    led = ledger(_scorecard(renewal=[_entry(rate=100.0), _entry(rate=180.0)]))
    assert led["distinct_predictions"] == 2, led["renewal"]["rows"]
    assert led["log_lines"] == 2
    assert {r["verdict"] for r in led["renewal"]["rows"]} == {"MISS"}


def test_headline_does_not_imply_a_track_record_when_nothing_is_graded(ledger):
    led = ledger(_pending_scorecard(today="2026-08-30"))
    assert "NO TRACK RECORD HAS BEEN ESTABLISHED" in led["headline"]
    body = _render(led)["pred-body"]["innerHTML"]
    assert "0 of 1 distinct predictions graded" in body, body
    assert "NO TRACK RECORD HAS BEEN ESTABLISHED" in body, body


def test_derived_counts_govern_over_the_upstream_claim(ledger):
    # Upstream claimed a grade for an entry whose own recorded outcome read
    # "gradeable_but_no_grading_logic_yet". A claimed grade is not a grade: the
    # derived count governs and the disagreement is PUBLISHED, not hidden.
    led = ledger(_scorecard(renewal=[_entry(renewal_date="2030-01-01")],
                            today="2026-08-30", upstream_graded=5,
                            log_entry_count=99))
    assert led["graded"] == 0
    assert led["log_entry_count_upstream_claimed"] == 99
    assert led["log_lines"] == 1
    assert "claims 5 graded across 99 log entries" in led["reconciliation"]
    assert "derives 0 graded across 1 log lines" in led["reconciliation"]
    body = _render(led)["pred-body"]["innerHTML"]
    assert "claims 5 graded across 99 log entries" in body, body


def test_a_constant_recommendation_is_labelled_not_scored(ledger):
    hedge = [{"decision_run_at": f"2026-07-{d:02d}", "hedge_recommendation": "INCREASE",
              "outcome": "ungraded -- market data has not advanced"}
             for d in range(4, 20)]
    led = ledger(_scorecard(hedge=hedge, today="2026-08-30"))
    assert led["hedge"]["distinct"] == 1 and led["hedge"]["log_lines"] == 16
    assert "A constant is not a forecast" in led["hedge"]["constant_warning"]
    body = _render(led)["pred-body"]["innerHTML"]
    assert "A constant is not a forecast" in body, body
    assert "ONE prediction re-logged 16 times" in body, body


# =========================================================================== #
# G6 / R10 -- the CLASS fails automatically, and the class-check can itself FAIL.
# =========================================================================== #
def test_ledger_integrity_holds_on_the_live_data():
    gpd = _gpd()
    led = gpd._predictions_ledger()
    assert led["integrity"]["ok"] is True, led["integrity"]["violations"]
    for row in led["renewal"]["rows"] + led["hedge"]["rows"]:
        assert row["verdict"] in gpd.VERDICT_VOCABULARY, row


def test_ledger_integrity_fires_on_a_permanently_parked_row():
    # The MUTATION for the class-check: re-introduce the exact original defect --
    # an entry parked in an undecided state past the horizon -- and prove the
    # integrity check catches it AND that the surface shouts about it.
    gpd = _gpd()
    parked = dict(kind="renewal", label="C9 @ 2025-06-29",
                  verdict=gpd.V_AWAITING, days_since_first_logged=999,
                  blocker={"source": "x", "detail": "y", "stamp": None,
                           "age_days": None})
    integ = gpd._ledger_integrity([parked])
    assert integ["ok"] is False
    assert "permanently parked" in " ".join(integ["violations"]), integ

    led = gpd._predictions_ledger()
    led["integrity"] = integ
    body = _render(led)["pred-body"]["innerHTML"]
    assert "LEDGER INTEGRITY FAILURE" in body, body
    assert "permanently parked" in body, body


def test_ledger_integrity_fires_on_a_verdict_outside_the_vocabulary():
    gpd = _gpd()
    integ = gpd._ledger_integrity([dict(kind="renewal", label="X",
                                        verdict="inconclusive")])
    assert integ["ok"] is False
    assert "outside the closed vocabulary" in " ".join(integ["violations"]), integ


def test_ledger_integrity_fires_on_an_undecided_row_with_no_blocker():
    gpd = _gpd()
    integ = gpd._ledger_integrity([dict(kind="hedge", label="INCREASE",
                                        verdict=gpd.V_UNGRADEABLE,
                                        days_since_first_logged=1)])
    assert integ["ok"] is False
    assert "names no blocker" in " ".join(integ["violations"]), integ


def test_an_unrecognised_verdict_never_renders_as_a_clean_verdict():
    # Defence in depth on the render side: if a verdict string ever escapes the
    # vocabulary, it must render in the FAILURE style, never neutral or green.
    gpd = _gpd()
    led = gpd._predictions_ledger()
    led["renewal"]["rows"] = [dict(cid="C9", renewal_date="2025-06-29",
                                   proposed_rate_gbp_per_mwh=153.49,
                                   relog_count=1, first_logged_at="2026-07-04",
                                   last_logged_at="2026-07-04",
                                   verdict="inconclusive",
                                   verdict_reason="not counted as a miss")]
    body = _render(led)["pred-body"]["innerHTML"]
    assert '<span class="o-miss">inconclusive</span>' in body, body
    assert "o-target" not in body, body


# =========================================================================== #
# R11 on the LIVE published data: the shipped headline is the one the data
# supports, and the old escape-hatch idiom is gone from the surface.
# =========================================================================== #
def test_live_surface_renders_the_derived_headline():
    gpd = _gpd()
    led = gpd._predictions_ledger()
    out = _render()  # the published site/data/proof.json, untouched
    body = out["pred-body"]["innerHTML"]
    published = json.loads(DATA.read_text())["predictions"]
    assert published["headline"] == led["headline"], \
        "site/data/proof.json is stale against the generator -- regenerate it"
    assert published["headline"] in body, body
    # The headline is a grading statement, not a log-line count.
    assert "distinct predictions graded" in body, body
    # ...and the old KPI that implied a record is gone.
    assert "Log entries" not in out["pred-kpis"]["innerHTML"], out["pred-kpis"]["innerHTML"]
    assert "Distinct predictions" in out["pred-kpis"]["innerHTML"]


def test_live_surface_has_no_unfalsifiable_escape_hatch_language():
    surface = _surface(_render())
    for hatch in ("not counted as a miss",
                  "no_renewal_detected_yet",
                  "ungraded -- market data has not advanced",
                  "mostly-ungraded state below is the honest early picture"):
        assert hatch not in surface, f"escape-hatch idiom still on the surface: {hatch!r}"
    # The upstream string "gradeable_but_no_grading_logic_yet" MAY appear, but only
    # where the surface is explaining that it is NOT a grade -- never as a verdict.
    hatch = "gradeable_but_no_grading_logic_yet"
    if hatch in surface:
        assert "is not a grade" in surface, \
            f"{hatch!r} appears on the surface without being disowned as a grade"
        for span in ('o-target">' + hatch, 'o-inconc">' + hatch, 'o-ungraded">' + hatch):
            assert span not in surface, f"{hatch!r} is still rendering as a verdict"


def test_live_surface_states_the_horizon_and_names_the_stale_snapshot():
    gpd = _gpd()
    led = gpd._predictions_ledger()
    out = _render()
    body = out["pred-body"]["innerHTML"]
    intro = out["pred-intro"]["innerHTML"]
    assert f"nothing waits longer than {gpd.INCONCLUSIVE_HORIZON_DAYS} days" in intro, intro
    assert "live_portfolio.json" in body, body
    assert led["outcome_source_stamp"] in body, body
    assert f"{led['outcome_source_age_days']} day(s) old" in body, body
    assert "day(s) old" in body


def test_live_repeated_c9_prediction_is_one_row():
    # The specific instance the Expert Hour caught: the SAME C9 prediction logged
    # on consecutive days rendered as several rows implying several predictions.
    #
    # RELATIONAL, NEVER PINNED. The live decision log is appended to every run, so
    # the re-log count and the flagged renewal date are GENERATED values that move.
    # Pinning them here would put a literal from today's data into a control that
    # gates publishing -- the exact defect that wedged publishing for four days.
    # So assert the de-dup RELATIONSHIP instead: N live log lines collapse to
    # `distinct` rows, each row carries its own re-log count, and each renders once.
    gpd = _gpd()
    led = gpd._predictions_ledger()
    body = _render()["pred-body"]["innerHTML"]
    section = led["renewal"]
    rows = section["rows"]

    # The section's own arithmetic must close: the parts sum to the whole.
    assert len(rows) == section["distinct"], (len(rows), section["distinct"])
    assert sum(r["relog_count"] for r in rows) == section["log_lines"], section

    # ...and de-dup must actually be under test. If the live log ever stops
    # repeating a prediction this assertion is vacuous, so fail LOUDLY rather
    # than passing on an empty premise (an untested control is a failed control).
    assert section["log_lines"] > section["distinct"], (
        "live renewal log no longer repeats any prediction, so this control no "
        f"longer exercises de-duplication: {section['log_lines']} log line(s), "
        f"{section['distinct']} distinct")

    for row in rows:
        n = row["relog_count"]
        assert body.count(f"renewal {row['renewal_date']}") == 1, \
            f"the {row['cid']} prediction still repeats on the surface"
        if n > 1:
            assert f"re-logged {n}&times;" in body, body
