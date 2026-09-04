"""THE DEFECT: the run's commit stamp was read AFTER the run, so it named a different commit.

`background/sim_runner.run_simulation()` mints the versioned artefact name
`run_output_<sha>_<ts>.json` from `git rev-parse --short HEAD` at the moment the run STARTS.
`tools.run_annual_report.reconcile_and_stamp()` wrote `_cache_meta.git_commit` from the same
command evaluated at the END. A full run takes ~13 minutes and several lanes land commits into
this tree every hour, so the two fields inside one artefact disagreed on every run that spanned
a commit. Measured on disk, 2026-09-04:

    run_output_fbd2970c6_20260904T060810Z.json   _cache_meta.git_commit = b83ec58ec
    run_output_b83ec58ec_20260904T062230Z.json   _cache_meta.git_commit = e94442a37

`tools/generate_dashboard_data` believes the stamp over the filename, so the published
`meta.git_commit` named a commit whose code had not been loaded when the numbers were computed.
It is the 2026-09-04 provenance defect one layer down: a real SHA belonging to a different
instant satisfies a presence check exactly as well as the literal "latest" did, and this one is
harder to see because both fields are real SHAs of the same repo.

THE PROPERTY: the stamp is HEAD at the instant the process imported its code, because that is
what produced the numbers. Both legs below are keyed to that and not to any particular SHA.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.run_annual_report as rar

_AT_LAUNCH = "aaaaaaaaa"
_AT_STAMP_TIME = "bbbbbbbbb"


def _reconcilable(monkeypatch):
    """Neutralise the two collaborators that are not this file's subject."""
    monkeypatch.setattr(rar, "reconcile_published_run_output", lambda data: [])
    monkeypatch.setattr(rar, "world_level_identity", lambda: {"digest": "0" * 16})


def test_the_stamp_is_the_commit_handed_in_not_head_at_stamp_time(monkeypatch):
    """MUTATION: drop `code_commit` from the stamping expression -- or accept the parameter and
    ignore it, which is the shape a signature-keyed guard misses -- and this fires."""
    _reconcilable(monkeypatch)
    monkeypatch.setattr(rar, "_git_commit_hash", lambda: _AT_STAMP_TIME)

    data = rar.reconcile_and_stamp({"years": []}, code_commit=_AT_LAUNCH)

    assert data["_cache_meta"]["git_commit"] == _AT_LAUNCH, (
        "the stamp named HEAD at the moment of stamping, not the commit whose code ran"
    )


def test_with_no_commit_handed_in_the_old_end_of_run_reading_still_answers(monkeypatch):
    """The fallback is deliberate and is NOT the defect: `save_run_output_json()` stamps and then
    builds its own filename FROM the stamp, so those two agree by construction whatever the
    reading is. Pinned so the fallback is never mistaken for an oversight and deleted -- and so
    the parameter cannot be made mandatory without someone reading this."""
    _reconcilable(monkeypatch)
    monkeypatch.setattr(rar, "_git_commit_hash", lambda: _AT_STAMP_TIME)

    data = rar.reconcile_and_stamp({"years": []})

    assert data["_cache_meta"]["git_commit"] == _AT_STAMP_TIME


def test_the_publishing_path_reads_head_before_the_run_not_after(monkeypatch, tmp_path):
    """THE LOAD-BEARING LEG: it binds `main()`, which is the path that actually publishes.

    HEAD is made to MOVE during the run, exactly as it does in this tree. A test that only
    checked `reconcile_and_stamp` in isolation would stay green with the capture left in its old
    place, because the parameter would simply be fed the wrong reading.

    MUTATION: move `code_commit = _git_commit_hash()` back below `run_phase4c_on_phase2b(...)`
    and this fires.

    THE MUTATION IS INJECTED BY THE STUBBED RUN ITSELF, and the first draft of this test proved
    why that is not optional. It handed `_git_commit_hash` an ITERATOR of readings and asserted
    the first was used -- which counts CALLS, not position, so moving the capture below the run
    returned the same first reading and the mutation SURVIVED. A control over an ordering has to
    make the two orders produce different answers; here that means the run must MOVE HEAD, which
    is exactly what it does in the real tree.
    """
    _reconcilable(monkeypatch)

    head = [_AT_LAUNCH]
    monkeypatch.setattr(rar, "_git_commit_hash", lambda: head[0])

    def _run_and_land_a_commit(report_end=None):
        head[0] = _AT_STAMP_TIME  # another lane lands while the 13-minute run is in flight
        return {"raw": True}

    monkeypatch.setattr(rar, "run_phase4c_on_phase2b", _run_and_land_a_commit)
    monkeypatch.setattr(rar, "extract_report_data", lambda raw: {"years": [{"year": 2025}]})
    monkeypatch.setattr(rar, "generate_annual_report", lambda data: "# report")

    save_json = tmp_path / "run_output.json"
    monkeypatch.setattr(
        "sys.argv",
        ["run_annual_report", "--save-json", str(save_json), "--output", str(tmp_path / "r.md")],
    )

    rar.main()

    stamped = json.loads(save_json.read_text())["_cache_meta"]["git_commit"]
    assert stamped == _AT_LAUNCH, (
        "HEAD was read after the simulation, so the published stamp names a commit that landed "
        "while the run was in flight rather than the one whose code produced its numbers"
    )


def test_no_artefact_on_disk_disagrees_with_its_own_filename(monkeypatch):
    """THE LEG THAT BINDS THE ARTEFACTS, not the function -- and it is the one that fires TODAY.

    A versioned run output names a commit twice: in its filename and in `_cache_meta`. They are
    the same quantity measured at two instants, so they must agree. Scoped to artefacts written
    from 2026-09-04T08:00Z onward (the fix's own landing), because every earlier one carries the
    defect and re-writing published artefacts to make a control green is the wrong direction:
    the historical ones are the evidence.
    """
    reports = Path(__file__).resolve().parents[2] / "docs" / "reports"
    if not reports.is_dir():
        pytest.fail("docs/reports/ is missing -- an unavailable check is a FAILED check (R15)")

    import re

    pattern = re.compile(r"^run_output_([0-9a-f]{7,40})_(\d{8}T\d{6})Z\.json$")
    disagreements = []
    checked = 0
    for path in sorted(reports.glob("run_output_*.json")):
        match = pattern.match(path.name)
        if not match or match.group(2) < "20260904T080000":
            continue
        try:
            stamped = (json.loads(path.read_text()).get("_cache_meta") or {}).get("git_commit")
        except (OSError, ValueError):
            continue
        if not stamped:
            continue
        checked += 1
        named = match.group(1)
        if not (str(stamped).startswith(named) or named.startswith(str(stamped))):
            disagreements.append(f"{path.name} is stamped {stamped!r}")

    assert not disagreements, (
        "a run artefact names one commit in its filename and another in its own stamp:\n  - "
        + "\n  - ".join(disagreements)
    )
    # An empty subject is reported, never silently passed: this leg says nothing until a run
    # lands under the fixed code, and a reader is owed that rather than a green.
    if checked == 0:
        pytest.skip("no run artefact written since the fix landed -- this leg has no subject yet")
