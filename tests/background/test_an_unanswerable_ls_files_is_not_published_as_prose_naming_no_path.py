"""A `git ls-files` that would not answer must not reach the reader as "your item named no path".

THE DEFECT (2026-09-18, one layer up from the third voice landed in `38a8241f3`). `_tracked_files`
was written `_git("ls-files") or ""`, and `_git` reports a git that FAILED as `None` and a git that
answered nothing as `""`. The `or ""` threw that apart away, so an unanswerable git produced an
empty tracked set; `_paths_named_in` then kept nothing, `_claim_paths` returned `[]`, and the
residual took its NO-PATHS branch and published:

    CANNOT ANSWER, not 'nothing landed': this item's prose names no tracked path (in `named_paths`
    or either store holding its text), so no commit query could be built and git was never asked

THE VOICE WAS RIGHT AND THE REASON WAS A LIE, which is why this needed its own control rather than
being covered by the `could_not_ask` predicate the other four suites share. `could_not_ask` was
ALREADY true here -- the residual correctly said it could not answer -- so every existing leg was
green while the sentence sent a reader to recover an item's prose that was never missing. What is
graded here is the CAUSE the residual names, and that is the only thing that moved.

KEYED TO THE PROPERTY, NOT TO TODAY'S WORDING. The discriminator is which SUBJECT the reason blames
-- git, or the item -- so a reworded sentence that still blames the right one stays green and a
rewording that puts the conflation back reds. `ls-files` is asserted present because it is the
actionable half a reader needs (it names the command that would not run), and the prose-blaming
phrase is asserted ABSENT because publishing it for git's silence is the defect itself.

BOTH BRANCHES ARE ASSERTED REACHABLE IN ONE STATEMENT (`test_THE_PARTITION...`), which is the rare-
branch discipline this repository learned by entering the same trap three times in one afternoon. A
`_tracked_files` that raised unconditionally would pass the defect leg and is caught only by the leg
that requires the prose-blaming sentence to STILL be published when git genuinely answered and the
item genuinely named nothing. That branch did not stop existing; it stopped being reachable by the
wrong road.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl
from tests.background.residual_voices import could_not_ask

#: The reason the NO-PATHS branch publishes. Matched on its load-bearing clause rather than the whole
#: sentence so a rewording that keeps blaming the item still reds the defect leg below.
BLAMES_THE_ITEM = "names no tracked path"

GIT_DOWN_ID = "a-window-judged-while-git-would-not-answer-ls-files"
QUIET_ITEM_ID = "a-window-whose-prose-genuinely-names-nothing-we-track"

SUBJECT_PATH = "background/delivery_lane.py"

NOW = 1789000000.0
DRAWN_AT = NOW - 8 * 3600


def _ledger(tmp_path, rows: dict):
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def _row(**extra):
    row = {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT}
    row.update(extra)
    return row


def _git_down(*args, **kwargs):
    """A git that will not answer ANYTHING -- every call is `None`, which is `_git`'s failed case."""
    return None


def _git_answering(*args, **kwargs):
    """A git that RUNS: `ls-files` lists one real path, `log` exits 0 with no matches.

    `""` AND NOT `None` FOR THE EMPTY `log`, which is the distinction this whole family exists to
    keep: real `git log` exits 0 and prints nothing when its pathspec matches nothing, and `None` is
    reserved for a git that could not run. A fake that said `None` to both would make the two legs
    below indistinguishable and grade neither.
    """
    if args and args[0] == "ls-files":
        return SUBJECT_PATH + "\n"
    if args and args[0] == "log":
        return ""
    return ""


@pytest.fixture(autouse=True)
def _no_cached_direction_history():
    """`_direction_history_text` caches for the life of the process, and a suite is one process."""
    dl._reset_direction_history()
    yield
    dl._reset_direction_history()


@pytest.fixture
def prose(monkeypatch):
    """Stub `_item_text` per id: the live item stores hold no synthetic row."""
    texts: dict[str, str] = {}
    monkeypatch.setattr(dl, "_item_text", lambda fid: texts.get(str(fid), ""))
    return texts


def test_THE_PARTITION_git_silent_blames_git_and_a_quiet_item_still_blames_the_item(
        monkeypatch, prose):
    """Both roads to `could_not_ask`, in ONE statement, each naming its own cause.

    THE FLATTERING READING THIS REFUSES: a subject that raised on every `ls-files` would satisfy the
    defect leg on its own. Only requiring the item-blaming sentence to SURVIVE for a genuinely quiet
    item establishes that the branch was made unreachable by the wrong road rather than deleted.
    """
    prose[GIT_DOWN_ID] = "repair " + SUBJECT_PATH
    prose[QUIET_ITEM_ID] = "file it in docs/design and tell the director"

    monkeypatch.setattr(dl, "_git", _git_down)
    git_silent = dl._disposition(_row(), DRAWN_AT, focus_id=GIT_DOWN_ID)

    monkeypatch.setattr(dl, "_git", _git_answering)
    item_quiet = dl._disposition(_row(), DRAWN_AT, focus_id=QUIET_ITEM_ID)

    assert could_not_ask(git_silent) and could_not_ask(item_quiet), (
        "both roads must still reach the CANNOT-ANSWER voice; that half was never the defect")
    assert "ls-files" in git_silent["evidence"] and BLAMES_THE_ITEM not in git_silent["evidence"], (
        "git's silence was published as the item's: " + git_silent["evidence"])
    assert BLAMES_THE_ITEM in item_quiet["evidence"], (
        "the NO-PATHS branch must stay reachable when git ANSWERED and the prose named nothing "
        "tracked -- a subject that raises unconditionally passes the leg above and is wrong here")


def test_A_FAILED_LS_FILES_RAISES_rather_than_reporting_an_empty_repository(monkeypatch):
    """`_tracked_files` itself. MUTATION: restore `or ""` and this is the leg that fires.

    Asserted at the seam as well as through the residual because the residual reaches it down four
    functions, and a leg that only ever grades the far end cannot say which layer re-collapsed.
    """
    monkeypatch.setattr(dl, "_git", _git_down)
    with pytest.raises(dl.GitUnavailable):
        dl._tracked_files()

    monkeypatch.setattr(dl, "_git", _git_answering)
    assert dl._tracked_files() == {SUBJECT_PATH}, "the fake is not deaf: a live git still answers"


def test_AN_EMPTY_LS_FILES_IS_AN_ANSWER_and_keeps_returning_no_paths(monkeypatch):
    """A git that RAN and tracks nothing is not a git that would not run.

    This is the half `_git_or_raise` exists to preserve, and it is asserted because the cheap way to
    pass the leg above is to treat every empty `ls-files` as a failure -- which would send a reader
    hunting a broken git on a repository that is merely empty.
    """
    monkeypatch.setattr(dl, "_git", lambda *a, **k: "")
    assert dl._tracked_files() == set()
    assert dl._paths_named_in("repair " + SUBJECT_PATH) == []


def test_THE_DRAW_IS_STILL_REMEMBERED_when_ls_files_will_not_answer(tmp_path, monkeypatch):
    """`record_draw` must not lose `last_drawn_at` to the new raise. The regression this guards.

    THE STAMP IS OPTIONAL AND THE INSTANT IS NOT. `record_draw`'s outer `except` RETURNS, so letting
    `_paths_named_in`'s raise reach it would have dropped the whole row -- and every window, sweep
    and disposition downstream keys off `last_drawn_at`. A control on the reason the residual gives
    would never have noticed: the row would simply not be there to dispose of.
    """
    store = _ledger(tmp_path, {})
    monkeypatch.setattr(dl, "_git", _git_down)
    dl.record_draw(GIT_DOWN_ID, DRAWN_AT, path=store, text="repair " + SUBJECT_PATH)

    # READ BACK THROUGH THE SUBJECT'S OWN LOADER, not a hand-rolled `read_text` + `json.loads`.
    # `tests/architecture/test_a_control_reads_python_as_code.py` refused the hand-rolled version and
    # was right to: a control that re-implements its subject's reader can pass while the real reader
    # is broken, and the census exists to stop exactly that. `claims_mod._load` is what
    # `_disposition` and `tree_verdict` use, so this leg now fails if that path fails.
    row = (dl.claims_mod._load(dl._ledger_path(store)) or {}).get(GIT_DOWN_ID)
    assert row and row.get("last_drawn_at") == DRAWN_AT, (
        "an unanswerable ls-files cost the row its draw instant, not just its path stamp")
    assert "named_paths" not in row, (
        "no stamp may be invented from a git that never answered -- absent is the honest state, "
        "and the reach-back is what covers it")


def test_TREE_VERDICT_STAYS_SILENT_rather_than_raising_through_its_callers(tmp_path, monkeypatch,
                                                                          prose):
    """`tree_verdict` promises `None` covers "a git that would not answer". It now keeps it on purpose.

    Before this the promise held by ACCIDENT, because the unavailable case arrived as an empty list.
    `sweep_stale` reads `None` as "neither question was answered" and lets the ordinary swept-claim
    alarm fire, so silence is the right answer HERE even though it is the wrong answer in the
    residual -- this reader has no voice to say which silence it hit, and the residual does.
    """
    prose[GIT_DOWN_ID] = "repair " + SUBJECT_PATH
    store = _ledger(tmp_path, {GIT_DOWN_ID: _row()})
    monkeypatch.setattr(dl, "_git", _git_down)

    assert dl.tree_verdict(GIT_DOWN_ID, now=NOW, path=store) is None
