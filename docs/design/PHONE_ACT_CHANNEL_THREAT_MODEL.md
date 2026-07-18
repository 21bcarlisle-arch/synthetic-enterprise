# Phone-answerable [ACT] channel — THREAT MODEL & provable-security design

**Atom:** `H27_phone_act_channel` (lane H_harness, epoch 2). **Stage:** DISCOVER (this doc) — design only, NO code, NO safety-control change, NO activation.
**Status of the mechanism:** the 4-part mechanism is already FRAMED in `docs/design/maturity_map.yaml` (atom `H27_phone_act_channel`, sim1). This document adds the THREAT MODEL and provable-security design the FRAME does not yet contain — it does not re-derive the mechanism.
**Author:** DISCOVER fork (Opus), 2026-07-18. **Real-world anchor:** a bank's out-of-band push-to-approve on an identity-bound device (tap-to-approve) vs. logging into online banking.

> **BINDING GATE (restated up front so it is never lost):** this atom ADDS AN AUTHORITY CHANNEL = an authorization-trust-model change. Design + build + mutation-prove are workable now. The **FINAL ACTIVATION** (the record/flag that declares phone-acts to be valid director authority) is **DIRECTOR-AUTHENTICATED-CONSOLE-ONLY** — one last console act, never agent-set. See §6.

---

## 0. The requirement and what already exists (cited, not re-derived)

**Director, verbatim:** *"Annoying having to log in and paste."* An `[ACT]` decision needing the director's authority must be answerable **from his phone in seconds** — no SSH, no console paste — while carrying **unforgeable director provenance equal to a live console act**.

**What the repo already has (read first, cited):**

- **The gate-authorization ledger** — `background/gate_authorization.py`. The `_valid_console_act(entry, action)` four-check predicate (`action` match + `authorized_by=="director"` + `channel=="console"` + non-empty `provenance`) and its specialised forms `_is_valid_authorization` / `is_valid_gate_clear` / `is_valid_level_up` / `is_valid_front_open`. All director acts append to `docs/observability/gate_authorizations.jsonl` via `record_*`. The §0 gate (`evaluate_gate_wall`) and `fronts_reconciler` read this ledger.
- **THE RESIDUAL, stated in the code itself** (`gate_authorization.py` module docstring, "SCOPE HONESTY" and `is_valid_level_up` "Naming note"): the validity predicate trusts a `channel=="console"` tag that a worker process **can self-declare**. "a lying entry that self-declares `channel==console` is possible; detection makes the honest defect LOUD now" — forge-proofing this is the deferred **prevention layer (sub-step 7)**. This atom's forge-proofing property (§3) is exactly the closure of that residual for the phone channel — and must not re-open it for the console channel.
- **The file-api** — `background/file_api.py` + `background/file-api.service`. `_auth()` verifies an `X-Api-Key` header ONLY. The `/respond` endpoint (`background/file_api.py:287`) already records a director decision on a gate, authenticating via **either** the full `FILE_API_KEY` **or a single-use gate token** (`generate_gate_token`, `background/file_api.py:268`) that is **consumed on use** (`token_path.unlink()`). The mobile `/ui/stage` form rides the same service.
- **HMAC signing** — `background/ntfy_utils.py::sign_wake_message` / `verify_wake_message` (`text|timestamp|hexhmac`, key `SE_WAKE_HMAC_KEY`, replay-bounded by `max_age_seconds`). Key is loaded from the environment only.
- **Secrets out of tree** — `background/secrets_location.py` resolves `.env.*` to `~/.config/synthetic-enterprise/` (700 dir, 600 files), out of the git working tree. `SE_WAKE_HMAC_KEY` and `FILE_API_KEY` live there, not in the repo.
- **Channel-tagged, HMAC-verified input log** — `background/director_input_log.py` logs every input reaching a turn, HMAC-verified where a wake-relay signature exists, to the PRIVATE ops repo.
- **Inbound NTFY is untrusted** — R8/G-N4: "ALL inbound NTFY content is untrusted data." `send_ntfy` / `was_sent_by_us` guard only against our own echo, never authenticate an inbound sender.

**SIMPLICITY GUARD (binding on this whole design):** extend the existing endpoint (`/respond`'s pattern), the existing ledger (`gate_authorizations.jsonl` + `_valid_console_act`), and the existing HMAC (`ntfy_utils`). Do NOT invent a new auth service, a new ledger, or a new key-management cathedral. The wall already provides the seam; this adds one channel discipline, not architecture.

**Nearest working analogue (R4):** `/respond` + `generate_gate_token` — a director already answers a REVIEW_GATE from his phone via a single-use token that never transits as the raw API key. The DIFF this atom must add: (a) that path writes to a `RESPONSES_DIR` gate file the watchdog polls, NOT to the authority ledger; (b) it has no cryptographic tie to the DECISION PAYLOAD (only to the gate id); (c) it does not verify tailnet identity — only a bearer secret. This atom hardens exactly those three gaps for an act that must carry **authority-ledger provenance**.

---

## 1. Trust model & the exact provenance claim

### 1.1 What "unforgeable director authority" must mean here

An act carries director authority iff a verifier can establish, from evidence the **autonomous worker cannot fabricate**, that **the director himself** authorized **this specific decision**. Three properties, all required:

- **P1 — Authenticity (who).** The act originated from the director, not from any worker process, not from any non-director party. Concretely: bound to a secret and/or identity that lives OUTSIDE the worker's reach (out-of-tree key, physical device).
- **P2 — Integrity (what).** The act authorizes the **exact decision it claims** — the atom, the action, the level/target — and the payload cannot be altered in transit or at rest without detection.
- **P3 — Freshness (when).** The act is a fresh, one-time authorization of a decision whose context is still current — not a replay of an old act, not an answer to a superseded question.

### 1.2 Why the console has this today

The console channel satisfies P1–P3 by **physics, not cryptography**: a console turn is a human typing into a live terminal on the director's own machine. The worker cannot type into that terminal; it can only be *woken* by a doorbell (R7 — injected/wake text carries ZERO authority). So `channel=="console"` is *intended* to mean "a fact the worker cannot manufacture." **The known residual (§0):** the predicate trusts the *tag*, and a worker that writes to the ledger file can write `channel=="console"` itself. The console channel's real defense is that the honest writer discipline + LOUD detection (`evaluate_gate_wall`) catch a forged tag today; the cryptographic tie is deferred (sub-step 7).

### 1.3 The security property the phone channel must achieve to be console-equivalent

**The phone channel must satisfy P1–P3 by cryptographic + network evidence, so that a valid phone-act is at least as unforgeable as a console act — and specifically must NOT be forgeable by the exact self-declared-tag path that is the console channel's residual.** A phone-act is valid authority iff:

1. it arrives at a **tailnet-only** director endpoint (network evidence of origin — §2.3), AND
2. it carries a **director secret token** the worker does not hold (P1 — out-of-tree), AND
3. it carries a valid **HMAC signature over the full decision payload**, keyed by an out-of-tree director key (P1+P2), AND
4. it carries a **fresh, single-use nonce** bound into that signature (P3),

and the ledger validity predicate derives the verdict from **(1)–(4) as recomputed facts**, NEVER from a self-declared `channel` field. This is strictly STRONGER than the console channel's current tag-trust, and closing the phone path this way must not lower the console path (§3.4).

---

## 2. Attack surface enumeration

Each vector: the attack, the concrete defense, and whether the defense is **FAIL-CLOSED** (an unverifiable/missing/ambiguous condition ⇒ the act does NOT count).

### 2.1 A malicious/compromised worker process self-issues a phone-act
**(SAME CLASS as the self-declared `channel=="console"` residual — the single most important vector.)**
The autonomous worker can write to `gate_authorizations.jsonl` (it is a repo file) and could append a record self-declaring `channel=="phone"`, `authorized_by=="director"`, with a plausible provenance string — exactly as it could forge `channel=="console"` today.
**Defense:** the phone-act validity predicate (`is_valid_phone_act`, §3) requires a valid **HMAC signature over the payload, keyed by `SE_PHONE_ACT_KEY` which lives out-of-tree** (`~/.config/synthetic-enterprise/`, per `secrets_location.py`) and is NEVER loaded into a worker's environment. A worker without the key cannot compute the signature; a self-declared tag with no valid signature is REJECTED. Validity is a recomputed fact, not a trusted tag.
**FAIL-CLOSED:** yes. Missing signature, unloadable key, or bad signature ⇒ not valid authority ⇒ console required.
**Honest caveat:** this holds iff the phone-act HMAC key is genuinely absent from every worker process environment. That is an operational property (env-file scoping) that must be TESTED (§5) and audited, not assumed — see §7 Q4.

### 2.2 NTFY inbound replay / spoof (R8/G-N4)
Anyone can POST to the ntfy.sh topic (topic secrecy is not authentication). An attacker could replay a captured `[ACT]` deep-link or craft a fake reply.
**Defense:** the NTFY `[ACT]` message and its deep link are **the doorbell, not the authority** (R7/R8). The AUTHORITY is the signed POST to the tailnet-only endpoint (§2.3) carrying the token+HMAC+nonce. Capturing the outbound NTFY yields the *decision text and options* (public-ish) but NOT the director token, NOT the HMAC key, so a captured link cannot be turned into a valid act. The deep link pre-fills options (FRAME part 2) but the SIGNED authorization is minted only on the director's device against the out-of-tree secret.
**FAIL-CLOSED:** yes. An NTFY-borne payload alone never satisfies `is_valid_phone_act`.

### 2.3 Tailscale identity assumptions — what tailnet membership proves and what it does NOT
The FRAME names "the director's Tailscale identity (his device on the tailnet)" as an auth factor. This is the vector most likely to be over-trusted.
**What `_auth` does TODAY:** verifies `X-Api-Key` ONLY (`background/file_api.py:51`). It does NOT verify any tailnet identity. **And critically:** `_funnel_active()` (`background/file_api.py:323`) shows the service can be exposed via **Tailscale Funnel** — i.e. reachable from the PUBLIC internet, where there is no tailnet peer identity at all. **So "reachable only via Tailscale" is FALSE whenever Funnel is active.**
**What tailnet membership actually proves (when the connection is over the tailnet, not the funnel):** the request originated from a node enrolled in this tailnet, whose node/user identity can be read via `tailscale whois <peer-ip>` (login name, node name, ACL tags). **What it does NOT prove:** (a) nothing at all if the endpoint is Funnel-exposed — a public attacker bypasses the tailnet entirely; (b) that the *human* is the director — a shared device, an unlocked/stolen phone, or a **second tailnet node the director (or an attacker with enrollment) added** all present as "on the tailnet"; (c) it inherits DNS/routing trust in the tailnet control plane.
**Defense (defense-in-depth, all required, fail-closed):**
- **(D-a) Bind the phone-act endpoint tailnet-ONLY, never Funnel.** The phone-act route must refuse to serve if it cannot confirm the request arrived over the tailnet (not the funnel). Concretely: the route reads the peer address and requires `tailscale whois` to resolve it to a tailnet peer; a request with no resolvable tailnet identity (i.e. a funnel/public request) is REJECTED. This is a NEW route with its OWN guard — it must NOT reuse the funnel-exposed `_auth`. **Q1 (§7):** exact enforcement (separate listener/port bound to the tailscale interface vs. per-request `whois`) is an open implementation choice.
- **(D-b) Restrict to a specific director identity, not "anyone on the tailnet."** `tailscale whois` must resolve to the director's specific login/node identity (an allowlist of one), not merely "a tailnet member." This blocks a second node / a tagged service node.
- **(D-c) Tailnet identity is a NECESSARY factor, never SUFFICIENT.** It is combined with the token (§2.4) and the HMAC-over-payload (§2.6). A stolen/unlocked device on the tailnet still lacks the ability to mint a *valid signature over the specific decision* unless it also holds the key — so tailnet identity narrows the network origin, the crypto proves authorship of the specific act.
**FAIL-CLOSED:** yes — no resolvable director tailnet identity ⇒ reject; funnel-exposed request ⇒ reject.

### 2.4 Token leakage (logs, repo, NTFY payloads)
A director token could leak into a committed file, a log line, or an outbound NTFY body.
**Defense:** (a) the token/key live out-of-tree (`secrets_location.py`); (b) `director_input_log.py` already scrubs known secrets via `background/secret_scrub.py` (`scrub(content, known_secrets=[...])`) — the phone-act key and token MUST be added to the `known_secrets` list so they are hash-redacted if they ever appear; (c) the token is NEVER placed in the outbound NTFY body or the deep link — the link carries only the decision id + framed options; the SECRET is supplied on the director's device (as `/respond` already avoids embedding `FILE_API_KEY` in the ntfy reply, using a single-use token instead). **Improvement over `/respond`:** even the single-use token should not be the sole factor — pair it with the payload-HMAC so a leaked token alone cannot forge a specific decision.
**FAIL-CLOSED:** partial — leakage prevention is defense-in-depth; the payload-HMAC (§2.6) is the fail-closed backstop if a token leaks.

### 2.5 HMAC key compromise / where the key lives
If the phone-act HMAC key is compromised, an attacker can forge any act.
**Defense:** the key lives out-of-tree per `secrets_location.py` (600-perm file, never in the working tree read by company/saas/site tool calls). It is a DISTINCT key from `SE_WAKE_HMAC_KEY` (blast-radius isolation: a wake-relay leak must not grant authority) — call it `SE_PHONE_ACT_KEY`. **This is a Category-5/Category-8 secret; its creation, placement, and rotation are DIRECTOR-CONSOLE-ONLY** (the agent never provisions authority secrets — CLAUDE.md one-way-door #5/#8). Key rotation policy is **Q2 (§7)**.
**FAIL-CLOSED:** yes — `verify_wake_message`-style code already returns `None`/False when the key is absent; the phone-act verifier must treat key-absent as FAIL (an unavailable check is a FAILED check — R15 fail-silent doctrine), never as pass.

### 2.6 Deep-link tampering (can the answer/options be altered in transit)
The `[ACT]` NTFY carries a deep link pre-populated with the decision + machine-framed options. An attacker (or a MITM on the public ntfy path) could alter the atom, the action, or flip approve→reject.
**Defense:** the authorization the director's device submits is an **HMAC over the FULL canonical decision payload** — `{decision_id, atom, action, target_level|verdict, nonce, ts}` — not just over a gate id (this is the concrete gap vs. `/respond`, which signs nothing about the decision content). The server recomputes the HMAC over the received payload; any altered field ⇒ signature mismatch ⇒ REJECT. The framed options presented to the director are bound into the `decision_id` the server issued, so the director cannot be shown one thing and sign another without the server detecting the mismatch.
**FAIL-CLOSED:** yes — any payload field that does not match the signed bytes ⇒ reject.

### 2.7 A stale/queued [ACT] answered after its decision context changed
The director taps "approve" on an `[ACT]` whose underlying context has since changed (the atom moved, the front closed, a superseding decision landed), or replays a valid old act.
**Defense (freshness/replay, P3):** each `[ACT]` mints a server-side **single-use nonce** bound to a specific `decision_id` (reusing the `generate_gate_token` pattern — a file that is **consumed on use**, `token_path.unlink()`). The signed payload includes the nonce + a `ts`. On receipt the server: (a) checks the nonce is still live (unconsumed) and consumes it — a replay finds it gone ⇒ REJECT; (b) checks `ts` within a bounded window (like `verify_wake_message`'s `max_age_seconds`) ⇒ a stale act REJECT; (c) re-validates that the decision is still OPEN/current (the atom is still in the state the decision assumed) before writing authority — a decision whose context changed is REJECTED and re-surfaced. **Nonce store** design is **Q3 (§7)**.
**FAIL-CLOSED:** yes — consumed nonce, expired ts, or superseded context ⇒ reject; console required.

### 2.8 (Completeness) Endpoint reachability / DoS / downgrade
An attacker floods the endpoint, or forces a downgrade to the weaker `X-Api-Key`-only path.
**Defense:** the phone-act route does NOT accept the generic `_auth` (X-Api-Key-only) path as sufficient for AUTHORITY — that path may serve staging reads/writes but a phone-ACT requires the full tailnet+token+HMAC+nonce set. No single-factor downgrade to authority exists. DoS degrades to "director uses console" (the fail-closed fallback), which is availability-degraded but never authority-compromised.
**FAIL-CLOSED:** yes.

---

## 3. The validity predicate (design, not code)

### 3.1 What a verified phone-act must prove
A record counts as a valid phone-act authority iff ALL of:
1. **Tailnet-director-identity** — the submitting request resolved (via `tailscale whois`, tailnet-only, not funnel) to the director's specific allowlisted identity (§2.3 D-a/D-b);
2. **Director token** — a valid director secret token, out-of-tree, single-use-scoped to this decision (§2.4);
3. **Payload HMAC** — a valid HMAC over the canonical decision payload `{decision_id, atom, action, target_level|verdict, nonce, ts}`, keyed by out-of-tree `SE_PHONE_ACT_KEY` (§2.5/2.6);
4. **Fresh nonce** — the `nonce` is live+unconsumed and `ts` within the freshness window, and the decision is still current (§2.7).

### 3.2 The forge-proofing tie (the core property)
**Validity MUST NOT be derivable from a self-declared `channel` tag.** The verdict is computed by RE-VERIFYING (1)–(4) against out-of-worker-reach evidence (tailnet identity, out-of-tree key). A ledger entry that merely says `channel=="phone"` (or `"console"`) with no verifiable signature is REJECTED. This closes, for the phone channel, the exact residual the console channel still carries (`gate_authorization.py` "SCOPE HONESTY" / sub-step 7): the tag is DECORATION for readability; the SIGNATURE is the authority.

### 3.3 How it extends the existing predicate
Add `is_valid_phone_act(entry)` alongside `_is_valid_authorization` / `is_valid_gate_clear` / `is_valid_level_up` in `gate_authorization.py`. It shares the SAME action/authorized_by/atom shape checks as `_valid_console_act` but ADDS the signature verification as the load-bearing check — it does NOT call `_valid_console_act` (which would accept the self-declared console tag). A phone-act entry has `channel=="phone"` AND a verifiable `sig`+`nonce`; `is_valid_phone_act` recomputes the HMAC (loading `SE_PHONE_ACT_KEY` via `secrets_location.py`) and returns False if the key is unavailable (fail-closed, R15). The set-builders (`authorized_atoms`, `is_valid_level_up`-driven level gate) union the console-valid and phone-valid entries — a phone-act clears exactly what the equivalent console act clears.

### 3.4 Not weakening the console path
The console predicate is UNTOUCHED. Phone validity is an ADDITIONAL, STRICTER route to the same authority — it can only ADD valid acts (ones proven by signature), never accept an act the console path would have rejected. Because `is_valid_phone_act` requires a signature the console path never required, no console act is retroactively invalidated, and no new way to forge a console act is introduced. (If anything, this design's crypto tie is a template for the deferred console-channel prevention layer — but that is out of scope here and director-reserved.)

---

## 4. Provenance record shape

A verified phone-act appends to `docs/observability/gate_authorizations.jsonl` (the SAME ledger the §0 gate + `fronts_reconciler` read), via a new `record_phone_act(...)` writer that mirrors `_append_record` but adds the signature fields. Example for a level authorization:

```json
{
  "atom": "D5_account_hierarchy_payments",
  "action": "LEVEL_UP_PROPOSED",
  "level": 3,
  "ts": 1752878400.0,
  "authorized_by": "director",
  "channel": "phone",
  "provenance": "director phone-act, tailnet-id=<director-node>, decision_id=<id>",
  "decision_id": "<server-issued id>",
  "nonce": "<consumed single-use nonce>",
  "sig": "<hex HMAC over canonical payload, SE_PHONE_ACT_KEY>",
  "tailnet_identity": "<tailscale whois login/node>"
}
```

**Honest distinction — recorded provenance vs. proof:** the `provenance`, `channel`, and `tailnet_identity` fields are HONESTLY-RECORDED CONTEXT (human-readable, like the console path's provenance string) — they are NOT self-authenticating and a worker could type them. The **PROOF is `sig` + `nonce`**, re-verified by `is_valid_phone_act` against the out-of-tree key and the nonce store. A forged entry can copy every descriptive field but cannot produce a `sig` that verifies, so `authorized_atoms`/the level gate never count it. This is the same discipline the code docstring already states for the console residual, but here it is CLOSED by verification rather than left as detection-only. **The §0 gate + `fronts_reconciler` honor a valid phone-act identically to a console act because both flow through the same `authorized_atoms`/`is_valid_level_up` union — a phone LEVEL_UP/GATE_CLEAR clears exactly what a console one does, and a forged one clears nothing.**

---

## 5. R15 mutation-test plan

Each test asserts the CONTROL FIRES on its own named defect — a mutation that removes the guard must turn the test RED (R15: a control that cannot fail is worse than none). All tests run with `SE_PHONE_ACT_KEY` set to a test key in the test env and `send_ntfy` pytest-suppressed (per `ntfy_utils.py` guard).

- **T1 — forged reply, no valid identity → REJECTED.** Submit a phone-act record with `channel=="phone"` and a plausible provenance but NO valid tailnet-director identity (whois resolves to a non-director / funnel origin). `is_valid_phone_act` returns False; `authorized_atoms` excludes it; `evaluate_gate_wall` reports the promotion as UNAUTHORIZED. **Mutation:** remove the identity check → test goes RED.
- **T2 — self-declared `channel=="phone"` with NO signature → REJECTED.** The core forge-proofing test. Append `{channel:"phone", authorized_by:"director", action:"LEVEL_UP_PROPOSED", atom:X}` with NO `sig`/`nonce` (the self-declared-tag attack). `is_valid_phone_act` returns False (no signature to verify). **Mutation:** make the predicate accept the tag without recomputing the HMAC → RED. (This is the H25/sub-step-7 residual, proven closed for the phone channel.)
- **T3 — replayed valid act → REJECTED.** Submit a genuinely-valid phone-act (valid sig+nonce); it is accepted and the nonce consumed. Submit the IDENTICAL act again; the nonce is gone ⇒ REJECTED. **Mutation:** skip nonce consumption / accept a consumed nonce → RED.
- **T4 — tampered payload → REJECTED.** Take a valid signed act, alter one field (flip `action` reject→approve, or bump `level`) WITHOUT re-signing. Recomputed HMAC ≠ `sig` ⇒ REJECTED. **Mutation:** verify the sig over only the gate-id / a subset of fields → RED.
- **T5 (fail-silent, R15 killer-pattern) — key unavailable → REJECTED, not passed.** Run `is_valid_phone_act` with `SE_PHONE_ACT_KEY` UNSET. It must return False (an unavailable check is a FAILED check), NEVER True. **Mutation:** return True / skip verification when the key is missing → RED.
- **T6 (fail-open, R15 killer-pattern) — empty/missing sig field → REJECTED.** `sig==""`, `sig` absent, `nonce` absent each ⇒ False. **Mutation:** treat missing `sig` as "no signature required" → RED.
- **T7 — console path unchanged (regression).** A valid console `LEVEL_UP_PROPOSED` still validates via the unchanged console predicate; adding the phone predicate did not alter console verdicts. Asserts §3.4.
- **T8 — stale/superseded decision → REJECTED.** A valid signed act whose `ts` is outside the freshness window, or whose `decision_id` refers to a decision no longer current, is REJECTED. **Mutation:** drop the ts/context check → RED.

Endpoint-level (integration): **T9** — a request to the phone-act route arriving via the Funnel (no tailnet peer) is refused (§2.3 D-a); **T10** — a tailnet request from a NON-director node is refused (§2.3 D-b).

---

## 6. Activation gating (non-negotiable)

This atom ADDS AN AUTHORITY CHANNEL = an authorization-trust-model change. Per CLAUDE.md one-way-door #5 (security posture/secrets/safety-control changes) and #8 (anything changing what the machine is ALLOWED to do), and this atom's own FRAME:

- **DESIGN (this doc), BUILD (the endpoint + predicate + tests), and mutation-PROVE are workable NOW** as normal DISCOVER/BUILD work — because none of it grants authority until activated. The built code can be fully proven (all §5 tests green) with the channel INERT.
- **What "activation" concretely is:** the phone channel is INERT until a specific **director-console act declares phone-acts to be valid authority**. Concretely, activation is a **`PHONE_CHANNEL_ACTIVATE` record written to `gate_authorizations.jsonl` via the console path** (or an equivalent single flag the §0 gate reads), carrying the same `authorized_by=="director"`, `channel=="console"`, non-empty-provenance envelope, provisioned together with the director's creation/placement of `SE_PHONE_ACT_KEY` in `~/.config/synthetic-enterprise/`. Until that record exists, `is_valid_phone_act` returns False for EVERY phone-act regardless of signature (the predicate checks the activation record first — fail-closed by default-off).
- **This switch-on is DIRECTOR-AUTHENTICATED-CONSOLE-ONLY, never agent-set.** The agent must never write `PHONE_CHANNEL_ACTIVATE`, never create/place the phone-act key, never enable the endpoint route as authority-bearing. The key's provisioning is itself a Category-5/8 secret act, director-console-only. Bring the switch-on to him as one last console act (fittingly, plausibly the last routine console act needed). Mutation test: with no activation record, a perfectly-valid signed phone-act still clears NOTHING.

---

## 7. Open questions (author-tagged, honest)

- **Q1 — Tailnet-only enforcement mechanism.** Whether to enforce tailnet-only origin by binding the phone-act route to a separate listener on the tailscale interface (never Funnel-served), vs. a per-request `tailscale whois` guard on the shared service, vs. Tailscale's `serve` (tailnet-only) as distinct from `funnel` (public). All three are plausible; the security-load-bearing requirement is only that a Funnel/public request can NEVER reach the authority route. Needs a live check of the current `tailscale serve`/`funnel` config and the FastAPI peer-address plumbing. **UNSURE:** I have not verified that FastAPI/uvicorn here reliably exposes the true tailnet peer IP (proxies/`X-Forwarded-For` can spoof it) — if the peer IP is not trustworthy, `whois`-based identity is unsound and a separate bound listener is the safer construct. This must be settled at BUILD, not assumed.
- **Q2 — Token/key rotation policy.** Rotation cadence for `SE_PHONE_ACT_KEY` and the director token, and the revocation path if a device is lost. Rotation is a Category-8 director act; the mechanism (how a rotated key is picked up by the running file-api per R2) needs design. Leaning: reuse the `secrets_location.py` resolve + a service restart, but "hot rotation without an authority gap" is open.
- **Q3 — Nonce store.** Where live nonces persist (a directory of single-use token files like `GATE_TOKENS_DIR`, vs. an append-only consumed-nonce log). The `generate_gate_token` file-per-token + `unlink`-on-use pattern is the simplest reuse and is my leaning (SIMPLICITY GUARD), but its durability across a file-api restart and its concurrency (two rapid taps) want a concrete test.
- **Q4 — Worker key-isolation is an assumption, not yet a proven fact.** §2.1's fail-closed guarantee rests on `SE_PHONE_ACT_KEY` being absent from every worker/`claude -p` fork environment. The env-loading paths (`start_worker.sh`, the file-api unit, fork spawn) must be AUDITED to confirm no worker inherits it, and a test should assert a worker-context `is_valid_phone_act` cannot self-sign. Until audited, treat the forge-proofing as DESIGNED-not-PROVEN.
- **Q5 — Tailscale identity granularity.** Whether to allowlist by tailnet login (user identity, survives device change) or by specific node (device identity, tighter but breaks on a new phone). Leaning login-identity + a single trusted node, but this is a genuine director preference (a lost-phone story differs between the two).
- **Q6 — Funnel exposure of the EXISTING routes.** Out of scope for this atom but flagged: if `/respond` or `_auth`-guarded routes are currently Funnel-exposed, the single-use-token path is reachable publicly (token brute-force surface). Worth a director-visible note; not this atom's to fix.

---

## Appendix — mechanism recap (from the existing FRAME, not re-derived)

4-part mechanism (FRAME): (1) authentication = director-only file-api endpoint gated by Tailscale identity PLUS a director secret token, fail-closed; (2) pre-framed answers = each `[ACT]` NTFY carries a deep link pre-populated with machine-framed options (tap/single word); (3) provenance = a verified phone-act writes to the SAME `gate_authorizations.jsonl` via the SAME `record_*` path with a channel tag + identity-proof; (4) fail-closed = unverifiable auth ⇒ the act does not count, console required. THIS document adds: the threat model, the payload-HMAC + nonce that the FRAME's "token" alone does not provide, the tailnet-vs-funnel identity analysis, the forge-proof validity predicate that closes the self-declared-tag residual, the R15 mutation plan, and the concrete activation record.
