**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# The director's "a save is never paid for by the stayers" control is red at origin, and no red census holds it (2026-10-14)

**Fate (2026-10-14):** ATOM -- in hand: the stayers control and its bisect are running, and the director let them finish (2026-10-14 18:15).

`tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py` fails 2 of 8. The two failures are the
same on both sides of e3b5ed01a:

| test | 58e1e8905 (origin, e3b5ed01a's parent) | e3b5ed01a (writer one's basis) |
|---|---|---|
| `test_a_saved_term_ends_and_stayers_renew_after_it` (line 76) | FAILED | FAILED |
| `test_no_stayer_price_moves_with_the_save_price` (line 95) | FAILED | FAILED |
| the other six | pass | pass |

Run 2026-10-14 in `/var/tmp/se-w1-origin` and `/var/tmp/se-w1-basis`, 1h45m each at load ~47. The logs are
`/var/tmp/w1-basis-out/stayers-{origin,fix}.log`.

**What fails.**

- **Line 76 is the precondition.** The `on` and `placebo` arms no longer save the same households.
- **Line 95 is the director's condition** (2026-10-08). It lists stayer price moves on both sides. Pytest
  truncated the list, so the count is not known; the first rows carry different unit rates on the two sides.

Line 95's red cannot be read while line 76 is red. If the arms save different households, a stayer's price
can differ for that reason alone. So the control currently says nothing either way about whether the stayers
pay for the save. That is why this finding is BLOCKING: the save has been live by curriculum since
2026-10-10.

**Not established:**

- **When it went red.** The last commit to the test is afd818b22 (2026-10-11). The test is slow, so it is
  probably outside every selection that ran since then.
- **Why it is held nowhere.** It is in neither `head_red_observed.json` nor `head_red_baseline.json`. Whether
  the census skips it for its runtime is the first thing to ask.

**What it changed.** The writer-one claim had held e3b5ed01a off origin on exactly this comparison. Its holder
died before the comparison ran. Both reds are already present at origin, so e3b5ed01a did not cause them, and
it is promoted on that basis. The regrade5 arms (price match against risk tiers, plus the save's S1) wait on
that promotion.

**Next, one variable at a time:**

1. Bisect line 76 between bfcae065d (2026-10-08, where the control was written green) and 58e1e8905. The
   control takes about 50 minutes on an idle machine, so bisect with `--report-end` shortened only once a
   shorter window is shown to still end a saved electricity term. The docstring says the first one ends on
   2018-06-20.
2. Find out why the census cannot see this test.

---

## Delivery seat, 2026-10-14 13:20 BST — two premises corrected, the range narrowed, and the divergence located

**Correction: a census DOES hold this test.** The note above read
`docs/observability/head_red_observed.json`. That is the LEGACY path. It was untracked on 2026-09-10
(e4aa02359), and its last run is dated 2026-09-15. The live store is `.head_red_observed.json`
(`background/head_red_register.OBSERVED_PATH`), and it reads:

| census run | HEAD | line 95 | line 76 |
|---|---|---|---|
| 2026-10-10 05:41Z | cf8706023 | red (NEW RED) | green |
| 2026-10-11 05:45Z | ab1bf89f7 | red | green |
| 2026-10-12 05:56Z | ed9aa25eb | **green** | **green** (setup 1335s, so it ran) |
| 2026-10-13, 2026-10-14 | — | deferred by the memory governor, suite not run (UNPROVEN) | — |

So the census has held the test since it was written. It cannot hold today's red because the
census has not run since 2026-10-12. The resident long jobs' declared peaks exceed the 23 GB
budget, so the governor defers it. The question "why is it held nowhere" is therefore spent. The real
gap is narrower: **two nights of UNPROVEN census are not surfaced as a hole in the red record.**
Whether that is filed elsewhere is checked below.

**The bisect range is `ed9aa25eb..58e1e8905`, not `bfcae065d..`.** Line 76 was green at ed9aa25eb.
The range holds 48 commits that touch `simulation/`, `company/`, `saas/` or the arms tool, instead of 520.

**Where the arms split (read from `/var/tmp/w1-basis-out/stayers-origin.log`, no new run).** The
first differing saved row is index 18: `on` saved SYN-2016-365 on 2017-08-13, and `placebo` did not
save it. Its record is identical in both arms up to that point. It is the same term 0
(2016-08-13→2017-08-13, £99.69/MWh, net £24.62), it was never saved before, and both arms print the same
`p_retain=0.7336 roll=0.9391` for it. In `placebo` it churned ("Fresh acquisition failed … £28" is
the replacement attempt). So the two arms gave this household a different save answer before the
save had ever touched it. Some input to the save offer was already arm-dependent by 2017-08-13, and
an arm-dependent company-wide input is exactly what this control exists to catch.

The test makes that flip easy to trigger. `world_save_response_scale` is 50, so the household stays when
`p_stay_at_save − p_stay_at_offer ≥ (0.9391 − 0.7336)/50 = 0.0041`. A difference of pennies in the save
rate or the renewal rate is enough.

**Pre-registered before the probe returns** (probe:
`/var/tmp/stayers-probe/probe.py`, run in an origin worktree at ec192c93d. It dumps both arms' full
save logs, both account-state logs, and the stayer-move list without truncation):

- P1. SYN-2016-365's 2017-08-13 row has the same `p_stay_at_offer` in both arms but a different
  `save_unit_rate_gbp_per_mwh` or `renewal_unit_rate_gbp_per_mwh`. Confidence about 0.7: the renewal or
  floor price is the only input the scaled answer is that sensitive to.
- P2. At least one non-saved account-state row has a different unit rate before 2017-08-13. If P2 holds,
  the stayers were already paying before the first saved term ended, and line 95 is the primary red
  and line 76 a symptom. If P2 fails, the channel is local to the save offer.

**On the census's staleness: no new control.** `HEAD_RED_REGISTER.md` already prints "Last run
2026-10-12T05:56:43 at HEAD ed9aa25eb", and the governor's deferral names its reason in the journal.
A reader can see the record's age. The census will hold line 76 at its first night with room.

**P2 answered from the bytes on disk, without a run: before the split, no stayer's price moved.**
I parsed every `term N (start→end): unit_rate=` line of both arms in `stayers-origin.log`. Before
2017-08-13 exactly 18 terms differ, and they are the 18 saved terms, each at on/placebo = 0.850 (the
15% cut). P2 is refuted for the pre-split window. Whatever flipped SYN-2016-365 is not a stayer's
price, and the channel sits in the world's answer to the save.

**The candidate channel, named before any run tests it: the rival sees the save.** After a save,
`unit_rate` is the billed rate, and `_competitor_position_ledger.observe(term_start_str, unit_rate, …)`
runs a few lines later. In `on` the rival's ledger records the save price; in `placebo` it records
the renewal price. `CompanyPositionLedger` is "the company's published position as a rival would see
it". A quarter later the rival's reference differs between arms, and so does every later household's
P(stay). At `world_save_response_scale = 50`, a few ten-thousandths of P(stay) flip a save. The
channel already existed at ed9aa25eb (line 3513 there), so if it is the cause, something in the range
made it bite rather than opened it.

It is also wrong on its own terms. A save is a reactive price offered only to a household that has
already chosen to leave. It is on no tariff list a rival or a comparison site reads.

**Prediction for the one-variable run** (origin ec192c93d plus only this change: the ledger records
the pre-save rate; worktree `/var/tmp/se-stayers-fix`): line 76 GREEN, about 0.7. Line 95: I cannot
yet say. If line 76 is green and line 95 still red, the remaining moves are the director's
condition proper, read on equal arms.

---

## Worker tick, 2026-10-14 14:47 BST — both runs are in flight as units of their own

**The one-variable run had never started.** `/var/tmp/se-stayers-fix` holds the patch above
(`simulation/run_phase2b.py`: `_rate_the_rival_sees = unit_rate` before the save block, and that rate
fed to `_competitor_position_ledger.observe`), but `/var/tmp/stayers-probe/fix-launch.out` is empty, and
`/var/tmp/w1-basis-out/stayers-fix.log` dates from 11:47, before the patch was written. A second
lane also queued a probe and a first-parent bisect (`/var/tmp/stayers-probe/handoff.sh`) at 14:38.
Its launcher died with its tick: the log stops at its first `QUEUED` line and no process survives.
A queued retry loop runs inside the tick's own cgroup, and setsid does not take it out.

Both are now launched with `--wait-for-pid 3022845` (termcost-arms-floor-a, 11,200 MB declared), so
each unit exists at once in its own cgroup and starts the moment that run exits:

- `longjob-stayers-fix-one-variable`: the whole stayers control in the fix worktree →
  `/var/tmp/stayers-probe/fix-run.done`. The prediction is the one filed above, before any run:
  line 76 GREEN at about 0.7, line 95 not yet called.
- `longjob-stayers-probe-and-bisect`: the probe at origin 55701bb84, then the endpoint check and
  the bisect, as described in `handoff.sh` → `/var/tmp/stayers-probe/ALL_DONE`.

If line 76 goes green on the fix, the bisect only says which commit made a channel that already
existed start to bite. The fix lands on the one-variable evidence, without waiting for the bisect.

---

## The one-variable run read, 2026-10-14 16:38 BST: both lines green, and the fix lands

`longjob-stayers-fix-one-variable` ran the whole control in `/var/tmp/se-stayers-fix`, at origin
`f6e806b8f` plus only the rival-ledger change. `simulation/run_phase2b.py` has not changed between
`f6e806b8f` and the origin it lands on. Before it could run, the box had to be freed:
termcost-arms-floor-a was stopped ungraded, and the reasons are in `58d629a20`. The run took 39 min 12 s
and wrote `/var/tmp/stayers-probe/fix-run.done`. All 8 tests passed.

| line | at origin (above) | on the fix | prediction filed before the run | grade |
|---|---|---|---|---|
| 76 `test_a_saved_term_ends_and_stayers_renew_after_it` | FAILED | **PASSED** | GREEN, about 0.7 | **TRUE.** The arms save the same households, a saved term ends inside the window, stayers renew after it, and the save price is billed |
| 95 `test_no_stayer_price_moves_with_the_save_price` | FAILED | **PASSED** | not called | **The director's condition holds on equal arms.** `stayer_price_moves(...) == []`, so the full list of stayer moves is empty |

**What this establishes.** The rival's ledger reading the save price was the channel. It is the only
change between a red and a green control, so the attribution is one-variable. This was a world-fidelity
leak: a reactive, unlisted price offered only to a leaver reached the market reference, and through it
every later household's P(stay). The stayers did not pay for the save. The world was mispricing the
rival.

**What it does not establish.** Which commit in `ed9aa25eb..55701bb84` made a channel that already
existed start to bite. That is the bisect (`the-save-stayers-control-read-the-bisect`), still queued
behind the probe. It no longer gates anything. When it reads, it should be graded against this result,
and an endpoint that turns green once this fix is merged is expected, not a contradiction.

**Discharged:** `tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py::test_a_saved_term_ends_and_stayers_renew_after_it`, `tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py::test_no_stayer_price_moves_with_the_save_price` -- the rival's ledger observes the pre-save rate, and the director's stayers control passes 8 of 8 on that one change (lines 76 and 95 both green)

## The bisect read, 2026-10-14 22:05 BST (recorded 2026-10-15 by the delivery seat)

`longjob-stayers-probe-and-bisect` ended and wrote `/var/tmp/stayers-probe/ALL_DONE`. It ran a first-parent bisect over
`ed9aa25eb..55701bb84` on the index-18 comparison, without the fix. The first bad commit is **`03a0b66da`**, which floors
writer 1's renewal discount at the term's cost floor. Before it, the on and placebo arms saved the same households (22 and 22).
From it on, the on arm saves one more (23 against 22) and they diverge at index 18 (SYN-2016-365 against SYN-2016-391).
This fits the channel above. The cost floor moved what a save is billed at, the rival's ledger read the moved price, and
P(stay) moved with it. It is graded against the one-variable result as expected, not as a contradiction. The step log is
`/var/tmp/stayers-probe/bisect_steps.log`.

The first landing of this fix (`land-fix4`, 19:10) was queued on the memory budget and died at 19:51 partway through the
test gate without committing. The delivery seat re-landed it from an isolated worktree at origin `9ab9b7959`, where
`simulation/run_phase2b.py` is still unchanged since `f6e806b8f`. That second landing (`/var/tmp/stayers-land2/land.log`,
04:47 on 2026-10-15) was refused because the commit gate ran past its 3600 s limit. The stayers control was not the
cause: the gate's own `select_targets` does not pick that file for a `run_phase2b.py` change. It picks 54 others,
whole-loop simulation tests among them, and the box was loaded. The fix itself was then on no ref except fork_salvage's
`e7c26dd51`, which is now held at `refs/preserved/stayers-fix-e7c26dd51` on origin.

**Third landing, 2026-10-15 05:50 BST (worker tick).** The fix's two hunks were applied to a fresh worktree at origin
`e0492757e`, where `simulation/run_phase2b.py` is still byte-identical to `f6e806b8f`. Because the gate does not select
the control, it is re-run on its own at that base (`/var/tmp/stayers-land3/control.log`). That re-run's verdict is
recorded beside this finding's move to `done/`.

## Closed, 2026-10-15 (worker tick)

The control was re-run on its own at **`4492d17bd`**, the merge that put `cc258be0a` on origin, in a clean worktree at that
commit (`/var/tmp/se-stayers-land4`, unit `longjob-stayers-control-at-4492d17bd`, log `/var/tmp/stayers-land3/control.log`).
It waited 7,125 s for the HEAD-green census to exit, then ran `tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py`:
**8 passed in 1,637 s, EXIT=0**. Lines 76 and 95 are both green at the commit that actually landed, as they were in the
one-variable run at `f6e806b8f`. The director's condition, that stayers never pay for a save, holds at origin again, and
this finding no longer blocks lane B_commercial.

What stays open: the commit gate still does not select this control for a `simulation/run_phase2b.py` change, so a
regression arrives only through the HEAD-green census. The census suite selects it: the file is not in `HEAVY_IGNORES`. The value-arms
re-take on the term-cost base can launch at `4492d17bd` or later.

## Worked 2026-10-14 (worker tick, claim `the-save-stayers-control-is-red-at-origin-bisect-and-hold-it`)

**Correction, beside "Why it is held nowhere".** The census does hold this test. The file read above
was the *legacy* tracked `docs/observability/head_red_observed.json`. Nothing has written it since
2026-09-10 (`background/head_red_register.py`, `LEGACY_OBSERVED_PATH`). The live observation is the
untracked `docs/observability/.head_red_observed.json`, and it reads:

| census run (head) | line 95 `test_no_stayer_price_moves_with_the_save_price` | line 76 |
|---|---|---|
| 2026-10-10 05:41 (cf8706023) | red | green (not listed) |
| 2026-10-11 05:45 (ab1bf89f7) | red | green |
| 2026-10-12 05:56 (ed9aa25eb) | **green** (`currently_red: false`) | green |
| 2026-10-13 03:37 | not run: deferred by the memory governor ("UNPROVEN ... register not updated") | — |
| 2026-10-14 03:38 | not run: deferred (termcost-arms-floor-a declared 11,200 MB) | — |

So the census stopped seeing it because the census stopped running, not because it skips the test.
It has been deferred two nights running. Nothing needs to change to "make the census hold it": the
next census that is admitted will record it. What is owed is the governor's two-night deferral,
which is the census's own standing condition and is not this item's to fix.

**What this does to the bisect.** Line 76 was green at ed9aa25eb (the 2026-10-12 census head, an
ancestor of origin). The range is ed9aa25eb..58e1e8905, not bfcae065d..58e1e8905: 263 commits,
about 20 first-parent commits touching `simulation/`, `company/`, `saas/` or `sim/`, so about 5
bisect steps instead of 9.

**What the failing run already says about line 76.** The first 18 saves are identical in both arms.
At index 18, `on` saved SYN-2016-365 (term 2017-08-13) and `placebo` saved SYN-2016-391 (2017-09-05),
and `on` holds one more save (SYN-2016-347, 2018-08-04). That is a divergence in **2017-08**, ten
months before the first saved electricity term ends (2018-06-20). So the cause is *not* an ended
saved term teaching the premium. Something that reads the save price *during* a saved term reaches a
later household's renewal rate or its roll. Line 95's first listed move is SYN-2016-406, electricity,
off 107.23 / on 106.78 £/MWh: a stayer priced 0.4% *lower* in the `on` arm.

**Prediction, filed before the probe below returns.** Stayer price moves begin before 2017-08-13, and
the earliest is a renewal priced after a save's first bill has posted. Probe: both arms to
2017-12-31 at origin 55701bb84, every stayer row diff with its keys
(`/var/tmp/stayers-probe/probe.py`, launched under `launch_long_job` as `stayers-probe-2017`).

**In flight (2026-10-14 14:38 BST).** One queued long job, `longjob-stayers-probe-and-bisect` (launcher
under setsid; log `/var/tmp/stayers-probe/launcher.log`). It waits on termcost-arms-floor-a's 11,200 MB
declaration and then runs, serially, at a 3,500 MB peak (a full-book arm measured 2.2 GB):

1. the probe at origin 55701bb84 to 2017-12-31 → `/var/tmp/stayers-probe/out-2017.json`: both
   arms' save logs, every stayer price move sorted by term start, every differing account-state
   key, and the rows only one arm holds;
2. ed9aa25eb asked rather than assumed: if its arms do not save the same households to 2017-09-30,
   there is no bisect and the census's green there was not this criterion;
3. `git bisect run --first-parent 55701bb84 ed9aa25eb` on that criterion, in
   `/var/tmp/se-stayers-bisect`, one line per commit in `/var/tmp/stayers-probe/bisect_steps.log`.
   `ALL_DONE` marks the end.

**The criterion's limit, stated before it runs.** "Same saved households to 2017-09-30" is narrower
than line 76, which asks the whole window to 2018-09-30. A commit whose divergence starts after
2017-09 grades good and moves the blame later. At origin the divergence is at 2017-08-13, so the
named commit must be confirmed by running line 76 itself at that commit and its parent before the
blame is written here as fact.
