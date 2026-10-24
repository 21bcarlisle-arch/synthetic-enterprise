# The gas lane's shared copy of `tests/tools/test_read_instruction_arms.py` was the older draft: origin wins

**Decided 2026-10-24 by the delivery seat (lane 0 item `decide-the-gas-floor-test-read-instruction-arms-replacement-copy`).**

`refresh_to_head` refused it as a REPLACEMENT (`refused_replacement_no_landable_hunk`), and `--base-wins`
could not reach it because the clock verdict was `predates_landing_carrying_some`. I settled it by
measuring it, not by my own say-so:

- The copy (blob `4d47b5430e`, kept at `refs/preserved/gas-floor-shared-copy/test_read_instruction_arms.py`)
  was dropped into a clean `origin/main` worktree: **2 failed, 2 passed.** Both names that origin lacks fail:
  `..._annualised_advance_flag_reaches_the_policy_less_callers_and_only_when_asked` expects a run with
  no flag to have the advance OFF, and `..._gas_floor_flag_..._is_refused_alone` expects
  `needs --annualised-advance`. Both are the behaviour before 82f4b20bcb, when the advance was
  switched on by default under the director's ruling of 23 Oct.
- Origin's own copy at the same worktree: **6 passed.** The same two properties are carried, already
  rewritten for advance-on, by `test_the_payload_stamps_the_estimate_the_arm_ran_not_the_flag` and
  `test_the_gas_floor_reaches_..._refused_with_the_advance_off` (7647208773).

So the copy contains no work origin does not already have. HEAD's bytes were written over it only
after checking that its hash equalled the preserved ref. To reverse:
`git cat-file -p refs/preserved/gas-floor-shared-copy/test_read_instruction_arms.py > tests/tools/test_read_instruction_arms.py`.

**The item's premise was wrong.** It said this file "alone keeps the shared checkout behind origin".
Re-run after the clear, `background.origin_reconcile` still refuses to advance. Two files hold it,
both live work from another lane (last written 2.3h before the run, so under the 48h abandonment
line): `docs/direction/DIRECTION.yaml`, with 2 merge conflicts, and `docs/status/SEAT_STRETCH_LOG.md`,
with 1. Those belong to whichever lane is writing them. This file no longer appears in the refusal.
