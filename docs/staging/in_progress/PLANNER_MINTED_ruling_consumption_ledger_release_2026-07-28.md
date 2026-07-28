<!-- SUPERVISOR_DRAW: blocked -->
# [PLANNER-MINTED] — Ruling-consumption must PRODUCE the ledger entry that releases a block — or name what can (§0 + WORK-THIS-CREATES deliverable 1) (2026-07-28)

> **[IN-PROGRESS DISPOSITION 2026-07-28] — DISCOVER DONE, BUILD blocked (director seam).**
> The DISCOVER/design half is EXECUTED → `docs/design/RULING_CONSUMPTION_LEDGER_RELEASE_DISCOVER.md`.
> **Verdict: hybrid A/B — and the transcription mechanism ALREADY EXISTS.** `record_director_ntfy_ruling`
> is the only worker-reachable ledger-write path and is structurally fail-closed (the worker cannot read
> the out-of-tree HMAC key, so it cannot forge a `BUILD_OPEN`). The three blocked rulings hit a **wiring**
> gap (consumed from bare staged docs = case B → no entry written), not a missing-authority gap.
> **BUILD half is BLOCKED** on `director_authority_seam_signoff` — adopting the `LEDGER: BUILD_OPEN <atom>`
> directive-line convention is a category-5/8 authority-seam decision (R16), NOT self-enactable. Registered
> as batched `[ACT]` `ruling_consumption_authority_seam_signoff` in the action_needed register. Marker flipped
> self-drawable → blocked (next step is director-gated).

**Source:** `DIRECTOR_RULING_BLOCKED_MINT_BATCH_2026-07-28.md`, **§0 (the mechanism fault)** and its
**WORK THIS CREATES deliverable 1**: *"Ruling-consumption creates the ledger entry that releases a
block — or a plain statement of what can, if it cannot."*

**Provenance:** RUNG-7 planner mint from a ratified ruling's WORK THIS CREATES block (§2+§4 mechanism,
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`). **grep-confirmed net-new:** no existing
`PLANNER_MINTED_*` doc or map atom builds a ruling-consumption→ledger-release bridge. The sibling mints
(`gap1_reader_contract_failopen_fix`, `gap_registers_as_mint_sources`, `inbound_ratification_batch_path`,
`generator_draw_wiring`, `dd_seasonal_cashflow_physics`) are each blocked ON exactly the gap this atom
closes — they wait for a `BUILD_OPEN`/`FRONT_OPEN` entry in `gate_authorizations.jsonl` that no consumed
ruling currently writes. This is the meta-fix that makes those releases arrive in a form the blocker can
read; distinct from every one of them.

**Serves:** §0 verbatim — *"If a block releases only on a ledger entry, then consuming a ruling must
create that entry — otherwise authority arrives in a form the blocker cannot read, and ruled work sits
blocked indefinitely. This is the same class as consumed-≠-absorbed."* Three director rulings
(`0ac3e1b5e` generator, `e685eb76d` cohorts, `27271871e` GAP1 BUILD) all RULED and all still blocked for
3+ hours because the authority never reached `is_valid_level_up` / the `_is_externally_blocked` gate in
the ledger form those gates read. This is a governance-integrity + liveness mechanism, not a scope add.

**Fidelity gained (one sentence):** none directly — an **authority-plumbing** mechanism ensuring a
director ruling that opens a BUILD cannot silently fail to release the atom it opens.

---
## The WALL this atom must resolve FIRST (why DISCOVER-first)
R16 is a WALL: *the agent cannot self-authorize a `BUILD_OPEN`; the ledger is authority, not a commit
message.* Category 5/8 (safety/authority, platform-admin) is director-reserved. So the design question
is genuine and load-bearing: **can ruling-consumption legitimately WRITE the ledger entry, or is writing
it the director's own act?** The candidate answer to be validated in DISCOVER: the machine only
**TRANSCRIBES** an *already-ratified, explicit, verified* director instruction into the ledger form —
that is the director's authority made machine-readable, not the agent minting its own. The failure mode
this must NOT open: the agent inferring/synthesising a `BUILD_OPEN` from a ruling that did not explicitly
grant it (that WOULD be self-authorization — a fail-open past R16). DISCOVER must land on ONE of:
- **(A) transcription is legitimate and fail-closed-able** → specify the exact trigger + verification +
  entry contract for BUILD; then BUILD it, blocked_on the director's sign-off on the authority seam.
- **(B) transcription is itself a director-reserved act** → then deliver §0's alternative verbatim:
  *"say so plainly and name what can"* — i.e. state that a human/console/phone-signed act must write the
  entry, and mint/point-to the smallest mechanism that makes that one act cheap and unambiguous (e.g. a
  ruling carries a machine-parseable `LEDGER: BUILD_OPEN <atom>` line the director's phone-tap emits).

## Lane / level / deps
- **Lane:** `H_harness` (`background/` — the `gate_authorizations.jsonl` writer/reader + the
  ruling/staging consumption path in `staging_disposition.py` / the director-input log).
- **Target level:** DISCOVER half → design doc (doc-only, drawable now). BUILD half → `level_current 0 →
  level_target 3` (built + R15-proven both ways + live), gated per the DISCOVER verdict.
- **Deps:** `gate_authorizations.jsonl` + `is_valid_level_up` (R16 ledger, exists); the advisor-bridge /
  director-authentication convention (console-only for safety-reducing changes; a ruling's authenticity
  is established by its staged/committed provenance, NOT by injected text — R7/R8).
- **blocked_on (BUILD half):** `director_authority_seam_signoff` — flipping how authority becomes a
  ledger entry is a safety/authority-seam change (category 5/8); the DISCOVER doc is drawn and escalated
  as a batched `[ACT]` for the director's one-time ratification of the chosen path (A or B), NEVER
  self-enacted. **The DISCOVER/design half is drawable NOW.**

## Exit criteria
- **(a) DISCOVER/design (drawable now):** a written contract answering the wall question with a verdict
  (A or B above), specifying — the **trigger** (a genuinely-ratified ruling, provenance-verified per
  R7/R8, that EXPLICITLY names a block-release for a named atom/front — never inferred); the **entry
  contract** (the exact `gate_authorizations.jsonl` record shape the blocker gate already reads —
  `BUILD_OPEN`/`FRONT_OPEN`/level-up — so authority lands in the form `_is_externally_blocked` /
  `is_valid_level_up` consume); the **fail-closed rule** (ambiguous/absent explicit grant → NO entry
  written, the block stays; injected/unverified provenance → NO entry); and the **release trace** (each
  written entry cites the ruling commit SHA + deliverable, so the release is auditable back to director
  authority). If verdict B: name precisely the human act that CAN write it and the smallest mechanism
  making it a single tap.
- **(b) BUILD (gated on the DISCOVER verdict + director seam sign-off):** consuming a qualifying ruling
  produces the releasing ledger entry (verdict A) or emits the single pre-framed director act (verdict
  B); the three currently-blocked atoms (generator/cohorts/GAP1) are the acceptance fixtures — after
  consumption their `_is_externally_blocked` returns False / their level-up validates.
- **(c) R15 both-ways (mandatory):** MUTATION — neuter the transcription and a consumed BUILD-opening
  ruling must leave its atom STILL blocked (the control FIRES: no silent release). FAIL-CLOSED — a ruling
  that does NOT explicitly grant a release, or whose provenance is unverified/injected, must produce NO
  ledger entry (the safe direction preserves R16; inference never releases). FAIL-SILENT — if the ledger
  writer is unavailable, consumption reports the block as UNRELEASED, never silently "done".

## Walls untouched
- **R16 / category 5/8 (the point):** the machine only transcribes an explicit, verified director grant;
  it never mints its own authority. If DISCOVER finds transcription itself is director-reserved, BUILD
  does NOT proceed — it delivers the "name what can" statement instead.
- **R7/R8:** authenticity comes from staged/committed provenance, never from injected/wake text; a
  ruling's mere arrival authorises nothing.
- **No level self-bump (R16):** the BUILD half lands with `blocked_on: director_level_up`.
