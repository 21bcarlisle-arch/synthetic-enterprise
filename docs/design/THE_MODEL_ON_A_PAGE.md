# THE MODEL ON A PAGE

**Status:** CANON (Tier-2). **Adopted:** 2026-07-23.
**Provenance:** [DIRECTOR-RULING → canon] via advisor bridge —
`docs/staging/DIRECTOR_CANON_MODEL_ON_A_PAGE_2026-07-23.md` (staged commit be3da591a).
The director asked for the whole design on one page, split into exactly two timeframes: what
the machine runs on NOW (core), and what it EVOLVES INTO (later).

**Reading rule (director's, binding):** anything in **Timeframe 1** claimed as working must carry
its proof (level, test, or gap named). Anything in **Timeframe 2** stated as present tense anywhere
on the site is a **claim-status defect**. Where this page and any FRAME doc disagree, surface the
disagreement as a finding (see §Open findings).

---

## The one-sentence company
**Poesys is an autonomous UK energy supplier being run inside a faithful simulation of the real
market, whose mission is cutting carbon through personalisation — measured in £ per tonne of CO₂e
saved — and whose test on every line is: could a real supplier know this?**

## The spine (true in both timeframes)

**THE WORLD (SIM truth, behind the wall):** Real weather → real half-hourly wholesale prices and
demand (2016–2025, 168k settlement periods, the actual record including the 2021–22 crisis). A drawn
population of synthetic households — different mix every run — each with coupled hidden traits and a
metered life.

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
serves and converses → settles months later and learns from the true-up. It can be wrong, and it can
die.

**THE SCORE:** Survive (hard constraint, judged worst-case). Earn (EV, probability-weighted). Abate
(tCO₂e per customer from grid-intensity × half-hourly use, priced in £/tonne).

---

## TIMEFRAME 1 — CORE (running or landing now)

**World:** the real 9-year record as ground truth · weather→price coupling proven
(Beast-from-the-East regime) · single imbalance price · settlement lag real (world at 2025-12, books
at 2025-06).
**Population:** curriculum-drawn cohorts (coverage knee ~12 cells, protected tails: fuel-poor
off-gas, prepay, vulnerable) · engagement mix 0.45/0.35/0.20 (ratified) · tenure×adoption gating live
· assets (EV/HP/PV) on anchored S-curves.
**Company organs:** acquisition & churn (market-coupled swell proven; moneyness trigger absent —
known) · naive forward belief (120-day trailing) it must outgrow · UK-compliant billing, three clocks
· collections · Tier-1 bill-accuracy compliance · conversations v1 (the F1 triad: company writes,
customers respond, harness scores the gap).
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
