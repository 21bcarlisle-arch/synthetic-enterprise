"""A commit on a path an item asked only to READ may not retire that item.

THE DEFECT (measured 2026-09-22 on the live ledger, and it is the first time this ledger failed
towards DONE). `the-settlement-ceiling-can-move-now-that-its-curve-has-landed` was disposed
`landed_elsewhere` citing `edc1b14df` — a commit whose own message says `NOT TOUCHED:
simulation/net_new_acquisition.py` in capitals, which is the item's entire subject. The match was
`background/publish_freshness.py`, a path the item named exactly once, to read a constant out of;
and the same item's path set also held `simulation/premise_population.py`, which it named only
inside an explicit `DO NOT TOUCH` clause. So a commit to a file the item FORBADE would have
credited it too. An afternoon's finished fit was dropped and the ledger published, as evidence,
three path names the commit had not touched.

THE DIRECTION FILE IS AN INPUT TO THIS MECHANISM (director, same day): the words written in an
item's `what` become the ledger's path set, so prose that carefully names what NOT to touch was
what supplied the false disposition. Naming a path to protect it made it creditable.

WHY THIS IS ONE TEST AND NOT TWO. A reader that treats EVERY mentioned path as a subject — which
is what shipped — passes every assertion about a true match. A reader that treats NONE of them as
subjects passes every assertion about a true refusal. Either of those is a control that cannot
fail, and this project has walked into that trap through three separate doors in one afternoon.
So the partition is asserted in ONE statement: an item whose CHANGED path was touched must be
credited, and an item whose READ-ONLY path was touched must not, from one ledger and one git.

THE MUTATIONS THIS FILE CLAIMS, both one-way and both red on the partition line:
  (a) `_claim_subject_paths` returns `_claim_paths` unfiltered — the shipped reading. The
      read-only row is credited and the partition line reds on its half.
  (b) `_claim_subject_paths` returns `[]`, or `_path_roles` classifies every occurrence as a
      mention. The changed row falls to the residual and the partition line reds on the other.
  (c) drop the `_NEGATED_CHANGE` clause from `_READ_ONLY_GOVERNORS`, so `DO NOT REWRITE <path>`
      matches `rewrite` in the CHANGE vocabulary — `..._A_NEGATED_CHANGE_VERB_FORBIDS` reds.
      This is not hypothetical: the first draft of the classifier had exactly this hole, and it
      was found by printing the whole live ledger's roles rather than by rereading the regex.
  (d) put `paths[:3]` back in either evidence string — `..._THE_EVIDENCE_NAMES_THE_PATH_THAT
      _ACTUALLY_MATCHED` reds, because the matched path sorts fourth there on purpose.

WHAT IS NOT CLAIMED. The role reading is ONE-SIDED by construction: no governor found leaves a
path a SUBJECT, which is what every path was before this existed. So a gap in the read vocabulary
can only fail to remove an over-credit, never invent one, and there is no mutation of the
vocabulary's COMPLETENESS to write — the honest statement of that limit is in `_path_roles` and
the cost direction is stated there too (an under-credit costs one redraw; an over-credit retires
live work).
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl

#: Synthetic ids. NOT the live ledger's -- a control pinned to today's rows goes green the moment
#: the sweep gets quieter, which is the failure being fixed wearing a better name.
CHANGED_ID = "an-item-whose-changed-path-a-sibling-touched"
READ_ONLY_ID = "an-item-whose-read-only-path-a-sibling-touched"
FORBIDDEN_ID = "an-item-that-forbids-the-path-the-sibling-touched"
HOLDER_ID = "the-row-that-actually-landed-it"

NOW = 1789000000.0
#: Older than `CLAIM_STALE_SECONDS`, so every window below has closed, and inside the 24h horizon.
DRAWN_AT = NOW - 4 * 3600
IN_WINDOW = DRAWN_AT + 900

#: Paths this repo tracks, so the readings below hold on any checkout of it. Four, because the
#: evidence leg needs the matched path to sort OUTSIDE the first three.
SUBJECT_PATH = "background/delivery_lane.py"
READ_PATH = "background/publish_freshness.py"
FORBIDDEN_PATH = "simulation/premise_population.py"
LATE_PATH = "tools/surgical_land.py"
MIDDLE_PATHS = ["docs/design/maturity_map.yaml", "site/index.html"]

SHA = "5544332211009988776655443322110099887766"
LATE_SHA = "ab12cd34ef567890ab12cd34ef567890ab12cd34"


def _ledger(tmp_path, rows: dict):
    tmp_path.mkdir(parents=True, exist_ok=True)
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def _row(named_paths):
    return {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT,
            "named_paths": list(named_paths)}


def _holder(instant: float, paths):
    """The sibling row: drawn before this window and credited with `instant`.

    Its own draw is older so it is not itself a swept row under test, and its landing is what
    makes `_bound_by` name it as the holder of that second.
    """
    return {"first_drawn_at": DRAWN_AT - 7200, "last_drawn_at": DRAWN_AT - 7200,
            "last_landing_at": instant, "last_landing_paths": list(paths)}


def _fake_git(commits, tracked):
    """A git that applies the pathspec ITSELF and prints `--name-only` under each commit.

    PRINTING THE FILENAMES IS THE POINT OF THIS FAKE rather than a detail copied from the real
    thing. The subject reads the intersection out of that output and both the credit leg and the
    evidence leg turn on it, so a fake that printed headers only would grade neither and would go
    green on a subject that had lost the intersection entirely.

    STRICTER THAN REAL GIT: `None` for any question not in the table, so this stand-in can only
    make the subject refuse MORE than the real thing would. A fake more permissive than its
    subject is how a fail-open becomes a green suite.
    """
    def fake(*args, cwd=None):
        if args and args[0] == "ls-files":
            return "\n".join(tracked) + "\n"
        if args and args[0] == "log":
            wanted = list(args[args.index("--") + 1:]) if "--" in args else []
            if wanted == [dl.DIRECTION_RECORD_PATH]:
                return ""
            out = []
            for sha, when, subject, paths in commits:
                hit = [p for p in paths if p in wanted] if wanted else list(paths)
                if wanted and not hit:
                    continue
                out.append("{}\x1f{:.0f}\x1f{}".format(sha, when, subject))
                out.extend(hit)
            return "\n".join(out) + "\n" if out else ""
        return None
    return fake


@pytest.fixture(autouse=True)
def _no_cached_direction_history():
    """`_direction_history_text` caches for the life of the PROCESS, and a test suite is one.

    Cleared on both sides so this file neither inherits another test's fake nor leaves one behind.
    """
    dl._reset_direction_history()
    yield
    dl._reset_direction_history()


#: The prose each synthetic item carries, written the way this project's direction actually reads
#: -- a change verb over the subject, and the read-only paths carried by `from` and by an explicit
#: forbidding clause. Fed through `_path_roles` UNSTUBBED: the roles below are derived from these
#: sentences by the code under test, not asserted into it.
PROSE = {
    CHANGED_ID: (
        "Rewrite the window reading in `{subject}` so it can refuse. "
        "Take the cadence from `{read}`.".format(subject=SUBJECT_PATH, read=READ_PATH)),
    READ_ONLY_ID: (
        "Move the ceiling in `{subject}` off its historical value, deriving the new one "
        "from `{read}`.".format(subject=FORBIDDEN_PATH, read=READ_PATH)),
    FORBIDDEN_ID: (
        "Repair the strand half in `{subject}`. DO NOT REWRITE `{read}`: a live lane holds "
        "it.".format(subject=SUBJECT_PATH, read=READ_PATH)),
}


def _prose_git(tmp_path, monkeypatch, rows, commits, tracked):
    store = _ledger(tmp_path, rows)
    monkeypatch.setattr(dl, "_item_text", lambda fid: PROSE.get(fid, ""))
    monkeypatch.setattr(dl, "_git", _fake_git(commits, tracked))
    return store


def test_THE_PARTITION_a_changed_path_credits_and_a_read_only_path_does_not(
        tmp_path, monkeypatch):
    """One ledger, one commit, two items that both name the path it touched. Opposite answers.

    THIS IS THE CONTROL THE REPAIR TURNS ON and the reason it is a single statement is in the
    module docstring: a reader that keeps every mentioned path passes the first half alone, and a
    reader that keeps none passes the second half alone. Together they are a partition no constant
    answer survives.

    BOTH ROWS NAME `{read}` AND NEITHER IS DRAWN ON IT. What separates them is only what their
    prose ASKED for it -- a source to take a cadence from in one, the same sentence's read-only
    object in the other -- and the commit touches nothing else. So this cannot be passed by a
    reader that discriminates on path names, on path counts, or on the ledger at all.
    """
    store = _prose_git(
        tmp_path, monkeypatch,
        rows={CHANGED_ID: _row([SUBJECT_PATH, READ_PATH]),
              READ_ONLY_ID: _row([FORBIDDEN_PATH, READ_PATH]),
              HOLDER_ID: _holder(IN_WINDOW, [SUBJECT_PATH, READ_PATH])},
        commits=[(SHA, IN_WINDOW, "one cadence, two homes", [SUBJECT_PATH, READ_PATH])],
        tracked=[SUBJECT_PATH, READ_PATH, FORBIDDEN_PATH, LATE_PATH] + MIDDLE_PATHS)

    changed = dl.disposition_of(CHANGED_ID, path=store)
    read_only = dl.disposition_of(READ_ONLY_ID, path=store)

    assert (changed["disposition"] == dl.LANDED_ELSEWHERE
            and read_only["disposition"] == dl.NOT_DONE), (changed, read_only)


def test_THE_REFUSAL_SAYS_THE_PATHS_WERE_NAMED_AND_NOT_THAT_NONE_WERE(tmp_path, monkeypatch):
    """An item that asks for nothing to change is not an item whose prose named nothing.

    THE FOURTH-VOICE SHAPE, one layer further out (`_tracked_files`, 2026-09-18). Narrowing the
    credit query to the subject set made the residual's NO-PATHS branch reachable a second way,
    and that branch's reason says *this item's prose names no tracked path*. Published over an
    item that named two and asked for neither to be changed, that sentence blames the prose for
    being precise and sends the reader hunting for text that was never missing. A right
    disposition with a fabricated cause is not a fail-closed check.

    KEYED TO THE TWO FACTS THE READER ACTS ON -- that paths WERE named, and that the reason is
    about what was asked for them -- not to the wording around them.
    """
    store = _prose_git(
        tmp_path, monkeypatch,
        rows={READ_ONLY_ID: _row([READ_PATH])},
        commits=[(SHA, IN_WINDOW, "one cadence, two homes", [READ_PATH])],
        tracked=[SUBJECT_PATH, READ_PATH, FORBIDDEN_PATH])

    got = dl.disposition_of(READ_ONLY_ID, path=store)

    assert got["disposition"] == dl.NOT_DONE, got
    assert READ_PATH in got["evidence"] and "CHANGED" in got["evidence"], got
    assert "names no tracked path" not in got["evidence"], got


def test_A_NEGATED_CHANGE_VERB_FORBIDS_RATHER_THAN_ASKS(tmp_path, monkeypatch):
    """`DO NOT REWRITE <path>` must not be read as `rewrite <path>`.

    MEASURED, NOT IMAGINED. The first draft of `_path_roles` had exactly this hole: the forbidding
    clause this repo's direction prose actually writes is `READ FIRST, DO NOT REWRITE: the shared
    tree holds <path>`, and with `rewrite` in the change vocabulary and no negation clause, all
    three paths that item forbade came back as subjects. It was found by printing the whole live
    ledger's roles at real inputs, which is the step that catches a formula no amount of rereading
    the regex does.

    ASSERTED THROUGH THE DISPOSITION, not against `_path_roles` directly: a negation the extractor
    understands and the credit join never sees is not a repair.
    """
    store = _prose_git(
        tmp_path, monkeypatch,
        rows={FORBIDDEN_ID: _row([SUBJECT_PATH, READ_PATH]),
              HOLDER_ID: _holder(IN_WINDOW, [READ_PATH])},
        commits=[(SHA, IN_WINDOW, "the live lane's own repair", [READ_PATH])],
        tracked=[SUBJECT_PATH, READ_PATH, FORBIDDEN_PATH])

    got = dl.disposition_of(FORBIDDEN_ID, path=store)

    assert got["disposition"] == dl.NOT_DONE, got


def test_THE_EVIDENCE_NAMES_THE_PATH_THAT_ACTUALLY_MATCHED(tmp_path, monkeypatch):
    """The reader is told which of this item's paths moved, not which three sort first.

    THE SENTENCE THAT WAS PUBLISHED ON THE RETIREMENT THAT CAUSED THIS REPAIR read *touched
    simulation/net_new_acquisition.py, ...* — the one path the commit's message says in capitals
    it did not touch. `", ".join(paths[:3])` names the QUESTION, and a reader takes it for the
    answer.

    THE FIXTURE IS BUILT SO THE TWO READINGS CANNOT AGREE: five subject paths, and the only one
    the commit touches sorts LAST. `paths[:3]` therefore cannot contain it and cannot be mistaken
    for a pass. Asserted in both directions — the matched path present AND the unmatched leader
    absent — because either alone is satisfied by a string that names everything.
    """
    named = sorted([SUBJECT_PATH, READ_PATH, LATE_PATH] + MIDDLE_PATHS)
    assert named[-1] == LATE_PATH and LATE_PATH not in named[:3], named
    prose = "Rewrite {} and {}.".format(", ".join(f"`{p}`" for p in named[:-1]),
                                        "`{}`".format(LATE_PATH))
    monkeypatch.setitem(PROSE, CHANGED_ID, prose)
    store = _prose_git(
        tmp_path, monkeypatch,
        rows={CHANGED_ID: _row(named),
              HOLDER_ID: _holder(IN_WINDOW, [LATE_PATH])},
        commits=[(SHA, IN_WINDOW, "the landing door names its refusal", [LATE_PATH])],
        tracked=named + [FORBIDDEN_PATH])

    got = dl.disposition_of(CHANGED_ID, path=store)

    assert got["disposition"] == dl.LANDED_ELSEWHERE, got
    assert LATE_PATH in got["evidence"] and named[0] not in got["evidence"], got


def test_AN_ITEM_WHOSE_PROSE_IS_GONE_KEEPS_EVERY_PATH_IT_STAMPED(tmp_path, monkeypatch):
    """No text is no ROLES, and a row must not become un-creditable because its item expired.

    THE NARROWING APPLIES WHERE ITS EVIDENCE EXISTS AND NOWHERE ELSE. `_claim_subject_paths`
    reads roles out of the item's prose, and `_item_text` goes quiet when the item leaves both
    live stores and the history reach-back. Reading that silence as "nothing was asked to be
    changed" would retire the credit half for every legacy row at once — fail-closed on the
    disposition and fail-SILENT on the work, which is the direction this whole module keeps
    having to be pulled back from.

    IT ALSO PINS THE NO-REGRESSION CLAIM. This is the pre-2026-09-22 reading, kept exactly where
    it cannot be improved on, so a future narrowing that quietly widens to unreadable rows reds.
    """
    store = _ledger(tmp_path, {CHANGED_ID: _row([SUBJECT_PATH, READ_PATH]),
                               HOLDER_ID: _holder(IN_WINDOW, [READ_PATH])})
    monkeypatch.setattr(dl, "_item_text", lambda fid: "")
    monkeypatch.setattr(dl, "_git", _fake_git(
        [(LATE_SHA, IN_WINDOW, "somebody else's landing", [READ_PATH])],
        tracked=[SUBJECT_PATH, READ_PATH]))

    got = dl.disposition_of(CHANGED_ID, path=store)

    assert got["disposition"] == dl.LANDED_ELSEWHERE, got


def test_A_STAMPED_ROW_STILL_ASKS_GIT_ONLY_THE_COMMIT_QUESTION(tmp_path, monkeypatch):
    """The roles reading may not cost a `git ls-files` a stamped row never needed.

    `_claim_paths` promises that a row carrying the draw-time stamp is answered from the ledger
    and "stays both free and unraisable", and `drawn_without_landing` asks this of every swept
    row to build the orientation brief. The first draft of `_claim_subject_paths` broke that
    promise by re-confirming the prose against `_tracked_files`, which also moved WHICH command a
    dead git is reported as having failed -- `ls-files` instead of `log` -- and an existing
    control caught it. `known=` is why it is a property and not a coincidence.
    """
    asked: list[str] = []
    inner = _fake_git([(SHA, IN_WINDOW, "the landing", [SUBJECT_PATH])],
                      tracked=[SUBJECT_PATH, READ_PATH])

    def counting(*args, cwd=None):
        asked.append(args[0] if args else "")
        return inner(*args, cwd=cwd)

    store = _ledger(tmp_path, {CHANGED_ID: _row([SUBJECT_PATH, READ_PATH]),
                               HOLDER_ID: _holder(IN_WINDOW, [SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_item_text", lambda fid: PROSE[CHANGED_ID])
    monkeypatch.setattr(dl, "_git", counting)

    got = dl.disposition_of(CHANGED_ID, path=store)

    assert got["disposition"] == dl.LANDED_ELSEWHERE, got
    assert "ls-files" not in asked, asked
