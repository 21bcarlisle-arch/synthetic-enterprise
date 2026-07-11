# W5 — Banking & Payment Rails: lane charter

**Dial reached 2 2026-07-11** (`docs/design/maturity_map.yaml`, `W5_1_banking_payment_rails`).
This charter is pulled forward of the map's base rule ("a lane earns its charter when its dial
reaches 3+", `docs/design/MATURITY_MAP.md`) under SPIKE_WEEKEND priority item 4, "DISCOVER/FRAME
charter flood for every lane at dial≥2 lacking one" (CLAUDE.md, 2026-07-11) — an intentional
pull-forward of the documentation, not a rule change, and not a claim that the lane's own
`level_target` (3) has been reached. Real build work has already landed this session (level
0→1→2) before this charter existed; this document is catching the framing up to work already
done, not starting the lane from zero.

## Mission

This lane's own `real_world_twin` (`docs/design/maturity_map.yaml`): "Bacs Direct Debit cycle
(AUDDIS/ARUDD/ADDACS), card acquirer settlement." Cash lands when the rails say, not when the
company decides it should — a Direct Debit submitted today doesn't fail (or succeed) instantly;
a real Bacs integration finds out on a fixed, multi-day, protocol-defined schedule, and a
supplier's own banked-cash ledger has to live with that lag as real physics, not a modelling
convenience. Per `docs/design/THE_VALUE_CYCLE_FRAMING.md`'s own framing of this lane: **"rails
ARE late-arriving truth, a limb of the spine, not an adjacent system."** This lane does not decide
*whether* a payment succeeds — that stays with the existing calibrated, stress-tier-anchored
behavioural model (`simulation/arrears_engine.py::payment_outcome()`, R13-protected) — it decides
*when the company finds out*, and with what real-world detail (a reason code, not just
success/fail), exactly as a real supplier's Bacs integration would experience it.

## Shared architecture note — a limb of the spine, not an adjacent system

W5 is the **rails-physics face** of the same three-clocks architecture that D2/W1 build the
market-data and billing-reconciliation faces of (`docs/design/charters/D_billing_metering.md`,
`docs/design/charters/W1_market_weather.md`). THE_VALUE_CYCLE_FRAMING.md's own C2 consequence
names three clocks — billed, settled, **banked** (DD cash, failures, seasonality) — and this
lane's job is to make the banked clock honest. It is registered as a **NEW W-lane component**
(EPOCH2_RATIFIED.md immediate effect 1, three director-ratified amendments to the framing) built
**adapter-shaped** behind an interface mirroring the real protocol: submission windows, a
multi-day cycle, AUDDIS-style mandate setup, ARUDD-style failure returns with reason codes,
ADDACS-style amendments. Full typed/versioned hardening of this seam onto
`company/interfaces/` is explicitly Epoch-3 work (the framing's own instruction: "add it to the
wall's adapter inventory now") — this lane's current build is the physics engine behind that
future seam, not the seam itself.

## Sub-capability tree

- **W5_1 (this atom, `W5_1_banking_payment_rails`)** — the rails-timing physics engine plus its
  wiring into the company-observable DD book. Built in two real, sequenced pieces this session:
  1. `simulation/bacs_rails.py` — a pure, stdlib-only physics/timing module: `submit_mandate_setup`,
     `submit_amendment`, `submit_collection` (return a `BacsSubmission` that is `pending` with no
     early knowledge of outcome, exactly what a real supplier's integration would see), and
     `resolve_submission` / `resolve_due_submissions` (apply an *already-decided* behavioural
     outcome and reveal it with realistic multi-day lag and a real AUDDIS/ARUDD reason code).
     Structurally guarded (by test) to contain no probability constants of its own — it never
     decides success/fail, only timing and the reason code around a decision made elsewhere.
  2. `simulation/dd_collection_book.py` — the wiring adapter. Populates
     `company/billing/direct_debit.py::DirectDebitBook` (found, via grep, to have **zero callers
     anywhere** before this — the same "paper compliance" class the M2 audit named for 18 other
     billing/collections modules) with real, Bacs-timed `DDPaymentAttempt` records, for
     `method == "direct_debit"` bills only (B2B bacs/chaps transfer is out of scope, a different
     real-world rail). Deliberately does not touch `simulation/arrears_engine.py` — the same
     `payment_outcome()` call, same RNG seed, same call sequence as the real ground-truth
     `compute_emergent_bad_debt()`/`compute_debt_recovery()`, so this book's outcomes never
     contradict the numbers already baked into `net_margin_gbp`/`treasury_cash_balance_gbp`; only
     a second, independently-seeded RNG stream drives the rails-timing lag draw on top.
- **Forward roadmap items**, named in THE_VALUE_CYCLE_FRAMING.md's M2 sequencing but not yet
  started by this atom: estimated billing (EAC/profile) → actual-read catch-up rebilling
  (back-billing law) → settlement runs on the real Elexon timetable → **DD cash engine with
  seasonality and failure** (this atom's own target, substantially delivered by the two modules
  above for the collection leg specifically) → ledger accrual/restatement → margin bridge v1.
- **Depends on** `D2_three_clocks` and `D_payments_maturity_audit` — both satisfied, which is why
  this atom's `loop_stage` moved from `idle` to `build`: D_payments_maturity_audit reached its own
  target (verdict published, `docs/design/M2_PAYMENTS_AUDIT_DD_RAILS.md` /
  `M2_PAYMENTS_AUDIT_BILLING_COLLECTIONS.md`, 2026-07-11) with the explicit finding that the
  Bacs rails-physics layer was **entirely absent, not partially modeled** — every DD/mandate
  state transition happened synchronously before this lane's build.
- **Adjacent, not this atom's own scope:** the audit's two flagged duplicated-register pairs
  (`direct_debit.py` vs `dd_mandate_register.py`; `prepayment.py`'s inline emergency-credit
  fields vs `ppm_emergency_credit_register.py`) — consolidation needed before further W5 wiring
  compounds the duplication, registered by the audit, not yet actioned.

## What L2/L3/L4 mean in this lane's terms

- **L0 (pre-this-phase):** the Bacs rails-physics layer was entirely absent — no 3-day cycle, no
  AUDDIS/ARUDD/ADDACS modeling of any kind; every DD/mandate state transition was synchronous.
  `DirectDebitBook` existed in `company/billing/direct_debit.py` but had zero callers anywhere —
  correctly built in isolation, connected to nothing.
- **L1 (2026-07-11, "rails sim first"):** `simulation/bacs_rails.py` built and tested in isolation
  — WebSearch-verified real Bacs mechanics (3-working-day submission→collection cycle, AUDDIS
  confirmation window, ARUDD failure-notification lag up to 2 working days after collection day,
  real reason codes), 21 tests, epistemic PASS, zero company/saas coupling. Proven correct
  standalone, not yet wired to anything live.
- **L2 (CURRENT, this atom's dial):** `simulation/dd_collection_book.py` wires that timing into
  the previously-unwired `DirectDebitBook`, using the identical `payment_outcome()` decision
  sequence as the real ground truth so no existing number changes, layered with realistic Bacs
  timing/reason codes via a separately-seeded RNG (a real desync bug — sharing one RNG stream
  between the outcome decision and the rails lag draw — was caught and fixed before shipping,
  proven by a regression test replaying the exact ground-truth sequence). The banked clock now has
  one real, company-observable artefact behind it for consumer Direct Debit collections
  specifically. 9 further tests, epistemic PASS, the full 74-test `arrears_engine` suite still
  green (confirms zero disturbance to ground truth).
- **L3 (this atom's `level_target`, not yet reached):** mandate SETUP and AMENDMENT flows wired
  the same way collections now are. `submit_mandate_setup`/`submit_amendment` already exist in
  `bacs_rails.py` but are currently unused by `dd_collection_book.py` — mandate creation still
  happens instantly (`book.create_mandate()` fires synchronously, not routed through the AUDDIS
  confirmation window `submit_mandate_setup()` models). Reaching L3 also means resolving the
  audit's duplicated-register finding for `DirectDebitBook`/`dd_mandate_register.py` before this
  lane becomes a second live writer into that state. Card-acquirer settlement — the other half of
  this lane's own `real_world_twin` alongside Bacs — is untouched at any level; this lane so far
  covers only the Direct Debit rail.
- **L4 (not yet targeted, forward):** the full typed/versioned protocol-adapter hardening of this
  seam onto `company/interfaces/`, per THE_VALUE_CYCLE_FRAMING.md's own instruction. Today's
  module is *adapter-shaped* (submit-then-later-resolve, mirroring what a real integration would
  see) but is not yet a formal typed/versioned message contract at the interface seam — that is
  explicitly registered as Epoch-3 work, not attempted early.

## Named best-practice references

- **Pay.UK's "Bacs System Principles" guide** — the real 3-working-day Direct Debit processing
  cycle (submission → processing → collection day), source for `bacs_rails.py`'s
  `BACS_PROCESSING_DAYS`, WebSearch-verified before building, per the module's own docstring.
- **AccessPaySuite / Hafiz Didarali Bacs reason-code references** — the real AUDDIS (mandate
  setup) and ARUDD (collection failure) reason codes, source for `ARUDD_REASON_CODES`/
  `AUDDIS_REASON_CODES` (ARUDD code 0, "Refer to Payer", correctly modelled as the genuine
  real-world dominant insufficient-funds-class failure code, not an invented one).
- **GoCardless Developers API documentation**
  ([developer.gocardless.com/mandates/responding-to-mandate-events](https://developer.gocardless.com/mandates/responding-to-mandate-events/),
  [support.gocardless.com mandate-statuses](https://support.gocardless.com/hc/en-gb/articles/17144912089884-Mandate-statuses)) —
  a real, live payments provider's own public reference implementation of a Direct Debit mandate
  lifecycle as an external API surface: a submitted mandate is only ~95% confirmed at day 5 and
  100% confirmed at day 6, with payment collected around day 4 — corroborates this lane's own
  multi-day, provisional-until-resolved design (`BacsSubmission.status == "pending"` until
  `resolve_*()` runs) as matching how a real payments provider's API genuinely behaves, not an
  invented shape.
- **Card-acquirer settlement timing** — general payments-industry description of T+1/T+2
  merchant-funding cycles negotiated per the acquiring agreement (e.g. Clearly Payments, "How Long
  Do Credit Card Payments Take to Settle?"; PXP's settlement-timing glossary) — the real external
  system this lane's own `real_world_twin` names alongside Bacs, and for which this lane has
  built no timing model yet: a genuinely open scope gap, named here rather than glossed over.
- **Martin Fowler, "Gateway" pattern** (*Patterns of Enterprise Application Architecture*, 2002;
  expanded explanation 2021, [martinfowler.com/eaaCatalog/gateway.html](https://martinfowler.com/eaaCatalog/gateway.html)) —
  "an object that encapsulates access to an external system or resource... use a gateway whenever
  you access some external software and there is any awkwardness in that external element." The
  general software-architecture pattern this lane's adapter-shaped `submit_*()`/`resolve_*()`
  design instantiates specifically for the Bacs/acquirer boundary — replacing the external
  dependency, or hardening it into a typed/versioned contract at L4, becomes straightforward
  precisely because the boundary is already named and encapsulated this way.

## Lane roadmap

1. **DONE this phase (2026-07-11):** rails sim built (`bacs_rails.py`, L0→L1) and wired into the
   live DD collection flow (`dd_collection_book.py`, L1→L2, current dial). 30 new tests across the
   two modules (21 + 9), epistemic PASS, the existing 74-test `arrears_engine` suite unchanged and
   green — confirms zero disturbance to the ground-truth financial figures this lane deliberately
   did not touch.
2. **Next (this atom's own `level_target`, L3):** extend the same wiring pattern to mandate setup
   and amendment (`submit_mandate_setup`/`submit_amendment` exist but are unused by
   `dd_collection_book.py` today); resolve the M2 audit's duplicated-register finding for
   `DirectDebitBook`/`dd_mandate_register.py` before or alongside, since this lane is becoming a
   second live writer into that state.
3. **Later (per THE_VALUE_CYCLE_FRAMING.md's M2 sequencing, not yet started by this lane):**
   estimated billing (EAC/profile) + actual-read catch-up rebilling under back-billing law;
   settlement runs paying/clawing on the real Elexon timetable; ledger accrual/restatement; margin
   bridge v1 attributing the lot. This lane's rails-physics work is a precondition for an honest
   "banked" clock feeding that sequence, not the whole of it.
4. **Not started, no design yet:** card-acquirer settlement timing — the other half of this
   lane's own `real_world_twin`. No atom or module exists for it yet.
5. **Epoch-3 (explicitly deferred, per the framing's own instruction):** full typed/versioned
   protocol-adapter hardening of this seam onto `company/interfaces/`, already logged on the
   wall's adapter inventory rather than built early.

## Simplifications register

(Full text lives in `docs/design/maturity_map.yaml`, `W5_1_banking_payment_rails.simplifications`
— three dated entries, condensed faithfully here, not re-invented.)

- **2026-07-11, registration:** director-ratified as a NEW W-lane via three amendments to
  THE_VALUE_CYCLE_FRAMING.md (the banking-as-swappable-interface worry). Built adapter-SHAPED
  behind an interface mirroring the real protocol; full typed/versioned hardening of the seam
  registered as Epoch-3 work on the wall's adapter inventory, not attempted now. `loop_stage`
  stayed `idle` until both `D_payments_maturity_audit`'s verdict and M1's exit test landed, per
  EPOCH2_RATIFIED.md immediate effect 4 — not started ahead of its dependencies.
- **2026-07-11, "rails sim first" built (L0→L1):** WebSearch-verified real Bacs mechanics before
  building, not assumed (3-working-day cycle, AUDDIS Day-2 confirmation, ARUDD failure lag up to 2
  days after collection day, real reason codes). Deliberately does not duplicate the existing
  calibrated behavioural failure-probability model (`arrears_engine.py::payment_outcome()`,
  R13-compliant) — structurally guarded by a test proving the module contains no probability
  constants of its own. Reason-code selection is deterministic to the documented dominant code,
  not RNG-randomised across the full code set, since no sourced real-world frequency split between
  codes exists and fabricating one would make rare codes (e.g. "Payer Deceased") appear
  unrealistically often. 21 new tests, epistemic PASS (pure stdlib module, zero company/saas
  coupling).
- **2026-07-11, rails timing wired into the live DD flow (L1→L2, director in-console approval):**
  R4 diagnosis before building — grepped for `DirectDebitBook`/`record_attempt`/`DDPaymentAttempt`
  callers and found zero anywhere, the same "paper compliance" class the M2 audit named for 18
  other modules. The genuinely live DD-relevant flow is
  `arrears_engine.py::payment_outcome()`/`compute_emergent_bad_debt()`/`compute_debt_recovery()`,
  which compute real ground-truth figures flowing into `net_margin_gbp`/
  `treasury_cash_balance_gbp` — deliberately NOT touched, since a same-day timing change there
  would shift which calendar year a write-off lands in and silently alter historical financial
  figures (the same caution class M1's own precedent established). Instead built
  `dd_collection_book.py` as a new, additive, company-observable artefact: same unchanged
  `payment_outcome()` decision and RNG sequence as the real ground truth, layered with
  `bacs_rails.py`'s timing/reason codes via a second, independently-seeded RNG. Caught and fixed a
  real bug before shipping: an initial shared-RNG design would have desynced every outcome after
  the first resolved bill from the real ground truth — fixed with a separate rng and a dedicated
  regression test proving an exact-match replay. 9 new tests, epistemic PASS, full 74-test
  `arrears_engine` suite still green.
- **This charter's own limits, registered directly (not yet in the map's own field, added here
  per R10):** mandate setup/amendment are built in `bacs_rails.py` but not yet exercised by
  `dd_collection_book.py` — only the collection leg is wired; card-acquirer settlement has no
  model at all yet despite being named in this lane's own `real_world_twin`; and the two
  duplicated-register pairs the M2 audit flagged remain unconsolidated while this lane adds a
  second live writer into `DirectDebitBook` state.
