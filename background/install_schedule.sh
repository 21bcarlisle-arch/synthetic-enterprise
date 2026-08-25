#!/bin/bash
# Reconstruct OS-level services from the repo — OPS1 sub-step 3 (reconstruct-from-repo).
# Installs every systemd (--user) unit declared in background/schedule_manifest.yaml from its
# committed unit_file, enables the boot-start ones, and daemon-reloads. Idempotent. On a fresh
# machine this script + the repo alone reproduce the service config — no hand-configuration, no
# hidden machine state. The declared cron set is empty by design, so nothing is installed there.
set -euo pipefail

# Seat guard, FIRST act: installing the resident seat's systemd units on foreign
# soil would persist the stack into a machine that is not the seat. One
# discriminator, shared with the daemons and the hooks (background/_seat.py).
if ! python3 "$(dirname "$0")/_seat.py"; then
  echo "seat-guard: foreign, install_schedule.sh not starting" >&2
  exit 0
fi

cd "$(dirname "$0")/.."
mkdir -p ~/.config/systemd/user

# REACH THE USER BUS, OR SAY SO AND STOP (2026-08-25). `systemctl --user` needs XDG_RUNTIME_DIR;
# a shell without it -- cron, a non-login shell, a headless turn -- gets "Failed to connect to
# user scope bus". Every enable/arm below then failed while its `&& echo` simply printed nothing,
# and this script exited 0 having copied files and ARMED NOTHING. That is the exact fail-silent
# the manifest exists to prevent: units declared in git, present on disk, never scheduled -- and
# a timer nobody fires is indistinguishable from a feature nobody built. Measured the day it bit:
# `delivery-seat.timer` installed, reported clean, and absent from `systemctl --user list-timers`.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "REFUSING: cannot reach the systemd --user bus (XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR)." >&2
  echo "  Units would be COPIED and never enabled or armed, and this script would exit 0." >&2
  echo "  Run from a session with a user bus, or export XDG_RUNTIME_DIR and retry." >&2
  exit 1
fi
FAILURES=0

UNITS="$(python3 -c '
from background.schedule_reconciler import load_manifest
for u in load_manifest()["systemd_units"]:
    print(u["name"] + "\t" + u["unit_file"] + "\t" + ("1" if u.get("enabled") else "0"))
')"

while IFS=$'\t' read -r name unit_file enabled; do
  [ -z "$name" ] && continue
  cp "$unit_file" "$HOME/.config/systemd/user/$name"
  echo "installed $name  <-  $unit_file"
  if [ "$enabled" = "1" ]; then
    if systemctl --user enable "$name" >/dev/null 2>&1; then
      echo "  enabled (boot-start)"
    else
      echo "  FAILED to enable $name -- it will not boot-start" >&2; FAILURES=$((FAILURES+1))
    fi
    # A .timer must be ARMED to actually run its schedule (a drift-control timer that is enabled
    # but never started is fail-silent, R15). Arming a timer is scheduling, not launching a daemon,
    # so it is exempt from the "no start" rule that applies to .service daemons (gated migration).
    case "$name" in
      *.timer) systemctl --user start "$name" >/dev/null 2>&1 \
          && echo "  armed (timer started)" \
          || { echo "  FAILED to arm $name -- DECLARED BUT NEVER FIRES" >&2
               FAILURES=$((FAILURES+1)); } ;;
    esac
  fi
done <<< "$UNITS"

# ── OPS1 sub-step 4: install the PROCESS-manifest daemon units (systemd owns lifecycle) ──
# The generated, committed units under background/systemd/ (one per owner==systemd entry) are
# installed here too, so a fresh machine reconstructs the whole systemd unit set from the repo.
# state drives ENABLE only: enabled -> enable (boot-start); held/dark -> install WITHOUT enable
# (that IS the hold/dark, declared once in process_manifest.yaml). This script NEVER `start`s a
# daemon: bringing the stack live is the GATED one-at-a-time migration (worker-seat -> supervisor
# -> deadmans), each with its own verify -- install+enable is inert until `systemctl start`/boot.
PROC_UNITS="$(python3 -c '
from background import process_reconciler as R
for e in R.load_manifest():
    if e.get("owner") == "systemd":
        print(e["session"] + "\t" + e["state"])
')"
while IFS=$'\t' read -r session state; do
  [ -z "$session" ] && continue
  src="background/systemd/${session}.service"
  if [ ! -f "$src" ]; then
    echo "  WARNING: $src missing (regenerate: python3 background/generate_units.py)"; continue
  fi
  cp "$src" "$HOME/.config/systemd/user/${session}.service"
  echo "installed ${session}.service  <-  $src  (state=$state)"
  if [ "$state" = "enabled" ]; then
    if systemctl --user enable "${session}.service" >/dev/null 2>&1; then
      echo "  enabled (boot-start)"
    else
      echo "  FAILED to enable ${session}.service" >&2; FAILURES=$((FAILURES+1))
    fi
  else
    echo "  install-only (state=$state: not enabled — that IS the hold/dark; started only by the gated migration)"
  fi
done <<< "$PROC_UNITS"

systemctl --user daemon-reload
echo ""
if [ "${FAILURES:-0}" -gt 0 ]; then
  # NON-ZERO EXIT so a caller that checks -- and a human reading a scrollback -- sees it. A
  # partial install reporting success is how a declared timer ends up never firing.
  echo "FAILED: $FAILURES unit(s) installed but not enabled/armed -- see the errors above." >&2
  exit 1
fi
echo "done — units installed (NOT started; starting is the gated migration)."
echo "reconcile: python3 -m background.schedule_reconciler  &&  python3 -m background.process_reconciler"
