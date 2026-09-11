<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over`

**Knowledge:** none — this is a landing/orphan state, not domain understanding.

# The demand-vector canon, deliverable by deliverable: three are in git, one is held by another lane's red, one is unbuilt and mis-described by its own header

**Measured 2026-09-08 from base `3502d6ff1`**, delivery seat, on the LANE 0 draw *"Land the
director's demand-vector canon or file precisely why it cannot"*. The draw said the canon was
*"sitting in a tree that says in its own header that it already landed"* and named
`sim/weather_world.py`, `tools/build_weather_world.py` and `tools/pull_book_weather.py` as the
untracked evidence. **Both halves of that were true, and they were true of different files.**

---

## The census, per deliverable, against `HEAD` rather than against the working tree

| # | Deliverable (canon §WORK THIS CREATES) | State at `3502d6ff1` | State now |
|---|---|---|---|
| 1 | Coverage re-measured against the demand vector, weighted acceptance, both N figures | `W2_29` at `HEAD` level 1; `tools/demand_vector_coverage.py` at `HEAD`, clean | unchanged — **landed already**, level 1 of 3, exit gated on item 4 |
| 2 | The weather partition re-opened as a joint question over a stock with varying fabric | `W1_28` at `HEAD` level 0; both named files absent from disk | unchanged — **genuinely unbuilt**, and legally so: naming is the bar at the mint |
| 3 | A control refusing a coverage/ceiling/sufficiency claim that does not declare its reduction dimension | control built, `??`; 2 of 10 suppliers at `HEAD`, 8 in the working tree only | **7 suppliers landed** at `f733b20af`; blocked set 8 → 1 |
| 4 | Per-household half-hourly electricity and seasonal gas shape | electricity wired long since; gas built, wired, settling money, **committed nowhere** | **landed** at `ab241ebc6` |
| 5 | People phase 1 re-cut so the physical layer stands alone | `simulation/household_physical_layer.py` + 7 controls at `HEAD` since `bde2514dc`; `W2_31` row still reads level 0 | unchanged — build landed, **the recorded level has not caught up** |

Two commits, twelve paths. What follows is only the part that is not in those commit messages.

## Item 4 is where the draw's "header claims it landed" actually lived

The draw pointed at the three weather modules. They are not it. The header making a false landing
claim was
`SEAT_RESULT_THE_GAS_HEATING_FRACTION_SPANS_0_25_TO_0_95_AND_EVERY_HOUSEHOLD_WAS_HANDED_0_70_2026-09-08.md`,
which lists `simulation/household_demand_shape.py` and its 21 controls as artefacts of a completed
result, in the past tense, while both were `??`.

**That claim was not merely untidy — it was holding a gate red for every lane.**
`tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py` refuses exactly this,
and it is in `tests/design/`, which is the FIRST of the cheap gates CLAUDE.md tells every session to
pre-run and the first thing the commit chain runs. Any lane pre-running its cheap gates in the
shared tree saw a red naming a document that was not theirs.

The gate names two remedies — commit the artefact, or correct the claim beside itself. **The first
one was available and nobody had checked.** The module was complete, its 21 controls passed, and
`run_phase2b` and `gas_settlement` already called it; what was missing was four paths in one commit,
because a module imported only by its own test is still an orphan. `tests/design/` is green now.

**The generalisable half:** a false landing claim and a wedged shared tree are the same event here,
and the gate cannot tell you which remedy is right because it cannot tell a claim written too early
from a claim written falsely. Ask which before reaching for the eraser — the cheaper remedy is the
one that makes the claim *true*, and it is the one that gets skipped, because correcting prose is
faster than assembling an orphan cluster.

## Item 3 is one file from done and that file is not mine to move

`simulation/weather_cell_siting.py` is the tenth supplier. Naming it in a pathspec selects
`tests/simulation/test_weather_cell_siting.py::test_derive_reproduces_the_committed_artefact`, and
**that test is red at `HEAD`** — re-proved this tick in a clean detached worktree at `3502d6ff1`
with no working-tree state: `1 failed, 13 passed`, on the same driver shares the 09-08 finding
recorded (`annual_wind` 0.2062 against 0.2782, `annual_sun` 0.2493 against 0.1725).

It is hidden in the shared tree because `sim/weather_cells/occupied_land_cells.csv` and
`site_cells.json` — the committed artefacts the test reproduces against — are themselves modified
and uncommitted. Landing those would settle a two-lane artefact cut on no evidence in order to make
my own gate go green, and lane `W1_market_weather` carries a live **BLOCKING** finding
(`SEAT_FINDING_TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE...2026-09-07`) saying the shared tree's
copy may be the losing one. **The reason stands and it is named rather than worked around.**

So `W2_28` stays at level 0, for the reason its own row already gives. The row says *"move it to 1
in the same commit that lands the control"*, and that commit is one red away — a red belonging to a
different lane, now twenty-four hours older than when it was first recorded.

## The three weather modules: built, untracked, and describing a tree that does not exist

`tools/build_weather_world.py`'s docstring says `tools/pull_book_weather.py` *"is deleted in the
same commit"*. **There was no such commit**, and two days later all three files are still `??`. That
header has been corrected in place beside the claim rather than over it.

Correcting it surfaced two more claims in the same docstring that the tree does not support, and
together they are why these three cannot simply be landed to make the first one true:

- **`tools/validate_weather_world.py` does not exist.** It is cited as the HadUK check that
  *"measures the store's resolution instead of assuming it"* — the sentence that turns an honest
  limit (ERA5-Land is ~9 km, so two cells closer than that get the same series) from a measurement
  into an assertion. A path in a prose comment is a reachability edge; this one points at nothing.
- **`sim/weather_world/` is an empty directory.** The store has never been built, so
  `sim/weather_world.py` is a reader with nothing to read.

Neither module has a control. Neither is imported by anything but the other. Landing them as they
stand adds two orphans and a false path — worse than leaving them, because a landed module reads as
a working one. `tools/pull_book_weather.py` is left on disk deliberately: it is untracked, so
deleting it is unrecoverable, and the module that supersedes it is not in git.

**They are the closest thing in this canon to work that is finished-looking and not finished**, and
the tell was in the docstring the whole time, in the two sentences that name artefacts.

## What is next, in order

1. **The `W2_31` level move.** The build and seven controls have been at `HEAD` since `bde2514dc`
   and the row still reads 0. Check the level definition against what the build earned rather than
   bumping to target — this is the second document to name it as the next obvious increment.
2. **`simulation/weather_cell_siting.py`'s declaration, the moment the W1 artefact cut resolves.**
   That single path closes item 3 and moves `W2_28` to level 1 in the same commit.
3. **The weather world needs its validator, its controls and one real pull before it is landable.**
   Three things, none of them large, and none of them started. Until then the header correction is
   the only true statement about it in the tree.
4. **Item 2 (`W1_28`) is unbuilt and unstarted**, and it is the one deliverable of the five with
   nothing at all behind it.

**Falsifier for the claim this document makes:** `git cat-file -e f733b20af` and
`git cat-file -e ab241ebc6`, and `git show HEAD:simulation/household_demand_shape.py | head -1`. If
item 4 is not at `HEAD`, this write-up is the same defect it describes.

— Delivery seat, 2026-09-08.
