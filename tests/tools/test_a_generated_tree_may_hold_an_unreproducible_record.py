#!/usr/bin/env python3
"""R15 proof that a carve-out honoured by ONE of two unioned oracles is not a carve-out.

THE DEFECT IT NAMES (2026-09-15). `WRITTEN_BUT_NOT_REPRODUCIBLE` is the escape hatch for a path a
module rewrites whole that is still nobody's photograph -- the maturity map, the director's canon,
an accumulated ledger spliced and written back. The remedy a consumer applies to a GENERATED path
is `git show HEAD:<path> > <path>`, so a record no run makes again must never be classified
generated. Until 2026-09-15 that list was subtracted from `written_artefacts` ONLY, and it was safe
purely by accident: no member happened to live under a `GENERATED_TREES` prefix, so the tree-keyed
oracle could not produce one however the list grew.

Declaring `("docs", "status")` ended the accident. `docs/status/SEAT_STRETCH_LOG.md` sits inside
that tree and `tools/stretch_log.append` splices ONE hand-written entry in after the header and
writes the file back whole -- the `naive_organ` shape, an append wearing a rewrite's clothes, which
`WRITING_MODE_CHARS` cannot see. The two oracles feed ONE union in
`origin_reconcile._split_generated`, so a path carved out of one and produced by the other arrives
in the union anyway and is offered the revert. The carve-out would have looked applied and done
nothing.

THE SECOND HALF IS THAT THE FIX MUST NOT BUY THAT SAFETY WITH THE GATE. `offends()` decides a
`file_scope` entry by tree PREFIX, so membership in `generated_artefacts` is SUBSUMED and removing
members cannot change `violations()`. That is asserted here over the live oracle rather than
assumed, because a subtraction that DID reach the gate would silently un-refuse a starving atom --
the failure this module's subject exists to catch, arriving through the repair for a different one.

FIXTURES CARRY BOTH SIDES. Each synthetic tree below holds a carved path and an uncarved SIBLING
reached the identical way, so a fixture that reaches nothing cannot pass vacuously -- the sibling
is the control that the door is open before the carved path is asserted shut.
"""
from __future__ import annotations

from pathlib import Path

from tools import file_scope_generated_paths as fs

# The live instance, and the tree that exposed it. Neither is asserted from memory: the real-tree
# legs below prove the log is genuinely write-reached before asserting it is kept out of the union.
STRETCH_LOG = "docs/status/SEAT_STRETCH_LOG.md"
FOURTH_TREE = ("docs", "status")
# The one live `file_scope` the fourth tree refuses, frozen in the same commit that declared it.
FROZEN_BY_THE_FOURTH_TREE = ("OPS3_first_post_ruling_publish", "docs/status/LATEST.md")

# Both paths are named as segment constants AND written, so each is reachable by BOTH oracles --
# which is the only shape that can prove a one-sided carve-out is not a carve-out.
#
# DELIBERATELY UNDER `docs/observability`, NOT THE TREE THAT EXPOSED THIS. The carve-out symmetry is
# a property of two oracles sharing one union, and it holds whichever trees are declared. Keying the
# fixture to `docs/status` coupled these legs to that declaration -- measured, not supposed:
# un-declaring the fourth tree reddened FIVE legs, of which only two were about the declaration. A
# control that goes red for somebody else's change is a control that gets deleted for the wrong
# reason.
LEDGER_MODULE = '''
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
LEDGER = PROJECT / "docs" / "observability" / "accumulated_ledger.md"
PHOTOGRAPH = PROJECT / "docs" / "observability" / "run_snapshot.md"


def record(entry):
    existing = LEDGER.read_text(encoding="utf-8")
    LEDGER.write_text(existing + entry, encoding="utf-8")


def snapshot(rows):
    PHOTOGRAPH.write_text(rows, encoding="utf-8")
'''

CARVED = "docs/observability/accumulated_ledger.md"
UNCARVED_SIBLING = "docs/observability/run_snapshot.md"


def _tree(root: Path) -> Path:
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "ledger_producer.py").write_text(LEDGER_MODULE, encoding="utf-8")
    return root


def test_the_fixture_reaches_both_oracles_before_anything_is_carved(tmp_path):
    """THE CONTROL OVER THE WHOLE PARTITION. A fixture whose paths reach NEITHER oracle passes
    every assertion below for the wrong reason, so the door is proven open first. Both paths must
    arrive through both doors -- that is what makes the next test's subtraction meaningful."""
    _tree(tmp_path)
    generated = fs.generated_artefacts(root=tmp_path)
    written = fs._write_reached_paths(root=tmp_path)
    for path in (CARVED, UNCARVED_SIBLING):
        assert path in generated, f"{path} did not reach the TREE-keyed oracle"
        assert path in written, f"{path} did not reach the WRITE-keyed oracle"


def test_a_carve_out_honoured_by_one_oracle_only_is_not_a_carve_out(tmp_path, monkeypatch):
    """THE DEFECT. Carving a path out of `written_artefacts` alone leaves the TREE-keyed oracle
    producing it, and the union is what the reconciler reads -- so the path is still offered a
    revert. Restoring the one-sided subtraction (dropping `found -= WRITTEN_BUT_NOT_REPRODUCIBLE`
    from `generated_artefacts`) makes the carved path reappear in `generated` and fails this."""
    _tree(tmp_path)
    monkeypatch.setattr(fs, "WRITTEN_BUT_NOT_REPRODUCIBLE", frozenset({CARVED}))

    generated = fs.generated_artefacts(root=tmp_path)
    written = fs.written_artefacts(root=tmp_path)
    union = generated | written

    assert CARVED not in generated, "the TREE-keyed oracle still produces the carved record"
    assert CARVED not in written
    assert CARVED not in union, (
        "a record no run reproduces is in the union the reconciler reads, so its refusal will "
        "advise `git show HEAD:<path> > <path>` and discard it")
    # The sibling is reached the identical way and is NOT carved, so this cannot be passing
    # because the fixture stopped reaching the oracle.
    assert UNCARVED_SIBLING in union


def test_a_carve_out_cannot_un_refuse_a_starving_file_scope():
    """THE FIX MUST NOT REACH THE GATE. Every member the tree-keyed oracle can return sits under a
    `GENERATED_TREES` prefix, so `offends()` answers True from the prefix test alone and membership
    is dead weight for the gate. Keyed to that PROPERTY rather than to today's count: it stays green
    as the oracle grows and goes red the moment a member escapes the prefix set, which is the only
    state in which a carve-out could silently un-refuse an atom."""
    generated = fs.generated_artefacts()
    escaping = sorted(s for s in generated if not fs.offends(s, set()))
    assert escaping == [], (
        f"{len(escaping)} oracle members are NOT caught by the prefix test, so subtracting them "
        f"from the oracle WOULD move the commit gate: {escaping[:5]}")


def test_carving_the_live_instances_tree_mate_leaves_the_gate_verdict_standing(monkeypatch):
    """The same property driven through the real consumer instead of the predicate. `LATEST.md` is
    the one live `file_scope` the fourth tree refuses; carving it out of the oracle entirely must
    leave that refusal exactly where it was."""
    monkeypatch.setattr(fs, "WRITTEN_BUT_NOT_REPRODUCIBLE",
                        fs.WRITTEN_BUT_NOT_REPRODUCIBLE | {FROZEN_BY_THE_FOURTH_TREE[1]})
    assert FROZEN_BY_THE_FOURTH_TREE in set(fs.violations()), (
        "removing a path from the oracle removed the violation that path was proving, so the "
        "carve-out is reaching the gate and an atom that starves is no longer refused")


def test_the_fourth_generated_tree_refuses_every_spelling_of_a_scope_under_it():
    """The declaration is the point of the change and `offends` names three live spellings. A
    declaration nobody can reach refuses nothing, so all three are driven."""
    assert FOURTH_TREE in fs.GENERATED_TREES, "the fourth tree is not declared"
    for spelling in ("docs/status", "docs/status/", "docs/status/LATEST.md"):
        assert fs.offends(spelling, set()), f"a file_scope spelled `{spelling}` is not refused"
    # ...and the neighbour DECLINED on the evidence stays un-refused, so this is a declaration and
    # not a blanket over `docs/`.
    assert not fs.offends("docs/reports/ANNUAL_REPORT.md", set())


def test_the_stretch_log_is_write_reached_and_still_kept_out_of_the_union():
    """THE REAL-TREE LEG, and the one that proves the carve-out is load-bearing rather than a line
    about a path nothing reaches. `stretch_log.append` genuinely satisfies the write-site test --
    that is asserted first -- and the union must still not contain it."""
    assert STRETCH_LOG in fs._write_reached_paths(), (
        "the stretch log is not write-reached at all, so its carve-out is proving nothing and "
        "this control cannot fail")
    union = fs.generated_artefacts() | fs.written_artefacts()
    assert STRETCH_LOG not in union, (
        "the seat's own stretch log is classified generated, so the reconciler will advise "
        "reverting it and the reasoning behind a stretch is lost")


def test_the_freeze_was_re_measured_against_the_wider_prefix_set():
    """A `GENERATED_TREES` addition moves the PREFIX set, so every `file_scope` under the new tree
    starts offending at once. A freeze measured against the narrower set reads STALE and refuses
    EVERY lane's commit, not just the lane that widened it."""
    assert FROZEN_BY_THE_FOURTH_TREE in fs.FROZEN
    assert FROZEN_BY_THE_FOURTH_TREE in set(fs.violations()), (
        "the frozen pair is not live, so `gate_violations` will report it as a STALE FREEZE")
    assert fs.gate_violations() == []
