**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The book the five grades wait on would have dropped three of their records, and it has not been built for 28 hours

Delivery seat, 21 Nov 2026, item `one-book-carries-the-blend-the-debt-records-the-dual-answer-and-b12`.
Read from code, the sim-runner journal and the live landing register. No measurement was taken.

## 1. The reducer dropped KNIFE3, B8 and the dual answer (FIXED in this landing)

The published `run_output_*.json` is `extract_report_data`'s REDUCED output (`tools/run_annual_report.py:599`).
The 20 Nov book (`run_output_6a588a832f_20261120T134224Z.json`, 133 keys) has no `phase2b` key. Three
producer-side records were landed with their own tests and never named in that whitelist:

| record | producer commit | whitelist on origin before this landing |
|---|---|---|
| `company_debt_recovery` (KNIFE3: write-offs with `invoice_ref`, `agency_remittances`, learner cells, sale rule) | 1624411d2 | absent |
| `retention_holdout_by_desk_year` (B8) | 775a3c46c | absent |
| `riding_leg_answers` (dual-fuel answer) | c41e70832 | absent (forwarded only by an uncommitted 3-line hunk on the shared tree, mtime 20 Nov 14:37) |

A book built at origin/main this morning would have lacked all three, so 3 of the 5 queued grades would
have opened it and found nothing. D48 (0ed751663) and B12 (a6de6f977) change computation inside
the run, not new keys, so they reach the book through existing fields.

Fix: the three forwards, each with `None` for a run that did not record it.
`tests/saas/reporting/test_a_grading_record_the_run_builds_reaches_the_published_book.py` has 6 tests.
Mutation-proven: deleting any line fails 2 tests, and defaulting any line to `[]` fails 1.
The `riding_leg_answers` lines are byte-identical to the shared tree's hunk, so that copy is
subsumed rather than conflicting.

~~**The class stays open.** A producer test that calls `run_phase2b` cannot tell a published
record from a dropped one. Today no control says that a `phase2b` key built for a grade reaches the reducer.~~

**The class is CLOSED (21 Nov, the commit that adds the control below).**
`tests/saas/reporting/test_every_key_the_run_returns_is_forwarded_or_dropped_by_name.py` reads the
key set from the dict `run_phase2b._main` returns (114 keys, static AST, no run). Each key must be
forwarded by `extract_report_data`, lifted by `run_phase4c_on_phase2b` and read from `run_output`,
written by `WORLD_WALK_TRUTH_KEYS`, or named in `annual_report.PHASE2B_KEYS_NOT_PUBLISHED` with its
reason. Mutation-proven on disk: deleting the `retention_holdout_by_desk_year` forward goes red, and
so does deleting one dropped-key entry. In-test, a new producer key goes red, and so does a deleted
`company_debt_recovery` forward.

The register lists 41 dropped keys. Writing it found these: **23 have no reader outside the
producer's tests.** One of them is `switching_gsop_payments`, the record the won-switch BLOCKING
finding is building towards. Another is `beyond_the_record`, whose own comment says it exists so
that a forward run never reads as historical, but the book drops it. They are listed as dropped,
not forwarded, because a forward adds a key and a cost to every book. The first grade that needs
one should move it into the forwards.

## 2. sim-runner owes a book and has built none since 20 Nov 15:39 (OPEN)

`book_admission` admits a book, and `/var/tmp/box-plan/box_free.py` correctly holds the s.12g 34-hour
watcher behind it ("a book is owed"), so the watcher does not race it. The book still has not
started. Between 15:34 and 19:14 on 21 Nov, every one of ~45 cycles deferred:

- roughly 35 for `landings come before experiments` (a different surgical_land each time);
- 7 for one long job (`longjob-stayers-control-rebuilt-belief-fix`, 16:35–17:04);
- 6 for `the code a run would import is not origin's: saas/reporting/annual_report.py`. This is the dirty hunk in part 1.
  On each of these cycles the queue had just cleared, and the dirty file refused the run at exactly that point.

Since 2026-11-08, `resource_headroom` has a FIFO waiter row that should stop landings overtaking a waiting run.
Two things appear to defeat it here. Both are inferred from the journal and not yet tested:
(a) sim-runner restarts hourly (04:14, 05:14, 16:54, 17:34, 18:14, 19:14), which gives it a new pid and puts it at the back of the queue;
(b) a cycle refused for code admission withdraws the waiter row, and the next landing registers ahead of it.

This landing removes the 6 code-admission refusals: after the shared tree rejoins origin,
`annual_report.py` matches origin. It does not address (a) or (b).

### §2 read from the journal, 22 Nov 05:10Z: (b) CONFIRMED, (a) CONFIRMED but secondary

`journalctl --user -u sim-runner`, 21 Nov 00:00Z to 22 Nov 05:05Z. The waiter row works: while
landings were ahead of it the runner waited, one gate at a time, and no landing overtook it while
it held its place. Each time the queue cleared, the next check was `code_admission`, and it refused
on the shared tree's uncommitted C32 hunks: 00:55, 01:25, 02:15, 03:05, 04:00, 04:10, 04:50, 04:55,
05:00, 05:05. The row had already been dropped when the queue cleared, so the next cycle found a new
landing ahead of it (01:30, pid 2493617, 45 minutes; 02:20, two gates, 25 minutes). That is (b).
Strictly, the row was not withdrawn by the refusal. It was deleted when the hold cleared, and the
refusal came after. Either way, a refusal taken after the hold clears gives the slot away.

(a) is real but does not explain the night. sim-runner started 11 times between 21 Nov 00:00Z and
22 Nov 05:05Z, but only once (04:15Z) in the five hours after 00:15Z, while the book kept failing to
start. That restart put the new pid behind two pending gates, which is an overtake.

**Fixed (22 Nov, the commit that lands this paragraph).** `sim_runner.book_checkout` puts a detached
worktree at origin/main (`/var/tmp/se-sim-runner-book`, sim-runner's own), and the run is launched
from it (`cwd` and `PYTHONPATH`). `code_admission` reads the import closure there. An in-place edit
on the shared tree cannot refuse a book any more. On a live check at origin 20a58061f4, with the
C32 hunks still dirty on the shared tree, the book was admitted. The loop now asks the landing hold
LAST: checkout, code and book admission first, and a refusal there withdraws the waiter row. When
the queue clears, the run starts. The run's one cwd-relative output, `ledger_latest.json`, is moved
back to the shared `docs/reports`. Controls are in
`tests/background/test_a_run_whose_imported_bytes_are_off_its_commit_is_not_published.py`, 3 new
tests. All four on-disk mutations go red: launching from the shared tree, dropping `root=` from
`code_admission`, asking the hold first, and skipping the checkout's refresh.

**Still open.** The deployed daemon runs the old code until its next restart. The book itself:
a `run_output_<sha>_<ts>.json` whose sha descends from 6f87ccb38. Restart overtakes, from (a), are
not addressed.

**The book started, 22 Nov 05:52:47Z.** sim-runner was restarted at 05:52 to load b1c7d76b16. Seven
seconds later it began `run_output_b1c7d76b16_20261122T055247Z.json` from `/var/tmp/se-sim-runner-book`
at b1c7d76b16. The shared tree still carried uncommitted hunks.

**Correction to the item's done-criterion.** The item asked for a book "whose sha descends from
6f87ccb38". 6f87ccb38 is on no branch. Its parent is a7bb4b28cd, `SALVAGE(auto): preserve this fork's
uncommitted work`, so it never reached origin. What it was meant to guarantee, that the book carries
`company_debt_recovery`, `retention_holdout_by_desk_year` and `riding_leg_answers`, is met at origin
anyway: each is forwarded in origin's `annual_report.py`, and so is `won_switches_not_supplied`. What
6f87ccb38 alone carries is the key-register control,
`tests/saas/reporting/test_every_key_the_run_returns_is_forwarded_or_dropped_by_name.py`, and the
`PHASE2B_KEYS_NOT_PUBLISHED` register. Both still sit uncommitted on the shared tree, and so does an
edit to §1 that marks the class closed. Until they land, the class stays open.

### 22 Nov 12:45Z: §2 is closed; the book is running and may die at report time

Read from `journalctl --user -u sim-runner` and git, 22 Nov 12:42Z. No measurement was taken.

- **§2 does not hold the book back any more.** The 05:52Z book (b1c7d76b16) started and died at
  07:57Z on `KeyError 'SYN-2016-144_3'` at `saas/cost_to_serve.py:246`, the roster defect. From
  08:02Z to 12:15Z every deferral named memory: the queued long job
  `longjob-value-test-cut012-new-book` first, then its 11,800 MB residency. No cycle deferred for code
  admission or for a landing overtake. When s.12g died at 12:20Z (0eb416a0ac), sim-runner started the
  next book within a minute.
- **The book in flight:** `run_output_35316f9395_20261122T122055Z.json`, pid 156398. 35316f9395
  descends from 25f0ea40b. Its `saas/reporting/annual_report.py` forwards all three of
  `company_debt_recovery`, `retention_holdout_by_desk_year` and `riding_leg_answers` (static read of
  the blob, so whether each is non-None waits on the published file).
- **The risk:** 35316f9395 does not carry the roster fix (no commit to `saas/cost_to_serve.py` or
  `annual_report.py` since 0efa633c1b), so this book can die the way b1c7d76b16 did. The fix is in
  flight under claim `the-book-reports-every-customer-it-supplies`: pid 24098 in
  `/var/tmp/se-seat-executor` has `saas/customers.py` and `annual_report.py` modified. I left it alone.
  If the book dies, the next book after that fix lands is the one the grades open.
- The non-None check on the three records, and the grading, go to the queued continuations
  (`d48-grade-...`, `grade-the-supplied-won-switches-...`), which open the published book anyway.
  `one-book-carries-the-blend-the-debt-records-the-dual-answer-and-b12` is released with this record.
