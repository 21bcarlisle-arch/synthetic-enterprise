# Pre-registration: the ending-term renewal belief, graded on the coming book

**Written 2026-11-22 by the autonomous worker, for the claim
`the-ending-term-renewal-belief-is-graded-on-the-coming-book`.** No book carrying the field this grade reads
existed when this was written: the latest published book (`6a588a832f`, 20 Nov) has no
`desk_belief_log`, and sim-runner has built no book since 20 Nov 15:39. The analysis code
(`tools/grade_ending_term_belief_on_a_book.py`) lands in the same commit, so the method is fixed too.

The switch is `DecisionPolicy.renewal_belief_by_ending_term`, built at `7a7ad95dc`. It was graded in
arms at `427e5f021` (§14) and `5cdb72eb3` (§14 re-taken on the clean book), and both times the
departure interval straddled zero. The live belief reads **0.333** on 2019's 268 desk states. This
grade does not flip the switch.

## 0. Two corrections to the item, both found before any outcome was read

**(a) A standing book cannot give a departure interval.** The book runs with the switch off. The
departure channel is the money the switch moves against flat. It only exists as a difference
between paired arms with the switch on and off (§14's design). One book holds one arm. The switch-on
rule is in §3. It needs arms, and this book does not supply them. What the book **can** grade is
the switch's precondition: does the conditioned belief still rank leavers on today's world, and
does it beat the live belief paired on the same states? §10's 0.819 comes from one 21 Oct arms book,
and 29+ world and company commits have landed since.

**(b) The book could not carry this grade at all until this commit.**
- `extract_report_data` never forwarded `desk_belief_log`, so the published file had no desk states.
- With the switch off, `desk_belief_log` rows never said which term the renewal ended:
  `_ending_term_type` is `None` unless the policy is on.

This commit changes both:
- The run writes `ending_term_type` on every desk row, with the switch on or off. It is the
  company's own contract record and does not change any decision.
- The reducer forwards the log (`saas/reporting/annual_report.py`).

So the book this grade reads is **the first published book whose producing commit descends from this
commit**, not merely from `25f0ea40b`. A book built from an earlier commit carries no
`desk_belief_log` (or rows without `ending_term_type`) and is refused under that name. The grader
does not check ancestry itself, so the reader checks `git merge-base --is-ancestor` first.

**(c) No rule in `company/policy/decision_policy.py` switches it on.** The field is a `bool`,
`False` on every policy. The switch-on rule is prose in the arms record. §3 restates it.

## 1. What is graded

- **States.** Rows of the book's `desk_belief_log` with `desk_asked`, a belief and a non-null
  `ending_term_type`, with `term_start` from 2019-01-01 to 2024-12-31 (every 365-day window closes
  inside the book).
- **Outcome.** The household (`simulation.household.household_of`) has a `churned` row in
  `customer_events` within 365 days of `term_start`. This is the 0.333's outcome. It includes SVT-drift
  departures, which the at-the-roll `left` flag misses. The world rolls no departure at a default
  anniversary (P10c), so an at-roll outcome would partly grade that world rule. It is reported beside
  the grade and is not tested.
- **Conditioned belief.** For each row, the live belief scaled by
  `CompetitivePressureLedger.ending_term_multiplier` for its type. The ledger is fed only the same
  book's desk rows from **earlier years** (n, believed losses, losses at the roll), then passed through
  `condition_on_ending_term`. This is the in-run rule, with the §5a shrinkage, read online. It is not
  §10's one-off pre-2019 fit.
- **Bounds.** 95% intervals from an account-clustered bootstrap (1,000 draws, seed 7), and the paired
  difference (conditioned minus live) taken over the same states.
- **Void, not refuted:** fewer than 100 states or fewer than 15 leavers.

## 2. Predictions (filed before the book exists)

| | prediction | confidence |
|---|---|---|
| **Q1** conditioned AUC | point 0.78, range 0.68–0.86; clustered lower bound above 0.5 | 90% |
| **Q2** live AUC, same states | point 0.45, range 0.30–0.58 | 70% |
| **Q3** paired conditioned − live | lower bound above 0 | 85% |
| **Q4** share of leavers whose ending term was a fix | ≥ 0.75 | 75% |
| **Q5** `multiplier_for_2019["default"]` | below 0.5; `["fixed"]` within 0.8–1.3 | 80% |
| **Q6** sample | ≥ 150 states and ≥ 25 leavers | 80% |

Why Q1 is below §10's 0.819: these are online multipliers shrunk towards 1. In 2017–2018 they are
weak, and the window adds 2021–2023, when fixes vanished and the end of a fix stopped marking a
leaver (14 Nov retrain prereg §2). Why Q2 is above 0.333: the 8 Oct published run scored 0.52 on a
wider population, and this window pools years where the default-roll share differs from 2019. I
have not looked at any count by type for this book.

## 3. What each result does (fixed now)

The **switch-on rule is unchanged** from `5cdb72eb3` §3 and the director's 23 Oct ruling. The rule:
`renewal_belief_by_ending_term` is proposed for `CURRENT_POLICY` only when paired arms against flat
give a `departure` interval above zero, both gross and by household net, with mean net ≥ 0. Under
point 2, a grade that meets the rule is the machine's switch-on. Under point 3, a switch whose rule
is not met stays off, with its reason. Nothing below meets that rule, so **nothing here flips it.**

- **Q1's lower bound > 0.5 and Q3's lower bound > 0:** the ranking survives today's world. The read
  pre-registers the departure grade that would decide the switch: §14's arms re-taken on a book
  descending from this commit, with the seed count from `5cdb72eb3` §5 (6 seeds by its arithmetic).
  It lands that before any arm launches and queues the launch as a costed run. The wrong row
  `the-live-renewal-belief-ranks-leavers-backwards` keeps its owner.
- **Q3's interval includes 0 or lies below it:** the corrected belief no longer beats the live one on
  today's world. The read changes that wrong row's owner. The next fix becomes the retrain (14 Nov
  prereg), not this switch, and the switch stays off with this grade as its reason.
- **Void (floors not met, or refused):** the read says so, with the refusal text, in this file. It
  then hands the read on to the next qualifying book.

## 4. The read

Run `python3 -m tools.grade_ending_term_belief_on_a_book <book>` on the first
`docs/reports/run_output_*.json` whose `producing_commit` descends from this record's landing commit.
Write the output and each Q's verdict as §5 of this file, beside the predictions, unedited. The read
is queued as the seat continuation `read-the-ending-term-belief-grade-on-the-coming-book`.

**Unheld leg, stated:** no control proves that a full run puts a non-null `ending_term_type` on
real rows. The source control proves that the key is written. The grader refuses a book whose rows
lack the key. If every row came out `None`, the grader would see zero typed states, and the floors
would void the grade rather than pass it.
