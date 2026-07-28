# DISCOVER — separate `supply_start` (real relationship start) from the term-schedule anchor

**Finding:** `coldwalk:c1_2_successor_acquisition_date_mismatch` (adjudicated-real, ledger 2026-07-12).
**Mint spec:** `docs/staging/PLANNER_MINTED_supply_start_semantic_separation_2026-07-28.md`.
**Stage:** DISCOVER (self-drawable). No production code changed here; BUILD half is `blocked_on director_level_up`.
**Author:** worker (RUNG-7 DISCOVER half). Evidence-first, every claim cites file:line + a fetched value.

---

## VERDICT (top)

**The gap is REAL and it is LIVE, not merely latent.** `acquisition_date` is a single field carrying
**three** incompatible meanings, and for a successor customer it is proven wrong on surfaces the director
actually looks at *today*:

- **Ground truth (observable):** `C1_2`'s real acquisition event is
  `"event_date": "2020-12-30"`, `"channel": "home-move-win"`, `"predecessor_id": "C1"`
  — `docs/reports/run_output_latest.json:45775-45779`.
- **What the field says:** `"acquisition_date": "2016-01-01"` — `saas/customers.py:340` and copied
  verbatim into the rendered site record `site/data/customers/C1_2.json` (`"acquisition_date": "2016-01-01"`).
- **Consequence:** the customer/company site pages render `C1_2` as "Customer since 2016-01-01" and the
  annual report puts it in the **2016 acquisition cohort** with **~9 years tenure**, when the real
  relationship began **2020-12-30 (~4.99 years phantom history)**.

**Class size:** one overloaded field → **11 distinct wrong-meaning consumer sites** spanning **3 distinct
"real relationship" semantics** (supply-start / tenure / acquisition-cohort), of which the registry
`supply_start` write named by the finding is the canonical instance. A further **~6 generator conduits**
cement the wrong value into the published site JSON. This is a genuine per-customer truth defect, **not** a
`not-worth-the-complexity` case. The mint's escape hatch (§Walls) does **not** apply.

**Scope of the overload:** it affects *only successors* (`successor_of` set AND `acquisition_date` pinned to
the predecessor's genesis date). It does **not** affect:
- base `CUSTOMERS` — their `acquisition_date` (2016-…) genuinely *is* their relationship start; and
- fresh-market `ACQUIRED_CUSTOMERS` — `make_acquired_customer` (`saas/customers.py:451`) sets
  `acquisition_date = acquisition_date` (the real win date), so for those the field is already correct.
The 6 pre-defined `SUCCESSOR_CUSTOMERS` (`saas/customers.py:336-417`) are the only records where the
billing anchor and the real supply-start diverge.

---

## The exact overloaded lines

**The billing/term anchor (CORRECT — must NOT change):**
```
saas/customers.py:340    "acquisition_date": "2016-01-01",   # C1_2 successor — pinned to predecessor C1
saas/customers.py:333-335 # comment: "`acquisition_date` matches the predecessor so
                          #  the term schedule aligns — but actual settlement starts at the churn date."
simulation/run_phase2b.py:883-887 # "Successors use the same acquisition_date as their predecessor so the
                          #  term schedule aligns — actual settlement only starts at the churn date."
```
Verified correct: keeping the anchor at 2016-01-01 makes the successor's 365-day renewal terms land on the
same grid as the predecessor, so `C1_2`'s first term boundary is five steps out (first invoice 2020-12-30),
with no extra reconciliation. **KEEP IT.**

**The overloaded write (THE finding):**
```
company/crm/customer_registry.py:87    supply_start    TEXT NOT NULL,          # column literally means real supply start
company/crm/customer_registry.py:133   ... c.get("acquisition_date", "2016-01-01"), "active",  # writes the ANCHOR into supply_start
```
`seed_from_customers` (`customer_registry.py:109-141`) pipes `acquisition_date` straight into a column named
`supply_start`. For a successor this stamps a supply-start ~5 years before the customer existed.
*(Note: `seed_from_customers` currently has no production caller — grep shows only `tests/company/crm/
test_customer_registry.py`. The registry `supply_start` defect is therefore DEFINITIONAL/LATENT; the
LIVE damage is on the render + tenure + cohort consumers below, which read `acquisition_date` directly.)*

---

## The three distinct semantics (name them precisely)

| # | Semantic | Meaning | Legitimately read at | Correct source for a successor |
|---|----------|---------|----------------------|--------------------------------|
| A | **Term / billing anchor** | The date from which the 365-day fixed-term renewal grid is counted | settlement, renewals, contract-end, renewal-period cadence | predecessor's genesis date (the pin) — **unchanged** |
| B | **Supply-start / relationship start** | The date the *this* customer's supply with us actually began | CRM `supply_start`, "Customer since"/"Acquired" render, onboarding clock, regulatory tenure clock | the real activation event (`event_date`, home-move-win) = 2020-12-30 |
| C | **Tenure / acquisition cohort** | "How long have they been ours" and "which intake year" | churn-estimate tenure input, CLV/payback, per-customer P&L tenure, cohort-year grouping | same real activation date as B |

Semantic **A** is the *only* legitimate reading of `acquisition_date` for a successor. **B** and **C** are
the overload: they mean "real relationship start" but currently read the anchor. B and C share the same fix
input (the observable activation date), so they are one class.

Note the correct home for B already exists and is *separate*: `company/crm/onboarding_journey.py:80`
(`supply_start_date`) and `company/crm/change_of_tenancy_register.py:62,143` (`supply_start_date`,
`accept_supply(...)`) both model a real supply-start date correctly — the registry just doesn't feed from them.

---

## Enumerated consumer table (every `acquisition_date` reader; verdict each)

**Legend:** A = term/billing anchor (CORRECT, keep) · B = supply-start (overload) · C = tenure/cohort
(overload) · LIVE = proven wrong for C1_2 in current output · LATENT = semantic overload not currently
exercised with a successor.

### CORRECT — term/billing anchor (semantic A, keep as-is)
| file:line | role | verdict |
|-----------|------|---------|
| saas/customers.py:495 (`customer_to_settlement_input`) | anchor → settlement input | A keep |
| simulation/settlement.py:64-70 | contract-active window `acq ≤ d < acq+365` | A keep |
| simulation/renewals.py:254,272,356 (`build_renewal_schedule`) | term_start grid from anchor | A keep |
| simulation/run_phase2b.py:445,490,874,887,905,908 | term_start / schedule build | A keep |
| simulation/run_phase1c*/1d/1e*/2a*/0b/0c/scenario/segments | term_start = anchor | A keep |
| company/billing/contract.py:31 (`contract_end_date`) | renewal-date from anchor | A keep |
| saas/churn_model.py:96,100,105 (`_renewal_periods`) | renewal-period cadence from anchor | A keep |
| simulation/population_draw.py:196-331 / segments.py / live_market.py:78 | anchor as settlement seed | A keep |
| simulation/customer_events.py (`win_probability` roll uses term_start, not acq) | — | n/a |

### OVERLOAD — reads anchor but means "real relationship start" (semantics B/C — the fix targets)
| # | file:line | what it does with `acquisition_date` | semantic | status |
|---|-----------|--------------------------------------|----------|--------|
| 1 | company/crm/customer_registry.py:133 | writes it into `supply_start` column | B | LATENT (no prod caller; definitional — the named finding) |
| 2 | company/crm/lifecycle_tracker.py:74 (`tenure_days`) | `as_of − acquisition_date` | C | LATENT (caller-supplied date) |
| 3 | company/crm/acquisition_cohort.py:33 (`lifetime_months`) | drives CLV / net_clv / payback | C | LATENT (caller-supplied date) |
| 4 | company/portal/templates/dashboard.html:72 | renders "Acquired {{acquisition_date}}" | B | LATENT (`_CUSTOMER_INDEX` = base `CUSTOMERS` only, portal excludes successors — app.py:52,171) |
| 5 | simulation/customer_events.py:148 | `tenure_years = term_start − acq` → **company churn estimate** | C | **LIVE** (C1_2 churn est. computed on ~5yr-inflated tenure) |
| 6 | simulation/run_phase2b.py:1175 | `tenure_for_est` → churn estimate | C | **LIVE** (same inflation, main run path) |
| 7 | saas/reporting/annual_report.py:4503 | per-customer `tenure_years` | C | **LIVE** (C1_2 in per_cid_pnl) |
| 8 | saas/reporting/annual_report.py:380,6725 | `_year(acquisition_date)` = acquisition-cohort bucket | C | **LIVE** (C1_2 bucketed to 2016, not 2020) |
| 9 | site/customers/index.html:574 | renders "Customer since {acquisition_date}" | B | **LIVE** (C1_2.json shows 2016-01-01) |
| 10 | site/customers/index.html:189 | "modelled account carried since …acquisition" | B | **LIVE** |
| 11 | site/company/index.html:659 | "a real residential household acquired {acquisition_date}" | B | **LIVE** |

### Generator conduits (propagate the wrong value into published surfaces — not independent meaning, but they cement it)
| file:line | conduit |
|-----------|---------|
| tools/generate_customers_json.py:48,74 | → site/data/customers*.json (`Customer since`) |
| tools/generate_customer_sample.py:196 | → customer_sample.json |
| tools/generate_dashboard_data.py:602 | → dashboard data |
| tools/generate_shadow_html.py:585 | → shadow HTML |
| tools/generate_company_data.py:207 | → company data |
| tools/generate_customer_data.py:216 | → per-customer render dict |

**Wrong-meaning consumer count: 11 distinct sites** (rows 1-11), of which **7 are LIVE-wrong for C1_2 today**
(rows 5-11) and 4 are latent/definitional (rows 1-4). Plus 6 generator conduits that publish the LIVE-wrong
value. Correct (anchor) consumers: ~20 sites, all keep.

---

## BUILD sketch (design only — no code here; BUILD is `blocked_on director_level_up`)

**Principle:** do not touch `acquisition_date` (semantic A is correct and load-bearing for the term grid).
Introduce a *second, separate* field for the real supply-start and route B/C consumers to it.

1. **Source the real date from an observable, not from the anchor.** The activation date already exists as a
   first-class *observable* customer event: `run_phase2b.build_customer_events` emits
   `{event_type:"acquisition", customer_id, event_date, channel:"home-move-win", predecessor_id}`
   (`run_phase2b.py:554-564`; seen in `run_output_latest.json:45775`). A real UK supplier's CRM records
   supply-start from exactly this registration/switch event — so reading it is **wall-legal** (it is an
   observable interface output, not a SIM internal). Base customers and fresh-market `ACQUIRED_CUSTOMERS`
   already carry the correct date in `acquisition_date`; only the 6 successors diverge.

2. **Derive `supply_start` in `customer_registry.seed_from_customers`:**
   `supply_start = real_activation_date(customer)` where `real_activation_date` =
   - the acquisition-event `event_date` for a successor / fresh-market win (passed in via an
     `activation_by_account: dict[str,str]` argument sourced from `won_successor_activations` +
     `fresh_acquisitions`), else
   - `acquisition_date` unchanged for a record with `successor_of is None` (base customers — already correct).
   Keep the column name `supply_start`; stop feeding it the anchor. `acquisition_date` stays available for
   any genuine term-anchor need (none currently read it from the registry).

3. **Route the B/C render + tenure + cohort consumers** (rows 4-11 + conduits) to the derived supply-start:
   add a `supply_start` field alongside `acquisition_date` in the customer dict / generated JSON, and change
   the *render/tenure/cohort* sites to read `supply_start` (leaving every semantic-A site on
   `acquisition_date`). This is the "one field → two fields" separation the finding asks for; the anchor and
   the relationship-start become independently addressable.

4. **R10 class guard (extend the invariant library, not an instance fix):** add a CRM invariant
   `supply_start >= first_observable_event(account)` where `first_observable_event` = min(first meter read,
   first issued bill, acquisition event date). This fails the *entire class* — any account, any run — whose
   `supply_start` predates its own first observable, so a future successor (C2_2…C6_2, or any fresh
   home-move win) cannot silently reintroduce a phantom. Register it next to the existing CRM/compliance
   invariants (`company/compliance/domain_invariants.py` style, `effective_from` dated).

**Portability / scale notes:** keep the successor→activation mapping keyed by the acquisition *event*
(C-S1 event-arrival tolerance: one event, possibly late/out-of-order — don't assume batch completeness).
No new billing engine, no schema cathedral — one extra column-source + one invariant.

---

## R15 mutation-test shapes (BUILD acceptance — both must FIRE on their named defect)

**Test 1 — supply_start separation (the finding):**
- *Arrange:* seed a successor whose real activation date (`event_date`, e.g. 2020-12-30) ≠ its
  `acquisition_date` anchor (2016-01-01).
- *Assert:* `get_account(successor).supply_start == "2020-12-30"` (the activation) AND the anchor
  `acquisition_date` is still usable for term math (unchanged).
- *Mutation (must fail the test):* revert the derivation to write `acquisition_date` into `supply_start`
  (i.e. restore today's `customer_registry.py:133` behaviour) → `supply_start` becomes 2016-01-01 → assert
  fires. This proves the control is not a tautology (activation date is sourced from the *event stream*,
  independent of the anchor field it's compared against — R15 independence).

**Test 2 — R10 class guard (never-earlier-than-first-observable):**
- *Arrange:* a CRM record with `supply_start` earlier than its first observable event.
- *Assert:* the invariant check raises / flags for that account.
- *Mutation (must fire):* set a successor's `supply_start` back to the predecessor's genesis date while its
  first observable (bill/read/acquisition event) is later → invariant must FAIL. Fail-open guard: the check
  must reject a *missing* first-observable as a failure, not pass (R15 fail-open pattern — an absent
  observable is a failed check, not a green one).

**Render-verification (R11) for the BUILD close:** fetch the live `C1_2` customer-page value after the fix
and assert the rendered "Customer since" reads **2020-12-30**, not 2016-01-01 — the pixel, not the file.

---

## Not-worth-it check (mint §Walls)

Explicitly **not** invoked. The overload has ≥7 live wrong-meaning consumers (rows 5-11) producing an
observably wrong per-customer truth for C1_2 in the current published site + annual report. The finding
stands as a real remediation, gated to BUILD.
