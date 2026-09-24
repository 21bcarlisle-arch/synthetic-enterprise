**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_and_landing_doors`

# The door that enacts the base winning is landed, and the remedy its sibling refusal prints named an index the tool it names refuses outright

Lane 0 item `build-the-door-that-enacts-head-wins-on-premise-population`. Two commits:
`c00d0fcbf` (the door) and the one carrying this note (the off-by-one).

## The door was already built and unlanded, not missing

The item said *"no existing door enacts that decision — `refresh_to_head` surveys and
`surgical_land` lands, neither discards."* That was true of HEAD and false of the tree.
`tools/refresh_to_head.py` in the shared working copy already carried `--base-wins` in full —
eight hunks, all additive against HEAD, mtime 2026-09-22 09:26 — together with seven controls in
`tests/tools/test_refresh_to_head.py`. A prior invocation built it, ran it (the preserved ref
`refs/preserved/refresh-to-head/premise-population-control-base-wins-20260922` is its own 09:28
output, over `tests/simulation/test_premise_population.py`) and never landed it. HEAD binds every
name it imports — `PREDATES`, `CLOCK`, `cuts_among`, `dead_among`, `landable_hunks`, `Dead` — so
it was not a draft against a dead API; it ran on the real tree on first ask.

So the work this turn owed was **landing it**, not building it. Mutation-proven first, in an
isolated worktree so no mutation touched the shared tree:

| mutation | legs that red |
|---|---|
| drop the `BASE_WINS_RULES` clock gate (`clock.rule in BASE_WINS_RULES` → `clock is not None`) | `..._refuses_a_copy_that_carries_SOME_of_its_landing` |
| let the flag reach a copy with a landable hunk (`if not landable:` → `if True:`) | 4 legs, including `test_every_verdict_in_the_partition_is_reachable` |
| default the flag on in `refresh()` | `..._the_flag_is_off_by_default_everywhere_the_tool_is_called` |

The ratchet red at commit time (`I001` 1305 vs baseline 1306) was **not this diff**: it is
`tests/tools/test_generate_maturity_map_data.py`, another lane's dirty file that fixed a violation
without lowering the baseline. HEAD alone measures 1306. `surgical_land` gates the tree the commit
*would* create, which is why it was the right door and the commit is green.

## The item's DONE condition is unreachable as written, and the reason is a rename

DONE was *"the file clearing the census by that door"*. `simulation/premise_population.py` does
not qualify for that door and should not:

```
gains: SETTLEMENT_CEILING_SLOPE_DIR, SETTLEMENT_CEILING_SLOPE_GLOB, WHOLE_RUN_FOOTPRINT,
       load_settlement_ceiling_slope, measured_whole_run_rss_curve
drops: PRODUCTION_PARENT_RSS_MB, WHOLE_RUN_FOOTPRINT_POPULATION, WHOLE_RUN_RSS_CURVE_GLOB,
       load_whole_run_rss_curve
```

Every gain is a **rename of a drop**: `WHOLE_RUN_FOOTPRINT` ↔ `WHOLE_RUN_FOOTPRINT_POPULATION`,
`load_settlement_ceiling_slope` ↔ `load_whole_run_rss_curve`, `SETTLEMENT_CEILING_SLOPE_GLOB` ↔
`WHOLE_RUN_RSS_CURVE_GLOB`. `WORKER_RESULT_THE_THREE_CLEARABLE_REVERTS_ARE_GONE_..._2026-09-22`
already said so in its point 3 and I am confirming it by measurement, not repeating it: the
symbol-set difference cannot see a rename, because a rename IS an addition plus a deletion, so the
copy grades `holder work` while being a REPLACEMENT in substance. That is why `--base-wins`
excludes `SUPPLIES_NEW` and why the exclusion is right in general and costly here: the "route that
keeps the work" it points at — `--keep 1,2` — installs `SETTLEMENT_CEILING_SLOPE_DIR/GLOB`
*alongside* HEAD's `WHOLE_RUN_RSS_CURVE_GLOB`, which is a second home for one quantity, and
neither of the two constants it adds has a reader in the bytes that selection builds (their
readers live in the hunks the selection drops). **Not built this turn, and named rather than
guessed at:** the general fix is a rename-aware gain count, and it is a judgement about when two
names are one subject, which is not something a set difference is entitled to decide.

## The off-by-one, which is the defect this turn found and fixed

`stale_copy_refusal.landable_hunks` returned **0-based** gids. Its own docstring said *"Numbering
is `isolate_hunks --survey`'s, so a caller can print an index a reader can then select"*, and the
comment directly beneath it said re-deriving a second numbering *"would mean this verdict cites an
index that the tool it sends the reader to does not agree with"*. Both sentences describe exactly
what the implementation did. `isolate_hunks` is internally consistent — `--survey` prints
`enumerate(groups, start=1)` and `--keep N` parses `int(sel) - 1` — so the shift was entirely in
the number the refusal printed.

Measured on the real tree, before the fix:

```
refresh_to_head  -> "...and land hunk(s) 0, 1 over HEAD"
isolate_hunks --keep 0 --keep 1  -> REFUSED: hunk 0 does not exist (4 in this file).
isolate_hunks --keep 1 --keep 2  -> kept 2 of 4 hunk(s)        <- what it meant
```

The loud failure is the better half. The quiet one is a reader who drops the impossible `0`, runs
`--keep 1` alone, lands **one** of the two hunks and believes they landed both.

**Why no control caught it for the function's whole life.**
`test_the_holder_work_verdict_names_a_hunk_the_landing_tool_agrees_with` is named for exactly this
claim and could not test it: it fed the cited indices straight into `reconstruct`, which is the
0-based internal the numbers came out of. It asked whether the numbering agrees with itself, and
the answer was yes throughout. Its other leg — `str(gid) in verdict.reason` — is satisfied by the
refusal printing the same wrong digits. This is the catalogue's *a control that stubs its own
subject* shape: the user-facing surface, `--keep`, was never typed at.

The new leg, `test_the_cited_hunks_are_selectable_by_the_tool_the_refusal_names`, runs
`isolate_hunks.build` with exactly the digits the refusal prints. Mutation-proven in both
directions, which matters because one direction is the bug and the other is the over-correction:

| mutation | result |
|---|---|
| `out.append(gid + 1)` → `out.append(gid)` | new leg reds (`SystemExit` at `isolate_hunks.py:202`) |
| `out.append(gid + 1)` → `out.append(gid + 2)` | new leg **and** the repaired sibling red |

The sibling is kept and repaired rather than deleted: it is still the only check that the
selection does not *lose* work, and its docstring now says which half of the question it answers
and which leg carries the other.

## What is still true of the census

`simulation/premise_population.py` remains in it, correctly refused, and the refusal now names a
remedy that runs. Whether that remedy should be *taken* is the rename question above, and it is a
decision, not a door. Nothing about this turn changes the seat's ruling that HEAD wins on that
file — it changes only what the machine is able to say about it.
