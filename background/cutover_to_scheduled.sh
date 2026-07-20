#!/bin/bash
# CUTOVER to scheduled bounded invocations (SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md §8, 2026-07-20).
# DIRECTOR-RUN, FROM OUTSIDE THE WORKER SEAT. This retires the persistent worker seat — which is the
# session the migration was BUILT in — and a process cannot cleanly kill itself mid-turn, so run this
# from a SEPARATE shell (same pattern as bounce_worker_seat.sh). Platform-administration (systemd +
# the autonomy transport): director-reserved.
#
#   Diagnose only:   background/cutover_to_scheduled.sh
#   Apply cutover:   background/cutover_to_scheduled.sh --apply
#   Roll back:       background/cutover_to_scheduled.sh --rollback
#
# Idempotent. Each apply step is reconcile-checked. Rollback is a flag flip + unit swap — the
# persistent-seat heartbeat is byte-for-byte intact behind the flag, so fallback is not a rebuild.
set -euo pipefail
cd "$(dirname "$0")/.."

FLAG="docs/observability/.scheduled_invocations_enabled"
MODE="${1:-diagnose}"

banner() { echo ""; echo "==== $1 ===="; }

diagnose() {
  banner "SCHEDULED-INVOCATIONS CUTOVER — STATE"
  echo "scheduled flag:        $([ -f "$FLAG" ] && echo PRESENT || echo absent)"
  echo "worker-tick.timer:     $(systemctl --user is-active worker-tick.timer 2>/dev/null || echo inactive)"
  echo "worker-tick.path:      $(systemctl --user is-active worker-tick.path 2>/dev/null || echo inactive)"
  echo "worker-seat-manager:   $(systemctl --user is-active worker-seat-manager.service 2>/dev/null || echo inactive)"
  echo "build_executor flag:   $([ -f docs/observability/.build_executor_enabled ] && echo ON || echo off)"
  echo ""
  echo "Reconcile (expect 0 drift AFTER an --apply + the committed manifest flip):"
  python3 -m background.schedule_reconciler 2>&1 | tail -5 || true
}

apply() {
  banner "APPLYING CUTOVER"
  # 1. Scheduled-mode flag: the Stop hook stops heartbeating; any live seat allow-stops cleanly at
  #    its next rest (no more token burn). Reversible: just delete the flag.
  touch "$FLAG"
  echo "1. created $FLAG (Stop hook -> scheduled mode: allow-stop, no heartbeat)"

  # 2. Install (from committed unit files) + start the timer and path. install_schedule.sh installs
  #    all declared units; here we explicitly enable+start the two continuity triggers.
  bash background/install_schedule.sh >/dev/null 2>&1 || true
  systemctl --user daemon-reload
  systemctl --user enable --now worker-tick.timer worker-tick.path
  echo "2. worker-tick.timer + worker-tick.path enabled + started"

  # 3. Retire the persistent seat manager. The old tmux 'claude' seat will exit at its next
  #    allow-stop (scheduled mode); if it lingers, kill it BY SESSION ID (never the ambiguous name).
  systemctl --user disable --now worker-seat-manager.service 2>/dev/null || true
  echo "3. worker-seat-manager.service stopped + disabled (persistent seat retired)"
  echo "   NOTE: if a tmux 'claude' seat lingers, the director closes it (it is this session)."

  # 4. Revert the stop-hook block cap (no keep-alive blocks to cap in scheduled mode). Manual, in
  #    .claude/settings.json — printed here rather than auto-edited (settings is director-owned).
  echo "4. TODO (director, IaC): revert CLAUDE_CODE_STOP_HOOK_BLOCK_CAP in .claude/settings.json to default."

  banner "IaC SYNC REQUIRED (reconstruct-from-repo) — COMMIT THESE"
  echo " - background/schedule_manifest.yaml: flip worker-tick.timer/.path/.service to enabled/active."
  echo " - retire worker-seat-manager from the process manifest (owner:systemd -> retired)."
  echo " - .claude/settings.json: block-cap revert (step 4)."
  echo "Until committed, reconcile will show drift — that is the IaC guard working, not a failure."

  diagnose
}

rollback() {
  banner "ROLLING BACK TO THE PERSISTENT SEAT"
  rm -f "$FLAG"
  echo "1. removed $FLAG (Stop hook -> persistent-seat heartbeat, unchanged behind the flag)"
  systemctl --user disable --now worker-tick.timer worker-tick.path 2>/dev/null || true
  echo "2. worker-tick.timer + worker-tick.path stopped + disabled"
  systemctl --user enable --now worker-seat-manager.service 2>/dev/null || true
  echo "3. worker-seat-manager.service re-enabled + started (re-seeds the persistent seat)"
  diagnose
}

case "$MODE" in
  --apply)    apply ;;
  --rollback) rollback ;;
  *)          diagnose ;;
esac
