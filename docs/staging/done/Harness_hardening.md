[PROJECT] Harness hardening -- encode this week's three failure modes as durable constraints

This week produced three recurring-intervention patterns. Per the garbage-collection principle, each becomes a permanent harness rule. Update CLAUDE.md and the phase-close checklist accordingly.

RULE 1 -- PRIORITIES.md freshness is a phase-close gate.
Root cause of the 130-sprint loop: PRIORITIES.md went stale and NEXT_PHASE.md defaulted to self-generated work. From now on, phase-close checklist includes: confirm PRIORITIES.md has at least one real roadmap item in "Next" that outbids any self-generated default. If PRIORITIES.md is stale or empty, refreshing it IS the next phase -- before any other work.

RULE 2 -- "Done" means a verifiable artifact, not a statement.
Twice this week completion was reported before it was real (coverage sprints "stopped" while still running; boundary fixes described as recommended but not landed). From now on, any completion claim in an NTFY or report must name its evidence: a phase entry in PROJECT_OVERVIEW.md, a passing CI check, a fetchable file, or a number. No artifact, no claim -- say "in progress" instead.

RULE 3 -- Every proposed phase states its value before it runs.
NEXT_PHASE.md proposals must answer one line: what real-world fidelity or capability does this add, and which roadmap item or named gap does it serve? A phase that cannot answer gets outbid by PRIORITIES.md. Calibration-score improvements (recall/precision/F1 per NJ/NK pattern) count as valid answers; raw test-count increases do not.

Also fold in the standing benchmark check: annual report gains a "plausibility vs industry" section -- net margin %, capital ratio, bad debt rate, churn rate vs UK supplier benchmark ranges, RAG-flagged -- so economic drift is caught mechanically, not by Rich noticing.

Update CLAUDE.md, the phase-close checklist, and PRIORITIES.md structure to encode all of this. Confirm with a named phase entry.