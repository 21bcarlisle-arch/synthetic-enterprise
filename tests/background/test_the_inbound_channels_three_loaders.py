"""The three loaders on the only inbound route the director has, asked the loader question.

WHY THESE THREE TOGETHER, RATHER THAN ONE MORE CENSUS ROW. The Lane 0 direction ranks the unasked
`benign` census rows by what the carrier's WRITER does, and named `.ntfy_responder_seen_hashes.json`
as a read-modify-write. Reading `background/ntfy_responder.py` to rank it moved the unit of work:
that one daemon holds THREE unasked carriers, they are the watermark, the replay-dedup and the
flood window, and a defect in the first two is not a lost suppression -- it is the director's
messages not arriving.

MEASURED BEFORE THE REPAIR (the full tables are in the three loaders' docstrings):

    _load_since        json `null` / `[1, 2, 3]` / `["x", 2]` -> RAISED TypeError, UNCAUGHT.
                       That call is the FIRST statement of `main()` with no try above it, so the
                       responder did not start AT ALL.
    _load_seen_hashes  `null` -> None and `{"other": 1}` -> a dict, both from a function annotated
                       `-> list[str]`. `check_once` opens with `set(seen_hashes)` on every
                       successful poll: None raised there, `main`'s loop caught it and logged it,
                       and the responder went on polling every 20s forever without advancing the
                       watermark or processing a message -- alive, warm and deaf.
    _load_rate_state   sound in every direction, because it already screened `isinstance(dict)`.
                       Recorded rather than assumed; the prediction that it needed the reason and
                       not the repair is in the pre-registration and it held.

EVERY LEG ASSERTS THE TWO ANSWERS **DIFFER**, never that they match, and each carrier carries a
REACHABILITY leg proving a live prior reaches a third answer. Without those, "differs" is satisfied
by a loader that answers UNREADABLE to everything -- which for the watermark means alarming on
every single start and teaching the director to ignore it.
"""
from __future__ import annotations

import json

import pytest

from background import dispatcher, ntfy_responder, ntfy_utils, staging_watcher
from background.episode_prior import ABSENT, READABLE, UNREADABLE

#: The whole partition. `null`, `[1, 2, 3]` and `["x", 2]` all PARSE, which is exactly why an
#: `except JSONDecodeError` never saw them and why three of them reached a subscript and raised.
UNREADABLE_RAW = pytest.mark.parametrize(
    "raw",
    [
        pytest.param("", id="empty-file"),
        pytest.param('{"since": 12', id="truncated"),
        pytest.param("null", id="json-null"),
        pytest.param("[1, 2, 3]", id="list-of-non-strings"),
        pytest.param('["x", 2]', id="list-partly-strings"),
    ],
)

LIVE_SINCE = 1_756_900_000.0
LIVE_HASHES = ["9b1c0f", "44ade2"]


@pytest.fixture
def since_file(tmp_path, monkeypatch):
    path = tmp_path / ".ntfy_responder_since.json"
    monkeypatch.setattr(ntfy_responder, "STATE_FILE", path)
    return path


@pytest.fixture
def hashes_file(tmp_path, monkeypatch):
    path = tmp_path / ".ntfy_responder_seen_hashes.json"
    monkeypatch.setattr(ntfy_responder, "SEEN_HASHES_FILE", path)
    return path


@pytest.fixture
def rate_file(tmp_path, monkeypatch):
    path = tmp_path / ".ntfy_responder_rate.json"
    monkeypatch.setattr(ntfy_responder, "_rate_state_file", lambda: path)
    return path


# =====================================================================================
# .ntfy_responder_since.json -- the one that stopped the daemon STARTING
# =====================================================================================

@UNREADABLE_RAW
def test_no_partition_member_can_stop_the_responder_starting(raw, since_file):
    """THE CRASH HALF. MUTANT: restore `json.loads(...)["since"]` under
    `except (JSONDecodeError, KeyError)` and three of these five raise TypeError -- out of the
    first statement of `main()`, so the director's only inbound route is silently absent."""
    since_file.write_text(raw, encoding="utf-8")

    since, verdict = ntfy_responder._load_since()  # must not raise

    assert verdict == UNREADABLE
    assert isinstance(since, float), "a watermark the poll can use, whatever the file held"


def test_the_responder_tells_a_first_run_from_a_lost_watermark(since_file):
    """ABSENT and UNREADABLE take the same ACTION -- resume from now -- and are DIFFERENT ANSWERS.
    That difference is the whole repair: it is what lets `main` preserve the bytes and alarm on one
    while staying silent on the other. MUTANT: return a bare float for both and this fires."""
    assert not since_file.exists()
    assert ntfy_responder._load_since()[1] == ABSENT

    since_file.write_text("null", encoding="utf-8")
    assert ntfy_responder._load_since()[1] == UNREADABLE


def test_a_readable_watermark_is_resumed_from(since_file):
    """REACHABILITY NULL CONTROL. Without it every leg above is satisfied by a loader that answers
    UNREADABLE to everything -- which would alarm on every start and resume from now every time,
    losing exactly the messages the watermark exists to keep."""
    since_file.write_text(json.dumps({"since": LIVE_SINCE}), encoding="utf-8")

    since, verdict = ntfy_responder._load_since()

    assert verdict == READABLE
    assert since == LIVE_SINCE


def test_a_mapping_with_no_watermark_is_a_third_answer(since_file):
    """The file PARSED, so it is not unreadable; it carries no watermark, so it is not readable
    either. Three distinct reasons, and the remedies differ -- unreadable bytes are worth
    preserving and this record is not. MUTANT: fold `_NO_WATERMARK` into UNREADABLE and `main`
    starts preserving files that hold nothing, burying the copy that did."""
    since_file.write_text('{"other": 1}', encoding="utf-8")

    verdict = ntfy_responder._load_since()[1]

    assert verdict == ntfy_responder._NO_WATERMARK
    assert verdict not in (ABSENT, UNREADABLE, READABLE)


def test_a_boolean_is_not_a_watermark(since_file):
    """`isinstance(True, int)` is True, so a bare numeric check accepts `{"since": true}` and the
    poll then asks ntfy for messages since 1970. MUTANT: drop the bool exclusion."""
    since_file.write_text('{"since": true}', encoding="utf-8")

    assert ntfy_responder._load_since()[1] == ntfy_responder._NO_WATERMARK


# =====================================================================================
# .ntfy_responder_seen_hashes.json -- the one that left the daemon ALIVE AND DEAF
# =====================================================================================

@UNREADABLE_RAW
def test_no_partition_member_can_wedge_the_poll_loop(raw, hashes_file):
    """THE OTHER CRASH HALF, asserted through the OPERATIONS THAT ACTUALLY BROKE rather than
    through a type annotation -- the annotation said `list[str]` while the function returned None
    and dicts. `set(...)` is `check_once`'s first act on every successful poll and `.append(...)`
    is what a new message does. MUTANT: restore the old body and `null` wedges the loop forever
    while `{"other": 1}` waits and raises on the first real message."""
    hashes_file.write_text(raw, encoding="utf-8")

    hashes, verdict = ntfy_responder._load_seen_hashes()

    assert verdict == UNREADABLE
    set(hashes)              # check_once line 1 -- TypeError on None before this repair
    hashes.append("beef00")  # a new message arriving -- AttributeError on a dict


def test_the_responder_tells_a_first_run_from_a_wiped_dedup_set(hashes_file):
    """Same ACTION (start from an empty set), DIFFERENT ANSWERS. MUTANT: return `[]` for both."""
    assert not hashes_file.exists()
    assert ntfy_responder._load_seen_hashes() == ([], ABSENT)

    hashes_file.write_text('{"other": 1}', encoding="utf-8")
    assert ntfy_responder._load_seen_hashes() == ([], UNREADABLE)


def test_a_readable_dedup_set_is_resumed_from(hashes_file):
    """REACHABILITY NULL CONTROL: a loader that answered UNREADABLE to everything would drop the
    replay dedup on every start and re-ack every replayed body, and every leg above would pass."""
    hashes_file.write_text(json.dumps(LIVE_HASHES), encoding="utf-8")

    assert ntfy_responder._load_seen_hashes() == (LIVE_HASHES, READABLE)


def test_an_empty_dedup_set_is_a_fact_and_not_a_failure_to_read_one(hashes_file):
    """`[]` is a READABLE empty record; an empty FILE is not. MUTANT: treat falsy as unreadable
    and every fresh responder alarms about state it never lost."""
    hashes_file.write_text("[]", encoding="utf-8")
    assert ntfy_responder._load_seen_hashes() == ([], READABLE)

    hashes_file.write_text("", encoding="utf-8")
    assert ntfy_responder._load_seen_hashes() == ([], UNREADABLE)


def test_the_recovery_does_not_destroy_the_record_it_is_recovering_from(hashes_file):
    """THE DESTRUCTIVE HALF, in the order `main` performs it: preserve, THEN start saving. Both
    files here are read once at startup and written back last-writer-wins every cycle, so without
    the preserve the first `_save_seen_hashes` -- 20 seconds later -- is what destroys the
    evidence. MUTANT: drop the `preserve_unreadable(SEEN_HASHES_FILE)` call from `main`."""
    hashes_file.write_text('["already_acked_body", 2]', encoding="utf-8")

    kept = ntfy_responder.preserve_unreadable(hashes_file)
    ntfy_responder._save_seen_hashes(["whatever_arrives_next"])

    assert kept is not None
    assert "already_acked_body" in hashes_file.with_name(kept).read_text(encoding="utf-8")


# =====================================================================================
# .ntfy_responder_rate.json -- the one that was already sound, recorded not assumed
# =====================================================================================

@UNREADABLE_RAW
def test_the_flood_window_never_raises_and_always_hands_back_a_usable_window(raw, rate_file):
    """Ranked last and measured anyway: `benign` on the census answered whether a write could
    shorten an EPISODE, and a row nobody asked the loader question is a gap, not a pass. This one
    passed. MUTANT: drop the `isinstance` screen this loader always had and `[1, 2, 3]` reaches
    `_register_inbound_and_detect_flood`."""
    rate_file.write_text(raw, encoding="utf-8")

    state = ntfy_responder._load_rate_state()

    assert isinstance(state["events"], list)
    assert isinstance(state["last_alert"], (int, float))


def test_a_mapping_whose_events_is_not_a_list_is_not_a_window(rate_file):
    """A record that is only PARTLY right is not a record -- the `["x", 2]` lesson, applied to the
    mapping-shaped carrier. MUTANT: keep the mapping and the flood guard iterates a string."""
    rate_file.write_text('{"events": "nope", "last_alert": 3}', encoding="utf-8")

    assert ntfy_responder._load_rate_state()["events"] == []


def test_a_readable_flood_window_is_resumed_from(rate_file):
    """REACHABILITY NULL CONTROL: a loader that discarded every window would never detect a flood
    and would look identical in the log to one that simply saw no floods."""
    rate_file.write_text(json.dumps({"events": [1.0, 2.0], "last_alert": 9.0}), encoding="utf-8")

    state = ntfy_responder._load_rate_state()

    assert state["events"] == [1.0, 2.0]
    assert state["last_alert"] == 9.0


# =====================================================================================
# The helper the fourth call site was about to fork
# =====================================================================================

def test_every_carriers_preservation_goes_through_the_one_helper(tmp_path, monkeypatch):
    """Three modules held a BYTE-IDENTICAL private `_preserve_unreadable_*`, two of them with a
    docstring saying "same shape as" the first -- a fork of the fix history wearing a
    cross-reference, and the fourth copy was about to be written for the responder.

    Keyed to the PROPERTY, not to the source text: patch the central helper and all three must
    change their answer. A grep-for-the-call-site control would go green on a copy that merely
    LOOKS like a delegation. MUTANT: re-inline any one of the three bodies and its row fails."""
    import background.episode_prior as ep

    # REDIRECT THE THREE REAL PATHS FIRST. Found by running the mutant: a re-inlined body ignores
    # the spy and performs a REAL `Path.replace`, which moved the live `background/
    # .dispatcher_seen.json` out of the working tree. A control whose FAILING branch damages the
    # thing it guards is not a control.
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", tmp_path / ".sent_ntfy_ids.json")
    monkeypatch.setattr(staging_watcher, "STATE_FILE", tmp_path / ".staging_watcher_seen.json")
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / ".dispatcher_seen.json")

    calls: list[str] = []
    original = ep.preserve_unreadable

    def spy(path):
        calls.append(str(path))
        return "SENTINEL"

    carriers = (
        (ntfy_utils, "_preserve_unreadable_sent_ids"),
        (staging_watcher, "_preserve_unreadable_seen"),
        (dispatcher, "_preserve_unreadable_seen"),
    )
    for module, helper in carriers:
        # `staging_watcher` and `dispatcher` bind the name at import; `ntfy_utils` imports it
        # inside the function. Patching BOTH routes is what makes this a property and not a
        # test of one import style.
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


def test_the_first_loss_is_the_copy_that_survives(tmp_path):
    """The FIRST loss is the one that still holds the record; the second is most likely an empty
    file. MUTANT: use a fixed suffix in `preserve_unreadable` and the evidence is overwritten."""
    path = tmp_path / ".carrier.json"

    path.write_text('["first_loss", 2]', encoding="utf-8")
    first = ntfy_responder.preserve_unreadable(path)
    path.write_text("", encoding="utf-8")
    second = ntfy_responder.preserve_unreadable(path)

    assert first != second
    assert "first_loss" in path.with_name(first).read_text(encoding="utf-8")
