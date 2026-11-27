# S3 losses flip: premise spent, the grade is carried by its successor (2026-11-27)

Lane 0 drew `s3-the-world-settles-electricity-losses-against-s1` again after it had already landed.

- The flip and the test leg are on origin at **802a18f42**. `SETTLEMENT_LOSSES_APPLIED: bool = True` is set in
  `simulation/hedged_settlement.py:75`, and the off-by-default leg moved to the new default.
- The one-variable arm is **in flight**: longjob `s3-losses-arm-76f894811d` (pid 3800775, expected about 120 min),
  writing to `/var/tmp/se-s3-losses/out/run_output_arm.json`. That file did not exist at 2026-11-27 ~10:00.
- The grade against S1's book (`docs/reports/run_output_76f894811d_20261126T155009Z.json`, P1–P4) belongs to
  **`s3-grade-the-losses-arm-against-s1s-book`**, which is embargoed until that file exists.

Disposition: `--premise-spent ... 802a18f42`, then `--release`. No second arm was launched over the same seeds.
