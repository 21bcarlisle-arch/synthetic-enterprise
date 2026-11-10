**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Every failure feeds a learning loop that changes how we work, not a report

**Type:** STEER, through the advisor channel. The director's words, from chat, Tue 10 Nov:

- 12:24 GMT: "When things fail, such as you highlight above, are we still capturing why and trying to prevent and improve ?"
- 12:36 GMT: "I don't know what a report changes. I want a learning loop that drives improvement. These are then ways of working insights."

## What prompted it

The advisor told him that product defects are handled well: a named class, a test written first, a mutation check, a gate row, and a prediction filed before each run. It also told him that failure is not learned from as a pattern. Three examples from origin:

- **Prediction misses are recorded one at a time, and nobody reads them together.** In the 78f82e4242 grade:
  - INV_OVERDUE_WITHIN_BALANCE was predicted 0-10 and read 60.
  - PAGE_BALANCE left-level was predicted at most 113 and read 135.
  - P5 was predicted at most 30 and read 49.
  - On 9 Nov a fix took the overdue rows from 151 to 614.

  Repeated misses in one area say the model of that area (level DD) is wrong. Today that triggers the next fix, not a step back.
- **No one tracks whether new classes per cold read are falling.** The ninth read found three. If the count is not falling, the stretch is not converging.
- **"Why did no gate catch this?" is not a standard step.** N22 and N23 escaped seven reads and every gate. The 11 Nov review asks it once.

## The intent

He does not want a report. He wants a **loop**, the same shape as the product's improvement loop, pointed at the way the machine works:

1. **Failure is the input.** That covers a prediction outside its filed range, a regression, a class escaping to a cold read, a stall, a refused publish, and a fix that had to be redone.
2. **Ask why the process let it happen, not only why the code was wrong.** Why was the prediction wrong? Why did no gate see it? Why was the fix made before the area was understood?
3. **The answer is a ways-of-working insight.** File it as **insight** on the "Building it" side of the taxonomy, with a trust grade, and with the failures it rests on cited. It sits beside the reading log and the control stack, and it is published like any other insight.
4. **The insight changes practice.** That means a gate, a rule in the draw, a step in the grade chain, or a stop condition, for example: "three misses in one area means map the area before the next fix". File a prediction of what the change will improve, then measure it.
5. **Keep it, adjust it or take it out on the measure.** An insight that changes nothing, or a change that does not improve its measure, is retired and recorded as such.

The loop's health is a small number of measures the machine chooses, not a document. Examples are the prediction hit rate, escapes per cold read, regressions per fix and repeat failures. They should be visible where the work is drawn, so they steer the next draw.

## Ownership

Under the 30 Oct steer ("raise concerns and the issue to solve with ideas. Let it really think about it and own the solution"), the design is the machine's. Specifically:

- Decide the triggers, where the insights live, how a change to practice is tested, and what retires one.
- Build on what exists rather than adding another register: the control stack, the reading log, the 11 Nov two-reader review, the declared-defects register and the decisions log.
- Raise concerns, such as cost, noise and overlap, with ideas.
- Start with the level-DD prediction misses as the first worked case, because the evidence is fresh.

The director will judge it by whether the same kind of failure stops recurring, not by what is written about it.

## Done

*Worker tick, 10 Nov 2026 ~19:00 GMT.* The loop is designed and its first case is worked, with its change to
practice live. Whether it works is judged as he said: by whether the same kind of failure stops recurring.

- **Design:** `docs/design/THE_LEARNING_LOOP_ON_HOW_WE_WORK.md`. The six failure inputs are cited where they are
  already recorded, not copied. Three process questions per failure. Insights live beside the reading log, in
  `docs/institutional/ways_of_working.md`, with status, what they rest on, a change, a measure, a prediction and a
  review date. Four health measures: prediction hit rate per area (reported with the ranges' widths, so a wider
  range cannot buy a better rate), escapes per cold read, regressions per fix, repeat failures.
- **First case, level DD (W1):** every graded prediction in the two level-DD findings was counted. 80 graded, 34
  missed: 18 because our model of our own code was wrong, 8 because the reader was, 4 because a book carried
  several changes, 0 because we misread the domain. The miss rate did not fall from 8 to 10 Nov.
- **The change, live:** a stop condition. Three misses in one area in seven days, from our model of the code or
  the reader, stop fixes in that area until the area's map exists. Applied to level DD in the BLOCKING finding's
  new last section, so the existing blocking rung draws the map first in its lane. No new draw code.
- **Prediction filed:** over the next 20 graded level-DD predictions, at most 3 misses for those causes (26 of 80
  before), with range widths reported. Refuted at 6 or more. Review 24 Nov.
- **W2**, a book carrying several changes grades none of them, is filed as a hypothesis with no change yet.

**Not done, and owed:** the published side (the Building it part should read `ways_of_working.md` through the
reading-log feed), and the draw rule as code, which is built if the trigger fires on a second area. Escapes per
cold read is named as a measure and not yet computed.

**Addendum, delivery seat, 10 Nov late.** The measures now show where the draw is made: `background/learning_loop.py`
reads `Graded:` and `Cold-read:` commit trailers on origin, and the orienting seat's brief prints per-area hit rate with
range widths, code-or-reader misses with `STOP` at three, regressions per fix and escapes per cold read, on every
orientation. W1 names the four cases the draw cited (INV_OVERDUE 10 to 60, PAGE_BALANCE 113 to 135, the 151 to 614
fix, class L's P3 2 to 3) and why the process let each through. The draw still refuses nothing; that is built if a
second area reaches `STOP`.
