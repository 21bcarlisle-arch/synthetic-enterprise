# W2_7_willingness_classification — DISCOVER findings: anchoring willingness incidence

**Atom:** `W2_7_willingness_classification` (epoch 3, `docs/design/maturity_map.yaml`). **Status:**
DISCOVER only, per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 — BUILD stays gated pending epoch
sequencing (this atom is also epoch 3, not yet current). Its own registration explicitly asked for
this: *"Anchor willingness incidence to Ofgem debt research / industry sources where possible — tag
[L] and VERIFY before encoding."*

## Headline finding: the "can't pay, won't pay" framing itself is a live, contested political issue

This is not a settled, neutral classification question in the real UK energy sector right now — it
is an active controversy directly relevant to how this atom's own hidden-truth generator should be
anchored:

- **[L] Ofgem's interim chief executive was publicly criticised (Utility Week, 2026) for using a
  "can't pay, won't pay" framing of energy debt customers**, which the End Fuel Poverty coalition
  called "reductive" and disputed on the evidence.
- **[L] The End Fuel Poverty Coalition's own explicit framing: "it's a can't pay crisis, not a won't
  pay one"** — i.e., real UK fuel-poverty advocacy takes the position that the WILLINGNESS quadrant
  (won't-pay despite ability) is comparatively rare, and that the dominant real driver of energy debt
  is ability (can't-pay), not attitude.

**Implication for this atom's eventual build:** the willingness-incidence rate should NOT be
anchored to a naive/arbitrary split (e.g. 50/50, or any assumption that "won't pay" is a large,
stable minority) — real UK debt-advocacy evidence and regulatory framing both point toward can't-pay
being the dominant quadrant. Building this atom with an inflated won't-pay incidence would
misrepresent the real population this project claims to model, and would itself be politically
loaded in a way the real regulator is currently being challenged on.

## Quantified anchor found (real, sourced, but from a self-selected population — caveat below)

- **[L] StepChange client data, H1 2024: 41% of StepChange clients responsible for paying energy
  bills had arrears; of that group, 47% had a "negative budget"** (monthly income insufficient to
  cover basic monthly costs) — a real, sourced, quantified signal that a large share of energy-debt
  cases among people already seeking debt advice are genuinely ability-constrained, not attitudinal.
- **Honest caveat, not glossed over:** StepChange's own client base is self-selected (people who
  sought debt-charity help), which skews toward higher-need populations than the general customer
  base this project's own population draws model. This 47% figure anchors "ability-constrained
  incidence within an already-distressed sub-population," not "ability-constrained incidence across
  the whole customer base" — a materially different (larger) denominator this atom's own SIM-side
  population draw would need to model. Do not encode 47% as a whole-population willingness-classifier
  parameter without this adjustment.

## Regulatory framework confirms the real-world stakes (already partially known, reconfirmed)

- **SLC 27.8** (Standard Licence Conditions, confirmed via WebSearch) requires suppliers to accept
  repayment at an affordable rate and to assess ability-to-pay — the real regulatory mechanism this
  atom's own "mis-classification physics" (can't-pay treated as won't-pay = customer harm +
  compliance breach) directly models.
- **Ofgem's 2025 Debt Relief Scheme** (OFG1164, live/current policy work, not historical) is Ofgem's
  own current attempt to standardise ability-to-pay assessment across suppliers — direct evidence
  this is a live, unresolved regulatory problem space, not a solved one, reinforcing the atom's own
  framing that the company must classify under genuine uncertainty.

## What this does NOT yet resolve (honest, open items — R10)

- **No precise, quotable numeric split for "genuine won't-pay incidence" was found** in this pass —
  searched specifically for a StepChange/Citizens Advice report giving a direct percentage
  comparison and did not locate one. This remains a real, named gap for the eventual BUILD/FRAME
  pass to either find (a more targeted literature search, or a direct read of StepChange's "Plugging
  the Gap" report in full) or explicitly acknowledge as un-anchorable to a precise external number,
  requiring a director-set assumption instead (matching R13's curriculum-is-the-director's-instrument
  principle if no real anchor exists).
- The whole-population (not self-selected/distressed-only) willingness incidence rate is not
  directly evidenced by anything found this pass — the StepChange figure anchors a sub-population,
  as noted above.
