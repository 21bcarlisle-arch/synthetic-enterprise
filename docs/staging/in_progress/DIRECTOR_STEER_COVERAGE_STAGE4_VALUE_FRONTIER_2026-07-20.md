> **[REFRAMED — 2026-07-20, DIRECTOR_STEER_SEGMENTATION_LEARNING_VALUE_REFRAME]** The objective below (P&L "value of the customer", bad debt as a value REDUCTION, four fixed weights) was CORRECTED by the director to LEARNING/INFORMATION value (bad debt a positive learning signal; weights withdrawn for a data-derived metric; protection a floor OUTSIDE the ranking). The reframed analysis is built and committed: report `docs/market_research/POPULATION_LEARNING_FRONTIER_STAGE4.md`; data `population_coverage/{learning_value_model,learning_value_frontier}.json` + `build_learning_frontier.py`. Values-call (a) is now the equal-vs-tilt choice (ASSERTED, sensitivity-tested), not a four-number weight. Awaiting director reaction to the reframed ranking + knee; the generator wiring stays reserved. The old value_frontier.json / value_outcome_model.json remain for the knee-delta only.
>
> **[IN-PROGRESS DISPOSITION — 2026-07-20, value-frontier ANALYSIS COMPLETE; awaiting director on two values-calls + the reserved wiring]**
> **DONE (DISCOVER/FRAME, analysis only, not pushed):** the value-vs-segment-count frontier is built.
> Value knee = **~12 segments** (`price_sensitivity × tenure`, 78% of valuable variance); recommended
> minimum-segment design = **~31 segments** (12-cell commercial core + cross-cutting protected overlay
> → 78.7% variance + 100% critical coverage). Modal-outward and worst-cell-greedy CONVERGE on the
> variance frontier (identical to the knee). The two objectives kept separate — they do NOT co-move
> (finding). Report: `docs/market_research/POPULATION_VALUE_FRONTIER_STAGE4.md`; structure:
> `population_coverage/{value_outcome_model,critical_groups,value_frontier}.json` + `build_value_frontier.py`.
> **AWAITING DIRECTOR (values-calls, proposed ASSERTED, changeable):** (a) the business-value weighting
> [margin 0.40 / retention 0.25 / bad-debt 0.20 / carbon 0.15] and (b) the critical/protected set
> [5 groups]. Confirm or adjust — the frontier rebuilds deterministically from the two sidecar files.
> **STILL-OPEN WALL (what keeps this file in in_progress):** the population-GENERATOR wiring is
> DIRECTOR-RESERVED — proposed in §7 of the report (two derived tags on the existing archetype; no new
> source data), NOT applied. Bring back as **[ACT]**. **Coupled to** the population-coverage/segmentation
> campaign in `in_progress/` — continue there, not as a fresh atom.

# DIRECTOR STEER — Stage 4: the value frontier, and how many segments is enough (2026-07-20)

**Type:** [STEER] — extends the coverage loop from *coverage* to *value*. Method yours.

**First, the coverage result is banked and correct.** The threshold sweep showing the design barely moves between 1.3/1.5/2.0, the off-gas fuel-poor tail staying coupled at every setting, and N=200 as the completeness knee with the three critical cells each covered ×4 — that is a clean result and 1.5 is on the right side. Nothing to revisit there.

## The distinction that opens stage 4

What is built answers **coverage**: does every important cell *appear*. What the director now wants answers **value**: is each segment *worth having*. These are different questions, and the second is the one the director actually posed:

> **"How much valuable variance and critical small groups can we cover with minimum number of segments. So we want both volume of covers and scope of features/complexity."**

This is a **coverage-vs-cost frontier**: maximise what matters, minimise the segments spent. The deliverable is the *curve* — value captured against segment count — and the **knee** of that curve is the answer to "how many segments is enough." N=200 was the *coverage* knee; this asks for the *value* knee, which is not yet built.

## The objective — two things covered, kept deliberately separate

A single blended metric would trade these against each other silently, so keep them explicit:

1. **Valuable variance** — segments whose customers *behave differently in ways that move a business outcome*. A new segment earns its place if its members act distinctly enough to change a decision (pricing, hedging, retention, collections, carbon). This is the volume-weighted half: large groups with genuinely distinct behaviour.
2. **Critical small groups** — the rare cells that matter out of all proportion to their count (fuel-poor off-gas, vulnerable prepayment). These barely register on variance-explained but carry regulatory and mortality weight, and are **protected regardless of size**.

**A segment is justified if it adds material valuable-variance OR captures a critical group.** Build the curve of (variance captured + critical-group coverage) against segment count; report the knee where the next segment buys almost nothing. This directly tests the personalisation thesis's first hypothesis: does value keep rising past coarse cohorts, and where does it stop?

## Two definitions the director must set (everything else is machinery)

These are values-calls, flagged not invented:

- **What makes variance "valuable"** — the outcome(s) the design optimises toward: margin, churn/retention, carbon abated, bad-debt risk, or a weighting across them. Propose a default weighting marked *asserted*; the director will confirm or adjust.
- **What makes a group "critical"** — the protected set that survives regardless of size: vulnerability, regulatory exposure, affordability/mortality risk. Propose the criteria; the director confirms.

Report both as explicit, changeable choices in the committed structure — the same claim-status discipline as the threshold.

## Method notes (candidates, evaluate not adopt)

- Building **from the modal customer outward** (DD, owner-occupier, working smart meter, online, loyal, no debt — the perfect, simplest customer) is a legible way to order the expansion and is naturally nested; the director offered it as an intuition. Whether centre-out expansion or worst-cell-greedy is the better constructor, they should land on the same frontier — use whichever makes the curve and its knee clearest to read.
- **Add each dimension by its TAIL-aware correlation, not aggregate** (the load-bearing stage-2 finding): couple where coupled-in-the-tail (fuel→region), cross only where genuinely independent in the tail. This prevents phantom households in the outer rings.
- Variance attribution across segments is a variance-decomposition / marginal-contribution problem; the fidelity grid's worst-cell scoring already exists and is reusable for the critical-group half.

## The handoff the director reserved

The coverage design is banked; the next step — **building this structure into the population generator** — is the one the director reserved (no silent change to archetype ground truth). This steer authorises the value-frontier *analysis* (DISCOVER/FRAME, doc-and-data). The **generator change itself remains gated**: propose the wiring, show what changes in archetype ground truth, and bring it back before altering the live generator.

**Risk & proportionality:** the frontier analysis is doc-and-data, reversible. The generator wiring is contract-touching and reserved — propose, do not apply. Tag: **narrow/reversible for the analysis; wall for the generator change — bring it back as [ACT].** Report in prose + committed structure per the loop.

— Advisor, carrying the director's steer, 2026-07-20.
