"""The carbon page can be rebuilt from the repository: its inputs are committed, or ride with it.

e816040ce8 published `site/data/explore_carbon.json` reading 3 measured households. Rebuilt in a
clean worktree at origin it read 0, because the publisher regenerated
`docs/market_data/grid_intensity_feed.json` every cycle and its commit list never staged
`docs/market_data/`. Two legs, one per way the defect can come back:

  * the page refuses to build from a tracked input that differs from HEAD, and names it, unless
    the caller says the inputs ride in the same commit;
  * the caller that says so -- the publisher -- really does commit every input's directory.

MUTATIONS (each reds this file): drop the refusal in `generate`; drop `HEAD` from the diff in
`uncommitted_inputs` (the staged edit is missed); drop "docs/market_data" from
`process_run_complete.TRACKED_PUBLISH_DIRS`.
"""
from __future__ import annotations

import subprocess as sp
from pathlib import Path

import pytest

from background import process_run_complete as prc
from tools import generate_explore_carbon as gec

PROJECT = Path(__file__).resolve().parents[2]


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    for rel in ("docs/market_data/feed.json", "docs/market_data/staged.json",
                "docs/market_data/clean.json", "site/state/s.json"):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text("a\n", encoding="utf-8")
    sp.run(["git", "init", "-q"], cwd=repo, check=True)
    sp.run(["git", "add", "-A"], cwd=repo, check=True)
    sp.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"],
           cwd=repo, check=True)
    return repo


def test_an_edited_or_staged_input_is_named_and_a_clean_or_untracked_one_is_not(tmp_path):
    repo = _repo(tmp_path)
    paths = [repo / "docs/market_data" / n for n in ("feed.json", "staged.json", "clean.json")]
    assert gec.uncommitted_inputs(paths, repo) == []
    (repo / "docs/market_data/feed.json").write_text("b\n", encoding="utf-8")
    (repo / "docs/market_data/staged.json").write_text("b\n", encoding="utf-8")
    sp.run(["git", "add", "docs/market_data/staged.json"], cwd=repo, check=True)
    (repo / "docs/market_data/untracked.json").write_text("b\n", encoding="utf-8")
    got = gec.uncommitted_inputs([*paths, repo / "docs/market_data/untracked.json"], repo)
    assert got == ["docs/market_data/feed.json", "docs/market_data/staged.json"], got


def test_git_that_cannot_answer_is_not_read_as_clean(tmp_path):
    (tmp_path / "f.json").write_text("a\n", encoding="utf-8")
    with pytest.raises(gec.UncommittedInput, match="cannot tell"):
        gec.uncommitted_inputs([tmp_path / "f.json"], tmp_path)


def test_the_page_refuses_a_dirty_input_by_name_and_builds_when_it_rides_with_the_page(
        monkeypatch, tmp_path):
    reached = []

    def stop(_path):
        reached.append(True)
        raise LookupError("past the guard")

    monkeypatch.setattr(gec, "load_shape", stop)
    monkeypatch.setattr(gec, "uncommitted_inputs",
                        lambda: ["docs/market_data/grid_intensity_feed.json"])
    with pytest.raises(gec.UncommittedInput, match="grid_intensity_feed.json"):
        gec.generate(out_path=tmp_path / "out.json")
    assert not reached
    # Both sides of the partition are reachable: the declared path and the clean path build.
    with pytest.raises(LookupError):
        gec.generate(out_path=tmp_path / "out.json", inputs_ride_with_the_page=True)
    monkeypatch.setattr(gec, "uncommitted_inputs", lambda: [])
    with pytest.raises(LookupError):
        gec.generate(out_path=tmp_path / "out.json")
    assert len(reached) == 2


def test_the_publisher_commits_every_tracked_file_under_its_census_dirs(tmp_path):
    repo = _repo(tmp_path)
    (repo / "docs/market_data/untracked.json").write_text("b\n", encoding="utf-8")
    got = {str(Path(p).relative_to(repo)) for p in prc.tracked_publish_files(repo)}
    assert got == {"docs/market_data/feed.json", "docs/market_data/staged.json",
                   "docs/market_data/clean.json", "site/state/s.json"}, got


def test_every_input_of_the_carbon_page_is_in_a_directory_the_publish_commits():
    """The publisher's `inputs_ride_with_the_page=True` is only true if this holds. `site/data`
    is staged by the publisher's own glob; everything else must be under a census directory."""
    committed = ("site/data", *prc.TRACKED_PUBLISH_DIRS)
    for path in gec.INPUTS:
        rel = Path(path).resolve().relative_to(PROJECT).as_posix()
        assert any(rel == d or rel.startswith(d + "/") for d in committed), (
            "{} feeds the carbon page but no publish commit stages it, so the page would again "
            "rest on an uncommitted input".format(rel))


def test_the_publisher_declares_the_inputs_ride_with_the_page():
    source = Path(prc.__file__).read_text(encoding="utf-8")
    assert "gen_carbon(inputs_ride_with_the_page=True)" in source
