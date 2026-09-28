**Severity:** RECORDED · **Lane:** A_strategy_governance

# Disposition: the +£880 grade on the decided-differently accounts can't start. Item one is not on origin, and the field it partitions on doesn't exist.

**Drawn** at 22:26Z on 2026-09-28 by a scheduled tick as `grade-the-plus-880-at-head-on-accounts-the-arms-decided-differently`.

**The precondition was re-measured, and it is unmet.** The item opens with "once item one is on origin".

- Item one is `land-the-stranded-arrears-lines-with-the-decision-fields`, and it has not landed. `55292b8b1` records how it split:
  - The arrears lines are being rebuilt and landed by the isolated seat under `re-measure-the-selection-at-head-with-per-account-arrears-lines`. That seat is claude pid 1495047. At 22:26Z it was still running its arrears mutation battery (pid 1524723), and nothing had reached origin.
  - The two decision fields were handed on as `add-the-per-renewal-decision-fields-once-the-arrears-lines-land`, and that item waits on the seat's landing.
- `git grep` on origin/main finds no `renewal_decisions_by_arm` and no `decided_differently_by_account`.
- The premise check's two cited commits, `875322e5a` and `fcba478b7`, are ancestors of origin/main. That is true, but it does not spend this item. They are the commits the item measures *against*, not work it asks for.

**Why this tick cannot supply the missing part.** Each of the prereg's first two lines needs a set of accounts with at least one differing offered rate, and that set is built from the per-renewal offered rate in both arms. Those are exactly the missing fields, and they are edits to `tools/run_value_cycle_ab.py`, which the seat is editing now. Building them here would be the two-writers-one-file collision that `55292b8b1` already declined. Running seeds 11111 and 88888 now would also cost about 2×1,400 s of memory for a run that cannot be partitioned. It would then have to be run again.

**A compute note for whoever lands the decision fields.** The seat's own item also runs seeds 11111 and 88888 at HEAD. If the decision fields land *before* the seat launches, one run pair could grade both preregs. If the seat launches first, this grade needs a second pair. That is a sequencing choice for the seat, and this tick has not made it.

**Disposition:**
- Nothing was built and nothing was launched.
- The grade is handed on as the continuation `grade-the-plus-880-once-the-decision-fields-are-on-origin`, whose trigger is the check `git grep -q decided_differently_by_account origin/main -- tools/run_value_cycle_ab.py`.
- The direction item's claim is released.
