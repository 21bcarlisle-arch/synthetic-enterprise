**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The sharing side of R3 is worth 7.4x the carbon it abates, and only a third of this book could be sold the tariff that shares it

**Found:** 2026-09-07, delivery seat, claim `a49-ceilings-the-sharing-side-of-r3`.
**Instrument:** `tools/tou_sharing_ceiling.py` · **Artefact:** `docs/observability/tou_sharing_ceiling.json`
**Pre-registration:** `docs/staging/PREREG_WHETHER_THE_SHARING_CEILING_CLEARS_ITS_NULL_AT_R3S_OWN_PANEL_SIZE_2026-09-07.md`

## What was asked

`SEAT_FINDING_R3_MEASURES_VALUE_CREATED_AND_THIS_BOOK_HAS_NO_INSTRUMENT_OF_SHARING_IT_2026-09-07.md`
found that R3 bounds value CREATED and nothing bounds SHARING it: a shifted kWh is cheaper only on
a time-of-use tariff, this book holds none, and so R4's `time_shifting` arm reports
`gbp_per_household_year: None`. Its own recommendation was A49's discipline applied to the gap A49
exposed — **bound the ToU tariff before building it.** This is that ceiling.

## The four findings

**1. The money is the case, not the carbon — and by a wide margin.** The same act R3 measures —
every kWh moved into the day's cleanest six half hours — avoids **£13.33/MWh of wholesale cost, 30%
of the mean day price**, over 1,520 whole days of Elexon MID, 2016-09 to 2020-12. On this book that
is **£51.36 per household-year** at a shiftable share of 1.0, against R3's hindsight carbon value of
**£6.91**. A ratio of **7.4x**.

The two are never summed — a wholesale cost avoided and tonnes valued at the DESNZ traded price are
two currencies — but their **ratio is a quantity**: both are pounds per household-year, over the
same book, from the same act, at the same shiftable share. It says which column the case rests on.

**2. And only one of the two can be shared.** The carbon lands on nobody's bill. The money does.
That reverses the way this thread has been read: the tariff is not a way of *monetising* R3's
abatement, it is the **precondition for the abatement happening at all** — the money is what pays
for the behaviour that abates the carbon. Build the timing advice without the tariff and you get a
product that demonstrably works and that nobody can be charged for; build the tariff and the carbon
arrives as a by-product of a household acting on its own bill.

**3. Sharing creates nothing, and the company's own optimum is interior without any elasticity.**
The household's share and the company's share sum to the created value at every pass-through, by
construction. That identity is asserted in code, not stated in prose. And the endpoints settle a
question that looked like it needed a behavioural parameter:

- at **zero** pass-through a household's bill is identical whenever it draws, so it has no money
  reason to move any of it; nothing moves, nothing is created, the company keeps a share of nothing;
- at **full** pass-through everything created reaches the bill and the company retains none of it.

Zero at both ends, so **for any shift response that rises with pass-through the company's own take
is maximised strictly in the interior.** That follows from the endpoints and needs no elasticity.
*Where* it sits does need one, and none is established — a named gap, not a number.

**4. The binding constraint is the meter, and it is a third of the book.** A time-of-use tariff is
settled half-hourly and half-hourly settlement needs a smart meter. **22 of the 68 households that
carry an electricity EAC also carry a smart meter (32%)**, so the whole reachable book is
**£1,125 a year** at the ceiling — a ceiling, at a shiftable share no source establishes, before any
cost of the product. The per-household figure is published over R3's denominator so the two
instruments' columns divide the same book; the book figure is published over the reachable
population only, and the payload says which is which.

## The pre-registered question, and its answer

Predicted before looking: the ceiling clears its null at R3's panel size, at a ratio **between 3x
and 12x**, i.e. the same order as R3's 4.82x rather than an order above it.

Measured: **5.04x at the median of 60 draws, 2.97x at the worst, 7.20x at the best, and it clears in
every draw.**

Prediction confirmed on the median and the mechanism. **The worst draw at 2.97x falls just under the
3x floor I wrote**, and that is recorded here rather than quietly widened: the range was a little
tight at the bottom.

The whole-panel ratio is 23.21x and **must not be read against R3's 4.82x** — R3's null is a mean
over 20 days and this one over 1,520, and the maximum over draws of a mean falls as the panel grows
for sampling reasons that have nothing to do with signal. The instrument publishes the matched-panel
figure and says the whole-panel one is not comparable. A control holds that the ratio genuinely
falls with panel size; **its first draft did not** — it compared the matched ratio against the
whole-panel ratio and survived the mutation that replaces the subsample with the whole series,
because the two legs took their maxima over different numbers of draws. It was measuring the draw
count. Both legs now use the same draw count and differ only in the panel.

## What this does NOT say

- **Not that the tariff should be built.** £51.36 is a CEILING at a shiftable share of 1.0 — every
  kWh moved — which no household has. At a tenth of load moved it is £5.14. And it is gross: the
  cost of half-hourly settlement, of a smart-meter rollout to the traditional-metered majority, and
  of the shape and imbalance risk a supplier takes on when it prices a household half-hourly are
  none of them in this figure.
- **Not a number for what the company would earn.** That is a point on a frontier and the frontier
  is an identity. Picking a pass-through is a commercial decision nobody has taken.
- **Not a bound on the whole ToU case.** Only the WHOLESALE leg is counted. Avoided red-band DUoS,
  triad exposure and capacity costs are real value a ToU tariff creates and none is in this figure.

## Errors, in both directions, because publishing one direction is arguing

**Overstates:** a price differential between two half hours is producer surplus PLUS the resource
saving from dispatching cheaper plant, and only the second is value created; this bound cannot
separate them. The price shape is also exogenous here, and a book-wide shift would flatten the
differential it is paid out of.

**Understates:** the counterfactual is the day's MEAN price, chosen to match R3's construction
exactly so the two columns describe the same act — but households draw disproportionately in the
evening peak, above the mean, so the cost their shift actually avoids is larger. Only the wholesale
leg is counted. And the MID panel ends 2020-12, before the 2021-2023 episode when within-day
differentials were far wider than anything in this window.

## What is next on this thread, and I am not asking

The instrument is landed and its artefact is committed. Two things follow and neither is this turn:

1. **Wire it to a reader.** R4's `time_shifting` arm should keep its `None` — on THIS book the bill
   saving really is zero — and gain a pointer to what it would be if the tariff existed, and
   `/harness/` should carry the frontier beside the two ceilings already there. An instrument
   nobody reads is an orphan, which is the defect the previous commit on this thread fixed.
2. **The shift response as a function of pass-through** is the one number that would turn the
   frontier into a decision, and it is a question to research rather than a value to pick. It is
   the same class of gap as the shiftable share, and the two multiply.
