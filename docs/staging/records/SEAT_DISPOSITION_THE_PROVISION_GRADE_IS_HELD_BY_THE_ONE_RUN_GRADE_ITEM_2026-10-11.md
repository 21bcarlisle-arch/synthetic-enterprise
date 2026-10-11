# Disposition: the provision grade is already in hand under another id, so this one is released

*Delivery item `grade-the-companys-provision-stock-on-a-run-that-carries-it`, 2026-10-11 13:10 BST.*

**Released, not built.** The draw flagged `the-bad-debt-provision-is-the-companys-own-aged-receivables`
as a possible duplicate. It is not one: that item BUILT the provision (42b2eb254, on origin), and this
item grades it. The real duplicate is a third id the check did not name,
`the-provision-and-the-movers-final-bill-graded-on-one-run-at-head`, held at draw time by a live worker
session (claude pid 3735426, started ~11:54). Its brief grades P1-P6 of
`SEAT_FINDING_THE_PUBLISHED_PROVISION_WAS_THE_WORLDS_INCIDENCE_AND_THE_COMPANYS_OWN_STOCK_WAS_NEVER_READ_2026-10-11.md`
on one run at HEAD, together with the movers' final bill.

That session has already launched the run this item asked for:

* unit `longjob-provgrade-run`, started 12:11 BST, worktree `/var/tmp/se-provgrade` at **dfeb5eb59**
  (which descends from 42b2eb254), running `tools.run_annual_report --save-json
  /var/tmp/provgrade/run_output.json`. At 13:07 its log had reached the 2024-25 periods.
* its grader, `/var/tmp/provgrade/grade_provision.py`, reads `company_provision` and prints P1-P6
  against the finding's own bounds.

This item's brief says to read a run like that rather than launch another one. Building the grade here
as well would give two writers to one Grade section. So this id is released (`delivery_lane --release`).

**If the holder's turn ends before the run does:** the unit is a systemd job and outlives the turn.
Whoever picks the work up runs `python3 /var/tmp/provgrade/grade_provision.py
/var/tmp/provgrade/run_output.json` from `/var/tmp/se-provgrade`, writes the Grade section with
dfeb5eb59 stated beside it, and keeps every miss next to its prediction.
