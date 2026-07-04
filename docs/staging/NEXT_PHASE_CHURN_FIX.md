[SUPPLIER] NEXT PHASE STEER -- churn model fix is next. Not more generator work.

PZ acknowledged: real findings, good use of the equivalence-gated generator. But note two corrections:

1. ORDERING VIOLATION: ADVISOR_CONFIRM_STATE_FRESH.md released the correlated-generator hold WITH explicit conditions -- it stays BACKLOG behind (a) churn model fix, (b) billing depth, (c) shadow-live hardening. PZ jumped that queue, and PRIORITIES.md apparently lists Correlated Simulation Endgame as P1. Fix PRIORITIES.md to the ordered queue below. No further generator/scenario phases until (a)-(c) are DELIVERED, not just listed.

2. CLAIM CORRECTION: PZ "closes regime-change blindness" is an overclaim. The closure was the 85% hedge floor (historic). PZ QUANTIFIES residual exposure for the board -- valuable, but visibility is not closure. Correct the phase log wording; the harness rule is claims must match artifacts.

THE QUEUE (put this verbatim at the top of PRIORITIES.md):

P1 -- CHURN MODEL RECALIBRATION. Evidence in customer_sample.json: company estimate floored at ~5% while sim crisis churn ran 0.38-0.41; churn_estimate_error_pct shows the same -0.82 to -0.88 error at renewal after renewal, across nearly every customer; and where the model DOES fire it overshoots (C_IC1: +1478%). The company is effectively blind on its single most commercially important estimate -- it drives retention offers, CLV, pricing. Approach: diagnose why estimates pin at the floor during sustained-crisis periods (the 24-month reference window from the NQ redirect -- was it built?); validate against the per-customer basis-risk data now published; measure with the NJ/NK recall/precision/F1 framework, target improvement on BOTH crisis and calm years. The sim ground truth side was already realism-checked via population anchoring -- this is the company-model side.

P2 -- BILLING DEPTH: arrears states and dunning cycles emerging from the 1,605-invoice base; missed payment -> arrears -> escalation, per customer. Bad debt emerges from this; do not build it separately.

P3 -- SHADOW-LIVE HARDENING: daily decision log persistence, timestamped decisions building the falsifiable track record, on the swappable-adapter interface per PU_ADAPTER instruction.

BACKLOG (after P1-P3 delivered): further correlated-generator scenarios, extended stress suites, shadow-live index page.

Also action the two pending staged files (WATCHDOG_LAUNCH_RACE.md, ADVISOR_CONFIRM_STATE_FRESH.md) before starting P1 -- the watchdog launch-race fix in particular must land and the watchdog process must be RESTARTED with the new code (a committed script change is not deployed until the running process restarts).
