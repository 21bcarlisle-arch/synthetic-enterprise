**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `payments-and-direct-debit` -- `docs/market_research/payments_and_direct_debit_2026-10-25.md` "What is owed"

# A level DD journey cures when the next instalment is collected, but the missed one is never made good (2026-11-09)

**Found by.** The desk-cure ledger leg pre-registered on the level-DD finding (`SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_SO_ITS_PAGE_PRINTS_OVERDUE_WHILE_IN_CREDIT_2026-11-07.md`,
"Added pre-registration leg"). It said that if the leg failed it would become its own finding. It failed on the first
two books carrying step 2b (a3136e29fa). The grade is on that finding, in the section "The desk-cure ledger leg and the
BSCP504 rows on the step 2b books".

**The trace (298149a1fc book, `/var/tmp/grade-2981/ledger.json`).** SYN-2016-549's electricity pays a GBP 45 level DD.
- 4 Apr 2018: the instalment fails. On 5 Apr the desk opens a journey, overdue GBP 45.
- 4 May 2018: the next instalment, GBP 45, is collected. The desk cures the journey ("overdue balance cleared on the
  ledger", overdue 0).
- The failed April GBP 45 is never collected again. Invoice 50827 is still outstanding at GBP 45 at run end (4 Jul 2025).
- The pattern repeats: 4 Sep 2018 fails, the desk opens, then cures on 26 Nov. The 4 Sep and 4 Oct failures are still
  outstanding at run end (GBP 45 and GBP 90).
- The household then leaves level DD for standard credit. The desk cures 27 later journeys while those failed
  instalments are still on the page.

Ofgem's letter of 20 Sep 2011 (App. 2 para 2.8, quoted on the knowledge page) says a DD customer who defaults on a
payment is in debt. Collecting May's instalment does not make good April's. **The desk's cure seems to read the shortfall
for the current period, not the shortfall carried forward against the schedule.** That is the hypothesis. I have not
yet traced it in `company/` code.

**Size, on the 298149a1fc book** (the reader is `/var/tmp/grade-84f7-ledgerleg/split.py` with level legs capped at the
schedule shortfall; the split is `/var/tmp/grade-2981-cure/compose.py`; output in `/var/tmp/grade-2981-cure/`):

| Shape at the cure | Cures held over a debt | Accounts |
|---|---:|---:|
| Level DD at cure, and an invoice due by the cure is still unpaid at run end | 88 | 43 |
| Level DD at cure, and nothing due by the cure is unpaid at run end | 104 | 83 |
| Left level DD, and an invoice due by the cure is still unpaid at run end | 151 | 19 |
| Left level DD, and nothing due by the cure is unpaid at run end | 3 | 1 |
| Never on level DD | 1 | 1 |

The 88 and the 151 fit the hypothesis: the debt never goes away. **The 104 I cannot yet say.** The reader was written
before step 2b. It measures a level leg's shortfall from invoice-keyed level payments, so it may be counting a
seasonal debit that step 2b's schedule does not owe.

**Not the cause:** two schedules. On this book `only_post_loop` is 0 and `differ` is 0.2% (the level-DD finding's
298149a1fc grade).

**What done means.** On the first book after the fix:
- no level-DD journey cures while a failed instalment presented before the cure has not been made good;
- the 88 + 151 shapes read 0;
- every non-level journey keeps its cure date.

The control: a two-instalment level account whose first instalment fails and whose second succeeds. The control must
keep the journey open. A partition leg is also needed: an account whose failed instalment is re-presented and collected
must cure.

**Recommended next, one variable.** Find the cure predicate for a level leg in the collections desk (step 2b's
"shortfall against the schedule"). Then print its shortfall for SYN-2016-549 on 4 May 2018. The prediction, filed before
reading the code: it prints 0, because it compares May's collection against May's instalment.

## Correction, before any run: the predicate is cumulative, so the filed mechanism is wrong (worker, 9 Nov 2026 ~08:00 GMT)

The hypothesis above said the cure "reads the shortfall for the current period". **It does not.**
`arrears_engine.level_shortfall` (`company/billing/arrears_engine.py:254`) computes
`min(requested to date - received to date, debit balance)`. That is cumulative. A failed April instalment that was never
made good stays in "requested". The prediction filed above ("prints 0, because it compares May's collection against May's
instalment") is withdrawn as a mechanism. It was refuted by reading the code, not by running it.

Two candidates remain, read from the code and not yet printed:
1. **The debit-balance cap.** A shortfall is counted only up to the debit balance (Ofgem: "a shortfall in credit is
   nothing owed"). If the desk's ledger balance on the cure day is nil or in credit, the journey cures by design. The page
   then still shows the failed instalment's invoice as outstanding. That would make it a page-and-desk disagreement
   about one account, not a false cure. The page reader put SYN-2016-549 at GBP 2.79 owed on 4 May 2018. So the two
   balances differ by at least that much on that day.
2. **Once level, always level.** The desk's `level_of` (`payment_observation_consumer.py:901`) returns a schedule
   for any account that has *ever* had a level collection requested. So `_step(level=True)` follows the account after it
   leaves level DD. On that path, a journey cures whenever the view shows nothing overdue. It never asks
   `_owes_a_bill_due_by`, and it opens only on a level return. This fits the 151 cures on 19 accounts that left level DD.
   One example is SYN-2016-549 in 2020: on standard credit, three failed bills unpaid, journeys cured.

**Prediction, filed before printing:** on SYN-2016-549, `level_of` is non-None after its last level request on
24 Jan 2019. Candidate 2 accounts for at least 140 of the 151 left-level cures. Candidate 1 accounts for most of the 88
level-at-cure cures that still have an unpaid invoice. Recommended next, one variable: replay the desk on SYN-2016-549
alone and print `level_of`, `level_shortfall` and `ledger.balance` on each cure day.

## The replay, graded (worker, 9 Nov 2026)

**Readers.** `/var/tmp/grade-2981-replay/replay.py` replays the desk predicate on one account from a ledger
rebuilt off the page rows. `desk_own.py` and `join.py` grade the whole book from the desk's own cure stage:
`days_overdue` 0 means the view held a shortfall item aged 0 days, and None means it held no item.
**The rebuild is not faithful past 2022.** It lacks write-offs and the cash the desk posts itself. On 272 cures it
reads a shortfall more than 0 days old where the desk read none, so the book-wide grade uses only the desk's own record.

**SYN-2016-549, each cure day:**
- 4 May 2018: level_of is set; level_shortfall is GBP 45.00, aged 0 days; the balance is GBP 201.82.
- 26 Nov 2018: level_shortfall is GBP 42.84, aged 0 days; the balance is GBP 204.70.
- The desk recorded both cures as overdue 0 and days 0. That is an item aged 0 days, not the absence of an item.
- Every cure from 14 Apr 2020 on is after the last level request (24 Jan 2019). level_of is still set. The desk read
  days None, meaning no item. `_owes_a_bill_due_by` reads True on every one in the rebuild.

**The prediction, graded:**
1. *level_of is non-None after 24 Jan 2019:* **HELD.** `_level_requests` is never cleared.
2. *Candidate 2 explains 140 or more of the 151 left-level cures:* **HELD.** 150 of 151 cured with no item in a level view.
   That view never asks for the scheme's debit. The one left is aged 0 days.
3. *Candidate 1 explains most of the 88:* **FELL.** 43 of the 88 cured on an item aged 0 days. At most 45 could be the
   debit-balance cap or a met schedule.

**The cause the prediction missed, a third mechanism.** The shortfall is cumulative, as the 08:00 correction says. But
the cash is applied to the oldest request first. So the next instalment's cash meets the failed one, and the shortfall
moves onto the request presented that day. That request ages 0 days. The desk cured on "the view reads nothing
overdue", which needs more than 0 days. The non-level path already guards this exact day-of-due shape with
`_owes_a_bill_due_by`. The level path had no equivalent. Book-wide on the desk's own record: 110 level-at-cure cures
are of this shape, and 91 had no item.

## The fix (worker, 9 Nov 2026)

- `arrears_engine.on_level_dd(ledger, schedule, on)` decides whether an account is still on level DD. It is, while
  some supply leg's latest bill issued by `on` is one a level collection paid for. The leg is the part of the bill
  reference before its first `::`. It is per leg because 61 accounts on 298149a1fc mix a level leg with a non-level
  one. Level requests are always DD, so their correlation id is the invoice reference.
- The desk walks an account on its schedule only while `on_level_dd`. A level journey cures only when
  `level_shortfall` is None. The view's "nothing overdue" is no longer enough. An account that has left level DD is
  walked on its bills: it cures only if `not _owes_a_bill_due_by`.
- The consumer's collections view reads the schedule only while `on_level_dd`. After that, it ages the balance on
  its bills, the debit the scheme ran up included.
- **Control and partition leg, in one test:** `test_a_missed_instalment_not_made_good_holds_the_journey_and_a_made_good_one_cures`.
  The made-good branch is asserted first. The left-level leg is `test_an_account_that_left_level_dd_is_dunned_on_its_bills`.
  At HEAD that account cured on 6 Mar 2025 with GBP 260 owed on bills past due.
- **Mutations:**
  - M1, the level cure reads the view again: red.
  - M4, the level cure never fires: red, on two tests.
  - M3, the view keeps the schedule after the account leaves level: red, on the opening amount.
  - M2, the desk keeps the account on level after it leaves: **does not fire alone. This is a missing test, not an
    equivalence.** The fixed view still blocks the cure, except when a left-level household pays down to a balance
    that sits only on a bill due that day. There, the level path's `level_shortfall` excludes today's ask and cures,
    and `_owes_a_bill_due_by` holds. No fixture here builds that case. It is filed below.

**GAP, filed: no closing statement for a level scheme.** Once an account leaves level DD, its scheme debit is aged
from the due dates of the bills it sat on. The fixture's journey opens at GBP 290 and goes straight to the plan-offer
rung. A real supplier sends a closing statement with its own terms. Ofgem's para 2.8 says a debit at the end of a
payment scheme is not debt by itself. Nothing in the tree models that statement, so the opening rung on a left-level
account is harsher than practice. That is the open half of this fix. It needs a knowledge-page entry before it is
built (K8).

## Prediction for the first book carrying the fix (filed before any such book exists)

- The finding's 151 shape (left level, an invoice due by the cure unpaid at run end) reads **0**.
- Within the 88 shape, the 43 cures on an item aged 0 days read **0**. **The 45 with no item I predict will persist.**
  These are level-at-cure cures where the schedule was met or the balance cap applied, while a bill the scheme had not
  covered is unpaid at run end. That is a seasonal debit, which para 2.8 says is not debt. So the drawn "88 reads 0"
  is not what this fix should do, and I am not claiming it.
- Cure dates on accounts that never held a level request are **byte-identical**: neither predicate changed for them.
- **Expected and unsized:** more journeys, and longer ones, on accounts that left level DD in seasonal debit. Their
  debit is now dunned. I cannot yet say how many.
- **Refuted if:** any non-level journey's cure date moves; or any level-at-cure cure is recorded on an item aged
  0 days; or any left-level cure lands while `_owes_a_bill_due_by` holds.
