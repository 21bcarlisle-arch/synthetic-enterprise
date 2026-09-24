"""`--landed` reported success on a bind that could not clear the row, and said nothing.

THE DEFECT, measured 2026-09-24 on this lane's live ledger. Two deliberate decisions meet badly.
`_remember_landing` writes `last_landing_at` as the COMMIT's own timestamp, so a reader comparing
it against a turn's start instant is comparing two facts about git. `drawn_without_landing` keys
its third clause to THIS draw, so a stale credit cannot settle a new window. Both are right on
their own. Together they mean a landing bound to an id that has since been RE-DRAWN cannot clear
the row -- and the success path of `--landed` printed `bound 5 path(s) to <id>` and returned 0,
which reads as settled and is not.

WHY IT LANDS ON THE WORST POPULATION. The bind is prescribed for exactly one shape: an item the
seat was offered again because its landing was never bound. Every unbound re-draw pushes the latest
window further past the commit, so the longer the row has been going round, the more certainly the
prescribed remedy is a no-op -- and the caller is told it worked.

THE INSTANCE. `the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` landed at
`3b01193a8` on 2026-09-23 17:54, was re-drawn 2026-09-24 11:36, and a seat spent a whole Lane 0
item whose entire content was *run `--landed` on it; finished when the row stops appearing in the
brief*. The bind ran, reported success, and the row stayed exactly where it was. Only
`--premise-spent` -- the one per-window disposition -- could answer that window, and nothing on the
success path named it.

KEYED TO THE PROPERTY, NEVER TO THAT ROW: **a binding whose commit predates the id's latest draw
owes the caller a sentence saying it does not settle that window, and one inside the window owes
nothing.** No live id, sha, horizon or stale-seconds constant appears below; every instant is
relative to the fixture's own two draws, so the control survives any of those moving and goes red
if the property does.

MUTATIONS (each must fire, and which test catches it):
  (a) delete the `landing_predates_this_window` call from `main`'s `--landed` success branch --
      the defect itself; `..._THE_PRODUCTION_CALLER_PRINTS_IT_AND_STILL_EXITS_ZERO` goes red;
  (b) make the caveat non-empty unconditionally, i.e. warn on every bind --
      `..._A_STALE_BIND_SPEAKS_AND_A_FRESH_ONE_IS_SILENT` goes red on its SECOND leg, because both
      readings are asserted over one row's two arrangements and a warner that warns at everything
      fails the partition;
  (c) return `""` unconditionally -- the same test's FIRST leg goes red, from the other side;
  (d) flip `landed >= drawn` to `>` or to `<` -- `..._THE_BOUNDARY_IS_THE_DRAW_INSTANT_ITSELF`
      goes red, because its two legs straddle that instant by one second;
  (e) drop the `_stated_at(stated) >= drawn` guard on the already-disposed branch, or drop the
      branch entirely -- `..._A_WINDOW_ALREADY_DISPOSED_IS_NOT_ASKED_TO_DISPOSE_ITSELF_TWICE`
      goes red on one leg or the other. Both directions are asserted: a disposition stated for
      THIS window silences the sentence, and one stated for an EARLIER window does not;
  (f) drop the door out of the sentence, or rename it -- `..._THE_SENTENCE_NAMES_THE_DOOR` goes
      red. A caveat that reports a dead end and no move is the same stall as no caveat;
  (g) make the `except` re-raise instead of answering `""` --
      `..._AN_UNREADABLE_LEDGER_LOSES_THE_CAVEAT_AND_NEVER_THE_BINDING` goes red, because losing
      the sentence must never convert a successful bind into a traceback. It goes red on its THIRD
      leg only, and the first draft had no third leg: see that test's own correction.
"""

import json

from background import delivery_lane as dl

#: ONE id, two windows. The second draw is an hour after the first, which is the shape the sentence
#: exists for; the commit sits between them, which is the arrangement that produced the defect.
FIRST_DRAW = 1789000000.0
SECOND_DRAW = FIRST_DRAW + 3600
FOCUS = "an-id-drawn-twice-whose-landing-was-bound-once"


def _ledger(tmp_path, monkeypatch, **row):
    """A claims store and its draw ledger beside it, with one row arranged as the caller asks.

    Writes through `_ledger_path` rather than naming the `.draws.json` suffix, because the suffix
    is the module's business and a fixture that hard-coded it would go green against a reader that
    had stopped looking there.
    """
    claims = tmp_path / "claims.json"
    monkeypatch.setattr(dl, "CLAIMS_FILE", claims)
    base = {"first_drawn_at": FIRST_DRAW, "last_drawn_at": SECOND_DRAW}
    base.update(row)
    dl._ledger_path(claims).write_text(json.dumps({FOCUS: base}))
    return claims


def test_A_STALE_BIND_SPEAKS_AND_A_FRESH_ONE_IS_SILENT(tmp_path, monkeypatch):
    """One row, two arrangements, two different answers -- which no constant reading can give.

    Both legs over the SAME row on purpose: a warner wired to a constant passes whichever leg its
    constant happens to match and fails the other, so the partition is the control and neither leg
    is one on its own.
    """
    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW - 1800)
    stale = dl.landing_predates_this_window(FOCUS)
    assert stale, (
        "a commit that landed BEFORE this id's latest draw cannot clear the row, and the caller "
        "who has just been told the bind succeeded has no other way to learn it")

    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW + 1800)
    assert dl.landing_predates_this_window(FOCUS) == "", (
        "a landing INSIDE the current window settles it -- warning there would train the reader "
        "to ignore the sentence on the rows where it is true")


def test_THE_BOUNDARY_IS_THE_DRAW_INSTANT_ITSELF(tmp_path, monkeypatch):
    """A commit stamped at the draw second settles that window; one second earlier does not.

    `drawn_without_landing` clears a row on `last_landing_at >= drawn`, so this sentence must go
    quiet on exactly the same comparison. Legs one second either side, so a `>` or a `<` fires.
    """
    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW)
    assert dl.landing_predates_this_window(FOCUS) == "", (
        "the reader clears the row at `landed >= drawn`; a caveat that still spoke there would "
        "contradict the very function it is telling the caller about")

    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW - 1)
    assert dl.landing_predates_this_window(FOCUS), (
        "one second before the draw is the other side of the reader's own boundary")


def test_A_WINDOW_ALREADY_DISPOSED_IS_NOT_ASKED_TO_DISPOSE_ITSELF_TWICE(tmp_path, monkeypatch):
    """The sentence asks for a disposition, so a disposition of THIS window silences it.

    And a disposition of an EARLIER one does not, which is the same per-window rule `_disposition`
    holds: a sentence nobody was willing to restate against the new draw explains no window.
    """
    spent = {"commit": "0" * 40, "reason": "already on origin/main when this was drawn"}
    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW - 1800,
            premise_spent=dict(spent, at=SECOND_DRAW + 60))
    assert dl.landing_predates_this_window(FOCUS) == "", (
        "this window HAS been disposed, so the caller has already done the thing the sentence "
        "would ask of them")

    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW - 1800,
            premise_spent=dict(spent, at=FIRST_DRAW + 60))
    assert dl.landing_predates_this_window(FOCUS), (
        "a disposition stated in the FIRST window is not an answer about the second, and reading "
        "it as one is the across-windows fail-open this lane has already paid for once")


def test_THE_SENTENCE_NAMES_THE_DOOR(tmp_path, monkeypatch):
    """It carries the command that can settle the window, and both instants it is comparing."""
    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW - 1800)
    said = dl.landing_predates_this_window(FOCUS)
    assert "--premise-spent" in said, (
        "naming the dead end without the move is the stall; `--premise-spent` is the only "
        "per-window disposition, so it is the only honest next step to offer")
    assert FOCUS in said, "the caller is holding several ids; the sentence must say which"


def test_AN_UNREADABLE_LEDGER_LOSES_THE_CAVEAT_AND_NEVER_THE_BINDING(tmp_path, monkeypatch):
    """A store that will not answer answers `""`, and does not take the bind down with it.

    The fail-open direction is chosen here and nowhere else in this family: the sentence runs AFTER
    a binding that already succeeded, and a traceback would lose the binding to protect a warning.

    CORRECTION, KEPT BESIDE THE CLAIM. The first draft of this test wrote unparseable JSON into the
    ledger and asserted `""`, and that leg was an EQUIVALENCE, not a control: `seat_work_in_hand.
    _load` is a pure reader that already answers `{}` for absent AND unreadable, so the bytes never
    reached the `except` this test names. Making the `except` a bare `raise` left all six legs
    green -- the third cause of a green mutation, the mutation itself being a no-op. The corrupt
    file is kept as the FIRST leg because it is the realistic shape and the property is true of it;
    the raising collaborator below is what actually reaches the handler.
    """
    claims = tmp_path / "claims.json"
    monkeypatch.setattr(dl, "CLAIMS_FILE", claims)
    dl._ledger_path(claims).write_text("{not json at all")
    assert dl.landing_predates_this_window(FOCUS) == ""

    dl._ledger_path(claims).write_text(json.dumps({FOCUS: "a string where a row should be"}))
    assert dl.landing_predates_this_window(FOCUS) == ""

    def _refuses(_store):
        raise OSError("the ledger's own path could not be resolved")

    monkeypatch.setattr(dl, "_ledger_path", _refuses)
    assert dl.landing_predates_this_window(FOCUS) == "", (
        "a collaborator that RAISES is the only way into the handler, and the handler is the "
        "whole reason a successful bind cannot be turned into a traceback by a warning")


def test_THE_PRODUCTION_CALLER_PRINTS_IT_AND_STILL_EXITS_ZERO(tmp_path, monkeypatch, capsys):
    """The chain, not the rule: `--landed` itself must reach this, and must not turn it into a red.

    Every control above stays green while no production caller asks the question, which is the
    shape that has cost this project most often. `record_landing` is stubbed because it needs a
    real commit in a real repository and it is NOT the subject here -- the subject is the sentence
    and the branch that prints it, both of which run for real.
    """
    _ledger(tmp_path, monkeypatch, last_landing_at=SECOND_DRAW - 1800)
    monkeypatch.setattr(dl, "record_landing", lambda *a, **k: ["company/crm/churn_model.py"])
    monkeypatch.setattr(dl, "resolve_claim_id", lambda fid, **k: FOCUS)

    code = dl.main(["--landed", FOCUS, "--commit", "0" * 40])
    printed = capsys.readouterr().out
    assert "bound 1 path(s)" in printed, "the binding still happened and must still be reported"
    assert "--premise-spent" in printed, (
        "the caveat has to reach the CALLER, not just a test of the helper")
    assert code == 0, (
        "the bind succeeded; a non-zero here would teach the next tick to retry a command that "
        "did exactly what it was asked to do")
