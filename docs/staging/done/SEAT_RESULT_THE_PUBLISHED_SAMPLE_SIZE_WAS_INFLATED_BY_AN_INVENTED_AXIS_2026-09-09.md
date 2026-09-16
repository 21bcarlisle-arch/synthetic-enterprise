<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

**Knowledge:** `how-many-synthetic-households` — the page publishing the figure this corrects.

# The published sample size was inflated by an invented axis, and the control that found it kept it

**Measured 2026-09-09**, delivery seat, from base `7e699a126`, on the LANE 0 draw *"Land the
director's demand-vector canon or file precisely why it cannot"*. That draw's premise was spent —
`SEAT_RESULT_THE_DEMAND_VECTOR_CANONS_FIVE_DELIVERABLES_ARE_THREE_LANDED_ONE_HELD_AND_ONE_UNBUILT_2026-09-08`
had already done the part-by-part census and landed items 3 and 4 — so this took the first entry in
that document's *what is next*, and the trail from it led somewhere else.

---

## What the draw pointed at, and why it moved

Item 1 of *what is next* was the `W2_31` level move: the physical layer build and its seven controls
have been at `HEAD` since `bde2514dc` and the row still reads level 0. **That move is refused, and
the refusal is the finding's own subject:**

```
OPS11: the level-raise on `W2_31_people_phase1_the_physical_layer_stands_alone` is REFUSED --
lane `W2_customer_generator` holds 2 live BLOCKING finding(s)
  - DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md
```

The canon is BLOCKING because *"two live coverage claims rest on the collapse this document
names"*. So the canon blocks the recording of one of its own delivered items, and it stays BLOCKING
until the coverage claims stop resting on the collapse. That made the coverage instrument the work,
not the level row.

## The defect: one of seven declared axes was a copy of another, and invented

`SEAT_FINDING_TWO_AXES_OF_THE_DEMAND_VECTOR_ARE_THE_SAME_AXIS_2026-09-08` established this and it
reproduces exactly at `generated_population(points=12000)`:

    corr(seasonal_swing, weather_sensitivity_kwh_per_degree_day) = 1.000000
    eigenvalues [4.9436, 1.0000, 0.9732, 0.0660, 0.0171, 0.0000, -0.0000]

Provable without measuring anything. `weather_sensitivity` is `hlc * 24`; `seasonal_swing` was
`0.5 * (1 + 0.15 * z(hlc))`. Both affine in one scalar, so the correlation is ±1 by construction.

And the duplicate was the invented half. `weather_sensitivity` is a real quantity the physics
computes. `seasonal_swing` was `hlc`, z-scored, scaled by **0.15** and centred on **0.5** — two
numbers with no source, no comment and no derivation. Its docstring called it *"the share of the
year's demand falling in the coldest half"*, which **it was not and could not be**:
`demand_case_coverage.DOYS` is 1 October to 31 March, so the model does not simulate the warm half
of the year at all. The second copy of the term, in `population()`, looked more like a measurement
and was worse — its leading factor was `coldest.sum() / len(doys)`, a share of *days* identical for
every household, with all the per-household variation still coming from `1 + 0.15 * z(hlc)`.

## What it cost the published figure, measured as a one-variable bridge

Same population, same seed, same reference, same tolerance; the only thing varied is the axis set.
`smallest_n_chosen` takes `axes` as a parameter, so no code change was needed to measure it.

| Figure | With the duplicate | Without it |
|---|---|---|
| **Full vector** (distribution + response) — the published headline | **6,816** | **5,215** |
| Distribution axes only | 6,811 | 6,809 |

6,816 is the figure `site/data/knowledge_topics.json` publishes, reproduced to the digit — so the
bridge is measuring the published quantity and not a neighbour of it. **The published headline was
30.7% higher than the honest one**, because a direction appearing twice must be satisfied twice
while teaching nothing after the first.

**The second row is the part I did not predict, and it changes what may be claimed.** On the
distribution axes alone the duplicate costs essentially nothing — 6,811 against 6,809, two
households in seven thousand. The whole of the 30.7% sits in the FULL-VECTOR figure. So the earlier
finding's *"every N this instrument has published"* is too broad: the distribution N was near enough
unaffected, and it is the number the canon calls the first of its two. What was inflated is the
number the canon calls **the real one**.

I cannot yet say why the two behave so differently, and I am not going to guess in a document that
will be read as established. The tell is that N here is not monotonic in the axis count at all —
adding the two response axes to the six-axis set *lowers* N from 6,809 to 5,215, because
`choose_for_difference` selects a different set of cases when it has more directions to spread over,
and a better-spread set can be weighted to fit with fewer members. That is a property of the design
worth understanding on its own, and it is filed as a question rather than answered here.

## The part that is a lesson rather than a number: the control found it and kept it

The degeneracy was already caught. `test_NO_NEW_PAIR_OF_DECLARED_AXES_IS_EXACTLY_THE_SAME_AXIS`
existed at `HEAD`, correctly measured all three collinear pairs, and **listed them in a
`_KNOWN_COLLINEAR` ratchet** — recording the 6,816-to-5,215 cost in its own docstring. Its stated
reason for holding rather than fixing:

> *"replacing it honestly needs the cold-half share of ANNUAL demand, and the model stops on 31
> March. That is the `simulate_premise` build, not a patch."*

**Every clause of that is true, and it answers the wrong question.** It asks how to REPLACE the
axis. Nobody asked whether the axis should be there at all — and **deleting it needs no build**. The
direction it carried is still measured by `weather_sensitivity_kwh_per_degree_day`, which is the
quantity the physics actually computes. What deletion removes is the *claim* that seasonal shape was
spanned, and `blind_to` is where that belongs. An invented axis inflated a published number; a
declared blindness states the same limit and cannot be quoted as coverage.

The control's own prose had even named the exit — *"removing the known one means deleting a line
here"* — and nobody deleted the line, because the docstring had already supplied a reason not to.

**The generalisable half: a ratchet on a defect reads as containment and is a decision to keep it.**
A list of known-bad states earns its place only while removal is genuinely blocked. Ask which
entries are merely UNEXAMINED before adding another.

## A second wrong claim, surfaced by the control refusing my own first edit

Adding `seasonal_gas_shape` to `blind_to` was refused by `tools/reduction_dimension.declare`:

    ['seasonal_gas_shape'] are declared blind AND reduced over -- one of the two is wrong

Because `weather_sensitivity_kwh_per_degree_day` was declared `derived_from=("annual_gas_kwh",
"seasonal_gas_shape")`. **That declaration was wrong and had been since it was written.** `demand()`
computes `hlc = (fabric_loss + 0.33 * ach * volume) / 1000` — wall, roof and floor U-values, air
change rate, site wind, and *nothing from any seasonal profile*. The degree-days it is a rate per
come from the cell and are shared by every household in it. The axis is the winter gas total
normalised by the cell's climate, which is why it correlates 0.985 with `annual_gas_kwh`. It says
how much demand MOVES with temperature; it cannot say how demand DISTRIBUTES across the season.

Naming the shape there is what let the shape look covered even after the fake axis was noticed.
The declaration now reads `("annual_gas_kwh",)` and the control passes.

## What is now true of the vector, including what is still degenerate

    AXES     annual_gas_kwh, annual_electricity_kwh, weather_sensitivity_kwh_per_degree_day,
             peak_window_share, insulation_ceiling_kwh, turndown_ceiling_kwh
    blind_to half_hourly_electricity_shape, seasonal_gas_shape

The exact duplicate is gone from both generators. **One near-identity remains and is named rather
than quietly accepted:** `weather_sensitivity ~ turndown_ceiling_kwh` at 0.999997, because
`turndown_ceiling` is `hlc * 24 * (cold - warm degree-days)` and that difference is near-constant
across cells. So there are still five effective directions under six labels. It stays on
`_KNOWN_COLLINEAR` and it is a different class from what was removed — a physical near-identity, not
two typed constants — and removing `turndown_ceiling` would delete a response axis the mission needs
for ranking interventions.

## A confound worth recording, because it nearly produced a fitted fixture

Deleting the `seasonal_swing` column from `_grid()` in `tests/tools/test_demand_vector_coverage.py`
turned `test_THE_WEIGHTING_MUST_DO_WORK` red. **That red was not about the axis.** Every column drew
from one shared `rng` in dict order, so removing any column reshuffled every column below it — the
four remaining axes got different random numbers, and "I changed one axis" became "I changed the
whole population". Held draws, six axes, seeds 7/11/13/21/42: designed beats random every time.

Each column now draws from its own stream. This is the state that invites re-tuning a fixture until
it agrees, and the tell was that the red appeared in a control with no causal path to the change.

## Falsifiers

- `python3 -c "from tools.demand_vector_coverage import AXES; print('seasonal_swing' in AXES)"` →
  `False`. If True, this write-up is describing a tree that does not exist.
- The 6,816 row above is checkable against the live page: if the published figure was never 6,816,
  the bridge measured a neighbouring quantity and the 30.7% is not attributable.
- `pytest tests/tools/test_demand_vector_coverage.py tests/tools/test_gas_carries_a_hot_water_term.py`
  → 18 passed.

## What is next, in order

1. **The `W2_31` level move, once this lane's BLOCKING findings clear.** Still item 1 of the
   previous document's list, still blocked, and now blocked for a reason with a named remedy rather
   than an unexamined one.
2. **The 120,000-reference figure.** The page leads with 8,822 on the full vector against a
   120,000-household reference; the bridge above is at 20,000. The re-measurement is running and the
   page carries the corrected pair when it lands.
3. **The seasonal axis, properly, needs the annual model.** `simulate_premise` past 31 March is what
   makes the cold-half share of demand computable. Until then `seasonal_gas_shape` is declared blind
   and every N here remains a floor for one more named reason than it had yesterday.
4. **Why N is not monotonic in the axis count**, from the second row of the bridge table. Six
   distribution axes need 6,809 and the same six plus two response axes need 5,215. If that is the
   design working as intended it should be stated on the page, because a reader who assumes more
   axes means a bigger sample will misread every figure here; if it is not, it is a defect in
   `choose_for_difference` and it sits underneath both published numbers.

— Delivery seat, 2026-09-09.
