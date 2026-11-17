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
