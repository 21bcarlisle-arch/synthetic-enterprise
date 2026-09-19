**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "the-half-hourly-shape-reaches-four-customers-of-two-hundred-and-ten"

**Class:** uncommitted_and_orphaned_work

# The drawn pull is the design the director refused, and the "dead" branch was two stale rival working copies

Autonomous worker, scheduled tick, 2026-09-16. Both legs of the drawn item are discharged and
**neither is discharged the way the item said**. Leg (a)'s cause was not the one named; leg (b)'s
remedy is one the director has already refused in writing.

**Landed:** `simulation/weather_cell_siting.py`, `tools/reduction_dimension.py`.

**Downloaded: nothing.** The pull was started, caught and killed before any archive was written.
`sim/weather_data/` is C1–C4 and clean, as it was at the start of the turn.

---

## Leg (a) — the branch was never dead here either, and the cause was the opposite of the one named

The item directed: *"Fix `simulation/weather_cell_siting.cell_matched_site`, which accepts NOTHING
on this working tree ... the uncommitted artefact that kills it."* Two things are wrong with that,
and the second is the expensive one.

**The premise was already retracted before it was drawn.** The finding the item cites carries a
correction, by the seat that filed it, saying so: the accept branch reaches 117 of 194,865 occupied
land cells, and the original `None` was measured through an expired `REACHABILITY_WITNESS`. The item
was minted from the finding's headline and not from its foot.

**And the live cause on disk is the mirror of the one named.** The item says an *uncommitted
regeneration* kills the mechanism. Measured:

| path | disk mtime | what it holds |
|---|---|---|
| `simulation/weather_cell_siting.py` | 2026-09-07 16:21 | the 09-07 cut |
| `sim/weather_cells/site_cells.json` | 2026-09-07 17:32 | witness at `(50.4689,−4.1492)`, cells `(6,10,12)` |
| `HEAD` (`1bf4821b6`, 2026-09-16) | — | witness re-sited to `(50.5305,−4.2225)`, cells `(16,10,12)` |

**The working copies are OLDER than HEAD, not newer.** `1bf4821b6` landed through `surgical_land`,
which never writes the working tree, so the disk kept the pre-landing bytes and the test file — which
*was* refreshed — read the re-sited witness out of a module that still had the old one. That is not
an uncommitted regeneration about to reach the book. It is a landing that never reached the disk, and
the direction matters because the two call for opposite remedies: the item's remedy is to *discard*
the disk bytes as another lane's mistake; the actual remedy is to *adopt* HEAD's.

Writing HEAD's bytes over both paths: `1 failed, 13 passed` → **`14 passed`**. No code changed.

## The refusal that saved the holder work, and why a blind refresh would have destroyed it

`tools/refresh_to_head.py` **refused both paths**, and both refusals were right:

```
simulation/weather_cell_siting.py  [refused_supplies_names_head_lacks]
    this copy SUPPLIES 3 name(s) HEAD does not have  -- REDUCES_OVER, _HEAT_LOAD_DRIVERS, declare
sim/weather_cells/site_cells.json  [refused_no_reader]
    this control has no reader for .json files, so it CANNOT establish that the copy has nothing to lose
```

The known failure mode here is that *"a name HEAD lacks" is holder work only if HEAD never had it* —
a deleted name reads identically. Checked rather than assumed: `git log --all -S` puts
`REDUCES_OVER` and `_HEAT_LOAD_DRIVERS` in `e38730761` and `2800d9faf`, both `SALVAGE(auto)`
commits, **reachable from no branch**. HEAD never had them. So it is holder work, it is real, and the
refresh the item's framing would have licensed would have deleted a week-old declaration nobody had a
second copy of.

Preserved, then re-applied over HEAD's bytes rather than kept alongside them — so the landed file is
HEAD plus the declaration and nothing of the stale cut.

## What that unlocks, which was the actual blockage and is now discharged

`tools/reduction_dimension.OUTSTANDING` had exactly one row, and it named this file:

> the declaration is written and landing it selects `tests/simulation/test_weather_cell_siting.py`,
> red at pristine HEAD on an artefact cut owned by lane W1_market_weather

**That red is the one `1bf4821b6` fixed.** The debt row's own stated discharge condition was met by a
commit in another lane nine hours earlier, and nothing connected the two. `stale_outstanding()` — a
function that exists for precisely this and is printed rather than asserted — named it as soon as the
declaration was on disk. The row is deleted in the same commit that lands the declaration, so the
census never passes through a state where the claim is silent and unaccounted.

`simulation.weather_cell_siting` now reports two declarations and `OUTSTANDING` is empty.

## Leg (b) — the pull is the refused design, and the item inverts its own instruction

The item directed a per-location Open-Meteo pull, and `tools/pull_book_weather.py` (untracked,
2026-09-08) implements it: 145 locations, 213 accounts, ~1 hour. I started it.

It is the design the director refused. `sim/weather_world.py:20-24`, read at source rather than
taken from a sibling's commit message:

> *"The weather happened; everyone in that place experienced the same weather... **Two households in
> the same cell must experience identical weather** — that's what makes the difference in their
> demand attributable to fabric and people rather than to two separate downloads."*

The argument is one number in that file: **of the book's 257 located accounts, 101 share a 1 km
cell.** A per-property pull gives those 101 a second download of a sky someone else already has, and
the difference between the two series is then indistinguishable from a difference in fabric or
people — which is the exact attribution the fabric switch exists to make. It also destroys the
synchrony result: cold arriving across Britain in five-day blocks is a property of ONE shared world.

**The item contained its own correction and it was two clauses later than the instruction.** It said
to bind to prior draws and not mint a rival; the prior draw
(`widen-the-weather-archive-beyond-c1-c4`) says *"READ FIRST, DO NOT REWRITE"* and names
`sim/weather_world.py` as the thing to read. Reading it inverts the instruction above it.

Killed mid-probe. Nothing was written. A sibling seat was mid-`surgical_land` on the sanctioned
design at the moment I checked, taking fabric-eligible accounts **4 → 142 of 232 with no byte
downloaded**, by wiring a cell-keyed store that had sat uncommitted for eight days with no reader.
I did not touch any path in its landing.

## Recorded, not taken: the narrowing that would have cleared my own blocker

`tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py` is **red at pristine
HEAD** — proved in a clean `git archive` extract, not inferred — on `tools.generate_value_arms_data`.
The census puts it in class through `_CEILING_PROBE`, a **private** module constant whose value is a
*filename*, not a claim.

The detector is asymmetric: `_claim_symbols` skips private `FunctionDef`s (`not
node.name.startswith("_")`) and does not skip private `Assign`s, where `"_CEILING_PROBE".isupper()`
is `True`. Making the two legs consistent is a one-line change and it is **not** the change to make.
Measured first: the set of modules in class *solely* through a private upper-case assign is

    tools/generate_value_arms_data.py  ['_CEILING_PROBE']

**Exactly one module, and it is the one blocking me.** A narrowing whose entire population is the
thing obstructing its author is the amnesty shape this control's own `OUTSTANDING` docstring warns
against, and it would be indistinguishable from the honest fix at review. Not taken.

The honest disposition is one of two things and I could not establish which from outside that lane,
so I am naming both rather than guessing: either the module is a **renderer** of
`simulation.premise_population`'s ceiling and owes a re-export — the precedent is exact and
documented at `tools/generate_cohort_coverage.py:61`, *"RE-EXPORTED, not restated"* — or it owes its
own declaration for the "smallest book that does not work" requirement, whose unit its docstring
already states (*"THE UNIT IS DECISIONS, DECLARED, NEVER ACCOUNTS"*) along with its blind spots in
`what_is_not_established`. The second reading is the more likely, because that block publishes a
figure and `_pass_cost` publishes a one-sided floor beside it; but a declaration states what a figure
reduces over, and a wrong one is worse than a missing one.

**This is a live red at HEAD that will refuse other lanes' commits, not only mine.**

## Class registration

`uncommitted_and_orphaned_work`, in the least visible shape it has: a landing that reached the
commit and never reached the disk, leaving a rival working copy that carried both the *superseded*
bytes and the *only surviving copy* of unlanded holder work. The stale-copy control could not judge
it — the module leg refused because of the holder work, and the artefact leg has no `.json` reader at
all — so an "unavailable check is a failed check" and the file sat unjudgeable in the tree while a
debt register in another module waited on the red it was causing.
