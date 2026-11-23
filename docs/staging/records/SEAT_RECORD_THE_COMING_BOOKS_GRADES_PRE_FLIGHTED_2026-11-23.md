# The coming book's grades, pre-flighted: what reads clean, what was broken, what still waits on the run

Delivery seat, 23 Nov 2026, item `the-coming-books-grades-are-pre-flighted-on-the-shared-2016-2018-run`.
This is a plumbing check. **No prediction is graded here, and no number from a 2016-2018 run is the book.**

## Status: increments 1 and 2 of 2, finished

Increment 1: the static half (every record each reader names, against the code that writes the book
at origin `813c99ccae`) and one live break fixed (§2). Increment 2 (§5): every reader run by its own
method against the 2016-2018 run's book. One reader would have voided its grade on the coming book
and is fixed. Two reader texts are corrected. No writer is missing a record.

## 1. Which run, and why not the shared fixture's dict

`tests/simulation/conftest.py::phase2b_2016_2018` (83570bd1c) returns `run_phase2b.main()`'s raw dict.
None of the readers reads that dict. Each reads a published `run_output_*.json`, which is
`extract_report_data`'s reduced output after `run_phase4c_on_phase2b`, plus the
`world_walk_truth_*.json` written beside it. Records that the raw dict holds but the reducer drops are
exactly the failure this check exists to catch (the 21 Nov finding that the reducer dropped KNIFE3, B8
and the dual answer). So the faithful plumbing check is **the same 2016-2018 window through the book's
own writer**: `python3 -m tools.run_annual_report --end-year 2018 --save-json ...`, in a detached
worktree at origin/main (`/var/tmp/preflight-2018`, `813c99ccae`). That is one extra run of the fixture's
window, not a second book.

## 2. A reader that had already gone missing (FIXED here)

`grade-dual-household-answers-apart-on-the-first-book-carrying-c41e70832` was **not in
`seat_continuation.live()`** at 09:15Z. Its window opened 02:45Z, nobody drew it, and
`STALE_AFTER_SECONDS` (6 h) dropped it at 08:45Z. It was not superseded or retired, just gone. Two
consequences:

- The coming book would have been read by nothing for the dual answer's §7.5c prediction.
- B8's flip gate (`SEAT_PREREG_B8_..._2026-11-23.md`, step 1) checks that none of the five grade ids is
  still in `live()`. A silently expired row passes that check. The gate's second leg, verdicts written
  beside each prediction, would still catch it, but only if the reader checks the prose.

Fix: re-handed off with its text unchanged except for the window, now **07:00Z 24 Nov**. No book can
start before then. sim-runner yields to the resident `longjob-value-test-cut012-new-book`, declared to
end around 06:30Z 24 Nov. The same expiry would have taken three more grades at 15:00Z today:
`grade-the-supplied-won-switches-...`, `grade-knife3-i1-to-i5-...` and
`read-the-ending-term-belief-grade-on-the-coming-book`. They are re-armed to the same 07:00Z 24 Nov
window, with their texts otherwise unchanged. The d48 row already carried that window.

**Class, not filed as a finding here:** a continuation that waits on a book has a 6-hour life, and a
book is roughly 30 hours away. Every book-waiting row has to be re-armed by hand or by a draw. The
draw had been doing that until today's 02:45 window landed in a stretch with no draw.

## 3. Static reading: every record each reader names, against origin's reducer

Read from `saas/reporting/annual_report.py::extract_report_data` and
`tools/run_annual_report.WORLD_WALK_TRUTH_KEYS` at `813c99ccae`. "Forwarded" means the reducer writes
that key into the book. It does not mean the key is non-empty on a run.

| reader (continuation id) | records it names | forwarded at origin | status |
|---|---|---|---|
| D48 blend 0.5 (`d48-grade-...-59cd5ebda-...`) | `bills`, `meter_read_log` (via `tools/d48_spar_blend_counterfactual.py`, `tools/couple_w2_36_d48.py`) | yes, both | static clean; mechanical owed |
| KNIFE3 I1-I5 (`grade-knife3-i1-to-i5-...`) | `company_debt_recovery` (`share_of_gbp_with_invoice_ref`, `learned.remittance_lag_days`, `learned.by_cell`, `sale_decisions`, `remitted_gbp_on_a_ref_written_off`, `remitted_gbp`) | top key yes; subfields owed | static clean at the top key; subfield names owed |
| dual-household answers (`grade-dual-household-...-c41e70832`) | `riding_leg_answers` (`renewal_outcome`, `own_position_vs_default`, `household_answer`, `basis`) | top key yes | **was unread (§2), re-armed**; subfields owed |
| won-switch P2-P5 (`grade-the-supplied-won-switches-...`) | `acquired_customers`, `bills.customer_id`, `won_switches_not_supplied`, `total_net_gbp`, `switching_gsop_payments` | yes, all five | static clean; mechanical owed |
| ending-term belief Q1-Q6 (`read-the-ending-term-belief-...`) | `customer_events`, `desk_belief_log`, `producing_commit` (via `tools/grade_ending_term_belief_on_a_book.py`) | `customer_events`, `desk_belief_log` yes; `producing_commit` is the writer's stamp | static clean; mechanical owed |
| switching-level leavers (`grade-switching-level-leavers-...`) | `bills`, `per_customer_behavioral`, `closing_balances`, `level_dd_collections`, `credit_refund_log`, `home_move_outs`; `world_walk_truth_*.json` `final_month_nets.rows` | yes, all; `final_month_nets` is in `WORLD_WALK_TRUTH_KEYS` | static clean; mechanical owed (its replay imports `simulation.arrears_engine` privates `_resolve_bills`, `balance_settlement_from_outcomes`, `level_collection_difference`, so it must run in a worktree at the book's own commit, as its method says) |
| B8 holdout (`b8-flip-...`, then `b8-grade-the-switch-on-prereg-...`) | `retention_holdout_by_desk_year["blind_approach"]["by_year"]`, `retention_blind_holdout_log` | yes, both | static clean. Graded on the flip book, not the coming one. *Corrected in increment 2:* on the coming book (flag off), both are ABSENT by design (`growth_desk.retention_holdout_by_desk` writes `blind_approach` only when the switch is on; the reducer forwards the log as `null`), so the flag-off check is the top key, not these two |
| s.12g outcome (`s12g-has-a-reader-when-it-ends`) | `/var/tmp/vtn-driver/grade_new_book.out`, from the long job's own members | n/a | **not a book reader.** It reads the s.12g job's own output, not `docs/reports/`, so this run cannot pre-flight it |

## 4. The mechanical half: queued (increment 1; it ran, see §5)

`launch_long_job` refused to start it now: 17,428 MB resident (s.12g's twin child holds 11,800 MB) +
6,000 MB declared = 23,428 MB, over the 23,010 MB budget. The 6,000 MB is the measured ~6 GB peak of
a full book cycle (21 Nov finding, §2), used as an upper bound for a 3-year window. Starting it anyway
would put the s.12g thesis run at OOM risk, so it waits.

Unit `longjob-preflight-2016-2018-book(-queued)`, artefact
`/var/tmp/preflight-2018-out/run_output_2018.json` (and `world_walk_truth_2018.json` beside it), log
`/var/tmp/longjob-preflight-2016-2018-book.log`. It is queued now, so `book_admission` defers the book
to it. When s.12g ends, this run (about 45 min) goes ahead of the ~30 h book. That ordering is the
purpose of the item.

When the artefact exists, the continuation
`finish-the-coming-books-pre-flight-on-the-2016-2018-book` runs each reader in §3 against it. For each
one it records **reads-clean** (finds every record and field and computes its grade mechanically; the
value is not read) or **blocked-on-<writer>** (the exact missing record or field, and the module that
should write it). It fixes a reader that points at the wrong path or name, and files a finding for each
writer that is missing.

## 5. The mechanical half, run (increment 2)

The queued run finished at 12:11Z: `/var/tmp/preflight-2018-out/run_output_2018.json` (143 keys,
`producing_commit` `813c99ccae`, which descends from 59cd5ebda, da34c45c1, c41e70832, 1624411d2,
f80fe3951 and c09847b7c, so every grade's own commit is in it) and `world_walk_truth_2018.json`.
Each reader was run by its own method. **No grade value is read or written here**; "reads clean" means
the method found every record and field it names and computed its figure to the end.

| reader | result on the 2016-2018 book |
|---|---|
| D48 blend counterfactual | **was blocked on the reader; fixed.** `--ends --book-spar 0.5` raised `ValueError: advance 2016-03-04..2018-06-30 carries weight 1 at the book's SPAR 0.5` and the raise voided the whole sweep. Two electricity accounts (SYN-2016-110, SYN-2016-492) got their first actual read more than two years after opening, so one advance has weight min(1, FYC x 0.5) = 1 and the opening figure cannot be un-blended. The 10-year book will hold more such accounts. Fix: `rebill_or_name` keeps such an account as billed at every SPAR (the module's existing rule for bills it cannot re-bill) and names it in `held_as_billed_opening_unrecoverable`, so the grade reports how many it held fixed. With the fix it reads clean: 2 held, at SPAR 0 and 3. Rejected alternative: starting from `opening_registry_kwh_by_customer` instead. Against the un-blended figure on the 320 accounts where both exist, it is not the same number (ratio 0.61 to 1.08, median 1.00). |
| W2_36 <-> D48 coupler | reads clean, but only as `python3 -m tools.couple_w2_36_d48 --book <book>`. The continuation's `tools/couple_w2_36_d48.py` run as a script dies on `No module named 'background'`, so its text is corrected. |
| KNIFE3 I1-I5 | reads clean for I1, I2, I5 and the shape of I3/I4: `share_of_gbp_with_invoice_ref`, `learned.remittance_lag_days`, `learned.by_cell`, `sale_decisions[].sold_at` keyed `0.054`/`0.070`/`0.093`, `remitted_gbp_on_a_ref_written_off`, `remitted_gbp`. The **aged** cell of I3 has no row in this window: `by_cell` holds only `under_a_year_past_due`, and all 34 sale decisions are `over_a_year_past_due: false`. That is the window (no debt written off here was over a year past due), not a missing writer. I3's aged-vs-young comparison and I4's aged leg are only readable on a longer book. |
| dual-household answers | reads clean once its text is unambiguous. The text said "rows whose own renewal_outcome on own_position_vs_default". `renewal_outcome` is the function in `simulation.customer_events`, not a row key. The row's `answer` field is the post-fix outcome, and a reader taking it would measure the fix against itself. 25 of 139 rows have `household_answer` null (`basis` `no_household_answer`). The text now names the function and excludes those rows. `basis` for the residue is present on every row. |
| won-switch P2-P5 | reads clean. `acquired_customers` is a list of ids, not dicts. Every one carries a bill or is in `won_switches_not_supplied`, so P2's join works. `total_net_gbp` and `switching_gsop_payments` are present. |
| ending-term belief Q1-Q6 | reads clean; void by window, as its method says. The grader grades only 2019-2024 terms, so this book returns `0 states ... the grade is void, not refuted`. With its window widened to 2016-2018 in a probe (not the method), it builds 192 states. Its household join on `customer_events` finds leavers, and the join agrees with the desk row's own `left` on all 192. |
| switching-level leavers | reads clean. `replay.py` and `table.py` were copied to `/tmp/pf-ll` with only the two book paths (and their own scratch outputs) swapped, and run from the worktree at the book's commit. Replay closing vs book: 363 legs, 0 mismatched. `final_month_nets.rows` carries `debit_asked_gbp` for the addendum's count. |
| B8 | reads clean for a flag-off book. `retention_holdout_by_desk_year` carries `renewal_offer` and `save_offer`. `blind_approach` and the log are absent by design (§3, corrected). |

**Missing writers: none.** No finding is filed, because none of the eight readers is blocked on a
record the book does not write. The one block was in a reader, and it is fixed in this landing.
**Cleanup:** worktree `/var/tmp/preflight-2018` removed after this landing. The run's output stays
under `/var/tmp/preflight-2018-out/` as the evidence for this section.
