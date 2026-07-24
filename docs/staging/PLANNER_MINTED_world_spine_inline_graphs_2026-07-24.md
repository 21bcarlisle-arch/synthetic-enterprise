# [PLANNER-MINTED] Inline graphs IN the /world causal spine (legibility at a glance) (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). **Propose-then-proceed.**

## Ratified goal served
**DIRECTOR_AXES.md v1, Axis 1 — Website** (verbatim): "Usefulness to him as an operational window — can he open the site and understand the state of the company without asking" + "Simplicity / clarity as a marketing tool — legible to someone who is not the builder." Plus the **explicit director-named non-blocking follow-on on SITE_V5 surface_2** (`CAMPAIGN_REGISTER.yaml` surface_2_the_world note, verbatim): "(a) inline graphs in the spine itself (graphs currently in deeper sections)."

## Real-world fidelity gained
The /world causal spine currently renders each node as a single figure (240 HDD, £85.92/MWh, £5,067.57 billed) with the supporting graphs buried in deeper sections. A veteran reads a supply book by its SHAPE — the winter HDD curve, the SSP spike distribution, the bill spread — not point figures. Putting a small inline graph AT each spine node (weather HDD sparkline, wholesale price band, bill distribution) makes the whole causal chain legible in one glance, directly serving axis-1 "understand the state without asking." Verified this tick: no inline spine graphs exist on the world page yet (grep of `site/index.html` — the gap is real).

## Scope (propose-then-proceed; drawable NOW, no wall)
1. **READ the dataviz skill FIRST** (before any chart code, per its own trigger) — form heuristic, palette validator, mark specs.
2. **BUILD:** one small inline mark per spine node, rendered (render-not-author) from the already-published `site/data/world.json` / `premise_demand.json` series — weather HDD sparkline, wholesale SSP band/exceedance, premise-demand worst-cell bar, bill spread. No new data organ; consume existing feeds. Colour is information-only (SITE_CONSTITUTION), light-and-dark consistent.
3. **R11 + R15:** render-harness executes the page JS against published data and asserts each inline graph renders its real series; mutation flips a series value and the mark must visibly change; fail-closed-visible when a feed is missing.

## Walls (untouched)
- Site-lane only, `site/**` disjoint file_scope (L2, parallel to builds; disjoint from the in-flight `premise_demand` doc which owns its own feed — coordinate on the shared world page render, don't co-edit the same block).
- No figure fabricated; every mark reads a published series carrying its basis (R14).
- No curriculum/ground-truth touch.

## Propose-then-proceed window
Reversible (site render + tests; git reverts). No one-way door. Proceed on draw; director's axis-1 verdict on the landed surface is his eyes (R11 residual), never a build gate.
