"""R15 proof for background/staging_root_resurrection_watch.py.

An instrument gets exactly two ways to be worthless, and both are tested here in both
directions:

  1. IT NEVER FIRES -- the reappearance happens and no record is written. Every `fires_*` test
     below stages a real reappearance on real disk and asserts the record names it.
  2. IT ALWAYS FIRES -- a record on every landing is noise, and noise is how a real event gets
     read past. The NULL CONTROL (`test_silent_when_nothing_reappeared`) moves the sample, not
     the law: same bracket, same disk, no reappearance, and it must write nothing.

The third failure mode is the one that would make this worse than no instrument at all: an
observer that breaks the observed. `test_bracket_never_breaks_the_landing_*` mutate each half to
raise and assert the landing is untouched.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from background import staging_root_resurrection_watch as watch

MARKER = "run_complete_20260820T072000Z.md"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo, because `blob_known_to_git` is the record's discriminating field and it
    is answered by the object store, not by a mock."""
    root = tmp_path / "repo"
    (root / "docs" / "staging" / "done").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    (root / "seed.txt").write_text("seed\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    return root


def _staging(repo: Path) -> Path:
    return repo / "docs" / "staging"


def _events(log: Path) -> list[dict]:
    if not log.is_file():
        return []
    return [json.loads(ln) for ln in log.read_text().splitlines() if ln.strip()]


# --------------------------------------------------------------------------------------------
# 1. It fires.
# --------------------------------------------------------------------------------------------

def test_fires_when_a_marker_appears_during_the_bracket(repo, tmp_path):
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    with watch.bracket(repo, "test-landing", staging_dir=sdir, out=log):
        (sdir / MARKER).write_text("body\n")

    events = _events(log)
    assert len(events) == 1, "the reappearance was not recorded"
    ev = events[0]
    assert ev["count"] == 1
    assert ev["label"] == "test-landing"
    assert [f["name"] for f in ev["files"]] == [MARKER]
    assert ev["files"][0]["mtime_iso"] is not None, "no wall-clock: the finding's one clue"


def test_fires_when_the_bytes_are_rewritten_under_an_existing_name(repo, tmp_path):
    """A file that was never deleted but was overwritten with the pre-archive bytes presents
    identically at the gate. Scoping to new names only would answer a narrower question."""
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    (sdir / MARKER).write_text("original\n")
    with watch.bracket(repo, "test-landing", staging_dir=sdir, out=log):
        (sdir / MARKER).write_text("restored to the pre-archive bytes\n")
    assert len(_events(log)) == 1


def test_fires_even_when_the_bracketed_body_raises(repo, tmp_path):
    """A REFUSED landing is exactly as interesting as a successful one -- the earlier evidence
    says refused attempts are where some of this happens. The record must survive the raise."""
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    with pytest.raises(RuntimeError):
        with watch.bracket(repo, "red-gate", staging_dir=sdir, out=log):
            (sdir / MARKER).write_text("body\n")
            raise RuntimeError("GATE RED")
    assert len(_events(log)) == 1


def test_the_record_separates_a_restore_from_a_producer(repo, tmp_path):
    """`all_bytes_known_to_git` is the field that would have settled the two wrong answers.

    Bytes that are ALREADY a git object were committed here before -- a checkout/reset/merge
    restore. Bytes that are not were composed by something. Both directions asserted, because a
    flag that is always True separates nothing.
    """
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    known_bytes = b"these bytes are already an object\n"
    subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=repo,
                   input=known_bytes, check=True, capture_output=True)

    with watch.bracket(repo, "restore-shape", staging_dir=sdir, out=log):
        (sdir / MARKER).write_bytes(known_bytes)
    with watch.bracket(repo, "producer-shape", staging_dir=sdir, out=log):
        (sdir / "run_complete_20260820T093000Z.md").write_bytes(b"freshly composed\n")

    by_label = {e["label"]: e for e in _events(log)}
    assert by_label["restore-shape"]["all_bytes_known_to_git"] is True
    assert by_label["producer-shape"]["all_bytes_known_to_git"] is False


def test_the_record_states_the_twin_that_actually_refuses_the_commit(repo, tmp_path):
    """The gate refusal is on the TWO ROOMS state, and the finding's own census says every twin
    was a strict superset (the done/ copy is the root copy plus the retirement footer). The
    record states that rather than leaving the reader to re-run the detector against a tree that
    has since moved."""
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    (sdir / "done" / MARKER).write_text("body\n\n## Superseded (not published)\n\nfooter\n")
    with watch.bracket(repo, "twin", staging_dir=sdir, out=log):
        (sdir / MARKER).write_text("body\n")
    f = _events(log)[0]["files"][0]
    assert f["twin_in_done"] is True
    assert f["twin_is_strict_superset"] is True


def test_a_simultaneous_batch_is_flagged_as_one_event(repo, tmp_path):
    """Ten files with one mtime is a restore; a spread is a drip. That distinction is the whole
    reason the batch-level fields exist."""
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    names = ["run_complete_2026082{}T070000Z.md".format(i) for i in range(3)]
    with watch.bracket(repo, "batch", staging_dir=sdir, out=log):
        for n in names:
            (sdir / n).write_text("body\n")
        for n in names:                       # one simultaneous event, as a restore would be
            import os
            os.utime(sdir / n, ns=(1_700_000_000_000_000_000, 1_700_000_000_000_000_000))
    ev = _events(log)[0]
    assert ev["count"] == 3
    assert ev["distinct_mtimes"] == 1
    assert ev["single_mtime"] is True


def test_watch_records_a_reappearance_while_polling(repo, tmp_path):
    """The live-case instrument. Driven with an injected sleep so the test is deterministic and
    does not spend a second of gate time per poll."""
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    state = {"n": 0}

    def fake_sleep(_):
        state["n"] += 1
        if state["n"] == 2:
            (sdir / MARKER).write_text("body\n")
        if state["n"] >= 4:
            raise TimeoutError            # end the loop deterministically

    with pytest.raises(TimeoutError):
        watch.watch(duration=10_000, root=repo, staging_dir=sdir, out=log, _sleep=fake_sleep)
    events = _events(log)
    assert len(events) == 1
    assert events[0]["label"] == "watch"
    assert [f["name"] for f in events[0]["files"]] == [MARKER]


# --------------------------------------------------------------------------------------------
# 2. The NULL CONTROL -- it stays silent.
# --------------------------------------------------------------------------------------------

def test_silent_when_nothing_reappeared(repo, tmp_path):
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    (sdir / MARKER).write_text("body\n")     # present BEFORE and untouched throughout
    with watch.bracket(repo, "quiet landing", staging_dir=sdir, out=log):
        pass
    assert _events(log) == [], "an instrument that fires on a quiet landing is noise"


def test_silent_for_findings_and_director_docs_arriving_in_the_root(repo, tmp_path):
    """Findings and director docs land in the staging root legitimately and constantly. A record
    on those is the noise a real event gets read past."""
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    with watch.bracket(repo, "landing", staging_dir=sdir, out=log):
        (sdir / "WORKER_FINDING_SOMETHING_2026-08-20.md").write_text("a finding\n")
        (sdir / "DIRECTOR_CONSOLE_2026-08-20.md").write_text("a steer\n")
    assert _events(log) == []


def test_silent_when_a_marker_is_correctly_ARCHIVED_during_the_landing(repo, tmp_path):
    """Retirement is the healthy path: root -> done/. The instrument must not report the fix as
    the defect."""
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    (sdir / MARKER).write_text("body\n")
    with watch.bracket(repo, "landing", staging_dir=sdir, out=log):
        (sdir / MARKER).rename(sdir / "done" / MARKER)
    assert _events(log) == []


# --------------------------------------------------------------------------------------------
# 3. The observer never breaks the observed.
# --------------------------------------------------------------------------------------------

def test_bracket_never_breaks_the_landing_when_forensics_raises(repo, tmp_path, monkeypatch):
    log = tmp_path / "out.jsonl"
    sdir = _staging(repo)
    monkeypatch.setattr(watch, "forensics",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("instrument broke")))
    landed = []
    with watch.bracket(repo, "landing", staging_dir=sdir, out=log):
        (sdir / MARKER).write_text("body\n")
        landed.append(True)
    assert landed == [True], "the instrument took the landing down with it"
    assert _events(log) == []


def test_bracket_never_breaks_the_landing_when_the_log_is_unwritable(repo, tmp_path):
    sdir = _staging(repo)
    unwritable = tmp_path / "no-such-dir" / "x" / "out.jsonl"
    (tmp_path / "no-such-dir").write_text("this is a FILE, so mkdir under it fails")
    landed = []
    with watch.bracket(repo, "landing", staging_dir=sdir, out=unwritable):
        (sdir / MARKER).write_text("body\n")
        landed.append(True)
    assert landed == [True]


def test_the_bodys_exception_propagates_unchanged(repo, tmp_path):
    """A `finally` that swallows is how an instrument silently converts a RED gate into a green
    landing. The type and the message must both survive."""
    sdir = _staging(repo)
    with pytest.raises(ValueError, match="GATE RED on the resulting tree"):
        with watch.bracket(repo, "landing", staging_dir=sdir, out=tmp_path / "o.jsonl"):
            raise ValueError("GATE RED on the resulting tree")


def test_census_returns_empty_on_an_unreadable_directory(repo, tmp_path):
    """FAIL-SAFE DIRECTION: an unreadable staging dir must yield no record, never an exception
    into the landing. `before is None` also has to disable the after-census, or a missing
    baseline would report the whole directory as having reappeared."""
    missing = tmp_path / "does-not-exist"
    assert watch.census(missing) == {}


# --------------------------------------------------------------------------------------------
# 4. It has a real running caller.
# --------------------------------------------------------------------------------------------

def test_the_landing_tool_actually_brackets_its_gate(repo):
    """A control's own test is not a caller. The consumer is `surgical_land._land_once`, which
    runs on every landing on this tree -- and the bracket has to be around `run_gate`, because
    the gate run is the window the evidence points at."""
    import inspect

    from tools import surgical_land

    src = inspect.getsource(surgical_land._land_once)
    assert "staging_root_resurrection_watch.bracket" in src, "the instrument has no caller"
    bracket_at = src.index("staging_root_resurrection_watch.bracket")
    gate_at = src.index("run_gate(checkout, hook_rel)")
    assert bracket_at < gate_at, "the bracket must open BEFORE the gate it is watching"
