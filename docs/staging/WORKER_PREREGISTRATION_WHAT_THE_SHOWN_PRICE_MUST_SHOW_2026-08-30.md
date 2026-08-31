**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# Pre-registration: what C3 — the price the household is shown — must show

**Filed:** 2026-08-30, before a single line of C3 was written and before any run.
**Reads on:** `docs/design/CHOICE_AND_CHANNEL_ROADMAP.md` §C3 ·
`docs/staging/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md` §4.

A prediction filed after the answer is not a prediction. This exists so the run can refute me.

---

## The premise, checked rather than assumed

The roadmap asserts *"every household today responds to a true differential computed at its own
billed consumption"*. That was worth checking, because the differential itself
(`simulation.customer_events._price_differential_vs_market`) is a pure **unit-rate fraction** and
carries no consumption at all — so the premise could have been wrong and C3 empty.

It is not. Consumption enters one line later.
`market_switching_propensity.churn_position_multiplier` turns that fraction into POUNDS using
`_annual_bill_gbp(billing_account, ...)` — *"what we billed THIS household over the trailing year,
across ALL its supply points"*. Ofgem/BMG 2024 is the source for households valuing savings in
absolute terms, and that part is right. What no household can observe is **its own trailing-year
settled bill**, which is the number the world hands it.

## The change, and it is deliberately one variable

`shown_annual_bill_gbp = own_trailing_year_gbp × (TDCV_kwh / own_annualised_kwh)`

The same tariff, the same trailing window, the same standing charges, the same construction — at
**typical** volume instead of the household's own. Only the volume moves. The alternative
constructions (a fresh TDCV bill from unit rate × TDCV, or a commodity-only figure) would move the
LEVEL as well as the heterogeneity, and then no result could be attributed.

`TDCV_DUAL_FUEL_MWH = 14.2` already exists in `simulation/competitor_reference.py`, cited to
Ofgem's published TDCV (2,700 kWh single-rate electricity + 11,500 kWh medium gas). Reused, not
re-stated: one name, one number.

The **settlement** keeps the true bill. Only the switching decision moves to the shown one.

## Measured before the change, on the live book

162 domestic households, annualised from `site/data/customers.json`:

| | shown ÷ felt saving |
|---|---|
| median | **0.81** |
| mean | 0.97 |
| min / max | 0.19 / 5.54 |
| households who would perceive a **smaller** saving than today | **106 of 162** |

## The predictions

1. **Most households become less switchy, and the population level therefore falls.** The median
   household perceives 19% less saving than today. The level anchor is fitted to hold the realised
   rate inside the published band, so `test_the_worlds_realised_departure_rate_is_inside_the_
   published_band` should go **RED below the band** after this and before a re-fit. If it goes red
   ABOVE the band, my sign is wrong and the step must be re-read before it is believed.
2. **The company's measured advantage must not improve.** The world's truth becomes flatter — the
   per-household bill scale collapses from 162 values to three (electricity-only, gas-only,
   dual-fuel) — so there is LESS per-customer variation for a per-customer belief to discover.
   If the value arm's advantage over the flat control rises after C3, that is a signal the step is
   wrong, not a win. This is the roadmap's own filed direction and I am not softening it.
3. **The belief-vs-truth gap should widen, not narrow.** The company's estimator keys on its own
   view of the household; the world now keys on a convention the company is not using. A NARROWING
   gap here would mean the company accidentally became right, which needs explaining before it is
   published — and under the standing rule (`docs/design/INDEPENDENCE_IS_NOT_INFERENCE_2026-08-30.md`)
   a narrower gap is not evidence of skill in any case.
4. **2022 should reproduce as a price effect through the convention** rather than by assertion. The
   crisis year's switching collapse is a savings collapse; at TDCV volume it should still collapse.
   If 2022 only reproduces when the household's own bill is used, the convention is not carrying
   the mechanism and the roadmap's §C3 claim is overstated.

## What would make me abandon rather than re-fit

If the level moves so far that no anchor inside the published band can be fitted — i.e. the
shown-price world cannot reach the record at any level — then the convention is wrong for this
population and C3's simplification (one TDCV pair for everybody) is the thing to revisit, not the
anchor. **Widening the band is not on the table.**

## A defect noticed in passing, not fixed here

Several accounts labelled `resi` carry annualised **electricity-only** consumption of 11,700–14,300
kWh/year — up to **5.3× TDCV**, and industrial-looking. They receive the domestic switching curve
today. This is adjacent to `WORKER_FINDING_ELEVEN_DRAWN_HOUSEHOLDS_ARE_WEARING_A_BUSINESS_LABEL`
but is not the same accounts (these are founder `C`-series). Recorded here rather than folded into
C3, because it moves the same numbers and folding it in would leave neither attributable.

---

*Filed before the work. Whatever the run says, this document is not edited — the result is written
beside it.*

---

# THE RESULT, AND PREDICTION 1 IS REFUTED

**Measured 2026-08-31, two full captures in an isolated worktree at `915bfab9b`** — the same tree
in both arms, differing only by `simulation/shown_price.py` and the seam in `customer_events.py`,
so that another lane's uncommitted C1b work could not confound it. The world is seeded and
deterministic, so these differences carry no run-to-run noise: they are exact.

| year | band | baseline % | in? | C3 shown % | in? | move |
|---|---|---|---|---|---|---|
| 2016 | 17.0–17.6 | 17.60 | yes | 18.10 | **NO** | +0.50 |
| 2017 | 13.5–14.0 | 14.00 | yes | 14.31 | **NO** | +0.31 |
| 2018 | 19.5–20.0 | 20.00 | yes | 20.14 | **NO** | +0.14 |
| 2019 | 20.7–21.3 | 21.30 | yes | 21.83 | **NO** | +0.53 |
| 2020 | 22.5–23.0 | 23.00 | yes | 23.68 | **NO** | +0.68 |
| 2021 | 17.9–18.4 | 18.40 | yes | 18.02 | yes | −0.38 |
| 2022 | 2.9–4.3 | 4.30 | yes | 4.16 | yes | −0.14 |
| 2023 | 8.9–12.5 | 12.50 | yes | 12.44 | yes | −0.07 |
| 2024 | 12.5–16.1 | 16.10 | yes | 16.21 | **NO** | +0.11 |
| 2025 | 14.3–17.9 | 17.90 | yes | 17.77 | yes | −0.13 |

2017–2024 mean: **16.20% → 16.35%, +0.15pp.** Departures **79 → 79**. Renewal decisions 465 → 459.

## I predicted DOWN. It went UP. That is the refutation, in my own words

The pre-registration says: *"the population level therefore falls … should go RED below the band …
If it goes red ABOVE the band, my sign is wrong and the step must be re-read before it is
believed."* It went red **above** the band in five years. **My sign was wrong** and this section is
what the pre-registration was filed to make possible.

## Two things the table says that the prediction did not anticipate

**1. The band exits are mostly an artefact of the anchor, not a measure of C3's size.** Look at the
baseline column: 17.60 against a 17.0–17.6 band; 14.00 against 13.5–14.0; 23.00 against 22.5–23.0.
**The baseline sits exactly on the band's high endpoint in every year**, because
`departure_level_anchor` was fitted to that endpoint — §6's anti-flattering tie-break. There is
*zero headroom above*, so **any** upward movement, of any size, exits the band. A +0.11pp move in
2024 "leaves the published band" and means almost nothing.

That is worth more than this experiment: **the level control cannot distinguish a small honest
change from a large one in the upward direction, because the fit left it on the ceiling.** Filed
separately rather than buried here.

**2. The effect is small — 0.15pp on 16.2%, under 1% relative — and it moved no departures at all.**
79 either way. The 6 fewer renewal decisions are re-timing, not attrition.

## Why my sign was wrong, as a hypothesis to test rather than a conclusion

My 0.81 median shown/felt ratio was computed over **lifetime book totals annualised**, while the
world scales by the **trailing-year bill at each renewal**. Those are different populations, and I
compared one to reason about the other — the ratio-of-two-different-things error I have a standing
note about.

The candidate mechanism for the sign: `_savings_to_rate` is piecewise and flattens toward its
calibrated ceiling, so a household already deep in the saturated region loses little propensity
when its perceived saving is cut, while a low-consumption household — whose shown bill is up to
**5.5×** its own — gains a lot when lifted from the steep part of the curve. The gains at the
bottom would then outweigh the losses at the top. **This is not established.** Testing it means
splitting the per-decision `sim_price_response` change by where each household sat on the curve,
which is one pass over the two captured tables and is the next step.

## What is NOT answered

Predictions 2 and 3 — that the company's advantage must not improve, and that the belief-vs-truth
gap should widen — need the value-arms A/B, a separate run that has not been made. **C3 is
therefore measured but not cleared, and it is not landed on `main`.** The band exits above would
need the anchor re-fitted whatever the cause, and re-fitting to absorb a change whose mechanism I
cannot yet explain would be fitting the world to make a control green.

*The prediction above is left exactly as filed.*

---

# THE CURVE-POSITION SPLIT, AND IT REFUTES MY OWN EXPLANATION TOO

**Measured 2026-08-31** by `tools/split_price_response_by_curve_position.py` over the two captured
tables, now both in the repo: `docs/reports/c2_departure_factors.json` (baseline) and
`docs/reports/c3_shown_price_departure_factors.json` (arm). 459 of 465 decisions pair; the 6
unmatched are the re-timing already reported.

The hypothesis above was: *"a household already deep in the saturated region loses little propensity
when its perceived saving is cut, while a low-consumption household gains a lot when lifted from the
steep part of the curve. The gains at the bottom would then outweigh the losses at the top."*

**That is not what happened. Curve position does not decide the sign — the company's own price side
does.**

| baseline curve position | n | cens | mean £ → arm | price_response | Σ Δp_churn pp | departures |
|---|---|---|---|---|---|---|
| **CHEAPER (we undercut) — 338** ||||||
| 0–100 steep bottom | 139 | 0 | 45 → 34 | 0.853 → 0.886 | **+24.69** | 27 → 28 |
| 100–250 steepest | 103 | 0 | 167 → 134 | 0.533 → 0.621 | **+44.91** | 23 → 23 |
| 250–400 flattening | 40 | 6 | ≥314 → ≥241 | 0.333 → 0.430 | **+18.12** | 4 → 4 |
| ≥400 SATURATED | 56 | 56 | ≥400 → ≥345 | 0.227 → 0.298 | **+13.03** | 4 → 4 |
| **side total** | 338 | | | | **+100.75** | |
| **DEARER (we price above) — 121** ||||||
| 0–100 steep bottom | 75 | 0 | 37 → 28 | 1.148 → 1.115 | **−9.09** | 13 → 13 |
| 100–250 steepest | 32 | 0 | 156 → 127 | 1.852 → 1.677 | **−15.20** | 4 → 4 |
| 250–400 flattening | 6 | 0 | 304 → 266 | 2.957 → 2.875 | **−2.57** | 2 → 2 |
| ≥400 SATURATED | 8 | 0 | 500 → 347 | 5.599 → 3.640 | **−27.13** | 1 → 1 |
| **side total** | 121 | | | | **−53.99** | |

**Net +46.76pp summed, +0.1019pp per decision.**

## Why the hypothesis is wrong

1. **Every segment within a side carries the SAME sign.** There are no "losses at the top" on the
   cheaper side — the saturated bucket contributes **+13.03pp**, in the same direction as the
   bottom. The losses are entirely on the *dearer* side, where every segment is negative.
2. **The largest single contributor is not the bottom** — it is the 100–250 *steepest* segment
   (+44.91pp on 103 decisions), which is where the curve's slope is greatest. That is the
   ordinary consequence of a slope, not the saturation story I told.
3. **0 violations, out of 422 moved decisions**, of *"fewer perceived pounds → more switchy when
   we are cheaper, less switchy when we are dearer."* The relationship is monotone within a side.
   Curve position sets the **size** of a household's move; **side sets the direction.**

## The actual mechanism

Perceived pounds **fell** for 335 of 459 decisions (median shown/felt ratio at renewal **0.692** —
the renewing population consumes *more* than TDCV, so its shown bill is smaller). When we are
cheaper, the perceived saving is what *holds* a household; shrinking it moves them toward parity,
and parity is switchier than cheap. **338 of 459 decisions are on that side, so the book-level
effect is up.**

This also predicts the year-by-year sign, which the original write-up left unexplained:

| | cheaper-majority years | dearer-majority years |
|---|---|---|
| years | 2016, 2017, 2018, 2019, 2020, 2023, 2024 | 2021, 2022, 2025 |
| level moved | up (+0.11 … +0.68) — **6 of 7** | down (−0.38, −0.14, −0.13) — **3 of 3** |

**8 of 10 years' sign is set by the arm mix alone.** 2023 is the exception: 96% cheaper yet moved
−0.07pp. Not explained, and stated as unexplained rather than rounded away.

## A defect found in my own first pass, recorded because it nearly reached this table

The first inversion extrapolated `_savings_to_rate`'s last graduated segment across the **jump
discontinuity at £400** (the curve steps 0.18 → 0.22 there; rates in [0.18, 0.22) are unreachable)
and reported a mean of **£520** for a bucket whose every member is censored at £400. Caught by
printing the curve at real inputs before trusting the table. The `cens` column and the `≥` marks
now say which figures are floors rather than means.

## WHAT THIS CHANGES ABOUT LANDING C3 — AND IT IS THE ARGUMENT FOR *NOT* LANDING IT

The blocker recorded on `edd5a497e` was *"a world change whose mechanism I cannot yet explain is
not one to land"*. **That blocker is discharged: the mechanism is established above.** But the
split replaces it with a sharper one, and this is a finding rather than a restatement:

> **C3's effect on the world depends on where the company chose to price.** Same world change,
> same households: **+100.75pp** where the company undercut the market, **−53.99pp** where it
> priced above. The convention does not have a fixed sign — it has the company's sign.

That is exactly why **predictions 2 and 3 cannot be waived**. They ask whether the company's
measured advantage improves and whether the belief-vs-truth gap widens, and both are questions
about a *different pricing arm* — which this split now shows will get a **different sign** from
the identical world change. Landing C3 on the strength of a run made at one price position would
be generalising from the one arm whose answer cannot speak for the others.

**C3 remains NOT LANDED. The blocker is now specific and testable: the value-arms A/B run.** The
band exits above are separately unreadable as evidence — the anchor sits on its ceiling with
**0.00pp room above in all ten years**, so a +0.11pp move that shifted zero departures exits the
band identically to one ten times larger (`tools/measure_departure_level.py` now prints that
margin). The anchor is **not** being re-fitted to absorb C3: re-fitting to make a control green is
fitting the world to the answer, and it would be doing so for a move whose sign is a property of
our own price position.

*The prediction and the first result section above are left exactly as filed.*

---

# WHERE THE C3 ARM ACTUALLY IS, BECAUSE THIS DOCUMENT DID NOT SAY

Added 2026-08-31, on re-reading the blocker above rather than on new measurement.

**The defect in my own write-up.** Everything above names the next step precisely — the value-arms
A/B run — and nowhere says **where the code to run it lives**. It says only *"not landed on
`main`"*, which tells the next reader where it ISN'T. `simulation/shown_price.py` exists in exactly
one place and it is not in this repository's working tree, so a reader who draws the A/B run from
the sentence above would conclude the arm had to be rebuilt from the prose. That is how a blocker
that looks discharged-in-principle becomes a rebuild.

**Where it is, verified rather than remembered:**

| handle | value | checked |
|---|---|---|
| salvage tag | `salvage/c3-shown-price-measure` | → `f93fd1ea9`, `git ls-tree` shows `simulation/shown_price.py` |
| branch | `c3-shown-price-measure` | tip `f93fd1ea9` — **identical to the tag**, `git diff` empty |
| worktree | `/tmp/.../scratchpad/c3wt` | clean, idle, and **on `/tmp`** |

The arm is two files against `915bfab9b`: `simulation/shown_price.py` (new, 122 lines) and the seam
in `simulation/customer_events.py`, with `tests/simulation/test_shown_price.py` beside them.

**Cite the TAG, not the branch or the worktree.** The branch is being counted as an orphan by
`background/alarm_repetition.py` — *"[FORK ORPHANS] 1 orphaned fork branch(es) never merged home
[ENFORCE (salvage+reap)]"*, fired 3 times — and that reaper's enforce mode deletes the branch name.
The worktree is on `/tmp` and does not survive a reboot. **The salvage tag is the only durable
handle of the three**, and until this section it was named by nothing: the reaper wrote the tag, and
no artefact a reader would reach pointed at it.

**The tag is durable by construction, and that is why no new control is filed here.** I was going
to write a test asserting the arm stays reachable. `background/fork_reconciler.py` already carries
the floor — *"salvage ALWAYS precedes reap; a reap that cannot first confirm salvage is REFUSED"* —
mutation-proven in `tests/background/test_fork_reconciler.py`
(`test_salvage_precedes_reap_and_refuses_when_salvage_cannot_be_confirmed` asserts `branch -D` is
never called when the tag does not match the tip). The reap that deletes the branch cannot happen
unless this tag already holds the work. A second control over the same property would guard my own
pointer rather than the arm.

**This orphan is intentional and should not be read as an escape.** The branch is unmerged because
the section above decided it stays unmerged — C3's sign is a property of our own price position, so
one arm cannot speak for the others. It is not abandoned work that lost its way home. What was
missing was only the pointer, and the alarm was right that something needed saying even though it
was wrong about what.

*No number above is restated or revised here. This section adds a location, nothing else.*

---

## DISPOSITION, 2026-08-31: parked deliberately, and the work was nearly lost

**The branch it was on is gone.** `c3-shown-price-measure` no longer exists — a fork/branch reaper
removed it, and `edd5a497e` survived only as a dangling object, one `git gc` from being
unrecoverable. Preserved as an annotated tag, **`parked/c3-shown-price`**, which no branch reaper
walks. Recorded here because "it is on a branch" turned out not to be a place things stay.

**And the measurement above no longer describes the world.** It was taken on a book of **465 renewal
decisions**; C1b landed the SVT product and the renewal population is now **144**, a different and
selected sub-population — the households that took a fixed deal. The +0.15pp level move, the
79-either-way departure count and the by-price-side split are all readings of a book that no longer
exists. **Re-deciding C3 means two fresh captures, not a re-read of this document.**

**Not landed, and the reasons ranked:**

1. Its own result refuted the prediction that motivated it, and the by-product finding (the
   departure-level control's missing headroom) was worth more than the experiment — **that half is
   already landed and discharged**, so the value has been extracted.
2. Predictions 2 and 3 remain untested, and testing them needs the value-arms A/B on a book that has
   since changed underneath it.
3. `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md` ranks four items above it, and one of them —
   union the departure routes and declare the denominator — has to land **first** anyway, because
   until it does, any C3 re-measurement would be taken on the same selected sub-population that made
   this one stale.

**What is still true and is why it is parked rather than deleted.** Modelling what a household is
*shown* — an annual bill at typical consumption — rather than only what it would pay per unit is a
**rung-2 fidelity improvement**: households compare annual figures, and the world currently asks
them to respond to a quantity nobody is ever quoted. That argument survives the refuted prediction
intact. It is the *effect size* that was not established, not the mechanism.

**Revisit when:** the routes are unioned and the denominator declared, at which point one capture
pair answers it properly. Until then this is a decision, not a queue.
