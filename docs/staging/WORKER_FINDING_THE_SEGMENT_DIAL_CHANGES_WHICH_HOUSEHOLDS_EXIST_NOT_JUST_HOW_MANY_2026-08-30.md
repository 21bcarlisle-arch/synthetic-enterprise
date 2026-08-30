**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Suspending a business segment changes WHICH households exist, not just how many — so no A/B across that dial is attributable

**Found:** 2026-08-30, dispositioning the HEAD red census. Filed BLOCKING rather than LATENT
because it is a confound in a curriculum dial: any measurement taken across `SE_SERVED_SEGMENTS`
compares two different populations and cannot be attributed to the dial.

**No published figure is known to be wrong.** The live book runs with all segments served, so the
confound has not been exercised by a published run. It is the measurement that is unsafe, not the
current number.

## Reproduced directly, same function, same seed

```
SE_SERVED_SEGMENTS="resi,SME,I&C"  ->  {resi: 238, SME: 9, I&C: 11}   n = 258
SE_SERVED_SEGMENTS="resi"          ->  {resi: 257}                     n = 257
```

The residential count moves from **238 to 257** when the business segments are suspended. If the
dial were a filter, suspending a segment could not add nineteen households.

And the sets are not nested in either direction:

```
resi accounts present ONLY when I&C is served:
  SYN-2016-003, -006, -010, -029, -035, -036, -049
resi accounts present ONLY when I&C is suspended:
  SYN-2016-004, -017, -021, -024, -025, -026, -050, -060, -061, -064, ...
```

**Households appear and disappear in both directions.** The dial is not selecting from a fixed
population; it is generating a different one.

## The mechanism

`simulation/live_population.py` applies the filter in three places, and two of them are fine.
`static` is filtered after the roster is read (line ~434) and `drawn` is filtered after the trickle
is drawn (line 204) — both pure subsets, both correct.

The third is the growth campaign:

```python
won = [c for c in _won_customer_dicts(_campaign(_pre_growth_book(seed), seed))
       if _serves(c, served)]
```

The WINNERS are filtered, which is what the 2026-08-26 repair was about and is correct as far as
it goes. But the campaign's **input** is `_pre_growth_book(seed)`, and that function is itself
segment-filtered:

```python
book = [sc for sc in _drawn_trickle(seed) if _serves(sc.to_customer_dict(), served)]
...
static = [c for c in _STATIC_ROSTER if _serves(c, served)]
```

So suspending a segment changes the book the campaign plans against, which changes the campaign's
stochastic funnel, which changes **which residential prospects it wins**. The filter is applied
correctly at the output and leaks in through the input.

That is exactly what the red control says in its own words — *"the filter is not independent of
the segment it is filtering on"* — and the control is right.

## Why this is BLOCKING rather than a note

`served_segments` is a **curriculum dial**: it decides which world the company lives through, and
it is the director's instrument. The entire point of a dial is that it can be moved and the
consequence attributed. This one cannot be:

- Two arms differing only in the dial have different residential books, so any difference in P&L,
  churn or arms performance is confounded by population composition.
- The confound is invisible in the aggregate — 238 vs 257 looks like "we suspended some accounts"
  until you diff the identities.
- It sits on the same class as the standing rule that a comparison must not change two things at
  once. Here one deliberate change silently makes a second.

**Nothing has been measured across this dial yet as far as I can find, which is the only reason
this is not also a correction to a published figure.** Anyone who does so before it is repaired
will get a number and no way to know what it means.

## Is the campaign SUPPOSED to depend on the dial?

There is a real argument that it should: a supplier that serves fewer segments genuinely runs a
different acquisition campaign, and modelling that is more faithful than not. **That argument is
about the SIZE of the campaign, not about the IDENTITY of the households it wins.** A supplier
withdrawing from I&C does not thereby win a different set of houses; it wins the same houses with
a different budget.

So the repair is not "stop the campaign seeing the dial". It is to make the campaign's household
draw independent of the dial — the same C-S2 constraint the drawn cohort already honours, keyed on
the customer rather than on draw order — while leaving the campaign's scale free to respond.

## What is owed

1. Make the campaign's residential prospect draw a function of `(prospect_id, base_seed)` rather
   than of the book's contents, so the dial cannot reorder it.
2. A control keyed to the property: **the residential SET, not the residential COUNT, is identical
   across dial positions.** The existing test asserts the count, which is why it took a
   nineteen-account swing to fire — a dial that swapped ten households for ten others would have
   passed it silently. That is the sharper half of this finding and the reason it is filed
   separately from the labelling one it was found beside.

Not repaired here: it changes the composition of the live book and therefore moves published
figures. It needs its own pre-registration and a one-variable run.

## The consequence of the severity, chosen against my own convenience

BLOCKING means *"new level-raises in the affected LANE are refused until it is repaired, or until
the limitation is explicitly recorded and accepted."* The affected lane is
`W2_customer_generator`, which is the lane the entire choice-and-channel programme sits in — C1b
and C2 both live there.

I considered filing this LATENT for exactly that reason, and `background/finding_severity.py`
names that move in its own docstring as the anti-pattern: *"deciding one's own finding is not
BLOCKING in order to keep a lane open."* It is BLOCKING on the definition — the dial is an
instrument and the instrument is untrustworthy — so it is filed BLOCKING.

**What this does and does not stop.** It refuses new LEVEL-RAISES in `W2_customer_generator`. It
does not stop the work: C2 (competing-risks departures) and C1b (SVT assignment) touch nothing in
this path and proceed. What they cannot do until this is repaired is claim a level move on the
strength of a measurement taken across the segment dial — which is precisely the claim that would
be wrong.

**The accept-the-limitation route is the director's, not mine.** `served_segments` is a curriculum
instrument and R13 puts curriculum with him. The limitation is recorded above; accepting it is a
decision about his own dial. Recommendation if he wants the lane open before the repair: accept
it explicitly and narrowly — *no result may be attributed to the served-segments dial until the
residential SET is proven stable across dial positions* — which costs nothing today, because
nothing is measured across it.

## Its relationship to the companion finding, stated so they are not merged

`WORKER_FINDING_ELEVEN_DRAWN_HOUSEHOLDS_ARE_WEARING_A_BUSINESS_LABEL_2026-08-30.md` is a different
defect that presents in the same place. That one is a labelling error with no behavioural
consequence beyond three red controls. This one is a draw-order dependency in a curriculum
instrument. Fixing the labels would change the numbers above and would NOT fix this — the
nineteen-household swing would become a smaller swing, and the confound would remain, quieter.
**Merging them would have hidden this one behind the easier repair**, which is the reason for two
documents.
