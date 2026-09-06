**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** DD_seasonal_cashflow_physics

# Six DD level-collection controls are red at HEAD, in both trees, and nothing is tracking them

**Found:** 2026-09-06, delivery seat, incidentally — while grading a pre-registration for an
unrelated claim (`the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`). Not caused by that
work, established rather than assumed; see "It is not mine" below.

---

## The state

`tests/simulation/test_dd_level_collection_book.py` — **6 failed, 4 passed in 0.08s**:

```
test_collection_is_fixed_within_year_though_bills_vary      KeyError: 'C0'
test_re_estimation_moves_the_fixed_amount_between_years     KeyError: 'C0'
test_amount_equals_dd2_collected_by_construction            KeyError: 'C0'
test_collection_lands_on_staggered_payment_day              KeyError: 'C0'
test_summary_totals_and_count                               KeyError: 'C0'
test_sample_schedules_bounded                               assert 0 == 6  (len({}))
```

**In the shared tree too**, with the real gitignored data present — so this is not the linked-worktree
artefact it looks like at 0.08s. It is a genuine red at HEAD.

## It is not mine, and that was checked rather than asserted

The turn that found it added a guard to `simulation.population_draw.price_elasticity_for_customer`.
Disabling that guard and re-running changes nothing: **red with it, red without it.** The failure
mode is also the wrong shape — a `KeyError` on an empty mapping, not the `ValueError` the guard
raises. It is red at `3851553ec`, before this seat's commit.

## What is actually happening

Not the payment-method gate, which is where the fixture's own comment points and where I looked
first. The fixture picks ids by `payment_method("resi", 90.0, cid, "electricity") == "direct_debit"`
and says it "mirrors `dd_balance_book`'s own gate"; the book evaluates the same call per bill with
that bill's own amount (`dd_balance_book.py:246`). That looked like classic mirror drift — a fixed
£90 against a varying bill — and it is **not** the cause: C0 resolves `direct_debit` at every amount
the fixtures use (40, 45, 60, 80, 90, 110, 130). Recorded because it is the plausible wrong answer
and the next reader will reach for it too.

The actual break is one step further in:

```
build_dd_balance_book(_monthly_bills("C0", [70]*12))
  ->  trajectories: 0     unestimated_customers: 1     (['C0'])
build_dd_level_collection_book(...)
  ->  schedules: 0
```

Every customer lands in `unestimated_customers`, so there is no trajectory, so there is no level
schedule, so `book.schedules[_DD_ID]` raises `KeyError` and `sample_schedules` is empty. The level
amount is sourced through `company.interfaces.dd_review_outcome.reviewed_monthly_amount` — a
COMPANY-side interface the test imports directly — and a bare bill fixture no longer satisfies
whatever that needs.

**The suspect, named as a suspect and not a conclusion:** `c98707b91` (2026-08-10) *"KNIFE3 B4: the
world stops running the supplier's billing routines (3 of 4 edges)"*, which is the last commit to
touch this test file. That edge cut is exactly the shape that would leave a world-side book
depending on a company-side review outcome that no longer reaches it. **I have not bisected it and
the date is not evidence** — if that is right these controls have been red for close to four weeks.

## Why this is BLOCKING rather than a chore

Six controls on `DD_seasonal_cashflow_physics` — the atom whose whole subject is that a level direct
debit is FIXED while consumption swings — are not asserting anything, and the one that would catch a
collection wired to the bill (`test_collection_is_fixed_within_year_though_bills_vary`) is among
them. A control that cannot run is indistinguishable on the maturity map from one that passes.

And nothing noticed: `background.head_red_register` reports `owed: 830, accepted: 0, runs: 1` and
holds no entry naming this file. The path-scoped selections that gate commits do not reach it unless
a lane touches `simulation/dd_*`, which is the same shape as
`SEAT_FINDING_FORTY_TWO_TESTS_LIVE_WHERE_NO_RUNNER_LOOKS_AND_ONE_OF_THEM_HAS_BEEN_RED_FOR_SEVEN_WEEKS_2026-09-05`.

## What would close it

Establish first **which side is wrong**, because both readings are live and they lead to opposite
repairs:

- the world-side book should not need a company-side review outcome to produce a trajectory at all,
  in which case KNIFE3 B4 cut the edge correctly and `dd_level_collection_book` still reaches across
  it — a wall question, not a fixture question; or
- the edge is legitimate and the FIXTURE is what went stale, in which case the six tests need to
  supply a review outcome and the mirror comment in `_pick_ids` needs deleting, because it points at
  a gate that is not the one that fails.

**Do not fix the fixture first.** Making the tests green by feeding them a review outcome would close
the red and hide the wall question underneath it, and the wall question is the one that matters.

**Not opened as a second writer:** this seat has not touched `simulation/dd_*`,
`company/interfaces/dd_review_outcome.py` or that test file. Filed for whoever holds the DD lane.
