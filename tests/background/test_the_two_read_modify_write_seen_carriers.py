"""The two seen-set carriers whose recovery from an unreadable file DESTROYED the file.

WHY THESE TWO WERE RANKED AHEAD OF THE OTHER 29 UNASKED `benign` CENSUS ROWS. Both are
read-modify-write over the whole record: the loader returns a fresh empty container and the very
next save writes it back, so a corrupt file is not a lost suppression, it is a wiped record. And
`benign` on the self-clearing-alarm census answered only "can a write shorten an EPISODE" -- these
carriers hold no episode, so they were never asked whether they could tell ABSENT from
PRESENT-BUT-UNREADABLE. They could not.

MEASURED BEFORE THE REPAIR, each against a live prior (the tables are in the two loaders'
docstrings). `staging_watcher.load_seen` had no `try` at all and RAISED on three members --
`main()` calls it as its first act, so a half-written state file killed the watcher at startup and
the only symptom was staging going quiet, which looks exactly like an empty queue. The three that
did not raise returned a set of the wrong things and RESUMED from it, making the whole staging
backlog read as new. `dispatcher._load_seen` was annotated `-> dict[str, str]` and returned `None`
for `null` and a list for `[1, 2, 3]`, both of which parse and so were never seen by its
`except (json.JSONDecodeError, Exception)` -- which is only `except Exception` anyway.

EVERY LEG ASSERTS THE TWO ANSWERS **DIFFER**, never that they match, and each carrier has a
REACHABILITY leg proving a live prior reaches a third answer. Without those, "differs" is satisfied
by a loader that answers UNREADABLE to everything -- which for the watcher means reseeding on every
single start and never notifying anything again.
"""
from __future__ import annotations

import json

import pytest

from background import dispatcher, staging_watcher
from background.episode_prior import ABSENT, READABLE, UNREADABLE

#: The whole partition. `null` and `[1, 2, 3]` PARSE -- which is exactly why an `except
#: JSONDecodeError` never saw them -- and `["x", 2]` is a list that is only PARTLY right, the
#: member that a plain `isinstance(parsed, list)` screen still admits.
UNREADABLE_RAW = pytest.mark.parametrize(
    "raw",
    [
        pytest.param("", id="empty-file"),
        pytest.param('{"a": "b"', id="truncated"),
        pytest.param("null", id="json-null"),
        pytest.param("[1, 2, 3]", id="list-of-non-strings"),
        pytest.param('["x", 2]', id="list-partly-strings"),
    ],
)

LIVE_MAP = {"from_rich_a.md": "normal", "from_rich_b.md": "urgent"}
LIVE_LIST = ["from_rich_a.md", "from_rich_b.md"]


# =====================================================================================
# staging_watcher -- the one that could not START
# =====================================================================================

@pytest.fixture
def watch_state(tmp_path, monkeypatch):
    path = tmp_path / ".staging_watcher_seen.json"
    monkeypatch.setattr(staging_watcher, "STATE_FILE", path)
    return path


@UNREADABLE_RAW
def test_no_partition_member_can_stop_the_watcher_starting(raw, watch_state):
    """THE CRASH HALF. `main()` calls `load_seen()` first, so any raise here is the daemon dead
    before it does anything, with staging silently unwatched. MUTANT: restore the old body
    (`set(json.loads(...))` with no try) and three of these five raise."""
    watch_state.write_text(raw, encoding="utf-8")

    seen, verdict = staging_watcher.load_seen()  # must not raise

    assert verdict == UNREADABLE
    assert seen is None, "an untrustworthy record must not be resumed from"


def test_the_watcher_tells_a_first_run_from_a_destroyed_one(watch_state):
    """ABSENT and UNREADABLE take the same ACTION (seed, announce nothing) and are DIFFERENT
    ANSWERS, which is what lets `main` alarm on one and stay quiet on the other. MUTANT: return a
    bare `None` for both and this fires."""
    assert not watch_state.exists()
    assert staging_watcher.load_seen() == (None, ABSENT)

    watch_state.write_text("null", encoding="utf-8")
    assert staging_watcher.load_seen() == (None, UNREADABLE)


def test_a_readable_seen_set_is_resumed_from(watch_state):
    """REACHABILITY NULL CONTROL. Without it every leg above passes for a watcher that reseeds on
    every start -- which would announce nothing, ever, and look perfectly healthy doing it."""
    watch_state.write_text(json.dumps(LIVE_LIST), encoding="utf-8")

    seen, verdict = staging_watcher.load_seen()

    assert verdict == READABLE
    assert seen == set(LIVE_LIST)


def test_an_empty_seen_set_is_a_fact_and_not_a_failure_to_read_one(watch_state):
    """`[]` is a READABLE empty record; an empty FILE is not. A loader that lumps them re-seeds a
    watcher whose queue legitimately drained. MUTANT: treat falsy-parsed as unreadable."""
    watch_state.write_text("[]", encoding="utf-8")
    assert staging_watcher.load_seen() == (set(), READABLE)

    watch_state.write_text("", encoding="utf-8")
    assert staging_watcher.load_seen() == (None, UNREADABLE)


def test_the_watchers_recovery_does_not_destroy_what_it_is_recovering_from(watch_state):
    """THE DESTRUCTIVE HALF, in the exact order `main` performs it: preserve, THEN reseed. The
    reseed is a whole-set overwrite, so without the preserve the only record of what had already
    been announced is gone -- destroyed by the recovery itself. MUTANT: drop the
    `_preserve_unreadable_seen()` call from `main` and the original bytes are unrecoverable."""
    watch_state.write_text('["announced_already.md", 2]', encoding="utf-8")

    preserved = staging_watcher._preserve_unreadable_seen()
    staging_watcher.save_seen({"whatever_is_in_staging_now.md"})

    assert preserved is not None
    kept = watch_state.with_name(preserved)
    assert "announced_already.md" in kept.read_text(encoding="utf-8")


def test_a_second_loss_never_overwrites_the_first_preserved_copy(watch_state):
    """The FIRST loss is the one that still holds the filenames. MUTANT: use a fixed suffix and
    the second corruption -- an empty file, most likely -- overwrites the evidence."""
    watch_state.write_text('["first_loss.md", 2]', encoding="utf-8")
    first = staging_watcher._preserve_unreadable_seen()
    watch_state.write_text("", encoding="utf-8")
    second = staging_watcher._preserve_unreadable_seen()

    assert first != second
    assert "first_loss.md" in watch_state.with_name(first).read_text(encoding="utf-8")


# =====================================================================================
# dispatcher -- the one annotated `-> dict[str, str]` that returned None and lists
# =====================================================================================

@pytest.fixture
def disp_state(tmp_path, monkeypatch):
    path = tmp_path / ".dispatcher_seen.json"
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", path)
    return path


@UNREADABLE_RAW
def test_the_dispatcher_always_returns_something_it_can_subscript(raw, disp_state):
    """The caller's next line is `seen[path.name] = classification`. MUTANT: restore the old body
    and `null` returns None (TypeError on assignment) and the two lists return lists (TypeError:
    list indices must be integers) -- on every staged file the dispatcher handles."""
    disp_state.write_text(raw, encoding="utf-8")

    seen, verdict = dispatcher._load_seen()

    assert isinstance(seen, dict), "a function annotated -> dict returned something else"
    assert verdict == UNREADABLE
    seen["from_rich_new.md"] = "normal"  # the caller's actual next move, must not raise


def test_the_dispatcher_tells_a_first_run_from_a_wiped_one(disp_state):
    """Both give `{}` so the caller cannot crash, AND the verdicts differ so the wipe is visible.
    MUTANT: return only the dict and the distinction is laundered away again."""
    assert not disp_state.exists()
    assert dispatcher._load_seen() == ({}, ABSENT)

    disp_state.write_text("[1, 2, 3]", encoding="utf-8")
    assert dispatcher._load_seen() == ({}, UNREADABLE)


def test_a_readable_classification_memory_is_kept(disp_state):
    """REACHABILITY NULL CONTROL. A dispatcher that answered UNREADABLE to everything would
    re-classify and re-route every staged from_rich on every restart, and pass every leg above."""
    disp_state.write_text(json.dumps(LIVE_MAP), encoding="utf-8")

    seen, verdict = dispatcher._load_seen()

    assert verdict == READABLE
    assert seen == LIVE_MAP


def test_a_mapping_that_is_not_this_record_is_still_readable(disp_state):
    """Deliberately NOT unreadable, and the contrast with the watcher's list screen is the point:
    a seen-map's keys are arbitrary filenames, so there is no schema here to violate. Unknown keys
    are simply files we have not seen since. Pinned so a later 'tightening' has to argue with it."""
    disp_state.write_text('{"other": 1}', encoding="utf-8")
    assert dispatcher._load_seen() == ({"other": 1}, READABLE)


def test_the_dispatchers_recovery_does_not_destroy_the_classifications(disp_state):
    """Same destructive half, same order as `main`. The dispatcher's `_save_seen` writes the whole
    map, so the first save after a corrupt read is what makes the loss permanent."""
    disp_state.write_text('{"routed_already.md": "urgent"', encoding="utf-8")

    preserved = dispatcher._preserve_unreadable_seen()
    dispatcher._save_seen({"a_new_one.md": "normal"})

    assert preserved is not None
    assert "routed_already.md" in disp_state.with_name(preserved).read_text(encoding="utf-8")
