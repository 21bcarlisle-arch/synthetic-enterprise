"""The merge census attributes each merge to the commits that forced it, and tells a clean merge
from a conflicted one. Defect it names: nothing measured which files drive merges or what they cost,
so fixes went to symptoms (director, 2026-10-04)."""

import json
import subprocess

import pytest

from tools import merge_pressure_census as census


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def _commit(repo, path, text, subject):
    f = repo / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)
    _git(repo, "add", path)
    _git(repo, "commit", "-q", "-m", subject)
    return _git(repo, "rev-parse", "HEAD").strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    r = tmp_path / "r"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    _commit(r, "a.py", "a\n", "base")
    _commit(r, "shared.txt", "x\n", "shared base")
    monkeypatch.setattr(census, "ROOT", r)
    return r


def _lane_merge(repo, lane_path, origin_commits, lane_text="lane\n"):
    """A lane cuts a branch, origin moves by `origin_commits`, the lane merges origin in."""
    _git(repo, "checkout", "-q", "-b", "lane")
    _commit(repo, lane_path, lane_text, "lane work")
    _git(repo, "checkout", "-q", "main")
    for path, text, subject in origin_commits:
        _commit(repo, path, text, subject)
    _git(repo, "checkout", "-q", "lane")
    subprocess.run(["git", "merge", "-q", "--no-edit", "main"], cwd=repo, capture_output=True)
    if subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], cwd=repo,
                      capture_output=True, text=True).stdout.strip():
        (repo / lane_path).write_text("resolved\n")
        _git(repo, "add", lane_path)
        _git(repo, "commit", "-q", "-m", "merge\n\n[surgical-land receipt]\n"
             "tests: no tests selected\nconflicts-resolved: " + lane_path)
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--ff-only", "lane")
    _git(repo, "branch", "-q", "-D", "lane")


def test_every_forcing_kind_is_reachable_and_a_conflict_is_told_from_a_clean_merge(repo):
    """The partition control first (a census that files everything as `work` passes any test of
    one kind): one merge each forced by heartbeat, seat records and work, and one that conflicts.

    MUTATION (must fire): make `kind_of` return "work" unconditionally."""
    _lane_merge(repo, "l1.py", [("site/data/tick_heartbeat.json", "1", "chore(liveness): beat")])
    _lane_merge(repo, "l2.py", [("docs/direction/DIRECTION.yaml", "o", "seat oriented")])
    _lane_merge(repo, "l3.py", [("b.py", "b\n", "other lane work")])
    _lane_merge(repo, "shared.txt", [("shared.txt", "theirs\n", "edit shared")], lane_text="ours\n")

    all_rows = census.merges("30.years", ref="main")
    s = census.summarise(all_rows)

    assert s["forced_by"] == {"heartbeat": 1, "seat_record": 1, "work": 2}
    assert s["textual_conflicts"] == 1 and s["resolved_by_someone"] == 1
    conflicted = [r for r in census.merges("30.years", ref="main") if r["textual_conflict"]]
    assert [r["conflicted_paths"] for r in conflicted] == [["shared.txt"]]
    assert conflicted[0]["resolved"] == ["shared.txt"]
    clean = [r for r in census.merges("30.years", ref="main") if not r["textual_conflict"]]
    assert len(clean) == 3 and all(not r["resolved"] for r in clean)


def test_a_merge_with_two_kinds_arriving_is_mixed_not_credited_to_either(repo):
    """Removing one kind would not have spared a merge another kind also forced."""
    _lane_merge(repo, "l1.py", [("site/data/tick_heartbeat.json", "1", "chore(liveness): beat"),
                                ("b.py", "b\n", "other lane work")])
    [row] = census.merges("30.years", ref="main")
    assert row["forced_by"] == "mixed"
    assert row["kinds"] == {"heartbeat": 1, "work": 1}


def test_token_cost_counts_each_api_call_once_however_many_blocks_it_wrote(tmp_path):
    """A transcript writes one line per content block, each repeating the call's usage; summing
    lines would count a two-block merge call twice. MUTATION (must fire): key by line, not id."""
    usage = {"input_tokens": 10, "cache_creation_input_tokens": 0, "output_tokens": 5,
             "cache_read_input_tokens": 100}
    rows = [
        {"type": "assistant", "timestamp": "2099-01-01T00:00:00Z",
         "message": {"id": "m1", "usage": usage, "content": [{"type": "text", "text": "x"}]}},
        {"type": "assistant", "timestamp": "2099-01-01T00:00:00Z",
         "message": {"id": "m1", "usage": usage, "content": [
             {"type": "tool_use", "input": {"command": "python3 -m tools.surgical_land --merge origin/main"}}]}},
        {"type": "assistant", "timestamp": "2099-01-01T00:00:00Z",
         "message": {"id": "m2", "usage": usage, "content": [
             {"type": "tool_use", "input": {"command": "ls"}}]}},
    ]
    (tmp_path / "s.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    out = census.token_cost(0, dirs=(tmp_path,))
    assert out == {"calls": 2, "merge_calls": 1, "billed": 30, "merge_billed": 15,
                   "cache_read": 200, "merge_cache_read": 100}


def test_the_monday_step_carries_the_weeks_merge_pressure(repo, monkeypatch):
    """The census has a caller that runs every week, and a census that cannot run says so on the
    page rather than vanishing."""
    from background import weekly_rhythm

    _lane_merge(repo, "l1.py", [("b.py", "b\n", "other lane work")])
    _git(repo, "update-ref", "refs/remotes/origin/main", "main")
    section = "\n".join(weekly_rhythm._merge_pressure_section(days=10000))
    assert "## Merge pressure, this week" in section and "**1 merges**, forced by: work 1" in section

    monkeypatch.setattr(census, "merges", lambda since, ref="origin/main": 1 / 0)
    assert "NOT MEASURED" in "\n".join(weekly_rhythm._merge_pressure_section())


def test_the_monday_document_itself_carries_the_section(monkeypatch):
    """The section function existing is not the Monday step calling it. MUTATION (must fire):
    drop `_merge_pressure_section` from the Monday body."""
    from datetime import date

    from background import weekly_rhythm

    monkeypatch.setattr(census, "render", lambda days=7.0: "MEASURED-HERE")
    body = weekly_rhythm._step_body(weekly_rhythm.MONDAY_STEP, date(2026, 10, 5), [])
    assert "## Merge pressure, this week" in body and "MEASURED-HERE" in body
