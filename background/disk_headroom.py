#!/usr/bin/env python3
"""
REUSE: background/disk_headroom.py
CLASS: CUSTOM
INDEX: searched "headroom", "disk space", "cleanup", "tmp", "reap", "housekeeping". Fourteen
       rows mention cleanup and thirteen are single-purpose deleters inside the thing that made
       the mess (`surgical_land` removes its own extract on the happy path, `epistemic_wall`
       its own worktree) -- each correct and each blind to the volume they share, which is how
       80 orphaned extracts reached 99% with no alarm anywhere.
       THE ONE REAL CANDIDATE IS `background/resource_headroom.py` AND IT IS THE SAME SHAPE:
       floors, bands, hysteresis, transition-only alarms, for MEMORY instead of disk. I did not
       extend it, and the reason is the finding this commit exists to fix rather than a
       preference: it was built 2026-08-10 after 64 oom-kills and HAS NEVER EXECUTED ONCE -- no
       caller, no unit test, no state file. Extending a module nobody runs would have produced a
       second dormant governor and called it reuse.
       WHAT IS REUSED IS THE DESIGN, deliberately and visibly: the same band names, the same
       hysteresis rule, the same R5 transition-only alarm contract, so the two read as siblings.
       WHAT IS NOT SHARED IS THE REAPER, and that asymmetry is the point -- memory has nothing
       to delete, disk deletes files, so this half fails toward KEEPING on any uncertainty while
       every other path here fails toward PRESSURE. Folding an irreversible act into a shared
       abstraction would have hidden that the two halves need opposite failure directions.
       AND THE SAME COMMIT WIRES `resource_headroom` INTO THE WORKER LOOP. The reuse the index
       could not suggest was not "call this module" but "run the one you already have".
Disk headroom: bounded lifetimes for scratch, and an alarm BEFORE exhaustion.

DIRECTOR RULING, 2026-08-19:

    "That's the second resource exhaustion in ten days — the memory cleanse was the same
     shape. There's a governor for RAM and nothing for disk. I don't want a third instance:
     make file and workspace housekeeping a standing property of the system, with the same
     teeth as anything else — bounded lifetimes, alarms before exhaustion rather than after,
     and no reliance on anyone noticing."

WHAT HAPPENED, MEASURED. On 2026-08-19 `/tmp` reached 99% — 152 MB free of 7.8 GB — and the
machine stopped: pytest failed en masse with ENOSPC, the publish gate could not create its
own checkout ("cannot mkdir", "git is not installed", then a VACUITY GUARD on a scope of 0
test files), and 81 test failures were disk rather than code. The cause was 80 abandoned repo
extracts at ~150 MB each — the throwaway checkouts `tools/surgical_land.py` and the publish
gate create to judge a resulting tree — accumulated over many sessions. Nothing reaped them
and nothing watched the free space. It was found by a human noticing the machine had stopped,
which is exactly the reliance the ruling forbids.

THE THREE PROPERTIES, EACH A SEPARATE MECHANISM (a single "clean up sometimes" would be the
prose-only rule MAKE_IT_STICK says evaporates):

  1. BOUNDED LIFETIMES — `reap()`. Every scratch directory this project creates matches a
     declared pattern and has a TTL. Past it, it is deleted. A directory that is in use by a
     live process is never reaped regardless of age, so a long gate run cannot be shot in the
     back.
  2. ALARM BEFORE EXHAUSTION — `observe()`. Bands with hysteresis, transitions only (R5), on
     the same design as `background/resource_headroom.py`. The floor is set to the space a
     full publish cycle actually needs, so the alarm predicts the stop rather than announcing
     it -- the failure the RAM governor's own comment names.
  3. ADMISSION — `admit()`. A caller about to create a scratch tree asks first. Below the
     floor it is refused, and refusing one extract is cheaper than an ENOSPC that fails every
     writer on the box at once.

FAIL-CLOSED, DELIBERATELY, AND IN THE DIRECTION THAT COSTS LEAST. An unreadable filesystem
reads as PRESSURE, not as healthy: a governor that cannot see the disk must not certify it.
`reap()` is the exception -- it refuses to delete anything it cannot positively identify as
scratch, because a reaper that deletes on uncertainty is a worse failure than a full disk.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".disk_headroom_state.json"

#: Where scratch actually lands. `/tmp` is a tmpfs on this box and is the one that stopped it.
#: BOTH scratch roots, and the second one was nearly missed. `/tmp` is the tmpfs that
#: stopped the machine, but the two biggest producers -- `tools/surgical_land.py` and the
#: publish gate -- default to `/var/tmp` (SE_LAND_EXTRACT_ROOT / SE_GATE_CHECKOUT_ROOT), which
#: is on the root filesystem. A governor watching only the volume that failed last time would
#: have been blind to the one where most of the scratch is actually written.
WATCHED = (Path("/tmp"), Path("/var/tmp"), PROJECT_DIR)

# Bands in MB free, with a hysteresis gap (R5). Set against what a publish cycle NEEDS, not
# against a round number: one gate extract is ~150 MB, a full publish cycle creates several
# plus pytest temporaries, and the observed working set for one cycle is ~1 GB. A floor of
# 2 GB is therefore roughly two cycles of warning -- enough to reap and still finish the run.
# The RAM governor's comment makes the same argument for the same reason: an alarm that waits
# for the last few hundred MB announces the kill rather than predicting it.
PRESSURE_FLOOR_MB = 2048
CRITICAL_FLOOR_MB = 512
RECOVERED_FLOOR_MB = 3072

HEALTHY, PRESSURE, CRITICAL = "healthy", "pressure", "critical"

#: Scratch this project creates, with how long it may live. Every entry is a pattern this
#: repository's own tooling produces -- nothing here guesses at another program's files.
#: TTLs are generous against the work that makes them: a publish gate runs ~20 minutes and a
#: contested surgical landing can re-gate three times, so two hours is several times the
#: longest legitimate life.
#: VERIFIED AGAINST THE CREATORS, not guessed. Each prefix was read out of the module that
#: makes it; a pattern that matches nothing is a decorative reaper, and the first draft of
#: this tuple had exactly that defect (`head-checkout-*` matches no directory this project
#: has ever created -- the publish gate's prefix is `publish-gate-head-`).
SCRATCH_PATTERNS: tuple[tuple[str, int], ...] = (
    # tools/epistemic_wall.py:651   tempfile.mkdtemp(prefix="wall-head-")
    ("wall-head-*", 2 * 3600),
    # tools/surgical_land.py:611    mkdtemp(prefix="surgical-land-", dir=EXTRACT_ROOT=/var/tmp)
    ("surgical-land-*", 2 * 3600),
    # tools/surgical_land.py:332    mkstemp(prefix="surgical-land-index-")
    ("surgical-land-index-*", 2 * 3600),
    # process_run_complete.py:1753  mkdtemp(HEAD_CHECKOUT_PREFIX, dir=/var/tmp)
    ("publish-gate-head-*", 2 * 3600),
    # pytest's own root; it keeps the last 3, this bounds everything older
    ("pytest-of-*", 6 * 3600),
)

#: Both roots are reaped. A reaper pointed at one volume while the tooling writes to two is
#: the same blind spot as a governor watching one.
REAP_ROOTS = (Path("/tmp"), Path("/var/tmp"))


class DiskUnavailable(RuntimeError):
    """The filesystem could not be read. Treated as PRESSURE, never as healthy."""


def sample(paths: tuple[Path, ...] = WATCHED) -> dict:
    """Free space per watched path, plus the tightest of them."""
    out = {}
    for p in paths:
        try:
            usage = shutil.disk_usage(p)
        except OSError as e:
            raise DiskUnavailable(f"{p}: {e}") from e
        out[str(p)] = {
            "free_mb": usage.free // (1024 * 1024),
            "total_mb": usage.total // (1024 * 1024),
            "used_pct": round(100 * usage.used / usage.total, 1) if usage.total else 100.0,
        }
    if not out:
        raise DiskUnavailable("no watched path could be read")
    tightest = min(out.items(), key=lambda kv: kv[1]["free_mb"])
    return {"paths": out, "tightest": tightest[0], "free_mb": tightest[1]["free_mb"],
            "used_pct": tightest[1]["used_pct"]}


def band(free_mb: int, previous: str | None = None) -> str:
    """Band with hysteresis: recovery needs more headroom than entry cost, so a filesystem
    hovering at the floor does not alarm on every sample."""
    if free_mb <= CRITICAL_FLOOR_MB:
        return CRITICAL
    if free_mb <= PRESSURE_FLOOR_MB:
        return PRESSURE
    if previous in (PRESSURE, CRITICAL) and free_mb < RECOVERED_FLOOR_MB:
        return PRESSURE  # not recovered yet -- do not announce an all-clear at the boundary
    return HEALTHY


def _state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(payload: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def in_use_dirs() -> set[str]:
    """Directories a live process is sitting in. Never reaped, whatever their age."""
    live = set()
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            live.add(os.readlink(proc / "cwd"))
        except OSError:
            continue
    return live


def reapable(now: float | None = None, roots: tuple[Path, ...] = REAP_ROOTS) -> list[dict]:
    """Scratch past its TTL and not in use. Identification is POSITIVE ONLY: a directory that
    matches no declared pattern is never a candidate, however old and however large."""
    now = now or time.time()
    busy = in_use_dirs()
    out = []
    for root in roots:
        if not root.is_dir():
            continue
        for pattern, ttl in SCRATCH_PATTERNS:
          for path in root.glob(pattern):
            if not path.is_dir():
                continue
            if str(path) in busy:
                continue
            try:
                age = now - path.stat().st_mtime
            except OSError:
                continue
            if age < ttl:
                continue
            out.append({"path": str(path), "age_h": round(age / 3600, 1), "ttl_h": ttl // 3600})
    return out


def reap(dry_run: bool = False, roots: tuple[Path, ...] = REAP_ROOTS) -> dict:
    """Delete scratch past its TTL. Returns what went, so the log is a receipt."""
    victims = reapable(roots=roots)
    freed = 0
    removed = []
    for v in victims:
        p = Path(v["path"])
        try:
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
        except OSError:
            size = 0
        if not dry_run:
            shutil.rmtree(p, ignore_errors=True)
        freed += size
        removed.append({**v, "mb": size // (1024 * 1024)})
    return {"removed": removed, "freed_mb": freed // (1024 * 1024), "dry_run": dry_run}


def stdlib_shadows(roots: tuple[Path, ...] = REAP_ROOTS) -> list[dict]:
    """Stray files in shared scratch whose NAME shadows a standard-library module.

    Found the hard way on 2026-08-19: an ad-hoc debugging script saved as `/tmp/bisect.py`
    shadowed the stdlib `bisect` for every process whose cwd was `/tmp` -- and
    `tests/hooks/test_pull_next_work.py` runs a subprocess there BY DESIGN, to prove the Stop
    hook imports correctly from an alien cwd. So a throwaway script broke a control in an
    unrelated subsystem through its filename alone, went red at HEAD, and blocked every commit
    that selected it. Nothing connected the two, and nothing would have.

    Reported, never deleted: these are somebody's working files and a governor that silently
    removes them is worse than the collision. The point is that the collision becomes VISIBLE
    before it costs another morning.
    """
    import sys

    stdlib = set(sys.stdlib_module_names)
    out = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.glob("*.py"):
            if path.stem in stdlib:
                out.append({"path": str(path), "shadows": path.stem,
                            "risk": f"any process with cwd={root} imports this instead of the "
                                    f"standard library {path.stem!r}"})
    return out


def admit(need_mb: int = 256, paths: tuple[Path, ...] = WATCHED) -> tuple[bool, str]:
    """May a caller create a scratch tree? Refusing one extract beats an ENOSPC that fails
    every writer on the box. Reaps first: the space may already be there."""
    s = sample(paths)
    if s["free_mb"] - need_mb > PRESSURE_FLOOR_MB:
        return True, f"{s['free_mb']} MB free on {s['tightest']}"
    freed = reap()
    s = sample(paths)
    if s["free_mb"] - need_mb > PRESSURE_FLOOR_MB:
        return True, (f"admitted after reaping {freed['freed_mb']} MB from "
                      f"{len(freed['removed'])} expired scratch dir(s)")
    return False, (f"REFUSED: {s['free_mb']} MB free on {s['tightest']}, need {need_mb} MB and "
                   f"a {PRESSURE_FLOOR_MB} MB floor; reaping freed only {freed['freed_mb']} MB")


def observe(paths: tuple[Path, ...] = WATCHED) -> dict:
    """One sample, banded, alarming on TRANSITION only (R5). This is what a scheduled caller
    runs; it never repeats an unchanged status."""
    try:
        s = sample(paths)
        current = band(s["free_mb"], _state().get("band"))
    except DiskUnavailable as e:
        s, current = {"free_mb": 0, "used_pct": 100.0, "tightest": "unreadable",
                      "error": str(e)}, PRESSURE
    prev = _state().get("band")
    changed = current != prev
    payload = {"band": current, "previous": prev, "changed": changed,
               "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **s}
    shadows = stdlib_shadows()
    if shadows:
        payload["stdlib_shadows"] = shadows
        payload["shadow_alarm"] = (
            f"{len(shadows)} stray file(s) in shared scratch shadow a standard-library module: "
            + ", ".join(f"{s['path']} shadows {s['shadows']!r}" for s in shadows)
            + ". Any process running there imports the stray file instead. On 2026-08-19 this "
              "reddened a hook control at HEAD and blocked the tree. Not deleted -- they are "
              "someone's working files -- but they must not stay invisible."
        )
    if current in (PRESSURE, CRITICAL) and changed:
        payload["alarm"] = (
            f"DISK {current.upper()}: {s['free_mb']} MB free on {s['tightest']} "
            f"({s['used_pct']}% used). Floor is {PRESSURE_FLOOR_MB} MB. This alarms BEFORE "
            f"exhaustion by design -- on 2026-08-19 the machine stopped at 152 MB with no "
            f"warning at all. `python3 -m background.disk_headroom --reap` clears expired scratch."
        )
    _save(payload)
    return payload


def main(argv=None) -> int:  # pragma: no cover - operator surface
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reap", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.reap:
        r = reap(dry_run=args.dry_run)
        print(json.dumps(r, indent=2) if args.json else
              f"{'would free' if args.dry_run else 'freed'} {r['freed_mb']} MB from "
              f"{len(r['removed'])} expired scratch dir(s)")
        return 0
    o = observe()
    if args.json:
        print(json.dumps(o, indent=2))
    else:
        print(f"disk: {o['band'].upper()} -- {o['free_mb']} MB free on {o['tightest']} "
              f"({o.get('used_pct')}% used)")
        if o.get("alarm"):
            print(o["alarm"])
    return 1 if o["band"] == CRITICAL else 0


if __name__ == "__main__":
    raise SystemExit(main())
