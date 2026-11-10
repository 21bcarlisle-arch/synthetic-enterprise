# The learning loop on how we work: a failure changes practice, and the change is measured (2026-11-10)

*Delivery seat (worker tick), 10 Nov 2026, for
`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_FAILURE_FEEDS_A_LEARNING_LOOP_THAT_CHANGES_HOW_WE_WORK_2026-11-10.md`.
The design is the machine's, under his 30 Oct steer. This page says what the loop is, where each part
lives, and what was changed on the first worked case. The insights themselves live in
`docs/institutional/ways_of_working.md`.*

## 1. What it is, said before anything is counted

The product already has a loop: a defect becomes a named class, a test, a mutation check and a gate row
(`build.learning` on the map, `background/finding_classes.py`). That loop asks **why the code was wrong**.

This loop asks **why the way we worked let it happen**. Its input is a failure of the process, not of the
code. Its output is a change to practice, with a prediction of what the change will improve. A change that
does not improve its measure is retired.

## 2. The inputs: what counts as a failure

Six kinds, each already visible somewhere, so none needs a new recorder to be seen:

| Failure | Where it is already recorded |
|---|---|
| A graded prediction outside its filed range | the finding's "Held?" table and the grading commit |
| A regression: a fix that moved a count the wrong way | the grade after the fix |
| A class that escaped to a cold read | the cold-read finding (`SEAT_FINDING_THE_*_COLD_READ_*`) |
| A stall | the repeating-alarm findings |
| A refused publish | `docs/observability/.post_publish_reader_reds.json`, `HEAD_RED_REGISTER.md` |
| A fix that had to be redone | a "Correction, beside the claim" section, or a second fix to the same row |

## 3. The questions, asked of the process

For each failure, three questions, in order:

1. **Why was the prediction wrong?** Name the model of the area that produced it, and where it differed
   from what was there.
2. **Why did no gate see it?** If a gate could have, that is a product-loop item (a new class). If none
   could, say why not.
3. **Why was the fix made before the area was understood?** Was there a map of the area, and was it read?

The answers are the material for an insight. One failure rarely carries an insight; a repeated failure
in one area does.

## 4. Where an insight lives, and what it carries

One file, beside the reading log: `docs/institutional/ways_of_working.md`. The reading log records what
**outside** sources taught us about building; this file records what **our own failures** taught us.
It is not a second register of failures; the failures stay where §2 says they are, and are cited.

Each insight carries the five facets' insight fields (`docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §7):
the claim; its status (`hypothesis`, `held`, `refuted`, `retired`); what it rests on (the failures, cited);
the practice change; the measure and the prediction filed for it; and a review date. A refuted or retired
insight keeps its row.

It sits on the map's `build.learning` concept, the "Building it" side.

## 5. A change to practice, and how it is tested

The change has to be one of: a gate, a rule in the draw, a step in the grade chain, or a stop condition.
A paragraph of advice is not a change. Each change carries:

- **its measure**, chosen so that the change could fail to move it;
- **a prediction**, filed with the change, before it has run;
- **a review date**, at which the insight is kept, adjusted or retired on the measure.

A change that never fires is checked like any guard here: first show it CAN fire (§7's replay), then ask
whether it improves anything.

## 6. The loop's health: four measures

Chosen because each is countable from records we already keep, and each can move the wrong way:

1. **Prediction hit rate**, per area, over a rolling seven days: graded predictions held / graded.
2. **Escapes per cold read**: new error classes each cold read finds. If it is not falling, the
   correctness stretch is not converging.
3. **Regressions per fix**: grades where a fix moved its target the wrong way.
4. **Repeat failures**: the same insight's trigger firing again after its change landed.

Where they show: in the draw, so they steer the next draw (§7), and on the "Building it" side once the
published feed exists (§9).

## 7. The first worked case: level direct debit

Every graded prediction in the two level-DD findings, 8 to 10 Nov, was counted: 80 graded, 34
missed. None missed because we misread the domain. Eighteen missed because our model of our own code
was wrong, and eight because the reader measuring it was. The miss rate did not fall over the three
days. The full table and the three process questions are insight W1 in `ways_of_working.md`.

**The trigger, set from this case:** three graded predictions in one area, within seven days, that
missed because our model of our own code or of our reader was wrong. Misses for other causes (an
unattributable multi-change book, a domain fact) do not count towards it, because a map would not
have prevented them. Three, not one, so that a single miss stays the next fix's business.

**The change:** a stop condition. Fixes in the area stop, and the next item is the area's map: its
states, and the code and every reader that decides each, traced on a real household. It is applied
by hand this time, as the next step of the BLOCKING level-DD finding, so the existing blocking rung
draws it first in its lane.

**The prediction:** W1's. Over the next 20 graded level-DD predictions, at most 3 misses for those
causes, against 26 of 80 before; reported beside the ranges' widths.

A second insight, W2 (a book carrying several changes grades none of them), is filed as a hypothesis
with no change yet, because W1's map may remove its cause.

## 8. Concerns, with ideas

- **Cost.** Each insight is cheap; the risk is the recorder. The rule here is that no failure is
  re-recorded: §2's homes are cited, not copied.
- **Noise.** One failure is not a pattern. The trigger in §7 needs three in one area in seven days, so
  a single miss never mints an insight by itself.
- **Overlap.** The product loop owns "why was the code wrong". This loop owns "why did we work that
  way". When an answer is "a gate could have caught it", it goes to the product loop, not here.
- **The loop grading itself.** The measures are diagnostics, never targets (R12). A change is kept
  because the failures it was aimed at stop recurring, not because a hit rate rose: a hit rate can be
  raised by filing wider ranges. So the hit rate is always reported with the ranges' widths beside it.

## 9. Not built yet

- The published side: the "Building it" part reads the reading log through `tools/reading_log_feed.py`;
  the same feed should read this file. Minted as the next step.
- The draw rule as code: today the rule in §7 is applied by hand through the existing BLOCKING-finding
  rung. If the trigger fires a second time on another area, it is built into the draw, reading graded
  predictions from a commit trailer.
