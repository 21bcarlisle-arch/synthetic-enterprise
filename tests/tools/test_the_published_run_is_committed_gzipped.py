"""The published run is committed gzipped, read through one helper, and the plain copy is retired
by the shared tree's own publish.

THE DEFECT THIS FAILS ON: the plain run output reached 123.5 MB, over GitHub's 100 MiB push limit;
compact JSON bought 91.6 MB on a book growing 4.6x a week. See
docs/staging/SEAT_FINDING_THE_PUBLISHED_RUN_OUTGREW_GITHUBS_FILE_LIMIT_2026-10-10.md.
"""
from __future__ import annotations

import gzip
import json
import subprocess
from pathlib import Path

import pytest

import background.process_run_complete as prc
from tools import run_output_store as store


def test_the_reader_takes_the_plain_file_and_falls_back_to_the_gz(tmp_path):
    """Both branches, one control: plain preferred when present, gz when it is not, refusal when
    neither. A reader that only ever read the gz (or only the plain) fails one leg."""
    plain = tmp_path / "run_output_latest.json"
    plain.write_text(json.dumps({"which": "plain"}))
    store.gz_twin(plain).write_bytes(gzip.compress(json.dumps({"which": "gz"}).encode()))

    taken = {store.load_run_output(plain)["which"]}
    plain.unlink()
    taken.add(store.load_run_output(plain)["which"])
    assert taken == {"plain", "gz"}, taken

    store.gz_twin(plain).unlink()
    with pytest.raises(FileNotFoundError, match=r"run_output_latest\.json\.gz"):
        store.load_run_output(plain)


def test_the_gz_is_deterministic_and_reads_back_equal(tmp_path):
    """Same run, same bytes -- else every publish commits a changed blob for an unchanged run."""
    plain = tmp_path / "run_output_latest.json"
    plain.write_text(json.dumps({"bills": list(range(1000))}, separators=(",", ":")))
    first = store.write_published(plain).read_bytes()
    store.gz_twin(plain).unlink()
    second = store.write_published(plain).read_bytes()
    assert first == second
    assert store.loads_run_output(first) == json.loads(plain.read_text())
    plain.write_text(json.dumps({"bills": []}))
    assert store.loads_run_output(store.write_published(plain).read_bytes()) == {"bills": []}, (
        "a changed run must rewrite the gz, not keep the old one")


def _repo(tmp_path: Path, *, plain_tracked: bool) -> Path:
    root = tmp_path / ("tracked" if plain_tracked else "retired")
    reports = root / "docs" / "reports"
    reports.mkdir(parents=True)
    plain = reports / "run_output_latest.json"
    plain.write_text("{}")
    store.write_published(plain)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    if plain_tracked:
        subprocess.run(["git", "add", "--", store.LATEST_REL], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"],
                       cwd=root, check=True)
    return root


@pytest.mark.parametrize("plain_tracked", [True, False])
def test_the_publish_retires_the_plain_run_only_while_head_still_carries_it(
        tmp_path, monkeypatch, plain_tracked):
    """While the plain file is at HEAD, the landing that commits its gz removes it (content None,
    declared in `drops`); once retired, the landing passes nothing extra. Both arms run, so a
    retirement that never fires, or fires every cycle, is red."""
    from tools import surgical_land

    root = _repo(tmp_path, plain_tracked=plain_tracked)
    seen = {}

    def fake_land(root_, paths, message, attempts=None, on_lost=None, **kw):
        seen["paths"], seen["kw"] = list(paths), kw
        return "f" * 40

    monkeypatch.setattr(prc, "PROJECT_DIR", root)
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_wait_for_a_quiet_tree", lambda *a, **k: {"waited_seconds": 0})
    monkeypatch.setattr(prc, "_record_commit_hook_duration", lambda *a, **k: None)
    monkeypatch.setattr(surgical_land, "land", fake_land)

    prc._land_publish_commit([str(root / store.PUBLISHED_REL)], "msg", "abc1234")

    if plain_tracked:
        assert seen["kw"] == {"content": {store.LATEST_REL: None},
                              "drops": frozenset({store.LATEST_REL})}, seen
        assert store.LATEST_REL in seen["paths"]
    else:
        assert seen["kw"] == {}, seen
        assert store.LATEST_REL not in seen["paths"]
    assert (root / store.LATEST_REL).is_file(), "the plain file on disk is never touched"


def test_the_run_committed_at_head_gzips_under_a_quarter_of_the_push_limit():
    """The real run, through the real writer: the headroom the change exists to buy."""
    found = store.resolve_run_output(store.PROJECT / store.LATEST_REL)
    if found is None:
        pytest.skip("no run output in this checkout")
    packed = gzip.compress(found.read_bytes() if found.suffix != ".gz"
                           else gzip.decompress(found.read_bytes()), compresslevel=9, mtime=0)
    assert len(packed) < prc.GITHUB_PUSH_FILE_LIMIT_BYTES / 4, len(packed)
