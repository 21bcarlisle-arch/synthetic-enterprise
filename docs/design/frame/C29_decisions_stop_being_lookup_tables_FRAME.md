# C29_decisions_stop_being_lookup_tables — FRAME (canonical per-atom, doc-only)

**Atom** `C29_decisions_stop_being_lookup_tables` · lane `C_customer_ops` · value stream
`meter_to_cash` · epoch 4 · dial 45 · `level_current: 0` → `level_target: 3` ·
`loop_stage: idle` (BUILD-gated).

**Measured at** `c1609e374`, 2026-09-19. **DISCOVER/FRAME output only** — no BUILD code is written
here, per `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rule 7 and the atom's own `block_reason`
("DISCOVER and FRAME on this atom are drawable NOW").

---

## 0. What this doc is, and the four claims it re-asked

The atom's prose (director, 2026-08-28, P6, held in the record store as `map_notes.gain`) makes four
factual claims about this tree. Every one of them is an **un-re-asked prediction**: true when
written, and worth nothing as a FRAME input until asked again of the code that exists now. A FRAME
that restates them has done nothing.

All four re-asked against HEAD:

| # | Claim (director, 2026-08-28) | Verdict at `c1609e374` |
|---|---|---|
| 1 | "Acquisition budget takes no customer id" | **CONFIRMED** — finest key is `(channel, segment)` |
| 2 | "Dunning keys on segment and days overdue" | **CONFIRMED** — and it is the one surface whose table is *legally correct* |
| 3 | "...while capacity_to_pay and the breathing-space register go unread" | **CONFIRMED, exactly as written** — both modules exist, complete and tested, and **both have zero production callers** |
| 4 | "Retention is a fixed offer and fixed tiers" | **PARTLY REFUTED** — the offer is already per-account in magnitude, and the real defect is larger than the one claimed |

Claim 4 is the one worth the pass. Claim 3 turned up a live compliance hole.

---

## 1. Claim 1 — acquisition. CONFIRMED.

`company/crm/acquisition_strategy_book.py`:

- `analyse_channel(channel, segment, expected_annual_margin_gbp, expected_tenure_years=None, cac_override_gbp=None)`
- `rank_channels(segment, expected_annual_margin_gbp, ...)`
- `model_growth_scenario(target_new_customers, channel, segment, ...)`

`company/crm/marketing_budget.py`:

- `MarketingBudgetTracker.record_spend(category, year, ...)` → `MarketingCategory` × year
- `blended_cac_gbp`, `cac_by_category(year)`

No account identity reaches any of them. The decision unit is a *channel/segment cell*, and CLV is
`expected_annual_margin_gbp × tenure` where tenure is `_TYPICAL_TENURE_YEARS.get(segment, 3.0)` — a
segment table with a defaulted fallback. Claim confirmed as written.

**Observed in passing, not this atom's subject.** `analyse_channel` resolves CAC as
`_TYPICAL_CAC_GBP.get(channel, 50.0)`: an unrecognised channel silently receives a £50 acquisition
cost from a defaulted parameter. That is precisely the shape CLAUDE.md's standing note names (the
invented £150 CAC against the sourced £55 in `saas/opex_ledger.py`) — a number that will read as
established. Recorded here as an observation for the constant-origin lane rather than fixed in a
FRAME pass, because it is a different atom's subject.

---

## 2. Claim 2 — dunning. CONFIRMED, and its remedy is NOT "widen it".

`company/billing/arrears_engine.py` holds a literal table:

```
_DUNNING_PATHS: Dict[Segment, List[DunningStep]]
```

read by `dunning_path(segment)` and `current_dunning_step(segment, days_overdue)`, and reached from
`select_dunning_step(items, segment)`. The claim is exact: **segment and days overdue, and nothing
else.**

**But the table is the law, and this is the FRAME's first correction to the atom's framing.** The
residential path encodes Ofgem SLC 27 ability-to-pay ordering (reminder → reminder → *repayment plan
offer before any enforcement* → final notice → prepayment/agency); the SME and IC paths encode LPCDA
interest-notice timing. These are not lazy defaults standing in for a per-customer decision. They
are a statutory envelope.

So "decisions stop being lookup tables" **cannot mean "replace the dunning table"**. A per-account
dunning path that reordered or accelerated these steps would be a regulatory breach, not a widened
decision surface. What the surface is actually missing is not *variation* — it is a **gate**: the
per-account facts that should be able to *stop* the table from advancing. Which is claim 3.

---

## 3. Claim 3 — the two unread registers. The sharpest finding in this pass.

### 3.1 `capacity_to_pay` exists as a complete module, and is called by nothing

**Correction, recorded beside the claim it replaces.** This pass first concluded that
`capacity_to_pay` "does not exist" and that the mechanism lived under another name
(`company/crm/affordability_inference.py`). That was wrong, and the way it was wrong is worth more
than the answer.

`grep -rn "capacity_to_pay" company/ saas/ --include=*.py` returns **nothing** — and
`company/billing/capacity_to_pay.py` has existed since June. The file contains **zero occurrences of
its own name**: a content-grep cannot see a module whose identity is carried by its *filename*. The
standing lesson is that a grep for a name is blind to the mechanism; this is its mirror, and the
cheaper one to fall into. `docs/design/ORPHAN_DISPOSITION_REGISTER.md` had the module listed all
along — **the register knew, and the grep did not.**

What is actually there (`company/billing/capacity_to_pay.py`, 4 tests, no importer):

```
CtPAssessment(customer_id, assessment_date, monthly_income_gbp,
              monthly_essential_outgoings_gbp, total_debt_gbp, is_vulnerable)
  .disposable_income_gbp / .energy_share_of_income_pct
  .affordable_monthly_repayment_gbp        # disposable × 10%, capped at the debt
  .outcome            -> CAN_PAY_IN_FULL | CAN_PAY_PARTIAL | CANNOT_PAY | FUEL_POVERTY
  .recommended_action -> STANDARD_PLAN | EXTENDED_PLAN | MINIMUM_PLAN
                       | PPM_CONVERSION | DEBT_ADVICE_REFERRAL | WRITE_OFF_CONSIDERATION
  .estimated_plan_months
```

Read that against the residential dunning path's day-28 step, `repayment_plan_offer` — the SLC 27
ability-to-pay obligation. **`recommended_action` and `affordable_monthly_repayment_gbp` are exactly
the two values that step needs in order to make an offer that is anything other than a form letter,
and they are computed by a sibling module in the same package that `arrears_engine.py` does not
import.**

`company/crm/affordability_inference.py` (atom `C6`) is a *second*, separate ability-to-pay organ on
the CRM side. Two implementations of the same concept, in two packages, neither reaching the
collections path — which is the "one legal requirement, five implementations" shape CLAUDE.md names
as the seat's own class of defect.

So the remedy is **a wire, not a build** — and the correction makes that *more* true, not less.

### 3.2 The breathing-space register exists, is complete, and is called by nothing

`company/billing/breathing_space_register.py` implements the Debt Respite Scheme (Breathing Space
Moratorium and Mental Health Crisis Moratorium) Regulations 2020, SI 2020/1311, in force 4 May 2021.
Its own docstring states the supplier's duties:

> 1. Stop all debt collection contact (calls, letters, emails about debt)
> 2. Freeze interest and charges on qualifying debts
> 3. Halt enforcement action (disconnection, court proceedings)
> 4. Cancel any pending disconnection orders

It exposes exactly the query a dunning gate needs: `BreathingSpaceRegister.active_records(as_of)`
and `BreathingSpaceRecord.is_active_as_of(as_of)`.

**It has zero production callers.** `grep -rn "BreathingSpace" company/ saas/` outside the module
itself returns nothing; the only importers in the tree are its own two test files
(`tests/company/billing/test_breathing_space_register.py`,
`tests/company/billing/test_phase_fy_breathing_space.py`).

### 3.3 The collections path has no route to any of them

`company/billing/arrears_engine.py` imports exactly two things:
`company.billing.account_ledger` and `company.crm.account_hierarchy.Segment`.

There is no import path — direct or transitive — from the dunning selection to `capacity_to_pay` or
`breathing_space_register`, **both of which sit in the same `company/billing/` package**, nor to
`affordability_inference` or `vulnerability_register` (the last has four production callers:
`life_event_detector`, `service_log`, `self_rationing_detector`, `consumer_vulnerability_register` —
**none in the collections path**).

### 3.4 The consequence, stated plainly

At HEAD, `current_dunning_step` can select `final_notice`, `prepayment_or_debt_agency` or
`disconnection_warning_or_agency` for an account inside an active statutory moratorium, because
nothing in the selection can see the moratorium. The register that would say so is in this tree,
tested, and consulted by no one.

**This is a compliance defect, not a selection gain**, and that distinction is the whole point of
§5. It does not depend on `B10_competitor_switching_response`, `PB4` or `PB5`. It is filed as a
finding by this pass rather than fixed in it, because a FRAME pass does not write BUILD code.

---

## 4. Claim 4 — retention. PARTLY REFUTED, and the true defect is a definition.

### 4.1 What is actually true

`company/crm/customer_retention.py::_choose_offer` is **not** a fixed offer. The offer value is
already per-account:

```
offer_val = annual_kwh * unit_rate_p_per_kwh / 100.0 * <fraction>
max_spend = net_margin_gbp * _MAX_RETENTION_SPEND_FRACTION   # 0.50
```

so magnitudes already vary with that account's own consumption, own rate and own margin, and the
offer is refused outright when `net_margin_gbp <= 0` (`NET_NEGATIVE_ACCOUNT`) or when 50% of margin
is under £20 (`INSUFFICIENT_MARGIN`). "A fixed offer" is wrong as written.

What *is* fixed is the **rate** (`_LOYALTY_DISCOUNT_FRACTION = 0.05`, `_PRICE_MATCH_FRACTION = 0.08`)
and the **branch** — a categorical on `dominant_driver` crossed with `has_ev` and
`is_electricity_only`.

### 4.2 The defect the prose misses, which is larger than the one it names

`_choose_offer(risk: CustomerChurnRisk, ...)` receives the whole risk object. It reads exactly four
fields — `dominant_driver` (twice), `account_id`, `risk_band`.

`CustomerChurnRisk` (`company/crm/portfolio_churn_risk.py`) also carries:

```
churn_probability: float                                   # this account's probability of leaving
expected_loss_gbp = churn_probability * annual_revenue_gbp  # already derived
```

**Neither reaches the offer decision.** The exact number the atom's own `real_world_twin` says the
desk should price against — "that account's own value and its own probability of leaving" — is
already computed, is sitting inside the argument that was passed in, and is dropped on the floor.
`expected_loss_gbp` has no reader anywhere outside its own module and its own unit test.

### 4.3 And the omission is load-bearing in a published figure

```
RetentionOffer.expected_retention_value_gbp = net_margin_gbp - offer_value_gbp
```

There is no probability anywhere in it. **A quantity named "expected" is not an expectation.** It is
the value of a save assumed *certain*, computed for an account that by construction might never have
left. `CustomerRetentionBook.total_expected_retention_value_gbp` sums it across the book and
`retention_summary()` publishes the total.

This is the CLAUDE.md "before measuring a thing, say what it is" class, and it is the same failure
as *average unit rate*, *net margin* and *bill shock*: a precise-sounding word over a quantity nobody
defined. The honest form is arithmetic on two numbers this tree already has:

> `E[save] = P(leave) × margin_saved − offer_cost`

### 4.4 Why this half is not BUILD-gated

That formula is right in a flat world and right in a reactive one. A world that cannot react makes
the resulting *ranking* uninformative — it does not make the *definition* wrong. The atom's
`block_reason` argues that widening a decision surface against a flat world buys a
better-instrumented null; it makes no claim about arithmetic that is currently mis-named.

---

## 5. The frame: the atom splits in two, and only one half is BUILD-gated

**This is the load-bearing output of the pass.** C29 has been read as one BUILD-gated block. It is
two, and the defects found above fall almost entirely on the ungated side.

### HALF A — SELECTION. Genuinely gated; the `block_reason` stands unaltered.

Conditioning acquisition spend, dunning discretion and offer size on per-account traits *in order to
choose better*. This is exactly what the recorded measurement addresses — the A/B's decision surface
is nine accounts wide and the choosing is worth −£175 against an error bar 25× the estimate.
Widening this before the world can reward width buys a better-instrumented null. Gated on
`B10_competitor_switching_response`, `PB4`, `PB5`, and downstream of R1's inference ceiling
(`tools/r1_inference_ceiling.py`, which names this atom as the R2 headline blocked on it).
**Do not build.**

### HALF B — ARITHMETIC AND LEGALITY. Not gated, and never was.

1. **The breathing-space gate on enforcement steps** (§3). Statutory. Asserts no advantage.
2. **`expected_retention_value_gbp` becoming an actual expectation** (§4). Definitional, on two
   numbers already computed in-tree.
3. **The `capacity_to_pay` wire into the SLC 27 day-28 `repayment_plan_offer` step** (§3.1). A wire
   between two modules in the *same package*, one of which already computes exactly the two values
   the step needs. Includes deciding which of the two live ability-to-pay organs
   (`company/billing/capacity_to_pay.py` vs `company/crm/affordability_inference.py`) is the one,
   because two is the defect.

None of these three makes a selection claim. Each is correct against a flat world. Each is
refutable today. None is what `block_reason` defers.

The split is what this FRAME buys: three-quarters of the *defects* sitting under C29 are not
selection work at all, and have been parked behind a sequencing argument that was only ever about
selection.

---

## 6. Level definitions 0 → 3 (this atom carried none)

- **L0 — today.** Decisions key on segment / channel / categorical-driver tables. Per-account facts
  computed elsewhere in the tree (`churn_probability`, affordability, breathing-space status) do not
  reach them.
- **L1 — Half B landed.** Enforcement steps gated on the breathing-space register; the retention
  "expected" value carries its probability or is renamed to what it actually computes; affordability
  reaches the SLC 27 repayment-plan step. **No selection claim is made at this level.**
- **L2 — conditioned, with the null beside it.** At least one decision surface reads a per-account
  continuous trait, and the published figure carries the selection-corrected null R1 established.
  **This level is reachable while honestly returning "no gain".**
- **L3 — conditioned and priced.** The gain, or its absence, is measured against that null on a
  world that can react (B10 landed), with the value of the choosing stated with its error bar rather
  than asserted.

L2's shape is deliberate. A level definition that can only be met by a *positive* result is a
target, not a diagnostic — and outputs here are diagnostics, never targets
(`tests/company/test_carbon_not_a_target.py` is the enforced form of that rule). L2 must be
satisfiable by a well-measured null, or the map is paying for a flattering answer.

---

## 7. `file_scope` was wrong at HEAD, and is corrected by this pass

The row named `company/customer_ops/` — **that directory does not exist in this tree.** A file scope
pointing at nothing silently un-scopes every tool that reads it. Corrected to the real homes:

- `company/crm/` — `customer_retention.py`, `portfolio_churn_risk.py`, `affordability_inference.py`,
  `acquisition_strategy_book.py`, `marketing_budget.py`
- `company/billing/` — `arrears_engine.py`, `breathing_space_register.py`, `capacity_to_pay.py`
- `company/pricing/` — retained; `value_based_renewal.py` and `renewal_desk.py` are the renewal-side
  twin of the same decision
- `tests/company/` — retained

---

## 8. What this pass deliberately did NOT do

- **No BUILD code.** Epoch gating rule 7; the atom is `loop_stage: idle`.
- **No level move.** 0→3 is not earned by a FRAME doc, and a FRAME that moved its own level would be
  a control keyed to its author.
- **No edit to `block_reason`.** The sequencing judgement it records is correct *for Half A*. This
  doc does not overturn it — it **bounds** it, by showing what it was never about.

---

*Measured against `c1609e374`, 2026-09-19. Every claim above is a statement about files in that
commit; re-ask them before building on them.*
