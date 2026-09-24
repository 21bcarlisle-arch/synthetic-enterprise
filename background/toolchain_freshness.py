"""Is the Claude Code this machine runs still close to the published one?

WHY THIS EXISTS, and it is not the reason it looks like. On 2026-07-09 the director flagged the
CLI's auto-updater failing with *"no write permission to npm prefix"*. The cause was diagnosed
correctly and is still written down at `background/start_worker.sh:38-43`: this machine's SYSTEM npm
(`/usr/bin/npm`) has prefix `/usr`, which is root-owned, while `claude` runs from a user-owned NVM
install. The response was `DISABLE_AUTOUPDATER=1` on every launch path, on the stated reasoning that
the mismatch *"is inside the closed-source CLI binary, not something this repo can patch directly"*.

**The cause was right and the conclusion was wrong.** Nothing needed patching in the CLI. Running
`npm install -g @anthropic-ai/claude-code` with NVM's OWN npm -- whose prefix is the user-owned NVM
directory -- updates the very install that is running, needs no sudo, and leaves no root-owned file
in a user prefix. It took 33 seconds on 2026-09-25.

SO THE DEFECT WAS NOT A MISSED WARNING. The warning was the residue of a mechanism deliberately
switched off, and the note recording the switch-off asserted the problem was unfixable here, so
nobody re-asked for 78 days. Meanwhile `DISABLE_AUTOUPDATER=1` was set on `autonomous_runner`,
`start_worker.sh`, `seat_executor`, `worker_tick` and `delivery_seat` -- every automated path -- and
in NO shell rc. **The one surface still printing the failure was the director's own console**, which
is the only place a human would read it and therefore the only place it could be mistaken for
cosmetic noise. The suppression covered every reader except the one who could act.

WHAT IT COST: the install froze at 2.1.226 (July) while the published version reached 2.1.282, and
2.1.226 predates Claude Opus 5.5 -- so `/model opus-5-5` answered "not found" and a 20%-cheaper
model with 60%-cheaper cache reads could not be selected at all. A frozen toolchain is not a
cosmetic problem; it silently removes capability.

THREE THINGS THIS CONTROL DOES DIFFERENTLY FROM THE WARNING IT REPLACES:

1. **It is keyed to the PROPERTY, not to the message.** The subject is "how far behind the published
   version are we", which stays meaningful when the CLI's error text changes, when the updater is
   re-enabled, or when the install moves prefix. A control pinned to *"no write permission to npm
   prefix"* would go quiet the moment that string changed while the freeze continued.
2. **It FAILS CLOSED on input it could not read.** "I could not reach the registry" and "we are
   current" are different answers and must never share a return code: an unreadable check that
   reports health is the shape that let this sit for 78 days. `cannot_tell` is its own state.
3. **It carries the fix.** The remedy was rediscovered from scratch on 2026-09-25 because nowhere
   recorded it. `fix_command()` is that command, derived from the running install rather than
   hardcoded, so it stays right when the node version changes.

NOT A HEARTBEAT. `should_notify` fires only when the (installed, latest) pair CHANGES, so a machine
left behind for a week says so once, not seven times. Nothing here decides the update: updating is
reversible and therefore mine to do (THE_STANDARD §2 reserves four things and this is none of them).
The part that is genuinely the director's is the RESTART -- a running process holds the binary it
started with -- which is why the message says so rather than claiming the upgrade already applies.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

PACKAGE = "@anthropic-ai/claude-code"

#: How far behind is worth telling anyone about. ONE published release is noise -- releases land
#: most days and a machine an hour behind is not a finding. This is deliberately a count of
#: releases rather than days: the quantity that cost us capability was "the install predates the
#: model", and versions are what carry that, not wall-clock.
BEHIND_PATCH_THRESHOLD = 3

STATE_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "observability" / "toolchain_freshness.json"
)


class CannotTell(RuntimeError):
    """The check could not read one of its two inputs.

    Its own class rather than a None return, so a caller cannot accidentally treat "unknown" as
    "current" -- which is precisely the confusion that made the original warning ignorable.
    """


def _login_path_claude() -> str | None:
    """Where `claude` resolves on an interactive login PATH.

    Resolved rather than hardcoded: the running install is under NVM today and the node version in
    that path changes with every node upgrade, so a literal path here would become a control that
    silently describes a directory nobody uses.
    """
    exec_path = os.environ.get("CLAUDE_CODE_EXECPATH")
    if exec_path and Path(exec_path).exists():
        return exec_path
    found = shutil.which("claude")
    if found:
        return found
    try:
        out = subprocess.run(
            ["bash", "-lic", "command -v claude"],
            capture_output=True, text=True, timeout=30,
        ).stdout.strip().splitlines()
        return out[-1] if out else None
    except Exception:
        return None


def install_root() -> Path:
    """The package directory of the install that actually runs, via its own binary path."""
    binary = _login_path_claude()
    if not binary:
        raise CannotTell(
            "no `claude` on CLAUDE_CODE_EXECPATH, this PATH, or a login PATH, so there is no "
            "install to describe. This is NOT 'up to date'."
        )
        # (unreachable guard kept explicit: the raise above is the whole point)
    path = Path(binary).resolve()
    for parent in path.parents:
        if (parent / "package.json").exists() and parent.name == "claude-code":
            return parent
    raise CannotTell(
        f"resolved `claude` to {path} but found no claude-code package.json above it, so the "
        "installed version cannot be read"
    )


def installed_version() -> str:
    root = install_root()
    try:
        return str(json.loads((root / "package.json").read_text())["version"])
    except Exception as exc:
        raise CannotTell(f"{root / 'package.json'} is unreadable or carries no version: {exc}")


def _npm_for_install() -> str:
    """The npm whose prefix OWNS the running install -- the whole point of this module.

    Sitting beside the node that runs `claude`, so its prefix is that node's user-owned directory.
    The system npm at /usr/bin/npm has prefix /usr and is root-owned; calling it is the original
    defect, and nothing here may fall back to it.
    """
    root = install_root()
    for parent in root.parents:
        candidate = parent / "bin" / "npm"
        if candidate.exists():
            return str(candidate)
    raise CannotTell(
        f"found no `npm` in any bin/ above {root}, so there is no user-prefix npm to update with. "
        "Refusing to name the system npm: its prefix is root-owned and using it is the defect "
        "this module exists to describe."
    )


def latest_version(*, timeout: float = 120.0, _run=None) -> str:
    run = _run or subprocess.run
    try:
        npm = _npm_for_install()
    except CannotTell:
        npm = "npm"
    env = dict(os.environ)
    try:
        env["PATH"] = f"{node_bin_dir()}:{env.get('PATH', '')}"
    except CannotTell:
        pass
    try:
        proc = run([npm, "view", PACKAGE, "version"],
                   capture_output=True, text=True, timeout=timeout, env=env)
    except Exception as exc:
        raise CannotTell(f"`{npm} view {PACKAGE} version` did not complete: {exc}")
    out = (getattr(proc, "stdout", "") or "").strip().splitlines()
    if getattr(proc, "returncode", 1) != 0 or not out:
        raise CannotTell(
            f"`{npm} view {PACKAGE} version` returned rc="
            f"{getattr(proc, 'returncode', '?')} and no version. The registry may be unreachable; "
            "that is NOT evidence this install is current."
        )
    return out[-1].strip()


def node_bin_dir() -> str:
    """The `bin/` holding the node that runs `claude`. Load-bearing -- see `fix_command`."""
    return str(Path(_npm_for_install()).parent)


def fix_command() -> str:
    """The command that actually works here, derived from the running install.

    Recorded because its absence is what cost 78 days: the remedy was rediscovered from scratch
    rather than read. No sudo -- a root-owned file in a user prefix only moves the failure to the
    next update.

    **THE `PATH=` PREFIX IS NOT COSMETIC AND MUST NOT BE TRIMMED.** npm is a shim that resolves
    `node` from PATH, so calling NVM's npm by absolute path from a shell where NVM is not loaded
    runs it under the SYSTEM node -- and it then reports prefix `/usr`, root-owned, and fails with
    the very "no write permission to npm prefix" this module exists to describe. The first draft of
    this function omitted the prefix and its own control caught it: the absolute path alone is the
    original defect wearing the remedy's clothes.
    """
    try:
        npm = _npm_for_install()
        return f'PATH="{node_bin_dir()}:$PATH" {npm} install -g {PACKAGE}'
    except CannotTell:
        return f"npm install -g {PACKAGE}   # with an npm whose prefix you own -- never sudo"


def effective_prefix(*, timeout: float = 120.0) -> str | None:
    """What npm's prefix ACTUALLY is when invoked the way `fix_command` invokes it.

    The only honest way to answer "will the fix work": asked of the resolved npm under the resolved
    node, not of whichever npm happens to be on the caller's PATH.
    """
    try:
        npm = _npm_for_install()
        env = dict(os.environ)
        env["PATH"] = f"{node_bin_dir()}:{env.get('PATH', '')}"
        proc = subprocess.run([npm, "config", "get", "prefix"],
                              capture_output=True, text=True, timeout=timeout, env=env)
        out = (proc.stdout or "").strip().splitlines()
        return out[-1].strip() if out and proc.returncode == 0 else None
    except Exception:
        return None


def _as_tuple(version: str) -> tuple[int, ...]:
    parts = []
    for chunk in str(version).split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def snapshot(*, _run=None) -> dict:
    """What we can say, including when the answer is that we cannot say.

    `cannot_tell` is a first-class outcome and never collapses into `behind=False`.
    """
    out: dict = {"package": PACKAGE, "cannot_tell": None, "installed": None, "latest": None,
                 "behind": None, "releases_behind": None, "fix": None}
    try:
        out["installed"] = installed_version()
        out["fix"] = fix_command()
    except CannotTell as exc:
        out["cannot_tell"] = str(exc)
        return out
    try:
        out["latest"] = latest_version(_run=_run)
    except CannotTell as exc:
        out["cannot_tell"] = str(exc)
        return out
    inst, late = _as_tuple(out["installed"]), _as_tuple(out["latest"])
    out["behind"] = inst < late
    if len(inst) == len(late) and inst[:-1] == late[:-1]:
        out["releases_behind"] = max(0, late[-1] - inst[-1])
    return out


#: How long a measurement stands before the registry is asked again. The tick runs every ~30
#: minutes and the published version changes at most daily, so measuring per tick would be 48
#: network calls a day to answer a question that moves once. The CACHE is what makes this safe to
#: call from a hot path; the NOTIFICATION rate-limit (`should_notify`) is a separate concern.
SNAPSHOT_MAX_AGE_SECONDS = 6 * 3600


def cached_snapshot(*, max_age: float = SNAPSHOT_MAX_AGE_SECONDS, now: float | None = None,
                    _run=None) -> dict:
    """`snapshot()` behind a disk cache, for callers on a frequent cadence.

    A cache MISS re-measures. A cache read that cannot be parsed re-measures rather than assuming
    health -- the one thing this module may never do is let an unreadable input look like "current".
    """
    import time
    now = time.time() if now is None else now
    try:
        cached = json.loads(STATE_PATH.read_text())
        measured_at = float(cached.get("measured_at") or 0)
        snap = cached.get("snapshot")
        if snap and (now - measured_at) < max_age:
            return dict(snap)
    except Exception:
        pass
    snap = snapshot(_run=_run)
    try:
        from background.live_ledger_guard import guard_live_ledger_write
        path = guard_live_ledger_write(STATE_PATH, writer="toolchain_freshness.cached_snapshot")
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        try:
            existing = json.loads(path.read_text())
        except Exception:
            existing = {}
        existing.update({"measured_at": now, "snapshot": snap})
        path.write_text(json.dumps(existing, indent=1) + "\n")
    except Exception:
        pass
    return snap


def is_stale(snap: dict | None = None) -> bool:
    """Behind by enough to be worth saying. `cannot_tell` is NOT stale -- it is unknown, and the
    caller must handle it separately or it will read an outage as health."""
    snap = snap if snap is not None else snapshot()
    if snap.get("cannot_tell") or not snap.get("behind"):
        return False
    behind = snap.get("releases_behind")
    return True if behind is None else behind >= BEHIND_PATCH_THRESHOLD


def describe(snap: dict | None = None) -> str:
    snap = snap if snap is not None else snapshot()
    if snap.get("cannot_tell"):
        return f"Claude Code freshness UNKNOWN: {snap['cannot_tell']}"
    if not snap.get("behind"):
        return f"Claude Code {snap['installed']} is current ({snap['latest']} published)."
    behind = snap.get("releases_behind")
    gap = f"{behind} releases behind" if behind is not None else "behind"
    return (
        f"Claude Code {snap['installed']} is {gap} ({snap['latest']} published). The auto-updater "
        f"is DISABLED on every automated path (background/start_worker.sh:38), so this does not "
        f"self-heal. Fix: {snap['fix']} — then the console session must be RESTARTED, because a "
        f"running process holds the binary it started with. A frozen install silently removes "
        f"capability: 2.1.226 predated Claude Opus 5.5 and `/model` could not offer it."
    )


def _read_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def should_notify(snap: dict | None = None) -> bool:
    """Once per (installed, latest) pair, never once per tick.

    A daily nag about a fact that has not changed is how a real signal becomes wallpaper -- which
    is the failure mode this whole module is a response to.
    """
    snap = snap if snap is not None else snapshot()
    if not (is_stale(snap) or snap.get("cannot_tell")):
        return False
    key = f"{snap.get('installed')}->{snap.get('latest')}|{bool(snap.get('cannot_tell'))}"
    return _read_state().get("last_reported") != key


def record_reported(snap: dict) -> None:
    """MERGES, never overwrites: this file also holds `cached_snapshot`'s measurement clock, and a
    wholesale rewrite here would drop it and re-measure on the very next tick."""
    from background.live_ledger_guard import guard_live_ledger_write
    path = guard_live_ledger_write(STATE_PATH, writer="toolchain_freshness.record_reported")
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict = {}
    try:
        existing = json.loads(path.read_text())
    except Exception:
        existing = {}
    existing.update({
        "last_reported": f"{snap.get('installed')}->{snap.get('latest')}"
                         f"|{bool(snap.get('cannot_tell'))}",
        "installed": snap.get("installed"), "latest": snap.get("latest"),
        "cannot_tell": snap.get("cannot_tell"),
    })
    path.write_text(json.dumps(existing, indent=1) + "\n")


def raise_if_stale(*, _defer=None, _run=None, _snap=None) -> str | None:
    """Put the finding on the channel that reaches the director, once. Returns the message sent."""
    snap = _snap if _snap is not None else cached_snapshot(_run=_run)
    if not should_notify(snap):
        return None
    message = describe(snap)
    defer = _defer
    if defer is None:
        from background.notification_digest import defer as defer  # noqa: PLC0414
    defer(message, kind="toolchain_freshness", topic_class="harness")
    record_reported(snap)
    return message


def main(argv: list[str] | None = None) -> int:
    """rc 0 current, rc 1 behind, rc 2 CANNOT TELL.

    Three codes rather than two, because the two-code version is the bug: a check that cannot reach
    the registry must not exit 0 beside a check that confirmed we are current.
    """
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit non-zero when behind or unknown")
    ap.add_argument("--notify", action="store_true", help="defer a digest line if newly stale")
    args = ap.parse_args(argv)

    snap = snapshot()
    print(describe(snap))
    if args.notify:
        sent = raise_if_stale()
        print("(deferred to the digest)" if sent else "(nothing new to report)")
    if not args.check:
        return 0
    if snap.get("cannot_tell"):
        return 2
    return 1 if is_stale(snap) else 0


if __name__ == "__main__":  # pragma: no cover
    try:
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/toolchain_freshness.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("toolchain_freshness")
    raise SystemExit(main())
