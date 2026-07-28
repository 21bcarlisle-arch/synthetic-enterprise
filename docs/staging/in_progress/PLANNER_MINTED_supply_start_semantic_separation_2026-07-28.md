<!-- SUPERVISOR_DRAW: blocked -->
# [PLANNER-MINTED] — separate `supply_start` (real relationship start) from the term-schedule anchor (2026-07-28)

> **CLOSED 2026-07-28 (DISCOVER done): enumeration published at `docs/design/SUPPLY_START_SEMANTIC_SEPARATION_DISCOVER.md`.**
> Verdict **REAL and LIVE** (not merely latent): C1_2's real acquisition event is 2020-12-30 (`run_output_latest.json`),
> yet its field reads `acquisition_date: 2016-01-01` — a ~4.99-year phantom rendered as "Customer since 2016" on the
> live customer/company pages and bucketed into the 2016 cohort with ~9yr tenure. **11 wrong-meaning consumer sites**
> (7 LIVE-wrong for C1_2 today + 4 latent), scoped to the **6 successors only** (base + fresh-market customers already
> carry correct dates). The overload is THREE semantics: (A) term/billing anchor — keep; (B) supply-start; (C)
> tenure/cohort — B+C share one fix. BUILD sketch + R10 class invariant (`supply_start >= first_observable_event`) +
> two R15 mutation shapes specified. **BUILD blocked_on director_level_up (R16 — no self-bump); category: SUPPLIER
> product front (`company/crm`).** No production code touched.

**finding_key:** `coldwalk:c1_2_successor_acquisition_date_mismatch` (adjudicated-real, ledger 2026-07-12).

**Source:** `docs/design/SANITY_FINDING_COVERAGE_MAP.md` row 3 — the P2 coverage audit's LAW-C read found
this adjudicated-real finding has **no remediation atom** (grep of staging/design/map = none). This mints it.

**Provenance:** RUNG-7 planner mint from the ratified backlog's own deferred P2 disposition (a defect fix is
a `mint`-direction move, GAP2 §2, autonomous). Distinct from the billing-anchor mechanism, which is
deliberate and correct and must NOT change.

**The defect (root-caused in the finding's own evidence).** `saas/customers.py` intentionally keeps a
successor's `acquisition_date` identical to the predecessor's so the 365-day term-schedule anchor aligns
(verified correct: C1_2's first invoice genuinely lands 2020-12-30, five steps from the shared 2016-01-01
anchor — this is what makes the churn→successor handoff work without extra reconciliation, KEEP IT). The
**real gap:** `acquisition_date` is *overloaded* to also mean "real relationship start date" by a different
consumer — `company/crm/customer_registry.py:133` writes it straight into a DB column literally named
`supply_start`, so a successor's CRM record claims a supply-start ~5 years before the customer actually
existed. One field, two incompatible meanings, never separated.

**Serves:** DIRECTOR_AXES v1 **#2 Segmentation/customer truth** (a supply-start date 5y wrong is a
per-customer truth defect a real supplier's CRM would never carry) and **#3 Believability**.

**Fidelity gained (one sentence):** the successor's CRM supply-start reflects the real relationship start,
not the predecessor's billing anchor — so tenure/loyalty/regulatory-clock logic keyed off supply-start stops
inheriting a 5-year phantom history.

## Exit criteria (falsifiable, R11 + R15)
- **DISCOVER (self-drawable now):** design doc naming the two distinct semantics (billing/term anchor vs
  real supply-start) and where each is read; enumerate every consumer of `acquisition_date` to find which
  ones actually mean "relationship start" (the overload surface).
- **BUILD (gated):** `customer_registry` derives `supply_start` from the real churn/activation date, not
  the anchor; R15 mutation — a successor whose activation ≠ anchor MUST show `supply_start` = activation
  (mutate to write the anchor → the test FIRES). Class guard (R10): a CRM invariant that `supply_start`
  is never earlier than the customer's own first observable event.

## Lane / rank / walls
- **Lane:** `company/crm` (SUPPLIER product front). **DISCOVER/design self-drawable now; BUILD blocked_on the
  relevant front/level move (director_level_up on the level move, R16 — no self-bump).**
- **Rank:** among product-lane atoms per the ratified GAP2 method; PRODUCT-FIRST guard — never outranks a
  live product item on composite alone.
- **Walls:** R13 untouched (no baseline/curriculum value). No silent closure — if the overload turns out to
  have no wrong-meaning consumer, that is a credited `not-worth-the-complexity` argued outcome, not a
  reclassification of the finding.
