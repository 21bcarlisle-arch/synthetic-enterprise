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

THE THIRD DEFECT, 2026-09-15: the header says WHICH CODE and WHICH WORLD and not WHICH MACHINE.
`SIM_FAST_MODE=1` swaps the local-LLM risk committee for a deterministic always-increase mock, so
two runs at one commit in one world can be drawn by different decision processes and stamp
identically. The five arms of the blind envelope rest entirely on "all five ran SIM_FAST_MODE=1,
identically", and grepping a filed run output for `fast_mode`, `SIM_FAST_MODE`, `mock` and
`risk_committee_mode` returns nothing -- the claim is unfalsifiable from the artefacts it is
about.

  * `test_a_written_run_output_names_which_committee_ran` -- ONE control over the whole partition,
    because a stamp that says "mock" unconditionally passes any single-mode leg. Kill it by
    pinning `execution_mode` to a constant, by deleting the block, or by keying it to `args.fast`
    (which is False for the `SIM_FAST_MODE=1 python3 -m tools.run_annual_report` launch shape the
    arm runs and `tools/tournament_runner` both use).
  * `test_the_stamp_and_the_committee_obey_one_predicate` -- re-inline the environment read inside
    `risk_committee_agent.invoke`, so the stamp and the branch become two facts that agree today.
  * `test_a_fast_mode_variable_set_to_something_other_than_one_is_not_fast_mode` -- write
    `bool(os.environ.get(...))` anywhere in the pair. `SIM_FAST_MODE=0` is a truthy string.
  * `test_the_declared_execution_mode_field_still_resolves_for_the_census` -- rename the field
    without moving the declaration, or declare the bool (which the census silently drops).
"""
from __future__ import annotations

import json
import re

import pytest

import sim.risk_committee_agent as rca
import tools.run_annual_report as rar
from tools.promoted_artefact_claim_census import _artefact_dates, _resolve_declared_field


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


def _written_with_fast_mode(value, stubbed_world, monkeypatch, tmp_path, name) -> dict:
    """The artefact `main()` writes with `SIM_FAST_MODE` set to `value` (None = unset).

    The variable is set in the ENVIRONMENT and no `--fast` flag is passed, because that is the
    launch shape the blind-envelope arm runs and `tools/tournament_runner` both use, and it is the
    shape a stamp keyed to `args.fast` gets wrong. `tests/conftest.py` sets the variable to "1"
    for the whole session, so every leg here must say what it wants rather than inherit it."""
    if value is None:
        monkeypatch.delenv(rca.FAST_MODE_ENV, raising=False)
    else:
        monkeypatch.setenv(rca.FAST_MODE_ENV, value)
    stubbed_world(_adding_up())
    return json.loads(_run_main(monkeypatch, tmp_path / name).read_text())


@pytest.fixture()
def _fast_mode_run(stubbed_world, monkeypatch, tmp_path):
    def _run(value, name):
        return _written_with_fast_mode(value, stubbed_world, monkeypatch, tmp_path, name)
    return _run


def test_a_written_run_output_names_which_committee_ran(_fast_mode_run):
    """WHICH MACHINE DREW THESE FIGURES, and it is not answered by the commit or the digest.

    `SIM_FAST_MODE=1` replaces the local-LLM risk committee with a deterministic always-increase
    mock, so every hedge decision in the run comes out of a different process. Two runs at one
    commit in one world, one fast and one not, stamped identically until this block existed.

    ONE CONTROL OVER THE WHOLE PARTITION, NOT A LEG PER MODE. A stamp hard-coded to "mock" passes
    every assertion a fast-mode-only leg can make, and the mock is what nearly every run on this
    box uses -- so the constant would have looked right for months. The property is that the two
    modes are DISTINGUISHABLE in the artefact; the per-mode readings below only say which way
    round."""
    fast = _fast_mode_run("1", "fast")
    live = _fast_mode_run(None, "live")

    for written, label in ((fast, "SIM_FAST_MODE=1"), (live, "SIM_FAST_MODE unset")):
        mode = written.get("execution_mode")
        assert mode is not None, (
            "the run output published by {} does not say which risk committee drew its hedge "
            "decisions, so no reader can tell it from a run of the other kind".format(label)
        )
        assert mode.get("risk_committee"), "the execution mode names no committee"

    assert fast["execution_mode"]["risk_committee"] != live["execution_mode"]["risk_committee"], (
        "both modes stamp {!r}, so the field is a constant and the arms of any blind envelope "
        "filed against it are as unfalsifiable as they were before it existed".format(
            fast["execution_mode"]["risk_committee"])
    )
    assert fast["execution_mode"]["fast"] is True, "a SIM_FAST_MODE=1 run did not stamp as fast"
    assert live["execution_mode"]["fast"] is False, (
        "a run with SIM_FAST_MODE unset stamped as fast, so the mock committee's fingerprint is "
        "on a run that called Ollama"
    )
    assert "execution_mode" in list(fast)[:5], (
        "the execution mode is not in the artefact's header, so a reader of a 27MB file has to "
        "go looking for it; the first five keys are {}".format(list(fast)[:5])
    )


def test_the_stamp_and_the_committee_obey_one_predicate(monkeypatch, tmp_path):
    """TWO COPIES OF A PREDICATE ARE TWO FACTS. The stamp is a claim about a branch it does not
    watch being taken, so the only thing that makes it true is that `invoke()` asks the same
    question this module's `fast_mode_enabled` answers.

    This does not read the source for a call. It moves the predicate and asserts the BRANCH moves:
    with the environment saying nothing, a patched-True predicate must reach the mock, and
    `_call_local` -- the Ollama path -- must not be reached at all. Re-inline the environment read
    inside `invoke` and this goes red."""
    monkeypatch.delenv(rca.FAST_MODE_ENV, raising=False)
    monkeypatch.setattr(rca, "_read_handshake_context", lambda: "context")
    monkeypatch.setattr(rca, "_log_decision", lambda *a, **k: None)

    def _refuse(*a, **k):
        raise AssertionError(
            "`invoke` called the LLM committee while `fast_mode_enabled()` said fast mode, so "
            "the published `execution_mode` stamp describes a branch the run did not take"
        )

    monkeypatch.setattr(rca, "_call_local", _refuse)
    monkeypatch.setattr(rca, "fast_mode_enabled", lambda: True)

    adjustments = rca.invoke("2021-06-01", 1, {"C1": 0.10})
    assert adjustments == {"C1": 0.20}, (
        "the mock committee's minimum +0.10 did not reach the caller: {!r}".format(adjustments)
    )


def test_a_fast_mode_variable_set_to_something_other_than_one_is_not_fast_mode(_fast_mode_run):
    """THE TRUTHINESS TRAP, and it is the obvious way to write this pair. `SIM_FAST_MODE=0` is a
    non-empty string: `bool(os.environ.get(...))` reads it as fast mode and
    `sim.risk_committee_agent.invoke` does not, so the artefact would say "deterministic mock" for
    a run that spent its whole length in Ollama. A plausible sentence about the wrong run is the
    defect this header exists to close, not one it may introduce."""
    written = _fast_mode_run("0", "zero")

    mode = written["execution_mode"]
    assert mode["fast"] is False, (
        "SIM_FAST_MODE=0 stamped as fast mode, but `risk_committee_agent.invoke` compares the "
        "variable to the exact string '1' and would have called the LLM"
    )
    assert mode["sim_fast_mode"] == "0", (
        "the raw value is not published, so a reader cannot check the producer's reading of it"
    )


def test_the_declared_execution_mode_field_still_resolves_for_the_census(_fast_mode_run):
    """THE DECLARATION MUST REACH A LEAF, and a declaration that does not is silent.

    `promoted_artefact_claim_census._resolve_declared_field` returns None for a missing path, for
    a container AND for a bool -- so declaring `execution_mode.fast` would name a field that
    contributes nothing to grading and reports nothing about contributing nothing. This calls the
    real resolver rather than re-implementing the rule, which is the only version of this
    assertion that a rename on either side can fail."""
    written = _fast_mode_run("1", "declared")

    declared = written["run_identity_fields"]
    assert "execution_mode.risk_committee" in declared, (
        "the execution mode is published but not declared as run identity, so the census that "
        "grades every claim about this promote target cannot read it; declared: {}".format(
            declared)
    )
    for dotted in declared:
        assert _resolve_declared_field(written, dotted) is not None, (
            "the artefact declares {!r} as its run identity and the census resolver reaches no "
            "leaf there, so that field grades nothing and says nothing about it".format(dotted)
        )
