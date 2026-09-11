**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`
· **Class:** measurements_that_mirror

**Knowledge:** none -- this is a machine finding about our own instrument, not domain understanding.
The domain page it sits under is `how-many-synthetic-households`, which is written and blocked on the
site lane; this document is the reason its axis count needs a correction before it publishes.

# Two axes of the demand vector are the same axis, and one of them is invented

**Measured 2026-09-08**, delivery seat, at `41501920c`, while checking whether wiring hot water and
headcount had broken the collinearity the gas brief found. It had, partly. It also surfaced this,
which is older and worse.

Reproduce: `generated_population(points=12000)`, then the correlation matrix of `values`.

---

## The finding

**`seasonal_swing` and `weather_sensitivity_kwh_per_degree_day` correlate at r = 1.0000.** Not
0.9879, which is what the gas brief reported for the old three-way degeneracy. Exactly one.

The correlation matrix's smallest eigenvalue is **0.0000**. The vector is declared over seven axes
and has at most six independent directions.

    eigenvalues  [4.3503, 1.0391, 0.9966, 0.5513, 0.0526, 0.0100, 0.0000]

## Why it is exactly one, which is provable without measuring anything

    swing                = 0.5 * (1 + 0.15 * (hlc - hlc.mean()) / hlc.std())
    weather_sensitivity  = hlc * 24.0

Both are **affine functions of the same scalar**, `hlc`. An affine function of an affine function of
one variable is affine, so the correlation is ±1 by construction. No amount of population, no choice
of seed and no future change to the fabric model can make these two axes differ. **Measuring both is
measuring one of them twice.**

## And the invented half is worse than the duplication

`weather_sensitivity` is a real quantity: the heat-loss coefficient in kWh per degree-day, which the
physics computes. `seasonal_swing` is not. It is `hlc`, z-scored, scaled by **0.15** and centred on
**0.5** -- two numbers with no source, no comment and no derivation, producing a quantity whose
values are spread around 0.5 because 0.5 was typed.

The module's own docstring says the axis is *"the share of the year's demand falling in the coldest
half"*. **It is not that, and it cannot be computed here**: `demand_case_coverage.DOYS` is
`range(274, 366) + range(1, 91)` -- 1 October to 31 March. The model does not simulate the warm half
of the year, so the share falling in the cold half is not available to it. A quantity that could not
be computed was filled with a plausible-looking transform of one that could.

This is the shape `CLAUDE.md` names: *"a number invented to fill a slot will be load-bearing within
a week and unattributable within a month."* It has been load-bearing in every N this instrument has
published.

## What it means for the numbers already published

**Every N from this instrument has been scored over a vector containing a duplicated axis.** The
direction is double-weighted in the joint slices and in the acceptance, so the published figures --
275, then 243, and whatever the current run returns -- are all answers to a question with seven
labels and six axes.

The effect on the FIGURE is not established and this document does not guess at it. Two things pull
opposite ways and I have not separated them: a duplicated axis makes the joint easier to reproduce
in one sense (there is less independent information than the axis count implies) and harder in
another (the acceptance must pass on slices that load on it twice). **That is the measurement to
run, not a thing to reason about**, and it is one variable, so it can be run cleanly: score the same
population with `seasonal_swing` removed and difference the ladders.

## Not fixed here, and why

The honest replacement -- the actual share of annual demand in the coldest half -- **needs the
summer simulated**, which is exactly the `simulate_premise` build the director approved on
2026-09-08 ("retire the closed form, use `simulate_premise`, half-hourly for gas"). Half-hourly gas
over a full year gives this axis for free and gives it correctly, including the part that makes it
genuinely independent: a household with more people has a larger flat hot-water base, so its gas is
*less* seasonally peaked than a single-person household in the same dwelling. That is real physics,
it is an axis that varies with people rather than with fabric, and it is unavailable to a closed
form that stops on 31 March.

Patching `0.15` and `0.5` into some other pair of numbers now would replace one invented constant
with another and would still be exactly collinear with `weather_sensitivity`.

## What is next, in order

1. **Re-run the ladder with `seasonal_swing` dropped**, one variable changed, and record what N does.
   Until that runs, the axis count published on the knowledge page should read **six independent
   axes of seven declared**, not seven.
2. **Restore it as a real quantity** when `simulate_premise` lands the full year, computed as the
   cold-half share of modelled demand rather than as a rescale of anything.
3. **A control that a declared axis is not an affine transform of another declared axis.** The
   smallest mechanism that catches this class: the correlation matrix of `values` must be full rank.
   One assertion, no register, and it would have caught this the day it was written.

**Falsifier for item 3:** `tests/tools/test_gas_carries_a_hot_water_term.py` is the file it belongs
beside; the control is red at `41501920c` and must be red on any tree where two declared axes are
exactly collinear. It is not written yet -- this document is filed before the fix rather than after,
so the claim that it was found before it was convenient is checkable.


---

## AMENDED 2026-09-08, same day -- the one-variable experiment ran and it settles the direction

Above I wrote: *"Two things pull opposite ways and I have not separated them... that is the
measurement to run, not a thing to reason about."* It ran. Same population, same seed, same ladder,
one variable changed -- `seasonal_swing` dropped from the scored vector.

| vector | axes declared | independent | smallest eigenvalue | **N at tolerance 0.05** |
|---|---:|---:|---:|---:|
| with `seasonal_swing` | 7 | 6 | 0.000000 | **6,816** |
| without it | 6 | 6 | 0.000003 | **5,215** |

**The duplicated axis INFLATES N by 31%.** Of the two effects I could not separate by reasoning, the
harder one dominates: a direction that appears twice is double-weighted in the joint slices, so the
acceptance must satisfy it twice while learning nothing new from the second copy. The sample was
being made larger by an axis that carries no information.

So the correction to the published figure runs the same way as the correction to its honesty. The
number was not merely scored over a mislabelled vector -- **it was too big, by about a third, for a
reason that is an artefact of the instrument rather than a property of the population.**

**The prediction I filed hours earlier was wrong in a way worth recording.** The gas brief predicted
that breaking the collinearity would RAISE N ("a 2-4x rise from breaking the r ~ 0.99 degeneracy").
That is right about set-point and schedule, which add real independent variation. It is exactly
backwards for this axis, and the difference is the thing to keep: **adding an independent axis
raises N; removing a DUPLICATE axis also lowers N.** Both are "breaking a degeneracy" in loose
speech, and they move the answer in opposite directions. The loose speech is what made one
prediction cover both.

Item 1 of "what is next" is therefore discharged, and item 3 -- the full-rank control -- is now the
whole of what is outstanding before the axis is rebuilt on `simulate_premise`.


---

## AMENDED AGAIN, same day -- it is THREE axes, and the control found what I did not

The title says two. It is three, and I only know that because I wrote the control instead of
trusting the reading I had already taken by hand. The control's first run refused a pair I had not
looked at.

    +1.000000   seasonal_swing            x  weather_sensitivity_kwh_per_degree_day
    +0.999997   seasonal_swing            x  turndown_ceiling_kwh
    +0.999997   weather_sensitivity...    x  turndown_ceiling_kwh

    eigenvalues  [4.9436, 1.0000, 0.9732, 0.0660, 0.0171, 0.0000, -0.0000]

**TWO zero eigenvalues. Seven declared axes, rank five, and only THREE directions carrying more than
1% of the trace.** `turndown_ceiling_kwh` is `hlc * 24 * (cold - warm degree-days)`, and that
difference is near-constant across cells because almost every cell heats on almost every day of the
window -- so it is a third scaled copy of the heat-loss coefficient.

**And it was only visible because a defect had just been fixed.** While the hot-water term was
leaking into the counterfactual (`41501920c`), `turndown_ceiling_kwh` correlated +0.38 with
HEADCOUNT, which made it look partly independent of fabric. Removing the leak removed the spurious
independence and showed the axis had always been a copy. **A defect was flattering the instrument.**
Fixing it made the measurement look worse and the tree more honest, which is the direction that
counts -- and it is the second time today that fixing one thing exposed a larger thing underneath it.

This also revises the correction upward. Dropping `seasonal_swing` alone moved N from 6,816 to
5,215. That was measured with `turndown_ceiling_kwh` still in the vector as a third copy, so **31%
is a lower bound on the inflation, not the size of it.**

### The control is landed and it is a ratchet

`test_NO_NEW_PAIR_OF_DECLARED_AXES_IS_EXACTLY_THE_SAME_AXIS` names the three known pairs in
`_KNOWN_COLLINEAR` and reds on any pair not on that list. It also reds if a listed pair STOPS being
collinear without being deleted, so the list cannot rot into a permanent excuse. Poison round:
making a fourth axis an affine copy reds it; the tree as it stands is green.

Landing it red was not an option -- a red control wedges every lane -- and weakening it to something
today's tree passes cleanly would have keyed it to today's answer. Keying it to the SET is neither,
and it costs one line to discharge when the axes are rebuilt.
