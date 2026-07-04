[PROJECT] Institutional memory: write the verification-week retrospective + encode the permanent rules + establish periodic retros as standing practice

THREE deliverables, one commit each or combined -- all verifiable artifacts.

DELIVERABLE 1 -- docs/retrospectives/2026-07-04-verification-week.md
Write the retrospective of 2026-06-30 -> 2026-07-04. Content (adapt wording, keep substance):

L1. "Done" has layers and every layer lies. Observed variants: committed-not-deployed (PROJECT_STATE.txt), deployed-not-served (CDN cache), script-fixed-but-old-process-running (watchdog, twice), fresh-to-producer-stale-to-consumer (CC fetch vs advisor fetch). RULE: completion is verified by the CONSUMER of the artifact at the consumer's access path. Self-certification is invalid wherever producer/consumer views can diverge.

L2. Autonomous drift goes to the cheapest legible work when the directed queue empties. Coverage sprints (~130 phases) then board Observatories -- same reflex, new costume. STRUCTURE beats vigilance: PRIORITIES.md freshness as phase-close gate; cheap defaults named and barred as a CLASS; every phase proposal states the real gap it closes.

L3. Two false "fixed" claims on one component = stop patching, eliminate the mechanism. send-keys failed 3 ways (race, nvm PATH, quote-swallowing); the fix was removal, not a third patch. Two-strike redesign rule.

L4. Differential diagnosis beats theorising. Every breakthrough came from a contrast pair: LATEST.md fresh vs PROJECT_STATE.txt stale; CC fetch vs advisor fetch; interactive vs login shell. When stuck: find the nearest working twin and diff.

L5. Wedged problems: reduce to the smallest closed loop. Four generator "fixes" failed; the one-timestamp write->push->fetch->paste hard gate succeeded in one round and exposed the cache split as a bonus.

L6. Alert design is governance. Alerts fire on state TRANSITIONS only, carry diagnostic payload (captured pane text), never repeat. An alert that does not change what the human knows should not exist.

L7. Label-substance swap: instructions get honoured in name, swapped in substance (P1-P4 as four board sections; PX queue-jump). Acceptance criteria must be ARTIFACTS ("advisor fetches X and sees Y"), never descriptions ("improve observability").

L8. Advisor-side failures, logged with the same honesty: protocol reflex overriding live instructions; "transient noise" verdict on 58 failures before checking; wrong usage-limit diagnosis; asking again after approval. Corrections: instruction outranks protocol; verify before asserting; act on approval; retract wrong diagnoses immediately.

META: the binding constraint on autonomous enterprise is not capability -- it is truthful state, verified completion, and drift control. That IS the harness thesis, validated the hard way. The harness pieces forged this week: verify-by-fetch, hard-gate pattern, two-strike redesign, transition alerting, differential debugging, the advisor bridge.

DELIVERABLE 2 -- CLAUDE.md amendments (add to the permanent rules section):
R1. Consumer-verified completion: any artifact with an external consumer is done only when that consumer's fetch confirms it. Quote the fetched evidence in the completion NTFY.
R2. Long-running processes: a code fix is deployed only when the running process has been RESTARTED with it. Committed != running.
R3. Two-strike redesign: a second false completion claim on the same component mandates mechanism elimination/redesign, not another patch.
R4. Diagnosis discipline: before proposing a fix for a stuck problem, name the nearest working analogue and state the diff. If none exists, build the smallest closed-loop test first.
R5. Alerting: NTFYs fire on state transitions only, include the diagnostic payload, never repeat an unchanged status.
R6. (already added, reaffirm) Board/report sections are never the primary work of a phase.

DELIVERABLE 3 -- Standing retro practice (add to CLAUDE.md phase governance + PRIORITIES.md process section):
- A retrospective is written at: (a) resolution of any multi-day or multi-false-claim problem, (b) every ~50 phases or 2 weeks, whichever first, (c) any harness rule change.
- Format: what happened, what was tried and failed, the contrast/evidence that cracked it, the rule extracted, where the rule now lives.
- Retros live in docs/retrospectives/, listed in PROJECT_OVERVIEW.md key documents, fetchable by the advisor.
- Retro completeness is a phase-close checklist item after qualifying events.

Confirm with: the retro file's live URL, the CLAUDE.md diff summary, and the phase-close checklist addition -- all in one NTFY.
