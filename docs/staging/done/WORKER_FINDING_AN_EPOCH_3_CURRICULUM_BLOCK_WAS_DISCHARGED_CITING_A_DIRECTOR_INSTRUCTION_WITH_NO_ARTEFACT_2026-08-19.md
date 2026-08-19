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

---

## 6. DISCHARGED 2026-08-19 (worker tick) — the instruction does not exist, and the cell is restored

**Step 1 ran first, as §5 sequenced it, and the answer is negative on every channel.** The
search this document could not complete is now complete, and it was widened past `docs/`,
which is where §2 stopped:

| channel | result |
|---|---|
| `docs/staging/`, `in_progress/`, `done/` | no 2026-08-19 artefact names EP6 |
| `from_rich_*.md` (ntfy IS the director) | newest is `from_rich_20260803_093552.md` |
| private ops repo `director_input_log.md` + `ntfy-mirror.md` | EP6 appears **only in `[OUT]` lines** — my own outbound. Newest `[IN]` of any date: **2026-08-03 09:35:50 UTC** |
| `gate_authorizations.jsonl` | newest three are D45, W2_17, OPS3 |

**Measured by the shipped door rather than by grep, which is the evidence that matters:**
`background.pull_forward_proposal.release_verdict("EP6_wall_protocol_typing")` returns
`released: False`, `reason: "PENDING — no director word on disk names this atom with a
release"`, over **381 director sources with `unreadable_sources: []`** — so this is a
COMPLETE scan reporting silence, not a blind one reporting nothing. That module is
fail-closed by construction and would have said so.

**And the transition never went through the door at all — this is observable, not inferred.**
`apply_release` DELETES `block_reason` on a real release. It has never written
`block_reason_discharged`, and neither has anything else: that identifier appears in **zero
`.py` files** in the repo. The field was hand-authored in a spelling nothing reads.

**ACTED (§5 step 1): EP6 restored** to `loop_stage: idle` with its original `block_reason`
byte-restored from `02ada0701^`. `file_scope` was deliberately LEFT as the sweep set it —
`file_scope` declares ownership, not the gate, and framing it on a parked atom is
DISCOVER/FRAME work the epoch gate explicitly permits. Only the wall crossing is reversed.

**The sibling hunk is NOT reverted, and the distinction is the substance.** `EP1_clv_three_
horizon` is **epoch 2**, whose gate per the founding ruling §1 is the *ruled*
`EPOCH2_EVIDENCE_PASS` (archived in `docs/staging/done/`), not a director unblock — 92 of 133
epoch-2 atoms are already unparked and EP1's own `block_reason` was empty. Nothing was
crossed, so it is RECORDED rather than reverted.

**A third consequence of the same sweep, which this document had not found:** EP1's unparking
left `test_blocked_atom_visibility.py`'s frozen `UNPARKED_SUBJECT_COVERAGE` **RED at HEAD**
since `02ada0701`. Verified as pre-existing and not mine — the `clv` unparked set reads
`[EP1, W2_17]` identically at HEAD and in the worktree, and `[W2_17]` at `02ada0701^`. The
control was doing exactly its job; it is greened by writing the ledger line its own docstring
asks for, with the reason above.

**Step 2 (the R10 class fix) is BUILT** — `pull_forward_proposal.discharge_violations()`, see
§7. **Step 3's residual is QUEUED, not invented:**
`WORKER_FINDING_THE_MAP_HAS_NO_FIELD_THAT_SAYS_AN_ATOM_IS_CURRICULUM_GATED_2026-08-19.md`.

## 7. The control that now exists, and the two legs measured and REJECTED

`discharge_violations()` scans **all 316 atoms** for any `block_reason*` field and raises:

- `unknown_block_field` — any spelling outside `LEGAL_BLOCK_FIELDS = {"block_reason"}`. This
  keys on the field NAME, so **the control cannot be greened by rewording the claim**; the
  only escape is deleting the field, which returns the atom to a legal state.
- `unresolvable_discharge` — such a field exists AND `release_verdict` finds no director word
  naming the atom. This reuses the door's own recogniser rather than inventing a second
  authority channel (CLAUDE.md: *do not invent authority checks*).

**Two plausible legs were measured and rejected, which is the part worth keeping:**
- *"epoch ≥ 3 and not parked must have a director release"* — **109 of 164** epoch-3+ atoms
  are already drawn at HEAD. `epoch` is the NARRATIVE arc label, not the gate. This leg reads
  as the strongest one available and would have landed red on 109 atoms belonging to other
  lanes.
- *"a live `block_reason` on a drawn atom"* — 10 at HEAD, none of them this defect; reported
  as `stale_park_cells`, never enforced. A further 11 carry the key EMPTY, which is the
  separate, already-gated `unstated_reason_block` class and is deliberately counted apart, so
  the reported number means one thing.

**R15, proven RED on the real tree before the repair, not on a fixture:** the control named
`EP6_wall_protocol_typing`, its field, and quoted the unresolvable claim verbatim, over 316
atoms. After the repair: population 0, 0 violations. Because that live population is
legitimately **zero** — a wall enforced over a rotation set of zero being this project's own
recurring defect — the fire is pinned by mutation instead: the defect reproduced, three
rewordings, an unreadable map (fail-closed to a violation, never an empty pass), a blind scan,
and the honest-door null in which `apply_release` leaves nothing to find. 11 new tests,
**46 passed** in the atom's own file, 91 across the three affected suites.

**WHAT THIS CONTROL CANNOT SEE, stated rather than glossed:** an atom whose `block_reason` is
simply DELETED by hand with `loop_stage` set to `build` is byte-indistinguishable from one the
door released honestly. The map carries no typed field saying "this atom is curriculum-gated",
and `candidates()` already refuses to match on the free-text gate for good reason. That is
§5's residual, and it is queued rather than invented here.
