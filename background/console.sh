#!/bin/bash
# Sanctioned director-console launcher — OPS1 sub-step 1, guarantee G-L1
# (docs/design/OPERATIONAL_LAYER_DESIGN.md §2.1).
#
# Starts an interactive Claude Code console that is STRUCTURALLY exempt from
# watchdog reaping: it registers THIS process id in the console-sanctity marker
# BEFORE handing the terminal to claude, so session_watchdog can never kill it
# (the exit-143 console-kill class, made impossible by construction — and
# independent of tmux being reachable).
#
# Mechanism: register $$ (this shell's pid), then `exec claude`. exec REPLACES
# the shell with claude while KEEPING THE SAME pid and start-time, so the pid we
# registered is exactly the running claude — no race, no lookup-after-spawn.
#
# Usage:  background/console.sh [extra claude args...]
# The director launches his console this way instead of a bare `claude`.
set -euo pipefail
cd "$(dirname "$0")/.."

# Register this pid as a sanctified console (records its /proc start-time as the
# anti-forgery key). Best-effort: if registration fails we still start the
# console — it just falls back to the inference belt rather than the structural
# guarantee, and we say so loudly rather than silently.
if python3 -m background.console_sanctity sanctify "$$"; then
  echo "console.sh: pid $$ registered as a sanctified console (G-L1) — watchdog can never reap it."
else
  echo "console.sh: WARNING — could not register sanctity for pid $$; console will rely on the inference belt only." >&2
fi

exec claude --dangerously-skip-permissions "$@"
