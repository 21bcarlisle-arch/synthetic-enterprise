"""Two pieces of work that move the same files are the same work, however they are labelled.

Director, 2026-08-31: *"Include duplication in that build — you named it as the larger risk and you
did it yourself today."*

WHAT HAPPENED. Another lane filed the ceiling-vs-belief finding at `b666a2b50`; I filed the same
defect, from the same capture, found the same way, minutes later at `9b3aa883b`. Neither of us could
see the other was mid-flight. The staging root is a RANKED queue, so a duplicate does not merely
waste a turn — it displaces something real down the order.

WHY THE KEY IS PATHS AND NOT NAMES. `delivery_lane` already claims an ITEM, so two ticks cannot take
one focus id. That is blind to two writers choosing the same work under two different names, which
is exactly what happened. `claim()` has carried a `paths` file_scope since it was written and
nothing ever asked the question it makes answerable.

WHY IT WARNS BY DEFAULT AND REFUSES ONLY FOR UNATTENDED WRITERS. An overlap is strong evidence and
not proof; a guard that cried wolf on `docs/staging/` would be routed around within a day, and a
guard nobody obeys is worse than none. So shared-by-design directories are excluded, a human-driven
caller is shown the holder, and only `refuse_if_duplicated` — used by the promotion route and the
executor — raises.
"""
from __future__ import annotations

import json
import time

import pytest

from background.seat_work_in_hand import (
    DuplicateWork,
    overlapping_claims,
    refuse_if_duplicated,
)


@pytest.fixture
def store(tmp_path):
    path = tmp_path / "claims.json"
    path.write_text(json.dumps({
        "someone-elses-work": {
            "claimed_at": time.time(),
            "note": "union the departure routes",
            "paths": ["tools/measure_departure_level.py", "tools/population_anchor.py"],
        }
    }))
    return path


def test_an_overlap_on_a_REAL_path_is_reported_with_the_holder(store):
    """The finding in one call: who already holds what I am about to move.

    MUTATION: return only a boolean, or drop the holder's id, and this fires — a warning that
    cannot name the other claim sends the reader nowhere.
    """
    clash = overlapping_claims(["tools/measure_departure_level.py"], stores=[store])
    assert clash == {"someone-elses-work": ["tools/measure_departure_level.py"]}


def test_work_on_DIFFERENT_paths_is_not_duplication(store):
    """The guard must be silent on genuinely separate work or it will be ignored.

    MUTATION: return every live claim regardless of overlap and this fires.
    """
    assert overlapping_claims(["tools/inference_claim.py"], stores=[store]) == {}


def test_SHARED_BY_DESIGN_directories_do_not_count_as_duplication(store):
    """Every lane appends to `docs/staging/` by design; one file per writer is not a collision.

    This exclusion is the difference between a guard people obey and one they route around. It is
    deliberately SHORT — every exemption is a place duplication can hide.

    MUTATION: remove the `_SHARED_BY_DESIGN` filter and this fires, and the guard would then
    refuse essentially every landing this project makes.
    """
    store.write_text(json.dumps({
        "another-lane": {"claimed_at": time.time(), "note": "",
                         "paths": ["docs/staging/A_FINDING.md", "docs/observability/x.json"]},
    }))
    assert overlapping_claims(
        ["docs/staging/MY_FINDING.md", "docs/observability/y.json"], stores=[store]
    ) == {}


def test_a_writers_OWN_claim_is_not_a_clash_with_itself(store):
    """Re-checking your own claim must not refuse you.

    MUTATION: drop the `exclude` handling and this fires — a writer would be blocked by itself the
    moment it re-checked, which is exactly when it would be about to promote.
    """
    assert overlapping_claims(
        ["tools/measure_departure_level.py"], exclude="someone-elses-work", stores=[store]
    ) == {}


def test_a_STALE_claim_does_not_hold_a_path_forever(store):
    """A dead writer must not be able to block a live one indefinitely.

    MUTATION: stop sweeping before reading and this fires — the claim store would become a
    graveyard that refuses everything it ever saw.
    """
    old = time.time() - (30 * 24 * 3600)
    store.write_text(json.dumps({
        "long-dead": {"claimed_at": old, "note": "", "paths": ["tools/measure_departure_level.py"]},
    }))
    assert overlapping_claims(["tools/measure_departure_level.py"], stores=[store]) == {}


def test_an_UNATTENDED_writer_is_REFUSED_and_told_who_holds_the_paths(store, monkeypatch):
    """The half that raises. An unattended writer cannot read the other claim and judge.

    MUTATION: make `refuse_if_duplicated` warn instead of raise and this fires.
    """
    import background.seat_work_in_hand as mod

    monkeypatch.setattr(mod, "CLAIMS_FILE", store)
    monkeypatch.setattr(mod, "overlapping_claims",
                        lambda paths, **k: {"someone-elses-work": list(paths)})
    with pytest.raises(DuplicateWork) as exc:
        refuse_if_duplicated(["tools/measure_departure_level.py"])
    message = str(exc.value)
    assert "someone-elses-work" in message
    assert "tools/measure_departure_level.py" in message
    assert "Release the other claim" in message, (
        "the refusal must say what to DO — a refusal with no route out gets bypassed"
    )


def test_BOTH_claim_stores_are_read__the_collision_was_across_them(store, tmp_path):
    """The pair that actually collided was one item held by a tick and one by a session.

    A check that read one store would have been blind to exactly the case it exists for.

    MUTATION: read only `CLAIMS_FILE` and this fires.
    """
    second = tmp_path / "lane_claims.json"
    second.write_text(json.dumps({
        "a-tick-item": {"claimed_at": time.time(), "note": "", "paths": ["tools/generate_proof_data.py"]},
    }))
    clash = overlapping_claims(
        ["tools/measure_departure_level.py", "tools/generate_proof_data.py"],
        stores=[store, second],
    )
    assert set(clash) == {"someone-elses-work", "a-tick-item"}


def test_an_UNREADABLE_store_does_not_block_a_writer(tmp_path):
    """A broken claim file must cost the guard its answer, never the machine its work.

    MUTATION: let `_load` raise out of `overlapping_claims` and this fires — one corrupt JSON file
    would stop every writer in the project.
    """
    broken = tmp_path / "broken.json"
    broken.write_text("{ not json")
    assert overlapping_claims(["tools/anything.py"], stores=[broken]) == {}


def test_the_DEFAULT_store_list_is_both_writers_stores(monkeypatch, tmp_path):
    """Every leg above passes `stores=` explicitly, so none of them exercises the DEFAULT.

    THIS LEG EXISTS BECAUSE ITS MUTATION SURVIVED. Narrowing the default to one store left the
    whole file green: the tests were all supplying their own list, so the line that decides what
    happens in production was never run. A control that only exercises its own fixtures is testing
    the fixtures.

    MUTATION: drop either store from the default and this fires.
    """
    import background.delivery_lane as lane
    import background.seat_work_in_hand as mod

    seen: list = []
    monkeypatch.setattr(mod, "sweep", lambda **k: None)
    monkeypatch.setattr(mod, "_load", lambda p: seen.append(p) or {})
    mod.overlapping_claims(["tools/real_path.py"])

    assert mod.CLAIMS_FILE in seen, "the interactive seat's own claim store was not read"
    assert lane.CLAIMS_FILE in seen, (
        "the delivery lane's claim store was not read — the pair that actually collided on "
        "2026-08-31 was one item held by a tick and one by a session, so a check that reads only "
        "one store is blind to exactly the case it exists for"
    )
