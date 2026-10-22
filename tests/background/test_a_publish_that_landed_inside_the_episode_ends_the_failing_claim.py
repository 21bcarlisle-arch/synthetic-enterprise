"""A publish that landed after a failure episode began ends that episode's claim to be FAILING.

THE DEFECT (2026-10-22, director steer DIRECTOR_STEER_THE_FRONT_DOOR_SAYS_PUBLISHING_IS_FAILING_
AND_IT_IS_NOT). Two gate refusals opened an episode at 2026-10-19T05:29Z; the publish landed at
09:15Z by a route that never closed it. `.publish_gate_state.json` then held `episode_failures: 2`
beside `last_landed_publish` 09:15Z and `failures_since_landed_publish: 0`, and every page read
"PUBLISHING IS FAILING ... over 80.0h" for three days over figures that were on the site.

ONE CONTROL OVER THE PARTITION: the same failing episode must read `failing` when no landing
followed it, when the landing came before it, and when a failure followed the landing -- and must
not read `failing` when a landing followed it cleanly. A reader that never supersedes, or always
does, reds the final assert.
"""
from __future__ import annotations

import json

from background import publish_freshness

T0 = 1_800_000_000.0
HOLD = {"next_opens": "2026-10-26T04:00:00+00:00", "reason": "held", "ts": T0 + 7200}


def _reading(tmp_path, **fields):
    path = tmp_path / ".publish_gate_state.json"
    state = {"episode_failures": 2, "wedge_since": T0, "episode_clean_publishes": 0,
             "publish_hold": HOLD, "last_clean_publish": T0 - 86400}
    state.update(fields)
    path.write_text(json.dumps(state))
    return publish_freshness.publisher_refusal(now=T0 + 10_000, path=path)


def test_only_a_clean_landing_after_the_episode_began_supersedes_it(tmp_path):
    readings = {
        "no_landing": _reading(tmp_path)["state"],
        "landed_before": _reading(tmp_path, last_landed_publish=T0 - 60,
                                  failures_since_landed_publish=0)["state"],
        "failed_since": _reading(tmp_path, last_landed_publish=T0 + 3600,
                                 failures_since_landed_publish=1)["state"],
        "count_unknown": _reading(tmp_path, last_landed_publish=T0 + 3600,
                                  failures_since_landed_publish=None)["state"],
        "landed_after": _reading(tmp_path, last_landed_publish=T0 + 3600,
                                 failures_since_landed_publish=0)["state"],
    }
    assert readings == {"no_landing": "failing", "landed_before": "failing",
                        "failed_since": "failing", "count_unknown": "failing",
                        "landed_after": "held"}, readings


def test_a_superseded_episode_says_so_and_keeps_its_count(tmp_path):
    """The count is not erased -- the record still says two attempts failed -- it is only no
    longer read as a publisher that is failing now."""
    r = _reading(tmp_path, last_landed_publish=T0 + 3600, failures_since_landed_publish=0)
    assert r["superseded_by_landed_publish"] is True and r["consecutive_failures"] == 2
    assert _reading(tmp_path)["superseded_by_landed_publish"] is False
