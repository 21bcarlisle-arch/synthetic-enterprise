"""THE DOORBELL PRINTED AN ID THE STORE DID NOT HOLD, AND THE WORKER'S OWN INSTRUCTION BOUND NOTHING.

THE DEFECT, filed 2026-09-11 as a BLOCKING finding
(`WORKER_FINDING_THE_DELIVERY_LANE_TRUNCATES_A_CLAIM_ID_AT_A_DECIMAL_POINT...`) and reproduced from
the record here. `_DISPATCHED_ID` recovered the Lane 0 id from the `--landed` instruction the
doorbell carries, and its character class was `[a-z0-9-]`. An id with a decimal in it --
`the-third-arm-separates-fewer-accounts-from-different-accounts-in-p6s-2.45-percent` -- was
captured as `...-in-p6s-2`, so **the dispatch claimed a spelling the doorbell never printed**.

The claims store then held two rows for one piece of work, written by two routes that spelt it
differently: `claim_dispatched` (truncated) and `seat_executor.run_once`/`draw` (the id as written
in `DIRECTION.yaml`). Three consequences, and the third is the one that cost a turn:

  1. the worker ran the `--landed <full-id>` its own doorbell gave it and bound NOTHING, so the
     real claim kept `paths: []` and was swept back into the pool 100 minutes later, however much
     had landed -- exactly the outcome the instruction exists to prevent;
  2. the other row sat in the store with an empty path list and a NEWER `claimed_at`, reading like
     a fresh unstarted claim of the same work;
  3. the refusal said *"an older commit here is genuinely somebody else's work"*, which is true of
     the population it was written for and false here, and it sends the reader looking for a rival
     lane that does not exist.

WHAT THE FINDING GOT WRONG, corrected here beside the claim rather than quietly. It said the rival
row was "minted by my own `--landed`" and asked for a refusal to mint. `record_landing` has never
minted: it reads the store and returns `[]` on an id the store does not hold, which is measurable
in three lines and is the first leg below. The mint was the DISPATCH, under the other spelling. The
remedy the finding asked for second -- *"resolve the id the way the draw did"* -- is the real one,
and it is what `resolve_claim_id` does.

THE PROPERTY, and it is deliberately not "the regex now allows a dot": **an id printed in a
doorbell's own bind instruction binds the claim that doorbell's dispatch made, whatever characters
it contains** -- and a bind can only ever reach a claim the store already holds.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl
from background import seat_continuation
from background import seat_work_in_hand as claims_mod

from .test_delivery_lane import _land, repo  # noqa: F401 - fixture used by name

#: A real id from the record. The decimal is the whole subject.
DOTTED = "the-third-arm-separates-fewer-accounts-from-different-accounts-in-p6s-2.45-percent"

#: What the capture used to make of it, and what the store still holds rows under.
TRUNCATED = "the-third-arm-separates-fewer-accounts-from-different-accounts-in-p6s-2"


def _keys(store):
    return set(json.loads(store.read_text())) if store.exists() else set()


def test_landed_binds_the_claim_and_MINTS_NOTHING_across_the_whole_partition(repo):  # noqa: F811
    """ONE CONTROL OVER ALL FOUR SPELLINGS, because each of the flattering failures passes a
    subset of them.

    A `record_landing` that minted on miss passes every "it bound the right claim" leg. One that
    resolved nothing passes every "it did not mint" leg. One that resolved by bare prefix passes
    both of those and binds the WRONG item's commit in row four. Only the four rows together can
    tell the mechanism from any of the three ways of not having one.
    """
    landed_at = _land(repo, "background/thing.py")
    claims_mod.claim(TRUNCATED, "drawn under the spelling the dispatch could hold", paths=[],
                     path=repo["claims"], now=landed_at - 60)
    claims_mod.claim("a-different-item-in-p6s-2.99-other", "not this work", paths=[],
                     path=repo["claims"], now=landed_at - 60)
    before = _keys(repo["claims"])

    # 1. THE INSTRUCTION AS THE DOORBELL PRINTS IT. The store holds the other spelling; this is
    #    the run that refused, and the finding's whole subject.
    assert dl.record_landing(DOTTED, path=repo["claims"]) == ["background/thing.py"]
    assert json.loads(repo["claims"].read_text())[TRUNCATED]["paths"] == \
        ["background/thing.py"], (
        "the paths must land on the claim the DRAW made -- a bind that satisfies some other row "
        "leaves the real claim empty and swept, which is the defect wearing a fix's clothes"
    )

    # 2. The spelling the store holds, unchanged behaviour, so the widening cannot have been paid
    #    for by breaking the ordinary case.
    assert dl.record_landing(TRUNCATED, path=repo["claims"]) == ["background/thing.py"]

    # 3. DIFFERENT WORK that shares everything the truncation can see. `-2.99-other` and
    #    `-2.45-percent` both truncate to `...-p6s-2`; neither is a prefix of the other, and a
    #    resolver keyed only to the truncation would credit one item's commit to the other.
    assert dl.record_landing("a-different-item-in-p6s-2.45-percent", path=repo["claims"]) == []

    # 4. An id nothing in the store resembles. The mint the finding asked to be refused.
    assert dl.record_landing("never-claimed-anything-at-all", path=repo["claims"]) == []

    assert _keys(repo["claims"]) == before, (
        "--landed wrote a row the store did not already hold. Its job is to ATTACH to a claim; a "
        "write path that mints turns a spelling difference into a rival record"
    )


def test_the_refusal_names_the_row_that_IS_there(repo):  # noqa: F811
    """Consequence 3, and the half a bind alone does not fix.

    Both legs are asserted at the same id and store so the pass cannot come from the near-match
    branch being unreachable, and the second leg is the population the old sentence was written
    for -- it must keep saying what it said.
    """
    _land(repo, "background/thing.py")
    claims_mod.claim("some-item-in-p6s-2.99-other", "live claim, different work", paths=[],
                     path=repo["claims"])

    near = dl.refusal_reason("some-item-in-p6s-2.45-percent", path=repo["claims"])
    assert "some-item-in-p6s-2.99-other" in near and "NOT CLAIMED under that spelling" in near, (
        "an id whose only difference from a live row is where its spelling stops must be told so "
        "-- 'it is NOT CLAIMED' sends the reader to look for a sweep that never happened"
    )
    assert "somebody else's work" not in near

    plain = dl.refusal_reason("nothing-resembles-this", path=repo["claims"])
    assert "it is NOT CLAIMED" in plain and "different spelling" not in plain, (
        "an id with no near match must keep the ordinary reading; a near-match sentence that "
        "fires on everything names nothing"
    )


def test_release_frees_the_claim_under_either_spelling(repo, monkeypatch):  # noqa: F811
    """The more expensive miss of the two. A bind can be repeated on the next commit; a claim left
    standing under the other spelling is re-offered to a later tick as unstarted work, and the
    seat only re-orients every three hours.

    Asserts the claim is HELD first, so a release that frees nothing cannot pass by acting on an
    empty store.
    """
    monkeypatch.setattr(dl, "CLAIMS_FILE", repo["claims"])
    monkeypatch.setattr(seat_continuation, "STORE", repo["root"] / "continuations.json")
    claims_mod.claim(TRUNCATED, "drawn under the spelling the dispatch could hold", paths=[],
                     path=repo["claims"])
    assert TRUNCATED in dl.held(path=repo["claims"])

    assert dl.main(["--release", DOTTED]) == 0
    assert TRUNCATED not in dl.held(path=repo["claims"]), (
        "releasing by the id the doorbell printed left the claim the dispatch made standing"
    )


@pytest.mark.parametrize("dispatched", [DOTTED, TRUNCATED])
def test_a_dispatch_claims_the_id_the_doorbell_printed(repo, monkeypatch, dispatched):  # noqa: F811
    """THE MINT SIDE, at the only place both halves are visible at once.

    `claim_dispatched` reads the id out of the composed text, and that text is the only place the
    id survives into the dispatched prompt. Parametrised over both spellings because the property
    is an IDENTITY between what was printed and what was claimed -- a capture that always returned
    the truncation satisfies the second row and fails the first, and one that always returned the
    whole rest of the sentence fails both.
    """
    monkeypatch.setattr(dl, "DRAW_LEDGER_FILE", repo["claims"].with_suffix(".draws.json"))
    text = f"LANE 0 DELIVERY -- ... run `python3 -m background.delivery_lane --landed {dispatched}`"

    assert dl.claim_dispatched(text, path=repo["claims"]) == dispatched
    assert _keys(repo["claims"]) == {dispatched}


def test_a_dispatch_adopts_a_live_claim_under_the_other_spelling(repo, monkeypatch):  # noqa: F811
    """The legacy population: rows written by the old capture are still in the live store, and a
    dispatch is exactly where the second row used to appear.

    The deadline leg is not decoration -- adopting must not restart the claim's clock, or a
    re-dispatched item could never be swept.
    """
    monkeypatch.setattr(dl, "DRAW_LEDGER_FILE", repo["claims"].with_suffix(".draws.json"))
    claims_mod.claim(TRUNCATED, "written by the old capture", paths=[], path=repo["claims"])
    first = json.loads(repo["claims"].read_text())[TRUNCATED]["claimed_at"]

    assert dl.claim_dispatched(f"... --landed {DOTTED}`", path=repo["claims"]) == TRUNCATED
    assert _keys(repo["claims"]) == {TRUNCATED}
    assert json.loads(repo["claims"].read_text())[TRUNCATED]["claimed_at"] == first


def test_the_capture_does_not_eat_a_trailing_full_stop():
    """The cost of widening the class, paid where it is visible. An id is allowed a dot INSIDE it
    and never at either end, so an instruction that ends a sentence still names the id and not the
    id plus punctuation -- which would be the same defect with a different stopping point.
    """
    assert dl._DISPATCHED_ID.search("run --landed some-id-2.45-percent.").group(1) == \
        "some-id-2.45-percent"
    assert dl._DISPATCHED_ID.search("run --landed plain-id, then").group(1) == "plain-id"
    assert dl._DISPATCHED_ID.search("run --landed x.").group(1) == "x"
