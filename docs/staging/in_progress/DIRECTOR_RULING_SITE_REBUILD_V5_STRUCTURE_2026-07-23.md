# [CC PROCESSING STATUS — 2026-07-23] IN PROGRESS (sequence step 1 DONE)
#
# STEP 1 (structure confirmation against canon) is COMPLETE — verdict CONFIRMED, no
# propose-back. Artifact: `docs/design/SITE_V5_STRUCTURE_CONFIRMATION.md`. The five-surface IA,
# the three goals, the kills, the didactic-graph rule and the 1→5 sequence are all reconciled
# against BRAND_CONSTITUTION / SITE_CONSTITUTION (rules 1–7) / _redirects / the site-lane gate /
# fronts.yaml (site build is authorized now under the open SUPPLIER front). The one IA conflict
# (six-door → five-surface) is one this ruling itself resolved.
#
# OPEN (the still-open sub-items — why this file is parked in in_progress, not root):
#   §4.2 — build the five surfaces, ONE per phase, in order 1→5, each landed LIVE and
#   Expert-Hour-reviewed against its single job before the next starts. Tracked as a ranked
#   campaign in PRIORITIES.md (§SITE_V5 REBUILD CAMPAIGN, top of queue). Per-surface DoD in the
#   confirmation doc §4.
#   NEXT DRAWABLE PHASE: Surface 1 — Front door MVP (v4 argument, 10-second test; swap the
#   /now/ landing LAST). UNBLOCKS when it lands live + passes its Expert Hour → then Surface 2.
#
# Parked here (excluded from the supervisor unprocessed-staging scan) so it does not re-grant a
# turn every cycle with nothing new to do; the ongoing build is driven by the PRIORITIES.md
# campaign entry via the L2 SITE lane, not by a staging re-scan.
# ─────────────────────────────────────────────────────────────────────────────────────────────

# DIRECTOR RULING — Site rebuild: ratified structure + MVP sequence (2026-07-23)

**Provenance.** Director-ratified in advisor conversation, 2026-07-23. Follows the director's live axis-1 review of the
site against `docs/design/BOARD_SPEC_005_RECONCILIATION.md`. Advisor-staged; the structure below is the director's
decision, transmitted as a decision. Where this ruling conflicts with `POESYS_SITE_BRIEF.md`'s six-door IA or the
2026-07-19 site-reorient steer, **this ruling wins** — it is the later director act, aligned to pitch v4.

---

## 1. The verdict (context, decided)

**Axis-1: site 1/5.** Row-by-row scoring was abandoned after two rows — the deficiency is global. The site fails all
three of its actual goals: (1) **marketing** — the landing sells nothing in ten seconds; (2) **observability of the
SIM's causal relationships** — weather, wholesale, segments, demographics, usage and behaviour are not walkable as a
connected chain; (3) **evidence of the e2e supplier SaaS**. These three goals are the standard for the rebuild.
Spec 005's rubric rows remain the standing fidelity oracle but are **subordinate** to these three goals.

## 2. Ratified structure (DECIDED — do not redesign the IA)

Five surfaces. Each has exactly one job.

1. **Front door — the pitch.** V4's argument, lay-readable, passes the ten-second test. Carbon thesis
   (£/tCO₂e, personalisation at near-zero marginal cost). The honesty line above the fold: no customers, no
   licence, a running simulator. *Job: marketing.*
2. **The World — the simulation, walkable.** The causal chain is the page's spine:
   weather → wholesale price → demographics/segments → usage & behaviour → bills → carbon. Each link opens
   onto live data and its external anchor (Elexon, ONS, DESNZ, Ofgem). *Job: SIM relationship observability.*
3. **The Company — the supplier SaaS.** The e2e operating stack shown as product: pricing, hedging, billing,
   credit & collections, customer service, compliance, monthly accounts — each with real outputs from the
   latest run. Product capability, never effort metrics. *Job: e2e SaaS evidence.*
4. **Proof.** Fidelity results including failures; claim-status on every figure (v4 Note-on-Claims vocabulary);
   the corrections/retractions history rendered in place; the challenge channel. Method content folds in here.
   *Job: v4's "corrects itself in public" claim, made real.*
5. **Director window.** Authenticated, off-nav, minimal MVP: the reserved queue first, machine health second.
   Everything else in Spec 005 §3 (delta view, DO battery, stop control) is DEFERRED — do not build this pass.

**Kills (decided):** `/now/` as the default landing; the shadow site (`site/shadow/**` — supersession banner +
noindex at minimum, removal preferred); Method and Journey as separate doors; the test-count and commits/day
charts as public surfaces (the publish-gate build stamp is internal and untouched).

## 3. Design requirements (DECIDED as requirements; the design itself is yours)

- **BRAND_CONSTITUTION.md is binding.** BRAG palette, colour-is-information, six-glyph grammar, the type-only
  wordmark. SITE_CONSTITUTION rules 1–7 remain binding except where this ruling changes the IA.
- **Didactic graphs are the site's centre of gravity.** The director's words: *powerful and impressive but simple
  graphs of the data. It should be didactic. Explain the things we know. Proving the relationship and hypothesis.*
  Concretely: every major graph teaches ONE relationship the project has actually established, states the
  hypothesis in plain language, shows the evidence proving it, and cites the anchor. Examples of relationships we
  genuinely know and can prove from real run data: cold snaps → demand → price; the 2021-22 crisis in the real SSP
  series; demographic segment → consumption shape; estimated reads → catch-up bill shock; hedged vs unhedged P&L
  through the crisis. A graph that decorates rather than teaches does not ship.
- **Claim-status discipline** (observed / external benchmark / chosen / not-yet-instrumented / hypothesis /
  retracted) on every published figure, per v4's Note on Claims. R11 CLAIM=PIXEL and R14 basis-clock stand.
- The Spec 005 reconciliation's findings F1–F5 are absorbed by this structure; treat its rows as the
  per-surface acceptance rubric where they don't conflict with the three goals.

## 4. Sequence (DECIDED)

1. **Structure confirmation first.** Before building, confirm this IA against canon (SITE_CONSTITUTION,
   BRAND_CONSTITUTION, redirects, site-lane gate, data-layer dependencies). If a genuine conflict emerges that
   this ruling has not already resolved, propose back — do not silently resolve.
2. **Then MVP per surface, in order 1→5**, one surface per phase, each landed live and Expert-Hour-reviewed
   against its single job before the next starts. MVP means: the surface does its one job with real data and
   didactic graphs — not feature-complete, never fabricated.

## 5. Decided vs open

**Decided:** the five-surface IA; the three goals as the standard; the kills; didactic-graph requirement;
sequence 1→5; deferral of the director-window DO battery. **Open (yours):** page-level design, graph selection
within the didactic rule, data-layer refactoring, redirect scheme, how Method content folds into Proof.

## 6. Risk

**Touches:** `site/**`, `site/data/` generators in `tools/`, `_redirects`, site-lane test gate, publish gate's
site checks. **Blast radius:** public surface entirely; every existing door URL. **Probable failure modes:**
(a) broken links/redirects when doors are killed — mitigate with 301s and a full-link walk before each landing;
(b) losing R11/R14 discipline mid-rebuild while pages are in flux — mitigate by keeping the site-lane gate green
at every commit, never landing a surface without its passports; (c) the didactic-graph rule drifting into
decorative charts — mitigate by stating each graph's hypothesis in the page copy itself, so an Expert Hour can
fail it; (d) killing `/now/` before the new front door exists — sequence the landing swap last within surface 1.
**Proportionality:** contract-touching (site canon) — implement with the named mitigations; the IA itself is
director-ratified and not open.
