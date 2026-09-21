**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the ceiling's cost curve is CONVEX, my filed prediction is refuted, and the memory bound the page calls slack is ~15x optimistic

**Filed:** 2026-09-21. Drawn as Lane 0 delivery,
`the-capacity-that-refuses-the-thesis-book-stands-on-nothing`.

BLOCKING on one clause only, and it is named at the bottom: `site/data/value_arms.json` publishes
`memory_ceiling.max_customer_years = 38,275` and the sentence *"Memory is not what caps this book"*,
and direct measurement puts the true figure between one and two orders of magnitude lower. The rest
of this document is RECORDED.

---

## 0. What was already in flight, which is the first thing a reader needs

**I did not launch this measurement and I must not be read as having taken it.** A prior invocation
under this same claim launched it at 16:54 local, gated behind
`tools.wait_for --pid 798381 --subject "the live producer run this cost measurement must not
contend with"` — which is the §6a requirement, honoured — as:

```
python3 -m tools.settlement_ceiling_probe --budgets 1200 2000 2800 3400 \
        --publish-interval 604800 --menu-intervals 5400 86400 604800 \
        --json docs/observability/settlement_ceiling_slope_20260921.json
```

At the time of writing three of its four points have completed and the fourth (3,400) is 85 minutes
in. The parent holds `peak_rss_mb` for the completed points in memory and writes the report only
when all four finish, so **this document reports the three children's own `child_wall_s` from
`~/.cache/synthetic-enterprise/settlement_ceiling_probe/point_*.json` and takes memory from a
`/proc` sample of the live child.** Everything below is labelled with which of those it is.

Two things the parent's own flags already settle, and they are the prior invocation's judgement
rather than mine: the publish interval was passed as a **menu** (5,400s / 86,400s / 604,800s) and
not as a single chosen value. That is the correct shape — the constant's note is explicit that the
interval is a preference for the director to name, not a measurement — and it means the deliverable
here is the **curve**, with the number falling out of whichever interval he picks.

---

## 1. The measurement

Three points, sequential, same box, `producer_in_flight` null at the start and end of each:

| budget | customer-years committed | wall clock (child, s) | wins | refused by the budget |
|---|---|---|---|---|
| 1,200 | 1,197.0 | 1,494.1 | 81 | 419 |
| 2,000 | 1,995.2 | 2,660.9 | 240 | 260 |
| 2,800 | 2,799.3 | 4,585.2 | 421 | 79 |

The funnel supplied 500 wins at every point, so the budget is what bound all three and the x-axis
is what was actually spent, not what was offered.

**The marginal cost RISES with the book:**

* 1,197 → 1,995 cy: **1.462 s per customer-year**
* 1,995 → 2,799 cy: **2.393 s per customer-year**

## 2. My prediction, refuted, kept beside the result

I filed, before the run: *"the marginal cost is ≈0.67s per customer-year on a ≈215s fixed
component, so the smallest leg's book should settle in roughly 2,300s on a quiet box, and I predict
wall clock will not bound it either."*

**Both halves are wrong, and the second follows from the first.**

The model was *linear with a positive fixed component*, fitted to the only two points that existed
(796.1 cy at 746.8s, 1,200.0 cy at 1,018.7s). Three points refute the shape outright, and the
cheapest way to see it needs no fitting at all: **a straight line through today's two lowest points
has an intercept of −255.8 seconds.** A negative fixed cost is not a thing, so no line fits, and the
curve is convex.

Fitted exactly through the three measured points (`T` in seconds, `cy` in customer-years):

```
T(cy) = 1,132.2  −  0.3933 · cy  +  0.00058116 · cy²
marginal(cy)  =  −0.3933 + 0.0011623 · cy
```

| book | predicted by MY filed model | measured / fitted today |
|---|---|---|
| 1,197 cy | ~1,017 s | **1,494 s (measured)** |
| 3,163.9 cy (the smallest leg) | ~2,335 s | **5,705 s (95 min, fitted)** |
| 3,400 cy | ~2,493 s | **6,513 s (109 min, fitted)** |

So the smallest leg's book takes **~2.4x longer than I predicted**, and wall clock is a real cost
that grows faster than the book does. The prediction failed in the direction that flatters the
thesis, which is the direction to distrust.

## 3. Do the two existing cost points still lie on the curve? NO — and the way they miss is informative

The item asked this explicitly. Both August points sit far **below** today's curve:

| point | measured then | today's curve says | ratio |
|---|---|---|---|
| 796.1 cy, 2026-08-24 | 746.8 s | 1,187.4 s | 1.59x |
| 1,200.0 cy, 2026-08-29 | 1,018.7 s | 1,497.1 s | 1.47x |

**But the SLOPE agrees and the INTERCEPT does not.** August's marginal, measured between its own
two points (midpoint cy ≈ 998), was 0.673 s/cy. Today's fitted marginal *at that same book size* is
**0.767 s/cy** — 14% apart, which is well inside what two points and a different day can resolve.
What moved is the fixed component: August's two points imply **~211 s**, today's three imply
**~1,132 s**.

So the honest reading is: **the per-customer-year settlement cost is roughly unchanged since
August; the run's fixed cost is about 900 seconds heavier.** That is a different defect from the one
the item was looking for, it is attributable to neither this constant nor the book, and I am not
going to guess at its cause here. **I cannot yet say** whether it is a code regression in the
non-settlement part of the run or residual box contention — the three points were taken with no
producer run in flight but not on an idle box, and separating those needs one repeat of the 1,200
point, which is the cheapest next measurement anyone can take and is handed off below.

What the convexity is NOT explained by: contention would have to grow with the book to produce it,
and a uniform slowdown factor cannot make a positive intercept negative.

## 4. THE BLOCKING PART — the memory bound is ~15x optimistic, in the flattering direction

`site/data/value_arms.json` publishes, and `site/capabilities/` renders:

```
memory_ceiling.max_customer_years      = 38,275
memory_ceiling.bytes_per_customer_year = 224,239          (0.224 MB/cy)
what_it_does_not_bound: "Memory is not what caps this book ..."
what_is_not_established: "... the RSS ceiling is 38,275 customer-years, about twelve times what
                          that leg needs ..."
```

Measured, from `/proc/<pid>/status` on the live 3,400-customer-year child:

```
VmHWM = 12,272,460 kB  =  11,984 MB     at budget 3,400
```

Against the August clean point (4,193 MB at 1,199.9 cy) that is two points on a memory curve:

```
slope   ≈ (11,984 − 4,193) / (3,400 − 1,200)  =  3.54 MB per customer-year
intercept ≈ 4,193 − 3.54 × 1,200             ≈  ~-56 MB, i.e. ~0 fixed
```

**3.54 MB/cy measured against 0.224 MB/cy published — a factor of 15.8.** On the same
`budget_rss_bytes` the feed uses (8,582,946,816 = 8,186 MB), the measured rate gives a ceiling of
roughly **2,300 customer-years**, not 38,275. That is *below* the 3,164 the smallest leg needs.

**Why the published figure is wrong, named rather than left as a discrepancy.**
`premise_population.settled_book_ceiling_customer_years` prices exactly two stage costs from an old
scale probe — `settlement_build` and `run_output_serialization` — multiplied by a
records-per-customer-year rate. It therefore prices **the retained settlement rows and nothing else
the run holds**. The 2026-09-21 repair at `c58350e2e` was right to re-rule the record population
from 17,520 (half-hourly, an I&C rate for a segment suspended on 2026-08-24) down to 289.4 (the
folded daily rows the book actually retains), and that fixed a 59.7x error in the **pessimistic**
direction. It left a second error, of similar size, in the **optimistic** one — because the thing
being priced was never the run's footprint, only one of its data structures.

**Optimistic is the dangerous direction here**, and that is why this clause is BLOCKING rather than
RECORDED. `bound_kind: "upper_bound"` and `both_are_floors: true` are honest labels and the
arithmetic is a genuine upper bound; an upper bound 16x above the truth is still an upper bound.
What is not honest is the **sentence** the page derives from it — *"Memory is not what caps this
book"* — and `what_is_not_established`'s *"about twelve times what that leg needs"*. Both are
published as findings about the world, both are false on measurement, and both are hard-coded in
`settled_book_ceiling_customer_years`'s own `what_it_does_not_bound` string, which also pins the
literal "1,200" and "slack by 4.5x". That is a claim keyed to today's answer, sitting inside the
function whose answer it describes.

**It is not fixed in this commit, deliberately.** The repair is to price the ceiling against a
MEASURED whole-run RSS curve rather than against two stage costs, and the curve's third and fourth
points arrive when the in-flight probe writes
`docs/observability/settlement_ceiling_slope_20260921.json`. Landing a re-ruled ceiling from one
`/proc` sample of an unfinished child would replace a wrong number with a less-wrong number taken
the same careless way. The finding is filed BLOCKING so the page's sentence cannot be cited again
in the meantime.

## 5. What this means for the thesis lever, which is why the item was drawn

The item's hope was that nothing bounds 1,200 and the smallest leg (3,164 cy) is therefore
reachable. On the measurement:

* **Memory does bind**, at roughly 2,300 cy on the feed's own RSS budget — *below* the leg.
* **Wall clock does bind**, and harder than linearly: the leg's book costs ~95 minutes of run
  against today's ~25 minutes at 1,200.
* Neither of those makes 1,200 the right number. **1,200 still stands on nothing** — it is not the
  memory bound (that is ~2,300 on today's budget share) and it is not a time bound (there is still
  no chosen interval). It remains a historical number, and the constant's own note continues to say
  so correctly.

The shape of the answer has changed, though, and this is the part worth carrying forward: before
this measurement, "raise the ceiling" was blocked only by an unstated preference. After it, raising
the ceiling to reach the smallest leg is **a real engineering cost with a real memory wall in front
of it**, and the director's interval choice is no longer the only thing in the way. A measured
*"this box cannot reach that book without a fold"* is a complete answer, and it is now within two
points of being provable.

---

## 6. Owed

1. **The in-flight probe's report.** `docs/observability/settlement_ceiling_slope_20260921.json`,
   with `peak_rss_mb` for all four points, is the artefact this document is standing in for. Land
   it when it lands.
2. **One repeat of the 1,200 point**, to separate "the run's fixed cost regressed ~900s" from "the
   box was contended". Cheapest measurement on the board.
3. **Re-rule the memory ceiling against measured whole-run RSS**, and delete the hard-coded
   "1,200"/"slack by 4.5x" sentence from `settled_book_ceiling_customer_years` — it is a claim
   pinned to an answer inside the function that computes it.
4. **`tools/settlement_ceiling_probe.py` is 226 lines dirty on the shared tree** (the
   `--menu-intervals` work, among others) and uncommitted. It is what is producing this
   measurement. It is not landed here because the lane that wrote it is mid-run against it;
   landing its bytes underneath a live parent is the one thing that could lose the four points.

---

# ADDENDUM — the probe finished at 19:49Z, twenty minutes after the above was filed

Everything above was written from three of four points and a `/proc` sample. The parent has since
written `docs/observability/settlement_ceiling_slope_20260921.json` with all four and its own
parent-side `peak_rss_mb`. **Three of my figures above are wrong and one of my judgements was.**
They are corrected here rather than edited above, because a document revised after its answer
arrived is not evidence that it was written before.

## What the fourth point changed

| budget | committed cy | wall (s) | peak RSS (MB) | probe says clean |
|---|---|---|---|---|
| 1,200 | 1,197.0 | 1,499.6 | 5,507.4 | **yes** |
| 2,000 | 1,995.2 | 2,666.5 | 8,504.7 | no |
| 2,800 | 2,799.3 | 4,591.5 | 12,501.8 | no |
| 3,400 | **3,135.5** | 5,296.0 | 13,920.9 | **yes** |

**CORRECTION 1 — two of the three points I built §1–§3 on are labelled UNCLEAN by the probe
itself**, and I did not know it because the reason lives in a parent-side field the child files do
not carry: *"another process wrote `book_growth_campaign.json` during this run"*, so their
committed customer-years are not their own. Their wall clock and RSS are parent-side and
uncontaminated; it is the x-axis that is suspect. The probe therefore computes ONE marginal, over
the two clean points only: **1.958 s and 4.340 MB per customer-year.**

**The convexity conclusion survives that**, and it is worth saying why rather than assuming it: on
the two CLEAN points alone, a straight line has an intercept of **−844.6 s**. A negative fixed cost
is not a thing, so the curve is not affine over that range whichever middle points you trust. What
does NOT survive is my fitted quadratic — it predicted 5,613 s at 3,135.5 cy against 5,296 measured,
and the last segment's marginal (2.10 s/cy) is *below* the previous one's (2.39), so the curve is
not uniformly convex either. **My "T(cy) = 1,132.2 − 0.3933·cy + 0.00058116·cy²" in §2 should not be
quoted.** The defensible statement is the probe's: 1.958 s/cy between the clean points, against
August's 0.673 at a smaller book.

**CORRECTION 2 — the memory error is 19.4x, not the 15.8x I estimated**, and my "~2,300
customer-years" was too generous. Measured 4.340 MB/cy against a published 0.224. On the probe's own
25%-of-guest share the ceiling is **1,312.3 customer-years** against a published 38,275 — a factor
of **29.2**. The §4 finding is right in direction and understated in size.

**CORRECTION 3 — my §5 claim that "1,200 still stands on nothing" is now FALSE, and this is the
result.** The probe's recommendation is `binding_bound: "memory"`, `binding_bound_is_evidence:
true`, `supported_customer_years: 1312.3`. Across the whole interval menu it was given — 90 minutes,
24 hours, one week, a factor of **112** — the supported ceiling moves only **1,194.6 → 1,312.3, or
9.9%**. Time binds at 90 minutes; memory binds at both longer intervals.

So **1,200 sits inside the entire admissible band, and is defended by measurement for the first
time — by measurement arriving at it, not by anyone having chosen it well.** Not moved: the band is
±10%, the 2026-08-29 allocation fix means a wrong value costs precision rather than coverage, and
moving to 1,312 spends the last of the memory headroom on a box with 107 lifetime OOM kills.

And the interval — four weeks of treating the director's choice as the thing standing between us
and a bigger book — turns out to move the answer by a tenth. **That was reasoning about the wrong
leg**, and nothing before this measurement could have told us.

## The one that closes the item

At budget 3,400 the campaign **refused nothing**: 500 funnel wins, 500 booked. So the campaign's
entire demand is **3,135.6 customer-years**, and the probe says it plainly — *"a ceiling above it
buys no accounts at all."*

The smallest leg of `what_would_settle_the_sign` needs **3,163.9**.

**The world tops out about 28 customer-years short of the book the thesis needs, and this box stops
at 1,312.3 long before that.** Compared on the page's own terms — the same comparison
`can_a_book_that_size_be_built` already makes against the 1,200 — the answer to "can a book that
size be built" is NO on two independent legs, one of them not an engineering limit at all.

That is the measured *"this world cannot reach it"* the drawn item named as a complete answer. It
is complete.

## My filed prediction, scored

> *"the marginal cost is ≈0.67s per customer-year on a ≈215s fixed component … I predict wall clock
> will not bound it either and that 1,200 will turn out to be bounded by nothing."*

Wrong on every clause. The marginal is 2.9x what I said, there is no positive fixed component,
wall clock binds at 90-minute cadences, and 1,200 is bounded by memory at 1.09x slack. The item
offered me an out — *"if the curve is stale my prediction is probably wrong"* — and the curve was
not stale in the way I meant: its **slope at a given book size is roughly unchanged since August**
(§3 stands: 0.767 fitted vs 0.673 measured). What I got wrong was assuming a slope measured over
796–1,200 customer-years describes 3,000, on a run whose cost per customer-year rises with the book.

## Still owed, revised

1. ~~The in-flight probe's report~~ — landed with this addendum.
2. **Two live constants both declare themselves the publish cadence and differ by 112x.**
   `publish_freshness.PUBLISH_CADENCE_SECONDS = 604800` (the director's, stated 2026-09-04, and the
   module calls itself "the SINGLE SOURCE OF TRUTH") against
   `suite_duration_watch.PUBLISH_CADENCE_SECONDS = 5400`, which is what stamps
   `publish_gate_duration.jsonl` and therefore what this probe falls back to when no interval is
   passed. Every reading the probe produced before today carried the 5,400 one. A repo defect, not
   a director question, and the reason §5's original conclusion was reachable at all.
3. **Re-rule `settled_book_ceiling_customer_years` against measured whole-run RSS**, and delete its
   hard-coded `what_it_does_not_bound` string — it pins "1,200", "slack by 4.5x" and "Memory is not
   what caps this book", all three now refuted, inside the function that computes the number they
   describe. Until that lands, `site/data/value_arms.json` keeps publishing 38,275 and the sentence
   that goes with it. **This is what keeps the finding BLOCKING.**
4. One repeat of the 1,200 point on a genuinely idle box, to settle §3's open question — the run's
   fixed cost is ~900s heavier than August's and I still cannot attribute it.
