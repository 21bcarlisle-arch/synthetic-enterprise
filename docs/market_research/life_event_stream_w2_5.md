# W2_5_life_event_stream — DISCOVER findings: anchoring real UK life-event incidence

**Atom:** `W2_5_life_event_stream` (epoch 3, `docs/design/maturity_map.yaml`). **Status:** DISCOVER
only per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 — BUILD stays gated (registered "Build in M3
with the population draw"). Named events: job loss, illness, divorce, retirement, new child.

## Real, current (2026) UK anchors found for each named event

- **Job loss / unemployment.** [L] UK unemployment rate 4.9% (Feb-Apr 2026), 1.76 million people
  unemployed, up 124,000 over the year. Separately, **9.14 million people aged 16-64 are
  economically inactive (21.0% inactivity rate)**, with ONS publishing a distinct experimental
  breakdown specifically for long-term sickness as a cause of inactivity — i.e. real UK data
  already distinguishes "unemployed and job-seeking" from "economically inactive due to illness"
  as two DIFFERENT flows, not one generic "lost income" event. This atom's own event taxonomy should
  likely keep job-loss and illness as genuinely distinct hidden-state transitions (different
  recovery dynamics, different real incidence bases) rather than merging them.
- **Illness / long-term sickness.** Covered by the same ONS economic-inactivity data above — a real,
  named, separately-tracked UK statistical category (not a residual "other" bucket), reinforcing it
  deserves its own real incidence anchor rather than being folded into unemployment.
- **Divorce.** [L] 102,678 divorces in England & Wales in 2023 (a real, current, "return to
  pre-pandemic levels" figure per ONS) — a real annual-count anchor. Converting to a per-household
  annual hazard rate for this atom's own population would need the matching married-household
  denominator (not sourced in this pass — see honest gaps below).
- **New child.** [L] Total fertility rate 1.41 children per woman (2024, England & Wales) — the
  THIRD consecutive record-low year. This is directly relevant to sizing this event's real incidence
  AND to the direction of travel: a real, current, ongoing DECLINE, not a stable historical constant
  — worth flagging for whichever period (BASELINE vs CURRICULUM, R13) this atom's incidence rates
  are ultimately anchored to.
- **Retirement.** ONS publishes real State Pension age population/flow statistics, but the specific
  datasets surfaced in this pass only went up to 2021 in their public summary — a genuine gap (see
  below), not filled by assumption.

## Shared-generator implication (confirmed, not new — cross-checked against the registration)

The registration's own "ONE event generator serving BOTH the payment-difficulty triggers AND
C5_key_moment_conversion's adoption-journey windows" design is reinforced by this pass's own finding
above: real UK statistical practice already treats these as genuinely distinct, separately-measured
event categories with different real incidence rates and trends (unemployment declining/rising
independently of fertility's own multi-year decline, for instance) — supporting a shared EVENT-BUS
architecture (one substrate, many named event types) over either a single blended "distress score"
or duplicate separate generators per consumer.

## Honest open items (R10)

- **No per-household annual HAZARD RATE was derived for any of the five events in this pass** — the
  real ONS figures found are either economy-wide stocks/flows (unemployment, inactivity) or absolute
  annual counts (divorces, births) requiring a matching denominator (households, married couples,
  women of childbearing age) this pass did not source. Converting these into per-customer/per-run
  probabilities is real, unstarted FRAME/BUILD work, not implied by the raw figures found here.
- **Retirement flow data was the least resolved anchor** — ONS confirmed to publish it, but the
  specific dataset surfaced in this pass only covers historical years up to 2021; a more targeted
  search (or a direct ONS dataset pull) is needed for a current figure before this event is sized.
- No UK-specific research was found in this pass connecting these life events QUANTITATIVELY to
  energy-bill payment difficulty specifically (as opposed to general financial distress) — the
  causal link is asserted by this atom's own registration and by real-world plausibility, not
  independently sourced with a number here.
