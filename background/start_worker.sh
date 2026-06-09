#!/bin/bash
# Start the background worker in a detached tmux session
# Usage: bash background/start_worker.sh
cd ~/synthetic-enterprise
tmux new-session -d -s background-worker -c ~/synthetic-enterprise \
  "python3 background/background_worker.py"
echo "Background worker started in tmux session 'background-worker'"
echo "Attach with: tmux attach -t background-worker"
echo "Worker will pause automatically between 16:00-19:00 GMT"
