"""A premise_spent disposition retires the continuation with the same id, and only that one.

THE DEFECT (2026-11-18). The draw ledger recorded `the-box-runs-the-skip-pair-before-another-book`
as premise_spent by c18067646, and `seat_continuation.live()` went on offering it to the box's
one worker: the ledger and the offer are two stores, and only the first heard the disposition.
Its own `retire` had been HELD on the skip pair's control files -- another item's output -- so the
retirement path also had to accept a git-checked disposition as passing that hold.

THE PARTITION IS ONE STATEMENT: the spent id is gone from live(), the not-done id is still there.
A guard that emptied live() passes the first leg alone; the second is what makes it able to fail.

MUTATIONS (each must fire):
  (a) delete the `seat_continuation.retire` call in `note_premise_spent` -- the spent id stays live;
  (b) drop `premise_spent=` from that call -- the artefact hold keeps the spent id live;
  (c) retire every live row instead of the one id -- the not-done leg reds;
  (d) retire when `path` is given without `continuation_path` -- the isolation test reds.
"""

from pathlib import Path

from background import delivery_lane as dl
from background import seat_continuation as sc
from background import seat_work_in_hand as claims_mod

NOW = 1_800_000_000.0
SPENDER = "c" * 40
SPENT = "a-continuation-whose-premise-a-landed-commit-already-spent"
NOT_DONE = "a-continuation-nobody-has-finished"
# A path no test machine has: under the old rule it HELD the retirement, which is the shape of
# the live row (named control files another item will write).
ABSENT = "/var/tmp/no-such-dir-for-this-test/control_11111_22222.json"


def _git(*args: str):
    if args[:1] == ("rev-parse",):
        return SPENDER + "\n"
    if args[:2] == ("merge-base", "--is-ancestor"):
        return ""
    return ""


def _stores(tmp_path: Path) -> tuple[Path, Path]:
    claims = tmp_path / "claims.json"
    claims_mod._save({}, claims)
    claims_mod._save({i: {"first_drawn_at": NOW - 60, "last_drawn_at": NOW - 60}
                      for i in (SPENT, NOT_DONE)}, dl._ledger_path(claims))
    cont = tmp_path / "continuations.json"
    sc._save([{"id": i, "what": f"wait for {ABSENT} then grade it", "why": "w",
               "done_means": "d", "written_at": NOW - 60} for i in (SPENT, NOT_DONE)], cont)
    return claims, cont


def test_THE_PARTITION_the_spent_id_leaves_live_and_the_not_done_id_stays(monkeypatch, tmp_path):
    claims, cont = _stores(tmp_path)
    monkeypatch.setattr(dl, "_git", _git)
    monkeypatch.setattr(dl, "current_orientation", lambda *a, **k: "oriented-for-the-test")
    assert dl.note_premise_spent(SPENT, SPENDER, "spent before it was drawn",
                                 path=claims, continuation_path=cont) == ""

    offered = [i["id"] for i in sc.live(now=NOW, path=cont)]
    assert SPENT not in offered and NOT_DONE in offered, offered
    row = next(i for i in sc.retired(path=cont) if i["id"] == SPENT)
    assert row["retired_by_premise_spent"]["commit"] == SPENDER, row


def test_A_TEST_STORE_NEVER_REACHES_THE_SHARED_OFFER(monkeypatch, tmp_path):
    """A caller passing its own claims `path` and no `continuation_path` must retire nothing."""
    claims, cont = _stores(tmp_path)
    monkeypatch.setattr(dl, "_git", _git)
    calls = []
    monkeypatch.setattr(sc, "retire", lambda *a, **k: calls.append((a, k)) or True)
    assert dl.note_premise_spent(SPENT, SPENDER, "spent", path=claims) == ""
    assert calls == [], calls
