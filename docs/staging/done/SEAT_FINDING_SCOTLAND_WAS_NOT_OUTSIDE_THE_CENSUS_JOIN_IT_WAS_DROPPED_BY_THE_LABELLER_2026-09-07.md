# SEAT FINDING — Scotland was never outside the census join. The labeller dropped it, a counter recorded it, and nothing read the counter.

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_18_the_housing_joint_the_sample_and_the_ceiling

**Measured and fixed 2026-09-07 in an isolated worktree.** Claim
`W2_18-the-frame-has-no-scottish-region`. Pre-registered before any number here was computed:
`docs/staging/SEAT_PREREGISTRATION_WHETHER_SCOTLAND_IS_OUTSIDE_THE_CENSUS_JOIN_OR_A_LOST_REGION_2026-09-07.md`.

## The question and the answer

The direction asked which of two things the frame's missing Scottish region was: **the census
join's scope**, or **a lost region**. It is a lost region, and the measurement is not close:

> Of the **46,270** output areas the region labeller discarded into
> `output_area_outside_the_grouping`, **46,270 carried the NRS `S00` prefix and none did not.**
> They held **2,503,270 households — 9.2 % of the GB census total.**

The join had already counted every one of them. `weather_cell_weights.read_households()` merges
Census 2021 TS041 (188,880 E&W areas) with **Scotland's Census 2022** (46,363 areas, 2,508,542
households), and `pull_scotland` fails closed if the Scottish pack is absent with the words *"Scotland
is 8% of GB households and it is the cold, windy end"*. ONSPD carries Scottish postcodes with grid
references; the HadUK-Grid normals cover Scotland. **Three of the four links in the chain were
GB-wide.** The fourth was `region_namer`, which resolved every output area through
`oa21_to_region_england.csv` — the England-and-Wales lookup — and returned `None` for Scotland,
because Scotland is a country with no row in an England-and-Wales table.

Scotland needed no lookup row at all. It is one region in the curriculum's vocabulary, exactly as
Wales is, and the module **already had** a country-code fallback for Wales sitting three lines away.

## The predictions, with their outcomes

Listed rather than summarised, because a pre-registration only ever reported as "confirmed" is not
evidence of anything.

| # | Prediction | Outcome |
|---|---|---|
| 1 | ≥ 99 % of the 46,270 drops are `S00` | **46,270 / 46,270 = 100 %**, zero non-Scottish |
| 2 | Scotland enters the frame at 2.3–2.7 M households, 7–10 % of it | **2,464,507**, **9.08 %** |
| 3 | distinct frame coordinates rise from 139,938 to within 5 % of 175,188 | **exactly 175,188** — see below |
| 4 | `output_area_outside_the_grouping` falls below 200 | **0** |
| 5 | the ten existing regions do not move, to the row | **144,542 rows byte-identical**, all ten totals unchanged |
| 6 | the drawn book does not move | **210/210 sited, 0 Scottish**, max latitude 55.08 |

**P3 held far beyond its stated bound and that is the finding's point.** The frame's coordinate set
and W1_14's occupied-land-cell set are now **equal — 0 cells in either direction**. This is not a
coincidence and not a tautology: `census_weights(group_of=None)` is the union over groups of
`census_weights(group_of=namer)`, so the two sets were *always* meant to be the same set, and the
20.1 % gap was exactly the country the labeller dropped. **The "two populations, one number" defect
that motivated this claim is now one population**, and the GB coverage figures W1_14 publishes over
175,188 cells are true of the population that gets looked up in them.

## What was actually wrong, and it was not the code

The code did everything right. The labeller returned `None`, `census_weights` counted that in
`output_area_outside_the_grouping` **exactly as designed**, and the number was written into the
committed manifest at 46,270 from the frame's very first build. `tests/tools/
test_weather_cell_weights.py` even carries a test whose docstring names *"Scotland ... the live
instance"* and *"8% of GB households vanishing quietly would leave every English region's weather
looking exactly as it should"* — the hazard was written down, the instrument was wired, the number
was published, and **nobody read it**.

> **A drop counter is not a control.** It is a diagnostic that requires a reader, and the reader
> was a human who never came. The fix is not a better counter; it is one assertion on the number
> the counter already produced.

That assertion is now `test_THE_LABELLER_NAMES_EVERY_OUTPUT_AREA_THE_CENSUS_JOIN_COUNTED`. It reads
the **committed** manifest, so it needs no census cache and would have gone red on day one.

## Two controls were keyed to the answer of the day, and both were green throughout

This is the R15 half of the finding, and it is the more expensive half.

**`test_the_NAMER_DROPS_SCOTLAND_rather_than_folding_it_into_a_region`** asserted
`namer("S00000001") is None`. Its stated defect — Scotland folded into the North East — was real
and worth guarding. But `None` is satisfied by **two opposite worlds**: Scotland correctly held
apart, and Scotland silently lost. It was the second, for the frame's whole life, and the control
was green because `None` was the answer it wanted. *A control whose pass condition is the defect's
own signature cannot distinguish the defect from the fix.* It is now two separate legs — never
wearing another region's name, and wearing its own — so neither can stand in for the other.

**`test_the_frame_covers_exactly_the_regions_the_curriculum_draws`** asserted set equality against
the curriculum. Its docstring names the defect as a **missing** region; equality also refused an
**extra** one, which is not that defect. That extra direction is what made the bug unfixable in
isolation: the frame was forbidden from carrying a real GB region until the world agreed to draw
from it, so 2.5 M sourced households stayed discarded pending a curriculum change nobody was
making. It is now coverage (`frame ⊇ curriculum`), which is the property the docstring always
described.

**The relaxation is bounded, because a bare `⊇` would be a worse control than the equality it
replaced** — a misspelt `"Scotand"` would site nobody, refuse nothing and pass. The extras are
enumerated by name in `household_siting_frame.CARRIED_AHEAD_OF_THE_CURRICULUM`, and `build()`
refuses any it does not recognise.

## Poison round

Three mutations, each reverted, tree checksummed back to identical (`md5sum` match):

| Mutation | Killed by | Line |
|---|---|---|
| Scotland folded into `"North East"` (the named hazard) | `..._NEVER_FOLDS_SCOTLAND_INTO_ANOTHER_REGION` | the folding leg |
| Scotland dropped again (the world before this turn) | the same test's **other** leg | the identity leg |
| `CARRIED_AHEAD_OF_THE_CURRICULUM` emptied (phantom region) | `..._covers_every_region_the_curriculum_draws` | the extras leg |

The two legs of the namer control fired on **different lines** for **opposite mutations**, which is
the evidence that splitting it was not cosmetic.

## What this does NOT close, and it is the whole remaining question

**The world still draws no Scottish household.** `region_marginal_synthetic_acquisitions` holds ten
regions, and this turn deliberately did not touch it: the frame's Scottish rows site nobody today.
`siting_refusal("Scotland")` now returns `None` — the frame *can* site a Scottish household the
moment the world draws one, and the rebuild that would otherwise have been needed (72 MB ONSPD, the
UPRN grid, the HadUK normals — none of it in a fresh worktree) is already committed. **The blocker
has moved from "needs a data pull" to "needs a number."**

That number is a **fidelity change to the curriculum (R13)**, not a labelling fix, and it is
sourced rather than picked. The marginal's own `basis` reads *"Census 2021 England & Wales
household counts by region, normalised over the schema's 10-region set"* — it inherited the same
England-and-Wales scope from the same join, for the same reason. The GB recomputation is now
available from data already in the tree:

| | households | GB share |
|---|---|---|
| England & Wales (TS041) | 24,783,304 | 90.81 % |
| **Scotland (Census 2022)** | **2,508,542** | **9.19 %** |
| GB | 27,291,846 | 100 % |

A GB supplier modelled against the GB record that draws zero Scottish customers overstates every
other region by a factor of 1.101, and Scotland is the cold, windy end — so the omission is
biased, not merely absent, in exactly the drivers W1_14's cells exist to carry. **That is the next
piece**, and its blast radius (every drawn book moves) is why it is named here rather than smuggled
into a labelling fix.
