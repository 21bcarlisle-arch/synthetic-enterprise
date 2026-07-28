<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_level_up -- privacy-policy page; agent proposes the level, the director moves the cell (R16) -->
> **BUILT + R11-VERIFIED LIVE 2026-07-28** (worker tick, commit `a094c87b8`). `site/privacy/index.html`
> is live at **https://poesys.net/privacy/** (HTTP 200; rendered content asserted on the deployed page:
> simulation banner "no real customers and processes no real personal data", UK GDPR, Data Protection
> Act 2018, PROVISIONAL label, Priority Services Register, ICO, `noindex`). A "Privacy" footer link is
> live on both the home page (`href="./privacy/"`) and the customers page (`href="../privacy/"`) —
> confirmed on the deployed surfaces. Site link-walk = 0 dead links; `pytest site/` = 348 passed.
> Marker flipped self-drawable→blocked: the ONLY remaining sub-item is the **level claim**, which is
> `blocked_on: director_level_up` (R16 — the agent proposes level, never moves the cell).
>
> **Sanity-finding disposition:** `coldwalk:no_privacy_policy_page` (register 6) is now genuinely
> remediated. Per the RATIFIED answer `docs/design/GAP_TRIAGE_STALENESS_AND_BLASTRADIUS.md` §(a), a
> remediated/stale row is dropped by the **read-time staleness filter in the GAP1 reader** (evidence:
> the live page + this commit), **NOT** by mutating the ledger `state` (which honestly stays
> `adjudicated-real` — it *was* real; and there is no `resolved` state in `_VALID_STATES`). That reader
> is `PLANNER_MINTED_gap1_reader_contract_failopen_fix` BUILD half, blocked_on `director_build_open`.
> The ledger is left untouched by design; the remediation evidence is recorded here for it and for any
> re-adjudication cold-walk.

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
