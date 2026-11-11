"""While the delivery seat is orienting, nobody else commits `docs/direction/DIRECTION.yaml`.

WHY. The seat takes about 40 minutes from brief to landing, and its landing refuses when origin's
DIRECTION.yaml moved in that time -- rightly, because it will not overwrite an edit it never read.
On 2026-11-11 two of four orientations were lost that way (12:24, 18:22), the second to a worker
tick actioning an advisor reading whose edit the seat's own record already carried
(`docs/staging/SEAT_FINDING_THE_DIRECTION_RECORD_LOSES_ITS_LANDING_TO_A_SECOND_WRITER_ON_DIRECTION_YAML_2026-11-11.md`).
The cheap side to move is the second writer's: leave the edit to the seat, or wait for the unit.

WHO IS THE SEAT is answered by the kernel, not by an env var someone must remember to pass: every
process the unit starts -- the python, its `claude` child, `surgical_land`, this hook -- sits in
`delivery-seat.service`'s cgroup, and nothing else does.

A oneshot unit reads `activating` while it runs, never `active`; both count.

FAILS OPEN, LOUDLY, when systemd cannot be asked (a container, a CI box): this guards a three-hour
delay, not data, and a wedged commit path costs more than one lost orientation.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DIRECTION_YAML = "docs/direction/DIRECTION.yaml"
SEAT_UNIT = "delivery-seat.service"
RUNNING_STATES = ("active", "activating", "reloading")


def verdict(staged: list[str], seat_state: str | None, own_cgroup: str,
            seat_started: str = "") -> tuple[bool, str]:
    """(ok, why). Refuses only a non-seat commit of DIRECTION.yaml while the seat runs."""
    if DIRECTION_YAML not in staged:
        return True, ""
    if seat_state not in RUNNING_STATES:
        return True, ""
    if SEAT_UNIT in own_cgroup:
        return True, ""
    since = f" since {seat_started}" if seat_started else ""
    return False, (
        f"{SEAT_UNIT} is orienting{since} (state {seat_state}) and lands its own {DIRECTION_YAML} "
        "within about 40 minutes. Its landing is refused if this file moves on origin first, which "
        "cost two of four orientations on 2026-11-11.\n"
        f"Either unstage {DIRECTION_YAML} and commit the rest (the seat reads the stretch, so name "
        "the change you wanted in your commit message or a staging finding), or wait for the unit "
        "and commit after it:\n"
        f"    python3 tools/wait_for.py --pid $(systemctl --user show -p MainPID --value {SEAT_UNIT}) "
        "--deadline 4500 --subject 'the delivery seat landing its direction record'")


def _seat() -> tuple[str | None, str]:
    r = subprocess.run(["systemctl", "--user", "show", SEAT_UNIT,
                        "-p", "ActiveState", "-p", "ExecMainStartTimestamp"],
                       capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"systemctl exited {r.returncode}")
    props = dict(line.split("=", 1) for line in r.stdout.splitlines() if "=" in line)
    return props.get("ActiveState"), props.get("ExecMainStartTimestamp", "")


def _cgroup() -> str:
    return Path("/proc/self/cgroup").read_text(encoding="utf-8", errors="replace")


def _staged() -> list[str]:
    r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                       capture_output=True, text=True, timeout=60, check=True)
    return [p for p in r.stdout.splitlines() if p.strip()]


def main() -> int:
    try:
        staged = _staged()
        if DIRECTION_YAML not in staged:
            return 0
        state, started = _seat()
        cgroup = _cgroup()
    except Exception as exc:  # noqa: BLE001 -- fails open, loudly; see the docstring
        print(f"[direction-seat-window] could not ask git/systemd, not blocking: {exc}", file=sys.stderr)
        return 0
    ok, why = verdict(staged, state, cgroup, started)
    if not ok:
        print("[direction-seat-window] COMMIT REFUSED.\n" + why, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
