# The 20261004r floor is the same book: its control arm is re-drawn too, and two near misses churn on every seed

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-20261004r-floor-book-mismatch-is-explained` (Lane 0 delivery)

Answers `records/SEAT_FINDING_THE_QEP_REFIT_LANDS_AND_ITS_FLOOR_IS_REFUSED_AS_A_DIFFERENT_BOOK_ON_ONE_CHURN_COUNTED_FIELD_2026-10-04.md`.

## Premise at draw

`b9ede156f` is on origin, and the page still refused the floor. The duplicate claim the draw named
was this item's own id. The premise held.

## The prediction filed beforehand was wrong

It said the floor drives the value or level arm through a code path that skips an end-of-window
filter. **Refuted.** `run_noise_floor` reads `book_identity.control_arm` per seed (the same
`book_identity()` and the same `portfolio.account_count` the three-arm uses). No arm differs and no
filter differs.

## What it is

The floor re-draws elasticity in EVERY arm, the control included, and never at the run's base
seed. So the floor's control arm is a different realisation of the churn, not a re-run of the
figure's. Measured from the run logs (`/var/tmp/longjob-qep2-arms-three-arm.log`,
`/var/tmp/longjob-qep3-arms-floor.log`), control arm only:

| | churns | extra vs base |
|---|---|---|
| three-arm control (base draw) | 26 | — |
| floor seed 11111 / 22222 / 33333 | 28 / 28 / 28, same set | PROS-2016-0046, PROS-2016-0092 |

Both extras are near misses the base draw happened to survive:

| household, date | roll | base p_retain | re-drawn p_retain (3 seeds) |
|---|---|---|---|
| PROS-2016-0046, 2017-02-16 | 0.7455 | **0.7608** (retained) | 0.7256, 0.7402, 0.7355 |
| PROS-2016-0092, 2021-03-27 | 0.6384 | **0.6562** (retained) | 0.4589, 0.2217, 0.1381 |

Every other churn is roll-dominated, so p_retain moves on every seed while the churn set does not.
That gives 42 on every seed (44 − 2) and a control net of £93,475.24 on every seed, against the
three-arm's £99,172.40. This is explanation 2 from the finding ("insensitive to the re-draw"), with
a twist. The count is insensitive WITHIN the floor, but the floor never includes the base draw, so
its flat range can sit wholly outside the figure's.

Explanation 3 (different populations) is refuted. All four counts that a churn re-draw cannot move
agree exactly.

## What changed (`tools/generate_value_arms_data.py`)

1. **`_realised_book_pairing` no longer compares `accounts_at_end_of_window`.** The field counts
   who is still on supply at the edge, which is a churn outcome, and churn is what the floor
   re-draws. Its docstring assumed a moving field would widen its own range. Three seeds that all
   miss the base draw's two near misses do not widen it. The excluded field is named, with its
   reason, in `not_compared` (`BOOK_FIELDS_THE_FLOORS_REDRAW_MOVES`), not dropped silently. The four
   settled-in-window counts still refuse a different book, and the 164-vs-154 case still refuses.
2. **The sign sentence reads the spread.** `which_sign_question_this_answers` asserted "the
   re-draws fall on both sides of zero" as a literal. The first time it went live it was over the
   20261004r advantage re-draws (£24.1k–£27.5k, all positive), and it said the opposite of the data.

Both carry a two-leg control, and both mutations were run and went red.

## What the page now says about the current world

- Value advantage over 3 re-draws: £24,134–£27,538 (mean £26,086).
- Level leg: £12,988–£20,989.
- Selection leg: £6,550–£13,598 (its distance-to-sign stays VOIDED, as on 09-27).

**The verdict is still withheld**, and that is correct. Seven `simulation/`/`company/` paths moved
between `96517e68c` and the publishing commit, and none is exempt. This item did not touch that
refusal.

One reading the page now shows: the published draw (£20,889) sits BELOW all three re-draws. That
is the same two near misses seen from the other side. The base draw kept two control customers that
every re-draw lost, which raised the control's net and lowered the advantage. With n=3 I cannot say
whether the base draw is unusually lucky or the floor is unusually unlucky. A wider family would
tell.

## Not done

- No exemption argument for the seven moved paths, and no re-run at HEAD. Each is a separate item.
