# [ADVISOR-FINDINGS] — Money-core characterization: verified defects and signals (2026-08-06)

**Severity:** BLOCKING · **Lane:** E_finance_treasury

**Type:** [FINDINGS]. Companion to merged PR #9 ([CCM], 304 characterization tests over 8 money-core modules, tests-only). The PR body holds 30 findings rows; the tests carry inline surprise-comments on main. This note registers what the advisor INDEPENDENTLY VERIFIED by reading source, plus signals for the wake. Characterized, not endorsed — fixes are the worker's to sequence.

## Two control defects, verified in source
1. **`company/finance/double_entry.trial_balance` structurally cannot fail.** `account_balances` posts the SAME `amount_gbp` to the debit account's dr and the credit account's cr for every entry, so total dr ≡ total cr for ANY journal — corrupt or not — and `balanced` compares two identical-by-construction sums (the code's own comment on the headline totals says "always equal by construction"). A money-invariant control that cannot fire. Second exhibit for retro instantiation 4 (reconciliation-class checks must be *seen to fail*), joining the credit-balance netting case.
2. **`company/pricing/ofgem_price_cap` silently un-caps on fuel-string case.** Contract is lowercase `'electricity' | 'gas'`; a capitalized `"Electricity"` returns None instead of raising, and a None cap reads as "no ceiling" downstream — a customer charged uncapped by spelling. Silent-None on contract violation is the defect class; the fix shape (raise or normalise) is the worker's call. Note the module is otherwise exemplary — the two-lookup cap-window design with the 1 Apr 2022 step is exactly right — which is what makes the one silent hole worth naming.

## Signals
- **Coverage is not a quality signal here:** these eight sat at 95% line coverage before and after; three were at 100% *while carrying the defects above*. Coverage measures execution, not judgment — evidence for the proof-not-effort discipline already ruled for public surfaces.
- **Suite health (wake reconciliation item):** on base main, CCM's comparative run found 10 pre-existing failures within the first 1,700 results; full suite ≈20,800 tests, ~4h projected, `make test` red independent of any CCM change. The wake worker owns triage.
- **Isolation debt is live:** running only the 8 new files dirties observability artifacts (conftest documents this known debt) — advisor reproduced it. Belongs with the lifecycle-certificate work.
- **Next target, parked for the director's word:** `company/billing/invoice.py` — highest money in-degree (6) — was rightly skipped as its surface is the embedded SQLite store (see the corrected data-architecture review). Advisor recommendation: yes, characterize it fixture-based (tmp-file or :memory:), same tests-only fence; brief ready on request.

— Advisor findings, 2026-08-06; every claim above traced to a source read or replicated run this date.


## Pass 2 — second 8 modules (captured verbatim from issue #11, 2026-08-07)

Delivered as an issue, not a PR: a test-spawned liveness push fast-forwarded main past the branch
(mechanism identified and closed same week — see the v4 incident note and PR #13). The eight test
files are on main at `ea3f711`, advisor-executed green there 2026-08-07. Tables below are the
machine's own census/findings/coverage, relocated here so the consume path holds them; same
discipline as Pass 1 — characterized, not endorsed; fixes are the worker's to sequence.

## Phase 1 — selection

### The census, re-run

Same method as PR #9: `ast` walk for in-degree over every non-test module in `company/`, `saas/`, `sim/`, `simulation/`, `interface/`, `background/`, `tools/`, `functions/` (relative imports resolved, `from pkg.mod import X` attributed to the longest matching module); the same walk over `tests/` for tested-by; each module imported in a subprocess for importability.

| criterion | company/ + saas/ (476 non-`__init__` modules) |
|---|---|
| (a) no test file imports it | **1** — `company/market/tou_periods.py` |
| no dedicated `test_<name>.py` exists | 66 |
| imports cleanly in this sandbox | **471 / 476** |

**Criterion (a) is still saturated**, exactly as PR #9 found — 475 of 476 modules are imported by some test. So "untested" in the import sense could not drive selection again, and the ranking is in-degree × money/regulatory criticality × importability, with measured coverage used as a check afterwards rather than as the selector.

The five modules that do not import:

| module | reason |
|---|---|
| `saas/clv_model.py` | needs `arviz` — out of scope per the brief |
| `saas/enterprise_value.py`, `saas/reporting/annual_report.py` | import `saas/clv_model.py`, so `arviz` transitively |
| `company/portal/app.py` | needs `fastapi` — out of scope |
| `company/trading/emir_reporting_register.py` | **`SyntaxError` on Python 3.11.15 — PR #9's F29 still reproduces verbatim** |

### Selected (8)

| module | LOC | in-degree | why selected |
|---|---|---|---|
| `saas/ledger.py` | 574 | **4** | the transaction log every P&L, cash figure and board report is derived from |
| `company/pricing/tariff_engine.py` | 381 | 3 | PR #9's named runner-up ("strong candidate; cut at the 8-module limit") — the company's own forward price |
| `saas/tariff_pricing.py` | 129 | **8** | highest money in-degree left in the codebase; the unit rate every simulated household pays |
| `company/regulatory/settlement_reconciliation.py` | 157 | 1 | brief-named: settlement. The R1/R2/R3/RF exposure the board is shown, with a RAG control |
| `company/market/settlement_reconciler.py` | 112 | 0 | brief-named: the other settlement reconciler. Two implementations of one job is itself worth freezing |
| `company/finance/period_reconciliation.py` | 149 | 1 | brief-named: reconciliation. Where a period's margin is struck and post-close variances are booked |
| `company/regulatory/price_cap.py` | 115 | 0 | brief-named — the sibling `company/pricing/ofgem_price_cap.py`'s header points at. Carries a compliance **check** |
| `company/billing/collections.py` | 90 | 1 | brief-named: collections logic, and importable without `starlette` (only its *test* needs it — see below) |

Three of the eight (`price_cap`, `settlement_reconciler`, `collections`) were taken on brief-named money/regulatory criticality over raw in-degree. Each carries a check, a control or a duplicated regulatory authority — the classes the brief singles out.

### Rejected

| module | in-deg | reason |
|---|---|---|
| `company/billing/invoice.py` | 6 | **owned by the parallel session** per the brief |
| `saas/customers.py` | **22** | highest in-degree in the repo, but a customer/population model, not a money-movement path |
| `company/crm/payment_behaviour_analytics.py` | 7 | genuinely borderline — but a predictive-scoring surface, not money movement or a regulatory obligation. **Best next target.** |
| `company/finance/corporation_tax.py` | 0 | the direct sibling of PR #9's F3 (tax computed but never journalled); cut at the 8-module limit. Second-best next target |
| `company/finance/vat_book.py` | 0 | same class as above — real cash owed to HMRC; cut at the limit |
| `company/compliance/domain_invariants.py` | 6 | 1,453 LOC invariant library; too large to characterize honestly in this scope |
| `saas/customer_reaction.py`, `saas/churn_model.py`, `company/crm/churn_model.py` | 10 / 6 / 6 | behavioural models, not money paths |
| `company/billing/payment_observation_consumer.py` | 2 | 757 LOC; rejected on size in PR #9 and still too large |
| `company/trading/wholesale_credit_exposure.py` | 2 | strong money candidate at 383 LOC; cut at the limit |
| `company/portal/app.py` | — | requires `fastapi` — out of scope |
| `company/trading/emir_reporting_register.py` | — | **cannot be imported** (F29) |

Nothing was dropped mid-flight for needing Skynet-local resources. No test in this change touches Ollama, the file API, the network, or any `docs/staging/` path.

---

## Coverage — before → after

Measured over the union of the 24 existing test files that reference any of the eight (found by grep), with `--cov` restricted to the eight. Before = that set. After = that set **+** the 8 new files. Same command, same scope, so the columns are comparable.

| module | before | after | stmts | missed before → after |
|---|---|---|---|---|
| `company/billing/collections.py` | **0%** * | 98% | 49 | 49 → 1 |
| `company/finance/period_reconciliation.py` | 99% | **100%** | 91 | 1 → 0 |
| `company/market/settlement_reconciler.py` | 100% | 100% | 35 | 0 → 0 |
| `company/pricing/tariff_engine.py` | 97% | 99% | 152 | 4 → 2 |
| `company/regulatory/price_cap.py` | 97% | **100%** | 59 | 2 → 0 |
| `company/regulatory/settlement_reconciliation.py` | 100% | 100% | 69 | 0 → 0 |
| `saas/ledger.py` | 99% | **100%** | 156 | 1 → 0 |
| `saas/tariff_pricing.py` | 100% | 100% | 18 | 0 → 0 |
| **TOTAL** | **91%** | **99%** | **629** | **57 → 3** |

\* `collections.py` does not appear in the before run at all: **no collectable test imports it.** Its only existing test file, `tests/company/billing/test_collections.py`, imports `starlette.testclient` and errors at collection in this environment, so all 49 statements of a live collections path were unexecuted here. That is the one place in this pass where coverage was a real gap; everywhere else the story is PR #9's again — **three of eight were already at 100% before a line was written**, and every finding below was sitting under existing tests that executed those lines without asserting on the values.

The 3 remaining uncovered statements are `collections.py:89` (the oldest-due-date reassignment, unreachable while the SQL orders by due date) and `tariff_engine.py:237,248` (the `REGIME_DETECT_ENABLED = False` short-circuit, and the non-positive-long-mean guard).

---

## Findings — SUSPECTED, not adjudicated

Numbering continues from PR #9 (F1–F29). Every row is pinned by a passing test that asserts the **current** behaviour and carries an inline comment naming the surprise. I am not the judge of these; the resident worker is. Nothing was fixed.

Per the brief, every check/validation/reconciliation entry point was driven with at least one deliberately corrupt input and the result — fires or does not fire — frozen. **Four controls were found that cannot fail on their own named defect** (F47, F48, F57, F61).

### `saas/ledger.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F30** | `derive_cash_position` | one £1,000 bill, 10% provision, payment lifecycle on | **`1800.0`** | `billing_event` is +£1,000 (an invoice **raised**) and `payment_received_event` is +£900 (the cash actually collected against that same invoice). Both are positive; the function sums every event. The moment payment-lifecycle events are switched on, the reported cash position is roughly **double** the money that moved. Without them the same bill correctly yields £1,000. | double-count |
| **F31** | `derive_pnl` | £1,050 bill incl. £50 VAT, £400 wholesale | `revenue_gbp 1000.0` but `cash_net_margin_gbp 545.0` | `revenue_gbp` is struck net of VAT; `cash_net_margin_gbp` is `cash_collected - wholesale - capital - non_commodity` and never subtracts the VAT remittance, even though the event exists and the cash was collected VAT-inclusive. Cash margin is overstated by the whole VAT liability. | unit |
| **F32** | `make_billing_event` / `build_ledger` | £1,000 bill and £9,999 rebill, same customer/commodity/`period_start` | identical `transaction_id`, both appended | The id is keyed on (customer, commodity, period_start) — the amount is not in the key. The ledger carries two different amounts under one identity, so any consumer deduplicating on `transaction_id` (C-S2 idempotent replay) drops real money. `make_fixed_cost_event` collides on month alone. | boundary |
| **F33** | `unbilled_revenue_accrual` | `catchup_applied` set, `catchup_period_start` **missing** | every earlier estimate resolved; accrual → `0.0` | The missing bound defaults to `""`, and `"" <= period_end <= end` is true for every estimated bill up to the end date. One malformed catch-up silently writes off a customer's entire unbilled-revenue asset. The mirror case (missing *end*) fails **closed** — two missing bounds, opposite directions. | fail-open |
| **F34** | `unbilled_revenue_accrual` | one estimated bill of `0.0`; or +£500 and −£500 | `outstanding_bill_count 1` (or 2), `by_customer {}` | The count increments per unresolved bill but `if customer_total:` drops any customer netting to zero. The returned dict is internally inconsistent: outstanding bills with no customer owning them. | boundary |
| **F35** | `build_ledger` | any bill with a provision > 0 | appends to a **process-global** decision log, stamped `datetime.now(utc)` | Documented as deriving a log from existing outputs, and the functions below it are labelled "pure function — no simulation state". Building the same ledger twice is not a no-op on process state and is not reproducible — the C-S2 deterministic-replay constraint. | purity |
| **F36** | `build_ledger` | customer with an electricity record then a gas record | every bill stamped `"electricity"` | Commodity is inferred from whichever settlement record for that customer appeared **first**, then applied to all their bills. A dual-fuel customer's gas bills are mislabelled, silently. | boundary |
| **F37** | `derive_pnl` | a `retention_cost_event` of £250 | `net_margin_gbp` unchanged; cash position −£250 | `make_retention_cost_event` mints real negative cash, but `derive_pnl` has no branch for it. Retention spend moves the cash position and appears in **no margin line at all** — the two views disagree by the whole spend. | omission |
| **F38** | `derive_pnl` | £1,050 bill with `vat_gbp` absent | `revenue_gbp 1050.0`, no `vat_remittance_gbp` key | `if b.get("vat_gbp")` — a missing, `None` or `0.0` VAT field produces no remittance event, so the VAT-inclusive total is reported as ex-VAT supplier revenue. £50 of HMRC's money booked as the company's own, with no line showing it. Zero-rated and field-dropped are indistinguishable. | fail-open |
| **F39** | `derive_pnl` | a `back_billing_write_off_event` missing `write_off_amount_gbp` | `KeyError` | Subscripted directly rather than `.get`, so one malformed memo event takes down the **entire P&L derivation**, not just its own line. | boundary |

### `company/pricing/tariff_engine.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F40** | `get_forward_price` | 30 half-hourly records **from a single day** at £500 | prices at `540.0` | `MIN_RECORDS_FOR_ESTIMATE` is checked as `len(filtered) < 30` over raw **rows**, not distinct days. One day of HH data satisfies a guard whose whole purpose is to refuse pricing on thin history; the engine then reports a "120-day rolling estimate" built from part of one day, with no signal that it did. | boundary |
| **F41** | `get_forward_price` | `fuel="Gas"`, winter delivery | `108.00` instead of `120.75` | Two separate exact-match tests on the fuel string: the risk premium is `gas` or *else electricity*, and the seasonal block matches `"electricity"`/`"gas"` exactly. So `"Gas"` takes the **electricity** premium **and** gets no seasonal shape — a 10.6% under-price from a capitalisation slip, silently. Same fail-open, case-sensitive fuel-match class as PR #9's F21. | boundary / unit |
| **F42** | `get_forward_price` | two 12-month contracts starting 1 Oct and 1 Apr | `116.64` vs `103.68` | The winter/summer shape is chosen from the **contract start month alone**, while `term_months` scales only the term premium. A full-year deal delivers across every season either way, so two identical annual contracts six months apart differ by 12.5% on this factor. | unit |
| **F43** | `_compute_regime_premium` | 60 days at £200 over a £100 baseline | ratio `1.5`, not `2.0` | `long_means` runs `long_start..end_date` — the **same end date** as the short window — so the "baseline" contains the period it is compared against. The sibling `_estimate_term_structure_slope` in the same module uses **disjoint** windows. Two conventions for "short vs long"; the overlap systematically understates divergence, which is exactly the regime-change blindness the project guards against. | boundary |
| **F44** | `compute_portfolio_premium` | `[8.0, 8.0, 8.0, 8.0]` — margins as **percentages** | `-0.05` (max discount) | The classic unit confusion at this seam is not caught: shortfall becomes −7.92 and the clamp turns it into the maximum 5% tariff **cut**. A company hitting its target exactly would cut every tariff by 5% and nothing would report an anomaly. The function also never truncates to `PORTFOLIO_PREMIUM_LOOKBACK` despite the constant documenting "the last N terms". | unit |
| **F45** | `compute_portfolio_premium` | — | never called | `CompanyTariffEngine.get_forward_price` does not call it. The Phase 17a "portfolio learning premium" only reaches a tariff if some caller remembers to multiply it in; the engine's own output is unaffected by the company's realised margins. | dead path |
| **F46** | `get_forward_price` | `term_months=1` vs `12` | identical | The structural term premium is `max(0.0, tenor - 1) * 2%`, so sub-year deals get no discount. The stated rationale (longer deals carry more price risk) implies the converse should be cheaper; it is floored instead. | boundary |

### `company/regulatory/price_cap.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F47** | `CapComplianceCheck.status` | `quarter="2024-Q1"`, supplier `99.0p`, **`cap_rate_p_kwh=150.0`** | `BELOW_CAP`, `is_compliant True` | **The control cannot fail.** The cap rate is supplied by the *caller*. The class holds a quarter key and the module holds a full published table keyed by exactly that string — and never looks the rate up (the real 2024-Q1 ceiling is 24.5p). A supplier declares itself compliant by passing its own cap number. R15 tautology: the checked value is not independent of the checker. | tautology |
| **F48** | `CapComplianceCheck.status` | `quarter="2026-Q1"` / `"2024-q1"` / `""`, supplier `500.0p` | `PRE_CAP`, `is_compliant True` | The quarter key does one thing: if it is not in the table the status is `PRE_CAP`, which `is_compliant` treats as compliant. The table ends at **2025-Q1**, so *every* future quarter — plus any case typo or missing value — makes any breach compliant. Correct for genuinely pre-2019 quarters, which is what hides it. The sibling `ofgem_price_cap.py` documents forward-carry precisely because the alternative "would silently un-cap every resi customer"; this module has the opposite behaviour. | fail-open |
| **F49** | `CapComplianceCheck` | gas rate `6.3p` vs electricity cap `24.5p` | `BELOW_CAP`, headroom `18.2p` | `commodity` is recorded and read by nothing. A fuel mismatch between the rate and the ceiling is structurally invisible. | omission |
| **F50** | `peak_annual_bill_year` | — | `"2022"` (a `str`), annotated `-> int` | Returns a 4-char slice; `== 2022` is False, so any arithmetic or int comparison downstream breaks or silently mismatches. It also filters to quarters ending `-Q2`/`-Q3`, so a peak in Q1 or Q4 can never be found — it agrees with the unfiltered `cap_summary` peak by coincidence, not construction. | unit |
| **F51** | this module vs `company/pricing/ofgem_price_cap.py` | electricity, 2019-Q1 / 2022-Q3 / 2024-Q1 | `17.14` vs `16.52`; `52.00` vs `28.34`; `24.50` vs `28.62` p/kWh | **Two modules claim the same regulated ceiling and disagree, in both directions.** Evidence for why: this module's "2022-Q3" carries 52.00p and a **£3,549** typical annual bill — the published levels of the cap period beginning **1 October 2022** — while the sibling's 1 Jul 2022 window is 283.4 £/MWh, which is this module's "2022-Q1"/"Q2" figure. The two tables are the same regulatory history under **non-aligned quarter labels**. On top of that the sibling applies the Energy Price Guarantee (340 £/MWh for Oct–Dec 2022) where this module publishes the un-guaranteed 52.0p. Which module a caller reaches for decides whether a rate is a breach. | unit |

### `company/billing/collections.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F52** | `get_overdue_invoices` | a db path that does not exist | creates the file **and its parent directory**, returns `[]` | A **read** function calls `create_schema(db_path)`. Two consequences in one line: a query has a filesystem write side effect, and a typo'd or mis-deployed DB path reports "no overdue debt" rather than failing. Silent, and the answer is the reassuring one. | fail-open |
| **F53** | `get_overdue_invoices` / `get_collections_queue` | `partially_paid` invoice, £900 of £1,000 paid | reported as `1000.0` owed | `partially_paid` rows are selected but the amount reported is `total_gbp` — the **original** invoice value. The `invoices` table has no amount-paid column at all, and this module never joins the separate payments table. Collections chases, and the queue totals, money already received. | unit |
| **F54** | `get_overdue_invoices` | `payment_status` of `"Unpaid"`, `"disputed"`, `"written_off"`, `""` | invoice vanishes from collections | The WHERE clause matches two exact lowercase literals. A capitalisation difference, an empty status, or any status the rest of the system invents later removes the debt from collections permanently — never chased, and never reported as excluded. There is no unrecognised-status bucket. | fail-open |
| **F55** | `get_overdue_invoices` | `due_date` of `"31/05/2024"`; separately `"2024-02-30"` | silently excluded; **`ValueError` aborting the whole run** | The overdue test is a string comparison against an ISO pivot, so a UK-format date sorts out of the query and the debt disappears. An ISO-*shaped* impossible date passes the filter and then raises in `date.fromisoformat` — and there is no per-row guard, so one bad row stops every other customer's debt from being returned. Same whole-run-outage shape as PR #9's F9. | fail-open / boundary |
| **F56** | `get_collections_queue` | £1 overdue 545 days vs £50,000 overdue 89 days | the £1 account ranks first | The queue a credit team works down is sorted purely by `-max_days_overdue`, with no value-weighted view anywhere in the output. The customer tier is likewise taken from the single oldest invoice. | boundary |

### `company/market/settlement_reconciler.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F57** | `reconcile_against_bill` | statement claiming 1,000 kWh @ £100/MWh but billing **£3**; company billed £3.05 | `flagged False`, imbalance 1.7% | **The control cannot fire on a corrupt statement.** `volume_kwh`, `ssp_gbp_per_mwh` and `hedge_pnl_gbp` are carried on the statement and read by nothing — no function in the module ever compares `volume × price` against `net_settlement_cost`. The one input that makes a settlement statement provably wrong is invisible to the reconciliation that exists to catch it; only a revenue gap can ever flag. A period whose entire economics are a £5,000 hedge loss reconciles identically to one with no hedge. | tautology |
| **F58** | `reconcile_against_bill` | £1,000,000 settlement, £11 gap, `threshold_pct=50.0` | `flagged True`, `imbalance_pct 0.0` | `flagged` is an OR against a module-level **£10** constant the caller cannot reach, so `threshold_pct` cannot reduce flagging below it. At portfolio scale a 0.001% discrepancy flags, i.e. the control flags everything and the parameter is inert. | boundary |
| **F59** | `reconcile_period_batch` | statement for C2, C2 absent from `billed_revenues` | reconciled against `0.0`; −£200 adverse | `.get(cid, 0.0)` makes a **missing billing record** indistinguishable from a genuine zero-revenue customer. A data-integrity failure is laundered into a trading loss with no separate signal. The reverse — revenue billed with no settlement statement — is dropped silently and `checked` never notices. | fail-open |
| **F60** | `imbalance_summary` | `{}`; and a perfectly reconciled 3-statement batch | a well-formed, cheerful report | Summarising a batch result that is entirely missing returns zeros and `net_position "favourable"` rather than raising. Exactly-zero imbalances are counted in **neither** bucket, so `favourable + unfavourable != checked` and a flawless period looks like an empty one. `>= 0` also calls a dead-flat zero "favourable". | fail-open |

### `company/regulatory/settlement_reconciliation.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F61** | `_rag` | £1,000,000 max adverse, monthly revenue `0.0` (or negative) | **`GREEN`** | **The control cannot fail on its own worst case.** The guard exists to avoid a divide-by-zero, but it answers "is this exposure safe?" with "yes" instead of declining to answer. Zero revenue with open settlement exposure is the worst state a supplier can be in — it is the SoLR shape exactly. A negative max-adverse also rates GREEN. | fail-open |
| **F62** | `build_reconciliation_series` | `hh_revenue_fraction=2.0` | `max_adverse_gbp -133_800.0`, `rag GREEN` | The fraction is never bounded. Above 1.0 the blended variance goes **negative**, so the board is told its worst-case adverse settlement adjustment is a £134k *gain*, the RAG control rates it GREEN, and the corrupt fraction is echoed back verbatim into the published record. | fail-open |
| **F63** | `build_reconciliation_series` | any revenue at the default `hh_revenue_fraction=0.90` | always `GREEN` | The exposure is a fixed 0.372 × 0.0085 = 0.316% of annual revenue, i.e. **3.79% of monthly revenue whatever the revenue** — under the 5% GREEN threshold by construction. At the default the RAG rating has one reachable output for every real portfolio; AMBER/RED are only reachable by moving the HH fraction toward non-HH. | tautology |
| **F64** | `build_reconciliation_series` | a year with `revenue_gbp` of `0.0`, negative, or **absent** | the year vanishes from the series | `if rev <= 0: continue`, and `.get(..., 0.0)` makes a malformed year identical to a zero year. A loss-making year is not rated — it is not reported at all, and `len(series)` silently stops matching the number of trading years. (A non-numeric year *key* is the one malformed input that does raise.) | fail-open |
| **F65** | `build_reconciliation_series` | 2020 vs 2022, same revenue | every number identical | The module docstring promises a "crisis-year bias: demand destruction causes actual < estimated consumption → net credit in late reconciliation". `is_crisis_year` is set for 2021/2022 and then used by nothing; pool, adverse band and expected adjustment are unchanged. The documented asymmetry does not exist in the numbers. Related comment drift: the `pool_fraction` inline comment says "e.g. 2 months / 12 = 0.17" where the actual constant is 4.46 months → 0.372. | dead path |

### `company/finance/period_reconciliation.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F66** | `add_variance` after `close()` | −£50,000 booked into a RECONCILED period | accepted; margin restated; status unchanged | `close()` sets a status and nothing else. A closed period stays fully writable, so post-close adjustments silently restate a signed-off period's margin with no reopen step, no audit trail and no move to DISPUTED. There is no `reopen()`; `DISPUTED` and `WRITTEN_OFF` exist in the enum but nothing in the module ever sets them. | boundary |
| **F67** | `add_variance` | an RF adjustment booked 28 months later | dated `period_start` | Every variance is stamped with the period's *start* date whatever period it was discovered in, so a variance carries no information about **when the company learned of it** — the entire point of a 28-month reconciliation tail. | boundary |
| **F68** | `add_variance` / `open_period` | the same `variance_id` twice; the same `period_id` twice | both counted | No uniqueness check on either. A re-submitted settlement adjustment is double-counted against margin with no error. A duplicate period is stored twice and **both** are summed into `annual_gross_margin_gbp`, but `get()` can only ever reach the first — the second is unaddressable while still moving the annual figures. | boundary |
| **F69** | `annual_gross_margin_gbp` | period with £90k gross and a −£40k variance | `50_000.0` | Named `annual_GROSS_margin_gbp`, sums `adjusted_margin_gbp` — i.e. net of variances. Name and number differ. Related: `variances_by_type` nets signed amounts, so a −£1m and a +£1m settlement difference report `0.0`, identical to no variance at all. | unit |
| **F70** | `ReconciliationVariance` | `REVENUE_SHORTFALL` of **+£50,000** | `is_adverse False` | Nothing ties the sign to the type; the type is a free-text label on an arbitrary signed number. A shortfall that increases margin is accepted and reported as favourable. | sign |

### `saas/tariff_pricing.py`

| # | function | input | current behaviour | why it looks wrong | class |
|---|---|---|---|---|---|
| **F71** | `price_tou_tariff` | any ToU customer | priced with **zero** policy and network cost | The function takes no `policy_cost_per_mwh`, `network_cost_per_mwh` or `profitability_uplift_per_mwh` and passes none to `price_fixed_tariff`. Every smart-meter ToU customer is priced with **no RO/CfD levy, no DUoS/TNUoS recovery and no net-negative-account repricing** — ~£65/MWh in the frozen example. The omission is in the signature: there is no argument a caller could pass to include them. | omission |
| **F72** | `price_fixed_tariff` | `term_start=""` or `"2023"`; separately a `datetime.date` | prices at the **pre-2023** sigma; `TypeError` | `term_start >= "2023-01-01"` is a string comparison. A missing or truncated term start sorts below the pivot and silently takes the cheaper regulatory-floor capital charge — malformed input systematically **under-prices risk**. A real `date` object, the natural thing for a caller to hold, raises. | fail-open / boundary |
| **F73** | `price_fixed_tariff` | `eac_kwh=0`; separately `-3100` | `ZeroDivisionError`; prices normally | A vacant or new property with zero EAC crashes the pricing call rather than returning forward + margin. A *negative* EAC is arithmetically invisible because the size term cancels, so a sign error upstream prices identically to a valid customer. | boundary |
| **F74** | `price_fixed_tariff` | `naked_fraction` omitted | capital component `£24.68` vs `£3.70` per MWh | The default is 1.0 — capital priced as if **none** of the volume were hedged — while the mandate floors hedging at 85%. A caller that forgets the argument charges 6.7× the capital cost the company actually incurs. Flagged in the module's own docstring as "backward compatible"; recorded because the default is the trap. | unit |
| **F75** | `price_fixed_tariff` | `forward_price=-50.0` | rate `-60.34` | The capital charge is proportional to the forward price with no floor, so a negative forward — which GB wholesale really produces — turns the collateral charge into a **discount**. `naked_fraction` is likewise unbounded above 1.0. | sign |

### One control that does hold

Worth stating, since the table above is all negative: `price_tou_tariff`'s revenue-neutrality claim is **true**. At the documented 30/70 peak/off-peak split, ToU revenue equals flat revenue to floating-point precision (`0.30 × 1.50 + 0.70 × 0.7857… == 1.0`). Frozen, along with the fact that the neutrality is an assumption about the *customer*, not a property of the tariff — a 50/50 customer pays 14.3% more.

---

## Test design

- Each file's module docstring carries: *"CHARACTERIZATION: freezes current behaviour, including behaviour that may be defective. Characterized, not endorsed."*
- Files mirror module paths (`company/billing/X.py` → `tests/company/billing/test_X_characterization.py`), suffixed so they sit alongside any existing `test_X.py`.
- **Fixed, explicit inputs throughout.** No RNG is drawn anywhere, so there is nothing to seed. Where a value is a digest — `saas/ledger.py`'s uuid5 `transaction_id`s — three are frozen **verbatim**, so a change to the id scheme (which would silently re-key every event in every ledger and break C-S2 replay) cannot pass unnoticed.
- **Time gaps, recorded rather than worked around.** Seven of the eight modules take every date as an argument, so their paths are fully freezable. Two gaps exist and are marked in the tests:
  - `company/billing/collections.py` defaults `as_of` to `date.today()`. Every value assertion passes `as_of` explicitly; the default path is exercised for membership only, in a test that says so.
  - `saas/ledger.py`'s `build_ledger` reaches `log_decision_event`, which stamps `datetime.now(utc)` into a module-global log with no injection point. That path is exercised (F35) but its timestamp is not asserted.
- **Every check, validation and reconciliation entry point gets at least one deliberately corrupt input**, per the brief: `_rag` with zero revenue, `CapComplianceCheck` with a fabricated ceiling, `reconcile_against_bill` with an internally impossible statement, `build_reconciliation_series` with an out-of-range fraction, `unbilled_revenue_accrual` with a half-missing range, `get_overdue_invoices` with two shapes of bad date and a nonexistent database, `price_fixed_tariff` with a zero EAC and an empty term start, `derive_pnl` with a malformed memo event. In each case the test freezes **whether the check fires** — and in four cases it does not.
- Scope limited to in-memory and pure surfaces plus one throwaway SQLite database under `tmp_path` (collections). Nothing touches the network, Ollama, the file API, or `docs/staging/`.

---

## `make check` — attempted, reported both ways

`make check` = `ruff check .` then `pytest tests/ -v --tb=short`.

**Lint step — fails, and already failed before this change.**

```
ruff check .   (base tree, my files stashed) → Found 2421 errors
ruff check .   (with my files)               → Found 2421 errors
ruff check <the 8 new files>                 → All checks passed!
```

Identical count either way: **this change adds zero lint errors.** The 2,421 are pre-existing.

**Test step — the full suite does not finish quickly in this sandbox.** It is ~21,400 tests; it was started and was still running when this was written. What I can report with evidence:

- **All 264 new tests pass**, in 1.04s: `264 passed`.
- The 24-file scoped run used for the coverage table: **`17 failed, 870 passed`** after, **`17 failed, 606 passed`** before. The failure lists are **byte-identical** (`diff` of the sorted `FAILED` lines is empty), so all 17 are pre-existing and none is introduced here:
  - 9 × `tests/architecture/test_static_quality_ratchet.py` (tool-version pinning and mypy/ruff baseline checks — environment-sensitive; the branch merged as PR #8 notes the baseline is host-interpreter-specific)
  - 5 × `tests/company/test_phase_ob_settlement_reconciliation.py` and 2 × `tests/simulation/test_phase29a_network_charges.py` (board-section renderers reached through `saas/reporting/annual_report.py`, which needs `arviz`)
  - 1 × `tests/tools/test_lane_wall_hook.py`
- Repo-wide collection: **21,373 tests collect, 74 errors — all 74 are `arviz` (49), `starlette` (23), `fastapi` (2)**, exactly the heavy-modelling/service class the brief puts out of scope. None involves the selected eight.
