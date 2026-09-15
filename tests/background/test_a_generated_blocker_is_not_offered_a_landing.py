"""A blocking path a PRODUCER writes must never be handed the landing recipe.

THE DEFECT THIS NAMES (2026-09-09). `origin_reconcile._landing_clause` classified every modified
blocker as "this tree's uncommitted work" and led with `isolate_hunks` + `surgical_land --content`.
On 2026-09-09 the single path holding the shared tree behind origin was `site/data/value_arms.json`,
a publisher's output. Its local bytes were generated at 04:25:38Z and origin's at 05:11:32Z, and
landing the local ones -- the refusal's own first and most detailed advice -- would have
re-published the "IN THE WORLD AS IT IS NOW" headline that origin's commit `77d92e0d1` existed to
delete. The remedy named the one action that undoes another lane's fix.

KEYED TO THE PROPERTY, NOT TO `value_arms.json`. What must hold is that a generated path is never
offered a landing and an authored one still is -- not that one particular file is in the set. The
oracle's membership is allowed to change; the split is not.

THE SECOND INSTANCE, AND WHY ONE ORACLE WAS NOT ENOUGH (2026-09-15). The same defect returned on
`docs/design/orphan_baseline.json` -- `tools/orphan_ratchet.py --freeze` writes it, a photograph of
a scan -- and the split missed it because `generated_artefacts` is keyed to generated TREES and this
is a producer's output inside an AUTHORED one. `_split_generated` now unions that oracle with
`written_artefacts`, which is keyed to the write SITE, and the legs below drive both kinds through
the same property rather than adding a second test about a second file.
"""
from __future__ import annotations

import pytest

from background import origin_reconcile as orc

AUTHORED = "background/origin_reconcile.py"
GENERATED = "site/data/value_arms.json"
# A producer's output in an authored tree: found only by the WRITE-keyed half of the union.
GENERATED_IN_AN_AUTHORED_TREE = "docs/design/orphan_baseline.json"

LANDING_RECIPE = "isolate_hunks.py --survey"


def _clause(paths):
    return orc._landing_clause([{"path": p, "kind": orc.FF_MODIFIED} for p in paths])


def test_the_oracle_supplies_both_sides_so_neither_leg_below_is_vacuous():
    """THE POISON ROUND. Every assertion here is 'X is on one side of a split'; if the oracle
    returned an empty set, or everything, each leg would still pass while measuring nothing. So
    prove the partition is genuinely populated BEFORE trusting any verdict keyed to it."""
    generated, authored, failed = orc._split_generated([GENERATED, AUTHORED])
    assert not failed, "oracle unavailable -- every leg below would be vacuous: {}".format(failed)
    assert generated == [GENERATED], generated
    assert authored == [AUTHORED], authored


def test_a_generated_blocker_is_told_to_revert_and_never_to_land():
    clause = _clause([GENERATED])
    assert "GENERATED path(s)" in clause
    assert "do NOT land them" in clause
    assert "git show HEAD:<path> > <path>" in clause
    # The whole point: the landing recipe must be ABSENT, not merely accompanied.
    assert LANDING_RECIPE not in clause, (
        "a producer's output was offered the landing recipe: {}".format(clause))


def test_an_authored_blocker_still_gets_the_landing_recipe():
    """The narrowing must not be asymmetric. A fix for a false positive that also suppresses the
    true positives is the failure mode this leg exists to catch."""
    clause = _clause([AUTHORED])
    assert LANDING_RECIPE in clause
    assert "GENERATED path(s)" not in clause


def test_a_mixed_set_states_both_steps_and_counts_each_side_separately():
    clause = _clause([GENERATED, AUTHORED])
    assert "1 GENERATED path(s)" in clause
    assert "1 MODIFIED path(s)" in clause
    assert LANDING_RECIPE in clause  # still offered -- but only for the authored one


def test_the_write_keyed_half_of_the_union_supplies_the_authored_tree_case():
    """THE SECOND POISON ROUND, for the half the tree-keyed oracle structurally cannot answer. If
    this path fell out of the write-keyed set the leg below would still pass by classifying it
    authored -- which is the defect, not the control. So prove the membership first."""
    generated, authored, failed = orc._split_generated(
        [GENERATED_IN_AN_AUTHORED_TREE, AUTHORED])
    assert not failed, failed
    assert generated == [GENERATED_IN_AN_AUTHORED_TREE], generated
    assert authored == [AUTHORED], authored


def test_a_producers_output_in_an_authored_tree_is_told_to_revert_and_never_to_land():
    """The 2026-09-15 instance: the one path holding the shared tree behind origin, being advised
    to land a photograph of a run over whatever origin's later freeze recorded."""
    clause = _clause([GENERATED_IN_AN_AUTHORED_TREE])
    assert "do NOT land them" in clause
    assert LANDING_RECIPE not in clause, clause


def test_an_unavailable_oracle_says_so_rather_than_splitting_silently(monkeypatch):
    """FAIL-SOFT IS ONLY HONEST IF IT ANNOUNCES ITSELF. The remedy must not block the tree when the
    oracles die, but an unsplit list that reads exactly like a clean split is how a reader lands a
    generated path believing the question was asked.

    BOTH halves are killed, because killing one now leaves a REAL split running -- a version of
    this leg that patched only `generated_artefacts` would assert 'everything is authored' while
    the other oracle was still answering, and would pass for the wrong reason."""
    import tools.file_scope_generated_paths as oracle

    def _boom():
        raise RuntimeError("map unreadable")

    monkeypatch.setattr(oracle, "generated_artefacts", _boom)
    monkeypatch.setattr(oracle, "written_artefacts", _boom)
    generated, authored, failed = orc._split_generated([GENERATED, AUTHORED])
    assert generated == []
    assert authored == [GENERATED, AUTHORED]  # fail-soft: nothing is blocked
    assert "map unreadable" in failed

    clause = _clause([GENERATED, AUTHORED])
    assert "UNSPLIT" in clause and "could not be asked" in clause


def test_HALF_an_oracle_reports_a_PARTIAL_split_and_not_an_unsplit_one(monkeypatch):
    """The third state two oracles create, which the old two-valued note could not express. A
    reader told 'UNSPLIT' about a half-split list re-checks paths that were already classified and
    trusts the ones that were not -- so the note must say which half is missing, and the split it
    could still make must survive."""
    import tools.file_scope_generated_paths as oracle

    monkeypatch.setattr(oracle, "written_artefacts",
                        lambda root=None: (_ for _ in ()).throw(RuntimeError("write scan died")))
    generated, authored, failed = orc._split_generated(
        [GENERATED, GENERATED_IN_AN_AUTHORED_TREE, AUTHORED])
    assert generated == [GENERATED], "the surviving oracle's split was thrown away: {}".format(
        generated)
    assert GENERATED_IN_AN_AUTHORED_TREE in authored  # only the dead oracle knew this one
    assert "PARTIAL" in failed and "written_artefacts" in failed and "write scan died" in failed
    assert "UNSPLIT" not in failed

    clause = _clause([GENERATED, AUTHORED])
    assert "PARTIAL" in clause


def test_the_unknown_kind_branch_is_still_reachable():
    """The rare branch, asserted to be TAKEABLE and not merely to refuse correctly."""
    clause = orc._landing_clause([{"path": "x", "kind": "FF_SOMETHING_ELSE"}])
    assert "none of these paths is a kind it knows how to name a step for" in clause


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
