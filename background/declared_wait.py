"""A declared wait: a watcher that names the file it waits for, so RUNG 1 can stay quiet.

THE DIRECTOR'S RULING, 18 Nov 2026 ("Yes."; docs/staging/advisor/done/DIRECTOR_RULING_QUIET_THE_
WEDGE_REFILL_AND_ALARM_TUNING_IS_YOURS_TO_DECIDE_2026-11-18.md). When the open publish episode's
cause is `domain_invariant_refused` and the owed book waits behind an armed, declared watcher on a
named file, the priority-zero refill names that file and stays quiet. It fires at once if the
watcher is gone, if the file appears and no book follows within 1 h, or if the episode passes 72 h.
On 17-18 Nov the refill re-asked 59 times while `flag1-stop-at-pair3-watch` waited for
`/var/tmp/vta-out-flag1/control_55555_66666.json`; each re-ask cost a commit cycle and repaired
nothing.

HOW A WATCHER DECLARES (the design choice). A systemd user unit name plus an absolute path, written
here by `--declare`, which refuses unless the unit is active at the moment of declaring. The record
is kept apart from the unit, not in its Environment, because the 1 h leg needs it to OUTLIVE the
unit: a watcher's job usually ends when its file appears (flag1's did, 34 s after the file), and a
declaration that vanished with it would read "watcher gone" and fire an hour early.

A wait quiets only while it can still end the episode:
  * file absent, unit active                  -> quiet (the wait is armed)
  * file absent, unit not active / unreadable -> fires (the watcher is gone; nothing will arrive)
  * file present, mtime under 1 h ago         -> quiet (the book is owed within the hour)
  * file present, mtime 1 h or more ago       -> fires (the file came and no book followed)
and every leg is overridden by an episode older than 72 h, or one whose cause is not established
as `domain_invariant_refused`. Every unreadable input fails LOUD: silence must be earned.

    python3 -m background.declared_wait --declare --unit X.service --awaits /abs/path --why "..."
    python3 -m background.declared_wait --list
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DECLARED_WAITS_FILE = PROJECT_DIR / "docs" / "observability" / ".declared_waits.json"

#: The ruling's three numbers, his words: "within 1 hour", "passes 72 hours".
BOOK_FOLLOWS_WITHIN_SECONDS = 60 * 60
EPISODE_CAP_SECONDS = 72 * 60 * 60
#: The one cause the ruling covers. Declared by `publish_cause.DOMAIN_INVARIANT_REFUSED`.
QUIETABLE_KIND = "domain_invariant_refused"
#: A declaration older than this cannot be about an episode the cap still lets it quiet.
_PRUNE_AFTER_SECONDS = 7 * 24 * 3600


def unit_is_active(unit: str) -> bool:
    """`systemctl --user is-active`. Anything but active/activating -- including a probe that
    cannot run -- is False, so an unreadable watcher reads as gone and the refill fires."""
    try:
        out = subprocess.run(["systemctl", "--user", "is-active", unit],
                             capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:  # noqa: BLE001 - unreadable is gone, see docstring
        return False
    return out in ("active", "activating")


def _file_mtime(path: str) -> float | None:
    try:
        return os.stat(path).st_mtime
    except OSError:
        return None


def read_waits(path: Path | None = None) -> list[dict]:
    try:
        data = json.loads(Path(path or DECLARED_WAITS_FILE).read_text())
    except (OSError, ValueError):
        return []
    return [w for w in data if isinstance(w, dict)] if isinstance(data, list) else []


def _episode_cause(state: dict) -> str | None:
    """The kind on the newest recorded failure. An empty list establishes nothing."""
    failures = state.get("failures")
    if not isinstance(failures, list) or not failures or not isinstance(failures[-1], dict):
        return None
    kind = failures[-1].get("kind")
    return kind if isinstance(kind, str) else None


def _episode_start(state: dict) -> float | None:
    v = state.get("wedge_since")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not v > 0:
        return None
    return float(v)


def quiet_reason(state, waits, *, now: float | None = None, unit_active=unit_is_active,
                 file_mtime=_file_mtime) -> tuple[bool, str]:
    """(True, why it is quiet) or (False, why it fires). Never raises."""
    now = time.time() if now is None else float(now)
    if not isinstance(state, dict):
        return False, "the publish-gate record is unreadable"
    cause = _episode_cause(state)
    if cause != QUIETABLE_KIND:
        return False, f"the episode's newest recorded failure is `{cause}`, not `{QUIETABLE_KIND}`"
    started = _episode_start(state)
    if started is None:
        return False, "the episode has no readable start, so its 72 h cap cannot be checked"
    age = now - started
    if age >= EPISODE_CAP_SECONDS:
        return False, f"the episode is {age / 3600:.1f} h old, past the 72 h cap"
    if not waits:
        return False, "no watcher has declared a wait"
    fired = []
    for w in waits:
        unit, awaits = str(w.get("unit") or ""), str(w.get("awaits") or "")
        if not unit or not awaits:
            fired.append("a declaration without a unit or a file")
            continue
        mtime = file_mtime(awaits)
        if mtime is not None:
            since = now - mtime
            if since < BOOK_FOLLOWS_WITHIN_SECONDS:
                return True, (f"{awaits} appeared {since / 60:.0f} min ago; the book is owed "
                              f"within 1 h of it (episode {age / 3600:.1f} h)")
            fired.append(f"{awaits} appeared {since / 3600:.1f} h ago and no book followed")
        elif unit_active(unit):
            return True, (f"the owed book waits on {awaits} behind {unit}, which is armed "
                          f"(episode {age / 3600:.1f} h of the 72 h cap)")
        else:
            fired.append(f"{unit} is gone and {awaits} never appeared")
    return False, "; ".join(fired)


def declare(unit: str, awaits: str, why: str, *, path: Path | None = None,
            now: float | None = None, unit_active=unit_is_active) -> str:
    """Record a wait, or raise ValueError naming the refusal."""
    if not os.path.isabs(awaits):
        raise ValueError(f"refused: {awaits!r} is not an absolute path, so the refill cannot check it")
    if not why.strip():
        raise ValueError("refused: a wait with no reason cannot be judged by whoever finds it")
    if not unit_active(unit):
        raise ValueError(f"refused: {unit} is not active; a dead watcher cannot hold the refill quiet")
    now = time.time() if now is None else float(now)
    p = Path(path or DECLARED_WAITS_FILE)
    kept = [w for w in read_waits(p)
            if w.get("unit") != unit and now - float(w.get("declared_ts") or 0) < _PRUNE_AFTER_SECONDS]
    kept.append({"unit": unit, "awaits": awaits, "why": why.strip(), "declared_ts": now,
                 "declared_at": datetime.fromtimestamp(now, timezone.utc).isoformat(timespec="seconds")})
    tmp = p.with_name(p.name + f".tmp-{os.getpid()}")
    tmp.write_text(json.dumps(kept, indent=1) + "\n")
    tmp.replace(p)
    return f"declared: {unit} awaits {awaits}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--declare", action="store_true")
    ap.add_argument("--unit")
    ap.add_argument("--awaits")
    ap.add_argument("--why", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.declare:
        if not a.unit or not a.awaits:
            print("refused: --declare needs --unit and --awaits", file=sys.stderr)
            return 2
        try:
            print(declare(a.unit, a.awaits, a.why))
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 1
        return 0
    for w in read_waits():
        state = "active" if unit_is_active(str(w.get("unit"))) else "gone"
        present = "present" if _file_mtime(str(w.get("awaits"))) is not None else "absent"
        print(f"{w.get('unit')} [{state}] awaits {w.get('awaits')} [{present}] -- {w.get('why')}")
    return 0


if __name__ == "__main__":
    from background._seat import refuse_if_foreign

    refuse_if_foreign("declared_wait")
    sys.exit(main())
