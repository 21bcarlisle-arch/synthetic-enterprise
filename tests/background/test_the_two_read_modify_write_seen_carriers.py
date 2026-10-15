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

The dispatcher's half was deleted with the dispatcher (inbound NTFY route retired 2026-10-15). The
helper-delegation control moved here from the responder's loader tests, which went with it.
"""
from __future__ import annotations

import json

import pytest

from background import staging_watcher
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
# The helper a fourth call site was about to fork
# =====================================================================================

def test_every_carriers_preservation_goes_through_the_one_helper(tmp_path, monkeypatch):
    """Byte-identical private `_preserve_unreadable_*` copies were folded into
    `episode_prior.preserve_unreadable`. Keyed to the PROPERTY, not to the source text: patch the
    central helper and each carrier must change its answer. MUTANT: re-inline the body and its
    row fails. (`ntfy_utils`'s sent-ids carrier left this list 2026-10-15, deleted with its
    last reader.)"""
    import background.episode_prior as ep

    # REDIRECT THE REAL PATHS FIRST: a re-inlined body ignores the spy and performs a REAL
    # `Path.replace`, which once moved a live state file out of the working tree.
    monkeypatch.setattr(staging_watcher, "STATE_FILE", tmp_path / ".staging_watcher_seen.json")

    calls: list[str] = []
    original = ep.preserve_unreadable

    def spy(path):
        calls.append(str(path))
        return "SENTINEL"

    carriers = (
        (staging_watcher, "_preserve_unreadable_seen"),
    )
    for module, helper in carriers:
        # Patch both the central name and any import-time binding, so a carrier added here with
        # either import style is tested as a property and not as one import style.
        ep.preserve_unreadable = spy
        rebound = hasattr(module, "preserve_unreadable")
        if rebound:
            module.preserve_unreadable = spy
        try:
            answer = getattr(module, helper)()
        finally:
            ep.preserve_unreadable = original
            if rebound:
                module.preserve_unreadable = original
        assert answer == "SENTINEL", (
            f"{module.__name__}.{helper} does not delegate to episode_prior.preserve_unreadable"
        )

    assert len(calls) == len(carriers)
