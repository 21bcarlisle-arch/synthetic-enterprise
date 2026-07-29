<!-- SUPERVISOR_DRAW: hold -->
<!-- BLOCK_RELEASE: director_ratification -- director answers yes/no on key-match: YES -> only the live E2E proof remains (sign one harmless ruling, agent shows it ledgered); NO -> regenerate-and-place command prepared then. See docs/staging/done/RESPONSE_DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md. -->

> **HOLD 2026-07-29 — THE ACT IS NOT "PROVISION THE KEY" (already provisioned). DO NOT SEND AS WRITTEN.**
> Disk check this tick: the 64-hex `SE_WAKE_HMAC_KEY` is already present in
> `~/.config/synthetic-enterprise/.env.ntfy` and loaded in the running verify daemon. The Seed's premise
> ("empty `SE_WAKE_HMAC_KEY=` line, fill it") is FALSE. The batched [ACT], if any, is at most
> "confirm-or-regenerate to a key the director controls + one live E2E proof (sign a harmless ruling →
> ledger row)". **Blocker:** whether the present key is the director's (phone-side match) is
> director-reserved and open. **Unblocks when:** director answers yes/no (see
> `docs/staging/done/RESPONSE_DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md`). If YES → only
> the E2E proof remains (ready to hand over). If NO → the regenerate-and-place command is prepared then.
> Escalated via NTFY 2026-07-29.

# [PLANNER-MINTED] One batched [ACT] to provision the signing key: verbatim short command, file format, restart, success test, safe proof (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md`,
WORK-THIS-CREATES **#3** ("One batched [ACT]: the verbatim short command, file format, restart, success
test, and safe proof.") — the ruling's §2, priority zero, gating 16 of 21 blocked items.
**Serves:** the split the ruling draws — *diagnosis is delegable, the key is not.* The director performs
**one act** (generate + place the secret); everything else is prepared. The agent must never generate or
read the value — that property is the entire worth of the channel (ruling §1).
**Real-world fidelity gained:** none — director-authority provisioning. Value = one short director act
turns the fully-built-but-keyless lock into a working channel, unblocking the signable batch (#4).

## Seed (verified this tick — the draw starts HERE, not cold)
- Target file: `~/.config/synthetic-enterprise/.env.ntfy` — **exists**, carries an **empty**
  `SE_WAKE_HMAC_KEY=` line (placeholder present, value blank). So the act is *fill the existing line*,
  not create the file. Confirm the exact read path at build time: systemd `EnvironmentFile=-.env.ntfy`
  (`generate_units.py:49`) — verify the unit path against `resolve_secret_file(".env.ntfy")`.
- Generation: `openssl rand -hex 32` (ruling's suggestion), run by the director on his own box; the
  value never leaves that box or his phone.
- Verify path on empty key: `ntfy_utils.py:45` reads it; `sign/verify_wake_message` raise
  `SE_WAKE_HMAC_KEY is not set` (`ntfy_utils.py:53-57`) — so "provisioned" is directly testable.

## Exit criteria — ONE committed batched [ACT] doc + a batched NTFY [ACT] pointing at it, containing:
1. **The exact command(s) the director runs — verbatim, short enough to not line-wrap on a phone
   terminal** (the advisor's first attempt wrapped and ran as fragments). Prefer a single one-liner that
   generates AND writes in place (e.g. an in-place edit of the empty line), or two ultra-short lines.
   State the assumption that he generates the key himself and it never leaves his box.
2. **The exact file + line format** to write — matching what the daemons actually read (the empty
   `SE_WAKE_HMAC_KEY=` line in `~/.config/synthetic-enterprise/.env.ntfy`), verified against the real
   loader/EnvironmentFile path (cite it), not assumed.
3. **Whether any code change is needed first** — pulled from the sibling loader atom
   (`wake_hmac_key_loader`): if a loader is required it lands BEFORE this act; if the EnvironmentFile
   path suffices, say so. This atom's ACT sequences AFTER that determination.
4. **What must be restarted + the R2 check** — the exact daemons (verify path:
   `ntfy_responder`/authority channels) and the check that the restart is now running with the key
   loaded (a liveness/verify probe, not "committed").
5. **The observable success test** — what the director sees to know a signed ruling now verifies, with
   no one to ask (a ledger row / NTFY reply / status flip). Tie to `record_director_ntfy_ruling` /
   `_maybe_ledger_director_ruling`.
6. **A safe end-to-end proof that never reveals the key** — the director signs ONE harmless ruling
   (e.g. a no-op / test atom) and the agent shows it ledgered (`gate_authorizations.jsonl` row /
   `is_valid_level_up`). The proof asserts the LEDGERED effect, never the key value.
- **R11-style:** every "expected result" quotes the real function that produces it.
- **Do NOT ask the director to open a terminal for anything except this one command** (ruling §2).

## Deps
- **depends_on:** `wake_hmac_key_loader` (#2) — the success test (#4/#5 above) only passes if the
  provisioned value is reachable by the verify path; that atom resolves loader-needed-or-not first.
- **Gates:** the §4 signable batch (`blocked_item_literal_act_ledger` / `BLOCKED_ITEM_LITERAL_ACTS.md`)
  — those 16 phone-signed rulings only verify once this act lands. The batch is already ready (not
  re-minted); this act is what makes it executable.
- **Acceptance (ruling):** the director performs one short command and one signature, and 16 blocked
  items release. That live E2E is a director-present step — the joint acceptance of this atom + #4,
  not this mint's own close (the mint closes when the batched [ACT] doc is committed and sent).

## Coverage mapping
- SIGNING_KEY #3 → **this atom.**
- SIGNING_KEY #1 → sibling `PLANNER_MINTED_phone_signer_a1_correction_2026-07-29.md`.
- SIGNING_KEY #2 → sibling `PLANNER_MINTED_wake_hmac_key_loader_2026-07-29.md`.
- SIGNING_KEY #4 → ALREADY COVERED (`blocked_item_literal_act_ledger` / `BLOCKED_ITEM_LITERAL_ACTS.md`);
  this atom is the provisioning act that makes that ready batch executable.

**Propose-then-proceed window:** proceed by default for the PREPARATION (doc + verified acts, reversible
via git; the agent never generates or reads the key). The director's own act (§2's one command) is the
irreducible one-way-door step (#5 security/secrets, category 5) — escalated via the batched NTFY [ACT],
never performed by the agent.

## Deliverable (verbatim)
> One batched [ACT]: the verbatim short command, file format, restart, success test, and safe proof.
