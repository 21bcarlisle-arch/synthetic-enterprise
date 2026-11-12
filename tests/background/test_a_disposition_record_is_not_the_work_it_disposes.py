"""A commit that carries only a disposition record does not retire the item it disposes.

THE N29 SHAPE (12 Nov 2026). `n29-set-off-netted-in-the-debt-legs-walk` was drawn by a second tick
while a worker already held the build. That tick wrote
`docs/staging/records/SEAT_DISPOSITION_N29_WALK_BUILD_IS_IN_FLIGHT_UNDER_A_WORKER_AND_WAS_NOT_BUILT_TWICE_2026-11-12.md`,
landed it as 0367c57375 at 04:36:56 with `--landed`, and released. Ten seconds later the continuation
retired. `origin_refusal` asked the right question ("does a commit on origin bind it?"), and the answer
was yes. But the bound commit was a note saying where the work was, not the work. The worker died, and
the finished build survived only in salvage 696aa94034. It was the third finished build retired with
nothing on origin.

ONE CONTROL OVER THE WHOLE PARTITION, so a guard that refuses everything fails it as surely as one that
refuses nothing:
  * the n29 shape (disposition-only commit on origin, bound by `--landed`) is HELD, naming the item
    and the commit;
  * a work commit on origin bound the same way RETIRES (the retire path can still be taken);
  * a commit carrying the disposition AND work retires (the record does not poison a real landing);
  * the n29 shape with `--premise-spent` recorded retires (the sanctioned way to say "nothing to do").
"""
from __future__ import annotations

import json
import os
import subprocess

from background import delivery_lane, seat_continuation

N29 = "n29-set-off-netted-in-the-debt-legs-walk"
WORK = "a-drawn-item-whose-work-reached-origin"
BOTH = "a-drawn-item-whose-landing-also-filed-a-disposition"
SPENT = "a-drawn-item-disposed-with-its-premise-recorded-spent"
DISPOSITION = ("docs/staging/records/SEAT_DISPOSITION_N29_WALK_BUILD_IS_IN_FLIGHT_UNDER_A_WORKER"
               "_AND_WAS_NOT_BUILT_TWICE_2026-11-12.md")


def _setup(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args, when=None):
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ["PATH"]}
        if when:
            env.update(GIT_AUTHOR_DATE=f"@{when}", GIT_COMMITTER_DATE=f"@{when}")
        return subprocess.run(("git", *args), cwd=repo, check=True, text=True,
                              capture_output=True, env=env).stdout.strip()

    def land(when, message, *paths):
        for p in paths:
            (repo / p).parent.mkdir(parents=True, exist_ok=True)
            (repo / p).write_text(f"{p} at {when}\n")
            git("add", p)
        git("commit", "-q", "-m", message, when=when)

    git("init", "-q")
    stamps = {N29: 1_700_000_000, WORK: 1_700_000_100, BOTH: 1_700_000_200, SPENT: 1_700_000_300}
    land(stamps[N29], "delivery seat: the N29 walk build is in flight under a worker", DISPOSITION)
    land(stamps[WORK], "the set-off nets in the debt leg's walk", "simulation/arrears_engine.py")
    land(stamps[BOTH], "the build, and the record of the duplicate it absorbed",
         "docs/staging/records/SEAT_DISPOSITION_THE_OTHER_DRAW_2026-11-12.md",
         "tools/generate_billing_ledger.py")
    land(stamps[SPENT], "delivery seat: the premise was spent by another landing",
         "docs/staging/records/SEAT_DISPOSITION_SPENT_2026-11-12.md")
    git("update-ref", delivery_lane.PUBLISHED_REF, "HEAD")
    monkeypatch.setattr(delivery_lane, "PROJECT_DIR", repo)

    store = tmp_path / "continuations.json"
    monkeypatch.setattr(seat_continuation, "STORE", store)
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda *a, **k: [])
    claims = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", claims)
    monkeypatch.setattr(delivery_lane, "current_orientation", lambda *a, **k: "o1")
    ledger = {i: {"first_drawn_at": 1.0, "last_drawn_at": 1.0, "last_landing_at": float(t)}
              for i, t in stamps.items()}
    ledger[SPENT]["premise_spent"] = {"commit": git("rev-parse", "HEAD"), "reason": "spent"}
    claims.with_suffix(".draws.json").write_text(json.dumps(ledger))
    seat_continuation._save([{"id": i, "what": "w", "why": "y", "done_means": "d",
                              "written_at": 1.0} for i in stamps], store)
    return git, store


def test_the_N29_shape_is_HELD_and_a_bound_work_landing_still_RETIRES(tmp_path, monkeypatch, capsys):
    """MUTATION: drop the disposition-only leg from `_origin_binding_commit` and N29 retires (leg 1,
    red at 0367c57375's base). Make every commit read as disposition-only and WORK and BOTH are held
    (legs 2 and 3). Drop the `premise_spent` leg of `focus_tombstone_refusal` and SPENT is held."""
    _, store = _setup(tmp_path, monkeypatch)

    outcomes = {i: delivery_lane.retire_continuation(i) for i in (N29, WORK, BOTH, SPENT)}
    assert outcomes == {N29: False, WORK: True, BOTH: True, SPENT: True}, outcomes

    held = next(i for i in json.loads(store.read_text()) if i["id"] == N29)
    reason = held["retire_held"]["reason"]
    assert "only a disposition record" in reason and DISPOSITION in reason, reason
    assert f"did NOT retire the continuation {N29}" in capsys.readouterr().out
    assert N29 in {i["id"] for i in seat_continuation.live(now=2.0, path=store)}


def test_the_held_N29_row_retires_once_its_work_lands_on_origin(tmp_path, monkeypatch):
    """The hold is a reading: when the salvage reaches origin under the id, the same release retires."""
    git, store = _setup(tmp_path, monkeypatch)
    assert seat_continuation.retire(N29, path=store) is False
    (tmp_path / "repo" / "simulation").mkdir(exist_ok=True)
    (tmp_path / "repo" / "simulation" / "set_off.py").write_text("x\n")
    git("add", "simulation/set_off.py")
    git("commit", "-q", "-m", f"the N29 netted set-off reaches origin\n\nNEXT: {N29}")
    git("update-ref", delivery_lane.PUBLISHED_REF, "HEAD")
    assert seat_continuation.held_reason(N29, path=store) is None
    assert seat_continuation.retire(N29, path=store) is True
