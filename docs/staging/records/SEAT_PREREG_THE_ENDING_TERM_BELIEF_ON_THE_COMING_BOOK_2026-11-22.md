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

**Read attempt, 22 Nov 10:36 UTC: not graded, re-embargoed.** The newest book is still `6a588a832f`
(20 Nov), which does not descend from `c09847b7c`. sim-runner has stopped deferring on the dirty
shared-tree files. It now yields to `longjob-value-test-cut012-new-book.service`, started 09:58 UTC
with 2,100 minutes declared. That job writes `/var/tmp/vtn-driver/grade_new_book.out` when it ends.
The read is handed on, gated on that file.

## 5. The read: graded on `f2c6979d01`, 25 Nov

**Book:** `docs/reports/run_output_f2c6979d01_20261124T215935Z.json` (149.9 MB, written 24 Nov 23:45).
Its `producing_commit` is `f2c6979d01`. `git merge-base --is-ancestor` confirms that it descends from
`c09847b7c` (this record's landing) and from `59cd5ebda`, `c41e70832`, `1624411d2` and `da34c45c1`.
So it is the qualifying book §4 names. Baseline: `SEAT_RECORD_THE_RENEWAL_BELIEFS_ON_HELD_BACK_YEARS_2026-11-23.md`
(20 Nov world, rows rebuilt from renewal events).

### 5.1 The grader, unedited

`python3 -m tools.grade_ending_term_belief_on_a_book <book>`, 2.1 s:

```json
{
  "states": 259, "leavers": 54, "accounts": 166, "producing_commit": "f2c6979d01",
  "auc_live": 0.395, "auc_live_95": [0.312, 0.475],
  "auc_conditioned": 0.882, "auc_conditioned_95": [0.84, 0.924],
  "paired_conditioned_minus_live": 0.487, "paired_95": [0.416, 0.564],
  "bootstrap_draws_used": 1000,
  "leavers_at_fix_end_share": 1.0,
  "by_type": {"fixed": {"states": 97, "leavers": 54},
              "default": {"states": 155, "leavers": 0},
              "default_after_declined_fix": {"states": 7, "leavers": 0}},
  "multiplier_for_2019": {"fixed": 0.8863269853801622, "default": 0.027394103317504224,
                          "default_after_declined_fix": 0.9998631999162344},
  "secondary_2019_only": {"auc_live": 0.3659476117103236, "auc_conditioned": 0.7935285053929122,
                          "paired": 0.4275808936825886},
  "secondary_left_at_roll": {"auc_live": 0.39498644986449866, "auc_conditioned": 0.8823848238482385}
}
```

(Only the whitespace is reflowed. Every key and value is as printed.)

### 5.2 Verdicts against §2

| | predicted | read | verdict |
|---|---|---|---|
| **Q1** | point 0.78, range 0.68–0.86, lower bound > 0.5 | 0.882 [0.840, 0.924] | **decision part held** (lower bound 0.840). **Range refuted, high**: the point is above 0.86 |
| **Q2** | 0.45, range 0.30–0.58 | 0.395 [0.312, 0.475] | **held** |
| **Q3** | paired lower bound > 0 | 0.487 [0.416, 0.564] | **held** |
| **Q4** | fix-end share ≥ 0.75 | 1.0 | **held** |
| **Q5** | default < 0.5; fixed 0.8–1.3 | default 0.027, fixed 0.886 | **held** |
| **Q6** | ≥ 150 states, ≥ 25 leavers | 259 / 54 | **held** |

Not void. **Q1's lower bound > 0.5 and Q3's lower bound > 0, so §3's first branch applies.** The
follow-on is to pre-register §14's paired arms against flat, with 6 seeds, on a book that descends
from `c09847b7c`, and to queue the launch as a costed run. Nothing here flips the switch.

### 5.3 The 23 Nov record's §4.4 asks

Per-year figures, `within_fixed` and the secondary outcome were computed after the grade, by the 23 Nov
appendix script adapted to read the book's own `desk_belief_log` instead of rebuilding rows. The
script is at `/var/tmp/se-seat-executor-probe/per_year.py`, outside the repository.

**1. Against the baseline.** Pooled live 0.395 [0.312, 0.475] against the baseline's 0.452
[0.377, 0.528]: the intervals overlap. Conditioned 0.882 [0.840, 0.924] against 0.857 [0.811, 0.901]:
they overlap. Paired 0.487 [0.416, 0.564] against 0.405 [0.341, 0.470]: they overlap. Every point
moved the same way, with the live belief worse and the conditioned belief better, but no figure fell
outside its baseline interval. **I cannot say that the commits since `6a588a832f` moved the
ranking.** The baseline was also read from rebuilt rows, not real ones (item 2), so two things
changed at once.

| year | states | leavers | live | conditioned | paired | live within `fixed` |
|---|---|---|---|---|---|---|
| 2019 | 70 | 11 | 0.366 [0.207, 0.533] | 0.794 [0.682, 0.890] | 0.428 [0.298, 0.560] | 0.556 [0.322, 0.772] (29 / 11) — void |
| 2020 | 58 | 17 | 0.402 [0.256, 0.562] | 0.857 [0.746, 0.943] | 0.456 [0.321, 0.591] | 0.712 [0.512, 0.869] (32 / 17) — **graded** |
| 2021 | 59 | 12 | 0.647 [0.491, 0.800] | 0.900 [0.820, 0.971] | 0.253 [0.128, 0.390] | 0.782 [0.560, 0.962] (21 / 12) — void |
| 2022 | 0 | 0 | — | — | — | no desk state this year |
| 2023 | 23 | 0 | — | — | — | void, no leaver |
| 2024 | 49 | 14 | 0.147 [0.024, 0.306] | 0.918 [0.822, 1.000] | 0.771 [0.602, 0.928] | 0.143 (15 / 14, one stayer: not a figure) — void |

**2. Rebuild check: it fails for one type.**
- The baseline's shares were 105 / 173 / 28 of 306, which is 34.3% / 56.5% / 9.2%.
- This book's real rows give 97 / 155 / 7 of 259, which is 37.5% / 59.8% / 2.7%.
- `fixed` is 9% high and `default` is 6% high, both inside the 10% line.
- `default_after_declined_fix` is 71% low: 7 states, where ≈ 24 were expected.

So either the 23 Nov rebuild (its "the last occasion was `declined_fix`" rule) mistyped about 17
rows as declined-fix defaults, or the world since 20 Nov offers fewer declined fixes. One read on
one book cannot separate the two. Under §4.4's own rule, **cite the 23 Nov record for its counts
only**, and do not use its `default_after_declined_fix` figures (multiplier 0.808 there, 0.9999
here, where the ledger has almost no rows of this type to learn from).

**3. `within_fixed` beside Q1.** Pooled live AUC within the fix-ending states is **0.670
[0.560, 0.782]** on 97 states / 54 leavers. The baseline was 0.648. Q1's 0.882 and Q3's 0.487 are
again mostly the type split: every leaver ended a fix, and no default state left inside the grader's
outcome. Inside the type at risk, the live belief ranks leavers better than chance but well short of
the conditioned pooled figure. A better belief *within* fix-ending states is still owed. That is the
retrain's subject (14 Nov prereg). This switch does not touch it, because `condition_on_ending_term`
preserves the order within a type.

**4. Drift exits are still only in `svt_departures`.**
- The book has **252** `svt_departures` rows.
- It has 111 `churned` rows in `customer_events`, all with `departure_occasion` `renewal`.
- No `svt_departures` row (customer and date) appears among them.

So the grader's 365-day outcome cannot see a default household leaving by drift. Adding
`svt_departures` as a secondary outcome brings only 2 more leavers into the window, both
`default` (one in 2019, one in 2021). Pooled live becomes 0.413 [0.332, 0.495], conditioned 0.871
[0.825, 0.915] and paired 0.459 [0.378, 0.542]. Its lower bound stays above 0 under either outcome.

### 5.4 What the arms will measure, said before they are pre-registered

The departure channel that §14's arms grade is money. That money comes from the desk treating
default-anniversary households as low-risk. On this book, the world never rolls a departure at that
moment (P10c), and only 2 of 252 drift exits land inside a desk state's 365-day window. A
positive arms result would therefore partly grade the world's no-departure-at-default rule, not the
company's skill. The arms pre-registration has to state this. Its outcome should also count drift
exits, so the arms cannot win on a channel the world has switched off. Whether P10c is true of GB
households is a fidelity question, and this read does not answer it.
