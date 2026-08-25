**Severity:** BLOCKING · **Lane:** W4_the_wall

**Rank:** after the current top item.

BLOCKING is the honest reading of the ruling's own definition rather than a self-flattering
one: the maturity map is the instrument the picker reads, and for this atom it is
untrustworthy in the specific way that matters — it reports a BUILD-complete, published atom
as parked, blocked and owning no files. The lane-scoped consequence is correct and intended:
no new level-raise in `W4_the_wall` should be recorded until EP13's entry describes the tree,
because the ledger the raise would be written into is the one this finding says is not being
reached. No published *figure* is wrong — the carbon numbers on the live site are the ones
this atom's code produces — so the scope is the instrument, not the output.

# EP13's map entry says parked-and-unbuilt while the site publishes the atom, and the correction cannot land behind EP1

All claims below are `observed-with-evidence` unless labelled `inferred` (R9).

## The state, at HEAD

`8f15b78c1` ("carbon: the number this company exists to produce now exists") committed
EP13_adapter_carbon_intensity's entire code deliverable — 15 files, 13,088 insertions,
including `sim/grid_carbon_intensity.py`, `docs/market_data/grid_intensity_feed.json`,
`site/data/explore_carbon.json` and the Explore page that renders it.

The atom's own map entry did not go with it. At HEAD, `docs/design/maturity_map.yaml` still says:

    level_current: 0
    loop_stage: idle
    block_reason: "director-reserved curriculum sequencing (R13). Epoch-3 commitment set
                   (ruling §1); pull-forward is proposal-only (§3)."
    file_scope: []

`docs/observability/gate_authorizations.jsonl` at HEAD carries **zero** EP13 records
(`git show HEAD:docs/observability/gate_authorizations.jsonl | grep -c EP13` → 0).

So the map describes an atom that is parked, blocked on a director-reserved curriculum
question, unbuilt, and owning no files — while the live site publishes its output and the
block was in fact discharged by the director's own instruction of 2026-08-25, quoted at
`docs/staging/DIRECTOR_CONSOLE_2026-08-25.md:264` ("Wire the carbon ledger to live meter reads
and grid intensity, publish it with its provenance, and say plainly what it does and does not
yet include").

**Why this is HIGH and not bookkeeping:** `loop_stage: idle` + a `block_reason` is what the
draw reads. The atom is BUILD-complete at L2 and will keep presenting to the picker as
director-blocked and parked, which is the shape that causes an atom to be silently skipped
(`docs/design/MATURITY_MAP.md` §9). It also makes `file_scope: []` — the condition
`tools/file_scope_generated_paths.py` was written about, where an atom is never drawn because
it declares no ground.

## The correction is written and is held out of its commit

Prepared and verified, not committed:

- `file_scope` extended to the nine files the atom actually owns, including the two new ones.
- The L2 rationale rewritten to record that of its three stated reasons, the **coupled-triad
  rung is now CLOSED** — `sim/neso_carbon_intensity.py` is the independent truth series — one
  is quantified but unfixed (no coal, no interconnector imports), and one is untouched (no
  Expert Hour, a HARDEN draw).
- `level_current: 2`, `loop_stage: build`, `block_reason: null`, and the L0→L2
  self-certification line for `gate_authorizations.jsonl` (R16).

It cannot land. Touching `docs/design/maturity_map.yaml` selects
`tests/design/test_simplifications_store.py`, which is **RED AT HEAD** and refusing every lane:

    EP1_clv_three_horizon:              map simplifications_count=18 != store file count=16
    PB3_book_growth_as_earned_outcome:  map simplifications_count=3  != store file count=2

Verified pre-existing rather than assumed: `git archive HEAD | tar -x` into a clean directory
and running the test there fails identically, with no working-tree state involved.

## Why EP1's half is not landable by this seat

A simplifications-store roll is a multi-file atomic write, and the repair has a staircase of
three refusals, each only visible after the previous one is cleared:

1. **count red** — EP1's archive chunks `.009`/`.010` are staged but uncommitted.
2. Commit those chunks alone → **`test_no_entry_is_in_both_the_archive_and_the_live_file`**:
   2 entries in both. The live file's *deletion* of them is the roll's other half.
3. Commit the live file too → **`record_landing_claim_check`** refuses. That file claims five
   symbols landed which no tree carries: `ep1_series_provenance`, `select_belief`,
   `flatten_ep1_series` in `tools/couple_clv.py`, `build_three_horizon_clv_snapshots` in
   `company/analytics/customer_value_view.py`, `three_horizon_clv_snapshots` in
   `simulation/run_phase4c_on_phase2b.py`. They exist only in another lane's **uncommitted
   working tree**.

Clearing step 3 means adopting a foreign in-flight build unreviewed — including
`company/analytics/customer_value_view.py`, which `sim_runner` reads from the working tree.
The alternative, correcting EP1's map count from 18 down to 16, would be making a red test
green by moving the number, which CLAUDE.md forbids in the same breath as the CLAUDE.md size
limit. Neither is this seat's call to make unilaterally.

Per the standing rule ([[when the co-blocking atom's store repair is itself unlandable]]),
the code landed without its register entry and this finding records the gap.

## What unblocks it

**Recommendation, and the default if nobody objects:** the lane holding EP1's uncommitted
`three_horizon_clv` build lands it — that single act clears step 3, then the roll and both
map counts land together, and EP13's map correction follows in the next tick. That lane's own
map note already says pass 18 "finished the code and ended without committing it", so this is
the second consecutive pass where EP1's uncommitted tree has wedged unrelated lanes, which
makes it an **R3 two-strike candidate**: the mechanism to redesign is a store whose register
entry can be written before the code it claims exists.

Second option if that build is not ready: split EP1's live-file entry so the `LANDED:` claims
are removed from the uncommitted note, land the roll, and re-add the claims when the code
lands. Cheaper, but it edits another lane's record.

## Evidence

- `git show --stat 8f15b78c1` — 15 files, EP13's code, no `maturity_map.yaml`.
- `git show HEAD:docs/design/maturity_map.yaml | grep -A 22 '^- id: EP13'` — level 0, idle,
  block_reason set, `file_scope: []`.
- `git archive HEAD | tar -x -C /tmp/gh && cd /tmp/gh && python3 -m pytest
  tests/design/test_simplifications_store.py::test_counts_match_file_contents` — fails on EP1
  and PB3 with no working-tree state.
- Landing attempts and their distinct refusals are quoted in full in the three
  `surgical_land` runs of this tick.

---

## Update, 2026-08-25 09:05 UTC — the recommended unblock ran, and its WRAPPER killed it

`observed-with-evidence`. The recommendation above ("the lane holding EP1's uncommitted
`three_horizon_clv` build lands it") was in fact attempted, and was in flight while this finding
was being drawn. PID 1036229, started 07:57:33 UTC:

    timeout 4000 python3 -m tools.surgical_land -m "$(cat …/msg_ep1.txt)" -- \
      tools/couple_clv.py company/analytics/customer_value_view.py \
      company/interfaces/customer_value.py simulation/run_phase4c_on_phase2b.py \
      saas/reporting/annual_report.py docs/design/simplifications/EP1_clv_three_horizon.yaml \
      …archive/EP1_clv_three_horizon.009.yaml …archive/EP1_clv_three_horizon.010.yaml \
      docs/design/simplifications/PB3_book_growth_as_earned_outcome.yaml …4 test files

Its pathspec was RIGHT — it carried both halves of the roll and both wedged atoms, EP1 and PB3.
It ran for 66 minutes and its entire recorded output is one word:

    Terminated                 timeout 4000 python3 -m tools.surgical_land …

**It was not refused. No test went red. `timeout 4000` reached its limit and killed the gate
mid-run**, and because `timeout` kills rather than reports, the landing left no error, no partial
commit and no diagnosis — the 795-byte task output above is the whole record. HEAD is unchanged
at `0dc6e252f`, and every claim in the body of this finding still holds.

**This is the third consecutive pass EP1's uncommitted tree has wedged unrelated lanes, and the
mechanism is now identified and is not the one this finding first proposed.** Pass 18 ended
without committing; pass 19 was refused by the per-atom map budget; this pass was killed by its
own wrapper. The R3 candidate is therefore narrower and more fixable than "a store whose register
entry can be written before the code it claims exists": **the landing command is wrapped in a
timeout shorter than the gate it is wrapping.** EP1's pathspec selects the company analytics,
seam, run_phase4c and annual-report suites; that gate demonstrably needs more than 66 minutes,
so any wrapper below ~90 minutes converts a green gate into a silent no-op. This is the known
class [[a timeout wrapper kills surgical_land mid-gate and leaves no error]], recurring with a
measured duration attached for the first time.

**Recommendation, and the default if nobody objects:** re-run that exact command with **no
`timeout` wrapper at all** — `surgical_land` already retries a lost HEAD race by itself and
already has its own lock handling, so the wrapper adds no safety and removes the diagnosis. It
must be run by a seat that can stay with it to completion rather than at the tail of a bounded
tick, because the failure mode being fixed is precisely a landing that is cut off partway.

Not done by this seat, and why: adopting another lane's 722-line uncommitted build across
`company/`, `tools/`, `simulation/` and `saas/` unreviewed is the call this finding already
declined to make unilaterally, and a >66-minute landing cannot be verified inside a bounded
tick — starting one and exiting would produce a fourth unattended attempt, which is the defect
rather than the fix.

