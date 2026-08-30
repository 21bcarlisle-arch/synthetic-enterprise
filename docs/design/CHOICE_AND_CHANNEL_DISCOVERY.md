# Choice and channel — what the world actually does today

**Date:** 2026-08-30. **Author:** the delivery seat. **Status:** DISCOVERY.
**Occasion:** `docs/staging/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md`, WORK item 2 —
*"what our world does today against that evidence, including what already exists unwired."*

Companion pieces: the knowledge is `site/data/knowledge_topics.json` →
`choice-and-channel` (WORK item 1); the roadmap is
`docs/design/CHOICE_AND_CHANNEL_ROADMAP.md` (WORK item 3).

Every claim below was checked by enumerating live-tree readers and discarding substring
matches. That discipline is not ceremony: five false findings were produced in one day on
2026-08-27 by not doing it, and one of this document's own findings (§3) is precisely a
substring that looks like a hit and is not.

---

## 0. The finding in one sentence

> **The world models winning a customer as a process — five stages, real dates, per-stage
> leakage and per-stage cost — and losing one as a single coin flip with no cause.**

`simulation/acquisition_funnel.py` walks `quote → application → credit_check → onboarding →
cooling_off`, each with its own conversion rate and its own calendar-day spacing.
`simulation/customer_events.py` decides a departure by multiplying five scalars into one
probability and rolling once against it. The asymmetry is not a matter of polish. It is why
the company can be right or wrong about whether it *wins* a household and can be neither
about why it *loses* one.

---

## 1. The departure decision, read off the code

`simulation/customer_events.py:~420–535`. The composition is multiplicative on the churn
probability, each stage scaling the survivor of the last:

| order | factor | module | shape |
|---|---|---|---|
| base | bill-shock base rate | `renewal_data["churn_probability"]` | scalar |
| 1 | price vs the market reference | `market_switching_propensity.churn_position_multiplier` | one curve, weighted by a per-household elasticity, scaled by that household's own annual bill in pounds |
| 2 | income stress | `switching_propensity.adjust_churn_probability` | bucket multiplier |
| 3 | tenure (renter/owner) | same call | category multiplier |
| 4 | satisfaction | `satisfaction_churn.adjust_churn_for_satisfaction` | one curve, everyone |
| 5 | retention offer | `retention_modifier` | applied last, after the pre-offer probability is captured |

Then: `retained = roll <= effective_p_retain`, a single uniform draw.

**The record it emits** (`customer_events.py:531–545`) carries `event_type`
(`"renewed"` | `"churned"`), `churn_probability`, `win_probability`,
`effective_retention_probability`, `realized_churn_probability`, `random_roll`,
`home_move_won`, `company_churn_estimate`, `churn_estimate_error_pct`,
`retention_offered`. **There is no cause field, and there is nowhere one could be
computed from.**

That second clause is the point, and it is stronger than "the field is missing". By the
time the die is cast the five causes have already been multiplied into one number. A
departure is not *unlabelled*; it is **uncaused by construction**. Adding a `reason` column
to this record could only ever hold a story invented after the roll.

Confirmed by enumeration: `grep -rn '"churned"'` over `simulation/`, `company/`, `saas/`
returns twelve live sites, all of which branch on the event type and none of which reads or
writes any reason. `reason` appears in these modules only inside English prose in comments.

### The one thing that IS a reason today, and its scope

`home_move_won` is a genuine second event with its own semantics and its own seed — but it
fires *after* a departure has already been decided, and it asks whether we win the mover's
new property. It is a consequence of a move, not a cause of a departure. The world has no
home-move-onto-deemed-contract arrival at all.

---

## 2. What exists on the acquisition side, and where it stops

`simulation/acquisition_funnel.py` is real and better than its counterpart:

- five named stages with published-ish conversion rates (`QUOTE_TO_APPLICATION`: resi 0.24,
  SME 0.28) and stated confidence (M/L on most rows);
- real calendar spacing per stage, with `COOLING_OFF_PERIOD_DAYS` hard-anchored to the
  Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013;
- an honest scope note: the entry point is a **quote-issued** event, mid-funnel, and
  awareness/consideration is explicitly out of scope and delegated to
  `saas.growth_mandate.should_attempt_acquisition()`.

**And it is channel-blind from end to end.** Every quote costs the same, arrives the same
way, and is introduced by nobody. There is no comparison site in the world, no affiliate, no
broker, no doorstep, no direct-brand route. The cost side has been repaired —
`saas/growth_mandate.COST_PER_ACQUISITION` (invented, £150/£400) was replaced on 2026-08-28
by the sourced model in `saas/opex_ledger.py` — but a **sourced cost with no channel
attached is still one number for a set of routes the published evidence says differ by an
order of magnitude and by kind** (a per-switch commission for PCW; a per-kWh trail for
broker; no published GB figure at all for direct brand).

So: the world has a quote and no channel on the acquisition side, and neither on the
departure side.

---

## 3. The substring that is not a hit — `channel_pref`

`simulation/population_draw.py:1212` draws `channel_pref` per household, with curriculum
marginals (55/30/15, cited to Ofcom/Ofgem), a coverage test
(`population_coverage.py:51`), a structural exclusion in `cohort_discovery.py:218`, a
curated symbol scan in `epistemic_verifier.py:122` and planted-leak mutation tests.

Two facts about it, and both matter:

1. **Its levels are `("digital", "phone", "assisted")`** (`tools/couple_cohort.py:98`). This
   is a **service contact** preference — how a household would rather talk to its supplier.
   It is not an acquisition or discovery channel. The repository therefore contains the word
   *channel*, carrying real machinery and a real citation, meaning a different thing from the
   brief's channel. **That is how this gap stayed invisible**: any search for "channel"
   returns a well-tested subsystem and stops.

2. **It reaches no live behaviour.** Outside the draw/coverage/wall apparatus, no live module
   reads it — and `WHAT_A_HOUSEHOLD_DECIDES_ON.md` already established that its declared
   discovery channel (*"discoverable via the contact channel actually used"*) does not exist
   either: `contact_propensity` keys on the engagement archetype, never on `channel_pref`.

Not re-litigated here, and not this document's finding. Recorded because the next reader
searching for "channel" will land on it, as I did.

---

## 4. Competition — half-built, on 2026-08-28, and price-only

`simulation/competitor_reference.py` landed two days ago and is a real repair. Before it,
`simulation/svt_rates.py` did double duty as both the ceiling the company priced against and
the reference the population churned against — one immovable calendar table on both sides,
which is why a profit maximiser correctly discovered that charging up to the cap was close to
free. Now:

    reference(t) = clamp( svt(t) + CHASE * min(0, company(t) - svt(t)), floor(t), svt(t) )

The rival matches a company that undercuts it, over quarters, never below its own costs, and
`CHASE = 0` reproduces the old world exactly — which is the killer mutation for its controls.

**What it is:** a single scalar reference *price* that responds to ours.
**What it is not:** a supplier. It has no identity, no product range, no offer, no book, no
cost structure of its own, and it cannot be seen. The world has one number where the brief
asks for a market. In particular there is no menu — nothing anywhere holds a set of rival
tariffs a household could be shown and choose between.

---

## 5. The quote a household is shown — does not exist

The brief's sharpest ask is *"model what the household is shown, not only what it would
pay."* The world does not do the first half at all.

`customer_events._price_differential_vs_market` computes a differential between this
customer's own offered rate and the reference, converts it into pounds at that household's
own billed consumption, and weights it by a per-household elasticity. Every part of that is
a **true** quantity. Nothing anywhere renders an **annualised figure at typical
consumption**, which is the only number a real household actually sees — on a comparison
site, and in the cap headline.

The published convention is exact and is in the commons already: Ofgem's typical domestic
consumer values are **2,700 kWh electricity and 11,500 kWh gas per year**, and the April
2025 cap headline of **£1,849** (direct debit, dual fuel) is that figure quoted at those
volumes. A household comparing a fixed offer against its own cap-headline is comparing a
real forward price against an implied forward price nobody is offering.

So the world today has households responding, correctly and invisibly, to a truth no real
household can observe. **This is a wall-shaped defect pointing the other way from the usual
one**: not the company knowing too much, but the *population* deciding on ground truth. It
has never been written down as such, because the epistemic wall is enforced on
`company/` and `saas/` and this is in `simulation/`.

---

## 6. The SVT product — the standing owed repair

Already determined, and re-measured this morning:
`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`.

The world settles **100%** of drawn domestic accounts as annual fixed-term contracts with a
locked rate and an active renewal decision at every boundary. Published domestic fixed share
across the run window is a minority in every single year — roughly 10% to 46%, centred near
one third. `build_renewal_schedule` can settle four types (`fixed`, `flex`, `deemed`,
`pass_through`) and **none of them is a standard variable tariff**; SVT exists in the world
only as a comparison benchmark and a published observable. `deemed` is out-of-contract spot
+ 20% — a gap *between* contracts, not a variable tariff.

The measured consequence, from the addendum: all 141 electricity legs the company found —
the 90 it won and the 51 it drew — render `tariff_type` present-and-`None`, and are refused
at `UPLIFTABLE_TARIFF_TYPES = {fixed, pass_through}`. The 15 founder legs omit the key, take
the `.get(..., "fixed")` default, and are admitted. **The gate is a property of the record
shape, so no book size opens it**: the first household the company ever won is not priced at
any book size, only at a world that gives it a product.

This is the single place where the missing mechanic is already costing a published result.

---

## 7. What this bounds

The thesis is that the company's advantage comes from **inference**. The quantity to infer
is why a household moved.

- The world has one reason, spread across five multipliers, and destroys the decomposition
  before it emits the event.
- Two thirds of a real domestic book has no renewal decision to be right about, and our
  world gives that two thirds a fixed contract instead.
- The company's forecast target (`realized_churn_probability`) is a scalar, so the best
  possible company model is a curve fit to a scalar. `WHAT_A_HOUSEHOLD_DECIDES_ON.md` §4
  reached the same ceiling from the response-function side; this is the same ceiling from
  the **event** side, and it is the tighter of the two, because a richer response function
  still emits one undifferentiated `churned`.

That is the bound, and it is structural rather than a matter of sample size. It is not
fixed by more seeds, a bigger book, or a better company model.

---

## 8. Nothing here is a defect report

Per the standing instruction on this class of work — *"where the SIM is simply too simple,
that's a discovery and a roadmap item, not a defect to fix in place"* — none of the above is
filed as a finding and nothing was fixed on sight. §5 is the one item I considered filing,
because a population deciding on ground truth is wall-shaped; it is carried into the roadmap
instead, on the grounds that the wall as written governs `company/` and `saas/` and this
would be an extension of it rather than a breach of it. That call is recorded so it can be
overturned rather than discovered.
