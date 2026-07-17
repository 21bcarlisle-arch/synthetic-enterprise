#!/bin/bash
# Reconstruct OS-level services from the repo — OPS1 sub-step 3 (reconstruct-from-repo).
# Installs every systemd (--user) unit declared in background/schedule_manifest.yaml from its
# committed unit_file, enables the boot-start ones, and daemon-reloads. Idempotent. On a fresh
# machine this script + the repo alone reproduce the service config — no hand-configuration, no
# hidden machine state. The declared cron set is empty by design, so nothing is installed there.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p ~/.config/systemd/user

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
    systemctl --user enable "$name" >/dev/null 2>&1 && echo "  enabled (boot-start)"
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
    systemctl --user enable "${session}.service" >/dev/null 2>&1 && echo "  enabled (boot-start)"
  else
    echo "  install-only (state=$state: not enabled — that IS the hold/dark; started only by the gated migration)"
  fi
done <<< "$PROC_UNITS"

systemctl --user daemon-reload
echo ""
echo "done — units installed (NOT started; starting is the gated migration)."
echo "reconcile: python3 -m background.schedule_reconciler  &&  python3 -m background.process_reconciler"
