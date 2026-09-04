"""A corrupt seen-hash file wedged the responder permanently, and nothing could tell.

THE CENSUS ROW: `.ntfy_responder_seen_hashes.json`, verdict `benign` -- correctly, because no write
to it can shorten an episode. It had never been asked the LOADER question, which is a different one
with a different consequence. Measured 2026-09-04 against a live prior of three hashes, following
the loaded value into `check_once`'s `set(seen_hashes)` and `seen_hashes.append(h)`:

    prior             loaded          set()       'h1' seen?  append       file after save
    LIVE (control)    [h1,h2,h3]      ok          True        ok           [h1,h2,h3,h_new]
    missing file      []              ok          False       ok           [h_new]        correct
    empty file        []              ok          False       ok           [h_new]        ALL LOST
    truncated         []              ok          False       ok           [h_new]        ALL LOST
    json null         None            TypeError   --          AttrError    !! save raised
    mapping           {'h1': 1}       ok          True(KEYS)  AttrError    !! save raised
    bare string       'h1h2h3'        ok          SUBSTRING   AttrError    ["h1h2h3"]
    [1, 2, 3]         [1,2,3]         ok          False       ok           [1,2,3,"h_new"]
    ["h1", 2]         ['h1',2]        ok          True        ok           ["h1",2,"h_new"]

`main()` binds `seen_hashes` ONCE and hands the same object to `check_once` every cycle, so the
TypeError at `set(None)` is raised on every poll that returns anything, caught by `main`'s bare
`except Exception`, logged, and retried against the same value forever -- and a restart re-reads the
same file. The responder stays up, keeps polling and answers nothing. That is the director's channel
going deaf with the daemon alive, which is the self-clearing shape the census exists to enumerate.

WHAT EACH LEG IS FOR, because a guard that refuses everything passes every refusal test:

  * the CONTROL leg drives the dedup working. Without it every assertion below is satisfiable by a
    responder whose seen-list does nothing at all.
  * the NO-WEDGE legs drive the real `check_once` over the whole partition. They fail on the
    pre-repair code by raising, which is the defect, not by an assertion about a return value.
  * the PRESERVATION leg is what makes absent and unreadable different FACTS rather than the same
    action taken twice: the rebuild must not be able to destroy bytes it could not read.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from background import action_needed as _action_needed  # noqa: E402
from background import (  # noqa: E402
    episode_prior,
    ntfy_utils,
)
from background import ntfy_responder as responder  # noqa: E402

#: Every member of the partition that is PRESENT and cannot be trusted. `null`, a mapping, a bare
#: string and a wrong-typed list all PARSE -- which is exactly why the old `except JSONDecodeError`
#: never saw them and why they reached `set()` and `.append` instead.
UNREADABLE_BYTES = pytest.mark.parametrize("raw", [
    pytest.param('["a", "b"', id="truncated"),
    pytest.param("", id="empty-file"),
    pytest.param("null", id="json-null"),
    pytest.param('{"a": 1}', id="a-mapping"),
    pytest.param('"abc"', id="a-bare-string"),
    pytest.param("[1, 2, 3]", id="list-of-ints"),
    pytest.param('["a", 2]', id="list-partly-strings"),
])

BODY = "Please kick off the overnight reconciliation batch now, thanks."


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Staging, the register, the watermark, the log, the sent-ids record and the seen-hash record
    all in tmp. `SEEN_HASHES_FILE` is an absolute path resolved at import from the REAL tree, so it
    is monkeypatched rather than derived -- a test that wrote the live one would be corrupting the
    running responder's own memory."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    (tmp_path / "docs" / "staging").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(_action_needed, "open_items", lambda *a, **k: [])
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", tmp_path / ".sent_ntfy_ids.json")
    monkeypatch.setattr(responder, "SEEN_HASHES_FILE", tmp_path / ".seen_hashes.json")
    monkeypatch.setattr(responder, "notify", lambda msg, **k: None)


def _feed(monkeypatch, msg_id, msg_time, message=BODY):
    class FakeResponse:
        text = json.dumps(
            {"event": "message", "id": msg_id, "time": msg_time, "message": message}
        )

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())


def _staged(tmp_path):
    """Files in the SCANNED staging root -- non-recursive, so quarantine does not count."""
    return list((tmp_path / "docs" / "staging").glob("from_rich_*.md"))


# ---------------------------------------------------------------------------------------
# 1. REACHABILITY. The dedup list is load-bearing, so "nothing was dropped" is a real claim.
# ---------------------------------------------------------------------------------------

def test_a_readable_prior_actually_suppresses_the_replay_of_that_message(tmp_path, monkeypatch):
    """CONTROL. The prior is DERIVED from the module -- the hash comes out of a first real run --
    rather than hand-built, because a hand-built operand would be testing my md5 against theirs.

    Two different message IDs, one body: the claim ledger's at-most-once is keyed to the id, so a
    second delivery under a new id can only be stopped by the CONTENT hash this file carries.
    """
    _feed(monkeypatch, "id-first", 100_000)
    _, hashes = responder.check_once(99_999, [])
    assert hashes, "the first run recorded no content hash -- the rest of this file proves nothing"
    responder._save_seen_hashes(hashes)
    assert len(_staged(tmp_path)) == 1

    prior, verdict = responder._load_seen_hashes()
    assert verdict == episode_prior.READABLE
    _feed(monkeypatch, "id-second", 100_001)
    responder.check_once(100_000, prior)

    assert len(_staged(tmp_path)) == 1, "the replay was staged again -- the dedup did nothing"


# ---------------------------------------------------------------------------------------
# 2. NO MEMBER OF THE PARTITION MAY WEDGE THE POLL. This is the defect, and it RAISES.
# ---------------------------------------------------------------------------------------

@UNREADABLE_BYTES
def test_no_unreadable_prior_can_stop_the_responder_answering(raw, tmp_path, monkeypatch):
    """The wedge leg. Pre-repair, `null` raised TypeError at `set(seen_hashes)` and the mapping and
    the bare string raised AttributeError at `.append` -- inside `main`'s catch-all, on every poll,
    forever. A responder that is up and answering nothing is worse than one that died."""
    responder.SEEN_HASHES_FILE.write_text(raw)
    prior, verdict = responder._load_seen_hashes()
    assert verdict == episode_prior.UNREADABLE, "fixture must actually be unreadable"

    _feed(monkeypatch, "his-steer", 100_000)
    responder.check_once(99_999, prior)          # pre-repair: raises

    assert len(_staged(tmp_path)) == 1, "the message was lost as well as the dedup memory"


@UNREADABLE_BYTES
def test_the_save_that_follows_an_unreadable_read_never_raises_or_writes_junk(raw, monkeypatch):
    """The write half. `main` saves the list every cycle, so a value that survives `check_once` and
    dies at the save is the same wedge one line later -- and a list holding a non-string member is
    junk written BACK, which is how `["a", 2]` outlives the corruption that made it."""
    responder.SEEN_HASHES_FILE.write_text(raw)
    prior, _ = responder._load_seen_hashes()
    prior.append("deadbeef")
    responder._save_seen_hashes(prior)

    written = json.loads(responder.SEEN_HASHES_FILE.read_text())
    assert all(isinstance(h, str) for h in written), f"a corrupt member was persisted: {written}"
    assert not responder.SEEN_HASHES_FILE.with_name(
        responder.SEEN_HASHES_FILE.name + ".tmp").exists(), "the atomic save left its tmp behind"


# ---------------------------------------------------------------------------------------
# 3. ABSENT AND UNREADABLE ARE DIFFERENT FACTS, and the difference is on disk.
# ---------------------------------------------------------------------------------------

def test_a_missing_seen_hash_file_is_told_apart_from_an_unreadable_one(monkeypatch):
    """Same ACTION -- start with an empty dedup list -- and not the same ANSWER. Collapsing them is
    how the distinction was lost the first time: a first run and a destroyed record read alike."""
    absent, absent_verdict = responder._load_seen_hashes()
    responder.SEEN_HASHES_FILE.write_text("null")
    unreadable, unreadable_verdict = responder._load_seen_hashes()

    assert absent == unreadable == []
    assert absent_verdict != unreadable_verdict
    assert (absent_verdict, unreadable_verdict) == (episode_prior.ABSENT, episode_prior.UNREADABLE)


@UNREADABLE_BYTES
def test_the_unreadable_bytes_are_preserved_before_the_rebuild_overwrites_them(raw, monkeypatch):
    """The read-modify-write half of this row. The loader hands back `[]` and the very next save
    writes that `[]` plus one hash over the record, so without this the only evidence of what the
    file held is gone one cycle later, before anyone can look at it."""
    responder.SEEN_HASHES_FILE.write_text(raw)

    kept = episode_prior.preserve_unreadable(responder.SEEN_HASHES_FILE)
    responder._save_seen_hashes(["fresh"])

    assert kept is not None
    assert responder.SEEN_HASHES_FILE.with_name(kept).read_text() == raw
    assert json.loads(responder.SEEN_HASHES_FILE.read_text()) == ["fresh"]


def test_preserving_twice_keeps_the_FIRST_loss_and_not_the_second(monkeypatch):
    """The first loss is the one that still holds the real record. A second corruption an hour
    later must not overwrite the only copy of it."""
    responder.SEEN_HASHES_FILE.write_text('["the-real-record"')
    first = episode_prior.preserve_unreadable(responder.SEEN_HASHES_FILE)
    responder.SEEN_HASHES_FILE.write_text("null")
    second = episode_prior.preserve_unreadable(responder.SEEN_HASHES_FILE)

    assert first != second
    assert responder.SEEN_HASHES_FILE.with_name(first).read_text() == '["the-real-record"'


def test_the_five_hand_rolled_preserve_copies_now_go_through_one_loop(tmp_path):
    """The helper replaced five copies of this loop, and a sixth would be written the next time
    somebody repairs a loader. Keyed to the PROPERTY -- each carrier still preserves, and does it
    via the shared helper -- by patching the helper and watching every wrapper stop preserving.

    Subjects come from the tree, not from a list this test also owns: a hard-coded roster is how a
    seventh wrapper joins silently.
    """
    import background.dispatcher as dispatcher
    import background.staging_watcher as staging_watcher
    import background.weekly_rhythm as weekly_rhythm

    wrappers = [
        (dispatcher, "_preserve_unreadable_seen", "_SEEN_FILE"),
        (staging_watcher, "_preserve_unreadable_seen", "STATE_FILE"),
        (ntfy_utils, "_preserve_unreadable_sent_ids", "SENT_IDS_FILE"),
        (weekly_rhythm, "_preserve_unreadable_baton", "BATON"),
    ]
    for i, (mod, fn_name, path_attr) in enumerate(wrappers):
        target = tmp_path / f"carrier{i}.json"
        target.write_text("null")
        original = getattr(mod, path_attr)
        try:
            setattr(mod, path_attr, target)
            assert getattr(mod, fn_name)() is not None, f"{mod.__name__}.{fn_name} preserved nothing"
        finally:
            setattr(mod, path_attr, original)
        assert not target.exists(), f"{mod.__name__}.{fn_name} left the unreadable bytes in place"
        assert target.with_name(target.name + ".unreadable").read_text() == "null"
