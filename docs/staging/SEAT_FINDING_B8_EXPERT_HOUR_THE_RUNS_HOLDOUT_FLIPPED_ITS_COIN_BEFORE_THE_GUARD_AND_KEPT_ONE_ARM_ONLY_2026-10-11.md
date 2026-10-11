**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# B8's Expert Hour, run blind: FAIL, held at L2. One disqualifier was a live defect and is fixed here

*2026-10-11, worker tick.*

## The pass

I gave a fresh agent only a plain-words packet from `tools/blind_review.py`. The description was a
restatement, not the index text. The persona was a veteran of UK domestic retail pricing and
retention who has designed randomised holdouts. The agent returned 15 questions, 9 of them
disqualifying. They are recorded in `docs/observability/blind_review_ledger.jsonl`. The audit says
the blindfold held and records independence as false. Below, each disqualifier is graded against
the tree.

## Fixed in this commit (Q11: randomisation)

**The run's holdout put households nobody would offer into one arm only.** The company's coin was
flipped at every renewal the guard considered, which was before the guard's own value test. The run
then:

- kept every held-out row, including renewals the guard would have declined, and
- dropped a treated renewal whenever no offer was made.

So the held-out arm contained "would never be offered" households and the treated arm did not.
That is the defect the FRAME named in 2026-07 ("assign before the eligibility threshold"), and it
sat behind the threshold that comes after the coin.

Now the decision is read on both arms (`RetentionHoldout.decide`), and
`RetentionHoldout.would_offer` says whether the company would offer before the coin matters. That
means the learned decision once there is one, and the standing guard until then. A row is written
on either arm exactly when that is true. The run's log carries `would_offer` on each coin-flip row.

A **save on the loss notice** that keeps a leaving household is now carried on the holdout row
(`saved_on_loss_notice`). It still counts as stayed, so the estimate is the renewal offer's effect
with the save running on both arms. But a save that reaches the held-out arm is now counted rather
than hidden. Q11 asked for exactly that.

Controls are in `tests/company/test_discovered_price_sensitivity.py`. Four mutations, all red:

- decide returns early on the held-out arm (2 red);
- `would_offer` ignores the decision (green on the first draft, because the arm-blind leg holds
  either way; I added an assertion that the decided no-cut leg is not due when the guard says yes);
- the save flag is dropped.

**What no unit control reaches.** The run loop's own predicate (`_holdout_would_offer` in
`simulation/run_phase2b.py`) can only be reached through a run with `retention_runs_holdout` on, and
no test runs one. **Prediction, filed before any run:** on the default roster to 2019-12-31, the
flag-off run offered 120 of the 121 renewals the guard considered. So the change moves at most one
or two holdout rows, the effect stays undecided, and the headline net moves by less than one offer's
cost.

## Graded, still open

- **Q1, epistemics: CLOSED in the tree.** The "+1pp for £7.50/MWh" figure is the company's own
  holdout estimate, taken on the coin-drawn harness decision set at national-book scale. In the run,
  the company reads only its own rows closed before today, and its interval never decides. So no
  run decision rests on that figure. "Offer to nobody" is the harness's L2 result, not a decision
  the run makes.
- **Q2, value basis: PARTLY.** L2 brackets the margin share at two sourced ends: the cap's 0.019
  EBIT allowance and 0.14 gross. L3 uses the term's own forward margin over its own billing.
  Tenure is undiscounted, with no re-acquisition cost and no cost to serve. All three are already
  named simplifications.
- **Q4, targeting: PARTLY.** The harness reads the effect by observed position: acquisition route,
  days on default, and ever actively renewed (`SAVE_POSITION_OBSERVABLES`). The run's decision
  reads only payment channel.
- **Q5, relative price: OPEN for the renewal cut.** The cut is an absolute £/MWh. The reactive save
  is sized against the market's best published deal (afd818b22), and the renewal cut is not.
- **Q7, eligibility (30 decisions a year from 400 homes): PRINTED, see the addendum.** Before: The reasons are stated on the
  director's row (correction 2026-10-10): founders renew together, most roll passively to the
  default, and cheaper 2019 renewals fall below the threshold. The renewal-event count itself has
  not been printed beside the considered count. That is measurable and is owed.
- **Q8, decision rule: OPEN, and the reviewer is right about its structure.** The rule is "act once
  the interval excludes zero", then expected value. A significance gate keeps a small book passive
  for good. At the run's own point estimate (+0.042) against a break-even near +0.15, expected
  value under a flat prior also says no cut, so here the rule does not change the answer. A rule on
  expected value with a prior is the director's open row (`the-run-s-company-cannot-learn-whether`),
  because the only informative prior is evidence from outside the book.
- **Q10, outcome: CLOSED in the code, the window is a named gap.** See the addendum below.
- **Q15, is "a small book cannot evaluate" a real limit? PARTLY.** The reactive save was built and
  measured as a separate intervention (0f1fb3f6a: the only retention shape that beats never
  offering), so the limit is the proactive renewal cut's alone. Targeted, sequential and pooled
  designs were not tried. Pooling with external priors is the director's row.

## Verdict

FAIL, held at L2. This is not an independence park: independence is not the open question. The
buildable next items are, in order: Q10 (an outcome window), Q7 (print renewal events beside
considered ones), and Q5 (size the renewal cut against the best published deal, as the save
already is). Q8 waits on the director's row.

Reverse: revert this commit. The holdout is off on every standing policy, so no standing run moves.

## Addendum, same day, later tick: Q10 and Q7 (direction `b8-the-holdouts-stay-has-an-outcome-window`)

The worker that wrote the section above died before landing it. A later tick took over its worktree
and lands both together.

### Q10: a row's outcome is read at a window, from the company's own loss notices

- A holdout row now keeps its **stay-or-leave on the decision** (`stayed_at_decision`) and its
  **renewal kind**: `re_fixed`, `declined_fix_on_default` (the household stayed and sits on the
  default) or `left_at_decision`. A rollover onto the default is carried apart from a re-fix.
- Its outcome is **"no loss notice on the account's own supply points inside the window"**. That is
  read from `CoSRegister.losses_notified()`, the supplier's own register, and only notices that had
  reached the company before the day of the decision count. A row closes when the household left
  on the decision, when a notice inside the window had arrived, or when the whole window had passed.
  A move-out is not a loss notice and does not count against the row.
- **The window length is not established.** SLC 22C fixes the renewal notice (42-49 days before
  term end) and the fee-free exit before it, not how long after the decision a loss is attributed.
  The only "six or twelve months" I found is a practitioner case study's advice. So
  `RETENTION_OUTCOME_WINDOW_DAYS = None`, with that reason on the constant and a row in
  `docs/institutional/knowledge_map.md` (Market Switching). While it is None no row closes, the
  company learns nothing from its own holdout, and the standing guard decides. On the founders'
  book that is what already happened, since the interval never decided. Window 0 is the old
  definition, kept nameable.
- **For the director (the practitioner side):** how long after a renewal does a retention team
  count a loss as that renewal's? Setting the constant is one line.
- Controls are in `tests/company/test_discovered_price_sensitivity.py`. They are one partition over
  a row's seven states, the None-window leg and the renewal-kind leg. Seven mutations: six red.
  The one green, counting a loss effective on the decision day against a row that stayed, is an
  **equivalence**: the run files a decision-day loss only for a household that left, and a left row
  never reads losses.

**The live run (holdout on, default roster, 2016-01-01 to 2019-12-31, 1,064 s).** The prediction,
filed before the run: with no window, no row closes, so every decision is None and every row's
would-offer is the standing guard's.

- 68 coin flips, all would-offer, 0 decided, every row carrying window None. **Held.**
- Rows by arm and kind:

  | arm | `re_fixed` | `declined_fix_on_default` | `left_at_decision` |
  |---|---|---|---|
  | treated | 20 | 3 | 10 |
  | holdout | 12 | 9 | 14 |

  The offer turns decliners into re-fixers: 3 against 9.
- Stayed, read at each window (treated, then holdout). This is right-censored: rows from 2019 had
  no full year left in the run.

  | window | treated | holdout |
  |---|---|---|
  | 0 days | 23/33 | 21/35 |
  | 30, 60, 90 or 180 days | identical to 0 days | identical to 0 days |
  | 365 days | 19/33 | 18/35 |

**What the window cannot find in this world, which is a finding for the world lane.** There are 10
later losses:

- Nine came at **365 days or more**. Each is a re-fixed household leaving at its *next* renewal,
  which is that renewal's own departure, not this one's.
- One came at 615 days, from the default tariff.

None comes "two or three months later", because the world has no route by which a household on a
fixed term leaves mid-term (exit fees are unmodelled: `simulation/departure_risks.py`, §EXIT FEES).
A household on the default leaves only at the start of a cap-period segment. So the bias the
reviewer named cannot arise in the run as it stands. The mechanism is built and controlled, and the
world does not yet produce what it measures. Two consequences:

- Any window under a year reads the same as the decision-day outcome here.
- A window at or past the new term's end would count a re-fixed household's next-renewal departure
  against this renewal. Whoever sets the window should keep it inside the term it attributes.

### Q7: renewal events beside considered, in numbers

The full-window census is `tools/renewal_population_by_step` on `docs/reports/run_output_latest.json`
(run 7379375f6, threshold 0.3). Accounts at each step, by year:

| year | live accounts | fixed term ended | fixed term reached a decision | fixed term considered | default anniversary decided | default anniversary considered | fixed-to-default with no decision |
|---|---|---|---|---|---|---|---|
| 2016 | 438 | 4 | 3 | 1 | 0 | 0 | 1 |
| 2017 | 444 | 281 | 99 | 53 | 35 | 0 | 182 |
| 2018 | 408 | 102 | 42 | 19 | 66 | 36 | 60 |
| 2019 | 366 | 99 | 38 | 1 | 56 | 10 | 61 |
| 2020 | 309 | 84 | 37 | 1 | 36 | 1 | 47 |
| 2021 | 284 | 75 | 33 | 21 | 39 | 8 | 42 |
| 2022 | 272 | 42 | 0 | 0 | 0 | 0 | 42 |
| 2023 | 277 | 6 | 4 | 0 | 25 | 13 | 2 |
| 2024 | 302 | 34 | 14 | 1 | 47 | 30 | 20 |
| 2025 | 255 | 34 | 16 | 5 | 10 | 6 | 18 |

Read across a typical year, 2019:

- 366 live accounts.
- 99 fixed terms ended, and 61 of them rolled onto the default with no decision.
- 38 reached a decision, and 1 was above the 0.3 belief threshold.
- 56 default anniversaries were decided, and 10 were considered.

So of the ~400-home book, about a quarter reach any renewal decision in a year, and how many are
considered swings with the belief from 0 to 55. Across 2016-2019, 120 were considered against the
121 above. In this tick's own run to 2019 (current code), 123 were considered: 68 reached the coin
and 55 were refused first by the 10-10 gate.

Reverse: revert the commit. The holdout is off on every standing policy, so no standing run moves.

### Landing note, 10:40

The tick that wrote the addendum also died before it landed. Its surgical_land was seen in its gate at 08:23. The work was still in `/var/tmp/se-b8-harden`, uncommitted, with its owner pid gone. Lane 0 redrew the item at 10:38. This tick carried the source, test and record hunks onto origin/main (`800c4b18d`) with a 3-way apply. That base already held two later commits to `simulation/run_phase2b.py` (42b2eb254, 68793db33), and the apply was clean. Both control files pass at the new base (27 passed). The generated observability files from that worktree were not carried. The live-run tables above are the earlier tick's, taken at its base, and were not re-run here.
