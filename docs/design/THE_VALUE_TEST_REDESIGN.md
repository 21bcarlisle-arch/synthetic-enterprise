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


**The second test, (a) against (c): predictions filed 14 Nov 09:41Z, before launch.** *(Committed as `2b45da063` saying 09:50Z; the clock read 09:42Z when the next note was written, so 09:41Z is the honest time.)* §7 refuted
(b). This run puts the published configuration through the re-draw harness itself. It uses the same
worktree at `45122d156`, world `cdba75ebb9197b33`, the 272-household book, `noise_floor` and sidecar,
as one pair in one fresh process (`/var/tmp/vt12-driver/published.py`, out to `/var/tmp/vt-pub-out/`).
- **Member 1, seed 20260724.** This is the run's own base seed (`live_population._DEFAULT_BASE_SEED`).
  At this seed the elasticity patch hands every household `real(id, 20260724)`, which is what the
  unpatched 8 Oct run computed. So this member is the published draw, run by the harness. It runs
  first in the process, as every 12-draw pair's first seed did. The sidecar records
  `run_base_seed()` after the run, so the grade can confirm that 20260724 really was the base seed.
- **Member 2, seed 11111.** It is a known control: £11,766.20 on both 8 Oct and 13 Nov, each time run
  first. Here it runs second, so it also tests whether a figure depends on its place in the process.

| | Under (a): the published draw is an ordinary seed the family was not centred on | Under (c): something other than the seed sets the published run apart |
|---|---|---|
| Member 1, whole advantage | **£5,244.00 to the penny** (£2.86 per household-year on 1,831) | **Inside £5,556 to £12,462.** I expect £7,200 to £12,000 (about the family mean ± 1.4 sd), or £3.9 to £6.6 per household-year |
| Member 1, level leg | **−£6,100.76** to the penny | Inside −£3,003 to +£5,560; I expect −£1,000 to +£4,500 |
| Member 1, choosing leg | £11,344.76 | Inside £3,274 to £12,388 |
| Member 2, seed 11111 | £11,766.20 | £11,766.20 |

**My prior, written before the answer: (a) at about 60%.** At the base seed the patch is a
passthrough by construction, and seed 11111 already reproduced 8 Oct to the penny, so the world under
the worktree has not moved. If the 13 draws are exchangeable, the chance that the published one falls
outside the other 12 is 2/13, about 15%, so an extreme seed is not unlikely. Two things could
nevertheless make it (c). The 8 Oct three-arm run was a separate process from 8 Oct's own noise
floor (05:24Z against 11:20Z), so process or tree state may differ. And a reload that leaves state
behind (staged 14 Nov, `WORKER_FINDING_A_BOOK_RELOAD_LEAVES_THE_SUPPLY_BOOK_HOLDING_THE_OLD_RECORDS…`)
would make a run depend on what ran before it in the same process.
**If member 2 does not reproduce £11,766.20, the place in the process matters.** In that case
neither (a) nor (c) can be read cleanly from member 1, and I will say so rather than pick one.

**Observed at 09:42Z, before the pair had started (it was queued behind sim-runner), from the 12-draw
files and the 8 Oct artefact, with no new run.** Each arm's book net, published against the 12 re-draws:

| Arm | Re-draws: min to max (mean, sd) | Published | Distance from the family mean |
|---|---|---|---|
| Control | £229,503 to £233,781 (£231,506, £1,179) | **£235,588** | **+3.46 sd** |
| Level | £230,778 to £236,586 (£233,566, £1,687) | £229,488 | −2.42 sd |
| Value | £238,348 to £243,167 (£241,097, £1,302) | £240,832 | −0.20 sd |

**The published value arm is not unusual.** Its net, £240,832.431409, is identical to the sixth
decimal to seed 99999's value arm. 11111 and 77777 also share one value arm and one priced
fingerprint, so a value-arm net is a coarse function of the draw. **What sets the published run
apart is its control arm,** which is £1,807 above the highest re-draw. The level arm is also low. So
the low £5,244 comes from a high control, not a low value arm. I did not know this when I wrote the
prediction above, and **I revise my prior on (a) from about 60% to about 45%**. A control 3.5 sd out
on its own is as hard to get from an ordinary seed as the whole figure was. The table above is
unchanged, and the run will grade it.

**Graded 14 Nov 12:53Z: (a) held.** The pair finished at 12:52Z (`pair [20260724, 11111] done`,
10,616 s). I graded it with `/var/tmp/vt12-driver/grade_published.py`, run unchanged over
`/var/tmp/vt-pub-out/`. It ran at commit `45122d1565`, on world `cdba75ebb9197b33` and the 272-account
book. The sidecar reads `run_base_seed()` = 20260724 after each member.

| Member 1, seed 20260724 | Published (8 Oct) | Harness (14 Nov) | Difference | Per household-year (1,831) |
|---|---|---|---|---|
| Whole advantage | £5,244.00 | £5,244.004943 | £0.000000 | £2.86 |
| Level leg | −£6,100.76 | −£6,100.759561 | £0.000000 | −£3.33 |
| Choosing leg | £11,344.76 | £11,344.764504 | £0.000000 | £6.20 |
| Control arm net | £235,588.43 | £235,588.426466 | £0.000000 | £128.67 |
| Value arm net | £240,832.43 | £240,832.431409 | £0.000000 | £131.53 |
| Level arm net | £229,487.67 | £229,487.666905 | £0.000000 | £125.33 |

These are book totals over 272 accounts. Each per-household-year column divides that book total by
the control arm's 1,831 household-years, as rule 2 does. The arms' own household-years differ:
control 1,831, value 1,779, level 1,724. Every control-arm account net also matches the 8 Oct
artefact: the largest per-account difference is £0.00.

Member 2, seed 11111, ran second and reproduced **£11,766.198097**, which matches the known figure
to £0.000000. Running second in the process did not change it, so I can read member 1 cleanly
(see the caveat above). Its control net, £229,503.37, is the lowest control in the 12-draw family.

**What this settles.** The published £5,244 is the published configuration's own elasticity draw,
seed 20260724. When the re-draw harness runs that seed, it reproduces every figure to the penny.
That rules out (c): no process state or tree state sets the 8 Oct run apart. The published figure
sat outside the 12 re-draws because the family never contained its seed, and at that seed the
control arm happens to be high. I first put (a) at 60%. **My 09:42Z revision to 45% moved the wrong
way.** I treated a control 3.5 sd out as evidence against an ordinary seed. One draw in 13 at
+3.46 sd is unusual, but nothing beyond the draw is needed to explain it. The rule-1 bullet below
("the re-draw family includes the published draw's own seed") is the fix that this grade supports.
Across the 13 draws, seed 20260724 is the lowest whole advantage. The published figure is a real
member of its family, at that family's bottom, and the page should say so rather than present it as
typical.

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

**Step 1, launched 13 Nov 13:14Z (read 14 Nov 08:54Z; the grade is §7).** The family runs at `45122d156` in its own
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

### 6a. After the 16 Nov reset: the order of the three belief-and-book candidates

*Written 14 Nov, after §2 graded (a) and before the `churn_roll` family (§8) reads. It changes no
code and launches nothing. It does not guess the family's answer. It writes down, for each answer,
what the Monday ranking should take first, so the order comes from this page rather than from
memory.*

**The three candidates, and what each costs.** Points use the `tools.work_cost_estimate` medians
read on 14 Nov, with quartile ranges: supplier 0.72, knowledge 0.62, grading 0.46, harness 0.45.
Machine time comes from this page's own runs. One seed of the three arms on the 272-household book
takes about 1.5 h: the published pair ran 10,616 s for two members. Twelve seeds took 18 h 46 min
in §7. One arm at the settlement budget holds about 1,200 households (rule 2).

| | Candidate | The one variable it changes | Sessions and points | Machine time | The prediction it must beat |
|---|---|---|---|---|---|
| **A** | **Switch on the corrected belief** `renewal_belief_by_ending_term` (`7a7ad95dc`, default off, never yet run inside the value test) | The value arm's belief: the policy flag goes from off to on. World, book, arms and draws are unchanged | 2 grading: **0.9 (0.6 to 1.5)**. The code exists, and the driver sets the flag outside the repo | One draw: about 1.5 h. Twelve draws: about 19 h | The flat-arm AUC with the flag off: **0.549** (0.530 to 0.572 across §7's 12 draws), with its interval clear of 0.50, by more than the `churn_roll` family's AUC half-range. Calibration: believed minus realised retention must move from **−0.21** towards zero. Money cannot be read at 272: the switch moved about £1 to £1.50 per household-year in §14 and the clean-book re-take, and 272 households resolve about £10 |
| **B** | **The renewal retrain** (pre-registered at `22b06c6c2`, `docs/staging/records/SEAT_PREREGISTRATION_THE_RENEWAL_BELIEF_RETRAIN_2026-11-14.md`) | On top of A: a learned level plus a price-position slope, fit on the company's own closed renewals. The belief is otherwise A's | 3 supplier, the knowledge page amended first (K8), and 1 grading: **3.2 (2.2 to 4.9)** | 2019 scoring takes minutes. The value-test read takes the same time as A | Its pre-registration's R1 to R4. R1, 2019: 0.82 (0.79 to 0.86), where the switch alone already scores 0.819. R2, value test: 0.68 (0.60 to 0.78), clear of 0.50. R3, calibration within ±0.06. R4, +£3 to +£9 per household-year. **Once A has read, B must beat A's own value-test AUC**, not today's 0.549, because the type split is A's |
| **C** | **A book of about 4,860 households** (§7: £3 told from zero, at 80% power, on one draw) | Book size only: households 272 → about 4,860. Belief, arms and world are whatever is current when it runs | Sharding one book across several runs under one world does not exist yet: 3 harness and 2 grading, **2.3 (1.6 to 3.6)**. **Rule 2 sends this to the director with its cost**, because it is beyond one run on this machine | About 4 runs of ~1,200 households, so about 12 arm-hours per draw for three arms, or about 24 h with rule 3's and rule 4's six arms | "Not distinguishable from zero". The family's +£5.24 per household-year has an interval of −£3.34 to +£14.35. At 4,860 households the 95% half-width should be about **£2.1** (1.96 × £75 / √4,860). A true +£3 then reads clear of zero four times in five |

**Why A comes before B whatever the family says.** B is defined in its own pre-registration as two
changes on top of A's type split. If B runs before A, a value-test result moves with both the type
split and the refit, and it cannot be attributed. Running A first makes B a one-variable step.

**What §2's result does to the order.** §2 graded **(a)**: the harness reproduces the published run
to the penny at seed 20260724, so no process or tree state sets that run apart. Had it graded (c),
all three candidates would have waited until that state was found, because no comparison between
runs could be trusted. Under (a) nothing waits on it. Every candidate's family includes seed
20260724, as the rule 1 fix requires.

One reading for the grade, not a ruling: B's pre-registration says to stop if "the value arm's
level leg is set by something other than the belief's offers". §2 shows the published level leg's
extreme came from a high **control** arm at that draw. Whether that meets the clause depends on
which arms carry the belief. That is now established from the code (read 14 Nov, nothing run), below.
So B's R4 should also be read on
the choosing leg (value minus level), where the value arm's belief acts, and not only on the whole
advantage, which carries the control arm's draw.

**Which arms carry the renewal belief (read 14 Nov from the code; nothing run).** The company
has two renewal beliefs, and they are not the same one. The *pricing belief* is
`enriched_churn_estimate` inside `decide_margin`'s `_score`. It is what an offer is chosen on, and
it is what `value_arm_log.believed_p_retain` and so the 0.549 AUC read. The *desk belief* is
`churn_desk.estimate_renewal_churn`. The run loop asks it once per renewal, and it decides the
retention offer.

*At the `churn_roll` family's commit* (`45122d156`, the tree `/var/tmp/vtcr-driver/driver.py` runs
from `/var/tmp/value-test-12-draw`, 3 arms per seed through `run_value_cycle_ab(level_arm=True)`,
which `noise_floor` (`tools/run_value_cycle_ab.py:6759`) calls as its runner):

| Arm | Policy (`tools/run_value_cycle_ab.py`) | Pricing belief | Desk belief |
|---|---|---|---|
| control | `CURRENT_POLICY`, `flat_rules` (:5540) | **Never called.** `renewal_margin_uplift` returns 0 before any scoring (`company/pricing/value_based_renewal.py:1503`) | Called on every renewal (`simulation/run_phase2b.py:2927`). It gates the retention offer (:2950–2954) |
| value | `VALUE_ARM_POLICY`, `value_based` (:5551) | Called on every candidate margin, and the offer is the argmax (`value_based_renewal.py:1167`, belief at :977) | The same as control |
| level | `replace(CURRENT_POLICY, flat_at_level)` at the value arm's realised median (:5569–5580) | Called once, at the fixed level, only to report `p_retain` (`value_based_renewal.py:1119`). The **price** does not read it per renewal. The level itself is the value arm's median, so the belief sets it in aggregate | The same as control |

`renewal_belief_by_ending_term` reaches **none of them at that commit**. `7a7ad95dc` (21 Oct) is
not an ancestor of `45122d156` (8 Oct; `git merge-base --is-ancestor` exits 1), and the name
appears nowhere in that tree.

*Where the flag acts on `origin/main`.* It is a `DecisionPolicy` field
(`company/policy/decision_policy.py:280`). The run loop derives the ending-term type only when the
flag is on (`simulation/run_phase2b.py:4226–4230`) and hands it to the **desk belief** (:4266,
:4287). The desk scales its estimate there (`company/crm/churn_desk.py:179–183`), and the retention
guard reads the scaled number (`run_phase2b.py:4329`). The **pricing belief** never receives it: the
`enriched_churn_estimate` call in `_score` (`value_based_renewal.py:981`) has no ending-term
argument, and nothing in `company/pricing/renewal_rate_chain.py` names it. All three arms are built
from `CURRENT_POLICY` (`VALUE_ARM_POLICY` and the level policy are `replace`s of it). A driver that
switches the flag there therefore switches it on all three arms, and it moves the retention offers
on all three.

**What this does to the three candidates.**
1. **A, as written, cannot move its own bar.** The bar is `belief_against_control_outcomes`
   (`tools/run_value_cycle_ab.py:1815`, reading `value_arm_log` at :1847). That log is the pricing
   belief (`renewal_rate_chain.py:707`, `believed_p_retain = decision.p_retain`), and the flag does
   not reach the pricing belief. Switching the flag on moves the desk belief and the retention
   offers on every arm. The value arm's offers move only second-hand, through who stays.
   *Correction beside the claim:* row A's "the value arm's belief: the policy flag goes from off to
   on" is wrong on both counts. The flag changes the desk belief, and it changes it on every arm.
2. **A also cannot hold "world, book, arms unchanged" against the `churn_roll` family**, because
   the flag needs a tree at or after `7a7ad95dc`. Under rule 1, A's comparator is an off-flag family
   at A's own commit. It is not §7's or §8's 0.549.
3. **The only leg A could attribute is the choosing leg (value minus level)**, and only if the flag
   is on in both of those arms. The control arm's retention offers move too, so the whole advantage
   carries the flag on both sides.
4. **To test what A's prediction claims** (that the type split improves the belief the price is
   chosen on), the ending-term type has to be passed through the rate chain into `_score`. That is a
   supplier build. Under K8 the knowledge page comes first, and the change is B-sized, not 0.9
   points. The alternative is to restate A's bar on the desk belief's own AUC against outcomes.
   **Recommendation:** restate the bar on the desk belief. That is what the flag was graded on
   (0.819 out of sample from 2019), it needs no code, and B can then make the pricing belief carry
   the type as one variable.

**Does §2's high-control level leg meet B's stop clause?** On the code, yes, as far as the
clause's own words go. The level leg is level minus control. The control arm never calls the
pricing belief and makes no belief-chosen offer. So an extreme that came from a high control arm
was "set by something other than the belief's offers": the control arm's draw, plus desk-belief
retention offers that run under the same rule on every arm. The clause should therefore be read
as firing on the level leg and the whole advantage. It does not fire on the choosing leg, where
the only thing that differs between the two arms is the pricing belief's per-renewal selection
around a common level. This is a reading for the grade, not a ruling. It supports reading B's R4 on
the choosing leg.

**The order under each `churn_roll` outcome.** Kill condition 1 is the roll share **< 0.25**. Kill
condition 2 is the flat-arm AUC half-range **< 0.03** (§8). §8's C4 predicts that 1 fires and 2
does not. The ranking takes the row set that matches the grade.

| `churn_roll` outcome | Position | Candidate | What to run, and why in this place |
|---|---|---|---|
| **Both fire** (B's §4: do not build the retrain) | 1 | A | **One draw (about 1.5 h).** The AUC barely moves between draws, so one seed reads it. This tests whether the 2019 type split carries into the value-test years |
| | 2 | C | Goes to the director with its cost (rule 2): the book must be in the thousands, and only households narrow the interval. Re-draws do not |
| | — | B | **Not built.** Its own pre-registration says it can only return "not distinguishable from zero" at this book size. It is revisited only once C exists |
| **1 fires, 2 does not** (§8 C4, the predicted case) | 1 | A | **Twelve `churn_roll` draws (about 19 h).** The AUC moves with who leaves, so A is read against the off-flag's spread across draws, not a single figure |
| | 2 | B | Built only if A's AUC clears the off-flag family by more than the half-range. Otherwise the type split does not carry into these years and B has nothing to build on. R1 to R3 are graded at 272. R4 waits for C |
| | 3 | C | Goes to the director in the same week as B's build (rule 2), because R4 and the thesis both need the thousands. It runs after A, so it carries the belief A settled |
| **2 fires, 1 does not** (roll share ≥ 0.25) | 1 | A | **One draw (about 1.5 h)**, for the same reason as the first case |
| | 2 | B | Built if the roll share is above 0.5 (B's §4 "build it"). Between 0.25 and 0.5 it is built only if A has cleared 0.549 |
| | 3 | C | **Becomes the step 6 sized run, not 4,860 households.** Re-draws now buy precision, so rule 2's 1,200 households at 12 draws (about 72 h with six arms) resolves £3. It needs no director call, and it fits after A and B |
| **Neither fires** | 1 | A | **Twelve draws (about 19 h)**, as in the second case |
| | 2 | B | As in the third case: built if the roll share is above 0.5, or if A has cleared its bar |
| | 3 | C | As in the third case: the 1,200-household sized run at 12 draws, not 4,860 |

In every case, each candidate's prediction is filed before it launches, against the bar in the cost
table. The value is written into the commit that launches it.

## 7. Step 1 graded: the 12-draw family at `45122d156` (read 14 Nov 08:54Z)

All six pairs and their control sidecars are in `/var/tmp/vt12-out/`. The fold is `family_12.json`
(08:00Z). Every member names `45122d156` and world `cdba75ebb9197b33`. The book is 272 households
on every seed *(corrected 15 Nov, §10: 272 billing accounts across 270 households, because two households hold a
second account; folding accounts into households moves this section's figures by at most £0.04 per
household-year and leaves the 4.6% roll share unchanged)*. Seed 11111 reproduces 8 Oct's £11,766.20 to the penny, so the world under the
worktree has not moved. Each seed's per-account columns sum to its seed-level advantage
(reconciliation £0.00 on all 12). The grader is `/var/tmp/vt12-driver/grade.py`, run unchanged. The
per-seed legs, household-year counts and belief scores come from a read-only pass over the same files.

**The per-household-year divisor.** Pairs 4 to 6 carry their own control-arm count: 1,808 to 1,815
household-years (mean 1,811, a spread of 7, or 0.4%). That spread is small, so the six uncounted
seeds are divided by the counted mean of 1,811, and I say so here. The published run's own count is
1,831, which is 1.1% more. The grader's household-level figures use 1,831 / 272, as rule 2 does.

| | Published (8 Oct) | 12-draw family: min to max | Family mean (sd) |
|---|---|---|---|
| Whole advantage, book | **£5,244** | **£5,556 to £12,462** | £9,591 (£1,769) |
| per household-year | **£2.86** | £3.06 to £6.88 | £5.30 (£0.98) |
| Choosing (selection), book | £11,345 | £3,274 to £12,388 | £7,531 |
| per household-year | £6.20 | £1.80 to £6.84 | £4.16 |
| Price level, book | **−£6,101** | **−£3,003 to +£5,560** | £2,060 (£2,355) |
| per household-year | −£3.33 | −£1.66 to +£3.07 | £1.14 (£1.30) |
| Belief's skill: AUC against who left under the flat price | 0.52 (0.40 to 0.64) | 0.530 to 0.572 | 0.549 |
| Believed minus realised retention | −0.22 | −0.21 to −0.22 (believed 0.641 to 0.650; realised 0.848 to 0.862) | −0.21 |

**Which candidate held.** The published £5,244 is **outside** the 12-draw range, **£311 below its
lowest member** (seed 88888, £5,556), or £0.17 per household-year. **2 Nov prediction 1 held: (b),
"too few re-draws", is refuted as the test was written.** The published run therefore differs from
its re-draws in something other than the elasticity seed, so (a) or (c) holds. The margin is narrow
and I say so beside the verdict. The published figure sits 2.46 family standard deviations below the
family mean, and the family's own minimum sits at 2.28. If the family were normal, a draw that low
would come about once in 140. So the whole-advantage figure alone does not refute (b) strongly.

**The split does.** The published choosing leg (£11,345) is inside its 12-draw range. **The published
price-level leg (−£6,101) is not**: it is 3.47 standard deviations below the family mean, and twice as
far below zero as the family's only negative member (−£3,003, seed 44444). The published run is set
apart by how it splits the same households between choosing and level, chiefly the level leg. It is
not set apart by its total. This is what the second test in §2 is for: re-run the published
configuration with the re-draw harness itself, so that (a) and (c) can be told apart.
*(Graded 14 Nov 12:53Z in §2: (a) held. The harness reproduces every arm at seed 20260724 to the penny.)*

**The level-leg prediction (filed 13 Nov) held on both parts.** 1 of 12 re-draws is negative
(predicted at most 1). The leg's spread per household-year (£1.30) is wider than its mean (£1.14),
though only just.

**The belief's skill, per seed.** Against who left under the flat price, the AUC is 0.53 to 0.57
across all 12 seeds. On each seed it rests on about 250 scored renewals, of which 35 to 38 left. The
re-draw barely moves it. The households are the same on every seed, so the 12 seeds do not narrow
8 Oct's sampling interval (0.40 to 0.64), and the reading in §3a stands: the belief sits on a coin.
The run's own `belief_vs_outcome.discrimination_auc` is 0.64 to 0.68. It scores the belief against
outcomes that the value arm's own prices shaped, so it is not evidence of skill on its own, and I do
not use it here.

**Across households, the family says what §3a said.** The mean whole advantage is **£5.24 per
household-year** on the 1,831 divisor (£5.30 on 1,811), with a 95% interval of **−£3.34 to +£14.35** (2,000 resamples of households, each
keeping its 12 draws). It is not distinguishable from zero. The family mean is about twice the
published £2.86. **I do not offer it as the better figure.** Neither figure is distinguishable from
zero, and the published run is the one the page names.

**P6 missed.** Roll noise (within-household variance across the 12 re-draws) is **4.6% of the
per-household variance** of the whole advantage, with an interval of 1.5% to 10.0%. P6 needed at
least half. The re-draw sd is £16.0 per household-year. The between-household sd is £72.9. This
family re-draws only the elasticity assignment, so the measured roll share is a lower bound and the
heterogeneity is an upper bound. As §6 set out, the honest reading is **"not shown"**, not "false".
The next measurement is a `churn_roll` family. Until it reads, rule 2's heterogeneity column governs.
To tell £3 per household-year from zero, a book needs **about 4,860 households on one draw, and
about 4,650 on 12 draws**. Re-draws buy almost nothing. Only households do. A £10 effect needs about
440 households. On this family's numbers, a £3 effect is beyond one run on this machine. Step 6's
book size waits for the `churn_roll` family before it is fixed.

| Prediction | Held? |
|---|---|
| 2 Nov 1: £5,244 stays outside the 12-draw range | **Held**, by £311 |
| 13 Nov, level leg: at most 1 of 12 negative | **Held** (1) |
| 13 Nov, level leg: spread per household-year wider than its mean | **Held** (£1.30 against £1.14) |
| P6: roll noise is at least half the per-household variance | **Missed** (4.6%; a lower bound, so "not shown") |

## 8. The `churn_roll` family: pre-registered 14 Nov 11:45Z, before launch

**What it re-draws, and what it holds.** At `45122d156`, on the same world and the same 272-household
book, the floor is keyed `redraw_key="churn_roll"`: every household's renewal dice
(`customer_events.churn_roll_for_renewal`) are re-rolled from the namespaced stream `floor{seed}_…`,
in all three arms alike. The elasticity draw is **not patched**, so every household keeps the run's own
base seed (20260724), which is the published 8 Oct assignment. Seeds, mode (`all`), pairs per child
process and sidecar fields are §6's. The only code difference is the key. The sidecar also records
`run_base_seed()` after each run, so the grade can show the elasticity was held. Driver and grader are
`/var/tmp/vtcr-driver/`; outputs go to `/var/tmp/vtcr-out/`. The grader is §6's `grade.py` with
the output path changed and kill-condition lines appended. On §7's own files it returns 4.6% and 1
negative level leg, so it reproduces §7. Its "reproduction vs 8 Oct seed 11111" line means nothing
for this family, because seed 11111 here is a churn-roll seed.

**Why 12 members.** Kill condition 1 compares a roll share with §7's 4.6%. The within-household
estimate is only like for like at the same K. Kill condition 2 is a spread of AUCs across draws, and
a half-range from fewer than about 10 draws understates it. Fewer members would not answer the
question, so the family has 12.

**What "the AUC moves" means here, defined before the result.** It is half the min-to-max range of
`belief_against_control_outcomes.discrimination_auc` across the 12 members. The standard deviation is
reported beside it. The elasticity family's own figures are a half-range of **0.021** and an sd of
**0.011**. Kill condition 2 (from the retrain pre-registration, §4) fires if the half-range is
**below 0.03**. Kill condition 1 fires if the roll share is **below 0.25**. The retrain is not worth
building only if **both** fire.

**Predictions** (each a point and a range for the point estimate):

| # | Quantity | Prediction | Reasoning, in one line |
|---|---|---|---|
| C1 | Roll share of per-household variance of the whole advantage | **0.20 (0.08 to 0.45)** | A re-rolled leaver changes tenure, and the advantage scales with tenure. But both arms take the same dice, so most re-rolls move both arms together, and the households that never reach a renewal carry no roll noise. |
| C2 | Flat-arm AUC half-range across the 12 | **0.08 (0.04 to 0.14)**; sd 0.04 (0.02 to 0.07) | With 35 to 38 leavers in about 250 renewals, a re-drawn leaver set moves a weak classifier's AUC by about 0.04 sd. The elasticity family barely changed who left. |
| C3 | Flat-arm AUC mean across the 12 | **0.50 to 0.60** | The belief is the same; only the dice move. |
| C4 | Which kill conditions fire | **1 fires and 2 does not**, so the retrain is **not** ruled out by this family, and the book stays in the thousands | Follows from C1 and C2. |
| C5 | The published £5,244 is **inside** this family's whole-advantage range | inside | The elasticity is the published draw. If (a) of §7 holds, re-rolling the dice spreads around it. |
| C6 | Level legs negative | **at least 6 of 12** (published −£6,101) | Low confidence. §7 found the published run apart in its level leg; if that is the elasticity draw's doing, it survives a re-roll. If fewer than 6 are negative, the level leg is not the published elasticity draw's. |

C1 is the one that decides most. I lean towards kill condition 1 firing, which goes against the
thesis (F11). Refutations: C1 is refuted outside 0.08 to 0.45; C2 is refuted if the half-range is
below 0.04 or above 0.14; C5 and C6 are refuted as written.

**When it runs.** One leg at a time, after §2's published-configuration re-run
(`longjob-vt-published-config-redraw`, pid 1875257, ETA about 13:30Z) has exited. The launch waits
on that pid (`launch_long_job --wait-for-pid`). §7's family took 18 h 46 min for 12 seeds, so this one
should read about **09:00Z on 15 Nov**, before the 16 Nov reset. Its grade is a separate
continuation. It does not build the retrain.

## 9. Candidate A: pre-registered before the `churn_roll` grade (filed 14 Nov 15:55Z)

Filed while `/var/tmp/vtcr-out/` holds no member file, so the `churn_roll` grade cannot have informed
it. The grade picks the shape (§6a's table). Both shapes are filed here, and the launch commit
names which one runs. Nothing is launched: the `churn_roll` family holds the memory.

**What A is, after §6a.** A switches `renewal_belief_by_ending_term` on, on all three arms, because
all three are built from `CURRENT_POLICY`. The flag needs a tree at or after `7a7ad95dc`, and
`45122d156` is not one. So A's comparator is **its off-flag twin at A's own commit** (rule 1), on
the same seeds and the same `churn_roll` key. It is not §7's or §8's family. §6a established that the
flag reaches only the desk belief, which gates retention offers on every arm. It never reaches the
pricing belief that `belief_against_control_outcomes` scores (the bar's AUC, `renewal_rate_chain.py:707`).
**So these predictions are for A as written, and they predict a null.** That goes against the
thesis, and §6a's code reading is what the grade tests (F11). The leg named in item 1 is the **choosing
leg** (value minus level), the only one A can attribute.

**The driver.** `/var/tmp/vta-driver/` is a copy of `/var/tmp/vtcr-driver/`. `VTA_FLAG=1` runs A and
`VTA_FLAG=0` runs the twin, into `/var/tmp/vta-out-flag{0,1}/`. `VTA_SEEDS=1` runs the one-draw shape
(seed 11111), and leaving it unset runs the twelve. The shape is the same on both sides, so it is not a
variable between A and its twin. The key, the seeds, the mode, the pairs per child process and the
sidecar fields are §8's. The diff in the run path is the two `replace` lines:

```diff
+    from dataclasses import replace
+    m.CURRENT_POLICY = replace(m.CURRENT_POLICY, renewal_belief_by_ending_term=FLAG)
+    m.VALUE_ARM_POLICY = replace(m.VALUE_ARM_POLICY, renewal_belief_by_ending_term=FLAG)
```

The level arm is `replace(CURRENT_POLICY, …)` inside `run_value_cycle_ab` (`:5580`). It reads the
module global at call time, so it carries the flag too. Everything else in the diff is bookkeeping:
the docstring, the `FLAG`/`OUT`/`SEEDS` lines, `mkdir`, the fold file name, and two sidecar fields
(`renewal_belief_by_ending_term` and the run's own `arm_identity`). `grade.py` changes only its `OUT`
line. Both diffs are on disk as `driver.diff` and `grade.diff`. **It is one variable, and this was
measured, not argued.** At origin/main, the flagged `CURRENT_POLICY` and the flagged `VALUE_ARM_POLICY`
differ in `name` and `renewal_margin_arm` only, which is the arm identity the run already publishes. The
flagged and unflagged `CURRENT_POLICY` differ in `renewal_belief_by_ending_term` only. The sidecar
records `arm_identity` and the flag for every member, so the grade can show both held on each one.

**The bar, two ways.** As §6a writes it, the bar is 0.549 plus the family half-range: **0.570** on §7's
half-range (0.021), or 0.549 plus §8's measured half-range once that is graded. Under rule 1, the bar
A is graded against is **the twin's mean AUC plus the twin's half-range**. For the one-draw shape it is
the twin's AUC at seed 11111 plus §8's half-range. Both are reported.

| # | Quantity (A minus twin, paired by seed) | One draw (seed 11111) | Twelve `churn_roll` draws | Kill condition |
|---|---|---|---|---|
| A1 | Pricing-belief AUC against who left under the flat price | **0.00 (−0.03 to +0.03)**. A does **not** clear either bar | Mean paired difference **0.00 (−0.015 to +0.015)**; sd of the paired differences ≤ 0.02. A clears **neither** bar | The difference is more than 0.05 on one draw, or the mean is more than the twin's half-range on twelve: the flag reaches the pricing belief, or moves the control arm's leavers more than second-hand. §6a's reading is then wrong and is re-read before B is built |
| A2 | Calibration, believed minus realised (twin about −0.21) | **0.00 (−0.03 to +0.03)**; A at −0.24 to −0.18 | Mean **0.00 (−0.02 to +0.02)** | Outside the range: the flag moved the pricing belief's level, or the desk's retention offers moved realised retention by more than 3 points |
| A3 | Choosing leg (value minus level), £ per household-year | **£0 (−£1.50 to +£1.50)** | Mean paired **£0 (−£1.00 to +£1.00)**. The 95% household-resample interval (§7's method) **contains zero** | More than £3 on one draw, or an interval that excludes zero on twelve: the flag acts on the selection by more than who stays. The prediction is refuted, and the mechanism is found before anyone reads it as the belief improving |

Low confidence on A3's width. §7's choosing leg spans £1.80 to £6.84 across elasticity draws. A
changes the retention offers on tens of renewals, not everyone's elasticity, so I expect a narrower
range, but nothing has measured it.

**What a held null means, and what it does not.** If A1 to A3 hold, A as written says nothing about
the 2019 type split. It says only that the flag does not reach the bar, which §6a predicted from the
code. That is the case for §6a's recommendation: restate A's bar on the **desk belief's** AUC against
outcomes. **GAP:** no run output carries the desk belief per renewal, so this driver cannot read that
bar. Restating the bar needs one sidecar field from the run, which is a run-output change, not a flag.
It is a separate commit with its own pre-registration. I did not add it here, because then the
driver would differ by more than one variable.

**Cost.** Each shape runs twice (A and its twin): about 3 h for one draw, and about 38 h for twelve.
§6a's table priced A once, so its hours double under rule 1.

### 9a. Candidate A on the desk belief: the GAP closed and the bar restated (filed 15 Nov 10:45Z, before any run)

Filed while `/var/tmp/vta-out-flag0/` and `/var/tmp/vta-out-flag1/` are empty. Nothing below has
been run.

**The GAP above is closed by one sidecar field.** `simulation/run_phase2b.py` keeps
`desk_belief_log`: one row per renewal on the decision leg, with `account_id`, `term_start`, `fuel`,
`desk_churn_belief` (the `company_est_pre` that gates the retention offer), `desk_asked` and `left`
(whether the household left at that renewal). It is appended after the roll, beside
`_record_renewal_decision`. `desk_asked` is False where the desk was never asked and the value is
the no-rate-history base rate (`estimate_churn_without_rate_history`). `run_value_cycle_ab` copies
it per arm as `desk_belief_by_arm`. The driver adds it to the sidecar and refuses a tree that does
not emit it (rc 4).

**Pre-registration 1: the sidecar changes nothing else.** With the flag off, a run on the new tree
is byte-identical to the tree before it, apart from the new `desk_belief_log` and
`desk_belief_by_arm` keys and the clocks every run stamps (`generated_at`, `producing_commit`). The
log is written after the roll, draws no random number and is read by nothing in the run.
`tests/simulation/test_desk_belief_log_is_never_read_by_the_run.py` holds the last part: the name
appears at its definition, its one append and the results dict, and nowhere else. A mutation that
reads it (`len(desk_belief_log)`) turns the test red. **Not run: a byte comparison.** The run that
would show it costs about 3 h, and the twin below is that run's flag-off side, so it is not run
separately. The cheaper evidence is the construction plus the test. *If a later grade finds the
twin's money columns differ from a flag-off run on the parent tree, this prediction is refuted, and
the sidecar is the first suspect.*

**The shape: a pair, not one draw.** §9's one-draw shape (`VTA_SEEDS=1`) cannot run. `noise_floor`
refuses fewer than two seeds (`tools/run_value_cycle_ab.py`, "a noise floor needs at least two
seeds"), and the driver's pairing loop would have failed on `pair[1]` first. *Correction beside §9's
claim:* the one-draw shape and its "about 3 h" cost were never runnable. The smallest runnable shape
is the first pair, `VTA_SEEDS=2` (11111 and 22222), in one child process per side. **Seed 11111 is
the graded draw**, as directed. Seed 22222 is read as a second paired draw and does not change the
verdict on 11111. Cost: about 3.2 h per side (1,140 min over six pairs), so about 6.3 h for A and its
twin back to back.

**The twelve-draw launch at 09:44Z was stopped at 10:20Z.** It was 36 minutes in, with no member on
disk. Its driver could not read the desk belief, so as §9 says, it could only return A's predicted
null. The delivery seat's direction (`candidate-a-reads-the-desk-belief-per-renewal`, written 09:25Z)
asks for the small run first. To reverse: re-run the two `launch_long_job` lines recorded in §10, at a
tree carrying `desk_belief_log`.

**Pre-registration 2: A's bar, restated on the desk belief.** The quantity is the AUC of the desk
belief against who left. It is read on the **control arm** (flat price, where the desk belief is
the only belief acting), over renewals with `desk_asked` true, in the primary window `term_start` from
2019-01-01 on. That is the window in which the flag's type split was graded (0.819 out of sample) and
the desk belief measured backwards (0.333 on 268 desk states). The secondary window is all years.
The value and level arms are printed and not graded. Grader: `/var/tmp/vta-driver/grade_desk.py`,
written before launch. AUC is P(a leaver's belief > a stayer's), with ties at 0.5.

| # | Quantity, seed 11111, control arm, 2019 on | Predicted | Kill condition |
|---|---|---|---|
| D1 | Twin's desk-belief AUC | **0.42 (0.30 to 0.55)**: at or below chance, as the 0.333 reading says | Above 0.60: the desk belief already ranks leavers on this book, so the 0.333 reading does not carry to the run. The case for A falls, and A is re-read before anything else |
| D2 | A's desk-belief AUC | **0.62 (0.48 to 0.80)** | — |
| D3 | A minus twin, paired | **+0.20 (+0.05 to +0.40)** | Under +0.05: the type split does not make the belief rank leavers in the run, whatever it did out of sample |
| D4 | Leavers among the graded rows | **25 to 60** per side | Under 20: the AUC carries a half-width over about 0.12, and the grade reads "I cannot yet say" whatever D3 shows |

**The bar.** A clears it on seed 11111 when D3 > **0.112** (§8's AUC half-range, which is the
conservative allowance; a paired difference should be far tighter) **and** A's AUC is above 0.5. §9's
A1 to A3 are graded too, as filed, on the pricing belief and the choosing leg. They still predict a
null.

**The twelve-draw decision, written before the run.**
- A clears on 11111 and 22222 has the same sign: **the twelve-draw A family is earned**, to size the
  paired effect. It is launched at the same tree, behind the headroom check.
- D3 under +0.05 on both seeds: A is closed with no rank gain in the run, and **no twelve-draw**.
- Anything between: "I cannot yet say". There is no twelve-draw on that alone. The grade records what
  would separate the readings.

## 10. The `churn_roll` family graded against §8 (read 15 Nov 09:40Z)

All six pairs and their control sidecars are in `/var/tmp/vtcr-out/`. The fold
(`family_12_churn_roll.json`, 06:45Z) returned rc 0 and names `45122d156` on every member. **The
elasticity was held:** `run_base_seed_after_run` is 20260724 on all 12 controls. **The dice moved:**
`draws_redrawn` is 209 to 232 on every seed, under `redraw_key="churn_roll"`.

**The grader did not run unchanged, and why.** `/var/tmp/vtcr-driver/grade.py` stops with
`KeyError: 'C5_2'`. Once the dice are re-rolled, a household can leave and rejoin as a second
account in one arm and not the other. `C5_2` appears in seed 20202's and 55555's value arms only,
`C3_2` in 11111's and 99999's control arms only, and `C6_2` in 11111's control arm only. §7's files
never showed this, because its dice were held. The grader's unit is the household, so
`grade_hh.py` (beside it, one hunk) folds each account into its household (`C5_2` into `C5`), and an
account absent from an arm counts as £0 in that arm. Nothing else changes. Two checks show that
the fold neither drops nor invents money:
- each seed's household columns still sum to its seed-level advantage, with a reconciliation of
  **£0.00 on all 12**;
- on §7's own files the fold returns the same **4.6%** (1.5% to 10.1%) and £5.28 per household-year,
  against £5.24. So §7 is not moved by it, and the two families compare like for like.

The fold finds 270 households, not 272: §7's "272" was billing accounts, and it is corrected beside
the claim. The per-household-year divisor stays at rule 2's 1,831 / 272 so the families stay
comparable.

| | Published (8 Oct) | `churn_roll` family: min to max | Mean (sd) |
|---|---|---|---|
| Whole advantage, book | **£5,244** | **£4,299 to £22,868** | £14,136 (£5,592) |
| Choosing (selection), book | £11,345 | £2,960 to £17,036 | £9,418 (£4,774) |
| Price level, book | **−£6,101** | −£3,192 to +£16,393 | £4,718 (£5,560) |
| Flat-arm AUC (the belief against who left under the flat price) | 0.52 | **0.494 to 0.719** | 0.574 (0.063) |

**Across households,** roll noise (the within-household variance across the 12 re-rolls) is
**42.7% of the per-household variance** of the whole advantage, with an interval of 30.0% to 53.6%
(2,000 household resamples). That is 0.39 without the three households that rejoin, so the fold
does not carry it. The roll sd is £49.6 per household-year and the between-household sd is £57.5.
The mean is **£7.78 per household-year (£0.69 to £14.95)**. **I do not read the interval clearing
zero as established**, because this family holds the elasticity at one assignment, just as §7 held
the dice. Each family's interval leaves out the other family's source of noise, and no run has
re-drawn both together.

| Prediction (§8) | Predicted | Measured | Held? |
|---|---|---|---|
| C1 roll share | 0.20 (0.08 to 0.45) | **0.427** (0.30 to 0.54) | **Held**, at the top of its range. The point missed high, by more than twice. |
| C2 AUC half-range; sd | 0.08 (0.04 to 0.14); 0.04 (0.02 to 0.07) | **0.112; 0.063** | **Held** on both |
| C3 AUC mean | 0.50 to 0.60 | **0.574** | **Held** |
| C4 kill conditions | 1 fires, 2 does not | **Neither fires** | **Refuted** on kill 1. The consequence C4 named still stands: the retrain is not ruled out, and the book stays in the thousands |
| C5 £5,244 inside the range | inside | inside, £945 above the minimum | **Held** |
| C6 level legs negative | at least 6 of 12 | **2** (11111, 33333) | **Refuted**. As C6 was written, the published run's negative level leg is **not the published elasticity draw's**. |

**What follows, and what does not.**
- **The retrain (pre-registration §4) is not stopped by this family.** Neither stop condition holds.
  Its build condition is "roll noise above half, or the book resized to the thousands". Roll noise
  is not above half (0.43; the interval reaches 0.54). So the build rests on the book.
- **Step 6's book size.** Telling a £3 effect per household-year from zero takes **about 5,030
  households on one draw, or 3,060 on twelve**. §7's figures were 4,895 and 4,688. Re-draws now buy
  about 40% fewer households, where under §7 they bought almost nothing. A +£6 effect, R4's middle,
  takes about **1,260 households on one draw, or 770 on twelve**. The book is in the thousands for £3
  and in the high hundreds for £6, on twelve draws. Neither is the 272 book.
- **The published level leg (−£6,101) sits outside both families.** It is below this family's
  minimum (−£3,192) and 1.95 sd under its mean. It is also outside §7's range. One family re-draws
  the dice and the other the elasticity, and neither produces it. The published run is the only
  configuration with **both** at their base draws. **I cannot yet say** whether that is an
  interaction between the base dice and the base elasticity or a tail draw. A family that
  re-draws both together is the test, and §7's mean (£9,591) against this family's (£14,136) says
  the base dice are the unfavourable ones.
- **The AUC reading.** Re-rolling who leaves moves the belief's flat-arm AUC by an sd of 0.063, about
  what 35 to 38 leavers in 250 renewals allow. So the published 0.52 is one draw from a spread
  centred on 0.574. It is above chance across the dice on this book, but the households are the
  same on every seed, so that is not an interval for the population.
- **Candidate A's bar (§9).** On §8's measured half-range, §6a's bar becomes 0.549 + 0.112 =
  **0.661**. On the one-draw shape, the bar is the twin's seed-11111 AUC plus 0.112. A one-draw
  comparison cannot see a difference smaller than about 0.1. A and its twin share the dice, so the
  paired difference should be far tighter than the half-range. That is §9's A1 prediction, and it
  should be read paired, not against the bar.

**What this grade does to §6a's "neither fires" row (read 15 Nov, after the grade).** That row sends
A first, on twelve draws. B is built only if A clears its bar, because the roll share (0.43) is not
above 0.5. For C the row says "the 1,200-household sized run at 12 draws, not 4,860". **The second
half of that is refuted by this family's own variances.** At 12 draws a £3 effect needs about
**3,060 households**, not 1,200. A 1,200-household book at 12 draws resolves about **£4.80** per
household-year, and about £6.10 on one draw. So C is still beyond one run on this machine. Under
rule 2 it goes to the director with its cost, as in §6a's first two rows, and it is raised in
`for_the_director` (`the-value-test-s-sized-book-candidate`) with a recommendation. A and B do not wait on that.

**Candidate A launched, 15 Nov 09:44Z: the twelve-draw shape.** §10 lands in §6a's "neither fires" row, so
twelve draws run, not one. A and its twin both run in the worktree `/var/tmp/value-test-candidate-a`,
pinned at `ed371fa35`, which has `7a7ad95dc` as an ancestor. A (`VTA_FLAG=1`) runs as
`longjob-value-test-candidate-a-flag1` into `/var/tmp/vta-out-flag1/`. Its twin (`VTA_FLAG=0`)
runs as `longjob-value-test-candidate-a-flag0` into `/var/tmp/vta-out-flag0/`. The twin is queued
behind A's pid, because each peaks at about 11.5 GB and the two do not fit together. They take about
19 h each, so the twin should read about **Tue 17 Nov 05:00Z**. The driver and grader are §9's,
unchanged. The grader inherits §10's household fold, because re-rolled dice create the same
second accounts. A1 is read paired by seed, not against the 0.661 bar.

*Stopped 15 Nov 10:20Z, 36 minutes in, with no member written. The pair-shaped run on the desk belief
goes first (§9a).*

### 10a. The desk pair: the flag-on member was written, and the fold killed the unit before the twin ran (16 Nov 04:50Z)

**What happened.** `longjob-value-test-candidate-a-desk-pair` launched 15 Nov 13:35Z as §9a's pair
shape: `VTA_FLAG=1` then `VTA_FLAG=0`, back to back. The flag-on side wrote its member and sidecar
(`/var/tmp/vta-out-flag1/member_11111_22222.json`, `control_11111_22222.json`, 16 Nov 00:11Z). Its
driver then called `--fold` on one member, and `fold_floors` refused it ("a fold needs at least two
floor runs; got 1"). The driver exited 1, so the `&&` never started the twin. **Nothing about A's
own run is wrong**: both seeds were drawn (838 redrawn each), `renewal_belief_by_ending_term` is True,
and `producing_commit` is `41734bbe71` on both. The defect was the driver's: it always folded, and a
fold of one pair is a copy that the fold rightly refuses.

**The fix, outside the repo.** `/var/tmp/vta-driver/driver.py` now returns 0 with "one pair, no
fold" when it holds fewer than two members. The twelve-draw path is unchanged, and the pre-fix copy
is kept beside it as `driver.pre-nofold.py`. The fixed driver run against the written flag-on member
(`VTA_FLAG=1 VTA_SEEDS=2`, from the worktree) prints "pair [11111, 22222] already on disk, kept" and
exits **0**, in 0.06 s.

**The twin, relaunched 16 Nov 04:38Z.** `VTA_FLAG=0 VTA_SEEDS=2`, from the same worktree at the same
`41734bbe71`, as `longjob-value-test-candidate-a-flag0-twin` through `launch_long_job` (its exit status
is the run's own), writing `/var/tmp/vta-out-flag0/member_11111_22222.json`. It went to the
launcher's queue (`longjob-value-test-candidate-a-flag0-twin-queued`). At launch, the head-green
census (12.0 GB) and the sim runner (7.1 GB) were resident against an 11.5 GB peak, so it starts when
they leave. The flag-on side is not rerun. Grading is `grade_desk.py` against D1 to D4 as filed.

**Two corrections beside §9a's claims, read off the written sidecar:**
- *The book.* §9a costs the pair on the 272-household book. At `41734bbe71` the book is **767
  billing accounts and 5,673 control-arm household-years** on seed 11111 (5,814 on 22222). §7 and
  §8 had 1,831. The book grew with the tree, so A and its twin share it, and the pairing holds. But
  A is graded on a different book from §7, §8 and §10, and the 0.112 half-range allowance was
  measured on the smaller one. Expect D4's leaver count to sit **above** its 25 to 60. That is a
  bigger sample, not a kill.
- *The cost.* §9a said about 3.2 h per side. The flag-on side took **38,144 s (10.6 h)**: six
  arm-runs (two seeds, three arms) at about **1.77 h per arm-run** on about 5,700 household-years.
  The unit also shared the box with cycles that deferred to it. So the twin should read about 11 h
  after it starts.

**What the cost does to step 6 (sequencing, read now, before A's grade).** The settlement budget
(`SETTLEMENT_CUSTOMER_YEAR_BUDGET`, 7,700 household-years) is the "1,200-household" book. At 1.77 h
per 5,700 household-years, an arm-run there takes about 2.4 h. `noise_floor` runs three arms per
draw (`level_arm=True`), so the ruling's twelve-draw book is about **36 arm-runs, or 86 h**, run
serially because each peaks near 11.5 GB. If A earns its twelve-draw family under §9a's rule, that
family is about 64 h at this book (36 arm-runs at 1.77 h), and it runs first. **Together that is
about 150 machine-hours from the twin's end. Step 6 then reads around 23 to 24 Nov, past its 22 Nov
commitment.** If A does not earn the family, step 6 alone reads around 20 Nov. *Prediction, filed
before A's grade:* A does not clear on both seeds (§9a's D3 predicts +0.20, but §9's A1 to A3 predict
a null on the pricing belief, which is the belief step 6's value arm chooses with). So step 6 most
likely goes straight after the twin and meets its date. If A does clear, the order stands as
ruled and the date slips by about 3 days. That slip is the delivery seat's to say in the stretch log,
not a reason to change the ruled order.

**Step 6's pre-registration waits for A's grade, because the ruling makes A its prior.** It goes in
`docs/staging/` before launch, with the difference expected per household-year and the resolution
this book earns. The §10 figure is £4.80 at 1,200 households on twelve draws, measured on the
270-household book's variances; it is restated on A's 767-account variances if they differ.

*Correction beside §10a's step-6 cost, read 16 Nov 05:00Z from the published book and A's sidecar; nothing run.*
**Step 6's book is A's book, not a larger one.** The published run commits **7,699.3 of the 7,700**
customer-year budget (`site/data/book_growth.json` `settlement`, generated 16 Nov 04:21Z) and refuses
387 of 597 funnel wins to stay inside it. So the default run is already the budget-bound book that the
ruling calls "the 1,200-household book". The 7,700 counts customer-years committed from each win to the
horizon. A's 5,673 and 5,814 control-arm household-years are what was realised after leavers exit.
They are the same book measured two ways, and §10a's scaling from 5,700 up to 7,700 counts the budget
twice. Three things follow:
- **Cost.** A step-6 arm-run takes about 1.77 h, as A's did, not 2.4 h. Twelve draws are 36 arm-runs,
  so about **64 h, not 86 h**.
- **The run.** Step 6 needs no book knob and no new driver. It is the twelve-draw `churn_roll` family
  at A's tree on whichever belief A's grade leaves current. That is exactly one side of A's own
  twelve-draw family: `/var/tmp/vta-driver/driver.py` with `VTA_FLAG` set and `VTA_SEEDS` unset.
  The driver keeps any pair already on disk, and pair 11111/22222 is written on both sides once the
  twin ends. So **five pairs, 30 arm-runs, about 53 h** remain on either side. If A earns its family
  (§9a), its flag-on half *is* step 6 on A's belief. The ruled order holds, and step 6 reads when that
  half folds, not after the whole family. The flag-off half, which sizes A's paired effect, runs after it.
  From the twin's end, step 6 reads in about 2.5 days either way, which is inside the 22 Nov commitment.
  §10a's "slips by about 3 days" is withdrawn.
- **Resolution.** "1,200 households" was rule 2's estimate of how many households the budget holds.
  A's book settles **767 to 776 billing accounts** in the window. Per-household variance as in §10
  gives a 12-draw resolution of about £4.80 × √(1,200 / 767) ≈ **£6.00** per household-year, not £4.80.
  This is a prediction. The step-6 pre-registration restates it on A's own per-household variances
  before launch. The ruling's choice (one unsharded book at the budget, no sharding) is unchanged. Only
  the figure it was quoted with moves.

### 10b. Candidate A graded against its twin: it clears §9a's bar, and the money cannot tell it from zero (17 Nov)

**What was read.** The twin wrote `/var/tmp/vta-out-flag0/member_11111_22222.json` and its sidecar on
16 Nov at 20:25Z. Both sides have `producing_commit` `41734bbe71`, and the flag is False on the twin and
True on A for every seed. `arm_identity` differs in `name` and `renewal_margin_arm` only, on all four
sidecars. `/var/tmp/vta-driver/grade_desk.py` ran unchanged, as filed. Seed 11111 is graded, and 22222
is read beside it.

| # | Seed 11111, control arm, 2019 on | Predicted | Measured (22222 beside it) | Held? |
|---|---|---|---|---|
| D1 | Twin's desk-belief AUC | 0.42 (0.30 to 0.55) | **0.361** (0.380) | **Held**. The kill (above 0.60) does not fire |
| D2 | A's desk-belief AUC | 0.62 (0.48 to 0.80) | **0.819** (0.826) | **Missed high** |
| D3 | A minus twin, paired | +0.20 (+0.05 to +0.40) | **+0.458** (+0.446) | **Missed high**. The kill does not fire, and the bar (> 0.112, A > 0.5) is cleared on both seeds |
| D4 | Leavers among graded rows | 25 to 60 per side | **52 and 53** (48 and 48) | **Held**. §10a expected more on the bigger book. It did not come |
| A1 | Pricing-belief AUC, A minus twin | 0.00 (−0.03 to +0.03) | **+0.0004** (+0.015) | **Held** |
| A2 | Calibration, A minus twin; A at −0.24 to −0.18 | 0.00 (−0.03 to +0.03) | **−0.011** (−0.006); A at **−0.243** (−0.274) | **Missed** on its level clause: the twin itself sits at −0.232, not −0.21. The paired clause held |
| A3 | Choosing leg, A minus twin, £ per household-year | £0 (−£1.50 to +£1.50) | **−£0.05** (−£0.39) | **Held** |

Four held and four missed, with the fourth miss being §10a's *"A does not clear on both seeds"*,
which is refuted. Both prediction misses on the desk belief are in A's favour. A's in-run AUC (0.819)
matches the out-of-sample figure from the flag's build commit (`7a7ad95dc`, 0.819 [0.757, 0.877]) to
three places. That is two independent windows agreeing, not the same rows twice. The flag's input is
the previous tariff type (`ending_term_type`, `run_phase2b.py:4231`), which a supplier holds on its own
books, so the ranking crosses no wall. On the value and level arms, A ranks at 0.84 to 0.88 and the
twin at 0.17 to 0.26 (fewer leavers, 16 to 31). There the flat belief ranks stayers above
leavers. That is printed, not graded.

**The money, in £ per household-year, paired by household.** Written as
`/var/tmp/vta-driver/grade_paired_gbp.py` after D1 to D4 had printed and before any money pairing was
read. The unit is the household (accounts folded as in §10). The divisor is the twin's control-arm
household-years on each seed (5,676 and 5,823). The interval is from 2,000 household resamples, each
keeping both seeds. This is **supplier net margin**, the same quantity the value test's whole advantage
has always been. It is not household value.

| A minus twin | 11111 | 22222 | Mean (95%) | Households moved |
|---|---|---|---|---|
| **Control arm (the flat-rules book with A's desk belief)** | +£0.17 | +£0.10 | **+£0.14 (−£1.15 to +£1.37)** | 261 of 780 |
| Value arm | −£1.32 | −£1.10 | **−£1.21 (−£2.35 to −£0.38)** | 101 |
| Level arm | −£1.27 | −£0.71 | −£0.99 (−£2.49 to +£0.40) | 130 |
| Whole advantage (value minus control) | −£1.49 | −£1.20 | −£1.35 (−£3.03 to +£0.13) | 284 |
| Choosing leg (value minus level) | −£0.05 | −£0.39 | −£0.22 (−£1.78 to +£1.35) | 150 |

**The grade, as asked: we cannot tell.** Better ranking of leavers by the desk is worth **+£0.14 per
household-year on the flat book, with an interval of −£1.15 to +£1.37 that spans zero**. On the value
arm the flag *costs* £1.21, and that interval excludes zero on two draws. **I cannot yet say why.**
The candidates are these. The retention offers move to households the value arm's pricing was
already keeping. Or the value arm loses the offers it used to make by accident to households that left
and were worth keeping. Or it is the two draws' dice. The 101 households that moved on the value arm are where to look, and
nothing here separates the three. Two draws hold the same 780 households, so the interval is over this
book's households, not a population.

**What §9a's rule does with this.** A clears on 11111, and 22222 has the same sign: **A's twelve-draw
family is earned.** Under §10a's correction, its flag-on half *is* step 6 on A's belief. The rule was
written on the ranking alone, and the money does not overturn a ranking that clearly moved. But the
money says the twelve-draw family is now the test of whether the ranking is *worth* anything, not just
a test of its size. Step 6 below is written that way.

## 11. Step 6 pre-registered: A's belief on twelve `churn_roll` draws (filed 17 Nov, before launch)

Filed with `/var/tmp/vta-out-flag1/` holding only pair 11111/22222. Nothing below has run.

**The run.** `/var/tmp/vta-driver/driver.py` with `VTA_FLAG=1` and `VTA_SEEDS` unset, at
`41734bbe71`, in the worktree `/var/tmp/value-test-candidate-a`, through `launch_long_job`. The driver
keeps the pair on disk and runs **five pairs, 30 arm-runs, about 53 h** (1.77 h per arm-run, §10a),
then folds twelve members. After it comes the flag-off half (`VTA_FLAG=0`), the same five pairs, which
sizes A's paired effect. Each peaks near 11.5 GB, so it launches behind the headroom check and **not
while `d5-land8` holds the box**. The continuation `value-test-step-6-pre-registered-and-launched-after-a-grade`
does the launch.

**Resolution, restated on A's own variances (§10a asked for this).** A's pair gives 784 households
at 7.33 household-years each. Roll sd is £55.1 and between-household sd is £60.0 per household-year,
and the roll share is 0.46 (twin 0.41). On twelve draws, the effect this book resolves at 80% power
(2.8 standard errors) is **£6.21 per household-year** (twin's variances: £6.67), against §10a's
predicted £6.00, which holds. A £3 effect needs about 3,360 households on twelve draws. Two draws
estimate a variance poorly, so these are restated again on the twelve.

| # | Quantity (A's family, twelve draws, £ per household-year on the control-arm divisor) | Predicted | Kill condition |
|---|---|---|---|
| S1 | Whole advantage, mean | **+£4 (−£2 to +£10)**. The pair gives £5.15 and £0.59. The twin's pair sits about £1.35 higher, and §10's family mean on the old book was £7.78 | — |
| S2 | Its 95% household-resample interval | **Spans zero**, width about ±£6 | An interval that excludes zero is a claim, and goes to the page only with the twin half's paired figure beside it |
| S3 | Desk-belief AUC on the control arm, 2019 on, across draws | Mean **0.80 to 0.84**, sd **under 0.04** | Mean under 0.70: the pair's 0.82 was its dice, and §10b's clearance is re-read |
| S4 | Control arm, A minus twin (once the flag-off half folds) | **£0 (−£1 to +£1)**, interval spans zero | Above +£1 with an interval clear of zero: the ranking is worth money on the flat book, and that becomes the lead |
| S5 | Value arm, A minus twin | **−£1 (−£2 to £0)**: the pair's cost survives | Interval spans zero: the pair's −£1.21 was two draws' dice |

**What follows from each reading.** If S2 spans zero (as predicted), the page keeps its lead and
says "we cannot tell" with the £6.21 resolution beside it. Per-customer inference is not shown to
beat the flat book at this book size, and C's sized book (`the-value-test-s-sized-book-candidate`) stays
the director's call. If S5 holds, the desk's better ranking costs money on the value arm. The
mechanism is found before B is built, because B builds on the same belief.

**Launched 17 Nov 06:10Z, as filed.** `longjob-value-test-step-6-flag1` through `launch_long_job`
(`VTA_FLAG=1`, `VTA_SEEDS` unset, cwd `/var/tmp/value-test-candidate-a` at `41734bbe71`, declared peak
11,800 MB, admitted at 18,593 of 23,010 MB). It went to the launcher's queue
(`longjob-value-test-step-6-flag1-queued`) because a commit gate was pending: landings come before
experiments. It starts when that gate ends. Artefact: `/var/tmp/vta-out-flag1/family_12_churn_roll.json`;
log `/var/tmp/longjob-value-test-step-6-flag1.log`. The flag-off half launches after it exits, not
beside it. To reverse: `systemctl --user stop` the unit; the members already written are kept.

**Paused at the pair-2 boundary for the D5-on book (armed 17 Nov 11:00Z; direction focus
`the-d5-book-runs-at-step-6s-next-pair-boundary`).** sim-runner yields to any resident long job, so no
book carrying D5 (341df4965) could run until step 6 ended, about 50h away. Transient unit
`d5book-pause-watch` (`/var/tmp/d5book-pause/watch.sh`, log `watch.log` beside it) waits until
`member_33333_44444.json` and `control_33333_44444.json` are both on disk, stops this unit, waits for the
next `docs/staging/run_complete_*.md`, and relaunches the unit with the same argv, `VTA_FLAG=1`, cwd,
peak and question. The driver skips pairs already on disk, so the family is split at a pair boundary
(pairs 1 and 2 before the book, 3 to 6 after it) and nothing is redrawn. A pair-3 child killed at the stop
loses minutes and restarts from its first seed. The grade must read the relaunch line in
`/var/tmp/longjob-value-test-step-6-flag1.log` ("pair [11111, 22222] already on disk, kept", and the same for
33333_44444). Reverse: `systemctl --user stop d5book-pause-watch`; if step 6 is already stopped, run the
relaunch block of `watch.sh` by hand.

## 12. Why the value arm loses £1.21 on A's belief: pre-registered 17 Nov 14:40Z, before the read

**What has been read so far.** Only the files' schema: the key names in the member and control
sidecars, and one flag-on row (C5, 2016) to learn the shape. No A-versus-twin pairing of any decision
or money field has been read. The inputs are the two pairs on disk and nothing else:
`/var/tmp/vta-out-flag{0,1}/member_11111_22222.json` and `control_11111_22222.json`. Nothing is launched.

**What a "decision" is here.** The value arm's decision for a household is its renewal price:
`chosen_margin_gbp_per_mwh` in `renewal_decisions_by_arm["value_arm"]`, one row per account, commodity
and `term_start`. A *retention offer* is a lower margin than the other run chose at the same renewal;
a *withdrawn offer* is a higher one. The outcome at each renewal is `renewals[].outcome` in
`value_arm_decisions_by_account`, with its `p_retain` and `roll`. Money is the household's value-arm net
(accounts folded, absent = £0, as in §10). The divisor is the twin's control-arm household-years on each
seed, as in §10b.

**The partition, fixed before the read.** Each of the 101 households whose value-arm money moved goes
into exactly one bucket, and its whole money difference (A minus twin) goes with it:
- **(a) Offers move to households already kept.** No renewal outcome differs between A and the twin,
  and at least one renewal price differs. The money is a price change on someone who stayed (or left)
  either way. It has both signs: A cutting a stayer's price is a loss, and A raising it is a gain.
- **(b) Accidental offers to leavers worth keeping are lost.** At least one renewal outcome differs, and
  at the first renewal where it differs, the price moved in the direction that explains the flip (A
  dearer and the household left in A only, or A cheaper and the household stayed in A only). The
  mirror (A keeps someone the twin lost) is a gain and nets inside (b).
- **(c) The dice.** An outcome differs, but at the first differing renewal the price did not move, or
  moved against the flip, or the `roll` itself differs between the runs. That flip is not the price's
  doing. Separately from the partition, for (b)'s flips I also report the expected part
  (|Δ`p_retain`| × the household's money difference) against the realised part. The difference between
  them is the dice *inside* (b), and it is printed beside the partition, not folded into it.
- **Unexplained.** The money moved, but no renewal price and no outcome differs (arrears, bills,
  successor accounts, or something not named here).

**Prediction (shares of the −£1.21; they sum to 100%).**

| Bucket | Point share | Range | Why I expect it |
|---|---|---|---|
| (a) | **40%** | 10% to 75% | A ranks leavers far better (D2 0.82), so its margin logic is more confident about who stays. I expect it to move prices on households that do not change their outcome, in both directions, with net loss |
| (b) | **35%** | 5% to 70% | When the twin ranked badly (D1 0.36), its "offers" landed by accident on some households worth keeping. A withdraws them and some leave |
| (c) | **15%** | 0% to 40% | Two draws, about 100 households: a handful of flips worth £100 to £300 each can carry a £1 per household-year mean |
| Unexplained | **10%** | 0% to 30% | The value-arm net carries arrears and successor-account lines that a renewal price does not touch |

**Kill conditions.** If unexplained is above 30%, the partition is the wrong frame, and the next change is
to find what the arm moved other than price, not a lever. If (c) is above 50%, the reading is "we cannot
tell, the dice" and step 6's S5 is the test. If (a) and (b) together are under 40%, neither candidate
§10b named is the mechanism.

**What each reading would make the next change.**
- (a) leads: the value arm spends A's better belief on discounts to households it already keeps. The next
  change is the **objective**, which treats a retained household as a margin to buy back rather than as
  already kept.
- (b) leads: the value arm prices up households its better belief now calls safe, and they leave. The
  next change is the **lever**, so that confidence in retention does not set a price that the elasticity
  then punishes.
- (c) leads: **we cannot tell, the dice**. Step 6's S5 decides it.

### 12a. Read against the prediction (17 Nov 15:30Z, after `da4cb352e` filed it)

**The script.** `/var/tmp/vta-driver/attribute_value_loss.py`, written after §12 was committed and
before it was run. It reproduces the total, **−£1.207**, and the count of **101** households whose
money moved. 177 households had at least one decision move. Its per-household rows are in
`value_loss_attribution_v2.json` beside it.

**A defect in the first run of the script, corrected before grading.** v1 (kept as
`attribute_value_loss.v1-mean-margin.py`) compared each run's average margin over the fuels *it*
priced. A dual-fuel household that left at its electricity renewal never had its gas renewal priced in
that run. So the twin's average included a thin gas margin that A's lacked, and v1 read that as "A
dearer". On v1, (b) took 90%. v2 compares only the fuels both runs priced at the same renewal. The
grade is v2's.

| Bucket (§12's definitions) | Predicted | Measured (v2) | Households (seed-rows) | Held? |
|---|---|---|---|---|
| (a) price moved, no outcome moved | 40% (10 to 75) | **4.5%** (−£0.054) | 301, of which 42 moved money | **Missed low** |
| (b) outcome flipped with the price | 35% (5 to 70) | **19%** (−£0.229) | **1** (PROS-2017-0371, +£0.25/MWh) | Held in range. But it is one household whose price moved by 0.3%, so this is (c)-shaped too |
| (c) outcome flipped, not by the price | 15% (0 to 40) | **72%** (−£0.865) | 10 | **Missed high. The (c) kill fires as written** |
| Unexplained | 10% (0 to 30) | **4.9%** (−£0.059) | 128 (one OCC account carries −£705) | Held |

**Each flip, one row per household.** The roll is identical in A and the twin on every row. Δmargin is A
minus twin over the fuels both priced, in £/MWh. The money difference is A minus twin, in £.

| Seed | Household | Date | Δmargin | A | Twin | p (A / twin) | Roll | £ |
|---|---|---|---|---|---|---|---|---|
| 11111 | SYN-2016-557 | 2018-12-02 | 0 | churned | renewed | 0.527 / 0.581 | 0.945 | −3,892 |
| 22222 | SYN-2016-604 | 2017-12-25 | 0 | churned | renewed | 0.275 / 0.279 | 0.222 | −2,674 |
| 11111 | PROS-2017-0371 | 2018-11-29 | +0.25 | churned | renewed | 0.527 / 0.550 | 0.906 | −2,601 |
| 22222 | SYN-2016-458 | 2018-10-09 | −4.50 | churned | renewed | 0.441 / 0.455 | 0.997 | −1,087 |
| 22222 | PROS-2017-0318 | 2018-10-07 | −1.50 | churned | renewed | 0.513 / 0.543 | 0.669 | −976 |
| 22222 | SYN-2016-498 | 2018-10-31 | 0 | churned | renewed | 0.529 / 0.547 | 0.967 | −629 |
| 11111 | SYN-2016-581 | 2018-12-10 | 0 | churned | renewed | 0.288 / 0.388 | 0.797 | −571 |
| 11111 | PROS-2016-0263 | 2018-09-16 | 0 | churned | renewed | 0.579 / 0.634 | 0.676 | −85 |
| 11111 | SYN-2016-468 | 2018-10-17 | 0 | churned | renewed | 0.519 / 0.538 | 0.707 | −23 |
| 11111 | SYN-2016-315 | 2018-07-10 | 0 | churned | renewed | 0.602 / 0.616 | 0.640 | 0 |
| 11111 | SYN-2016-215 | 2020-05-01 | −3.75 | renewed | (no renewal) | 0.349 / — | 0.076 | −14 |

The 42 bucket-(a) households whose money moved are price moves on households whose outcome did not
change. In 567 of the 569 renewals priced differently, A was **cheaper** (by £2.94 to £6.37/MWh on
average). Those cost £618 in all.

**Why bucket (c) is not the dice, and the label is corrected here.** §12 named (c) "the dice" on the
assumption that a flip the price does not explain is luck. In this pair the dice are **held**: every
flip has the same roll in both runs. A flip at the same roll and the same price is a *decision* that
the sidecar does not record, not a re-roll. The sign settles it. At identical rolls, A loses the
household **10 times and keeps it 0 times** on the value arm. Across all three arms the count is
**20 to 1**: control 4 to 1, value 10 to 0, level 6 to 0. Under luck the signs would split. A two-sided
sign test on 20 of 21 gives p ≈ 2×10⁻⁵. So the (c) kill fires by its letter, and its consequence ("we
cannot tell, the dice") **does not follow**. The prediction failed. The pre-registered partition had
no bucket for "a retention decision the run does not log", which is what the evidence points to.

**What the missing decision most likely is (inference, not read).** In nine of the ten twin rows the twin
kept the household with its roll above its recorded stay probability: for example 0.945 at 0.581, 0.997 at 0.455,
and 0.797 at 0.388. Only SYN-2016-604 (0.222 at 0.279) is a plain roll. Under `resolve_departure` a
full-price event leaves on any of those. Something on the twin's side held those households at the
same price and the same pricing belief (scored `believed_p_retain` 0.4515 against 0.453 on
PROS-2017-0371, as A1 said). `simulation/retention_offer.answer_retention_offer` is that something: it
re-asks the world at the offered rate on the same roll. A's flag feeds `ending_term_type` into the
desk belief, and `run_phase2b.py`'s `_would_offer` gate reads that belief. In every flipped row the
twin's recorded p is above A's, which is what an offer's `max(p_full, p_effective)` leaves behind.
**GAP:** the member and control sidecars carry no `retention_offered`, discount, save rate or
departure cause per renewal, so the offer itself cannot be read from them. That is why it could not be
a bucket.
*Closed in code 17 Nov:* each `decisions_by_billing_account` renewal row now carries
`retention_offered`, `retention_discount_pct`, `p_stay_without_offer`, `p_stay_at_offered_rate`,
`offer_held` (renewed on a roll above `p_stay_without_offer`) and `departure_cause`
(`tools/run_value_cycle_ab.retention_offer_fields`). Files written before that commit still lack
them; the 11 flips are re-read from a rerun of pair 11111/22222 once step 6 and the D5 book release
the box.

**So the loss is §10b's candidate (b), "accidental offers to leavers worth keeping are lost". It is the
retention offer, not the renewal price.** The twin's desk belief ranked leavers backwards (D1 0.36),
so its offers fell on households that A's better ranking calls safe. Some of those were leaving, and
the offer kept them. A stops making those offers. On the flat book the offers it saves roughly pay for
the households it loses (+£0.14). On the value arm the households lost are the ones the value arm's
pricing made most valuable (£570 to £3,900 each over the window), so the same withdrawal costs £1.21.
That reading explains why the cost is arm-specific. It is an inference until the offer is logged.

**The named next change: the lever.** The retention-offer gate (`_would_offer`: value protected above
offer cost, under the desk belief) should be read against **what the arm will earn if the household
stays**, not the flat book's margin. A better belief about *who leaves* has been spent on withdrawing
offers from households the gate under-values. This is not the objective: the value arm's pricing
moved its outcome on one household in 101. **Before building it**, the run must log the offer per
renewal (`retention_offered`, discount, the save outcome) in the value-test sidecars. Without that,
the next pair cannot see the lever either.

**What step 6's read can confirm or refute with fields it already writes.** On each of the five new
pairs, count value-arm flips at identical rolls and identical common-fuel margins, A against twin.
- **Confirms:** at least 80% go against A, and they carry most of S5's value-arm cost.
- **Refutes:** they split near evenly, or S5's interval spans zero.
This is a one-variable read, because the dice are held within each pair.

Graded value-test: §12 prediction — (a) MISSED low (4.5% vs 10–75%); (b) HELD in range (19%) on one household; (c) MISSED high (72% vs 0–40%) and its kill fires, but the bucket is mislabelled (held rolls, 20-to-1 signs), so its consequence is withdrawn; unexplained HELD (4.9%). Mechanism: retention offers withdrawn under A's desk belief (inferred; offer not logged, GAP). Next change: the retention-offer gate's value basis (lever), after the run logs the offer.

### 12b. The offer re-read: built and pre-registered 17 Nov 15:07Z, before the rerun exists

**Why the rerun is not at `f318f1e48`.** That commit carries the offer logging, but between `41734bbe71`
(the pair §12a read) and it, 198 commits change the world itself: `sim/weather_world/` regenerated,
`simulation/arrears_engine.py`, `run_phase2b.py`, `world_payment_truth.py`, and two `company/billing`
modules. A pair rerun there is a different world with different flips, and the 11 could not be re-read
from it. So the rerun tree is `41734bbe71` plus `f318f1e48`'s one hunk in `tools/run_value_cycle_ab.py`
and nothing else. The world event at `41734bbe71` already emits every field the hunk reads
(`simulation/retention_offer.answer_retention_offer` sets them). `f318f1e48`'s five tests pass on that tree.
The tree is `/var/tmp/value-test-offer-reread`, locked, and `fork_salvage` committed the hunk there as
`870201d1e7`, so the run's `producing_commit` names the bytes it runs. Driver: `/var/tmp/vto-driver/driver.py`
(`/var/tmp/vta-driver/driver.py` with only `OUT` moved to `/var/tmp/vto-out-flag{0,1}`). Reader:
`/var/tmp/vto-driver/read_offers.py`, written now.

**When it runs.** Not while step 6 or the D5 book holds the box. A pair takes about 10.5 h per flag at an
11.4 GB peak (the desk pair's unit, 15–16 Nov), so it cannot run beside step 6. The transient unit
`vto-offer-reread-watch` (`/var/tmp/vto-driver/watch.sh`) waits until both step 6 families
(`vta-out-flag{1,0}/family_12_churn_roll.json`) are on disk and no `longjob-value-test*` unit or
`d5book-pause-watch` is active. It refuses if the tree has moved off `870201d1e7`. Then it launches
`longjob-value-test-offer-reread` through `launch_long_job`: flag 1, then flag 0, then the reader, which
writes `/var/tmp/vto-driver/read_offers.out`. It gives up after 10 days and says so. Reverse:
`systemctl --user stop vto-offer-reread-watch`.

**Step 1, a control, read first.** The rerun must reproduce §12a's pair: every renewal's outcome, roll and
`p_retain` on all three arms, and every account's value-arm net to the penny. The hunk only adds keys to a
row, so I predict **0 mismatches**. If there is any mismatch, step 2 is not read (the reader exits 2), and
the finding is that the logging moved the world. The reader was dry-run on the §12a pair against itself:
0 mismatches, and it recounts §12a's flips at held rolls exactly (control 4 to 1, value 10 to 0, level 6 to 0).

**Step 2, the prediction (the 10 value-arm flips at the same account and date; §12a's 11th row,
SYN-2016-215, has no twin renewal and is not a flip).**

| Claim | Prediction | Refuted if |
|---|---|---|
| The twin made an offer on the flipped renewal | **9 of 10** (range 7–10) `retention_offered` True | 5 or fewer |
| The twin's offer held the household (`offer_held`: renewed on a roll above `p_stay_without_offer`) | **9 of 10** (range 7–10). Not SYN-2016-604, whose roll 0.222 sits under the twin's 0.279, so it stays at the full rate | 5 or fewer: §12a's mechanism is refuted, and the lever is not the next change |
| A made no offer on those renewals | **8 of 10** (range 6–10) `retention_offered` False | 4 or fewer: A offers too, and the question becomes the offer's *size*, not whether it is made |
| All three arms: the twin's offer held on the flips A lost | **17 of 20** (range 14–20) | 10 or fewer |

**The row I cannot call: SYN-2016-604 (22222, 2017-12-25).** A left it on roll 0.222 with its logged
`p_retain` at 0.275. A departure is the upper tail (`resolve_departure`), so a full-rate event with those
numbers stays. Two readings. (i) A made an offer and the event kept is the offered one, which churned
(`answer_retention_offer`'s third branch), with `p_retain` logged as `max(p_full, p_effective)`. (ii) The
logged p is not the one rolled against, which is a logging defect. I put **60% on (i)**. Under (ii),
`departure_cause` and `p_stay_without_offer` will show it.

**What each reading makes the next change.** If held: build the retention-offer gate's value basis, i.e.
`_would_offer` reads what the arm earns if the household stays (§12a's lever). It is written knowledge page
first (K8), and the value test's next pair grades it. If refuted: §12a's attribution is withdrawn beside
its claim, and the value arm's £1.21 goes back to "a decision the sidecar does not record", with the offer
ruled out.

### 12c. Pair 2 cannot be graded yet, and pair 1's desk belief names the gate: the threshold, not the value test (17 Nov 23:30Z)

**Pair 2: only A's half exists.** `/var/tmp/vta-out-flag1/{member,control}_33333_44444.json` (17:40Z) are
step 6's flag-1 files. §12a's read compares A with its **twin**, which is flag 0 at the same seeds. There is no
`/var/tmp/vta-out-flag0/*_33333_44444.json`, and nothing is armed to write it. DIRECTION.yaml's `not_now` holds
the flag-off half of step 6, and no unit or watcher launches it. So the confirm/refute count cannot be taken on
pair 2. It has not refuted, and it has not confirmed. **Knock-on:** `vto-offer-reread-watch` (§12b) waits for
`vta-out-flag0/family_12_churn_roll.json`, and no scheduled job writes that file. As armed, it will give up after
10 days without launching. The flag-off half has to be ordered (behind flag 1, through `launch_long_job`) before
§12b's re-read can run. That is now a box-scheduling decision. Nothing was launched here.

**What pair 1 already shows, read in minutes without box time.** The sidecars carry
`desk_belief_by_arm` (§9a): the desk's churn belief at each renewal. This is the belief the offer gate reads
(`company_est_pre` in `run_phase2b.py`). The offer gate is two tests in series:
1. `company_est_pre > RETENTION_THRESHOLD` (0.30, `simulation/run_phase2b.py:528`). Below it, no offer is
   considered.
2. Only then `_would_offer`: `retention_value_protected(expected_margin, acq_cost_saved, …) > ret_cost`.

On the value arm of both A and the twin, every save-odds, engagement and bad-debt switch is off. So test 2
compares **`expected_margin + acq_cost_saved` against the cut's cost**, and no belief enters it.
`expected_margin` is `term_contribution_per_year` at the arm's **own** `unit_rate` (`_chain.unit_rate`, the
value arm's chosen price). §12a found that identical in A and the twin on every flip. So at a flip, test 2
can differ only through the cut's risk tier. Test 1 is where the belief acts.

| Seed | Household | Date | A's desk belief | Twin's desk belief | Over 0.30 (A / twin) |
|---|---|---|---|---|---|
| 11111 | SYN-2016-557 | 2018-12-02 | 0.137 | 0.362 | no / yes |
| 22222 | SYN-2016-604 | 2017-12-25 | 0.424 | 0.371 | yes / yes |
| 11111 | PROS-2017-0371 | 2018-11-29 | 0.126 | 0.335 | no / yes |
| 22222 | SYN-2016-458 | 2018-10-09 | 0.122 | 0.340 | no / yes |
| 22222 | PROS-2017-0318 | 2018-10-07 | 0.124 | 0.351 | no / yes |
| 22222 | SYN-2016-498 | 2018-10-31 | 0.119 | 0.331 | no / yes |
| 11111 | SYN-2016-581 | 2018-12-10 | 0.129 | 0.343 | no / yes |
| 11111 | PROS-2016-0263 | 2018-09-16 | 0.123 | 0.329 | no / yes |
| 11111 | SYN-2016-468 | 2018-10-17 | 0.112 | 0.304 | no / yes |
| 11111 | SYN-2016-315 | 2018-07-10 | 0.111 | 0.301 | no / yes |

**9 of 10 flips: A's belief is below the threshold and the twin's is above it.** The tenth, SYN-2016-604, is above
it in both runs, and it stays §12b's open row. Across the whole value arm, at the renewals both runs reached, A
moves **188 of 575** (11111) and **182 of 569** (22222) renewals from above 0.30 to below it, and **1** the other
way. A does not move the cutoff's population at the margin. It moves a third of the book across it, because
the ending-term belief sits on a lower **level** (0.11 to 0.14 on these households) while the threshold stayed
where the twin's scale put it. AUC (§10b's 0.82) grades ranking, not level. All nine households A rated at
0.11 to 0.14 **left**, so on this tail A's level is too low as well. A ranks better overall and still
under-reads this tail.

**Graded against §12a.**
- §12a's mechanism, "offers withdrawn under A's desk belief, from households A calls safe": **HELD** on 9 of 10,
  now read rather than inferred. The offer itself is still unlogged (§12b re-reads it). The belief that gates it
  is logged, and it points the same way.
- §12a's named lever, "`_would_offer` should value a kept household at what the arm earns": **MISSED.** At these
  flips the value test is never reached, and where it is reached it already reads the arm's own rate. A
  value-basis switch cannot change one of the nine. So step 3 of the direction item (the switched gate) is
  **not built**: it would be a mutation-proven control on a branch the loss never passes through.

**What the next change is instead (proposal, not built).** The loss is a **fixed belief threshold, applied to
a belief whose level a policy switch moved.** Two candidates, in order:
1. Drop the threshold as a test of its own, and let the value test carry the belief: offer where
   `p_churn × save_rate × value_protected > cost`. `retention_weighs_save_odds` already builds the weighing.
   It is off on both arms, and it sits **inside** the 0.30 test (`run_phase2b.py:4334`), so turning it on alone
   removes nothing. The build is one default-off switch that skips the 0.30 test when the weighing is on.
   A run with both on against A without them is the one-variable test of "the threshold costs the value arm
   its saves".
2. Calibrate the desk belief's level (observed-over-expected on its own closed renewals, as
   `competitive_pressure` already does per ending term) before any fixed cutoff reads it.

Both are G9-free (nothing he ruled), and both go to the K8 page first. 0.30 itself has **no declared origin**:
`RETENTION_THRESHOLD` is a supplier decision constant that lives in `simulation/`. Filed as
`SEAT_FINDING_THE_RETENTION_OFFER_IS_GATED_BY_AN_UNSOURCED_0_30_BELIEF_THRESHOLD_IN_SIMULATION_2026-11-17.md`.

**Prediction for candidate 1, filed before any run.** On pair 11111/22222, value arm, A with the threshold
skipped and the save-odds weighing on, against A as run: at least 6 of the 9 flips are re-offered, and the value arm's
A-minus-twin money moves from −£1.21 toward zero by at least £0.40 per household-year. Refuted if 3 or fewer
are re-offered. This cannot run until the box is free.

*Correction beside it (18 Nov, filed before any run).* Candidate 1 is built default-off as
`retention_skips_the_belief_threshold_when_save_odds_weigh` (knowledge §11f). Two things the prediction did not
say: (a) under the cutoff it weighs a renewal only once the save rate for its ending-term type is learned, so a
flip whose type had no closed 2017 offer is not re-offered for that reason; (b) the threshold is isolated by A +
weighing + switch against A + weighing, not against A alone. The 6-of-9 line stands for that pairing. Count the
`retention_log` rows with `considered = the_save_odds_carry_the_belief` before grading.

### 12d. The box plan: the threshold-skip pair, then the re-read, then step 6's flag-0 half (18 Nov 00:45Z)

§12c found that `vto-offer-reread-watch` waited on `vta-out-flag0/family_12_churn_roll.json`, which no
job writes, so it would have given up on 27 Nov without launching anything. The threshold-skip switch
(ff4fe0f3ef) also had no run. Both are now ordered. Nothing was launched here, and step 6's flag 1
(pid 1051692, pair 55555/66666) was not touched.

| Order | What holds the box | Starts when | Unit | Rough length | Deadline |
|---|---|---|---|---|---|
| 0 | Step 6 flag 1, pairs 3 to 6, then the fold | running | `longjob-value-test-step-6-flag1` | pair 2 took 11.5 h, so ends about 19 Nov 18Z | none |
| 1 | The next book (sim-runner) | flag 1's unit ends | sim-runner | about 2 h | none |
| 2 | Threshold-skip pair: A + weighing + skip, then A + weighing | `vta-out-flag1/family_12` on disk, box free, no book owed | `vts-threshold-skip-watch` launches `longjob-value-test-threshold-skip` | about 23 h | 28 Nov |
| 3 | §12b offer re-read, unchanged | stage 2's `vts-out-skip0/member_11111_22222.json` on disk (or its unit ended without it) and the same box test | `vto-offer-reread-watch` (re-armed) launches `longjob-value-test-offer-reread` | about 23 h | 2 Dec |
| 4 | Step 6 flag 0, pairs 2 to 6 (pair 11111/22222 is kept on disk) | `vto-driver/read_offers.out` on disk (or its unit ended) and the same box test | `vta-flag0-watch` launches `longjob-value-test-step-6-flag0` | about 58 h | 6 Dec |

The chain should end around 24 Nov. Each deadline leaves days of slack for a paused pair or a second book.

**"Box free"** (`/var/tmp/box-plan/box_free.py`) means four things are all true. No `longjob-*` unit is active,
including queued ones. `d5book-pause-watch` is not active. sim-runner holds no `sim_run` reservation. **No
book is owed**: a book is owed when sim-runner's own `book_admission` admits one and its next-run-not-before
has passed. The last test is what puts billing first. At 00:40Z a book was owed and was waiting only on flag 1.
So when flag 1 ends, sim-runner takes the box and no stage starts until that book has run. The plan does not
pause flag 1 to get the book sooner (that was 72fc73cc77's decision, and nothing here changes it). If the book
lane pauses flag 1 at a pair boundary, stage 2 still waits, because it needs flag 1's family on disk and does
not just wait for flag 1's unit to end.

**Why the threshold-skip pair goes before the re-read, and both go before flag 0.** These are the seat's own
reasons. The drawn item said only that flag 0 should come after flag 1 and the book. Stage 2 tests the next
lever against a prediction already filed (§12c). The re-read checks, at the offer itself, a mechanism §12c has
already read as HELD on 9 of 10 flips from the logged belief. Flag 0's five pairs only give the family noise
floor, and nothing waits on it. Each pair-11111/22222 stage costs a day; flag 0 costs nearly three.

**The threshold-skip tree.** `/var/tmp/value-test-threshold-skip` is 870201d1e7 (the §12b re-read tree:
41734bbe71 plus the offer logging) with ff4fe0f3ef's code and test hunks applied. All of them applied cleanly,
and the 32 tests in its three test files pass there. So the world is §12a's, and the 9 households in §12c's
table are the same flips. The hunks are uncommitted, so `producing_commit` can still name 870201d1e7. To cover
that, the driver (`/var/tmp/vts-driver/driver.py`) does two things. It refuses to run unless
`git diff --binary 870201d1e7 -- company saas sim simulation tools tests` hashes to the pinned
`53feeb15…f8ddd` (`threshold_skip.patch.sha256`; the patch itself sits beside it). It also writes that block
into every sidecar row as `tree_patch`. The switches go on all three arms, the way step 6 sets its flag. The
decision rows also carry `retention_considered_on_save_odds`, the event key ff4fe0f3ef sets, so the grade can
count the renewals weighed under the cutoff before reading the offers. That is the check §12c's correction
asks for, read from the event and not from `retention_log`.

**Reverse.** `systemctl --user stop vts-threshold-skip-watch vto-offer-reread-watch vta-flag0-watch`. After a
stage has launched, also stop its `longjob-*` unit. The plan's files are in `/var/tmp/box-plan/`, and each
watcher logs to `<unit>.log` there.

**The reader, written 00:55Z, before either run exists** (*correction beside it: the line this replaces said it
was handed on*). `/var/tmp/vts-driver/read_threshold_skip.py` reads the skip1 run's value arm. For each of the
9 flips it prints `retention_considered_on_save_odds`, `retention_offered` and the outcome. It grades against
§12c's line (6 or more re-offered held, 3 or fewer refuted). It prints the value-arm money two ways and grades
neither: skip1 minus skip0, and skip1 minus the twin, both in £ per household-year using `grade_paired_gbp.py`'s
method. It exits 2 if a flip renewal is absent or unlogged, or if a run's `tree_patch` is not the pinned one.
It was dry-run by putting A's §12a sidecars in place of both skip runs. All 9 flips were found, and all 9 were
reported unlogged, because those sidecars predate the offer fields, so it exited 2. A against itself gave £0.000.
A against the twin gave **−£1.207 (−£2.32 to −£0.37)**, which reproduces §12a's −£1.21. Stage 2's job runs it
after both flags and writes `/var/tmp/vts-driver/read_threshold_skip.out`.

#### 12d, re-planned (18 Nov 02:10Z): flag 1 stops at pair 3, the book, then the skip pair. No flag 0, no re-read

*This replaces the table above as the box order. The table is kept as the plan it was.* The direction
(DIRECTION.yaml, 18 Nov) drops step 6's remaining flag-1 pairs and its whole flag-0 half. They measure the 0.30
gate that §12c read as the loss, so neither is worth a day of the box.

| Order | What holds the box | Starts when | Unit |
|---|---|---|---|
| 0 | Step 6 flag 1 finishes pair 3 (55555/66666), then stops. Pairs 1 to 3 are kept on disk | running | `longjob-value-test-step-6-flag1`, stopped by `flag1-stop-at-pair3-watch` |
| 1 | The owed book (sim-runner, origin HEAD) | flag 1 stopped | sim-runner |
| 2 | Threshold-skip pair: skip1 (A + weighing + skip), read at once, then skip0 (A + weighing), read again | pair 3's control file on disk (or flag 1's unit ended) and `box_free.py` free, which includes no book owed | `vts-threshold-skip-watch` launches `longjob-value-test-threshold-skip` |

- **The pair boundary.** It is read from `vta-out-flag1/{member,control}_55555_66666.json`, both parsing as
  JSON. The driver writes control last. It is never read from a marker's mtime. **`row7book-pause-watch`
  (1378c5d815) is stopped.** It stopped flag 1 at the same boundary and then relaunched it once the book's
  `run_complete` landed. That relaunch is exactly what the direction removes. `flag1-stop-at-pair3-watch`
  does the stop and nothing else. The row-7 book it waited for is still the book in step 1, because a book was
  owed at 02:10Z (`box_free.py`: "a book is owed").
- **`vto-offer-reread-watch`: retired, not re-armed.** `vta-flag0-watch` is retired too. The §12b re-read
  re-ran A and the twin only to log the offer. The skip tree carries the same offer logging (870201d1e7), so
  skip1 logs `retention_offered` and `retention_considered_on_save_odds` at the nine flips. That is the offer,
  read at the gate that matters. A re-read of A's offers would only re-confirm a gate §12c already read from
  the logged belief.
- **The comparator, and why the job still runs skip0.** The direction compares skip1 with A as run
  (`vta-out-flag1/member_11111_22222.json`) "so the switch is the only variable". The switch is refused
  without `retention_weighs_save_odds`, so skip1 differs from A in two ways: the weighing and the skip. Only
  skip0 isolates the skip (§12c's correction). Each pair costs about 11.5 h, and nothing is queued after it
  any more. So the job runs skip1, writes `read_threshold_skip.skip1.out` at once (the flips, the under-cutoff
  count and skip1 − A), and then runs skip0 for `read_threshold_skip.out` (skip1 − skip0 as well). The grade
  is not held for skip0. The money is attributed only once skip0 is on disk.
- **The reader, amended before any run** (`read_threshold_skip.py`; v1 kept beside it). skip1 is required.
  skip0 and the twin are read when they are on disk. It adds skip1 − A, and it counts the value arm's
  renewals weighed under the cutoff across the whole book, not just at the nine flips. It was dry-run with
  A's sidecars standing in for skip1 and the pin check off: A − A came out at £0.000, A − twin at
  **−£1.207 (−£2.32 to −£0.37)**, and all nine flips were unlogged, so it exited 2 as built. The skip tree
  still hashes to the pinned `53feeb15…f8ddd`. That holds even though a SALVAGE commit (128d6842e2, 01:05Z)
  moved its HEAD, because the pin is a diff from 870201d1e7 to the working tree.
- **When.** Pair 3 began about 20:00Z on 17 Nov, and pair 2 took 11.5 h, so flag 1 should stop around 07:30Z.
  Add the book (about 2 h). skip1's read should land around 21:00Z on 18 Nov and skip0's around 08:30Z on
  19 Nov. The skip watcher's deadline is 28 Nov.
- **The prediction is unchanged** (§12c as corrected): 6 or more of the 9 re-offered holds, 3 or fewer
  refutes. If it refutes, §12c's candidate 2 (calibrating the belief level) is next.
- **Reverse.** `systemctl --user stop flag1-stop-at-pair3-watch vts-threshold-skip-watch`. To resume step 6,
  run the relaunch block in `/var/tmp/row7book-pause/watch.sh`. `launch_threshold_skip.v1.sh` and
  `read_threshold_skip.v1.py` are the pre-re-plan versions.

The result goes in §12e: §12d is this plan, and the direction's "s.12d" named the next free section when it was
written.
