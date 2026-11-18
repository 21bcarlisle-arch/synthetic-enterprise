**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `DD_seasonal_cashflow_physics`

# Row 7's grade waits for the first book carrying 594ed8239. The grading probe is proven on the book before it (2026-11-17)

*Claim `row7-graded-on-the-first-book-carrying-594ed8239`. This grades the four predictions in
`SEAT_FINDING_ROW_7S_THREE_LEAVERS_ARE_THE_WORLDS_DUE_ONLY_READ_AT_THE_FINAL_BILL_2026-11-17.md`.*

## The premise, re-measured at 22:56Z

- 594ed8239 is on origin/main, and so is d645233e8, the walk file. The shared tree's HEAD (0825afec31) carries both.
  So `book_admission` (`background/next_book_requires.yaml`) now admits a book on the shared tree.
- **No such book exists yet.** The newest run is still `run_output_18f201c5bf_20261117T181948Z.json`. Its re-grade
  at 22:19Z was refused again on `INV_OVERDUE_WITHIN_PAGE_BALANCE 20`, as `ae5bc25924` predicted. Since 22:34Z
  sim-runner has deferred each cycle behind `longjob-value-test-step-6-flag1` (memory). The last run took about
  6,700 s, so a grade cannot come before about 01:00Z on 18 Nov, and only if the long job frees memory by then.
- The item's ask is **not spent**, only not yet answerable. Grading it without a book would mean making up a number.

## The control: the probe reproduces the finding on the 18f201c5bf book

`/var/tmp/row7probe/grade_row7.py` (copied below) wraps the row-7 evaluator so it returns **every** breach. The
publisher's `domain_invariants.json` keeps only five examples. The probe reads the shared tree's
`docs/state/billing_ledger.json` and `site/data/customers`, as the publisher's gate does. On the 18f201c5bf
ledger it prints the finding's own numbers:

| household | steps | overdue printed | page balance |
|---|---|---|---|
| SYN-2016-001 | 2 | 386.23 (15 Aug 2023) | 329.71 |
| SYN-2016-471 | 5 | 38.13 | 28.78 |
| SYN-2016-523 | 5 | 139.33 | 114.05 |
| SYN-2016-546 | 8 | 49.98 | 43.25 |

That is 20 steps, 18 of them the three leavers. Row 4 (`INV_OVERDUE_WITHIN_BALANCE`) is 0 of 978 on the same book.
So prediction 4's baseline is 0, inside its "at most 1".

## How the next draw grades it (one command, run as soon as the book is processed)

1. Check that the ledger is the new book's: `head -c 300 docs/state/billing_ledger.json` names `source_json`. Its
   git must descend from 594ed8239 (`git merge-base --is-ancestor 594ed8239 <sha>`). Grade only after
   `process_run` regenerates the ledger, and before the run after it overwrites the ledger.
2. From the shared tree root, run `python3 /var/tmp/row7probe/grade_row7.py`. If it is gone, re-create it from
   the copy below.
3. Grade the predictions:
   - **P1:** none of SYN-2016-471/-523/-546 appears. Row 7 reads 2 (SYN-2016-001), or another count only if
     001's 15 Aug 2023 lump moved.
   - **P2:** for any new household, compare desk − page with an amount netted off its final bill. Now that
     d645233e8 is in, read that from the walk / final-month-nets file beside the run.
   - **P4:** row 4 in `docs/reports/domain_invariants.json` is at most 1.
   - **P3:** I cannot yet say. It needs move-out collections and level-leaver write-offs on both ledgers. The 18f201c5bf ledger is kept at
     `/var/tmp/row7probe/billing_ledger_18f201c5bf.json`, outside the repo, for a one-on-one comparison.
4. Not predicted, so record it and do not grade it: the closing-refund row (`INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`,
   24, excepted) reads the balance through the credit-bill "waits" rule, which 594ed8239 also changed. Whether it
   moves, and which way: **I cannot yet say.**

```python
"""Every row-7 breach on the shared tree's current ledger + printed pages, grouped by household."""
import json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "/home/rich/synthetic-enterprise")
from tools import domain_invariant_runner as r
ID = "INV_OVERDUE_WITHIN_PAGE_BALANCE"
captured = []
ev, needs = r.EVALUATORS[ID]
def wrap(inv, book, **kw):
    t = ev(inv, book, **kw); captured.extend(t.breaches); return t
r.EVALUATORS[ID] = (wrap, needs)
P = Path("/home/rich/synthetic-enterprise")
led = P / "docs/state/billing_ledger.json"
print("ledger source:", json.loads(led.read_text()[:400].split(',"customers"')[0] + "}")["meta"]["source_json"])
raw = r.load_book(ledger_path=led, printed_path=P / "site/data/customers")
invs = [i for i in r.load_invariants() if i["id"] == ID]
row = r.run(invs, raw)[0]
print({k: row.get(k) for k in ("status", "checked", "breached")})
by = defaultdict(list)
for b in captured: by[b["where"].split()[0]].append(b)
for h, bs in sorted(by.items()):
    print(h, len(bs), sorted({(b["where"].split()[1], b["value"], b["bound"]) for b in bs}))
```

## The next book does not end the wedge, and SYN-2016-001's walk is narrowed, not named (worker, 17 Nov 23:30Z)

- **What the next book means for the wedge.** If P1 holds, row 7 reads 2, not 0. No exception covers row 7, so the
  first book carrying 594ed8239 is **refused again** on `INV_OVERDUE_WITHIN_PAGE_BALANCE 2`. That book's value
  is the walk file (d645233e8), which names the walk SYN-2016-001's lump crossed behind. It does not publish.
  The wedge closes only on a book built after that walk is fixed.
- **When.** sim-runner yields every cycle to `longjob-value-test-step-6-flag1`: 12 churn_roll draws, declared
  3,200 min, about 190 min run at 23:10Z. Its earlier seeds took about 21,000 s each, so the yield can last a day or
  more. It is held on purpose (`sim_runner.cycle_admission`: a cycle once OOM-killed a long job). I did not force a
  cycle beside it, because the book it would buy is predicted not to publish. Whether to pause the value test so the
  diagnostic book comes sooner is the seat's call. It is not a wall.
- **001's 15 Aug, read from the 18f201c5bf pages.** Gas INV21608 (April, raised 3 May) is paid on 15 Aug, the due date
  of gas INV21611 (raised 1 Aug). Electricity follows the same pattern: INV21494 is paid on 17 Jul, INV21496's due
  date, and INV21495 on 16 Aug, INV21497's. So the 56.52 lump is pushed inside INV21611's `record_period`, after
  that call's first delivery. Both desk steps (Consent rung and prepayment withheld) printed 386.23 = 251.89 elec + 134.34 gas, which is the
  start-of-day balance. Code and grader share one convention (`_settle_held` walks to the day **before** a lump),
  so this is a real lump behind a walk. It is not a grader artefact.
- **Ruled out by reading:** (a) a journey advanced outside `_walk`: `advance_collections_journey` has one caller,
  `LivePaymentTriad._walk`, so the counter sees every path. (b) The gas leg dropping out of `legs_still_posting`
  while the electricity term posts: `_pending_starts` is seeded with every term at the start, and a term leaves it
  only when it pops, so an unposted gas term still holds the bound to gas's last due (INV21610's, about 17 Jul).
- **Not ruled out:** a walk whose bound already counts gas INV21611's 15 Aug due date, made before that call pushes
  the INV21608 lump. Candidates are the reader `_deliver_settlements_through(.., force=..)` →
  `_settle_held` for another held lump on the account dated after 15 Aug, and the `record_period` walk itself. Which
  one: **I cannot yet say.** The walk file's `rows` for `ACC-SYN-2016-001`, `settled_on` 2023-08-15, names it.

## Re-measured at 23:25Z: still no book, and the seat will not pause the value test for one (delivery seat, 17 Nov)

- `docs/state/billing_ledger.json` on the shared tree still names `run_output_18f201c5bf_20261117T181948Z.json`, and it
  is still the newest `run_output_*`. sim-runner logged `DEFERRED` at every 5-minute cycle from 23:00 to 23:20Z,
  each time behind `longjob-value-test-step-6-flag1` (196 of 3,200 declared minutes). Nothing has been graded. The
  probe was not re-run, because it would only print the 18f201c5bf numbers already in the table above.
- **Decision: do not pause the value test to get this book sooner.** The book is predicted to be refused on row 7's 2,
  so it cannot unwedge the publish. Its only value is the walk file that narrows SYN-2016-001's lump. Pausing would
  throw away about 3 hours of a run that answers a step-6 question. That run is the scarcer thing. This is reversible
  and is the seat's call, not the director's.
- The grade is handed on with a dated draw embargo, so the pool stops re-offering it every turn before a book can
  exist. The steps in "How the next draw grades it" are unchanged.

## SYN-2016-001's walk is named by reading, and fixed: a delivery walked past its own `through` (worker, 17 Nov 23:50Z)

- **The walk.** The candidate was `_settle_held` for another held lump on the account dated after 15 Aug, and that is
  the one: electricity INV21495's lump, paid **16 Aug**. In gas INV21611's `record_period`, the 15 Aug gas lump is pushed
  to the queue, then `_leg_last_due[gas]` moves to 15 Aug, then the call delivers through gas's **previous** due
  (about 17 Jul). That delivery only moves lumps dated up to 17 Jul out of the queue, but `_settle_held` walked as far
  as `_walk_bound`, which now reads 15 Aug. So it walked to 15 Aug to cross the held 16 Aug lump, with the gas cash
  still queued. The desk stepped 15 Aug on 386.23, and the gas lump crossed behind the walk. This needs electricity's
  term to post before gas's (whole terms post in turn), so electricity's 16 Aug lump is already held.
- **Fix.** `_deliver_settlements_through` caps each `_settle_held` at its own `through`. Every queued lump dated up to
  that day has left the queue, so no walk can step a day whose cash is still queued. Held lumps past `through` wait
  for the next delivery, which is that leg's next `record_period`. The test that reproduces it is
  `tests/background/test_a_lump_crossing_behind_the_desks_walk_is_counted.py::test_a_delivery_does_not_walk_past_a_lump_still_queued_for_its_own_day`.
  It reds without the fix and is green with it.
- **Prediction, filed before any book carries it (P5).** On the first book carrying this commit and 594ed8239, row 7
  (`INV_OVERDUE_WITHIN_PAGE_BALANCE`) reads **0**, and the walk file's `count` for `settle_held` is 0. If 001's 15 Aug
  still breaches, this reading is wrong. In that case the walk file's `walked_by` for `ACC-SYN-2016-001` on
  2023-08-15 names the walk. A book built on 594ed8239 alone still reads 2, as P1 says.
- **Not predicted:** other counts that read held-lump timing (`crossed_despite_a_plan`, the excepted closing-refund
  row) may move. Forced reader crossings can now come before a walked one. Which way they move: **I cannot yet say.**

## The 23:25Z "do not pause" premise no longer holds, so step 6 pauses at its pair-3 boundary (worker, 18 Nov 01:42Z)

- **What changed.** 23:25Z declined to pause the value test because the next book was predicted refused on row 7's 2.
  20d4cbeccc (01:38Z) fixes those 2, and P5 predicts row 7 = 0 on the next book. So that book is now the predicted
  unwedge, not a diagnostic one. The shared tree carries 594ed8239 and 20d4cbeccc, and `background/live_payment_triad.py`
  matches HEAD.
- **Cost of the pause: none of the draw work.** The driver skips any pair whose member and control files are on disk.
  Pair 3 (`55555_66666`) started at 20:04Z and pairs take about 21,000 s, so it lands at about 02:00Z.
- **Armed:** `row7book-pause-watch` (`/var/tmp/row7book-pause/watch.sh`, log `watch.log` beside it). It is the
  `d5book-pause-watch` script with pair 3 in place of pair 2. It stops step 6 once pair 3 is on disk, waits for a new
  `docs/staging/run_complete_*.md` (at most 8 h), and then relaunches step 6 with its original arguments. Step 6 is
  never stopped mid-pair. If the unit ends first, the watcher exits without touching anything.
- **REVERSE:** `systemctl --user stop row7book-pause-watch`. If step 6 is already stopped, run the relaunch block in
  watch.sh by hand.
- Grading is unchanged: the steps above, P1 and P5 on the book, when it lands.

**18 Nov 02:30Z (claim `row-7s-last-two-and-the-verified-publish`).** The last 2 are named and fixed by 20d4cbeccc.
The writer is `_deliver_settlements_through`, which let `_settle_held` walk past the delivery's own `through`.
The fix is in `background/live_payment_triad.py`, which the world run calls (`simulation/run_phase2b.py`), so no
re-grade of the 18f201c5bf output can clear them. Only a new book can. 20d4cbecc is now a row in
`background/next_book_requires.yaml`, so a book built without it is deferred. Path to the publish: flag1-stop-at-pair3-watch
frees the box → sim-runner builds the owed book → `process_run` → grade P1–P5 with the probe above (P5: row 7 = 0)
→ the publish gate verifies. Nothing on that path waits on the director.

**18 Nov 02:40Z (claim `row7-graded-on-the-first-book-carrying-594ed8239`, executor draw). Still no book, so nothing is graded.**
`docs/state/billing_ledger.json` on the shared tree still names `run_output_18f201c5bf_20261117T181948Z.json`, and that is
still the newest dated `run_output_*`. Pair 3's driver (pid 1051692, `--child 55555,66666`) is 6 h 33 min in at 98% CPU
and about 7.2 GB RSS. That is past the about 21,000 s a pair took before, so the 02:00Z ETA has slipped, but the driver
is still working. `control_55555_66666.json` is not on disk yet. `flag1-stop-at-pair3-watch` has been waiting since
02:08Z. The owed book still needs pair 3, then about 6,700 s of sim-runner, then `process_run`, so a grade cannot come
before about 05:00Z. The probe was not re-run, because it would only print the table above again. The grade is handed on
with a dated embargo. The steps in "How the next draw grades it" and P1–P5 are unchanged.

**18 Nov 03:56Z (claim `the-book-carrying-all-three-row-7-fixes-is-graded-and-published`, executor draw). Still no book, so nothing is graded.**
The newest `run_output_*` is still `run_output_18f201c5bf_20261117T181948Z.json`, and so is the ledger's `source_json`. The newest
marker is still `run_complete_20261117T181948Z.md`. `site/data/publish_provenance.json` on origin is still paused (`paused_since`
2026-11-16T04:26:22Z, `last_verified` 6fe7827ab2). Pair 3's driver (pid 1051692) has run 7 h 44 min of CPU at 98% and 7.5 GB RSS.
`control_55555_66666.json` is not written yet. Pair 2 (`33333_44444`) wrote at 17 Nov 17:40Z, so this pair is now about 2 h past the
roughly 21,000 s pairs took before. It is still working, not hung. `flag1-stop-at-pair3-watch` has been waiting since 02:08Z, and sim-runner
logged `DEFERRED` at 03:47Z and 03:52Z behind it. Following the item, I did not pause flag 1. The earliest possible grade is now pair 3,
plus about 6,700 s of sim-runner, plus `process_run`. That is about 07:30Z at the soonest. The grade is handed on with a dated embargo.
The steps above and P1–P5 are unchanged.

**18 Nov 07:55Z (claim `the-book-carrying-all-three-row-7-fixes-is-graded-and-published`, executor draw). The owed book is building. It is not graded yet.**
Pair 3 of flag 1 wrote `control_55555_66666.json` at 06:57Z. sim-runner (pid 3731606) started at 07:02:21Z and is writing
`docs/reports/run_output_6af7fd0bfd_20261118T070221Z.json`. 6af7fd0bfd carries 594ed8239, d645233e8, 20d4cbecc and f4f825b8b
(checked with `merge-base --is-ancestor`). So this is the book P1–P5 grade. At 07:53Z it was in March 2023 of the run, 51 min in. With the
last run at about 6,700 s, it ends at about 08:55Z, and then `process_run` runs. The ledger still names 18f201c5bf. Origin's
`publish_provenance` is still paused (`paused_since` 2026-11-16T04:26:22Z, `last_verified` 6fe7827ab2). Flag 1 was not touched.
The grade is handed on with an embargo on `docs/staging/run_complete_20261118T070221Z.md`. The steps above and P1–P5 are unchanged.

## GRADED on book 6af7fd0bfd (run_complete_20261118T070221Z), 18 Nov 09:05Z (claim `the-book-carrying-all-three-row-7-fixes-is-graded-and-published`)

The book finished at 08:45:36Z. Its producing commit, 6af7fd0bfd, descends from all seven `next_book_requires.yaml` rows
(157e05c23, fc3129a86, 163bf831a, 586e304ce, 341df4965, 594ed8239, d645233e8; checked with `merge-base --is-ancestor`).
`process_run` regenerated `docs/state/billing_ledger.json` at 08:49Z (`source_json` = this run) and the printed pages at 08:49Z.
Flag 1 was not touched.

**(a) Row 7, `INV_OVERDUE_WITHIN_PAGE_BALANCE`: 20 → 0, as predicted.** The probe (`/var/tmp/row7probe/grade_row7.py`) on the
new ledger and pages reads `CLEAN, checked 6115, breached 0`. The publisher's own `docs/reports/domain_invariants.json`
(git 6af7fd0bfd) says the same. At 08:58Z the gate logged `Domain invariants: 0 unexcepted breach(es) across 0 invariant(s);
8 excepted. ENFORCED: nothing unexcepted, so the publish stands.` The refusal of the last 59 cycles is gone.
- P1 **held**: none of SYN-2016-471/-523/-546 appears (no household appears at all).
- P5 **held**: row 7 = 0, which also clears SYN-2016-001's two steps.
- P4 **held**: row 4 (`INV_OVERDUE_WITHIN_BALANCE`) is 0 of 975, inside "at most 1".
- P2: not exercised, because no new household breaches. Not counted.
- P3: still **I cannot yet say**. Not counted.
- Not predicted, recorded only: the closing-refund row (`INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`) stays at
  24 of 132, excepted. It did not move.

**(b) The walk file** (`docs/reports/world_walk_truth_6af7fd0bfd_20261118T070221Z.json`). `settlements_behind_the_walk.count`
is 1, `by_walk` is `{record_period: 1}`, and **`settle_held` is 0**, so the second leg of P5 **held**. ACC-SYN-2016-001's
2023-08-15 settlement is **not** behind the walk any more. The one remaining row is ACC-OCC-731d3b63ba00 (leg -g, settled
2017-08-21, GBP 27.42, walked through to 2018-02-20 by `record_period`). It is a different leg on a different path. The row
is not predicted, so it is recorded and not graded. `later_settlements`: delivered 1,452, withdrawn 0, crossed_despite_a_plan
0, lost_at_close 22, already_cleared 2, cut_to_balance 8, crossed_after_close 1. `missing` is empty.

**(c) The account page's repayment shortfall against the world's cash: 194 legs / GBP 6,399.16 → 0 legs / GBP 0.00.**
Reader: `/var/tmp/repay-truth/measure.py` (the 10 Nov definition: T is the world's repayment cash, P is what the page posts,
dated on or before the book date of 2025-07-04). On this book: 368 legs carry a repayment. T is GBP 91,842.60, P is
GBP 91,842.60, and the page differs from the cash on **no** leg in either direction. The output is kept outside the repo at
`/var/tmp/row7grade/repay_6af7.json`.
`final_month_nets` beside it has 259 legs, 136 of them ever level. 81 of them netted ledger credit off the final bill, for
GBP 1,520.13, and 20 final collections failed. **Not explained here:** the same reader puts the *engine's* walk credits (E,
kind `repayment`) **short of the cash by GBP 6,647.57 on 137 legs**, with none over. The page now posts the cash and not
the engine's figure, which is why page against cash reads 0. Whether the 137 are the final-month nets, or the engine
recording a settlement under another kind: **I cannot yet say.** That is the next piece, below.

**The publish of this book was refused, but not on row 7.** The domain-invariant gate and the pytest publish gate both
passed. Provenance stamped `Verified 2026-11-18T09:20:49Z` for this run. The commit was then refused at 09:43Z by the
site lane in the hook chain (`process_run` log: `Publish commit REFUSED by the hook chain -- blocking test(s)`), on two
`site/**` tests:
1. `site/explore/test_a_catch_up_bills_vat_is_the_vat_of_the_lines_above_it.py::test_inv5940_...` failed with
   `KeyError: 'OCC-a097d0031a9f-INV5940'`. Invoice numbers are minted per book, and the same April 2023 catch-up bill
   (catch-up GBP 21.57) is INV6447 in this book. The control was keyed to the answer of the day, not the bill.
   **Fixed in this landing:** the test now finds the account's April 2023 bill by its period. Green on both books (the
   16 Nov extract in git, and this book's file). The old version is red on this book, as the gate's own record shows.
   The class test beside it (every catch-up bill, at least 100 of them) already held the property. This was the
   instance pin.
2. `site/test_no_published_page_renders_an_empty_field.py` failed on `harness/index.html`, which printed "...the
   survivor tier is undefined..." and "...A run with S5 undefined...". That is English prose, but it matches the
   detector's `\bundefined\b`. **Not reproducible now:** with the shared tree's `delivery.json` (regenerated 09:28Z),
   `proof.json` and `director_delta.json` staged, the test passes 3/3. The phrase exists nowhere on disk or in git now,
   except as a quotation inside a decision row's `landing_refused` (`decisions.jsonl`, 06:21Z), which shows the seat hit
   the same red at about 06:2xZ. Its source prose: **I cannot yet say.** It is transient, so no fix is landed for it.
   If it recurs, the place to look is the feed `harness/index.html` renders at the moment of the publish commit.
- The worker re-armed the marker at 09:47:44Z, and `process_run` (pid 209102) re-attempts this book. Its fast-forward
  onto origin happens just before its commit, so this fix reaches it if it lands first.

**10:05Z: both reds are answered on origin, and the book is re-offered by hand.**
- Correction to "no fix is landed for it" above: another lane landed 22639d0ad ("The empty-field sweep counts
  'undefined' as a leak only when a script made it"). That fixes the second red as a class.
- The worker's one automatic re-attempt (09:47Z) fast-forwarded onto 49d41097b, which carries the INV5940 re-key, and
  was then refused at 10:03Z without running a test. origin had moved to 22639d0ad between its fast-forward and its
  commit, and the primary-checkout guard refuses a commit on a stale base. That is a race, not a red.
  `refused_marker_to_rearm` re-attempts a marker only once, so nothing would offer this book again.
- So I re-drove it by hand, as the 13 Oct and 19 Oct refusals were: `process_run_complete.py
  docs/staging/done/run_complete_20261118T070221Z.md`, pid 274211, started 10:03Z, log `/var/tmp/row7grade/rerun.log`.
  `/var/tmp/row7grade/rerun.done` is written when it exits.
- **Prediction (filed before the answer):** domain invariants are 0 unexcepted again, the pytest gate is green, the site
  lane is green, and the commit lands unless origin moves inside its commit window again. Then origin's
  `publish_provenance.json` has `last_verified.git_commit` = 6af7fd0bfd and no `paused_since`.
