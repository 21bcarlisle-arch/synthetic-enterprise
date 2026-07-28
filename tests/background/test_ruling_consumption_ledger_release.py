"""R15 both-ways for the ruling-consumption -> block-release REPORTING mechanism
(atom `ruling_consumption_ledger_release`, DISCOVER §7).

The mechanism is READ-ONLY on authority: it detects a ruling's `LEDGER: <ACTION> <target>`
directive, CONFIRMS an authenticated ledger entry exists, and reports the block UNRELEASED when
it does not -- it NEVER writes a ledger entry (R16 preserved by construction). These tests prove:
  MUTATION  -- neutering the confirm-step would silently release an atom with no authenticated
               entry; the real control reports it UNRELEASED (the check FIRES).
  FAIL-CLOSED -- a directive with no authenticated entry, a bare doc author (spoofable), or a
               malformed/absent directive produces NO release and NO ledger write.
  FAIL-SILENT -- an unavailable ledger reader reports every directive UNRELEASED, never "done".
"""
import json
from pathlib import Path

import background.gate_authorization as g
from background.staging_disposition import unreleased_ledger_directive_in_staging


def _write_ledger(path: Path, entries: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")


def _console_build_open(atom: str) -> dict:
    return {"atom": atom, "action": "BUILD_OPEN", "ts": 1.0,
            "authorized_by": "director", "channel": "console", "provenance": "console act SHA=abc"}


# ── parse_ledger_directives ────────────────────────────────────────────────────────────────
def test_parse_extracts_canonical_directive():
    ds = g.parse_ledger_directives("preamble\nLEDGER: BUILD_OPEN generator_draw_wiring\ntail")
    assert ds == [{"action": "BUILD_OPEN", "target": "generator_draw_wiring"}]


def test_parse_level_up_captures_level():
    ds = g.parse_ledger_directives("LEDGER: LEVEL_UP_PROPOSED W1_5 3")
    assert ds == [{"action": "LEVEL_UP_PROPOSED", "target": "W1_5", "level": 3}]


def test_parse_fail_closed_skips_noncanonical_and_malformed():
    # non-canonical action, missing target, and a prose mention of a blocked_on: must all be skipped
    txt = ("LEDGER: FROBNICATE atom_x\n"
           "LEDGER: BUILD_OPEN\n"
           "the ruling references blocked_on: director_level_up in prose\n"
           "LEDGER:BUILD_OPEN no_space_after_colon\n")
    assert g.parse_ledger_directives(txt) == []


def test_parse_non_string_is_empty():
    assert g.parse_ledger_directives(None) == []


# ── confirm_authenticated_release ──────────────────────────────────────────────────────────
def test_confirm_build_open_true_only_with_authenticated_entry():
    led = [_console_build_open("generator_draw_wiring")]
    assert g.confirm_authenticated_release({"action": "BUILD_OPEN", "target": "generator_draw_wiring"}, led) is True
    assert g.confirm_authenticated_release({"action": "BUILD_OPEN", "target": "some_other_atom"}, led) is False


def test_confirm_rejects_worker_self_declared_console_entry():
    # a worker-forged BUILD_OPEN missing the director/console/provenance trust markers is NOT authority
    forged = {"atom": "x", "action": "BUILD_OPEN", "ts": 1.0, "authorized_by": "worker", "channel": "doorbell"}
    assert g.confirm_authenticated_release({"action": "BUILD_OPEN", "target": "x"}, [forged]) is False


def test_confirm_level_up_bounded_by_level():
    led = [{"atom": "W1_5", "action": "LEVEL_UP_PROPOSED", "ts": 1.0, "authorized_by": "director",
            "channel": "console", "provenance": "p", "level": 2}]
    assert g.confirm_authenticated_release({"action": "LEVEL_UP_PROPOSED", "target": "W1_5", "level": 2}, led) is True
    # a directive for L3 is NOT confirmed by an L2 entry (fail-closed)
    assert g.confirm_authenticated_release({"action": "LEVEL_UP_PROPOSED", "target": "W1_5", "level": 3}, led) is False


# ── report_ruling_release: the acceptance fixture (DISCOVER §6.4) ───────────────────────────
def test_report_released_when_authenticated_entry_exists(tmp_path):
    ledp = tmp_path / "gate.jsonl"
    _write_ledger(ledp, [_console_build_open("generator_draw_wiring")])
    rpt = g.report_ruling_release("LEDGER: BUILD_OPEN generator_draw_wiring", ledger_path=ledp)
    assert rpt["directives"] == 1
    assert rpt["released"] == [{"action": "BUILD_OPEN", "target": "generator_draw_wiring"}]
    assert rpt["unreleased"] == []
    assert rpt["ledger_available"] is True


def test_report_unreleased_and_never_writes_ledger(tmp_path):
    # FAIL-CLOSED: directive present, NO authenticated entry -> UNRELEASED, block stays, ledger UNTOUCHED
    ledp = tmp_path / "gate.jsonl"
    _write_ledger(ledp, [_console_build_open("some_other_atom")])
    before = ledp.read_bytes()
    rpt = g.report_ruling_release("LEDGER: BUILD_OPEN unauthorised_atom", ledger_path=ledp)
    assert rpt["unreleased"] == [{"action": "BUILD_OPEN", "target": "unauthorised_atom"}]
    assert rpt["released"] == []
    assert ledp.read_bytes() == before  # R16: read-only, never mints authority


def test_report_bare_doc_no_directive_is_no_release(tmp_path):
    ledp = tmp_path / "gate.jsonl"
    _write_ledger(ledp, [_console_build_open("generator_draw_wiring")])
    rpt = g.report_ruling_release("a staged ruling with no machine-parseable directive at all", ledger_path=ledp)
    assert rpt["directives"] == 0 and rpt["released"] == [] and rpt["unreleased"] == []


def test_mutation_neutered_confirm_would_release_unbacked_atom(tmp_path, monkeypatch):
    # The control's named defect: silently releasing an atom that has NO authenticated entry.
    # Real control -> UNRELEASED. Mutant (confirm always True) -> released. Proves the check fires.
    ledp = tmp_path / "gate.jsonl"
    _write_ledger(ledp, [])  # empty ledger: nothing is authenticated
    txt = "LEDGER: BUILD_OPEN unbacked_atom"
    real = g.report_ruling_release(txt, ledger_path=ledp)
    assert real["unreleased"] and not real["released"]

    monkeypatch.setattr(g, "confirm_authenticated_release", lambda d, led: True)
    mutant = g.report_ruling_release(txt, ledger_path=ledp)
    assert mutant["released"] and not mutant["unreleased"]  # mutant leaks -> the real check is load-bearing


def test_fail_silent_unavailable_reader_reports_unreleased():
    def _boom(_path):
        raise OSError("ledger unavailable")
    rpt = g.report_ruling_release("LEDGER: BUILD_OPEN generator_draw_wiring", reader=_boom)
    assert rpt["ledger_available"] is False
    assert rpt["unreleased"] == [{"action": "BUILD_OPEN", "target": "generator_draw_wiring"}]
    assert rpt["released"] == []  # unavailable check is a FAILED check, never a silent pass


# ── the staging surfacing detector ─────────────────────────────────────────────────────────
def test_detector_surfaces_unreleased_but_not_authenticated_or_directiveless(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    ledp = tmp_path / "gate.jsonl"
    _write_ledger(ledp, [_console_build_open("authed_atom")])

    (staging / "RULING_UNRELEASED.md").write_text("LEDGER: BUILD_OPEN not_authed_atom\n", encoding="utf-8")
    (staging / "RULING_AUTHED.md").write_text("LEDGER: BUILD_OPEN authed_atom\n", encoding="utf-8")
    (staging / "RULING_NO_DIRECTIVE.md").write_text("just a normal ruling, no directive\n", encoding="utf-8")

    out = unreleased_ledger_directive_in_staging([staging], ledger_path=ledp)
    assert out == ["RULING_UNRELEASED.md"]  # only the unauthenticated one surfaces (no false churn)


def test_detector_never_raises_on_missing_dir(tmp_path):
    assert unreleased_ledger_directive_in_staging([tmp_path / "nope"]) == []
