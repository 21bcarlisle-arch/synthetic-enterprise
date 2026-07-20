# DIRECTOR STEER — Un-park the test-throughput regime; scaling customers will re-raise the ceiling (2026-07-20)

**Type:** [STEER] — resume parked work with a sharpened priority. Method yours; the design already exists in `docs/design/TEST_THROUGHPUT_MEASUREMENT_AND_PROPOSAL.md`.

## Why now

The acute fix landed (the two decade-replay tests, 413s → 49s) and is banked. But the *systematic* throughput regime — the one from the 2026-07-19 steer (tier by cadence, run only what a change touches, predictive selection, separate the stochastic test population from the deterministic one) — was **parked in `in_progress/`** when the weekend's continuity fires and the scheduled-worker migration took priority. That was the right call then. It is the wrong place for it now.

The reason it must resume is directly downstream of what the director just commissioned: the **value-frontier and population-generator work heads toward larger, richer populations**. Bigger populations mean heavier simulation and test runs. If the throughput regime stays parked, test time re-becomes the ceiling *exactly as customers scale up* — the precise constraint the director is trying to remove. The two workstreams are coupled: segmentation expands the population; the throughput regime is what keeps that expansion affordable to validate.

## The sharpened priority

Resume the regime, and **prioritise the parts whose benefit scales with population size**, ahead of the parts that don't:

1. **Impact-based / predictive selection** — run the tests a change actually touches, full suite on a cadence. Benefit grows with suite size, which grows with population richness. Highest leverage as customers scale.
2. **The stochastic/deterministic split** — separate the distributional tests (whose variance and runtime both grow with population) from the deterministic ones, so a stochastic run neither wedges a deterministic gate nor drowns failure-prediction in noise. This is the one that specifically bites *because* populations get bigger.
3. **Tier by cadence** — fast checks per commit, full fidelity validation nightly / at level-promotion, using the existing `@pytest.mark.operational` partition as the template.
4. Parallelisation and the cheap structural wins (simulate-once-assert-many, small-world tests for scale-invariant properties) as available.

## Non-negotiables (unchanged from the original steer)

- **Measure before restructuring** — where the time actually goes; the measurement doc already exists, extend it.
- **Prove no safety loss at each step** (R15): a real regression must still be caught under the new regime, demonstrated by mutation. Selection can miss things, so the full suite still runs on a cadence as the net.
- **Do not restructure the gates and the selection logic in one turn** — sequence, own commits, revert path each step.

## Sequencing against the segmentation work

This does not block the value-frontier analysis — run them together. But the throughput regime should land **before** the population generator is actually widened (the reserved generator change), so the larger population arrives into a validation regime that can afford it rather than one that chokes on it.

**Risk & proportionality:** touches the test/CI machinery — blast radius is everything, since every gate depends on it. Incremental, measured, each step proven safe before the next. Tag: **contract-touching — implement with named mitigations; sequence deliberately.**

— Advisor, carrying the director's steer, 2026-07-20.
