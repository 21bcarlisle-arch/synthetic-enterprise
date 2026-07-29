# RESPONSE — the authority seam is withdrawn; the signature workflow is dropped (2026-07-29)

**Trigger:** director ntfy, 2026-07-29 17:28 UTC (`from_rich_20260729_172812.md`, duplicated as
`..._172820.md`): *"The authority seam approval is withdrawn — we removed signatures entirely. Drop it
and carry on."*

**Authority:** plain ntfy = full director authority for every routine act
(`DIRECTOR_RULING_NTFY_IS_THE_DIRECTOR_2026-07-29.md`). No correlation ceremony required — asking for
one would itself be the defect that ruling names ("do not invent authority checks").

---

## What was withdrawn

`DIRECTOR_RULING_CONSUMPTION_AUTHORITY_SEAM_SIGNOFF_2026-07-28.md` §1 — "a blocked atom is RELEASED only
through a channel the worker cannot forge: the console `record_gate_opening`, or a phone-signed
`RULING:BUILD_OPEN` via `record_director_ntfy_ruling` (out-of-tree HMAC)". **That seam no longer exists.**
The 2026-07-29 ntfy ruling had already superseded it; this message closes it explicitly and instructs the
workflow be dropped rather than left parked.

§2 (machine-parseable `LEDGER:` directive lines) and §3 (the six BUILD_OPENs already released) are
unaffected — §2 is a transcription convenience, not an authority check, and §3 is already actioned.

## DROPPED — five staged items moved `in_progress/` → `done/`

All were already PARKED by the ntfy ruling; the director has now said drop, so they are archived rather
than left to be re-read every scan. Parked-not-deleted throughout — git history restores any of them.

| File | What it was |
|---|---|
| `DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE_2026-07-29.md` | the phone-signer channel ruling; its open sub-item was a director-present live E2E signing proof |
| `DIRECTOR_RULING_ROTATE_SIGNING_KEY_2026-07-29.md` | rotate the 2026-07-11 agent-era key to a director-controlled one |
| `PLANNER_MINTED_signing_key_provision_act_2026-07-29.md` | the rotation handover command for the director to run |
| `PLANNER_MINTED_phone_signer_a1_correction_2026-07-29.md` | correcting `PHONE_SIGNER_SETUP.md`'s A1 step |
| `PLANNER_MINTED_wake_hmac_key_loader_2026-07-29.md` | already determined no-build (systemd `EnvironmentFile` suffices) |

## Carried forward, deliberately

- **The key stays provisioned.** The ntfy ruling kept it for the rare reserved acts (real money, real
  people, irreversible public publish, real-people safety controls). Nothing here touches it, and the
  agent still never reads/echoes/logs it. **Not rotated** — rotation was a property of the withdrawn
  seam, and rotating now would be re-erecting the ceremony under another name.
- **The anti-self-ratification wall stands.** The ruling withdrew the *signature*, not the director's
  substantive say-so. The 16 atoms carrying `blocked_on: director_level_up` are the agent's own
  self-promotions with no director act attached; releasing them on my own reading would be marking my own
  homework. A plain ntfy "yes to the pending level-ups" releases all 16 with zero ceremony. **Reported,
  not queued as a blocker** — no work is waiting on it.

## A doc-hygiene sweep survives the drop, unbundled

`phone_signer_a1_correction` carried a *class* finding worth more than its instance: **documentation that
asserts runtime state by reading the source**. That sweep is independent of the signer and stays
available if wanted; it is not re-minted here (SELF-INTERRUPT: the supply of findings is infinite).

— Worker tick, 2026-07-29.
