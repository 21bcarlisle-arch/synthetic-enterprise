#!/bin/bash
# The deliberate interactive path for the director (SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md §7,
# director requirement 2026-07-20: "after cutover there is no persistent seat to attach to —
# preserve a deliberate path for me to interact directly").
#
# After the scheduled-invocations cutover there is no resident worker seat. This launches an
# on-demand INTERACTIVE Claude Code session in the repo whenever the director wants one. It is:
#   - NEVER the worker: it does NOT set SE_SBI_WORKER, so the Stop hook (scheduled mode) allow-stops
#     it and the systemd timer/path never deliver work into it. It is a director console, full stop.
#   - ALWAYS immediately responsive: nothing resident holds a session or a lock, so there is no
#     queue to wait behind — the exact failure (27-min input block) that the migration removes.
#   - Coexisting with the headless worker: worker `claude -p` invocations run in the background;
#     commits from either are serialized by tree_lock. When the director leaves, this session simply
#     idles at ~0 cost (allow-stop) while the scheduled worker keeps running underneath.
#
# Usage:  background/director_console.sh          # fresh interactive session
#         background/director_console.sh --resume # resume the last director session
set -euo pipefail
cd "$(dirname "$0")/.."

# Resolve claude off nvm (a plain shell may not have it on PATH).
CLAUDE="$(command -v claude || true)"
if [ -z "$CLAUDE" ]; then
  CLAUDE="$(ls -1 "$HOME"/.nvm/versions/node/*/bin/claude 2>/dev/null | sort | tail -1 || true)"
fi
if [ -z "$CLAUDE" ]; then
  echo "claude binary not found (checked PATH and ~/.nvm/versions/node/*/bin)"; exit 1
fi

# Explicitly UNSET the worker discriminator so this can never be mistaken for a worker invocation,
# even if the launching shell happened to inherit it.
unset SE_SBI_WORKER

echo "Launching director console (interactive, opus-4-8, NOT the worker seat)."
echo "The scheduled worker keeps running headless in the background; this session is yours."
exec "$CLAUDE" --dangerously-skip-permissions --model claude-opus-4-8 "$@"
