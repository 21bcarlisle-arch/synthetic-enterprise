**Severity:** LATENT · **Lane:** 0 (delivery seat) · **Item:** `the-four-unparsed-grades-reach-the-learning-loop`

# Four grades restated in the trailer the learning loop parses (2026-11-20)

`background.learning_loop.measures()` on origin/main (c41e708321) listed four commits under `unparsed`,
each with "needs held= and missed=". A landed commit cannot be amended, so this record restates each
grade **exactly as the original commit graded it**. Where the original gives no count, this record
says so and **does not invent one**.

| commit | what its trailer said | what its own grading says | restated as |
|---|---|---|---|
| 617ec5faa9 (D48, 19 Nov) | `67d454905c -- elec gap 0.361 (SPAR 0.5, in band) / 0.276 (SPAR 3, 0.004 below the band floor; …); E1 breaches 10=10=10, flags 35=35=35` | The record (`SEAT_PREREG_D48_THE_ELECTRICITY_RESIDUAL_BY_ESTIMATE_ROUTE_2026-11-19.md`, "Graded 2026-11-19") reads the pre-registered band [0.28, 0.38] at two points. **SPAR 0.5: inside** (0.361). **SPAR 3: outside** by 0.004 (0.276), "the band is refuted at the high end, and that stands as written." It calls E1 "a replication by the harness. It is not the graded invariant for 67d454905c". | `d48 held=1 missed=1`. The area was the book sha, so it is now the atom's name. code and reader are left at their default of 0: the record names the cause of the miss as the no-skill denominator moving between books (+6.3%), which is neither our model of our own code nor the reader. E1 is not counted, as the record says. No width is stated; the band's width could be derived, but it was never filed as one. |
| 47881a984c (level-dd, 18 Nov) | `level-dd -- not yet; no book exists to grade.` | No grade: no book carrying the fix existed. | **No count, so no grade.** It is restated here as ungraded and nothing is added to level-dd. |
| 22f1dfa987 (W2_30, 20 Nov) | `none -- a count of the store and the book, plus a prediction filed for the next book (fabric legs >= 180)` | A count, not a graded prediction. The prediction it files is still open. | **No count, so no grade.** It is not restated. |
| f165c9b1ee (W2_30, 20 Nov) | `none -- an attribution of a move already seen, not a prediction` | An attribution, not a prediction. | **No count, so no grade.** It is not restated. |

## Why `none` was not a defect, and what changed so it stops reading as one

Two of the four (22f1dfa987, f165c9b1ee) were correct: they declared that they graded nothing, and
gave the reason. The loop read that declaration as a malformed grade. `parse` now treats
`Graded: none -- <reason>` as an explicit no-grade, so it is neither a grade nor a refusal. A bare
`Graded: none` with no reason is still refused.

The other two cannot be fixed at their source. The restating commit carries `Restates: <sha>` for
617ec5faa9 and 47881a984c. That moves their refusals out of `unparsed` and into a new `restated`
list, which names the restating commit. They are not dropped: the docstring's rule that "a malformed
grade read as no grade would make the hit rate look better" still holds for anything nobody has
answered.

## The gate

Before this commit, nothing on the commit-msg path read `Graded:`. Both malformed trailers passed
`message-gate: rc 0` (their receipts say so). The commit-msg hook now runs
`python3 -c ... refuse_message` (no `__main__`: a background entrypoint would need a seat guard), which uses the loop's own `parse`, so the
gate and the reader cannot disagree. Read against the four originals, it refuses 617ec5faa9 and
47881a984c, passes 22f1dfa987 and f165c9b1ee, and passes b1e04fab35 (`value-test held=3 missed=0`).

## The two drawn rows, disposed separately (no commit needed: the ledger is the record)

- `the-0-12-pair-is-read-and-the-advantage-is-published-with-its-interval` gets `--premise-spent`
  by b1e04fab35. That commit graded the pair and published the advantage over the twin with its
  interval: −0.33 (−1.77 to +0.96).
- `poesys-net-goes-behind-a-login` gets `--premise-spent` by ff5b0224b9, not `--landed`. The row
  holds no claim, so `--landed` refused ("NOT CLAIMED"). Its window was 19 Nov 17:49–20:29, and the
  work landed after it: ff5b0224b (the gate), 5be769d15 (the side door), and 39337b8c6 and
  7d99949ce7, which read every route and every remaining deployment answering 401 from outside.
  `drawn_without_landing` now reads both rows as `premise_spent`.
