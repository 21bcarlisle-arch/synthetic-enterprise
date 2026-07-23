# [DIRECTOR-RULING] — HMAC forgery gap: OPTION 1. Strip the key from the worker spawn env now (2026-07-23)

**Type:** [DIRECTOR-RULING] via advisor bridge, answering the numbered [ACT] on the director_ntfy forgery gap. Note on channel validity: this bridge path authenticates by advisor authorship, not the symmetric HMAC key — it is unaffected by the gap it is ruling on.

## The answer: 1

Strip `SE_WAKE_HMAC_KEY` from the worker's spawned environment now. The worker needs the topic to SEND; it must never hold the key to SIGN. The director explicitly declines option 3 — a forgeable director channel is worse than none.

## Requirements on the fix

- **R15 both directions:** (a) a forgery signed from inside the worker environment must now FAIL the wall — reproduce the exact inheritance path (`os.environ.copy()` in spawn_invocation) as the failing test first; (b) the worker can still send ordinary NTFYs; (c) the responder-side genuine-ruling path still passes.
- **Sweep the class, not the instance (R10):** enumerate every spawn/inheritance path that copies the parent env into any model-facing process (worker, forks, sub-agents, hooks) and confirm the key reaches none of them. One leak found means others are possible.
- Credit on the record: this gap was **self-caught and flagged before reliance** — the overstated claim corrected in code and proposal. That is the standard; the daily note should carry it as an honest-red-turned-fix.

## Sequencing (unchanged from its own proposal)

Gap closed → then the phone-side signer walkthrough with the director (one step per message; the director provisions the key to his phone himself; it is never transmitted) → then the live proof: one real ruling from the director's phone, shown to ledger and act → **then and only then the console retires for routine authority.** The bridge channel continues throughout.

**Risk & proportionality:** env-handling change on the authority surface — failing test first, own commit, R15 proven before deploy. Tag: **proceed, evidence-first.**

— Advisor bridge, carrying the director's answer, 2026-07-23.
