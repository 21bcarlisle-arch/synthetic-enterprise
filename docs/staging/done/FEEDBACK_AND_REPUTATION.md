[SIM + SUPPLIER] Customer feedback instrument + public reputation layer -- Rich's directive. Completes the satisfaction architecture with the two missing halves: measurement and reputation.

CONTEXT: SIM-side satisfaction ground truth exists (accumulator, complaints anchored to Ofgem, service events). Missing: (1) the company's MEASUREMENT INSTRUMENT -- real companies never see satisfaction, only solicited feedback; (2) PUBLIC REPUTATION -- the channel through which service quality compounds into acquisition cost and churn. CTO guidance's "reputational gravity" concept, now built. Part of the PROCESS_NOT_EVENTS family; queue behind current threads (churn journey, decision loop, design system) -- do not interrupt them.

LAYER 1 -- SOLICITED FEEDBACK (the company's biased instrument):
- Post-service-event CSAT surveys: after contacts, complaints, home moves, onboarding -- sent per company policy, answered per SIM behaviour with REALISTIC response rates (single-digit-to-low-tens %) and U-SHAPED RESPONSE BIAS (very dissatisfied and very satisfied respond; the middle is silent). Response propensity modulated by emotional state / income stress (the overwhelmed do not answer surveys).
- Periodic NPS campaign: company-run, quarterly, same bias physics; feeds the existing nps_tracker as its actual data source.
- EPISTEMIC RULE: company-side satisfaction metrics (service quality, CSAT, NPS) must derive ONLY from survey responses + complaints + contact outcomes -- never from SIM satisfaction directly. Verify current service-quality/bill-clarity scores comply; if any read SIM internals, fix as an epistemic violation.
- BASIS RISK DISPLAY: measured CSAT/NPS vs SIM-true satisfaction, both sides of the wall, on the surfaces -- the measurement gap IS the product insight (silent-middle churn = customers who never appeared in any survey).

LAYER 2 -- PUBLIC REPUTATION (visible to everyone, owned by no one):
- Review generation: customers post public reviews (Trustpilot-class) with propensity driven by satisfaction extremes and event triggers (billing error, great service recovery, switching friction). Rolling public score + review volume.
- Regulator-style quarterly rating (Citizens Advice star-rating analogue) computed from complaints volume, contact performance, billing accuracy -- POPULATION-ANCHORED to real published supplier rating distributions.
- THE LOOPS: reputation feeds acquisition funnel conversion (PROCESS_NOT_EVENTS funnel stage) and in-market entry probability in the churn journey (bad press makes customers shop). Company levers: service recovery, review responses, complaint-handling investment -- each an EV decision in the decision loop (cost vs reputation-mediated CLV effect).

EVIDENCE RULE APPLIES: Rich must see -- a customer leaving a review after a real service event (Customers tab, named account, dates), the reputation trend vs satisfaction truth (Sim tab, correlation panel), and the company CSAT dashboard vs SIM truth divergence (Supplier tab). Spec to Project tab as archive.
Tier 3 for the design (novel scope, 4h window unless Rich pre-approves); implementation Tier 2 after.
