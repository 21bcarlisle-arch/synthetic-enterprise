# THE CONTROL KILL LIST

**Spec:** `docs/staging/CONTROLS_THAT_CANNOT_FAIL.md` (director P0, rank HIGHEST).
**Method:** `tests/controls/test_control_mutation.py`. **Registry:** `docs/design/control_registry.json`.
**Produced:** 2026-07-13.

> A control that CANNOT FAIL is worse than no control — it manufactures confidence.
> For every control we injected the exact defect it exists to catch. It must fire.
> A control that does not fire on its own named defect is **THEATRE**.

---

## HEADLINE (the honest number)

- **13 controls inventoried** in the highest-tier / customer-impacting set.
- **13 mutation-tested this pass.**
- **12 FIRED** on their own named defect.
- **1 is THEATRE** — the flagship `vat_by_segment` arithmetic check (`check_vat`), a
  **TAUTOLOGY**. It is retained as documented defence-in-depth but structurally
  cannot catch the SME-as-Household mislabel it is named for; the independent
  cross-check that replaces it (`check_vat_consistent_with_consumption`) **fires**.

### By killer pattern (found across the library)
| Killer pattern | Count | Controls |
|---|---|---|
| **TAUTOLOGY** | 1 | `check_vat` (vat_by_segment arithmetic) — THEATRE, mitigated by an independent control |
| **FAIL-OPEN** | 1 (**FIXED**) | pre-bill gate skipped all VAT validation when subtotal ≤ 0 |
| **FAIL-SILENT** | 1 (**FIXED**) | Qwen internal-audit backstop returned "clean" when Ollama was down |

Plus two **documented, sourced limitations** (not killer patterns): the YearlyRange
pre-cap "cannot check" branch, and the epistemic verifier's two coverage gaps —
both listed below, neither counted as theatre.

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

## COVERAGE HONESTY — inventoried but NOT yet mutation-tested

This pass completed the highest-tier / customer-impacting set. The following categories
are inventoried in `control_registry.json` under `inventoried_not_yet_mutation_tested`
and are **not** claimed as mutation-proven:

- **Evaluators** — `phase-close-evaluator`, `epistemic-verifier` agents (LLM-judge;
  no deterministic mutation harness this pass).
- **Daemons** — the sanity daemon's own scheduling/dedup logic (its two inputs,
  internal_audit + population checks, ARE covered here).
- **Population-sanity checks** — `company/compliance/population_sanity.py`.
- **Health / page-consistency checks** — `tools/generate_dashboard_data.py`
  (`_check_consistency`, `_check_basis_labels_present` / R14).
- **Other compliance trackers** — green-claims, consumer-duty, social-obligation,
  crisis-bad-debt validators (registered with `existing_tracker` pointers; internal
  predicates not mutation-tested this pass).

**The standing rule this establishes:** no control may be counted as evidence for a
level promotion, an Expert-Hour pass, or a green suite unless it has a passing mutation
test proving it fires on its own named defect. (For CLAUDE.md — orchestrator to land.)
