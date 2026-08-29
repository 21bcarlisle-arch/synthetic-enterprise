#!/usr/bin/env bash
# ONE SESSION, BOTH LEGS. The published pair disagrees about its own clock -- the three-arm
# artefact was measured 2026-08-28T14:08:48Z on 210 settled accounts and the noise floor
# 2026-08-27T23:32:17Z on a different book -- so the error bar on the live headline is measured
# against a run the headline is not from. Running them in one shell, back to back, off one book,
# is what makes `staleness_caveat` and `clock_caveat` have nothing left to say.
#
# NEW PATHS, never over the published artefacts: a publish running concurrently in this shared
# tree must not read a half-written file, and the two must stay diffable.
#
# Seeds are the SAME three the 2026-08-27 floor used (11111,22222,33333). A floor re-drawn on
# different seeds would not be comparable with the one it is replacing.
set -u
cd /home/rich/synthetic-enterprise
LOG=docs/observability/arms_rerun_20260829.log
echo "START $(date -u +%FT%TZ) pid=$$ pgid=$(ps -o pgid= -p $$ | tr -d ' ')" >> "$LOG"

python3 -m tools.run_value_cycle_ab --level-arm \
  --out docs/observability/value_cycle_ab_s1_three_arm_20260829.json >> "$LOG" 2>&1
echo "END three_arm rc=$? $(date -u +%FT%TZ)" >> "$LOG"

python3 -m tools.run_value_cycle_ab --noise-floor-seeds 11111,22222,33333 \
  --out docs/observability/value_cycle_ab_s1_noise_floor_20260829.json >> "$LOG" 2>&1
echo "END noise_floor rc=$? $(date -u +%FT%TZ)" >> "$LOG"

echo "END ALL $(date -u +%FT%TZ)" >> "$LOG"
