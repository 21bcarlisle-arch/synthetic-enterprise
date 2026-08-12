# Money-core characterization (PR #9 + issue #11) — disposition register

Source: `docs/staging/in_progress/ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md`
— it stays in `in_progress/`, NOT `done/`, because the 40 findings below are unbuilt
work rather than staging noise; the copy that was left in the staging root (still
reading BLOCKING, still re-ringing the doorbell as unactioned) is removed in the same
commit as this register.
(Originally BLOCKING, lane `E_finance_treasury`; downgraded to OPEN when the six R15
wall items closed.) 46 numbered findings (F30–F75) plus two
advisor-verified control defects. The advisor characterized, did not endorse;
sequencing the fixes is the worker's.

This register exists so the 40 findings NOT fixed in the first pass stay visible.
A findings note that gets archived with most of its contents unactioned is how a
register turns back into prose.

## Sequencing rule used

R15 is a WALL: a control that cannot fail is worse than none. So the first pass
took **every control that structurally could not fire**, and nothing else —
6 defects across 5 modules. Value-and-unit defects (wrong number, right control)
are queued below; they are real, but a wrong number is visible in a way that a
green light over a corrupt book is not.

## Pass 1 — CLOSED (2026-08-12)

Each fix carries an R15 mutation proof: the frozen-defect characterization test
was rewritten to assert the control now FIRES, and each names the edit that
reverts it to green. All 5,001 tests in the four affected directories pass.

| ref | module | defect | fix |
|---|---|---|---|
| verified-1 | `company/finance/double_entry.py` | `trial_balance.balanced` a TAUTOLOGY — one `amount_gbp` posted to both a dr and a cr bucket, so the totals were equal by construction for any journal, corrupt or not (the code said so itself: "always equal by construction") | `entry_violations`/`journal_violations` check what CAN fail on this record shape — two distinct accounts, both known to `ACCOUNTS`, finite non-negative amount. `balanced` requires no violations AND the tie; `violations` names each breach. Malformed rows are excluded from the totals rather than raising |
| verified-2 | `company/pricing/ofgem_price_cap.py` | Silent un-cap on fuel case: `"Electricity"` returned None, and None means "no cap applies" — a customer charged uncapped by a spelling | `_normalise_fuel` folds case/whitespace and RAISES on anything else. Checked before the pre-2019 shortcut so a bad fuel cannot hide behind a legitimate None |
| F47 | `company/regulatory/price_cap.py` | `CapComplianceCheck` TAUTOLOGY — the cap was supplied by the caller, i.e. the party being checked; the module's own published table was never consulted | `effective_cap_p_kwh` resolves the ceiling from the table. The caller's `cap_rate_p_kwh` is inert (kept for signature compatibility, defaulted) |
| F48 | `company/regulatory/price_cap.py` | FAIL-OPEN — any quarter absent from the table was `PRE_CAP`, which reads as compliant. The table ends 2025-Q1, so every future quarter, case typo and empty string cleared any breach | New `CapStatus.UNKNOWN`, not compliant. `PRE_CAP` now requires a parsed quarter genuinely before 2019-Q1 |
| F49 | `company/regulatory/price_cap.py` | `commodity` recorded and read by nothing — a gas rate cleared against the electricity cap | Lookup keyed on quarter AND commodity; unrecognised commodity → `UNKNOWN` (fixed with F47: the lookup cannot be done without it) |
| F57 | `company/market/settlement_reconciler.py` | TAUTOLOGY — `volume_kwh`, `ssp_gbp_per_mwh`, `hedge_pnl_gbp` read by nothing, so the one input making a statement provably wrong was invisible to the reconciliation that exists to catch it. Only a revenue gap could flag | `_statement_integrity` ties volume × SSP − hedge against the stated cost. Reports `statement_checked`/`statement_consistent`/`implied_cost_gbp`; an unchecked statement reports `checked=False`, never a reassuring pass |
| F61 | `company/regulatory/settlement_reconciliation.py` | FAIL-OPEN — `_rag` returned GREEN on zero/negative revenue, rating the worst state a supplier can be in (open exposure, no revenue — the SoLR shape) as safest. Negative max-adverse also GREEN | Zero revenue with exposure → RED; zero revenue with zero exposure stays GREEN; negative max-adverse → RED |

**Test-fixture defect found while fixing F57 (not in the advisor's list).** Both
reconciler test files built statements from a FIXED `volume_kwh=1000.0` while
overriding `net_settlement_cost_gbp`, so almost every fixture contradicted its
own cost line. Harmless while nothing read those fields — and precisely why the
gap survived. Both helpers now derive volume from cost/SSP/hedge; the tests that
want a corrupt statement pass volume explicitly, which is what makes them corrupt.

## Open — queued, NOT fixed

Still-live findings, by class. None is a control that cannot fail; all are value,
unit, sign, omission or dead-path defects.

- **`saas/ledger.py`** — F30 cash double-count (payment lifecycle on → position
  ≈2× the money that moved), F31 VAT never subtracted from cash margin, F32
  `transaction_id` collision (amount not in the key — breaks C-S2 replay dedup),
  F33 missing catch-up bound writes off a customer's unbilled revenue, F34
  internally inconsistent accrual dict, F35 `build_ledger` not pure (process-global
  log, wall-clock stamp), F36 dual-fuel bills all stamped one commodity, F37
  retention spend in no margin line, F38 missing VAT field books HMRC's money as
  revenue, F39 one malformed memo event `KeyError`s the whole P&L.
- **`company/pricing/tariff_engine.py`** — F40 thin-history guard counts rows not
  days, F41 `"Gas"` takes the electricity premium and no seasonal shape, F42
  annual contracts differ 12.5% on start month, F43 overlapping regime windows
  understate divergence, F44 percent/fraction unit confusion → max discount, F45
  `compute_portfolio_premium` never called, F46 sub-year term premium floored.
- **`company/regulatory/price_cap.py`** — F50 `peak_annual_bill_year` annotated
  `-> int` returns a `str`, and filters to Q2/Q3 so a Q1/Q4 peak is unfindable.
  F51 **this module and `company/pricing/ofgem_price_cap.py` disagree about the
  same regulated ceiling in both directions** — non-aligned quarter labels plus
  EPG applied in one and not the other. Two modules claiming one legal authority
  is the structural item here; F51 is the highest-value open finding.
- **`company/billing/collections.py`** — F52 a read function creates the DB (a
  typo'd path reports "no overdue debt"), F53 chases the original invoice value
  ignoring part payments, F54 unrecognised payment status silently drops the debt,
  F55 UK-format date excluded / impossible ISO date aborts the whole run, F56
  queue ranked by age with no value weighting.
- **`company/market/settlement_reconciler.py`** — F58 £10 floor makes
  `threshold_pct` inert at portfolio scale, F59 missing billing record laundered
  into a trading loss, F60 `imbalance_summary` cheerful on an empty batch and
  exact zeros counted in neither bucket.
- **`company/regulatory/settlement_reconciliation.py`** — F62 `hh_revenue_fraction`
  unbounded (>1 → negative exposure; the RAG now fires but the number is still
  nonsense), F63 at the default fraction the exposure is 3.79% of monthly revenue
  whatever the revenue, so AMBER/RED are unreachable — a second tautology, in the
  THRESHOLD rather than the guard, F64 a zero/negative/absent revenue year
  vanishes from the series, F65 `is_crisis_year` documented and used by nothing.
- **`company/finance/period_reconciliation.py`** — F66 a closed period stays
  writable with no reopen step or audit trail, F67 variances stamped with the
  period start so "when we learned of it" is lost, F68 no uniqueness on variance
  or period id (duplicate period summed twice but unreachable via `get()`), F69
  `annual_gross_margin_gbp` is net of variances, F70 variance type not tied to sign.
- **`saas/tariff_pricing.py`** — F71 ToU priced with zero policy and network cost
  (~£65/MWh missing, and no argument exists to pass them), F72 string-compared
  term start under-prices risk on malformed input and `TypeError`s on a real
  `date`, F73 zero EAC `ZeroDivisionError` / negative EAC invisible, F74
  `naked_fraction` defaults to 1.0 against an 85% hedging floor (6.7× capital),
  F75 negative forward turns the collateral charge into a discount.

### Cross-cutting, from the note's own signals

- **F63 is the same class as F61 but in the threshold, not the guard** — worth
  taking next inside this lane: a RAG with one reachable output is a control that
  cannot fail, so it is a WALL item the first pass did not reach.
- **Coverage is not a quality signal here.** All eight modules sat at 95% line
  coverage before and after; three were at 100% *while carrying the defects
  above*. Coverage measures execution, not judgment.
- **F29 still reproduces**: `company/trading/emir_reporting_register.py` raises
  `SyntaxError` on Python 3.11.15 and cannot be imported at all.
- **Isolation debt** — running the 8 new test files dirties observability
  artifacts (documented in conftest). Belongs with the lifecycle-certificate work.
- **Next characterization target** the advisor recommends: `company/billing/invoice.py`
  (highest money in-degree at 6), fixture-based against a tmp SQLite store.
