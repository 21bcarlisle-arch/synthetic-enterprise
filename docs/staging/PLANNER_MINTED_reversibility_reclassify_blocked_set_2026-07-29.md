<!-- SUPERVISOR_DRAW: self-drawable -->

# [PLANNER-MINTED] Reclassify the whole blocked set against the reversibility test (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29.md`, WORK-THIS-CREATES **#1**
("The blocked set reclassified against the reversibility test.").

**Serves:** the ruling's root diagnosis (§0/§9): the reserved set was drawn **by category** (all level
moves, all curriculum, all BUILD_OPENs) not **by risk**, so a doc atom moving L1→L2 is walled as hard
as a safety control. This atom applies §2's test — *"Can this be undone by a single act, with no
external consequence in the meantime?"* — to every currently-blocked item and produces the
reclassification the ruling asks the agent to author.
**Real-world fidelity gained:** none directly — operational-authority hygiene. Value = the input to
the release action (#2) and to the batched [ACT] (#3): a per-item verdict of proceed-at-risk vs
genuinely reserved, so the director's act-list shrinks to genuine one-way doors only.

**Lane:** DISCOVER + FRAME (read-only enumeration + judgement; no production behaviour changes).
Self-drawable now.
**Target level:** doc-only operational artifact (no maturity-map level claimed). Output = one committed
table/register.
**Deps:** none — self-drawable now. It is the **upstream** of the action atom
`PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md` (that atom depends on THIS).

## NOT the same as existing mints (why this is not a re-mint)
- `PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29.md` groups the ~21 blocked mints **by
  director channel, assuming each genuinely needs the director**, and produces the paste. THIS atom
  runs one step earlier: it *tests whether each item needs the director at all*. The ledger consumes
  this atom's output — items that reclassify to proceed-at-risk drop OUT of the ledger.
- `PLANNER_MINTED_self_authority_release_sweep_2026-07-29.md` releases under the **pre-ruling narrow**
  definition of own authority (elapsed windows, consumed-ruling self-drawable mints, twin L1/L2). This
  atom's whole point is that §2 **widens** that class (level moves, BUILD_OPENs on ratified decisions).

## Exit criteria
- Enumerate every currently-blocked item (the ~21 blocked `PLANNER_MINTED_*` mints in
  `docs/staging/in_progress/` plus any map atom carrying `blocked_on`/`director_level_up`).
- For each: apply §2 and record a one-line verdict — **PROCEED-AT-RISK** (name the single reversing act)
  or **RESERVED** (name the specific irreversibility: real money/customer/market, external
  communication, safety-control/authority-trust change, evidence destruction, unpublishable, or R13
  curriculum-as-science).
- **§4 binding applied:** any RESERVED verdict that cannot state its irreversibility is invalid — flip
  it to PROCEED-AT-RISK and say so.
- Output = one committed register (`docs/observability/` or alongside the ledger), consumed by the
  action atom (#2) and the batched [ACT] (#3).

## Reverse / undo
Delete the register file; no production state changed (read-only analysis). git revert of the commit.
