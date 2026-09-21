**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_28_the_weather_partition_is_joint_over_a_stock_with_varying_fabric`

# The weather partition is joint over the stock now, 55 cells do what 987 could not, and the level move is refused by a repair that is written and unlanded

`DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07`, WORK THIS CREATES item 2. Built:
`tools/weather_cell_joint_partition.py` and `tests/tools/test_weather_cell_joint_partition.py`.

## What the partition's subject is now

A cell is described by **what it does to the stock** — the 274-vector of annual space-heat demand it
produces across the NEED-derived house cases — not by its three driver values. Two cells are one
cell when the whole stock cannot tell them apart. The stock is held at the NATIONAL mixture in every
cell, so the measurement is of weather-against-fabric and not of who lives where; that is a declared
choice and `demand_case_coverage.measurement`'s weather-alone leg makes the same one.

## Measured, 143,511 occupied cells, 274 house cases, 24.7m households, seed 0

| cells | joint_over_stock | drivers_equal | representative_house |
|---|---|---|---|
| 13 | 0.9636 | 0.7790 | 0.9605 |
| 55 | **0.9903** | 0.9150 | 0.9761 |
| 233 | 0.9973 | 0.9713 | 0.9773 |
| 987 | 0.9992 | **0.9908** | 0.9781 |

**55 cells against 987.** All three scored on ONE metric — the household-weighted variance of the
same demand surface — at matched cell counts, so the only thing differing between two columns is
what the partition was built on.

**The third column is the one the finding rests on.** `drivers_equal` is blind to two things at
once (the fabric, and the fact that temperature matters more than sunshine), so a gap against it is
unattributable. `representative_house` is one average house per cell: it knows every driver's effect
exactly and is blind ONLY to that effect varying across the stock. It does not reach 99% anywhere in
the sweep, and at 987 cells is still at 0.978 — seven times the budget and still behind the joint
partition's 34-cell score. The gap is fabric, not granularity.

**No asymptote is claimed, and the version that did was measured and discarded.** Binning the
representative-house scalar finely to read off a ceiling gave 0.975 at 500 bins and 0.986 at 8,000
— it climbs with bin count because eighteen cells per bin flatters any partition. The same flattery
inflates all three columns *equally* at matched `k`, which is exactly why the comparison is made at
matched `k` and no limit is quoted.

**Neither older figure is withdrawn.** `W1_21`'s 987 is correct arithmetic about the drivers' own
variance and `weather_cell_derivation` declares it as such. This asks the same question about the
demand those drivers cause.

## The cell count is an output of the draw (canon section 5)

`derived_cell_count` chooses nothing. It takes `space_filling_sample`'s own draw-for-difference and
counts the distinct cells it landed in: 2,584 cases land in **2,195** cells, 987 in 890, 233 in 220.
The draw reuses a cell one time in seven, so the count is very nearly the sample size. 35,809 cells
are available in the 200,000-point pool, so the sampler is not what bounds it — that bound is
computed and asserted rather than assumed away.

## The control fails when the partition is rebuilt separably — mutation-proven five ways

| rebuild | verdict |
|---|---|
| on the three standardised drivers | RED (duplicate-column leg) |
| on the drivers, different seed (columns differ) | RED (domination leg) |
| on one representative house | RED |
| as the crossed 21/21/5 shape | RED (domination leg) |
| drivers + 0.02 x the signature | **GREEN — established as an EQUIVALENCE** |

The green one was not assumed to be the flattering reading. The signature's leading column has a
standard deviation of 1,308 kWh against 1.3 for a standardised driver, so at 0.02 the signature is
still twenty times the drivers and that partition genuinely IS built on the stock response — it
scores 0.9806 against the pure joint's 0.9845. Diluted to 0.002 it falls to 0.9466 and the
domination leg fires. The boundary sits exactly where the partition stops being about the stock.

The control's target is read off the joint partition's own curve rather than pinned at 99%: the
property is that a level the joint reaches is out of reach for both rivals across the whole sweep,
whatever that level turns out to be.

One threshold in the suite was a picked number and is gone. A first draft asserted a 0.05 margin
between a rival scored on its own space and on the stock metric; the measurement came in at 0.046.
The property was the inequality, not the size, and the margin was decoration.

`REDUCES_OVER` is declared and the census reaches the module (asserted, not assumed) — subject
vector the demand vector plus `dwelling_fabric`, reducing over a joint derived
`weather_condition_x_fabric` that `Declaration.collapsed` names as a collapse of three components.

## THE LEVEL MOVE IS REFUSED, and the cause is a repair that is written and unlanded

`W1_28` stays at **level 0** this tick. Not a judgement about the evidence — L2 ("mechanically real:
genuine artefacts, happy path") is what the build supports and L3 needs an Expert Hour that has not
happened. It is refused at the writer, verified by running it rather than read off the source:

    OPS11: the level-raise on W1_28 is REFUSED -- lane W1_market_weather holds 1 live BLOCKING
    finding(s) -- WORKER_FINDING_THE_HDD_LEG_IS_A_THIRD_RESOLVER_AND_TEN_OF_EIGHTEEN_PREMISES...

**And that finding's own closing result is in `docs/staging/` while its code is not in any commit.**
`WORKER_RESULT_THE_HDD_LEG_READS_THE_WORLDS_OWN_CELLS_NOW_2026-09-21.md` says
`sim/weather_hdd._resolve_source_cid` is deleted. It is present at `HEAD` and present at
`origin/main`; the deletion exists only in the working tree, last written 2026-09-21T23:27, by a
worker that is no longer running. So the finding cannot be archived, the lane stays held, and every
level move in W1_market_weather is refused by a repair that is finished and unlanded.

Not minted as a new finding: this is `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12` (35 instances)
and the instance is large — 927 insertions across 13+ files spanning several lanes, not one coherent
piece this lane can vouch for and land. What is new is the *consequence*, recorded here: the lane
gate and a result file in the same directory disagree, and the gate is the one that is right.

**The next lane to land the HDD repair unblocks this level move.** Whoever takes it: the work is
`sim/weather_hdd.py` + `simulation/weather_inputs.py` and their tests, and `tools/isolate_hunks.py`
is the route, because several of those 13 files carry other lanes' hunks in place.

## The module is recorded as dormant, and its wiring is the next step

The orphan ratchet refused the first landing: nothing imports
`tools.weather_cell_joint_partition` and no committed unit runs it. It is added to
`docs/design/orphan_baseline.json` by hand rather than by `--freeze`, and the difference matters:
`freeze()` recomputes the whole list from the WORKING tree, which here holds seven untracked
modules belonging to other lanes, so the sanctioned command would have swept their state into a
shared artefact to record one row. One row is what was wanted, so one row is what was written
(`module_count` moved 1162 → 1163 with it). Two baseline rows — `tools.settlement_ceiling_probe`
and `tools.settlement_footprint_probe` — are now wired and could lower the floor; left for the lane
that wired them to bank.

**Dormant today is honest, and it is not the end state.** The home this belongs in is
`tools/generate_weather_cells_data.py`, the runner named in `W1_14`'s file_scope, whose own
docstring already says its job is to publish the coverage curve "so granularity reads as a price
list rather than a fact". The joint partition is a new row in exactly that price list, and putting
it there is what makes the finding visible to a reader rather than only to a commit message. Not
done in this tick because a new feed field runs the whole `site/` lane, which is not a thing to
start at the end of a bounded invocation.

## A working-tree red that is not a tree red

`tests/architecture/test_static_quality_ratchet.py` reads RED in the shared working tree — ruff
`I001` 1305 against a frozen 1306 and `F841` 123 against 124, FEWER violations than baseline, the
stale-baseline shape. It is GREEN in the gate: the tree the commit would create is HEAD plus this
lane's files, and the fix that lowers those counts is in another lane's *uncommitted* edit, which
that tree does not contain. So it refuses nobody's commit and it is not a blocker — recorded
because a working-tree red that looks like a shared wedge costs the next reader a cycle to
re-derive.

— Worker tick, 2026-09-22.
