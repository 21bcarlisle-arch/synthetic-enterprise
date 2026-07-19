#!/usr/bin/env bash
# bounce_worker_seat.sh — reconcile the worker-seat IDENTITY DRIFT (IDENTITY_DRIFT_FIX, 2026-07-19).
#
# WHY: the seat was seeded with `--resume WORKER_SESSION_ID`, but this Claude Code build brought it up
# under a DIFFERENT live session id. The pull-loop Stop hook identifies the worker by
# `session_id == WORKER_SESSION_ID`, so the drifted seat was rejected as "non-worker" on every Stop —
# no work was ever delivered (the doorbell rang at a stale address). The committed fix makes worker_seat
# seed DETERMINISTICALLY with `--session-id` and verify identity in its keep-alive; this script deploys
# that fix and bounces the one already-drifted seat so the transport recognises it (which also arms the
# REST HEARTBEAT).
#
# RUN THIS FROM A SEPARATE TERMINAL, OUTSIDE any claude seat/console.
#   Diagnose only (no changes):   bash background/bounce_worker_seat.sh
#   Apply the bounce (asks y/N):  bash background/bounce_worker_seat.sh --apply
#
# The agent BUILT this but did NOT run it (a re-seed kills the drifted session, and the agent may BE it).
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
WORKER_ID="$(python3 -c 'from background.worker_seat import WORKER_SESSION_ID as w; print(w)')"

diagnose() {
  echo "== WORKER_SESSION_ID the transport expects : $WORKER_ID"
  echo "== worker_seat.py has the deterministic-seed fix?"
  if grep -q 'DETERMINISTIC IDENTITY' background/worker_seat.py; then echo "   YES (fix present on disk)"; else echo "   NO — 'git pull' the fix before applying"; fi
  echo "== tmux sessions (which one holds the seat):"
  tmux list-sessions 2>/dev/null || echo "   (no tmux server)"
  echo "== all live claude sessions and their ACTUAL live id (via open transcript fd):"
  for pid in $(pgrep -f 'claude --dangerously-skip-permissions' 2>/dev/null); do
    id="$(ls -l /proc/$pid/fd 2>/dev/null | grep -oE '[0-9a-f-]{36}\.jsonl' | head -1 | sed 's/\.jsonl//')"
    echo "   pid=$pid live_id=${id:-unknown}"
  done
  echo "== live id inside tmux 'claude' (the managed seat):"
  local live; live="$(python3 -c 'from background import worker_seat as W; print(W._live_session_id())')"
  echo "   live=$live"
  # Verdict routed through _classify_seat (NOT a bare string compare) so an UNREADABLE id (None,
  # e.g. a fresh seat with no transcript yet) reads as OK, not a false 'DRIFT: None != ...'.
  echo "   -> $(python3 -c 'from background import worker_seat as W; print(W.drift_report(W._session_alive(), W._live_session_id()))')"
  echo "== current pull-loop health:"; cat docs/observability/.pull_loop_health.json 2>/dev/null; echo
}

apply() {
  local cur; cur="$(tmux display-message -p '#S' 2>/dev/null || echo '')"
  if [ "$cur" = "claude" ]; then echo "REFUSING: you are INSIDE tmux 'claude' (the seat itself). Re-run from a separate terminal."; exit 1; fi
  echo ">> [1/4] restarting worker-seat-manager (loads the fixed worker_seat.py)"
  systemctl --user restart worker-seat-manager.service || { echo "   restart failed — check the service"; exit 1; }
  echo ">> [2/4] archiving any stale transcript so --session-id is a clean create"
  python3 -c 'from background import worker_seat as W; W._archive_stale_transcript()'
  echo ">> [3/4] ending the drifted seat (tmux 'claude'); the manager re-seeds it deterministically."
  echo "   NOTE: if the agent's current interactive session lives in tmux 'claude', THIS ENDS IT —"
  echo "         that is expected: that session IS the drifted seat. A clean, recognised worker seat"
  echo "         replaces it; keep steering via NTFY / docs/staging/."
  tmux kill-session -t claude 2>/dev/null || echo "   (tmux 'claude' already gone; manager will re-seed)"
  echo ">> [4/4] waiting for the deterministic re-seed (manager polls ~60s)…"
  for _ in $(seq 1 15); do sleep 10; tmux has-session -t claude 2>/dev/null && break; done
  sleep 8
  local live; live="$(python3 -c 'from background import worker_seat as W; print(W._live_session_id())')"
  echo ">> new live seat id: ${live:-unknown}   (expected $WORKER_ID)"
  if [ "$live" = "$WORKER_ID" ]; then
    echo "PASS: seat identity reconciled. The pull-loop will now recognise it and (once its bring-up"
    echo "      turn ends) the REST HEARTBEAT keeps it alive. Expect a fresh worker health outcome soon:"
  elif [ "$live" = "None" ] || [ -z "$live" ]; then
    echo "PENDING: live id not readable yet (fresh seat has written no transcript) — re-run diagnose in ~2 min."
  else
    echo "CHECK: id CONFIRMED mismatched ($live != $WORKER_ID) — the seat may still be mid-bring-up. Re-run diagnose in ~2 min."
  fi
  cat docs/observability/.pull_loop_health.json 2>/dev/null; echo
}

case "${1:-diagnose}" in
  diagnose|"") diagnose ;;
  --apply|apply)
    diagnose; echo
    read -r -p "Proceed to APPLY the bounce (restart manager, archive, kill+reseed tmux 'claude')? [y/N] " a
    if [ "$a" = "y" ] || [ "$a" = "Y" ]; then apply; else echo "aborted (no changes made)"; fi ;;
  *) echo "usage: $0 [diagnose|--apply]"; exit 1 ;;
esac
