**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] The founder number is 400 households, provided it fits in memory (2026-10-19)

**Type:** RULING, through the advisor channel. It answers the question your 17 Oct finding raised with `director_concerns` (`WORKER_FINDING_THE_OPENING_BOOK_WAS_ONE_PERCENT_DUAL_FUEL_AND_NOW_BEARS_THE_PUBLISHED_SPLIT_2026-10-17`, "the founder number now has two readings"). The director's words, from chat on Mon 19 Oct:

- 16:37 BST: "Households, as long as it doesn't create a memory problem"

## What it means

- **The 400 counts households.** It counts homes: a dual-fuel home is one founder with two supply points. It is not 400 supply points. Expect about 700 supply points. The ceiling (500) and the prospect cap (400) keep their numbers, and the ceiling is read in households too.
- **The condition is his, and it binds.** Before the production shape changes, measure peak memory and wall time for a full production run at 400 households. Use the one memory budget for the box (R7), with landings reserving first, and keep the reaper as it is ("Don't ask me to disable the reaper; it's the safety net"). Do it the cheap way: measure on small books and scale up, per R8. Avoid a blind full run.
  - **If it fits** with the budget's headroom: switch the production shape to 400 households and record it in `docs/design/FOUNDER_BOOK.yaml`. Use the trailer `Director-doc: his-words -- founders are households, director 19 Oct 16:37`, and quote the line above.
  - **If it does not fit:** don't switch. Report the largest household count that does fit, with its measurement, and what would close the gap (for example streaming per R8, or index-once per R6). Bring that back as a proposal. Don't change the number on your own.
- **The world claims re-run on the change**, as yesterday's mechanism requires (`tools/world_claims.py`). Record the before and after on the same seed: homes, supply points, dual share, and the per-household figures that move.
- **EP17.** This is a deliberate change to the held draw. Record the new draw as the one now held, as was done on 17 Oct.

## Report

One stretch-log entry with:
- the memory and time measurement;
- which branch was taken;
- the census before and after;
- the published figures it moves.

— Director ruling, 19 Oct 2026, his words above; the drafting is the advisor's.
