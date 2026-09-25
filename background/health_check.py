#!/usr/bin/env python3
"""Autonomous stack health check.

Verifies that every expected background process is running and that the
staging directory is being policed. Sends an NTFY summary. Exits 0 if all
healthy, 1 if any process is missing (so the caller can alert or restart).

Usage:
    python3 background/health_check.py          # print + NTFY on failure only
    python3 background/health_check.py --always # print + NTFY regardless
    python3 background/health_check.py --quiet  # no output, NTFY on failure only
"""

import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "health-check-log.md"

sys.path.insert(0, str(PROJECT_DIR))
# The set of daemons whose ABSENCE is a fault, DERIVED from the single declared
# manifest (background/process_manifest.yaml) rather than hand-maintained here.
# OPS1 sub-step 2 (G-L2): the old hand-maintained dict had silently DRIFTED from
# start_worker.sh's launch set — it was missing naive-organ, so the health check was
# blind to whether that daemon was running. There is now ONE declaration; this derives
# from it, and a test binds the manifest to start_worker.sh so drift can't recur silently.
# Dark-gated (executor-daemon, correctly absent when not enabled) and support services
# (token-proxy, file-api) carry health_checked:false in the manifest, so they are excluded
# here exactly as before — plus naive-organ is now correctly included.
from background import process_reconciler as _reconciler  # noqa: E402
from background import tree_lock  # noqa: E402
from background.notify import notify  # noqa: E402
from tools import maturity_map_store as map_store  # noqa: E402

EXPECTED_PANES = _reconciler.health_checked_map()


def _tmux_panes() -> dict[str, str]:
    """Return {session_name: pane_command} for all running tmux panes."""
    try:
        out = subprocess.check_output(
            ["tmux", "list-panes", "-a", "-F",
             "#{session_name} #{pane_current_command}"],
            text=True, timeout=5,
        )
        result = {}
        for line in out.splitlines():
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                result[parts[0]] = parts[1]
        return result
    except Exception:
        return {}


def _running_scripts() -> list[str]:
    """Return list of python script paths currently running as processes."""
    try:
        out = subprocess.check_output(
            ["ps", "aux"], text=True, timeout=5,
        )
        return [line for line in out.splitlines() if "python" in line.lower()]
    except Exception:
        return []


def _process_start_times_by_script() -> dict[str, "datetime"]:
    """{script_basename: LATEST real python-daemon start time (UTC)} for every
    currently-running python process actually EXECUTING one of EXPECTED_PANES'
    own scripts. Uses `ps -eo lstart,args` (one call, no per-PID lookups) --
    lstart's fixed-width `%c` format ("Mon Jul 13 06:52:48 2026") is parsed
    directly, in the machine's own local timezone (matches file mtimes, which
    are also local-time-based via os.stat -- both sides of the later
    comparison use the same clock).

    2026-07-13 precision fix (found live, false-positive): the previous
    version matched ANY process whose command line merely CONTAINED the
    script path -- which wrongly includes the launcher/wrapper command lines
    that name the script as an ARGUMENT, not as the thing they execute:
      - `tmux new-session -d -s background-worker ... python3 background/background_worker.py`
        (a lingering launcher process, alive since the ORIGINAL session
        creation -- its ancient start time made a freshly-restarted daemon
        read as "stale")
      - `sh -c python3 background/background_worker.py` (the pane's wrapper
        shell -- the real daemon is its python3 CHILD, a separate process)
    Both are excluded now by requiring the process's own EXECUTABLE (first
    argv token) to be a python interpreter. And because a restart can leave
    an old orphan briefly co-existing with the new process, this takes the
    LATEST start time per script (the authoritative just-restarted process),
    so a genuinely-completed restart reads green rather than being dragged
    stale by a lingering older match."""
    try:
        out = subprocess.check_output(
            ["ps", "-eo", "lstart,args"], text=True, timeout=5,
        )
    except Exception:
        return {}
    result: dict[str, "datetime"] = {}
    for line in out.splitlines()[1:]:  # skip the header row
        line = line.strip()
        if not line:
            continue
        # lstart is always exactly 24 chars wide in `ps`'s own fixed format
        # ("Mon Jul 13 06:52:48 2026"), args is everything after.
        if len(line) < 25:
            continue
        lstart_str, args = line[:24], line[25:]
        tokens = args.split()
        if not tokens:
            continue
        # The process's OWN executable must be a python interpreter -- this is
        # what distinguishes the real daemon (`python3 background/foo.py`) from
        # a `tmux .../`sh -c` line that merely names the script as an argument.
        exe = tokens[0].rsplit("/", 1)[-1]
        if not exe.startswith("python"):
            continue
        for script in EXPECTED_PANES.values():
            if script in args:
                try:
                    started = datetime.strptime(lstart_str, "%a %b %d %H:%M:%S %Y")
                except ValueError:
                    continue
                # Latest wins: the just-restarted process is authoritative.
                if script not in result or started > result[script]:
                    result[script] = started
    return result


def _check_stale_running_code() -> str | None:
    """R2/R3 class ("committed != running", now a REPEAT occurrence --
    2026-07-13, ANTI_LIVELOCK_AND_WIDTH.md's own fix sat committed on disk
    for 17 real minutes while the live supervisor.py process, started
    2026-07-12 20:29, kept running the pre-fix code -- the identical class
    already found once before for the same daemon, "supervisor tmux daemon
    had stale pre-fix code loaded since 14:14"). A manual restart fixed the
    incident both times; per R3 (two-strike redesign), the manual fix is
    not enough the second time -- this function is the mechanism, not
    another one-off restart.

    For every EXPECTED_PANES daemon, compares its own script file's mtime
    against its actual running process's start time (via `ps`, not assumed
    from the tmux pane's own shell -- `_start_session()` launches
    `sh -c "python3 <script>"`, so the real long-lived process is a CHILD
    of the pane's own PID, not the pane PID itself). A process that started
    BEFORE its own script was last modified is running stale code -- flagged
    as a real, named finding, never silently "probably fine."

    Named limitation, not hidden: only checks each daemon's OWN top-level
    script file, not every module it transitively imports (e.g. supervisor.py
    importing a changed background/tree_lock.py would not be caught here) --
    a real, cheaper, high-precision check for the exact incident class that
    has now recurred twice, not a general "any code changed anywhere"
    scanner (which would flag near-constantly and erode the signal, the
    same "cries wolf" risk this project already avoids for the epistemic
    verifier and the stale-dependency check)."""
    started_by_script = _process_start_times_by_script()
    background_dir = PROJECT_DIR / "background"
    stale = []
    for session, script in EXPECTED_PANES.items():
        started = started_by_script.get(script)
        if started is None:
            continue  # not running at all -- the existing pane/process check already covers this
        script_path = background_dir / script
        if not script_path.is_file():
            continue
        mtime = datetime.fromtimestamp(script_path.stat().st_mtime)
        if mtime > started:
            age_min = (mtime - started).total_seconds() / 60
            stale.append(f"{session} ({script}): running since {started:%Y-%m-%d %H:%M}, own script modified {mtime:%Y-%m-%d %H:%M} ({age_min:.0f}min of drift)")
    if stale:
        return "Stale running code (restart to pick up committed changes): " + "; ".join(stale)
    return None


def stale_daemon_sessions() -> list[str]:
    """The ACTION half of _check_stale_running_code's DETECTION (2026-07-16, Item 3
    "a restart must deploy current HEAD"). Returns the tmux SESSION NAMES whose live
    process started BEFORE its own script's last modification -- i.e. is running code
    older than what's committed on disk. start_worker.sh kills exactly these before its
    start block, so its own `has-session` skip ("safe to re-run") stops meaning "leave
    stale code running" and starts meaning "already on current HEAD, nothing to do."

    This closes the gap the 2026-07-13 retro named but left as detect-only: every fix
    shipped to a running daemon was silently defeated until a human noticed the symptom
    and manually restarted. A (re)start now deploys HEAD by construction.

    Same OWN-top-level-script scope + limitation as _check_stale_running_code (a changed
    transitively-imported module is not caught here) -- a high-precision check for the
    exact recurred incident class, not a cries-wolf "anything changed" scanner."""
    started_by_script = _process_start_times_by_script()
    background_dir = PROJECT_DIR / "background"
    stale_sessions: list[str] = []
    for session, script in EXPECTED_PANES.items():
        started = started_by_script.get(script)
        if started is None:
            continue  # not running -> _start_session will start it fresh anyway
        script_path = background_dir / script
        if not script_path.is_file():
            continue
        if datetime.fromtimestamp(script_path.stat().st_mtime) > started:
            stale_sessions.append(session)
    return stale_sessions


def _pixel_verification_root() -> Path:
    """The ONE tree whose `node_modules/` the Playwright probe must resolve
    against, identical from the main tree and from every linked worktree.

    `common_git_dir()` names the single shared `.git`, so its parent is the main
    worktree -- the only checkout where a gitignored `node_modules/` can live.
    Reused from `background/tree_lock.py` rather than re-deriving here: there is
    one correct answer to "which tree is the shared one" and it should have one
    implementation.

    Falls back to `PROJECT_DIR` when the resolved root carries no `package.json`
    (a bare/absent git dir, or a layout where the parent is not a checkout), so
    the probe degrades to its old cwd-ish behaviour rather than raising -- and a
    genuinely missing Playwright still reports unavailable either way.
    """
    root = tree_lock.common_git_dir(PROJECT_DIR).parent
    return root if (root / "package.json").is_file() else PROJECT_DIR


# The browser binaries a pixel check on THIS machine actually launches -- not
# the set Playwright would install if asked. `browsers.json` marks chromium,
# chromium-headless-shell, firefox, webkit and ffmpeg `installByDefault`, and
# only the headless shell and ffmpeg are on disk here; keying the probe to
# `installByDefault` would red a machine whose pixel checks all pass, which is
# the exact false-red that cost a full Lane 0 item on 2026-09-17.
#
# ffmpeg is video recording, not pixel verification, and is excluded despite
# being present -- requiring a browser because it happens to be on disk today is
# keying the control to today's answer.
#
# `chromium-1234` IS on disk (installed 2026-09-17) and is still NOT required
# here, for that same reason. What was called "the headed gap" turned out to be
# the FULL-BINARY gap, and the difference is not pedantry -- measured with it
# absent, BOTH of these failed on the identical missing executable:
#   chromium.launch(headless=False)                   -> Executable doesn't exist
#   chromium.launch(headless=True, channel="chromium")-> Executable doesn't exist
# The second is a HEADLESS mode: Playwright's own accurate-rendering channel.
# "We only render headless here, so it cannot matter" was therefore false, which
# is why the binary was installed rather than the absence being written down.
# Headed additionally needs a display -- the binary alone is not the capability:
# docs/design/PIXEL_VERIFICATION_ON_THIS_MACHINE.md has what renders and how.
#
# WHEN TO ADD A NAME HERE: when something in the tree LAUNCHES it. That used to
# be this sentence and nothing else, which is to say nothing decided when it
# stopped being true. It is now graded in both directions --
# `test_the_requirement_tracks_what_the_tree_launches_in_both_directions`
# reds if a consumer appears without the requirement, AND reds if the
# requirement is asserted with no consumer.
REQUIRED_PIXEL_BROWSERS = ("chromium-headless-shell",)

# `playwright install --dry-run` prints, per browser, a header naming it and an
# install directory:
#   Chrome Headless Shell 151.0.7922.34 (playwright chromium-headless-shell v1234)
#     Install location:    /home/rich/.cache/ms-playwright/chromium_headless_shell-1234
_PIXEL_BROWSER_HEADER = re.compile(r"\(playwright (\S+) v[^)]*\)")
_PIXEL_INSTALL_LOCATION = re.compile(r"^\s*Install location:\s*(\S.*?)\s*$")


def _playwright_install_locations(dry_run_stdout: str) -> dict[str, str]:
    """Map Playwright's own browser name -> the directory it resolves that
    browser to, parsed from `playwright install --dry-run` output.

    Parsing Playwright's answer rather than re-deriving the path is deliberate:
    the cache root moves with `PLAYWRIGHT_BROWSERS_PATH` and the directory name
    is not the browser name (`chromium-headless-shell` installs to
    `chromium_headless_shell-1234` -- underscores, and a revision that changes
    on every version bump). A second implementation of that logic here would be
    wrong the first time either of them changed, and wrong in the direction
    that reports a present browser missing.
    """
    locations: dict[str, str] = {}
    current: str | None = None
    for line in dry_run_stdout.splitlines():
        header = _PIXEL_BROWSER_HEADER.search(line)
        if header:
            current = header.group(1)
            continue
        location = _PIXEL_INSTALL_LOCATION.match(line)
        # First location wins: a browser's own header always precedes its
        # location line, and later lines (download fallbacks) must not
        # overwrite it.
        if location and current and current not in locations:
            locations[current] = location.group(1)
    return locations


def _check_pixel_verification_capability() -> str | None:
    """Return warning string if real browser pixel-verification (Playwright)
    is not actually launchable right now.

    ADVISOR_STEER_BROWSER_REGRESSION.md (2026-07-11): pixel verification is
    part of the harness baseline, not an optional nicety -- if it silently
    stops working, that must be an ALARMED failure (this check), not a caveat
    buried in a digest days later. Root-cause of the specific 2026-07-11
    incident this check guards against: the capability was never actually
    broken -- `npx playwright --version` worked the whole time -- an earlier
    check that turn used the wrong invocation (`which playwright`, `pip3 show
    playwright`) and concluded "unavailable" without trying `npx`. This check
    uses the correct invocation so that class of false-negative can't recur,
    and so a REAL future breakage (binary removed, npx cache cleared, network
    egress blocking the download) surfaces here instead of being silently
    reasoned around again.

    Deliberately lightweight: no browser launch/page navigation -- this runs on
    every routine health-check cycle and must stay fast. A full live-site pixel
    check is a separate, on-demand verification step, not a routine
    health-check concern.

    ANCHORED TO THE SHARED TREE, NOT THE CALLER'S CWD (2026-09-17). `npx
    --no-install` resolves `playwright` by walking up from its cwd, and
    `node_modules/` is gitignored -- so it exists ONLY in the main worktree and
    never in a linked one. Probing from cwd therefore answered "does THIS
    CHECKOUT have node_modules", while the sentence it returns, the alarm it
    raises and this function's own name all claim a property of the MACHINE.
    Run from a worktree it reported the capability lost while the very same
    probe returned `Version 1.62.0` from the main tree one second later -- a
    full Lane 0 item was spent establishing that the machine had lost nothing.
    Anchoring to `common_git_dir().parent` (the ONE tree that holds the
    dependency, identical from every checkout) makes the answer a property of
    the machine, which is the thing being asserted.

    This cannot hide a real breakage, which is why it is a correction and not a
    narrowing: delete `node_modules/` from the main tree and every caller, in
    every checkout, goes red together. What it removes is the FALSE red, which
    is the one that was costing turns.

    THE NPM PACKAGE IS NOT THE BROWSER (2026-09-17). Until this date the probe
    ran `playwright --version`, which answers from the npm package alone -- so
    emptying `~/.cache/ms-playwright` left it reporting "available" while every
    real pixel check failed. A fail-open in a control CLAUDE.md treats as
    load-bearing ("done means the rendered value changed"), and the more
    expensive direction: the previous outage showed a WRONG READING of this
    alarm costs a whole Lane 0 item.

    It now also STATS THE BROWSER BINARY, via `playwright install --dry-run`.
    That respects the no-launch rule the paragraph above states rather than
    working around it: the dry run opens no socket, starts no browser, and cost
    0.6s measured -- the same order as the version check it replaces, so the
    every-cycle speed budget is intact. It subsumes the version check, too: the
    package must resolve before the subcommand can run at all, so a missing
    `node_modules/` still exits non-zero here exactly as before.
    """
    try:
        result = subprocess.run(
            ["npx", "--no-install", "playwright", "install", "--dry-run"],
            cwd=str(_pixel_verification_root()),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return f"Pixel-verification (Playwright) unavailable: {result.stderr.strip()[:200]}"
        locations = _playwright_install_locations(result.stdout)
        for name in REQUIRED_PIXEL_BROWSERS:
            location = locations.get(name)
            if location is None:
                # Fail closed, and name the reason. Playwright still answers,
                # but no longer about the browser we require -- so this probe
                # cannot tell present from missing, and "we cannot tell" is a
                # result that belongs on the surface rather than passing as a
                # silent green.
                return (
                    f"Pixel-verification (Playwright) unavailable: '{name}' is absent from "
                    f"`playwright install --dry-run`, so this check can no longer tell whether "
                    f"the browser it needs is installed"
                )
            if not Path(location).is_dir():
                return (
                    f"Pixel-verification (Playwright) unavailable: browser binary '{name}' is "
                    f"not installed at {location} -- run `npx playwright install {name}`"
                )
        return None
    except FileNotFoundError:
        return "Pixel-verification (Playwright) unavailable: npx not found"
    except subprocess.TimeoutExpired:
        return "Pixel-verification (Playwright) unavailable: browser-binary check timed out"
    except Exception as e:
        return f"Pixel-verification (Playwright) unavailable: {e}"


def _check_stale_dependencies() -> str | None:
    """Return a warning string if any non-idle maturity-map atom (loop_stage
    in build/frame -- i.e. genuinely due for self-refill selection) is
    permanently excluded from the dial-weighted draw by an unmet dependency
    on an atom whose own loop_stage is idle.

    Idle-hole #8 (ADVISOR_STEER_OVERNIGHT.md, 2026-07-11): D3_catchup_rebilling
    was the director's own explicitly-named hot-lane build, but sat unselected
    for ~90 minutes because its depends_on required W1_reveal_over_time at its
    FULL target level -- while W1 was correctly, deliberately parked below
    target (one specific sub-component deferred to M4 by a separate director
    decision). The dependency was real when set, then went stale when W1's
    own scope narrowed, with no mechanism to ever notice. Root-cause note (see
    D3's own maturity_map.yaml simplifications for the full audit): NOT every
    non-idle-atom-blocked-by-idle-dependency instance is stale -- this check
    SURFACES candidates for human/agent review, it does not assert they are
    all bugs. Silence is not the goal; visibility is.

    2026-07-12: this docstring previously cited E2_revenue_reconciliation as
    the canonical "deliberate, correctly-reasoned, NOT stale" counter-example
    (its own simplifications explicitly chose depends_on over loop_stage=idle
    because writing its lane charter was still legitimate FRAME work at the
    time). That charter was written the very next day and is now complete --
    the reasoning that justified loop_stage=frame no longer holds, and E2's
    own maturity_map.yaml entry was corrected to loop_stage=idle. Kept as a
    live example of exactly the point above: a flag here is a candidate for
    review, and review can conclude either "still deliberate, leave it" (as
    E2 was in 2026-07-11) or "now genuinely stale, fix it" (as E2 became by
    2026-07-12) -- the check's job is to keep surfacing the question, not to
    answer it once and stop looking.
    """
    # The `import yaml` availability probe that used to stand here is gone with the parse it
    # guarded: the map is read through `map_store`, which imports yaml at module scope, so a
    # missing yaml fails this module's own import long before this line and the probe could
    # only ever have been dead.
    map_path = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
    try:
        atoms = map_store.load_atoms(map_path)
    except (OSError, Exception):
        return None
    if not isinstance(atoms, list):
        return None
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}

    flagged = []
    for atom in atoms:
        if not isinstance(atom, dict) or "id" not in atom:
            continue
        if atom.get("loop_stage") not in ("build", "frame"):
            continue
        level_current, level_target = atom.get("level_current"), atom.get("level_target")
        if level_current is None or level_target is None or level_current >= level_target:
            continue  # no real gap, nothing to select anyway
        for dep_id in atom.get("depends_on") or []:
            dep = by_id.get(dep_id)
            if dep is None:
                flagged.append(f"{atom['id']} depends on missing atom {dep_id}")
                continue
            dep_level, dep_target = dep.get("level_current"), dep.get("level_target")
            unmet = dep_level is None or dep_target is None or dep_level < dep_target
            if unmet and dep.get("loop_stage") == "idle":
                flagged.append(
                    f"{atom['id']} (loop_stage={atom.get('loop_stage')}) blocked by "
                    f"idle dependency {dep_id} ({dep_level}/{dep_target})"
                )
    if flagged:
        return "Stale-dependency candidates (review, not all are bugs): " + "; ".join(flagged)
    return None


def _check_staging_age() -> str | None:
    """Return warning string if any from_rich_*.md is older than 2 hours unactioned."""
    staging = PROJECT_DIR / "docs" / "staging"
    if not staging.is_dir():
        return None
    now = datetime.now(timezone.utc).timestamp()
    old = []
    for f in staging.glob("from_rich_*.md"):
        age_h = (now - f.stat().st_mtime) / 3600
        if age_h > 2:
            old.append(f"{f.name} ({age_h:.1f}h old)")
    if old:
        return "Unactioned messages: " + ", ".join(old)
    return None


def _director_console_pids(pids, pane_session, ppid_of, session_name, _max_hops=32):
    """Subset of `pids` that are the director's OWN console: an interactive claude
    whose process -- or an ancestor within _max_hops -- is a live tmux pane in a
    session OTHER than the managed one (`session_name`). These are legitimate and
    unlimited (the reap logic spares pane-backed sessions identically); only the
    managed session + non-pane-backed ghosts are the duplicate/ghost this alarm
    exists for. The walk is up the ANCESTOR chain, not pane_pid==pid, because a
    console pane can shell-wrap claude -- the pane_pid may be claude's PARENT
    (observed 2026-07-17: the `work` pane_pid was claude's ppid, not claude itself)."""
    console = set()
    for pid in pids:
        cur = pid
        for _ in range(_max_hops):
            if cur is None or cur <= 1:
                break
            sess = pane_session.get(cur)
            if sess is not None and sess != session_name:
                console.add(pid)
                break
            cur = ppid_of(cur)
    return console


def _check_single_interactive_session(_pids=None, _pane_session=None) -> str | None:
    """Return a problem string if MORE THAN ONE non-console interactive Claude
    session is running (2026-07-16, director: a Jul-15 ghost session survived a
    full day, spamming NTFY every gate cycle -- the next ghost must page within a
    health cycle, not a day). Exactly one MANAGED session is healthy; zero is fine
    (watchdog resumes); >1 is the ghost/duplicate alarm.

    Console-exclusion (2026-07-17): a session the director opened himself in his
    OWN tmux session is NOT a duplicate -- excluded exactly as the reap logic
    spares pane-backed sessions. Without this, a director console open ALONGSIDE
    the managed session false-paged 'MULTIPLE sessions' every restart (a console
    is a `claude --dangerously-skip-permissions` process too). The `_pids` /
    `_pane_session` params are injection points for mutation-testing (R15);
    production passes neither and reads live state.

    Fail-safe: if tmux is unreachable (no pane map), fall back to the raw >1
    alarm -- never go silent on a possible real duplicate."""
    try:
        from background.interactive_session_probe import (
            SESSION_NAME,
            _ppid_of,
            interactive_claude_pids,
        )
        pids = interactive_claude_pids() if _pids is None else list(_pids)
        if len(pids) <= 1:
            return None
        if _pane_session is None:
            res = subprocess.run(
                ["tmux", "list-panes", "-a", "-F", "#{pane_pid} #{session_name}"],
                capture_output=True, text=True,
            )
            if getattr(res, "returncode", 1) != 0:
                # tmux unreachable -> cannot classify the console; fall back to the
                # original raw alarm rather than risk silencing a real duplicate.
                return (f"MULTIPLE interactive Claude sessions ({len(pids)}: {pids}) -- a "
                        "duplicate/ghost session. Each runs the test suite and burns tokens. "
                        "REPORT-ONLY (OPS1 sub-step 4): the auto-reaper is DELETED (the exit-143 "
                        "console-kill vector) -- clear the extra session manually / via systemd, "
                        "never an automated kill.")
            pane_session = {}
            for line in res.stdout.split("\n"):
                parts = line.split()
                if len(parts) == 2:
                    try:
                        pane_session[int(parts[0])] = parts[1]
                    except ValueError:
                        pass
        else:
            pane_session = _pane_session
        console = _director_console_pids(pids, pane_session, _ppid_of, SESSION_NAME)
        countable = [p for p in pids if p not in console]
        if len(countable) > 1:
            return (f"MULTIPLE interactive Claude sessions ({len(countable)}: {countable}) -- a "
                    "duplicate/ghost session (director's own console panes excluded). Each runs "
                    "the test suite and burns tokens. REPORT-ONLY (OPS1 sub-step 4): the "
                    "auto-reaper is DELETED (exit-143 vector) -- clear the extra session "
                    "manually / via systemd, never an automated kill.")
    except Exception:
        return None  # never break the health run on this check
    return None


def drift_headline(drift: dict) -> str:
    """The one phrase a reader meets the deployment-drift numbers in. PURE, so the phrase has a
    door of its own rather than living inside a 200-line health run nothing can call.

    THE DENOMINATOR COMES FIRST AND IT IS NOT DECORATION. `stale` is counted only over the
    sessions the rules could actually grade; measured 2026-09-25 that was 1 of 11, so an empty
    `stale` list read exactly like a clean fleet, and `deploy_restart --report` printed `stale 0`
    at a fleet whose running code version was unknown for ten of its eleven members.

    An ABSENT `graded` key renders `?`, never 0 and never the population: a caller passing an older
    report must read as "this instrument could not say", which is the opposite of "none".
    """
    graded = drift.get("graded")
    return "{} stale of {} graded, {} observed".format(
        len(drift.get("stale") or []),
        "?" if graded is None else len(graded),
        len(drift.get("population") or []))


def run_health_check() -> tuple[bool, list[str], list[str]]:
    """
    Returns (all_ok, ok_lines, problem_lines).
    """
    panes = _tmux_panes()
    ps_lines = _running_scripts()

    ok_lines = []
    problem_lines = []

    for session, script in EXPECTED_PANES.items():
        if session in panes:
            ok_lines.append(f"  ✓ {session} (tmux pane present, cmd={panes[session]})")
        elif any(script in line for line in ps_lines):
            ok_lines.append(f"  ✓ {session} (process running, no tmux pane)")
        else:
            problem_lines.append(f"  ✗ {session} — NOT RUNNING ({script})")

    staging_warn = _check_staging_age()
    if staging_warn:
        problem_lines.append(f"  ✗ {staging_warn}")
    else:
        ok_lines.append("  ✓ staging — no stale messages")

    pixel_warn = _check_pixel_verification_capability()
    if pixel_warn:
        problem_lines.append(f"  ✗ {pixel_warn}")
    else:
        ok_lines.append("  ✓ pixel-verification (Playwright) available")

    stale_code_warn = _check_stale_running_code()
    if stale_code_warn:
        problem_lines.append(f"  ✗ {stale_code_warn}")
    else:
        ok_lines.append("  ✓ no daemon running code older than its own committed changes")

    session_warn = _check_single_interactive_session()
    if session_warn:
        problem_lines.append(f"  ✗ {session_warn}")
    else:
        ok_lines.append("  ✓ exactly one interactive Claude session")

    # Informational, not a hard failure (idle-hole #8): a flagged candidate
    # can be a genuine, expected, long-lived block (E2/W5_1-style, reviewed
    # and found correct) rather than a bug -- treating every occurrence as
    # DEGRADED would erode the signal (the same "cries wolf" risk this
    # project already avoids for the epistemic verifier). Always surfaced in
    # ok_lines (not gated behind --always) so it's visible on every routine
    # run without triggering a false-alarm NTFY.
    stale_dep_warn = _check_stale_dependencies()
    if stale_dep_warn:
        ok_lines.append(f"  ℹ {stale_dep_warn}")
    else:
        ok_lines.append("  ✓ no stale-dependency candidates in the maturity map")

    # Pull-loop transport health (OPS1_transport_failure_must_be_loud, §9): the on-demand view
    # of the same typed signal the deadman alarms on periodically. LOOP_BROKEN is a real problem;
    # DISABLED / HEALTHY_IDLE / HEALTHY_DREW are informational (a paused or quiescent loop is not
    # a fault -- that IS the 'idle because no grant reads differently from idle because broken').
    try:
        from background.process_reconciler import evaluate_pull_loop
        _pl = evaluate_pull_loop()
        if _pl["alarm"]:
            problem_lines.append(f"  ✗ pull-loop transport {_pl['status']}: {_pl['detail']}")
        else:
            ok_lines.append(f"  ✓ pull-loop transport {_pl['status']} — {_pl['detail']}")
    except Exception as exc:  # noqa: BLE001 -- a sub-check must never break the health run
        ok_lines.append(f"  ℹ pull-loop transport check unavailable: {exc}")

    # Booted-SHA deployment drift (OPS1 sub-step 5, G-D3): a systemd daemon running code OLDER
    # than HEAD is stale — a restart deploys HEAD (G-D2, a separate step). This generalises the
    # own-script-mtime stale check to catch imported-module drift. Fail-safe: no stamp yet / git
    # unavailable -> nothing flagged (the deadman commit-clock is the backstop).
    try:
        from background.process_reconciler import evaluate_boot_sha_drift
        _bd = evaluate_boot_sha_drift()
        _over = drift_headline(_bd)
        _faults = []
        if _bd.get("stale"):
            _faults.append("daemon(s) running an OLD copy of a module they import (restart to "
                           "deploy): " + ", ".join(_bd["stale"]))
        if _bd.get("vacuous"):
            _faults.append("VACUOUS — the drift population is EMPTY while systemd units are "
                           "active; the check cannot fail, so it has failed")
        if _bd.get("unresolved"):
            _faults.append("unresolvable (an unanswered check is a FAILED check): "
                           + ", ".join(f"{s}={r}" for s, r in sorted(_bd["unresolved"].items())))
        if _bd.get("misdeclared"):
            _faults.append("manifest launched_by disagrees with the observed launcher: "
                           + ", ".join(m["session"] for m in _bd["misdeclared"]))
        # IS THE INSTRUMENT ALIVE? Every fault above is derived FROM the boot stamps, so a dead
        # stamper makes all of them vacuous rather than clean -- and that is not hypothetical: from
        # 2026-09-04 the units' declared ExecStartPre was a no-op that exited 0, and this check
        # read the resulting three-week-old stamps as valid for twenty days. `"stamper" in` and not
        # `.get("stamper")`: a caller that passes an older report must not be read as a PASS.
        if "stamper" in _bd and not (_bd.get("stamper") or {}).get("ok"):
            _st = _bd.get("stamper") or {}
            _faults.append(
                "THE BOOT STAMPER THE UNITS DECLARE DOES NOT STAMP "
                f"({_st.get('verdict', 'unknown')}) -- every staleness verdict above is derived "
                f"from stamps nothing is writing: {_st.get('detail', 'no detail')}")
        if _faults:
            problem_lines.append(f"  ✗ deployment drift ({_over}): " + "; ".join(_faults))
        else:
            ok_lines.append(
                f"  ✓ no deployment drift — {_over}; none of the GRADED daemons runs a changed "
                "imported module, and nothing is claimed about the rest; the declared boot "
                f"stamper stamps ({(_bd.get('stamper') or {}).get('detail', 'not probed')})")
    except Exception as exc:  # noqa: BLE001 -- a sub-check must never break the health run
        ok_lines.append(f"  ℹ boot-SHA drift check unavailable: {exc}")

    # A1_learn_loop_chair L3: the retrospective-cadence nudge fires automatically in the
    # live pipeline (the watchdog runs run_health_check every cycle). Informational, not a
    # hard failure -- a stale retro is a prompt to reflect, not a broken system. Defensive:
    # a nudge-check error must never break the daemon's own health run.
    try:
        from background import retro_cadence_check
        retro_warn = retro_cadence_check.check_retro_staleness()
        if retro_warn:
            ok_lines.append(f"  ℹ {retro_warn}")
        else:
            ok_lines.append("  ✓ retrospective cadence current")
    except Exception as exc:  # noqa: BLE001 -- nudge check must never break the health run
        ok_lines.append(f"  ℹ retro-cadence check unavailable: {exc}")

    all_ok = len(problem_lines) == 0
    return all_ok, ok_lines, problem_lines


def _log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"\n- [{ts}] {msg}")


def main() -> int:
    always_ntfy = "--always" in sys.argv
    quiet = "--quiet" in sys.argv

    all_ok, ok_lines, problem_lines = run_health_check()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    status = "OK" if all_ok else "DEGRADED"

    lines = [f"[{ts}] Stack health: {status}"]
    if problem_lines:
        lines += problem_lines
    lines += ok_lines

    report = "\n".join(lines)

    if not quiet:
        print(report)

    _log(f"health={status} problems={len(problem_lines)} ok={len(ok_lines)}")

    if not all_ok:
        notify(
            f"[HEALTH CHECK] Stack DEGRADED — {len(problem_lines)} problem(s):\n"
            + "\n".join(problem_lines),
            kind="real_alarm",
            headers={"X-Priority": "4", "X-Tags": "warning"},
        )
    elif always_ntfy:
        # G-N3: "everything is fine" is the definition of a message he does not need to act
        # on, so it batches. The DEGRADED branch above stays instant and unclassified.
        from background import notification_digest
        notify(f"[HEALTH CHECK] Stack OK — {len(ok_lines)} processes healthy.",
               kind="director_echo", topic_class=notification_digest.ROUTINE_LANDING)

    return 0 if all_ok else 1


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/health_check.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("health_check")
    sys.exit(main())
