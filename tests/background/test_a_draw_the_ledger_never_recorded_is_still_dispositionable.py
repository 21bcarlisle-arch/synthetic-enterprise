"""A live claim the draw ledger never recorded could not be dispositioned by any verb.

THE DEFECT, measured 2026-09-21 on this lane's own stores. `the-landed-binder-defaults-to-head-and-
the-liveness-refusal-never-reaches-it` was handed out at 15:05:32 and written to the CLAIMS store.
It got no row in the draw ledger -- while the two claims sitting beside it in that same store both
had one. Its subject had already been repaired and published at 12:51:53, 2h14m earlier, so the
drawn item was spent before it was drawn. Both dispositions for exactly that situation refused, and
each refused on the same clause: `focus_id was never drawn -- the ledger has no row for it`.

WHY THE REFUSAL COST MORE THAN IT SAVED. `--premise-spent` is the ONLY verb for "drawn after the
work had already landed", so the clause left the single population the verb exists for unable to
reach it. And the refusal does not hold the row: the claim is swept at 100 minutes and returned to
the pool, while the seat re-orients every three hours. The row therefore goes back out BEFORE it
can be dropped, and buys another whole invocation re-deriving an answer already in origin/main.
That is how the subject reached its THIRD slug -- `the-landed-unbound-binder-counts-a-heartbeat-as-
a-landing` (2026-09-19), `...-and-two-swept-rows-are-now-dispositionable` (which landed the work),
and the one above.

`--landed-under` is NOT the missing verb here and widening it would be wrong. Its own rule refuses a
landing that is not newer than the id's first draw, and this landing predates the draw by design --
that is what "spent" means. The fix belongs to `premise_spent` alone.

WHAT IS GRADED HERE IS THE PROPERTY, NOT THE INSTANCE: **an id that was demonstrably handed out can
be dispositioned, whichever of the two stores recorded the handing-out; an id in NEITHER store
still cannot.** No sha, id or timestamp from the live stores appears below.

THE PARTITION IS ONE STATEMENT, and for this family's usual reason. A disposition that fired on
every string would be a free eraser over the seat's most urgent list -- the one thing
`note_landing_under`'s docstring says this family must never become -- and it would pass every
per-branch check of "does it record a ledger-backed row?" written on its own. So the reachability
of the REFUSING branch is asserted in the same statement as the two recording ones.

MUTATIONS (each must fire):
  (a) delete the claims-store fallback, restoring the bare refusal -- the ledgerless leg reds;
  (b) make the fallback unconditional (drop the `claimed_at <= 0.0` guard) -- the neither-store
      leg reds, which is the free-eraser shape;
  (c) seed the synthesised row with a `last_landing_at` -- the DELIVERED guard then swallows the
      ledgerless leg and it reds;
  (d) drop the ancestry check -- `test_..._STILL_REFUSES_AN_UNPUBLISHED_SPENDER` reds.
"""

from pathlib import Path

from background import delivery_lane as dl
from background import seat_work_in_hand as claims_mod

DRAWN_AT = 1_700_000_000.0
SPENDER = "d" * 40
REASON = "the subject was repaired and published before this id was handed out"

LEDGER_BACKED = "an-id-the-draw-ledger-recorded-normally"
CLAIMS_ONLY = "an-id-only-the-claims-store-ever-heard-of"
UNKNOWN = "an-id-neither-store-has-ever-held"


def _fake_git(*, published: bool = True):
    """A `_git` answering only the two questions `note_premise_spent` asks of it.

    `merge-base --is-ancestor` returns None for "not an ancestor", which is how the real helper
    reports a non-zero exit -- that asymmetry is the whole of mutation (d).
    """

    def _git(*args: str):
        if args[:1] == ("rev-parse",):
            return SPENDER + "\n"
        if args[:2] == ("merge-base", "--is-ancestor"):
            return "" if published else None
        return ""

    return _git


def _store_with(tmp_path: Path, *, ledger_row: bool, claim: bool, focus_id: str) -> Path:
    """A claims store, and its sibling ledger, holding exactly the combination asked for."""
    store = tmp_path / "claims.json"
    store.parent.mkdir(parents=True, exist_ok=True)
    claims_mod._save({}, store)
    if claim:
        claims_mod.claim(focus_id, "doing the thing", paths=[], path=store, now=DRAWN_AT)
    ledger = {}
    if ledger_row:
        ledger[focus_id] = {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT}
    claims_mod._save(ledger, dl._ledger_path(store))
    return store


def _dispose(monkeypatch, tmp_path, *, ledger_row: bool, claim: bool, focus_id: str,
             published: bool = True) -> str:
    """The refusal string `note_premise_spent` returns -- empty meaning it RECORDED."""
    store = _store_with(tmp_path, ledger_row=ledger_row, claim=claim, focus_id=focus_id)
    monkeypatch.setattr(dl, "_git", _fake_git(published=published))
    return dl.note_premise_spent(focus_id, SPENDER, REASON, path=store)


def test_THE_PARTITION_either_store_can_evidence_the_draw_and_neither_store_still_refuses(
        monkeypatch, tmp_path):
    """The whole partition in one statement, because two thirds of it passes for the wrong reason.

    A `note_premise_spent` that recorded unconditionally satisfies both recording legs and is a
    free eraser; one that refused unconditionally satisfies the refusing leg and is the defect
    this repair removes. Only the three together separate the rule from either.
    """
    ledger_backed = _dispose(monkeypatch, tmp_path / "a", ledger_row=True, claim=False,
                             focus_id=LEDGER_BACKED)
    claims_only = _dispose(monkeypatch, tmp_path / "b", ledger_row=False, claim=True,
                           focus_id=CLAIMS_ONLY)
    neither = _dispose(monkeypatch, tmp_path / "c", ledger_row=False, claim=False,
                       focus_id=UNKNOWN)

    assert (ledger_backed == "" and claims_only == "" and neither != ""), (
        f"ledger-backed={ledger_backed!r} claims-only={claims_only!r} neither={neither!r}")


def test_THE_REFUSAL_NAMES_BOTH_STORES_so_the_caller_knows_what_would_have_satisfied_it(
        monkeypatch, tmp_path):
    """A refusal naming only the ledger sent the caller to fix the store that was not the reason.

    That is not pedantry about wording: the old sentence said "the ledger has no row for it", which
    is TRUE of the claims-only case too, so a reader who hit it had no way to tell the recoverable
    situation from the unrecoverable one.
    """
    refusal = _dispose(monkeypatch, tmp_path, ledger_row=False, claim=False, focus_id=UNKNOWN)
    assert "ledger" in refusal and "claims store" in refusal, refusal


def test_A_LEDGERLESS_DISPOSITION_IS_READABLE_AFTERWARDS_with_its_commit_and_its_reason(
        monkeypatch, tmp_path):
    """The point of recording it is that the next orientation can READ it, not that it returned ''.

    A row synthesised into existence and then left without the disposition on it would clear the
    verb's return value and none of the thing the verb is for.
    """
    store = _store_with(tmp_path, ledger_row=False, claim=True, focus_id=CLAIMS_ONLY)
    monkeypatch.setattr(dl, "_git", _fake_git())
    assert dl.note_premise_spent(CLAIMS_ONLY, SPENDER, REASON, path=store) == ""

    row = claims_mod._load(dl._ledger_path(store))[CLAIMS_ONLY]
    assert row["premise_spent"]["commit"] == SPENDER
    assert row["premise_spent"]["reason"] == REASON
    # The synthesised row must not claim a landing it never had: `premise_spent` and `landed` are
    # different facts, and the DELIVERED guard reads this field to tell them apart.
    assert not row.get("last_landing_at")


def test_IT_STILL_REFUSES_AN_UNPUBLISHED_SPENDER_even_when_the_draw_came_from_the_claims_store(
        monkeypatch, tmp_path):
    """The new route must inherit every guard the ledger-backed route has, not just reach the code.

    Synthesising the row moves the id PAST the first guard only. An unpublished spender is still a
    claim about the future and is still refused, which is what makes this a widening of the
    evidence for a draw rather than a hole beside the checks.
    """
    refusal = _dispose(monkeypatch, tmp_path, ledger_row=False, claim=True,
                       focus_id=CLAIMS_ONLY, published=False)
    assert "origin/main" in refusal, refusal
