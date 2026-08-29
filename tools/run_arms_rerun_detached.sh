#!/usr/bin/env bash
# Both legs of the arms comparison, ONE session, one clock, to NEW paths.
#
# Why this exists as a script rather than a shell one-liner in a tick: the tick runs inside
# `worker-tick.service`, whose KillMode is `control-group`. When the tick's oneshot service
# finishes, systemd SIGTERMs every process in that cgroup. `setsid` does NOT escape a systemd
# cgroup -- the 2026-08-28 run recorded `pid==pgid==sess` and was killed anyway, mid-progress,
# with no traceback. The only launch that survives a tick boundary here is a transient unit of
# its own (`systemd-run --user --unit=...`), which is what invokes this file.
#
# Both legs run in one process so the two artefacts cannot end up on different clocks -- the
# defect that put a 2026-08-27 noise floor underneath a 2026-08-28 three-arm figure.
set -uo pipefail

cd /home/rich/synthetic-enterprise

STAMP=20260829
THREE_ARM="docs/observability/value_cycle_ab_s1_three_arm_${STAMP}.json"
FLOOR="docs/observability/value_cycle_ab_s1_noise_floor_${STAMP}.json"
LOG="docs/observability/arms_rerun_${STAMP}_scoped.log"

{
  echo "START $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$ pgid=$(ps -o pgid= -p $$ | tr -d ' ') sess=$(ps -o sess= -p $$ | tr -d ' ')"
  echo "cgroup=$(cat /proc/self/cgroup)"

  echo "=== LEG 1/2: three arms (--level-arm, 3 passes) -> ${THREE_ARM} ==="
  python3 -m tools.run_value_cycle_ab --level-arm --out "${THREE_ARM}"
  echo "LEG1_RC=$? at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

  echo "=== LEG 2/2: noise floor (seeds 11111,22222,33333, 9 passes) -> ${FLOOR} ==="
  python3 -m tools.run_value_cycle_ab --level-arm \
      --noise-floor-seeds 11111,22222,33333 --out "${FLOOR}"
  echo "LEG2_RC=$? at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

  echo "DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "${LOG}" 2>&1
