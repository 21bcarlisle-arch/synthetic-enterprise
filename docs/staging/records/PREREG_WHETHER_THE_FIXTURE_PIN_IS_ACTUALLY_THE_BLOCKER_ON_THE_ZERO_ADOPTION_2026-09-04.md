**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# Pre-registration: is the pinned fixture actually what blocks restamping a zero episode start?

Filed 2026-09-04 by the delivery seat, **before running anything**, against
`SEAT_FINDING_A_ZERO_START_TIME_RENDERED_AS_AN_ESTABLISHED_1970_EPISODE_ON_THE_DIRECTORS_OWN_SURFACE_2026-09-04.md`.

That finding's closing recommendation is: *change the fixture, not the adoption semantics* —
naming `tests/background/test_publish_gate_blocking_payload.py::
test_the_state_the_supervisor_draw_reads_carries_the_blocking_test`, which pins
`persisted["wedge_since"] == 0.0`, as the cost of the repair. The direction that drew this said
plainly that whoever took it should **test that recommendation rather than assume it**. This is
that test, registered before the answer is known.

## The subject

`background/process_run_complete.py:6339`

    prev_wedge_since = state.get("wedge_since")
    wedge_since = prev_wedge_since if isinstance(prev_wedge_since, (int, float)) else now

The proposed repair is one clause: adopt a persisted start only when it is a *positive* instant,
and restamp `now` otherwise — the same property the renderer was just keyed to.

## Predictions

**P1 — the named blocker does NOT red.** With line 6339 repaired and nothing else changed,
`test_the_state_the_supervisor_draw_reads_carries_the_blocking_test` stays GREEN and
`persisted["wedge_since"]` is still `0.0`.

Reason: `_write_publish_gate_state` runs the write through
`episode_monotonic.guard_episode(..., since_fields=("wedge_since",))`, and a `since_field` is
LOW-water — `out[field] = old if old_key[1] <= new_key[1] else proposed`. The prior on disk is
`0.0`, the repaired writer proposes `1800`, and `0.0 <= 1800` — so the guard writes the zero back.
**The repair at the adoption site is a no-op against a persisted zero.**

**P2 — a DIFFERENT control reds, and it is the sibling from the same finding.**
`tests/background/test_a_zero_start_time_is_not_a_start_time.py::
test_a_persisted_zero_does_not_reach_the_alarm_text` goes RED on `assert "1970" not in msg`.

Reason: `_episode_phrase` is handed the *local* `wedge_since` variable, not the persisted one, so
it receives `1800` — a positive start, correctly reported as `1970-01-01T00:30 UTC`. The fixture's
clock is a fake one near the epoch, so an honest restamp of a fake clock renders an honest 1970.
The leg's premise ("the writer adopts the zero, so the renderer is the last thing standing") is
what the repair removes.

**P3 — the load-bearing change is in `episode_monotonic._episode_key`, not in either fixture.** A
non-positive epoch is not an orderable episode start, for the reason that module's own `_is_num`
already gives about `True`: *"would silently become 1970 and read as a 56-year episode."* Zero
falls straight through the branch written to stop exactly that.

## What would refute each

* P1 is refuted if that test reds — then the finding's account was right and the guard is not in
  the path.
* P2 is refuted if the sibling stays green — then `_episode_phrase` is not reading the local
  variable and my read of the call at line 6401 is wrong.
* P3 is refuted if repairing 6339 alone makes the persisted value change.

## Method

Apply the one-clause change at 6339 alone. Run the three suites that name the field
(`test_publish_gate_blocking_payload`, `test_a_zero_start_time_is_not_a_start_time`,
`test_episode_monotonic_guard`) and read the result against the three predictions above **before**
touching anything else.

---

# RESULT (appended after the run, beside the predictions rather than over them)

**P1 CONFIRMED.** `test_the_state_the_supervisor_draw_reads_carries_the_blocking_test` stayed
GREEN with the adoption clause repaired and nothing else changed. Printed at the value rather than
inferred from a green test: `persisted wedge_since = 0.0`. The named blocker was never the blocker.

**P2 CONFIRMED.** `test_a_persisted_zero_does_not_reach_the_alarm_text` reddened on
`assert "1970" not in msg`, rendering `wedged since 1970-01-01T00:30 UTC` — exactly the predicted
consequence of restamping a fake clock at `now=1800`.

**P3 CONFIRMED.** The persisted value changed only once `episode_monotonic` stopped remembering a
non-positive prior. Reverting that screen alone reds 7 of 59 legs.

**WHAT NONE OF THE THREE PREDICTED, and it took a tautology mutation to find.** Replacing the
writer's whole clause with `wedge_since = now` left every new leg green: the PERSISTED field has a
second guard (the low-water rule restores the real start), but `_episode_phrase` is built from the
writer's LOCAL variable, so a seven-hour wedge paged as `0h00m` — the 2026-08-09 under-reporting
defect, on the NTFY path, invisible to every control here. Established as a MISSING TEST, not an
equivalence, by printing both surfaces side by side under the mutation. Written up in
`docs/staging/SEAT_FINDING_THE_FIXTURE_PIN_WAS_NEVER_THE_BLOCKER_AND_THE_ALARM_TEXT_HAD_HALF_THE_GUARDS_THE_STATE_FILE_HAD_2026-09-04.md`.
