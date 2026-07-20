# Proposal — restore the operational window + deepen the segmentation (2026-07-20)

**Responds to** `docs/staging/DIRECTOR_STEER_LEGIBILITY_AND_SEGMENTATION_2026-07-20.md` (two linked
[STEER]s, contract-touching, "propose and proceed — correct-after"). This is the "propose the
structure before rebuilding" step. I proceed on Part 1 (world/supplier) immediately after; Part 2
runs DISCOVER→FRAME before any generator change, as instructed.

## Retro — own the cause (R9, no deflection)

The site-reorientation steer said the narrative spine should follow the pitch's argument. Executing
that literally produced a well-made **pitch document** where the director's **operational window**
used to be. His standing brief has three jobs — (1) his live window on the system, (2) the sales /
promotion tool, (3) the results-of-actions control surface he steers from — and the v4 rebuild
served (2) while gutting (1) and (3). "I don't get any of it anymore. I can't follow what the world
is doing, what the supplier is doing, and what this is like for an individual customer." That is the
defect: legibility of **running state** was traded for legibility of **argument**. The fix is not to
undo v4 — it is to make the two coexist, because (the pitch's own claim) honest state *is* the
argument.

## PART 1 — The operational window (reconciled with world / supplier / customers / project)

**Principle:** every door carries two layers — a **narrative layer** (the pitch, for the outsider)
and an **operational layer** (the running state, for the director). Default the director's entry to
the operational layer; the outsider reads the narrative. This reconciles with his long-standing
four-section framing (world / supplier / customers / project) rather than inventing a third — the
existing doors already map to it (World, Company=Supplier, Customers, Project=Journey).

The four things he must be able to follow **as running state, not argument**, and the data that
already exists to show them (the gap is SURFACING, not generating):

| Section | "What is it doing right now?" | Live data (already on disk) |
|---|---|---|
| **World** | current weather + the **regime it is in** and how it got there; market, prices | `weather.json`, `world.json`, price feeds — now with the shipped cold-and-still regime physics |
| **Supplier** | current hedging / pricing / billing / collections / **cash**; the decisions it took and **why** | `supplier.json`, `company.json`, `decisions.json`, `margin_bridge.json`, `wip_flow.json` |
| **Customer** | ONE named/numbered household: consumption, bill, payments, products, arrears, experience | `customer_sample.json`, `customers.json`, `state/billing_ledger.json` — **depth-blocked by Part 2** |
| **CO₂** | the per-customer carbon trajectory (the mission's unit of account) | E5 (designed, not instrumented) — show HONESTLY as "designed, instrumenting", never a fabricated number |

**Structure proposed:** on each of the four doors, add an operational panel at the top ("STATE — as
of <stamp>") that reads the live JSON and renders the current running state + the last few decisions
with their *why*; the narrative continues below. A customer section shows a **specific** household
end-to-end (a drill-down from a cohort, once Part 2 gives real cohorts). The regime line on World
ties to the just-shipped weather physics. Freshness stamp + basis labels on every figure (R11/R14).
**No fabricated numbers**: where the trajectory/£-per-tCO₂e is not yet instrumented, say so.

**Proceed now (correct-after):** World + Supplier operational panels first — their data is fully on
disk and they carry none of Part 2's dependency. Customer + CO₂ deepen as Part 2 and E5 land.

## PART 2 — Segmentation (D-SEGMENT): cohorts by combination, derived from data

**The gap:** existing segments (`simulation/segments.py`, `company/crm/behaviour_segment.py`, …) are
largely **single-axis** (a debt band, a behaviour label). The mission rests on **permutations** of
orthogonal factors — the valuable and dangerous customers are rare *combinations*, not the
population centre. Part 1's customer view is blocked by this: you cannot show a cohort the model does
not have.

**The factor axes** (the trait layer only — timing/events/salience are the separate later state
track, not conflated here):
- **Need** — house physics (thermal performance, heating system) + occupancy.
- **Attitudes / values** — price sensitivity, environmental motivation, trust.
- **Engagement capacity / behaviour** — digital engagement, payment reliability, responsiveness.

**Method (DISCOVER → FRAME, no generator change yet):**
1. **DISCOVER** — cluster / estimate the JOINT structure across the axes from the **linked evidence
   base** (`data/lake/lcl_household_load_shapes_2013/` real load shapes + the population anchor),
   NOT asserted. Report the discovered cohort combinations + their joint frequencies. Where a
   combination is asserted rather than estimated (thin data in a corner), declare it a simplification
   with provenance (R10).
3. **Independence discipline** — the generator anchor and the validation anchor come from **disjoint
   sources**; the company never validates discovered cohorts against SIM ground truth.
4. **Worst-cell, not average** — the frame scores the rare dangerous combinations (Atom A, already
   built, is the scoring frame; this steer is about the population MODEL carrying the structure Atom
   A scores). Score the joint tail, never the population centre.
5. **FRAME** — the cohort schema (the permutation space + the reconciliation invariant: cohort mix
   aggregates back to the population). Only after FRAME does any generator change get proposed —
   **do not silently alter existing archetype ground truth mid-campaign.**

## Sequencing + what comes to the director as [ACT]

1. **Now:** this proposal + PROCEED on Part 1 World/Supplier operational panels (SITE lane, ungated).
2. **Next:** Part 2 DISCOVER (cluster the evidence base) → FRAME the cohort schema.
3. **Then:** deepen Part 1's Customer section on the real discovered cohorts; wire CO₂ honestly as E5 lands.

Only genuine gate-opens come as [ACT] (per the steer): a generator change to the population model
(Part 2, after FRAME — it touches archetype ground truth, director-reserved) and any E5 emissions-
factor values-call for the CO₂ section. Everything else proceeds under correct-after.
