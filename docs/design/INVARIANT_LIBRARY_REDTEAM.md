# Invariant / Obligations Library — DISCOVER red-team

**Date:** 2026-07-13
**Lane:** DISCOVER (Lane-3), doc-only. No code, `background/`, `site/`, or `maturity_map.yaml` touched.
**Scope:** the company's absurdity-catching machinery —
`company/compliance/domain_invariants.py`, `obligations_register.py`, `internal_audit.py`,
`population_sanity.py`, `sanity_adjudication.py`, and the preventive gate
`company/billing/pre_bill_validation.py` — plus how each is (or isn't) wired into the real
pipeline (`saas/bill_generator.py`, `simulation/run_phase4c_on_phase2b.py`,
`tools/generate_billing_ledger.py`).
**Method:** read every module in full, then constructed concrete adversarial bills and called the
real `validate_bill()` / `check_*()` functions from a live REPL against this repo's code (no
mocking). Every finding is **CONFIRMED** (executed against real code) or **SUSPECTED** (reasoned,
not executed), per R9. Read-only — no repo file modified as part of the exercise.

**Relation to the prior red-team** (`docs/observability/invariant_redteam_2026-07-12.md`): that
pass found 8 findings against the same two files. Its Findings **3 (write-off magnitude) and 4
(malformed `catchup_direction` fail-open) are now CLOSED** — I re-ran both adversarial bills
against the current `check_back_billing_cap_respected()` and both correctly return `False`/HELD
(the R3/R4 self-correction at `domain_invariants.py:459-518` landed). Its Findings **1, 2, 5, 6,
7, 8 remain open** (re-verified 1/2/5 below). This pass extends the surface beyond those two files
(register coverage, the internal-audit backstop, the pipeline-level VAT tautology, structural
bill-integrity) and does **not** re-litigate the closed ones.

---

## CONFIRMED gaps

### C1 — The flagship "VAT-by-segment" Tier-1 check is a production tautology; it can never fire (most serious)

`vat_by_segment` is one of only two Tier-1 obligations the pre-bill gate claims to enforce
(`obligations_register.py:226`, `pre_bill_validation.py:8-11`). It has **zero detective power
against the only bill source in the pipeline.**

- The bill generator computes VAT *from* the segment: `vat_gbp = subtotal_gbp * vat_rate(segment)`
  (`saas/bill_generator.py:158`; `vat_rate()` = `non_commodity.py:152-154`).
- The gate recovers the rate by dividing straight back:
  `_actual_vat_rate = vat_gbp / subtotal` (`pre_bill_validation.py:60-68`) `== vat_rate(segment)`,
  then checks it against `vat_rate_for_segment(segment)` (`domain_invariants.py:395-406`).
- Both sides are the *same function of the same `segment` field*. Algebraically the check passes
  for **every** bill the generator can emit — it is trivially-true, never-fires false comfort.

The genuine R10 "C6 SME-as-Household" defect is a *mislabel*: the bill's `segment` disagrees with
the customer's true classification. Because VAT is derived from the (wrong) label and the gate
re-derives from the same label, the two always agree — the VAT check structurally **cannot** catch
the very defect class it is named for (prior Finding 5 noted "segment self-declared"; this sharpens
it to a pipeline-level tautology and identifies the flagship control as inert, which the prior pass
filed only as a "minor note" about the redundant second `and` clause).

**Invariant that SHOULD exist (class-level, R10):** VAT correctness must be tested against a signal
*independent of the bill's own segment label* — MPAN/MPRN profile class, tariff/product code, or a
consumption-implied segment band — so a bill whose declared segment disagrees with its independent
classification is HELD. A self-consistency check is not a control.

### C2 — No arithmetic-footing / internal-consistency invariant on the money lines

There is a reads-reconciliation invariant for the *usage* line (`check_reads_reconcile`,
`pre_bill_validation.py:119-137`) but **nothing** checks that the money foots. Verified:

```
resi bill, correct 5% VAT ratio, commodity 60 + non_commodity 15 + standing 9 + vat 4.2,
           total_amount_gbp = 999999.0
validate_bill(...) -> PASS, reasons=[]
```

A bill whose printed total is £999,999 against ~£88 of component lines issues silently. This is
live-exploitable, not hypothetical: `tools/generate_billing_ledger.py:241` re-rounds each component
to 2dp *independently*, so rounded parts need not equal a rounded total even when the generator was
correct.

**Invariant that SHOULD exist:** `total_amount_gbp == commodity + non_commodity + standing + vat`
to the penny at display precision, and `vat_gbp == subtotal * expected_rate(segment)` — the money
analogue of the reads-reconcile check that already exists for the usage line.

### C3 — No non-negativity / domain-sign invariant, and a fail-OPEN on non-positive subtotal

No invariant asserts that monetary fields or consumption are `>= 0` for any segment. Verified:

```
resi bill, standing_charge_gbp = -50, vat_gbp = -10, total = -60   -> PASS, reasons=[]
sme  bill, all-zero subtotal                                        -> PASS, reasons=[]
```

Worse, `_actual_vat_rate()` returns `None` when `subtotal <= 0` (`pre_bill_validation.py:66-67`),
so a zero-or-negative-subtotal bill **skips the VAT check entirely** — a fail-*open* on unverifiable
data, the exact opposite of the fail-*closed* principle the back-billing fix established
(`domain_invariants.py:486-502`).

**Invariant that SHOULD exist:** every monetary field and consumption on any bill is `>= 0` (credits
are separate, positively-signed refund artefacts, never negative bills); a non-positive subtotal
must fail **closed** (HELD), not silently skip the rate check.

### C4 — Temporal-impossibility class is unguarded

`_days_in_period()` clamps a reversed or zero-length period to 1 day with `max((end-start).days+1, 1)`
(`pre_bill_validation.py:53-57`) and raises no flag. Verified:

```
resi, period_start 2024-01-31, period_end 2024-01-01, 40 kWh   -> PASS   (silently treated as 1 day)
sme,  period_start 2024-12-31, period_end 2024-01-01, 500,000 kWh, total £88,888 -> PASS
```

A reversed-date bill is never flagged *as* a date error — it either coincidentally trips the
consumption band (right verdict, wrong reason) or passes outright (any small resi, or any SME —
SME has no consumption check at all, prior Finding 2). Nothing checks `period_start <= period_end`,
plausible period length, future-dating, or overlap with the customer's prior period.

**Invariant that SHOULD exist:** `period_start <= period_end`, `1 <= length <= ~400 days`,
`period_end <= as-of/issue date`, and no overlap with the account's previously-issued period.

### C5 — The invariant gate is bills-only; other customer-facing money surfaces have no gate

`validate_bill` is the only invariant chokepoint, and it runs on bill dicts. Other customer-facing
*monetary* artefacts never pass through it or any `check_*()` predicate: annual statements
(`company/billing/annual_statement.py`), Direct-Debit review reset amounts (`dd_review.py`),
credit-refund amounts (`credit_refund.py`), quotes / tariff comparisons
(`company/pricing/tariff_comparison.py`). R10/R11 name the absurdity class as *any* customer-facing
figure, not only a bill — an absurd DD reset or a mis-totalled annual statement reaches the customer
with no invariant in the path.

**Invariant that SHOULD exist:** a shared invariant gate (footing + sign + plausibility) that every
customer-facing monetary artefact routes through, not a bill-specific one — the seam already implied
by the obligations register's "customer_financial" impact tier spanning more than billing.

### C6 — `internal_audit` (the human-catches-it backstop) is fail-silent and non-load-bearing

`internal_audit.py` is explicitly the "institutionalise the local-Qwen skeptic" backstop for
absurdities *no automated invariant was written for yet* (its docstring, lines 1-22 — the module
that motivates R10's own C6 story). But `call_qwen()` returns `""` on any failure
(`internal_audit.py:35-63`), and `parse_audit_response("")` defaults `verdict = "clean"`
(lines 85-95). So when Ollama is unreachable — **the norm in autonomous/no-network runs**
(MEMORY.md: "No network in autonomous runs") — *every* sampled bill and artefact is silently
"clean," indistinguishable from "audit ran and found nothing." The one mechanism designed to catch
what the invariants miss produces maximal false comfort exactly when it is unavailable, and emits
no coverage signal that it didn't actually run.

**Invariant/mechanism that SHOULD exist:** audit *coverage* (model-reachable? N sampled? ran vs
skipped) is a first-class output; a phase-close/digest must treat "audit could not run" as a
distinct, non-clean state — never fold an unreachable model into a clean verdict.

### C7 — Obligations register: physical-harm coverage hole, unverified trackers, stale rationale, SLC-ref drift

Reading `obligations_register.py:158-299`:

- **(a) The top severity tier is nearly empty.** `ImpactTier.PHYSICAL_HARM` is assigned to exactly
  **one** obligation — PSR (`:212`). Gas safety (`company/billing/gas_safety_incident_register.py`
  exists), PPM self-disconnection and the winter moratorium (`ppm_emergency_credit_register.py`,
  `winter_moratorium.py` exist) are textbook physical-harm domains with live trackers but **no
  register row** — so they can never reach Tier-1 via the register's `derive_risk_tier` path.
- **(b) Whole regimes absent:** complaints handling / Ombudsman referral timescales, data
  protection / GDPR, theft & revenue-protection conduct, disconnection conduct, microbusiness
  back-billing (an explicitly acknowledged gap, `domain_invariants.py:336-341`).
- **(c) `existing_tracker` is unverified free text.** Nothing asserts the named module exists or is
  load-bearing. `slc_31a_back_billing_cap` (`:174-187`) credits
  `simulation/meter_reads.py (MAX_CONSECUTIVE_ESTIMATED_PERIODS)` and rates likelihood **MEDIUM**
  on the claim that mechanism "structurally prevents the cap being exceeded" — but the entire
  `ADVISOR_STEER_BACKBILLING_GATE` programme existed *because* that structural prevention was
  insufficient, and the real control is now the pre-bill gate. The rationale is stale and
  contradicted by its own follow-on work.
- **(d) SLC-reference drift.** The register row is `slc_31a_back_billing_cap`, source
  "Ofgem SLC 31A" (`:175-177`); the enforcing invariant, gate, and comments all say
  "SLC 21BA" (`domain_invariants.py:328,341,446`). Same obligation, two different licence-condition
  citations (real Ofgem domestic back-billing is SLC 21B/21BA; "31A" appears wrong), and the row and
  the invariant that enforces it share no cross-reference key — a domain-fidelity smell and a
  traceability gap.

**Invariant/mechanism that SHOULD exist:** (a) add the physical-harm rows so gas-safety and
self-disconnection can tier correctly; (b) each `existing_tracker` string resolves to a module that
actually exists AND is asserted load-bearing (imported by a run), else it's treated as
`existing_tracker=None` (a real gap) not a silent pass; (c) register rows carry the invariant/gate
key that enforces them, so `31A`-vs-`21BA`-class drift fails a consistency test.

---

## SUSPECTED gaps

### S1 — 19 of ~28 library invariants remain inert (prior Finding 1, re-confirmed by grep)

Standing-charge (all 4), non-commodity-cost (all 4), `NON_COMMODITY_SHARE_OF_BILL`, TDCV bands
(all 6), and both margin invariants are defined in `ALL_INVARIANTS` but never reach any `.check()`
call site (verified: only VAT, monthly resi-consumption, unit-rate, annual-consumption, and
back-billing are consumed anywhere). The gate's docstring claim to check "every bill against the
Tier-1 obligations using the anchored predicates" is materially overstated. Marked SUSPECTED here
only because it is the prior pass's already-open Finding 1, not new — but it is the cheapest
class to close (the RangeInvariants already exist; only a per-bill wiring is missing).

### S2 — Per-bill vs annual coverage seam (prior Finding 6) interacts with C4's date-clamp

The Tier-1 gate uses only the monthly envelope; the annual envelope runs later, population-side,
with a 60-day minimum-coverage carve-out (`population_sanity.py:40-65`). Combined with C4's silent
1-day clamp, a run of corrupt short periods could each pass the monthly band *and* be excluded from
the annual check for insufficient coverage — a compounding blind spot. Not executed end-to-end;
SUSPECTED.

### S3 — `sanity_adjudication` keys are free-form strings with no schema link to a finding source

`adjudicate(finding_key, ...)` (`sanity_adjudication.py:59`) takes an arbitrary string key; nothing
ties a `finding_key` to an actual check id in `population_sanity`/`internal_audit`. A renamed check
or a typo'd key silently orphans a prior "adjudicated-false-positive" verdict, re-opening
alarm-fatigue the ledger exists to prevent. Reasoned from the code shape, not executed; SUSPECTED.

---

## Top 3 to register as atoms

1. **VAT-by-segment control is inert (C1).** The flagship Tier-1 obligation cannot catch its own
   named defect class because it checks the bill against itself. Register an atom to re-base the VAT
   check on a segment signal independent of the bill's own label. Highest severity: a live Tier-1
   control providing false assurance is worse than a known gap.
2. **Structural bill-integrity invariants (C2 + C3 + C4 as one coherent atom).** Footing
   (total == Σ lines, vat == subtotal·rate), non-negativity + fail-closed on non-positive subtotal,
   and temporal sanity (start ≤ end ≤ as-of, plausible length). All three are class-level, all
   currently absent, all trivially exploitable in one REPL session, and all belong to the same
   "a human would catch this instantly" family R10 targets.
3. **Obligations-register coverage & traceability (C7).** Add the physical-harm rows (gas safety,
   self-disconnection) so the highest-impact tier isn't a near-empty set; make `existing_tracker`
   resolve-or-degrade-to-gap rather than be trusted free text; carry the enforcing invariant key on
   each row so SLC-citation drift fails a test. C6 (audit-coverage-as-a-first-class-state) is the
   strong runner-up.
