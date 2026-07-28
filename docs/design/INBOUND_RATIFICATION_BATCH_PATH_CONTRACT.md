<!-- DISCOVER artefact — GAP-M2 exit criterion (a): the batched inbound-ratification contract. This is
the DISCOVER/design half only (drawable now, doc-only, THREE_LANES L3). The BUILD half (b)(c) is
blocked_on director_build_open_ledger_entry (R16: the agent cannot self-authorize a BUILD_OPEN). This
doc SPECIFIES what the BUILD half will implement; it enacts nothing. -->
# Batched Inbound-Ratification Path — Contract (GAP-M2, DISCOVER half)

**Serves:** `DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28` §2 (the AMENDMENT — asymmetric ratification
on bucket moves). The amendment establishes: moving a gap **INTO** `deliberate-and-staying` is a scope
claim in the direction where honest reds quietly vanish → it **returns for director ratification**;
moving a gap **OUT** toward `mint`, or between the other three buckets, is **autonomous**. Without a
mechanism that (i) detects the into-`deliberate-and-staying` direction and (ii) *batches* those requests
rather than escalating singly, the amendment is prose-only and decays (MAKE_IT_STICK).
**Mint:** `PLANNER_MINTED_inbound_ratification_batch_path_2026-07-28`.
**Governs the buckets defined in:** `docs/design/GAP_TRIAGE_AND_RANKING.md` (GAP2, ratified).

> **R12 up front:** the count of batched requests is a diagnostic, never a score, target, or headline.
> This path routes and holds scope-claims; it never optimises toward a number of them.

---
## 1. Purpose & guarantee (state it first — OPS1 standard)
**Purpose.** Make the one non-autonomous move-direction — retiring a gap *into*
`deliberate-and-staying` — **impossible to enact silently**, while letting every autonomous move flow
without friction. **Guarantee:** an into-`deliberate-and-staying` move never changes a gap's live bucket
until the director ratifies it; and such requests reach the director **batched** (one escalation),
never as N single interrupts.

## 2. The asymmetry this contract encodes (the whole reason it exists)

| Move | Direction of risk | Disposition |
|------|-------------------|-------------|
| any bucket → **`deliberate-and-staying`** | a live/honest red is being **retired as a scope choice** — the direction where reds quietly vanish | **HELD + batched-return-for-ratification.** The row stays in its prior bucket until the director ratifies. |
| any bucket → **`mint`** | a gap is being **opened as work** (Rule-0 direction — work exists) | **autonomous**, unbatched — passes straight through. |
| moves among **`mint` ⇄ `blocked-on-director` ⇄ `not-worth-the-complexity`** | reclassification that does **not** retire a red into "deliberate scope" | **autonomous**, unbatched. |

**FAIL-SAFE (mandatory, exit (c)):** a move whose direction is **ambiguous or unclassifiable** is
treated as **into-`deliberate-and-staying`** (HELD), **never** as autonomous. The safe default preserves
reds — the same asymmetry GAP2 register-1 uses (ambiguous simplification → `mint`, measure it) and that
GAP-Q's staleness filter uses (unproven-stale → alive). Silence never retires a red.

## 3. Contract — what the BUILD half (b) must implement

- **(T) Trigger.** A triage output (canonically **GAP3**'s ranked list, but any run of the ratified
  method) classifies, or reclassifies, a row **into** `deliberate-and-staying` where that row was **not
  already director-ratified** as `deliberate-and-staying`. Detection compares the row's *proposed*
  bucket against its *last director-ratified* bucket (the ledger of prior ratifications), not against
  its previous *proposed* bucket — so a re-run cannot launder an unratified into-move as "no change".
- **(B) Batching rule.** Accumulate all into-moves from a triage run into **ONE** escalation, not N
  singles (§2: *"Batch the inbound-ratification requests rather than escalating singly"*). The batch
  carries, per row: the gap id, its prior (ratified) bucket, the proposed `deliberate-and-staying`
  argument, and the **measured bound** GAP2(iv) requires (argued + bounded + faced-or-scheduled). A
  batch with zero into-moves emits **no** escalation (no empty-batch noise).
- **(C) Channel.** The batch escalates via **`[ACT]` NTFY / a staged proposal doc**, **never** the
  interactive window (ESCALATION_IS_NTFY_NEVER_WINDOW — a window-ask is a silent stall). Naturally an
  extension of the existing `[ACT]` machinery and the twin `route_blocking_decision` surface, not a new
  channel.
- **(H) HELD semantics.** Every row in the batch **stays in its prior bucket** (its last ratified
  disposition, or `mint` if never ratified) until the director ratifies the into-move. An into-move is
  **never self-enacted** — the ranked list may *display* the proposed `deliberate-and-staying` tag as
  `PROPOSED / HELD`, but the row's operative disposition (what the machine draws on) is the prior bucket.
  On ratification, the row flips and the ratification is recorded in the ledger (so a later re-run sees
  it as ratified and does not re-escalate).
- **(A) Asymmetry guard.** Moves **out** toward `mint`, and moves among the other three buckets, pass
  through **autonomously and unbatched** — the mechanism does not touch them. Only into-moves are held.

## 4. BUILD half — still blocked (for the director's BUILD_OPEN decision)
- **(b) BUILD:** a small classifier + batched-escalation path in `background/` — most naturally an
  extension of the existing escalation / `[ACT]` machinery and the twin route-blocking surface. It
  detects an into-`deliberate-and-staying` move, holds it (row stays in prior bucket), and emits a
  single batched ratification request; autonomous directions are untouched.
- **(c) R15 both ways (mandatory).**
  - **MUTATION (control must FIRE):** neuter the batch/hold path → an into-`deliberate-and-staying`
    move must **not** silently land (the row must **not** flip to `deliberate-and-staying` without a
    recorded ratification). If it lands, the control is dead.
  - **PASS-THROUGH (asymmetry is real, not a blanket gate):** an **out-toward-`mint`** move must pass
    **without** escalation — proving the mechanism is directional, not a gate on all moves.
  - **FAIL-SAFE:** an ambiguous / unclassifiable move direction is treated as **into** (HELD), never
    autonomous.
- **blocked_on:** `director_build_open_ledger_entry` — an `H_harness` `BUILD_OPEN` / `FRONT_OPEN` in
  `gate_authorizations.jsonl` (H_harness is off every open product front; `filter_build_candidates`
  excludes it; R16: ledger is authority, the agent cannot self-authorize a `BUILD_OPEN`). **Note:** §4's
  build-open in the sibling ruling names the GAP1 *reader* contract specifically — it does **not** cover
  this distinct mechanism, which needs its own open. The DISCOVER/design half (this doc) needed no open.

## 5. Walls untouched
- **No self-ratification (§2 / DIRECTOR_TWIN Law B):** the mechanism only *routes and holds*; the
  director ratifies the into-moves. It never approves one on his behalf — a twin that unblocks the
  builder becomes a rubber stamp.
- **No level self-bump (R16):** the BUILD half lands at build-quality with `blocked_on:
  director_level_up` for its 0→3 move.
- **R12:** the count of batched requests is a diagnostic, never a score.
