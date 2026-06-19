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

_start_session "autonomous-runner" \
  "python3 background/autonomous_runner.py" \
  "Fires claude -p turn after 30min idle — replaces broken tmux keystrokes autoloop"

echo ""
echo "Stack startup complete. Running health check..."
python3 background/health_check.py --always
echo ""
echo "Attach to any session: tmux attach -t <session-name>"
echo "Sessions: background-worker, session-watchdog, staging-watcher,"
echo "         ntfy-responder, dispatcher, discovery-daemon"
