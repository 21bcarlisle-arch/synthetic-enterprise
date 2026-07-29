<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BUILT 2026-07-29 (scheduled tick): docs/design/PHONE_SIGNER_SETUP.md written against the existing
     R15-proven mechanism — every step's expected result quotes the real function (sign_wake_message /
     verify_wake_message / _bound_signed_text / record_director_ntfy_ruling / _maybe_ledger_director_ruling).
     Includes a self-contained offline WebCrypto signer page (byte-for-byte match to sign_wake_message)
     and an honest irreducible-acts table (only A2 key-onto-phone is device-bound; no terminal step).
     NOT YET DONE: exit-gated on the sibling terminal-audit atom (phone_signer_terminal_audit, #3) — it
     must run against the written doc before #1 closes. Kept OPEN in in_progress/ until that audit passes.
     Reversible: git revert removes the doc; no secret handled by the agent. -->

# [PLANNER-MINTED] PHONE_SIGNER_SETUP.md — the phone-only, one-action-per-step signer walkthrough (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE_2026-07-29.md`,
WORK-THIS-CREATES **#1** ("`PHONE_SIGNER_SETUP.md` — phone-only, numbered, one action per step, with
the irreducible acts named honestly.").
**Serves:** the *channel* problem (§29 of the ruling) — where the director must be. Today every routine
ruling forces tmux-from-phone. The signer lets him sign an HMAC ruling from his phone; the advisor
relays the walkthrough one numbered step at a time. §0 standing rule: **information is never
console-bound** — a walkthrough is a DOCUMENT, not a console session.
**Real-world fidelity gained:** none directly — director-authority ergonomics. Value = the console
retires for routine authority; the director acts in one tap.

**Lane:** DISCOVER + FRAME (doc-only: enumerate the exact phone steps against the EXISTING verified
mechanism; verify each step's expected result against real code — no new signer is built, the machinery
already exists and is R15-proven/wired). Self-drawable now.
**Target level:** doc-only operational artifact at `docs/design/PHONE_SIGNER_SETUP.md`. No maturity-map
level claimed.
**Priority:** AFTER `director_act_rung_zero_draw` (deliverable #2) — the ruling: *"Answer this BEFORE
the setup is built."* A signer landing acts into an 11h queue is worthless; latency first, then channel.

## Ground truth to build ON (do NOT rebuild — memory `phone_native_authority_proposal`)
The signer path already exists, is RATIFIED+WIRED (2026-07-22, commits `41aaf4dfc`/`cd8b953ca`) and
R15-proven both ways, with the worker-forgeability gap CLOSED (2026-07-23, `6d81a7b08` — key scrubbed
from every model-facing spawn env). The document ENUMERATES how the director uses it from a phone; it
does not add a mechanism. Key files to read for the exact message shape / verify path:
- `background/ntfy_utils.py` — `sign_wake_message` / `verify_wake_message` (HMAC, key `SE_WAKE_HMAC_KEY`).
- `background/director_authority_channels.py` — routine-action allowlist, `record_director_ntfy_ruling`.
- `background/gate_authorization.py` — how a verified `RULING: BUILD_OPEN / LEVEL_UP_PROPOSED` releases.
- `background/ntfy_responder.py` — ledgers HMAC-verified RULING inbounds.

## Exit criteria (the ruling names the required content §19)
`docs/design/PHONE_SIGNER_SETUP.md` exists, written for a **non-technical reader on a phone, discrete
numbered steps, one single action per step, each with an expected result**, covering:
1. **What to install/configure on the phone** — the concrete app/tool that computes an HMAC-SHA256 over
   the exact message bytes with the director's key (name a real phone-runnable option; if none is
   turnkey, say so and name the minimum — see #3 sibling).
2. **Key handling** — how the director generates or receives `SE_WAKE_HMAC_KEY` **without it ever being
   transmitted through any chat, written to the repo, or logged** (§19). State the generation step and
   where it lives on the daemon side (out-of-tree, already provisioned) vs the phone side.
3. **Composing + sending a signed ruling** — the EXACT message shape (the literal string the director
   types/pastes on his phone: the `RULING:` body + `LEDGER:` directive line + the HMAC signature field),
   and the send channel (NTFY topic). One tap = one act.
4. **Verifying acceptance** — how the director confirms the signature was accepted and the atom released
   (what NTFY reply / ledger row / status he looks for), which closes the loop with deliverable #2's
   next-tick guarantee.
- **Irreducible acts named honestly (§21):** where a step genuinely cannot be done from a phone, say so
  and name the minimum irreducible act — do NOT pad the console back in by assumption. (This is the
  audit performed by sibling deliverable #3.)
- **R11-style verify:** each numbered step's "expected result" is checked against the real code/mechanism
  (quote the function that produces it), not asserted.

## Deps
- **depends_on:** `director_act_rung_zero_draw` (deliverable #2) — the walkthrough's verify step (#4)
  and the ruling's Acceptance both rely on the next-tick release guarantee that atom provides.
- **Acceptance (ruling, shared with #2):** the director completes setup and sends ONE live signed ruling
  **without opening a terminal at any point**, and that ruling releases its atom on the next tick. That
  live E2E proof is the joint acceptance of #1+#2 (director-present step, not this mint's own close).

## Coverage mapping
- PHONE_SIGNER #1 → **this atom.**
- PHONE_SIGNER #2 → sibling `PLANNER_MINTED_director_act_rung_zero_draw_2026-07-29.md`.
- PHONE_SIGNER #3 → sibling `PLANNER_MINTED_phone_signer_terminal_audit_2026-07-29.md`.

**Propose-then-proceed window:** proceed by default (ruling tagged *"proceed, after the literal-act
list"*; doc-only, reversible via git; the key never leaves the director's device — no secret handled by
the agent).

## Deliverable (verbatim)
> `PHONE_SIGNER_SETUP.md` — phone-only, numbered, one action per step, with the irreducible acts named honestly.
