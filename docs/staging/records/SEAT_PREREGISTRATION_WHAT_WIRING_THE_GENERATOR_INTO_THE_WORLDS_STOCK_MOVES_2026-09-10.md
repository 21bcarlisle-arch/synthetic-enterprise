**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# PRE-REGISTRATION — what wiring the generator into the world's premise stock moves, and what it does not

**Filed 2026-09-10 21:0x BST, delivery seat, BEFORE the wiring is written.** Director console,
2026-09-10: *"Wire the sample. That's the priority until my allowance resets Monday morning… the
population the world runs on should be the one the sampler chooses, weighted."*

This document exists because two of the numbers below were measured **before** the build and they
partly refute the instruction, and because the one number that decides whether the build was worth
doing — what it does to the company's margin — is one I cannot predict.

---

## What was measured first, read-only, and what it settled

**The choosing does not earn its keep at the world's size.** `choose_for_difference` +
`fit_weights` against 5 random draws, worst KS across the six demand axes, over a 20,000-point
generated population:

| N | chosen + weighted | random mean | ratio |
|---|---|---|---|
| 40 | 0.1361 | 0.2280 | **1.68×** |
| 91 | 0.0885 | 0.1448 | 1.64× |
| 173 | 0.0640 | 0.1068 | 1.67× |
| 400 | 0.0457 | 0.0597 | 1.31× |
| 582 | 0.0426 | 0.0583 | 1.37× |
| 1000 | 0.0350 | 0.0408 | 1.17× |
| 2000 | 0.0183 | 0.0290 | 1.59× |
| **4400** (the world's stock) | **0.0177** | **0.0184** | **1.04×** |

At the size the world actually runs, a deliberately chosen weighted sample is **four per cent**
better than picking at random. The design's whole value is compression, and at 4,400 draws out of a
20,000-point population there is nothing to compress. Separately: `smallest_n_chosen` returns
**5,215** under its per-stratum criterion — the world's 4,400 is *below* the sampler's own
acceptance threshold, not a candidate for reduction from it.

**I am not repeating the "22× better than random" figure** from the 2026-09-08 console reply. It
does not reproduce on KS distance at any N I measured, best case 1.68×. It was probably measured on
distinct cells covered, which is a different quantity; it is not evidence for this build and is
filed as its own question.

**The real reason nothing connected.** The world's dwelling record cannot express the demand vector
at all:

| attribute the physics needs | on `simulation.household.Household`? |
|---|---|
| floor area band | **absent** |
| loft insulation flag | **absent** |
| cavity wall insulation flag | **absent** |
| PV | present but **hardcoded `has_solar=False` for every home ever drawn** |
| insulation level | present, but a **deterministic lookup on the EPC letter** — six distinct values in the whole country |

Floor area is the dominant term in heat loss and the world does not carry it. So the six demand
axes are not merely unmeasured on the world's population — they are **unmeasurable** on it. That is
why `demand_vector_coverage` has no importer under `simulation/`: not an oversight, an impedance
mismatch nobody had written down.

## What is therefore being built, and what is being refused

**BUILT: the generator into the stock.** `draw_premise` gains a path that takes its structural
attributes from one row of the NEED-fitted joint (`stock_joint_generator.fit_joint`, 1,292 real
co-occurring combinations) raked onto the world's own published marginals, instead of drawing
(type, era, EPC) from a 144-cell joint and then heating, bedrooms, insulation and PV independently
or not at all. `Household` gains `floor_area_band`, `has_loft_insulation`,
`has_cavity_wall_insulation` and `has_mains_gas_supply`, defaulting to `None` — `None` meaning "this
dwelling was not drawn from the fitted joint", which cannot be mistaken for "no loft insulation".

**REFUSED: the chooser into the stock.** Measured at 1.04×. Wiring it there would be machinery that
changes no number, and this project has a class register for that.

**Two inherited decisions, cited rather than re-made.** NEED's 30.2% unrated rows are dropped before
raking on the EPC axis, which is the rule `tools/need_stock_joint` already established and whose
residual it already records ("what would not wash out is a home's EPC being systematically better or
worse than an unrated home of the SAME type and age — and NEED cannot answer that"). And NEED's
`MAIN_HEAT_FUEL` is carried as `has_mains_gas_supply` — a fact about a **meter** — and is NOT mapped
onto `heating_system`, because the 2026-09-07 stretch entry established these are different concepts
and 50.3% of flats read as "not gas" when they are communal or unmetered.

---

## The predictions, in bands, decided before the run

**P1 — the three published marginals hold.** Property type, build era and EPC band each move by
**less than 1.0 percentage point** against today's 4,400-home stock. They are raked to the same
published targets, so a larger move means the rake is not doing what I think it is.

**P2 — solar stops being zero.** `has_solar` goes from **0.0%** to **1.2–2.2%** (NEED's PV flag is
800/50,000 = 1.6%).

**P3 — insulation stops being a function of the EPC letter.** Today the whole country has exactly
**6** distinct `(epc_rating, insulation)` pairs. After, the count of distinct
`(epc_rating, has_loft_insulation, has_cavity_wall_insulation)` triples is **greater than 12**.

**P4 — the demand vector becomes computable on the world.** All six axes evaluate on the world's own
4,400 homes without a `None`, and their worst KS against the generated reference is **below 0.05**.
This is close to an identity — same generator, same physics — so if it FAILS, the mapping from a
case to a `Household` has lost something, and that is the result worth having.

**P5 — the company's net margin moves, and I cannot call the sign.** |Δ net margin| is **greater
than 1%** of £147,887. I am recording no direction. The homes change, so their consumption changes,
so revenue and cost of supply both move; PV appearing for the first time pushes one way and a
different EPC/fabric mix pushes either way. *This is the prediction I most expect to be wrong about
in magnitude and it is the reason this file exists.*

**P6 — the settlement sample rate does not move.** It stays at **0.183 ± 0.005** and the wins
refused stay at **409 ± 10**. Nothing in this step touches the settlement budget. If it moves, the
budget is coupled to dwelling attributes through a path nobody has named, and that finding outranks
the rest of this document.

**P7 — the book stays roughly the size it is.** Commercial accounts **582 ± 30**, settled **173 ±
15**. Acquisition is driven by the funnel, the prospect ceiling and the budget — none of which this
step touches.

## What would make me abandon the build rather than adjust it

If P1 fails by more than 3pp on any axis, the raked joint is not carrying the published population
and the world would be **less** faithful after the change than before. That is the one outcome where
the correct move is to revert and file, not to tune the rake until it agrees.

## How it will be graded

The same table, run before and after, printed into the stretch log beside these predictions whichever
way they went — including P5's magnitude, which is the one with no band around its direction.

---

# GRADED, 2026-09-10 21:0x BST

Both arms run at ONE HEAD with ONE variable changed — `STOCK_FROM_FITTED_JOINT` set in a driver
outside the tree, not an env var and not two tree states. Old arm 13 min, new arm 15 min, both rc 0.

**Three of seven predictions hold. Three fail. One was the wrong question.**

| | prediction | outcome | |
|---|---|---|---|
| **P1** | published marginals move < 1.0pp | worst move **1.84pp** (SEMI_DETACHED) | **FAILS as written** |
| **P2** | solar 1.2–2.2% | **1.50%** (from 0.00%) | HOLDS |
| **P3** | > 12 distinct (epc, loft, cavity) triples | **19** (from 6 pairs) | HOLDS |
| **P4** | the demand vector "becomes computable" | it was **always** computable | **WRONG QUESTION** |
| **P5** | \|Δ net margin\| > 1% | **−0.37%** (£376,131.94 → £374,745.50) | **FAILS** |
| **P6** | sample rate 0.183±0.005, refused 409±10 | **0.1820, 409** — identical in both arms | HOLDS |
| **P7** | accounts 582±30, settled 173±15 | **582 / 173** — identical in both arms | HOLDS |

**P1 — the band was the wrong test and I set it on the wrong thing.** It compared the new stock
against the OLD SAMPLE, when the property that matters is whether each stock carries the PUBLISHED
marginal. Asked that way the new stock is as good or better: worst |z| against published on EPC
goes **3.03 → 0.87**, and on property type 1.53 → 2.30. The raked joint hits all three published
margins to 1e-6, verified directly. A 1.84pp gap between two independent 4,400-draw samples is 2.0
standard errors across sixteen categories — ordinary. *I predicted a population quantity and graded
it on a sample.*

A one-seed reading then nearly produced a second error on top: `ERA_1919_1944` came out **3.29 SE**
light, which reads exactly like a biased band→era mapping. Across five seeds its mean z is **−0.09**
and no era exceeds |0.44|. It was the draw. That check is kept as a control, not a note.

**P4 — the claim underneath it was too strong, and the correction matters more than the
prediction.** I asserted the demand vector was *unmeasurable* on the world because `Household` had
no floor area. It always evaluated: `fabric_physics.floor_area_m2` derives an area from property
type and bedroom count. What is true is narrower — the area was inferred from a bedroom count drawn
from property type alone, `insulation` was a lookup on the EPC letter, and `has_solar` was hardcoded
`False`.

So the deliverable is a **level correction on the mission's own quantity**, not a new capability.
At 4,400 homes with weather held constant:

| | old (inferred) | new (measured) |
|---|---|---|
| mean floor area | 79.4 m² | 84.8 m² |
| mean fabric | 144.4 W/K | 168.8 W/K |
| **mean remaining insulation ceiling** | **41.5 W/K** | **61.4 W/K** |
| 10th pct of that ceiling | **0.0** | 2.0 |
| spread (cv of fabric W/K) | 0.729 | 0.744 |

The remaining insulation ceiling is *what is left to do* — the size of the intervention the company
could actually sell. The old model understated it by a third and put a tenth of the country at
**exactly zero** remaining opportunity, because an A/B rating mapped to FULL insulation by
construction. The spread barely moves; it is the level that was wrong.

**P5 and P6/P7 together are the R13 evidence.** The company's net margin moves −0.37% and the book
is identical to the account — 582 commercial, 173 settled, 91 of 500 wins settled, 409 refused, in
both arms. The acquisition funnel and the settlement budget are insensitive to what the dwellings
are. A baseline fidelity change that leaves the score alone is the cleanest evidence available that
it was not tuned against the score, and it also says plainly that **this change buys fidelity, not
profit** — anyone reading the commit for a P&L story should stop here.

**The abandon criterion was not met.** P1 failing by more than 3pp on any axis would have meant the
raked joint was not carrying the published population; the worst move was 1.84pp against the old
sample and 2.30 SE against published, and the rake itself is exact. The build stands.

## What this leaves open, carried forward

The chooser is still unwired, on purpose, and the measurement says where it would earn something:
**1.64× at N=91**, which is exactly the size of the settled book. The settlement budget refuses 409
of 500 wins by a systematic count-based cull that is unbiased by year and blind to what the homes
are. Now that the dwellings carry measured attributes, that sample could be chosen for difference
and weighted — and that is the piece where "the constraint we argue about" becomes a real question
rather than a phrase. It needs its own pre-registration, because it moves every published financial
figure, and it is not in this landing.
