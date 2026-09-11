**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — a second estimand beside `method_skill.concordance`) · **Class:** measurements_that_mirror

# RESULT — the unselected cut is 0.4209, and the censoring term was missing from my own bridge

Graded against
`docs/staging/records/SEAT_PREREGISTRATION_THE_FIXED_HORIZON_ESTIMAND_THAT_DOES_NOT_CONDITION_ON_SURVIVAL_2026-09-08.md`,
landed as **`e1a7f1a56` before the estimand was implemented and before any run of it**, and against
`SEAT_RESULT_THE_UNSCORED_DECISIONS_ARE_EXACTLY_THE_DEPARTURES_..._2026-09-08.md`, which specified
the estimand and made its own prediction.

Run: `docs/observability/value_cycle_ab_fixed_horizon_2026-09-08.json`, the full 2016–2025 book,
214 priced decisions, observation end **2025-06-07**.

---

## The number

| | decisions | rank |
|---|---:|---:|
| `method_skill.concordance` — published, survivors, ratio | 168 | **0.5337** |
| the same, less the censored — leg 1 | 124 | 0.4991 |
| the same decisions in pounds — leg 2 | 124 | 0.5130 |
| **every priced decision in pounds — the estimand** | **161** | **0.4209** |

Null on every leg: exactly 0.5. The published figure's own null interval is [0.4494, 0.5503] at
p = 0.192 — *the survivor-only figure was already indistinguishable from chance.*

**The decomposition, one variable per step:** censoring **−0.0346**, unit **+0.0139**, population
**−0.0921**. They sum to −0.1128, which is exactly 0.5337 → 0.4209.

## The predictions, graded beside the numbers

**P1 — "the scored population rises from 168 to roughly 208". REFUTED, and by its own named
escape.** It is **161**, *lower* than the survivor-only population. 47 of 214 priced decisions are
**censored**: their 365 days had not finished when the settled book ended. The pre-registration
said *"I cannot predict the censored count and am not pretending to… If censoring is large, P1 is
wrong and the reason is a run-length artefact, which is exactly what property 2 exists to
surface."* That is what happened. The specifying result doc's own "168 → ~208" is refuted for the
same reason.

**This is the finding P1's failure buys:** the fixed-horizon estimand is *more* expensive in
sample than the concordance at this run length, because it insists on a closed horizon that the
concordance never asked for. 47 decisions is a bound a longer run removes and nothing else does.

**P2 — "the fixed-horizon concordance falls below 0.5334". HELD.** 0.4209, and the population term
alone is −0.0921. The reading the run composed: *"Admitting the departures LOWERS the figure, which
is what survivor-conditioning was hiding: the arm's price ranks the households it kept better than
it ranks the ones it lost."*

**P3 — "the unit change moves it by less than the population change". HELD.** |unit| = 0.0139
against |population| = 0.0921, a factor of 6.6. The sign of the unit effect was explicitly not
predicted and it came out positive.

**P4 — "`null_constant_signal_concordance` stays exactly 0.5 on every leg". HELD**, on all of
them. Independent by construction: a constant signal ties every pair, and `_concordance` scores a
signal tie as a half regardless of the outcomes, so the null cannot see the population or the unit.

**P5 — "the zero-outcome decisions will be the departures". HELD, 37 of 37**, on a key
`_survivorship` had never been asked on. Zero residue.

## What I got wrong, in the mechanism built to stop exactly this

**The bridge I built to prevent a misattribution was itself missing a term, and on its first live
run that term was larger than one of the terms it had.**

The pre-registration reasoned that *two* things change between the published figure and this one —
the population and the unit — and specified three nested legs to separate them. Three legs is
wrong. **Censoring restricts the population *before* the first leg**, so it is invisible between
the legs that follow it. The three-leg bridge accounted for −0.078 of a −0.113 move and offered no
account of the rest. A reader would have attributed the whole thing to survivorship.

Censoring is **−0.0346**. The unit term it silently displaced is **+0.0139**. The missing term was
two and a half times the size of one of the terms that was there.

**Nothing but printing the numbers at real inputs would have caught it.** Every unit test passed,
all fifteen mutations died, the shape was correct, and the block was internally consistent. It was
wrong against the one thing that was not in any fixture: a real book whose observation window ends
in the middle of forty-seven priced terms.

Corrected in the same lane: leg 0 `the_published_population_ratio_outcome` now reproduces
`method_skill.concordance` through a different code path, so the bridge **starts at the figure the
page publishes** rather than near it. That forced the coverage gates to run *before* the horizon
test — the concordance applies those gates and has no horizon test, so excluding a decision for the
wrong one would put two differences between leg 0 and the figure it checks.

**The artefact above carries three legs, not four**, because it is the run that found the defect.
Its leg 0 is the published concordance on the same page, so the four-term decomposition in this
document is exact and reproducible from it; the next run carries the leg natively.

## Two mutations that survived, and what each cost

**Replacing each leg's computed null with the literal `0.5` survived the first battery.** A value
assertion cannot tell a computed constant from a typed one, and a constant signal really does score
a half on every population and every unit — so the mutation was invisible to a test written against
the real shape. They differ in exactly one place: a leg where every outcome ties has no comparable
pair, so `_concordance` returns `None` and the null must too. A literal 0.5 there publishes the
null for a population nothing can rank. That is the fail-open killer and it is now driven, on a
book where every priced term settled nothing.

**Zeroing the censoring term survived twice.** The first time there was no assertion on it at all.
The second time the fixture had a censored decision that had settled *nothing* — which never
reaches a row, so leg 0 equalled leg 1 and the fixture agreed with the mutation. It needs a
censored decision that **did** settle, priced low where it produced most. *A fixture that reaches
the branch is not the same as a fixture that makes the branch matter.*

## What is on the page, and what is not

`site/capabilities/index.html` renders `fixedHorizonBlock` immediately under the survivorship split
— both populations named, all four legs with the population each was computed over, the censored
count named as a run-length artefact when there is one, and this cut's own different bound (pounds
carry account size and this estimand cannot normalise it away, because a household that left has no
metered volumes over the horizon).

**The live feed is still in the withheld branch and the page correctly says so.** The page's input
is `docs/observability/value_cycle_ab_s1_three_arm.json`; the run that carries the estimand is at
`value_cycle_ab_fixed_horizon_2026-09-08.json`. **Which artefact the page reads is not mine to swap
in passing** — `CURRENT_WORLD_THREE_ARM_PATH` and `THREE_ARM_PATH` have a recorded history of
moving one without the other, and "the page is a run behind" is already an owed item that predates
this work. Until that is decided, the page says it cannot offer the unselected cut and names why.

## What is next

1. **Decide which artefact the page reads**, and move both path constants together or neither. That
   is the one step between this and a reader seeing 0.4209. It is the same decision the
   already-owed "the page is a run behind" needs, and doing them separately would move two things
   at once.
2. **The censoring cost is a finding in its own right and is not yet anywhere but here.** 47 of 214
   priced decisions, 22%, unscoreable by this estimand at this run length — a bound that a longer
   observation window removes and that no book size does. It belongs beside `A46`'s book-depth
   arithmetic, which is about a different bound entirely.
3. **Neither cut clears its null.** 0.5337 sat inside [0.4494, 0.5503]; 0.4209 is below that
   interval, but the interval belongs to the *other* leg's population and this document does not
   borrow it. The estimand's own permutation null is not computed — `concordance_null_spread` runs
   on the concordance's points only. Until it is, **0.4209 is a point estimate with no bound of its
   own, and no claim that the arm ranks worse than chance is available from it.**
