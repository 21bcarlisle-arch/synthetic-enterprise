**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The 08f267b666 book's third refusal was a test answered sixteen minutes later, and its grade was already spent (2026-11-02)

Drawn as `the-08f267b666-book-republish-and-grade`: re-offer the 08f267b666 book once the compact ledger
(58d49405e) was on the shared tree, quote the publish outcome, and grade
INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS against 308a3f168's prediction of 18 -> 0.

## Premise, re-measured at draw time

**The grade half is spent.** fb671d3015 graded this book: 308a3f168 cleared the 18 PC2 breaches on
the four accounts and 2 new ones sat on SYN-2016-582. b0378f0b34 traced those 2 to the grader, which
dated SYN-2016-582's change of supply from its first issued bill, and retired the exception at 0 of 30,708.
I re-graded at HEAD 5769f6209d on the book's ledger (91.2 MB, 20:53Z) and its printed set (1,293
files, 20:53:53-54Z). The printed set is the 08f267b666 regen, not the 09:32Z set the item warned about.

| row | breached | flagged | denominator |
|---|---|---|---|
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 0 | 136 | 30,708 estimated bills on a graded rung |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 3 (excepted, ceiling 3) | 14 | 4,309 estimated runs |

Gate verdict: "0 unexcepted breach(es) ... 6 excepted. ENFORCED: nothing unexcepted, so the publish stands."

**The size half was answered, but the publish was still refused.** The worker's one automatic re-arm
(20:50Z) ran after the compact ledger and was refused at 21:22Z for a different cause.
`test_every_real_period_exports_readings_that_reproduce_our_own_volume` failed on 6,428 of 52,828
periods ("C2g/38: reads give -40.9 but the bill used 180.3"). That is the catch-up-bill defect in the
test that f5b852ba49 fixed at 21:38Z, sixteen minutes later. The book was made at 08f267b666, which
already carries 1bdd86b849, so the book's catch-up bills open on the last estimated reading, as
f5b852ba49's test now expects. At HEAD the test passes on this ledger: it walked 52,828 periods,
matched the meta's invoice_count, and found 0 wrong.

## What was done

- 21:45Z: re-offered by copy, as the item directed. I copied `done/run_complete_20261102T173915Z.md`
  into the shared tree's `docs/staging/` without its three did-not-land stamps. The automatic re-arm
  would not do this, because it allows one attempt per marker and that attempt was spent at 20:50Z.
  `run_output_latest.json` is byte-identical to the book's JSON (`cmp`).
- **21:50Z: the copy was deleted before any publisher read it.** The worker's two-rooms repair logged
  "removed 1 redundant staging copy/copies already archived: run_complete_20261102T173915Z.md". A
  root copy whose name is already in `done/` with more text is treated as a duplicate. **Re-offering
  a marker by copying it back to `staging/` cannot work; the item's prescribed route is closed.**
  The route that works is the one the automatic re-arm uses: give the publisher the `done/` path.
- 21:52Z: I stamped the `done/` marker `publish-rearmed ... by=delivery-seat` with the reason, then ran
  `python3 background/process_run_complete.py docs/staging/done/run_complete_20261102T173915Z.md` from
  the shared tree's root.
- The run started at 21:22Z (0a6391d186) has no `simulation/`, `sim/` or `company/` commit over
  08f267b666, so its book will be this book's twin. The re-offer gets a current site about an hour
  sooner, and no figure differs.

- 22:04Z: the publisher logged "TWO ROOMS, not safely repairable, so the landing below is expected to
  be REFUSED" on `SEAT_FINDING_THREE_SMALL_EXCEPTIONS_TRACED_ON_THE_209C_BOOK_..._2026-10-29.md`.
  The `done/` copy was untracked and dated 29 Oct 16:42. The root copy is tracked and was last landed
  at b0378f0b34. The root copy contains every line of the `done/` copy, plus one correction to a line
  and a later section, so the `done/` copy is a stale duplicate. ~22:12Z: I moved it, not deleted it,
  to `/var/tmp/two_rooms_aside_20261102/`. To reverse, move it back.

## Publish outcome

**Did not land: `commit_refused`, 22:40Z, and no content is implicated.** In the publisher's words:
"Publish landing REFUSED: HEAD moved under the gate on all 2 attempt(s), so no verdict ever described
the tree the commit would have created. Nothing was committed and no test is implicated -- the gate is
longer than the gap between commits on this tree". Attempt 1 lost the race when the base moved
feeaadc44 -> d5567880e at 22:27Z. Attempt 2 waited 75s for a quiet tree, gated, and lost again. The
two-rooms warning raised at 22:04Z did not appear as a cause.

I did not make a third attempt by hand. The 0a6391d186 run started at 21:22Z on a book with the same
code, and finishes around 23:00Z. Its marker reaches the publisher on the worker's ordinary glob, and once
it publishes it supersedes this marker. A third attempt on 08f267b666 would meet the same hot tree and
then be overtaken.

**What the next publish should see:** the raw-export test passes at HEAD on this book's twin, the
invariant gate passes it, and the two-rooms conflict is cleared. The one remaining way to be refused
is the one measured here: four tree-wide landings in ~13 minutes (21:38-22:27Z) against a gate that
needs ~10.

## Still open, not this item's

The compact ledger is 91.2 MB, 87% of GitHub's 100 MiB file limit. The durable choice is still open
in `SEAT_FINDING_THE_PUBLISHED_RUN_OUTGREW_GITHUBS_FILE_LIMIT_2026-10-10.md`.
