# The constant census is blind to the live path's own window

**Found:** 2026-08-17, worker tick, D29 DISCOVER/FRAME pass 4 (LANE 3 idle draw). **Not fixed on
sight** — SELF-INTERRUPT DISCIPLINE; the census is `D30_the_belief_band_is_this_books_length`'s, not
D29's. **Severity:** LATENT. **Lane:** H_harness.

Everything below is `observed-with-evidence` unless labelled otherwise (R9). Measured in a detached
worktree at HEAD `b7349bee0`; `tools/couple_w2_11_d5.py` clean at HEAD this tick.

## What the control claims

`SCENARIO_CONSTANT_CENSUS` (`tools/couple_w2_11_d5.py`) exists because the same defect was found
twice by accident: a harness constant chosen to REMOVE A CONFOUNDER is also a silent RESOLUTION
decision, and both times an Expert Hour tripped over it rather than a control catching it. D27 found
`DD_FAILURE_WINDOW_DAYS = 400` ("generous on purpose"); D29 found `AS_OF_BUFFER_DAYS = 30`
("comfortably past").

The census is enforced by `_check_census_is_complete`, and it is a genuinely fail-closed keyset
check — its own docstring: *"FAIL-CLOSED ON THE KEYSET. The subject comes off `build_scenario`'s AST,
so a constant added to the scenario and never censused raises here instead of waiting for an Hour to
trip over it."* That is true, and it is a good control.

## The defect

**Its subject is `build_scenario`'s AST.** `build_scenario` is the OFFLINE book builder. The LIVE
population — `background/live_payment_triad.py`, the L3 escalation that scores real `run_phase2b`
runs through the same `score_triad` — is not in that AST and can never be.

And the live path has one of exactly this class:

```python
# background/live_payment_triad.py:116-119
# Run-spanning belief window (see module docstring RECENCY-WINDOW NOTE). A live
# run covers ~2016-2025 (~3650 days); a comfortable ceiling keeps the belief
# severity count on the same all-time basis as the truth count.
_RUN_SPANNING_WINDOW_DAYS = 6000
```

It is the live counterpart of `DD_FAILURE_WINDOW_DAYS` — it is what the live consumer's
`dd_failure_window_days` is constructed with (`live_payment_triad.py:528`), i.e. the company's memory
`W` for every live belief figure. Its stated reason is confounder-removal in the same voice as the two
the census already holds; the module docstring says so outright: *"otherwise the two would diverge on
a recency artefact rather than on the channel blind spot this triad is built to measure."*

**Observed:** `SCENARIO_CONSTANT_CENSUS` has 8 members — `AS_OF_BUFFER_DAYS`, `N_PERIODS`,
`PERIOD_SPACING_DAYS`, `BILLING_CYCLE_SPREAD_DAYS`, `DD_FAILURE_WINDOW_DAYS`, `FIRST_DUE_DATE`,
`PAYMENT_TERMS_DAYS`, `BILL_AMOUNT_GBP` — all eight read by `build_scenario`. `grep -n
"6000\|RUN_SPANNING" tools/couple_w2_11_d5.py` returns **nothing**: the token does not appear anywhere
in the offline module, so no census entry, no owner, no `sets_edges`, and no edge-owner cross-check
can reach it.

So this is the third member of the class the census was built for, and the census is structurally
incapable of naming it. The control is not fail-open — it is fail-closed over the wrong population.

## Why it matters rather than being a tidiness point

At `W = 6000` against a run of ~3650 days, the live belief window is saturated by construction with
roughly 2,350 days of headroom — every longer memory, to infinity, publishes one number. That is
exactly the collapse D27 named at this edge and D29 named at the other, sitting unmeasured on the LIVE
figure. (The ~3650 is the module's own comment, not a figure this pass measured; `run_phase2b` was not
run here. Labelled **inferred** on that arithmetic, **observed** on the constant and the census.)

It is somewhat masked today, and the masking is itself worth recording: the live ledger entry
`W2_11_payment_behaviour_source` publishes `metric: detection` (gap `0.0833907649896623`), and the
belief pair rides only as prose inside that entry's `note` (`live_payment_triad.py:731` — *"The
companion belief/ageing gaps ride inline in the note"*). So no live BELIEF figure is published as a
gap at all. The saturation is real but currently lands on a number that is not a headline. A future
promotion of the live belief gap to a published metric inherits it silently.

## The shape, for the class

This is `controls_that_cannot_fail`, killer pattern: **the subject is chosen by the checker's own
convenience.** An AST walk of one function is cheap and exact, so the population became "what that
function reads" rather than "what sets the resolution of a published figure". The offline builder and
the live builder are two implementations of one thing; the wall is enforced over one of them.

Prior member of the same shape: `a_wall_can_be_enforced_over_an_EMPTY_set_while_a_second
_implementation_runs_unwalled`, and `a_harnesss_convenience_chose_the_controls_subject`.

## Proposed repair (D30's call, not taken here)

Widen the census subject from `build_scenario`'s AST to **both** producers of a scored population —
`build_scenario` and `LivePaymentTriad` — and give `_RUN_SPANNING_WINDOW_DAYS` a census entry with
`owning_atom` and `sets_edges`, as the offline window has.

**R15 mutation that must fire, and it is the honest one:** add a new confounder-removing constant to
`live_payment_triad.py`, wire it into the live consumer, and the census check must raise. Today it
passes. Note that the *current* check would also pass if `build_scenario` were deleted outright
(empty subject, empty violation list) — worth a second mutation covering the empty-subject case.

## Disposition

**RECORDED**, queued as a finding against `D30_the_belief_band_is_this_books_length`, whose census
this is. No code changed this tick; nothing in any atom's `file_scope` was touched. R12: no published
number was tuned or written.
