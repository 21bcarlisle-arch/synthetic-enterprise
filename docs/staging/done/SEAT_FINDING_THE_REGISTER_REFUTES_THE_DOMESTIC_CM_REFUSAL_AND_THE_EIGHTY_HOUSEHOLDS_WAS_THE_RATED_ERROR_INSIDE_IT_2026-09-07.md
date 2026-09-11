**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a51-derating-callers-and-the-dsr-cmu-shape

# The register refutes the domestic CM refusal, and the "~80 households" was the rated-capacity error living inside it

**Written:** 2026-09-07, delivery seat, claim `a51-derating-callers-and-the-dsr-cmu-shape`.
Pre-registration: `SEAT_PREREGISTRATION_WHAT_A_REAL_DSR_CMU_IS_MADE_OF_AND_WHAT_WOULD_REFUTE_THE_DOMESTIC_REFUSAL_2026-09-07.md`, written before either CSV was opened.

---

## The headline

The drawn item asked whether two modules should now apply a de-rating factor, and asked for the
CMU/Component lists to "put evidence under the domestic refusal". The de-rating answer is **no, in
both, for two different reasons** — recorded below so the question is not re-opened by inspection.

The evidence half did not put evidence under the refusal. **It knocked half of it out.**

`DOMESTIC_PARTICIPATION_REFUSAL` rested on two grounds: a household cannot reach the Capacity
Market except through an aggregator, and nobody publishes what an aggregator pays a member. The
publisher's own Capacity Market Register carries **awarded DSR CMUs whose operators describe them
as "domestic demand turn down" and "aggregated components less than 30KW"**, from **delivery year
2023** — inside the run window. By DY2025 there are 43 such awarded CMU-years, **633.5 MW of
de-rated capacity**, **713,838 components**, under **eight named GB operators** including Octopus
Energy and Ohme. The first ground is refuted. The refusal now stands on the second alone, and says
so.

## The uncomfortable part

**The refusal contained the exact error the whole de-rating pass exists to end.**

"~80 households per minimum CMU" is 1,000 kW ÷ 12.4 kW, where 12.4 kW is a whole flexible house's
**rated** asset power. The register publishes what a domestic component actually contributes to an
awarded CMU: a capacity-weighted **1.1655 kW**, i.e. **~858 households**. The published figure was
**10.7× low**, because it divided by rated capacity where the publisher gives contracted capacity.

That is the rated-vs-delivered error — the one `derating_factor()` was fetched to end, the one the
I&C leg was corrected for in the previous commit — sitting inside the sentence that names it, in
the module written to be the single honest home for it. It was not found by looking for it. It was
found because the register was asked a question the arithmetic could not be asked.

Independently corroborated: NESO's DFS record says 91% of domestic delivery is below 1 kW. A
different publisher, a different service, the same order of magnitude.

## Prediction scorecard, kept beside the answers

| # | Pre-registered | Outcome |
|---|---|---|
| 1 | Median DSR CMU ≤ 5 components; p90 < 50 | **Correct** — median 1, p90 20 |
| 2 | Median component ≥ 200 kW; < 1% below 15.4 kW | **REFUTED** — 98.6% of run-window DSR *components* sit in CMUs averaging ≤ 15.4 kW |
| 3 | Zero DSR CMUs majority-domestic | **REFUTED** — 57 of 1,448 run-window awarded CMU-years (3.9%) |
| 4 | Median DSR CMU 2–10 MW de-rated | **Correct** — 6.95 MW |
| 5 | Smallest awarded DSR CMU at/just above 1 MW | **Correct, exactly** — 1.0000 MW; the threshold binds |

The two I got wrong are the two that mattered, and I got them wrong in the same direction and for
the same reason: I reasoned about the median CMU when the question was about components. **The
distribution is bimodal and the median is useless.** 3.9% of DSR CMUs hold 98.6% of DSR components.
A statistic over "the average DSR CMU" answers a question about industrial sites; one over "the
average DSR component" answers a question about households; and they disagree by four orders of
magnitude. This is the "say what it is before you measure it" rule, arriving in a distribution
rather than in a definition.

**Prediction 6, on the regulatory module, was half refuted** — see below.

## The de-rating verdicts, and why each is "no"

| Module | Verdict | Reason |
|---|---|---|
| `company/market/flexibility_potential.py` | **No factor, ever** | A factor is a multiplier below 1. Applying one to a *refusal* makes a number that does not exist smaller, and a number that does not exist has no size. What is missing is a published pass-through, and no factor supplies one. |
| `company/market/capacity_market.py` | **No factor here — it would double-count** | `CMUnit.derated_capacity_kw` says its input is *already* de-rated. A factor inside `annual_revenue_gbp` applies the de-rating twice. The live hazard is the opposite one, and it now has a door. |
| `company/regulatory/capacity_market.py` | **No factor — and the one it carries was never a de-rating factor** | The supplier's CM charge is levied on *demand*. Demand is not de-rated; de-rating applies to capacity providers. See below. |

The second verdict came with work rather than a comment. Nothing stopped a caller passing a
**rated** figure into a field whose name says de-rated — silent, plausible, and the founding defect
of this whole family arriving through an argument list instead of a constant.
`derated_kw_from_rated()` is now the sanctioned door: it resolves its factor through the same
`auction_actually_held()` as the price, so DY 2022/23's substituted T-3 cannot be paired with the
suspended T-4's factor.

**Half the door's value is what it refuses.** Three of the six `CMUnitType` members do not
determine a de-rating class at all: Storage is published split by duration (0.5h–12h, factors
differing by more than 3×), so `BATTERY` and `PUMP_STORAGE` name no class; interconnectors are
published per named link (0.06 to 0.69), so `INTERCONNECTOR` names none either. Those raise with
the reason. An inline caller in a hurry would have picked a plausible neighbour.

**The publisher renamed its own classes mid-record**, which a single class-name-per-type map would
have swallowed silently: OCGT is `OCGT and Reciprocating Engines` in the 2016 Transitional auction
and again in the T-4 for DY 2019/20, and `Open Cycle Gas Turbine (OCGT)` everywhere else. A single
string returns `None` for DY 2019/20 and a caller reads "no factor established" for a year the
register fully covers. Aliases are tried in order; the control asserts **both** legs.

## What is next — a defect this pass found and did not fix

`company/regulatory/capacity_market.py` is a **fourth home for the CM clearing price** and carries
`_DERATING_FACTOR = 0.92 # Assumed average de-rated supply margin %` — an invented constant doing
a job no de-rating factor does. Printed at a real input (5 TWh) against the sourced Ofgem Annex 9
series already in this repo (`docs/market_research/capacity_market_levy_2016_2024.md`, wired into
`simulation/policy_costs.py`):

| DY | this module £/MWh | Annex 9 £/MWh | ratio |
|---|---|---|---|
| 2016 | 4.25 | 0.50 | **8.51×** |
| 2020 | 1.22 | 5.86 | **0.21×** |
| 2021 | 0.15 | 4.67 | **0.03×** |
| 2022 | 14.18 | 3.37 | **4.21×** |
| 2024 | 12.29 | 7.27 | 1.69× |

**My pre-registered prediction was ">2× and the direction is over". Half right and the wrong half
matters:** it is over from 2022 and *under* by up to 33× before it, so the module does not track
the published series in level *or* in sign of error. I predicted a biased estimator and found one
that is not an estimator of that quantity at all.

Removing the invented 0.92 makes 2024 read **13.36** rather than 12.29 — i.e. **the fudge was
pulling an overstated figure slightly toward plausibility**, which is the most expensive thing an
invented constant can do, because it makes the route look roughly calibrated.

Two of its controls are the shapes this project has a rule about: `test_derating_factor_reduces_
obligation` is pinned to today's `0.92`, and `test_cm_obligation_unknown_year_uses_2025_rate`
asserts the **fail-open default as the contract**. The same shape the previous commit found in the
NX suite.

There is also a category conflation underneath it: `delivery_status`, `shortfall_kw` and
`penalty_gbp` model a **capacity provider's** delivery obligation, which a supplier does not hold.
A supplier's CM obligation is a payment.

**Not fixed here, deliberately.** Fixing it properly means founding the supplier levy on the
regulation commons so both lanes read one publication — the `ro_commons` shape — and that is a
piece of work, not a line. It has **no production caller** (only its own tests), so nothing
published today is wrong because of it. Handed off.

## A control that failed for the right reason, twice

`test_the_refusal_names_its_reason_and_the_reason_carries_the_threshold` asserted
`"1,000 kW minimum CMU" in reason`. It went **red** when the refusal was rewritten to carry the
register's evidence — that is, when the claim got *narrower and better sourced*. A control keyed to
today's word order goes red when the code becomes more honest and green when the claim rots.

The identical pinned assertion existed in **two files** and both fired. Both are now keyed to the
property (`f"{MINIMUM_CMU_CAPACITY_KW:,.0f} kW" in reason`). The test's own docstring reads "a
refusal that says why is how the refusal itself gets found to be wrong" — and it was, by that test,
about the sentence that test was guarding.

## Evidence

**Poison round before any mutation claim** — "survived" means two opposite things. Baseline 77
green; 8 mutations, **8 killed** (no de-rating in the door 2; alias list collapsed 1; T-3
substitution ignored 2; revenue double-counting the factor 4; battery silently classed 2; domestic
leg wired back up 3; observed scale reset to rated 2; refusal reverted to ~80 2); restored 77 green.

**The first run of that harness reported 8 of 8 SURVIVED** — because I passed `-q` twice, pytest
suppressed the summary line, and the regex found no failure count. The baseline printed `.....`
where 77 dots belonged and I read past it. A mutation harness that cannot parse its own output
reports a perfect survival rate, which looks exactly like a suite full of controls that cannot
fail. The harness now asserts a summary was parsed at all.

102 green across the three market suites plus the NX I&C suite.

**Fetch note, filed in the artefact:** these NESO URLs **302 to Cloudflare R2 and `curl` does not
follow a redirect without `-L`**. Without it you get an 8-line HTML redirect page written over your
CSV **and an exit code of zero**. The first attempt did exactly that — `wc -l` read 11 where 51,509
were expected. Same family as the rate-limited weather pull that wrote header-only CSVs and exited
zero; a transport that fails into a valid-looking file is the failure mode worth checking for by
size, never by status.

## What a component is not

The register publishes a capacity and a count, not an occupancy. Two of the eight operators (Ohme,
Pod Point) are EV-charger businesses whose "component" is plausibly a charger rather than a
dwelling. Every figure here is *components in CMUs that describe themselves as domestic*, which is
the closest the publisher gets and is not the same claim. **Nothing here establishes pass-through**,
and the register never could — which is exactly why the refusal survives on that ground.
