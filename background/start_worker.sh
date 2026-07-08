#!/bin/bash
# Start all autonomous background processes in detached tmux sessions.
# Usage: bash background/start_worker.sh
# Safe to re-run — skips sessions that are already running.
cd ~/synthetic-enterprise
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_NUM_CTX=8192

_start_session() {
  local name="$1"
  local cmd="$2"
  local desc="$3"
  if tmux has-session -t "$name" 2>/dev/null; then
    echo "  [already running] $name"
  else
    tmux new-session -d -s "$name" -c ~/synthetic-enterprise "$cmd"
    echo "  [started] $name — $desc"
  fi
}

echo "Starting synthetic-enterprise autonomous stack..."

_start_session "background-worker" \
  "python3 background/background_worker.py" \
  "Qwen task queue, runs off-peak (not 16:00-19:00 GMT)"

_start_session "session-watchdog" \
  "python3 background/session_watchdog.py" \
  "Auto-resumes Claude session after usage-limit resets"

_start_session "staging-watcher" \
  "python3 background/staging_watcher.py" \
  "Sends NTFY when new files land in docs/staging/"

_start_session "ntfy-responder" \
  "python3 background/ntfy_responder.py" \
  "Instant-acks all inbound NTFY messages, writes to staging/"

_start_session "dispatcher" \
  "python3 background/dispatcher.py" \
  "Classifies from_rich_*.md as URGENT/NORMAL/FYI and routes"

_start_session "discovery-daemon" \
  "python3 background/discovery_agent.py --daemon" \
  "Validates simulation assumptions every 6h via Qwen"

_start_session "sim-runner" \
  "python3 background/sim_runner.py" \
  "Continuous 9.5yr simulation loop — pegs GPU off-peak, writes run_complete markers"

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

# Load FILE_API_KEY from .env.file-api if not already exported
if [ -f background/.env.file-api ]; then
  export $(grep -v "^#" background/.env.file-api | xargs)
fi

_start_session "file-api" \
  "python3 -m uvicorn background.file_api:app --host 0.0.0.0 --port 8765" \
  "Authenticated file API + Ollama /query proxy on :8765"

echo ""
echo "Stack startup complete. Running health check..."
python3 background/health_check.py --quiet
echo ""
echo "Attach to any session: tmux attach -t <session-name>"
echo "Sessions: background-worker, session-watchdog, staging-watcher,"
echo "         ntfy-responder, dispatcher, discovery-daemon"
