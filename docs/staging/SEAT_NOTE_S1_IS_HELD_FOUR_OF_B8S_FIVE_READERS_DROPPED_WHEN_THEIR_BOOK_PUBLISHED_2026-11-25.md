**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# S1 is held: four of B8's five readers left the queue before their book published, and none wrote a verdict

Drawn 25 Nov 09:25Z: `s1-contract-the-first-term-at-its-quote-on-the-book-after-s0`. Its step 1 gate is
in `docs/staging/records/SEAT_RECORD_THE_DEFAULT_OFF_SWITCHES_AND_THE_ORDER_THEY_FLIP_IN_2026-11-24.md`
§3. It says S1 waits until B8 P4's five grades are written on the post-s.12g standing book (S0).
**The gate is not met, so the flip is not made.** `CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE` stays `False`.

## What was read

S0 is `docs/reports/run_output_f2c6979d01_20261124T215935Z.json`, published 24 Nov 23:45Z.
`producing_commit` is f2c6979d01, which descends from 59cd5ebda, c09847b7c, c41e70832, 1624411d2 and
da34c45c1 (checked with `git merge-base --is-ancestor`). It carries `company_debt_recovery`,
`riding_leg_answers`, `desk_belief_log`, `customer_events` and `meter_read_log`. So the book qualifies
for all five readers.

| grade | verdict on S0 | reader in `seat_continuation.live()` at 09:25Z |
|---|---|---|
| won-switch P2–P5 | **written** (c2e2b551a8, 25 Nov 09:18) | finished |
| ending-term belief Q1–Q6 | none (no §5 in its prereg) | no: `DONE`, aged out 76 h after its draw |
| dual-household answers | none | no: `DONE`, aged out |
| KNIFE3 I1–I5 | none | no: `RETIRED`. Two rows each named the other in `supersedes`, so both were retired |
| D48 blend at 0.5 | none | no: `EXPIRED`, never taken |

The gate's first leg, "none of them is still live", passed vacuously. Its second leg, "each prereg
has its verdicts", is what caught this. That is the case the 23 Nov pre-flight record (§2) warned
about.

## What was done

- The four readers were re-armed against S0's own path, so they can be drawn now:
  `read-the-ending-term-belief-grade-on-the-coming-book`,
  `grade-dual-household-answers-apart-on-the-first-book-carrying-c41e70832`,
  `d48-grade-the-first-book-descending-from-59cd5ebda-with-the-blend-at-0-5`, and KNIFE3 under a new id,
  `grade-knife3-i1-to-i5-on-book-f2c6979d01`. The new id replaces the two rows retired by the cycle. Each
  keeps its original grading instruction unchanged. Only the old "wait for a book" rule is replaced
  by the name of the book that now exists.
- S1 was re-handed for 09:00Z on 26 Nov with its text unchanged, plus the KNIFE3 successor id.

## Class (not fixed here)

A reader that waits on a book lives at most 6 h past its window, but a book takes about 30 h. Pre-flight §2 named
this class on 23 Nov. It took four of five readers on the one book they were all waiting for. The
supersede cycle is a second, separate defect: `--supersedes` lets a row retire the row that retires it.
