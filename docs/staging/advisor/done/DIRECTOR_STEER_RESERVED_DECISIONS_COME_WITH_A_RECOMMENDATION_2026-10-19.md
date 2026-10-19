**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A decision reserved to him still arrives with a considered recommendation (2026-10-19)

**Type:** STEER, standing, through the advisor channel. The director's words, from chat on Mon 19 Oct:

- 16:38 BST: "Ps. Even items that are reserved for me I'd prefer it to make a considered recommendation"

## What it means

When something reaches him because it is his (G5, G9, P11, C14, a curriculum value, a ruling), it arrives with these parts:
- **The question, in one line.**
- **A recommendation**, said plainly: "I recommend X". A neutral list of options doesn't meet this.
- **The evidence and reasoning**, with sources and numbers where they exist (K-rules).
- **The trade-off**: what X costs, and what the main alternative would buy instead.
- **The holding position until he rules**, and why it is the safe default. Work does not stop for it (P7, P8).
- **What would change the recommendation.**

**The 400 example (19 Oct).** The 17 Oct finding proposed holding 400 supply points as the safe default. That was a holding position, not a recommendation on the question itself. He ruled "Households, as long as it doesn't create a memory problem". The better shape would have recommended households or supply points on the evidence, as suppliers count customers, priced the memory and run-time cost, and named the holding position separately.

**Not changed.** What is reserved stays reserved, and the recommendation does not act on itself. It only tells him what the machine would do and why.

## Where this lands

- `docs/design/DIRECTOR_CANON.md`: add one line to G9, quoting the director's words above verbatim (canon "How this canon works", items 2–3, marked as his words of 19 Oct).
- `CLAUDE.md`: point to G9, without rewording it.
- The `director_concerns` / `for_the_director` row format: give it a required `recommendation` field. The staging watcher flags a row that lacks one. That is the mechanism. Make it mutation-proven, and keep it small.
- Open rows already waiting for him: add a recommendation to each in the next pass, and report how many.

— Director steer, 19 Oct 2026, his words above; the drafting is the advisor's.

## Done

Done by the delivery seat on 19 Oct, in the commit that moves this file. Each landing named above:
- **Canon G9** has one new line quoting his words of 19 Oct, 16:38 BST, verbatim and marked as his.
  It names the mechanism.
- **CLAUDE.md** points to G9 and does not reword it. The operating-model mirror is
  republished.
- **The row format.** `for_the_director` rows carry `recommendation`.
  `direction.concern_lacks_recommendation` asks an open row for a non-empty "I recommend X". A
  neutral list of options fails, and answered rows are not asked.
  - `director_concerns.raise_concern` and `--raise --recommendation` refuse a row without one,
    and write nothing.
  - `staging_watcher.flag_concerns_without_recommendation` logs a `FLAGGED` line each cycle in
    which the set of open rows without a recommendation changes.
  - `carry_problems` lets a carried row gain a recommendation but never lose or reword one.
  - The seat's brief shows the field, and the delivery projection carries it.
  - The design is small, as the steer asked: one predicate, used by the write door and the
    watcher. It is not a `validate` refusal, because a refusal there restores the orienting
    seat's previous record every stretch.
- **Mutation-proven.** `tests/background/test_director_concerns.py` has a partition over a good
  row, an empty recommendation and a list of options, across both legs, plus a gain/lose carry
  control. Each of these turns them red:
  - the predicate returning None;
  - dropping its "recommend" clause;
  - dropping the raise refusal;
  - the watcher returning nothing;
  - dropping the carry clause.
- **Rows already waiting for him.** 8 were open. 7 now carry a recommendation, with the question,
  evidence, trade-off, holding position and what would change it. The 8th, the founder number, is
  closed as answered with his 16:37 words ("Households, as long as it doesn't create a memory
  problem"). The memory condition on it is being measured under
  `docs/staging/records/SEAT_PREREG_WHAT_400_FOUNDER_HOUSEHOLDS_COST_IN_MEMORY_AND_TIME_MEASURED_ON_SMALL_BOOKS_2026-10-19.md`.
