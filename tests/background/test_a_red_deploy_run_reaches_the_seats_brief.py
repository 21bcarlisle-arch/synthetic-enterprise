"""A red site deploy reaches the seat's brief, with the line that refused it (2026-10-22).

Four deploy runs went red on 22 Oct and only the director's advisor saw them: nothing the seat
reads looked at GitHub Actions. `red_deploys_since` is fed a fake `gh`. A red run inside the
stretch is listed with its refusal and makes the stretch material. A green run is not listed, and
neither is a red run from before the stretch. An unreadable `gh` is stated, never read as none.

MUTATIONS, RUN 2026-10-22, each red here: the conclusion filter dropped (the green run is listed);
the `since` filter dropped (the old red is listed); the `is_material` clause deleted.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

from background import delivery_seat as seat

SINCE = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)
RUNS = [
    {"databaseId": 3, "conclusion": "failure", "createdAt": "2026-10-22T16:07:15Z",
     "headSha": "2406226c8aaaa", "displayTitle": "front door"},
    {"databaseId": 2, "conclusion": "success", "createdAt": "2026-10-22T14:38:29Z",
     "headSha": "bbbbbbbbb", "displayTitle": "green"},
    {"databaseId": 1, "conclusion": "failure", "createdAt": "2026-10-22T09:49:22Z",
     "headSha": "989ce4f1c", "displayTitle": "before the stretch"},
]
LOG = ("2026-10-22T16:16:28Z   serving the deployed bytes after 16s: x\n"
       "2026-10-22T16:16:28Z     STALE -- another asset of this same push is being served\n")


def _fake(returncode=0):
    def run(argv, **_):
        if argv[:3] == ["gh", "run", "list"]:
            return subprocess.CompletedProcess(argv, returncode, json.dumps(RUNS), "no auth")
        if argv[:3] == ["gh", "run", "view"]:
            return subprocess.CompletedProcess(argv, 0, "77\n", "")
        return subprocess.CompletedProcess(argv, 0, LOG, "")
    return run


def test_a_red_run_in_the_stretch_is_listed_with_its_refusal_and_nothing_else_is():
    got = seat.red_deploys_since(SINCE, run=_fake())
    unreadable = seat.red_deploys_since(SINCE, run=_fake(returncode=1))
    brief = {"substantive_count": 0, "deploys_red": got}
    material, why = seat.is_material(brief)
    assert (got["readable"] and [r["run"] for r in got["red"]] == [3]
            and got["red"][0]["refused_by"][0].startswith("STALE")
            and material and "deploy run(s) went red" in why
            and unreadable["readable"] is False), (got, why, unreadable)
