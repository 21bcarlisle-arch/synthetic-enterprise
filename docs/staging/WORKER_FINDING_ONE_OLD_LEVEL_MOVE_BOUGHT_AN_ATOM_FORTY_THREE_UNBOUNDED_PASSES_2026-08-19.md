**Severity:** LATENT · **Lane:** H_harness
**Discharged:** `tests/tools/test_discovery_pass_ceiling.py::test_MUTATION_one_old_level_move_does_not_buy_unlimited_further_passes`,
`::test_the_boundary_is_the_day_of_the_move_and_both_sides_are_asserted`,
`::test_MUTATION_FAIL_CLOSED_an_undated_pass_counts_toward_saturation`,
`::test_a_date_deep_in_the_body_is_not_mistaken_for_the_passs_own_date`,
`tools/discovery_pass_ceiling.py` — the predicate now asks how many passes an atom has taken
SINCE it last moved a level, so a single historic move no longer buys unlimited further
passes; 17 passed in 165s. What is NOT discharged is the wiring, recorded in full below.

# FINDING — the pass ceiling counted every move an atom had ever made, so one old move made it permanently unsaturatable

**Found by:** the `H27_payment_belief_gap` self-refill HARDEN draw, 2026-08-19, on the tick
after the ceiling landed. The atom the draw handed me is the one the ceiling should have
refused to hand anyone.

## Observed, with evidence

Every claim here is `observed-with-evidence` (R9), read off the live tree.

`tools/discovery_pass_ceiling.py` shipped this morning against the director's ruling — *"make
it impossible for the system to run indefinitely on work that cannot change its own state"* —
with the saturation predicate:

```python
"saturated": passes >= ceiling and moved == 0,   # `moved` = LIFETIME level moves
```

`moved` is the count of `LEVEL_UP` rows the atom has in `gate_authorizations.jsonl` **over all
time**. So an atom that moved a level once, at any point in its history, satisfies `moved == 0`
never again and can take passes for ever.

**The worst case in the project was invisible to it.** `H27_payment_belief_gap`, surveyed
before the fix:

| atom | passes | lifetime moves | saturated (as shipped) |
|---|---|---|---|
| `H27_payment_belief_gap` | 48 | 1 (`ts` 1786200106 → 2026-08-08) | **False** |

43 of those 48 passes are dated after that move. The atom's own store says so in words: its
latest entry opens *"FORTY-FIRST HOUR … THE LEVEL DOES NOT MOVE, and this is the THIRTEENTH
consecutive Hour to find a real flaw in the instrument."* Thirteen consecutive passes, level
pinned at 2/3, and the control written that morning to end exactly this read it as healthy.

**The control's own R15 proof was holding the blindness in place.** `test_every_saturated_atom_
is_either_awaiting_its_decision_or_has_had_one` asserted `r["level_moves"] == 0` of every
saturated row. Any correct reading — an atom with one old move and forty-three passes since —
would have gone red on that assertion. The test could not have been written by someone who
believed the predicate was wrong, which is precisely why it is worth recording: this is the
second time that one test has pinned the defect it was meant to catch (its docstring already
records the first).

## The class

R15 FAIL-OPEN: *passes on missing/zero/empty* — here, passes on the state it exists to catch,
because the condition it tests (`moved == 0`) is not the condition that matters (*moved since
when?*). The class member trait is a control keyed on a LIFETIME fact where the live question
is a SINCE fact — the same shape as a ratchet that counts total coverage rather than coverage
of the current subject.

`background.finding_classes --list` reports this document as `unclassed`, because membership is
keyed on the TITLE alone and this title carries none of the class's vocabulary. The
classification is wrong and I am leaving it visible rather than renaming the file to satisfy the
matcher: a consolidation whose membership can be changed by a synonym is worth catching with an
instance in hand, and this is that instance.

## The repair, and what it moves

The question is now "how many passes SINCE the atom last moved a level", from two independent
sources: the ledger dates the move (R16), and each pass dates itself in its own text (1,075 of
the live store's 1,079 entries carry a date in their first 400 characters). **An undated pass
counts toward saturation** — fail-closed, in the same direction as everything else in the
module, because a pass nobody can place in time is not evidence of productivity; and the scan
window is bounded so a date quoted in a body cannot re-date the pass.

Corrected, the saturated set moves **13 → 23 of the 112 atoms below target**:

```
  since passes  moves  stage    level  atom
     43     48      1  harden     2/3  H27_payment_belief_gap
     18     18      1  build      2/3  SITE2_two_sided_wall_exhibit
      8      9      1  idle       1/3  H_forward_discovery_draw
      8      8      1  harden     2/3  W3_1b_intra_year_price_cap_granularity
      7      7      1  harden     2/3  D_money_boundary_reconciliation
      7      7      1  build      2/3  SP3_size_and_clone_ratchet
      6      6      1  harden     2/3  W2_payment_channel_dd_consistency_invariant
      5     15      1  build      2/3  SITE1_expert_doors
      5     11      1  build      1/3  EP1_clv_three_horizon
      5      7      1  harden     2/3  HX2_stall_set_coverage_verdict
```

(the ten newly saturated; the thirteen already saturated are unchanged, since an atom that
never moved counts every pass exactly as before.)

## What is NOT repaired, and it is the larger half

**The corrected reading barely reaches a draw.** `saturated_ids()` has one consumer,
`supervisor._idle_discover_frame_draw`, which feeds only on `idle` atoms. Of the ten newly
saturated, **one is idle** (`H_forward_discovery_draw`); the other nine are `build` or
`harden`, where nothing consults the ceiling. `H27_payment_belief_gap` is therefore still fully
drawable by the below-target core draw, by the same rung that drew it into this tick, and a
forty-fourth pass since its last move is available right now.

That is a real decision and I am not taking it inside this tick, for a stated reason rather
than caution: gating the CORE draw on saturation is a Rule-0 hazard in a way the discovery
tier was not. Discovery could close safely because BUILD and HARDEN stayed open beneath it —
the loop was pushed toward state-changing work. Closing the core draw has nothing beneath it,
and for a `build`-stage atom drawing it again IS the promote path the ceiling asks for, so a
naive exclusion would refuse exactly the answer it demands.

**What I recommend, and would take on the next tick:** gate the **harden** rung, not the build
rung, on the ceiling. Six of the ten newly saturated are `harden` at 2/3 — an atom hardening at
level 2 for its eighth, thirteenth, forty-third pass without certifying level 3 is the exact
shape of the ruling, whereas a `build` draw at least attempts the move. `EP1` and `SITE1` show
the distinction working the other way: 15 and 11 lifetime passes, but only 5 since their last
move, i.e. atoms that were investigated hard and then actually moved.

**Not done in this tick, deliberately:** no entry was appended to `H27_payment_belief_gap`'s
own store. This pass touched nothing in that atom's `file_scope` (`tools/couple_w2_11_d5.py`
and its test) — the defect was in the machinery that handed the atom over, not in H27's
instrument — and the store append is coupled to a `simplifications_count` edit in
`maturity_map.yaml`, which is carrying another lane's uncommitted work in this shared tree. A
forty-ninth H27 entry recording that H27 was not worked would have been the mirror of the
defect above.
