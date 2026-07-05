[SIM] BEHAVIOURAL ECONOMICS & NUDGE LAYER -- research-first directive. Queue in backlog behind the design wave; do not interrupt current threads.

RICH'S BRIEF: research behavioural economics and nudge theory and add it to the SIM -- how the supplier can persuade people, EVEN IF IT DOESN'T KNOW IT.

STEP 1 -- RESEARCH NOTE (Tier 3, docs/design/BEHAVIOURAL_LAYER.md): survey the literature with an ENERGY-SPECIFIC and UK lens, and propose the model. Cover at minimum:
- Default effects & status quo bias (auto-rollover vs opt-in; the SVT inertia / loyalty-penalty story IS a default effect)
- Loss aversion & framing ("you are losing GBPx" vs "save GBPx" in renewal/retention comms)
- Social norms (Opower/HER neighbour-comparison: ~1.5-2% consumption effect, well published -- a calibration anchor)
- Present bias (upfront discount vs long-run saving in offer design)
- Friction & sludge (switching friction, exit friction -- and its regulatory limits)
- Salience & timing (bill-shock salience, reminder timing, channel effects)
- Choice overload (tariff menu size -- Ofgem's tariff-simplification history is the natural experiment)
- Anchoring in price presentation
UK CALIBRATION ANCHORS: published trial effect sizes only -- Opower HERs, Ofgem/CMA collective-switch trials (~20%+ switching vs low-single-digit control), loyalty-penalty findings, pension auto-enrolment as the default-effect benchmark. Population-anchoring discipline applies: susceptibility distributions must reproduce published aggregate effects.

STEP 2 -- THE MODEL (implement after design review):
- SIM side: per-customer HIDDEN susceptibility parameters (default-following, loss-aversion weight, social-norm responsiveness, present bias, friction tolerance) joining the behavioural dimension; they modulate journey-stage transitions (in-market entry, offer acceptance, consumption response).
- COMPANY side: interventions gain FRAMING/CHANNEL/TIMING attributes (an offer is no longer just a price -- it is a price + a frame + a moment). The company NEVER sees susceptibilities.
- THE POINT: the decision loop's counterfactual lift measurement discovers what persuades empirically -- the company learns nudges without knowing the theory. Emergent behavioural science as a headline discovery when it happens.
- ETHICS/REGULATORY GUARDRAIL: model sludge honestly in the world, but company-side use respects SLC fair-marketing constraints -- and make dark-pattern-vs-legitimate-nudge an explicit flag on interventions, because that boundary is itself worth simulating (Ofgem watches it in reality).

EVIDENCE RULE: a worked case on the surfaces -- same offer, two frames, measured lift difference, both sides of the wall (true susceptibility vs company's inferred response rate).
