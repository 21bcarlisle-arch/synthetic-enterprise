"""THE DEFECT: `main()` is the path that publishes, and it did neither of the two things
`save_run_output_json()` does.

`background/sim_runner.py` runs `python3 -m tools.run_annual_report --save-json ... --output ...`.
That reaches `main()`. `save_run_output_json()` -- which carries the treasury-reconciliation
refusal and the `_cache_meta` stamp -- is reached only from `tools/run_phase4c_pipeline.py`, which
nothing on the publish path calls. Measured 2026-09-04: `_cache_meta` absent from all 131 September
run outputs; the refusal had never executed against a published artefact.

These tests fail if either half is removed from `main()`. They do NOT assert the presence of a
call by reading the source -- they run `main()` with the world stubbed out and read what lands on
disk, because a control that asserts a function is NAMED cannot tell whether it was OBEYED.

Each leg names the mutation that must kill it:
  * `test_a_run_output_that_does_not_add_up_is_never_written` -- delete the `reconcile_and_stamp`
    call from `main()`, or downgrade its `raise` to a warning.
  * `test_a_written_run_output_names_the_world_it_ran_in` -- delete the `world_level` key, or
    revert `main()` to `json.dumps(extract_report_data(raw_output))`.
  * `test_the_stamped_digest_tracks_the_anchor_block` -- pin the digest to a literal, or key it to
    anything that does not move when the departure level moves.
"""
from __future__ import annotations

import json

import pytest

import tools.run_annual_report as rar


def _adding_up() -> dict:
    """The smallest payload the treasury identity accepts. `years` is what the report renderer
    wants; nothing here is a figure any assertion below depends on."""
    return {
        "starting_treasury_gbp": 250_000.0,
        "total_net_gbp": 138_152.77,
        "final_treasury_gbp": 388_152.77,
        "years": [],
    }


@pytest.fixture()
def stubbed_world(monkeypatch):
    """Run `main()` without running a world. The simulation, the reduction and the renderer are
    replaced; everything between them -- which is the subject -- is the real code."""
    payload: dict = {}

    def _set(data: dict) -> None:
        payload.clear()
        payload.update(data)

    monkeypatch.setattr(rar, "run_phase4c_on_phase2b", lambda report_end=None: {"raw": True})
    monkeypatch.setattr(rar, "extract_report_data", lambda raw: dict(payload))
    monkeypatch.setattr(rar, "generate_annual_report", lambda data: "report")
    return _set


def _run_main(monkeypatch, tmp_path):
    out_json = tmp_path / "run_output.json"
    out_md = tmp_path / "report.md"
    monkeypatch.setattr(
        "sys.argv",
        ["run_annual_report", "--save-json", str(out_json), "--output", str(out_md)],
    )
    rar.main()
    return out_json


def test_a_run_output_that_does_not_add_up_is_never_written(stubbed_world, monkeypatch, tmp_path):
    """FAIL CLOSED, AND BEFORE THE WRITE. A run whose own treasury identity is broken must leave
    no artefact at all -- the publisher picks up whatever is on disk, so a written-then-refused
    file is the same as no refusal."""
    broken = _adding_up()
    broken["final_treasury_gbp"] = 999_999.0
    stubbed_world(broken)

    out_json = tmp_path / "run_output.json"
    out_md = tmp_path / "report.md"
    monkeypatch.setattr(
        "sys.argv",
        ["run_annual_report", "--save-json", str(out_json), "--output", str(out_md)],
    )
    with pytest.raises(ValueError, match="does not add up"):
        rar.main()

    assert not out_json.exists(), (
        "the run output was written before the identity was checked, so the publisher would "
        "have found and published a page that does not add up"
    )


def test_a_written_run_output_names_the_world_it_ran_in(stubbed_world, monkeypatch, tmp_path):
    """A commit hash moves for every reason and a timestamp cannot see a re-fit, so neither
    answers 'is this figure from the same world as the last one'. The digest does."""
    stubbed_world(_adding_up())
    written = json.loads(_run_main(monkeypatch, tmp_path).read_text())

    meta = written.get("_cache_meta")
    assert meta is not None, "the published run output carries no provenance stamp at all"
    assert meta.get("git_commit"), "no commit recorded, so `generate_dashboard_data` falls back"
    world = meta.get("world_level")
    assert world is not None, (
        "the run output does not say which departure world it executed in, so a reader "
        "comparing two publishes cannot tell a company result from a world change"
    )
    assert world.get("digest") or world.get("unavailable_because"), (
        "the world slot is present but says nothing -- an absent answer must name its reason"
    )


def test_the_stamped_digest_tracks_the_anchor_block(stubbed_world, monkeypatch, tmp_path):
    """KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Moving the departure level must move the
    stamp; if it does not, two runs either side of a re-fit stamp as the same world and the
    disclosure this exists for is silently false."""
    stubbed_world(_adding_up())
    before = json.loads(_run_main(monkeypatch, tmp_path).read_text())
    before_digest = before["_cache_meta"]["world_level"]["digest"]
    assert before_digest, "no digest to compare"

    from simulation import departure_level_anchor as dla

    moved = dict(dla.YEAR_LEVEL_ANCHOR)
    a_year = sorted(moved)[0]
    moved[a_year] = moved[a_year] + 1.0
    monkeypatch.setattr(dla, "YEAR_LEVEL_ANCHOR", moved)

    after = json.loads(_run_main(monkeypatch, tmp_path).read_text())
    assert after["_cache_meta"]["world_level"]["digest"] != before_digest, (
        "moving the {} anchor did not move the stamp, so a re-fit is invisible to every "
        "reader of a published run output".format(a_year)
    )
