# THE MODEL ON A PAGE

**Status:** CANON (Tier-2). **Adopted:** 2026-07-23. **Mission superseded 2026-08-28** (§The mission).
**Provenance:** [DIRECTOR-RULING → canon] via advisor bridge —
`docs/staging/DIRECTOR_CANON_MODEL_ON_A_PAGE_2026-07-23.md` (staged commit be3da591a).
The director asked for the whole design on one page, split into exactly two timeframes: what
the machine runs on NOW (core), and what it EVOLVES INTO (later).
**2026-08-28, director direct, verbatim and binding:** the mission sentence below replaces the former
"one-sentence company" here AND the fidelity line in `CLAUDE.md`. It is a change of PURPOSE, not a
correction of fact — unlike C1/C2/C3 (2026-08-28), which corrected claims this page made about the
code. Nothing in the spine, the wall, the timeframes or the reading rule is withdrawn by it; what
changes is what all of that is FOR.

**Reading rule (director's, binding):** anything in **Timeframe 1** claimed as working must carry
its proof (level, test, or gap named). Anything in **Timeframe 2** stated as present tense anywhere
on the site is a **claim-status defect**. Where this page and any FRAME doc disagree, surface the
disagreement as a finding (see §Open findings).

---

## The mission

> **We are creating enterprise value by automating ways to find individual customers we can create
> value for, and sharing in that value — by saving them money, time and carbon, through personalised
> modelling, tariffs and advice.**

*Director, 2026-08-28, verbatim. Supersedes "cutting carbon through personalisation, measured in £ per
tonne of CO₂e saved" here and "Goal: detailed enough to say 'that is how a real UK energy supplier
works'" in `CLAUDE.md`.*

**Carbon is not demoted — it is one of three.** The old sentence made carbon the mission and £/tCO₂e
the score. The new one makes carbon one of three currencies the household is saved in, and makes the
*method of finding and serving that household* the thing being built. Every carbon commitment on this
page (`E5`, the SAVED/SPENT/NET ledger, the £/tCO₂e front-page target) survives intact and keeps its
level; what it loses is the claim to be the whole purpose.

### What follows from it, that no document said before

**1. Every decision has two sides, and transfer is not creation.** Value is created and *then* shared,
so a decision is scored on the household as well as on us. **Charging someone the cap transfers value
rather than creating any** — which is exactly why the profit maximiser kept finding it
(`docs/staging/WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED_2026-08-25.md`).
That finding read the cap as a defect in the churn model's ceiling. Under this mission it is better
read as a **defect in the objective**: the maximiser was optimising a one-sided score correctly, and no
ceiling repair fixes a score with a side missing. The two readings are compatible and both fixes are
real; the ordering changes, because a two-sided score makes cap-pricing unattractive *on the merits*
rather than merely unreachable.

**2. There are three currencies — money, time and carbon — and only money has been optimised.**

| | household side (value CREATED) | our side (value SHARED) |
|---|---|---|
| **money** | **instrumented 2026-08-28** — `company/analytics/household_value_share.py` computes what a household kept against the published SVT at its own metered volumes, per customer-year; read by the price ladder, carried per ARM by the value-cycle A/B, and **published beside the company's own net margin on `/capabilities/` since 2026-08-28** — the first surface on which a reader meets both sides of one decision; read by no decision surface (`A47` at L2) | **EARN** — instrumented; the only leg of the *scored* objective |
| **time** | **does not exist** | **does not exist** |
| **carbon** | **ABATE** — designed, not instrumented (`E5`) | £/tCO₂e — designed, downstream of the cell to its left |

*The money row moved on the day the mission landed and the distinction it forced is the useful part:
what is instrumented is the household's **SHARE**, not the value **CREATED**. Creation is a comparison
of costs — a supplier whose cost stack equals the incumbent's and prices below it has transferred
margin, not made any — and the counterfactual supplier's cost is not observable to us. So the split of
a surplus is measured and the surplus's size is not (`A48`). Nothing optimises the household figure:
half of a two-sided objective is not the objective until the director decides it is, which is R13, and
`tests/company/test_household_share_is_not_yet_a_target.py` holds that and names its own release.*

*Time, observed-with-evidence 2026-08-28:* no time-, hours-, effort- or hassle-as-value symbol exists
anywhere in `company/`, `simulation/`, `saas/` or `tools/`, and no design document names time as a
currency. This is not "thinly built" — it is **absent**, and it is the only cell in the table that is.

**3. The enterprise value is the automated method, not the book** — the book is the evidence the
method works. *Observed, and it bites immediately:* `saas/enterprise_value.py`, the only module in the
repo carrying the mission's own noun, defines it as *"the portfolio-wide sum of the resulting
per-account CLVs … the total discounted future net margin of the customer book."* That is precisely
the definition this mission supersedes. Filed as
`docs/staging/WORKER_FINDING_THE_ONLY_MODULE_NAMED_ENTERPRISE_VALUE_MEASURES_THE_BOOK_2026-08-28.md`.

### Fidelity keeps its place, and gains its reason

The old sentence made faithfulness the goal. It is now the **precondition**: a world that cannot press
back cannot tell value CREATED from value TRANSFERRED, because in a market that never responds,
extracting and earning look identical on every instrument we have. That is the director's C2
correction (no competitor module) reaching the same conclusion from the other side, and it is why
`docs/design/THE_WORLD_MUST_PRESS_SEQUENCE.md` outranks new capability. Unchanged and still binding:
the two-way wall, the Point-in-Time Blindfold, and the test on every line — **could a real UK energy
supplier know this?**

### The three channels, and which of them reaches a household

Personalised **modelling**, **tariffs** and **advice** are how the mission says value gets to a
customer. Status as at 2026-08-28, observed-with-evidence — **noted, not being fixed here**, on the
director's instruction:

- **Tariffs — LIVE, and the only channel that reaches a household.** The renewal pricing engine sets a
  unit rate, the rate reaches the customer's churn decision (`simulation/customer_events.py`), and the
  household's outcome changes. This is the whole of the company's current contact with the value it
  claims to create.
- **Personalised modelling — EXISTS, but pointed at us.** The discovery loop clusters the book and
  `company/analytics/customer_value_view.py` builds a per-account view — explicitly *"the supplier's
  OPINION about value and retention"*, feeding cost-to-serve, churn risk and CLV. It is modelling **of**
  customers for our decisions, not modelling **for** a customer producing a household outcome. Nothing
  it computes is ever offered to the household it is about.
- **Advice — MODULES ON DISK, NO RECIPIENT.** `company/pricing/switching_recommendation.py` renders
  inside `company/portal/app.py`, and `company/crm/decarb_recommender.py` exists and is discovery-wired.
  But **nothing in `simulation/` consumes a recommendation** and no simulated customer visits the
  portal, so no advice has ever reached a household or changed one's behaviour. The channel is built
  everywhere except at the point where it would matter.

Two of the three channels therefore cannot yet create the value the mission is about, which bounds
every household-side measurement before it is taken.

## The spine (true in both timeframes)

**THE WORLD (SIM truth, behind the wall):** Real weather → real half-hourly wholesale prices and
demand (2016–2025, 168k settlement periods, the actual record including the 2021–22 crisis). A drawn
population of synthetic households — different mix every run — each with drawn hidden traits and a
metered life. *Traits express through ONE channel and two carry none — corrected 2026-08-28 (C1):*
`price_sensitivity` reaches the world through the churn decision (landed 2026-08-27) and carries a
published between-group spread of only **1.26×**, which this seat has measured as structurally
unlearnable on the current book; `green_stance` and `channel_pref` are drawn, coverage-tested and read
by no response function at all. The world therefore still **records** more heterogeneity than it
**expresses**.

**THE WALL (two-way — F-MOAP-2, 2026-07-23):** Ground truth never crosses; everything else is an
interface flow in one of two directions. *Inbound* (what the company sees): market feeds and forward
curves, *published forecasts with realistic error*, meter reads (imperfect), payments, complaints,
replies, and **settlement — arriving late** (a first-class inbound gate: the truth about a period lands
months behind it). *Outbound* (what the company sends): **bills, offers, messages**. A bill is
**outbound**, never an observable — the inbound observable is the *payment or complaint that answers a
bill*, not the bill itself. Forecast error is the wall on the future; discovery-through-behaviour is the
wall on the customer.

**THE COMPANY:** Acquires customers → forecasts its book's shaped demand → prices tariffs from the
cost stack → hedges forward to delivery → bills on three clocks (billed/settled/banked) → collects →
serves and converses → settles months later and learns from the true-up. It can be wrong, and it must **not be
guaranteed to live** — *corrected 2026-08-28 (C3, director): the company does not have to die; survival
has to be genuinely at risk on a path the world can actually produce.* Three mechanisms carry that risk
in reality and **none of them presses yet**: **hedging** (collateral is a cost line sized once at term
start and fixed for the term — never a CALL), **competition** (blocked entirely by C2), and **debt**
(arrears do not yet arrive coupled to wholesale peaks). All three are cash-and-timing problems, not
profit problems, and there is no mechanism converting a bad quarter into a liquidity constraint — which
is why EARN has been the only leg the world can press on. Atoms `B6_collateral_cash_death_loop`,
`B7_customer_state_layer_moves_and_shocks`, `SPINE_1_scenario_world_state`.

**THE SCORE:** Survive (hard constraint, judged worst-case). Earn (EV, probability-weighted). Abate
(tCO₂e per customer from grid-intensity × half-hourly use, priced in £/tonne). *Corrected 2026-08-28
by the mission above: all three legs are scored on the COMPANY. Survive and Earn are ours by
construction, and Abate — though it counts a household's tonnes — is instrumented as our £/tCO₂e and
is not yet instrumented at all. **The score has no household-side term in any currency**, which is the
structural reason a maximiser can win it by transferring value rather than creating any. Making it
two-sided is a mission-level change to the objective, not a tuning of it; the six cells and what fills
them are in §The mission.*

---

## TIMEFRAME 1 — CORE (running or landing now)

**World:** the real 9-year record as ground truth · weather→price coupling proven
(Beast-from-the-East regime) · single imbalance price · settlement lag real (world at 2025-12, books
at 2025-06).
**Population:** curriculum-drawn cohorts (coverage knee ~12 cells, protected tails: fuel-poor
off-gas, prepay, vulnerable) · engagement mix 0.45/0.35/0.20 (ratified) · tenure×adoption gating live
· assets (EV/HP/PV) on anchored S-curves.
**Company organs:** acquisition & churn (market-coupled swell proven; moneyness trigger absent —
known; **the market DEFENDS but does not yet CONTEST — corrected 2026-08-28 (C2), and corrected again
the same day by `tools/canon_drift_check.py`, which caught this page still carrying the morning's
verdict hours after the code had moved**: reading the real switching record is genuine coupling to
history, and there is now **a rival that moves: `simulation/competitor_reference.py`** — it matches a
company that undercuts it, over quarters, on a lag the company does not control, and never below its
own cost stack, so a price advantage now DECAYS instead of persisting (measured: −10.0% position at
CHASE=0, −5.0% one quarter later at CHASE=0.5). What has NOT changed: market position is a run-level
constant where no offered rate is to hand, and the company still cannot price above the cap at all
(`renewal_desk._apply_competitive_ceiling` clamps it), so **over-pricing still carries no competitive
consequence** — the maximiser's discovery that charging the cap is close to free is the discovery that
the cap is a hard ceiling with nothing above it. Nobody yet targets the company's book. **Consequence,
stated where the capability is:** every measurement of the company's pricing decisions taken BEFORE
2026-08-28 was taken against an opponent that could not move, so "beats the flat baseline" compares two
internal policies, not two suppliers, and stays that way until it is re-measured against the defending
rival. Atoms `B10_competitor_switching_response` (defence leg landed), the contested ceiling
next.) · naive forward belief (120-day trailing) it must outgrow · UK-compliant billing, three clocks
· collections · Tier-1 bill-accuracy compliance · conversations v1 (the F1 triad: company writes,
customers respond, harness scores the gap).

**THE PER-CUSTOMER PRICING ARM REACHES 2.07% OF THE RENEWALS THE WORLD OFFERS — measured
2026-08-28, and it bounds every A/B figure this project publishes.** Of 1,209 renewals: 398 are
acquisition terms with no prior term to price against, 357 are **gas** (the arm is
electricity-only), 429 carry no product label the arm prices, and **25 are priced**. Two of those
three exclusions are deliberate scope; the third is a gap in the drawn book. The consequence worth
carrying: the world's own switching response is calibrated **dual-fuel**
(`MARKET_SAVINGS_BY_YEAR`), so **the arm is narrower than the world it is scored against** —
an electricity-only policy judged by a dual-fuel switching curve. Finding:
`WORKER_FINDING_THE_ARM_IS_NARROWER_THAN_THE_WORLD_IT_IS_SCORED_AGAINST_2026-08-28`.
**Discovery loop:** company clusters its book from observables only, scored on worst-cell
belief-vs-truth; first refuted assumption already recoupled (renters/heat-pumps).
**Carbon:** designed ledger (SAVED/SPENT/NET), honestly *not yet instrumented* — the site says so
plainly.
**Method:** the harness itself — gates, R1–R17, twin approvals, daily self-note — the third product.

## TIMEFRAME 2 — EVOLUTION (registered, sequenced, not yet true)

**World deepens:** scenario spine live (NESO-central / crisis-replay / glut, tail-heavy sampled,
true-probability tagged) · gas storage stock-and-flow that can *produce* a 2022 inversion · forecast
layer at multiple horizons with error shrinking to delivery · warming trend without thinned extremes ·
spike-tail fixed (the declared 10× gap) · renewables/battery/interconnector penetration as scenario
fundamentals.
**Market deepens:** the traded product ladder (seasons/quarters/months/DA) with moving
contango/backwardation · shaped annual cost as the benchmark · cover-fan vs policy ladder · trading
value-add ledger net of day-one friction · cap observation-window mechanics · **competitors**, so
pricing meets opposition.
**Company deepens:** collateral→cash death loop (2021-22 replay must show death-by-collateral with
P&L surviving) · retail gas actively hedged into the existing plumbing · cost-to-serve & opex ·
VAT/CCL tax cycle · cannot-pay/will-not-pay collections physics.
**Customers deepen:** the state layer (moves = credit exit + two deemed entries, births/deaths/divorce,
income shocks) · continuous engagement replacing the three bins · price-sensitivity and attitudes
*discovered* through conversations and offers, never tagged · misclassification-cost physics ·
holdout-measured uplift so "this segment justifies its treatment" is proven, not asserted.
**Carbon becomes the headline:** E5 instrumented — NESO intensity × every half-hourly read →
per-customer trajectories → **£/tCO₂e on the front page**.
**Endgame:** whole company lives rerun across scenario worlds to death or endpoint — the evolutionary
tournament where EV is fitness and mortality is selection.

---

## Open findings (director-authored reading rule: surface disagreements)

**F-MOAP-1 — "seed /simplified" conflicts with the SITE_V5 five-surface IA (director call).**
The adoption instruction has two sub-items: (a) adopt this to canon [DONE, this file]; (b) "treat it
as the seed for the /simplified lay page — same content, plainer words." Sub-item (b) is **blocked on
a director IA decision**, not on build capacity:

- The SITE_V5 structure ruling (`docs/design/SITE_V5_STRUCTURE_CONFIRMATION.md` §row 4, director-ratified
  the same day, 2026-07-23) **folded `site/simplified/` into Proof** and surface_4_proof landed live
  with `/simplified → /proof` 301'd (its door killed as part of the cut-to-five-surfaces IA).
- This canon file asks for a plain-language **lay page** seeded from the model-on-a-page. That is a
  *different artefact* from the simplifications *register* that was folded into Proof — but it would
  need a home in (or a reopening of a door within) an IA the director just deliberately narrowed to
  five surfaces.

Choosing the host — resurrect `/simplified` as a lay page, host the lay explainer inside an existing
surface (Front door / Proof), or defer — is a **category-6 IA / values call reserved to the director**
(the same authority that set the five-surface IA). The agent does not unilaterally reopen a door the
director just closed, nor silently drop his seed instruction. **Escalated via NTFY; default if no
reply: host the plain-language model-on-a-page as a fold inside the Front-door surface (the closest
match to "the pitch in plainer words") when surface_1 next iterates, NOT as a resurrected `/simplified`
door.** Tracked as the open sub-item on the parked staging file.
