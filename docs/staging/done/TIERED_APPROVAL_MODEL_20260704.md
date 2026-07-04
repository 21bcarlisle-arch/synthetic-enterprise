[PROJECT] Tiered approval model -- replace the flat 4h opt-out. Concentrate Rich's attention where it changes outcomes.

APPROVED BY RICH. Amend CLAUDE.md phase governance and the watchdog/proposal flow:

TIER 1 -- ONE-WAY DOORS: hard REVIEW_GATE, explicit approval required, NO timeout. Never proceed on silence. Applies to: architecture changes that are expensive to reverse (scale jumps, data-model rewrites, SIM/company boundary changes), anything touching the epistemic law, deleting/rewriting historical run data, external-facing changes (live site structure, anything that could transact), spending decisions, and any safety-control modification (this tier itself, skip-permissions, verifier, staging flow). If in doubt whether something is Tier 1, it is.

TIER 2 -- PRE-APPROVED QUEUE: items already named in PRIORITIES.md (or an actioned staged instruction) proceed IMMEDIATELY on reaching the front of the queue. No opt-out window -- staging/priorities approval WAS the approval. NTFY on start (transparency, not permission). Example: QD emergent bad debt was P2-queued; under this model it would have started at 12:04 not 16:04.

TIER 3 -- NOVEL SELF-GENERATED PROPOSALS: anything not in PRIORITIES.md and not staged -- new ideas, emergent directions, scope additions. Keep the 4h opt-out window exactly as now. This is where Rich's veto has real information value.

MECHANICS:
- Every proposal NTFY states its tier and why: "Tier 2 (P2 in PRIORITIES.md) -- starting now" / "Tier 3 (novel) -- proceeding 4h unless redirected" / "Tier 1 (one-way door: <reason>) -- BLOCKED awaiting explicit approval".
- Tier 1 items park in a REVIEW_GATE file (docs/review_gates/) with the decision needed, options, and CC's recommendation; NTFY once; re-ping daily while blocked; work continues on other queue items meanwhile.
- Misclassification rule: claiming Tier 2/3 for something that is Tier 1 is a serious harness violation; when ambiguous, classify UP.

Confirm with the CLAUDE.md diff summary and the first correctly-tiered proposal NTFY as evidence.
