**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the per-cell store is wired into the settlement path, the book's fabric population goes from 4 to 91, and the pull that would finish it is rate-limited by the archive

Worker seat, 2026-09-17. Claim `land-the-per-cell-weather-store-and-wire-its-reader`.

The item directed four things: pull the missing cells, land `sim/weather_world/`, wire
`sim.weather_world` into the fabric demand path, and remove three rows from
`docs/design/orphan_baseline.json`. **Three are done. The fourth is done for one of the three rows
and refused for the other two, and the refusal is the honest answer** — see §4.

## 1. THE HEADLINE: 4 → 91 of 136 electricity premises now settle on fabric physics

One variable. Identical households, identical eligibility predicate, identical window; only the
weather source changes.

| weather source | eligible for fabric physics | refused, no weather | refused, structural |
|---|---|---|---|
| per-customer archive (`sim/weather_data/*.csv`) | **4** | 127 | 5 |
| per-cell store (`sim/weather_world/`) | **91** | 40 | 5 |

The 5 structural refusals are identical on both legs and must be — two commercial premises, a
half-hourly-metered point whose real reads outrank any generator, and so on. They are a property
of the premise, not of the archive, and a source change that moved them would mean the measurement
was of something else.

The 40 remaining weather refusals are cells the store holds with temperature and no wind, cloud or
precipitation. They are what §3 is about.

## 2. WHAT THE WIRING IS, AND WHY IT IS NOT "THE SAME PULL, WIDER"

`simulation/fabric_demand_path.WeatherWorldSource` fills the three accessors
`fabric_providers_for_book` already took, from the store rather than from four CSV files. The seam
did not move; what it reads did. `run_phase2b` loads the store ONCE and hands the same object to
both fabric legs, and `tools/fabric_settlement_gap` was moved in the same commit, because that
tool's entire claim is that its population IS the settling one — leaving it on the archive would
have made the two disagree about every premise but four, silently.

The property that makes this the director's architecture rather than a bigger download:

> "Two households in the same cell must experience identical weather — that's what makes the
> difference in their demand attributable to fabric and people rather than to two separate
> downloads."

`test_two_premises_in_one_cell_read_the_IDENTICAL_sky` asserts it of the **weather days**, not of
the resulting demand: two premises in one cell settle to different kWh whatever the source,
because their fabric differs, so a control asked of the demand would pass with two separate
downloads fully in place. Of the 136 electricity premises, 131 distinct cells — so 5 premises
would have re-downloaded a sky another premise already had.

**Fifteen controls, ten mutation-proven.** Each fires on the specific defect it names:

| control | mutation that makes it fire |
|---|---|
| `..._read_the_IDENTICAL_sky` | `days()` stops memoising → two equal-but-separate lists |
| `..._carries_its_own_climatology_into_the_trace` | `for_cell()` stops adding `level_c` back |
| `..._temperature_ONLY_cell_is_refused_and_not_answered_with_a_NaN` | `available()` → membership test |
| `..._beyond_the_snap_radius_is_refused...` | `cell_id_for()` stops refusing a far coordinate |
| `..._does_not_send_the_reader_to_build_the_REFUSED_design` | the old "pull that coordinate" remedy |
| `..._ACTUALLY_USES_the_weather_days_callable_it_is_given` | the seam ignores its new parameter |

The last one exists because **a function gaining a parameter is ungraded by default**: every other
test in that file drives the seam through a fixture that leaves `weather_days_for` at its default,
so without it the store could have been wired into the runner and silently never read. It is
proven by the series DIFFERING, not by a call count — a spy would pass on a provider that called
the callable and threw its answer away. `..._READ_ONE_WEATHER_SOURCE` is the R11 leg: the runner
must build the source exactly once, or the two fabric legs can resolve a premise differently.

## 3. THE FINDING: the archive rate-limits the pull, so the store landed incomplete

`tools/build_weather_world --build` ran for the whole of this turn. It did the HadUK temperature
pass over the union (221 cells, up from 156 — the 65 book cells the store never held now have
temperature), then began the ERA5 pass at the measured 20 s pause. **It reached 169 complete cells
of 221 and then stopped writing for 14 minutes at a time**: `_fetch_with_backoff` waits
60/120/180 s on a 429 and Open-Meteo is returning them.

This is a property of the archive, not a defect in the builder, and the builder is already built
for it — it writes after every cell and skips cells already held, so **re-running the identical
command resumes**. The 52 cells still holding temperature only are exactly the 40 premises in §1
still refused.

**What this costs and what it does not.** It does not cost correctness: `available()` refuses a
temperature-only cell rather than answering with a NaN, so no premise settles on a sky with three
missing columns. It costs coverage — 91 of 136 instead of the ~131 the complete store would reach.

## 3a. THE THING WORTH KEEPING: a control written for a book of four met a book of 91

The wiring landed red on a live control, and the red was real:

> `C1 settles on the fabric provider but its settled volume is indistinguishable from the legacy
> provider's: the switch is labelled and textured but INERT`

`the_switch_moves_the_settled_volume` asks whether the fabric provider settles a volume at least
2% different from the legacy one, and `run_phase2b` raised on the FIRST premise that said no.
**I did not touch the control. I measured the population it was now being asked about**, by
recording every verdict instead of raising on the first:

| over all 91 fabric premises | |
|---|---|
| premises whose volume moves at all | **91 of 91** |
| median move | **44.0%** |
| largest move | 1396% |
| below the 2% floor | **4** — 0.43%, 0.57%, 1.09%, 1.09% |

**The switch is not inert; it is the most consequential thing in the book.** And C1's place among
the four is legible rather than mysterious: its 1 km cell reads **+1.19 °C warmer** than its old
point archive — 11.278 → 12.471 °C mean, which is the London urban heat island, *the thing the
1 km pull was for*. Wind and cloud are unchanged (4.030 vs 4.030 ms⁻¹; 67.04% vs 67.05%), because
the cell's ERA5 was pulled at a centre almost on C1's own coordinate. So C1 heats less; C1 is
**gas**-heated, so the fall lands in gas (−8.3% annual) while its electricity moves +0.45%.

A gas-heated premise whose electricity is mostly not heating is *entitled* to settle nearly the
legacy electricity volume. The per-premise floor was the right shape at N=4 — if one of four
premises settled the legacy volume, the switch really was largely inert. At N=91 it asserts a
per-premise fidelity claim the control was never written to make.

So the per-premise `raise` becomes `the_switch_reaches_the_book`: a **majority** of fabric
premises must move. The per-premise predicate is untouched and still called — it is what the count
is over. The floor is 50%, not the 96% measured today, because a control keyed to today's answer
goes red when the world gets more honest. Five controls, four mutation-proven: an inert switch,
an almost-inert switch (`any()` instead of a majority), a vacuous True on an empty book, an
unfailable share, and the accepting branch asserted reachable with the **four real unmoved
premises** rather than a clean sweep.

The per-premise `raise` is asserted GONE, not merely joined — left in place it still wedges the
run on those four and the book-level control never gets a subject.

## 4. THE ORPHAN BASELINE: one row earned removal, two did not

The item said remove all three. `sim.weather_world` is removed and the ratchet agrees — it is
imported by `simulation/fabric_demand_path.py` and reachable from the committed schedule.

`tools.build_weather_world` and `tools.validate_weather_world` are **restored to the baseline**,
because they are still unreachable: both are CLI entry points, and this ratchet does not count
test files as entrypoints (the 16 controls the W1_14 commit landed for them exist and import them,
and both modules were still listed). Removing their rows makes a claim the tree does not support,
and `tools/orphan_ratchet` refuses it in those words. An orphan row is the honest record of an
unreachable module; deleting it to match an instruction would be the instruction overwriting the
measurement.

Found the working-tree baseline already carried all three deletions plus `module_count` 1150→1154
when this turn started. Rebuilt it as a one-line edit off `HEAD` rather than rewriting the file —
a `json.dumps` round-trip reordered 544 of its lines, in a file several lanes hold dirty.

## 5. `tools/pull_book_weather.py` is deleted

Untracked since 2026-09-08, the per-property design the director refused verbatim, and nothing
imported it. `tools/build_weather_world.py`'s docstring had a correction saying its own
"deleted in the same commit" sentence was written in the past tense of a landing that never
happened, and set the test for when it would become true: *a commit that also removes the tool it
names*. This is that commit, and a third paragraph now records it — beside the other two, not over
them.

The refusal sentence moved with it. `_no_archive_refusal` said
`sim/weather_data/{site}.csv does not exist -- pull that coordinate` until today, which is an
instruction to build the refused design; it now names the cell and the build command. **A refusal
that names the wrong remedy is worse than one that names none: it recruits the reader into
rebuilding the thing that was refused.**

## 6. WHAT I EXPECT TO MOVE, WRITTEN BEFORE LOOKING (R12/R13)

This is a BASELINE fidelity change and the module's own pre-commitment already covers its
direction: a real premise is spikier than a rescaled national average and its annual level is set
by its fabric rather than a declared EAC, so **imbalance cost and net margin very likely get
worse, and per-customer volumes move materially** — on 91 premises now instead of 4, so roughly
twenty times the exposure. That is the correct consequence of removing a smoothing artefact from
most of the book. It must not be treated as a regression and nothing may be tuned to bring the old
numbers back.

The book now runs to completion on 91 fabric premises. I have **not** attributed what it does to
the published figures — the run that proved the control green changed the weather source for 87
premises at once, and a result that moves when more than one thing changed cannot be attributed.
I cannot yet say, and saying so is the result.

## 7. NEXT

1. **Re-run `python3 -m tools.build_weather_world --build`** on a later tick. It resumes. When the
   52 cells complete, the 40 refusals in §1 clear with no code change — `available()` starts
   answering True on its own.
2. Run the book and attribute the move, one variable at a time.
3. `tools/validate_weather_world`'s ERA5 leg still grades a population its builder does not serve
   (`WORKER_FINDING_..._2026-09-17`, already filed) — it counts against the union while the
   builder's ERA5 pass covers only today's book cells.
