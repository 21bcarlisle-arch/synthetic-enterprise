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

### Rule 2. A book large enough to price

The run's arms are scored on a book of 272 (`composition`); the `decisions` block counts 154
accounts (§2, "two counts"). At either size one household (PROS-2016-0098) can move the result by
about as much as the result itself. The redesign sizes the book from **one** stated criterion,
power, rather than from habit:

- The 2,490 SVT renewals and the 154 accounts above are the 18 Sep run's; the 8 Oct run's book
  is 272.
- **The question:** can the test tell an advantage of £X per household-year from zero, on the money
  axis, at two-sided 5%, with 80% power?
- **The size follows from the family's own spread**, which is measurable per household-year from the
  existing families. **GAP: X is not established.** The design carries it as a named input, and the
  first sizing run reports the N needed at several values of X rather than picking one.
- One household's share of the figure is reported beside the result as a diagnostic. It is not a
  second sizing rule, because no threshold for it is established.
- **Machine limits are real.** The floor runs were OOM-killed at three seeds on 3 Sep
  (`tools.run_value_cycle_ab.floor_run_headroom_refusal` serialises them). Book size is therefore
  bounded by `background.resource_headroom`, read at run time, and the design states the largest
  book this machine can run per seed before it commits to a size.

### Rule 3. Arms that reach the whole book

Today 2,490 of 2,824 renewals are standard-variable households with no rate this supplier struck
(`product_not_upliftable`), and 227 more are first terms. The thesis is tested only on the
remaining 107. The redesign adds two arms, and keeps the existing one:

| Arm | Who it reaches | The decision it makes |
|---|---|---|
| Renewal pricing (today's) | Households at the end of a fixed term | The renewal margin |
| **Tariff placement** (new) | Standard-variable households, at a point a real supplier could act on (a review, a cap change, a contact) | Whether to offer a fixed or time-of-use tariff, which one, and at what margin, where the household is better off on its own measured use |
| **Acquisition pricing** (new) | First terms | The quoted margin to a prospective household |

The tariff-placement arm is the one the thesis most needs: it is where most of the book is, and it
is where choosing could create value for the household (a better-fitting tariff) rather than move
it. It needs a household's response to an offer, which the world already draws
(`docs/design/CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md`, the hidden traits). It must respect the
licence rules on what an SVT customer can be offered and the cap. K8 applies: the
tariff-and-default-tariff knowledge page (`site/knowledge/tariffs-and-the-default-tariff/`) is read
and amended first.

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

A per-customer engine that beats the EBIT-allowance flat arm has shown it chooses better than an
efficient flat supplier. A per-customer engine whose gain over the cap arm comes out of the
household's bill has moved value, not created it (M2). The level-matched arm (today's third arm)
stays, because it is what separates choosing from charging.

### Rule 5. The write-off rule, settled against GB evidence before the next value run

See §4. K8: the knowledge page is amended before any world change.

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

Written now, before any of it is built or run. Each states what refutes it, and each will be kept
beside its result.

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

## 6. Order of work, after the correctness exit test

1. The two one-variable measurements that cost one run each: the published seed re-drawn inside its
   family (prediction 1), and PROS-2016-0098 under the current write-off rule (prediction 5).
2. The single-invocation runner at the page's own code (rule 1) and its publisher refusal, on
   today's arms only. That alone lets the page state the sign its family already carries.
3. The knowledge-page entries for the two write-off GAPs (debt-sale price, C1), with ranges.
4. The two sourced baselines (rule 4), with the pre-2019 gap read first.
5. Book sizing from the measured spread (rule 2).
6. The tariff-placement arm, after its knowledge page (rule 3). Acquisition pricing after it.
7. The vector scorecard columns that do not exist yet: cash flow, fairness, then time.

**What waits for the director:** the weighting of any trade between axes (his, per 31 Oct), and
whether the cap is the right baseline for the tariff-placement arm (it is a choice about what
"beating a flat supplier" means). Both are in the one `for_the_director` row raised for this note,
in `docs/direction/DIRECTION.yaml`, with a recommendation.
