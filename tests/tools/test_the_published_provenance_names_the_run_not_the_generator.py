"""THE DEFECT: `meta.git_commit` named the commit the GENERATOR ran at, not the one the RUN did.

`generate_dashboard_data.generate()` read `cache_meta.get("git_commit") or _git_head()`. The stamp
was absent from every published run output (see
`tools/run_annual_report.reconcile_and_stamp` and instance 10 of `no_caller_and_never_runs`), so
that expression always returned `_git_head()` -- HEAD at the moment the SITE was rebuilt. Those
differ by every commit landing between a run finishing and the site being regenerated, which on
2026-09-03 was twelve hours' worth.

Measured on the published artefact, 2026-09-04:

    meta.git_commit = cbbeb99d38839b9256a93bd0b06a9a0a46638856   <- no run has ever been produced
    meta.source_file = run_output_c9ac07327_20260904T035205Z.json   at that commit

The right answer was in the adjacent field. The comment guarding that line closed one fail-open --
"never a filename fragment dressed as a SHA" -- and the branch it installed opened a quieter one,
because a real SHA belonging to a different thing satisfies a presence check exactly as well as the
literal "latest" did.

The last test here is the one that binds the page rather than the function; the four above it are
what stop the function regressing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import tools.generate_dashboard_data as gdd

DASHBOARD = Path(__file__).resolve().parents[2] / "site" / "data" / "dashboard.json"
_SENTINEL_HEAD = "f" * 40


def test_a_stamped_run_is_believed_and_says_so():
    """MUTATION: drop the `_cache_meta` tier and this fires. The run's own stamp is the
    authoritative tier -- everything below it is an inference from a filename.

    THE FIXTURE WAS REWRITTEN (2026-09-04, second sitting). It used to prove precedence with a
    pair that DISAGREED -- stamp `abc1234` against filename `deadbee` -- and so it also asserted
    that a stamp beats a filename it contradicts. That turned out to be the wrong ruling: the
    stamp was read at the END of the run and the filename at the START, so a contradiction meant
    the stamp named a commit that landed mid-flight. See
    `test_a_contradiction_inside_one_artefact_is_settled_by_the_filename` below. This leg now
    proves precedence on the only shape a correct run can produce -- an agreeing pair -- so it
    tests tier order and nothing else.
    """
    commit, source = gdd._run_provenance_commit(
        {"git_commit": "deadbee42"}, Path("run_output_deadbee_20260904T000000Z.json")
    )
    assert commit == "deadbee42", "the run's own stamp was not believed"
    assert source == "run_stamp"


def test_a_contradiction_inside_one_artefact_is_settled_by_the_filename(monkeypatch):
    """MUTATION: restore the plain `if stamped: return stamped, "run_stamp"` precedence and this
    fires.

    THE DEFECT, measured on disk 2026-09-04: `run_output_fbd2970c6_20260904T060810Z.json` carries
    `_cache_meta.git_commit = "b83ec58ec"`. One artefact, two commits, because the producer read
    HEAD after a 13-minute run and the daemon had named the file before it. The code that
    computed the numbers is the code the process imported, so the filename is the better answer
    -- and the reader is told the answer was contested rather than being handed a quiet winner.
    """
    monkeypatch.setattr(gdd, "_git_head", lambda: _SENTINEL_HEAD)
    commit, source = gdd._run_provenance_commit(
        {"git_commit": "b83ec58ec"}, Path("run_output_fbd2970c6_20260904T060810Z.json")
    )
    assert commit == "fbd2970c6", (
        "the mid-flight commit was published as the provenance of a run whose code predates it"
    )
    assert source == "run_filename_over_contradicting_stamp", (
        "the page must say the two fields disagreed, not silently pick one"
    )


def test_shas_of_different_lengths_naming_one_commit_are_not_a_contradiction():
    """The two fields are `git rev-parse --short` output and nothing guarantees equal length, so
    the comparison is by prefix. MUTATION: compare with `!=` and this fires -- and it fires as a
    FALSE contradiction, which would demote a perfectly good `run_stamp` on every artefact whose
    two abbreviations differ in length."""
    commit, source = gdd._run_provenance_commit(
        {"git_commit": "08e7f7de57a3b82dd3fcbf814f7a0a08048b05b7"},
        Path("run_output_08e7f7de5_20260904T072726Z.json"),
    )
    assert source == "run_stamp"
    assert commit == "08e7f7de57a3b82dd3fcbf814f7a0a08048b05b7"


def test_an_unstamped_run_is_named_by_its_own_filename_not_by_head(monkeypatch):
    """MUTATION: reinstate `or _git_head()` and this fires.

    THE LOAD-BEARING LEG. The daemon builds `run_output_<sha>_<ts>.json` from
    `git rev-parse --short HEAD` at the moment the run STARTS, so the filename names the run's
    commit. The generator's HEAD names something else entirely and must never stand in for it."""
    monkeypatch.setattr(gdd, "_git_head", lambda: _SENTINEL_HEAD)
    commit, source = gdd._run_provenance_commit(
        {}, Path("run_output_c9ac07327_20260904T035205Z.json")
    )
    assert commit == "c9ac07327", "the run's own filename was not believed"
    assert source == "run_filename"
    assert _SENTINEL_HEAD not in commit, (
        "the generator's HEAD reached the published provenance slot -- that is the defect this "
        "file owns, and it looks exactly like a correct answer"
    )


#: REAL FILES IN `docs/reports/`, not invented ones. The first draft of this test used only
#: `run_output_latest.json` and the loosening mutation SURVIVED it -- `latest.json` carries no
#: second underscore, so `run_output_(.+?)_` fails to match it for a reason that has nothing to do
#: with the pattern being tight. Every other name below DOES match the loose pattern, and
#: `run_output_latest_phase6a_fwdA.json` matches it as the literal string "latest", which is the
#: 2026-07-29 fail-open reproduced exactly. A fixture whose subject satisfies the guard for the
#: wrong reason makes the guard an equivalence.
_NOT_A_COMMIT = [
    "run_output_latest.json",
    "run_output_latest_phase6a_fwdA.json",
    "run_output_naked_kwh_only.json",
    "run_output_old_reactive_model_pre5c.json",
    "run_output_segments_latest.json",
    "run_output_unknown_20260630T002847Z.json",
]


@pytest.mark.parametrize("name", _NOT_A_COMMIT)
def test_a_run_file_whose_name_is_not_a_commit_yields_unknown(monkeypatch, name):
    """MUTATION: loosen the filename pattern to `run_output_(.+?)_` and this fires.

    The 2026-07-29 fail-open by name: a run filename parsed to the literal string "latest", which
    satisfied every presence check forever and could never contradict a claim."""
    monkeypatch.setattr(gdd, "_git_head", lambda: _SENTINEL_HEAD)
    commit, source = gdd._run_provenance_commit({}, Path(name))
    assert source == "unavailable", (
        "{!r} was read as naming a commit; it does not".format(name)
    )
    assert commit == "unknown"


def test_head_is_never_the_answer_for_any_input(monkeypatch):
    """The property, over every shape the two inputs can take: whatever this function returns, it
    is not the generator's HEAD. A tier-by-tier test can be satisfied by a fourth tier nobody
    named; this cannot."""
    monkeypatch.setattr(gdd, "_git_head", lambda: _SENTINEL_HEAD)
    cases = [
        ({}, "run_output_latest.json"),
        ({}, "some_other_file.json"),
        (None, "run_output_latest.json"),
        ({"git_commit": ""}, "run_output_latest.json"),
        ({"git_commit": None}, "not_a_run_output.json"),
    ]
    for cache_meta, name in cases:
        commit, source = gdd._run_provenance_commit(cache_meta, Path(name))
        assert commit != _SENTINEL_HEAD, (
            "`{}` with cache_meta={!r} published the generator's HEAD as the run's "
            "provenance".format(name, cache_meta)
        )
        assert source in {
            "run_stamp",
            "run_filename",
            "run_filename_over_contradicting_stamp",
            "unavailable",
        }


def test_the_published_dashboard_provenance_agrees_with_the_run_it_names():
    """THE LEG THAT BINDS THE PAGE, not the function.

    `meta.source_file` and `meta.git_commit` are six lines apart in the same block and disagreed
    for months. This asserts the identity a reader would check: if the source file names a commit,
    the provenance field is that commit.

    It is deliberately NOT keyed to today's SHA -- pinning the literal would go red the moment the
    world moved on, which is backwards. It is keyed to the two fields agreeing.
    """
    if not DASHBOARD.is_file():
        pytest.fail(
            "site/data/dashboard.json is missing -- the published provenance cannot be checked, "
            "and an unavailable check is a FAILED check (R15)"
        )
    meta = json.loads(DASHBOARD.read_text()).get("meta") or {}
    match = re.match(r"^run_output_([0-9a-f]{7,40})_\d{8}T\d{6}Z\.json$", meta.get("source_file", ""))
    if not match:
        pytest.skip(
            "the published dashboard was built from {!r}, which encodes no commit, so there is "
            "nothing to agree with".format(meta.get("source_file"))
        )
    published = str(meta.get("git_commit") or "")
    run = match.group(1)
    assert published.startswith(run) or run.startswith(published), (
        "the page publishes `git_commit` {!r} while naming run file {!r}, which was produced at "
        "{!r}. The provenance names a different commit from the run it says it came "
        "from.".format(published, meta.get("source_file"), run)
    )
