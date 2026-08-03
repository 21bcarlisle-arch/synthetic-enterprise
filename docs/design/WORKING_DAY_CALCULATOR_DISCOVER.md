# Working-Day Calculator — DISCOVER/design half (2026-07-28)

> **BUILD PASS 1 LANDED 2026-08-03 — and it found two errors in this document. Read these
> before trusting §1 or §4 below; both are corrected in place, with the original claim kept
> visible so the correction is auditable rather than a silent rewrite.**
>
> 1. **§1's census of 22 is an UNDERCOUNT. The real figure is 25.** The census was built by
>    grepping for four known helper names. The BUILD half's structural guard rule (§5 rule 3)
>    found three more that a name grep cannot see:
>    `company/market/transfer_objection_register.py::_add_wd` and
>    `company/regulatory/annual_compliance_attestation_register.py::_add_wd` — the same
>    arithmetic under a shortened name, i.e. the exact rename fail-open §5 predicted, present
>    in the live tree rather than hypothetical — plus
>    `company/trading/bsc_credit_register.py::is_cdn_overdue`, the inline-loop case §1 row 6
>    correctly predicted but attributed to a helper name that does not exist. **This is the
>    evidence that rule 3 earns its place**: a name-only guard would have shipped green over
>    three live second definitions.
> 2. **§4's `working_days_between` interval is WRONG.** §4 specifies half-open `[start, end)`.
>    The four shipped implementations increment BEFORE testing, so the real interval is
>    `(start, end]` — days *after* `start`, up to and *including* `end`. The two readings agree
>    whenever both endpoints are working days, which is why the slip survived review; they
>    diverge exactly when an endpoint is a weekend or holiday (Fri→Sat is 0 shipped, 1 under
>    this doc). Building to the doc literally would have silently moved every deadline the
>    primitive is meant to leave unchanged. **Shipped semantics is canonical**, and is now
>    pinned by `test_interval_is_start_exclusive_end_inclusive`.
>
> Also closed: §3's TO-BE-SOURCED 2016–2018 gap — sourced, not fabricated. See §3.
>
> Pass 2 (migrate the 25 callers, shrink the allowlist to empty) remains OUTSTANDING.

**Status:** DISCOVER/design only. The BUILD half is `blocked_on: director_build_open` per
`docs/staging/in_progress/PLANNER_MINTED_working_day_calculator_2026-07-28.md`. This document
does NOT create the module, migrate a caller, or change any code — it is the handoff artefact
the blocked BUILD half draws from.

**Source atom:** `PLANNER_MINTED_working_day_calculator_2026-07-28.md`, itself minted from
`DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §2.1 + Acceptance item 1,
extending the class of the already-fixed `simulation/bacs_rails.py` "calendar-not-working-days"
instance defect (R10: class fix, not a second instance).

---
## 1. Census — modules that compute working-day arithmetic independently

Grepped `company/`, `sim/`, `simulation/`, `saas/` for `working[_ ]day`, `bank[_ ]holiday`,
`bacs` (excluding `tests/`). **22 modules** define their own working-day arithmetic (a named
helper, or an inline weekend-skipping loop) — every one of them Mon–Fri-only, none
bank-holiday-aware. This is higher than the mint spec's "~17" estimate (which appears to have
undercounted the inline-loop cases below); 22 is the actual current count, confirmed by the
`def _add_working_days|def _working_days_between|def working_days_open|def working_days_to_pay`
grep plus a manual check of the two files that use an inline loop with no named helper.

| # | File:line | Arithmetic |
|---|---|---|
| 1 | `company/crm/change_of_tenancy_register.py:22` | `_add_working_days` — MPAS notify / COT read deadlines |
| 2 | `company/crm/service_log.py:91` | `_add_working_days` — 2-WD acknowledgement deadline |
| 3 | `company/crm/service_ticket.py:53` | `_add_working_days` — SLC 18.7 3-WD complaint ack |
| 4 | `company/crm/onboarding_journey.py:50` | `_add_working_days` — 20-WD objection window, 15-WD welcome pack (SLC 14.2) |
| 5 | `company/trading/emir_reporting_register.py:49` | `_add_working_days` — T+1 WD EMIR trade-repository deadline |
| 6 | `company/trading/bsc_credit_register.py:113-121` | inline `while days_added < N: ... if weekday()<5` — 5-WD cure-period deadline (no named helper) |
| 7 | `company/billing/credit_refund.py:28,48` | `_working_days_between` + `working_days_to_pay()` — SLC 14 10-WD refund deadline |
| 8 | `company/market/dcc_meter_registration.py:37` | `_add_working_days` — 10-WD DCC registration, 5-WD retry |
| 9 | `company/billing/energy_theft_book.py:31` | `_working_days_between` — GS(SS)5 2-WD DNO notification |
| 10 | `company/market/erroneous_transfer.py:40` | inline `working_days_open()` method — 20-WD overdue threshold |
| 11 | `company/regulatory/gsop_tracker.py:49` | inline `working_days_open` property — GSOP breach ageing |
| 12 | `simulation/bacs_rails.py:115` | `_add_working_days` — Bacs 3-WD processing cycle, 2-WD ARUDD lag, 2-WD AUDDIS confirm (already HARDEN-fixed for weekends 2026-07-27; bank holidays explicitly registered-simplification'd, see §2) |
| 13 | `simulation/credit_refund_events.py:69` | `_add_working_days` — on-time/late refund event generation |
| 14 | `company/market/meter_technical_investigation_register.py:16` | `_add_working_days` — SLC 21A 20-WD outcome deadline |
| 15 | `company/billing/dd_indemnity.py:29` | `_working_days_between` — 10-WD BACS DD Guarantee investigation deadline |
| 16 | `company/market/css_performance_register.py:38` | `_add_working_days` — 5WD switching guarantee |
| 17 | `company/billing/deemed_contract.py:28` | `_working_days_between` — SLC 2B 5-WD notification deadline |
| 18 | `company/market/mpas_standing_data_correction_register.py:20` | `_add_working_days` — 2-WD ack, 10-WD resolution |
| 19 | `company/market/bsc_performance_assurance_register.py:23` | `_add_working_days` — 20-WD assessment deadline |
| 20 | `company/market/bsc_settlement_dispute_register.py:26` | `_add_working_days` — 20-WD SQ raise, 40-WD SAA investigation |
| 21 | `company/market/mop_appointment_register.py:27` | `_add_working_days` — D0147 5-WD change notice |
| 22 | `company/regulatory/gsop.py:36` | `_add_working_days` — GSOP payment-due deadlines by type |

Every one of the 22 is `weekday() < 5` (or timedelta-loop equivalent) — pure Mon–Fri, zero
bank-holiday awareness. Signatures are inconsistent across the set (`date`↔`date`,
`date`↔`int`, some accept `datetime`, `emir_reporting_register.py` works in `datetime` not
`date`) — the canonical API (§4) must accommodate both `date` and `datetime` callers without
forcing every caller through a type coercion at the call site.

Not counted as "own arithmetic" (mention `bacs`/working days in prose or use the *result* of
another module's calculation, not define new arithmetic): `company/billing/switching.py`,
`company/billing/dd_mandate_register.py`, `company/billing/direct_debit.py`,
`company/billing/payment_ledger.py`, `company/billing/payment_method_register.py`,
`company/trading/trade_blotter.py`, `company/trading/shape_risk_book.py`,
`company/trading/imbalance_cashflow.py`, `company/regulatory/remit_book.py`,
`company/regulatory/remit_surveillance_register.py`,
`company/regulatory/licence_renewal_tracker.py`,
`company/billing/revenue_protection_register.py`, `company/compliance/obligations_register.py`,
`company/regulatory/compliance.py`, `company/regulatory/slc_compliance_tracker.py`,
`company/billing/billing_dispute.py`, `company/market/tpi_conduct_register.py`,
`company/compliance/consumer_duty_board_report.py`, `company/regulatory/licence_monitor.py`,
`simulation/acquisition_funnel.py`, `simulation/payment_behaviour_source.py`,
`simulation/arrears_engine.py`, `simulation/payment_seam_adapter.py`,
`simulation/dd_collection_book.py`, `company/billing/payment_observation_consumer.py`,
`simulation/run_phase2b.py`, `saas/opex_ledger.py`.

---
## 2. The 3 modules that already mention bank holidays

- **`simulation/bacs_rails.py`** (lines 63-71, `_add_working_days` docstring lines 115-123):
  fixed the calendar-vs-working-days bug 2026-07-27 (the original class instance defect this
  mint extends), and carries an honest **REGISTERED SIMPLIFICATION** comment: bank holidays are
  deliberately NOT skipped because "no UK bank-holiday calendar exists anywhere in this
  codebase to anchor to, and inventing one would be false precision (R13)." It quantifies the
  residual gap (~104 weekend days/yr vs ~8 bank holidays) and scopes the exposure to the
  business-surface DD-rails display only, never a cash-timing figure. **This module is the
  primary named beneficiary once a real calendar exists** — landing the calculator lets this
  comment be deleted rather than kept as permanent debt.
- **`sim/profile_class_1.py`** (lines 40-74) and **`sim/profile_class_3.py`** (lines 40-74,
  near-identical): compute `august_bank_holiday = last_monday_of_month(year, 8)` to derive BSC
  load-profile season boundaries (summer/high-summer/autumn cutoffs), per Elexon's "Load
  Profiles" guidance note. This is a **different concern** from deadline arithmetic — it needs
  only the single fact "August Bank Holiday = last Monday of August," which is an
  algorithmically fixed rule with **no substitution-day exception** (unlike Christmas/New
  Year/Good Friday, which shift when they fall on a weekend). It does not need calendar-table
  lookup and is **out of scope for caller migration** — noted here for completeness per the
  mint spec's explicit ask, not because it is a working-day-calculator caller.

---
## 3. Calendar source

**Recommendation: commit a static JSON snapshot sourced from the two authoritative GDS
(Government Digital Service) channels, refreshed on a documented cadence — not a third-party
library.**

### Evaluated options
1. **Live `https://www.gov.uk/bank-holidays.json` fetch at runtime.** REJECTED as the sole
   source: violates C-S4 (persistence/data behind an interface, swappable but not
   network-dependent at simulation-run time) and the project's "no network in autonomous runs"
   constraint (`feedback_no_network_in_autonomous_runs.md`) — a sim run cannot depend on a live
   HTTP call succeeding. Verified live 2026-07-28 (WebFetch): this is the real, current,
   official GOV.UK feed. Structure: three top-level division keys
   (`england-and-wales`, `scotland`, `northern-ireland`), each an `events` array of
   `{title, date (YYYY-MM-DD), notes, bunting}`. **Coverage is a rolling window only** —
   confirmed live as 2019–2028 (56 events for england-and-wales) as of today; GOV.UK does not
   publish arbitrarily far back.
2. **`alphagov/calendars`** (github.com/alphagov/calendars) — the actual GDS source repository
   that *serves* the `/bank-holidays.json` endpoint. **RECOMMENDED as the sourcing mechanism**:
   pull the current live JSON from the endpoint above for the in-window years, and pull
   **historical committed JSON snapshots from this repo's own git history** for any year GDS
   has since dropped from the live rolling window — because those are the same authoritative
   government-published values, just not currently being served, not a third-party
   reconstruction. This satisfies "never fabricated" for both current and past years without
   pulling in a runtime dependency.
3. **Third-party Python packages** (`ministryofjustice/govuk-bank-holidays`, `workalendar`,
   `holidays`). Considered, not recommended as primary: adds a dependency for something that
   reduces to "read a JSON file GDS already publishes"; the MoJ package itself only wraps the
   same `gov.uk/bank-holidays.json` feed, so it doesn't solve the pre-2019 coverage gap either.
   Could serve as a **cross-check** oracle when populating the pre-2019 table (compare its
   values against `alphagov/calendars` git history before committing), but is not the source
   of record.
4. **Hand-typed table from memory/general knowledge.** REJECTED outright — this is exactly the
   fabrication R13/the mint spec forbid. Every date in the committed table must trace to a
   fetched or archived GDS artefact, cited by URL/commit in the module docstring.

### What I verified live today (2026-07-28, WebFetch against `https://www.gov.uk/bank-holidays.json`)
England & Wales, 2025 and 2026 (**real, GDS-published, fetched live — safe to seed now**):

| Date | Title | Notes |
|---|---|---|
| 2025-01-01 | New Year's Day | |
| 2025-04-18 | Good Friday | |
| 2025-04-21 | Easter Monday | |
| 2025-05-05 | Early May bank holiday | |
| 2025-05-26 | Spring bank holiday | |
| 2025-08-25 | Summer bank holiday | |
| 2025-12-25 | Christmas Day | |
| 2025-12-26 | Boxing Day | |
| 2026-01-01 | New Year's Day | |
| 2026-04-03 | Good Friday | |
| 2026-04-06 | Easter Monday | |
| 2026-05-04 | Early May bank holiday | |
| 2026-05-25 | Spring bank holiday | |
| 2026-08-31 | Summer bank holiday | |
| 2026-12-25 | Christmas Day | |
| 2026-12-28 | Boxing Day | substitute day (2026-12-26 is a Saturday) |

Live feed's full current window (also fetchable, not individually reproduced here): E&W
2019–2028, 56 events total.

### RESOLVED 2026-08-03 (BUILD Pass 1) — sourced, not fabricated
The gap below is CLOSED. Source of record for the committed table is
**`ministryofjustice/govuk-bank-holidays`, `govuk_bank_holidays/bank-holidays.json`** (@ `main`,
fetched 2026-08-03) — chosen over the live gov.uk feed for two reasons: it covers **2012–2028**,
including every year GDS has dropped from its rolling window, and `githubusercontent.com` is on
this project's **egress allowlist** (`background/egress_allowlist.py`) whereas `gov.uk` is not.

**Three-way reconciliation run before any date was committed — all three agree EXACTLY on every
overlapping year:**

| comparison | years | result |
|---|---|---|
| `alphagov/calendars` (`lib/data/bank-holidays.json`, @ `master`) vs source of record | 2015–2021 | 56 events each, **identical set** |
| live `gov.uk/bank-holidays.json` vs source of record | 2019–2028 | 83 events each, **identical set** |
| `alphagov/calendars` vs live feed | 2019–2021 | 24 events each, **identical set** |

`alphagov/calendars` is archived and stores dates as `DD/MM/YYYY` under
`divisions.england-and-wales.<year>`; normalised to ISO before comparison. Note the live feed has
grown since this DISCOVER pass (83 E&W events for 2019–2028, not the 56 recorded in §3 above).

### TO-BE-SOURCED (do not fabricate) — original text, now superseded by the block above
The sim runs against real 2016–2025 Elexon settlement history (per `CLAUDE.md`), so the
committed table needs **2016–2018 E&W bank holidays**, which fall outside the live feed's
current rolling window. I did not fetch these — they must be sourced from
`alphagov/calendars`' git history (or cross-checked against a second GDS-derived source, e.g.
the MoJ package's bundled historical data, itself traceable to GDS) **before** being committed,
each with its source citation in the same docstring pattern `simulation/bacs_rails.py` already
uses for its WebSearch-verified Bacs facts. **Do not let the BUILD half fill this gap from
memory** — this is the one concrete blocking sub-item for that half to resolve before the table
can be marked complete; 2019–2026 above is safe to seed immediately, 2016–2018 is marked
TO-BE-SOURCED.

Northern Ireland and Scotland dates are visible in the same feed (extra NI/Scotland-only
holidays e.g. St Patrick's Day, Battle of the Boyne, St Andrew's Day) but out of scope per §4's
four-nations materiality judgement.

---
## 4. Canonical API design

**One module:** `company/compliance/working_days.py` (lives under `company/compliance/` —
alongside `domain_invariants.py` and `obligations_register.py`, the existing home for
regulation-derived primitives; every caller across `company/`, `simulation/`, `sim/` imports
from here rather than each domain owning its own copy — matches the existing seam precedent of
`company/interfaces/internal_seams.py` as a single cross-domain source of truth).

```python
def is_working_day(d: date, *, nation: Nation = Nation.ENGLAND_AND_WALES) -> bool:
    """True iff d is Mon-Fri AND not a bank holiday for `nation`."""

def add_working_days(start: date, n: int, *, nation: Nation = Nation.ENGLAND_AND_WALES) -> date:
    """Advance n working days from start. n=0 returns start unchanged (matches
    existing _add_working_days(...,0) contracts already relied on by callers).
    n<0 raises (no existing caller subtracts working days; adding it silently
    would be undiscovered scope, not a real need)."""

def working_days_between(start: date, end: date, *, nation: Nation = Nation.ENGLAND_AND_WALES) -> int:
    """Count working days in [start, end). Matches existing _working_days_between
    semantics (half-open, so a same-day call returns 0)."""
```

Design decisions:
- **Accepts `date`, not `datetime`.** `company/trading/emir_reporting_register.py` currently
  works in `datetime` (T+1 working day off an execution timestamp) — that caller migrates via
  `.date()` at the call site, since the *deadline itself* is date-grained (a working day has no
  meaningful sub-day resolution) and mixing time-of-day into the arithmetic is exactly the kind
  of scope creep this mint should avoid introducing.
- **Timezone:** none — operates on naive `date` objects, consistent with every existing caller
  (all 22 already use naive `date`/`datetime.date()`). No caller currently needs Europe/London
  DST-awareness for this arithmetic (that concern lives in `sim/profile_class_1.py`'s own
  clock-change logic, a separate module, untouched).
- **Four-nations split — materiality judgement (recorded per the mint's own instruction):**
  build **England & Wales only** now, with `nation` as a required-by-signature-but-currently-
  single-valued enum (`Nation.ENGLAND_AND_WALES`) rather than a bare function with no nation
  concept at all. Rationale: (a) every one of the 22 callers is a GB-wide regulatory deadline
  (Ofgem SLC, BSC, EMIR) or a company-wide operational one (Bacs, CRM) — none is currently
  segmented by customer nation; (b) the company's own customer base/geography split is not
  modelled elsewhere in the codebase yet (no `nation` field found on any customer/account
  record during this DISCOVER pass); (c) England-and-Wales is the strict superset baseline (the
  gov.uk feed's own default division) and Scotland/NI diverge by *adding* extra holidays, so
  starting E&W-only under-skips rather than over-skips days — the safer default error direction
  for a deadline calculator (a deadline computed 1 day early from an unmodelled Scotland-only
  holiday is conservative, not a breach). Widening to per-nation is a forward-compatible
  addition (new enum member + new calendar array), not a rework — satisfies the portability
  constraint (typed-by-function boundary, no hardcoded "GB-only" assumption baked into the
  function signature itself).

---
## 5. Second-definition guard design

**Model:** `tools/internal_seam_verifier.py` / `tests/tools/test_internal_seam_verifier.py` —
the existing AST-based guard in this repo for "no code outside the approved seam may do X." Same
shape applies here.

**Mechanism (`tools/working_day_guard.py`, new file, BUILD half's to write):**
1. `ast.walk` every `.py` file under `company/`, `sim/`, `simulation/`, `saas/` (excluding
   `company/compliance/working_days.py` itself and its tests).
2. Flag any `FunctionDef`/`AsyncFunctionDef` whose name matches
   `_add_working_days|_working_days_between|working_days_open|working_days_to_pay|
   add_working_days|working_days_between|is_working_day` (the exact names found in the census,
   plus the canonical names themselves, so a copy-paste-rename can't dodge it).
3. Flag any inline weekend-skip loop pattern too (the `bsc_credit_register.py` /
   `erroneous_transfer.py` / `gsop_tracker.py` shape: a `while`/`for` loop containing both a
   `timedelta(days=1)` increment and a `.weekday()` comparison in the same function body) — a
   name-only check would miss these three, which is exactly the R15 FAIL-OPEN pattern this
   guard must not repeat (a renamed or unnamed reimplementation must still be caught).
4. Exit 0 = no second definition found; exit 1 with file:line list = FAIL.
5. Wire into the phase-close / pre-commit gate path alongside `internal_seam_verifier.py`.

**R15 both-ways plan (mandatory per exit criteria):**
- **Mutation test A (fires):** `tests/tools/test_working_day_guard.py` plants a fresh file (or
  temp fixture, matching `test_internal_seam_verifier.py`'s own pattern) defining a new
  `_add_working_days`-shaped function OR a bare weekend-skip loop, asserts the guard's exit code
  is 1 and the violation is reported at the right file:line.
- **Mutation test B (clears):** remove the planted definition, assert exit code 0.
- **Not a tautology:** the guard's pattern list is derived from the independent census in §1
  (grep-confirmed against the live tree), not from the calculator module's own exports — an
  attacker (or a future careless PR) reimplementing under a *new* name still trips rule 3
  (structural loop-shape check), not just rule 2 (name check) alone.
- **Not fail-silent:** guard runs as its own gate step with a distinct exit code, not folded
  silently into a broader "tests pass" umbrella where its own crash/absence would be invisible
  (matches the `internal_seam_verifier.py` precedent of a standalone `python3 -m` entry point).

---
## 6. Two-pass BUILD shape (handoff to the blocked half)

Per the mint's own §2 mandatory shape:

**Pass 1 — land in isolation, call sites unchanged:**
- Create `company/compliance/working_days.py` (API in §4) + the E&W bank-holiday table (2019–
  2026 seeded from the live-verified dates in §3; 2016–2018 sourced from `alphagov/calendars`
  git history before commit, not fabricated; each entry cites its source in the module
  docstring, matching `simulation/bacs_rails.py`'s own citation style).
- Create `tools/working_day_guard.py` + `tests/tools/test_working_day_guard.py` (§5), R15
  both-ways proven, **but scoped to flag only NEW second definitions** — i.e. land the guard
  with the 22 existing definitions still in place, either via a documented baseline allowlist
  (same pattern as `internal_seams.py::BASELINE_ALLOWLIST`) or by not yet enabling it in the
  blocking gate until Pass 2 completes migration. Verify the module in isolation: unit tests for
  `add_working_days`/`is_working_day`/`working_days_between` against the seeded calendar,
  including a case that spans a real bank holiday (e.g. a Friday-before-Christmas start date)
  and asserts the result differs from the old weekend-only callers' output — this IS the
  "moved-figure diff" the exit criteria requires to be published explicitly with its `//` basis
  clock, not left as silent drift.

**Pass 2 — migrate the 22 callers, separately verified:**
- One caller (or a small disjoint batch) at a time; each migration deletes that module's local
  `_add_working_days`/`_working_days_between`/inline-loop and replaces call sites with the
  canonical import.
- After each migration, run that module's own test suite plus the full fast suite (per
  `feedback_control_false_positive_jams_pipeline.md` — a legitimate-edge-case regression here
  would silently jam the compliance pipeline).
- Once all 22 are migrated, flip the guard from baseline-allowlisted to fully enforcing (remove
  the allowlist entries one by one as each caller lands — mirrors how `internal_seams.py`'s own
  allowlist is meant to shrink, not grow).
- Any published financial/compliance figure that moves because a deadline now correctly skips a
  bank holiday gets an explicit before/after with its clock, per the mint's exit criteria — this
  is EXPECTED baseline movement (R13: correcting the company/SIM's own date arithmetic to
  reality, not tuning a world parameter), not a regression to chase down.
- `sim/profile_class_1.py` / `sim/profile_class_3.py` are explicitly **not** migrated (§2) — their
  August-Bank-Holiday rule stays as is; noting this so Pass 2 doesn't treat their absence from
  the migrated-caller list as an oversight.

**Target level:** `level_current 0 → 3` on the migrated result, `blocked_on: director_level_up`
per R16 — the BUILD half cannot self-promote either.
