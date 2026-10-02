**Severity:** LATENT · **Lane:** B_commercial (world side: `simulation/`) · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon (upstream world fidelity)
**Answers:** `docs/staging/WORKER_FINDING_SVT_EXITS_NOW_RUN_AT_C1BS_RATE_AND_AN_SVT_CONVERSION_NO_LONGER_LOGS_A_RENEWAL_DECISION_2026-10-02.md` (its recommended remedy)
**Claim:** `log-a-non-rolled-renewal-decision-for-a-household-converting-off-svt`

# An SVT conversion is a `renewed` row again, and its journey decision is still skipped

**2026-10-02, autonomous worker.**

## What landed

- `simulation/customer_events.py`: `svt_conversion_event` and `DEPARTURE_OCCASION_SVT_CONVERSION`.
  The row has `event_type` set to `renewed` and `departure_rolled` set to False. `churn_probability`,
  `win_probability`, `effective_retention_probability` and `random_roll` are None, because there was
  no roll. `realized_churn_probability` is **0.0**, and that is the world's real value, not a
  placeholder: the term gives the household no exit route. The finding's remedy asked for None
  here. I chose 0.0 because `departure_population.union_by_year` counts a decision whose
  probability is None as `unpriced_decisions`, which sets `expected_rate_pct` to None. With None,
  every year that holds a conversion would have lost its expected rate. The occasion is its own
  value, `svt_conversion`, so `roll_lifecycle_event` stays the only producer of rolled
  `renewal` events.
- `simulation/run_phase2b.py`: when `departure_rolled_at_renewal` is False, that row is appended to
  `customer_events_log` and to nothing else. The end-of-run summary prints it as "converted off
  SVT, not rolled" and does not format None as a float.
- Readers that would have crashed on the None fields, found by a census of every
  `customer_events` reader that indexes a roll field:
  - `saas/reporting/annual_report._customer_lifecycle_events_section`: `:.4f` on None.
  - `tools/generate_dashboard_data`: `float(None)`. It now publishes `sim_churn_p` None, not a
    fabricated 0.
  - `tools/run_value_cycle_ab`: the `"random_roll" in e` filter would have counted the row as a
    rolled renewal decision.

  `population_anchor`, `churn_accuracy_report`, `threshold_sensitivity`,
  `grade_renewal_churn_belief` (which skips rows with no numeric belief), `clv_gap_selection`,
  `_build_churn_basis_risk` and `_compute_company_divergence` all handle the row unchanged.
  `population_anchor`'s docstring said `customer_events` rows always carry `churn_probability`.
  It now names the exception.
- One control: `tests/simulation/test_departure_rolled_at_renewal.py::test_a_household_converting_off_the_svt_is_still_a_retention_every_counting_reader_keeps`.
  Reverting the `annual_report` guard turns it red.

## Is the world unchanged? Yes by construction, and checked

Nothing inside the run loop reads `customer_events_log`. In `run_phase2b.py` its only in-loop use
is the `append`; every read comes after the loop (the summary at about line 3484, and the output
dict). The new row is appended outside the `if event is not None:` block, so it reaches no journey,
retention-log, nudge or departure code. So it needed no one-variable run. The fixture world,
2016–2018, was run in the worktree to confirm the branch fires and the summary does not crash. See
"Fixture run" below.

## Still open: 1cd4b03dc also stopped the journey recording the decision

Skipping `roll_lifecycle_event` also skips `_journey.record_decision(..., switched=False)`. Before
`1cd4b03dc`, a household converting off the SVT recorded a stayed decision on its churn journey.
Now it records nothing. It also skips writing `outcome` onto a retention-log entry made on that
term, and skips the matching `nudge_physics_log` row. Commit `1cd4b03dc` said "journey advance ...
unchanged", and that is wrong for `record_decision`. This IS a world change, because the journey
feeds later behaviour. It needs its own pre-registration and a one-variable run, and I have not
done either. The question is whether a conversion off the default tariff is an engaged decision
the journey should see. It almost certainly is: the household chose a fixed deal.

## Fixture run (2016–2018, SIM_FAST_MODE, this worktree)

`customer_events`: 52 rows -- rolled `renewal`: 21 renewed + 12 churned; `svt_conversion` (renewed, not rolled): 19. Run exit 0; the summary prints each conversion as "converted off SVT, not rolled". Without this change those 19 retentions would have had no row in the 2016-2018 window.

The same fixture now carries a wiring control, `tests/simulation/test_run_phase2b.py::test_a_household_converting_off_the_svt_leaves_a_renewed_row_in_the_run`.
