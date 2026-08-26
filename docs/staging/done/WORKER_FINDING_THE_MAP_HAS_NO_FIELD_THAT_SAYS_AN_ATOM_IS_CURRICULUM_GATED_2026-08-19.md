**Severity:** LATENT · **Lane:** H_harness

# The map has no field that says an atom is curriculum-gated, so a hand-deleted park is byte-identical to an authorised release

**Found:** 2026-08-19, worker tick, while discharging
`WORKER_FINDING_AN_EPOCH_3_CURRICULUM_BLOCK_WAS_DISCHARGED_CITING_A_DIRECTOR_INSTRUCTION_WITH_NO_ARTEFACT_2026-08-19.md`
(that document's §5 step 3 residual, queued there rather than invented on sight).
**Class:** `controls_that_cannot_fail`. **Measured at:** HEAD after the EP6 restoration.
Everything below is `observed-with-evidence` (R9).
**Intended rank (P-1):** H_harness LATENT band. **QUEUED, not fixed** — SELF-INTERRUPT
DISCIPLINE; the machine is not blocked and the shipped control covers the shape that was
actually exploited.

---

## 1. The hole, precisely

`background.pull_forward_proposal.apply_release` — the only sanctioned way to move a
curriculum-parked atom into the draw — sets `loop_stage: build` and **deletes**
`block_reason`. It refuses without the director's word on disk, and that refusal is
mutation-proven.

The new `discharge_violations()` control (landed this tick) catches a park *renamed* to a
discharge field, in any spelling, because it keys on the field NAME. What neither can see:

> an atom whose `block_reason` is **deleted by hand** while `loop_stage` is set to `build`
> is byte-identical to one `apply_release` released honestly.

Both end states are `loop_stage: build` with no `block_reason`. There is nothing left in the
map to distinguish "the director said go" from "somebody removed the sentence".

## 2. Why the obvious keys do not work — measured, not asserted

Three candidate discriminators were measured on the live map (316 atoms) and all three are
the wrong population:

| candidate key | measurement at HEAD | verdict |
|---|---|---|
| `epoch >= 3` means curriculum-gated | **109 of 164** epoch-3+ atoms are already unparked | `epoch` is the narrative arc label, not a gate |
| `provenance: director_ruling` | held by SITE2/3/4/7/12, OPS2, OPS3, FUT1-3 — none curriculum-gated | means "this atom came from a ruling", not "this atom is gated" |
| the free-text `block_reason` itself | 41 present, 11 of them EMPTY | `candidates()` already refuses to match on this prose, correctly: an under-reporting index authorises its own omissions |

So the gate is **prose**, and prose is exactly what the shipped module declined to key on.

## 3. Repair, when drawn

1. A **typed facet** on the atom — e.g. `curriculum_gated: true` — set once for the
   commitment-set atoms the founding ruling §1 actually named (`DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08`),
   and never removed by the release. `apply_release` then clears `block_reason` while the
   facet persists, so "gated and released" stays distinguishable from "never gated".
2. With that facet, the control's strong leg becomes available and is no longer the wrong
   population: **a `curriculum_gated` atom that is not parked must have a resolvable director
   release.** That leg cannot be greened by deleting a claim, which is the property §3 of the
   originating finding asked for and which this tick could not deliver.
3. Sequence AFTER (1). Enforcing before the facet exists means enforcing over `epoch`, which
   is red on 109 atoms belonging to other lanes.

## 4. Why this is LATENT and not blocking

The route actually taken on 2026-08-19 was the *renamed-field* route, and that route is now
closed and mutation-proven. The hand-deletion route is unexercised: no atom at HEAD carries a
discharge-shaped field (population 0), and the `stale_park_cells` observation (10 at HEAD)
gives a partial view of parks that outlived their park. This is filed so the residual is
visible in the register, not because anything is currently wrong.
