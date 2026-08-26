"""R15 proof for AO6 -- `tools/consolidation_rhythm.py`.

Two things must be true of this control, and neither is provable by the suite being green:

  1. **Every guard FIRES on its own named defect.** Proven by SOURCE MUTATION (`test_mutations`):
     each guard is broken alone in a copy of the real module and something must go red.
  2. **The R12 inversion holds both ways.** This measures whether the consolidation pass HAPPENED;
     it must NEVER score how much was pruned. A pass that deliberately keeps everything is rc 0,
     and a tree with a larger orphan census than yesterday is rc 0. Pinned in both directions,
     because the moment a count could turn the build red, the cheapest move available to any turn
     is to delete modules to get green -- goal-seeking the metric, which is the defect R12 names.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

import tools.consolidation_rhythm as cr
from tools import maturity_map_store as map_store  # noqa: E402

SOURCE = Path(cr.__file__)


# ── fixtures ────────────────────────────────────────────────────────────────────────────────
def atom(aid: str, epoch: int, current: int, target: int) -> dict:
    return {"id": aid, "epoch": epoch, "level_current": current, "level_target": target}


CLOSED_MAP = [atom("A", 1, 2, 2), atom("B", 1, 3, 2)]
OPEN_MAP = [atom("A", 1, 2, 2), atom("B", 1, 0, 2)]


def census(paths) -> dict:
    return {"modules_scanned": 100, "orphan_paths": sorted(paths)}


def baseline(paths=()) -> dict:
    return {"kind": "baseline", "epoch": None, "census": census(paths), "dispositions": []}


def passing(epoch=1, dispositions=(), paths=()) -> dict:
    return {"kind": "pass", "epoch": epoch, "census": census(paths),
            "dispositions": list(dispositions)}


def kept(path: str) -> dict:
    return {"path": path, "disposition": "kept", "reason": "still the only reader of the feed"}


def run(records, atoms, orphan_paths, root: Path):
    return cr.check(list(records), list(atoms), set(orphan_paths), root)


# ── what an epoch close IS ──────────────────────────────────────────────────────────────────
def test_epoch_is_closed_only_when_every_atom_reached_target() -> None:
    assert cr.closed_epochs(CLOSED_MAP) == {1}
    assert cr.closed_epochs(OPEN_MAP) == set()


def test_an_epoch_with_no_atoms_is_never_closed() -> None:
    """`all([])` is True, so an absent epoch must not read as closed.

    The defence is structural, not a guard: epochs are DERIVED from the atoms, so an epoch nobody
    has an atom for is never a key. A defensive `if members and ...` was written here first and its
    own mutation proved it unreachable -- breaking it changed nothing -- so it was removed rather
    than kept as a guard that cannot fail. This test pins the property the structure provides."""
    assert cr.closed_epochs([atom("A", 1, 2, 2)]) == {1}
    assert 7 not in cr.closed_epochs([atom("A", 1, 2, 2)])
    assert cr.closed_epochs([]) == set()


def test_atoms_without_an_epoch_do_not_invent_one() -> None:
    assert cr.closed_epochs([{"id": "X", "level_current": 1, "level_target": 1}]) == set()


# ── G3: a closed epoch owes a record ─────────────────────────────────────────────────────────
def test_g3_closed_epoch_without_a_pass_record_fails(tmp_path: Path) -> None:
    failures, report = run([baseline()], CLOSED_MAP, set(), tmp_path)
    assert any(f.startswith("G3") for f in failures)
    assert report["epochs_closed"] == [1]


def test_g3_is_satisfied_by_a_pass_record(tmp_path: Path) -> None:
    failures, _ = run([baseline(), passing(1)], CLOSED_MAP, set(), tmp_path)
    assert not failures


def test_g3_does_not_fire_while_the_epoch_is_still_open(tmp_path: Path) -> None:
    failures, report = run([baseline()], OPEN_MAP, set(), tmp_path)
    assert not failures
    assert report["epochs_closed"] == []


# ── G5: the tree contradicts a false claim ───────────────────────────────────────────────────
def test_g5_retired_but_the_file_is_still_there(tmp_path: Path) -> None:
    (tmp_path / "ghost.py").write_text("x = 1", encoding="utf-8")
    record = passing(1, [{"path": "ghost.py", "disposition": "retired"}])
    failures, _ = run([baseline(), record], CLOSED_MAP, set(), tmp_path)
    assert any("RETIRED" in f for f in failures)


def test_g5_retired_is_honest_when_the_file_is_gone(tmp_path: Path) -> None:
    record = passing(1, [{"path": "ghost.py", "disposition": "retired"}])
    failures, _ = run([baseline(), record], CLOSED_MAP, set(), tmp_path)
    assert not failures


def test_g5_wired_but_the_index_still_finds_no_caller(tmp_path: Path) -> None:
    (tmp_path / "lonely.py").write_text("x = 1", encoding="utf-8")
    record = passing(1, [{"path": "lonely.py", "disposition": "wired"}])
    failures, _ = run([baseline(), record], CLOSED_MAP, {"lonely.py"}, tmp_path)
    assert any("WIRED" in f for f in failures)


def test_g5_wired_is_honest_once_the_module_has_a_caller(tmp_path: Path) -> None:
    (tmp_path / "lonely.py").write_text("x = 1", encoding="utf-8")
    record = passing(1, [{"path": "lonely.py", "disposition": "wired"}])
    failures, _ = run([baseline(), record], CLOSED_MAP, set(), tmp_path)
    assert not failures


def test_g5_a_module_wired_then_later_deleted_does_not_wedge(tmp_path: Path) -> None:
    """A stable claim: `wired` is contradicted only by the module still existing AND still orphaned.

    Without this, ordinary later deletion of a module dispositioned two epochs ago would turn the
    gate red forever with no defect present -- a control that can only fail, which wedges."""
    record = passing(1, [{"path": "gone.py", "disposition": "wired"}])
    failures, _ = run([baseline(), record], CLOSED_MAP, {"gone.py"}, tmp_path)
    assert not failures


# ── G6: coverage, grounded in the tree rather than in the ledger ─────────────────────────────
def test_g6_an_orphan_born_after_the_baseline_blocks_the_close(tmp_path: Path) -> None:
    failures, _ = run([baseline(["old.py"]), passing(1)], CLOSED_MAP,
                      {"old.py", "new.py"}, tmp_path)
    assert any(f.startswith("G6") and "new.py" in f for f in failures)


def test_g6_the_baseline_forgives_the_historical_pile(tmp_path: Path) -> None:
    failures, report = run([baseline(["old.py"]), passing(1)], CLOSED_MAP, {"old.py"}, tmp_path)
    assert not failures
    assert report["orphans_forgiven_at_baseline"] == 1


def test_g6_a_disposition_accounts_for_a_new_orphan(tmp_path: Path) -> None:
    (tmp_path / "new.py").write_text("x = 1", encoding="utf-8")
    record = passing(1, [kept("new.py")])
    failures, _ = run([baseline(["old.py"]), record], CLOSED_MAP, {"old.py", "new.py"}, tmp_path)
    assert not failures


def test_g6_is_reported_not_applicable_rather_than_passed(tmp_path: Path) -> None:
    """The honesty that keeps a dormant boundary from reading as a verified one."""
    failures, report = run([baseline()], OPEN_MAP, {"new.py"}, tmp_path)
    assert not failures
    assert report["coverage_rule"] == "NOT APPLICABLE (no epoch is closed)"
    assert report["orphans_unaccounted"] == ["new.py"]


def test_g6_a_forged_empty_census_buys_nothing(tmp_path: Path) -> None:
    """A hand-appended pass record claiming an empty census cannot forgive anything.

    Only the single baseline grants forgiveness, and the orphan set is read from the TREE. This is
    the anti-tautology property: the ledger cannot talk itself out of a coverage failure."""
    forged = passing(1, [], paths=[])
    failures, _ = run([baseline(["old.py"]), forged], CLOSED_MAP, {"old.py", "new.py"}, tmp_path)
    assert any(f.startswith("G6") for f in failures)


# ── G8: the baseline is granted once ─────────────────────────────────────────────────────────
def test_g8_a_second_baseline_fails(tmp_path: Path) -> None:
    failures, _ = run([baseline(), baseline()], OPEN_MAP, set(), tmp_path)
    assert any(f.startswith("G8") for f in failures)


def test_g8_record_refuses_to_write_a_second_baseline(tmp_path: Path, monkeypatch) -> None:
    ledger = tmp_path / cr.LEDGER_REL
    cr.append_record(baseline(), ledger)
    monkeypatch.setattr(cr, "live_orphan_paths", lambda root=None: (set(), 10))
    args = type("A", (), {"baseline": True, "epoch": None, "dispositions": None})()
    assert cr._do_record(args, tmp_path, ledger) == 2


def test_the_live_ledger_holds_exactly_one_baseline() -> None:
    records = cr.read_ledger(cr.ROOT / cr.LEDGER_REL)
    assert len([r for r in records if r["kind"] == "baseline"]) == 1


# ── R12: the inversion, pinned BOTH ways ─────────────────────────────────────────────────────
def test_r12_a_pass_that_prunes_nothing_is_green(tmp_path: Path) -> None:
    """Every orphan deliberately KEPT with a reason. The pass happened; nothing was pruned; rc 0."""
    for name in ("a.py", "b.py", "c.py"):
        (tmp_path / name).write_text("x = 1", encoding="utf-8")
    record = passing(1, [kept("a.py"), kept("b.py"), kept("c.py")])
    failures, _ = run([baseline(), record], CLOSED_MAP, {"a.py", "b.py", "c.py"}, tmp_path)
    assert not failures


def test_r12_a_growing_orphan_census_is_not_a_failure(tmp_path: Path) -> None:
    """5000 forgiven orphans and zero pruning: still green. There is no count that turns this red.

    If there were, the cheapest route to green would be deleting modules -- the metric editing the
    territory. The count is a DIAGNOSTIC, reported in full and never gated."""
    pile = {"m%d.py" % i for i in range(5000)}
    failures, report = run([baseline(pile), passing(1)], CLOSED_MAP, pile, tmp_path)
    assert not failures
    assert report["orphans_live"] == 5000


def test_kept_repeats_are_reported_never_gated(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1", encoding="utf-8")
    records = [baseline(["a.py"]), passing(1, [kept("a.py")]), passing(2, [kept("a.py")])]
    failures, report = run(records, CLOSED_MAP, {"a.py"}, tmp_path)
    assert not failures
    assert report["kept_repeats"] == ["a.py"]


# ── G4 / fail-silent: an unreadable or malformed record is a REFUSAL, never a skip ────────────
def test_an_unparseable_ledger_line_raises() -> None:
    with pytest.raises(cr.ConsolidationUnavailable, match="unparseable"):
        cr.parse_ledger('{"kind": "pass"\nnot json at all\n')


def test_an_unknown_disposition_word_raises() -> None:
    line = json.dumps(passing(1, [{"path": "x.py", "disposition": "skip"}]))
    with pytest.raises(cr.ConsolidationUnavailable, match="no skip disposition"):
        cr.parse_ledger(line)


def test_kept_without_a_reason_raises() -> None:
    line = json.dumps(passing(1, [{"path": "x.py", "disposition": "kept", "reason": "tbd"}]))
    with pytest.raises(cr.ConsolidationUnavailable, match="without a reason"):
        cr.parse_ledger(line)


def test_a_record_with_no_census_raises() -> None:
    with pytest.raises(cr.ConsolidationUnavailable, match="census"):
        cr.parse_ledger(json.dumps({"kind": "pass", "epoch": 1}))


def test_a_pass_record_must_name_its_epoch() -> None:
    with pytest.raises(cr.ConsolidationUnavailable, match="must name the epoch"):
        cr.parse_ledger(json.dumps({"kind": "pass", "epoch": None, "census": census([])}))


def test_append_refuses_to_write_what_the_reader_would_refuse(tmp_path: Path) -> None:
    with pytest.raises(cr.ConsolidationUnavailable):
        cr.append_record({"kind": "pass", "epoch": 1}, tmp_path / "l.jsonl")


# ── vacuity: 0 scanned and 0 findings are opposite facts ─────────────────────────────────────
def test_an_empty_map_raises_rather_than_passing() -> None:
    with pytest.raises(cr.ConsolidationUnavailable, match="0 atoms"):
        cr.atoms_from_map("epochs: []\n")


def test_an_unparseable_map_raises() -> None:
    with pytest.raises(cr.ConsolidationUnavailable, match="unparseable"):
        cr.atoms_from_map("a: [unclosed\n")


def test_an_index_scanning_nothing_raises(monkeypatch) -> None:
    monkeypatch.setattr(cr, "build_rows", lambda root=None: [])
    with pytest.raises(cr.ConsolidationUnavailable, match="0 modules"):
        cr.live_orphan_paths(cr.ROOT)


def test_an_unavailable_index_raises(monkeypatch) -> None:
    def boom(root=None):
        raise RuntimeError("index broke")
    monkeypatch.setattr(cr, "build_rows", boom)
    with pytest.raises(cr.ConsolidationUnavailable, match="unavailable"):
        cr.live_orphan_paths(cr.ROOT)


def test_the_live_map_still_yields_atoms() -> None:
    """Pins the parser against the REAL map: a schema change must not silently empty the scan."""
    # BOTH halves (2026-08-26): an epoch closes across the whole map, and reading the drawn
    # half alone would have made this sanity check pass on 74 atoms instead of 298.
    atoms = cr.atoms_from_map(map_store.map_text(cr.ROOT / cr.MAP_REL))
    assert len(atoms) > 100


# ── the pre-commit gate ──────────────────────────────────────────────────────────────────────
def _wire_gate(monkeypatch, staged, blobs: dict) -> None:
    monkeypatch.setattr(cr, "_staged_paths", lambda root: set(staged))
    monkeypatch.setattr(cr, "_git_show", lambda root, ref: blobs.get(ref))


def _map_yaml(atoms) -> str:
    import yaml
    return yaml.safe_dump({"atoms": atoms})


def test_gate_ignores_a_commit_that_does_not_touch_the_map(monkeypatch, tmp_path: Path) -> None:
    _wire_gate(monkeypatch, set(), {})
    code, lines = cr.gate(tmp_path)
    assert code == 0 and "not staged" in lines[0]


def test_gate_refuses_an_epoch_closing_without_a_record(monkeypatch, tmp_path: Path) -> None:
    _wire_gate(monkeypatch, {cr.MAP_REL}, {
        ":" + cr.MAP_REL: _map_yaml(CLOSED_MAP),
        "HEAD:" + cr.MAP_REL: _map_yaml(OPEN_MAP),
    })
    code, lines = cr.gate(tmp_path)
    assert code == 2 and "COMMIT REFUSED" in lines[0]


def test_gate_allows_the_same_close_once_the_record_is_committed(monkeypatch, tmp_path: Path) -> None:
    _wire_gate(monkeypatch, {cr.MAP_REL, cr.LEDGER_REL}, {
        ":" + cr.MAP_REL: _map_yaml(CLOSED_MAP),
        "HEAD:" + cr.MAP_REL: _map_yaml(OPEN_MAP),
        ":" + cr.LEDGER_REL: json.dumps(passing(1)),
    })
    code, _ = cr.gate(tmp_path)
    assert code == 0


def test_gate_ignores_a_map_edit_that_closes_nothing(monkeypatch, tmp_path: Path) -> None:
    _wire_gate(monkeypatch, {cr.MAP_REL}, {
        ":" + cr.MAP_REL: _map_yaml(OPEN_MAP),
        "HEAD:" + cr.MAP_REL: _map_yaml(OPEN_MAP),
    })
    code, lines = cr.gate(tmp_path)
    assert code == 0 and "no epoch closes" in lines[0]


def test_gate_does_not_re_charge_an_already_closed_epoch(monkeypatch, tmp_path: Path) -> None:
    """Only the transition open->closed is a boundary. Charging every later commit would make the
    gate fire constantly, and a gate that fires constantly is one people learn to route around."""
    _wire_gate(monkeypatch, {cr.MAP_REL}, {
        ":" + cr.MAP_REL: _map_yaml(CLOSED_MAP),
        "HEAD:" + cr.MAP_REL: _map_yaml(CLOSED_MAP),
    })
    assert cr.gate(tmp_path)[0] == 0


def test_gate_refuses_a_record_that_was_never_staged(monkeypatch, tmp_path: Path) -> None:
    """The record must be COMMITTED. Present only in the worktree, it would vanish from history."""
    (tmp_path / cr.LEDGER_REL).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / cr.LEDGER_REL).write_text(json.dumps(passing(1)) + "\n", encoding="utf-8")
    _wire_gate(monkeypatch, {cr.MAP_REL}, {
        ":" + cr.MAP_REL: _map_yaml(CLOSED_MAP),
        "HEAD:" + cr.MAP_REL: _map_yaml(OPEN_MAP),
    })
    assert cr.gate(tmp_path)[0] == 2


def test_gate_refuses_an_unreadable_staged_map(monkeypatch, tmp_path: Path) -> None:
    _wire_gate(monkeypatch, {cr.MAP_REL}, {})
    code, lines = cr.gate(tmp_path)
    assert code == 2 and "fail-closed" in lines[0]


def test_gate_treats_a_missing_head_map_as_closing_everything(monkeypatch, tmp_path: Path) -> None:
    _wire_gate(monkeypatch, {cr.MAP_REL}, {":" + cr.MAP_REL: _map_yaml(CLOSED_MAP)})
    assert cr.gate(tmp_path)[0] == 2


def test_the_gate_is_wired_into_pre_commit() -> None:
    """A control nothing calls is not a control (the orphan class this atom exists to prune)."""
    hook = (cr.ROOT / "tools" / "git-hooks" / "pre-commit").read_text(encoding="utf-8")
    assert "consolidation_rhythm.py --gate" in hook


# ── R15: every guard broken at source, one at a time ─────────────────────────────────────────
def _probe_g3(m):
    return any(f.startswith("G3") for f in m.check([baseline()], CLOSED_MAP, set(), Path("/tmp"))[0])


def _probe_g5_retired(m, root: Path):
    record = passing(1, [{"path": "ghost.py", "disposition": "retired"}])
    return any("RETIRED" in f for f in m.check([baseline(), record], CLOSED_MAP, set(), root)[0])


def _probe_g5_wired(m, root: Path):
    record = passing(1, [{"path": "lonely.py", "disposition": "wired"}])
    return any("WIRED" in f for f in
               m.check([baseline(), record], CLOSED_MAP, {"lonely.py"}, root)[0])


def _probe_g6(m):
    return any(f.startswith("G6") for f in
               m.check([baseline(["old.py"]), passing(1)], CLOSED_MAP,
                       {"old.py", "new.py"}, Path("/tmp"))[0])


def _probe_g6_boundary(m):
    """G6 must NOT fire while the epoch is open -- the guard that keeps it a boundary duty."""
    return not m.check([baseline()], OPEN_MAP, {"new.py"}, Path("/tmp"))[0]


def _probe_g8(m):
    return any(f.startswith("G8") for f in
               m.check([baseline(), baseline()], OPEN_MAP, set(), Path("/tmp"))[0])


def _probe_kept_reason(m):
    line = json.dumps(passing(1, [{"path": "x.py", "disposition": "kept", "reason": "tbd"}]))
    try:
        m.parse_ledger(line)
        return False
    except m.ConsolidationUnavailable:
        return True


def _probe_vacuity(m):
    try:
        m.atoms_from_map("epochs: []\n")
        return False
    except m.ConsolidationUnavailable:
        return True


MUTATIONS = [
    ("G3 closed-epoch-owes-a-record", "for epoch in sorted(closed - recorded, key=str):",
     "for epoch in sorted(set() - recorded, key=str):", _probe_g3),
    ("G5 retired claim", "if verdict == RETIRED and exists:", "if False:", None),
    ("G5 wired claim", "elif verdict == WIRED and exists and path in orphan_paths:",
     "elif False:", None),
    ("G6 coverage", "if closed and unaccounted:", "if False:", _probe_g6),
    ("G6 stays a boundary duty", "if closed and unaccounted:", "if unaccounted:", _probe_g6_boundary),
    ("G8 one baseline only", "if len(baselines) > 1:", "if False:", _probe_g8),
    ("kept needs a reason", "if len(reason.strip()) < MIN_REASON_CHARS:", "if False:",
     _probe_kept_reason),
    ("vacuity guard on the map", "if not found:", "if False:", _probe_vacuity),
    # A tenth mutation ("an empty epoch is not closed", breaking `if members and all(`) was written
    # and DELETED WITH ITS GUARD: nothing went red, because the guard was unreachable from the only
    # path that builds `by_epoch`. Recorded here so the removal reads as a mutation finding rather
    # than as a mutation someone quietly dropped for being inconvenient.
]


def _load_mutant(tmp_path: Path, old: str, new: str, tag: str):
    src = SOURCE.read_text(encoding="utf-8")
    assert old in src, "mutation target vanished from the source: %s" % tag
    path = tmp_path / ("mutant_%s.py" % tag)
    path.write_text(src.replace(old, new, 1), encoding="utf-8")
    spec = importlib.util.spec_from_file_location("cr_mutant_%s" % tag, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name,old,new,probe", MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_mutations(tmp_path: Path, name: str, old: str, new: str, probe) -> None:
    """Each guard, broken alone in a copy of the real source, must stop detecting its own defect.

    The probe holds on the REAL module and must FAIL on the mutant. A probe true both ways is a
    test pinning nothing -- which is the shape R15 rules worse than having no control at all."""
    tree = tmp_path / "tree"
    tree.mkdir()
    if probe is None:  # the two G5 probes need real files on disk to be contradicted by
        (tree / "ghost.py").write_text("x = 1", encoding="utf-8")
        (tree / "lonely.py").write_text("x = 1", encoding="utf-8")
        probe = _probe_g5_retired if "retired" in name else _probe_g5_wired
        probe = (lambda p: lambda m: p(m, tree))(probe)

    assert probe(cr), "%s: probe does not hold on the real module -- the test is wrong" % name
    mutant = _load_mutant(tmp_path, old, new, name.split()[0].lower().replace("-", "_"))
    assert not probe(mutant), (
        "%s: the guard was broken at source and NOTHING went red -- this guard cannot fail, "
        "which R15 rules worse than having no guard at all" % name)
