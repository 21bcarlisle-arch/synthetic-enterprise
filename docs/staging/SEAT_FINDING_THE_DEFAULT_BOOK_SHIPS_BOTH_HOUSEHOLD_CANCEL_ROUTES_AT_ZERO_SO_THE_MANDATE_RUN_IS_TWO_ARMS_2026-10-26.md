**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_41_a_household_cancels_its_mandate_as_its_own_act`

# The default book ships both household-cancel routes at zero, so the mandate run is two arms, and its predictions are filed before either answers

Drawn as `the-mandate-run-grades-pb8-and-w2-41-on-one-fresh-book` (worker tick, 26 Oct 18:24Z).

**Premise, re-measured at draw.** No finished run carries 1e6083838, bf56dd579, 71cb7debc and
f89db6ff3. The Monday run 4ae8da9b0f carries none of them, and the last basics run (12246cbae,
26 Oct 01:21Z) predates all four. So the ask was not spent. B13's pid 609471 is gone and nobody
claims B13. Item 3 landed as c77a181fa4. The shared tree's simulation/ still differs from origin on
four files: the superseded meter_reads draft the 26 Oct finding names, five-week-old
churn_journey dirt, and unlanded B13 L2 work in run_phase2b.py (`strike_gas_fixed_term`). None
of it reaches the run, because both arms run in a locked origin worktree:
`/var/tmp/se-mandate-run-67a893e749` (origin 67a893e749, all four commits verified ancestors).

**What the default book cannot answer.** Both routes by which a household ends its own mandate
ship at 0 on the default book:

- `method_own_reasons_cancel_share` (PB8, `simulation/payment_method_dynamics.py`): default 0.0,
  low 0.005, high 0.02.
- `dd4b_mandate_cancel_share_at_shock` (DD4b, `simulation/dd_shock_response.py`): default 0.0.

`bacs_rails.PAYER_CANCELLATION_PROBABILITY` is None too, with a named GAP: Bacs publishes no ADDACS
reason-code split. So a default-book run produces **zero ADDACS 1 events by construction**. It grades
the desk's own stops (on returns) and net, and it cannot grade W2_41. That is not a defect in the
toggles. The rate is unpublished and "off" is the honest default. But "grade W2_41 on the default
book" asks for something that does not exist.

**So the run is two arms, one variable apart.**

| arm | unit | the one change | answers |
|---|---|---|---|
| A, default book | `longjob-mandate-run-67a893e749` | none | the desk's stops on returns and what is owed at them; f89db6ff3's net |
| B, own-cancel low | `longjob-mandate-run-67a893e749-own-cancel-low` | `own_cancel_share` 0 → 0.005 (prepayment take-up held at 0; the `low` preset would have moved it to 0.3 as well, so it is pinned) | ADDACS 1 counts, when they reach the desk, and what is owed at each stop |

Scripts: `/var/tmp/mandate-run-scripts/{arm.py, arm_b.py, grade_d.py, grade_net.py}`. Outputs:
`/var/tmp/mandate-run-out-67a893e749{,-own-cancel-low}/`. Both were queued at 18:26Z behind
an in-flight `surgical_land`, because landings come before experiments.

**Leg (d), defined before the answer.** `grade_d.py` replays `dd_collection_book._run_rails` over
each arm's own issued bills and behavioral records. These are the inputs, and seed 42 is the seed,
that the money side and the billing ledger use. It taps the desk's two stop doors. The grader
reports counts per fuel leg and per household (`billing_account_of`), against DD legs and DD
households. "Owed at the stop" is what the desk can see: DD presentations returned unpaid since the
last collected one, up to the stop date. It is not the arrears balance and is not differenced
against it. "Reached the desk before a collection failed" means no presentation to that customer
returned unpaid in the 45 days before the ADDACS available date.

**Prediction 1, filed now: W2_41's "before any collection fails" claim does not hold in the run.**
`_run_rails` builds the ADDACS 1 record only from a collection that has already come back
"instruction cancelled" (`shock.cancel_return`), dated the next working day after that return.
`dd_shock_response`'s docstring says so: "the first collection presented after it comes back
'instruction cancelled'". So arm B should show every ADDACS 1 stop with a failed collection first,
and `reached_desk_before_any_collection_failed` = 0. In practice a payer who cancels at their bank
usually cancels days before the next collection. ADDACS reaches the supplier a working day later,
and nothing is presented. The ARUDD 1 return is the case where the cancel falls inside the
collection window. If the prediction holds, W2_41's row stays at 1, and the follow-on is a
fidelity choice about the timing of the cancel against the collection date. That choice goes
to the knowledge page first (K8), not to a constant.

**Prediction 2, f89db6ff3's, restated and not reworded** (K6 page, "Net and the annual report"):
"net's move has the same sign as gross's and a smaller magnitude". Any year where net moves further
than gross is listed, not assumed away. `grade_net.py` reads the settlement view that each arm forms
in-process, because `extract_report_data` reads module state the run populates and a fresh process
cannot rebuild it. That was tried on the 12246cbae pickles and failed: KeyError 'SYN-2016-001' in
`build_cost_to_serve`.

**Done means.** Both arms finish. `grade_d.py` and `grade_net.py` print against each output. The
counts, with denominators, and the two verdicts are added below this line unedited, and each
prediction is marked held or refuted. W2_41's row moves to 2 only if arm B shows ADDACS 1 stops
reaching the desk and priced; otherwise this page says why not.

## Result

Graded 26 Oct ~21:10Z by `the-mandate-run-arms-are-graded`. Both units finished (DONE.json, arm A
3,600 s, arm B 3,561 s, nothing skipped). Both graders ran from the run worktree (origin 67a893e749).
Outputs: `<out>/grade_d.json`, `<out>/grade_net.json`.

**Leg (d), the desk's stops.** Denominators are the same in both arms: 962 DD legs, 568 DD households.

| | arm A, default | arm B, own-cancel 0.005 |
|---|---|---|
| DD presentations / returned unpaid | 37,449 / 653 | 36,831 / 659 |
| returns stops (legs / households) | 64 / 43 | 66 / 45 |
| owed at a returns stop: total, median | £8,438.37, £87.23 | £8,517.17, £86.31 |
| returns stops with nothing owed | 0 | 0 |
| **ADDACS 1 advices received by the desk** | 0 | **0** |
| spells off DD / closed by a re-mandate | 64 / 0 | 66 / 0 |

Arm A's zero is by construction, as filed. **Arm B's zero is not.** The world did act. PB8 recorded
20 own-reasons cancellations (`household_method_acts_summary`: 10 moderate stress, 6 low, 4 high)
over 31 fuel legs. The triad honoured them: in the cancel month 20 of the 31 legs' collections come
back failed, and the following month they move to standard credit. (Of the other 11, 6 were
already paying on receipt that month, 5 of them because the desk had stopped them earlier on
returns. The other 5 show a DD success in the cancel month. That is not chased here.)
But the desk was told about none of them. `_run_rails` emits the ADDACS 1 record only when
`shock.cancel_return and told is None and exit_ is None` (`simulation/dd_collection_book.py:555`).
`told` is the one-payment-truth outcome, and it is set for **1,040 of 1,046 legs**, because
`world_payment_truth.UNIFIED` has shipped on since 12 Oct. So on the shipped world the household's
cancel reaches the rails as one failed collection, and then the leg leaves DD by the triad's truth.
The supplier's register still holds a live mandate, and no ADDACS 1 is ever received.

*Correction, same evening, beside the claim:* the last sentence overstates it. The company's
payment-observation consumer does hear ADDACS 1, through the triad's own mandate stream
(`background/live_payment_triad.py`, `_mandate_stream`). The desk that never heard it is the
collection book's rails desk. That desk is the one `grade_d.py` replays, and the one behind
`supplier_dd_stops`, the stop notices, the money side's DD spells and the published DD collection
book. So there are two supplier desks, and they disagreed on every household cancel.
**Fixed** in the commit that carries this note. The rails' ADDACS 1 now follows the cancel month's
failed collection whoever decided it (`outcome == "failed"`, not `told is None`). A truth that
collected that month sends no advice. Test:
`test_under_one_payment_truth_a_household_cancellation_still_reaches_the_desk_as_addacs_1`,
red before the fix and green after. The default book is unchanged, because both cancel shares ship
at 0. Arm B has not been re-run, so W2_41 stays at 1 until a run shows ADDACS 1 reaching this desk.

- **Prediction 1 (no ADDACS 1 stop reaches the desk before a failed collection): NOT GRADED.**
  Its denominator is zero: there are no ADDACS 1 stops to time. It is not marked held, even though
  the count it named (0 before) is 0. A vacuous zero is not a hold. In arm B, 20 of the 20 triad
  cancels that failed show a failed collection in the cancel month, which is the shape the
  prediction expected, but the advice that should follow it never fires.
- **W2_41 stays at 1.** Arm B shows the household's act, but not as an ADDACS 1 reaching the desk
  and priced. The cause is the gate above, not the timing question the prediction was about.
  Follow-on: the rails' ADDACS branch has to read the truth's failed cancel-month collection. That
  is an error fix, and it has landed (see the correction above). What remains is re-running arm B.

**f89db6ff3's net.** Settlement view formed in-process in both arms, over 732 supply-point-years.

| year | gross £ | net £ | supply-point-years |
|---|---|---|---|
| 2016 | −1.68 | **+32.69** | 78 |
| 2017 | −251.98 | **+39.46** | 168 |
| 2018 | −655.88 | −274.31 | 141 |
| 2019 | −291.30 | −187.50 | 109 |
| 2020 | −80.41 | −25.20 | 86 |
| 2021 | −71.25 | −53.98 | 45 |
| 2022 | +37.43 | **−7.53** | 21 |
| 2023 | +109.30 | +90.39 | 31 |
| 2024 | −623.66 | −156.84 | 38 |
| 2025 | −221.31 | −122.07 | 15 |
| **decade** | **−2,050.75** | **−664.89** | **732** |

Arm B differs from A by at most 3p in any cell (decade −2,050.78 / −664.92). That is expected,
because a mandate cancel moves no settled volume.

- **Prediction 2, as filed ("net's move has the same sign as gross's and a smaller magnitude"):
  HELD book-wide, REFUTED by year.** For the decade, net is −£664.89 against gross's −£2,050.75:
  the same sign, at 0.32 of gross. By year, **3 of 10 years have the opposite sign**: 2016, 2017
  and 2022. In **1 of 10** (2016) net moves further than gross, though gross there is £1.68, so
  the ratio says little. 2017 does say something: 168 supply-point-years, gross −£252 and net +£39.
- The filed reason ("levies are roughly a third to a half of an electricity unit rate") implies
  net ≈ gross × 0.5–0.67 wherever volume is what moves. The decade's 0.32 is outside that, and the
  same-sign years range from 0.25 (2024) to 0.83 (2023). So **net is not gross scaled by a levy
  share.** Something in net moves on a different base from gross's volume: the standing charge, the
  profile-spread rule applied to costs and revenue separately, or legs where one is a credit.
  **I cannot yet say which.** Prediction, filed now: the 2017 flip sits on a few legs whose policy
  and network costs move against their revenue. One-variable check: decompose 2017's net by leg
  into revenue, policy and network moves. Carried as `the-net-settlement-move-is-decomposed-by-leg`.

## Arm B re-run after the rails fix: pre-registered 26 Oct ~22:20Z, before launch

Drawn as `the-mandate-run-arm-b-is-re-run-after-the-addacs-fix`. Not re-run by anyone before this
(no output dir, no unit, no process). Arm B's script is unchanged and runs in a fresh worktree
`/var/tmp/se-mandate-run-8a56cb7ae8`. That is origin 8a56cb7ae8, which carries 331c128058 (the
rails' ADDACS 1 now keys on `outcome == "failed"`, `simulation/dd_collection_book.py:557`). Output
goes to `/var/tmp/mandate-run-out-8a56cb7ae8-own-cancel-low/`, and it is graded with `grade_d.py`
and `grade_net.py` unchanged.

**This is not one variable away from the 67a893e749 arm B.** There are 42 commits between the two
bases, among them the read-duty step (85dcdc3b83), B13 L2's dual fix on contact (b7b17b8bf3) and
the per-rate bill lines. So a move in DD counts, returns or net cannot be put down to the ADDACS fix.
The one quantity the fix alone governs is ADDACS 1 on the rails desk, which was 0 before.

- **P1 (ADDACS 1 reaches this desk):** ADDACS 1 stops are between 12 and 20 legs. At 67a893e749
  the triad's own-reasons cancels were 20, with a failed cancel-month collection. A leg the desk
  had already stopped on returns cannot be stopped twice, and the 42 commits may shift which
  households draw a cancel. Refuted if 0, or if more than the triad's failed cancel-month
  collections in this run.
- **P2 (the filed prediction 1, now non-vacuous):** `reached_desk_before_any_collection_failed`
  = 0 of N. Every ADDACS 1 is dated after a returned collection, because `_run_rails` still builds
  it from `shock.cancel_return`.
- **P3:** the decade gross and net are within £5 of 67a893e749's arm B (−2,050.78 / −664.92).
  A cancel moves no settled volume, and none of the 42 commits is meant to move settlement. If
  this misses, it is listed. It is not attributed.

W2_41 moves to 2 only if P1 holds: ADDACS 1 stops reach the rails desk, with what is owed at each
one priced.

## Arm B re-run after the rails fix: the result (graded 27 Oct, on the 26 Oct 23:24Z output)

The run finished in 3,287 s with no keys skipped. `grade_d.py` and `grade_net.py` were run unchanged.
Output: `/var/tmp/mandate-run-out-8a56cb7ae8-own-cancel-low/` (`grade_d.json`, `grade_net.json`).

| | 67a893e749 arm B | 8a56cb7ae8 arm B |
|---|---|---|
| DD legs / households / presentations / returned unpaid | 962 / 568 / 36,831 / 659 | 962 / 568 / 36,831 / 659 |
| ADDACS 1 advices received on the rails desk | 0 | **20** |
| ADDACS 1 stops (legs) / households | 0 / 0 | **18 / 13** |
| owed at the ADDACS 1 stops, total / median | — | £1,161.58 / £49.89; 0 stops with nothing owed |
| stops on returns (legs) / owed | 66 / £8,517.17 | 66 / £8,517.17 |
| spells off DD | 66 | 84 (= 66 + 18) |
| decade gross / net | −2,050.78 / −664.92 | −2,050.78 / −664.92 |

- **P1 HELD.** 18 ADDACS 1 stops, inside 12–20 and not above the 20 failed cancel-month collections.
  Of the 20 advices, 2 ended nothing. *Unmeasured explanation:* those 2 legs had already been
  stopped on returns, since "a leg cannot be stopped twice" was the reason the band went below 20.
  I have not checked this leg by leg.
- **P2 HELD, and is no longer vacuous.** `reached_desk_before_any_collection_failed` is 0 of 18.
  All 18 had a failed collection first, and the reason on every one was "Refer to Payer".
- **P3 HELD exactly.** Gross and net match to the penny in every cell. The 42 commits between the
  bases moved nothing in this arm's DD counts, returns or settlement. The only change is the 18
  ADDACS 1 stops, so that one move can be attributed to 331c128058.

**W2_41 stays at L1, and P1 is not the reason.** The pre-registration said L2 needed P1. But the
atom's own `real_world_twin` is "an ADDACS 1 file arriving the morning after a customer cancels at
their bank, *before any collection fails*". P2 shows the world produces the reverse: all 18
ADDACS 1 stops follow a returned collection, because the advice is still built from `shock.cancel_return`
and gated on `outcome == "failed"` (`simulation/dd_collection_book.py:557`). The rails desk now sees the household's own cancel, but only as the second
signal after the first failure. The twin's case, a cancel noticed before the next collection, is
never drawn. The open defect: the world draws the cancel date and the failed collection together.
It does not draw the cancel as its own dated act, with the advice a working day later and the
next presentation refused as "no instruction". Until it does, L2 would be measured on the
flattering half of the twin. A second mismatch: the comment at :552 says the cancel-month
collection comes back "instruction cancelled", but all 18 came back "Refer to Payer". So the
return reason the world gives does not name the cause it modelled. The pre-registration's L2 condition was wrong, and is corrected here
next to it.
