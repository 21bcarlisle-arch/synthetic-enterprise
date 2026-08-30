#!/usr/bin/env bash
# THE THREE-ARM LEG ONLY, re-run to carry `method_skill.drop_out` -- the funnel from the 20
# decisions the arm priced down to the 6 the concordance scores.
#
# WHY THE NOISE FLOOR IS NOT RE-RUN BESIDE IT, when the standing rule is that the pair share one
# clock. The change this run carries is PURELY ADDITIVE to `method_skill`: no arm, no policy, no
# seed and no estimator moved. So the published pair stays on one clock only if this run
# reproduces the 2026-08-29 three-arm artefact EXACTLY apart from `generated_at` and the new
# keys -- which is checked, not assumed, by the diff in `--check` below before anything is
# published. If the diff is not empty the run is NOT a re-measurement of one clock and must not
# be published over the old artefact; the correct move then is to re-run both legs together.
#
# Launched as a transient unit of its own: `worker-tick.service` is KillMode=control-group, and
# a job started from inside a tick is SIGTERMed when the tick ends. `setsid` does not escape a
# systemd cgroup -- the 2026-08-28 run proved that by dying with pid==pgid==sess.
set -uo pipefail

cd /home/rich/synthetic-enterprise

STAMP=20260830
NEW="docs/observability/value_cycle_ab_s1_three_arm_${STAMP}.json"
OLD="docs/observability/value_cycle_ab_s1_three_arm_20260829.json"
LOG="docs/observability/arms_skill_funnel_${STAMP}.log"

if [ "${1:-}" = "--check" ]; then
  # THE DETERMINISM DIFF. Everything except the clock and the two new keys must be identical.
  python3 - "${OLD}" "${NEW}" <<'PY'
import json
import sys

def strip(path):
    doc = json.load(open(path, encoding="utf-8"))
    doc.pop("generated_at", None)
    skill = doc.get("method_skill") or {}
    skill.pop("drop_out", None)
    skill.pop("dropped_sample", None)
    return json.dumps(doc, sort_keys=True, indent=1).splitlines()

old, new = (strip(p) for p in sys.argv[1:3])
if old == new:
    print("DETERMINISM OK -- the re-run reproduces the published artefact exactly.")
    raise SystemExit(0)
print("DETERMINISM FAILED -- the re-run is a different measurement, not the same one "
      "instrumented. Do NOT publish it over the old artefact.")
import difflib
for line in list(difflib.unified_diff(old, new, "published", "rerun", lineterm=""))[:60]:
    print(line)
raise SystemExit(1)
PY
  exit $?
fi

{
  echo "START $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$ cgroup=$(cat /proc/self/cgroup)"
  echo "=== three arms (--level-arm, 3 passes) -> ${NEW} ==="
  python3 -m tools.run_value_cycle_ab --level-arm --out "${NEW}"
  echo "RC=$? at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "${LOG}" 2>&1
