# Retro — the permission machinery outlived its own deletion (2026-08-03)

**Class:** governance / decay. **Severity:** the director's attention, five days of it.
**Caught by:** the director, in console, on being handed a list of decisions that had been void since 29 July.

---

## What happened

On the morning of 2026-08-03 a restarted main session was asked "what decisions are you waiting on
me for?" It answered with four items: a level-ratification batch (CA1–CA4), an authority-seam
sign-off, two residual BUILD-opens, and "~20 mints awaiting level ratification". It recommended the
director ratify them in one pass.

**Every one of those was abolished on 2026-07-29**, five days earlier, by
`DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY` + `NTFY_IS_THE_DIRECTOR` + `THE_STANDARD`. The
director's reply: *"that whole list is obsolete ... There is no such thing as needing a build opened
or a level ratified: propose, record, act."*

## Why the session believed it — evidence, not inference

The session did not hallucinate the list. It read it off live state, and every source it read was
still telling the old story:

| Source consulted | What it said | Status on 2026-07-29 |
|---|---|---|
| `docs/observability/action_needed_register.json` | 3 open asks, `last_sent_at: 2026-08-02` | void |
| `deadmans_switch._reping_open_action_needed_items` | re-paged all 3 daily, for five days | void |
| supervisor tick log, 05:56 UTC | "OPEN MINTS (23): ... → director_level_up (R16 — no self-bump)" | void |
| `CLAUDE.md` | 8 one-way doors, R16 "no self-bump", twin as BUILD-open approver | superseded |
| `background/fronts.yaml` | 6 declared gates, 4 of them director-permission | void |

The 29 July sweep was real and it was substantial — 13 atoms released, the block-type abolition
**mechanised** in `_is_externally_blocked`, the one-way-door list re-scoped to four real
consequences. It cleared the DATA. What it did not do was delete the code and the canon that
regenerate the data, so the convention grew back from the parts that were left.

## The general lesson

**Deleting a rule's instances does not delete the rule. Delete the thing that can create instances.**

Every survivor here was one of three shapes, and none of them is "a gate":

1. **A queue that outlives its item type.** The action-needed register had no opinion about what a
   valid director ask *is*, so three withdrawn-convention items sat in it and were re-pinged daily.
2. **An alarm that reports the absence of permission.** The deadman's `GATE_VIOLATION` paged on any
   `idle→build` move "with NO director-console authorization" — i.e. it alarmed on the machine doing
   exactly what THE_STANDARD requires. An alarm is not a gate, but it consumes the same scarce
   resource.
3. **Dormant machinery behind a deleted flag.** The fronts draw-filter was left flag-off, not
   removed. Dormant permission machinery is still permission machinery: one recreated file would
   have silently re-gated the BUILD draw.

There is a fourth, subtler shape: **the convention spelled out in English.** `_names_abolished_
permission_block` matched the token `director_level_up`, so six mints whose stated blocker was
"a director word authorising live activation" or "director ratification of the proposed set" stayed
blocked. Same abolished act, wearing a sentence instead of an identifier.

## What was removed (the full sweep)

Deleted outright: `background/fronts.yaml`, `background/fronts_reconciler.py`,
`background/inbound_ratification.py` (already caller-less), `background/director_authority_channels.py`
(the HMAC/phone-signature channel), the supervisor's fronts/BUILD_OPEN draw filter and its
`off_open_front` hold reason, the RUNG-1c director-act draw rung, the deadman's `_check_gate_wall`,
`staging_disposition.unreleased_ledger_directive_in_staging` (the authority seam), `ntfy_responder.
_maybe_ledger_director_ruling`, `director_twin.ratify_routine_level`, and from `gate_authorization`
the whole permission surface (`authorized_atoms`, `held_atoms`, `evaluate_gate_wall`, the
FRONT_OPEN/GATE_CLEAR/BUILD_OPEN family, the console/phone authority predicates, the twin validator).

Kept, each with the real-world consequence it prevents (the ruling's own Sweep requirement):

* **The level RECORD** (`record_level_up_self_certified` + `is_valid_level_up` + the pre-commit
  `tools/level_promotion_gate.py`). Prevents: a level move with no auditable trace. It refuses
  **unrecorded**, never **unpermitted** — that is the "record" in propose/record/act.
* **`one_way_door.classify_action`** as the SOLE enumeration of the four reserved real-world
  consequences. Prevents: real money spent, real people contacted, an irretractable public claim, a
  real person's safety.
* **The agent's own sandbox profile** staying director-console-only. Prevents: the machine widening
  what it is allowed to do on a real host. This is the one authentication convention that survives,
  and it is about the harness, not the simulation.

## Mechanised, so it cannot decay again (MAKE_IT_STICK)

Prose would have decayed exactly as the 29 July prose did. Three mechanisms:

1. **`action_needed.register_item` REFUSES** any ask outside the four reserved classes
   (`NotReservedForDirector`). The waiting-on-Rich queue can no longer refill with permission items.
   R15 both ways in `tests/background/test_action_needed.py`, using the three void asks verbatim.
2. **`_in_progress_minted_slugs` treats a permission-only blocker as self-drawable**, in token AND
   prose form, with the reserved half delegated to `one_way_door`. 15 of 23 parked mints became
   drawable on the spot. R15 both ways in `test_mint_permission_block_abolished.py`.
3. **`test_the_permission_surface_is_gone`** asserts the 17 deleted entry points stay deleted, so a
   future re-introduction fails a test rather than quietly re-gating a draw.

## Two findings this turned up

* **A gap in a WALL.** With every other gate deleted, `one_way_door` is now the only thing between
  the loop and real spending — and its REAL_MONEY patterns missed "authorise a real card payment for
  the paid feed subscription" and "pay for the subscription with the company card". Widened
  (detection-widening is safety-increasing). `invoice` and `direct debit` were deliberately NOT
  added: they are core simulated-domain vocabulary and would false-fire on the company's own work.
* **Keyword classifiers must read the ASK, not its rationale.** Run over the long how/why prose, the
  guard scored a level-ratification batch as an IRRETRACTABLE_PUBLIC_CLAIM ("publish-wiring is a
  named follow-on") and an authority-seam sign-off as LIVE_CREDENTIAL_EXPOSURE ("HMAC key"). Both
  now classify on `what` alone.

## Left open, deliberately

* **5 mints blocked with "reason unstated"** fail closed and stay parked. That is a doc-quality
  defect with its own mint (`unstated_reason_block_impossible`), not permission machinery.
* **R13 curriculum** (`value_chain_observation_window_cap`: "director for any named
  curriculum-difficulty value"). `VALUES_DECISION` is in `one_way_door._RELEASED_CATEGORIES` and
  THE_STANDARD's amendment says the machine owns its backlog — but curriculum authorship is a
  question about who writes the simulation's *content*, not about permission to build, so it was NOT
  swept in with the machinery. Flagged to the director rather than decided here.
