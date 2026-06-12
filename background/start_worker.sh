#!/bin/bash
# Start the background worker in a detached tmux session
# Usage: bash background/start_worker.sh
cd ~/synthetic-enterprise
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_NUM_CTX=8192
tmux new-session -d -s background-worker -c ~/synthetic-enterprise \
  "python3 background/background_worker.py"
echo "Background worker started in tmux session 'background-worker'"
echo "Attach with: tmux attach -t background-worker"
echo "Worker will pause automatically between 16:00-19:00 GMT"

tmux new-session -d -s session-watchdog -c ~/synthetic-enterprise \
  "python3 background/session_watchdog.py"
echo "Session watchdog started in tmux session 'session-watchdog'"
echo "Attach with: tmux attach -t session-watchdog"
echo "Restarts of the 'claude' session require a YES reply via NTFY (skynet-synthetic)"

tmux new-session -d -s staging-watcher -c ~/synthetic-enterprise \
  "python3 background/staging_watcher.py"
echo "Staging watcher started in tmux session 'staging-watcher'"
echo "Attach with: tmux attach -t staging-watcher"
echo "Sends NTFY (skynet-synthetic) when a new file lands in docs/staging/ — notification only, no auto-execution"
