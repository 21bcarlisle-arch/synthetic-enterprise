# PHONE_SIGNER_TERMINAL_AUDIT — adversarial audit of PHONE_SIGNER_SETUP.md §1

**Deliverable:** `DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE_2026-07-29.md`, WORK-THIS-CREATES **#3**
("Confirmation that no part of §1 requires a terminal — or precisely which part does and why.").
**Audited artifact:** `docs/design/PHONE_SIGNER_SETUP.md` (deliverable #1).
**Method:** each numbered step walked against the **real mechanism**, quoting the function/line each
step actually invokes — not against #1's prose. Fresh-eyes / cold-eyes discipline: the audit is a
distinct atom so the author does not self-certify (§13's "console-by-default habit" recorded as the
error it is). This is #1's **exit gate**.

---

## Per-step evidence table (what each step actually invokes)

| Step | What it invokes (verified in code) | Director-phone terminal? | Verdict |
|---|---|---|---|
| **A1** confirm daemon holds key | `background/secrets_location.py:40` `MODEL_FACING_FORBIDDEN_SECRETS = frozenset({"SE_WAKE_HMAC_KEY"})`; `scrub_model_facing_env()` (line 43); `git check-ignore background/.env.ntfy` → returns the path (gitignored, confirmed) | No director act at all — daemon-side, already provisioned | phone-doable (n/a) |
| **A2** get key onto phone | Out-of-band transfer (QR scan / one-time manual entry) into the A3 page; the symmetric `SE_WAKE_HMAC_KEY` (`ntfy_utils.py:45`) must be identical on both sides | **No director-phone terminal.** Presupposes a **one-time daemon-side act** to *surface* the key (see finding below) | phone-doable for the director; daemon-side provisioning is the ruling's device-bound carve-out |
| **A3** save signer page | Self-contained HTML, `crypto.subtle` HMAC-SHA256, no network; matches `sign_wake_message` (`ntfy_utils.py:51-63`) byte-for-byte (payload `text\|ts`, hexdigest, output `text\|ts\|hex`) | No | phone-doable |
| **B1** open page | Home-screen icon; offline | No | phone-doable |
| **B2** pick action + atom | Dropdown offers exactly the 7 allowlisted actions; daemon default-denies the rest — `director_authority_channels.py:69` `ROUTINE_ACTIONS` (BUILD_OPEN, FRONT_OPEN, FRONT_CLOSE, GATE_CLEAR, LEVEL_UP_PROPOSED, HELD_PENDING_VERIFICATION, GRADUATE) + `_routine()` (line 91, default-DENY) | No | phone-doable |
| **B3** tap Sign, copy line | Page emits `RULING:ACTION:atom\|ts\|hex`; `(action, atom)` bound inside the signed bytes — `_bound_signed_text` (line 97), replay-onto-another-atom fails `is_valid_director_ntfy` (line 104) | No | phone-doable |
| **B4** send to ntfy topic | Ordinary inbound; `ntfy_responder._maybe_ledger_director_ruling` (`ntfy_responder.py:238`, called at line 451 on **every** inbound) → `record_director_ntfy_ruling` (`gate_authorization.py:357`), fail-closed HMAC verify, fresh within `NTFY_MAX_AGE_SECONDS = 3600` (`director_authority_channels.py:88`) | No — the ntfy app the director already uses for steering | phone-doable |
| **B5** confirm accepted | `director_echo` reply (`ntfy_responder.py:455`); atom releases next tick because director acts draw rung-zero (`director_act_rung_zero_draw`, DONE) | No | phone-doable |

Every code reference above was re-read against the live tree on 2026-07-29; line numbers current as of
this commit (function names are the stable anchor if lines later drift).

---

## Finding — the one non-phone act, named precisely (statement (b), scoped)

**No step requires the DIRECTOR to open a terminal on his phone.** The repeatable signing flow (B1–B5)
and the daily act of authorising a ruling are phone-only: an offline WebCrypto page + the ntfy app he
already uses. That is the thing the ruling's Acceptance test names ("*without opening a terminal at any
point*"), and it holds.

**The single non-phone act is A2 — one-time key provisioning — and #1 already names it honestly.**
Being precise where the exit criteria demand it: A2 as written ("QR scan" / "manual entry") **presupposes
a one-time DAEMON-SIDE act to surface the key** for transfer — the out-of-tree secret (`~/.config/…`
or `background/.env.ntfy`) has to be *displayed* (rendered as a local QR, or read to screen) before it
can be scanned/typed, and on a headless daemon host that display is a shell command run by whoever
administers the daemon.

This is **not** the forbidden thing. It is:
- **daemon-side, not the director's phone** — the ruling forbids a *director-phone* terminal; a daemon
  administration act is a machine-side provisioning step the director never performs on his phone;
- **one-time, ever** — it happens once at setup and never again per §0/§21's explicit device-bound
  carve-out ("provisioning a secret onto the director's own device");
- **already disclosed** — #1's "Irreducible acts" table already marks A2 as the only genuinely non-chat
  act and A1 as a daemon act the director never performs. The audit's job was to check that disclosure
  is complete, and it is.

**Precision the audit adds to #1:** #1's table row A2 says "No terminal" with the daemon-side surfacing
left implicit. Strictly, the *surfacing* of the key is a one-time daemon-side terminal act (not a
director-phone one). This does not reopen #1 — it is the same device-bound carve-out, correctly on the
allowed side of the line — but it is stated here so the record is not "zero terminal anywhere" when the
honest answer is "zero director-phone terminal; one one-time daemon-side surfacing, which the ruling
allows."

---

## Anti-self-flattery — this audit can FAIL (R15 spirit)

The step that WOULD trip this audit is **A2**. The audit did not rubber-stamp #1's "phone-only" claim;
it reasoned from the mechanism (a *symmetric* key, `ntfy_utils.py:45` — "whoever verifies can also
sign") that the key must **physically move** from daemon to phone, which is a real one-time act that
cannot be pure-phone-no-setup. Concretely:

- If #1 had claimed "no setup at all — just start signing", this audit FAILS it: the signer page cannot
  produce a verifying signature until it holds `SE_WAKE_HMAC_KEY`, and that key is scrubbed from every
  model-facing process and stored out-of-tree — it has to be surfaced and transferred once.
- If #1 had hidden a **director-phone** terminal command inside B1–B5 (e.g. "run the signer from a
  shell"), this audit FAILS it: B1–B5 invoke only the offline HTML page and the ntfy app, verified
  above against `sign_wake_message` / the responder path — no shell on the director's phone anywhere in
  the repeatable flow.

A pass that would survive either planted defect would be theatre; this audit names the exact step
(A2 surfacing) and the exact mechanism fact (symmetric key ⇒ physical one-time transfer) that make it
non-theatre.

---

## Verdict — #1's exit gate

**PASS, with the A2 precision above recorded.** No part of §1 requires the director to open a terminal
on his phone. The only non-chat act is the one-time daemon-side surfacing/transfer of the symmetric key
(A2), which is the ruling's explicitly-allowed device-bound provisioning carve-out — a daemon
administration act, not a director-phone terminal. #1 (`PHONE_SIGNER_SETUP.md`) may close on this audit;
this file is committed alongside it.

## Reverse / undo
Doc-only. `git revert` of this commit removes the audit; nothing external is touched.
