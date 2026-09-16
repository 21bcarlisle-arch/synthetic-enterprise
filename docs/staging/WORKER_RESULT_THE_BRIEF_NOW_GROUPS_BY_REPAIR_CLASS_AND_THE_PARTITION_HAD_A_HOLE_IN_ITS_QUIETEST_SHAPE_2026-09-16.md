**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the ungradable split exists and the brief does not read it)

# The brief now groups by repair class, and the hole in the partition was in its quietest shape

**2026-09-16, scheduled tick, worker seat.** The direction had three parts. All three are built and
landed. One factual claim in the item is refuted and is recorded here beside the work rather than
quietly dropped.

## What was wrong, and it was mine

`tools/level_zero_contradicted_by_its_own_controls.ungradable_causes` already resolved the
ungradable rows into repair classes — the split I spent the previous stretch arguing for. Its only
consumer, `background/delivery_seat._by_reason`, bucketed on `u["reason"]`, which is the SHAPE of
the row's `file_scope` and carries no repair. So the split existed in the producer and the brief
printed the undifferentiated count anyway: a repair landing in the producer while the reader gets
the old answer, which is this project's most-repeated defect, committed against my own census.

## Part one — the brief reads the split

`_by_reason` is replaced by `_by_cause`, keyed on `causes[].cause`. The brief field is **renamed**
(`ungradable_named` → `ungradable_by_cause`) rather than reused: same key with different contents
is how a downstream reader comes to be quietly wrong about what it is reading.

A row with several causes appears under each, because `A51` has a pointer to repoint *and* a
control to write and a single primary cause would send the reader to repoint the pointer and call
the row repaired. The group sizes therefore sum to more than the row count, on purpose — they are
repairs owed, not a partition of rows — so `ungradable_owing_repair_count` counts distinct rows.

## Part two — the rows owing no repair are reported apart

`CAUSES_OWING_NO_REPAIR` is named in the module that defines the cause vocabulary, not at each
reader: "which of these is not a defect" is a judgement the producer owes its consumers, and a
caller left to decide it will decide differently from the next caller. `ungradable_owing_no_repair`
lists them; `ungradable_by_cause` excludes them; `ungradable_count` is **unchanged**, because
netting them out of the headline would be a smaller number nobody could check against the check's
own output.

## Part three — five rows carried no cause at all, and the old test defended it

`ungradable_causes` returned `[]` for a row whose every named path is on disk and one of which is a
runnable control. `assess`'s own comment argued this was the honest answer, because a spent budget
or a timeout "says something about the pass, not about the state of the work" — and
`test_an_instrument_state_carries_NO_cause_because_it_says_nothing_about_the_work` asserted it.

That was half right and the wrong half was expensive. **"The refusal is in the pass, not in the
row" is a reading**, and returning nothing made those rows invisible to any consumer grouping by
cause — a fail-silent in the control built to end an undifferentiated count, defended by its own
test. The flattering half of *a mutation that does not fire is either a missing test or an
equivalence*.

They now carry `NOTHING_IN_THE_ROW`, whose repair is "re-run this row ALONE (`--atom <id>`) and
read its reason line — do not edit `file_scope`, because nothing in it is wrong". The old test is
corrected in place, beside the claim it replaces, and keeps the leg that mattered: no cause here
may instruct a repair to the row.

`ungradable_causes` is now total. `test_EVERY_ungradable_row_carries_at_least_one_cause` spans all
four refusal shapes `assess` can emit, because the hole was in the one nobody thought to check.

## The measurement, on the live map

| | rows |
|---|---|
| ungradable (headline, unchanged) | **30** |
| owing a repair | **27** |
| owing no repair (honestly unbuilt) | **3** |
| carrying no cause at all | **0** (was 5) |

By repair class — 29 repairs over 27 rows, because `C_supply_start_consumer_routing` and
`SITE3_wall_exhibit_url_rename` each carry two:

| cause | rows |
|---|---|
| the control that would grade it was never written | 17 |
| the refusal came from the pass, not the row | 6 |
| every named entry is a directory | 4 |
| a named path rotted | 2 |

Owing no repair: `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement`,
`G15_forward_curve_series_to_backtest_hedging_by_physics`,
`W1_28_the_weather_partition_is_joint_over_a_stock_with_varying_fabric`.

## The item's own claim that is refuted

> *"the defect count falls to 26 by reporting the four unbuilt rows apart, which clears the
> 27-or-fewer test I set myself"*

Both halves are wrong, and neither changes the work.

1. **There is no 27-or-fewer test.** Grepped across `tests/`, `tools/`, `docs/` and the map: no
   numeric bar on the ungradable census exists anywhere in this tree. The nearest thing is
   `test_ungradable_build_rows_allowlist_only_shrinks`, a `<= 24` ratchet on a *different*
   partition (rows naming no `test_*.py` at all) which this change does not touch.
2. **Three rows owe no repair, not four**, so the count is **27**, not 26.

Filed rather than fixed: nothing here asks for a bar to be invented. A count that has just changed
meaning is the worst possible moment to freeze it, and `ungradable_owing_repair_count` is now a
quantity a ratchet could honestly be keyed to once it has moved under its own definition a few
times.

## Controls, mutation-proven

Five mutations were applied to the live modules and each fired on the leg written for it:

| mutation | fires |
|---|---|
| delete the `if not out` tail in `ungradable_causes` | 3 tests |
| group `_by_cause` on `u["reason"]` | 4 tests |
| drop the `CAUSES_OWING_NO_REPAIR` filter | 2 tests |
| count repairs instead of rows | 1 test |
| drop the `or [NO_CAUSE_RECORDED]` fallback | 1 test |

`test_the_brief_groups_by_CAUSE_and_not_by_the_REASON_SHAPE_FIELD` is the one that had to be built
carefully: its fixture gives three rows **one** reason and **three** causes, so grouping by reason
collapses them to a single heading. A fixture where the two groupings agree would pass on the
defect.
