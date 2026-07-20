# Carbon three-ledger — DISCOVER pass (E5, doc-only) — 2026-07-20

**Status:** DISCOVER, doc-only. Provenance: proposal. No level claimed. Writes no code, edits no
engine. The atom is `E5_carbon_three_ledger` (lane E_finance_treasury). This surfaces the design +
the **director values-calls** the build will face; it decides none of them.

**Why this exists.** `PURPOSE_PITCH_V4.md` §9 makes carbon abatement through personalisation the
company's mission, measured as **£ per tonne of CO₂e** = (cost to serve + cost to persuade, incl.
compute) ÷ carbon abated. The Note on Claims states plainly this is **designed, not built**: no
carbon ledger, no per-household cost-and-carbon trajectory, no £/tCO₂e computation exists today. This
is the largest new build the ratified purpose implies.

## 0. The binding wall (non-negotiable, precedes all design)

Everything below is bound by **`CARBON_NOT_A_TARGET_CONSTRAINT.md`**: £/tCO₂e and every metric derived
from it is a **DIAGNOSTIC**. It may be measured, reported, inspected — never **optimised**. The build's
DoD carries a mechanised guard (grep-guard test, raw-send-keys shape): no carbon metric is imported by
the fitness function, the atom draw, the risk committee, or any pricing/personalisation reward path.
An unavailable/zero carbon reading fails **LOUD** (fail-open doctrine), never reads as "great". The
£273/tCO₂e (2025, 2022 prices, ±50%) UK appraisal value is an **external-benchmark sanity band** (R12),
never a goal to hit. *This is the same law as LAW A / R12 — carbon being the mission makes it live.*

## 1. The three ledgers (a carbon P&L — a claim that counts one side is not a claim)

| Ledger | What it records | Basis / clock |
|---|---|---|
| **SAVED** (customer) | CO₂e a household would have emitted but did not, *because of* an intervention | counterfactual per household (§2) |
| **SPENT** (operational) | CO₂e emitted serving them: people, **compute, tokens** (ties the near-zero-marginal-cost claim + the token sensor, `RESOURCE_AWARE_SCHEDULING`) | activity-based, per period |
| **NET** | SAVED − SPENT, **always reported** | the honest headline |

Data model (behind the event-log interface, C-S4): an append-only `carbon_event` stream —
`{household_id | operational_source, tco2e, basis, provenance, as_of}` — from which SAVED/SPENT/NET
and £/tCO₂e are *derived views* (never stored scalars that can drift; same discipline as the R14
clocks and the fidelity evidence ledger). Idempotent + replayable (C-S2); event-arrival tolerant (C-S1).

## 2. The hard part — "carbon SAVED" is a COUNTERFACTUAL, and the method is a director choice

You cannot observe carbon a household *didn't* emit. SAVED is the gap between two trajectories: what
they emitted, vs what they'd have emitted absent the intervention. Method options (the build must pick
one, and this is a **DIRECTOR VALUES-CALL** — it defines what "abated" *means*):

- **(A) Same-household CRN A/B** — run the simulated household twice under common random numbers, once
  contacted, once not; the delta is the isolated causal effect. *Cleanest causally (it's exactly the
  fidelity-ablation discipline), but in-simulation only — proves the mechanism, not a real tonne (§13
  "any real tonne abated is NOT proven").* **Recommended default for the SIM.**
- **(B) Baseline-trajectory** — each household's pre-intervention cost-and-carbon path (the
  personalisation trajectory, itself unbuilt) as the counterfactual. *Cheaper, but the baseline is a
  model, and attribution to the intervention is weaker.*
- **(C) Population matched-control** — compare to similar un-contacted households. *Needs the business/
  scale population; confounded at small N.*

**Surfaced, not decided:** which counterfactual defines "abated"; the emissions factor set (gCO₂e/kWh —
grid marginal vs average, time-of-use, the SAVED accounting boundary); whether behaviour-persistence
decays the SAVED claim over time. All are director-facing (they define the mission metric), none is
the agent's to set — same rule as the A/D/G values-calls and R13 curriculum.

## 3. Dependencies + DISCOVER-vs-BUILD split

- **Depends on** the per-household **cost-and-carbon trajectory** (personalisation §7, also unbuilt —
  flagged "designed, not yet instrumented" on The Company). SPENT depends on the **token/compute
  sensor** (`RESOURCE_AWARE_SCHEDULING` step-zero done: sensor available at CC 2.1.215).
- **DISCOVER/FRAME workable now** (this doc + follow-ons): the event schema, the read-only-wall test
  shape, the emissions-factor register (anchored to a real published source, R10 for any asserted
  factor), the counterfactual method comparison.
- **BUILD is director-prioritised** (`blocked_on: director_build_open`): it is mission-core + values-
  adjacent (Epoch-4 fitness inclusion is a cat-6 director call), and gated behind the trajectory build.

## 4. What the site shows once built (already scaffolded honestly)
The Company's Personalisation section already states the trajectory + £/tCO₂e are *designed, not
instrumented*, cross-linking The Proof's "what we have not proven". When E5 builds, those become live
three-ledger views (Company + a carbon strand on World), each figure carrying its claim-status
(observed / not-yet-instrumented) per the constitution's rule 6. No number is published before it is
real (R11).
