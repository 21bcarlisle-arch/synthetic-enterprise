"""The naive organ asked nothing from 2026-08-10 to 2026-11-02 (27,663 purpose declines, 7 answers).

Three causes, one control over the partition:
- its open questions are published into LATEST.md, which T3 reads back as claims;
- the three that quote GOAL_CONST's "north star" are declined as purpose, and declines used to
  spend the max_new cap, so no real trigger was ever reached;
- a decline was re-logged every cycle, so the log grew 144 lines a day and looked busy.

The three questions below are the organ's own, verbatim from docs/observability/naive_organ_log.jsonl.
"""
import json

from background import naive_organ as organ

LOOPING_QUESTIONS = [
    'If the north star is enterprise value under an absolute survival constraint, what makes '
    '"physics first" the right ordering rather than whichever lever — renewables trends, zonal '
    "pricing, or DSR — most directly moves the survival-risk or valuation numbers you're actually "
    "being measured on?",
    'What evidence connects `route_blocking_decision` sending the W1_2→W1_3 weather-physics '
    'BUILD-open "to the standing" with any change in the supplier\'s enterprise value or its '
    'distance from administration — or is "the standing" just an internal state transition with '
    "no demonstrated bearing on the north star?",
    "What evidence shows that merging this weather-physics design doc actually moves enterprise "
    "value or survival probability, rather than just adding modeling machinery whose payoff is "
    "assumed but never measured against the north star?",
]
PURPOSE_CLAIM = "The north star is inherently enterprise value"
ORDINARY_CLAIM = "Settlement lag is inherent to the Elexon run cycle"


def _cycle(tmp_path, monkeypatch, log, latest):
    monkeypatch.setattr(organ, "ORGAN_LOG_PATH", log)
    monkeypatch.setattr(organ, "LATEST_PATH", latest)
    # Every other surface is empty and the commit clock reads now, so only LATEST.md can fire.
    for name in ("RUN_HISTORY_PATH", "RUN_INSIGHTS_PATH", "AGENT_STATUS_PATH", "IDLE_COUNTER_PATH",
                 "MATURITY_MAP_PATH"):
        monkeypatch.setattr(organ, name, tmp_path / "absent")
    monkeypatch.setattr(organ, "_last_commit_epoch", organ.time.time)
    monkeypatch.setattr(organ.subprocess, "run", lambda *a, **k: type("R", (), {"stdout": ""})())
    return organ.run_organ_cycle(invoke_fn=lambda prompt: "Which run shows it?", log_path=log,
                                 max_new=1)


def test_the_organ_asks_declines_and_never_reads_its_own_questions(tmp_path, monkeypatch):
    log = tmp_path / "naive_organ_log.jsonl"
    log.write_text("".join(json.dumps({
        "entry_id": f"2026-07-13T17:4{i}:00+00:00", "trigger_id": "T3_inherence",
        "mode": "interrogate", "fired_on": {"claim": f"claim {i}"}, "question": q,
        "asked_at": "2026-07-13T17:40:00+00:00", "verdict": "open"}) + "\n"
        for i, q in enumerate(LOOPING_QUESTIONS)))
    digest = organ.render_digest_section(log_path=log, hours=0)
    assert "[unanswered >0h]" in digest
    latest = tmp_path / "LATEST.md"
    # The purpose claim comes first so that, with max_new=1, a decline that spent the cap would
    # leave the ordinary claim unasked.
    latest.write_text(digest + "\n\n" + PURPOSE_CLAIM + ".\n" + ORDINARY_CLAIM + ".\n")

    first = _cycle(tmp_path, monkeypatch, log, latest)
    verdicts = {r["fired_on"]["claim"]: r["verdict"] for r in first}
    assert verdicts == {PURPOSE_CLAIM: "declined_purpose", ORDINARY_CLAIM: "open"}, verdicts

    lines_after_first = log.read_text().count("\n")
    second = _cycle(tmp_path, monkeypatch, log, latest)
    assert second == [], [(r["trigger_id"], r["fired_on"]["claim"]) for r in second]
    assert log.read_text().count("\n") == lines_after_first
