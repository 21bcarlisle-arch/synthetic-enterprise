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

**The class stays open.** A producer test that calls `run_phase2b` cannot tell a published
record from a dropped one. Today no control says that a `phase2b` key built for a grade reaches the reducer.

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
