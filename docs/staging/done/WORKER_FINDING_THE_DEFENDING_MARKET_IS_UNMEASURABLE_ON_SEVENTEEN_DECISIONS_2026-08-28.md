**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# The world now defends and I cannot yet show what it costs: the instrument's resolution is one account in seventeen

B10's defence leg landed today (`5f50408c6`). This is the coupled-triad measurement that would
take it to L3 — the company tested against a world that can defeat it, and the gap measured — and
**it does not reach L3**, for a reason worth having on the record rather than buried in a retry.

## What was run

`tools/run_price_ladder --end-year 2019 --rungs 0,0.5,1,2`, twice, identical in every respect
except `docs/design/COMPETITOR_AGGRESSION.yaml`:

- **ON** — `chase_per_quarter: 0.5`, the default. The rival follows a company that undercuts it.
- **OFF** — `chase_per_quarter: 0.0`, which is byte-for-byte the world as it stood on 2026-08-27.

Two full passes, ~4m50s each. Both report `SVT recon agrees=True` so the harness is scoring the
rate the customer was actually charged, and no reference comparison below is void.

## The result, stated as it came out

| rung | mean rate vs SVT | realised churn ON | OFF | delta |
|---|---|---|---|---|
| 0.0 | −15.24% | 0.1765 (3/17) | 0.1765 (3/17) | 0.0000 |
| 0.5 | −1.68% | 0.2941 (5/17) | 0.2353 (4/17) | **+0.0588** |
| 1.0 | +16.75% | 0.4118 (7/17) | 0.4118 (7/17) | 0.0000 |
| 2.0 | +62.16% | 0.4706 (8/17) | 0.4706 (8/17) | 0.0000 |

**One rung moved, by one account.** Every other rung is identical to the roll.

## Why this is not a result, and why saying so is the point

**The common population is 17 decisions and the outcome is binary.** The smallest change this
instrument can express is one account, which is **5.9 percentage points of churn rate**. A real
effect of two or three points is not small on this instrument — it is *invisible*. The single
moved account at rung 0.5 is exactly one quantum, which is the least distinguishable-from-noise
result an experiment of this shape can produce.

So the honest reading is not "the defence leg does almost nothing". It is **"this instrument
cannot tell the difference between the defence leg doing nothing and doing something worth
having."** Those are different claims and only the second is supported.

Two things follow, and the second is the one that matters.

**The rungs above parity should not have moved and did not.** At +16.75% and +62.16% the company
is above the cap, the chase is one-sided, and the rival correctly holds — so identical churn there
is the mechanism working, not the mechanism absent. That is a real, if small, confirmation: three
of the four rungs are *predicted* to be identical and are.

**The rung that should have moved most, moved least.** At −15.24% the company is well below the
cap, which is exactly where a defending rival bites hardest, and the churn is identical. On 17
binary rolls a full-quantum move requires roughly a 6pp effect; the modelled reference shift at
that depth is around 8% of position, which does not translate to 6pp of churn on this curve. The
mechanism is doing what the unit tests prove it does, at a magnitude this experiment is not built
to see.

## This is P9, measured a second way and independently

The director's P9 says *"Only 37 accounts carry five or more renewals, so nothing can compound.
Book depth bounds every comparison."* This is that bound arriving from a different direction and
on a different question: not "can anything compound" but **"can any world change be detected at
all"**. Seventeen common decisions is the whole population that survives being priced AND rolled
at every rung — and rungs above 1.0 churn accounts out early, which is why it is smaller than any
single rung's.

**It sharpens the recommendation already in front of him**
(`SEAT_TO_DIRECTOR_P9_BOOK_DEPTH_PRICED_2026-08-28.md`). The case for 80 founders was that
nothing compounds. The case is now also that nothing is *measurable*: a world that presses cannot
be shown to press, so every subsequent world change would land with no way to score it. That is a
worse position than a shallow book, because it makes the next ten pieces of work unfalsifiable
rather than merely bounded.

## What would make this measurable, in order of cost

1. **A deeper/wider common population.** P9's Option 1 (80 founders) raises accounts carrying
   5+ renewals from 37 to ~95 at zero wall-clock cost. Directly multiplies this instrument's
   resolution. **The decision is the director's and it is with him.**
2. **A continuous outcome instead of a binary one.** Score the *modelled churn probability* per
   decision, not the realised roll. The probability moves continuously with the reference and
   has no 1/17 quantum; the roll is what destroys the signal. This is cheap, needs no book
   change, and is the right next step regardless of P9 — filed as work below.
3. **Seed replication.** `run_value_cycle_ab --noise-floor-seeds` already exists and does exactly
   this for the pricing arms. The same shape here would put an error bar on the delta instead of
   leaving a single quantum to be over-read. Costs one full pass per seed.

## What is NOT claimed

- Not that the defence leg is too small to matter. Unsupported by this instrument.
- Not that it is worth having. Also unsupported. The unit tests prove the mechanism does what it
  says at the level of one decision; this experiment says nothing either way at the level of a book.
- Not that B10 is finished. It stays at **level 2**. L3 requires this measurement to return a
  number with an error bar, and it has not.

## WORK THIS CREATES

1. Score the ladder on **modelled churn probability** as well as realised rolls, so a world change
   has a continuous surface to move. Cheapest path to a measurable coupled-triad gap.
2. Re-run this comparison once (1) lands, with seed replication, and take B10 to L3 or record why
   it cannot go.
3. P9 remains the director's, with this as a second, independent reason to take it.

## Still live
