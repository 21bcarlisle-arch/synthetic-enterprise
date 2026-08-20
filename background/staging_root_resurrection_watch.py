#!/usr/bin/env python3
"""
REUSE: background/staging_root_resurrection_watch.py
CLASS: CUSTOM
INDEX: searched "resurrection", "staging root", "two rooms", "reappear", "watcher", "inotify".
       `background/finding_classes.py` DETECTS the end state (a marker in two rooms) and refuses
       the commit; `background/staging_two_rooms_repair.py` REPAIRS that state. Neither can say
       WHO put the file back, and both are deliberately left alone here: a detector wants to be
       eager, a repairer wants to be timid, and an INSTRUMENT wants to be neither -- it records
       and never acts. `background/background_worker.py` sweeps markers on a 30-minute loop,
       which is three orders of magnitude coarser than the event this has to catch.

THE INSTRUMENT FOR A WRITER NOBODY HAS IDENTIFIED.

`WORKER_FINDING_ARCHIVED_RUN_MARKERS_RETURN_TO_THE_STAGING_ROOT_AND_BLOCK_EVERY_COMMIT_2026-08-20`
filed the condition with the evidence and WITHOUT a mechanism, and said why: two causes were
proposed from reading the code and both measured wrong. Its instruction to the next person is
the reason this module exists rather than a third theory:

    "start by instrumenting rather than by reading, because reading is what produced the two
     wrong answers."

THIS DOES NOT NAME A CAUSE EITHER. It makes the next occurrence self-documenting.

WHAT IT BRACKETS, AND WHY THAT WINDOW. The one strong clue already in hand is a TIMESTAMP: an
earlier batch of ten markers all returned with an identical mtime (21:26:11), and that mtime sat
inside a gate run -- `git reflog` puts `surgical-land` for 6b6f364f5 at 21:26:51, forty seconds
later. One mtime for ten files is a single simultaneous event, not a producer writing files one
at a time. So the window worth watching is not "always"; it is THE LANDING. `bracket()` censuses
the real staging root either side of the gate and records anything that appeared in between,
which turns "it happened during some gate run" into "it happened during THIS one, whose pathspec
and message are in the record".

WHY A CENSUS AND NOT A DAEMON. There is no `inotifywait` on this box, and a 1-second poller is a
new long-running process -- behaviour-determining state that would have to be declared and
reconciled (CLAUDE.md, IaC). A bracket needs no process of its own: it runs inside a caller that
already exists and already runs on every landing. `watch()` is still provided for the live case,
as a bounded foreground command a seat can point at the condition while it is happening; it is
not a daemon and nothing starts it automatically.

WHAT A RECORD HAS TO CARRY TO BE WORTH ANYTHING. The two wrong answers were both reached by
reasoning about actors with intent. So the record deliberately leads with facts that separate
MECHANISMS rather than motives:

  * `mtime_ns` per file, and whether the batch shares one -- a simultaneous restore (checkout,
    reset, merge, copy of a saved set) versus a drip (a producer).
  * `blob_known_to_git` -- whether the bytes on disk are already an object in this repo's store.
    A restore of a tracked path yields a KNOWN blob; a producer writing fresh text almost never
    does. This is the single most discriminating field in the record and it costs one
    `git hash-object`.
  * `tracked_at_head` -- whether the path the file reappeared at is one git could restore at all.
  * The PROCESS TABLE at the moment of detection. Whatever did this was running; a snapshot taken
    seconds later still names it, and no amount of later reading will.

FAIL-SAFE DIRECTION (R15). An instrument that can break the thing it observes is worse than no
instrument: this one is wrapped so that EVERY failure inside it -- census, forensics, `ps`, the
log write -- is swallowed, and an exception raised by the bracketed body propagates UNCHANGED.
The failure mode is "no record", never "no landing". `tests/background/
test_staging_root_resurrection_watch.py` mutates each half to prove both directions.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

# Module-level so tests redirect them. A real-disk path that tests do NOT pin leaks into every
# unpinned loader and starts recording other tests' fixtures as live evidence -- the same defect
# background_worker.SWEEP_STATE_FILE carries a comment about.
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
LOG_PATH = PROJECT_DIR / "docs" / "observability" / "staging_root_resurrection.jsonl"

# The staging root's exhaust: the file class the finding is about. Deliberately NOT every `*.md`
# -- findings and director docs arrive in the root legitimately and constantly, and a record that
# fires on those would be noise the next reader learns to ignore.
MARKER_PREFIXES = ("run_complete_", "run_pending_")

# Enough of the table to identify a writer, capped so one record cannot become the log.
PROCESS_TABLE_LIMIT = 60


def _is_marker(name: str) -> bool:
    return name.endswith(".md") and name.startswith(MARKER_PREFIXES)


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def census(staging_dir: Path | None = None) -> dict[str, dict]:
    """The staging ROOT's run markers, by name, with the two facts that separate a restore from
    a fresh write: when the bytes landed, and what they are.

    Returns {} on any unreadable directory -- an instrument reports nothing rather than raising
    into its caller.
    """
    root = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    out: dict[str, dict] = {}
    try:
        entries = list(os.scandir(root))
    except OSError:
        return out
    for entry in entries:
        if not entry.is_file() or not _is_marker(entry.name):
            continue
        try:
            st = entry.stat()
        except OSError:
            continue
        out[entry.name] = {
            "mtime_ns": st.st_mtime_ns,
            "size": st.st_size,
            "sha256": _sha256(Path(entry.path)),
        }
    return out


def appeared(before: dict[str, dict], after: dict[str, dict]) -> list[str]:
    """Names that arrived, or whose bytes were REWRITTEN, between two censuses.

    A rewrite counts. The observed condition is a file coming back, and a file that was never
    deleted but was overwritten with the pre-archive bytes presents identically to whoever hits
    the gate refusal -- scoping this to new names only would answer a narrower question than the
    finding asks.
    """
    out = []
    for name, now in after.items():
        was = before.get(name)
        if was is None or (now["sha256"] is not None and now["sha256"] != was.get("sha256")):
            out.append(name)
    return sorted(out)


def _git(root: Path, *args: str, stdin: bytes | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(["git", *args], cwd=str(root), input=stdin,
                           capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()


def forensics(name: str, root: Path | None = None, staging_dir: Path | None = None) -> dict:
    """Everything about ONE reappeared file that a later reader cannot re-derive.

    `blob_known_to_git` is the discriminating one. `git hash-object` computes the sha the bytes
    WOULD have as a git object, and `cat-file -e` asks whether that object is already in this
    repo's store. True means these exact bytes have been committed here before -- the signature
    of a checkout/reset/merge/saved-copy restore. False means something composed them, which
    rules out every git-restore theory in one field.
    """
    repo = Path(root) if root is not None else PROJECT_DIR
    sdir = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    path = sdir / name
    rel = os.path.relpath(path, repo)
    info: dict = {"name": name, "path": rel}
    try:
        st = path.stat()
        info["mtime_ns"] = st.st_mtime_ns
        info["mtime_iso"] = datetime.fromtimestamp(
            st.st_mtime, tz=timezone.utc).isoformat()
        info["size"] = st.st_size
    except OSError:
        info["mtime_ns"] = None
        info["mtime_iso"] = None
        info["size"] = None
    info["sha256"] = _sha256(path)

    rc, blob = _git(repo, "hash-object", "--", str(path))
    info["git_blob"] = blob if rc == 0 and blob else None
    if info["git_blob"]:
        exists, _ = _git(repo, "cat-file", "-e", info["git_blob"])
        info["blob_known_to_git"] = exists == 0
    else:
        info["blob_known_to_git"] = None

    rc, _ = _git(repo, "cat-file", "-e", "HEAD:{}".format(rel))
    info["tracked_at_head"] = rc == 0

    # The twin is what actually refuses the commit, so the record states it rather than leaving
    # the reader to re-run the detector against a tree that has since moved.
    twin = sdir / "done" / name
    info["twin_in_done"] = twin.is_file()
    if info["twin_in_done"]:
        try:
            root_bytes = path.read_bytes()
            twin_bytes = twin.read_bytes()
            info["twin_is_strict_superset"] = (
                twin_bytes.startswith(root_bytes) and len(twin_bytes) > len(root_bytes))
        except OSError:
            info["twin_is_strict_superset"] = None
    else:
        info["twin_is_strict_superset"] = None
    return info


def process_table(limit: int = PROCESS_TABLE_LIMIT) -> list[str]:
    """Who was running at the moment of detection.

    Taken FIRST-HAND and IMMEDIATELY, because it is the one fact that expires. Filtered to the
    processes that could plausibly write a repo path (`git`, `python`, `pytest`, `sh`) so the
    record stays readable, and capped so a busy box cannot turn one event into a log file.
    """
    rc = subprocess.run
    try:
        r = rc(["ps", "-eo", "pid,ppid,lstart,etimes,cmd"],
               capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if r.returncode != 0:
        return []
    lines = r.stdout.splitlines()
    keep = [ln for ln in lines[1:]
            if any(tok in ln for tok in ("git", "python", "pytest", "surgical", "/bin/sh"))]
    return keep[:limit]


def record(event: dict, out: Path | None = None) -> bool:
    """Append one JSONL record. True if it landed. Never raises."""
    target = Path(out) if out is not None else LOG_PATH
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")
        return True
    except (OSError, TypeError, ValueError):
        return False


def build_event(names: list[str], label: str, root: Path, staging_dir: Path,
                started: float, ended: float) -> dict:
    """Assemble the record. The batch-level fields are the ones that answer the mechanism
    question; the per-file ones are the evidence for them."""
    files = [forensics(n, root=root, staging_dir=staging_dir) for n in names]
    mtimes = {f["mtime_ns"] for f in files if f["mtime_ns"] is not None}
    known = [f["blob_known_to_git"] for f in files]
    return {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "window_seconds": round(ended - started, 3),
        "window_started": datetime.fromtimestamp(started, tz=timezone.utc).isoformat(),
        "count": len(files),
        # One mtime for a batch is a single simultaneous event -- a restore. A spread is a drip.
        "single_mtime": len(mtimes) == 1 and len(files) > 1,
        "distinct_mtimes": len(mtimes),
        # True for every file means the bytes were all already git objects: a restore, not a
        # producer. This is the field that would have settled the two wrong answers.
        "all_bytes_known_to_git": bool(known) and all(k is True for k in known),
        "head": _git(root, "rev-parse", "HEAD")[1] or None,
        "pid": os.getpid(),
        "files": files,
        "processes": process_table(),
    }


@contextmanager
def bracket(root: Path, label: str, staging_dir: Path | None = None, out: Path | None = None):
    """Census the staging root either side of `body`, and record anything that appeared.

    THE BODY IS SACRED. Every failure in here is swallowed; an exception from the body
    propagates unchanged. The `finally` is what makes the record survive a RED gate -- a landing
    that was refused is exactly as interesting as one that succeeded, and the earlier evidence
    says refused attempts are where some of this happens.
    """
    sdir = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    started = time.time()
    try:
        before = census(sdir)
    except Exception:            # noqa: BLE001 -- an instrument never breaks the observed
        before = None
    try:
        yield
    finally:
        if before is not None:
            try:
                names = appeared(before, census(sdir))
                if names:
                    record(build_event(names, label, Path(root), sdir, started, time.time()),
                           out=out)
            except Exception:    # noqa: BLE001 -- likewise, and this one is in a `finally`
                pass


def watch(duration: float, interval: float = 1.0, root: Path | None = None,
          staging_dir: Path | None = None, out: Path | None = None,
          _sleep=time.sleep) -> int:
    """Poll the staging root for `duration` seconds. Returns the number of events recorded.

    The live-case instrument: a seat that is currently watching commits get refused points this
    at the condition and gets the wall-clock and the process table of the next reappearance,
    which is what the finding asked for and could not get. Bounded and foreground BY DESIGN --
    nothing starts it, so it is not a process the repo has to declare and reconcile.
    """
    sdir = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    repo = Path(root) if root is not None else PROJECT_DIR
    deadline = time.time() + duration
    before = census(sdir)
    events = 0
    while time.time() < deadline:
        _sleep(interval)
        started = time.time()
        now = census(sdir)
        names = appeared(before, now)
        if names:
            # Built BEFORE `before` is advanced, and the process table is taken inside it: the
            # gap between the write and the snapshot is what decides whether the writer is still
            # on the table.
            if record(build_event(names, "watch", repo, sdir, started, time.time()), out=out):
                events += 1
        before = now
    return events


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[3])
    ap.add_argument("--watch", action="store_true",
                    help="poll the staging root and record reappearances")
    ap.add_argument("--duration", type=float, default=900.0,
                    help="seconds to watch (default 900)")
    ap.add_argument("--interval", type=float, default=1.0, help="poll interval (default 1s)")
    args = ap.parse_args(argv)
    if args.watch:
        n = watch(args.duration, interval=args.interval)
        print("recorded {} reappearance event(s) to {}".format(n, LOG_PATH))
        return 0
    current = census()
    twins = [n for n in current if (STAGING_DIR / "done" / n).is_file()]
    print(json.dumps({"root_markers": len(current), "twins_in_done": sorted(twins)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
