**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (weekly rhythm)

# The 2 Nov Monday note is written only if the shared tree advances past 8b764fbdf1, and it has not advanced for 17 hours

**Found:** 28 Oct 2026, 12:40 GMT, by the delivery seat, pre-flighting the first live Monday note
(claim `the-first-monday-note-is-written-and-reads-right`).

**The facts, read just now.**

- The 07:00 tick is `daily-self-note.service`, run from `/home/rich/synthetic-enterprise`. It calls
  `weekly_rhythm.tick()` as a passenger, from the **shared tree's working copy**.
- The note writer (`weekly_rhythm.write_monday_note`, `director_concerns.monday_note`) arrived in
  `8b764fbdf1` (28 Oct 10:36 GMT). The shared tree's HEAD is `5e3e9966a5` (27 Oct 19:24). It does
  **not** contain `8b764fbdf1`, and `docs/operations/MONDAY_NOTE_FOR_THE_DIRECTOR.md` is not on disk there.
- The shared tree will not fast-forward. The supervisor logged this at 11:34 GMT: `ORIGIN FORK
  (NOT_ADVANCED)`, origin 55 ahead, refused by 30 dirty paths that origin also changes
  (`.gitignore`, `background/schedule_manifest.yaml`, `background/tick_mode.py`,
  `docs/direction/DIRECTION.yaml`, `docs/direction/decisions.jsonl`, ...). Its log says: "THE STEP IS TO LAND OR REVERT THOSE PATHS".
- The live baton (`docs/observability/.weekly_rhythm.json` on the shared tree) holds the 26 Oct
  Monday step: opened, finding filed, **never closed**. On 2 Nov the tick lapses it and opens the
  new Monday in the same call. That is the lapse branch. The note-writer test walked only the
  bootstrap branch until this commit.

**Pre-flight on origin's code.** I copied the live baton and ran `tick()` at 29 Oct, 1 Nov and
2 Nov 07:00 against temporary paths. The results were WAITING, WAITING, then OPENED with
`lapsed: 2026-10-26` and a note written. The note had all four sections. Its one close since
28 Oct (`the-26-oct-advisor-steer-asks-that`) was graded `nothing to land`. Nothing is waiting on
the director, and nothing is overdue.

**One reading defect, fixed in this commit.** The 26 Oct ruling closed four rows with one
resolution. The note printed its first 220 characters four times, cut off mid-word ("pr..."), and
named none of the four questions. A shared answer is now printed once, with each question it
closed listed beneath it, and truncation stops at a word boundary.

**What decides 2 Nov.** If the 30 paths are not landed or reverted on the shared tree before
2 Nov 07:00, the tick runs the old code. The step opens and no note is written. Nothing
says so, because the old code has no note to fail on. The ask is not to add a watcher. It is to
clear the shared tree's 30 contested paths, which other lanes hold.

**Discharges when** a note dated 2026-11-02 is on the shared tree with four sections, checked
after 07:00 on 2 Nov (handed on as `the-2-nov-monday-note-is-on-the-shared-tree`).

## Re-measured, 28 Oct 14:40 GMT (worker tick that drew `the-2-nov-monday-note-is-on-the-shared-tree`)

**The drawn item was not yet due.** It reads the note after 07:00 on 2 Nov, and it was drawn on
28 Oct. A continuation expires after six hours, so it cannot wait five days in that store either.
I released the claim. This finding carries the check: DO NOT DRAW BEFORE 07:15 on 2026-11-02.

**The premise is live, but narrower than "30 contested paths".** The shared tree is still at
`5e3e9966a5`, 68 behind origin, and does not contain `8b764fbdf1`. I ran the reconciler's own
read-only classifiers (`background/origin_reconcile.py`) over the 32 blockers it now names:

- **30 are lossless already.** 14 tracked and 10 untracked paths hash equal to origin's blob,
  and the rest match an earlier origin revision of their own path (`earlier_revision_twins`).
- **`docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`** is a producer's
  output (`generated_output_verdicts`), its change carries cleanly, and it has been untouched
  for 383h. That puts it in three clearable classes.
- **`tests/tools/test_generate_billing_ledger.py` is the one path that holds the whole advance.**
  It conflicts on carry and was last written 30.8h ago, under the 48h abandonment line. Its only
  content origin lacks is `test_an_occupier_bill_the_engine_never_collects_carries_the_credit_its_account_took`.
  Run against origin's code in a scratch worktree, that test FAILS: origin's ledger records *no*
  payment on a deemed-account bill (`{'OCC-EB1': [], 'OCC-EB2': []}`), by design (line 82,
  "collected nothing from anyone"). So the copy asserts a design origin has since replaced. It
  is not work that origin is missing.

**Prediction, filed before the outcome:** the copy crosses `ABANDONED_AFTER_HOURS = 48` at about
07:46 GMT on 29 Oct. On the next cadence after that, the reconciler preserves it on a ref, clears
it, and fast-forwards the shared tree past `8b764fbdf1`, three days before the 07:00 tick on
2 Nov. Nobody needs to touch another lane's file early. Two things would refute this: a new
conflicting edit lands in the shared tree before then, or the holder rewrites the test file
(which restarts its clock). If the shared tree is still behind `8b764fbdf1` at 12:00 on 29 Oct,
that is the next thing to look at, ahead of the 2 Nov read.

## Done, 29 Oct 07:20-07:40 GMT (worker tick, claim `the-shared-tree-advances-before-the-2-nov-note`)

**The shared tree advanced.** `5e3e9966a5` -> `faa06d46df`, 113 commits, by `git merge --ff-only`
inside `origin_reconcile.advance_shared_tree()`. `git merge-base --is-ancestor 8b764fbdf1 HEAD`
holds. Nothing was stashed, checked out, reset or added with `-A`.

**The prediction above was pre-empted, not tested.** I cleared the one holder by hand at about
07:25, roughly 20 minutes before the 48h abandonment line would have let the reconciler do it. So
this tick says nothing either way about whether the reconciler's abandonment class would have fired.

**The 33 paths that were dirty on the shared tree and also changed by origin, each with one fate.**
(a) = same bytes as origin, or an earlier origin revision of its own path, so a commit already
holds it. (b) = a daemon's or producer's state file it rewrites. (c) = real work no commit holds.

| Path | Fate |
|---|---|
| `.gitignore` | (a) tip twin |
| `background/schedule_manifest.yaml` | (a) tip twin |
| `background/tick_mode.py` | (a) tip twin |
| `background/two-reader-review.service`, `.timer`, `two_reader_review.py` | (a) untracked tip twins |
| `tests/background/test_tick_mode.py`, `tests/background/test_two_reader_review.py` | (a) tip twins |
| `docs/direction/DIRECTION.yaml`, `decisions.jsonl`, `wrong_triage.yaml` | (a) tip twins |
| `docs/market_research/income_shock_depth_and_duration_b7.md` | (a) tip twin |
| `docs/status/SEAT_STRETCH_LOG.md` | (a) tip twin |
| `docs/observability/trust_ledger.json`, `site/data/delivery.json` | (b) producer output; tip twins at the time |
| `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` | (b) `finding_classes` register |
| `docs/design/DOMAIN_INVARIANTS.yaml` | (a) earlier origin revision (`97d18d3878`) |
| `tools/generate_explore_cast.py`, `tests/tools/test_generate_explore_cast.py`, `site/data/explore_cast.json` | (a) earlier origin revision (`97d18d3878`) |
| staging notes: CRISIS_BAD_DEBT (`24c81d1394`), 2_NOV (this file, `d3ff2c1f5f`), DESK_DUNS (`1470776471`), PAGE_PRINTS (`d9828b5b3d`), PRINTED_REGISTER (`686fb73ef0`), SECOND_COLD_READS_ROWS (`6bdf089925`), PREREGISTRATION second cold read (`a4d2c45634`) | (a) earlier origin revisions |
| staging notes: EIGHT_COLD_READ_ROWS, PAYMENT_BELIEF_HARNESS, REAPER, SHARDED_SIMULATION_READ, SEAT_READING second cold read | (a) tip twins |
| `tests/tools/test_generate_billing_ledger.py` | **superseded draft, not (c).** Its one addition fails on origin with `IndexError` because origin draws no payer for a deemed-account bill (`7cec44a4b`). Origin's `test_a_bill_inside_the_occupier_window_is_the_deemed_accounts.py::test_a_window_month_the_ebss_credit_paid_leaves_the_payers_page_at_nothing` covers the property. |

**No path was (c), so nothing was landed under another lane's subject.** The one by-hand step was
the ledger test. `refresh_to_head --base-wins` refused it, because its name-based reading sees a
landable hunk and cannot see that the hunk fails. I preserved the bytes first at
`refs/preserved/refresh-to-head/occupier-ebss-ledger-test-superseded-by-7cec44a4b` (`23d586edc3`),
then removed the appended test so the file equals HEAD. The reconciler then cleared the other 32 and
preserved the 11 earlier-revision copies at
`refs/preserved/origin-reconcile-earlier-revision/origin-reconcile-5e3e9966a5` (`74d1c95a4`).

**Dry run on the advanced tree.** I copied the live baton and ran `weekly_rhythm.tick()` at
29 Oct, 1 Nov and 2 Nov 07:00 against temporary paths, with `MONDAY_NOTE` pointed at a temp file.
The results were WAITING, WAITING, then OPENED with `lapsed 2026-10-26`. The note was written with
the four sections: decided / waiting on you / closed on the seat's recommendation / overdue.

**A reading defect the first dry run showed, fixed in this commit.** The "printed once" fix from
`8b764fbdf1` never fired on the live rows. The four 26 Oct rows share the quoted ruling, and each
ends in its own outcome past character 220, so keying the group on the whole text grouped nothing.
The note printed the same cut-off quote four times and none of "Declined", "Ruled: ...", "Deferred".
Its test used four identical resolutions, so it was keyed to its fixture, not to the live shape.
`monday_note` now groups on the line the reader sees and prints each row's own remainder beneath
the quote. The new test leg is
`test_one_quoted_ruling_with_a_different_outcome_per_question_prints_each_outcome`, and its
mutation (grouping on the whole text again) fires. On re-run, the 2 Nov dry run names all four outcomes.

**Still owed, and not this item's:** the 07:15 2 Nov read that the note is actually on the shared
tree (`the-2-nov-monday-note-is-on-the-shared-tree`). Separately, `reconcile-watch` logged
boot-sha drift at 07:26: background-worker, deadmans-switch, naive-organ and sim-runner are
35 modules behind until they restart. `daily-self-note` is a oneshot that imports fresh, so the
note does not depend on those restarts.
