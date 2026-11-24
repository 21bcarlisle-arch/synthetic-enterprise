**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A landing that touches the ledger outruns the gate deadline under ordinary load, and the only door then refuses it

Found by the delivery seat, 23 Nov 2026, while landing the MSC replacement win (claim
`verify-msc-replacement-win-landing-v3`; salvage `ae573846b1` against base `4f9da23163`, nine paths).

**What happened.** The MSC change touches `saas/ledger.py`, `company/finance/double_entry.py`,
`company/finance/accounting_close.py` and `simulation/run_phase2b.py`. `[impact-select]` maps its 7
mappable changes to **1,074 impacted test files** through the static import graph (`/tmp/msc_land/sel_run.log`).
`tools/pre_commit_test_gate.py` runs them in one serial pytest, and `tools/surgical_land.py` kills the
hook at `GATE_TIMEOUT_SECONDS = 3600`.

> **Corrected 23 Nov 19:10Z (delivery seat). The two sentences above are wrong, and they are kept
> because what follows was built on them.** 1,074 is what `tools/select_impacted_tests.py` returns.
> Neither the commit hook nor `surgical_land` calls that tool; only `background/publish_scope.py`
> does, for the publish path. The hook selects with `pre_commit_test_gate.select_targets`, and for
> this pathspec that gives **181 files and 3,101 tests** (`gate_counts.txt`). For msc6's pathspec,
> which adds the two conftests, the flat-supplier test and the MSC test, it gives **183 files**
> (`/var/tmp/se-msc-keep/sel_msc6.txt`). So the gate was killed at 88% of about 3,100 tests, which
> is about 2,730 tests in the hour, not 13,000. The sharding measurement below split the 1,074
> files (`shard/s0-3.txt`, 268 or 269 each), not the hook's 181. **It measured a selection no gate
> runs, so it neither supports nor refutes sharding the real gate.** What it does show still holds:
> each whole-run fixture is paid again in every process that selects it.

- v2 (22–23 Nov): refused unrun. The hook timed out while the gas chain gated `run_phase2b.py` beside it.
- v3 (10:48–11:48Z, 23 Nov, `/tmp/msc_land/land3.log`): refused, `timed out after 3600 seconds`, with the
  pytest progress at **88%** and no failure printed. The 11.8 GB cut012 book and other lanes' suites
  were running at the time (16 cores; load 4–6).

There was no red in either attempt. The door could not finish asking.

**Why it matters.** The gate never fails a change like this. It times out on it, and the timeout
looks the same as a refusal. A change to the most widely imported money modules is exactly the
change that most needs gating, and it is the one most likely to run past a fixed deadline that was
set for publish-commit symmetry (`surgical_land.py:873`), not for selection size. Nothing in the
door tells the lander, before the hour is spent, that the selection will not fit.

**Not done here (correctly).** The deadline was not raised and the selection was not trimmed by
hand. Both would weaken a gate in order to land one change. v4 was re-launched unchanged at
11:56Z on a lighter machine (`/tmp/msc_land/land4.sh`, end marker
`/var/tmp/se-msc-land4-ended-20261123.txt`).

**Candidate remedies (for the harness lane; none taken):**
1. Let the gate predict its own run time from recorded per-file durations, and refuse up front with
   that named cause when the selection cannot fit, rather than after an hour.
2. Run the selected files in parallel (xdist) inside the gate, if the suite tolerates it. This needs
   a measurement first, because some controls share on-disk state.
3. `ADVISOR_QUESTION_WOULD_BATCH_THEN_BISECT_LANDING_CUT_GATE_TIME_2026-10-15.md` asks a related question.

**Done means:** a landing whose selection cannot finish inside `GATE_TIMEOUT_SECONDS` is either told
so before it starts, or is given a gate that finishes. A test should show a 1,000-file selection
under a recorded-duration model being refused with the named cause rather than killed.

## 23 Nov 13:00–14:10Z: v4 timed out too, and remedy 2 was measured and refuted (delivery seat, claim `verify-msc-replacement-win-landing-v4`)

v4 (11:56–12:56Z, `/tmp/msc_land/land4.log`) was killed at the hour at 88% with no red, like v3.
So the cause is the selection's size, not the load on the machine.

**Prediction, written before the run:** four round-robin shards of the 1,074 files would each
finish in roughly a quarter of the ~68 serial minutes, worst shard ~30 min (bounded by
`test_run_phase2b.py`'s ~26 min).

**Measured** (`/tmp/msc_land/shard/`, 4 concurrent pytests in the MSC worktree, `-x`, 13:00Z on;
the box also carried another lane's landing gate and an operational suite; box PSS peak of the
shards 8.2 GB):

| shard | tests run before stop | wall |
|---|---|---|
| 0 | 1,476, then a red | 3,397 s |
| 1 | 2,040, then a red | 1,604 s (re-run after two census reds, now fixed) |
| 3 | 1,687, then a red | 2,852 s |
| 2 | still running at 14:05Z, 53% | >3,800 s |

Together that is ~7,000 tests in ~55 minutes. The serial gate managed ~13,000 in 58 *(wrong: the
serial gate's selection is 3,101 tests, so 88% is about 2,730. See the 19:10Z correction above)*. **The
prediction is refuted. Sharding halved the throughput.** Each shard pays the whole-run fixtures
again: one setup alone, `test_the_flat_supplier_policy_makes_no_retention_offer`'s, took 1,660 s.
Four shards running together then contend for a box that is already loaded. The sharded gate was
written and its control mutation-proven, and it is **not landed**. It is kept at
`/tmp/seat_gate_shard/park/` as evidence only.

**What the run found instead:** the selection is not green at origin, so v2–v4 would have been
refused at the end even with a longer deadline. Four reds, each also red **at origin alone**
(6613986bc9), none caused by MSC:

1. `tests/background/test_an_empty_git_dir_made_scratch_immortal.py` (2 tests). They stubbed
   `resource_headroom.admitted`, but the census has queued through `queued` since a285086483, so
   they read the box's free memory. **Fixed, on origin as 9af8c4a14.**
2. `tests/background/test_two_reader_review.py::test_the_tick_spawns_nothing_when_the_dial_holds_it`:
   a wall-clock time bomb. Past `REVIEW_DATE` (11 Nov) the tick returns before it asks the dial.
   **Fixed in this commit** by pinning `_now` inside the trial window.
3. `tests/simulation/test_a_departure_rolls_on_exactly_one_named_leg.py::test_every_departure_booking_is_gated_on_the_resolved_decision_leg`:
   reg 6C's erroneous-gain return (cc9f08ae3d, `simulation/run_phase2b.py` ~3715) books
   `churned_billing_accounts.add` with no `commodity == _decision_leg` guard. Today a won switch
   is one leg, so its own commodity is its decision leg, and the double-roll the control guards
   cannot happen yet. A future dual-leg win would change that. **Not fixed: it is a world change
   to `run_phase2b.py`, whose gate selection is this same hour-long one.** The candidate fix: gate
   the booking on `commodity == _decision_leg`, and record a riding-leg return in
   `erroneous_gains_not_returned` with a named reason rather than dropping it.
4. `tests/company/test_the_per_account_engagement_estimate_ranks_better_than_the_channel_alone.py::test_both_arms_reach_their_own_branch_of_the_estimator`:
   the null arm now returns a finite prior strength on the live roster, which has grown with the
   gas-only wins. It is C29's lane, and it needs a judgement on the estimator. **Not fixed.**

   **Decided 23 Nov: (b), the control was keyed to today's answer.** The null arm was printed
   before choosing, on the live roster (628 households) and on random halves and three-quarters of
   it (3 draws each). It left the prior in all 7 cases, with strength 47–244 (dispersion z
   0.44–1.28) and a lift of −0.01 to −0.11. The planted arm on the same books had strength
   8.9–11.8 (z 4.0–6.7) and a lift of +0.23 to +0.26. Under a true null, the moment excess is a
   noise term centred on zero, so it is positive about half the time at ANY roster size. The old
   leg's `None` was a coin the roster's growth happened to turn. The estimator's response to a
   weak excess is already proportionate: at strength 65, a five-anniversary account moves 7% of
   the way from its channel rate toward its own record, against 35% when planted. (a) would need
   a significance level to gate on, and nothing published sets one for this. That is a picked
   constant standing in for a property the estimator already has. Re-keyed to the property: the
   null arm's prior is either `None` or weaker than the planted arm's on the same book. The
   collapse branch is asserted reachable on a book with no within-channel spread. The null's
   ranking stays graded by its own leg (lift < 0.10). Open, not acted on: on the null the
   estimate ranks slightly WORSE than the channel (lift ≈ −0.06). Part of that is the Spearman
   tie structure (two channel values against 628 distinct estimates), so it is not yet a
   decision cost.
   **Mutation-proven:** each of these turns the re-keyed leg red (1 failed), and the file
   is 8 passed unmutated. (1) Never collapse: return a finite strength where there is no excess.
   (2) Always collapse. (3) A strength that ignores the size of the excess.

**Next remedy, by the measurement:** the selection's content, as was done for reg 6C's billing
trigger. The slowest tests in three shards were dominated by `tests/background/` files
(`test_supervisor.py`, about ten tests at 80–216 s each; `test_daily_self_note.py`, about seven at
60–216 s). That is supervisor and self-note machinery. Ask, file by file, why a change to
`saas/ledger.py` / `company/finance/*` selects it, and whether that reason holds. The MSC
landing also still needs reds 3 and 4 settled first.

## 23 Nov 19:10Z: what msc6 changes in the hook's own selection, and what it leaves (delivery seat)

The selection's whole-run fixtures, read from the code at origin `c7b423b49a`:

| fixture | window | shared? |
|---|---|---|
| `phase2b_2016_2018` (`test_run_phase2b.py`, `test_run_phase2b_event_log.py`) | 2016–2018 | one session run since 83570bd1c |
| flat-supplier test, current arm | 2016–2017 | **msc6 makes it read `phase2b_2016_2018`** (fixture moved to `tests/conftest.py` so a file outside `tests/simulation/` can reach it). This saves one run, ~830 s of the 1,660 s setup |
| flat-supplier test, flat arm | 2016–2017 | no: it is the arm under test, run under `FLAT_SUPPLIER_POLICY` |
| `_phase2b_every_pre_css_win_erroneous` (reg 6C) | 2016–2017 | no: it monkeypatches the erroneous-transfer share to 1.0 for the whole run |

The deadline is not raised and no file is dropped from the selection. This correction landed on its
own ahead of MSC (the MSC gate cannot start before ~06:00Z on 24 Nov). land7 runs msc6 only after the
s.12g book (pid 65649) has ended, unlike land5, which gated beside it. A serial `--durations=40`
run of the 183-file selection is logged at `/var/tmp/se-msc-keep/durs_serial.log`. If the book ends
first, the run is interrupted so that land7 has the machine. The durations table goes here when
that run ends.

## 23 Nov 20:10Z: the durations table, and the gate does not fit even with msc6 (delivery seat)

**Measured** (`/var/tmp/se-msc-keep/durs_serial.log`): one serial run of the hook's own 183-file
selection, on origin `c7b423b49a` + msc6, with `--durations=40`, niced, beside the s.12g book (one
core of 16). **3,331 passed, 2 skipped, 1 xfailed in 4,604 s.** It was green and took 1,004 s
longer than `GATE_TIMEOUT_SECONDS`.

| setup | s | what it runs | can it read the shared run? |
|---|---|---|---|
| flat-supplier test (first user, so it pays `phase2b_2016_2018` too) | 1,542 | shared 2016–2018 + flat arm 2016–2017 | flat arm: no, it is the arm under test |
| `test_run_phase4c_on_phase2b.py::main_result` | **1,097** | `run_phase4c_on_phase2b.main(report_end="2018-12-31")`, **which runs `run_phase2b` over the shared run's own window again** | not as written: see below |
| `test_run_phase2b.py::_phase2b_every_pre_css_win_erroneous` (reg 6C) | 557 | 2016–2017, share patched to 1.0 | no |
| `test_collections_journey.py::answered_live_run` | 525 | 2017, plan answers patched to `high` | no |
| `test_collections_journey.py::live_run` | 176 | 2016 | not without re-checking its window-keyed legs |
| every other test, slowest single call | 71 | | |

The five whole-run setups take 3,897 s, which is 85% of the gate. Every other call is 71 s or less.
**What holds the gate is `tests/simulation/test_run_phase4c_on_phase2b.py`.** It repeats the 2016–2018
run that the session already holds.

**Why 4c cannot simply be handed `phase2b_2016_2018`.** `run_phase4c_on_phase2b._get_all_customers()`
reads `run_phase2b.ACQUIRED_CUSTOMERS`, `SUCCESSOR_CUSTOMERS` and `incoming_occupant_supply_points()`,
and the most recent `main()` in the process fills those. In the gate, the flat arm and reg 6C run
after the shared fixture, so 4c would bill against another run's acquired customers. Also,
`main` writes `phase2b_result["switching_gsop_credits_refused"]` (line ~733), and the shared dict
must not be mutated. **The lever, not built here:** the shared fixture snapshots those run-filled
lists beside its result. `run_phase4c_on_phase2b.main` then takes an optional
`(phase2b_result, run_state)`, deep-copies the result and reads the snapshot. A control would show
4c's output on the shared run equals its output from its own run. That saves about 950 s and brings
the measured gate to about 3,650 s. That is still not inside the hour with margin, so the
`live_run` window is the next lever.

**Prediction for land7 (msc6, after the book, written before it runs):** a timeout at about 90–95%,
no red. The book's absence frees one core, and the gate is a serial process. If it lands anyway,
this prediction was wrong, and the margin was the box's load and not the selection.

**The post-s.12g book is held** by the `commit: null` MSC row in `background/next_book_requires.yaml`
(d5a209bac). It holds until MSC lands or the file lapses after 24 Nov. If land7 times out as predicted,
the hold costs the book its 24 Nov slot. Deleting the row is the reverse (see the row's comment).

**land7's outcome, 24 Nov 05:38Z: UNGRADED.** The prediction above (timeout at 90–95%, no red) was
never tested: land7 was refused in 8 s at the stale-copy check, before any test ran, because msc8
deletes the `phase2b_2016_2018` fixture 83570bd1c added to `tests/simulation/conftest.py`. That
deletion is a deliberate MOVE to `tests/conftest.py` (with `book_after_the_run`, so phase 4c reads
the shared run); 83570bd1c does not share with phase 4c, so neither hunk duplicates the other.
`refresh_to_head` is the wrong door: restoring the sub-conftest copy would shadow the root fixture
for `tests/simulation` and bring back the second whole run. The door is `--drops`.

**The hold is released.** The `commit: null` MSC row is deleted from `next_book_requires.yaml`
(24 Nov), so the post-s.12g book builds without MSC; MSC enters the following book.

**Prediction for land9 (msc8 + `--drops tests/simulation/conftest.py`, gated only after the
post-s.12g book has ended and never beside rankq; written 24 Nov before it is armed):** the
stale-copy check passes. The gate's selection takes 3,300–3,700 s: msc8 removes phase 4c's own
1,097 s run from the 4,604 s serial run measured for msc6 (which already shared the run with the
flat-supplier file), leaving about 3,500 s. So it is a coin toss against the 3,600 s deadline, decided by load and not the selection,
with no red. If it times out, the fix is shrinking the selection, never raising GATE_TIMEOUT_SECONDS.
Script: `/var/tmp/se-msc-keep/land9.sh`; log `land9.log`.
