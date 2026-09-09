"""A window that closed with no landing meant THREE different things and the reading said one.

THE DEFECT (director, 2026-09-09, measured on this lane's own ledger). 61 of 224 rows in
`docs/observability/.delivery_lane_claims.draws.json` read `last_landing_at: null`, and
`drawn_without_landing` -- the join the orientation opens with, under the heading that tells the
next seat to check `git status` before starting anything new -- reported every one of them as the
same fact: handed out, window closed, nobody did it. Three situations wear that null:

  * NOTHING WAS DONE. The real miss, and the only one the heading is about.
  * IT LANDED ELSEWHERE. Worked and committed under a name that read better. `note_landing_under`
    has covered this since 2026-09-07 and writes a landing instant, so the row leaves the list.
  * THE PREMISE WAS SPENT. Drawn against a condition that was already true, so there was nothing
    left to deliver and no commit of this tick's could ever be bound. THIS ONE HAD NO ROUTE AT
    ALL -- the lane's own doorbell has printed the premise check since 2026-09-05 and told the
    reader to release the claim, and the row it came from stayed an unexplained miss forever.

`make-the-pages-two-selection-spreads-legible-now-that-they-sit-at-different-n` is the named
instance: swept because `420031dae` had already spent its premise, and indistinguishable in the
ledger from an item nobody touched. The cost is not bookkeeping -- this is the instrument every
focus item is graded with, and a null that means three things makes the grading guesswork.

KEYED TO THE PROPERTY, NEVER TO THE COUNT. Nothing here asserts 61, or 224, or that the number
falls. The property is: **every row `drawn_without_landing` returns names which of the three it
was, and the residual is the shape carrying NO evidence** -- so a row goes quiet only when a join
against something on disk says it may. A control pinned to today's 61 would go green when the
sweep merely got quieter, which is the failure being fixed wearing a better name.

MUTATIONS (each must fire, and which test catches it):
  (a) drop the `reason` requirement -- `..._A_DISPOSITION_WITH_NO_REASON_IS_REFUSED`;
  (b) drop the ancestor-of-origin/main join -- `..._AN_UNPUBLISHED_SPENDER_IS_REFUSED`;
  (c) drop the "resolves to a commit" check -- `..._A_SHA_THAT_IS_NOT_A_COMMIT_HERE_IS_REFUSED`;
  (d) drop the "was never drawn" guard -- `..._AN_ID_THAT_WAS_NEVER_DRAWN_HAS_NO_WINDOW`;
  (e) drop the already-landed guard -- `..._A_ROW_THAT_DELIVERED_KEEPS_THE_STRONGER_FACT`;
  (f) return "" everywhere -- the partition control reds on all five refusal legs at once;
  (g) make `_disposition` return `NOT_DONE` always, or `PREMISE_SPENT` always -- the partition
      control over the READING, which asserts all three appear from one ledger;
  (h) let a STALE `landed_under` credit settle a NEW draw -- `..._A_REDRAWN_ROW_IS_NOT_DONE_AGAIN`.

THE PARTITION CONTROLS COME FIRST, both of them, and each is one statement over the whole
partition. A `note_premise_spent` that refused everything passes all five refusal legs written
separately, and a `_disposition` that answered `NOT_DONE` always passes every "this row is a real
miss" leg written separately. This project has walked into that trap through three doors in one
afternoon; the answer is a control over the partition, not a leg per branch.

THE GIT JOIN IS EXERCISED FOR REAL where the repo can supply the fact -- `origin/main`'s own sha
is an ancestor of `origin/main` by construction, on any machine, forever -- and through a STRICTER
fake for the non-ancestor branch, because no sha in this repo is guaranteed to exist and not be
published. The fake answers only from an explicit table and returns None otherwise, so it can only
make the subject refuse MORE than real git would; a fake more permissive than its subject is how
a fail-open becomes a green suite here. `test_..._THE_FAKE_IS_NOT_DEAF` is the poison round: the
same fake with the ancestor answer flipped to yes must ACCEPT, which is what proves the refusal
came from the ancestor test and not from the fake declining to speak.
"""
from __future__ import annotations

import json
import subprocess

import pytest

from background import delivery_lane as dl

#: The live instance, read from the draw ledger on 2026-09-09.
SPENT_ID = "make-the-pages-two-selection-spreads-legible-now-that-they-sit-at-different-n"
MISSED_ID = "find-where-the-renewal-rule-prices-up-the-households-it-then-loses"
CREDITED_ID = "the-published-inversion-must-carry-its-attribution-on-the-page-not-only-in-the-tree"
LENDER_ID = "two-of-three-drawn-focus-items-were-finished-and-never-left-the-working-tree"

NOW = 1789000000.0
#: Older than `CLAIM_STALE_SECONDS` so every window below has closed, and inside the 24h horizon.
DRAWN_AT = NOW - 4 * 3600


def _published_sha() -> str:
    """`origin/main`'s own commit sha: an ancestor of `origin/main` on any machine, by identity."""
    out = subprocess.run(("git", "rev-parse", "--verify", "--quiet", "origin/main^{commit}"),
                         cwd=dl.PROJECT_DIR, capture_output=True, text=True)
    sha = out.stdout.strip()
    if not sha:
        pytest.skip("no refs/remotes/origin/main here -- the real-git leg has nothing to join on")
    return sha


def _ledger(tmp_path, rows: dict):
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def _rows(store):
    return json.loads(dl._ledger_path(store).read_text(encoding="utf-8"))


def _three_shapes(tmp_path):
    """One ledger holding all three dispositions' raw material, plus a row to refuse against."""
    return _ledger(tmp_path, {
        SPENT_ID: {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT},
        MISSED_ID: {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT},
        CREDITED_ID: {"first_drawn_at": DRAWN_AT - 600, "last_drawn_at": DRAWN_AT - 600,
                      "last_landing_at": DRAWN_AT - 60, "last_landing_paths": ["site/index.html"],
                      "landed_under": LENDER_ID},
        "a-row-that-delivered-under-its-own-name": {
            "first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT,
            "last_landing_at": DRAWN_AT + 60, "last_landing_paths": ["tools/x.py"]},
    })


def test_THE_PARTITION_of_the_reader_all_three_dispositions_come_back_from_one_ledger(tmp_path):
    """One ledger, three dispositions, one statement: a constant answer cannot survive it.

    A reader that always said `NOT_DONE` would leave the whole 61 unexplained -- the defect --
    and one that always said `PREMISE_SPENT` would silence every real miss. Both are caught here
    because all three are asserted together against one store, and the residual is asserted to
    carry NO evidence, which is what makes it the residual rather than a fourth guess.

    ASKED OF `disposition_of`, NOT OF `drawn_without_landing`, and that is not a convenience.
    The list reading drops a credited row by construction (the credit writes a landing instant),
    so `LANDED_ELSEWHERE` is UNREACHABLE there and asserting it through that door would be
    asserting a branch that cannot be taken. Both surfaces share one definition; this is the one
    where the whole partition is live.
    """
    store = _three_shapes(tmp_path)
    assert dl.note_premise_spent(SPENT_ID, _published_sha(), "420031dae already closed the two-n "
                                 "split before this was drawn", path=store) == ""

    spent = dl.disposition_of(SPENT_ID, path=store)
    missed = dl.disposition_of(MISSED_ID, path=store)
    credited = dl.disposition_of(CREDITED_ID, path=store)

    assert spent["disposition"] == dl.PREMISE_SPENT
    assert missed["disposition"] == dl.NOT_DONE
    assert credited["disposition"] == dl.LANDED_ELSEWHERE
    # The residual is the shape with NO evidence, and the other two must carry theirs -- otherwise
    # "names its disposition" is satisfied by a label nobody can follow back to a fact on disk.
    assert missed["evidence"] == ""
    assert _published_sha()[:9] in spent["evidence"]
    assert LENDER_ID in credited["evidence"]
    # The two answers that are NOT one of the three, kept distinct so "nobody did it" cannot
    # absorb "nobody was asked" -- the same conflation one rung up.
    assert dl.disposition_of("a-row-that-delivered-under-its-own-name",
                             path=store)["disposition"] == dl.DELIVERED
    assert dl.disposition_of("an-id-nobody-ever-drew", path=store)["disposition"] == dl.NOT_DRAWN


def test_THE_LIST_READING_names_the_two_dispositions_it_can_see_and_drops_the_settled(tmp_path):
    """`drawn_without_landing` is what the orientation opens with, and no row may come back
    unnamed. It sees exactly two of the three -- a credited row is settled and leaves -- and
    every row it does return carries the same vocabulary the row-level reader uses."""
    store = _three_shapes(tmp_path)
    assert dl.note_premise_spent(SPENT_ID, _published_sha(), "already closed", path=store) == ""

    got = {r["id"]: r for r in dl.drawn_without_landing(now=NOW, path=store)}

    assert got[SPENT_ID]["disposition"] == dl.PREMISE_SPENT
    assert got[MISSED_ID]["disposition"] == dl.NOT_DONE
    assert all(r["disposition"] in (dl.NOT_DONE, dl.PREMISE_SPENT) for r in got.values())
    # Settled rows are not on the missed list at all, by either route.
    assert CREDITED_ID not in got
    assert "a-row-that-delivered-under-its-own-name" not in got


def test_THE_PARTITION_one_record_is_taken_and_five_are_refused_each_naming_itself(tmp_path):
    """One ledger, six outcomes, one control: refuse-everything and accept-everything both red.

    Reasons are checked for their distinguishing word, not verbatim, so the messages can be
    improved without pinning this to today's wording.
    """
    store = _three_shapes(tmp_path)
    sha = _published_sha()
    taken = dl.note_premise_spent(SPENT_ID, sha, "the two-n split was already closed", path=store)
    no_reason = dl.note_premise_spent(MISSED_ID, sha, "   ", path=store)
    never_drawn = dl.note_premise_spent("an-id-nobody-ever-drew", sha, "whatever", path=store)
    delivered = dl.note_premise_spent("a-row-that-delivered-under-its-own-name", sha, "whatever",
                                      path=store)
    not_a_commit = dl.note_premise_spent(MISSED_ID, "0" * 40, "whatever", path=store)
    unresolvable = dl.note_premise_spent(MISSED_ID, "not-a-ref-anywhere", "whatever", path=store)

    assert taken == "", taken
    assert "reason" in no_reason
    assert "never drawn" in never_drawn
    assert "DELIVERED" in delivered
    assert "resolve" in not_a_commit
    assert "resolve" in unresolvable


def _fake_git(ancestor: bool):
    """A STRICTER `_git`: it answers two questions from a table and refuses everything else.

    It can only make the subject refuse more than real git would, never less, which is the safe
    direction for a fake standing in for a wall-adjacent join.
    """
    def fake(*args: str) -> str | None:
        if args[:2] == ("rev-parse", "--verify"):
            return "beefbeefbeefbeefbeefbeefbeefbeefbeefbeef\n"
        if args[:2] == ("merge-base", "--is-ancestor"):
            return "" if ancestor else None
        return None
    return fake


def test_AN_UNPUBLISHED_SPENDER_IS_REFUSED_because_it_may_still_be_rebased_away(tmp_path,
                                                                                monkeypatch):
    """A commit that exists but has not reached origin/main is a claim about the future."""
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(ancestor=False))
    refusal = dl.note_premise_spent(MISSED_ID, "beefbeef", "a sibling lane did it", path=store)
    assert "origin/main" in refusal
    assert "premise_spent" not in _rows(store)[MISSED_ID]


def test_THE_FAKE_IS_NOT_DEAF_the_same_fake_with_the_ancestor_answer_flipped_accepts(tmp_path,
                                                                                     monkeypatch):
    """The poison round. Without it, the refusal above is ambiguous between "the ancestor test
    fired" and "the fake declined to answer anything", and this project has read the second as
    the first before. Same fake, one bit changed, opposite outcome."""
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(ancestor=True))
    assert dl.note_premise_spent(MISSED_ID, "beefbeef", "a sibling lane did it", path=store) == ""
    assert _rows(store)[MISSED_ID]["premise_spent"]["reason"] == "a sibling lane did it"


def test_A_REDRAWN_ROW_IS_NOT_DONE_AGAIN_and_the_old_credit_does_not_settle_the_new_window(
        tmp_path):
    """A credited row drawn a SECOND time owes a second delivery.

    `landed_under` sits on the row forever, so reading it as "this window is explained" would let
    one credit silence every future draw of the same id -- the across-windows fail-open. The
    instant is compared against THIS draw, exactly as the caller's own third clause does.
    """
    store = _ledger(tmp_path, {
        CREDITED_ID: {"first_drawn_at": DRAWN_AT - 90000, "last_drawn_at": DRAWN_AT,
                      "last_landing_at": DRAWN_AT - 89000,
                      "last_landing_paths": ["site/index.html"], "landed_under": LENDER_ID},
    })
    got = {r["id"]: r for r in dl.drawn_without_landing(now=NOW, path=store)}
    assert got[CREDITED_ID]["disposition"] == dl.NOT_DONE
    assert got[CREDITED_ID]["evidence"] == ""


def test_THE_RECORD_TAKES_NO_CLAIM_AND_MOVES_NO_DRAW(tmp_path):
    """Disposing of a window is a note on the draw ledger and nothing else.

    Taking a claim would restart a deadline for work nobody is doing, and moving `last_drawn_at`
    would hide the window this exists to explain. Wired to the ledger only, on purpose.
    """
    store = _three_shapes(tmp_path)
    before_claims = store.read_text(encoding="utf-8")
    before_draw = _rows(store)[SPENT_ID]["last_drawn_at"]
    assert dl.note_premise_spent(SPENT_ID, _published_sha(), "already closed", path=store) == ""
    assert store.read_text(encoding="utf-8") == before_claims
    row = _rows(store)[SPENT_ID]
    assert row["last_drawn_at"] == before_draw
    assert not row.get("last_landing_at")


def test_THE_SEATS_OWN_PROSE_NAMES_THE_DISPOSITION_and_counts_only_the_undisposed():
    """The disposition has to reach the READER, not just the store.

    `delivery_seat._prompt` is the sentence the orienting session actually reads, above the JSON
    and outside the truncation, and it said "no landing -- CHECK `git status` FOR THESE" about
    every row. Sending the seat to look in the working tree for an item whose premise was spent
    before it was drawn is the instruction that wasted the windows this whole change is about, so
    the fix is not done until the prose stops giving it.

    The count is asserted to be over the `not_done` rows ALONE. A count over all of them would go
    on overstating the miss by exactly the number of rows that have been explained -- the defect,
    surviving the fix, in the one place the seat reads.
    """
    from background import delivery_seat as ds

    brief = ds.build_brief()
    brief["focus_drawn_never_landed"] = [
        {"id": "a-real-miss", "hours_since_draw": 3.0, "disposition": dl.NOT_DONE,
         "evidence": ""},
        {"id": "a-spent-premise", "hours_since_draw": 4.0, "disposition": dl.PREMISE_SPENT,
         "evidence": "420031dae: the two-n split was already closed"},
    ]
    prose = ds._prompt(brief)

    assert "1 of the 2 have NO disposition" in prose
    assert "a-real-miss (drawn 3.0h ago, not_done)" in prose
    assert ("a-spent-premise (drawn 4.0h ago, premise_spent: 420031dae: the two-n split was "
            "already closed)") in prose


def test_AN_UNWRITABLE_LEDGER_READS_AS_A_REFUSAL_not_as_a_silent_success(tmp_path, monkeypatch):
    """Fail CLOSED, unlike `drawn_without_landing`, and the direction is the whole point: the
    caller is about to print this, and a success over a store that did not change is the one
    answer that trains the next seat to stop checking."""
    store = _three_shapes(tmp_path)
    sha = _published_sha()

    def boom(*_a, **_k):
        raise OSError("read-only ledger")

    monkeypatch.setattr(dl.claims_mod, "_save", boom)
    refusal = dl.note_premise_spent(SPENT_ID, sha, "already closed", path=store)
    assert "could not be written" in refusal
