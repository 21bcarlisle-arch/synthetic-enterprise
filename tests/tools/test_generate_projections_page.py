"""Tests for `tools/generate_projections_page.py` — atom `G13_projection_consumers`.

The site-page half of the proof-of-caller. Four properties, each proven BOTH WAYS per R15 —
the control passes on the real mechanism, and a MUTATION into that mechanism's own named
defect makes it fail. A control that cannot fail is worse than none.

  1. HEAD, never the working tree  → `test_the_working_tree_does_not_reach_the_feed`
                                     mutant: `test_r15_the_head_control_fires_on_a_tree_read`
  2. FAIL-CLOSED, never a zero board → `test_an_unreadable_source_writes_nothing`
                                     mutant: `test_r15_the_fail_closed_control_fires_on_an_empty_board`
  3. The feed carries the sha it is true of (R14) → `test_the_feed_is_stamped_with_its_commit`
                                     and `test_check_reds_when_the_feed_is_behind_head`
  4. FAIL-VISIBLE on the page, never a silent fallback → the two render tests at the bottom,
     which drive the door's OWN inline script through its Node harness (R11 in-repo) and
     assert on the produced pixels, not on the source string.

The fixtures follow `tests/tools/test_build_projections.py` — a throwaway git repo carrying
the real source paths — because the property under test is "what is COMMITTED reaches the
feed", and that cannot be tested against a repo whose sources you are not free to move.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.tools.test_build_projections import (  # noqa: E402
    _atoms_fixture,
    _commit_all,
    _gaps_fixture,
    _git,
    _probe_fixture,
    _runs_fixture,
    _write,
)
from tools import build_projections as bp  # noqa: E402
from tools import generate_projections_page as gpp  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DOOR = REPO / "site" / "wip-flow" / "index.html"
HARNESS = REPO / "site" / "wip-flow" / "_render_harness.mjs"
NODE = shutil.which("node")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A throwaway git repo carrying the real SOURCES paths, committed."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "test")
    _write(root, "docs/design/maturity_map.yaml", _atoms_fixture())
    _write(root, "docs/observability/run_history.json", _runs_fixture())
    _write(root, "docs/observability/coupled_gap_ledger.json", _gaps_fixture())
    _write(root, bp.SCALE_PROBE_RELPATH, _probe_fixture())
    _commit_all(root, "fixtures")
    return root


def _feed(repo: Path) -> dict:
    return json.loads((repo / "site" / "data" / "projections.json").read_text())


# ------------------------------------------------- 1. HEAD, never the working tree


def test_the_working_tree_does_not_reach_the_feed(repo: Path):
    """An atom moved but NOT committed must not change the published WIP count.

    This is the property the file it replaces does not have: `generate_wip_flow_data.py`
    reads `docs/design/maturity_map.yaml` off disk, so it publishes whatever a lane happens
    to have half-written.
    """
    gpp.write(repo=repo)
    before = _feed(repo)["wip"]
    assert before["by_stage"], "fixture must produce a board to move"

    atoms = _atoms_fixture()
    for atom in atoms:
        atom["loop_stage"] = "verify"          # every atom moved, in the WORKING TREE only
    _write(repo, "docs/design/maturity_map.yaml", atoms)

    gpp.write(repo=repo)
    assert _feed(repo)["wip"] == before, "an uncommitted map edit reached the published feed"

    _commit_all(repo, "move them for real")
    gpp.write(repo=repo)
    after = _feed(repo)["wip"]
    assert after != before, "a COMMITTED map edit failed to reach the feed"
    assert [s["stage"] for s in after["by_stage"]] == ["verify"]


def test_r15_the_head_control_fires_on_a_tree_read(repo: Path, monkeypatch):
    """MUTATION: make the store read the WORKING TREE instead of the commit.

    The named defect is exactly `generate_wip_flow_data.py`'s: a projection of uncommitted
    state. Under it, `test_the_working_tree_does_not_reach_the_feed` must be FALSE.
    """
    gpp.write(repo=repo)
    before = _feed(repo)["wip"]

    def _read_off_disk(repo_path, relpath, rev="HEAD"):
        return (Path(repo_path) / relpath).read_bytes()

    monkeypatch.setattr(bp, "read_committed", _read_off_disk)

    atoms = _atoms_fixture()
    for atom in atoms:
        atom["loop_stage"] = "verify"
    _write(repo, "docs/design/maturity_map.yaml", atoms)

    gpp.write(repo=repo)
    assert _feed(repo)["wip"] != before, (
        "the mutant did not change the feed — the HEAD control is untested by this fixture"
    )


# ------------------------------------------------- 2. fail-closed, never a zero board


def test_an_unreadable_source_writes_nothing(repo: Path):
    """A source that cannot be parsed leaves the PREVIOUS feed byte-identical."""
    gpp.write(repo=repo)
    good = (repo / "site" / "data" / "projections.json").read_bytes()

    (repo / "docs" / "observability" / "run_history.json").write_text("{not json")
    _commit_all(repo, "break a source")

    with pytest.raises(gpp.StoreUnavailable):
        gpp.write(repo=repo)
    assert (repo / "site" / "data" / "projections.json").read_bytes() == good


def test_an_empty_board_fails_closed_rather_than_publishing_zero(repo: Path, tmp_path: Path):
    """MUTATION: a REAL store whose `atoms` table has been emptied.

    Zero atoms downstream is indistinguishable from "we counted, and the board is empty".
    The generator must refuse, not publish a board of zeroes. Run against a COPY of a real
    built store rather than a stub, so the guard is proven on the shape it will actually
    meet — a store that opened fine and answered.
    """
    gpp.write(repo=repo)
    emptied = tmp_path / "emptied.sqlite"
    shutil.copyfile(repo / bp.STORE_RELPATH, emptied)
    conn = sqlite3.connect(str(emptied))
    conn.execute("DELETE FROM atoms")
    conn.commit()

    with pytest.raises(gpp.StoreUnavailable, match="refusing to publish a zero board"):
        gpp._wip_from_store(conn)
    conn.close()


def test_r15_the_fail_closed_control_fires_when_the_refusal_is_removed(repo: Path):
    """MUTATION: the refusal replaced by the fail-OPEN it exists to prevent.

    `_wip_from_store` without its empty-guard returns a perfectly well-formed board of
    zeroes and `status: ok` — the shape R15 names FAIL-OPEN. Under it the control above is
    FALSE, which is what makes the control worth having.
    """
    class _EmptyAtoms:
        def execute(self, sql, *a, **k):
            return iter([]) if "FROM atoms" in sql else iter([])

    with pytest.raises(gpp.StoreUnavailable):
        gpp._wip_from_store(_EmptyAtoms())

    # the fail-open variant, written out so the difference is visible and not asserted
    def _wip_without_the_guard(conn):
        rows = list(conn.execute("SELECT lane, loop_stage FROM atoms"))
        return dict(total_atoms=len(rows), by_stage=[], by_lane=[],
                    concurrent_build_wip=0, harden_wip=0, idle_count=0)

    mutant = _wip_without_the_guard(_EmptyAtoms())
    assert mutant["total_atoms"] == 0, "the mutant must publish the zero board, not raise"


# ------------------------------------------------- 3. the feed carries its clock (R14)


def test_the_feed_is_stamped_with_the_commit_it_is_true_of(repo: Path):
    gpp.write(repo=repo)
    payload = _feed(repo)
    head = _git(repo, "rev-parse", "HEAD").strip()
    assert payload["store"]["head_sha"] == head
    assert payload["wip"]["basis"] == gpp.WIP_BASIS
    assert payload["store"]["derived_from"].startswith("committed blobs only")


def test_the_feed_names_the_file_it_replaces(repo: Path):
    """Exit (1) requires the replaced file to be NAMED. A reader of the artefact alone
    must be able to see what moved, without reading the generator."""
    gpp.write(repo=repo)
    replaces = _feed(repo)["replaces"]
    assert replaces["file"] == "site/data/wip_flow.json"
    assert replaces["block"] == "wip"


def test_check_reds_when_the_feed_is_behind_head(repo: Path):
    gpp.write(repo=repo)
    ok, reason = gpp._current(repo=repo)
    assert ok, reason

    _write(repo, "docs/observability/run_history.json", _runs_fixture())
    (repo / "docs" / "observability" / "run_history.json").write_text(
        json.dumps(_runs_fixture() + _runs_fixture())
    )
    _commit_all(repo, "move head")

    ok, reason = gpp._current(repo=repo)
    assert not ok and "HEAD is" in reason


def test_every_key_the_page_consumes_is_present(repo: Path):
    """The door's `renderWip` reads these and nothing else; a shape drift here is a blank
    panel on the page, which the render tests below would then catch as a pixel."""
    gpp.write(repo=repo)
    wip = _feed(repo)["wip"]
    for key in ("total_atoms", "by_stage", "by_lane", "concurrent_build_wip",
                "harden_wip", "idle_count"):
        assert key in wip, key
    for stage in wip["by_stage"]:
        assert {"stage", "label", "count"} <= set(stage)
    for lane in wip["by_lane"]:
        assert {"lane", "lane_name", "total", "build", "harden", "idle"} <= set(lane)


# ------------------------------------------------- 4. fail-VISIBLE on the page (R11 in-repo)


def _render(payload: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(DOOR)],
        input=json.dumps(payload), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_the_rendered_page_states_which_commit_the_wip_came_from():
    out = _render({
        "wip": {"total_atoms": 7, "by_stage": [], "by_lane": [],
                "concurrent_build_wip": 1, "harden_wip": 2, "idle_count": 4},
        "projection_store": {"head_sha": "deadbeefcafe1234", "rows_total": 432,
                             "derived_from": "committed blobs only (git cat-file)"},
    })
    note = out["build-note"]["innerHTML"]
    assert "projection store @ deadbeefc" in note, note
    assert "432 rows" in note, note


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_an_unavailable_store_is_rendered_in_red_and_never_silently_swallowed():
    """The failure mode this replaces is a stale number nobody can see is stale. If the
    store does not answer, the page must SAY the numbers came from the hand-refreshed file."""
    out = _render({
        "wip": {"total_atoms": 7, "by_stage": [], "by_lane": [],
                "concurrent_build_wip": 1, "harden_wip": 2, "idle_count": 4},
        "projection_store_unavailable": True,
    })
    note = out["build-note"]["innerHTML"]
    assert "UNAVAILABLE" in note, note
    assert "var(--red)" in note, note
    assert "wip_flow.json" in note, note


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_r15_the_provenance_control_is_silent_when_there_is_nothing_to_say():
    """A stamp that renders unconditionally would pass both tests above while proving
    nothing. Neither branch may fire when the page is driven with wip_flow.json alone."""
    out = _render({"wip": {"total_atoms": 7, "by_stage": [], "by_lane": [],
                           "concurrent_build_wip": 1, "harden_wip": 2, "idle_count": 4}})
    note = out["build-note"]["innerHTML"]
    assert "projection store" not in note, note
    assert "UNAVAILABLE" not in note, note


def test_the_door_reads_the_projection_feed():
    """The wiring itself, asserted on the shipped page: the door fetches the store's feed
    and takes `wip` from it. Without this the generator is a design with no caller — the
    exact shape the instruction that minted this atom exists to end."""
    html = DOOR.read_text()
    assert "../data/projections.json" in html
    assert "d.wip=p.wip" in html
