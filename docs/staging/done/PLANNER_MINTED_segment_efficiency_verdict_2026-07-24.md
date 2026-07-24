# [PLANNER-MINTED] Surface the activity-based EFFICIENCY verdict per segment (value vs cost-to-serve) (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Rungs 1–6 empty this tick (the 5 in-flight `PLANNER_MINTED_*` docs are parked at director/deploy walls; SITE_V5 closed; both fidelity-ledger rows already attached to in-flight docs). **Propose-then-proceed.**

## Ratified goal served
**DIRECTOR_AXES.md v1, Axis 2 — Segmentation, the *Efficiency* half** (verbatim): "value per segment (cost-to-serve vs value; activity-based, per CLAUDE.md pricing law)." Also serves the CLAUDE.md pricing law directly: "flat margin makes some customers net-negative. Any pricing model must account for cost-to-serve at the customer level."

**This is the EFFICIENCY half, distinct from the in-flight `PLANNER_MINTED_generator_draw_wiring` doc** which serves the *Sophistication* half (coupled structure discovered through the wall). No overlap.

## Real-world fidelity gained
A 20-year veteran opening the site should be able to see WHICH segments the book makes money on and which it subsidises — the single most important commercial fact about a supply book (activity-based cost-to-serve is how real suppliers decide who to shed at renewal). The compute organs already exist (`company/pricing/cost_to_serve.py`, `company/finance/segment_profitability.py`, `saas/cost_to_serve.py`, `site/data/activity_cost.json`); the axis-2 gap is whether the **value-vs-cost EFFICIENCY VERDICT is legibly surfaced per segment** (net-negative segments exposed, not buried), against the director's own eyes as acceptance.

## Scope (propose-then-proceed; drawable NOW, no wall)
1. **DISCOVER/AUDIT (drawable now, doc-only):** does any live surface show value-vs-cost-to-serve *per segment* with an efficiency verdict (which segments are net-negative)? Read `site/data/activity_cost.json`, `segment_profitability.py`, and the `/world` + `/company` segment renders. If the verdict is already surfaced and legible → close this doc cheaply (honest cheap-close is a valid outcome, not a failure).
2. **BUILD (if gap real):** a `site/data/` feed carrying per-segment {annual value, activity-based cost-to-serve, net margin £ and %, net-negative flag}, rendered on the segment surface as a ranked value-vs-cost view (dataviz skill governs the chart — read it before writing chart code). Lead with the OUTCOME (which segments subsidise which), never effort metrics (R6/RC5). Every £ carries its basis clock (R14).
3. **R11 + R15:** render-harness test executes the page JS against the published feed and asserts the rendered net-negative flag; mutation flips a segment's sign and the surface must visibly change (fail-closed-visible when the feed is empty).

## Walls (untouched)
- No pricing/curriculum change — this EXPOSES cost-to-serve, never tunes margin toward a target (R12 anti-goal-seek: margin is a diagnostic).
- Wall discipline: cost-to-serve is built from through-the-wall observables the company already books (meter-read volume, service contacts, payment-failure handling, settlement) — no SIM-internal segment labels cross the seam.
- Site-lane, `site/**` disjoint file_scope (L2, parallel-safe).

## Propose-then-proceed window
Reversible throughout (site feed + render + tests; git reverts). No one-way door. Proceed on draw; the only director touchpoint is the axis-2 *verdict* on the landed surface (his eyes = acceptance, R11 residual — never a build gate).

---
## DISPOSITION — CLOSE, no build (2026-07-24 worker tick; the DISCOVER/AUDIT step's honest outcome)
**Scope step 1 (AUDIT) resolves this to a no-build: the proposed surface contradicts a same-day standing director ruling.** `docs/staging/done/DIRECTOR_RULING_FRONT_MISSION_BLOCK_2026-07-24.md` (2026-07-24, director via advisor bridge) rules, verbatim:
- The cost-arbitrage / cost-to-serve leg does **not** lead — it was moved to `/proof` (economics section, `site/proof/index.html:377` `#economics-anchor`), kept "a direction, not a figure" (`:1061`), losing front-door billing.
- "£7/household true cost-to-serve (five households, AI-compute unpopulated, current-book snapshot) **fails the veteran sniff test** — real UK CTS runs in the hundreds of £/household." Under **RC7, no cohort-derived £ figure leads any page**; on /proof it appears only with N, floor-not-figure framing, and its missing-lines enumeration.

This doc proposes exactly the declined artefact: a per-segment `{value, cost-to-serve, net margin £/%, net-negative flag}` feed **rendered as a ranked verdict that "leads with the OUTCOME (which segments subsidise which)."** That is (a) cohort-derived £ leading a public surface (RC7 wall), and (b) built on the same thin data (segments derive from the same ~5-household book that already failed the sniff test). The axis-2 Efficiency intent is **already served** in the director-sanctioned form: the /proof economics leg, direction-not-figure. Category-6 wall (what leads a public surface = director's by right) + RC7. No build. Archived to `done/`.

**Queued harness finding (SELF_INTERRUPT_DISCIPLINE — note, don't fix):** the RUNG-7 planner minted this from DIRECTOR_AXES.md WITHOUT cross-checking the most-recent director rulings, so it proposed rebuilding an artefact a same-day ruling explicitly demoted. Class: planner-mint must reconcile against `docs/staging/done/DIRECTOR_RULING_*` (recent) before asserting a gap, not only against the (slower-moving) axes doc. Same class as the surface-resolution finding on the sibling `world_spine_inline_graphs` mint.
