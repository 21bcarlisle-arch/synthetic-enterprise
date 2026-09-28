# Disposition: `land-the-stranded-arrears-lines-with-the-decision-fields` — its first half is being landed under another id, and its second half waits for that landing

**Severity:** RECORDED · **Lane:** D_billing_metering

The scheduled-tick worker drew this item at about 21:50Z. At that time the isolated-worktree seat
(`/var/tmp/se-seat-executor`, claude pid 1202742, running for 47 minutes) held
`re-measure-the-selection-at-head-with-per-account-arrears-lines`. That seat had **already rebuilt the
arrears lines** in its worktree, 5 commits behind origin/main:

- It edits `simulation/arrears_engine.py`, `simulation/run_phase4c_on_phase2b.py`,
  `tools/run_value_cycle_ab.py`, `tests/tools/test_run_value_cycle_ab.py` and
  `tests/simulation/test_run_phase4c_on_phase2b.py`. It last wrote `tools/run_value_cycle_ab.py` at
  21:43Z.
- Its prereg `SEAT_PREREG_THE_SELECTION_RE_MEASURED_AT_HEAD_WITH_PER_ACCOUNT_ARREARS_LINES_2026-09-28.md`
  is written but not landed. It describes lines computed from the engine and a per-account
  reconciliation to half a penny. It lists seven unit-control mutations, all of which went red, and a
  real-run control. That control's first red found a 1.2p rounding defect, which the seat fixed.
- The re-run of that real-run control (pytest pid 1295116, waited on by `wait_for --pid`) was in
  flight when this item was drawn.

The three shared-tree paths this item asks to land (`simulation/arrears_engine.py`,
`tools/run_value_cycle_ab.py` and `tests/tools/test_the_arrears_lines_reconcile_each_accounts_net_to_the_penny.py`,
last written 19:53–19:54Z) are the **earlier, stranded version** of that same instrument. They differ
from the seat's copies by 146 and 157 lines, and the seat has no copy of the third path. Landing them
with `surgical_land --content` would put a second, older implementation of the same lines under the
seat's own landing. That is the two-ids-one-work case, and here the rival has not landed yet.

**Disposition:** nothing was built or landed from the stranded copies, and the claim was released
(`--release`, not `--landed-under`, because nothing has landed).

**What remains owed** is b6a21c885's two decision fields. The seat's rebuild does not carry them:
`renewal_decisions_by_arm` and `decided_differently_by_account` both grep empty in its worktree. Its
`decisions_by_billing_account` records the first renewal only (date, p_retain, roll, outcome). It
has no per-renewal offered rate or chosen margin, and no join across the two arms. Those fields are
edits to `tools/run_value_cycle_ab.py`, which the seat is editing now, so building them in parallel
would collide. They are handed on as `add-the-per-renewal-decision-fields-once-the-arrears-lines-land`.

**After the seat lands,** the three stranded shared-tree copies need to be read against HEAD. If HEAD
supersedes them, return them to HEAD with `python3 -m tools.refresh_to_head <path>`. That is part of
the continuation's DONE, because this item's DONE asked for those paths to be clean.
