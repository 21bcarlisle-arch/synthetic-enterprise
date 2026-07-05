[SIM] PROCESSES, NOT EVENTS -- Rich's architecture directive. Churn, acquisition, and debt are journeys with stages; supplier action attaches to stages. This is where the nuance of supplier action gets real.

THE PRINCIPLE: every commercial "event" (churn, sign-up, write-off) is the TERMINAL STATE of a process. The SIM must model the chain; the company observes only its exhaust. This is the SIM-side twin of DECISION_LOOP_AND_EVENT_LEDGER (company-side moments of truth) -- design them together.

CHURN AS A JOURNEY (first implementation):
State machine per customer: content -> irritated (service failure, bill shock, price-vs-market drift accumulating in the existing satisfaction accumulator) -> IN-MARKET (triggered by renewal letter, price rise, referral, crisis media; entry probability shaped by satisfaction, elasticity, inertia/activation energy, switching-cost perception) -> comparing (market offers vs current tariff; reputation effects) -> decision (switch / stay / roll to SVT) -> post-decision win-back window. Home move = forced-churn subtype with its own dynamics (existing home-move handling slots in). Life events modulate the whole chain (existing income-stress/life-event machinery feeds it).
EPISTEMIC SPLIT: SIM holds hidden state (satisfaction, in-market status, consideration). Company sees only exhaust: complaints, contact events, portal/quote signals where realistic, renewal responses. The company's churn model then predicts from real precursors -- fixing PASSIVE_CHURN_CAP honestly: recall improves because precursors now exist, not because the math was tortured.

ACQUISITION AS A FUNNEL: awareness -> consideration -> quote -> application -> credit check -> onboarding -> cooling-off. Stage-level leakage observable to the company; supplier levers per stage (price position, acquisition cost, onboarding friction). Makes CAC real and gives the acquisition-aware retention guard a genuine funnel to price against.

DEBT AS A PROCESS: QD already built the pattern (stress -> timing drift -> miss -> arrears -> plan -> write-off) -- generalize its shape: add the engagement/avoidance behavioural branch (the overwhelmed-not-delinquent distinction from the pitch's Stockport case).

SUPPLIER ACTIONS ATTACH TO STAGES: service recovery acts on irritated; renewal pricing acts before in-market; save offers act at comparing; win-back acts post-switch; payment plans act at drift-not-yet-miss. The decision loop's triggers ARE these stage transitions.

SEQUENCING: design note first (docs/design/PROCESS_MODEL.md) covering the churn journey state machine, observable-exhaust mapping, and calibration anchors (stage rates must aggregate to the population-anchored switching/complaint/arrears statistics -- anchoring discipline applies per stage). Then implement churn journey first, acquisition funnel second, debt-branch third. Tier 3 for the design note (novel scope -- 4h window applies); implementation phases Tier 2 once the design is reviewed. Evidence rule applies fully: Rich must SEE a customer walking the journey on the business surfaces, stage by stage, both sides of the wall.

<!-- CLOSED 2026-07-05: all three items delivered. Churn journey (Phase QL),
     acquisition funnel (Phase QR), debt-branch/DCA placement-recovery-sale
     (Phase QS). Design note: docs/design/PROCESS_MODEL.md. Evidence on all
     3 business surfaces for each item, per the directive's own rule. -->
