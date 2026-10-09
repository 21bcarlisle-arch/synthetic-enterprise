"""A lane unit that crashes on two consecutive runs is seen, and the 10-09 shape is repaired.

The fixture is the real worker-tick journal from 2026-10-09: one clean run, then the first two of
the runs that died with `AttributeError: ... has no attribute 'held_at_dispatch'` because
`worker_tick.py` was a working copy calling a name only an uncommitted `delivery_lane.py` defined.
The draw's own log lines are dropped; every systemd field the reader keys on is as journald wrote it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from background import delivery_seat
from background import lane_unit_crash as L
from background import reconcile_watch as W

FIXTURE = Path(__file__).parent / "fixtures" / "worker_tick_journal_2026_10_09_held_at_dispatch.jsonl"
LIVE_ROOT = "/home/rich/synthetic-enterprise"
EXC = "AttributeError: module 'background.delivery_lane' has no attribute 'held_at_dispatch'"

HEAD_COPY = b"from background import delivery_lane\n\ndef run_tick():\n    return 0\n"
STALE_COPY = (b"from background import delivery_lane\n\ndef _held_at_dispatch(reason):\n"
              b"    return delivery_lane.held_at_dispatch(reason)\n\ndef run_tick():\n    return 0\n")


def _journal(root: Path | None = None, exc: str | None = None) -> list[dict]:
    entries = [json.loads(line) for line in FIXTURE.read_text().splitlines() if line.strip()]
    for entry in entries:
        msg = entry.get("MESSAGE")
        if isinstance(msg, str):
            if root is not None:
                msg = msg.replace(LIVE_ROOT, str(root))
            if exc is not None and msg == EXC:
                msg = exc
            entry["MESSAGE"] = msg
    return entries


def _repo(tmp_path: Path, dirty: bool = True) -> Path:
    root = tmp_path / "shared"
    (root / "background").mkdir(parents=True)
    (root / "background" / "worker_tick.py").write_bytes(HEAD_COPY)
    git = ["git"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for key, value in (("user.name", "t"), ("user.email", "t@t")):
        subprocess.run(["git", "-C", str(root), "config", key, value], check=True)
    subprocess.run(git + ["-C", str(root), "add", "."], check=True)
    subprocess.run(git + ["-C", str(root), "commit", "-qm", "head"], check=True)
    if dirty:
        (root / "background" / "worker_tick.py").write_bytes(STALE_COPY)
    return root


def _journals(entries):
    return lambda unit: entries if unit == "worker-tick" else []


# --- DETECT --------------------------------------------------------------------------------------

def test_the_detector_can_say_both_answers_and_says_crashed_on_the_10_09_journal():
    """CONTROL OVER THE PARTITION FIRST: one clean run then one crash is NOT two crashes, and that
    pair is only readable at all because a clean run counts as finished. The first draft keyed
    `finished` to EXIT_STATUS, which systemd writes only on failure, and read the recovered live
    lanes as still crashing. MUTATION: `all` -> `any` in `reading`, or key `finished` to
    EXIT_STATUS -- either reds this."""
    entries = _journal()
    finished = L.runs(entries)
    assert [r["job_result"] for r in finished] == ["done", "failed", "failed"]

    first_crash_only = [e for e in entries
                        if (e.get("_SYSTEMD_INVOCATION_ID") or e.get("USER_INVOCATION_ID"))
                        != finished[-1]["invocation"]]
    clean_then_crash = L.reading("worker-tick", first_crash_only)
    assert clean_then_crash["available"] and clean_then_crash["crashed_twice"] is False

    both = L.reading("worker-tick", entries)
    assert both["crashed_twice"] is True
    assert both["streak_from"] == finished[1]["invocation"]
    assert [r["exception"] for r in both["runs"]] == [EXC, EXC]
    assert both["runs"][-1]["frame"] == LIVE_ROOT + "/background/worker_tick.py"


def test_the_seat_brief_names_the_crashed_lane_and_the_ntfy_fires_once_per_streak(tmp_path):
    """MUTATION: drop the `streak_from` comparison in `check` and the second pass pages again; drop
    `_lane_crash_sentence` from the brief and the lane is not named."""
    root = _repo(tmp_path, dirty=False)
    pages, state = [], {}
    journal = _journals(_journal(root))
    L.check(root=root, journal=journal, notify=lambda text, **k: pages.append(text), state=state)
    L.check(root=root, journal=journal, notify=lambda text, **k: pages.append(text), state=state)
    assert len(pages) == 1 and "worker-tick" in pages[0] and "held_at_dispatch" in pages[0]

    running = {"available": True, "lane_units": [L.reading("worker-tick", _journal())]}
    said = delivery_seat._lane_crash_sentence(running)
    assert "worker-tick" in said and "held_at_dispatch" in said
    clean = {"available": True, "lane_units": [L.reading("worker-tick", _journal()[:15])]}
    assert "CRASHED" not in delivery_seat._lane_crash_sentence(clean)


def test_the_detector_rides_the_five_minute_tick(monkeypatch, tmp_path):
    """MUTATION: delete the rider from `reconcile_watch.run` and this reds."""
    monkeypatch.setattr(W, "STATE_FILE", tmp_path / "s.json")
    monkeypatch.setattr(W, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(W._gap, "reconcile", lambda *a, **k: [])
    W.run([], [], notify=lambda *a, **k: None, gap_results=[], reconcile_fork=lambda: None,
          fork_streak=lambda: None, lane_crash=lambda: ["worker-tick ended its last two runs"])
    assert "lane unit crash: worker-tick" in W.LOG_FILE.read_text()


# --- REPAIR --------------------------------------------------------------------------------------

def test_the_repair_partition_reaches_restore_and_hold(tmp_path):
    """CONTROL OVER THE PARTITION: a guard that holds everything passes every hold test. MUTATION:
    make `plan` return hold unconditionally, or drop the REPAIRABLE leg -- this reds."""
    dirty = _repo(tmp_path / "a")
    clean = _repo(tmp_path / "b", dirty=False)
    restore = L.plan(L.reading("worker-tick", _journal(dirty)), dirty)
    committed = L.plan(L.reading("worker-tick", _journal(clean)), clean)
    keyerror = L.plan(L.reading("worker-tick", _journal(dirty, exc="KeyError: 'occ'")), dirty)
    assert restore == {"action": "restore", "path": "background/worker_tick.py", "exception": EXC}
    assert committed["action"] == "hold" and "matches HEAD" in committed["why"]
    assert keyerror["action"] == "hold" and "KeyError" in keyerror["why"]


def test_the_10_09_fixture_is_repaired_on_the_first_tick_after_the_second_crash(tmp_path):
    """The done-condition: the second crash finishes, the next five-minute tick preserves the copy
    and writes HEAD, so the THIRD lane run (one ten-minute cycle later) runs HEAD's file. MUTATION:
    skip the write in `restore` and the bytes check reds; skip `preserve` and the ref check reds."""
    root = _repo(tmp_path)
    pages = []
    L.check(root=root, journal=_journals(_journal(root)), notify=lambda t, **k: pages.append(t),
            state={})
    assert (root / "background" / "worker_tick.py").read_bytes() == HEAD_COPY
    refs = subprocess.run(["git", "-C", str(root), "for-each-ref", "--format=%(refname)",
                           "refs/preserved/"], capture_output=True, text=True).stdout.split()
    assert len(refs) == 1 and "lane-unit-crash-worker-tick" in refs[0]
    kept = subprocess.run(["git", "-C", str(root), "show", refs[0] + ":background/worker_tick.py"],
                          capture_output=True).stdout
    assert kept == STALE_COPY
    assert len(pages) == 1 and "REPAIRED" in pages[0] and refs[0] in pages[0]


def test_a_held_cause_writes_nothing_and_says_why(tmp_path):
    root = _repo(tmp_path)
    pages = []
    L.check(root=root, journal=_journals(_journal(root, exc="KeyError: 'occ'")),
            notify=lambda t, **k: pages.append(t), state={})
    assert (root / "background" / "worker_tick.py").read_bytes() == STALE_COPY
    assert len(pages) == 1 and "HELD for a person" in pages[0] and "KeyError" in pages[0]
