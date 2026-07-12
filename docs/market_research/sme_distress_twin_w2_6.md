# W2_6_sme_distress_twin — DISCOVER findings: sector shocks, insolvency, late-payment culture

**Atom:** `W2_6_sme_distress_twin` (epoch 3, `docs/design/maturity_map.yaml`). **Status:** DISCOVER
only per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 — BUILD stays gated (registered "Build in M3").
This atom's own registration named three anchors to verify: Companies House / Insolvency Service
insolvency statistics, late-payment-culture surveys [L], and the "lost supply point, not just a
write-off" mechanism.

## Insolvency incidence and sector concentration — real, current (2026) UK data

- **[L] Company insolvencies are genuinely concentrated by sector, not uniform.** Across the 12
  months to May 2026: construction (17% of insolvencies), wholesale & retail (15%), and
  accommodation & food services (14%) are the three largest categories — together over 45% of all
  UK company insolvencies. This is a real, sourced, quantified anchor for a sector-weighted
  insolvency-hazard model, rather than a flat/uniform hazard rate across all SME customers
  regardless of sector.
- **[L] Insolvency procedure mix is heavily skewed to CVL (Creditors' Voluntary Liquidation):** 76%
  of company insolvencies in a recent month were CVLs, with compulsory liquidation and
  administration far behind. Relevant to this atom's own "insolvency EVENT" concept — most real SME
  insolvencies are a voluntary wind-down, not a court-forced one, which plausibly correlates with a
  longer run-up of visible distress signals (a real detection opportunity for the company's own
  classification logic, echoing this atom's sibling W2_7's "classify under uncertainty" framing)
  rather than a single instantaneous shock.
- **Trend is directional, not flat:** insolvencies fell 16.1% quarter-on-quarter (Q1 2026 to Q2
  2026) in the data found — a reminder that any hazard-rate calibration should be anchored to a
  specific period, not treated as a timeless constant, consistent with this project's own
  baseline/curriculum split (R13): a real historical insolvency rate belongs to the BASELINE
  (calibrated to reality, changes only for fidelity reasons), while a director-chosen STRESS
  scenario (e.g. "elevated insolvency regime") is the CURRICULUM's own instrument.

## Late-payment culture — real, current (2026) UK data, including a live legislative change

- **[L] Late payments cost the UK economy ~£11bn/year and are linked to ~14,000 business closures
  annually** — a real, quantified, sourced causal link between late-payment culture and the
  insolvency-event side of this same atom, i.e. these are not two independent phenomena to model
  separately but a connected causal chain (late payment received BY an SME from ITS OWN customers →
  cash-flow distress → insolvency risk → late payment or default TO this company).
- **[L] Statutory late-payment interest is currently 11.75%** (Bank of England base rate 3.75% + 8
  percentage points, as of mid-2026) — directly anchors the segment T&C overlay this atom's own
  registration flags as a sibling concern (W2_9_segment_debt_tnc: "statutory late-payment interest
  applies" for business accounts, unlike household).
- **Live regulatory change, not stable background:** a Bill introduced in the House of Lords
  (19 May 2026) would impose a statutory 60-day payment-terms cap on B2B contracts (large buyer /
  smaller supplier) and make statutory interest mandatory (removing the current ability to
  contractually opt out of it), with enforcement/fines tied to a Small Business Commissioner
  register of persistent late payers. Not yet in force (no implementation date, "no earlier than
  2027") — but a genuine, live, in-motion regulatory fact relevant to how this atom's own T&C
  overlay might need to change if/when this atom is built, not a stable assumption to hardcode.

## "Lost supply point, not just a write-off" — mechanism confirmed, real UK practice

Searched specifically for what happens to the METER POINT (not just the debt) when a business
customer becomes insolvent and vacates premises — the registration's own claimed distinction from a
household default. Confirmed a real, distinct mechanism (NB: most search results address the
different scenario of the SUPPLIER going bust — Supplier of Last Resort / deemed contracts — a
separate real UK mechanism this project should not conflate with the customer-side event this atom
is about):

- **[L] When a tenant business vacates (including via insolvency), UK practice places energy
  account liability on the LANDLORD, not the departed tenant**, for the vacant period — standing
  charges continue to accrue against the landlord even with zero consumption. This is the concrete
  real-world shape of "a lost supply point, not just a write-off": the company's real loss is not
  only the unpaid balance from the insolvent tenant, but the loss of that customer relationship
  entirely (a new occupier, if any, is a fresh acquisition decision, not a continuation) — while the
  METER itself does not simply go dark, it transfers to a different (and often less profitable —
  vacant-standing-charge-only) counterparty until re-let.

## Named next step (FRAME, not built here)

The concrete next FRAME question this DISCOVER pass surfaces: does this atom's own hazard model need
a THIRD hidden state beyond "still trading" and "insolvent/departed" — namely "vacant, landlord-
liable" — to correctly represent the real churn/loss shape found above, rather than a simple
binary insolvency flag? Not resolved here — a real sizing question for the next FRAME pass once
epoch sequencing opens this atom.

## Honest open items (R10)

- No UK-specific SME energy-account bad-debt WRITE-OFF RATE (as opposed to general insolvency
  incidence) was found in this pass — the two are related but distinct numbers, and only the
  general insolvency/sector data above was sourced with confidence.
- The precise quantitative overlap between "late payment received" and "eventual insolvency" (i.e.
  what fraction of the ~14,000 annual closures were this project's own kind of customer, an SME
  energy account) was not found and is not asserted here — the £11bn/14,000 figures are UK-economy-
  wide, not energy-sector-specific.
