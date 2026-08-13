# [WORKER-FINDING] A won home-mover with no successor supply point delivers no successor and suppresses the market replacement too (2026-08-14)

**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Status:** measured and reported, **not fixed** —
this tick drew LANE 3 DISCOVER/FRAME on `EP12_adapter_css_rec_switching`, a doc-only lane, and this is world
BUILD code. Found while surveying the world's exit mechanism for EP12; full context
`docs/design/EP12_CSS_REC_SWITCHING_DISCOVER_FRAME.md` §7.

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
