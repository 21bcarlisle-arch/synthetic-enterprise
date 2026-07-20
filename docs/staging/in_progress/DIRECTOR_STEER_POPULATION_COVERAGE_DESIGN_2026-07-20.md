> **[PARKED — in_progress, learning loop, 2026-07-20]** Stage 1 (source landscape) COMPLETE and
> committed: `docs/market_research/POPULATION_COVERAGE_SOURCE_LANDSCAPE.md`.
> **Open sub-item blocking stage 2:** the FETCH stage needs (a) a network-capable session and (b) a
> director/advisor steer on §5 — how hard to push statistical fusion for the high-value D×(A/B/E) tails
> vs conservatively crossing them. Autonomous ticks have no network, so stage 2 does not auto-proceed.
> **Unblocks when:** either the director/advisor replies to §5, or an interactive/network session runs
> the stage-2 fetch plan (§7.1). Not a wall — a stage boundary in a deliberately staged loop.

---

# DIRECTOR STEER — Population coverage design: which N households span the space (2026-07-20)

**Type:** [STEER] — DISCOVER work, run as a **collaborative learning loop with the director and advisor**, not a one-shot spec. The brief will be refined as we all learn. Mechanism and method yours.

---

## The question (director's framing — this is the prescriptive question, not the descriptive one)

Not *"what cohorts exist in the data"* (clustering). The question is:

> **"Analysing the big data sets to work out the 100 customers that give us maximum feature build. And then 200, 500, 1000 etc. Covering the key dimensions. Where there is no correlation you can cover without spiralling size and complexity. This is really really important to figure out. It's at the heart of it."**

This is **experimental design**, not descriptive statistics: choose a small population that *spans* the factor space, rather than one that mirrors the national distribution. A random sample of 100 UK households yields eighty variations on the same house and misses every prepayment fuel-poor all-electric flat — which is where the money and the mortality live.

## Why the director's instinct about correlation is the crux

Where dimensions are genuinely orthogonal you must cross them; where they are correlated the effective space is far smaller. So **the joint structure must be estimated before the design can be built** — that is the whole game, and it is why this is discovery work first.

Relevant mature mathematics, offered as candidates to evaluate and improve, not as a specification: fractional-factorial and orthogonal-array designs (if the requirement is that every *pair* of factor levels appears rather than every full combination, required N grows roughly **logarithmically** in the number of factors rather than exponentially); covering arrays and pairwise/t-wise coverage; space-filling designs (Latin hypercube, maximin) for continuous dimensions; and D/A-optimal design where a model form is assumed. See also `docs/design/ADVISOR_IDEAS_CROSS_DISCIPLINE_2026-07-18.md` §D2 and §C5.

## Requirements

**1. Source landscape first.** Document which real datasets carry which dimensions, what each contains, licensing, and whether it is open-download or application-gated. The dimensions the director named: house type and fabric, heating system, tenure, EV ownership, PV, battery, socio-demographics — then attitudes: price sensitivity, channel preference, green/environmental stance, smart-meter attitude, and trust or satisfaction with energy suppliers. Note honestly where a dimension has *no* good open source; that is itself a finding.

**2. Fetch what is openly available.** You have network access and a working fetch pipeline (as used for AGWS). Cache raw data on the box.

**3. Commit STRUCTURE, not microdata.** Raw datasets stay out of the repo. Commit the **joint structure** in readable, reviewable form: marginals per dimension, pairwise cross-tabs, correlation/association matrices (with the right measure for categorical pairs), and a plain-language note on what is genuinely orthogonal versus what is strongly coupled. **This is what the director and advisor will read and reason over — make it legible, not just machine-usable.**

**4. Then the coverage design.** Given the estimated joint structure, construct populations at N = 100, 200, 500, 1000 that maximise coverage of the space. Two properties the director's framing requires:
   - **NESTED** — each population contains the previous one. This makes every increment a controlled experiment (same seeds, same weather, only coverage added), so the marginal fidelity and business value of each extra 100 households is *measurable* rather than assumed. Independently-optimal designs at each size would forfeit that.
   - **Scored on the WORST CELL, not the average** — coverage means the least-covered combination that matters, not mean representativeness. This is the same discipline as the fidelity grid.

**5. Report the marginal gain of each increment**, so growth is justified by evidence rather than appetite. This directly tests the personalisation thesis's first hypothesis: does value keep rising past coarse cohorts?

## How this is run — a learning loop, deliberately

The director wants to be **involved and to learn as this develops**, and to refine the brief as understanding improves. So: report findings in **readable prose plus committed structure** as you go — after the source landscape, after the joint-structure estimation, and after the first design — rather than delivering a finished answer. Expect the brief to change between stages; that is intended, not churn.

**Ownership stays yours.** The advisor will read the committed structure, reason over it, and may propose design approaches — treat those as hypotheses to test or refute, exactly as with the cascade. Where you judge an approach above to be wrong or a better method exists, say so with reasoning.

## Boundaries

- **Independence rule holds:** generation anchors and validation anchors from disjoint sources; the company never validates discovered cohorts against SIM ground truth.
- **Traits first.** The state layer (timing, events, salience) is a later track — traits set the distribution that states move within. Do not conflate.
- **No personal data.** Aggregates, published statistics and open datasets only; if a source requires an application or carries personal data, flag it and stop — the pitch's public honesty claims depend on this being true.

**Risk & proportionality:** DISCOVER work, doc-and-data only, no changes to the live population generator. It is upstream of the population model, so it must NOT silently alter existing archetype ground truth mid-campaign — propose before any generator change. Tag: **narrow/reversible for the discovery; contract-touching for any later generator change.**

— Advisor, carrying the director's steer, 2026-07-20.
