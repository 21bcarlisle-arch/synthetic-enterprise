**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A close that says "yes, we'll do it" is checked against done, and a short Monday note says what involved me (2026-10-28)

**Type:** STEER, through the advisor channel. The director's words, from chat on Wed 28 Oct:

- 06:39 GMT: "why are actions for me not getting flagged better and reminded?"
- 06:44 GMT, on the advisor's three recommendations (the advisor opens every chat with what is waiting on him; closes are checked against done; a weekly Monday note): "Do it. And give me paste for main chat to tell it what we did"

## What went wrong (the advisor's reading; check it)

1. **Everything waits for him to pull it.** His queue is `for_the_director` plus a panel deep in How it's built. Phone alerts are mothballed by his choice. The advisor only looks when he messages it, and only when the topic comes up.
2. **The noise fix overcorrected.** On 26 Oct, 13 rows were open and 9 did not need him. Since then only G5 rows are shown as waiting. That fixed the noise, but every other row is now "closed on the seat's own recommendation", and nothing is ever said to him about it.
3. **A close is never checked against done.** `reading-reviewer-trial-your-08-56-yes` was closed on 26 Oct as "the trial as proposed". By 28 Oct nothing ran it (see `DIRECTOR_RULING_GO_ON_THE_TWO_READER_REVIEW_AND_START_IT_NOW_2026-10-28.md`). This is the no-caller class applied to decisions instead of code.

The advisor has taken the first fix on its own side: every advisor chat now opens by reading `for_the_director`, and anything overdue under item 1 below, and states in one line what is waiting on him, or that nothing is. The other two are the machine's.

## 1. A close that commits to action carries a due date and is checked

When a `for_the_director` row, a concern or a staged item is closed with a commitment ("closed on the seat's recommendation: do X", "ruled: do Y"), the close names what done will look like and a date. If nothing has landed that meets it by the date, the item comes back as **overdue**, visibly. It goes on the waiting list as the machine's own debt, not his, and into the Monday note. It does not need a new store if an existing one can carry it. You choose the shape.

Prove it can fire on the real case: the 26 Oct reader close would have come back overdue.

## 2. A short Monday note, written for him

Every Monday, after the weekly run, write one note in plain words that he can read in two minutes:
- **What he decided this week,** and whether each one has landed.
- **What is waiting on him,** with your recommendation for each, so "yes" or "go" answers it.
- **What was closed on your own recommendation,** one line each, so nothing he would have wanted to see is closed silently.
- **What is overdue,** under item 1.

Put it where the advisor reads it at the start of a chat, and say in the stretch log where that is. Do not add phone alerts. If a section is empty, say "none". A short note beats a complete one.

## Not wanted

- No new gate or ceremony on his path.
- No return of the noisy list. Items that do not need him stay off the waiting list. They are simply visible in the note.

## Risk

Touches: `background/director_concerns.py` or wherever closes are recorded, and the Monday step (`background/weekly_rhythm.py`).
Blast radius: internal records and one note. Nothing public.
Probable failure mode: the overdue check keyed to today's rows, so it goes quiet when rows change shape. Key it to the property (a commitment with a date and no landing), and prove it on the reader case.
Proportionality: reversible and narrow — just do it.

— Director steer, 28 Oct 2026, his words above; the diagnosis and drafting are the advisor's.
