#!/bin/bash
# Start all autonomous background processes in detached tmux sessions.
# Usage: bash background/start_worker.sh
# Safe to re-run — skips sessions that are already running.
cd ~/synthetic-enterprise
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_NUM_CTX=8192

# Load SE_NTFY_TOPIC / SE_WAKE_HMAC_KEY from the gitignored env file before
# starting ANY session that touches NTFY or the tmux wake relay (session-
# watchdog, staging-watcher, ntfy-responder, dispatcher, discovery-daemon,
# sim-runner all import background.ntfy_utils, which raises loudly at import
# time if this isn't set — 2026-07-08 topic rotation,
# docs/staging/NTFY_CHANNEL_HARDENING.md).
NTFY_ENV_FLAGS=()
if [ -f background/.env.ntfy ]; then
  while IFS= read -r line; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    export "$line"
    NTFY_ENV_FLAGS+=(-e "$line")
  done < background/.env.ntfy
else
  echo "WARNING: background/.env.ntfy not found -- NTFY-touching sessions will fail to start." >&2
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
  "Qwen task queue, runs off-peak (not 16:00-19:00 GMT)"

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
FILE_API_ENV_FLAGS=()
if [ -f background/.env.file-api ]; then
  while IFS= read -r line; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    export "$line"
    FILE_API_ENV_FLAGS+=(-e "$line")
  done < background/.env.file-api
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
echo "         ntfy-responder, dispatcher, discovery-daemon"
