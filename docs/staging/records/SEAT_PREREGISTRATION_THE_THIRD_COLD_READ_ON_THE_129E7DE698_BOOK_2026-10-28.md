**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the third cold read, on a fresh full run at 129e7de698, per row, per slot and for the read (2026-10-28)

**Item:** `the-third-cold-read` (Lane 0, the exit test of
`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). **Status:
filed after the launch and before any output.** The run is still waiting on another job's memory.

## The gate the item sets, read at origin 129e7de698 (17:54 GMT)

| precondition | on origin |
|---|---|
| item 1, the desk fix graded on a fresh run | yes: `dd42166183` |
| item 2, the second cold read's classes become rows | yes: `6bdf089925` (six rows, graded on the 1a02c46116 book) |
| continuation `the-successor-page-carries-its-predecessors-meter-point` | yes: `971a37583c` |
| item 3, W2_36 opening read | not on origin. Not waited for: INV_OPENING_READ is reported as flagged, with its GAP |

**Item 1's book is not used.** It was run at `b2fc50facf`. Since then two commits touch run-side code:
`971a37583c` (`company/crm/customer_registry.py`, meter points minted from the supply point) and
`6bdf089925` (`company/billing/unread_month_estimate.py` and `monthly_bill_assembly.py`, a zero-kWh
window establishes no estimate). So one fresh run was launched at origin HEAD:

- `launch_long_job`, job `fresh-run-129e7de698`, worktree `/var/tmp/fresh-run-wt-129e7de698`,
  script `/var/tmp/fresh-run-scripts/arm.py`, output `/var/tmp/fresh-run-out-129e7de698`, at 17:55 GMT.
- It waits on pid 3070363 (a 4 GB `tools.run_annual_report`) so that nothing heavy runs beside it.

## The baseline, measured before this file and on no output of the new run

This is item 1's book (`/var/tmp/fresh-run-out-b2fc50facf`), graded with origin 129e7de698's runner,
rows and exceptions. The harness is `/var/tmp/third-read-scripts/grade.py`: the 6bdf089925 grade's
harness, with the page records built in memory from the ledger. The output is
`/var/tmp/third-read/baseline_b2fc_full.{txt,json}`. It reads **0 unexcepted, 11 excepted**, and every
excepted count equals its ceiling.

**One variable, separated first.** The b2fc50facf ledger rebuilt with 129e7de698's code
(`/var/tmp/third-read/b2fc_ledger_at_head.json`) grades identically in every row. So the ledger build
moves nothing, and any count that moves on the new book moves because of the two run-side commits.

## Predictions, per row

The account count is 1,293 ± 1%.

**Rows CLEAN or UNREACHED on the baseline stay at 0 breaches.** There are 27 of them (26 CLEAN, 1 UNREACHED), and the
row-by-row list is in `baseline_b2fc_full.txt`. The four UNCHECKABLE rows stay UNCHECKABLE.

| row | baseline | prediction |
|---|---|---|
| INV_UNIT_RATE_FIXED | 8 flagged | 0–20 flagged, 0 breached |
| INV_ANNUAL_USE_ELEC_ACCOUNT | 6 flagged | 0–15 flagged |
| INV_READ_DUTY_ANNUAL | 27.7% flagged | 20–35% |
| INV_SETTLEMENT_ACTUAL_SHARE_ELEC | 1 of 1 flagged | 1 of 1 |
| INV_OPENING_READ | 1,293 of 1,293 flagged | **every account flagged.** GAP: no typed opening read exists in the record until W2_36 lands |
| INV_DD_CADENCE | 59 flagged | 30–120 |
| INV_DD_STEP_CHANGE | 4.5% flagged | 3–7% |
| INV_BACK_BILLING_12M | 147 flagged | 80–250 |
| INV_SERIAL_REGISTER_COUNT_STABLE | 2 flagged | 0–5. `971a37583c` re-mints serials from the supply point, and I cannot say the direction |
| INV_MPAN_CORE_FORMAT | CLEAN, 707 | CLEAN. The checked count may fall, because successors now share their predecessor's core |
| INV_PPM_NOT_CREDIT_BILLED | 12 (C6, SME) | 12, all C6 |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | 6 | 3–6 |
| INV_EBSS_CREDIT_ON_THE_BILL | 6 | 3–6 |
| INV_OVERDUE_WITHIN_BALANCE | 0 | 0 |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | 3 | 0–5 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 9,455 | 8,980–9,930 (± 5%). Direction unknown |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 288 | 260–316 |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | 181 | 155–210 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 10 | 0–12 |
| INV_SMART_METER_BILLED_ON_ITS_OWN_READS | 4 | 4 (C2) |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 292 | 250–335 |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 11 | **at most 2.** 6bdf089925 says 10 of the 11 are occupier zero windows fixed run-side; this is the row the new run exists to move |

**The risk to leg one I can name in advance.** Every exception ceiling equals the last measured count
exactly, and the run is deterministic where the code did not change (288, 181, 10, 4, 292 and 11 are
identical on the 1a02c46116 and b2fc50facf books). The estimate fix changes the bills on some legs,
so every row that grades bills can move by a few either way. **A count one above its ceiling is an
unexcepted breach.** I predict that at least one of the eight bill-graded excepted rows rises above
its ceiling, at about even odds, and that any such rise is attributable to `6bdf089925`'s re-estimated
legs. I will check that by account, not assume it.

**Leg one: predicted MET at about even odds.** It is MET if no row exceeds its ceiling, or if every
row that does has its rise traced to a named cause in this turn.

## Predictions, the eight Explore slots (leg two)

The pages and the cast are rebuilt into `/var/tmp` from origin's tools, by the second read's route
(`/var/tmp/second-cold-read-scripts/build_run_output.py`, then the publisher's chain in
`process_run_complete` order).

| slot | prediction |
|---|---|
| switch_in, renewal, estimate_trap, debt, shock_2022, ev | filled, by the same households as the 1691ec0ecd cast, unless the estimate fix moves a bill they rank on |
| mover | **filled** (SYN-2016-417 on 1691ec0ecd, by d70e32cd5). It is the first time a blind reader sees it |
| storage_heating | empty, with its named check (no profile class 2 meter) |

**Leg two: predicted MET** (seven filled, one honestly empty), unless the reader shows a filled slot's
example is invalid. If the reader does, the grade is NOT MET whatever the generator says.

## Predictions, the cold read (leg three)

**The method** is ruling step 6, run the way the second read ran it. Each tab of the cast is rendered
and captured. **Six households** are drawn with `random.Random(20261029).sample` from the page's
picker, with the first and second reads' twelve households removed first. A fresh agent reads only the
packet, with no code access. It is briefed as a GB retail-energy professional and writes its priors
first. The seat checks the agent's quotes against the packet.

- **Leg three: predicted NOT MET.** I predict at least one new class: one outside the first read's
  37 objections, the second read's N1–N7, and the suite's rows. The class count went 37, then 7. Two
  places have not yet been read blind: the newly filled mover slot (a final bill and a successor
  account), and the six rows' fixes as printed. I name the mover slot's final bill and closing
  balance as the likeliest home of a new class, so a hit anywhere else counts as a miss on location.
- I predict 20–45 objections in total.

## What done means

The run graded unedited against each prediction above, the pages and cast rebuilt, the read taken,
and a reading in `docs/staging/` that grades each of the three legs MET or NOT MET with its evidence.
A new class keeps the stretch open, and the reading says so.

## Results, graded unedited against the predictions above (2026-10-28, item `the-third-cold-read`)

The book is `fresh-run-129e7de698`, which exited cleanly at 19:42Z after 4,255 s
(`/var/tmp/fresh-run-out-129e7de698/DONE.json`). It was graded with `/var/tmp/third-read-scripts/grade.py`
from the run's own worktree, so the code is 129e7de698's. The output is
`/var/tmp/third-read/grade.{txt,json}`. Nothing above this section has been edited.

**Accounts: 1,293.** Held.

**The 27 rows that were CLEAN or UNREACHED on the baseline: all still at 0 breaches.** Held. Two of
them have a checked count that moved by 2 (INV_OVERDUE_WITHIN_BALANCE and
INV_COLLECTIONS_EVENTS_ORDERED, 7,374 → 7,376 journeys). **The four UNCHECKABLE rows are still UNCHECKABLE.** Held.

| row | predicted | measured | verdict |
|---|---|---|---|
| INV_UNIT_RATE_FIXED | 0–20 flagged, 0 breached | 8 flagged, 0 breached | held |
| INV_ANNUAL_USE_ELEC_ACCOUNT | 0–15 flagged | 6 | held |
| INV_READ_DUTY_ANNUAL | 20–35% | 27.7% (313 of 1,130) | held |
| INV_SETTLEMENT_ACTUAL_SHARE_ELEC | 1 of 1 | 1 of 1 | held |
| INV_OPENING_READ | every account flagged | 1,293 of 1,293 | held |
| INV_DD_CADENCE | 30–120 | 59 | held |
| INV_DD_STEP_CHANGE | 3–7% | 4.5% (1,570; it was 1,575) | held |
| INV_BACK_BILLING_12M | 80–250 | 147 | held |
| INV_SERIAL_REGISTER_COUNT_STABLE | 0–5 | 2 | held |
| INV_MPAN_CORE_FORMAT | CLEAN | CLEAN, 707 checked (unchanged) | held |
| INV_PPM_NOT_CREDIT_BILLED | 12, all C6 | 12 | held |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | 3–6 | 6 | held |
| INV_EBSS_CREDIT_ON_THE_BILL | 3–6 | 6 | held |
| INV_OVERDUE_WITHIN_BALANCE | 0 | 0 | held |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | 0–5 | 3 | held |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 8,980–9,930 | **9,510, over its 9,455 ceiling** | held (the range). The ceiling breach is the risk named above |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 260–316 | 285 | held |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | 155–210 | 181 | held |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 0–12 | 10 | held |
| INV_SMART_METER_BILLED_ON_ITS_OWN_READS | 4 | 4 | held |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 250–335 | **249** | **refuted, by one.** The fix removed more than I allowed for |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | **at most 2** | **1** | **held.** 6bdf089925 moved the row it was run to move |

**"At least one of the eight bill-graded excepted rows rises above its ceiling, at about even odds":
held.** One row did: INV_OVERDUE_WITHIN_PAGE_BALANCE, 9,455 → 9,510. The gate printed **9,510
unexcepted, ENFORCED: the publish is refused.**

**The rise, by account.** `/var/tmp/third-read/all_{b2fc,new}_INV_OVERDUE_WITHIN_PAGE_BALANCE.json` hold every
breach on both books. The net +55 is +127 steps that breach only on the new book and −72 that
breach only on the old one, across 21 households. Three of those households carry most of it:
SYN-2016-434 (+43), SYN-2016-253 (+39) and SYN-2016-023 (−25).
- On 20 of the 21 households, at least one leg's printed bills changed between the books. 164 legs
  changed in all, which is what `6bdf089925`'s zero-window estimate fix does. Since the desk is posted the issued bill,
  a changed estimate re-prices the desk's ask.
- **What does not close.** The desk's journeys changed on 530 legs, more than three times the 164
  whose bills changed. One of the 21, SYN-2016-388 (+2), has no changed bill
  on any leg. So **I cannot yet say** whether the whole +55 is the
  estimate fix. Some of it may be `971a37583c`'s meter-point change, or desk drift the bills do not
  show.

**Leg one: predicted MET at about even odds. Measured NOT MET**, on either reading:
- the gate refuses at 9,510;
- under the item's stricter reading, an exception whose reason names an open defect is
  unexplained, and every one of the ten excepted rows names one.

Leg two (slots) and leg three (the read) are graded in the reading:
`docs/staging/records/SEAT_READING_THE_THIRD_COLD_READ_ON_THE_129E7DE698_BOOK_2026-10-28.md`.
