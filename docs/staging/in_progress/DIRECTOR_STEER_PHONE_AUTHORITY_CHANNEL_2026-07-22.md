# DIRECTOR STEER — End the console dependency: phone-native authority, plus F1 FRAME-open (2026-07-22)

> **PARKED IN in_progress/ — 2026-07-22 (worker tick).**
> - **Part 1 (F1 FRAME-open): DONE + committed.** `docs/design/frame/F1_conversations_coupled_triad_FRAME.md`
>   exists (coupled-triad SIM-response / company-generator+estimator / harness-gap, reconciled with the
>   segmentation schema; channel/trust as conversation-revealed traits; build proposal via the gate), committed
>   in `aeb42c742`; the forward-discovery register records F1 GRADUATED→FRAME.
> - **Part 2 (phone-native authority): DESIGNED + R15-PROVEN, awaiting the ONE console ratification.**
>   Proposal: `docs/design/PHONE_NATIVE_AUTHORITY_CHANNEL_PROPOSAL_2026-07-22.md`. Mechanism (standalone, not
>   wired): `background/director_authority_channels.py`. Proof: `tests/background/test_director_authority_channels.py`
>   (19 tests, both directions green).
> - **BLOCKING SUB-ITEM (what unblocks archival to done/):** the director's single console ratification —
>   "wire the phone-authority channel" — which applies the gate change (authz-trust ⇒ console-only by rule).
>   Nothing here authorizes anything live until then. This is the *last* thing that needs the console.

**Type:** [STEER + grant]. Staged by the advisor carrying the director's verbatim frustration. Mechanism yours to design; the requirement is the wall.

## The director, verbatim

*"I don't want stuff in the window. I'm only in the window because you and it keep, annoyingly, requiring me to paste stuff there. This is a stupid chicken and egg."*

He is right, and the cause is structural: R16 narrowed the valid authority channel to the console ledger, so every director ruling required tmux attachment from a phone — the exact manual-relay mode this architecture was built to eliminate. The console then became the default for everything. This steer ends that.

## Part 1 — F1 FRAME-open: proceed now, no console act needed

The director's graduation ruling is already ledgered (commit `aeb42c742`): **"F1 CONVERSATIONS — GRADUATE to FRAME only."** That recorded ruling IS the FRAME-open authorization. Do not wait for a console line. Open the F1 coupled-triad FRAME (SIM-response / company generator+estimator / harness gap, reconciled with the segmentation schema; channel and trust as conversation-revealed traits). The build proposal comes back through the gate as ruled.

## Part 2 — Design the phone-native authority channel (requirements, not mechanism)

**Goal: the director never needs to attach to the console for routine authority again.** Two channels must become R16-valid for routine director authority:

1. **Director-NTFY**: messages from the director on the two-way NTFY channel count as director provenance for: ratifications, level rulings, R13 values, graduation calls, steers, [ACT] answers. Authentication is yours to design proportionately (the topic is already a shared secret scrubbed from the ops mirror; consider whether a director marker/prefix or stronger is warranted — state your reasoning).
2. **Advisor-staged [DIRECTOR-RULING] docs**: rulings carried verbatim by the advisor's staging path, clearly marked, count identically. (The advisor already stages everything else; rulings were the one arbitrary exception.)

**What stays personal/console (the hard walls, unchanged):** safety-control and authorization-trust changes, Tier-1 approvals, one-way doors (volunteer approach, real customers, real money), account actions. These are rare by design — which is the correct amount of console.

**Consequential requirements:**
- **[ACT]s must be phone-answerable**: short reply forms (e.g. numbered options) a director can answer from a notification, never "paste this in the console."
- **NTFY becomes the complete record**: always send reports/[ACT]s via NTFY regardless of console presence — the "in-console, skipped the ping" courtesy inverts once the console is no longer his place.
- **R15 both directions before trust**: a non-director/forged message must FAIL the authority gate loudly; a genuine director-channel ruling must pass and ledger with channel provenance. Mutation-test the authentication.
- **The gate change itself is an authorization-trust change** — so it is proposed, not applied: design it, prove it, and present ONE final console ratification for the director. That single act ends the console era for routine authority; say so explicitly in the proposal.

**Risk & proportionality:** Part 1 is a recorded-ruling execution — proceed. Part 2 touches the authority gate — the most sensitive surface in the harness: design + R15 proofs + propose; the director's one ratification applies it. Tag: **Part 1 proceed; Part 2 propose-then-ratify (console, final time).**

— Advisor, carrying the director's ruling and requirement, 2026-07-22.
