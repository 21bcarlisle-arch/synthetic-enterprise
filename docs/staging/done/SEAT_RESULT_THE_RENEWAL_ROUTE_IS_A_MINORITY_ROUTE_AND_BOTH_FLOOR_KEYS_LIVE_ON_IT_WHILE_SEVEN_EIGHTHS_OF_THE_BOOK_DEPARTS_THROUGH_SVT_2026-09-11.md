# The renewal route is a minority route, both floor keys live on it, and the book departs through SVT

**Lane:** A_strategy_governance · **Severity:** LATENT · **Class:** measurements_that_mirror

*LATENT and not RECORDED: this carries a live unfixed defect that reaches a published artefact —
`product_label_by_account_class` states `the_guard_admits_it: true` for 152 electricity legs in the
same file whose funnel counts 1,347 `svt` terms. LATENT and not BLOCKING: nothing here refuses a
land, and the floor's own `except` leg already refuses on its own guard.*
**Date:** 2026-09-11
**Claim:** `the-renewal-funnel-not-the-redraw-key-is-what-keeps-the-rest-of-the-book-out-of-the-floor`

---

## Where these numbers were read

**Every figure below is read at `origin/main` = `cf16f724e6d79f02707008c0af143d2e00c1c90b`,
not at the local `HEAD` (`9076ffc36`).** The two have diverged — 23 local commits and 25 origin
commits with no message in common — and **the code this finding is about is not in the local tree
at all**: `git grep churn_roll_for_renewal` over the working tree returns nothing. A reader who
checks these line numbers against a local checkout will find neither the symbol nor the gate. That
divergence is somebody else's open alarm (`WORKER_FINDING_REPEATING_ALARM_DEADMAN_ORIGIN_FORK`,
`..._PUBLISH_REFUSED_ORIGIN_AHEAD`); it is recorded here only because it decides which ref the
claims are checkable at.

All world-level figures share one world: **digest `39a192ce04c1eda8`**. Sources:

| Artefact | What it supplies |
|---|---|
| `docs/observability/value_cycle_ab_floor_partition_probe_both_keys.json` | the two keys' reach (commit `a9ae86351`) |
| `docs/observability/value_cycle_ab_s1_three_arm_20260910.json` | `renewal_funnel`, `book_identity`, the 100-account roster |
| `docs/reports/svt_generated_share_verdict.json` | product mix by year, off the built schedules |
| `docs/reports/departure_level_route_attribution.json` | decisions and departure share, per route |

---

## The commissioned question, answered

> *Why do only 70 of the 164 settled billing accounts reach a renewal point in the window?*

**Because a renewal point only exists on a fixed-term boundary, and most of this book is not on a
fixed term.** Two structural facts, both measured:

**1. Eighteen accounts cannot ever take the roll.** `book_identity` gives 164 accounts settled in
the window and 146 with an electricity leg. `roll_lifecycle_event` is called for electricity legs
only — gas legs share the billing-account-level decision — so the residual **18 gas-only accounts
are structurally incapable of taking a churn roll**, whatever anyone prices them at. 146 + 18 = 164
exactly.

**2. Of the remaining 146, the fixed-term boundary is the rare state.** The gate is
`run_phase2b.py:1964`:

```python
if term_index >= 1 and commodity == "electricity" and not _indexed_tariff:
```

with `_indexed_tariff = term_tariff_type in ("deemed", "flex", SVT_TARIFF_TYPE)` at `:1728`. The
churn roll sits inside that gate, so **every deemed, flex or SVT term carries no renewal decision
and no churn roll**. Measured on the reference run: of 2,037 term boundaries the world put in front
of the arm, **1,347 (66%) are stamped `svt`** and 158 carry `None`
(`renewal_funnel.value_arm.product_not_upliftable_by_tariff_type`).

**That is not a transient.** Domestic electricity account-days on SVT, off the built schedules
(`svt_generated_share_verdict.json`, same world digest):

| 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| 0.0% | 42.6% | 54.7% | 55.3% | 58.2% | 58.0% | **78.5%** | **91.0%** | 58.2% | 53.4% |

**The mechanism that puts them there is a deliberate one**, at `simulation/renewals.py:154-170`: at
every non-first fixed-term boundary for a `resi` household, `rolls_active_renewal` decides, at an
anchored ~35% active rate. On the ~65% passive branch the household is diverted onto an SVT stint
running to its next anniversary — and an SVT stint has no notice date, no struck rate and no
renewal decision, by construction and on purpose.

So the answer is not the window and it is not the redraw key. **A household reaches a renewal point
only in the years it happens to roll active, and roughly two thirds of boundaries are not that.**

---

## And the finding that matters more than the one commissioned

> *The rest of the book does not renew here. That is a fact about the funnel and no choice of key
> touches it.* — `customer_events.churn_roll_for_renewal` docstring

True, and it stops one step short of the useful part. **The rest of the book does not renew, but it
does depart.** It departs through a *second route* the floor has no key on at all.

Those SVT households are rolled against `svt_inertia_hazard`, at `run_phase2b.py:1822`:

```python
_svt_roll = random.Random(f"svt_inertia_{billing_account}_{term_start_str}").random()
```

Measured, per route (`departure_level_route_attribution.json`, world `39a192ce04c1eda8`):

| Year | renewal-route decisions | SVT-route decisions | renewal share of departures |
|---|---|---|---|
| 2017 | 20 | 118 | 17.4% |
| 2018 | 17 | 143 | 22.0% |
| 2019 | 13 | 113 | 12.8% |
| 2020 | 13 | 135 | 15.7% |
| 2021 | 20 | 150 | 19.1% |
| 2023 | 19 | 193 | 29.5% |
| 2024 | 16 | 170 | 24.5% |

The renewal route makes **13–20 decisions a year** and carries **13–29%** of departures. The SVT
route makes **113–193** and carries **71–87%**. The SVT route also carries essentially all of the
record's year-to-year shape (`relative_slope` 0.9936, against the renewal route's **-0.0778**).

**Both floor keys are renewal-route quantities.** `population_draw.price_elasticity_for_customer`
sits inside `if differential:` and needs an offered rate. `customer_events.churn_roll_for_renewal`
is the renewal point's own dice. Neither exists on the SVT route. So:

> The `except` leg cannot measure the rest of the book along **either** key — not because the
> roster swallows the complement, and not because the window is short, but because **the rest of
> the book departs through a route neither key is defined on.** Re-keying from elasticity to the
> churn roll moved the leg from *refusing* to *running over two households* because it moved
> between two quantities on the same minority route.

This subsumes the roster-swallows-the-complement reading rather than contradicting it. That reading
is correct about what it measured and wrong about which constraint binds first.

---

## One remedy in the tree is refuted; the other is buildable and named

The comment block at `tools/run_value_cycle_ab.py:4756` says what would reach the rest of the book:
*"a longer window or a funnel that offers renewals more widely"*.

**The first half is refuted by the table above.** The renewal route's decision count is flat at
13–20 a year across all seven fitted years while SVT exposure *rises* through the window. A longer
window therefore adds SVT-route decisions about nine times faster than renewal-route ones: it
grows the population the key cannot see faster than the one it can. Lengthening the window makes
the instrument's *reach* worse, not better — the same direction-of-degradation the existing block
already identifies for the roster, arriving by a second road.

**The second half is right, and there is a cheaper move than changing the world's product mix.**
The SVT roll is written **inline**, so no floor leg can intercept it: `setattr` needs a name and
there is not one. That is exactly the state `churn_roll_for_renewal` was in until 2026-09-10.

> **Named next step.** Extract the SVT inertia roll behind a name —
> `svt_roll_for_segment(billing_account, term_start_str)` — the same way
> `churn_roll_for_renewal` was extracted: same seed string, same `Random`, same `.random()`, so
> not one byte of the world moves (R13), with a byte-identity control saying so rather than a
> sentence. Then add `svt_inertia` to `run_value_cycle_ab.REDRAW_KEYS`. **That is the only
> candidate key that reaches 71–87% of this world's departures.**

Not done in this turn, and deliberately not half-done: it edits `simulation/` and its control is a
byte-identity claim over the whole 2016–2025 record, which needs a run to earn. Filing it as one
step with its evidence beside it is worth more than an unproven extraction landed in a diverged
tree.

---

## What is NOT measured, and the instrument that would settle it

> *Why do 32 of the 100 accounts the value arm priced never roll at all?*

**I cannot yet say, and the two candidate mechanisms license different remedies.** Stated as
candidates rather than a split, because the probe published the count (`churn_roll.
roster_accounts_that_never_drew: 32`) and **not the ids**, and no artefact on disk carries the
rolled-account set.

1. **Priced on gas only.** Gas entered `UPLIFTABLE_COMMODITIES` on 2026-09-07 and
   `not_the_arms_commodity` is now 0, so the arm prices gas terms — but the roll is
   electricity-only. An account priced solely on its gas leg is priced and never rolls. The
   ceiling on this bucket is the 18 gas-only accounts above.
2. **`renewal_data is None`.** `roll_lifecycle_event` returns `None` — above the roll — when
   `build_churn_risk` has no entry for that account at that renewal period. A priced fixed
   electricity term still takes no roll in that case.

These are not alternatives to each other and the counts may overlap at zero or add to 32; nothing
on disk distinguishes them.

**The instrument:** one pass of `partition_probe`'s pass-through pattern, extended to record, per
billing account, *the stage it stopped at* — no electricity leg / no second term / indexed tariff /
`renewal_data is None` / rolled. That is one instrumented pass and it answers both halves of the
commissioned question exactly, instead of the one half this document answers with evidence and the
other half it refuses.

---

## A separate defect, found in passing

`run_value_cycle_ab.product_label_by_account_class` documents itself as publishing *"the value that
record's OWN schedule builder stamps on every term it emits"*, and reports `resolved_tariff_type:
"fixed"`, `the_guard_admits_it: true` for **all 152 electricity legs** — in the **same artefact**
whose funnel counts **1,347 terms stamped `svt`**.

Both blocks are reading honestly and the docstring's claim is false. `resolved_tariff_type(record)`
reads the *record*, which carries the leg's **starting** product; `build_renewal_schedule`
**re-stamps** terms mid-leg at every passive boundary (`renewals.py:163`). So the census cannot see
the roll-off, which is the one thing about the product mix it most needs to report — and it states
the opposite with `the_guard_admits_it: true`.

This is the project's recurring two-homes-for-one-fact shape, and it is the second time this
function has been caught by it: its own docstring already records publishing `null` for 137
electricity legs the builder labels `fixed`. The previous fix made the *spelling* single-sourced by
importing `resolved_tariff_type`. It did not fix the *unit* — a per-leg read cannot answer a
per-term question, however many callers share it.

**Filed, not fixed here:** the honest census is over emitted **terms**, not over records, and
changing that moves a denominator on a published page.

---

## Corrections to my own reasoning, kept

- I expected the SVT gate to be inert. `simulation/svt_product.py` says
  `test_no_account_is_on_the_svt_product_yet`, and I read that as "no SVT terms exist". **Wrong:**
  no account is *assigned* the SVT product at acquisition, and 1,347 terms are still stamped `svt`
  because households are *diverted* onto it at passive boundaries. An assignment-time control is
  blind to a mid-leg re-stamp — the same unit error as the census defect above, which is how I
  found that one.
- I expected passive roll-off alone to explain 70 of 164, and it does not. At an independent ~35%
  active draw per boundary, an account present for nine boundaries rolls active at least once with
  probability ~0.98, so roll-off alone predicts nearly every long-tenure account reaching a
  renewal point. The 18 gas-only accounts and short tenure (91 of 165 accounts were won by the
  funnel mid-window, and every account spends its term 0 ineligible — 252 boundaries sit at the
  `acquisition_term` stage) carry the rest. **I have not decomposed those two, and the count above
  is therefore a mechanism, not an arithmetic reconciliation.**
