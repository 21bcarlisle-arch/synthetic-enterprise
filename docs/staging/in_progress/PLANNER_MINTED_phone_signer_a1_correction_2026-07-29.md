<!-- SUPERVISOR_DRAW: hold -->

> **HOLD 2026-07-29 — PREMISE CONTESTED BY DISK EVIDENCE. DO NOT EXECUTE AS WRITTEN.**
> Disk check this tick: `~/.config/synthetic-enterprise/.env.ntfy` (236b, the exact file the ruling
> cites) contains a **real, full-entropy 64-hex `SE_WAKE_HMAC_KEY`**, and the running `ntfy_responder`
> daemon has it **loaded in its live env**. The key is NOT empty/unprovisioned. Correcting A1 to "key
> line is empty / director must provision" would write a NEW falsehood. **Blocker:** the true A1 text
> depends on whether the provisioned key is one the director controls (phone-side match) — an open,
> director-reserved question. **Unblocks when:** the director confirms yes/no (see
> `docs/staging/done/RESPONSE_DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md`); then A1 is
> corrected to whichever truth. Escalated via NTFY 2026-07-29.

# [PLANNER-MINTED] Correct PHONE_SIGNER_SETUP.md step A1 (key was never provisioned) + sweep siblings asserting runtime state from source (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md`,
WORK-THIS-CREATES **#1** ("Corrected `PHONE_SIGNER_SETUP.md` step A1 and any sibling docs asserting
runtime state from source.").
**Serves:** the ruling's finding — `SE_WAKE_HMAC_KEY` **has never been provisioned**; the phone-authority
channel has never been usable. `docs/design/PHONE_SIGNER_SETUP.md:38-44` step A1 asserts *"the daemon
already holds the key"* and cites the scrubbing code (`secrets_location.py:40`) as evidence — but that
is evidence the key *would be* protected, **not that it exists**. Verified on disk this tick:
`~/.config/synthetic-enterprise/.env.ntfy` carries an **empty** `SE_WAKE_HMAC_KEY=` placeholder (name
present, value blank), and `grep SE_WAKE_HMAC_KEY= ~` returns only a test assertion — no assignment.
**Real-world fidelity gained:** none — a truthfulness correction. Value = the setup walkthrough stops
asserting a runtime state (key loaded) from source code alone, closing the exact class the ruling flags.

**Lane:** DISCOVER + FRAME (doc correction of the already-written `PHONE_SIGNER_SETUP.md`, plus a
read-only sibling sweep for the broader class; no code change, no secret handled). Self-drawable now.
**Target level:** doc-only correction committed to `docs/design/PHONE_SIGNER_SETUP.md` (+ a short
findings note listing sibling docs corrected). No maturity-map level claimed.

## Exit criteria
- **Step A1 rewritten** from "Confirm the daemon already holds the key / Action: none" to the true
  state: the key line **exists but is empty**; the key must be **generated and written by the director**
  (the §2 handover), and until then no signed ruling can verify. The step's "expected result" must be
  checked against real code (`ntfy_utils.py:45` reads `os.environ.get("SE_WAKE_HMAC_KEY")` — empty ⇒
  `sign_wake_message` raises `SE_WAKE_HMAC_KEY is not set`, `ntfy_utils.py:53-57`), not asserted.
- **Class sweep (R10 — fix the class, not the instance):** grep the doc corpus for other places that
  assert a *runtime* state (key/process loaded, daemon running, value present) purely from *source*
  (a scrubbing constant, a comment, a service file). Candidate seeds: the A2/A1 table rows
  (`PHONE_SIGNER_SETUP.md:168-176`), any `phone_native_authority` / channel doc claiming the key is
  "already provisioned". Each sibling either corrected or explicitly cleared (checked against disk),
  with the list committed.
- **Anti-regression:** the corrected step must be able to say "not yet provisioned" and flip to
  "provisioned" ONLY when a real check (a value present in the daemon env / a passing verify) confirms
  it — no re-assertion from source. State the check that would flip it.

## Deps
- **depends_on:** none to START (doc read + edit). Its A1 "how to make it true" text POINTS AT the
  §2 handover atom (`signing_key_provision_act`) and the loader atom (`wake_hmac_key_loader`) but does
  not wait on them — this atom corrects the false claim now; those atoms make the true state reachable.
- **Related (do not fold):** `phone_signer_setup_doc` (CLOSED, `docs/staging/done/`) authored the
  now-incorrect A1; this atom is its correction, not a re-open.

## Coverage mapping (doorbell requires stating what each ruling deliverable maps to)
- SIGNING_KEY #1 (correct A1 + sibling docs) → **this atom.**
- SIGNING_KEY #2 (key-loading code if absent) → sibling `PLANNER_MINTED_wake_hmac_key_loader_2026-07-29.md`.
- SIGNING_KEY #3 (one batched [ACT]) → sibling `PLANNER_MINTED_signing_key_provision_act_2026-07-29.md`.
- SIGNING_KEY #4 (signable blocked-item list, ready) → **ALREADY COVERED** by
  `docs/staging/done/PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29.md`, whose output
  `docs/design/BLOCKED_ITEM_LITERAL_ACTS.md` (lines 18, 64-65) already lists the 16 items as ONE
  phone-signable action type (`RULING:LEVEL_UP_PROPOSED:<atom>`, HMAC-signed). Its *readiness* is gated
  on #2/#3 (the key must actually exist); not re-minted.

**Propose-then-proceed window:** proceed by default (doc correction only, reversible via git; no secret
handled by the agent).

## Deliverable (verbatim)
> Corrected `PHONE_SIGNER_SETUP.md` step A1 and any sibling docs asserting runtime state from source.
