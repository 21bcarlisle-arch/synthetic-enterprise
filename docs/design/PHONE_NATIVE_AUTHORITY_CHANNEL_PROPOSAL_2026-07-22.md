# PROPOSAL — Phone-native director authority (end the console dependency)

**Status:** ✅ **APPLIED 2026-07-22** — the director ratified in a live console turn ("wire the
phone-authority channel"), the last routine console act. Wired: `gate_authorization.py` now accepts
`director_authority_channels.is_valid_phone_authority` entries for ROUTINE actions (console composes
additively, unchanged); the advisor-bridge git-authorship check is added; `ntfy_responder.py` ledgers
HMAC-verified `RULING:<action>:<atom>` inbounds; deadman folds the proven-rest signal (no false STALL
on legitimate rest). R15 both-ways re-proven THROUGH the gate (33 gate tests incl. reserved-action /
repurpose / worker-forgery / no-key / stale-replay fail-closed). Daemons restarted (R2). Live end-to-end
proof with the director pending (his phone-side HMAC setup).
**⚠️ POST-WIRING SECURITY FINDING (2026-07-22, flagged to the director, OPEN):** the live mutation
proof passed (genuine ruling authorizes; reserved-action / repurpose / tamper / wrong-key / stale all
fail-closed). BUT the TAUTOLOGY guard's premise — "the worker can't read the HMAC key" — is **not met
live**: `worker-tick.service` loads `EnvironmentFile=.env.ntfy` (SE_WAKE_HMAC_KEY) and
`worker_tick.spawn_invocation` does `os.environ.copy()`, so the spawned `claude -p` worker **inherits
the key** and (HMAC being symmetric) could sign a forged `director_ntfy` ruling that passes the wall
cleanly. Not worse than the pre-existing console self-declaration residual (the wall is detection-only),
but a forged director_ntfy carries a valid signature → harder to detect. **Fix (director's call — it's
a key/env-boundary change):** strip `SE_WAKE_HMAC_KEY` from the worker spawn env (pop it in
`spawn_invocation`, as it already pops `ANTHROPIC_BASE_URL`; the worker needs `SE_NTFY_TOPIC` to SEND,
not the wake key to SIGN). Only `director_input_log` provenance-verification reads the key in the worker
context — a downgrade to unverified-provenance logging, not authorization. Until closed, the strong
channel's worker-unforgeability is aspirational, not proven.

**(historical) Status when written:** PROPOSED — designed + R15-proven, NOT applied.
**Provenance:** `docs/staging/DIRECTOR_STEER_PHONE_AUTHORITY_CHANNEL_2026-07-22.md`, Part 2.
**Steer tag:** *Part 1 proceed; Part 2 propose-then-ratify (console, final time).*

> The director, verbatim: *"I don't want stuff in the window. I'm only in the window because you and it
> keep, annoyingly, requiring me to paste stuff there. This is a stupid chicken and egg."*

He is right, and the cause was structural: R16 narrowed the valid authority channel to the **console
ledger**, so every routine ruling required tmux attachment from a phone — the exact manual-relay this
architecture exists to eliminate. This proposal ends that for **routine** authority while leaving the
hard walls exactly where they are.

---

## What changes (requirement, restated)

Two channels become R16-valid for **routine** director authority — ratifications, level rulings, R13
values, graduation calls, steers, [ACT] answers:

1. **Director-NTFY** — a message from the director on the two-way NTFY channel.
2. **Advisor-staged `[DIRECTOR-RULING]` docs** — rulings carried verbatim by the advisor's staging path.

## What does NOT change (the hard walls — steer §"What stays personal/console")

Safety-control changes, **authorization-trust changes**, Tier-1 approvals, and one-way doors (real
customer, real money, volunteer approach, account actions) **stay console-only**. These are rare by
design — the correct amount of console.

---

## The mechanism (built, R15-proven, not wired)

`background/director_authority_channels.py` — a **standalone** module (`gate_authorization.py` does NOT
import it). Two validators, one umbrella:

| channel | authenticated by | why proportionate |
|---|---|---|
| `director_ntfy` | **HMAC signature** (`ntfy_utils.sign/verify_wake_message`, `SE_WAKE_HMAC_KEY`, held **outside the working tree** per `secrets_location.py`); signed text binds `RULING:<action>:<atom>`; ≤1h freshness | R8: NTFY content is untrusted — the topic is a shared secret but human-visible on the director's phone, so a bare marker/prefix is trivially forgeable by anyone who has seen one message. This channel can open BUILD gates and move levels — **high-value authority ⇒ HMAC warranted**, not a prefix. The key being out-of-tree means the **autonomous worker (the only plausible forger) structurally cannot mint a valid entry** — which also discharges the "prevention layer" `gate_authorization.py` deferred. |
| `advisor_ruling` | `[DIRECTOR-RULING]` marker + the advisor-bridge **commit** (identity `21bcarlisle-arch`) + provenance | R7: a real `[ADVISOR-STAGED]`-class committed doc is trustworthy disk/git state. The marker distinguishes a director ruling from ordinary staging; the wiring step adds a git-authorship check that the commit is the advisor bridge's. |

**Default-deny allowlist (`ROUTINE_ACTIONS`).** Both channels may authorize ONLY:
`BUILD_OPEN, FRONT_OPEN, FRONT_CLOSE, GATE_CLEAR, LEVEL_UP_PROPOSED, HELD_PENDING_VERIFICATION, GRADUATE`.
Any other action — including a safety-control/authz-trust change or the gate change itself — is **INVALID
on a non-console channel even with a perfect signature**. This is the wall, mechanised.

## R15 — the authentication can FAIL, both directions (proven)

`tests/background/test_director_authority_channels.py` — **19 tests, all green**:

- **PASS** — a genuine HMAC-signed director NTFY ruling and a genuine marked advisor doc authorize;
  every routine action is accepted.
- **FAIL-CLOSED** — bad signature, unsigned, **signed with a different key** (the worker's forgery),
  stale (replay), **reserved action with a valid signature**, signature **repurposed** onto a different
  action/atom, non-director author, empty provenance, missing marker, missing commit → all rejected.
- **FAIL-SILENT guard** — key unavailable ⇒ invalid (an unavailable check is a FAILED check).
- **TAUTOLOGY guard** — the signature is bound to a key the writer cannot read.
- **Channel isolation** — a console entry returns False here; the two systems compose additively.

Run: `python3 -m pytest tests/background/test_director_authority_channels.py -q` → `19 passed`.

---

## The consequential requirements (from the steer)

- **[ACT]s phone-answerable.** Every [ACT] NTFY carries **numbered short-reply options**; the director
  answers `1` / `2` from the notification — the reply is HMAC-signed by his phone relay and validates as a
  `director_ntfy` ruling. Never "paste this in the console".
- **NTFY becomes the complete record.** Reports/[ACT]s always go via NTFY regardless of console presence —
  the "in-console, skipped the ping" courtesy inverts once the console is no longer his place. (This flips
  the CLAUDE.md NTFY-cadence default; applied at ratification.)
- **R15 both directions before trust** — done (above), not asserted.

## The one ratification (console, final time)

The gate change itself is an **authorization-trust change**, so it is proposed, not applied. **This single
console act ends the console era for routine authority** — after it, the director rules from his phone:

> **Wire it.** In `gate_authorization.py`, extend the authority predicates (`_valid_console_act` and the
> `is_valid_*` family) to ALSO accept an entry for which
> `director_authority_channels.is_valid_phone_authority(entry)` is True, and add the advisor-bridge
> git-authorship check to `is_valid_advisor_ruling`'s wiring. Then teach `ntfy_responder.py` to write a
> `director_ntfy` ledger record when an inbound message HMAC-verifies as a bound `RULING:<action>:<atom>`.
> Restart the responder + supervisor (R2). One mutation re-run confirms the wall still fails-closed live.

Ratify by (a) typing "wire the phone-authority channel" in a live console turn, or (b) — once ratified —
this becomes the *last* thing that needed the console. Until then, nothing here authorizes anything live.
