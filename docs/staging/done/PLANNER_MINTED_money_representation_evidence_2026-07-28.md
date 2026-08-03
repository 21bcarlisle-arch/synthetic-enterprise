<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BLOCK_RELEASE: propose_then_proceed -- was 'director_ratification', an act abolished 2026-07-29 and swept 2026-08-03: propose, record, act. Original note: evidence gathered; the float->Decimal migration is a director-reserved decision, boundary-reconciliation returned as [ACT] -->
<!-- DISCOVER CLOSED 2026-07-28: docs/design/MONEY_REPRESENTATION_EVIDENCE.md. Evidence gathered (NO money type migrated — director-reserved wall held): 0 Decimal usage (money is float end-to-end incl SQLite REAL at rest); worst single-bill drift £0.02, aggregate -£0.22 over 1,441 bills (shadow-Decimal cross-check vs 1,588 real bills, basis 2026-07-28T08:30:04Z billed); MATERIAL finding = 37.0% of bills' rounded line items don't sum to the printed total. Recommendation returned as [ACT]: boundary-reconciliation fix first (narrow blast radius, closes the 37%); full float->Decimal core migration reserved as a separate director decision before real customer money. -->
# [PLANNER-MINTED] — Money-representation evidence for the director (float vs Decimal) — DISCOVER ONLY (2026-07-28)

**Source:** `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §6 + Acceptance item 7
(committed `29361d1c2`). **RESERVED TO THE DIRECTOR — the decision is his; this atom gathers only the
evidence he asked for. Do NOT migrate money types on any initiative (one-way door #5-adjacent: it changes
how bills are computed under the Tier-1 "bills accurate above all" rule).**

**Provenance:** RUNG-7 planner mint — the sixth of the six the §4-DEFECT ruling's body creates, but the
BUILD/decision half is a **WALL**. Census verified today: **zero** uses of `Decimal` across the sampled
`saas/`+`company/` set (including `saas/bill_generator.py`, `saas/reporting/annual_report.py`); money is
computed in `float` everywhere. The ruling's point: the current position is not "float" or "Decimal" — it
is **undeclared**, the worst of the three.

**Serves:** the Tier-1 standing rule *bills accurate above all* — the director needs the evidence to rule
on a declared money representation.

**Fidelity gained (one sentence):** none until the director rules — this atom produces the **evidence**
(worst observed rounding drift; boundary-conversion blast radius) so the director can make an informed,
reversible-at-his-hand decision on money representation.

---
## Lane / level / deps
- **Lane:** `L3 DISCOVERY` — a read-only measurement + written recommendation. **Drawable NOW.**
- **Target level:** N/A — a findings/recommendation artefact returned to the director as ONE [ACT], **not
  actioned** (ruling: "Items 1–6 proceed. Item 7 stops at the wall.").
- **Deps:** none.

## Exit criteria (evidence to return, both items the ruling named)
1. **Worst observed rounding drift across a full billing run** — measure the cumulative float rounding error
   over a complete billing run (per-bill and aggregate), reported with its `//` basis clock (R14). Read-only
   instrumentation; **do not change any money type to measure it** (shadow/parallel Decimal computation for
   comparison is fine — it must not replace the live float path).
2. **Blast radius of a boundary conversion** — enumerate the surface where money crosses a boundary
   (bill_generator → reporting → dashboard → settlement) and estimate the migration cost + risk of a
   float→Decimal boundary conversion.
3. A **recommendation** (either answer can be right, per the ruling) + the evidence, returned to the
   director as one [ACT] NTFY / staged findings doc. **Recommendation only — no migration.**

## Walls untouched (this is the point of the atom)
- **One-way-door #5-adjacent / Tier-1 "bills accurate above all":** money representation is
  **director-reserved**. This atom NEVER migrates a money type; it measures and recommends.
- **R9:** every figure labelled observed-with-evidence or inferred; evidence before narrative.
- **R14:** the drift figure carries its basis clock.
- **No level move; no safety/auth/curriculum change.**
