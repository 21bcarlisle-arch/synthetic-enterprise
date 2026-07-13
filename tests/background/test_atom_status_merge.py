"""Proof test for the per-atom write-inbox merge (H9 / H10 Half B).

The director's DoD: two disjoint BUILD atoms building simultaneously, both
status updates landing, no lost writes, map integrity preserved, clean git
merge, pre-flight conflict detection. Spec:
docs/design/WORKTREE_AND_MAP_CONTENTION_DESIGN.md "Proof test spec".

These tests operate on a COPY of the real maturity_map.yaml in a tmp dir --
they never mutate the checked-in map.
"""
from __future__ import annotations

import shutil
import subprocess
import threading
from pathlib import Path

import yaml

from tools.merge_atom_status import (
    MergeError,
    changed_files,
    merge,
    preflight_inbox_overlap,
    preflight_overlap,
    scoped_suite_for,
)

PROJECT = Path(__file__).resolve().parent.parent.parent
REAL_MAP = PROJECT / "docs" / "design" / "maturity_map.yaml"

# Two disjoint real atoms currently at level 0 -- the H9/H10 pair this build
# is for. Kept generic (looked up, not hard-required) so the test survives a
# level bump of either atom.
ATOM_A = "H9_map_write_serialisation"
ATOM_B = "H10_worktree_isolation"


def _split_blocks(text: str) -> dict[str, str]:
    """Map atom id -> its exact block text (from its `- id:` line up to the
    next top-level list item). Preamble is keyed under '__preamble__'."""
    lines = text.splitlines(keepends=True)
    blocks: dict[str, str] = {}
    cur_id = "__preamble__"
    buf: list[str] = []
    for ln in lines:
        if ln.startswith("- id: "):
            blocks[cur_id] = "".join(buf)
            cur_id = ln[len("- id: "):].strip()
            buf = [ln]
        else:
            buf.append(ln)
    blocks[cur_id] = "".join(buf)
    return blocks


def _write_inbox(inbox_dir: Path, atom_id: str, level: int, tag: str) -> None:
    (inbox_dir / f"{atom_id}.yaml").write_text(
        yaml.safe_dump(
            {
                "id": atom_id,
                "level_current": level,
                "append_evidence": [f"docs/design/{tag}.md"],
                "append_simplification": [f"2026-07-13 BUILD {tag} landed"],
                "written_by": f"fork/{atom_id}",
                "written_at": "2026-07-13T00:00:00Z",
            }
        )
    )


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    map_copy = tmp_path / "maturity_map.yaml"
    shutil.copy2(REAL_MAP, map_copy)
    inbox_dir = tmp_path / "atom_status"
    inbox_dir.mkdir()
    return map_copy, inbox_dir


# ---------------------------------------------------------------------------
# 1. Concurrent writes are safe (disjoint paths => no lock, no corruption)
# ---------------------------------------------------------------------------
def test_concurrent_disjoint_inbox_writes_never_corrupt(tmp_path):
    _, inbox_dir = _fixture(tmp_path)
    errors: list[Exception] = []

    def writer(atom_id: str):
        try:
            for i in range(50):
                _write_inbox(inbox_dir, atom_id, i % 4, f"round{i}")
        except Exception as e:  # pragma: no cover
            errors.append(e)

    ta = threading.Thread(target=writer, args=(ATOM_A,))
    tb = threading.Thread(target=writer, args=(ATOM_B,))
    ta.start(); tb.start(); ta.join(); tb.join()

    assert not errors
    # both files exist and parse as valid YAML -- no partial/corrupt write
    for atom_id in (ATOM_A, ATOM_B):
        data = yaml.safe_load((inbox_dir / f"{atom_id}.yaml").read_text())
        assert data["id"] == atom_id


# ---------------------------------------------------------------------------
# 2 + 3. No lost update after merge; map integrity (only targets changed)
# ---------------------------------------------------------------------------
def test_merge_lands_both_and_preserves_every_other_atom(tmp_path):
    map_copy, inbox_dir = _fixture(tmp_path)
    before = map_copy.read_text()
    before_blocks = _split_blocks(before)

    _write_inbox(inbox_dir, ATOM_A, 1, "H9_proof")
    _write_inbox(inbox_dir, ATOM_B, 2, "H10_proof")

    folded = merge(map_path=map_copy, inbox_dir=inbox_dir, clear=True)
    assert folded == sorted([ATOM_A, ATOM_B])

    after = map_copy.read_text()
    after_atoms = {a["id"]: a for a in yaml.safe_load(after)}

    # (2) NO LOST UPDATE: both atoms show their new level -- neither clobbered
    assert after_atoms[ATOM_A]["level_current"] == 1
    assert after_atoms[ATOM_B]["level_current"] == 2

    # appended evidence + simplification landed on both
    assert "docs/design/H9_proof.md" in after_atoms[ATOM_A]["evidence"]
    assert "docs/design/H10_proof.md" in after_atoms[ATOM_B]["evidence"]
    assert any("H9_proof" in s for s in after_atoms[ATOM_A]["simplifications"])
    assert any("H10_proof" in s for s in after_atoms[ATOM_B]["simplifications"])

    # (3) MAP INTEGRITY: exactly {A, B} changed; every other block byte-identical
    after_blocks = _split_blocks(after)
    assert set(before_blocks) == set(after_blocks)
    changed = {k for k in before_blocks if before_blocks[k] != after_blocks[k]}
    assert changed == {ATOM_A, ATOM_B}, f"unexpected blocks changed: {changed}"

    # hand-authored fields on an untouched atom are intact (spot check)
    d1 = next(a for a in yaml.safe_load(before) if a["id"] == "D1_bill_correctness")
    d2 = next(a for a in yaml.safe_load(after) if a["id"] == "D1_bill_correctness")
    assert d1 == d2

    # inboxes cleared after a successful fold
    assert not list(inbox_dir.glob("*.yaml"))


# ---------------------------------------------------------------------------
# 5a. Pre-flight: same-atom double-target is rejected (inbox level)
# ---------------------------------------------------------------------------
def test_preflight_rejects_two_inboxes_targeting_same_atom(tmp_path):
    map_copy, inbox_dir = _fixture(tmp_path)
    # two inbox files can't share a filename, so simulate the overlap via the
    # pure detector (the real double-target arrives as a re-sequenced branch)
    inboxes = [{"id": ATOM_A}, {"id": ATOM_A}, {"id": ATOM_B}]
    assert preflight_inbox_overlap(inboxes) == [ATOM_A]
    assert preflight_inbox_overlap([{"id": ATOM_A}, {"id": ATOM_B}]) == []


def test_merge_aborts_on_unknown_atom(tmp_path):
    map_copy, inbox_dir = _fixture(tmp_path)
    (inbox_dir / "not_a_real_atom.yaml").write_text(
        yaml.safe_dump({"id": "not_a_real_atom", "level_current": 1})
    )
    try:
        merge(map_path=map_copy, inbox_dir=inbox_dir)
        assert False, "expected MergeError for unknown atom"
    except MergeError as e:
        assert "not found" in str(e)
    # aborted before writing -> inbox not cleared, map untouched
    assert (inbox_dir / "not_a_real_atom.yaml").exists()


# ---------------------------------------------------------------------------
# 4 + 5b. Clean git merge of disjoint branches; pre-flight overlap detection
# ---------------------------------------------------------------------------
def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout


def test_disjoint_branches_merge_clean_and_preflight_detects_overlap(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "base.txt").write_text("base\n")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()

    # sibling branches from base: A touches file_a only, B touches file_b only
    _git(repo, "checkout", "-q", "-b", "atomA", base)
    (repo / "file_a.txt").write_text("a\n")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "A")

    _git(repo, "checkout", "-q", "-b", "atomB", base)
    (repo / "file_b.txt").write_text("b\n")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "B")

    # (5b) pre-flight: disjoint => empty intersection
    ca = changed_files("atomB", "atomA", cwd=repo)
    cb = changed_files("atomA", "atomB", cwd=repo)
    assert preflight_overlap(ca, cb) == set()

    # (4) empty overlap => clean --no-ff merge
    _git(repo, "checkout", "-q", "atomA")
    merged = subprocess.run(
        ["git", "merge", "--no-ff", "-m", "merge B", "atomB"],
        cwd=repo, capture_output=True, text=True,
    )
    assert merged.returncode == 0, merged.stderr
    assert (repo / "file_a.txt").exists() and (repo / "file_b.txt").exists()

    # (5b) negative case: a sibling branch that ALSO touches file_a (a
    # mis-declared file_scope) is detected as a non-empty overlap
    _git(repo, "checkout", "-q", "-b", "atomC", base)
    (repo / "file_a.txt").write_text("a-modified-by-C\n")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "C touches file_a")
    over = preflight_overlap(
        changed_files("atomC", "atomA", cwd=repo),
        changed_files("atomA", "atomC", cwd=repo),
    )
    assert "file_a.txt" in over  # flagged for re-sequence, not merged blind


# ---------------------------------------------------------------------------
# Scoped-suite selector (design A3)
# ---------------------------------------------------------------------------
def test_scoped_suite_selector():
    assert scoped_suite_for(["saas/billing.py"]) == ["tests/saas"]
    assert scoped_suite_for(["company/compliance/x.py"]) == ["tests/company"]
    assert set(scoped_suite_for(["sim/foo.py", "simulation/bar.py"])) == {
        "tests/sim", "tests/simulation",
    }
    assert set(scoped_suite_for([".claude/agents", "background/tree_lock.py"])) == {
        "tests/background",
    }
    assert scoped_suite_for(["site/foo/index.html"]) == []  # pixel-verified, no unit suite
    assert scoped_suite_for([]) == []
