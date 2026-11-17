**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The acceptance recount at twenty measurement answers can't be done yet: there are none (2026-11-17)

*Drawn as `acceptance-recount-at-twenty-measurement`. Its premise commit, 28263e95c, is on origin/main.
That commit built the counter. It did not produce the twenty answers the counter needs.*

## What was measured

`python3 -m background.director_concerns --acceptance` on 17 Nov printed only `unkinded (...)` rows:
canon_intent 14, reserved 5, strategy 24, vision 1, all `uncoded`. There is **no `measurement` row**,
so the count of explicit coded measurement answers is **0 of 20**.

That is the expected result, not a defect:

- `for_the_director` rows carry a `decision_kind` only if they were raised on or after 17 Nov (14b2bbeb5).
  No row raised since then has been answered.
- Advisor-channel steers and rulings get coded (`Decision: <kind> <code>` in `## Done`) only if they
  arrive in advisor/done on or after `ADVISOR_DECISION_FROM = 2026-11-18`. That is tomorrow.
- By design, the earlier 19 measurement decisions (the 17 Nov reader count) are not re-coded. The item
  says to use codes written at answer time only, so they are excluded.

## When it will be reachable (prediction, written before any coded answer exists)

Rate: 103 DIRECTOR_STEER_/RULING_ files reached advisor/done across October and 1–17 November, 50 of
them in November. The reader count found 16 measurement decisions among the advisor files and 3 among
the seat rows. That is roughly 0.4 measurement decisions a day at the Oct–Nov rate, and about double
that at the November rate.

**Prediction:** measurement reaches 20 explicit coded answers between **2026-12-12 and 2027-01-10**.
The most likely date is around mid-December. If fewer than 10 exist by 14 Dec, the rate assumption was
wrong. The likeliest cause would be lanes writing `Decision: none` on steers that do answer a
recommendation, so read the `none` reasons before waiting longer.

## Disposition

Nothing was recounted, because there is nothing yet to recount. The item is handed back with a dated
embargo of 14 Dec 09:00 so the draw cannot offer it before then. When it is drawn again, done means:
`--acceptance` shows `measurement` with `explicit >= 20`, and its table is copied into a record next
to this one with the Wilson lower bound against 0.80. If it is still below 20, record the count and
re-embargo it.
