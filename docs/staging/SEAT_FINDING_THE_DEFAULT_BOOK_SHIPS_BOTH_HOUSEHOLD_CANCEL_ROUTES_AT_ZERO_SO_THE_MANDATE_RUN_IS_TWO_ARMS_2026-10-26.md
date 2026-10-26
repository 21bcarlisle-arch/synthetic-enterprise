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

*(owed: added by the continuation that grades the arms)*
