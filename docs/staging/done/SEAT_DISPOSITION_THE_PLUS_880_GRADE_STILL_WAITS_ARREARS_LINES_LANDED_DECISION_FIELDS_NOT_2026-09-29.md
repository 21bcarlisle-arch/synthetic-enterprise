# The +880 grade still waits: the arrears lines landed, the decision fields have not


**Severity:** RECORDED · **Lane:** A_strategy_governance

**Item:** `grade-the-plus-880-once-the-decision-fields-are-on-origin` — released without building, as its own precondition directs.

**Measured at draw (2026-09-29, origin/main `8970d037e`):**
- `git grep -q decided_differently_by_account origin/main -- tools/run_value_cycle_ab.py` → **absent**. Not in the shared working copy either (0 matches).
- The arrears lines ARE on origin: `f997f8bf7` "the value-cycle artefact carries each account's arrears lines…". So the blocker recorded in `SEAT_DISPOSITION_THE_PLUS_880_GRADE_WAITS_ON_THE_DECISION_FIELDS_WHICH_WAIT_ON_THE_ARREARS_LINES_2026-09-28.md` has moved one step: only the decision fields remain.
- Origin carries `priced_decision_fingerprint` (a per-seed digest), which is not the per-account partition this grade needs.

**Next:** the live claim `add-the-per-renewal-decision-fields-once-the-arrears-lines-land` is now unblocked and is the item to move. Re-issue this grade once that lands; the prereg (four predictions, seeds 11111/88888, leg 4b at HEAD default) is unchanged.
