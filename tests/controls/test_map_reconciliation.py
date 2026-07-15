"""RECONCILIATION GUARD: the map's level self-report must not silently diverge from
external truth (docs/design/MAP_TRUTH_RECONCILIATION.md, F2, 2026-07-15).

Root cause it guards: `maturity_map.yaml` `level_current` is a JUDGMENT-written self-report;
a fork writes its level to a narrow inbox at `docs/design/atom_status/<id>.yaml` and an
integrator folds it into the map via `tools/merge_atom_status.merge()`, which CLEARS the
inbox only after folding. An inbox left at rest is therefore a level report that never
reached the map — the exact self-report-vs-external-truth divergence the director gated the
unwatched loop on. This control FAILS on that signal (fail-closed), and is R15
mutation-proven: a planted inbox makes it fire; folding/clearing makes it pass.

The unwatched executor loop (background/executor_governor.run_loop) consults the SAME
primitive (`unfolded_inbox_ids`) as a per-cycle STOP condition, so the divergence class is a
loop halt, not a silent drift discovered hours later.
"""
from pathlib import Path

from tools.merge_atom_status import unfolded_inbox_ids

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_INBOX_DIR = REPO_ROOT / "docs" / "design" / "atom_status"


# ─────────────────────────────── the live guard ───────────────────────────────
def test_no_unfolded_atom_status_inbox_at_rest():
    """THE control: at rest, no atom carries an unfolded write-inbox. A non-empty
    result means a fork's level report never reached the canonical map — a silent
    map-vs-committed-work divergence. The loop treats this as a STOP."""
    unfolded = unfolded_inbox_ids(REAL_INBOX_DIR)
    assert unfolded == [], (
        "unfolded atom_status inbox(es) at rest -- a level report never folded into the "
        "map (self-report vs external truth, MAP_TRUTH_RECONCILIATION.md). Run "
        "`python3 -m tools.merge_atom_status` and commit the map, or delete the stale "
        f"inbox: {unfolded}"
    )


# ───────────────────── R15 MUTATION PROOF (mandatory) ──────────────────────────
def test_guard_FIRES_on_a_planted_inbox(tmp_path):
    """A planted inbox makes the guard fire (it is load-bearing, not tautological)."""
    (tmp_path / "SOME_atom.yaml").write_text("id: SOME_atom\nlevel_current: 2\n", encoding="utf-8")
    assert unfolded_inbox_ids(tmp_path) == ["SOME_atom"], "guard did NOT see the unfolded inbox"


def test_guard_PASSES_when_inbox_folded_and_cleared(tmp_path):
    """After the inbox is folded+cleared (merge()'s post-condition), the guard passes --
    proving it keys on the DIVERGENCE SIGNAL (inbox at rest), not on the dir existing."""
    inbox = tmp_path / "SOME_atom.yaml"
    inbox.write_text("id: SOME_atom\nlevel_current: 2\n", encoding="utf-8")
    assert unfolded_inbox_ids(tmp_path)  # fires while present
    inbox.unlink()  # merge(clear=True) deletes it after folding
    assert unfolded_inbox_ids(tmp_path) == [], "guard still fired after the inbox was cleared"


def test_guard_ignores_readme_and_non_inbox_files(tmp_path):
    """No false positive on the dir's README / non-*.yaml scaffolding (the real dir
    ships a README.md -- it must not read as an unfolded level report)."""
    (tmp_path / "README.md").write_text("# atom_status inbox dir\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("scratch\n", encoding="utf-8")
    assert unfolded_inbox_ids(tmp_path) == []


def test_guard_fail_closed_on_missing_dir(tmp_path):
    """A missing inbox dir is 'nothing unfolded' (clean), not an error -- the dir is
    created on demand by a fork; its absence is the empty state, never a false alarm."""
    assert unfolded_inbox_ids(tmp_path / "does-not-exist") == []
