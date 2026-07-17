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

systemctl --user daemon-reload
echo "done — reconcile with: python3 -m background.schedule_reconciler"
