**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# The ladder now resolves the defending market at every rung, and the company's belief does not move by one part in 10^12

The instrument that returned nothing on 2026-08-28 morning
(`WORKER_FINDING_THE_DEFENDING_MARKET_IS_UNMEASURABLE_ON_SEVENTEEN_DECISIONS`) now returns a
number at every rung. **The blocker was the roll, exactly as that finding predicted.** What the
measurement then says is not what I expected to be writing up, and it is the reason B10 stays at
level 2.

## What changed in the instrument

`tools/run_price_ladder.py` carried the world's own `realized_churn_probability` on its
per-decision rows and in `world_curve_vs_belief`, but **`per_rung` and `slopes` — the headline
table and the three published slopes — read only the binary flip count.** That count is k/17 on
this book, so its smallest expressible change is 5.9 percentage points.

The continuous quantity now reaches both, as `world_p_leave_mean` per rung and a
`world_p_leave` leg in each of the three slopes, beside the binary leg rather than replacing it
(a non-renewal is a thing that happened and a probability is not). Two controls, both
mutation-proven red:

- `test_the_continuous_leg_SEES_a_move_the_binary_leg_CANNOT` — two worlds with **identical
  rolls** and a world probability 3 points apart. The binary leg is bit-identical by
  construction; the continuous leg must report the move. Wiring it to the flips reds it.
- `test_a_rung_missing_the_world_probability_REFUSES_a_mean_rather_than_averaging_the_rest` —
  FAIL-OPEN. If one decision of ten carries no world probability, averaging the other nine
  publishes a mean over nine beside a realised rate over ten, and the population difference then
  reads as a price effect. Removing the completeness guard reds it.

The printed summary now also states the binary leg's own quantum (`1/17 = 0.0588`) beside the
slopes it bounds, so a reader cannot take a movement smaller than one account for a measurement.

## The measurement

Fresh chase-ON / chase-OFF pair on **one tree**, identical book, identical seeds, differing in
exactly one declared parameter (`chase_per_quarter`, supplied via the committed
`docs/observability/aggression_chase_off.yaml`; the director's
`docs/design/COMPETITOR_AGGRESSION.yaml` is untouched). Both runs report the null rung
reproducing the flat-rules control and `SVT recon agrees=True`, so the join scores the price the
customer was actually charged and no comparison below is void.

Fixed population: **17 decisions × 4 rungs = 68 paired observations**, every one carrying the
world probability (`world_p_leave_carried: [17,17,17,17]` in both worlds).

| rung | world ON | world OFF | **the chase** | belief | gap ON | gap OFF | binary ON | binary OFF |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 0.0530 | 0.0462 | **+0.0068** | 0.2595 | +0.2066 | +0.2134 | 3/17 | 3/17 |
| 0.5 | 0.1310 | 0.1154 | **+0.0156** | 0.3870 | +0.2560 | +0.2716 | 5/17 | 4/17 |
| 1.0 | 0.3194 | 0.2927 | **+0.0267** | 0.5384 | +0.2190 | +0.2457 | 7/17 | 7/17 |
| 2.0 | 0.5636 | 0.5185 | **+0.0451** | 0.8054 | +0.2418 | +0.2868 | 9/17 | 8/17 |

**Every rung moved, and every move is smaller than the binary instrument's 5.9pp quantum.** That
is the whole explanation of the morning's null: the effect was always there and was always too
small to appear. 34 of the 68 paired observations moved, **all of them upward**, none downward,
largest single move +0.6493.

## The company's belief does not move at all

Across all 68 paired observations the company's `believed_p_leave` is **bit-identical** between
the two worlds — `max |ON − OFF| = 0.0`, not approximately zero. (The believed *slopes* differ in
the sixth decimal, +0.004676 vs +0.004681, purely because the x-axis is the delivered uplift and
the arm's delivered price differs marginally between worlds. The y-values are identical.)

**The mechanism, named rather than inferred.** The company's only market-sensitivity channel is
`company/crm/market_conditions.market_conditions_multiplier(renewal_year)` — a lookup keyed on
the **calendar year alone**. It is structurally incapable of responding to a rival's price move
within a year. `B4_competitor_field` gives the company the Ofgem-published default tariff, which
is the *cap*, not the rival; the chase moves the rival and leaves the cap where it was.

So the gap is measured and it decomposes cleanly: the world moved 0.7–4.5pp, the company moved
0.0000, and **every pound of the change in the gap came from the world side.**

## B10 stays at level 2, and the reason is now a number rather than an absence

The coupled-triad law is that no world atom reaches L3 until the company has been tested against
it and the gap measured. The gap is now measured and non-null — 20.7 to 28.7 percentage points of
over-prediction at every rung, per decision, on a paired population. That half is satisfied and
it is a real advance on this morning.

**I am refusing the level move anyway, on the FRAME's own criterion.**
`docs/design/COMPETITOR_FIELD_FRAME.md` §5 says a large persistent gap is not itself a defect —
it is the expected signature of a real epistemic limit — but that **"a defect is a gap that never
moves in response to new observations"**. That is precisely what was measured: the gap does not
move because nothing about the rival reaches the company at all. §5's component 2 (does the
company's churn response move in the correct *direction*?) returns not "wrong sign" but "no
response exists", which is the worse of the two failures it names. §5's component 1, the ceiling
gap (`observed_ceiling` as seen by the company vs the true cheapest rival price), is **not
measured here** and needs an observation channel that does not exist yet.

Self-certifying L3 on a result whose content is "the company is blind to this world change" would
be recording the instrument's success as the atom's.

## What L3 now needs, and what it no longer needs

**No longer needed:** a deeper book, for *this* question. The morning finding's option 1 (80
founders, to raise resolution) is not on the critical path for B10 — the continuous leg resolves
a 0.7pp effect on 17 decisions, which is roughly nine times finer than the binary leg could
manage on a book five times larger. Book depth still bounds everything that compounds (P9); it no
longer bounds *detection* of a world change.

**Still needed:** a competitor observation channel the company can actually read — the §5 ceiling
gap. Until the company has some observable that moves when the rival moves, every future world
change will measure exactly this: the world presses, the belief holds still.

## On seed replication, which the direction asked for and which this comparison does not need

`realized_churn_probability = round(1.0 - effective_p_retain_pre_offer, 4)`
(`simulation/customer_events.py:520`) is computed **before** the roll and the roll never enters
it. The roll decides `event_type`; it does not touch this quantity. So the per-decision paired
comparison above carries **no sampling noise from the roll** — replicating seeds would put an
error bar on a quantity whose variance from that source is structurally zero, and would be a
misleading bar rather than a conservative one.

What the roll *does* affect is the **population**: who is still in the book at a later renewal.
That is handled by the fixed intersection, not by replication. Seed replication remains genuinely
owed on the **book-level P&L** comparison (the −£3.0k per arm in
`WORKER_FINDING_THE_DEFENDING_MARKET_IS_A_LEVEL_EFFECT`, item 4), where the outcome *is* a sum
over realised events and the roll is in it.

## A correction to my own earlier reading, made before anyone raised it

An intermediate analysis of the **morning's** artefacts (07:55/08:05) had the chase effect
*decaying* with price — largest at rung 0, near zero at rung 2 — and I was assembling the
one-sided-mechanism story that explains it (a rival holds when the company prices above the cap).
**The fresh pair shows the opposite: the effect grows monotonically with the rung.** The two pairs
were run on different trees (`039f202ce` and `69a0bb068` landed between, and the morning tree
additionally carried another lane's uncommitted settlement-clock work), so I cannot attribute the
difference and am not going to try. Only the fresh pair is reported above, because only it is
internally controlled. The decay story was drafted and is discarded; it is recorded here so it
does not get re-derived from the stale artefacts by whoever reads them next.

## Reproducing it

```
python3 -m tools.run_price_ladder --end-year 2019 --rungs 0,0.5,1,2 \
    --out docs/observability/ladder_competitor_chase_on_2019.json
```
For the OFF arm, set `competitor_reference.AGGRESSION_PATH` to
`docs/observability/aggression_chase_off.yaml` before importing the tool and assert
`aggression()["chase_per_quarter"] == 0.0` before the run — an override that silently failed to
take would report the chase as costing nothing, which is the fail-silent shape that would turn
the whole comparison into a confident null. ~9.5 minutes for the pair run concurrently.

## WORK THIS CREATES

1. **The §5 ceiling gap needs an observation channel.** This is B10's remaining L3 leg and it is
   a company-side build, not a world-side one.
2. **`market_conditions_multiplier(renewal_year)` is a year lookup standing in for a market.**
   Named here as the specific thing that makes the company chase-blind; whether it should become
   observation-driven is a design question, not a defect to patch.
3. Seed replication on the **book-level** P&L comparison, per the note above.

## Still live
