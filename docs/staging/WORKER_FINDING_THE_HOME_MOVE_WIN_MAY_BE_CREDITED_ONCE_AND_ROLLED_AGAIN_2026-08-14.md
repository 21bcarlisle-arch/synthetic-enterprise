# [WORKER-FINDING] The home-move win may be credited once by inflating retention and rolled a second time afterwards (2026-08-14)

**Severity:** LATENT · **Lane:** W2_customer_generator · **Disposition:** QUEUED (not fixed on sight)

**Class:** one probability enters a model twice through two different doors, and neither door can see the other.

**Provenance:** CLAIM B of `WORKER_FINDING_A_WON_HOME_MOVER_WITH_NO_SUCCESSOR_SUPPLY_POINT_SUPPRESSES_THE_REPLACEMENT_TOO_2026-08-14.md`,
re-filed as its own document when that finding's CLAIM A was repaired and archived on 2026-08-14. Split out
deliberately: Claim A's repair is neutral to this question, and leaving Claim B inside an archived document
would have discharged it by association — the "archived before its class was rendered" failure this project
has already recorded.

Filed **LATENT, not BLOCKING**, and the distinction is the point: nothing here says a control is untrustworthy
or that a published figure IS wrong. It says a modelled quantity may be counted twice, and **that is not yet
determinable from the code**. Calling it BLOCKING on a suspicion would be inventing a lane hold; calling it
RECORDED would be accepting a limitation nobody has measured. It is a real, open, unmeasured question.

## The two doors, both observed

`saas/home_move_win_rate.py::build_home_move_win_rates` (~line 334):

```python
effective_retention_probability = (1 - churn_probability) + churn_probability * win_probability
```

Its own docstring names the second term: *"winning the post-move-in occupant after a churn"*. That value
becomes `effective_p_retain` in `simulation/customer_events.py`, and `retained = roll <= effective_p_retain`
(line ~136) — so **the retained set already contains the home-move wins**.

`simulation/customer_events.py:139-142` then rolls, on the NOT-retained remainder, against the same figure:

```python
if not retained:
    win_roll = _random.Random(f"win_{billing_account}_{term_start_str}").random()
    home_move_won = win_roll <= renewal_data["win_probability"]
```

Read literally the total is `c·w + c·(1-w)·w` against a parameter of `c·w`.

## Why this is a question and not yet a defect

Two readings are both consistent with the code, and the code does not choose between them:

1. **Double-count.** One event modelled twice, and the world wins more home-movers than its parameter says.
2. **Two genuinely distinct events.** A mover retained on the SAME billing account (the retention term) versus
   a successor activated as a NEW supply point (the roll). Those are different objects in the CRM and have
   different downstream consequences, and a supplier really can experience both.

Reading 2 has real support: only the second door produces a `won_successor_activations` entry, and reading 1
would make the first door's contribution invisible in the event log. Reading 1 has real support too: the
docstring says the two terms describe the same thing.

Worse for either reading, `effective_p_retain` is not left alone after the win term is folded in — the market
switching multiplier, income stress, satisfaction and the retention modifier all subsequently transform
`1 - effective_p_retain` **as if it were a pure churn probability** (`customer_events.py:110-134`). So under
reading 1 the win term is not merely double-counted, it is also stretched by four adjustments that were never
meant to apply to it.

## What is NOT claimed

- **No run was executed to measure this** (R9). Everything above is read off the code path.
- **No published figure is asserted wrong.** The effect on the annual report's CRM reconciliation is
  plausible but unquantified, which is exactly why this is LATENT and its sibling was BLOCKING.
- **No repair is proposed.** The two readings imply opposite fixes (drop the term from
  `effective_retention_probability`, versus rename it and leave the arithmetic alone), and choosing between
  them on aesthetics would be the goal-seek R12 forbids.

## What would settle it — the cheapest first

The question is *whose* event the retention-term win is. One run, instrumented, answers it: compare the
realised rate of home-move wins **delivered as successor activations** against `win_probability` over the
population, and separately count accounts retained at a renewal whose `effective_retention_probability`
exceeded `1 - churn_probability` (i.e. those the win term rescued). If that second population is non-empty and
those accounts show no other trace of a home move, the two doors are counting the same event and reading 1 is
right. This is a measurement, not a design argument, and it must precede any change to either line.

Whichever way it resolves, the answer belongs in `saas/home_move_win_rate.py`'s docstring as a stated contract
— it is currently the only place the two doors are described, and it describes them as one thing.
