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

## Done

Done by the delivery seat on 19 Oct, 17:30Z. The memory condition was measured the cheap way: two
founders-only points, 100 and 200 homes, run one after the other through `launch_long_job` with
the reaper untouched. The result is graded in
`docs/staging/records/SEAT_PREREG_WHAT_400_FOUNDER_HOUSEHOLDS_COST_IN_MEMORY_AND_TIME_MEASURED_ON_SMALL_BOOKS_2026-10-19.md`.

**It fits.** At 400 homes the run uses about 4,180 MB with today's budget, or about 5,350–5,540 MB
with the budget raised to keep the campaign's room. The allowance is 6,008 MB.

**The switch is not made yet**, for a reason the ruling does not cover. 400 homes are 697 supply
points, and they commit 6,603 customer-years. That is more than the whole 5,000 settlement
budget, so the campaign would be admitted no win in any year. The budget question is raised to
him as `your-400-household-founder-ruling-fits-in` in `for_the_director`. It recommends households
with the budget raised to about 7,800, which is the logic of his 9 Oct approval. The holding
position until he rules is 400 supply points, unchanged.

**Owed when he answers:** `FOUNDER_BOOK.yaml` with the his-words trailer, the world claims re-run,
the census before and after on seed 20260724, and the EP17 held draw. The household-counting
mechanism they need is handed off as
`the-founder-book-can-count-households-behind-its-yaml-default-unchanged`, so his "yes" is one
commit. The stretch-log entry is filed.
