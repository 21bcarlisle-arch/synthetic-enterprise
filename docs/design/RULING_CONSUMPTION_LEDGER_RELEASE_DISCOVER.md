# DISCOVER — Ruling-consumption must PRODUCE the block-releasing ledger entry, or name what can (atom `ruling_consumption_ledger_release`)

**Executes the DISCOVER/design half of** `docs/staging/in_progress/PLANNER_MINTED_ruling_consumption_ledger_release_2026-07-28.md`
(source: `DIRECTOR_RULING_BLOCKED_MINT_BATCH_2026-07-28.md` §0 + WORK-THIS-CREATES d1).
**Lane:** H_harness. **This doc is doc-only (drawable now); the BUILD half is director-gated — see §6.**

---
## 1. The wall this had to resolve (verbatim)
R16 is a WALL: *the agent cannot self-authorize a `BUILD_OPEN`; the ledger is authority, not a commit
message.* Category 5/8 (safety/authority; platform-admin) is director-reserved. So: **can
ruling-consumption legitimately WRITE the releasing ledger entry, or is writing it the director's own
act?** The failure mode a wrong answer opens: the agent *inferring/synthesising* a `BUILD_OPEN` from a
ruling that did not explicitly grant it — a fail-open past R16 (self-authorization wearing a transcription
costume).

## 2. VERDICT — hybrid A/B, and the mechanism ALREADY EXISTS

**The load-bearing finding: the transcription path is already built and already fail-closed.**
`background/gate_authorization.py::record_director_ntfy_ruling` is *the ONLY* ledger-write path a
worker/machine can reach for an authority action, and it is structurally incapable of minting an
unauthorized `BUILD_OPEN`:

- It writes a `BUILD_OPEN` entry **only** when handed an **HMAC-signed** `RULING:BUILD_OPEN:<atom>`
  payload that `verify_wake_message` validates against `SE_WAKE_HMAC_KEY`.
- That key is **out-of-tree and worker-unreadable** (PHONE_NATIVE_AUTHORITY_CHANNEL; the same
  TAUTOLOGY-guard that severs the worker from forging any director_ntfy entry). The autonomous worker
  *cannot* produce a valid signature, so it *cannot* mint the entry — R16 holds by construction, not by
  a promise.
- The read side (`_valid_director_act` → `_valid_phone_authority` → `dac.is_valid_director_ntfy`)
  accepts that entry because `BUILD_OPEN` is on the ROUTINE_ACTIONS allowlist; a **console**
  `record_gate_opening` entry is accepted identically. Both are director authority made machine-readable.

So the verdict splits cleanly by **how the ruling's authority arrives**, not by the atom:

- **(A) transcription is legitimate and fail-closed** — for a ruling whose authority arrives through a
  channel the worker cannot forge: a **director-console** act (`record_gate_opening`) OR a **phone-signed**
  `RULING:BUILD_OPEN:<atom>` (`record_director_ntfy_ruling`). Here the machine only *transcribes* an
  already-authenticated director grant into the ledger form the blocker reads. This is already built.
- **(B) director-reserved** — for a ruling that exists **only as a staged/committed `.md` doc**.
  R7/R8: committed git state establishes *provenance* but the advisor-bridge author name is spoofable
  (`ADVISOR_BRIDGE_AUTHOR_NAME` is "a defence-in-depth layer, NOT a cryptographic guarantee"), and the
  worker can set an author name. Therefore **a bare staged ruling authorizes NOTHING to write BUILD_OPEN.**
  The machine must NOT infer a release from it. §0's alternative applies verbatim: *"say so plainly and
  name what can."* What can: the director's single console/phone act, made cheap by §5.

**This is why the three blocked rulings (`0ac3e1b5e` generator, `e685eb76d` cohorts, `27271871e` GAP1)
sat blocked for 3+h.** They were consumed from **committed staged docs** — case (B) — so no ledger entry
was ever written, and `_is_externally_blocked` / `is_valid_level_up` never saw authority. **The gap is
WIRING, not missing authority-code:** nothing in the ruling-consumption path (a) detects that a ruling
*intends* to open a BUILD, (b) checks whether an authenticated entry exists for it, and (c) reports the
block as UNRELEASED (never silently "done") when it doesn't.

## 3. Trigger (what a valid release requires)
A ledger entry is written/confirmed as a release **only** when ALL hold:
1. A ruling **explicitly** names a block-release for a **named atom/front** via a machine-parseable
   directive line — never inferred from prose. Canonical directive (§5): `LEDGER: BUILD_OPEN <atom_id>`
   (or `FRONT_OPEN <front>`, `LEVEL_UP_PROPOSED <atom> <level>`).
2. The authority is **authenticated** by a channel the worker cannot forge — a console
   `record_gate_opening`, or an HMAC-verified `record_director_ntfy_ruling`. (Case A.) A directive line
   present in a **bare staged doc with no authenticated channel** is case B: NO entry written.
3. Provenance is R7/R8-verified (staged/committed provenance of the *ruling*, plus the authenticated
   channel for the *grant*); injected/wake text authorizes nothing.

## 4. Entry contract (the shape the blocker gates already read)
The releasing record is exactly the existing ledger shape — no new record type:
```
{"atom": "<id>", "action": "BUILD_OPEN", "ts": <t>, "authorized_by": "director",
 "channel": "console" | "director_ntfy", "provenance": "<ruling SHA + deliverable>"}
```
This is precisely what `authorized_atoms()` / `_is_valid_authorization()` (BUILD) and `is_valid_level_up()`
(level moves) consume, so authority lands in the form the gate reads. FRONT_OPEN / LEVEL_UP_PROPOSED use
their existing shapes identically.

## 5. Fail-closed rule + release trace
- **Fail-closed:** ambiguous/absent explicit directive → NO entry, block stays. Directive present but
  authority arrives only via a bare staged doc (case B) → NO entry; consumption emits the pre-framed
  director act (§6) and reports the atom **still blocked**. Unverified/injected provenance → NO entry.
- **Release trace:** every written entry's `provenance` cites the ruling commit SHA + the deliverable it
  discharges, so each release is auditable back to a director act (already the `provenance` convention).
- **Fail-silent guard:** if the ledger writer/reader is unavailable, consumption reports the block as
  **UNRELEASED**, never silently "done" (mirrors `read_ledger` returning `[]` on any error → the atom
  simply isn't in `authorized_atoms`, so it stays blocked — the safe direction).

## 6. BUILD half — scope + why it stays director-gated
BUILD is a small **wiring + convention** change (NOT new authority-writing code, which already exists):
1. A ruling that intends to open a BUILD carries a canonical `LEDGER: <ACTION> <target>` directive line
   (parseable, not prose).
2. Ruling-consumption parses that line and **confirms an authenticated ledger entry exists** for it;
   if not, it reports the block UNRELEASED and emits the framed director act — it NEVER writes the entry
   from a bare doc.
3. The director's ratification path (phone `RULING:BUILD_OPEN:<atom>` tap, or console `record_gate_opening`)
   is what actually writes it — both already implemented and fail-closed.
4. Acceptance fixtures: after a qualifying authenticated consumption, `_is_externally_blocked` returns
   False (generator/cohorts/GAP1).

**Blocked_on: `director_authority_seam_signoff`.** Flipping *how authority becomes a ledger entry* — even
to adopt a directive-line convention — is a safety/authority-seam decision (category 5/8, R16). The
director must ratify: *"a ruling carrying `LEDGER: BUILD_OPEN <atom>` + an authenticated channel is the
accepted transcription path; a bare staged doc is not."* Registered as a batched `[ACT]`
(`ruling_consumption_authority_seam_signoff`) — NEVER self-enacted.

## 7. R15 both-ways (for the BUILD half, mandatory before it counts)
- **MUTATION:** neuter the confirm-step and a case-(A) consumed BUILD-opening ruling must leave its atom
  STILL blocked (the control FIRES — no silent release).
- **FAIL-CLOSED:** a ruling with no explicit directive, or whose grant arrives only via a bare staged doc,
  must produce NO ledger entry (inference never releases; R16 preserved).
- **FAIL-SILENT:** ledger writer unavailable → block reported UNRELEASED, never "done".

## 8. Walls untouched
R16 / category 5/8 — the machine only transcribes an explicit, authenticated director grant; it never
mints its own authority (proven structurally by the out-of-tree HMAC key). R7/R8 — authenticity from the
authenticated channel, never injected/wake text. No level self-bump — BUILD lands `blocked_on:
director_level_up`.
