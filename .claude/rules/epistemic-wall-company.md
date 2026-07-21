---
paths:
  - "company/**/*.py"
  - "saas/**/*.py"
---

# You are editing the COMPANY side of the epistemic wall

This code operates under the SAME information constraints as a real UK energy supplier. It cannot
see simulation internals — churn parameters, forward curve construction, weather engine outputs, VaR
internals, or any full historical dataset read without an as-of/bisect bound. It discovers the world
through observable interfaces only: market data feeds, meter reads, customer interactions, its own
bills and payments, regulatory publications.

**Before writing or editing anything here, ask: "Could a real UK energy supplier know this?"** If the
answer requires reading simulation internals, it is a violation — not a style issue, a Tier-1
epistemic-law concern.

- The SIM/company seam is `company/interfaces/sim_interface.py` — it exposes observables only, never
  internals. New crossings should prefer a typed, versioned-message adapter shape over a direct
  function call (the wall IS the future go-live seam).
- Point-in-time discipline: use `company/interfaces/point_in_time_view.py` /
  `bitemporal_event_log.py` for anything that needs "what did we know when" — never read a full
  historical dataset without an as-of/bisect bound. `.claude/hooks/block_point_in_time_read.py`
  flags exactly this pattern.
- Run `python3 -m tools.epistemic_verifier` before committing anything in this path — it scans for
  data-flow/timing violations, not just literal `simulation.*` imports.
- The company's models are approximations built from observed outcomes, not reads from ground truth.
  That imperfection is the point — do not "fix" it by giving the company more visibility than a real
  supplier would have.

**D-SEGMENT / cohort wall (2026-07-21, `docs/design/SEGMENTATION_RECONCILIATION_FRAME.md` §0, CANONICAL
WALL RULING — director console, verbatim):** "Segmentation ground truth lives entirely behind the wall.
The company starts with public-data priors only (EPC, census — what a real supplier could obtain), and
discovers everything else exclusively through acquisition and ongoing interaction, scored on the
belief-vs-truth gap. No segment label, attitude, or sensitivity ever crosses the wall directly." Concretely:
- `company/analytics/cohort_discovery.py` builds the company's BELIEVED cohort from EPC/census public
  priors + interaction observables only — it must NEVER import `simulation.population_draw` (or any
  `simulation.*`/`sim.*` module) and must NEVER read a SIM `Cohort`'s `green_stance` field (no company
  observable exists for it, ever — do not invent a proxy).
- `company/interfaces/sim_interface.py` (the ONE approved seam, otherwise allowed to import simulation
  internals) must never define a method/attribute/return-field carrying a segment label, attitude, or
  sensitivity — enforced by `tools.epistemic_verifier._scan_seam_files_for_forbidden_symbols` (a curated
  symbol scan, not the generic import-direction check, since this file legitimately imports SIM internals
  elsewhere). Run `python3 -m tools.epistemic_verifier` — it always runs this seam guard regardless of scan
  scope.
- `tools/couple_cohort.py` is the ONLY place permitted to hold the SIM-truth `Cohort` and the company's
  `BelievedCohort` side by side (it lives outside `company/`/`saas/`, exempt from this rule).
