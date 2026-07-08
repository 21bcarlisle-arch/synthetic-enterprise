# MAINTENANCE.md — Synthetic Enterprise

Operational maintenance tasks that are deliberately NOT automated (safety,
low frequency, or need a human eye) — as opposed to the autonomous stack in
`background/`, which handles everything else.

---

## Claude Code CLI version

**Auto-update is disabled** for every unattended launch (the watchdog and
autonomous-runner both set `DISABLE_AUTOUPDATER=1` on the spawned session —
see `background/session_watchdog.py::restart_claude()`). This is deliberate,
not an oversight: the npm global install directory on this box isn't
writable, so the background auto-update check fails on every restart for no
benefit — just noise. Manual update below is the sanctioned path instead.

**Cadence:** monthly, or sooner if a specific feature/fix is needed.

**Steps:**
1. Check current version: `~/.nvm/versions/node/*/bin/claude --version`
2. Update: `npm install -g @anthropic-ai/claude-code@latest`
   (run as the `rich` user — this is the same npm global install
   `resolve_claude_binary()` in `session_watchdog.py` globs for; a version
   bump doesn't change the binary's path, just its target, so the watchdog
   picks it up automatically on its next restart with no code change needed)
3. Verify: re-run `--version`, confirm it moved.
4. **Deliberate session cycle to pick it up:** the currently-running
   interactive session (and the watchdog-managed one, if separate) keep
   running the *old* binary in memory until restarted — per CLAUDE.md's R2
   ("committed != running"), the update isn't live until a fresh `claude`
   process actually launches. Either:
   - let the next natural restart (crash, usage-limit reset, manual `exit`)
     pick it up, or
   - deliberately kill and let the watchdog relaunch it if you want the new
     version live immediately.
5. Note the version bump in the next session's status update if it's
   relevant to anything you're debugging (new/changed CLI behaviour).

**Do not** run `claude install` (switches to the native installer) or change
the install method without checking first — several launchers
(`session_watchdog.py`, `autonomous_runner.py`) resolve the binary via a
fixed nvm-tree glob path (`CLAUDE_NVM_GLOB` / `resolve_claude_binary()`);
switching install methods could silently break that resolution.

---

## Retiring a background daemon — edit the launcher, not just the process

**Standing rule (2026-07-08, learned the hard way):** "retiring" a background
daemon means **commenting/removing its block in `background/start_worker.sh`
first, then killing the running process** — never a console kill alone.

`start_worker.sh` is idempotent and re-run on any stack restart; a killed
session it still lists gets silently resurrected on the next start. On
2026-07-07 the autonomous-runner was console-killed as "retired", but a stack
re-run brought a fresh instance back ~10s later (new pid, same cmd) — the
directive read as done in code while the process kept spawning `claude -p`
turns and burning budget for another day. That is worse than either clean
state (hidden + still running). See
`docs/review_gates/AUTONOMOUS_RUNNER_STILL_RUNNING.md`.

**Checklist to retire a daemon `X`:**
1. Comment out / remove the `_start_session "X" ...` block in
   `background/start_worker.sh` (leave a dated RETIRED banner explaining why).
2. Identify every live process the daemon owns (`pstree -p <pid>`), including
   any `claude -p` turns it spawned. Never blind-kill: if the retiring session
   is itself a descendant, killing the parent aborts its own work.
3. Kill the daemon (or have the human console-kill it if a session-launcher /
   safety-adjacent). Verify with `ps`/`pstree` that nothing remains parented
   to it.
4. Only then update `docs/observability/agent_status.json` to "retired" — and
   confirm the daemon doesn't self-write a "working" heartbeat that would
   overwrite it. Suppress its health-check alerting (`health_check.py`
   `EXPECTED_PANES`) so the retirement doesn't fire a false down-alert.
