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
import subprocess
import time
from pathlib import Path

from background.live_ledger_guard import guard_live_ledger_write

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

#: THE TYPED LIST ABOVE CANNOT SEE THE POPULATION THAT ACTUALLY FILLS THIS DISK, MEASURED.
#: On 2026-08-21 `/tmp` reached 84% of a 7.8 GB *tmpfs* -- 6.5 GB, which on this box is 6.5 GB
#: of the 16 GB of RAM, so swap hit 100% (0 MB free) and the box thrashed. 3,336 MB of that was
#: 22 abandoned repo copies: `wouldbe`, `wouldbe2`, `g13head`, `g13tree`, `knife3-step46`,
#: `wtree`, `ep6probe`, `ep6probe2`, `ep6probe.hafg`, `ep6tree.qeTc`, `tmp.U4B5Vgh6lA` ...
#: `reapable()` matched ZERO of the 22 and would have freed 0 of the 3,336 MB.
#:
#: The reason is structural, not an oversight in the list: SCRATCH_PATTERNS is a TYPED LIST of
#: five `mkdtemp` prefixes read out of five modules, and every one of those 22 directories was
#: made by a lane's ad-hoc `mkdir`/`mktemp -d` in a shell command. A name-based reaper can only
#: ever cover names somebody remembered to declare, and the lane that invents the next name
#: will not be the lane that edits this tuple. The list was already caught being decorative
#: once (`head-checkout-*`, see above); this is the same defect one level up.
#:
#: SO IDENTIFY BY CONTENT, WHICH NOBODY HAS TO REMEMBER TO DECLARE. A directory carrying all
#: of these paths is a copy of THIS repository -- something this project provably created, so
#: POSITIVE IDENTIFICATION (the doctrine in the module docstring) is preserved in full. This is
#: a DERIVED rule where the tuple above is an enumerated one, and it stays true for scratch
#: whose name has never been seen before.
REPO_SIGNATURE: tuple[str, ...] = (
    "CLAUDE.md",
    "PRIORITIES.md",
    "background/supervisor.py",
    "docs/PROJECT_OVERVIEW.md",
)

#: Generous against the work that makes these: an EP6 probe or a KNIFE step tree is a
#: multi-hour lane, so six hours is well past any legitimate life while still bounding the
#: accretion to one working session rather than the four days observed.
REPO_COPY_TTL = 6 * 3600


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
    guard_live_ledger_write(STATE_FILE, writer="disk_headroom._save")
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


def _is_repo_copy(path: Path) -> bool:
    """True if `path` carries every file in REPO_SIGNATURE -- i.e. it is a copy of this repo."""
    try:
        return all((path / rel).exists() for rel in REPO_SIGNATURE)
    except OSError:
        return False


def _git_dir_may_hold_work(git_path: Path) -> bool:
    """Could this `.git` hold a commit or an edit that exists nowhere else? FAIL-CLOSED: yes.

    THE EXCLUSION IS RIGHT AND WAS UNCHECKED (2026-09-02). `repo_copy_scratch` skipped any
    directory containing `.git`, on the stated ground that *"a registered worktree, a clone, or a
    gate checkout can hold committed branches or uncommitted edits that exist nowhere else"*. That
    reason is sound; nothing ever tested whether it was TRUE of the directory in front of it.

    MEASURED: `/tmp/hc2` — 232 MB, 40 hours old, `.git` present, **zero refs and no HEAD**. An
    empty `.git` directory made 232 MB immortal, and the module reported *"nothing reapable (all
    scratch in use or within TTL)"* while `/tmp` sat at 89% of a 12 GB tmpfs and the box's largest
    red of the month was an environmental failure on that filesystem.

    A control that fires correctly and does nothing is the same family as one that cannot fire.

    SO THE REASON IS EVALUATED RATHER THAN ASSUMED, and only in the one direction that is safe:
    a `.git` with NO refs and NO resolvable HEAD holds nothing, so it cannot be the thing the
    exclusion protects. Every other outcome — refs present, HEAD resolves, git unavailable, the
    call raises, a `.git` FILE rather than a directory (a linked worktree, whose real gitdir is
    elsewhere and whose work this reaper must never pre-empt) — keeps the directory. The failure
    direction is unchanged: uncertainty spares.
    """
    if not git_path.exists():
        return False
    if not git_path.is_dir():
        return True            # a `.git` FILE is a linked worktree pointer -- never our business
    try:
        refs = subprocess.run(["git", "--git-dir", str(git_path), "for-each-ref", "--count=1"],
                              capture_output=True, text=True, timeout=15)
        head = subprocess.run(["git", "--git-dir", str(git_path), "rev-parse", "--verify", "HEAD"],
                              capture_output=True, text=True, timeout=15)
    except Exception:  # noqa: BLE001 -- ANY failure to ask means we did not establish emptiness,
        return True    # and a probe that crashed the reaper would be worse than one that spared
    if refs.returncode != 0:
        return True            # not a readable repository -> assume it holds work
    return bool(refs.stdout.strip()) or bool(head.stdout.strip())


def _owner_pid_from_name(name: str) -> int | None:
    """The pid a scratch directory's NAME records, or None if it records none.

    THE TTL IS A PROXY FOR A QUESTION IT CANNOT ASK (2026-09-04). `REPO_COPY_TTL` exists because
    *"a probe that is still running is not abandoned"* — six hours, chosen against a multi-hour
    KNIFE or EP6 lane. But the population that actually fills this filesystem is `git archive HEAD`
    extracts from finished seat turns: ~288 MB each, no `.git`, and **dead within the hour**. The
    module reported *"nothing reapable (all scratch in use or within TTL)"* while `/tmp` — a 12 GB
    **tmpfs, i.e. RAM on this box** — sat at 83%, and the DISK CRITICAL alarm said it needed a
    person. 2.0 GB was then freed by hand. On a machine where an OOM kill has already destroyed a
    published bound, that is memory pressure, not housekeeping.

    So where the owner is RECORDED, ask it directly instead of waiting out a proxy. The only place
    it is recorded is the directory name (`bisect_daemon_1563179`), so this reads a trailing digit
    run after a `-` or `_` separator.

    NOT A NUMBER PICKED TO MAKE THIS WORK. The upper bound is the kernel's own `pid_max`: a
    trailing number above it cannot be a pid, so it is not an owner claim and the directory keeps
    its TTL. Nothing here loosens the TTL, which is the move that would make the measurement come
    out and teach nothing.

    THE FAILURE DIRECTION IS UNCHANGED — uncertainty spares:
      * no trailing digits           -> None -> TTL applies, exactly as before.
      * a recycled pid, now some other process -> reads ALIVE -> spared.
      * `/proc` unreadable           -> reads ALIVE -> spared (`_pid_is_alive`).
      * a number that is not a pid but is below `pid_max` and matches no live process -> reaped
        early. Bounded by every exclusion above it: it must ALSO be a content-identified copy of
        this repository, carry no `.git`, and have no live process anywhere inside it.

    WHAT THIS DOES NOT REACH, stated because a silent cap reads as coverage: three of the four
    extracts measured on 2026-09-04 (`headext`, `headx`, `prereg_3d36`, ~865 MB) record no owner in
    their names, so they still wait out the full six hours. The residue is the absence of any record
    of who made them — a separate decision, filed, not something to fix by moving the TTL.
    """
    stem = name.rstrip("0123456789")
    digits = name[len(stem):]
    if not digits or not stem or stem[-1] not in "-_":
        return None
    try:
        pid = int(digits)
    except ValueError:               # unreachable via the slice above; kept fail-closed
        return None
    if pid <= 0 or pid > _pid_max():
        return None
    return pid


def _pid_max() -> int:
    """The kernel's pid ceiling. Unreadable -> 0, which makes every candidate 'not a pid' and
    hands the whole population back to the TTL. Failing to read a bound may never widen it."""
    try:
        return int(Path("/proc/sys/kernel/pid_max").read_text().strip())
    except (OSError, ValueError):
        return 0


def _pid_is_alive(pid: int) -> bool:
    """FAIL-CLOSED: anything that stops us establishing death reads as alive, and alive spares."""
    try:
        return Path(f"/proc/{pid}").exists()
    except OSError:
        return True


def repo_copy_scratch(now: float | None = None,
                      roots: tuple[Path, ...] = REAP_ROOTS,
                      project_dir: Path = PROJECT_DIR) -> list[dict]:
    """Abandoned COPIES OF THIS REPOSITORY in shared scratch, identified by content.

    The companion to SCRATCH_PATTERNS, for the population a name list structurally cannot
    reach (see the REPO_SIGNATURE comment: 22 dirs / 3,336 MB, none of them matched).

    EVERY UNCERTAINTY KEEPS, matching this module's stated failure direction -- the four
    exclusions below are each a case where something that LOOKS like abandoned scratch might
    be a lane's live or unsaved work:

      * `.git` present -> NEVER a candidate. A registered worktree, a clone, or a gate
        checkout can hold committed branches or uncommitted edits that exist nowhere else.
        Worktree accretion is a different mechanism's job (`fork_reconciler`, report-only by
        ruling) and this reaper must not pre-empt it. This exclusion alone spares every
        worktree in `git worktree list` without needing to shell out to git.
      * in use by a live process -> never reaped at any age, as for patterned scratch.
      * the project itself, or anything containing/contained by it -> never a candidate, so a
        misconfigured root can never point the reaper at the working tree.
      * younger than REPO_COPY_TTL -> a probe that is still running is not abandoned.
    """
    now = now or time.time()
    busy = in_use_dirs()
    try:
        project = project_dir.resolve()
    except OSError:
        return []          # cannot establish what to protect -> reap nothing
    out = []
    for root in roots:
        if not root.is_dir():
            continue
        try:
            children = list(root.iterdir())
        except OSError:
            continue
        for path in children:
            if not path.is_dir() or path.is_symlink():
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved == project or resolved in project.parents or project in resolved.parents:
                continue
            if _git_dir_may_hold_work(path / ".git"):
                continue
            if not _is_repo_copy(path):
                continue
            if str(path) in busy or str(resolved) in busy:
                continue
            if any(b.startswith(str(resolved) + os.sep) for b in busy):
                continue          # a process is sitting somewhere INSIDE the tree
            try:
                age = now - path.stat().st_mtime
            except OSError:
                continue
            owner = _owner_pid_from_name(path.name)
            dead_owner = owner is not None and not _pid_is_alive(owner)
            if age < REPO_COPY_TTL and not dead_owner:
                continue
            out.append({"path": str(path), "age_h": round(age / 3600, 1),
                        "ttl_h": REPO_COPY_TTL // 3600, "kind": "repo-copy",
                        "reason": f"dead-owner pid {owner}" if dead_owner else "past-ttl"})
    return out


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
            out.append({"path": str(path), "age_h": round(age / 3600, 1), "ttl_h": ttl // 3600,
                        "kind": "patterned"})
    # The derived half. Kept as a separate source rather than folded into the loop above so the
    # two identification RULES stay visibly different things: one enumerates names, one reads
    # content, and the receipt says which found each victim.
    seen = {v["path"] for v in out}
    for v in repo_copy_scratch(now=now, roots=roots):
        if v["path"] not in seen:
            out.append(v)
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
    # SELF-HEAL BEFORE PAGING, because the alarm's own remedy was a sentence asking a human to
    # run a command. `observe()` was wired into the worker loop on 2026-08-19 and `reap()` was
    # not wired into anything: `admit()`, its only in-module caller, has no production caller
    # either, so between them the reaper had never executed outside a test. The 2026-08-19
    # ruling forbids exactly this -- "alarms before exhaustion rather than after, and no
    # reliance on anyone noticing" -- and a governor that only narrates is the reliance.
    # Only under PRESSURE/CRITICAL: reaping is not free, and a healthy box should not walk
    # shared scratch every worker cycle.
    if current in (PRESSURE, CRITICAL):
        try:
            freed = reap()
            if freed["removed"]:
                # DiskUnavailable is caught with OSError below: an unreadable filesystem must
                # keep reading as PRESSURE (the asymmetry this module is built on), and a
                # re-sample that raises here would take the whole governor out through
                # `observe()` -- which is worse than the exhaustion it watches for. Found by
                # test_MUTATION_FAIL_CLOSED_..., which is the test earning its keep.
                s = sample(paths)
                current = band(s["free_mb"], _state().get("band"))
                payload_reap = (f"reaped {freed['freed_mb']} MB from {len(freed['removed'])} "
                                f"expired scratch dir(s): "
                                + ", ".join(f"{r['path']}({r.get('kind', '?')})"
                                            for r in freed["removed"]))
            else:
                payload_reap = "nothing reapable (all scratch in use or within TTL)"
        except (OSError, DiskUnavailable) as e:
            # An unreapable filesystem is reported, never swallowed, and never treated as
            # having recovered the space. `current` is left at whatever the band above said,
            # which for an unreadable filesystem is PRESSURE.
            payload_reap = f"reap FAILED: {e}"
    else:
        payload_reap = None

    prev = _state().get("band")
    changed = current != prev
    payload = {"band": current, "previous": prev, "changed": changed,
               "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **s}
    if payload_reap is not None:
        payload["reaped"] = payload_reap
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
            f"warning at all. Expired scratch was ALREADY reaped before this alarm fired "
            f"({payload_reap}); this band is what remains after that, so it needs a person."
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
    # SEAT GUARD, first non-import statement (2026-08-27). A daemon started from a
    # foreign seat writes this tree while the real seat is also writing it; the guard
    # refuses instead. Structural rule, enforced by
    # tests/background/test_seat_guard_daemons.py::TestStructuralLock.
    from background._seat import refuse_if_foreign

    refuse_if_foreign("disk_headroom")
    raise SystemExit(main())
