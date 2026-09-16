**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# SEAT RESULT — R4's tariff fit pays nothing for knowing the household, and R3's timing ceiling is 263 tonnes

**Date:** 2026-09-07
**Instruments:** `tools/r3_score_ceiling.py`, `tools/r4_product_ceiling.py`
**Artefacts:** `docs/observability/r3_score_ceiling.json`, `docs/observability/r4_product_ceiling.json`
**Measured on `run_output_c453dfbad_20260907T013529Z.json` — 352 full household-years, 2016–2024.**

A49 was minted for exactly two things and had neither: a ceiling instrument for R3 (the score) and
one for R4 (products beyond price). Before this pass, `grep` over `tools/` returned six ceiling
instruments — five EP13's, one R1's — and none touching either. Both now exist, both run, and both
declare per published quantity whether it is a true CEILING, a handicapped FLOOR, or NOT A BOUND.

---

## R4 — the result that retires a candidate

| | 2016–2024, 352 household-years | bound |
|---|---|---|
| **LEVEL** — put every household on the single best tariff | **£211,359** | CEILING |
| **PERSONALISATION** — what knowing the individual household buys beyond that | **£0.00** | CEILING |

Zero. Not small — exactly zero, in **every one of nine years**, against menus of 132 to 381 tariffs
the company actually charged. One tariff on each year's menu is cheapest for every household in the
book.

**The reason is structural and the artefact publishes it rather than asserting it.** The menu is a
two-part *linear* tariff — a standing charge and a unit rate — so a household's ranking of two
offers turns entirely on where its consumption sits against their crossover. On the efficient
frontier the standing charges differ by fractions of a penny a day while the unit rates differ by
tens of pounds a megawatt-hour, which puts every crossover far below the book:

| year | highest frontier crossover | smallest household | margin |
|---|---|---|---|
| 2018 | 2 kWh/yr | 1,401 kWh/yr | 700× |
| 2024 | 38 kWh/yr | 781 kWh/yr | 21× |
| 2016 | 508 kWh/yr | 1,765 kWh/yr | 3.5× |

**A CEILING at zero retires the candidate outright.** Per-household tariff selection, on the menu
this company offers, is worth nothing — and no inference, however good R1 becomes, can be worth
more than perfect knowledge of the answer. What would change it is a product whose cost depends on
**when** a household draws. That is R4's own subject, and this measurement says it is the *only*
part of R4's tariff channel worth building.

**The £211k level gain is not banked as a win.** It is the company's own revenue moved to the
household. Whether any of it is value *created* depends on a cost this instrument cannot see — it
reads prices, not costs. Under the mission's own test (create, then share), an unexamined level
gain is transfer, and the artefact says so on its face.

### Four of six channels are REFUSED, each naming its missing input

Measured, not asserted. `fabric_eligibility` in the run output says **4 of 152** supply points carry
"fabric parameters and local weather"; **137 lack a weather archive for their location**.

* **efficiency**, **heat pumps** — refused at that measured 4/152. The modules exist
  (`company/pricing/fabric_intervention.py`, `company/billing/efficiency_advice.py`); what is
  missing is the book underneath them. Heat pumps additionally want a per-property heating asset
  register the run output does not carry.
* **solar** — refused on two separate gaps: no irradiance series per location, and no roof area or
  orientation. Closing the weather archive alone would not close this one.
* **time shifting (£)** — refused: the price feed carries 2 days against a floor of 365. **The
  carbon side of this channel is NOT refused** — R3's instrument bounds it, because the intensity
  feed carries a whole-series per-year summary the price feed does not.
* **advice** — refused *structurally*, and it is the one refusal no data fixes. Advice is the
  delivery of the other five channels; a separate figure would double-count every pound already in
  them. What advice needs measured is the act-on rate, which is `C30_advice_reaches_a_household`'s
  subject and is a behaviour, not a bound.

**Three of the four are one weather archive away from being computable.** That is worth more than a
number would have been, and it connects directly to the staged finding that a rate-limited weather
pull wrote header-only CSVs over ten years of real archive and exited zero.

---

## R3 — a large ceiling and a response that cannot be told from nothing

| rung | | bound |
|---|---|---|
| `book_emissions` | 339.2 tCO2e | CEILING of all abatement (abatement cannot exceed emissions) |
| `perfect_timing` | **263.2 tCO2e** · £71,841 (£35,920–£107,761) | **CEILING** of the timing channel · **FLOOR** of total abatement |
| `lcl_responded` | 1.73 tCO2e · £471 | **NOT A BOUND** |
| `lcl_placebo_null` | response −3.45% of the peak window's rate, **p = 0.1150** | does **not** clear α = 0.05 |

The ceiling is large: 78% of the book's electricity emissions are in principle removable by *when*
alone, worth £71,841 at the government's own carbon value (DESNZ / Green Book, £273/tCO2e, 2025
vintage, ±50%). **It does not retire R3.**

The honest end is the rung beneath it. The only figure here anchored to households that actually
existed and actually moved is the Low Carbon London trial (UK Power Networks, 2013, in this repo's
own data lake): its treated arm shifted **3.45%** of the signalled window's consumption rate against
its control arm, and the signalled window carries **19.0%** of a weekday's load — so **0.66% of
total load** actually moved. Against the intensity spread that is **1.73 tCO2e over nine years,
£471, about £1 per household per year.**

**And it does not clear its own null.** Splitting the trial's 244-household *control* arm against
itself 2,000 times produces a difference-in-differences at least as large as the observed one 11.5%
of the time. At the trial's sample size, the measured response cannot be told from no response.

That is not filed as a floor. A **real** response fraction times an **unreal** placement bounds
nothing in either direction, and calling it a floor would license an "at least this much" claim that
no part of it supports.

### The third bound kind, and why forcing a binary would repeat EP13's own error

A49 asks each instrument to say whether it is a CEILING or a FLOOR — the conflation EP13's tenth
pass made and its eleventh corrected. `lcl_responded` is honestly neither, and the available wrong
move was to file it as one, which is that same conflation wearing the requirement's own clothes. So
`BOUND_KINDS` has three members, `r4_product_ceiling` imports the vocabulary rather than restating
it (so the two instruments cannot drift into meaning different things by one word), and
`test_every_rung_declares_a_legal_bound_kind` pins it.

`perfect_timing` carries **both** labels because it is both: a ceiling on the timing channel, and a
floor on total abatement, since efficiency, fuel switching and generation are not in it. A reader
who took it as a ceiling on total abatement would retire R3 on a number that bounds it from below.

---

## The null that had to be thrown away

The first draft graded `perfect_timing` against an intensity series shuffled within the day. **That
null is degenerate.** Placing load at the minimum is a *sort*, and a sort is invariant to
permutation, so the shuffled null returns the identical number — every run would have read "the
ceiling is exactly the noise floor", a fail-silent tautology of the class
`docs/design/CONTROLS_THAT_CANNOT_FAIL.md` catalogues. The null had to move to a rung where chance
can actually reach: the trial's own control arm.

## Reachability was proved before anything was believed

A £0.00 is the one answer an arithmetic bug produces for free, and every control on this instrument
would have stayed green against a `personalisation_gain_gbp` that had become `0.0`
unconditionally. So the reachability leg came first: a synthetic menu whose ranking genuinely flips
inside the book's consumption range must produce a *positive* personalisation and more than one
winning tariff. It does. Only then does the live zero mean anything.

**Poison round, from a 31-green baseline** — five mutations, each killing exactly its own control
and nothing else:

| mutation | result |
|---|---|
| `personalisation_gain_gbp` forced to `0.0` | 1 failed |
| `perfect_timing` head-room made a constant | 1 failed |
| `clears_alpha` forced `False` | 1 failed |
| gas admitted to the timing ceiling | 1 failed |
| the fabric refusal made a fixed string | 1 failed |

---

## What this changes

1. **R4's tariff-fit channel is retired as a per-customer programme** on the menu as it stands. The
   surviving R4 candidates are the ones whose cost depends on *when*, and the four refused channels
   whose ceilings are not yet computable.
2. **R3 is not retired.** Its ceiling is 263 tCO2e / £71,841 and positive; what is unproven is that
   any real programme reaches an appreciable share of it, and the one real trial in evidence cannot
   be told from zero at its own sample size.
3. **The weather archive is now load-bearing for three of R4's six channels**, measured at 4/152
   rather than argued.
4. **A49's own deliverable exists.** Both instruments are `tools/`-side diagnostics reached by no
   decision surface — `tests/company/test_carbon_not_a_target.py` derives its subject set from
   `company/ sim/ simulation/ saas/ background/`, and both files are outside all five by
   construction rather than by an allowlist entry.

**Next, and not done here:** A49's level move from 0. The instruments are the deliverable; the
promotion is a separate act through `tools/level_promotion_gate.py` and is left to the seat's next
orientation rather than self-recorded in the same pass that built the thing being graded.
