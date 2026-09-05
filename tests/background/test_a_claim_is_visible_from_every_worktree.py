"""A claim made in one tree must be READABLE from another. It was not, and the refusal blamed a sweep.

THE DEFECT (measured 2026-09-05 05:46Z, from `/var/tmp/se-seat-executor`).
`delivery_lane.CLAIMS_FILE` and `seat_work_in_hand.CLAIMS_FILE` resolved against `PROJECT_DIR` --
the tree the module file sits in. The executor puts an autonomous turn in an isolated worktree and
tells it that `delivery_lane --landed <id>` is *what the turn is judged on*; from that worktree the
call could only ever bind nothing, because the claim lives in the shared tree's copy and
`.gitignore:26` means no commit can carry it across either.

    /var/tmp/se-seat-executor/docs/observability/.delivery_lane_claims.json   {}
    /home/rich/synthetic-enterprise/docs/observability/…                      the claim, 1752s from expiry

So work landed on `origin/main` correctly, was logged LANDED NOTHING, and the item was re-offered
to a fresh seat with no memory of the first -- which lands it again.

WHY THE OBVIOUS CONTROL WOULD BE A TAUTOLOGY, and it is the finding's own words: keying this to
`CLAIMS_FILE == <some path>` passes on today's answer and says nothing about whether a *linked*
worktree can see a *main* worktree's claim. That is the property, so the tests below build two
directories and prove the read CROSSES. Full write-up: `docs/staging/done/SEAT_FINDING_THE_BINDING_
THE_TURN_IS_JUDGED_ON_READS_A_STORE_THE_ISOLATED_WORKTREE_ALWAYS_HAS_EMPTY_2026-09-05.md`.

WHY THESE ARE A NEW MODULE. Every existing test of either store monkeypatches `CLAIMS_FILE` to a
`tmp_path` (16 call sites across six modules), so by construction not one of them can observe where
it points. The subject here cannot be a variant of a fixture that patches it away -- the same reason
`test_a_hand_off_from_a_worktree_reaches_the_shared_store.py` exists, whose worktree fixtures this
reuses rather than building a second pair.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from background import delivery_lane as dl
from background import seat_work_in_hand as claims_mod
from tests.background.test_a_hand_off_from_a_worktree_reaches_the_shared_store import (
    _fake_main_tree,
    _fake_worktree,
)

#: Both stores, named by the module that owns them, so every leg below runs over the pair. The
#: finding's own instruction: "every writer and reader of the claim store needs the same
#: resolution or the fix trades one asymmetry for another".
RESOLVERS = [
    pytest.param(dl.claims_file, ".delivery_lane_claims.json", id="delivery-lane"),
    pytest.param(claims_mod.claims_file, ".seat_work_in_hand.json", id="interactive-seat"),
]


# ── THE PROPERTY: THE READ CROSSES ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("resolve,name", RESOLVERS)
def test_a_claim_written_in_the_main_tree_is_read_from_a_linked_worktree(tmp_path, resolve, name):
    """The live defect, end to end, through the real claim/read machinery.

    MUTATION (must fire): resolve either store against the caller's own tree
    (`project_dir / "docs" / "observability" / name`) and the linked read returns an empty set.
    """
    main = _fake_main_tree(tmp_path)
    wt = _fake_worktree(tmp_path, main)

    claims_mod.claim("the-work", paths=["background/delivery_lane.py"], path=resolve(main))

    # ...and now ask from the worktree, which is where the executor stands.
    assert "the-work" in claims_mod.held(path=resolve(wt)), (
        f"{name}: a claim made in the main tree is invisible from a linked worktree, which is "
        f"the tree every autonomous turn is judged from")


@pytest.mark.parametrize("resolve,name", RESOLVERS)
def test_the_binding_the_turn_is_judged_on_reaches_the_claim(tmp_path, resolve, name):
    """Not just visible -- WRITABLE across, which is the call the executor singles out.

    `record_landing` is `--landed`'s whole body: it reads the claim, adds the paths a commit
    touched, and writes back. Reading across and writing back to the worktree's own copy would
    satisfy the test above and still lose the binding, so this asserts the round trip.

    MUTATION (must fire): have the write leg resolve against the caller's tree.
    """
    main = _fake_main_tree(tmp_path)
    wt = _fake_worktree(tmp_path, main)
    claims_mod.claim("the-work", paths=[], path=resolve(main))

    claims_mod.bind_paths("the-work", ["saas/opex_ledger.py"], path=resolve(wt))

    landed = json.loads(resolve(main).read_text())["the-work"]["paths"]
    assert "saas/opex_ledger.py" in landed, (
        f"{name}: the worktree's binding never reached the store the lane reads")


@pytest.mark.parametrize("resolve,name", RESOLVERS)
def test_a_main_checkout_resolves_to_itself(tmp_path, resolve, name):
    """The fail-closed direction, and the one every non-worktree caller lives on: a `.git`
    DIRECTORY is the shared tree, so nothing moves.

    MUTATION (must fire): resolve unconditionally to some other tree.
    """
    main = _fake_main_tree(tmp_path)
    assert resolve(main) == main / "docs" / "observability" / name


def test_the_draw_ledger_travels_with_the_claims_it_indexes(tmp_path):
    """`DRAW_LEDGER_FILE` is `first_drawn_at` for exactly the ids in `CLAIMS_FILE`, and
    `record_landing` compares against it. A ledger left in the worktree while the claims resolved
    across would put every re-drawn id's binding instant out of reach -- the same defect one file
    over.

    MUTATION (must fire): pin `DRAW_LEDGER_FILE` to `PROJECT_DIR`.
    """
    main = _fake_main_tree(tmp_path)
    wt = _fake_worktree(tmp_path, main)
    assert dl._ledger_path(dl.claims_file(wt)).parent == dl.claims_file(main).parent


# ── THE REFUSAL THAT NAMED THE WRONG CAUSE ──────────────────────────────────────────────────
def test_the_refusal_does_not_blame_a_sweep_when_it_is_reading_the_wrong_store(tmp_path,
                                                                               monkeypatch):
    """THE EXPENSIVE HALF OF THE FINDING. The message offered two readings, both about the
    claim's state -- "you already released it" and "it was swept, you are working unclaimed" --
    and the true cause was not in its vocabulary. The seat believed the sweep reading.

    The clause fires only when the store really is worktree-local, which after the repair means
    the resolution fell back closed or a worktree-local `path` was passed. Both legs below,
    because a clause that fires on "you are in a worktree" alone would now be false.

    MUTATION (must fire): return the unconditional "NOT CLAIMED" text.
    """
    main = _fake_main_tree(tmp_path)
    wt = _fake_worktree(tmp_path, main)
    monkeypatch.setattr(dl, "PROJECT_DIR", wt)

    local = dl.refusal_reason("the-work", path=wt / "docs" / "observability" / "claims.json")
    assert "WORKTREE" in local.upper() and "swept" not in local, (
        "the refusal still blames the claim when it is reading a store the claim never reached")

    # ...and the SAME worktree, with the store resolved across, must NOT be accused.
    crossed = dl.refusal_reason("the-work", path=dl.claims_file(wt))
    assert "WORKTREE" not in crossed.upper(), (
        "a resolved store is accused of being worktree-local, which trades one wrong cause for "
        "another")


def test_the_release_refusal_carries_the_same_two_readings(tmp_path, monkeypatch):
    """`--release` had this clause first, from the §6 trap, but keyed to `git rev-parse` alone --
    which after the repair says "linked worktree" about a store that resolved correctly.

    MUTATION (must fire): drop the `_store_is_worktree_local` guard and warn on the worktree
    alone; the second assertion fires.
    """
    main = _fake_main_tree(tmp_path)
    wt = _fake_worktree(tmp_path, main)
    monkeypatch.setattr(dl, "PROJECT_DIR", wt)

    local = dl.release_refusal_reason("the-work",
                                      path=wt / "docs" / "observability" / "claims.json")
    assert "LINKED WORKTREE" in local

    crossed = dl.release_refusal_reason("the-work", path=dl.claims_file(wt))
    assert "LINKED WORKTREE" not in crossed


def test_a_main_checkout_is_never_accused_of_being_a_worktree(tmp_path, monkeypatch):
    """The negative leg over the guard's own subject: with a `.git` DIRECTORY there is no second
    store to be reading, whatever path is passed.

    MUTATION (must fire): drop the `.git`-is-a-file test in `_store_is_worktree_local`.
    """
    main = _fake_main_tree(tmp_path)
    monkeypatch.setattr(dl, "PROJECT_DIR", main)
    assert not dl._store_is_worktree_local(main / "docs" / "observability" / "claims.json")


def test_the_resolution_is_wired_into_both_module_constants():
    """The constants the daemons actually read are the resolver's answer, not a second expression
    that happens to agree today.

    THIS LEG IS AN EQUIVALENCE WHEN THE SUITE RUNS IN A MAIN CHECKOUT, and saying so is the point:
    there `shared_tree_dir()` returns `PROJECT_DIR`, so reverting either constant to
    `PROJECT_DIR / ...` would not fire it. The crossing tests above carry the property; this one
    catches the constant drifting away from the function in the tree where it CAN differ.
    """
    assert dl.CLAIMS_FILE == dl.claims_file()
    assert claims_mod.CLAIMS_FILE == claims_mod.claims_file()
    assert dl.DRAW_LEDGER_FILE == dl._ledger_path(dl.CLAIMS_FILE)
    assert isinstance(dl.CLAIMS_FILE, Path)
