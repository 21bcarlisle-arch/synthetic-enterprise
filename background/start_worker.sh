#!/bin/bash
# Start all autonomous background processes in detached tmux sessions.
# Usage: bash background/start_worker.sh
# Safe to re-run — skips sessions that are already running.
cd ~/synthetic-enterprise
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_NUM_CTX=8192

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

echo "Starting synthetic-enterprise autonomous stack..."

_start_session "background-worker" \
  "python3 background/background_worker.py" \
  "Qwen task queue, runs off-peak (not 16:00-19:00 GMT)" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "session-watchdog" \
  "python3 background/session_watchdog.py" \
  "Auto-resumes Claude session after usage-limit resets" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "staging-watcher" \
  "python3 background/staging_watcher.py" \
  "Sends NTFY when new files land in docs/staging/" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "supervisor" \
  "python3 background/supervisor.py" \
  "Sole turn-granting authority (2026-07-09, doorbell failure #4) -- polls every 2min, grants a turn when idle+work exists" \
  "${NTFY_ENV_FLAGS[@]}"

# The self-continuing headless build loop (H17, DIRECTOR_ANSWERS_C7). DARK-gated:
# a bare launch is a safe no-op unless the director's console-only enable flag
# (docs/observability/.build_executor_enabled) is present, so it is safe to
# always start here. Added 2026-07-16: it was never in start_worker.sh, so it
# did not come up with the other daemons and a reboot lost it entirely (the gap
# behind "flag enabled but nothing executes the loop").
_start_session "executor-daemon" \
  "python3 background/executor_daemon.py" \
  "Self-continuing headless build loop -- draw->dispatch claude -p->gate on origin, DARK unless the enable flag is set" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "ntfy-responder" \
  "python3 background/ntfy_responder.py" \
  "Instant-acks all inbound NTFY messages, writes to staging/" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "dispatcher" \
  "python3 background/dispatcher.py" \
  "Classifies from_rich_*.md as URGENT/NORMAL/FYI and routes" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "discovery-daemon" \
  "python3 background/discovery_agent.py --daemon" \
  "Validates simulation assumptions every 6h via Qwen" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "sim-runner" \
  "python3 background/sim_runner.py" \
  "Continuous 9.5yr simulation loop — pegs GPU off-peak, writes run_complete markers" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "sanity-daemon" \
  "python3 background/sanity_daemon.py" \
  "DOMAIN_SENSE_AND_COMPLIANCE.md Phase 5 -- population-level statistical sanity checks every 30min, one NTFY per new/changed finding set" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "deadmans-switch" \
  "python3 background/deadmans_switch.py" \
  "Director-flagged 2026-07-09 (doorbell failure #5) -- independent of the tmux/supervisor stack: BLOCKED alert if 90min+ pass with no commit/observability activity AND real staged work is queued" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "director-comments" \
  "python3 background/director_comments.py" \
  "DIRECTOR_COMMENTS_BOX.md -- polls the dedicated comments-only ntfy topic, validates the PIN server-side, stages accepted director page comments" \
  "${NTFY_ENV_FLAGS[@]}"

_start_session "naive-organ" \
  "python3 -m background.naive_organ daemon" \
  "H11 L3 (NAIVE_ORGAN_BLIND_SPOT_AND_USAGE_WRITE.md): the independent outside-view skeptic on its OWN wall-clock timer (NOT publish-coupled), so it can fire when the system is silent; trigger #8 EXPECTED OUTPUT ABSENT reads the independent git commit clock" \
  "${NTFY_ENV_FLAGS[@]}"

# RETIRED 2026-07-08 (docs/staging/AUTONOMOUS_RUNNER_TRUE_RETIREMENT.md, director-approved
# Option A of docs/review_gates/AUTONOMOUS_RUNNER_STILL_RUNNING.md). Deliberately stopped:
# waste + tree-race source + budget burn. Single-writer mode = the watchdog-managed
# interactive session only. A console kill alone was NOT durable — a stack re-run
# (start_worker.sh) resurrected it, so the launcher block itself is commented out here.
# Retiring a daemon = edit its launcher, not just kill the process (see MAINTENANCE.md).
# Do NOT re-enable without a fresh director decision at a weekly re-rank.
# _start_session "autonomous-runner" \
#   "python3 background/autonomous_runner.py" \
#   "Fires claude -p turn after 30min idle — replaces broken tmux keystrokes autoloop"

_start_session "token-proxy" \
  "python3 -m background.token_proxy" \
  "Local HTTP proxy on :8801 — tracks token usage for autonomous turns"

# Load FILE_API_KEY from .env.file-api. Same warm-server `-e` requirement as
# NTFY_ENV_FLAGS above (2026-07-08) -- a plain `export` here silently did not
# reach a NEW session on an ALREADY-RUNNING tmux server; harmless historically
# only because file-api has never actually needed a mid-uptime restart yet.
# 2026-07-11, Option 2 floor -- same new-location-first, old-fallback
# pattern as NTFY_ENV_PATH above.
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

_start_session "file-api" \
  "python3 -m uvicorn background.file_api:app --host 0.0.0.0 --port 8765" \
  "Authenticated file API + Ollama /query proxy on :8765" \
  "${FILE_API_ENV_FLAGS[@]}"

echo ""
echo "Stack startup complete. Running health check..."
python3 background/health_check.py --quiet
echo ""
echo "Attach to any session: tmux attach -t <session-name>"
echo "Sessions: background-worker, session-watchdog, staging-watcher, supervisor,"
echo "         ntfy-responder, dispatcher, discovery-daemon, sanity-daemon,"
echo "         deadmans-switch, director-comments"
