"""RUNG 1c's product-priority exemption, and the starvation floor beside it.

Director, 2026-09-05: *"I changed the dial, and the dial isn't what chooses ... Fix the selector so
R1 and R2 can win against machinery work, not just against other atoms."* The dial had moved eleven
atoms to 45 and the machine then ran ten hours and 66 commits with none of them touched, because a
BLOCKING finding in lane W2_customer_generator removed the three core R1 atoms from candidacy before
any weighting happened.

Every test here names the defect it exists to catch.
"""
from __future__ import annotations

import pytest

from background import supervisor as s


def _atom(atom_id: str, lane: str, dial: int) -> dict:
    return {"id": atom_id, "lane": lane, "dial_inherited": dial}


@pytest.fixture
def two_atoms(monkeypatch):
    """One product-priority atom and one ordinary atom, both in the SAME blocked lane.

    Same lane deliberately: it is the only arrangement in which the exemption and the exclusion can
    be told apart. If they sat in different lanes, a filter that ignored the dial entirely would
    still produce the expected answer.
    """
    product = _atom("PB4_engagement", "W2_customer_generator", s.PRODUCT_PRIORITY_DIAL_FLOOR)
    ordinary = _atom("H9_some_harness", "W2_customer_generator", 3)
    monkeypatch.setattr(s, "_product_priority_ids", lambda: frozenset({product["id"]}))
    return product, ordinary


def test_a_blocking_finding_cannot_exclude_what_the_director_ranked_first(two_atoms):
    """THE DEFECT: EP17, PB4 and PB5 were dropped from every draw for a day, by lane."""
    product, ordinary = two_atoms

    kept = s._drop_lane_blocked([product, ordinary], frozenset({"W2_customer_generator"}))

    assert product in kept, "a product-priority atom must survive its lane being blocked"


def test_a_blocking_finding_still_excludes_ordinary_same_lane_work(two_atoms):
    """The other branch. Without this the exemption could be a filter that drops nothing at all,
    which would pass the test above while quietly repealing OPS12 clause 3 for the whole map."""
    product, ordinary = two_atoms

    kept = s._drop_lane_blocked([product, ordinary], frozenset({"W2_customer_generator"}))

    assert ordinary not in kept, "the lane exclusion must still apply to ordinary feature work"


def test_an_unblocked_lane_keeps_both_so_the_exclusion_is_not_always_on(two_atoms):
    """Reachability over the whole partition: with no lane blocked, nothing is dropped."""
    product, ordinary = two_atoms

    kept = s._drop_lane_blocked([product, ordinary], frozenset())

    assert kept == [product, ordinary]


def test_an_unreadable_map_fails_toward_the_exclusion_not_toward_exempting_everything(monkeypatch):
    """FAIL-CLOSED on the exemption. The harmful direction is exempting the entire map from a
    blocking finding because the map could not be parsed."""
    def boom(*_a, **_k):
        raise RuntimeError("map unreadable")
    monkeypatch.setattr("tools.maturity_map_store.load_live_atoms", boom)

    assert s._product_priority_ids() == frozenset()

    product = _atom("PB4_engagement", "W2_customer_generator", 45)
    assert s._drop_lane_blocked([product], frozenset({"W2_customer_generator"})) == []


def test_the_stretch_counts_commits_that_name_the_atom_not_ones_that_touch_its_files(monkeypatch):
    """THE DESIGN DECISION, and the one a scope-keyed detector gets wrong.

    Measured when this was written: 148 commits in twenty hours, ZERO naming a product-priority
    atom, and 123 file-touches inside one's declared scope. The R-set's scopes include `tools/`,
    `docs/design/` and `simulation/` -- what machinery work touches all day -- and three of the
    eleven declare no scope at all. A scope detector would have read "progress" continuously.
    """
    monkeypatch.setattr(s, "_product_priority_ids", lambda: frozenset({"PB4_engagement"}))
    # Commits that touch simulation/population_draw.py -- PB4's own file_scope -- but never name it.
    log = "".join("fix a thing in simulation/population_draw.py\x00body\x1e" for _ in range(40))
    monkeypatch.setattr(s.subprocess, "run",
                        lambda *a, **k: type("R", (), {"stdout": log})())

    stretch, starved = s._product_starvation_stretch()

    assert stretch == 40, "touching the atom's files is not naming the atom"
    assert starved is True


def test_naming_the_atom_resets_the_stretch_so_the_floor_drains(monkeypatch):
    """A floor that cannot be cleared by doing the work is a floor that fires forever."""
    monkeypatch.setattr(s, "_product_priority_ids", lambda: frozenset({"PB4_engagement"}))
    log = ("machinery\x00body\x1e" * 3) + "build PB4_engagement gate\x00body\x1e" + ("old\x00b\x1e" * 90)
    monkeypatch.setattr(s.subprocess, "run",
                        lambda *a, **k: type("R", (), {"stdout": log})())

    stretch, starved = s._product_starvation_stretch()

    assert stretch == 3
    assert starved is False


def test_an_unmeasurable_stretch_raises_the_floor_rather_than_lowering_it(monkeypatch):
    """THE DEFECT THIS SHIPPED WITH FOR ONE RUN: a NameError in the git call made the function
    return (0, False) -- "no starvation" -- on every single call. The floor was unreachable,
    silently, in exactly the way the mechanism exists to prevent."""
    monkeypatch.setattr(s, "_product_priority_ids", lambda: frozenset({"PB4_engagement"}))
    def boom(*_a, **_k):
        raise RuntimeError("git unavailable")
    monkeypatch.setattr(s.subprocess, "run", boom)

    stretch, starved = s._product_starvation_stretch()

    assert starved is True, "an unmeasurable stretch must report AS starvation"
    assert stretch == -1, "and must be distinguishable from a real measurement of zero"


def test_a_director_canon_is_recognised_by_the_one_rung_that_surfaces_his_documents(tmp_path):
    """THE DEFECT THAT COST THE DIRECTOR TWO CONSOLE PASTES.

    `_unconsumed_director_ruling_or_steer` is the single mechanism that puts a director document
    ahead of self-filed work, and it knew the words RULING and STEER and not the word CANON. Both
    `DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04` and `..._PRODUCT_AND_MACHINERY_2026-09-05` were
    therefore invisible to it. Nothing was broken and nothing logged a refusal: the mechanism
    existed, was tested, and was mute.

    Keyed to BOTH carriers, because they are separate code paths and widening one while leaving the
    other narrow is how this defect got here.
    """
    (tmp_path / "DIRECTOR_CANON_SOMETHING_2026-09-05.md").write_text(
        "# [DIRECTOR-CANON] - a standing rule\n\n**Severity:** LATENT\n")
    assert s._unconsumed_director_ruling_or_steer(tmp_path) is True

    # by content header alone, with a filename that carries no convention at all
    other = tmp_path / "DIRECTOR_CANON_SOMETHING_2026-09-05.md"
    other.unlink()
    (tmp_path / "zzz_untitled.md").write_text("# [DIRECTOR-CANON] - a standing rule\n")
    assert s._unconsumed_director_ruling_or_steer(tmp_path) is True


def test_an_ordinary_staged_finding_does_not_read_as_a_director_document(tmp_path):
    """The other branch: without it the predicate could return True for anything in the root, which
    would suppress every draw forever and pass the test above."""
    (tmp_path / "SEAT_FINDING_SOMETHING_2026-09-05.md").write_text(
        "**Severity:** BLOCKING\n\n# a finding this seat filed itself\n")
    assert s._unconsumed_director_ruling_or_steer(tmp_path) is False


def test_both_carriers_share_one_prefix_tuple_so_a_widened_vocabulary_cannot_stay_narrow(tmp_path):
    """The draw suppressor and the mint source carried the same tuple as two separate literals.
    This asserts they now read the same object, which is what stops the next word being added to
    one of them only."""
    assert "DIRECTOR_CANON_" in s._DIRECTOR_DOC_PREFIXES
    (tmp_path / "DIRECTOR_CANON_X_2026-09-05.md").write_text("# [DIRECTOR-CANON]\n")
    assert s._unconsumed_director_ruling_or_steer(tmp_path) is True
    assert s._is_ruling_or_steer("DIRECTOR_CANON_X_2026-09-05.md", "") is True


def test_the_priority_zero_rungs_are_still_above_product_and_are_the_essential_test(monkeypatch):
    """The director's bar for machinery: it earns precedence if a reader's page is broken or the
    machine cannot land work. Those are exactly the three priority-zero rungs, so THEY still
    outrank product work -- the exemption only reaches rung 1c, which by construction is neither."""
    monkeypatch.setattr(s, "_publish_gate_wedge_active", lambda: "wedged")
    assert s._priority_zero_active() is True
