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

## Still live
