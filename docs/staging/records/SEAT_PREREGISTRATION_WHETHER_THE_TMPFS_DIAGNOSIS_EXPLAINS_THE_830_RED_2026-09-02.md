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

> **CORRECTED 2026-09-02, before run 2, by the finding this paragraph promised**
> (`WORKER_FINDING_THE_830_ROW_WAS_HAND_TRANSCRIBED_FROM_A_RUN_THAT_DID_FINISH_2026-09-02.md`).
> **The disjunction above is resolved, and the reading it settles on is the one this paragraph
> ruled out.** The 04:30 run FINISHED: `status=1` is `main()`'s own `NEW_RED` return, and
> `verdict()` cannot reach `NEW_RED` unless `parse_passed_count` returned an integer. It wrote no
> row because it was running pre-`bc57c8e30` code (the journal prints the old *"newly failing"*
> wording, and the register did not yet exist); the row was transcribed by hand an hour later —
> the stamp is the journal's minute and second with BST relabelled as UTC. **The transcription is
> COMPLETE: 830 journal node ids against 830 store keys, zero either way.**
>
> So *"830 is a floor because the run may have been partial"* is **REFUTED**. 830 is the complete
> `FAILED` set of a completed run, missing one field. The clauses below are graded against a
> complete count, and the asymmetry this paragraph granted them — *"above is not a refutation,
> below still is"* — **is withdrawn: C1–C4 are graded in both directions.**
>
> One narrower caveat survives and is NOT the same claim: `parse_failures` reads only `FAILED`
> lines, so a test reported as a setup/collection `ERROR` is outside the count. Whether run 1
> emitted any is not establishable — the journal holds the census's printout, not raw pytest
> output. That bounds the ABSOLUTE number and not the delta, because it applies identically to
> run 2.

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

> **C1 CONFIRMED. `OSError` 760 → 0.** Not "under 40" — the bucket is empty; `OSError` does not
> appear in run 2's cause histogram at all. The predicted fall was ≥ 95 %; the observed fall is
> 100 %.

**C2 — the collapse is where the diagnosis put it.** Red nodes under `tests/background/` fall
from 820 to **< 90**. **Refuted if ≥ 400.**

> **C2 CONFIRMED. `tests/background/` 820 → 2.** The two survivors are named in C3's residual
> table below (`test_live_ledger_guard`, `test_seat_guard_daemons`); they are not fixture-setup
> failures. The collapse is where the diagnosis put it, to within two tests.

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

> **C3 CONFIRMED, and at the ceiling: 10 of 10.** The clause asked for ≥ 7 and every one of the
> ten named node ids is red again in run 2. These are the only nodes in the store with
> `runs_red: 2`; every other red in run 2 is seen for the first time. **This is the clause that
> matters most for what to do next** — it is direct evidence that the residual is a real backlog
> and not an artefact of the environment, because it survived a change that removed 781 of its
> neighbours.

**C4 — the real backlog underneath is real.** `AssertionError + CalledProcessError +
JSONDecodeError` in run 2 sum to **≥ 40** (they were 69 in run 1). **Refuted if < 10** — which
would mean tmpfs explained those too, there is no ~70-test backlog underneath, and the thing to
work next is not what Lane 0 says it is.

> **C4 NEITHER CONFIRMED NOR REFUTED — 13, in the dead band, and the clause was a bad instrument.**
> `AssertionError 13 + CalledProcessError 0 + JSONDecodeError 0 = 13`, against ≥ 40 to confirm and
> < 10 to refute. **Reported as a split, not rounded to the nearest verdict.**
>
> And the reason it landed in the dead band is worth more than the verdict: **the clause measured
> three cause NAMES as a proxy for "there is a real backlog", and the backlog changed its causes
> without changing its size.** Run 2's dominant cause is `FileNotFoundError x29` — which was **2**
> in run 1. The withdrawal recorded above ("a count coming in above a run-1 sub-count is now a real
> surprise and is reported as one") binds here: **2 → 29 is a fourteen-fold rise and it is
> reported, not absorbed.** It is the single largest unexplained move in the grading.
>
> The claim C4 was written to test — *the ~70-test backlog underneath is real* — is **CONFIRMED by
> C3 instead**, which counted node ids rather than exception names. That is the lesson: a cause
> histogram is a floor on named causes and never a partition, and this pre-registration said so in
> its own baseline section, then keyed a clause to one anyway.

**C5 — the run finishes and says so.** Run 2's stored `passed` is an integer, not `null`, and the
verdict is not UNPROVEN. **Refuted if `passed` is null again** — in which case nothing above can
be graded at all and the finding is about the timeout, not the tmpfs.

> **GRADED EARLY, 2026-09-02 — this is the one clause that did not have to wait for run 2, and it
> is now HELD BY A CONTROL rather than by hope.** `record()` refuses a run row whose `passed` is
> `None`, naming its reason; `_record_observation` already turns UNPROVEN away, so a countless row
> arriving at `record` proves the caller was not a completed census. **C5 can therefore no longer
> be refuted by a `null` row appearing — that outcome is now a loud refusal instead of a silent
> ungradeable row.** It can still be refuted by the run not finishing, which is C6's subject and a
> different failure.
>
> The write path was measured, not assumed — `evaluate()` on a realistic completed-run log returns
> `status=NEW_RED, passed=23456`, and the row it produces carries `'passed': 23456`. Three
> mutations applied, each confirmed failing, each reverted.

> **C5 CONFIRMED IN BOTH HALVES, 2026-09-02 14:32 — the observation half is now discharged too.**
> Run 2's stored `passed` is **30479**, an integer; the verdict is **NEW_RED**, not UNPROVEN. The
> row is in `docs/observability/head_red_observed.json` as the second entry. The thing this whole
> Lane 0 item existed to establish — *that a run which finishes can be recorded* — **is
> established, by a real run and not by a fixture.**

**C6 — the run is also faster.** If RAM-backed scratch was the binding constraint, removing it
should show in wall-clock, not only in the red count. Run 2 completes in **< 3537 s**. **Refuted
if ≥ 3537 s.** This is an independent leg on the same diagnosis: C1 could collapse for a reason
that has nothing to do with allocation (another lane's fix landing in between), and C6 would not.

> **C6 REFUTED. Run 2 took 5150 s against a threshold of < 3537 s** — not merely over, but **46 %
> SLOWER** than the run whose reds it removed 94 % of. The clause was written to be refutable and
> it refuted itself; there is no reading of 5150 that satisfies it.
>
> **What this does to the diagnosis, stated without rescuing it.** C6 was declared *"an independent
> leg on the same diagnosis"* precisely so that C1/C2 collapsing could not be the whole argument.
> That leg has now failed. So the honest position is: **the tmpfs repair removed the failures and
> did not make the run faster**, and the pre-registration's own logic says that is a reason to
> doubt the causal story, not a detail to footnote.
>
> The obvious rescue — *"run 2 ran under contention"* — is **available and is NOT taken**, for the
> reason the prereg already fixed: run 1 ran under contention too, so contention is not a
> difference between them. What IS a difference, and is recorded rather than argued: run 2 shared
> the box with a `process_run_complete` gate suite at both launch and finish (`ps_at_launch.txt`,
> `ps_at_finish.txt`), and it was the **second** full census of the day, which violates constraint
> 1 below. Neither of those is measured, so neither is offered as an explanation. **C6 stands
> refuted and the duration is an open question, filed as one.**

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

---

## A THIRD defect, and it changes what "at a post-fix commit" can mean

Filed in full as
`docs/staging/done/WORKER_FINDING_THE_CENSUS_LABELS_ITS_ROW_WITH_A_COMMIT_ITS_SUITE_NEVER_RAN_2026-09-02.md`
and repaired in `378c4d34d`. It belongs here because it bears directly on **"what is owed when it
returns"** below, which asks for *a second entry at a post-fix commit*.

`_head_sha()` was read **twice** — once to build the subject checkout, once to label the stored row
— with the whole unscoped suite in between. So the `head` field recorded whatever the shared tree
had advanced to by the time the suite finished, not the commit the suite ran against.

**That means the phrase "a row at a post-fix commit" was not verifiable.** The field would have
read post-fix whether or not a single test had run against a post-fix tree, so it could not
distinguish the two — a done-means satisfiable by a row that lied. It is keyed to the property now.

### AND THE RUN THAT IS PRODUCING RUN 2 IS AFFECTED — read this before grading it

Observed live while the run was in flight:

```
started            Wed Sep  2 12:52:44 2026   (pid 450950)
its subject holds  f5b19b43f      <- the commit its suite actually ran
shared HEAD then   2a84aec8e      <- six commits later
```

A running process does not re-read its own source, so `378c4d34d` **cannot reach it**.

> **The row written by the 12:52:44 run will name the wrong commit. Its true subject is
> `f5b19b43f`.** Do not read that row's `head` field; read this line instead. Every other field —
> `red`, `passed`, `causes`, the node ids — is unaffected, so **C1, C2, C3, C4 and C6 are graded
> from it exactly as written.** Only the attribution is wrong, and it is corrected here.

Note what this does to the *attribution* caveat already recorded above ("more than one thing
changed, so a move cannot be attributed to the tmpfs repair alone"). It gets **stronger**, not
weaker: `f5b19b43f` is post-`2112a1f03` and post-`3a8232eb6`, so the tmpfs repair **is** in this
run's subject and C1/C2/C6 are live. The clauses can be graded. The commit named on the row simply
is not the one they were graded at.

---

# GRADED IN FULL, 2026-09-02 14:32 — run 2 exists, and the split is 4 confirmed / 1 refuted / 1 neither

**Run 2 completed.** Launched 12:52:43 BST, finished 14:18:33 BST, **5150 s**, `rc=1` (`main()`'s
own `NEW_RED` return). **49 red, 30479 passed.** The row is in the store, and this is what the
Lane 0 item asked for: *a second row with `passed` non-null*.

| | run 1 | run 2 | |
|---|---:|---:|---|
| red at HEAD | 830 | **49** | −94 % |
| passed | *(unrecorded)* | **30479** | the field the whole item was about |
| `tests/background/` red | 820 | **2** | C2 |
| `OSError` | 760 | **0** | C1 |
| wall clock | 3537 s | **5150 s** | C6, refuted |

## The split, clause by clause. Not averaged, not rounded.

| clause | threshold | observed | verdict |
|---|---|---:|---|
| C1 `OSError` collapses | < 40 (refuted ≥ 200) | **0** | **CONFIRMED** |
| C2 collapse is in `tests/background/` | < 90 (refuted ≥ 400) | **2** | **CONFIRMED** |
| C3 residual survives by name | ≥ 7 of 10 (refuted ≤ 3) | **10 of 10** | **CONFIRMED** |
| C4 backlog by cause name | ≥ 40 (refuted < 10) | **13** | **NEITHER — dead band** |
| C5 run finishes and says so | `passed` an integer | **30479** | **CONFIRMED** |
| C6 run is also faster | < 3537 s (refuted ≥ 3537 s) | **5150 s** | **REFUTED** |

**The one-line answer to the director's question.** The 830 was **781 tests dying on a RAM disk
and 49 real reds**. The environmental cause is gone and the 49 are what is actually owed. But the
run did not get faster, so the *mechanism* is not closed — C6 says so and is not being explained
away.

## Constraint 1 was VIOLATED, and it is reported before anything is claimed from the run

The pre-registration said **"exactly one census run."** **Two full censuses ran on 2026-09-02.**

| | started | finished | wall | red | passed |
|---|---|---|---:|---:|---:|
| run 2a | 10:43:43 | 12:14:44 | 5461 s | 57 | 30471 |
| **run 2b (graded)** | **12:52:43** | **14:18:33** | **5150 s** | **49** | **30479** |

They did not overlap each other, but the constraint said one run and there were two. **The grading
above uses run 2b only** — 2a's subject commit was never captured (its launcher wrote no
`head_at_launch`), so it is unattributable, and folding an unattributable row into the store would
age every node a second time for a run nobody can locate. It is recorded here as a **replicate**,
which is what it is worth: independently, ninety minutes earlier, at a different commit, the same
two facts held — the red count is ~50 not ~830, and the run took ~5400 s. **The replicate
strengthens C1/C2/C3 and independently confirms C6's refutation.**

## The head-attribution defect fired live on run 2, exactly as predicted one section up

The prediction above — *"the row written by the 12:52:44 run will name the wrong commit"* — **is
now an observation.** The run's own code called `reg.record(head_sha=prc._head_sha())`, the
pre-`378c4d34d` shape, so it labelled its row with the live HEAD at 14:18. That was **`5eecfd04f`,
a `SALVAGE(auto)` commit another lane created at 14:14:27** — 82 minutes after this suite started.
A row naming a commit that did not exist when the measurement began is the defect at its purest.

**The row landed in the store carries `f5b19b43f`, the true subject**, taken from
`/var/tmp/census_run2/head_at_launch.txt` — written by the launcher at 12:52:43, *before* the run,
which is why it is evidence and not a reconstruction. The row was regenerated through
`reg.record()` from the run's own `census.json`, not hand-transcribed: **the failure mode that
produced run 1's countless row is not repeated here.**

## The 49, and their route into the draw

`docs/staging/reference/HEAD_RED_REGISTER.md` is re-rendered and names all 49 with their
recurrence counts. It is a BLOCKING register in the staging root, so it is drawn as work while the
count is non-zero — which is what `bc57c8e30` built it for. Shape of what is owed:

- **`tests/sim/test_renewable_capacity_trend.py` — 25 of the 49**, one file, first seen this run.
  Over half the entire backlog is a single module and it should be triaged as one item, not 25.
- **`tests/simulation/test_publish_market_feed.py` — 4**, also first seen this run.
- **The ten C3 residuals — the only nodes at `runs_red: 2`.** These have now survived two censuses
  and an environmental change that removed 781 of their neighbours. **They are the oldest debt in
  the register and the honest first draw.**

`FileNotFoundError x29` is the dominant cause and was 2 in run 1. Fourteen-fold, unexplained,
flagged under C4 above, and it is not assumed to be the same thing as the 26 `sim` reds until
somebody reads a traceback.
