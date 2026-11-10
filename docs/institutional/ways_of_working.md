# Ways of working: what our own failures taught us about how we work

One entry per insight. The reading log (`reading_log.md`, beside this file) records what **outside**
sources taught us about building. This file records what **our own failures** taught us. The failures
are not copied here; each insight cites where they are already recorded. The design, the triggers and
the measures are in `docs/design/THE_LEARNING_LOOP_ON_HOW_WE_WORK.md`.

Set up on the director's 10 Nov steer
(`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_FAILURE_FEEDS_A_LEARNING_LOOP_THAT_CHANGES_HOW_WE_WORK_2026-11-10.md`):
"I want a learning loop that drives improvement. These are then ways of working insights."

**Status:** `hypothesis` (filed, change not yet measured) · `held` (the measure moved as predicted) ·
`refuted` (it did not) · `retired` (it changed nothing, or its change was taken out). A refuted or
retired insight keeps its entry.

**Every insight carries a change to practice** (a gate, a rule in the draw, a step in the grade chain,
or a stop condition), a measure the change could fail to move, a prediction filed with the change, and
a review date. An insight with no change is a hypothesis with a review date, and it is retired if the
date passes with nothing changed.

---

## W1. When our predictions in one area keep missing, the area's map is wrong, and the next fix is not the cure (10 Nov 2026)

**Status:** hypothesis. **Area of the first case:** level direct debit (lane D_billing_metering).
**Review by:** 24 Nov 2026.

**The claim.** Repeated prediction misses in one area say our model of that area is wrong. Fixing the
next defect on the same model produces the next miss. The cheaper move is to map the area first: its
states, and which code and which reader decide each one.

**What it rests on.** A census of every graded prediction in the two level-DD findings and their
commits, 8 to 10 Nov (`SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_..._2026-11-07.md`,
`WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_ON_THE_NEXT_INSTALMENT_..._2026-11-09.md`):

| | Count |
|---|---|
| Graded predictions (each table row counted once) | 80, plus 5 void |
| Held | 45 |
| Missed (33 fell, 1 held its count on the wrong mechanism) | 34 |
| ... because our model of **our own code** was wrong | 18 (three of them refuted by reading the code, before any run) |
| ... because the **reader** measuring it was wrong or narrower than the defect | 8 |
| ... because the book carried several changes and one moved another's count | 4 |
| ... other or unattributed | 4 |
| ... because we misread what a real level direct debit does | **0** |

Misses by day graded: 5 of 10 on 8 Nov, 18 of 47 on 9 Nov, 11 of 23 on 10 Nov. The rate did not
fall as the work went on. One fix took the overdue rows from 151 to 614 (`f5b5a1b5b8`).

The class split is a census agent's reading of the documents; five rows are ambiguous between two
classes, and the totals above put each in its first-named class.

**The three process questions, answered.**
1. *Why were the predictions wrong?* Not the domain: the knowledge page held. The model of our own
   code was wrong: the world and the page ran two schedules, the cure predicate was cumulative, the
   leaving predicate misread accounts still paying level, an opening cached a `None`. Each was found
   only when a prediction fell, one at a time.
2. *Why did no gate see it?* The gates did see it: the domain-invariant rows refused every book. They
   say **that** a level account's page disagrees with its desk, not **which of four readers** (world
   schedule, desk, page, invariant row) holds the wrong idea of what a level account owes. Eight
   misses were the invariant reader itself.
3. *Why was each fix made before the area was understood?* There was no map of the area to read.
   Each fix was drawn from the last miss, and each miss was explained in the finding's newest section.
   Two findings grew to 173 KB of time-ordered sections, which no fix author reads end to end.

**The change to practice: a stop condition.** *Three graded predictions in one area, within seven
days, that missed because our model of our own code or of our reader was wrong, stop fixes in that
area. The next item in the area is its map:* one page listing the states a thing in the area can be
in, and for each state the code that decides it and every reader that reads it, each traced on one
real household. Every prediction filed in the area afterwards names the state it is about.

Applied by hand this first time, through the BLOCKING finding's own next step: the map is the next
level-DD item, ahead of any further fix (the finding's section of 10 Nov, "The stop condition fired").
It draws first in its lane through the existing blocking rung; no new draw code. If the trigger fires
on a second area, it is built into the draw (design §9).

**Measure and prediction (filed now, before the map exists).** Over the next 20 graded level-DD
predictions after the map lands: misses whose cause is our model of the code or the reader fall from
26 of 80 (32.5%) to **at most 3 of 20**. Reported with the median width of the filed ranges before and
after, because wider ranges would raise the hit rate without anyone understanding more.
**Refuted if** 6 or more of the 20 miss for those causes, or if the ranges widen by more than half.

---

## W2. A book carrying several changes in one area cannot grade any of them (10 Nov 2026)

**Status:** hypothesis, no change yet. **Review by:** 24 Nov 2026.

**The claim.** The rule already exists ("when a result moves and more than one thing changed, you
cannot attribute it", CLAUDE.md). It was broken anyway, because a book takes about two hours and the
fixes arrived faster than that, so books carried two to four untested changes each.

**What it rests on.** The 78f82e4242 book carried four changes. Its PAGE_BALANCE total held "only by
accident" while both its legs missed (`7f69f78825`); four misses in W1's census are this shape.

**What it might change.** The ledger replay is cheap and was used well (`0f9ebbad56`: 194 to 0 as
predicted). A grade-chain step would grade each change's prediction on a replay of the previous book
before the next book runs, and let the book grade only the combined count. Not adopted yet: W1's map
may remove most of the reason fixes arrive faster than books. Retired on 24 Nov if W1 holds and no
unattributable miss recurs.
