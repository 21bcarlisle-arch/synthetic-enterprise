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
