"""A publish that reached origin by a route other than the publisher's own clean exit closes the
open episode.

THE DEFECT (2026-10-22). On 2026-10-19 the publisher's commit was merged onto origin by a seat, so
`record_publish_gate_success` never ran; the episode's recorded cause (`gate_refusal`) is not one
git can re-ask, so `close_episode_if_cause_cleared` held it open, and the front door read
"PUBLISHING IS FAILING ... over 80.0h" for three days after the figures landed.

ONE PARTITION CONTROL over the three readings of git's landing date, so the rare branch is shown
reachable before what it does is asserted: absent and earlier than the episode both leave it open,
later closes it under its own rule name.

MUTATIONS, RUN 2026-10-22, all red:
  * the `landed > since` branch removed -> the "after" leg stays open.
  * `>` flipped to `<` -> "before" closes and "after" stays open.
  * the rule written as `cause_cleared` on every close -> the rule assert reds.
"""
from __future__ import annotations

import json

import pytest

import background.process_run_complete as prc

T0 = 1_800_000_000.0


@pytest.fixture
def gate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    origin = {"ts": None}
    monkeypatch.setattr(prc, "_landed_publish_ts", lambda: origin["ts"])
    return tmp_path / ".publish_gate_state.json", origin


def _open_episode(path):
    path.write_text(json.dumps({
        "failures": [{"ts": T0, "cause": "gate_refusal"}], "alerted_at": None,
        "wedge_since": T0, "episode_failures": 2, "episode_clean_publishes": 0}))


@pytest.mark.parametrize("landed, expect", [
    (None, "unknown"),
    (T0 - 3600, "unknown"),
    (T0 + 3600, "landed"),
])
def test_only_a_landing_after_the_episode_began_closes_it(gate, landed, expect):
    path, origin = gate
    _open_episode(path)
    origin["ts"] = landed
    assert prc.close_episode_if_cause_cleared(now=T0 + 7200, fork_fn=lambda: (0, 0)) == expect
    st = json.loads(path.read_text())
    if expect == "landed":
        assert st["episode_failures"] == 0 and st["wedge_since"] is None
        assert st["episode_closed_by"]["rule"] == "publish_landed"
    else:
        assert st["episode_failures"] == 2 and st["wedge_since"] == T0


def test_the_closed_record_reads_recovered_on_the_surface(gate, monkeypatch):
    path, origin = gate
    _open_episode(path)
    origin["ts"] = T0 + 3600
    prc.close_episode_if_cause_cleared(now=T0 + 7200, fork_fn=lambda: (0, 0))
    from background import publish_freshness
    assert publish_freshness.publisher_refusal(now=T0 + 7200, path=path)["state"] == "recovered"
