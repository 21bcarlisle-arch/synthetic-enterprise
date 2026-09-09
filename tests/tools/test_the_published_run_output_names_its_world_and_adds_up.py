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

THE SECOND DEFECT, 2026-09-09: `_cache_meta` answers a consumer that knows to look for it, and
answers NOTHING ELSE. `docs/reports/run_output_latest.json` is a promote-by-copy target -- bytes
copied onto a canonical name, no source file touched -- and it published no run identity a reader
or a control could find. Graded by `tools/promoted_artefact_claim_census._artefact_dates`, the
artefact on disk yielded 17 run-identity tokens and not one was the run's: twelve simulation-world
dates and five belonging to `scenario_analysis`, which is loaded off disk from a different
producer. The census leg that exists to say "this target cannot be graded" therefore reported
nothing, and a claim about which run sat there could be checked against a stress test's mark date.

The legs below are about the header that repairs it, and each names its mutation:
  * `test_a_written_run_output_carries_the_run_identity_header` -- delete the
    `_run_identity_header` call, or drop any of its three fields.
  * `test_the_published_run_identity_is_readable_by_the_census_that_grades_it` -- write
    `generated_at` in `_cache_meta`'s compact `%Y%m%dT%H%M%SZ` shape. That is the shape already in
    the file and the obvious thing to copy, and the census cannot match it at all.
  * `test_a_run_that_cannot_name_its_code_publishes_no_sha_at_all` -- pass `_git_commit_hash`'s
    `"unknown"` sentinel through into `producing_commit.commit`, where it is truthy and satisfies
    every presence check.
  * `test_the_header_and_the_cache_meta_cannot_disagree` -- resolve the commit, the clock or the
    world separately for the two slots instead of binding both to one local.
"""
from __future__ import annotations

import json
import re

import pytest

import tools.run_annual_report as rar
from tools.promoted_artefact_claim_census import _artefact_dates


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


def test_a_written_run_output_carries_the_run_identity_header(
    stubbed_world, monkeypatch, tmp_path
):
    """WHICH RUN IS THIS, answered in the payload and at the top of it.

    `run_output_latest.json` is a promote-by-copy target with eighteen binders. Before this header
    the answer was establishable only from `git log` -- i.e. not from the artefact at all, which
    is the one place a copied set of bytes carries its own truth."""
    stubbed_world(_adding_up())
    written = json.loads(_run_main(monkeypatch, tmp_path).read_text())

    assert list(written)[:3] == ["generated_at", "producing_commit", "world_identity"], (
        "the run identity is not the first thing in the artefact, so a reader of a 27MB file has "
        "to parse the whole of it to find out which run they are holding; got {}".format(
            list(written)[:3])
    )
    assert re.fullmatch(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", written["generated_at"]), (
        "`generated_at` is not the shape the other promote targets publish: "
        + repr(written["generated_at"])
    )

    commit = written["producing_commit"]
    assert commit.get("commit") or commit.get("unavailable_because"), (
        "the `producing_commit` slot is present and says nothing -- an absent answer must name "
        "its reason, because a consumer that cannot tell 'no commit' from 'some commit' is the "
        "fail-open this block exists to close"
    )
    world = written["world_identity"]
    assert world.get("digest") or world.get("unavailable_because"), (
        "the artefact does not say which world it ran in and does not say why not"
    )


def test_the_published_run_identity_is_readable_by_the_census_that_grades_it(
    stubbed_world, monkeypatch, tmp_path
):
    """THE LEG THAT MAKES THE HEADER REACH ITS CONSUMER, and it is not the same assertion as the
    one above.

    A header can be present, correct, and invisible. `_cache_meta` was all three: its stamp is
    `20260901T054223Z`, and `_RUN_IDENTITY` matches a compact date only at a word boundary -- the
    `T` that follows is a word character, so the pattern cannot fire inside it. Its world digest
    sits one level deeper than the census walks. The result was a target that published provenance
    and graded as though it published none.

    So this asserts the property that matters rather than the field that carries it: the run's own
    stamp is in the set the census grades claims against. Nothing here re-implements the census --
    it calls the real one, on the real bytes `main()` wrote."""
    stubbed_world(_adding_up())
    out = _run_main(monkeypatch, tmp_path)
    written = json.loads(out.read_text())

    tokens = _artefact_dates(out)
    assert written["generated_at"] in tokens, (
        "the run stamped itself {} and the census that grades every claim about which run sits "
        "at this promote target cannot see it; the tokens it did find were {}".format(
            written["generated_at"], sorted(tokens))
    )


def test_a_run_that_cannot_name_its_code_publishes_no_sha_at_all(
    stubbed_world, monkeypatch, tmp_path
):
    """A PLACEHOLDER THAT SATISFIES A PRESENCE CHECK IS WORSE THAN AN ADMITTED ABSENCE.

    `_git_commit_hash()` returns the literal `"unknown"` when `git rev-parse` does not answer, and
    `"unknown"` is truthy. `_cache_meta` publishes it as-is deliberately -- the dashboard wants the
    honest word -- but every `producing_commit` consumer in this tree keys on `commit` being None,
    so passing the sentinel through would let a run that cannot name its code read exactly like
    one that can."""
    stubbed_world(_adding_up())
    monkeypatch.setattr(rar, "_git_commit_hash", lambda: "unknown")
    written = json.loads(_run_main(monkeypatch, tmp_path).read_text())

    commit = written["producing_commit"]
    assert commit["commit"] is None, (
        "a run that could not read HEAD published {!r} as its producing commit".format(
            commit["commit"])
    )
    assert commit["unavailable_because"], "the absence is unexplained"


def test_the_header_and_the_cache_meta_cannot_disagree(stubbed_world, monkeypatch, tmp_path):
    """TWO SLOTS, ONE FACT. The same run's identity is published in `_cache_meta` (for the three
    consumers that already read it and for the versioned filename) and in the header (for readers
    and for the census). Computed separately they would be two facts that agree today; bound to
    one local they are one fact with two readers.

    The clock is the leg that would rot first and silently: `datetime.now()` called twice can
    straddle a second boundary, and a header stamped one second after the filename is a header a
    reader cannot join back to its own versioned copy."""
    stubbed_world(_adding_up())
    written = json.loads(_run_main(monkeypatch, tmp_path).read_text())

    meta = written["_cache_meta"]
    assert written["world_identity"] == meta["world_level"], (
        "the artefact names two different worlds in its two provenance slots"
    )
    # Keyed to the property and not to today's answer: the two slots must name the SAME commit, or
    # the header must be fail-closed about the one `_cache_meta` published. The second arm is the
    # `"unknown"` case above and is the only legitimate way for these to differ.
    header_commit = written["producing_commit"]["commit"]
    assert header_commit == meta["git_commit"] or (
        header_commit is None and written["producing_commit"]["unavailable_because"]
    ), "the header and `_cache_meta` name different producing commits, and neither says why"
    header_clock = written["generated_at"].replace("-", "").replace(":", "")
    assert header_clock == meta["generated_at_utc"], (
        "the header says {} and the versioned filename will be minted from {}, so the published "
        "artefact cannot be joined to its own dated sibling".format(
            written["generated_at"], meta["generated_at_utc"])
    )
