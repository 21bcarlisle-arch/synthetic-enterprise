"""Measure the `-x` premium in PEAK MEMORY, by watching two suites that are already running.

WHY THIS EXISTS. `WORKER_FINDING_THE_MEASUREMENTS_SUBJECT_IS_LARGER_THAN_THE_GATES_2026-08-11`
says the OPS2 measurement OOMs where the real publish gate does not, because
`measure_publish_gate_subject_cost._argv_without_x` strips `-x`: the gate stops at the first
failure of a red suite, the measurement runs the whole thing and accumulates the session's
memory. The finding filed that as `inferred` and said, explicitly, MEASURE FIRST -- the cheap
check being "peak RSS of one `-x` run against one `-x`-less run of the same tests".

Running two more full suites to get that number would cost ~40 minutes on a box whose OOM killer
is the thing under investigation. It is not necessary: on 2026-08-11 the box was ALREADY running
both sides -- the live publisher's gate (`-x`) and a `tools.enumerate_publish_gate_reds` sweep
(no `-x`) -- with argv identical apart from that one flag, started a minute apart. This samples
those, so the measurement costs an observer and not a third suite.

WHAT IT MEASURES, AND WHAT THAT IS WORTH. `VmHWM` is the kernel's own high-water mark for a
process, so a peak is not missed between samples; the tree SUM is sampled, because a peak sum
only exists at an instant and a child that has already exited no longer reports. Both sides
therefore carry `peak_tree_rss_kb` (sampled, a lower bound) and `max_single_process_hwm_kb`
(exact for every process seen alive at least once).

The two suites share a box, so this is not a clean-room comparison: they contend for page cache
and each pushes the other toward reclaim. That biases both sides in the SAME direction, and the
finding's claim is about a DIFFERENCE of thousands of MB (12.9G vs whatever the gate reaches),
so contention cannot manufacture the effect -- but a reader must not quote these as the isolated
peaks of either run. `contended: true` is written into the record for exactly that reason.
"""
import json
import os
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "gate_x_premium_rss.json"

SAMPLE_SECONDS = 10
# A full suite is ~20 minutes; two of them plus the tail is comfortably inside an hour. The
# deadline exists so a sampler orphaned by a dead parent cannot outlive its subject forever.
DEADLINE_SECONDS = 90 * 60


def _read_status(pid):
    """(VmHWM_kb, VmRSS_kb) for a pid, or None if it is gone or unreadable."""
    try:
        text = Path("/proc/{}/status".format(pid)).read_text()
    except (OSError, ValueError):
        return None
    hwm = rss = None
    for line in text.splitlines():
        if line.startswith("VmHWM:"):
            hwm = int(line.split()[1])
        elif line.startswith("VmRSS:"):
            rss = int(line.split()[1])
        if hwm is not None and rss is not None:
            break
    if hwm is None or rss is None:
        return None
    return hwm, rss


def _children(pid):
    """Direct children of a pid via /proc/<pid>/task/*/children (never raises)."""
    kids = []
    try:
        for task in Path("/proc/{}/task".format(pid)).iterdir():
            try:
                kids.extend(int(p) for p in (task / "children").read_text().split())
            except (OSError, ValueError):
                continue
    except (OSError, ValueError):
        return []
    return kids


def _tree(pid):
    """pid and every descendant alive right now."""
    seen, stack = [], [pid]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        if not Path("/proc/{}".format(cur)).exists():
            continue
        seen.append(cur)
        stack.extend(_children(cur))
    return seen


def _cmdline(pid):
    try:
        return Path("/proc/{}/cmdline".format(pid)).read_text().split("\0")[:-1]
    except (OSError, ValueError):
        return []


def _mem_available_mb():
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def _utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class _Side:
    """One arm of the A/B: a root pid and the running peaks of its process tree."""

    def __init__(self, label, pid, has_x):
        self.label = label
        self.root_pid = pid
        self.has_x = has_x
        self.argv = _cmdline(pid)
        self.peak_tree_rss_kb = 0
        self.per_process_hwm_kb = {}
        self.samples = 0
        self.alive = True
        self.first_seen = _utc_now()
        self.last_seen = None
        self.started_monotonic = time.monotonic()
        self.observed_seconds = 0.0

    def sample(self):
        pids = _tree(self.root_pid)
        if not pids:
            self.alive = False
            return
        total = 0
        for pid in pids:
            got = _read_status(pid)
            if got is None:
                continue
            hwm, rss = got
            total += rss
            prev = self.per_process_hwm_kb.get(str(pid), 0)
            if hwm > prev:
                self.per_process_hwm_kb[str(pid)] = hwm
        if total > self.peak_tree_rss_kb:
            self.peak_tree_rss_kb = total
        self.samples += 1
        self.last_seen = _utc_now()
        self.observed_seconds = round(time.monotonic() - self.started_monotonic, 1)

    def record(self):
        hwms = self.per_process_hwm_kb.values()
        return {
            "label": self.label,
            "root_pid": self.root_pid,
            "has_dash_x": self.has_x,
            "argv_length": len(self.argv),
            "peak_tree_rss_kb": self.peak_tree_rss_kb,
            "peak_tree_rss_gb": round(self.peak_tree_rss_kb / 1024 / 1024, 2),
            "max_single_process_hwm_kb": max(hwms) if hwms else 0,
            "max_single_process_hwm_gb": round(max(hwms) / 1024 / 1024, 2) if hwms else 0.0,
            "processes_seen": len(self.per_process_hwm_kb),
            "samples": self.samples,
            "still_alive": self.alive,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "observed_seconds": self.observed_seconds,
        }


def _verdict(with_x, without_x):
    """What the two peaks say about the finding's claim -- or that they cannot say it.

    Fails to a NAMED inconclusive rather than to a number: a side that was never observed alive,
    or was still running when the sampler stopped, has a peak that is a lower bound only, and a
    lower bound cannot refute 'the -x-less side goes higher'."""
    if with_x["samples"] == 0 or without_x["samples"] == 0:
        return {"claim": "inconclusive",
                "why": "a side was never observed alive; nothing to compare"}
    truncated = [s["label"] for s in (with_x, without_x) if s["still_alive"]]
    a = with_x["max_single_process_hwm_kb"]
    b = without_x["max_single_process_hwm_kb"]
    if a == 0 or b == 0:
        return {"claim": "inconclusive", "why": "a side reported no peak"}
    ratio = round(b / a, 2)
    out = {
        "with_x_peak_process_gb": with_x["max_single_process_hwm_gb"],
        "without_x_peak_process_gb": without_x["max_single_process_hwm_gb"],
        "without_over_with": ratio,
    }
    if truncated:
        out["claim"] = "inconclusive"
        out["why"] = ("still running when the sampler stopped, so its peak is a lower bound: "
                      + ", ".join(truncated))
        return out
    out["claim"] = "supported" if ratio > 1.0 else "not_supported"
    out["why"] = ("the -x-less run peaked {}x the -x run's peak process"
                  .format(ratio) if ratio > 1.0 else
                  "the -x-less run did NOT peak above the -x run; the finding's -x-premium "
                  "explanation for the OOM is not supported by these peaks")
    return out


def _write(path, sides, started, note):
    payload = {
        "purpose": "the -x premium in peak memory, per "
                   "WORKER_FINDING_THE_MEASUREMENTS_SUBJECT_IS_LARGER_THAN_THE_GATES_2026-08-11",
        "started_at": started,
        "updated_at": _utc_now(),
        "sampler_pid": os.getpid(),
        "contended": True,
        "contention_note": note,
        "mem_available_mb": _mem_available_mb(),
        "complete": not any(s.alive for s in sides),
        "sides": {s.label: s.record() for s in sides},
    }
    payload["verdict"] = _verdict(payload["sides"]["with_x"], payload["sides"]["without_x"])
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n")
    tmp.replace(path)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 2:
        print("usage: sample_gate_rss_premium.py <pid-with-x> <pid-without-x> [out]",
              file=sys.stderr)
        return 2
    with_x_pid, without_x_pid = int(argv[0]), int(argv[1])
    out = Path(argv[2]) if len(argv) > 2 else OUT_PATH
    note = ("both suites were already running when sampling began and shared the box; peaks are "
            "contended and are not the isolated peak of either run")
    sides = [_Side("with_x", with_x_pid, True), _Side("without_x", without_x_pid, False)]
    started = _utc_now()
    deadline = time.monotonic() + DEADLINE_SECONDS
    # Written before the first sample so a sampler killed in its first 10 seconds still says it
    # existed -- the lesson the OPS2 instrument itself had to learn twice.
    _write(out, sides, started, note)
    while any(s.alive for s in sides) and time.monotonic() < deadline:
        for side in sides:
            if side.alive:
                side.sample()
        _write(out, sides, started, note)
        time.sleep(SAMPLE_SECONDS)
    _write(out, sides, started, note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
