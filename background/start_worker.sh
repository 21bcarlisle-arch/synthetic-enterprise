#!/bin/bash
# Start all autonomous background processes in detached tmux sessions.
# Usage: bash background/start_worker.sh
# Safe to re-run — skips sessions that are already running.
cd ~/synthetic-enterprise
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_NUM_CTX=8192

# ── AUTO-RESTART STARTS THE FIXED STACK ONLY (2026-07-16, Item 5) ───────────────
# Tonight a cron re-ran this script every 30 min and kept RESURRECTING a broken
# stack all night. Two guards so an auto-restart (cron, or anything else) can never
# bring up a stack that is disabled or that does not even load:
#
# 1. DURABLE DISABLE FLAG. If docs/observability/.stack_disabled exists, refuse to
#    start and exit cleanly. This makes a deliberate DOWN state survive a cron tick
#    (a console kill alone did NOT -- the whole incident). The director/agent drops
#    the file to keep the stack down; removing it re-enables startup. Cron stays OFF
#    regardless (this is belt-and-braces for the day it is ever re-added).
STACK_DISABLED_FLAG="docs/observability/.stack_disabled"
if [ -f "$STACK_DISABLED_FLAG" ]; then
  echo "REFUSING TO START: $STACK_DISABLED_FLAG present -- the stack is deliberately"
  echo "disabled. Reason: $(head -c 300 "$STACK_DISABLED_FLAG" 2>/dev/null)"
  echo "Remove the flag to re-enable: rm $STACK_DISABLED_FLAG"
  exit 0
fi

# DISABLE_AUTOUPDATER=1 permanent, every launch path (2026-07-09, director
# flagged the auto-updater failing on npm permissions -- root cause: this
# machine's system npm prefix (/usr) is root-owned while `claude` itself
# runs via a user-writable NVM install, so the auto-updater's own npm call
# resolves to a permission-denied location; that mismatch is inside the
# closed-source CLI binary, not something this repo can patch directly).
# `tmux set-environment -g` (not a plain shell `export`) is required here --
# same lesson as the 2026-07-08 NTFY topic rotation: a `tmux new-session`
# against an already-running server does NOT inherit the calling shell's
# freshly-exported env, only the server's own global environment, fixed at
# whatever it was last set to. This makes DISABLE_AUTOUPDATER=1 the default
# for EVERY session the server creates from here on -- including a manual
# `tmux new-session` + `claude` Rich types himself, not just the daemons
# this script explicitly launches with `-e` flags (session_watchdog.py's
# restart_claude() already does that per-session; this is the belt to that
# brace, and the only fix that reaches a manually-created session too).
tmux set-environment -g DISABLE_AUTOUPDATER 1 2>/dev/null || true

# Load SE_NTFY_TOPIC / SE_WAKE_HMAC_KEY from the gitignored env file before
# starting ANY session that touches NTFY or the tmux wake relay (session-
# watchdog, staging-watcher, ntfy-responder, dispatcher, discovery-daemon,
# sim-runner all import background.ntfy_utils, which raises loudly at import
# time if this isn't set — 2026-07-08 topic rotation,
# docs/staging/NTFY_CHANNEL_HARDENING.md). background-worker is in this set
# too, INDIRECTLY: it does not import ntfy_utils itself, but it spawns
# process_run_complete.py as a subprocess (background_worker.py's
# process_leftover_run_markers()) which does, inheriting whatever env this
# tmux session was started with. Found live 2026-07-12: this session's own
# _start_session call was missing the "${NTFY_ENV_FLAGS[@]}" trailing
# argument every sibling session below correctly passes, causing
# process_run_complete.py to crash (RuntimeError at import) on every
# leftover-marker pass once a real headline change reached maybe_ntfy() —
# silently eating the run's own notification and leaving the marker to
# retry next cycle indefinitely (matches the repeated "Failed to process
# run_complete_*.md (rc=1)" entries in background-worker-log.md).
# 2026-07-11, Option 2 floor (director in-console authorization): secrets
# moved out of the working tree to ~/.config/synthetic-enterprise/ (see
# background/secrets_location.py) -- check there FIRST, fall back to the
# old in-tree path during the transition so this script keeps working
# either way, not a hard cutover that could break a restart mid-migration.
NTFY_ENV_PATH="$HOME/.config/synthetic-enterprise/.env.ntfy"
[ -f "$NTFY_ENV_PATH" ] || NTFY_ENV_PATH="background/.env.ntfy"
NTFY_ENV_FLAGS=()
if [ -f "$NTFY_ENV_PATH" ]; then
  while IFS= read -r line; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    export "$line"
    NTFY_ENV_FLAGS+=(-e "$line")
  done < "$NTFY_ENV_PATH"
else
  echo "WARNING: no .env.ntfy found (checked ~/.config/synthetic-enterprise/ and background/) -- NTFY-touching sessions will fail to start." >&2
fi

# _start_session takes any number of trailing `-e VAR=value` flag pairs
# (pass NTFY_ENV_FLAGS's expansion, or nothing) after name/cmd/desc.
#
# Deliberate `-e` use, not a plain shell `export` before the tmux call: a
# `tmux new-session` against an ALREADY-RUNNING server (the normal case here
# -- this script is "safe to re-run", and the server has usually been up for
# days) does NOT inherit the calling shell's current environment. It only
# inherits the tmux SERVER's own stored global-environment, fixed at the
# point the server itself first started, unless overridden per-session via
# `-e`. A plain `export` here silently has no effect on a warm server --
# discovered live 2026-07-08 when all 5 NTFY-touching sessions crashed
# instantly on the topic-rotation restart (RuntimeError at import, no
# visible error since the tmux pane -- and with it the session -- closes the
# moment the sole process in it exits). Confirmed directly:
#   export TESTVAR=x; tmux new-session -d -s t "env | grep TESTVAR > out"
# against a warm server produces an empty `out`. `-e` bypasses this because
# it's part of the new-session request itself, not ambient shell state.
_start_session() {
  local name="$1"
  local cmd="$2"
  local desc="$3"
  shift 3
  local extra_flags=("$@")
  if tmux has-session -t "$name" 2>/dev/null; then
    echo "  [already running] $name"
  else
    tmux new-session -d -s "$name" -c ~/synthetic-enterprise "${extra_flags[@]}" "$cmd"
    echo "  [started] $name — $desc"
  fi
}

# 2. IMPORT SMOKE TEST (Item 5). Do NOT start a stack whose core code does not even
#    load -- a broken import (a syntax error from half-landed work, a missing
#    SE_NTFY_TOPIC) makes the NTFY daemons crash-loop on startup, exactly the "broken
#    stack" cron kept resurrecting. The env is already loaded above, so ntfy_utils's
#    import-time topic check passes on a healthy tree. If any core daemon fails to
#    import, ABORT with the error and a non-zero exit -- refuse to bring up a stack
#    that cannot run, rather than spawn a dozen instantly-dying sessions.
SMOKE_ERR="$(python3 -c 'import background.ntfy_utils, background.health_check, background.worker_seat, background.boot_announce, background.process_reconciler, background.schedule_reconciler, background.ntfy_responder, background.supervisor, background.process_run_complete' 2>&1)"
if [ $? -ne 0 ]; then
  echo "REFUSING TO START: core daemon import smoke test FAILED -- the stack would only" >&2
  echo "crash-loop. Fix the import error before starting (this is the guard that stops an" >&2
  echo "auto-restart resurrecting a broken stack):" >&2
  echo "$SMOKE_ERR" | tail -20 >&2
  exit 1
fi

echo "Starting synthetic-enterprise autonomous stack..."

# DEPLOY CURRENT HEAD (2026-07-16, Item 3 "a restart must deploy current HEAD").
# _start_session below SKIPS an already-running session ("safe to re-run") -- which
# silently LEAVES a daemon running code older than its committed script, the exact
# stale-running-code class the 2026-07-13 retro named but left DETECT-only
# (health_check flagged it; nothing acted). Kill any daemon whose live process predates
# its own script's mtime so the _start_session call respawns it FRESH on current code.
# Only STALE sessions are touched; a healthy daemon keeps its state. The env is already
# loaded above, so health_check imports cleanly; best-effort (2>/dev/null || true) so a
# missing env or import hiccup never blocks startup (worst case: no refresh, == today).
STALE_SESSIONS="$(python3 -c 'from background.health_check import stale_daemon_sessions; print("\n".join(stale_daemon_sessions()))' 2>/dev/null || true)"
if [ -n "$STALE_SESSIONS" ]; then
  while IFS= read -r _stale_s; do
    [ -z "$_stale_s" ] && continue
    echo "  [stale->restart] $_stale_s runs code older than HEAD -- killing so it respawns on current code"
    tmux kill-session -t "$_stale_s" 2>/dev/null || true
  done <<< "$STALE_SESSIONS"
fi

# ── Launch set DERIVED from the single manifest (process_manifest.yaml) — OPS1 sub-step 2, G-L2 ──
# No hardcoded list here to drift. start_worker.sh launches exactly process_reconciler.startlist()
# (owner==start_worker.sh, state in enabled|dark). HELD and RETIRED entries are NOT launched — that
# IS the hold, declared ONCE in the manifest, so a held daemon can never be silently resurrected by
# a stack restart (the 2026-07-17 incident). Fail-closed: an unreadable manifest refuses to start a
# partial stack.

# file-api needs its own key (FILE_API_ENV_FLAGS); load before the loop (same warm-server -e need).
FILE_API_ENV_PATH="$HOME/.config/synthetic-enterprise/.env.file-api"
[ -f "$FILE_API_ENV_PATH" ] || FILE_API_ENV_PATH="background/.env.file-api"
FILE_API_ENV_FLAGS=()
if [ -f "$FILE_API_ENV_PATH" ]; then
  while IFS= read -r line; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    export "$line"
    FILE_API_ENV_FLAGS+=(-e "$line")
  done < "$FILE_API_ENV_PATH"
fi

STARTLIST="$(python3 -m background.process_reconciler startlist)" || {
  echo "REFUSING TO START: could not derive the launch set from background/process_manifest.yaml" >&2
  echo "(fail-closed: a stack whose declaration can't be read is not started)" >&2
  exit 1
}
while IFS=$'\t' read -r _session _command; do
  [ -z "$_session" ] && continue
  _extra=("${NTFY_ENV_FLAGS[@]}")
  [ "$_session" = "file-api" ] && _extra+=("${FILE_API_ENV_FLAGS[@]}")
  _start_session "$_session" "$_command" "manifest-declared" "${_extra[@]}"
done <<< "$STARTLIST"

echo ""
echo "Stack startup complete. Running health check..."
python3 background/health_check.py --quiet
echo ""
echo "Attach to any session: tmux attach -t <session-name>"
echo "Sessions: background-worker, session-watchdog, staging-watcher, supervisor,"
echo "         ntfy-responder, dispatcher, discovery-daemon, sanity-daemon,"
echo "         deadmans-switch, director-comments"
