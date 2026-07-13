# THE CONTROL KILL LIST

**Spec:** `docs/staging/CONTROLS_THAT_CANNOT_FAIL.md` (director P0, rank HIGHEST).
**Method:** `tests/controls/test_control_mutation.py`. **Registry:** `docs/design/control_registry.json`.
**Produced:** 2026-07-13.

> A control that CANNOT FAIL is worse than no control — it manufactures confidence.
> For every control we injected the exact defect it exists to catch. It must fire.
> A control that does not fire on its own named defect is **THEATRE**.

---

## HEADLINE (the honest CUMULATIVE number, 2 passes)

- **27 controls mutation-tested** cumulatively (Pass 1: 13 highest-tier / customer-impacting;
  Pass 2 / H12 L2→L3: 14 more — the inventoried-but-untested tail).
- **26 FIRED** on their own named defect.
- **1 is THEATRE** — the flagship `vat_by_segment` arithmetic check (`check_vat`), a
  **TAUTOLOGY**. Retained as documented defence-in-depth but structurally
  cannot catch the SME-as-Household mislabel it is named for; the independent
  cross-check that replaces it (`check_vat_consistent_with_consumption`) **fires**.
- **2 FIXED** cumulatively (both Pass 1). **Pass 2 fixed 0** and registered **5 new
  killer-pattern GAPS (KL-4..KL-8)** — every gap found is a semantics change across
  multiple callers, so per SELF_INTERRUPT_DISCIPLINE (QUEUE-by-default) they are
  ranked kill-list entries for the orchestrator, not fixed on sight. Every Pass-2
  control still fires on its *core* named defect, so **Pass-2 theatre count is 0**.
- Plus a **structural-only** check of the LLM-judge evaluators (their read-only
  guarantee is asserted; their verdict *quality* is documented as **not
  deterministically mutation-testable** and NOT counted as covered).

### By killer pattern (cumulative, found across the library)
| Killer pattern | Count | Controls |
|---|---|---|
| **TAUTOLOGY** | 2 | `check_vat` (THEATRE, mitigated); `social_obligation is_compliant` status-trust (KL-6, mitigated by independent `underspend_records`) |
| **FAIL-OPEN** | 3 | pre-bill subtotal≤0 (**FIXED** P1); `green_claims` zero-obligation (KL-7, listed); dashboard `_check_consistency` per-key skip (KL-8, listed) |
| **FAIL-SILENT** | 4 | Qwen backstop unavailable (**FIXED** P1); population estimated-read empty-log (KL-4, listed); `consumer_duty` empty-register=GREEN (KL-5, listed); dashboard `_check_consistency` no-insights (KL-8, listed) |

Plus **documented, sourced limitations** (not killer patterns): the YearlyRange
pre-cap "cannot check" branch, the epistemic verifier's two coverage gaps, and several
scoped not-applicable guards in the population checks — all listed, none counted as theatre.
Two Pass-2 controls PASSED their fail-audit as **fail-CLOSED (good)**: `health_check`
alarms when tmux+ps are both unavailable, and the change-detection gate processes (never
silently skips) when its dedup memory is unreadable.

---

## THE LIST

| # | Control | Named defect | Result | Killer pattern |
|---|---|---|---|---|
| 1 | `RateInvariant.check` (VAT rates) | wrong exact rate | **FIRED** | — |
| 2 | `RangeInvariant.check` (whole library sweep) | value outside plausible band | **FIRED** | — |
| 3 | `YearlyRangeInvariant.check` | unit rate order-of-magnitude off cap | **FIRED** | documented pre-cap fail-open (sourced) |
| 4 | `check_vat` (vat_by_segment arithmetic) | SME-as-Household **mislabel** | **THEATRE** | **TAUTOLOGY** |
| 5 | `check_vat_consistent_with_consumption` | same mislabel, via metered load | **FIRED** | — |
| 6 | `check_resi_bill_consumption_plausible` | SME-scale load on a resi record | **FIRED** | — |
| 7 | `check_back_billing_cap_respected` | SLC 21BA breach not written off | **FIRED** | fail-**closed** (good) |
| 8 | `check_billed_clock_reconciles` | revenue booked for HELD bills | **FIRED** | — |
| 9 | `validate_bill` (Tier-1 pre-bill gate) | mislabel / non-positive-subtotal skip | **FIRED** | **FAIL-OPEN — FIXED** |
| 10 | `check_reads_reconcile` | usage ≠ closing − opening reads | **FIRED** | scoped not-applicable guard |
| 11 | `internal_audit` (Qwen backstop) | absurdity + **checker unavailable** | **FIRED** | **FAIL-SILENT — FIXED** |
| 12 | `derive_risk_tier` / obligations tiering | obligation mis-tiered below Tier 1 | **FIRED** | classifier, not a gate |
| 13 | `epistemic_verifier` scan | company code importing SIM internals | **FIRED** | minor coverage gaps (listed) |

---

## WHAT WE FIXED THIS PASS (the class, not the instance)

### F6 — FAIL-SILENT: the Qwen internal-audit backstop (`company/compliance/internal_audit.py`)
**Before:** `parse_audit_response("")` returned `verdict="clean"`. `call_qwen` returns
`""` on any failure (Ollama down / timeout / unparseable). So on every autonomous run
where Ollama was down, `run_internal_audit` returned `[]` — the audit passed **by not
running**. The check had been passing by NOT RUNNING.

**After:** a third verdict state, `"unavailable"`, distinct from `clean` and `flagged`.
An empty or no-VERDICT-line response is now `unavailable`. `run_internal_audit` /
`run_phase_close_audit` emit a `kind="checker_unavailable"` finding when the model
could not be reached, so a caller (`background/sanity_daemon.py`) sees a **non-empty
findings list and alarms** on the outage instead of logging "0 flagged". It still
fabricates no finding against any specific bill (no false positives). **An unavailable
check is a FAILED check.**

### FAIL-OPEN: the Tier-1 pre-bill gate (`company/billing/pre_bill_validation.py`)
**Before:** `_actual_vat_rate()` returned `None` whenever the subtotal was ≤ 0, which
silently skipped **both** VAT checks. A bill with a zero or negative subtotal sailed
through the Tier-1 gate with no VAT validation at all — "passes when data is
zero/malformed", the fail-open pattern verbatim.

**After:** a negative subtotal, and any VAT charged on a non-positive subtotal, now
fail **CLOSED** (HELD) with a specific reason. A legitimately-empty zero/zero bill still
passes the VAT guard (it is caught elsewhere only if consumption is implausible).

---

## THEATRE WE DID NOT FIX (for the orchestrator to register as atoms)

### KL-1 — `check_vat` is a TAUTOLOGY (documented, mitigated, retained)
`check_vat(segment, rate)` derives the expected rate from `segment` and checks it
against a VAT figure the generator also derives from `segment` — the same function of
the same label on both sides. It passes every bill and **cannot** catch a mislabel.
It is **not deleted** because it still fires on a narrower real defect (a VAT rate
inconsistent with the *declared* label, e.g. a hand-edited `vat_gbp`), and the
independent control (`check_vat_consistent_with_consumption`) already covers the
mislabel. Recorded as THEATRE-for-its-named-defect in the registry with a strict
`xfail` in the harness so it can never be quietly relabelled a real control.
**Atom suggestion:** decide whether to keep `check_vat` as labelled defence-in-depth or
retire it once the independent cross-check is proven sufficient in production.

### KL-2 — `epistemic_verifier` coverage gaps (minor, listed)
(1) `_scan_file` returns `[]` on `FileNotFoundError` — a missing file reads as clean.
(2) Only line-start import syntax is matched — an `importlib`/`getattr` dynamic import
of a SIM internal is not caught. Both are detection-coverage gaps, not a fail-open on
the syntax it owns. **Atom suggestion:** add an AST-level scan and treat a missing
scanned-file path as an error, not a pass.

### KL-3 — `YearlyRangeInvariant` pre-cap branch (documented, sourced)
`check()` returns `True` for any year before the Ofgem cap existed (< 2019). This is a
deliberate, sourced limitation — no valid anchor pre-dates the cap and extrapolating
backwards produced real false positives on genuine competitive-market pricing (Phase 5).
Listed for honesty; **not** counted as theatre.

---

## PASS 2 (H12 L2→L3) — THE INVENTORIED-BUT-UNTESTED TAIL

| # | Control | Named defect | Result | Killer pattern / note |
|---|---|---|---|---|
| 14 | `population_sanity.check_consumption_distribution` | SME-scale annual load across a resi book | **FIRED** | documented <60-day not-applicable guard |
| 15 | `population_sanity.check_unit_rate_bands` | population drifting off the Ofgem cap band | **FIRED** | kwh≤0 scoped skip |
| 16 | `population_sanity.check_estimated_read_rate` | read-generation broken (0%/100%) | **FIRED** | **FAIL-SILENT gap KL-4** (empty log reads clean) |
| 17 | `population_sanity.check_payment_channel_mix` | everyone on one payment method | **FIRED** | total=0 scoped skip |
| 18 | `consumer_duty.overall_rag` | a RED outcome not escalating the register | **FIRED** | **FAIL-SILENT gap KL-5** (empty register = GREEN) |
| 19 | `social_obligation` `non_compliant`/`underspend_records` | underperforming / underspent obligation | **FIRED** | **TAUTOLOGY gap KL-6** (status-trust; mitigated by independent `underspend_records`) |
| 20 | `crisis_bad_debt_validator.validate_crisis_bad_debt` | flat trajectory, no 2021-22 crisis step-up | **FIRED** | R12 diagnostic; fails-closed on missing crisis data |
| 21 | `green_claims_audit.audit` | green claim not backed by held REGOs | **FIRED** | **FAIL-OPEN gap KL-7** (obligation=0 → COMPLIANT) |
| 22 | `generate_dashboard_data._check_consistency` | exec-summary insights disagree with totals | **FIRED** | **FAIL-SILENT+OPEN gap KL-8** (no-insights → pass; per-key skip) |
| 23 | `generate_dashboard_data._check_basis_labels_present` (R14) | headline GBP figure with no basis/clock label | **FIRED** | fails-closed on a present-but-unlabelled figure |
| 24 | `generate_dashboard_data._check_population_consistency` | Book Size not reconciling to source population | **FIRED** | — |
| 25 | `health_check.run_health_check` | an expected daemon not running | **FIRED** | **fails-CLOSED** when tmux+ps both unavailable (good) |
| 26 | `health_check._check_stale_running_code` (R2/R3) | daemon process older than its own script | **FIRED** | — |
| 27 | `process_run_complete` change-detection gate | skip a genuinely-changed run / spurious skip on corrupt memory | **FIRED** | **fails-CLOSED** on unreadable dedup memory (good); R11 near-identical class mitigated by `FORCE_REPUBLISH_FLAG`+`source_git_hash` |
| — | LLM-judge evaluators (`phase-close-evaluator`, `epistemic-verifier`) | a judge able to Write/Edit its way to a PASS | **STRUCTURAL-ONLY** | read-only guarantee asserted; verdict quality NOT mutation-testable |

### PASS-2 GAPS REGISTERED FOR THE ORCHESTRATOR (KL-4..KL-8)
- **KL-4 (FAIL-SILENT)** `check_estimated_read_rate([])` returns clean — a total absence of reads is the most-broken state. *Fix:* alarm when reads are expected for the window but the log is empty. Not fixed (empty can be a legitimate first-run; `sanity_daemon` consumes it).
- **KL-5 (FAIL-SILENT)** `ConsumerDutyRegister().overall_rag()` on an empty register = GREEN. Under FCA Consumer Duty an un-assessed outcome is a governance failure. *Fix:* add an explicit UNKNOWN/UN-ASSESSED state. Not fixed — 14+ callers treat GREEN as baseline.
- **KL-6 (TAUTOLOGY)** `social_obligation.non_compliant()` trusts the self-declared `status` field, not spend-vs-target; a mislabelled-PAID underspend passes. Mitigated by the independent `underspend_records()`. *Fix:* fold `is_underspend` into `non_compliant()`.
- **KL-7 (FAIL-OPEN)** `green_claims_audit.audit()` short-circuits `obligation==0` → 100% COMPLIANT; broken green-product detection reads compliant. *Fix:* cross-check obligation=0 against whether any active green product had billed consumption. Not fixed — zero obligation legitimately means no claims.
- **KL-8 (FAIL-SILENT + FAIL-OPEN)** `_check_consistency` returns pass when `run_insights.json` is missing, and silently skips a one-sided missing headline key (same class as the R11 orphan-transition incident). *Fix:* treat an absent insights file as a hard failure once the pipeline guarantees it, and count a one-sided missing key as a mismatch.

---

## COVERAGE HONESTY — what is now covered vs what genuinely can't be

Pass 2 reaches **near-full apparatus coverage of the DETERMINISTIC controls**: the
compliance trackers, the health / page-consistency gates (R14 + population + stack
health), and the daemon change-detection gate are now mutation-tested. Still **honestly
uncovered** (in `control_registry.json` under `inventoried_not_yet_mutation_tested`):

- **LLM-judge verdict QUALITY** — `phase-close-evaluator`, `epistemic-verifier` agents.
  Only their **read-only structure** is now asserted (a judge that can Write/Edit its way
  to a PASS is theatre). Their actual *judgement* has no fixed prompt→NEEDS_WORK oracle
  and is **not deterministically mutation-testable** — documented, NOT counted as covered.
- **Daemon SCHEDULING loops** — the sanity/session-watchdog/deadman daemons' own cadence,
  cooldown and restart-backoff logic (their control INPUTS are covered; the loops are not).
- **The long tail of accumulator-style regulatory registers** (`company/regulatory/*`, 50+
  modules) — mostly reporting/ledger accumulators rather than fire/not-fire gates.

**The standing rule (now CLAUDE.md R15):** no control may be counted as evidence for a
level promotion, an Expert-Hour pass, or a green suite unless it has a passing mutation
test proving it fires on its own named defect.

**L3 assessment (honest):** this pass takes H12 to **near-full apparatus coverage of the
deterministic control set** — a defensible L3 for that scope. It is **not** total coverage:
the LLM-judge judgement layer is structurally-bounded only, and the daemon scheduling loops
and regulatory accumulator tail remain inventoried-not-tested. L3 for the deterministic
apparatus; the remaining categories are named, not hidden.
