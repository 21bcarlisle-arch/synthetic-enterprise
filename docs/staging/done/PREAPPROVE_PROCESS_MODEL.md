[PROJECT] DIRECTOR PRE-APPROVAL: PROCESS_NOT_EVENTS design note is approved in advance. Drop the Tier-3 window. Run the whole thread Tier 2 tonight.

Rich has pre-approved the process-model design note (churn journey state machine, acquisition funnel, debt behavioural branch) sight-unseen to remove the 4h gate from tonight's throughput. Effective immediately:

- The design note (docs/design/PROCESS_MODEL.md) proceeds WITHOUT waiting its Tier-3 window. Write it, commit it, NTFY it -- and continue straight into implementation.
- All implementation phases of PROCESS_NOT_EVENTS and DECISION_LOOP_AND_EVENT_LEDGER are Tier 2: proceed immediately in queue order, start-NTFY only.
- Rich retains post-hoc redirect: he will review the committed design note when he reads the NTFY, and any correction arrives as a normal staged redirect. Build the churn journey first so any redirect lands before acquisition/debt work compounds on it.
- All quality gates unchanged (epistemic verifier, full tests, consistency gate, evidence surfaces, population anchoring per stage).

Tonight's target thread order: process-model design note -> churn journey implementation -> decision-loop triggers on journey stages -> event ledger surfaces -> design system (Part B) / per-fuel portal as parallel fill. Burn hard; the budget directive stands (~90% by Monday 04:00, honest burn lines).
