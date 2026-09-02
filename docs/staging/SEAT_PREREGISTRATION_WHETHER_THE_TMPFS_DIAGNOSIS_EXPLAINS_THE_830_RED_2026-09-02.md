# [SEAT PRE-REGISTRATION] Whether the tmpfs diagnosis explains the 830 red at HEAD

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`
**Filed:** 2026-09-02, BEFORE the second census runs. Lane 0: *"The director asked what the 830
reds were; we answered in prose and never showed him the number moving."*

The diagnosis is on the record in `2112a1f03` and in `bc57c8e30`'s message: `/tmp` is a 12 GB
tmpfs on a 24 GB box, `tests/background/conftest.py` has four autouse fixtures and every one
takes `tmp_path`, so a whole directory dies at fixture SETUP when allocation fails and reads as
820 defects. `2112a1f03` set `TMPDIR` to `/var/tmp` (real disk, 870 GB free) for the census's
pytest run. **Neither that repair nor `3a8232eb6` has been observed working.** This says what
the diagnosis predicts, before the run that can refute it.

---

## The baseline, and one thing wrong with it that must be said first

Run 1 — `head_red_observed.json`, `2026-09-02T04:30:02+00:00`, head `ec2e0b1a4`, 830 red:

| where | red nodes |
|---|---|
| `tests/background/` | 820 |
| `tests/tools/` | 6 |
| `tests/simulation/` | 3 |
| `tests/architecture/` | 1 |

Causes histogram, which the census's own docstring says is **a floor on named causes and never a
partition** (a bare `assert x == y` prints no type name, and one failure can print two lines —
these seven sum to 835 against 830 reds, so they already over-count):

`OSError` 760 · `AssertionError` 33 · `CalledProcessError` 24 · `JSONDecodeError` 12 ·
`FileNotFoundError` 2 · `IndexError` 2 · `KeyError` 2

**THE BASELINE ENTRY CARRIES `"passed": null`, AND THAT IS NOT A DETAIL.** `verdict()` reads a
missing pytest summary line as UNPROVEN, and `_record_observation` refuses to write an UNPROVEN
run into the store on purpose — *"a run whose suite did not execute has observed no test to be
green"*. So this row could not have been written by `main()` on a completed run: either the suite
never printed its summary (it was truncated or killed), or the store was seeded by a hand call to
`reg.record`. Both readings say the same thing about what the number is worth:

> **830 is a FLOOR on the reds at `ec2e0b1a4`, not the complete set**, and every clause below is
> graded against a floor. A residual count that comes in *above* a run-1 sub-count is therefore
> not automatically a refutation of the collapse; a residual count *below* one still is.

That is filed separately as a finding about the store, not resolved here.

`ec2e0b1a4` is not reachable from this worktree (`git cat-file` cannot name it), so run 1's
subject commit cannot be re-derived. Run 2's is recorded in the store by the machine.

---

## The run-duration allowance, which is NOT a prediction

`SUITE_TIMEOUT_SECONDS` was **3300**, and the nightly run that produced run 1 took **3537 s**
(58:57). The bound sits *below* the duration actually observed — `2112a1f03` fixed the ordering
(the suite's own timeout must fire before systemd's, so the census can say UNPROVEN instead of
vanishing) and in doing so removed what headroom there was. A run of last night's length would
now be aborted by its own timeout.

Set here: **`SUITE_TIMEOUT_SECONDS = 7200`**, **`TimeoutStartSec = 7500`**. Reason: this repo's
own house rule for a suite bound is `bound > 2 × worst measured` (`test_process_run_complete.py`,
`GATE_SUITE_TIMEOUT_SECONDS`), which against 3537 s demands ≥ 7074 s; the unit keeps the 300 s
the comment already allots for checkout, teardown and report, so the suite's timeout still fires
first. The timer fires once every 24 h, so 7500 s cannot overlap the next firing. **This is an
allowance for how long the run takes. It is not a claim about the code and it forgives nothing.**

---

## The clauses. Each is graded separately and the split is reported, not averaged.

**C1 — the `OSError` count collapses.** Run 2's `OSError` bucket is **< 40** (a fall of ≥ 95 %
from 760). **Refuted if ≥ 200.** Between 40 and 200 is neither: partially environmental, with
something else still allocating badly, and that is reported as a split.

**C2 — the collapse is where the diagnosis put it.** Red nodes under `tests/background/` fall
from 820 to **< 90**. **Refuted if ≥ 400.**

**C3 — the residual survives, by name.** These ten nodes were red in run 1 outside
`tests/background/` and tmpfs never explained them. **At least 7 of these 10 exact node ids are
red again in run 2. Refuted if ≤ 3 are.**

```
tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py::test_no_tree_scanning_test_passes_on_an_empty_population
tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market
tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_with_no_successor_still_goes_to_market
tests/simulation/test_price_response_curve_position_split.py::test_within_a_price_side_the_response_moves_monotonically_with_perceived_pounds
tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year
tests/tools/test_billing_tab_fix.py::test_closed_account_notice_date_tracks_the_record_not_a_constant
tests/tools/test_billing_tab_fix.py::test_closed_account_notice_real_churned_customer_c1
tests/tools/test_capability_index.py::test_the_live_register_rules_on_every_live_orphan
tests/tools/test_evidence_pages.py::test_page_is_reproducible_from_the_sources
tests/tools/test_year_spotlight.py::test_crisis_year_2022_worse_than_2020
```

**C4 — the real backlog underneath is real.** `AssertionError + CalledProcessError +
JSONDecodeError` in run 2 sum to **≥ 40** (they were 69 in run 1). **Refuted if < 10** — which
would mean tmpfs explained those too, there is no ~70-test backlog underneath, and the thing to
work next is not what Lane 0 says it is.

**C5 — the run finishes and says so.** Run 2's stored `passed` is an integer, not `null`, and the
verdict is not UNPROVEN. **Refuted if `passed` is null again** — in which case nothing above can
be graded at all and the finding is about the timeout, not the tmpfs.

**C6 — the run is also faster.** If RAM-backed scratch was the binding constraint, removing it
should show in wall-clock, not only in the red count. Run 2 completes in **< 3537 s**. **Refuted
if ≥ 3537 s.** This is an independent leg on the same diagnosis: C1 could collapse for a reason
that has nothing to do with allocation (another lane's fix landing in between), and C6 would not.

**A note on what C1–C4 cannot do.** Between run 1 and run 2 the tree moved: `3a8232eb6`,
`2112a1f03` and everything else that landed since `ec2e0b1a4`. **More than one thing changed, so
a move in the residual counts cannot be attributed to the tmpfs repair alone.** C1/C2/C6 are the
clauses the diagnosis actually owns, because the environmental change is the only one plausibly
capable of moving 760 fixture-setup failures at once. C3/C4 are about what is *left*, and a
surprise there is a finding about the backlog, not about the diagnosis.

---

## Constraints on the run itself, pre-registered because they are what invalidates it

1. **Exactly one census run.** Concurrency is what produced 1.67 GB → 3.36 GB of
   `pytest-of-rich` growth in an hour, and a second suite would manufacture the very failure
   being measured.
2. **I launch no other pytest process while it runs.** Other lanes' daemons are outside my
   control; what they were doing at launch is recorded below rather than assumed absent.
3. Evidence for 1 and 2 is a pasted `ps -eo pid,etimes,args | grep pytest` at launch and at
   finish, not a recollection of my own behaviour.

## What is owed when it returns

The graded result written **beside** each clause above, including any clause it refuted; a second
entry in `head_red_observed.json` at a post-fix commit; and the surviving reds named with their
route into the draw via `background/head_red_register`, which is what `bc57c8e30` built it for.

---

# GRADED IN PART, 2026-09-02 — the store clause, settled BEFORE run 2, and one caveat WITHDRAWN

Run 2 has not happened; C1, C2, C3, C4 and C6 are ungraded and stay ungraded until it does. What
is settled here is the clause about the store, because it turned out to be answerable from
evidence that already existed — and answering it **removes a constraint this pre-registration
placed on its own grading**, which must be said before the run rather than after.

## What the store clause said, and what is actually true

It offered three readings of `"passed": null` — *"the suite never printed its summary (it was
truncated or killed), or the store was seeded by a hand call to `reg.record`"* — and graded
everything below against the weakest of them. **It was the third, and the run was not truncated
or killed. It finished.**

| evidence | reading |
|---|---|
| `journalctl -u head-green-census.service`, 2026-09-02: `Consumed 59min 30s CPU over 58min 57s wall, 5.3G peak` then `status=1/FAILURE` | the process ran to completion and **exited**; it was not SIGTERMed |
| `status=1` is `main()`'s own return for `NEW_RED` (`return 1 if result["status"] == "NEW_RED"`) | a clean verdict, not a crash — "FAILURE" is systemd reading an intentional exit code |
| `verdict()` returns `UNPROVEN` **before** it can return `NEW_RED` when `passed_count is None` | a NEW_RED verdict is **unreachable** unless `passed` was a readable integer. The run had one |
| the journal printed **830** `NEW RED` lines, 830 distinct node ids, 0 `FIXED` | the complete list, not a prefix |
| those 830 node ids `diff` **identically** against the 830 keys in `head_red_observed.json` | the store is a hand transcription of that list |
| the journal's message reads `830 test(s) newly failing` — the wording `bc57c8e30` abolished at 07:41, three hours *after* the 04:30 run | the run executed **pre-`bc57c8e30`** census code, which had no `_record_observation` at all |
| `background/head_red_register.py` is `new file mode` in `bc57c8e30` | the module that writes the store **did not exist** when the run happened |

**So `main()` could not have written that row, and nothing is wrong with the run.** The row was
backfilled by hand into the register's own birth commit, from the alarm string in the journal —
and the alarm string was the one branch of `verdict()` that never stated `passed`. The number
existed inside the process for 58 minutes and reached no surface anybody could transcribe it from.

## The caveat this WITHDRAWS, stated plainly because it was load-bearing

The pre-registration wrote:

> **830 is a FLOOR on the reds at `ec2e0b1a4`, not the complete set**, and every clause below is
> graded against a floor. A residual count that comes in *above* a run-1 sub-count is therefore
> not automatically a refutation of the collapse; a residual count *below* one still is.

**That is withdrawn. 830 is the COMPLETE red set at `ec2e0b1a4`**, because it is the full `FAILED`
list of a run that reached its own summary line. The asymmetry it licensed is removed with it:
C1–C4 are graded symmetrically against run 1's sub-counts, in both directions, exactly as their
own thresholds are written. A count coming in above a run-1 sub-count is now a real surprise and
is reported as one.

This makes the grading **stricter**, not looser, which is the direction a correction to one's own
pre-registration should be viewed with most suspicion — so the evidence is tabulated above rather
than summarised, and the `diff` that settles it is reproducible from the journal.

`ec2e0b1a4` is still not reachable from any worktree here (`git cat-file -t` refuses it), so run
1's subject tree cannot be re-derived. That limit is unchanged and it bounds C3 in particular: the
ten residual nodes are named, but *why* they were red at that commit cannot be re-measured.

## C5 — the mechanism, discharged early; the observation, still owed

C5 said: *"Run 2's stored `passed` is an integer, not `null`, and the verdict is not UNPROVEN."*
It splits in two and only one half could be answered today.

- **The mechanism: DISCHARGED.** `_record_observation` now exists on the census's path, and the
  composition it belongs to — *a run that finished lands a row a reader can tell apart from one
  that did not* — was pinned by nothing. It is pinned now, end-to-end through `main(--from-log)`,
  by `test_a_completed_run_records_a_row_whose_passed_is_populated`, mutation-proven by dropping
  `passed=` from the `reg.record` call. Exercised on a realistic completed-run log: `passed`
  stores as `23891`.
- **The observation: STILL OWED.** No run 2 exists. C5 is graded against the real row tomorrow.

**Nothing here weakens C5.** If tomorrow's row still carries `null`, C5 is refuted and the finding
is about the timeout or the checkout, exactly as written.

## And a second defect found while establishing the first

`bc57c8e30` abolished "newly failing" — the word that made four absolute counts read to the
director as a rising delta — and mechanised the repair in `verdict()` **only**. `main()`'s notify
payload was a second, hand-authored copy of the same claim, so **tonight's NTFY would have said
"830 newly failing test(s) at HEAD" on the one channel he actually reads**, while the test pinning
the correction passed. One correction, two surfaces, one edited. The payload is now composed from
`result["reason"]`, so the two cannot disagree again, and
`test_the_alarm_carries_the_verdicts_own_sentence_and_cannot_drift_from_it` fails if either is
hand-authored back.
