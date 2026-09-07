**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_19_who_lives_where_money_and_composition

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the sample-design rows it will publish; the declaration is replaced when the
page lands.

# The sample size is a floor, and strata are what multiply it

**Measured 2026-09-07**, delivery seat. Reproduce with
`python3 -m tools.demand_vector_coverage --measure`.

The director refused the 275 figure and gave his reasoning:

> *"It's the number for a partial vector... the number has moved an order of magnitude every time an
> axis arrived: 800 with retrofit flags, 8,500 when electricity and the non-gas stratum went in. A
> single missing stratum multiplied it tenfold. I have no reason to expect the remaining axes to
> behave differently. I'd rather carry thousands and know why than carry 275 and find out later."*

**He is right that it is a floor and it is now published as one.** But the history says something
sharper than "every axis multiplies it", and the distinction is the useful part.

---

## The whole history of this number, and what moved it

| what was in it | N at tolerance 0.05 | what changed | move |
|---|---:|---|---|
| annual gas as a scalar | 13 | — | — |
| five output axes, variance criterion | 233 | criterion | — |
| gas + swing + 2 ceilings, E&W gas-heated only | 1,200 | distributional criterion | — |
| **+ electricity, + non-gas stratum** | **8,500** | **a missing STRATUM** | **×7** |
| same axes, chosen and weighted | 275 | **design**, not content | **÷31** |
| + Scotland, households generated not selected | 273 | geography | **×1.0** |
| **+ weather sensitivity** | **243** | a correlated continuous axis | **×0.9** |

**The two order-of-magnitude moves were not the same kind of event, and only one of them was an
axis arriving.**

- **8,500** came from a missing **stratum** — 18.5% of the stock, non-gas, with *different physics*.
  That is the move the director is generalising from, and he is right to.
- **275** came from fixing the **design** — random sampling replaced by chosen-and-weighted. That was
  never an axis; it corrected a measurement that was not doing what its own docstring claimed.

## So the mechanism is: strata multiply, correlated axes do not

Since the design was fixed, two things have been added and neither multiplied anything:

- **Scotland** — the coldest 8% of the book, structurally excluded before generation. 275 → **273**.
  It is more of the cold end rather than a new region of behaviour: the same physics, colder.
- **Weather sensitivity** — the axis the director named as unconfirmed. Now measured and spanned.
  273 → **243**. It is strongly correlated with the gas level, so it demands few new cases.

**A stratum is different in kind.** Non-gas households are not "more of" gas households; they have a
different heat source, a different bill and a different response to weather. The sample must span
each stratum *in its own right*, so strata compose multiplicatively where correlated axes compose
almost for free.

## The prediction, filed before the axes are built

**The remaining axes the director named are mostly STRATA, so I expect them to behave like the
non-gas one and not like Scotland.**

| axis | kind | strata | expected effect |
|---|---|---:|---|
| payment method | stratum | 3 (DD, standard credit, prepayment) | multiplicative |
| meter read pattern | stratum | 2 (estimated / half-hourly settled) | multiplicative |
| arrears position | stratum | ~2 | multiplicative |
| move history | mostly continuous | — | small |
| credit position | correlated with arrears | — | small |
| half-hourly shape | continuous, correlated | — | small to moderate |

**If the three genuine strata compose independently that is 12 combinations, and if each must be
spanned in its own right the figure lands near 243 × 12 ≈ 3,000.** They will not be fully
independent — prepayment correlates with arrears — so the honest range is **low thousands**, which
is the order the director said he would rather carry.

**This is a prediction and it is written down before the measurement, so it can refute me.** If
payment method lands and the figure moves by 10% rather than 3×, the stratum mechanism is wrong and
I will have to say so.

## What is published, and how

`UNCOUNTED_AXES` now enumerates the seven axes in the module itself, and `measurement()` emits
`"this_is_a_floor_not_an_answer": true` beside every figure. The number cannot be quoted from the
tool without the caveat travelling with it.

**One thing the declaration structurally cannot say**, and it is worth naming: the AST reduction
control only accepts `blind_to` entries that are components of the declared subject vector. Payment
method, read pattern, arrears, moves and credit position are not in the demand vector at all, so the
declaration *cannot express* that this N does not span them. The gap between what the declaration
can say and what is actually missing is exactly why the figure needs the floor label rather than
just the declaration.

## What generating bought

- **Scotland reachable.** 143,511 → **194,865 cells** (+51,406, +36%), 24.7m → **27.1m households**.
  Selection could never have reached it: NEED has no Scottish dwellings and the exclusion was
  written into the cell filter by name.
- **Combinations beyond the survey.** The joint holds 1,292 observed combinations and can produce
  rare-but-real ones a 50,000-row sample missed.
- **Plausibility, measured rather than assumed.** Drawing from the joint produces **0%**
  combinations the evidence never shows; drawing each attribute independently produces **25%**.
  That 25% is what "draw from the fitted joint rather than independently" actually buys.
- **Scotland raked, not assumed.** The joint is England-and-Wales-fitted, so its property-type
  margin is moved onto Scotland's own Census 2022 UV402 shares — 34.4% flats, far above England's.
  What a Scottish semi is like inside is still taken from an English semi, and that carry-over is
  the remaining assumption.

## A plausibility rule the evidence refuted

"Cavity insulation on a pre-1930 dwelling" looked like the clearest impossible combination the
fields can express — solid walls have no cavity to fill. Generating strictly from the joint still
produced it at **1.3%**, which means NEED's own dwellings show it. They do: the band is *"before
1930"* and cavity construction is general through the 1920s. **A rule that calls observed dwellings
impossible is a wrong rule, not wrong data**, so it was demoted from a refusal to a reported
observation.
