<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Privacy-policy page (customer-facing legibility/credibility gap) (2026-07-28)

**Source:** `PLANNER_MINTED_first_ranked_gap_list_2026-07-28` (GAP3) P3 + `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28`
§1. Net-new: register-6 standing sanity finding `coldwalk:no_privacy_policy_page`, **adjudicated-REAL and
unresolved** (`docs/observability/sanity_adjudication_ledger.json`). grep-confirmed **not** minted and
**not** present on the live shadow site — a genuine missing customer-facing artefact, not a duplicate.

**Provenance:** RUNG-7 planner mint (autonomous — `mint` direction, GAP_TRIAGE_RATIFIED §2). Ranked P3 in
GAP3 (PRODUCT-first, cost = S). Honours the draw-mix condition (a product/site-lane atom alongside the
machinery mint `gap1_reader_contract_failopen_fix`).

**Serves:** the disqualification-battery credibility standard a real UK energy supplier is held to — a
supplier website with no privacy policy is a "a practitioner would say this is not credible" item
(SPEC_005 legibility/impersonation-adjacent). A real supplier publishes a privacy policy; ours does not.

**Fidelity gained (one sentence):** the site gains the **privacy-policy artefact every real UK supplier
publishes** (UK GDPR / DPA-2018 obliged) — a concrete legibility/credibility gap closed on the live surface.

---
## Lane / level / deps
- **Lane:** `L2 SITE` (`site/**` / the shadow-site build) — parallel to builds permanently, disjoint
  file_scope. Drawable NOW (no BUILD_OPEN needed for the SITE lane).
- **Target level:** a published privacy-policy page reachable from the site, `blocked_on: director_level_up`
  for any level claim (R16). Content is a standard supplier privacy policy (data collected, lawful basis,
  retention, subject rights, contact) — **PROVISIONAL/simulation-labelled**, since this is a simulated
  supplier with no real customers (R11: no public claim that can't be retracted; no real-world commitment).
- **Deps:** none — a standalone site page.

## Exit criteria
- A privacy-policy page **live on the deployed site** and linked from the footer/nav (R11: verify to the
  rendered value — fetch the live URL and confirm the page renders, not just the file on origin).
- Clearly labelled a **simulation** artefact (no real data is processed) so it makes no real-world/legal
  commitment (one-way-door #2 untouched).
- The `coldwalk:no_privacy_policy_page` sanity finding can then be re-adjudicated resolved.

## Walls untouched
- **No real-world commitment (one-way door #2):** the page is a simulation artefact, explicitly labelled,
  binding nothing outside the repo; it makes no legal representation to a real data subject (none exist).
- **R11:** "done" = the page fetched from the LIVE site renders, not the committed file.
- **No level self-bump (R16):** lands with `blocked_on: director_level_up`.
