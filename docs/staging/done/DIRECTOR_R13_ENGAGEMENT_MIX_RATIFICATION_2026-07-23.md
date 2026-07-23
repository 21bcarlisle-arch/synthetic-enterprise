# Director R13 ratification — engagement mix (2026-07-23)

**Provenance.** Advisor-staged on the director's explicit verdict in live review, 2026-07-23. Answers the
handoff in `docs/design/ENGAGEMENT_MIX_RECONCILIATION_2026-07-22.md` §4–5. R13 authority: the engagement
mix is director-reserved curriculum; this doc IS the director's number.

## 1. RATIFIED

- **Shares:** `ENGAGEMENT_POPULATION_SHARE` → **ACTIVE 0.45 / PASSIVE 0.35 / DISENGAGED 0.20** (from
  0.48/0.23/0.29), per the reconciliation's candidate.
- **Q-A: YES** — the archetype remains a **behavioural disposition** (drives churn physics); the Ofgem RMI
  Oct-2025 three-way stock split is adopted as the external **anchor for shares only**, not a
  redefinition. The stock-vs-disposition seam stays registered (fusion-register entry 2 in
  `DIRECTOR_SEGMENTS_REVIEW_VERDICTS_2026-07-23.md` §1).
- **Q-B: static-first.** Single static mix now; **"regime-timed engagement schedule" is registered as a
  NAMED candidate curriculum scenario** — a future epoch-4-class lever, not a silent parameter.
- **Vintage clause (read before any future regime decision):** this baseline is a deliberate **hybrid** —
  **2025-recovery SHAPE on a pre-crisis-steady aggregate LEVEL** (shares from Ofgem Oct-2025 stock;
  aggregate active-renewal held ≈0.35 by unchanged per-archetype probabilities, 0.352→0.349). The baseline
  is not all one vintage; do not misread it as "the 2025 regime."

## 2. WITHHELD — explicitly not authorized

- **Per-archetype renewal probabilities (0.65/0.15/0.02) unchanged.** The aggregate is NOT to be pushed
  toward the ~45% recovery figure — R12 stands: that number is a diagnostic, not a target. Re-levelling
  the portfolio is a separate, future R13 decision.

## 3. NEW NAMED ATOM (DISCOVER, non-blocking, later)

**Continuous psychological/behavioural engagement model.** The director's standing ask: the three
discrete lifetime bins are a bounding simplification. The future model should treat engagement as a
**latent, distributed propensity** — state-dependent, movable by life events, service episodes, and price
shocks (a household can BECOME disengaged), coupled per the registered hypotheses
(engagement×price_sensitivity; U-shape by affluence). Register in the map as DISCOVER; do not begin
without a granted turn; it must not delay the share edit below.

## 4. Consume path

On this doc: the ratified share change is the **one-line granted-turn BUILD** the reconciliation defined
(`ENGAGEMENT_POPULATION_SHARE`, per-archetype probabilities fixed). Standard verify: the reconciliation's
aggregate-neutrality arithmetic is the acceptance check.

## 5. Risk

- **Touches:** `simulation/household_segments.py` (one line) + map (one new DISCOVER atom).
- **Blast radius:** anything consuming archetype shares downstream — churn/revenue aggregates move ≤0.3pt
  by design; any test pinning the old 0.48/0.23/0.29 or derived book-mix constants is the stale-test
  class — sweep dependents, not just the edited file.
- **Probable failure mode:** a consumer assumed DISENGAGED≈0.29 (e.g. book-mix expectations in site/state
  or reporting). Mitigation: grep consumers of the share constant and book-mix assertions before merge.
