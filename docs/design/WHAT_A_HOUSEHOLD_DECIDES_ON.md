# What a household decides on — the world's decision richness, and the roadmap to widen it

**Date:** 2026-08-27. **Author:** the delivery seat. **Status:** DISCOVERY + sequenced roadmap.
**Occasion:** director, 2026-08-27 — *"Your oracle ceiling of 0.81 is the ceiling of a world where
churn is driven by bill shocks... In a world with one decision axis the company can't show inference
advantage, because there's only one thing to infer. The world's richness sets the maximum skill the
company can ever demonstrate. So the SIM leads and the company catches up."*

This is not a defect report. Where the world is thin, that is a **roadmap item**, per the same
instruction: *"Where the SIM is simply too simple, that's a discovery and a roadmap item, not a
defect to fix in place."*

---

## 0. The correction to the premise, which makes the point sharper rather than weaker

The premise was *one decision axis*. That is not what the world has. **Six inputs reach the churn
decision today**, and they are individually well-anchored — one of them to an Ofgem stock series.

The real constraint is structural, and it is worse than a missing axis:

> **Every axis in the world is a UNIVERSAL RESPONSE FUNCTION. The per-household weights that would
> make households differ in KIND are drawn, seeded, coverage-tested and wall-guarded — and consumed
> by nothing.**

Two households in identical circumstances behave identically, because the price curve, the
satisfaction curve and the stress multiplier are the same functions for everybody. Adding a seventh
axis of the same shape would not change that. **There is no household TYPE to infer**, and inference
advantage means knowing something about *this* household that its observables do not already say.

That is the true ceiling on demonstrable skill, and it is a different repair from "add more axes".

---

## 1. What a household actually decides on

Anchored to the GB retail literature (Ofgem RMI, DESNZ/BEIS typologies, Nesta clusters) and to what
a supplier can actually observe:

1. **Price level** — the bill, and the shock when it moves.
2. **Price relative to alternatives** — what the switching sites show against what they pay.
3. **Engagement** — whether they look at all. A large minority never do.
4. **Service quality** — billing accuracy, call handling, complaint resolution.
5. **Product fit** — fixed vs variable, TOU/EV/smart, prepayment, payment method.
6. **Carbon / green** — and, for a real minority, willingness to pay MORE for it.
7. **Reputation and trust** — slow-moving, book-wide, mostly earned through failure.
8. **Friction and life events** — moving home, financial distress, bereavement.

And decisively: **households weight these differently, and trade them off against each other.**
Someone will pay £30/yr to never call the contact centre; someone else will switch for £5.

## 2. What the world models today — audited, with evidence

### LIVE — reaches the churn decision

| # | Axis | Where | Shape |
|---|---|---|---|
| 1 | Bill shock | `renewal_data["churn_probability"]` | base rate |
| 2 | Price vs market SVT | `market_switching_propensity.churn_position_multiplier` | **one curve, everyone** |
| 3 | Income stress | `switching_propensity.stress_switching_multiplier` | bucket multiplier |
| 4 | Tenure (renter/owner) | `switching_propensity.tenure_switching_multiplier` | category multiplier |
| 5 | Satisfaction | `satisfaction_churn.adjust_churn_for_satisfaction` | **one curve, everyone** |
| 6 | **Engagement** | `household_segments` → `run_phase2b.py:1402-1410` | **per-household latent type**, Ofgem RMI Oct-2025 shares (45/35/20), gates `passive_churn_cap` |

Composition is **multiplicative** (`customer_events.py:219-242`): each multiplier scales the
survivor of the last.

### DRAWN PER HOUSEHOLD, CONSUMED BY NOTHING

`population_draw.py:1071` draws three latent attitude axes per household —
**`price_sensitivity`**, **`green_stance`**, **`channel_pref`** — with curriculum marginals,
coverage tests (`population_coverage.py:51`), a structural exclusion in
`cohort_discovery.py:218`, a curated symbol scan in `epistemic_verifier.py:122`, and planted-leak
mutation tests (`test_control_mutation.py:473`).

Outside that draw/coverage/wall machinery, **no live module reads any of them.**

> The wall is guarding an empty room. A substantial enforcement apparatus protects the company from
> learning three facts that change nothing. (`tou_price_sensitivity` in `company/crm/` and
> `sim/weather_price_sensitivity.py` are unrelated — substring matches, not uses.)

### The curriculum declares two discovery channels that do not exist
*(added after the initial filing, on reading the marginals themselves)*

`docs/design/segmentation_curriculum_v1.json` does not merely draw these axes — it makes a sourced,
written claim about how each becomes knowable:

| Axis | `hidden_truth_only` | The curriculum's stated discovery channel | Exists? |
|---|---|---|---|
| `price_sensitivity` (30/45/25, Ofgem engagement work) | **false** | *"discoverable via rate-change churn response (get_churn_estimate)"* | **NO** — absent from every churn-response module |
| `channel_pref` (55/30/15, Ofcom/Ofgem) | **false** | *"discoverable via the contact channel actually used"* | **NO** — `contact_propensity` keys on the engagement archetype, never on `channel_pref` |
| `green_stance` (30/45/25, DESNZ tracker) | **true** | none, by design | consistent ✓ |

`green_stance` is honest: it declares itself hidden with no observable, and that is exactly what it
is. The other two are the problem. Each is marked **discoverable**, names its channel, and cites a
real source — and the channel is not implemented, so the axis is undiscoverable *in principle*, not
merely undiscovered.

**This converts S1 from a fidelity improvement into a contract repair.** The coupled-triad gap for
these axes cannot be measured today, while the curriculum states it can. A company that tried to
learn price sensitivity from churn response would be right to try and would fail forever, and the
failure would read as a weak company model.

The contrast that proves the distinction is drawn deliberately elsewhere: `contact_propensity.py:69`
says of its own engagement multipliers, *"The engagement multipliers ARE new physics and do move
simulated outcomes."* That module knew to say which of its inputs move outcomes. The attitude axes
never got that sentence — or that wiring.

### NOT MODELLED AT ALL
Product fit as a *choice*; reputation/brand; green willingness-to-**pay** (and no green product to
buy); **and any trade-off between axes** — the multiplicative stack means no household can rank
service above price.

## 3. Two things already decided, which the roadmap must not re-litigate

- **`SE_DRAW_POPULATION` is default-OFF and director-reserved**; the varied pool is armed but no
  published run consumes it (`CA4_COHORT_ACTIVATION_SEQUENCING_VERDICT.md`, honest caveat).
- **The segmentation programme is behaviourally inert BY DESIGN** —
  `SEGMENTATION_WIRING_PLAN.md` Step 3 requires the cohort layer be *"pure additive... identity when
  the clustering is trivial, so the existing archetype ground truth is byte-identical"*. Correct for
  legibility work, and it means **no amount of segmentation work will ever raise decision richness.**

**The consequence nobody has recorded:** flipping `SE_DRAW_POPULATION` today would yield a book that
is varied in *composition* and identical in *behaviour*, because the attitude axes weight nothing.
That would look like richness and be theatre. **Wiring the axes to responses is worth more than
flipping the population, and should precede it.**

## 4. Why this caps demonstrable skill — and what it says about today's A/B

With universal response functions, true churn probability is a **deterministic function of
observables** plus two coarse buckets. There is no latent variable, so the company's task is
*curve-fitting*, not *inference*. A perfect company model would converge on the oracle and still
demonstrate nothing that deserves the word skill.

**This is the same fact as today's A/B result, seen from the other side.** The third arm
(`flat_at_level`) was built to split the value arm's advantage into LEVEL and SELECTION. In a world
where every household shares one response curve, per-customer selection has almost nothing to select
*on* — so the level should carry the advantage and the selection should be worth little. That is
what the 2019 window shows. **The weak selection result is a property of the world, not a defect in
the company**, and it would have been misread as a pricing failure without this audit.

R12 note: none of what follows is a licence to tune the world until the company looks clever. These
are fidelity changes (§6), and the measured outcome may well be that the company gets *worse*.

## 5. The roadmap, sequenced

Ordered by compounding return (CLAUDE.md sequencing), not by depth.

### S1 — Give `price_sensitivity` a job *(first; smallest work, largest richness gain)*
Weight `churn_position_multiplier` by the household's own drawn sensitivity. Creates the world's
first genuine latent preference: two households, same price, different responses.
**R4 — the nearest working analogue is ENGAGEMENT**, which is already exactly this shape (latent
per-household type → real behavioural gate → externally anchored). **Two diffs, and the second is
the actual work:** (a) engagement was wired and this was not; (b) `engagement_level_for_customer`
needs only a `customer_id`, whereas `assign_cohort(customer_id, base_seed, ...)` also needs the
run's base seed and the cohort curriculum. It is deterministic in `(customer_id, base_seed)` and
keys directly on the customer with no draw-order dependency (C-S2), so it IS reachable — but S1
must either thread `base_seed` to the churn decision point or add an engagement-shaped convenience
accessor. Cost is in that threading, not in the weighting.
**Takes:** one weighting function + its calibration note + the seed threading; the draw, coverage
and wall already exist.
Anti-goal-seek constraint: must preserve the `m(d)·m(−d)==1` guarantee at the population mean.

### S2 — Heterogeneous engagement *depth*, not just the gate
Engagement currently gates a cap. Real disengagement damps response to *everything* — a disengaged
household barely reacts to a price rise at all. Turn the three-level type into a damping factor
across all axes.
**Takes:** small; reuses the Ofgem-anchored shares. Sharpens the book into the bimodal
sleepy-majority/active-minority shape GB retail actually has.

### S3 — Replace the multiplicative stack with a weighted trade-off *(the deep one)*
A per-household weight vector over the axes, so service can outrank price. **This is what creates
preference reversals — the property that makes per-customer pricing genuinely winnable**, and
therefore the item that most raises the ceiling on demonstrable skill.
**Takes:** largest. Re-derives `customer_events.py:219-252`, needs a fresh anti-goal-seek proof
(R12), and re-baselines every churn figure — so it needs its own DISCOVER→FRAME per the wiring
plan's own rule. Enables S4 and S5.

### S4 — Green as a real axis, with willingness-to-pay
`green_stance` becomes a **positive** term: a real minority accepts a higher price for a green
product. Requires a green product to exist, so it depends on S5.

### S5 — Product fit as a choice
More than one product shape, and households that prefer one. Company-side work as much as world-side.

### S6 — Reputation
Slow, book-wide, accumulated from service failures; affects acquisition more than retention.

**Sequence: S1 → S2 → S3 → (S5 → S4) → S6.** S1 and S2 are independent and cheap and can land
immediately. S3 is the gate on everything after it.

## 6. R13 discipline — which half of this is mine

The axes are drawn from **curriculum marginals** (`green_stance_marginals` et al.).

- **MINE (baseline/fidelity):** wiring a latent weight to a response *mechanism*. Real households
  differ in price sensitivity; a world where they cannot is less faithful, not easier. Decided blind
  to company P&L — and S1/S2 plausibly move **against** the company by making the book harder to
  read.
- **THE DIRECTOR'S (curriculum):** the marginals — *how many* households are highly elastic, how
  many would pay more for green. Those are difficulty settings and they stay his.

This split is why S1 can proceed without a director act, and why its calibration cannot.

---

*Filed as discovery + roadmap. No level moves, no curriculum edits. The audit's evidence is disk
state (R7/R9): every "consumed by nothing" claim above was checked by enumerating live-tree readers
and discarding substring matches, which is the failure mode that produced five false findings on
2026-08-27 alone.*
