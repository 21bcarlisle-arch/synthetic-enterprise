# The coming book's grades, pre-flighted: what reads clean, what was broken, what still waits on the run

Delivery seat, 23 Nov 2026, item `the-coming-books-grades-are-pre-flighted-on-the-shared-2016-2018-run`.
This is a plumbing check. **No prediction is graded here, and no number from a 2016-2018 run is the book.**

## Status: increment 1 of 2

Landed now: the static half (every record each reader names, against the code that writes the book at
origin `813c99ccae`) and one live break fixed (§2). Still owed: the mechanical half (§3), which needs a
book-shaped 2016-2018 output. That run is queued, not run, for the reason in §3.

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
| B8 holdout (`b8-flip-...`, then `b8-grade-the-switch-on-prereg-...`) | `retention_holdout_by_desk_year["blind_approach"]["by_year"]`, `retention_blind_holdout_log` | yes, both | static clean. Graded on the flip book, not the coming one; on the coming book (flag off) the check is only that the keys exist |
| s.12g outcome (`s12g-has-a-reader-when-it-ends`) | `/var/tmp/vtn-driver/grade_new_book.out`, from the long job's own members | n/a | **not a book reader.** It reads the s.12g job's own output, not `docs/reports/`, so this run cannot pre-flight it |

## 4. The mechanical half: queued, not run

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
