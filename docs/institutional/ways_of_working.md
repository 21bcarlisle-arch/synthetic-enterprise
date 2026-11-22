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

**Status:** refuted on its measure (16 Nov 2026, see "Measured" under the prediction below). The stop
condition stays in force. **Area of the first case:** level direct debit (lane D_billing_metering).
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

**Measured (16 Nov 2026): refuted, at exactly the line.** Counted from the function-by-function map
(`LEVEL_DD_AREA_MAP_2026-11-11.md`, 18285bfa11, 11 Nov 12:29Z), the first 20 graded level-DD
predictions are 72c936d313 (7), 3159a16f2c (7), b2f8e23fc0 (3) and f5d1203024 (3). **6 of 20 missed
for code or reader** (Wilson 95%: 15% to 52%, against 26 of 80 before). Every one was filed after
that map: 72c936d313's were pre-registered at 22:24 GMT on 11 Nov, and the predictions 3159a16f2c graded
are the map's own s.7, which landed in 72c936d313. Counted from the first map (a454d03fcc, 10 Nov),
the measure was already refuted: e58699ec9c read 4 of 14, as 18285bfa11 recorded. That record was only
in a commit message until now. The ranges did not widen: the post-map trailer widths are 0, 0, 0.86 and
1.2, against 2.0 on the 10 Nov pre-map grades. **The split moved, which the total hides:** code misses
were 1 of 20 (5%; 95%: 1% to 24%), against 18 of 80 before. Reader misses were 5 of 20 (25%; 95%: 11%
to 47%), against 8 of 80. The map traced the code, and none of its sections traced the readers. At 20
the intervals overlap, so this split is suggestive, not established. What it suggests: the next
level-DD map traces each reader against the states before a fix's prediction is filed, and the 20 that
follow it are counted again on this same line. Found by
`SEAT_FINDING_W1S_LEVEL_DD_MEASURE_READS_6_OF_20_AFTER_THE_MAP_WHICH_IS_ITS_REFUTATION_LINE_2026-11-14.md`.

**The named cases, each "the process let it", not "the code was wrong" (delivery seat, 10 Nov).**
INV_OVERDUE on the 78f82e4242 book, filed at most 10, read 60: the row's reading of a leaver was never traced
before the forecast. PAGE_BALANCE left-level steps, filed "at most 113, the cap can only lower it", read 135: a
"can only" argued from one function, not from the states a left-level account can be in. The fix that took
overdue rows from 151 to 614 (`f5b5a1b5b8`): drawn from the last miss with no map to read. Outside level DD,
class L's P3 (the desk's write-off), filed 17 to 2, read 3: the filter counted one account's collections
differently from the trace beside it, a reader miss. Every one is a model of our own code or of our reader
that was never laid against the states first. The stop condition is the answer to all four; the fourth says
the cause is not peculiar to level DD, which is why the measures below are per area.

**Where the draw reads it (10 Nov).** The seat's brief now carries the loop's measures
(`background/learning_loop.py`, `learning_loop` in `delivery_seat.build_brief`), printed above the JSON on
every orientation: per area, the hit rate with the median range width, the code-or-reader misses and
`STOP` when they reach three in seven days; regressions per fix; escapes per cold read. They are read from
two trailers on origin, so a grade is recorded by the commit that grades it and nowhere else:
`Graded: <area> held=<n> missed=<n> code=<n> reader=<n> regressed=<n> width=<x>` and
`Cold-read: <surface> new-classes=<n>`. A trailer that does not parse is printed as unparsed, never dropped.
*Prediction, filed before any trailer exists:* by 24 Nov at least two areas carry `Graded:` trailers, and the
first time any area other than level DD reaches `STOP`, its map is drawn before its next fix. **Refuted if** by
24 Nov no commit carries the trailer (then the measures are a page nobody feeds, and this change is retired),
or an area shows `STOP` and the next landing in it is another fix.

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

## W3. "Nothing is waiting on you" was said from a stale read (14 Nov 2026)

**Status:** hypothesis, change landed with it. **Review by:** 14 Dec 2026.

**The claim.** A claim about what is waiting on the director is only as fresh as the read behind it.
At 05:53 on 14 Nov the advisor told him "Nothing is waiting on you" while `for_the_director` row
`the-off-box-dead-man-misses-stops` had been open since the evening before. Its last full read of
the rows was 18:51 the day before; at 05:53 it scanned commit titles, and the title that raised the
row read as a finding. He asked: "Why did you miss this decsion for me? How do we fix that ?" A
second cause: the question was one the advisor could have answered, because its own cloud stall
check was recorded nowhere the machine reads.

**What it rests on.** `docs/staging/advisor/done/DIRECTOR_STEER_A_QUESTION_FOR_THE_DIRECTOR_MUST_BE_IMPOSSIBLE_TO_MISS_2026-11-14.md`.

**The change.** Three legs, one each. The advisor reads `for_the_director` from origin in the same
turn before saying what is or is not waiting (the advisor's own practice). A commit that opens or
reopens a row must start its title with `[FOR-THE-DIRECTOR]` and name the id; the commit-msg hook
refuses one that does not (`tools/director_document_gate.py`), and the seat's direction commit builds
the marked title itself (`director_concerns.marked_title`). Before raising, the seat checks whether
an advisor-run control already answers it (`docs/operations/MAINTENANCE.md` lists the cloud check);
if one could, the question goes to the advisor as a staged note first.

**The measure.** Director questions the advisor missed: open rows on origin at the moment the
advisor said nothing was waiting. Prediction: zero by the review date. One miss refutes it.

## W4. An alarm that cannot change anything is cost, not safety (18 Nov 2026)

**Status:** hypothesis, change landed. **Review by:** 18 Dec 2026.

**The claim.** The priority-zero publish-wedge refill was re-asked 59 times across 17-18 Nov, about one
commit cycle each, and repaired nothing. Every re-ask found the same thing: the refused book's cure
was waiting on one named file, behind a watcher that was already armed on it. An alarm whose cure is
already in hand cannot change what happens, so each firing is a cost with no safety bought.

**What it rests on.** `docs/staging/advisor/done/DIRECTOR_RULING_QUIET_THE_WEDGE_REFILL_AND_ALARM_TUNING_IS_YOURS_TO_DECIDE_2026-11-18.md`
and `for_the_director` row `the-priority-zero-publish-wedge-refill-fires` (answered yes).

**The change.** While the owed book waits behind an armed, declared watcher on a named file, the refill
names the file and stays quiet. It fires at once if the watcher is gone, if the file appears and no book
follows within 1 hour, or if the episode passes 72 hours. Those three legs keep a real stall loud. Tuning
the machine's own alarms like this is the machine's call, unless it changes something he ruled.
Commitment: `the-wedge-refill-names-its-wait-and-stays-quiet`, due 25 Nov.

*Built 18 Nov.* A watcher declares its systemd unit and the absolute file it awaits
(`python3 -m background.declared_wait --declare --unit <unit> --awaits <path> --why ...`, refused
unless the unit is active). RUNG 1 asks `supervisor._publish_gate_wedge_draw`, which logs the file
and stays quiet only while the episode's newest failure is `domain_invariant_refused` and a declared
wait is armed. The record outlives the unit on purpose: flag1's watcher exited 34 s after its file
appeared, so a declaration held in the unit would have read "watcher gone" and fired an hour early.
Printed at the 17-18 Nov record before the test: of the five re-asks the row names, 02:12, 04:32 and
05:42 go quiet; 22:20 still fires (flag1 was armed at 02:08); from 07:57 it fires again (file at
06:57, the book reached origin at 10:45). So the change would have saved 3 of those 5, not all of
them, and the 1 h leg is what kept the 3.8 h gap after the file loud. Control:
`tests/background/test_the_wedge_refill_names_its_wait_and_stays_quiet.py`.

**The measure.** Re-asks of a priority-zero rung whose cure waits on a named file behind a live
watcher. Prediction: zero once the change lands, with the refill still firing in its control while a
watcher is armed. One silent stall past 72 hours refutes the legs.

## W5. The nonsense was found by the director, or late, not by the machine asking "does this make sense?" (22 Nov 2026)

**Status:** hypothesis, measure started. **Review by:** 22 Dec 2026.

**The claim.** The machine gathers a good first layer of knowledge. It does not go on to ask how the
thing works, or whether an answer is plausible, before using it. In his words (22 Nov 07:51 GMT): "we
lack a little curiosity and desire to learn. To figure out more deeply how stuff works and if
answers make sense." The case that prompted it: on 21 Nov a practitioner question about call handle
time reached him before Citizens Advice's supplier data had been searched for it, and before anyone
had asked which decision needed the answer. None did.

**What it rests on.** `docs/staging/advisor/done/DIRECTOR_RULING_HOLDOUTS_YES_AND_CALL_TIMES_ARE_PUBLISHED_SO_ASK_WHY_THEY_ARE_NEEDED_2026-11-22.md`
and `docs/staging/advisor/done/DIRECTOR_STEER_BE_CURIOUS_FIND_OUT_HOW_THINGS_REALLY_WORK_AND_WHETHER_ANSWERS_MAKE_SENSE_2026-11-22.md`.

**The change, first leg (landed with this entry).** A knowledge GAP about contact, service or
complaints must clear a standard search list before it becomes a question for the director. The
question must also name the current decision that needs the answer. A question with no decision
behind it is closed as "not needed yet", with its reopen condition. The list and the rule are in
`docs/market_research/contact_centre_staffing_cost_and_call_wait_gb_energy_2026-11-21.md` §5a. The
other legs the steer offers are weighed in the 23 Nov weekly review, with their cost: a second view
before a number is used, mechanism on every rate, surprise as a work item, and a practitioner's
cold read of knowledge pages.

**The measure.** It counts **nonsense found by the director or the advisor before the machine found
it**: an implausible number, a missed obvious source, or a question he could have answered from
public data. Each case is one row below, dated when he or the advisor caught it. The baseline is the
cases the steer names. They are not all dated, so they set no rate. Prediction: no more than 2 new
rows in the four weeks to 22 Dec. More than 2 refutes the first leg as enough.

| Caught | By | What | Class |
|---|---|---|---|
| 2026-11-22 | director | Call handle time put to him before Citizens Advice's data was searched, with no decision needing it | missed obvious source |
| before 2026-11-22 | director | Value test "+£5k" published for weeks as a book total, never restated as about £5 per household-year | not restated per unit |
| before 2026-11-22 | check, late | 72% of homes drawn as POOR insulation, against about 15% true | implausible number |
| 2026-11-21 | director | Bill shock framed as one number; he supplied the structure (two families, three SVT moments, payment method) | no mechanism |
| before 2026-11-22 | director | Renewal belief with AUC 0.52 produced a margin gain the site led with | implausible number |
| 2026-11-14 | director | "Nothing is waiting on you" from a stale read (W3) | missed obvious source |

*The rows marked "before 2026-11-22" carry the steer's account. Their exact dates are not yet traced
to the commits, so they are the baseline and not graded rows. The prediction counts only rows dated
after 22 Nov.*
