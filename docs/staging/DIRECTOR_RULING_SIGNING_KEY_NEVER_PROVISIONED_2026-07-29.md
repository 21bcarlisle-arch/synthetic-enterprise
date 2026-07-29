# [DIRECTOR-RULING] — The signing key was never provisioned. Prepare everything; give the director ONE command. (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Priority zero — it gates 16 of the 21 blocked items.

## 0. The finding (evidence from the director's own session, this morning)

- `grep -rh "SE_WAKE_HMAC_KEY=" ~` returns **only a test assertion**. No assignment exists anywhere in the home directory.
- `grep -rn SE_WAKE_HMAC_KEY background/*.py` returns **five comments** describing how the key is scrubbed, held out-of-tree and protected — **and no code that loads it**.
- `~/.config/synthetic-enterprise/.env.ntfy` **exists** (236 bytes) and clearly works, since NTFY traffic flows — but the signing key is not in it.

**Conclusion: `SE_WAKE_HMAC_KEY` has never been provisioned. The phone-authority channel has never been usable.** The mechanism, the allowlist, the binding, the forgery tests and the scrubbing are all real and R15-proven — around a secret that was never created. A lock fully built, with no key ever cut.

**PHONE_SIGNER_SETUP.md step A1 is therefore wrong**: it states "the daemon already holds the key" and cites the scrubbing code as evidence. That is evidence the key *would be* protected, not that it exists. **Correct step A1**, and treat this as an instance of a broader class worth checking: *documentation asserting a runtime state from source code alone.* Look for siblings.

## 1. The advisor's error, and the working split

The advisor hand-debugged this over five phone commands. Wrong: **diagnosis is delegable, the key is not.** The split from here, and generally:

- **You:** everything except handling the secret — diagnose, prepare, write the loader if one is missing, fix the docs, verify afterwards.
- **The director:** one act, because the key must never exist in a model-facing process. That property is the entire value of the channel; if you generate or read it, it is worth nothing.

## 2. Required — prepare, then hand over ONE command

Determine what is actually needed and produce **one batched [ACT]** containing:

1. **The exact command(s) the director runs** — verbatim, **short enough to survive a phone terminal without line-wrapping** (the advisor's first attempt wrapped and executed as fragments). Assume he generates the key himself, e.g. `openssl rand -hex 32`, and that it never leaves that box or his phone.
2. **The exact file and line format** to write it into, matching what the daemons actually read — `EnvironmentFile=/home/rich/.config/synthetic-enterprise/.env.ntfy` per `generate_units.py:20`, unless your check finds otherwise.
3. **Whether any code change is needed first** — if nothing currently *loads* the key, build that, with the scrubbing preserved so it never reaches a model-facing spawn.
4. **What must be restarted**, and the R2 check that the restart took.
5. **The observable success test** — what the director should see to know a signed ruling now verifies, without asking anyone.
6. **A safe end-to-end proof** that does not require him to reveal the key: he signs one harmless ruling, you show it ledgered.

## 3. Then the batch

Once proven, the director signs the `BLOCKED_ITEM_LITERAL_ACTS.md` batch — 16 of 21 items in one action type. Have that list ready in signable form: exact `ACTION` and `atom` values, in the order to send them.

**Do not ask the director to open a terminal for anything except §2's one command.** Everything else is yours.

## WORK THIS CREATES

1. Corrected `PHONE_SIGNER_SETUP.md` step A1 and any sibling docs asserting runtime state from source.
2. Key-loading code if absent, with scrubbing preserved.
3. One batched [ACT]: the verbatim short command, file format, restart, success test, and safe proof.
4. The signable blocked-item list, ready.

Acceptance: the director performs one short command and one signature, and 16 blocked items release.

**Risk & proportionality:** the director alone handles the secret; everything else is preparation and documentation correction. Tag: **priority zero.**

— Advisor bridge, recording that the advisor hand-debugged what should have been delegated. 2026-07-29.
