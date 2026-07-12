# W2_4_household_budget — DISCOVER findings: anchoring the hidden budget state

**Atom:** `W2_4_household_budget` (epoch 3, `docs/design/maturity_map.yaml`). **Status:** DISCOVER
only per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 — BUILD stays gated (registered "Build in M3
with the population draw"). This atom names five hidden-state components to anchor: income band,
essential-cost floor, discretionary margin, savings buffer, priority-of-debts stack.

## Income band / discretionary margin — real, current (2026) UK data

- **[L] Median UK household disposable income (2026): ~£3,225/month (~£38,700/year gross).** A real
  anchor for the centre of the income-band distribution this atom needs.
- **[L] The aggregate "average household has £261/month left after essentials" figure MASKS real
  distributional structure: the bottom 20% of earners face essential expenditure EXCEEDING income
  by £71/month** (a genuinely NEGATIVE discretionary margin, not just a thin one), while middle-
  income households saw small real-terms improvement. This is a critical anchor for this atom's own
  "discretionary margin" concept: the shape must be able to represent a bottom decile/quintile that
  is structurally negative BEFORE any energy price shock is even applied, not merely "low margin" —
  matching this atom's own stated purpose ("arrears are the OUTPUT of a household budget meeting a
  price shock", per the adjudicated finding this atom exists to fix).

## Essential-cost floor — real, current (2026/27), quantified, with a real policy gap already built in

- **[L] JRF/Trussell's "Essentials Guarantee" research quantifies the essential-cost floor directly
  for 2026/27: a single adult needs at least £120/week, a couple £205/week**, covering food,
  clothing, and household bills — this is a real, current, directly-usable anchor for this atom's
  own "essential-cost floor" component, not an abstract concept needing a fresh estimate.
- **[L] From April 2026, Universal Credit's standard allowance (£98/week single, £154/week couple)
  sits BELOW that floor by £22/week (single) and £51/week (couple).** This is a decisive, real,
  quantified finding for the model: a materially-sized real UK population (UC claimants) lives with
  a STRUCTURAL, POLICY-DRIVEN shortfall against the essential-cost floor — i.e. for a real slice of
  the population the "essential-cost floor" is not merely close to income, income is already known
  to sit below it, independent of any energy shock. This should inform how the income-band/
  essential-cost-floor joint distribution is shaped (a genuine floor-vs-income overlap in the lower
  bands, not an assumption that essentials are always affordable in the base case).

## Priority-of-debts stack — a real discrepancy found, not just confirmed (important, not glossed over)

This atom's own registration text asserts an ordering: *"rent/mortgage, council tax, food before
energy"* (i.e. energy ranked LOWER than those four). Checked this directly against real debt-advice
sector guidance (Citizens Advice, StepChange) rather than assuming it — **and found this specific
ordering claim is not well supported as stated**:

- **[L] Citizens Advice / StepChange's own priority-vs-non-priority framework classifies energy debt
  WITH rent/mortgage, council tax, and HMRC debt as a PRIORITY debt — specifically because of
  disconnection risk** (the same class of severe consequence — losing your home, going to prison,
  losing an essential supply — that defines the priority tier), NOT a lower-ranked item paid only
  after those four are covered. Non-priority debts (credit cards, personal loans, other unsecured
  credit) are the ones explicitly described as lower-consequence and dealt with only once priority
  debts are under control.
- **What real guidance does NOT resolve (and this pass did not find further)**: a precise SECONDARY
  ordering WITHIN the priority tier itself (e.g. does a real household actually pay rent before
  energy when both are priority and money is short, or does the shorter disconnection timeline for
  energy make it go first in practice?) — the sources found describe the priority/non-priority
  SPLIT clearly but not a strict within-tier ranking.
- **Implication for the eventual build:** the atom's own registered ordering text should not be
  encoded as-is without revisiting this — "food before energy" in particular has no clear support
  found here (food is not itself a "debt" in the priority/non-priority framework at all, since there
  is no creditor relationship for future food purchases the way there is for rent/energy/council
  tax; food is better modelled as ongoing essential SPENDING competing for the same discretionary
  pool, not a debt-stack entry). This is a real, precise correction for the next FRAME pass, not
  asserted as already fixed here (no code/ordering has been built).

## Honest open items (R10)

- No precise within-priority-tier secondary ordering (rent vs energy vs council tax, when all three
  are simultaneously in arrears and money is genuinely insufficient for all) was found — a real gap
  for a more targeted search or an explicit director-set curriculum assumption (R13) if no further
  real anchor is found.
- The savings-buffer component (of the five named) was not separately anchored in this pass — no
  targeted search was run for UK household savings/buffer statistics by income band; registered here
  as a genuine remaining gap for the next DISCOVER pass on this atom, not silently skipped.
