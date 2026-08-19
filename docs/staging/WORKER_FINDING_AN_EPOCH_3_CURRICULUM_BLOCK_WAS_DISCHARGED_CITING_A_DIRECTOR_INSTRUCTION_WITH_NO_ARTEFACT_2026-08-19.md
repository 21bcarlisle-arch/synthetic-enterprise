**Severity:** LATENT · **Lane:** H_harness

# An epoch-3 curriculum block was discharged citing a director instruction that is on no disk anywhere — and it reached `main` inside another lane's commit

**Found:** 2026-08-19, worker tick, while landing H27 Expert Hour #40 (`02ada0701`).
**Class:** `uncommitted_and_orphaned_work`.
**Measured at:** `02ada0701`. §1 and §2 are `observed-with-evidence` (R9); §3 is explicitly
`inferred` and is NOT asserted.
**Intended rank (P-1):** H_harness LATENT band. **QUEUED, not fixed on sight**
(SELF-INTERRUPT DISCIPLINE): the machine is not blocked, and the repair is not this tick's.

---

## 1. What is in the commit

`02ada0701` is an H27 HARDEN landing whose declared pathspec named seven paths. Its
`docs/design/maturity_map.yaml` hunk carries **three** atom edits, not one. Only the first is mine:

| hunk | edit | author |
|---|---|---|
| `H27_payment_belief_gap` | `simplifications_count` 45→47, `expert_hour.last` → 2026-08-19 | this tick |
| an epoch-2 CLV atom (map line ~4081) | `loop_stage` idle→build, `file_scope` `[]` → three `company/analytics/` paths | **not this tick** |
| `EP6` (map line ~4230) | `loop_stage` idle→build, `block_reason` → `block_reason_discharged` | **not this tick** |

The EP6 discharge text reads, verbatim from the committed tree:

> R13 curriculum sequencing, discharged by the director's instruction of 2026-08-19 naming EP6
> for promotion. The old reason required his word and said 'never proceed on silence'; this is
> not silence, it is the word.

## 2. The cited instruction is not on disk — observed, not inferred

Searched at `02ada0701`: `docs/staging/`, `docs/staging/done/`, every `DIRECTOR_*` and
`from_rich_*` artefact, and every `.md` under `docs/` matching `EP6`. **No artefact dated
2026-08-19 naming EP6 for promotion exists.** The only 2026-08-19 file mentioning `EP6` at all is
an unrelated worker finding. `docs/observability/gate_authorizations.jsonl`'s newest three rows are
`D45_the_id_a_citation_points_at`, `W2_17_dual_fuel_leg_clv_attribution` and
`OPS3_first_post_ruling_publish` — none is EP6.

This matters because **R13 is a WALL, not a dial**: the curriculum is the director's, difficulty
changes are named, versioned, director-authored artefacts, and the block being discharged said in
its own words *"never proceed on silence"*. A discharge whose evidence cannot be located is the
`the record outran its code` shape applied to authority instead of to code — which is the exact
class H27 Hour #40 had just finished repairing a control for, one atom over.

## 3. Why it is LATENT and not BLOCKING — the part that is inferred

**Inferred, and deliberately not asserted:** the likeliest explanation is a concurrent lane
mid-flight whose supporting director artefact is authored but not yet landed, not a fabricated
authority. Both hunks appeared in the working tree during this tick's 13-minute pre-commit gate —
they were absent when the map was checked for single-lane cleanliness ~40 minutes before the
commit, and present at commit time. Nothing here shows anyone acting on silence; it shows a claim
whose artefact a reader cannot reach. **It is filed so the discharge is checked, not so anyone is
accused.**

## 4. How it reached `main`, which is a RECURRENCE and is deliberately not re-filed

`tools/surgical_land` gates the tree the commit would create, then commits the **working tree** at
the named paths. A pathspec therefore protects other lanes from my *index*, and not at all from
what a concurrent writer puts in the *worktree* while the gate runs. That is already registered as
`docs/staging/WORKER_FINDING_A_PATHSPEC_PROTECTS_OTHER_LANES_FROM_MY_INDEX_BUT_NOT_FROM_MY_STALE_COPY_2026-08-18.md`
and it is left to that document rather than re-filed here. Recorded only as evidence that the class
is live and recurring: the map was verified single-lane before the gate and was **not** re-verified
in the second between the gate returning and the commit being written, which is the only window
that exists.

**Not reverted, and the reason is stated rather than glossed:** both swept hunks now exist ONLY in
`02ada0701`. Reverting them to purify this commit's scope would destroy another lane's uncommitted
work, which is a strictly worse outcome than a commit whose message under-describes its diff. The
sweep is disclosed here and in the tick's report instead.

## 5. Repair, when drawn

1. **Locate or author the EP6 instruction.** If the director's 2026-08-19 word exists, land it as
   an artefact so the discharge resolves its own pointer. If it does not, EP6's `loop_stage` goes
   back to `idle` and the original `block_reason` is restored.
2. **The class fix, and it is the R10 reading.** `block_reason_discharged` is a free-text field
   that names an authority nothing resolves — the same shape as a design register naming an absent
   file. A control should require that a discharged block's cited artefact EXIST and NAME the atom,
   so a hopeful pointer fails in the register that took credit for the discharge. The population is
   every `block_reason_discharged` in the map, not this one cell.
3. Sequence after (1): a control that greens by deleting the claim it cannot resolve would be worse
   than none.
