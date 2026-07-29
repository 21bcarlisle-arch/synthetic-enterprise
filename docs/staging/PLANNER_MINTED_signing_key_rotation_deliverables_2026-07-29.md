<!-- SUPERVISOR_DRAW: hold -->
<!-- SUPERSEDED/PARKED 2026-07-29 by DIRECTOR_RULING_NTFY_IS_THE_DIRECTOR_2026-07-29.md (6abf25904): "park the phone-signer workflow; void the test signature. Plain ntfy = full authority, no signatures, no ceremony." Deliverables #1/#2 (rotation handover + phone-signed E2E proof) are PARKED — the phone signer is no longer the authority gate. #5 (inbound-instruction guard) STILL STANDS as a live harness item (R7/R8 VRAM-load vector, independent of the signer). See §SUPERSESSION below. -->

> **SUPERSESSION 2026-07-29:** `DIRECTOR_RULING_NTFY_IS_THE_DIRECTOR` withdrew the signature/ceremony
> requirement. The signing-key ROTATE workflow (#1 handover, #2 phone-signed E2E proof) is **PARKED**;
> the **test signature is VOIDED** (the `test_signature_proof/GRADUATE` ledger entry graduates a
> non-existent test atom — no effect, acknowledged void). Deliverable **#5 (inbound-instruction guard)
> remains live** — it is a responder-hardening / attention-DoS fix, not a signer feature. #3 (blocked-item
> batch) and the general doc-hygiene half of #4 stand on their own merits, not as signer work.

# [PLANNER-MINTED / GOVERNANCE] — Signing-key ROTATE ruling: five deliverables minted/covered (2026-07-29)

**Provenance:** processing `DIRECTOR_RULING_ROTATE_SIGNING_KEY_2026-07-29.md` as a mint source
(§2+§4 `WORK_DEFINITION_AND_COHERENCE`). The ruling **answers the one open question** the escalation
raised (`RESPONSE_DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md`, `d6b3be3bc`):
**NO — regenerate.** The escalation (parking rather than executing on a false premise) is recorded as
correct. This doc mints one atom per named `WORK THIS CREATES` deliverable and states coverage.

## Deliverable coverage table

| # | Deliverable | Status | Where |
|---|---|---|---|
| 1 | Rotation act handed over: short command, file format, restart + R2, success test | **COVERED — unpark + realign** | `PLANNER_MINTED_signing_key_provision_act` (parked; scope was "confirm-or-regenerate + E2E proof, ready to hand over the moment you confirm"). Director confirmed **regenerate** → unparked this tick, scope resolved to ROTATE. |
| 2 | Live E2E proof of a phone-signed ruling | **MECHANISM PROVEN LIVE (current key); rotated-key proof director-gated** | The channel fired end-to-end this tick: an inbound `RULING:GRADUATE:test_signature_proof\|1785326344\|…` was HMAC-verified and ledgered by `ntfy_responder` — real entry in `gate_authorizations.jsonl` (`channel: director_ntfy`, `authorized_by: director`, `ts 1785326452`). This proves phone→verify→ledger works. The ruling's acceptance is the same on the **director-generated (rotated)** key — that final proof stays director-gated (he must rotate+sign first). Not a separate front. |
| 3 | The signable blocked-item batch, ordered | **COVERED — already minted** | `PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29.md` (`done/`) + `docs/.../BLOCKED_ITEM_LITERAL_ACTS.md` — 16-of-21 items, one action type, signable order. NOT re-minted. |
| 4 | Record corrected; A1-class doc sweep retained | **COVERED — A1 done+unpark; record-correction is disposition** | A1: `PLANNER_MINTED_phone_signer_terminal_audit` (`done/`, audit PASS shown able to FAIL) + `PLANNER_MINTED_phone_signer_a1_correction` (unparked this tick). Record correction = the disposition acts below (§Disposition). |
| 5 | Inbound-as-instruction guard, folded into responder work | **MINTED — new atom (§ below)** | not previously minted. |

## §5 mint — `responder_inbound_not_instruction_guard`

**Serves:** ruling §4 (R7/R8 soft breach): two ntfy-app **test** notifications today were queued as
`[instruction]` and each triggered a model load (VRAM 1,383 → 10,726 MiB). Inbound text carries zero
authority and is untrusted data; queueing arbitrary inbound as an instruction is a cheap
denial-of-attention / VRAM-load vector for anyone who learns the topic.

- **Lane:** HARDEN / harness (`background/ntfy_responder.py`). **Folded into the rotation restart touch**
  of the responder, per the ruling ("Fold a fix into whatever next touches the responder — which the
  rotation does. Not a separate front.").
- **Target level:** L2.
- **Exit criteria (R15 both-ways):** MUTATION — a non-directive / test-class inbound (e.g. an ntfy-app
  self-test) must NOT be written as `[instruction]` and must NOT load the model; neuter the guard → the
  test reds. PASS-THROUGH — a genuine `>25`-char directive still routes to `from_rich_*.md`. FAIL-SAFE —
  an ambiguous inbound does NOT auto-escalate the model (classify conservatively; a real steer can be
  re-sent). The model load is the observable the mutation test asserts on.
- **Deps:** coincides with the responder restart the rotation requires (no independent restart cost).

## §Disposition of the three parked atoms (reversible, done this tick per the ruling's §3)

The director's **NO — regenerate** answers the yes/no all three were parked on:

1. `PLANNER_MINTED_signing_key_provision_act` (#3) → **UNPARKED**, scope resolved to the **rotation**
   handover (deliverable #1/#2). Hand-over is ready; the key is director-generated, never seen by the
   agent ("Do not read, echo, log or store the new key").
2. `PLANNER_MINTED_phone_signer_a1_correction` (#1) → **UNPARKED**. Ruling §3: *"the A1 finding stands
   separately and is still valid"* — the class (documentation asserting runtime state from source) is
   swept regardless. Correction target: key **present + daemon-loaded**, now being rotated (not "empty").
3. `PLANNER_MINTED_wake_hmac_key_loader` (#2) → **STAYS ANSWERED/CLOSED**. Determination unchanged by
   rotation: systemd `EnvironmentFile` loads the (new) key into the verify daemon; no non-systemd,
   non-model-facing caller exists → no Python loader needed. Rotation swaps the file's value, not the
   load path. Re-open only if such a caller is later found.

## §Record correction (deliverable #4, done this tick)

The `SIGNING_KEY_NEVER_PROVISIONED` ruling and its response are already in `done/`; the ruling's premise
is superseded on the record by `RESPONSE_...NEVER_PROVISIONED` (key IS provisioned) **and** by this
ROTATE ruling (regenerate anyway — an agent-minted key lacks the unforgeability the channel exists for).
No live doc now asserts "never provisioned" as an open finding.

## Walls untouched
- **Key generation / rotation** — director-reserved (cat 5 + 8, security posture / authority secret).
  The agent hands over the command and success test; the director generates, the key goes to the file and
  his phone signer, **nowhere else**. The agent never reads/echoes/logs/stores it (ruling §1).
- No one-way door for the agent's part (docs + a reversible responder guard); the irreducible core
  (the key) is the director's and is escalated, not executed.

— Planner mint, from DIRECTOR_RULING_ROTATE_SIGNING_KEY_2026-07-29, 2026-07-29.
