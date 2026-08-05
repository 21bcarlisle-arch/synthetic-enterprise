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

import pytest
import yaml

from tools import simplifications_store as store
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
REAL_STORE = PROJECT / "docs" / "design" / "simplifications"

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
    # simplifications live in the sibling store (retro FM-1); copy it beside the
    # map so the merge finds it exactly as it does in the live tree.
    shutil.copytree(REAL_STORE, tmp_path / "simplifications")
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

    # appended evidence landed in the map; appended simplification landed in the
    # sibling store (retro FM-1), with the map's count kept in sync.
    sd = map_copy.parent / "simplifications"
    assert "docs/design/H9_proof.md" in after_atoms[ATOM_A]["evidence"]
    assert "docs/design/H10_proof.md" in after_atoms[ATOM_B]["evidence"]
    assert any("H9_proof" in s for s in store.for_atom(ATOM_A, sd))
    assert any("H10_proof" in s for s in store.for_atom(ATOM_B, sd))
    assert after_atoms[ATOM_A]["simplifications_count"] == store.count_for_atom(ATOM_A, sd)
    assert after_atoms[ATOM_B]["simplifications_count"] == store.count_for_atom(ATOM_B, sd)
    assert "simplifications" not in after_atoms[ATOM_A] and "simplifications" not in after_atoms[ATOM_B]

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


# ---------------------------------------------------------------------------
# BLOCK-STYLE FOLD (2026-07-29 publish-gate wedge)
#
# The wedge: a fork wrote an inbox for OPS1_transport_failure_must_be_loud, whose
# `evidence:`/`simplifications:` are BLOCK-style lists. The fold supported only
# single-line FLOW lists and raised MergeError, so `merge()` aborted and never
# cleared the inbox -- and an inbox left at rest fail-closes
# tests/controls/test_map_reconciliation.py, which is IN the publish gate. One
# unfoldable style therefore wedged publishing indefinitely, and would again for
# any of the map's 30+ block-style atoms.
# ---------------------------------------------------------------------------
# Post-retro-FM-1 shape: `simplifications` moved to the sibling store, the map
# carries `simplifications_count`. The block-style `evidence:` fold (the actual
# 2026-07-29 regression) is preserved. `_block_fixture` seeds the store to match
# the counts below.
BLOCK_MAP = """\
- id: FLOW_atom
  level_current: 0
  evidence: [a.py]
  simplifications_count: 1
- id: BLOCK_atom
  level_current: 0
  evidence:
  - first.py
  - second.py
  simplifications_count: 1
  file_scope:
  - background/x.py
- id: TAIL_atom
  level_current: 1
  evidence: [z.py]
"""
# The existing notes those counts stand for (seeded into the fixture store).
_BLOCK_STORE_SEED = {
    "FLOW_atom": ["flow note"],
    "BLOCK_atom": [
        "an existing note that happens to be quite long and would be wrapped by a "
        "naive dumper across continuation lines"
    ],
}


def _assert_no_duplicate_keys(text: str) -> None:
    """pyyaml silently keeps the LAST of duplicate mapping keys, so a fold that
    CREATES a field the atom already has still round-trips and still looks right.
    That is a silent map corruption; detect it structurally."""
    class _StrictLoader(yaml.SafeLoader):
        pass

    def _no_dupes(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=deep)
            assert key not in seen, f"duplicate key in the folded map: {key!r}"
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)

    _StrictLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_dupes
    )
    yaml.load(text, Loader=_StrictLoader)


def _block_fixture(tmp_path: Path) -> tuple[Path, Path]:
    map_copy = tmp_path / "maturity_map.yaml"
    map_copy.write_text(BLOCK_MAP)
    sd = tmp_path / "simplifications"
    for aid, notes in _BLOCK_STORE_SEED.items():
        store.append_for_atom(aid, notes, sd)
    inbox_dir = tmp_path / "atom_status"
    inbox_dir.mkdir()
    return map_copy, inbox_dir


def test_block_style_atom_folds_and_clears_its_inbox(tmp_path):
    """THE regression: a block-style atom folds, and the inbox is CLEARED. The
    clear is the load-bearing half -- an inbox that survives the merge is what
    wedges the publish gate."""
    map_copy, inbox_dir = _block_fixture(tmp_path)
    _write_inbox(inbox_dir, "BLOCK_atom", 3, "blockproof")

    folded = merge(map_path=map_copy, inbox_dir=inbox_dir)

    assert folded == ["BLOCK_atom"]
    assert list(inbox_dir.glob("*.yaml")) == [], "inbox NOT cleared -- the gate stays wedged"

    atoms = {a["id"]: a for a in yaml.safe_load(map_copy.read_text())}
    atom = atoms["BLOCK_atom"]
    sd = map_copy.parent / "simplifications"
    assert atom["level_current"] == 3
    assert atom["evidence"] == ["first.py", "second.py", "docs/design/blockproof.md"]
    # the appended simplification lands in the STORE; the map's count tracks it
    assert store.for_atom("BLOCK_atom", sd)[-1] == "2026-07-13 BUILD blockproof landed"
    assert atom["simplifications_count"] == store.count_for_atom("BLOCK_atom", sd) == 2
    assert "simplifications" not in atom
    # the append must land in the RIGHT list -- not leak into the next field
    assert atom["file_scope"] == ["background/x.py"]


def test_block_fold_leaves_every_other_atom_byte_identical(tmp_path):
    """Narrow-fold contract: only the target atom's block may change."""
    map_copy, inbox_dir = _block_fixture(tmp_path)
    before = _split_blocks(map_copy.read_text())
    _write_inbox(inbox_dir, "BLOCK_atom", 2, "narrow")

    merge(map_path=map_copy, inbox_dir=inbox_dir)

    after = _split_blocks(map_copy.read_text())
    assert set(before) == set(after)
    changed = {k for k in before if before[k] != after[k]}
    assert changed == {"BLOCK_atom"}, f"unexpected blocks changed: {changed}"


def test_flow_and_block_atoms_fold_together(tmp_path):
    """Both styles coexist in the real map; one merge run must handle a mix."""
    map_copy, inbox_dir = _block_fixture(tmp_path)
    _write_inbox(inbox_dir, "BLOCK_atom", 3, "bb")
    _write_inbox(inbox_dir, "FLOW_atom", 2, "ff")

    assert merge(map_path=map_copy, inbox_dir=inbox_dir) == ["BLOCK_atom", "FLOW_atom"]

    atoms = {a["id"]: a for a in yaml.safe_load(map_copy.read_text())}
    assert atoms["FLOW_atom"]["evidence"] == ["a.py", "docs/design/ff.md"]
    assert atoms["BLOCK_atom"]["evidence"][-1] == "docs/design/bb.md"


def test_block_item_serialiser_emits_no_document_marker():
    """R15 mutation pin, on a bug this fix itself made first: `yaml.safe_dump`
    of a BARE scalar appends a `...` document-end marker, which `.strip()` keeps
    attached and which corrupts the map on write. Round-trip every awkward
    scalar shape rather than eyeballing one."""
    from tools.merge_atom_status import _dump_block_item

    for s in ["a, b", "it's", "x: y", "- dash", "p/q.py::test_x", "[bracketed]", "#hash"]:
        dumped = _dump_block_item(s)
        assert "\n" not in dumped, f"multi-line block item would corrupt the map: {s!r}"
        assert yaml.safe_load("- " + dumped) == [s], f"round-trip lost {s!r} -> {dumped!r}"


def test_EVERY_atom_in_the_real_map_is_foldable(tmp_path):
    """THE INVARIANT, not the instance (R10): no atom in the live map may be
    unfoldable. A single unfoldable atom is a latent publish-gate wedge that
    only appears when some fork happens to write that atom's inbox -- exactly
    how the 2026-07-29 wedge arrived. This asserts the whole LIST, so a new
    hand-authored style cannot re-open the hole silently."""
    map_copy = tmp_path / "maturity_map.yaml"
    shutil.copy2(REAL_MAP, map_copy)
    shutil.copytree(REAL_STORE, tmp_path / "simplifications")
    sd = map_copy.parent / "simplifications"
    inbox_dir = tmp_path / "atom_status"
    inbox_dir.mkdir()
    atom_ids = [a["id"] for a in yaml.safe_load(map_copy.read_text())]
    assert len(atom_ids) > 50, "map fixture looks wrong -- refusing a vacuous pass"

    # Folds are REAL and cumulative, never dry-run: a dry run only proves the tool
    # did not raise, and "did not raise" is exactly the fail-open that let a mutant
    # which silently created a DUPLICATE `evidence:` key pass this test.
    unfoldable = []
    for atom_id in atom_ids:
        for stale in inbox_dir.glob("*.yaml"):
            stale.unlink()
        _write_inbox(inbox_dir, atom_id, 1, "foldcheck")
        try:
            merge(map_path=map_copy, inbox_dir=inbox_dir)
        except MergeError as e:
            unfoldable.append(f"{atom_id}: {e}")

    assert unfoldable == [], (
        "atom(s) whose inbox could never be folded -- each is a latent publish-gate "
        f"wedge (the 2026-07-29 fault): {unfoldable}"
    )

    # And the fold must have LANDED on every atom, with no duplicate key papering
    # over a mis-targeted write.
    text = map_copy.read_text()
    _assert_no_duplicate_keys(text)
    folded_map = {a["id"]: a for a in yaml.safe_load(text)}
    # evidence lands in the map; the simplification lands in the sibling store,
    # with the map's count kept in sync -- and NO `simplifications` field returns.
    assert not any("simplifications" in folded_map[aid] for aid in atom_ids), \
        "the fold must never re-create a `simplifications:` field in the map"
    missing = [
        aid for aid in atom_ids
        if "docs/design/foldcheck.md" not in (folded_map[aid].get("evidence") or [])
        or "2026-07-13 BUILD foldcheck landed" not in store.for_atom(aid, sd)
        or folded_map[aid].get("simplifications_count") != store.count_for_atom(aid, sd)
    ]
    assert missing == [], (
        f"fold reported success but the value never reached the map for: {missing}"
    )


# ---------------------------------------------------------------------------
# The other two fold holes the whole-map invariant above surfaced on 2026-07-29:
# a COMMENTED flow list, and an ABSENT field on a freshly minted atom. Both were
# invisible fold failures -- neither the flow regex nor the block regex matched
# the line, so the tool reported "no such field" and aborted the whole merge.
# ---------------------------------------------------------------------------
COMMENTED_MAP = """\
- id: COMMENTED_atom
  level_current: 0
  evidence: [docs/design/BACKLOG.md]  # why this list is what it is [see note]
- id: MINTED_atom
  level_current: 0
  loop_stage: idle
  file_scope: [sim/x.py]
"""


def test_flow_list_with_a_trailing_comment_folds_and_keeps_the_comment(tmp_path):
    """The comment is hand-authored rationale -- folding must not eat it. The `]`
    inside the comment is the trap: a greedy `\\[.*\\]` match swallows it."""
    map_copy = tmp_path / "maturity_map.yaml"
    map_copy.write_text(COMMENTED_MAP)
    inbox_dir = tmp_path / "atom_status"
    inbox_dir.mkdir()
    _write_inbox(inbox_dir, "COMMENTED_atom", 2, "commented")

    merge(map_path=map_copy, inbox_dir=inbox_dir)

    text = map_copy.read_text()
    atoms = {a["id"]: a for a in yaml.safe_load(text)}
    assert atoms["COMMENTED_atom"]["evidence"] == [
        "docs/design/BACKLOG.md", "docs/design/commented.md",
    ]
    assert "# why this list is what it is [see note]" in text, "trailing comment lost"


def test_absent_field_is_created_not_aborted(tmp_path):
    """A newly minted atom has no `evidence:` yet. The FIRST fork to report on it
    must not wedge the publish gate."""
    map_copy = tmp_path / "maturity_map.yaml"
    map_copy.write_text(COMMENTED_MAP)
    inbox_dir = tmp_path / "atom_status"
    inbox_dir.mkdir()
    _write_inbox(inbox_dir, "MINTED_atom", 3, "firstreport")

    assert merge(map_path=map_copy, inbox_dir=inbox_dir) == ["MINTED_atom"]
    assert list(inbox_dir.glob("*.yaml")) == []

    atoms = {a["id"]: a for a in yaml.safe_load(map_copy.read_text())}
    atom = atoms["MINTED_atom"]
    sd = map_copy.parent / "simplifications"
    assert atom["level_current"] == 3
    assert atom["evidence"] == ["docs/design/firstreport.md"]
    # simplification lands in the store; the map gains only its count scalar
    assert store.for_atom("MINTED_atom", sd) == ["2026-07-13 BUILD firstreport landed"]
    assert atom["simplifications_count"] == 1
    assert "simplifications" not in atom
    assert atom["file_scope"] == ["sim/x.py"], "created field mis-nested into a sibling"


def test_a_wrapped_flow_list_FOLDS_now_instead_of_wedging(tmp_path):
    """A flow list whose `]` sits on a LATER line used to be unfoldable, and an unfoldable
    inbox never clears -- so it fail-closed the publish gate forever. Found live 2026-08-03 on
    OPS_run_marker_sweep_livelock (a four-entry evidence list wrapped over four lines), which
    reddened the gate for every writer. The scanner is now handed the rest of the BLOCK rather
    than the rest of the LINE; it was already quote- and depth-aware, so it stops at the true
    closing bracket. The wrapped list is rewritten as one line, with its entries preserved."""
    map_copy = tmp_path / "maturity_map.yaml"
    map_copy.write_text(
        "- id: WRAPPED_atom\n"
        "  level_current: 0\n"
        "  evidence: [first.py,\n"
        "    second.py]\n"
        "  loop_stage: idle\n"  # a stable sibling AFTER the wrapped `]`
    )
    inbox_dir = tmp_path / "atom_status"
    inbox_dir.mkdir()
    _write_inbox(inbox_dir, "WRAPPED_atom", 1, "wrapped")

    merge(map_path=map_copy, inbox_dir=inbox_dir)

    atom = yaml.safe_load(map_copy.read_text())[0]
    assert atom["evidence"][:2] == ["first.py", "second.py"], "wrapped entries lost in the fold"
    assert "wrapped" in " ".join(atom["evidence"]), "the inbox addition never landed"
    # and the sibling key is intact -- the multi-line splice must not eat the line after `]`.
    assert atom["loop_stage"] == "idle", "the splice consumed a sibling field"


def test_unparseable_field_STILL_aborts_rather_than_creating_a_duplicate_key(tmp_path):
    """R15: widening the parser must not disarm the guard. The create path (c) must never fire
    on a field that EXISTS but the fold failed to parse -- that writes a second `field:` key,
    pyyaml keeps the last, and the original value is silently lost. An UNTERMINATED flow list
    (no closing bracket anywhere in the atom) is a shape the depth scanner genuinely cannot
    read, so the guard must still raise on it."""
    map_copy = tmp_path / "maturity_map.yaml"
    map_copy.write_text(
        "- id: BROKEN_atom\n"
        "  level_current: 0\n"
        "  evidence: [first.py,\n"
        "    second.py\n"          # <- never closed
    )
    inbox_dir = tmp_path / "atom_status"
    inbox_dir.mkdir()
    _write_inbox(inbox_dir, "BROKEN_atom", 1, "broken")

    with pytest.raises(MergeError, match="refusing to create a duplicate key"):
        merge(map_path=map_copy, inbox_dir=inbox_dir)

    # fail-closed: the map is untouched and the inbox survives for a human to fix
    assert "second.py" in map_copy.read_text()
    assert (inbox_dir / "BROKEN_atom.yaml").exists()
