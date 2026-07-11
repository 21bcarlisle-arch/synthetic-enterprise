# M2 entry-gate payments audit: Direct Debit / PPM / rails cluster

**Persona:** a payments-operations veteran who has run DD mandate lifecycle,
Bacs 3-day cycle timing, AUDDIS/ARUDD/ADDACS messaging, and prepayment-meter
operations at a real UK domestic energy supplier. Scope: 16 modules named in
the M2 entry gate (`docs/design/maturity_map.yaml`'s `D_payments_maturity_audit`
atom), covering DD mandates, PPM, payment plans/refunds, exit fees and CoT.

## Findings table

| Module | What it actually does | Classification | Maturity verdict |
|---|---|---|---|
| `direct_debit.py` | In-memory DD mandate + attempt store; auto-suspends after 2 failed attempts; also a separate SQLite-backed helper set used by the portal | BOTH | Mandate/attempt state transitions are instant — no Bacs 3-day submission→processing→settlement cycle, no AUDDIS-style setup, no real ARUDD reason codes (just a free-text `failure_reason` string). |
| `dd_mandate_register.py` | A second, separate mandate lifecycle register (ACTIVE/SUSPENDED/FAILED/CANCELLED/REINSTATED) with excellent regulatory docstring knowledge | BOTH | Docstring correctly states real DDG facts (10 working days advance notice, 3-day bank return, 1 re-presentation within 8 days, auto-cancel after 2 failures) — **but none of this timing is modeled in code**; `record_failure` applies instantly. Also: **duplicates `direct_debit.py`** — two parallel, non-integrated mandate stores for the same concept. |
| `dd_review.py` | Annual DD amount review against actual spend (Ofgem SLC 27B, ±5% variance threshold) | COMPANY-LOGIC | Mature, correct regulatory basis, no rails dimension needed. |
| `dd_indemnity.py` | BACS DD Guarantee indemnity claim lifecycle (received→investigating→upheld/rejected/written-off), real 10-working-day investigation deadline | BOTH | Correct DDG mechanics and real working-day deadline math — but assumes the underlying DD payment it's contesting was itself instant (no submission-cycle context to anchor "payment_date" against). |
| `payment_ledger.py` | Generic payment record store (method × outcome), portfolio/method breakdowns | BOTH | Docstring correctly names ARUDD code R01 (insufficient funds) but the actual `PaymentOutcome` enum has only 4 generic states and no reason-code field at all — real reason codes exist only in prose, never as data. |
| `payments.py` | Payment-to-invoice reconciliation; 90-day bad-debt aging buckets | COMPANY-LOGIC | Reconciliation and aging policy are mature and standard; treats a payment event as already-settled the instant it's reconciled — no "cash lands when the rails say" concept at all. |
| `payment_method_register.py` | Per-account payment-method history (DD/PPM/BACS/cheque/cash), debt-mandated PPM tracking | COMPANY-LOGIC | Mature; correctly cites SLC 27 and the 2023 forced-PPM scandal. No rails dimension applicable. |
| `payment_plan.py` | Structured arrears repayment plans (Ofgem SLC 27A), default after 2 missed instalments | COMPANY-LOGIC | Mature, correct regulatory basis. |
| `payment_plan_adequacy.py` | Ability-to-Pay compliance scoring (affordable/borderline/unaffordable vs disposable income) | COMPANY-LOGIC | Mature; correctly cites Ofgem ATP guidance and the 2023 Citizens Advice affordability survey. |
| `credit_refund.py` | SLC 14 credit-balance refund tracking, 10-working-day deadline | COMPANY-LOGIC | Correct real regulatory facts (SLC 14, SLC 22A, 2022 crisis enforcement) — but the outbound refund payment itself is instant on "pay()"; no rails timing for money leaving the supplier either. |
| `prepayment.py` | PPM top-up crediting, debt-recovery withholding, emergency credit, friendly-hours self-disconnection rule | RAILS-PHYSICS | Mature and *correctly* near-instant — real smart/legacy PPM top-ups genuinely settle at the meter in seconds, so instant crediting here is realism, not a simplification. Real 2022 crisis self-disconnection framing. |
| `ppm_debt_loading.py` | Ofgem PPM Rules 2019 debt-loading compliance (£250 cap, 5% recovery-rate cap, smart-meter consent) | COMPANY-LOGIC | Mature, correctly cites the 2023 British Gas PPM scandal and Ofgem's response. |
| `ppm_emergency_credit_register.py` | Dedicated emergency/friendly/extra-credit register with 28-day welfare-check trigger | COMPANY-LOGIC | Mature, correct SLC 27A/26B/Consumer Vulnerability Duty basis — but **duplicates `prepayment.py`'s own emergency-credit fields** on `PPMAccount`, same fragmentation pattern as the DD pair above. |
| `ppm_warrant_register.py` | Pre/post-ban PPM warrant application tracking, vulnerability-check gating | COMPANY-LOGIC | Excellent, specific regulatory accuracy (real Feb/April 2023 British Gas scandal dates). Minor point-in-time inconsistency: `VulnerabilityCheck.is_expired` uses wall-clock `dt.date.today()` while the sibling `is_expired_as_of(as_of)` is correctly point-in-time-safe — the same class exposes both an unsafe and a safe path for the same check. |
| `exit_fee.py` | Fixed-term exit-fee calculation with 42-day notice-period waiver | COMPANY-LOGIC | Mature, correct Ofgem licence basis. |
| `cot.py` | Change-of-tenancy / void-property deemed billing, 28-day nomination trigger | COMPANY-LOGIC | Mature, fully point-in-time-safe (every method takes an explicit `as_of`) — a good reference example for the rest of the cluster. |

## Simplifications register

- **No Bacs 3-day cycle anywhere.** Every DD "attempt", "collection", or
  "failure" in `direct_debit.py`/`dd_mandate_register.py` happens
  synchronously the instant the caller invokes it. Real Bacs runs on a fixed
  3-working-day cycle (input day → processing day → entry/settlement day);
  nothing in this cluster represents that gap.
- **No AUDDIS-style mandate setup.** Mandate creation is a single in-process
  call (`create_mandate`/`setup_mandate`); no paperless-setup message,
  no setup confirmation delay.
- **No ARUDD-style failure reason codes as data.** Real codes (0 = no
  instruction, 1 = no account, 3 = no mandate, 5 = account transferred,
  K = mandate cancelled, Q = presentation after cancellation, etc.) are
  named correctly in *docstrings/comments* (`payment_ledger.py`'s R01
  citation) but never modeled as an actual enum/field a caller can branch
  on — every module collapses failure into one generic string or status.
- **No ADDACS-style amendment protocol.** Mandate amount/date changes are
  direct field mutations (`update_amount`), not a message exchange.
- **Outbound payment timing is also absent**, not just inbound DD: refund
  payments (`credit_refund.py`) and debt-plan collections both transition
  state instantly with no "money actually arrives N days later" concept.
- **Two duplicated mandate registers**, not one: `direct_debit.py`'s
  `DirectDebitBook` and `dd_mandate_register.py`'s `DDMandateRegister` model
  the same real-world concept (DD mandate lifecycle) with different data
  shapes and no cross-reference. Same pattern between `prepayment.py`'s
  inline emergency-credit fields and the dedicated
  `ppm_emergency_credit_register.py`.
- **One minor point-in-time inconsistency**: `ppm_warrant_register.py`'s
  `VulnerabilityCheck.is_expired` reads wall-clock `date.today()` instead of
  taking an explicit `as_of`, unlike its own sibling method and unlike every
  other module in this cluster (`cot.py` is the clean reference pattern).
- **Regulatory/policy layer (SLC 14/22A/26B/27/27A/27B/28, PPM Rules 2019,
  DDG mechanics, real 2022/2023 crisis events) is consistently well-cited
  and numerically accurate throughout** — this is not a simplification, it's
  the cluster's real strength, and the finding worth stating plainly: the
  gap is entirely on the *rails* side, not the *policy* side.

## Verdict on M2 shape

**HARDEN-EXISTING for the company-logic layer, clean NEW BUILD for rails —
not a rebuild of anything.** 13 of 16 modules are pure COMPANY-LOGIC and are
already mature, correctly regulation-anchored, and fit for purpose; nothing
here needs rewriting. The 3 BOTH-classified modules
(`direct_debit.py`/`dd_mandate_register.py`/`dd_indemnity.py`) and
`payment_ledger.py` need the rails-physics half added, not their existing
company-logic half rebuilt — this is exactly what
`W5_1_banking_payment_rails` (already registered, `docs/design/
maturity_map.yaml`) is scoped to supply: a real Bacs-cycle-shaped adapter
that these modules attach to, rather than a rewrite of the modules
themselves. The one piece of real pre-work before that wiring lands: resolve
the two duplicated-register pairs (DD mandate, PPM emergency credit) onto a
single canonical store per concept, so the new rails-timing data has one
clear home to attach to, not two divergent ones.
