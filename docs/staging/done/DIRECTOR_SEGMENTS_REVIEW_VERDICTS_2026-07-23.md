# Director segments-review verdicts — coupling hypotheses, prepayment estate, two new atoms (2026-07-23)

**Provenance.** Advisor-staged on the director's explicit verdict in live review, 2026-07-23. Follow-on to
`DIRECTOR_STEER_TRIANGULATION_SITE_SEGMENTATION_2026-07-22.md`, `SEGMENTATION_RECONCILIATION_FRAME.md`,
`BOARD_SPEC_006_RECONCILIATION.md`, and the population_coverage artefacts. Doc-only trigger; the builds it
seeds live inside already-authorized programmes.

**Proportionality.** Register/requirement changes = implement with named mitigations. Nothing here opens a
new wall or changes safety controls. The generator BUILD remains under its existing authorization
(propose-then-proceed, 2-hour veto).

**Sequencing constraint (the reason this batch exists now).** The cohort-generator BUILD is open. Every
coupling below changes what the population draw should generate. These must land in the fusion/hypothesis
register BEFORE the draw is wired, or they become retrofits against a shipped draw — the stale-dependent
breakage class. Treat §1 as blocking input to generator wiring; §2 as a requirement on the same build; §3
as non-blocking atoms.

---

## 1. DECIDED — register these coupling hypotheses (fusion register, with refutation conditions)

The director's practitioner model asserts joint structure the current draw crosses independently. Each
entry below is a HYPOTHESIS with a named evidence route — not a ratified marginal. **No coupling strengths
are set in this doc.** Where a strength has no external anchor, it is an R13 curriculum dial and waits for
the director's values batch. You design the register-entry form; requirements per entry: statement,
direction, evidence anchor, refutation condition, status (hypothesised → anchored/recoupled → refuted).

1. **cars × EV adoption** (driveway/off-street-parking agency). Sibling of the already-recoupled
   tenure×adoption entry — same class: an agency gate on low-carbon adoption. Off-street parking is one of
   the strongest real-world EV-adoption predictors. Evidence route: DESNZ/DfT EV uptake and charging
   surveys carry tenure/parking splits — discovery pass before any hand-set value. Note the frontier
   finding stands unchanged: cars earns ~zero marginal learning value AS AN AXIS; this entry is generative
   coupling, not a segmentation dimension. Both are true; do not let this entry re-admit cars to the axis
   set.
2. **engagement × price_sensitivity** (the director's high/low-elasticity versions of the same
   structural bundle). Currently drawn independent. No external cross-tab is known → strength is R13,
   director-reserved. Register the hypothesis and the seam it must respect: stock (current tariff state)
   vs disposition (switching propensity) per `ENGAGEMENT_MIX_RECONCILIATION_2026-07-22.md` §0.
3. **payment-method × structural block** (tenure/nssec/affordability). DD share is not uniform across the
   observed spine. Evidence route: Ofgem RMI payment-method splits and English Housing Survey. Becomes
   load-bearing the moment the prepayment estate (§2) exists.
4. **engagement U-shape by affluence** (older/poorer/less-educated disengage; the very-well-off also
   disengage; engagement peaks in the middle). A non-monotonic claim a naive monotone draw would miss.
   Evidence route: Ofgem Consumer Engagement Survey / DESNZ attitude tracker demographic splits —
   discovery pass BEFORE hand-setting. If the U is anchored, it constrains entry 2. Note the age gap:
   the schema carries no age axis; this entry names age's first concrete consuming mechanism (contact
   load + engagement shape). Whether age is admitted as a dimension remains a generator-side ask for the
   director — do not add it unilaterally.

## 2. DECIDED — prepayment estate requirement (sharpens the known #1 coverage gap)

Spec 006 finding stands: richest company-side payment machinery, no drawn PPM estate to meet it
(draw stamps binary `direct_debit|other`; `high_needs_prepay_proxy` is simultaneously the
highest-consequence critical group, mean 3.08, top-decile share .562). When the estate is drawn, the
director's requirement is that it contain AT MINIMUM two sub-populations with OPPOSITE payment
reliability:

- **Debt-mandated PPM** — arrived via arrears pathway; elevated default/self-disconnection risk; maps to
  the existing company-side `PaymentMethodSource.DEBT_MANDATED`.
- **Choice PPM / cash-cheque budget-controllers** — pay regularly and consistently; chose prepay for
  control of incomings/outgoings; NOT a distress population. A build that stamps all PPM as distressed is
  wrong and would be refuted by this requirement.

Both sub-populations carry elevated contact propensity (prepay calls a lot — practitioner anchor, and it
is consistent with the assisted/phone channel skew already in critical_groups). Mechanism design is
yours; sub-population shares are R13 unless an Ofgem/EHS anchor is found first (discovery preferred).

## 3. DECIDED — author two DISCOVER atoms in the map (non-blocking, loop self-draws)

1. **Change-of-tenancy debt physics.** Home-move exists as churn/acquisition mechanics
   (`home_move_win_rate.py`, churn_journey, customer_events). What is NOT confirmed built: the debt and
   revenue physics OF the move itself — move-out final-bill non-payment risk, move-in landing on deemed
   rates, the void-property problem (Spec 006 #9 PARTIAL). Director's frame, register verbatim: every
   tenancy change is **one credit-risk exit plus two deemed-rate entries** ("double jeopardy"), and
   simultaneously the prime acquisition moment for high-value low-churn customers. The atom unifies three
   things currently held separately: acquisition (thin), deemed tariff path (built), bad debt (built).
   Touches billing/lifecycle process model, not the population draw — does not block generator wiring.
2. **occupancy → consumption volume and shape.** Occupancy archetypes currently drive complaint
   propensity only; two extra people in a house changes how often they call, not what they use. The atom:
   wire occupancy (people count, adults vs children where anchorable) into demand volume and shape,
   alongside the director's causal sketch — hours-at-home, cooking fuel, overnight device load — as
   candidate shape drivers. Natural home: the held HH load-shape clustering lane; fold, don't duplicate.

## 4. OPEN — explicitly NOT decided here

- **Engagement mix number and regime question** (static constant vs regime-varying dial): R13,
  director-reserved. The reconciliation doc's proposal is with the director; the verdict rides in his next
  R13 batch. Do not set or change any share meanwhile.
- **All coupling strengths without external anchors** (entries 2, partially 4; PPM shares in §2 absent an
  anchor): R13 batch.
- **Age as a schema dimension**: named, not admitted.
- **Decision-linkage gate on the frontier metric** (board Child-test fold-in): values-adjacent. **[CORRECTED
  2026-07-23, DIRECTOR_RULING_DECISION_LINKAGE_PRECEDENCE_2026-07-23]** — this "awaits ratification separately"
  line was a parallel-session context gap: the director already RATIFIED this gate as CHOSEN by console on
  2026-07-22 (`decision_log.jsonl:53`, frame §2.4). The 2026-07-22 ratification STANDS; it was not withdrawn.
  Do not un-wire, hold, or re-park. (Only mechanisation in `build_learning_frontier.py` remains — candidate
  BUILD atom `SPEC006_decision_linkage_metric`, still gated as a follow-on.)

## 5. Risk

- **Touches:** fusion/hypothesis register (doc/design), generator build plan inputs, maturity map (two
  new DISCOVER atoms). No sim/company/saas/site code changes are authorized by this doc itself.
- **Blast radius:** generator wiring consumes §1–§2; mis-sequencing risk is the draw shipping before the
  register entries exist. Mitigation: treat §1/§2 as blocking input to the draw-wiring step specifically,
  not to the rest of the generator build.
- **Probable failure mode:** coupling hypotheses read as ratified marginals and hand-set strengths appear
  without R13. Mitigation: every entry carries status=hypothesised and an empty strength field until
  either an external anchor lands (cite it) or the director's R13 batch sets it.
- **Second failure mode:** cars×EV entry re-admits cars as a segmentation axis. Mitigation: entry text
  above states the frontier finding explicitly; keep it in the register, out of the axis set.

*Verdicts above are the director's, given in live review 2026-07-23. Interrogate the evidence routes
freely; if a discovery pass contradicts a hypothesis, that is the register working — report, don't
suppress.*
