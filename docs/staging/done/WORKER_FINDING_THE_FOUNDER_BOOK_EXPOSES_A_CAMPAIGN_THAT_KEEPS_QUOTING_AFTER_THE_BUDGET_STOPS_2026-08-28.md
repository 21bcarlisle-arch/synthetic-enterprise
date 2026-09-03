**Severity:** RECORDED (was BLOCKING; ruled and discharged) · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`A46_book_depth_is_a_curriculum_question` · **Ruled and landed 2026-08-28**

# The 80-founder book is built and NOT landed: it exposes a campaign that pays for quotes the budget can no longer convert

Director, 2026-08-28: *"take the 80 founders — that's my answer on P9."* The curriculum act is
recorded (`docs/design/FOUNDER_BOOK.yaml`) and the mechanism is built and unit-tested. **It is not
committed**, because running it turned four campaign tests red and the reason they are red is a
question, not a stale fixture.

## What the decision delivers

| | founders 13 (today) | founders 80 |
|---|---|---|
| opening book | 15 | **82** |
| campaign wins | 211 | **45** |
| end-of-window book | 226 | **127** |
| customer-years spent on founders | 130 | **800** of a 1,200 budget |
| accounts carrying 5+ renewals | 37 | **~80** (every founder is dated 2016 and carries ten) |

**The depth is delivered.** That was the point: three instruments — the ladder's 17 binary
decisions, the chase comparison, and A48's method skill on 12 decisions — all hit the same wall,
and ~80 accounts at nine or ten renewals apiece is a book a per-customer policy can compound on.

## Two corrections to the menu I priced

**The end book is 127, not the ~180 I told you.** My table said "80 founders → ~180 accounts". The
measured figure is 127. I had the founder cost right (800 customer-years of 1,200) and the growth
remainder wrong.

**And the mechanism line was wrong too.** The menu said *"Raise `accounts_held_at_start` from 18.
The parameter already exists and is already threaded through."* It is a derived argument
(`len(book)`), not a knob, and the opening book was 15 rather than 18 — 13 hand-authored founders
plus two trickle accounts. Building the parameter was the work; the costing assumed it away.

## What running it exposed, which I did not predict

**Quotes went UP while wins went DOWN.**

| | founders 13 | founders 80 |
|---|---|---|
| quotes the campaign paid for | 1,066 | **1,707** |
| wins booked | 211 | **45** |
| conversion | 20% | **2.6%** |

The customer-year budget is 1,200 (`net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET`). Founders
take 800 of it, so the campaign has 400 left, books its earliest and longest-tenured wins, and stops
converting — **but it keeps quoting, and every quote is booked as acquisition spend at £112.50.**

**The founder book did not cause this. It exposed it.** At 13 founders the budget never binds hard
enough for the gap between quoting and booking to be visible. Squeeze the remainder and the
behaviour surfaces: a supplier that goes on paying for leads after it has run out of the capacity to
serve them.

**Whether that is a defect or fidelity is a real question and I am not answering it here.** A real
supplier with no capacity stops marketing — but it also has notice periods, committed spend and
contracted channels, and "we kept paying for leads we could not take" is an ordinary commercial
failure rather than an impossible one. What is NOT defensible is that nothing currently reports it.

## Why the four red tests are not re-baselined

`tests/simulation/test_net_new_acquisition.py` pins `CAMPAIGN_QUOTES_INSIDE_WINDOW = 1066` and three
related spend assertions. Updating them to 1,707 would make the suite green and would be exactly
the move R12 forbids — a number changed to fit the run rather than the run understood. They stay
red and the founder book stays uncommitted until the quoting behaviour has a ruling.

## What is built and tested

- `docs/design/FOUNDER_BOOK.yaml` — the R13 curriculum artefact, director-attributed and versioned,
  with its own reversal (`founder_accounts: 13` restores the pre-decision book, and that reversal is
  tested rather than asserted).
- `simulation/live_population.founder_accounts()` / `founder_book()` / `_drawn_founders()` — reads
  the number, fails toward the roster and never toward zero, cannot shrink the hand-authored 13.
- Drawn founders take the existing founders' role — dated at the window start, claiming no premise —
  so PB2's subset verdict is untouched and its stated exclusion reason still holds word for word.
- `book_subset_verdict` now reports the WHOLE founder book (80) beside the hand-authored count (13).
  It reported 13 while excluding 80, against its own rule that "an exclusion nobody can count is an
  exclusion nobody can check".
- 14 tests. Four mutations proven red: founders drawn across the trickle's window instead of the
  start year, an unreadable curriculum file returning zero, the exclusion reverting to the roster
  count, and the file shrinking the roster.
- One mutation did **not** fire — swapping the founder draw onto the trickle's own seed — and it is
  an equivalence, not a gap: `iter_acquisition_events` builds a fresh generator per call and the two
  draws occupy disjoint year ranges. The property actually worth pinning was id collision, and it is
  pinned now.

## WORK THIS CREATES

1. **Rule on the quoting behaviour.** Either the campaign stops quoting when the budget can no
   longer convert, or it does not and the artefact says so with the number. Both are defensible;
   silence is not.
2. **Then land the founder book** and re-baseline the four tests against the ruled behaviour, in
   that order.
3. **Re-run everything downstream.** A different opening book is a different supplier: the A/B, the
   ladder, the method skill and every published figure move together, and comparisons across this
   boundary are comparisons of two books.
4. **My priced menu needs its corrections carried back** — the end-book figure and the mechanism
   claim — so the next reader of it is not misled the way I was.

## Where the work is

Held, not lost, and not in the shared tree: `docs/design/held/` carries the patch, the curriculum
file and the tests, with the restore commands and what blocks them. **It is out of the working tree
on purpose** — the gates read the whole tree, so leaving it in place would have made every lane's
commit red rather than only mine.

## SEAT NOTE 2026-08-28 — the 2.6% is a MIXED statistic, and a machine limit is inside the company's own belief

Added by the delivery seat after reading the module. Every claim below is
**observed-with-evidence in the code**, not re-measured from a run (R9) — no run was executed for
this note, and the 1,707/45 pair is taken from the finding above as reported.

1. **The refusal is not commercial.** `simulation/net_new_acquisition.py:603-606` refuses the win at
   `committed_cy + cost_cy > customer_year_budget` and sets `binding = "settlement_engine"`. The
   module's own note at `:641` says `1200.0` (`SETTLEMENT_CUSTOMER_YEAR_BUDGET`, `:429`) is
   *"THIS MACHINE's budget (60% of the 465 measured in AO12's scale probe), not a commercial
   limit."* So an unknown share of the wins that vanished between 211 and 45 were **won in the
   funnel and then refused a place on the book by the harness's own capacity** — they were not lost
   in the market.

2. **So "conversion fell to 2.6%" is a mixed statistic.** It divides quotes by BOOKED wins, and
   bookings are truncated by an engineering cap. It has to be split per class before anything is
   ruled: funnel wins, and funnel wins refused by the settlement budget. Only the first is about a
   supplier; reported together, the unobservable class reads as commercial behaviour.

3. **`by_year` cannot currently be split.** Its `wins` field is `won_this_year`, which counts BOOKED
   wins only (`:622`). The funnel's own verdict does survive in `spend[]["won"]`, so the split is
   recoverable from the returned dict — but it is on no row a reader sees, and `cy_exhausted_at`
   names only the FIRST refused prospect, never how many followed it. That, and not the quoting,
   is the thing that is genuinely unreported.

4. **The machine limit is inside the company's belief.** `wins_to_date += won_this_year` (`:617`)
   is what feeds `quote_budget_fn`, and `saas/growth_mandate.py:312-313` computes
   `expected_quotes_per_win` and `realised_win_rate` from exactly that pair. The company therefore
   plans next year's quote budget on a conversion rate that a harness capacity limit helped set.
   This is not the company being allowed to be wrong about the world — it is the harness reaching
   into the company's own books, and it is a wall question rather than a tuning one.

### What this changes about WORK item 1

The ruling asked for is *"either the campaign stops quoting when the budget can no longer convert,
or it does not and the artefact says so with the number."* On the evidence above that question is
malformed as posed: **the budget that stopped converting is not the company's**, so
*"a supplier that goes on paying for leads after it has run out of the capacity to serve them"* is
not yet shown to be what the run does.

**Recommendation, and the next thing I would do in this lane:** report the split FIRST — carry
`funnel_wins` and `wins_refused_by_settlement_budget` on every `by_year` row plus a campaign total —
then re-read the 1,707/45 pair against it, and only then rule. If most of the 166 missing wins are
engine-refused there is no commercial behaviour to rule on, and the founder book is being held
behind a measurement nobody has taken. Whether `realised_win_rate` should be computed on funnel wins
rather than booked wins is the separate wall question, and it outranks the quoting one.

**Not fixed here on purpose** (SELF_INTERRUPT_DISCIPLINE — queue, don't fix on sight): this note is a
disposition, not a change. The finding stays BLOCKING and stays in the staging root.

## RULING 2026-08-28 (delivery seat) — the campaign is RIGHT to keep quoting; the founder book LANDS

The seat note above said the question as posed was malformed and recommended reporting the split
before ruling. The split is now built (`funnel_wins` / `wins_refused_by_settlement_budget` on every
`by_year` row and in the campaign total), and `wins_to_date` now accumulates FUNNEL wins, so the
harness's capacity limit no longer reaches into the company's own believed conversion. Measured on
the live campaign with the 80-founder book and the sourced acquisition costs:

| year | quotes | funnel wins | booked | refused by the engine |
|---|---|---|---|---|
| 2016 | 135 | 24 | 24 | 0 |
| 2017 | 191 | 32 | 21 | 11 |
| 2018 | 239 | 43 | **0** | 43 |
| 2019 | 234 | 42 | **0** | 42 |
| 2020 | 232 | 44 | **0** | 44 |
| 2021 | 228 | 33 | **0** | 33 |
| 2022 | 178 | 30 | **0** | 30 |
| 2023 | 238 | 41 | **0** | 41 |
| 2024 | 238 | 53 | **0** | 53 |
| 2025 | 229 | 38 | **0** | 38 |
| **total** | **2,142** | **380** | **45** | **335** |

**Funnel conversion is 17.74%. Booked conversion is 2.10%.** The company converts at very nearly the
20% it believes; 335 of the 380 customers it won — 88% — were refused a place on the book by
`SETTLEMENT_CUSTOMER_YEAR_BUDGET`, which the module's own note calls *"THIS MACHINE's budget ... not
a commercial limit"*.

**So the ruling.** There is no commercial defect to rule on. The premise of the original finding —
*"a supplier that goes on paying for leads after it has run out of the capacity to serve them"* —
is **refuted**: the capacity that ran out is the harness's, the supplier never saw it, and a
supplier would not stop marketing because of a limit it cannot observe. The campaign keeps quoting
and that is correct. What was indefensible was that nothing reported it, and that is now fixed —
which is why the ruling could wait for the measurement instead of being guessed.

**My pre-registered inference was wrong and is kept here beside the result.** I wrote that the 2.6%
conversion showed a campaign paying for leads it could not convert. It showed a settlement engine
refusing wins the campaign had already made. Same number, different mechanism, opposite conclusion.

**The four red tests were red for a different reason again.** They pinned spend at invented prices.
R1 sourced the costs and they were re-baselined against the ruled behaviour, in that order, not to
make them green — `CAMPAIGN_SPEND_AT_SHIPPED_CONFIG` moved £135,285 -> £23,709 with the cause split
between the price change (78.0%) and the quote cutoff (4.4%).

### THE BIGGER FINDING THIS EXPOSES, and it outranks the one this document was opened for

**From 2018 onward the published book is not a commercial outcome at all.** The engine booked zero
of every year's wins. Every growth figure published for 2018-2025 is the settlement ceiling
expressed in customer-years, not the funnel's verdict, and no reader could tell — the ceiling is a
number in `net_new_acquisition.py`, and the book it produces looks exactly like a supplier that
stopped winning.

This is a blocker for R6. Acquisition spend cannot drive collateral demands through a book the
engine refuses to settle: the campaign spends £46,408 and books 45 accounts, so the mechanism the
CMA describes — growth weakening the balance sheet — has nothing to act through after 2017. **R6
needs this resolved first**, and the resolution is not a bigger budget for its own sake: it is that
the ceiling must stop being invisible in the published figures.

Recorded as its own item rather than fixed here (SELF_INTERRUPT_DISCIPLINE).

## THE RULING, 2026-08-28 — delivery seat, and it is NEITHER of the two options

**Landed with the founder book.** The ruling is in the code it rules on
(`net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET`) rather than only here, because a ruling a
reader of the module cannot find is a ruling that will be re-litigated.

**The question could not be answered as posed, and the reason is measured rather than argued.**
I ran it, one variable at a time, at the same seed:

| | founders 13 | founders 80 |
|---|---|---|
| quotes paid for | 1,066 | 2,089 |
| wins the FUNNEL gave | 200 | 380 |
| wins BOOKED | 200 | 45 |
| wins refused by THIS MACHINE | 0 | **335** |
| **funnel conversion** | **18.8%** | **18.2%** |

**There was no supplier marketing past its capacity.** The company converts at the same rate on a
book six times deeper; 335 of the 380 wins (88%) were won and then refused a place on the book by
an engineering ceiling that does not exist in the modelled world. The 2.6% was quotes over BOOKED
wins, and the seat note above was right that this mixes a commercial class with a harness one.

**So the director's reading is refuted on its first clause and delivered on its second.** His
direction was *"my reading, to act on unless the evidence says otherwise: it is a company defect —
the growth desk should stop paying for leads it has no capacity to serve — but the behaviour must
remain OBSERVABLE."* The evidence says otherwise on the defect: making the growth desk stop quoting
would have tuned the company to hide a machine limit, and would have put that limit into a
commercial decision. The observability clause stands verbatim and is what shipped.

**What WAS a defect is a wall breach, and it is fixed.** The refused wins were being fed back to
the company's own planner, so its `realised_win_rate` read 1.7% instead of 17.9% and its quote
budget went from 135 to 2,000: it bought 2,826 quotes (£62,812) to book 45 accounts. A supplier
responding rationally to a number the harness made up. It now plans on `funnel_wins` — what its own
funnel converted, which is the only thing it can actually know — and buys 2,089 (£46,408). **At 13
founders the fix changes nothing at all (1,066/200/200, byte-identical)**, which is what says it is
aimed at the artefact and not at the answer, and it means no currently-published figure moves
because of it.

### What shipped

- `funnel_wins` and `wins_refused_by_settlement_budget` on every `by_year` row and as campaign
  totals, with `funnel_wins == wins + refused` asserted on each row and against the spend ledger.
- The settlement note carries the COUNT of refused wins, not just the first prospect's id.
- `wins_to_date` feeds the planner the funnel's verdict, not the book's.
- Four controls: the split, its null control (nothing refused → zero, and no note), the wall test
  on a fixture where booked and funnel wins actually differ, and the 29-February class below.
- The four red tests re-baselined WITH the cause split and attributed in the header: +1,023 quotes
  from the deeper book (more opening capital), −737 from the wall fix.

### One thing the founder book exposed that nobody predicted

**A term starting 29 February crashed the whole run.** `d.replace(year=d.year - 1)` raises
`ValueError` on a leap day; the 80 founders are dated across 2016 and one landed on the 29th, so
`run_phase2b._company_eac_estimate` took the run down. Fixed as a class
(`simulation.customer_events.twelve_month_window_open`, 1 March, matching the convention
`fit_legacy_register` already had inlined) with a sweep over a whole leap cycle. Four other call
sites share the shape and are NOT fixed here — `customer_events` and `run_phase2b` were the two
that could reach a leap day in this run. **Queued, not fixed on sight.**

### What is NOT discharged and stays open

Items 3 and 4 of WORK THIS CREATES: everything downstream re-runs against a different supplier, and
the priced menu still needs its two corrections carried back. And the item another lane appended
above — that from 2018 the published book is the settlement ceiling rather than the funnel's
verdict — is now MEASURED (380 funnel wins, 45 booked) and reportable, but not resolved.

## Still live

## 2026-08-28, AFTER THE LANDING — the founders were charged for and never delivered

The ruling above is sound and stands. What none of it checked is whether the director's act
delivered the thing it was bought for, and it did not: **67 of the 80 founders never reached the
served book.**

**The two sides are different functions.** `_pre_growth_book` — what the campaign PLANS against —
read `founder_book(seed)`. `live_population` — what the company SERVES, bills and publishes —
rebuilt its opening book from the 13-account `CUSTOMERS` literal. So the campaign committed 800 of
its 1,200 customer-years to 80 founders, refused 335 of its own funnel wins to pay for them, and
then 67 of those founders existed nowhere a reader could see.

Measured at the run's own seed (20260724), one variable at a time:

| | founders 13 | founders 80, as landed | founders 80, fixed |
|---|---|---|---|
| campaign plans against | 15 | 82 | 82 |
| **published book** | **398** | **100** | **167** |
| founders in the published book | 13/13 | **13/80** | **80/80** |
| accounts with ≥5 renewals | 92 | 98 | **165** |

**As landed, the act bought to make the book deeper made it four times shallower** — 398 to 100 —
for six extra deep accounts. Fixed, it does what it was bought for: 92 → 165.

**Why the shipped tests all passed.** `test_the_opening_book_reaches_the_growth_plan` pins
`_pre_growth_book`, the planning side. Nothing pinned the served side. A count would not have
caught it either — 13 static + 2 trickle + 85 won = 100 looks like a book, and the campaign's own
wins made up the difference. The new control asserts the founders are present **by id**.

### What shipped with the fix

- `live_population` builds its opening book from `founder_book(seed)`; drawn founders are
  registered as supply points as the trickle and the wins already were.
- **The draw flag now gates founders in one place** (`founder_book`), so the planned and served
  books cannot disagree again. This restores the flag-off byte-identical guarantee the seam tests
  assert.
- `_gas_aq_kwh` extracted from `_gas_leg_for`: a drawn founder can BE a gas account (22 of 80
  were), unlike a campaign win, which is always won on electricity. Its record carried no
  `aq_kwh`, so the first one took `run_phase2b.TOTAL_GAS_AQ` down with the identical `KeyError`
  `net_new_acquisition.ELECTRICITY_ONLY` had already named. Fail-closed and skipped, never
  defaulted — the draw has headroom, so the director's number is still met without inventing an AQ.
- `live_premises` registers founders' dwellings from the SAME draw as the book (B12:
  `build_properties` raises `DwellingNotDrawn` otherwise). One draw, so the register cannot hold a
  founder the book lacks.
- Three seam controls had their SUBJECT split rather than their bounds widened: two draws now
  share the `SYN-` prefix, and the trickle's "≤15, not the 200-pool" guard would have been
  destroyed by raising it to swallow 80 founders.
- The 13-founder run is byte-identical across the whole fix (398 accounts, 92 deep), which is what
  says it is aimed at the artefact and not the answer.

### Still open, and item 3 above is now bigger

**Every published figure moves again**, and further than the landing implied — the book is 167,
not the 100 the tree published between these two commits and not the 127 the correction quoted.
The A/B, the ladder, the method skill and the site all need re-running against it.

**The priced menu's corrections are carried back** (item 4, discharged): the premise had already
expired — 92 accounts carried 5+ renewals before the act, not the 37 P9 was argued from, because
R1's sourced costs made quotes cheap enough for the campaign to win its own depth. The act is still
worth its place, but as an improvement on a working book rather than the rescue of a broken one.
