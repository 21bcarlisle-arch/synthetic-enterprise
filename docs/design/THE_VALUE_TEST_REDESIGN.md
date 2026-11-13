# The value test, redesigned so it can return an answer

*Delivery seat, 2026-11-02, for the director's steer of the same day, part 2 (signed text at
`2e50f42c3`; the file is now
`docs/staging/advisor/done/DIRECTOR_STEER_THE_VALUE_TEST_MUST_BE_ABLE_TO_ANSWER_AND_THE_SITE_MUST_BE_CURRENT_2026-11-02.md`).
**Thinking only. Nothing here is built.** The build waits for the correctness stretch's exit test
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). Every
figure below was read from `site/data/value_arms.json` as it stands at `88ba2ed1f1`, or from the
file named beside it. That one feed carries two runs, and each figure here names its run:
`current_world` is the run of 2026-10-08T06:52Z at `45122d156`. The top-level `book`, `decisions`
and `provisioned` blocks are the run of 2026-09-18T05:43Z at `b329e702b`.*

*Amended 2026-11-13 by the delivery seat for the director's steer of that day (section 2 and
addendum point 3 of
`docs/staging/advisor/done/DIRECTOR_STEER_THE_SITE_MUST_SAY_PLAINLY_WHETHER_PER_CUSTOMER_VALUE_WORKS_AND_THE_VALUE_TEST_GOES_FIRST_2026-11-13.md`).
Rules 2 to 5, §5 and §6 are rewritten: every effect is now stated **per household per year**, the
belief's skill comes before the money, the book is sized from a stated noise model with its compute
and token cost, the flat baseline is the efficient-supplier margin, the standard-variable arm is
named, and the write-off rule is settled against the 7 Nov debt evidence. Nothing was run for this
amendment. The new figures in §3a were computed from two artefacts already on disk:
`docs/observability/value_cycle_ab_s1_three_arm_20261008r.json` (the run the page publishes) and
`docs/observability/value_cycle_ab_s1_three_arm_20261013t.json` (a later three-arm run on a 780-account
book, at `05f9f3347`, which the page does not publish).*

## 3a. What the existing runs say per household per year (computed 13 Nov, nothing re-run)

**What is counted.** A household is one billing account; dual-fuel legs count as one. A
household-year is one (account, calendar year) group with settled supply in the control arm. A part
year counts as a whole one, so these per-year figures are, if anything, low. Each figure below is an
arm total divided by the control arm's household-years. Spreads are taken across households, with
each household's paired difference between two arms of the same run as the unit.

| | 8 Oct run (page) | 13 Oct run (not published) |
|---|---|---|
| Book | 272 households, 1,831 household-years | 780 households, 4,162 household-years |
| **Belief's skill, AUC against who left under the flat price** (0.50 is a coin) | **0.52**, 95% interval **0.41 to 0.65** (2,000 resamples, clustered on 122 accounts) | **0.55** (no interval computed) |
| **Calibration**: believed minus realised retention | **−0.22**, interval −0.27 to −0.17 (believed 64%, realised 87%) | **−0.25** |
| Whole advantage, per-customer arm over the £2/MWh flat arm | **+£2.86 per household-year** (£5,244) | **+£1.12** (£4,652) |
| Its spread across households (sd of the paired difference, per household over the run) | £522, so the mean is **0.6 standard errors** from zero | £394, **0.4 standard errors** from zero |
| Choosing alone, per-customer arm over the level-matched flat arm | **+£6.20 per household-year** (£11,345), 2.0 standard errors | **+£2.38** (£9,886), 1.2 standard errors |

*From the feed, 13 Nov.* The 8 Oct column is now computed at publish, not by hand:
`site/data/value_arms.json` → `current_world.per_household_year`
(`tools/generate_value_arms_data._per_household_year`). Capabilities' lead and its
per-household table are rendered from it. Every figure above reproduces. The one exception is the
AUC interval. The feed gives **0.40 to 0.64** (seed 20261113, stated in the feed), where the hand
computation gave 0.41 to 0.65 at an unrecorded seed. That is resampling noise, and the reading does
not change. The 13 Oct column is not published and stays hand-computed.

**What this says, plainly.** The belief cannot yet tell who leaves: both AUCs sit on a coin, and the
8 Oct interval runs from worse than a coin to modest skill. It expects far more households to leave
than do. The money advantage is a few pounds per household-year. **Across households it is not
distinguishable from zero in either run.** The "13.7 standard errors" the page carries is a
different spread: the world's re-draws of the same households, the floor in §2. It is not the spread
between households. A test of whether per-customer decisions work has to clear the second spread,
because that is the one a different book would show.

*Correction, beside the claim.* §2 called the 13.7 standard errors "a sign the family would state".
That holds for the family's own question: would the same 272 households give the same answer again?
It does not answer the thesis question, which is whether another book would show the same thing.
Rule 2 now sizes for the thesis question.

## 1. The question, stated before anything is measured

**Does a supplier that decides household by household create value that a supplier applying one
flat rule could not, and does the household keep a share of it?** (M2: created, then shared.)

"Value" is a vector, never a sum (the director's ruling of 31 Oct on
`docs/design/THE_IMPROVEMENT_LOOP.md` §3 D): customer money (cost, and cash flow, measured apart),
customer time (household minutes per kind of activity), customer carbon (CO2 saved), company
outcomes, and fairness, above the comfort and health floor (M3). A design wins only if it is no
worse on every axis and better on one; any weighted trade between axes goes to him.

The test today answers a narrower question: on households already on a fixed deal, at the end of
that deal, does choosing each household's renewal margin beat one flat margin, in company money on
the settled clock? The page publishes no answer even to that, for the reasons in §2. Within the run's own family an
answer exists; the page withholds it because the run is on older code than the page.

## 2. The advisor's five readings, tested against the feed and the run

Each was re-measured before it was adopted. **A fresh-context read of the first draft of this note
(2 Nov, verdict NEEDS_WORK) found that I had misread the feed on reading 4 and on the world's
write-off rule. The corrections are made below and marked where they stand, and the wrong first
reading is kept beside each one.**

| # | Advisor's reading | What the feed says | Verdict |
|---|---|---|---|
| 1a | The published whole advantage (£5,244) sits below all three re-draws (£9,375–£11,766) | `current_world.value_advantage_gbp` 5,244.00; `verdict_stability.redraw_values_gbp` 11,766 / 9,697 / 9,375 | **Confirmed** |
| 1b | The price-level leg changes sign between draws | Published level leg **−£6,100.76**; its three re-draws are **+£3,920 / +£4,975 / +£1,649** | **Confirmed**: the published draw has the opposite sign to every re-draw |
| 1c | 0 of 5 families state a sign for the choosing | The page states no sign: every leg's `resolved` is null and its verdict is withdrawn. **But the reason is code drift, not noise.** Within its own family the whole advantage is `distance_to_a_sign.sems_from_zero` **13.7** standard errors from zero against a bar of 4.30, positive. `selection_split` puts churn pricing +5.9 and credit +4.6 standard errors from zero, positive on every draw. I did not re-count five families | **The page states no sign, confirmed. "Cannot state one" is not**: the family would state one, and it is withheld for the gap in reading 4 |
| 2 | 104 of 2,824 renewals priced (3.7%) on a 154-account book; 2,490 unpriced are SVT | The `decisions` block (18 Sep run): `value_arm_priced` 104, `renewals_the_world_offered` 2,824, share 0.0368, `book_accounts_settled` 154; `outside_it`: `product_not_upliftable` 2,490, `acquisition_term` 227 | **Confirmed, but of the 18 Sep run**, not the 8 Oct run behind £5,244. The shape (most renewals are SVT) is the point, and it stands; see "two runs' counts" below |
| 3 | PROS-2016-0098 moves the figure by about £5,300, partly through the write-off-everything-on-exit rule | `root_cause`: "moves by −£5,344.10, because the simulated world writes off every failed bill in full for any customer who ever leaves"; its write-off part is `measured: false` (derived) | **Published, but the rule it names is out of date**, and its money is derived rather than measured: see §4 |
| 4 | Figures and bounds come from different code and books: 180 paths, floors on 164 vs 154, control pinned to 9 Sep | The 180 paths are between **the run (45122d156) and the page (185355386)**. They are not between the figure and its bound: `bound_tree_pairing` gives 45122d156 for both, same world `cdba75ebb9197b33`, same book (`composition.floor_selected_by_book` 272/272). The 164-vs-154 is in `contrast_bounds`, an older run pair (17/18 Sep). The 9 Sep control is `departure_term_rerun`'s baseline, not the run behind £5,244 | **Partly.** The page does mix runs, but the headline figure and its own bound are one instrument |
| 5 | The baseline is a £2/MWh flat margin, far below an efficient supplier's | Control is "£2.00/MWh"; `control_as_share_of_regulated_allowance` **[0.264, 0.8]** | **Partly**: a quarter of the allowance at one end, four-fifths at the other. "Well below" holds; "far below" only at the low end |

**The published draw is outside its own family, and the family has the same code, world and book.**

| Contrast | Published | Re-draws (min–max) |
|---|---|---|
| Whole advantage | £5,244 | £9,375 – £11,766 |
| Choosing (selection) | £11,345 | £4,722 – £7,846 |
| Price level | −£6,101 | +£1,649 – +£4,975 |

The re-draw means add up (£6,765 + £3,514 = £10,279, the whole's mean), so the family is internally
coherent. The published run splits the same households between choosing and level in a way none of
its re-draws reproduces.

*Correction, beside the claim.* My first draft said this showed "the figure and its bound are two
instruments", drawn on other code and another book. That was wrong: `bound_tree_pairing` says
`same_tree: true` at 45122d156, and the book is 272 on both sides. **The cause is open, and I cannot
yet say what it is.** Candidates, to be ranked by measurement, not by convenience:
(a) the re-draw varies one thing (the per-household elasticity draw), and the published run's own
draw is not one of the three seeds, so the family is not centred on it; (b) three re-draws are too
few to bound a figure that one household can swing by about its own size (reading 3); (c) something
none of us has thought of. The one-variable test is to widen the family at the same commit, the same
world and the same book, from 3 re-draws to 12, varying only the elasticity seed. If £5,244 falls
inside the 12-draw range, (b) is supported and the published draw was an ordinary but extreme
member. If it stays outside, (b) is refuted, and the published run differs from its re-draws in
something other than the seed: (a) or (c). A second test then separates those two: re-run the
published configuration with the re-draw harness itself.

**Two runs' counts on one page.** `current_world` (8 Oct, 45122d156) counts `priced_decisions` 272
of `renewals_offered` 5,874, on a 272-account book. The `decisions` block (18 Sep, b329e702b) counts
104 of 2,824 on 154 accounts. So the advisor's 3.7% and 154 accounts describe the older run, not
the figure beside them. On the 8 Oct run the share is 272 / 5,874 = 4.6%. I have not established
that "priced_decisions" there counts the same thing as "value_arm_priced", so I do not offer that
4.6% as the same quantity. The redesign gives each count one definition and one home (rule 1).
*(My first draft said I had not established which run each block came from; the top-level
`producing_commit` answers it.)*

## 3. The redesign

### Rule 1. One world, one code tree, one book, one date, for every figure on the page

The headline figure and its own bound already share code, world and book (§2, reading 4). What the
page mixes is **everything around them**. The figure was run on code 180 paths older than the page.
A control arm is pinned to a 9 Sep run. A floor pair is from 17/18 Sep on a 164-account book. Two
counts of priced decisions disagree. So the rule is about the page as a whole:

- Every figure and every bound the value test publishes comes from **one invocation**, at **one
  commit**, on **one world digest** and **one roster**. The artefact records all four once, at the
  top. A figure from any other run is not published beside it; it moves to the appendix with its
  own date.
- The run is at the **page's own code**, or the publisher states which code moved and why it
  cannot move the arms. Today that gap is the only reason a sign the family would state is
  withheld (reading 1c), so closing it is worth more than any new arm.
- The publisher refuses a value-test artefact whose figures carry different commits, worlds or
  rosters. That is one check, and it replaces the withdrawal prose rather than adding to it.
- Every count is published with what it counts.
- **The re-draw family includes the published draw's own seed**, so the published figure is a
  member of the family it is bounded by (§2, candidate (a)).

### Rule 2. A book sized so the predicted effect can be told from noise

**The question:** can the test tell a money advantage of £X per household-year from zero, at
two-sided 5% with 80% power, where the unit is the household? The predicted size is X = £3 (§5,
P3). That is the 8 Oct reading against a weak control, so against the efficient-supplier baseline
(rule 4) it is the generous end.

**What the floor decomposition can and cannot say.** The published decomposition
(`site/data/value_arms.json` `floor_decomposition`) cannot size this book, by its own account. Its
rest-of-book half returned the same figure on all three seeds, so every sizing key is withdrawn as an
identity. It was also measured on another book (104 of 2,009 renewals), another world
(`39a192ce04c1eda8`) and legs on different trees. What it does establish is that **all of the
seed-to-seed spread sits on the priced households**. So per-household noise has two parts:

- **roll noise**: the luck of each household's churn and payment rolls, which re-drawing the same
  household K times averages down by about √K; and
- **true heterogeneity**: how differently households really respond, which only more households
  buys down.

The decomposition the sizing needs is that split, measured per household. The first measurement in
§6 (the 12-draw family) yields it as a by-product, because it re-draws the same 272 households
twelve times.

**The size, stated now at both ends of that split.** The spread is about **£75 per household-year**
(8 Oct: £522 over 6.7 years on average; 13 Oct: £394 over 5.3 years; the two agree). Then
n = (2.80 × 75 / X)²:

| X, £ per household-year | Households needed, one draw each (all heterogeneity) | Households needed at 12 draws each, if all roll noise |
|---|---|---|
| £10 | 441 | 37 |
| £5 | 1,764 | 147 |
| **£3 (the prediction)** | **4,900** | **408** |
| £2 | 11,025 | 919 |
| £1 | 44,100 | 3,675 |

**Machine limits.** One arm at the settlement budget (`SETTLEMENT_CUSTOMER_YEAR_BUDGET`, 7,700
household-years) peaks at about 5.8 GB and takes about an hour (`settlement_ceiling_slope_20261025.json`,
3,567 s at 7,699 household-years). That is **about 1,100 to 1,400 households per run** at the two books' average
tenures (6.7 and 5.3 years); call it 1,200. So:

- If roll noise dominates, **a 1,200-household book at 12 draws resolves £3 with room to spare**.
  The commitment is one book of the budget's size, six arms (rules 3 and 4, with the £2/MWh
  bridge) and twelve draws: 72 arm-runs, run serially under the headroom refusal, about **72
  machine-hours** (3 days).
- If heterogeneity dominates, £3 needs about 4,900 households, **four times what one run can
  hold**. Then this machine cannot settle a £3 effect in one invocation. The honest result would be
  "we cannot tell at this size", and the remedy (sharded books under one world, or a smaller claim)
  goes to the director with its cost.
- Which of the two holds is the first measurement's answer, and §5 P6 predicts it before it is run.

**Token cost.** Runs are machine time, not tokens. The tokens are the sessions that launch, grade
and publish, priced from `tools.work_cost_estimate` (997 landed sessions over 30 days; 1 point = 1%
of the weekly allowance). A grading run costs a median 0.46 points. Launching and grading the sized
run is about **2 to 4 points**. The whole redesign is priced in §6.

One household's share of the figure is still reported beside the result as a diagnostic, not a
second sizing rule.

### Rule 3. Arms that reach the whole book

Today 2,490 of 2,824 renewals are standard-variable households with no rate this supplier struck
(`product_not_upliftable`), and 227 more are first terms. The thesis is tested only on the
remaining 107. The redesign adds two arms, and keeps the existing one:

| Arm | Who it reaches | The decision it makes |
|---|---|---|
| Renewal pricing (today's) | Households at the end of a fixed term | The renewal margin |
| **Standard-variable placement** (new; the "tariff placement" arm) | Standard-variable households, at a point a real supplier could act on (a review, a cap change, a contact) | Whether to offer a fixed or time-of-use tariff, which one, and at what margin, where the household is better off on its own measured use |
| **Acquisition pricing** (new) | First terms | The quoted margin to a prospective household |

The tariff-placement arm is the one the thesis most needs: it is where most of the book is, and it
is where choosing could create value for the household (a better-fitting tariff) rather than move
it. It needs a household's response to an offer, which the world already draws
(`docs/design/CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md`, the hidden traits). It must respect the
licence rules on what an SVT customer can be offered and the cap. K8 applies: the
tariff-and-default-tariff knowledge page (`site/knowledge/tariffs-and-the-default-tariff/`) is read
and amended first.

**The standard-variable arm, paired.** It runs as two arms on the same book:

- **SV-cap**: every standard-variable household is left at the cap. That is the "do nothing" a real
  supplier does.
- **SV-placed**: the per-customer engine may offer each standard-variable household a fixed or
  time-of-use tariff, chosen from that household's own metered use. It does so only where the offer
  is cheaper for the household than staying at the cap.

The paired difference is scored per household-year on each axis, and separately for the households
it moved and the ones it did not. It is the arm where the household side of M2 can show directly: a
lower bill with the company no worse off is value created; a lower bill with the company worse off by
the same amount is a transfer.

### Rule 4. A sourced baseline

The flat-rules supplier should be the best a flat-rule supplier could do, so that beating it means
something.

- **For fixed-term renewals: a flat margin at the cap's EBIT allowance.** That is 1.9% of revenue
  from the cap's launch (Ofgem, Default Tariff Cap decision, Nov 2018). From 1 Oct 2023 it is 12.3%
  cost of capital on £358 of capital employed, about £44 per customer a year (Ofgem, EBIT allowance
  decision, 25 Aug 2023). Both are in
  `docs/market_research/clv_discount_rate_and_terminal_value_for_a_gb_supplier.md`. A "2.4%" figure
  has no source and was corrected out (`suppliers_accounts_and_capital_2026-10-25.md` item 8).
  - Turning a per-customer or %-of-revenue allowance into a £/MWh margin needs a consumption. The
    world has each household's metered use, so the conversion is per household, not a typical
    figure.
  - **GAP: 2016–2018.** There is no cap and no allowance before 1 Jan 2019, and renewals are priced
    in those years (PROS-2016-0098's is 2017-03-23). The pre-cap evidence in
    `docs/market_research/CSS_BENCHMARKS.md` (supplier EBIT% by year) is the candidate. Until it
    is read for this purpose, the pre-2019 baseline is an open input, not a number.
- **For the tariff-placement arm: the cap itself.** The cap is a price ceiling for
  standard-variable households, not a flat margin on a fixed renewal, so it is the natural
  baseline only for the arm that reaches those households. A flat supplier leaving every SVT
  household at the cap is the "do nothing" a real supplier does.

**Settled 13 Nov: the flat baseline is the efficient-supplier margin, not £2/MWh.** In detail:

- **From 1 Oct 2023**: 12.3% on £358 of capital employed, about **£44 per household-year**.
- **1 Jan 2019 to 30 Sep 2023**: **1.9% of revenue**. That was about £34 per household-year by
  2023 (same source).
- **2016–2018**: 1.9% of revenue, carried back as a **stated belief**, not as an established
  figure. The basis is that the 1.9% is the CMA's 2016 investigation's cost of capital, which was
  measured on the pre-cap market, turned into a margin. The Big Six's realised pre-cap domestic
  EBIT of about 3–5% (`CSS_BENCHMARKS.md`, estimated) is the sensitivity's high end. That figure is
  what suppliers earned, not what an efficient one needed. The pre-2019 GAP above stays open until
  that file is read for the purpose.
- **Each household's allowance is converted at its own metered use and its own settlement date.**
  The 8 Oct artefact's `control_credibility` puts the converted allowance at a median of £2.5–£7.6
  per MWh, so the old £2/MWh control was a quarter to four-fifths of it.
- **The £2/MWh arm runs once more, as a bridge.** The first redesigned run carries it beside the
  new baseline, so that the change of baseline and the change of code can each be attributed. It
  is then retired.

A per-customer engine that beats the EBIT-allowance flat arm has shown it chooses better than an
efficient flat supplier. A per-customer engine whose gain over the cap arm comes out of the
household's bill has moved value, not created it (M2). The level-matched arm (today's third arm)
stays, because it is what separates choosing from charging.

### Rule 5. The write-off rule, settled against GB evidence before the next value run

**Settled 13 Nov, against the 7 Nov evidence**
(`docs/staging/advisor/done/DIRECTOR_EVIDENCE_WHAT_HAPPENS_TO_UNPAID_DOMESTIC_ENERGY_DEBT_2026-11-07.md`,
primary-checked in `docs/market_research/final_account_debt_recovery_primary_check_2026-11-07.md`).
The decision is the seat's (`priority_order.yaml`, `the-worlds-write-off-rule-meets-gb-evidence`).
It is made for fidelity, without reference to which arm it helps.

- **What the world does now** (§4): a leaver's balance is written off at close, after netting, and
  about 5p in the pound (2p–8.6p) comes back later. That is an effective loss of about **95%**
  (91–98%) of the balance at departure.
- **What the evidence supports, at grade P**: Centrica's 2025 accounts provision UK residential
  **final** bills at **84.0%** (2024: 85.6%), and at 87.8% once they are more than 90 days past
  due. This is a provision on the stock of aged final debt, so it is an upper bound on the loss
  when a household leaves, not the loss itself. The pack's own 65–80% rests on grade-A assumptions
  and is not used.
- **The rule**: a leaver's unpaid balance at close carries a final-account loss of **86%** (range
  84–88%). The 14% recovered comes back over 36 months, 50% in months 1–3, 30% in months 4–12 and
  20% in months 13–36. That phasing is grade A and is labelled **GAP: recovery timing**, because no
  primary publishes it. Nothing is recovered after month 72 (Limitation Act s.5, grade P).
  Debt-sale prices stay a GAP, with no sale leg.
- **Out of scope for this rule**: the switch rules (the 28-day objection, and prepayment debt
  assignment at £20–£500 paid at 90% plus VAT). They change who can leave owing money, and that is a
  separate world change.
- **Sensitivity.** The value run reads the rule at 84% and at 88% as well as 86%, on the
  level-matched pair only. That shows how much of the choosing leg depends on the loss rule.
- **Order (K8)**: first amend `docs/market_research/debt_and_collections.md` (row P5) with the rule
  and its two GAPs, then build it in `simulation/arrears_engine.py`, then measure prediction P7.

### Rule 6. Scored on the vector

Each arm reports, in its own unit and never summed:

| Axis | Measure | Exists today? |
|---|---|---|
| Customer money: cost | What each household paid, against the published default tariff at its own metered volumes | Yes (`household` block, settled clock) |
| Customer money: cash flow | Largest single payment and the variance of monthly outgoings | **No**: GAP, named |
| Customer time | Household minutes per kind of activity | **No**: nothing in the run counts minutes (the Capabilities page's "What is not built yet" table). Published as "not measured", never as zero (K2) |
| Customer carbon | Emissions per household are computed; CO2 *saved* needs a counterfactual | Emissions yes; saving **no** |
| Company outcomes | Net margin on the settled-realised clock, bad debt, retention | Yes |
| Fairness | The distribution of household money outcomes across the hidden traits the world draws (income, vulnerability, engagement), and the share of the gain kept by the worst-off decile | **No**: to design |
| Comfort and health floor | Any household on any arm that self-disconnects or under-heats below the floor | Partly (the world draws under-heating) |

The verdict is per axis. "Settled" means no worse on every measured axis and better on one.
Otherwise the published verdict is "we cannot tell", with the axis that decided it. An unmeasured
axis is shown as unmeasured, so a reader can see what the verdict does not cover.

### Rule 7. Predictions written down before the run

Filed in `docs/staging/` at the commit that starts the run, each with what would refute it.
§5 holds the first set.

## 4. The write-off rule against GB evidence

**What the page says and what the world now does are different.** The PROS-2016-0098 root cause
("writes off every failed bill in full for any customer who ever leaves") was established on 27 Sep
(`docs/staging/done/SEAT_FINDING_A_FAILED_BILL_IS_WRITTEN_OFF_IN_FULL_IFF_THE_CUSTOMER_EVER_LEAVES_2026-09-27.md`).
Since then the world (`simulation/arrears_engine.py`, all of it in the 8 Oct run's code) has
changed in four ways:

- It writes off **the leaver's balance at close**, after credits net against arrears (SLC 27.16).
  There is also a statute-bar leg (`emergent_bad_debt_lines`; ba1b6c259b is an ancestor of 45122d156).
- It **recovers part of a written-off debt later**. `post_write_off_recovery_share` reads
  `q3_post_write_off_recovery_share` from `docs/market_research/assumption_toggles.yaml`: about 5p
  in the pound, range 2p to 8.6p, sourced. Collection-agency recovery runs through
  `dca_recovered_amount`. The feed's own `changed_since_the_last_reading` records this: "the world
  now recovers less of it".
- **The debt-sale price is a deliberate GAP** (`debt_sale_price_share`, default null).
- **Provisioning for stayers' failed direct debits** (leg 4b) is wired but off by default. Its
  bucket (C1) has no source.

*Correction, beside the claim.* My first draft said the world loses a leaver's balance "in full, at
close, with no later recovery and no debt sale", and proposed building provision-and-recovery as
the first step. That was wrong; it mostly exists. The evidence on file
(`docs/market_research/how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`,
`docs/market_research/bad_debt_provisioning.md`, knowledge page `site/knowledge/bad-debt-provisioning/`)
already backs it:

- A failed direct debit is chased; it is not a write-off.
- Bad debt is recognised when it is provisioned, and the write-off finalises it. Provisioning
  rates run at about 75% weighted on 2022–24 debt (Ofgem DRS working paper, Aug 2025, §5.20).
- Final-bill debt is 17–29% of a large supplier's gross receivables (Centrica, derived).

**What is actually still open:**
1. **Whether PROS-2016-0098 still moves the figure by about £5.3k under the current rule.** Its
   write-off part was derived, not measured, and on a rule that has since changed. This is the
   first measurement, one variable at a time.
2. **The debt-sale price** (GAP), and **the stayer provision bucket C1** (GAP). Both are named
   gaps already. K8: the knowledge page carries each one with a labelled range before the world
   reads it.
3. **Whether the page's statement of the rule is current.** It is not. The root-cause text is a
   27 Sep reading published as today's world, so it moves to the appendix with its date.

These are world questions, decided for fidelity without reference to which arm they help. The value
result prompted them; it is not evidence for their answer.

## 5. Pre-registered predictions for the first redesigned run

*Rewritten 13 Nov, before any of it is built or run. The 2 Nov set is kept below, under "The 2 Nov
predictions", and is not withdrawn. Where a 13 Nov prediction restates one of them per household per
year, it says which. Every money figure is per household per year, with the book and the years
beside it. The book total comes second.*

**The run these predictions describe.** One world, one commit, one roster, 2016–2025. It has the
arms in rules 3 and 4: the efficient-supplier flat arm, the per-customer arm, the level-matched arm,
SV-cap, SV-placed, and the £2/MWh bridge. The book is the one rule 2 settles on after P6. The
intervals are 95%, clustered on households.

**First, the belief's skill. If this fails, no margin figure below is evidence for the thesis.**

- **P1. Discrimination.** The belief's AUC against who left under the efficient flat arm is
  **between 0.45 and 0.60**, and its interval includes 0.50.
  - Today: 0.52 (0.41 to 0.65) on 8 Oct; 0.55 on 13 Oct.
  - Refuted if the interval's lower end is above 0.50. That would be skill I do not expect from a
    belief no one has retrained.
- **P2. Calibration.** Believed minus realised retention is **between −0.27 and −0.10**. The belief
  still expects too many households to leave.
  - Today: −0.22 and −0.25.
  - Refuted if the gap is within ±0.05 (calibrated) or positive.

**Then the money, per household per year.**

- **P3. Against the efficient-supplier flat arm, the per-customer advantage is between −£3 and +£3
  per household-year, and its interval includes zero.**
  - Today, against £2/MWh: +£2.86 (8 Oct) and +£1.12 (13 Oct), each under one standard error from
    zero across households.
  - Refuted if the interval excludes zero on either side. If it excludes zero on the positive side,
    that is the thesis's first real evidence.
  - This restates 2 Nov prediction 2's second half per household.
- **P4. The bridge.** Against the £2/MWh arm in the same run, the advantage is **between +£0 and
  +£6 per household-year**.
  - Refuted outside that range. That would mean the code since 8 Oct moved the arms, not the
    baseline.
- **P5. Choosing alone** (the per-customer arm over the level-matched flat arm) is **between £0 and
  +£6.20 per household-year**, lower than 8 Oct's +£6.20. Part of the choosing leg's money is credit
  selection, and the new write-off rule (86% instead of about 95%) makes avoiding debtors worth
  less.
  - Refuted at £6.20 or above, or if the interval sits wholly below zero.
- **P6. The noise split that sizes the book.** In the 12-draw family, roll noise is **at least half**
  of the per-household variance of the whole advantage.
  - Refuted if it is under half. Then rule 2's heterogeneity column governs, and a £3 effect is
    beyond one run on this machine.
- **P7. One household under the new write-off rule.** PROS-2016-0098 moves the whole advantage by
  **less than £1.45 per household-year** of the 272-household book. That is £2,650, half of today's
  published £5,344.
  - Refuted at £1.45 or more. This restates 2 Nov prediction 5.

**The standard-variable arm, per household-year of the households it moves.**

- **P8. Reach.** SV-placed makes a decision for more households than the renewal arm does.
  - Refuted at the same number or fewer. This is 2 Nov prediction 3.
- **P9. Who gains.** Against SV-cap, the households SV-placed moves pay **£5 to £40 less per
  household-year**, and the company's net margin on those households is **lower**, by no more than
  the households' saving.
  - Refuted on the household side if they pay more. Refuted on the company side if its margin rises.
  - A household saving with a matching company loss is a transfer, and the page says so (M2).
  - This restates 2 Nov prediction 4.

**The vector.**

- **P10.** The first redesigned run cannot settle on the vector. Cash flow, time and fairness are
  not all measured, so the verdict reads "we cannot tell" and names those axes. This forecasts what
  will be built, not what the run will find. It is 2 Nov prediction 6.

### The 2 Nov predictions (kept as written)

1. **Widening the family from 3 to 12 re-draws at 45122d156, same world and book, still leaves the
   published £5,244 outside the range.** That is, I predict (b) "too few re-draws" is not the cause.
   Refuted if £5,244 falls inside the 12-draw range.
2. **At the page's own code, the whole advantage over the £2.00/MWh control stays positive and
   clears the family's own bar** (today 13.7 standard errors against 4.30). Refuted if its sign
   flips or it falls under the bar. Against the **EBIT-allowance** control I predict it is smaller,
   and **it does not clear the bar at a 272-account book**. Refuted if it does.
3. **The tariff-placement arm makes a decision for more households than the renewal arm does.**
   Refuted if it reaches the same number or fewer. (Today the renewal arm decides 107.)
4. **Against the cap baseline, the tariff-placement arm lowers what households pay in total and
   lowers the company's margin.** Refuted on the household side if the households it moves pay more
   in total than at the cap. Refuted on the company side if the company's margin rises.
5. **Under the current write-off rule, PROS-2016-0098 moves the whole advantage by less than
   £2,650, half of today's published −£5,344.10.** Refuted if it moves it by £2,650 or more.
6. **The first redesigned run cannot settle on the vector.** At least one of cash flow, time and
   fairness will still be unmeasured, and the verdict will read "we cannot tell", naming those axes.
   This forecasts what will be built, not what the run will find, and it is labelled as such.
   Refuted if all three are measured by that run.

## 6. Order of work, and what it costs

*The 2 Nov heading said "after the correctness exit test". The director's 11 Nov ruling replaced
that gate: features now get about a third of capacity. His 13 Nov steer makes this the first
feature item of the week of 16 Nov.*

Points come from `tools.work_cost_estimate` medians per landed session: supplier build 0.72, world
build 0.69, knowledge 0.64, grading run 0.46, harness 0.46. The ranges use the quartiles. Machine
hours come from the settlement curve in rule 2.

| # | Step | Sessions | Points (range) | Machine time |
|---|---|---|---|---|
| 1 | The 12-draw family at `45122d156`, which gives 2 Nov prediction 1 and the household noise split for P6 | 2 grading | 0.9 (0.6–1.5) | 36 arm-runs on 272 households, about 9 h |
| 2 | The write-off rule: knowledge page, then the world (rule 5), then P7 | 1 knowledge, 3 world, 1 grading | 3.2 (2.0–4.8) | one 272-household pair, about 1 h |
| 3 | The single-invocation runner and its publisher refusal (rule 1) | 3 harness | 1.4 (1.0–2.1) | none |
| 4 | The efficient-supplier baseline arm, with the pre-2019 belief (rule 4) | 1 knowledge, 2 supplier | 2.1 (1.5–3.0) | none |
| 5 | The standard-variable pair, after its knowledge page (rule 3) | 1 knowledge, 4 supplier, 1 world | 4.2 (2.9–6.1) | none |
| 6 | The sized run, with the book from step 1 and P1–P9 graded | 3 grading, 1 site | 2.2 (1.4–3.5) | about 72 h if P6 holds; beyond one run if it does not |
| 7 | The vector columns still missing: cash flow, then fairness, then time | 3 supplier | 2.2 (1.6–3.3) | none |
| | **Total** | **27 sessions** | **about 16 points (11–24)** | **about 82 machine-hours** |

**Step 1, launched 13 Nov 13:14Z (result not yet read).** The family runs at `45122d156` in its own
worktree as unit `longjob-value-test-12-draw-family-pairs`, with seeds 11111 to 99999, 10101,
20202 and 30303. The redraw key is `elasticity` and the mode is `all`, as on 8 Oct. Seeds run in
pairs, each pair in a child process. Each pair is the commit's own `noise_floor`, with the default
runner wrapped only to keep the control arm's net per household. The floor row drops that net, and
the whole advantage per household needs it. No arm, baseline or world is changed. The family is
then folded with `--fold`. Seed 11111 must reproduce 8 Oct's £11,766.20, or the world under the
worktree has moved. Everything outside the repo lives in `/var/tmp/vt12-driver/`: `driver.py` runs
the family and `grade.py` grades it. The outputs land in `/var/tmp/vt12-out/`. The grader was
checked on a fixture with a known 50/50 split and returned 0.49 (0.44 to 0.55).

*What this family's "roll noise" is.* It is the variance across re-draws of the elasticity
assignment. Churn and payment rolls are held at the base seed, so they count in the between-household
term. That makes the measured roll share a **lower bound**, and the heterogeneity term an upper
bound. If P6 holds on it, it holds. If P6 fails on it, the honest reading is "not shown", and a
`churn_roll` family is the next measurement.

*Correction, beside the claim.* The table says step 1 takes about 9 machine-hours. The last family
at this commit took 5 h 28 min for 3 seeds (8 Oct, 11:20 to 16:48Z), so 12 seeds take about
**22 hours**. A floor leg's 11.2 GB peak also leaves room for only one leg at a time. The result
reads around midday on 14 Nov, still before the 16 Nov review.

*Household-years per seed, added mid-run (13 Nov 19:40Z).* The floor row carried no household-year
count, so the error bar could not be stated per household per year (the page's `#arms-errorbar`
names that absence), and the re-draw band divided every re-draw by the published run's 1,831.
`driver.py` now keeps `household_years_by_arm` in each pair's sidecar, read off that seed's own
`household_side`. A child process reads the driver when it starts, so **pairs 4 to 6 (seeds 77777
to 30303) carry the count and pairs 1 to 3 do not**. Pair 3 had started at 19:29Z. The arms, the
world and the floor row are unchanged; the pre-edit driver is kept beside it as
`driver.py.before_household_years_20261113`. From the same commit, `noise_floor` writes the same
field on every row, so later families carry it without a wrapper. **The grade should do three things.**
It states the six counted seeds per household per year, each over its own count. It reports how much
the count moves between those seeds. Only if that spread is small does it divide the other six by
the counted mean, and then it says that it did so.

*The price-level leg, a question for the same grade.* The published draw is −£6,100.76 (−£3.33 per
household-year over 1,831), and all three earlier re-draws are positive (reading 1b). Twelve
re-draws of the level leg say whether the published draw is a tail of one distribution or a
different instrument. **Prediction, filed before the grade:** at most 1 of the 12 is negative, so the
published draw sits in the lowest tail, and the per-household-year spread of the level leg is wider
than its mean.

So the redesign takes about half of one week's feature third (33 points), with room left for the
world steers. Steps 1 to 4 fit the week of 16 Nov. Step 6 starts when steps 1, 2, 4 and 5 have
landed, and with the 72-hour run it probably reads in the week of 23 Nov. Acquisition pricing comes
after step 7.

**The page meanwhile.** Until step 6 reads, the Capabilities page keeps its 13 Nov lead: the 8 Oct
run, older than the page, and "we cannot yet say it works", with the reason (the director's done
condition). Step 1's result goes to the page's appendix with its own date as soon as it reads.

**What waits for the director:** the weighting of any trade between axes (his, per 31 Oct), and
whether the cap is the right baseline for the tariff-placement arm (it is a choice about what
"beating a flat supplier" means). Both are in the one `for_the_director` row raised for this note,
in `docs/direction/DIRECTION.yaml`, with a recommendation.
