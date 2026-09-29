**Severity:** RECORDED · **Lane:** H_harness · **Atom:** none (Lane 0 delivery)

# DISPOSITION: the tick worker drew `fold-home-move-successors-into-the-decided-set-as-a-labelled-diagnostic` while the seat was landing it

**What happened.** The tick drew this item at 15:47 BST. The duplicate-work note said the claim was held under the same id, and the claim's `claimed_at` was 115 s old, so the worker read it as the draw's own write. That was wrong: the seat executor (pid 558475) was building the same item in `/var/tmp/se-seat-executor`. At 15:51 the seat started `surgical_land` (pid 569022) with `tools/run_value_cycle_ab.py`, the arrears reconciliation test, a new successor test and a SEAT_RECORD.

**What the worker built, and then withdrew.** The worker added `successor_of` plus `activated_by` to `_decisions_by_billing_account`, taken from the run's `company_event_log` acquisitions, and a mutation-proven test. The edits were in the shared tree. It also added a fold line to `/var/tmp/se-ab5-out/grade5.py`. That fold also swept successors present in both arms (C3_2 on both seeds). The seat's fold is roster-only, which is the right partition: a successor in both arms was not caused by the arms deciding differently. The worker restored both shared-tree files to HEAD bytes and put the grader back to the seat's version. Nothing from the worker lands.

**One design difference stays open.** The worker's version also stamped market replacements (`channel: market-acquisition`). The seat's version reads `supply_book.successor_supply_points` and folds home-move successors only, and it names market replacements as not established. A market replacement is also causally downstream of the churn that the arm's price caused. Whether it belongs in the decision's fold is a real question, but it is not settled here.

**The mechanism gap.** The draw's duplicate-work note already has a rule for telling the draw's own write from another writer: `claimed_at` seconds old and identical in both stores. That rule did not separate them here, because the seat's claim and the draw's stamp coincided. `ps` for a rival `surgical_land` before building is what actually shows it.

**Disposition:** `--release` this id from the tick worker. The seat's landing is the one of record: `38a181221`, gated and committed in `/var/tmp/se-seat-executor` at 15:55 BST, not yet on origin/main when this was written. Pushing it is the seat's job.
