**Severity:** INFO · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The fresh-run item is spent; its grade is carried by the-fresh-run-at-2eeb3f0b3-is-graded (2026-10-27)

Delivery item `the-fresh-run-carries-both-fixes-and-retires-the-exceptions`, drawn again at 13:1xZ and
released as spent. Measured at draw, origin 490b9ed94c:

- (a) Two blind register rows: landed in 9f7b850189 (INV_REGISTER_ID_ONE_LABEL,
  INV_SERIAL_REGISTER_COUNT_STABLE). INV_PERIODS_CONTIGUOUS was traced in the same commit to bills
  the pre-bill gate holds and never issues.
- (b) Pre-registration: `docs/staging/records/SEAT_PREREGISTRATION_THE_FRESH_RUN_AT_2EEB3F0B3_CARRIES_THE_CLAMP_THE_OCCUPIER_CREDIT_UIG_AND_THE_SHARED_HUB_2026-10-27.md`,
  filed 12:17Z (sha256 0b2a93222ffc) before launch.
- (c) Run: unit `longjob-fresh-run-2eeb3f0b3` has been active since 12:43:25Z (pid 255149,
  `/var/tmp/fresh-run-scripts/arm.py /var/tmp/fresh-run-out-2eeb3f0b3`). No DONE.json yet.
- (d) Grade, exception retirement and marking each prediction held or refuted: carried by the live
  continuation `the-fresh-run-at-2eeb3f0b3-is-graded`. The held-bill release path that
  INV_PERIODS_CONTIGUOUS needs is carried by `a-held-bill-is-released-and-billed`.

This turn launched nothing. A second launch would run a second copy over the same seeds.

## Done

Disposition taken, claim released. No work was repeated.
