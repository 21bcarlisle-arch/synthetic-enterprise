[PROJECT] Phase-close rule: every capability lands IN THE BUSINESS, not in a spec. Rich's directive -- he wants to see features as a company director sees them, on the operational surfaces, with outcomes on both sides of the epistemic wall.

THE RULE (phase-close requirement for every capability phase, SIM or company):
A capability is not delivered until it is VISIBLE ON THE BUSINESS SURFACES, generated from the latest run:

1. THE SIGNAL (Sim tab): the new variable graphed over time from the actual run -- and at least one CORRELATION panel showing it moving against the factors it should move against (income stress vs payment delay; weather vs consumption; wholesale price vs bill shock events). Rich wants to see the signal exist and behave plausibly, not read that it exists.

2. THE CUSTOMER RECORD (Customers tab): at least one real customer where the feature manifests, shown as a company would show it -- the life event on their account timeline, the bill it changed, the arrears entry it created, the payment plan it triggered. Named account, real dates, real amounts from the run. Example standard: C7's Dec-2023 new baby -> income stress -> payment timing slip, visible in C7's payment history and bill record.

3. THE PROCESS (Supplier tab): the operational process that now consumes the feature, shown as a business process -- the churn estimate whose inputs now include the new signal, the collections queue now ordered by it, the retention offer that fired because of it, the hedge decision that moved. Show the DECISION changed, not the code.

4. BOTH SIDES OF THE WALL: where the feature has a SIM ground truth and a company-observed estimate, show BOTH and the divergence (basis risk) -- e.g. SIM income_stress vs company payment-behaviour inference. The gap between what is true and what the company can know is itself the product; display it.

5. THE SPEC (Project tab, secondary): the specification/record can live in the Project section as documentation, but it is the archive, never the evidence. A spec page without the four surfaces above does NOT close a phase.

GUARDRAILS:
- All of it GENERATED from run data on the single-source-of-truth pipeline (consistency gate applies) -- never hand-written, so it can never go stale or contradict.
- This is a phase-close BYPRODUCT, never a phase's primary work (Rule 0a unchanged). The tell of real evidence vs padding: a named customer with dates and amounts. Padding never has one.
- Retrofit first, in order: QD emergent bad debt (aging -> dunning -> payment plan -> write-off traced through one real account), the three-signal churn model (signal graphs + one renewal decision either side of the wall), income stress/life events (C7-class case).

This supersedes any spec-page interpretation of evidence surfaces. Fold into CLAUDE.md phase-close checklist. Confirm with the first retrofitted example's live URL -- acceptance is Rich looking at it and recognising a business, not software.
