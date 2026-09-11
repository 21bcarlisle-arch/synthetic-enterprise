**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the count cull is worse than a random draw, and the chooser's 1.64x does not transfer

**Lane 0 delivery**, claim
`the-settlement-sample-is-a-count-based-cull-and-the-chooser-earns-1.64x-at-its-size`.
Pre-registered first:
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md`,
landed **before** these numbers were taken.

---

## What was measured

The campaign was resolved **once** (seed 20260724, 500 funnel wins, 91 settled, rate 0.1826,
2,368 customer-years of campaign against a 1,200 budget). Three selection rules were then applied
to that **one** candidate list, so the rule is the only variable.

Distance is KS against all 500 candidates: per axis, and **JOINT** = the worst over 32 fixed random
directions in the z-scored 4-space (`demand_vector_coverage.accepts_weighted`).

| | ARM A — shipped count cull | ARM B — global chooser | ARM C — within-year chooser |
|---|---|---|---|
| accounts settled | 91 | 71 | **91** |
| customer-years spent | 427.6 | 362.2 | 428.2 |
| JOINT D | 0.1413 | 0.0646 | **0.1060** (9-seed mean) |
| worst marginal D | 0.0914 | 0.0939 | 0.0957 |
| per-year worst gap | 0.9pp | 5.3pp | **0.00pp** |
| years represented | 10/10 | 10/10 at k=60; **0/10 for 2024 at k=80 and k=91** | 10/10 |

## The finding nobody predicted, and it is the important one

**The shipped count cull sits at the 75th percentile of random.** Two hundred random equal-weight
draws of 91 from the same 500 give JOINT D median 0.1206, p05 0.0936, p95 0.1648. Arm A's 0.1413 is
*worse than three-quarters of random draws of its own size.*

The systematic cull was adopted for a real property — each year's booked wins are proportional to
that year's funnel wins — and that property is genuine (0.9pp worst gap). But it was never checked
against the distribution of what it books, and on the demand axes it is a **below-average draw**.
So the value on the table is not "a clever chooser beats a good incumbent". It is that the
incumbent gives away about a quarter of the available distributional quality, and recovering it is
most of the win.

## Verdict against each pre-registered prediction

**P1 — REFUTED as stated.** I predicted worst-axis KS would improve by 1.2x–2.0x. The **worst
marginal does not improve in either arm**: 0.97x for B, 0.95x for C. What improves is the JOINT
statistic. The sub-prediction inside P1 held — the gain is on the fabric axes and not on cost: in
Arm B, `fabric_w_per_k` 0.0825 → 0.0338 (2.4x) and `insulation_ceiling_w_k` 0.0914 → 0.0365 (2.5x),
while `eac_kwh` got **worse**, 0.0816 → 0.0939, which is exactly why the worst marginal did not
move: the worst marginal simply becomes `eac_kwh`.

**P2 — CONFIRMED, and it refuses Arm B under the acceptance test I wrote in advance.** The
pre-registration said: *"The per-account weights must reconstruct the per-year proportionality; if
they cannot, the change is refused."* They cannot. `fit_weights` fits to the demand axes, and year
is not one of them, so nothing in the fit has any reason to reproduce it. Worse than the predicted
5pp: at k=80 and k=91 the year **2024 is erased entirely** — 16.6% of the population, zero
representation.

That erasure is **the first-come cliff coming back**. `plan_growth_campaign`'s own comment records
why the allocation was moved out of the year loop on 2026-08-29: *"First-come therefore spends the
whole budget on the most expensive cohort and books ZERO in every year after it runs out."* Arm B's
budget guard walks the chosen set in index order, which is year order, so 2016's 9.83-customer-year
tails eat the budget and the late years drop off. I reintroduced, in a new mechanism, the precise
defect a previous fix had removed — and only the per-year column made it visible.

**P3 — REFUTED.** I predicted the settled account count would change and move every published
financial figure. Arm C settles **91 accounts, the same 91-account count, with the same per-year
counts and the same 428 customer-years**. The book's size does not move. *Which* accounts are on it
does, so financial figures still move, but not by the mechanism I predicted.

**P4 — NOT YET TESTED.** The null case (`campaign_cy <= headroom_cy`, byte-identical to no ceiling
at all) needs the wiring, which is not done. It is the first control to write.

**P5 — CONFIRMED.** The budget guard binds and remains the invariant; Arm C spends 428.2 against
Arm A's 427.6 of the same headroom.

## My own first number was a lucky seed, and the correction is the point

The single-seed Arm C run returned JOINT D = 0.0956 and I wrote "1.48x" beside it. Sweeping the
chooser seed 0–8 gives **mean 0.1060, sd 0.0115, range 0.0900–0.1240** — 0.0956 was near the *best*
of nine. The honest figure is **1.33x**, not 1.48x, and both are recorded here because a corrected
number kept beside the one it replaces is the only evidence the sweep was not run until it agreed.

**Arm C's whole nine-seed range sits inside the random null's 5–95 band** (0.0936–0.1648), at the
21st percentile. Arm C is a good draw, not a different kind of object.

## What this does NOT establish, stated plainly

**This is a one-run figure.** One candidate list, one run seed. The nine seeds vary only the
*chooser*, not the world — they bound my arm's internal noise and say nothing about whether 1.33x
survives another run seed. This project has paid for exactly this confusion more than once. **No
figure from this result may be published as a bound, and the claim "the chooser earns 1.64x at its
size" is not supported on this population by anything measured here.**

## What is next

1. Wire **Arm C** — the pre-registered fallback, named in the pre-registration before any arm ran.
   It keeps the cull's year stratification exactly, chooses medoids over the four axes *within*
   each year, and normalises each year's fitted weights so the year's weighted mass **is** its
   population share. That is what "per-account weights that reconstruct the per-year
   proportionality" has to mean, and it makes the 18.3% single inflation factor per-account.
2. **P4 first**: the null case must be byte-identical before anything else is believed.
3. A **run-seed** spread before any ratio reaches a page.

## The axis defect found on the way in

Three of the six axes I was going to choose over were one axis. On these 500 candidates,
`solar_aperture_m2 / floor_area_m2` has exactly **one** distinct ratio (0.05775) and
`internal_gain_kw / floor_area_m2` exactly one (0.004) — `fabric_parameters` derives all three from
the same area. Left in, the z-scored clustering would have weighted floor area three times while
looking like a six-axis design. Caught by printing the numbers at real inputs before shipping the
formula. Same class as `SEAT_FINDING_TWO_AXES_OF_THE_DEMAND_VECTOR_ARE_THE_SAME_AXIS_2026-09-08`,
one module over. `fabric_w_per_k` and `insulation_ceiling_w_k` correlate at 0.974 and both are
kept: a near-duplicate is not an identity, and the ceiling has real zeros and is the mission's own
quantity — what a household could still be sold.
