**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The three Lane 0 rows the brief listed as drawn and not landed were already disposed when this item was drawn (2026-11-14)

**Item:** `lane-0-not-done-rows-bound-to-where-their-work-landed`. **Premise: spent.** I re-measured it
against the draw ledger (`docs/observability/.delivery_lane_claims.draws.json`) and
`delivery_lane.drawn_without_landing()` at about 16:10Z on 14 Nov. Every disposition the item asked
for was already recorded:

| Row | Ledger state at draw | In the drawn-never-landed block? |
|---|---|---|
| `the-seat-executor-worktree-commits-reach-origin` | landing bound at 14:14Z: cfd1b980c's 3 paths, after the 12:19Z draw. 31a49789f is the same salvage re-landing's first half, on origin | no |
| `offbox-deadman-cadence-check` | `premise_spent` recorded at 16:02Z, commit 1f3b88e87, citing the director's 14 Nov 05:57 ruling ("6 hrs is fine") | yes, as `premise_spent`, until its 22:02Z draw leaves the 24h horizon. It is not counted as undisposed |
| `the-final-bill-issue-day-has-one-home-beside-bill-due-date` | landing bound at 01:14Z: 69866925b's 5 paths, after the 23:06Z draw | no |

**One credit is wrong, and the tool will not let it be corrected.** 69866925b is S6b: a repayment is
money in on its cash day. That is the sibling defect, not this item. The issue-day work
(`bill_issue_date` as the one home of reg 6D's refund-clock day) is **ceeefa596**. It reached origin
through merge 99c8e05dd at 22:57Z on 13 Nov, nine minutes before the item's last draw. So the honest
disposition of that last window is premise-spent on ceeefa596. `--premise-spent` refused to record it:
"already holds a landing at or after its last draw -- it DELIVERED, and premise-spent is the weaker
fact". The row reads as delivered, and that outcome is right. Only the evidence it names is the wrong
commit. Left as-is: no reader acts on it differently.

**Reverse:** delete this file.
