**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

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

## Still live
