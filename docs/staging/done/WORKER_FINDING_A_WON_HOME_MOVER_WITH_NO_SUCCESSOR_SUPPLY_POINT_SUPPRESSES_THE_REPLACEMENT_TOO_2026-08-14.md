# [WORKER-FINDING] A won home-mover with no successor supply point delivers no successor and suppresses the market replacement too (2026-08-14)

**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Status:** measured and reported, **not fixed** —
this tick drew LANE 3 DISCOVER/FRAME on `EP12_adapter_css_rec_switching`, a doc-only lane, and this is world
BUILD code. Found while surveying the world's exit mechanism for EP12; full context
`docs/design/EP12_CSS_REC_SWITCHING_DISCOVER_FRAME.md` §7.

**Discharged:** `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_with_no_successor_still_goes_to_market`, `tests/simulation/test_home_move_undeliverable_win.py::test_an_undeliverable_win_disposes_to_market`, `tests/simulation/test_home_move_undeliverable_win.py::test_the_affected_population_is_non_empty_on_the_live_roster`, `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market`, `simulation/customer_events.py` — 2026-08-14 RUNG-1c blocking draw: CLAIM A repaired at the call site via the home-move disposition helper, R15-proven on two independent mutations (every backtick on this line is read as a path, so the helper is named in prose here and in code below). The severity header states what the finding FOUND; this line is the release. CLAIM B is NOT discharged here and is re-filed as its own LATENT finding rather than answered by assumption.

> **DISPOSITION 2026-08-14 (worker tick, RUNG 1c blocking draw, lane W2_customer_generator) — CLAIM A
> DISCHARGED AND ARCHIVED; CLAIM B RE-FILED, NOT ANSWERED.**
>
> **CLAIM A confirmed exactly as written, and repaired.** The `if won: ... elif replace:` chain did take the
> outer branch, find no successor, and never reach the `elif`. The win roll and the DELIVERY of that win are
> two different facts, so they are now two different questions:
> `simulation/customer_events.home_move_disposition(home_move_won, successor_id)` returns
> `activate_successor` only when BOTH hold, and `go_to_market` otherwise — **an undeliverable win is a plain
> loss.** `run_phase2b` asks it instead of branching on the roll. The pathology the finding named (a `True`
> roll strictly worse for the company than a `False` one) is gone.
>
> **The population was mis-counted in this document, and the correction makes it worse, not better.** The
> finding says "6 keys against 20 customers", leaving 14 affected. Measured at HEAD: the churnable population
> is **13 billing accounts**, not 20 customers — gas legs bill under their electricity parent
> (`saas.customer_reaction._billing_account_id`) and successors are not themselves churnable. So the affected
> set is **7 of 13 billing accounts** (C7, C8, C9, C_IC1–C_IC4) — **54% of the book, not 70% of a roster**.
> The drawn SYN-* points the curriculum trickles in carry no successors at all, so activating the population
> draw only widens it. The count moved; the class did not.
>
> **What was deliberately NOT done: `win_probability` is untouched.** The finding is right that the world
> rolls a win it cannot deliver, but the missing successor is a ROSTER limitation, not a fact about that
> property. Zeroing the probability for accounts with no successor row would encode a book artefact as a
> belief about the world, and would move churn behaviour on 7 of 13 accounts as a side effect (the win term
> is inside `effective_retention_probability`). The consequence — the realised win rate runs below its
> parameter for those accounts — is therefore RECORDED, not tuned away: each undeliverable win stamps
> `home_move_win_undelivered` on its event, so the shortfall is visible in the event log instead of silent.
>
> **R15, proven both ways, on two independent mutations.** (1) Rewriting the helper to key on the win roll
> alone reds three controls including the behavioural one. (2) Reverting `run_phase2b` to the if/elif chain —
> leaving the helper correct — reds `test_a_won_home_mover_with_no_successor_still_goes_to_market` and
> nothing else, which is what proves that control's subject is the CALL SITE and not the helper. The call-site
> controls are behavioural over a real truncated run (a forced churn on a real account, spying on whether the
> growth desk was asked at all), never a source-text assertion — the import-shaped-conformance class is
> already filed against this project. They assert the company WENT TO MARKET, not that it WON: the defect
> suppressed the approach, and the outcome of that approach is a separate roll.
>
> **CLAIM B (possible double-count of `win_probability`) is carried forward untouched**, as
> `WORKER_FINDING_THE_HOME_MOVE_WIN_MAY_BE_CREDITED_ONCE_AND_ROLLED_AGAIN_2026-08-14.md` (LATENT). This
> repair was chosen precisely because it is neutral to Claim B: it changes only which branch an
> ALREADY-ROLLED undeliverable win takes, and moves no probability mass. Claim B stays open and answerable.

Classified BLOCKING under the OPS9 criterion *"a published figure may be wrong"*, not because a control is
untrustworthy. `saas/reporting/annual_report.py` publishes both a per-event customer-events table (line 3010,
acquisition rows carrying `channel`) and a **"SIM ground truth vs company CRM reconciliation"** of year-end
active/churned account counts (lines 3015-3045). The defect below changes which accounts exist in a run, so it
changes both. Under-classifying this to keep the lane open is the anti-pattern the ruling names, so it is
called as observed; if the board would rather accept the limitation than repair it, that is a recording, not a
re-classification.

## The measurement — CLAIM A, observed, no interpretation needed

`simulation/run_phase2b.py:1577-1589`:

```python
if event.get("home_move_won"):
    successor_id = SUCCESSOR_MAP.get(billing_account)
    if successor_id:
        won_successor_activations[successor_id] = term_start_str
        ...                                   # notify_acquisition(channel="home-move-win")
elif mandate_permits_replacement():
    ...                                       # decide_acquisition -> go to market
```

`home_move_won` is rolled for **every** non-retained account (`simulation/customer_events.py:139-142`, inside
`if not retained:`). `SUCCESSOR_MAP` is built from `SUCCESSOR_ELEC_CUSTOMERS` and, measured by import at HEAD,
has **6 keys — `C1`–`C6` — against 20 customers** (15 electricity, 5 gas).

For the other 14 accounts, a `True` roll:

1. takes the **outer** `if`,
2. finds `SUCCESSOR_MAP.get(...) is None`, so the inner block does nothing, and
3. **never reaches the `elif`**, because the outer branch was taken.

The account is lost with **no successor and no market replacement**. `mandate_permits_replacement()` returns
`False` only under a wind-down mandate (`company/interfaces/growth_desk.py:97-107`), so under every normal
mandate the suppressed branch is a live one.

Two consequences, both structural rather than statistical:

- **A `True` win roll is strictly worse than a `False` one for those 14 accounts.** Winning the home-mover
  costs the company the replacement it would otherwise have gone to market for.
- **The realised home-move-win rate is below its parameter** for those accounts — `win_probability` is
  computed for *every* account from segment + EPC + portfolio price differential
  (`saas/home_move_win_rate.py:283-340`) and is never zeroed for accounts with no successor supply point. The
  world rolls a win it has no way to deliver.

## CLAIM B — the same probability may be counted twice. Registered as a question, not asserted.

`build_home_move_win_rates` returns, per renewal point:

```python
effective_retention_probability = (1 - churn_probability) + churn_probability * win_probability
```

and its own docstring says the second term is *"winning the post-move-in occupant after a churn"*. That value
becomes `effective_p_retain`, and `retained = roll <= effective_p_retain` — so the retained set **already
includes** the home-move wins. `customer_events.py:142` then rolls `home_move_won` against the *same*
`win_probability` on the not-retained remainder.

Read literally, the win is credited once by inflating retention and rolled a second time afterwards, giving a
total of `c·w + c·(1-w)·w` against a parameter of `c·w`. Whether that is double-counting or two deliberately
distinct modelled events (a mover retained on the same account vs a successor activated as a new one) is **not
determinable from the code**, and this pass did not run the world to measure it. Recorded so the repair of
Claim A does not silently assume an answer to Claim B — they touch the same two lines and should be reasoned
about together.

## What is NOT claimed

- No run was executed this pass; the effect on any specific published figure is **inferred from the code path**,
  not measured against a run artefact (R9).
- No control was mutation-tested here, so nothing is said about whether an existing control should have caught
  this.
- No fix is proposed as a diff. The `if/elif` restructure is one line, but Claim B means the obvious
  restructure may be the wrong one.

## Disposition

Registered per SELF-INTERRUPT DISCIPLINE — queued, not fixed on sight. It belongs to
`W2_customer_generator`, not to `W4_the_wall` where this tick was drawn.
