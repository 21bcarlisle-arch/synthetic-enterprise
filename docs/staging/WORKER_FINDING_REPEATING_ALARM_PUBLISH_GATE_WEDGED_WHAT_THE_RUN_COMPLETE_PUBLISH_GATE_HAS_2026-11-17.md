**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ACTION NEEDED] publish_gate_wedged

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 1 separate day(s)**, on **2026-11-17**, and **1 member(s)** of
the family `auto:b2d82739052db5bf` have fired. Both counts are DERIVED from this document's own
dated lines every time the alarm fires again, so they age with the document rather than with
its first firing.

Separately, the observer that last filed reported **3 consecutive firing(s) without a state
change**, over **5.4h**. That is `notify()`'s streak counter, which resets; it is not a total
and does not combine with the two counts above.
<!-- counts:end -->

## The alarm, verbatim

```
[ACTION NEEDED] publish_gate_wedged
What: The run-complete PUBLISH GATE has failed 3 time(s) in a row within the last 60 min -- the site/report pipeline is WEDGED and run_complete markers are piling up unpublished. Latest cause: the domain-invariant gate refused the BOOK: it breaches invariants that no named, dated exception covers, so NO test was run. NOT a test failure. The breaches are in the cause evidence and in docs/reports/DOMAIN_INVARIANTS.md; fix their cause in the code, and the next run that grades clean publishes (rc=82, git=f7e17b1316). EPISODE: wedged since 2026-11-16T04:39 UTC -- 31h59m and 48 consecutive failures in THIS episode (not a fresh hour). Markers pending: 2.
How: ATTRIBUTED CAUSE: `domain_invariant_refused` -- breaches no exception covers at git=f7e17b1316: INV_OVERDUE_WITHIN_PAGE_BALANCE 7 (no exception); INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5 (5 breaches exceed the exception's max_breached 1). NO TEST WAS JUDGED -- the domain-invariant gate refused the book before the suite ran. Do NOT hunt a red and do NOT run the gate's pytest argv. Read the breaches in docs/reports/DOMAIN_INVARIANTS.md (the ATTRIBUTED CAUSE line names them), fix their cause, and offer a run made at or after the fix: this book will never grade clean. The alarm clears on the next clean publish.
Why: A silently-wedged publish gate stops the live site and report updating with NO other signal -- this is the exact ~45-min silent stall of 2026-07-14 (H15).
```

## What is known without diagnosing anything

- Signature: `auto:b2d82739052db5bf` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-11-17T07:17:29+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS` = 3, applied by `notify()`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

A REPEATING FAILURE IS ONE OF THE THREE TRIGGERS FOR THE END-TO-END CHECK (director,
2026-10-04): before fixing the instance, write the section below -- the loop may be the world,
the maths, the canon or the frame, not the code that is alarming.

## End-to-end check

Worker tick, 2026-11-17 12:50Z. **No test is red and no gate is wrong.** The cause is the book itself. All three failures in the window grade one book, `run_complete_20261116T070501Z` on f7e17b1316. That book was built before the fixes for its two refusing rows: INV_OVERDUE_WITHIN_PAGE_BALANCE 7 (D5, fixed by 341df4965) and INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5 (fixed by fc3129a86). It can never publish, and the gate is right to refuse it. A dated exception would print "overdue" to households that are in credit, so none is proposed.

Explanations, ranked by evidence:
1. **The world/code was wrong, and that is now fixed. Only a new book can show it (strong).** All five `background/next_book_requires.yaml` commits are ancestors of HEAD fca4fdc04e, and `sim_runner.book_admission()` returns `admitted` at HEAD. So the first cause has been removed.
2. **Capacity: one memory slot, two long jobs (strong).** sim-runner defers every cycle to `longjob-value-test-step-6-flag1` (11.8 GB). The cure is armed: `d5book-pause-watch` (`/var/tmp/d5book-pause/watch.sh`, commit 870cfa8a4c) stops step 6 once pair 2 (`member/control_33333_44444.json`) is on disk, then relaunches it when the D5-on book's run_complete lands.
3. **The alarm is wrong (weak).** The alarm is correct: nothing has published. But each regrade of the same refused book re-arms it, which is finding e2f6155891, fixed by 623b28e72e. The draw that sent this tick to "run the pytest gate" did not know that.

**Prediction, filed before the answer.** Seed 33333 finished at 12:06Z after 21,313 s. Seed 44444 is about 62% through, by log lines (2022-05 of 2016-2025). Its pair lands at about 14:30-16:00Z, so the watcher stops step 6 by 16:00Z. sim-runner then starts a D5-on book within one cycle. That book took about 6,700 s last time, so its run_complete should land by about 18:30Z. Graded, it reads 0 on both rows. If either row is non-zero on that book, the fix did not reach the book, and that row is the next item.

**Correction, 13:58Z (worker tick): the timing above is wrong; the mechanism is not.** Each seed is three full-window runs (`run_value_cycle_ab(level_arm=True)`; three `OUTCOME` lines, about 455k log lines each, before `[noise_floor] seed 1/2 done seed=33333`). "62%" was one run's progress through 2016-2025, read as the seed's. At 12:50Z, seed 44444 was about 13% through. Seed 44444's run 1 ended at 13:41Z and run 2 started at 13:52Z. At 33333's 21,313 s per seed, **pair 2 lands at about 17:40-18:10Z and the D5-on run_complete at about 20:00Z**. The watcher's pair-2 deadline is 23:00Z, so it still covers this. Stopping step 6 early would throw away the roughly 7.7 h of pair 2 the child holds in memory (noise_floor writes only at the end), so the watcher stays as armed. The refutation test is unchanged: the book grades 0 on both rows.

No concern is raised for the director: this is in-flight work with its mechanism armed. If the watcher exits 2 or 3 (`/var/tmp/d5book-pause/watch.log`), the pause never happened, and that is the next draw.

## Still live

## Instances seen
- `publish_gate_wedged what: the run-complete publish gate has failed # time(s) in a row within the last # min -- the site/` (first seen 2026-11-17)

## Re-asked
- **2026-11-17** — re-asked: **still_holds**. observed 2026-11-17, within the 3-day bar.
- **2026-11-17 12:50Z** — worker tick: cause is the pre-fix book, cure armed (d5book-pause-watch); see End-to-end check. Nothing to repair at HEAD.
- **2026-11-17 13:58Z** — worker tick: still holds; pair 2 is mid seed 44444, run 2 of 3. Timing corrected above (D5-on book at about 20:00Z, not 18:30Z).
- **2026-11-17 14:34Z** — worker tick: still holds; step-6 child pid 295849 alive (98% CPU, pair 2), d5book-pause-watch active; D5-on book still expected about 20:00Z.
- **2026-11-17 15:06Z** — worker tick: still holds; child 295849 alive, watcher waiting. Seed 44444 run 1 of 3 done (log line 1,821,922), run 2 at 2024-03 of 2016-2025, so about 1.6 h per run: pair 2 lands about 17:00-17:30Z, and the D5-on run_complete lands about 19:00-20:00Z, inside the earlier estimate.
- **2026-11-17 22:20Z** — worker tick: still holds, and no test is implicated. The 18f201c5bf book (run_complete_20261117T181948Z) is refused on INV_OVERDUE_WITHIN_PAGE_BALANCE 20 alone. The closing-refund row cleared when 153a675ad4 keyed its exception to the class. The four households are in the §9 grade of the VAT-rows finding. The cause is owned and landing: a live session holds `row7-three-leavers-desk-ask-traced` (claimed 21:05Z) and is running `surgical_land` of `background/live_payment_triad.py` plus `test_a_final_bill_reads_the_last_bill_issued_before_it_whether_or_not_it_is_due.py`. The publisher's re-grade of the same book (pid 1708674) cannot pass, because the book was built before that fix. Next: the first book built at or after the row-7 landing. Not duplicated here.
- **2026-11-18** — re-asked: **still_holds**. observed 2026-11-17, within the 3-day bar.
- **2026-11-18 02:12Z** — worker tick: still holds, no test implicated, nothing to repair at HEAD 1378c5d815. The refused book is still 18f201c5bf's (row 7 = 20), built before 594ed8239 and 20d4cbeccc. sim-runner defers every cycle to `longjob-value-test-step-6-flag1`. At 02:08Z, the s.12d re-plan replaced row7book-pause-watch with `flag1-stop-at-pair3-watch`, which is waiting for `control_55555_66666.json` (pairs 1 and 2 on disk, pair 3 not yet). `vts-threshold-skip-watch` launches only after any owed book has run. So the next book carries both row-7 fixes. Refutation test unchanged: that book grades row 7 = 0. Not duplicated here.
