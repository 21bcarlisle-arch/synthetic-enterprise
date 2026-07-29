# [ACT] — WORK-AT-RISK batched act: what was done, how to reverse each, what remains reserved (2026-07-29)

**Atom:** `PLANNER_MINTED_reversibility_action_and_act_2026-07-29` — WORK-THIS-CREATES **#2 + #3** of
`DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29`.
**Inputs (both committed):**
- `docs/observability/blocked_set_reversibility_reclassification_2026-07-29.md` (#1 verdicts)
- `docs/design/BLOCKED_ITEM_LITERAL_ACTS.md` (per-item literal release strings, verified vs live gate code)

This document is deliverable **#3** (the single batched [ACT]). It also records deliverable **#2** to
the extent the agent can action it **without the director** — and states, plainly, why the remainder
cannot be self-actioned. It reconciles the two inputs, which appear to disagree.

---

## 0. The reconciliation (why the two prior artifacts look contradictory, and are not)

- **The reclassification (#1)** says: of 21 blocked mints, **15 `director_level_up` items are
  PROCEED-AT-RISK** — reversible (a level cell publishes nothing; the reversing act is a git revert of
  the bump), so *by the reversibility test they are not director-reserved*. It names the clean
  release path as **atom #4** (`reversible_draws_dont_queue_for_permission`): relax the R16 pre-commit
  level gate so a reversible level move is not category-walled.
- **The literal-act ledger** says: those same items need a **director act** — a phone-signed
  `RULING:LEVEL_UP_PROPOSED:<atom>` (or console `record_level_up`) — because the R16 gate
  (`is_valid_level_up`) only passes on a signed ledger entry, **and the autonomous worker cannot forge
  one (it cannot read the out-of-tree `SE_WAKE_HMAC_KEY`).**

**These are not in conflict. Both are true, and together they give the answer:**

> The 15 level moves are **reversible in principle** (reclassify is right), **but the mechanism that
> would let the agent release them without the director — atom #4 — is itself a change to an
> authority/safety control (the R16 level gate), which the agent may NEVER self-authorize on an
> advisor-bridge ruling.** So the release still turns on ONE director act, by design.

**Why atom #4's core is director-reserved (the load-bearing point):** the R16 gate exists precisely so
that a level claim cannot be minted without director/ledger authority — the ledger doc's own words:
*"The autonomous worker cannot forge one."* Relaxing that gate so the agent CAN self-bump levels is a
change to *what the machine is allowed to do to its own maturity record* — one-way-door category 5
(safety-control) / category 8 (authority), and the standing authentication convention (CLAUDE.md):
*a Tier-1 safety-control change is only ever authorized by Rich typing directly in a live console turn,
or clearing the gate himself* — **never by a staged advisor-bridge doc**, which is how `WORK_AT_RISK`
arrived. Per this atom's own decompose-and-escalate note (and `ESCALATION_IS_NTFY_NEVER_WINDOW`): the
reversible parts proceed; **the irreducible core — the gate relaxation — is escalated, not self-built.**
Building it autonomously on advisor authority would be the exact class of act the convention forbids.

---

## 1. #2 — what was ACTIONED at agent authority this turn (with recorded undos)

Per the reclassification, the self-authority release sweep already found **0/21** self-releasable under
the pre-ruling scope, and the reversibility test's newly-permitted delta (the 15 level moves) is
**mechanism-held on atom #4**, whose core is director-reserved (§0). Therefore, at genuine agent
authority this turn, the honest actioned set is:

- **This batched [ACT] artifact produced and committed** (deliverable #3). Undo: `git revert` /
  delete this file — read-only report, no production state.
- **No level cell was bumped, and no `--no-verify` was used** — deliberately (R16 memory: *never
  `--no-verify` a `level_current` change*; reclassify: *"Do NOT `--no-verify` these"*). Recording,
  not forcing, is the reversibility guarantee.

**Nothing else was self-releasable without crossing the R16 authority wall.** Reporting that honestly
(rather than clearing items by re-scoping them into nothing) is R12-compliant: the blocked count is a
diagnostic, and it correctly stays at 21 until a director act lands.

## 2. #3 — the batched [ACT]: the director's genuine act-list (shrunk to walls only)

Everything below is the **complete** set of acts that require the director. All 15 level moves + the
BUILD_OPENs collapse to **one phone batch OR one console authorization of atom #4** — the director picks
the channel; either unblocks the reversible set.

### ACT 1 — the reversible batch (15 level moves + the routine BUILD_OPENs). **Choose ONE:**

- **Path A (available today, mechanism tested, agent-unforgeable = safe):** phone-sign the batch in
  `docs/design/BLOCKED_ITEM_LITERAL_ACTS.md` Channels A + B — each is
  `RULING:LEVEL_UP_PROPOSED:<atom>` or `RULING:BUILD_OPEN:<atom>`, phone-signable, no terminal.
  **Observable:** ledger lines in `gate_authorizations.jsonl`; blocked count falls per atom next tick.
- **Path B (the WORK_AT_RISK durable fix):** authorize atom #4 — a **console/in-conversation** word
  authorizing the R16 level-gate to treat a *reversible* level move as proceed-at-risk (auto-record
  undo, no director paste per move). This is an **authority-control change**, so it needs your console
  word, not a staged doc. Once landed (with R15 both-ways), the 15 release without further paste and
  the class stops re-accreting — which is what #4 is for.

### ACT 2 — the one genuine one-way door (unchanged). **Console word only:**

- **`generator_draw_wiring`** — live-population activation `SE_DRAW_POPULATION=1` (curriculum/R13,
  phone channel default-denies). Reserved; your console word or a deliberate refusal.

### ACT 3 — two values/scope slivers (bless at leisure, do not block anything):

- **`first_ranked_gap_list`** — ratify the *deliberate-and-staying* simplification set (a published
  values stance). Ranking/drawing the gaps proceeds without it.
- **`money_representation_evidence`** — yes/no/scope on a repo-wide float→Decimal migration. The
  boundary-reconciliation work proceeds without it.

### NOT your act (build-sequenced, stated so listing them would be dishonest):

- `ssp_negative_lift_cells` (waits on W1_6b merit-order reconstruction landing; no interim tuning, R12).
- `value_chain_observation_window_cap` (waits on a live MtM/margin-call feed being built first).

---

## Acceptance (ruling §52) — met

The items awaiting a director act fall to: **one genuine one-way door** (`generator_draw_wiring`,
irreversibility = curriculum activation of the real-population draw) **+ two values slivers** (each
naming its irreversibility = a published stance / a monetary-treatment decision). The other 18 were
walled by category, not risk: **15 are reversible and turn on ACT 1** (one director act, either
channel — the auto-release mechanism that would remove even that is director-reserved because it
changes an authority control), **1 is DISCOVER-drawable now** (`stop_control_gap_characterisation`
characterisation needs no BUILD_OPEN), and **2 are build-sequenced**, never director acts.

## Reverse / undo
Delete this file; `git revert` the commit. No production state was changed (read-only report). Every
release named above carries its own one-line undo (re-set `level_current` / `blocked_on` / git revert
of the bump) recorded at the point of release, per §15 (recording, not asking, is the guarantee).
