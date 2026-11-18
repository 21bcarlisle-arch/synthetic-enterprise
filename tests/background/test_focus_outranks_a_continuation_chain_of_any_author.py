"""Focus waits through at most SELF_HANDOFF_CHAIN_LIMIT continuation draws of ANY author.

The first leg (`_self_issued_chain`) arms only on a lane feeding itself. Continuations written by
an interactive session holding no claim never arm it, so the live record's focus went undrawn
through four records (17-18 Nov). `_focus_waited_through` counts continuation draws since the
record's `oriented_at` and its last focus draw, whoever wrote them.

MUTATION: `_focus_waited_through` returning 0 (the leg off) turns the partition control red --
the fourth draw is a fourth continuation.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import yaml

from background import delivery_lane as dl
from background import direction as d
from background import seat_continuation as sc
from background import seat_work_in_hand as claims_mod

# Draws happen in the recent past, after an orientation an hour ago: the record's liveness is
# judged against the real clock, so it must be both live and older than every draw here.
ORIENTED = datetime.now(timezone.utc) - timedelta(hours=1)
T0 = ORIENTED.timestamp() + 60.0
BATCH = 4


@pytest.fixture()
def lane(tmp_path, monkeypatch):
    direction_path = tmp_path / "DIRECTION.yaml"
    map_path = tmp_path / "maturity_map.yaml"
    map_path.write_text(yaml.safe_dump([{"id": "EP1_real_atom", "level_current": 1}]),
                        encoding="utf-8")
    monkeypatch.setattr(dl, "MATURITY_MAP", map_path)
    monkeypatch.setattr(d, "DIRECTION_PATH", direction_path)
    monkeypatch.setattr(sc, "STORE", tmp_path / ".seat_continuation.json")
    monkeypatch.setattr(dl, "CLAIMS_FILE", tmp_path / "claims.json")

    def write_focus(ids, oriented=ORIENTED):
        direction_path.write_text(yaml.safe_dump({
            "version": 1,
            "oriented_at": oriented.isoformat(),
            "focus": [{"id": i, "what": f"do {i}", "why": "the seat ranked it"} for i in ids],
            "not_now": [{"what": "something", "why": "it loses to the above"}],
        }), encoding="utf-8")

    write_focus(["the-seats-own-ranked-item"])
    return {"focus": write_focus, "claims": tmp_path / "claims.json"}


def _batch_then_draws(lane, draws):
    """One session holding no claim writes a batch, then `draws` real draws. Returns the ids."""
    assert not claims_mod.held(path=lane["claims"])
    for i in range(BATCH):
        sc.hand_off(f"session-wrote-{i}", f"piece {i}", "one session, one sitting", "done",
                    now=T0 + i)
    drawn = []
    for n in range(draws):
        text = dl.draw(now=T0 + 100.0 * (n + 1), path=lane["claims"])
        drawn.append(next((i for i in [f"session-wrote-{k}" for k in range(BATCH)]
                           + ["the-seats-own-ranked-item"] if text and i in text), None))
    return drawn


def test_a_continuation_WINS_FIRST_and_focus_WINS_AFTER_THE_LIMIT_whoever_wrote_the_run(lane):
    """ONE CONTROL OVER THE WHOLE PARTITION, from one mechanism with only the run length changed.
    The self-issued chain is asserted 0 throughout, so the first leg cannot be what fires."""
    limit = dl.SELF_HANDOFF_CHAIN_LIMIT
    assert limit < BATCH, "the batch must outlast the limit or focus winning proves nothing"
    drawn = _batch_then_draws(lane, limit + 1)
    assert dl._self_issued_chain(lane["claims"]) == 0

    assert (drawn[0] == "session-wrote-0"
            and drawn[limit] == "the-seats-own-ranked-item"), (
        f"draws were {drawn}: a continuation must win the first draw AND the live record's focus "
        f"must win once it has waited through {limit} continuation draws of any author")


def test_a_FOCUS_DRAW_resets_the_run_and_continuation_first_returns(lane):
    limit = dl.SELF_HANDOFF_CHAIN_LIMIT
    _batch_then_draws(lane, limit + 1)
    assert dl._focus_waited_through(lane["claims"]) == 0
    assert dl.next_item(now=T0 + 1000.0, path=lane["claims"])["id"].startswith("session-wrote-")


def test_a_FRESH_RECORD_starts_the_count_at_zero(lane):
    """Keyed to `oriented_at`: draws under an earlier record are not this record's wait."""
    limit = dl.SELF_HANDOFF_CHAIN_LIMIT
    lane["focus"]([])
    _batch_then_draws(lane, limit)
    assert dl._focus_waited_through(lane["claims"]) == 0          # no focus -> no live record
    lane["focus"](["the-seats-own-ranked-item"])
    assert dl._focus_waited_through(lane["claims"]) == limit
    lane["focus"](["the-seats-own-ranked-item"],
                  oriented=datetime.fromtimestamp(T0 + 100.0 * limit + 1, timezone.utc))
    assert dl._focus_waited_through(lane["claims"]) == 0


def test_a_row_the_LIVE_RECORD_NAMES_breaks_the_run_whatever_its_stamp_says(lane):
    """`source` is stamped once, at first draw. A row drawn as a continuation that the live record
    now names is direction being read, so it breaks the run like a focus draw."""
    limit = dl.SELF_HANDOFF_CHAIN_LIMIT
    lane["focus"]([])
    _batch_then_draws(lane, limit)
    lane["focus"]([f"session-wrote-{limit - 1}", "the-seats-own-ranked-item"])
    assert dl._focus_waited_through(lane["claims"]) == 0
