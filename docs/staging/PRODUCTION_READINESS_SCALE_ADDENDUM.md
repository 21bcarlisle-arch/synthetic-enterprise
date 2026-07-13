# PRODUCTION_READINESS_SCALE_ADDENDUM

**Status:** Director-decided (2026-07-13). Addendum to PRODUCTION_READINESS_BASELINE.md Part C (standing design constraints).
**Place in the epoch arc:** constrains Epoch 2 build and Epoch 3 walled-interface specification. Enables go-live scale; builds none of it. Nothing here changes epoch sequencing.

## Problem

The simulation compresses time: a 9.5-year company life replays in minutes as a single-process batch. Real operation is (a) industrial-strength daily/nightly batch at volumes 10^4–10^6× current (48 HH periods × 365 days × N customers), and (b) a narrow set of genuinely event-driven surfaces — portal, payments, and post-Epoch-3 device control, where real-world control paths (direct OEM cloud APIs, not the DCC meter chain) operate at seconds latency.

Time compression can silently license logic that only works because a whole period's events are conveniently present when the code runs. Every such assumption is a latent go-live defect the sim cannot surface, because sim-time never interleaves events the way live time does. A known instance of the class already exists: DD mandate submit+resolve in the same step, caught by Expert Hour review of W5_1.

**The director's decision: design for scale now by constraint, not by infrastructure.** Current volumes cannot exercise distributed infrastructure and building it now would be waste; but the constraints that make logic scale-safe are cheap today and brutal to retrofit.

## Director-decided architecture posture

1. **The retail/company core remains one coherent codebase over an append-only event history.** Industry evidence supports this: the market-leading UK retail platform (Kraken) runs tens of millions of accounts as a Python monolith over a relational store with queue-based async workers. Python is proven at national scale in exactly this domain; the constraint that matters is architecture shape, not language.
2. **Genuinely streaming-shaped workloads are confined behind the device wall, post-Epoch-3.** The industry's own structure separates the retail core from the device/flex platform at precisely such a seam (Kraken vs KrakenFlex; OVO's retail stack vs Kaluza's event-streaming flex platform). The device layer's two-way wall interface is where a streaming substrate may eventually live. Per existing sequencing law, nothing streaming is built or stubbed before its epoch.
3. **No horizontal-scale infrastructure (distributed stores, message brokers, cluster orchestration) is built in any current epoch.** Scale is enabled by the constraints below and later proven by non-functional evidence (Part B's existing scope).

## Standing design constraints (fold into Part C / CLAUDE.md)

- **C-S1 Event-arrival tolerance.** No company-side logic may assume batch completeness. Every decision, valuation, or state update must behave correctly when the events it consumes arrive one at a time, late, and out of order. This must be a testable property of the code, not a convention — the reveal-over-time law extended from "no look-ahead" to "no assumed completeness."
- **C-S2 Idempotency and deterministic replay.** Processing the same event twice must be harmless; replaying an event history must reproduce identical state.
- **C-S3 Asynchronous wall contracts.** Wall interfaces are specified as asynchronous exchanges — request and response are separate events in time, never a synchronous call assuming same-step resolution. Go-live's adapter swap then extends naturally to placing real transport behind the same contract, and the device layer's latency realities (seconds, with failures) fit the same shape.
- **C-S4 Persistence behind an interface.** All durable state access goes through the append-only event-log abstraction; no decision logic may depend on the current storage form (in-memory / JSON-on-disk). The storage engine must be swappable without touching logic.
- **C-S5 Time-scale invariance declaration.** Any company-side atom claiming maturity L3+ must state whether its logic is time-scale invariant (correct regardless of how fast events accumulate in wall-clock terms) and register any exception as a named simplification per R10.

## Explicitly open — NOT decided here

- Which storage or transport technologies eventually sit behind C-S3/C-S4: a go-live-era decision, informed by Part B evidence. Do not select or trial them now.
- Whether existing code violates C-S1/C-S2: an evidence question. EPOCH2_EVIDENCE_PASS's event-model and compute/storage verdicts should inform Part C's finalisation; this addendum does not pre-empt those verdicts.
- How the constraints apply to already-built atoms (retroactive audit vs remediation-on-touch): builder's sequencing call, stated with reasoning when Part C finalises.

## Definition of done

1. This addendum is folded into PRODUCTION_READINESS_BASELINE.md Part C when that draft finalises.
2. The constraints enter CLAUDE.md's standing design constraints in a form a future Expert Hour or phase-close evaluator can test against real code.
3. The builder's answer on retroactive application (open item 3) is recorded with its reasoning.
