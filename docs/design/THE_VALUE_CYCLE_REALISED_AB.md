# The value cycle — the realised A/B, and why it is the only honest score

**Director, 2026-08-26, handing over the one thing he had reserved:** *"if it passes, start the
value cycle — the per-customer decision engine the whole thesis rests on. That was the one thing
reserved to me and I'm giving it to you now."*

**Entry evidence:** `docs/design/EPOCH2_EVIDENCE_2026-08-26.md` — five of six questions pass; Q4
fails and is recorded as bounding publication rather than construction.

> ## READ THIS FIRST — the answer is at the bottom of this file, and it is not £3.08M
>
> Every result between "THE FIRST FULL RESULT" and "inference or luck" below was measured on a
> book the director had **already ordered changed** on 2026-08-24, and none of those sections
> said so, because at the time nobody had noticed. They are kept — nothing here is rewritten —
> but they are **SUPERSEDED**, and the two figures that escaped into conversation are both
> about five industrial accounts:
>
> | reading | book | net delta | status |
> |---|---|---|---|
> | −£110,731 EV | resi + SME + **I&C** | −£93,555 | superseded |
> | +£2,293,743 EV | resi + SME + **I&C** | +£3,082,499 | superseded — 99.97% of it 15 I&C accounts |
> | **+£10,800 EV** | **resi + SME (the served book)** | **+£16,773** | **current — [see below](#2026-08-26-1709z--the-answer-on-the-book-the-director-actually-asked-about)** |
>
> The last row is the only one that answers the question this project exists to ask.

## The thesis, stated as a measurable claim

A supplier deciding customer-by-customer on what it can infer beats a flat-rules baseline
**through better prediction and nothing else.** Three things have to be true for that sentence to
mean anything, and exactly one of them is currently unproven:

| | status |
|---|---|
| A per-customer decision exists | `company/pricing/value_based_renewal.decide_margin` — 263 accounts, 187 distinct margins |
| A baseline exists to beat | `decide_margin(arm=FLAT_RULES)` — this company's own flat £2.00/MWh, imported not restated |
| **The decision beats the baseline** | **not measured, and cannot be measured the way it is currently reported** |

## Why the existing comparison cannot answer it, in the module's own words

`company/pricing/value_based_renewal.py`, closing its own docstring:

> It does not show that pricing on value earns more. It cannot: the objective is built from the
> company's own beliefs, so scoring the arms on EXPECTED value would let the value arm win by
> construction — it maximises the very number it would be judged on, which is R15's tautology
> pattern with money in it. The only honest comparison is REALISED: the same book, the same
> world, run once per arm, scored on what actually happened. That needs two runs and it is the
> next step, not this one.

`tools/couple_value_based_pricing.py` says the same thing from the other side, and it is right to.
Today's artefact (`docs/observability/value_based_pricing_arms.json`) reports **decisions**, never
**earnings**, and refuses to be read as evidence of inference at all while its two sides share a
calibration source.

**So the value cycle is not "wire the arm up". It is "close the loop": decide → act → let the
world answer → score what actually happened.** The decision half is built. The world's answer is
the half that has never been taken.

## The instrument

Run the identical world twice — same seed, same weather, same prices, same population draw — and
change exactly one thing: which arm sets the renewal margin.

```
run A   arm = flat_rules    (today's company, frozen)
run B   arm = value_based   (the same company, deciding per customer)
```

Score on what the world did, not on what the company believed:

- realised net margin, on all three clocks (R14: settled / billed / banked)
- book at end of period, and churn events in between
- bad debt, because a higher price changes who pays
- revenue and volume, so a win can be attributed to price or to retention

**The gap between the two runs is the score, and it is allowed to be negative.** An arm that loses
is a result, not a defect — that is the whole reason a baseline was frozen before it was replaced.

## What the instrument must report beside the score, or the score is not readable

Three things are already known about this arm and each one changes how a realised result must be
read. All three are measured, not suspected, and all three come from
`docs/observability/value_based_pricing_arms.json` and the module's own bound:

1. **165 of 263 accounts had their candidate grid TRIMMED by `max_supported_rate_increase_pct()`
   (+83.1%, the Ofgem cap's own largest published single-step move).** For those accounts the arm
   is not choosing freely; the bound is. A realised win concentrated in trimmed accounts is a
   result about the bound, not about inference, and the report must be able to tell the two apart.
2. **The chosen margins are 15x to 40x the control** (modal region £60–£200/MWh against £2.00).
   This is not a tweak to a price, it is a different price level, and the world's churn response
   to it is the dominant term in any realised outcome.
3. **The control is weak, and by a measured amount.** This company's flat £2.00/MWh is 23.4%–53.6%
   of the EBIT allowance Ofgem grants an efficient supplier
   (`company/pricing/regulated_average_margin.py`, cap period 11a). Beating it is therefore a low
   bar, and any headline must carry that ratio beside it or it flatters the arm by omission.

## What it is NOT allowed to do

- **It may not move `MAX_CHURN_PROBABILITY`, `_MAX_RATE`, either leave-probability cap, or the
  world's switching curve** so the result reads better. R12 makes an output a diagnostic and never
  a target; R13 makes baseline changes fidelity-driven and decided blind to company results. The
  arm losing because the world punishes a 35x margin is the correct behaviour of a faithful world.
- **It may not become the default.** The arm switch defaults to `FLAT_RULES`, so a run that does
  not ask for the experiment is byte-identical to today's. The published figures stay the control's
  until a realised result says otherwise, and even then the change is the director's curriculum
  call, not this experiment's.
- **It may not report a single number.** A realised gap without (1) the trimmed-account split and
  (2) the regulated-allowance ratio is a number that cannot be read, which R14's clock rule already
  refuses for financial figures and this document extends to this one.

## Why this is worth two full runs

~700s each, measured over six consecutive runs on 2026-08-26 — **~23.4 minutes for the pair**, and
~46MB of output. In July the same experiment would have cost the same wall-clock against a
27-account book with no population draw, which is why it was correctly deferred then and is
affordable now. That change is Q3 and Q6 of the evidence pass, and it is the concrete reason the
pass had to be re-run before this document could be written.

## Sequence

1. **The arm switch — as a `DecisionPolicy` FIELD, not a new parameter.** This machine already has
   exactly the seam this needs and it must be reused rather than paralleled:
   `company/policy/decision_policy.DecisionPolicy` is the swappable per-run decision identity
   (`FROZEN_POLICY_BASELINE_DESIGN.md` option B), `simulation/run_phase2b.main(policy=…)` already
   takes it, `CURRENT_POLICY` is the default so every existing caller sees zero behaviour change,
   and `tools/run_frozen_baseline.py` already runs a second arm through it for a comparison the
   project has run before. So the arm is `renewal_margin_arm: str = FLAT_RULES` on that dataclass,
   read at the renewal price path, and nothing new is invented.

   **And the reuse buys the guard, not just the wiring.** `run_phase2b.main` already refuses a run
   whose `policy` and whose `active_policy()` scope disagree, in its own words: *"If those two
   disagree the run is a chimera — naive retention with current dunning letters — and the frozen
   baseline's delta silently attributes an uncontrolled variable to the policy change."* That is
   precisely the failure an A/B on pricing would otherwise be exposed to, already built and
   already fail-closed. A second switch beside it would have had to re-earn that guard, and
   probably would not have.
   **Where the arm ACTS is already decided too, and it is not a new seam either.**
   `company/pricing/renewal_rate_chain.py::decide_renewal_rate` is the ONE door through which
   every rate-moving supplier decision fires — the portfolio learning premium (writer 1), the
   realised-margin recovery surcharge (writer 2), the activity-based uplift for net-negative
   accounts (writer 3) and the Ofgem cap clamp (writer 4) — and its own docstring argues why it
   must be one door: *"the surcharge multiplies what the premium left, the cap clamps what the
   uplift added. Three doors would hand the ordering back to the world."* The value arm is a
   fifth writer in that chain, placed beside writer 3 and BEFORE writer 4, which is load-bearing
   in two ways: it inherits the price-cap clamp rather than needing its own ceiling, and it
   lands in the existing decomposition record (`components`, `chain_entries`) so the A/B can
   attribute a realised difference to this writer rather than to the four it sits among.

   **It takes writer 3's inputs, not `decide_margin`'s.** `renewal_unit_rate_uplift` already
   reaches the account's own settled history from `account_id` + `settled_records`, and
   `decide_renewal_rate` is called at `run_phase2b.py:1329` — BEFORE `tenure_for_est` and
   `company_eac` are computed at 1408/1414. So the arm derives tenure, EAC and cost-to-serve
   itself, inside `company/pricing/`, from the same observables writer 3 uses. That keeps the
   seam narrow (no six new keyword arguments across the wall), keeps the derivation behind the
   wall where a real supplier's would be, and avoids reordering a 3,000-line loop to feed it.

2. **The A/B runner**, shaped on `tools/run_frozen_baseline.py` — two runs, one seed, one world,
   two policies differing in exactly one field, one record. Realised figures only; the
   expected-value numbers stay where they are, in the decisions artefact, clearly labelled as
   decisions.
3. **The score, with its three caveats attached** (above), written where the coupled-gap ledger
   already lives so it is beside the belief-vs-truth record rather than replacing it.
4. **Only then**, a published surface — and only if the coupled record can by then state its own
   provenance, which it currently refuses to.

Steps 1–3 are reversible, cost ~24 minutes of machine time per experiment, and cannot reach a
customer, a pound or a public claim. Step 4 is the one that touches what the company says about
itself, and it stays behind the refusal the coupler already enforces.

---

## The dependency the first realised run exposed: the arm's LIFETIME term is ungraded

**Added 2026-08-26, after the first realised A/B.** The arm's objective is

    EV(m) = P(stay | m) x (m x eac_mwh + fixed_revenue - expected_cost(m)) x annuity(lifetime, r)

Three factors. Two of them are measured: `P(stay|m)` comes from
`company/crm/enriched_churn_estimate.py`, which is scored against the world's own churn, and the
money terms come from the supplier's settled book. **The third is not measured at all**, and the
2016-2018 result is what made that matter: +5.2% net margin, +£184 enterprise value. An arm that
converts book into cash at break-even on enterprise value is an arm whose view of how long a
customer lasts is doing no work — which is exactly what an unvalidated `annuity(lifetime, r)`
would look like.

### The gap that is published is not the gap it appears to be

`docs/observability/coupled_gap_ledger.json` carries `EP1_clv_three_horizon` at **gap 1.76**
against a no-skill baseline of £817.89 mean absolute error, measured 2026-08-19 over 5 completed
lives. A gap above 1 says the company's per-customer lifetime value carries LESS information
than assigning every account the population mean.

**But `tools/couple_clv.py` already states, in its own docstring, that this row does not grade
EP1's estimator**, and mechanises the declaration rather than leaving it implicit
(`belief_provenance()` resolves the producing callable from the source tree by AST;
`components.grades_atom_estimator` carries the answer onto the ledger row; its test fails the day
EP1 *is* wired in and the declaration is not updated). Its reason:

> EP1's estimator cannot be backtested today at all: a backtest needs a belief recorded BEFORE
> the outcome, and `three_horizon_clv` is a single end-of-run table with no per-year series.

So there are **two** problems under one number and they need separating:

1. **Mis-subjection.** The 1.76 grades a different belief and wears EP1's id. A reader — this
   seat included, in four consecutive direction records — takes it for EP1's.
2. **Right-censoring.** Even with the right belief, the ledger's note is correct that lifetime
   realised margin can only be scored on accounts whose life COMPLETED, and those are exactly the
   accounts EP1 refuses to value. The population the estimator serves and the population it is
   graded on are disjoint by construction.

### What actually unblocks it, and it is not "find a grading that reaches live accounts"

**(1) is a build, and a small one.** Write `three_horizon_clv`'s table once per YEAR during the
run into the run output — a belief SERIES rather than an end-of-run table. That is all a backtest
needs: a belief recorded before the outcome. The blocker the coupler names is that this sits
outside EP1's declared `file_scope` and moves a published surface; `file_scope` is a DIAL and
not a wall (CLAUDE.md RULE 0), and a surface that moves for a stated reason is the ordinary case.

**(2) does not need live accounts at all — it needs a FIXED HORIZON.** The atom is called
`EP1_clv_three_horizon`; the answer is in its own name. Scoring "did this belief predict TOTAL
LIFETIME margin" can only ever use the dead, and the dead are a biased sample of the living
because they are precisely the ones that churned. Scoring "as of date T, did the belief rank
accounts by their realised margin over the NEXT k years, among accounts alive at T" uses only
realised data, reaches the live population, and is the standard answer to right-censoring rather
than an invention. It also fits what the arm actually needs: the arm does not need to know a
customer's whole life, it needs the annuity over the term it is pricing.

### Why this is the value cycle's next dependency and not a separate errand

Until the lifetime term is graded, a realised A/B cannot say WHICH of the arm's three factors
produced its result — and the first run's shape (margin up, book down, enterprise value flat) is
consistent with a good churn signal being multiplied by a lifetime estimate that carries no
information. Grading it is what makes the next A/B attributable rather than merely measured.

---

## THE FIRST FULL RESULT (2026-08-26): the arm loses, and the horizon is why
**[SUPERSEDED — measured on the I&C book. The loss is five industrial accounts, not a finding
about this supplier's customers. See "the answer on the book the director actually asked
about" at the end of this file.]**

Full 2016–2025 window, 263-account book, one variable (`renewal_margin_arm`), both arms inside
`policy_scope` and passing `policy=`:

| | control (flat £2/MWh) | value arm | delta |
|---|---|---|---|
| gross margin | £6,543,452 | £6,418,661 | **−£124,791** |
| net margin | £1,145,681 | £1,052,126 | **−£93,555 (−8.2%)** |
| enterprise value | £1,391,262 | £1,273,010 | **−£118,252 (−8.5%)** |
| accounts at end | 172 | 170 | −2 |
| churned | 45 | 48 | +3 |
| renewals seen | — | 69 (66 priced, 3 declined) | — |

**The sign flipped against the short window.** 2016–2018 gave +£4,713 net and +£184 enterprise
value. The decade gives −£93,555 and −£118,252. Same code, same book, same world; a longer
horizon. The cheap experiment did not under-measure the expensive one, it pointed the other way.
That is now a standing fact about this instrument: **a truncated window is a different world, not
a rehearsal.** It is also how a real refusal was found — `C_IC3`, 2021, no lawful predictable
offer at all — in years the short window never reached.

### The loss is a horizon effect, and it names its own cause

Losing **£124,791 of GROSS margin on three extra churns** is not three customers' worth of
revenue. It is the compounding loss of the remaining LIVES of accounts driven away early. A
three-year window cannot show it: there is not enough remaining life left for it to compound.

That is precisely the signature of an underweighted `annuity(lifetime, r)` — the one factor in
the arm's objective that nothing grades (see the section above). The arm under-prices what losing
a customer costs, wins on the margin it can see, and pays for it over the years it cannot.

**So the ungraded lifetime term is no longer a tidiness concern. It is the leading candidate
explanation for a measured £118k loss**, and grading it is the precondition for a second attempt
being worth its 45 minutes.

### And half the answers were a bound's, not a customer's

36 of 66 priced renewals came back **endpoint-bound** — 20 at the ceiling, 16 at the floor — and
**27 were clamped by the domestic price cap**. The 263-account decision snapshot
(`value_based_pricing_arms.json`) reported 6 endpoint-bound of 263.

So the same arm reads as a per-customer chooser on a book scored at one instant, and as a
bound-follower over a decade of real terms. Only the realised run could tell those apart, and
that difference is a stronger argument for this instrument than the delta is.

### What must NOT happen next

R12: the arm losing is a **measurement**. No constant moves because of it — not
`MAX_CHURN_PROBABILITY`, not `_MAX_RATE`, not the candidate grid, not the support bound. The
control was frozen before it was replaced precisely so this number could come out negative and
mean something. The next step is to grade the lifetime term, not to make the arm look better.

---

## THE ANSWER TO BOTH OF THE ABOVE (2026-08-26): the chain handed the arm six of its twenty inputs

The two findings in the previous section — *the arm loses* and *half its answers were a bound's*
— looked like two problems and were one. They have the same cause and it is not in the decision.

`decide_margin` takes twenty company observables. `renewal_margin_uplift`, its only production
caller and the one every figure above was produced through, passed **six** and let the rest
default. `tools/couple_value_based_pricing.py` — the probe that reported 6 endpoint-bound of 263
— passes the full set. **Same module, same book, different information.** That is the whole of the
difference between "a per-customer chooser" and "a bound-follower", and it is why only the
realised run could see it.

Two of the defaults were the mechanism.

### 1. The rate the arm compared against was not the same KIND of number as its offer

A settled record's `revenue_gbp` **includes** the per-period standing charge —
`simulation/hedged_settlement.py` adds `sc_per_period` into it explicitly. So
`observed_account_state`'s `revenue / volume` was an **all-in** £/MWh. The number it was compared
against is not: `base_rate_gbp_per_mwh + margin`, the offer handed to the churn model, is a
commodity unit rate with no standing charge term in it at all.

The gap between them is the standing charge expressed per MWh, and on a small domestic account it
is enormous. £0.27/day is about £99 a year; over 1,779 kWh that is **£55/MWh**. The arm was asking
its churn model how a customer feels about moving from an all-in £176/MWh to a commodity £130/MWh,
and the model correctly answered *that is a price cut*. Fifty-five pounds a megawatt-hour of
phantom headroom, spent before the belief registered any rise at all — and the support bound is
`current_rate × 1.831`, so the inflated rate inflated the frontier by the same proportion on the
way past.

Measured on that account: the chosen margin falls from **£193.00 to £60.00/MWh** once the standing
charge is netted out of the rate and put back into the EV.

**This is also the better-evidenced explanation of the loss.** The previous section attributed the
£124,791 of gross margin lost on three extra churns to an underweighted `annuity(lifetime, r)`.
But `expected_value_gbp`'s own docstring already names a mechanism with exactly that signature and
it is this one: *"fixed revenue is only earned from a customer who STAYS, so it sits inside the
retention term. Making retention more valuable makes losing the customer more expensive, and the
optimiser responds by charging LESS to keep them."* An arm that never saw its standing charge
under-prices what losing a customer costs, wins on the margin it can see, and pays for it over the
years it cannot — which is the measured result, stated in advance, by the module itself.

The ungraded lifetime term remains ungraded and remains worth grading. It is no longer the
*leading* candidate.

### 2. No ceiling reached the search, so the cap arrived afterwards as a clamp

`decide_margin` refuses this order in its own body: *"THE CEILING IS APPLIED BEFORE THE SEARCH, not
after it. Scoring a candidate the company may not lawfully offer and then clamping the winner would
report an expected value nobody can earn, and would make the arm look better than the supplier it
describes."* The adapter passed no `max_offered_rate_gbp_per_mwh`, so on the only path a live run
uses, the cap landed as chain writer 4 — exactly the forbidden order, on 27 of the 66 renewals.

Two consequences, both R15 shapes rather than approximations:

- `ceiling_bound` is computed as `max_offered_rate_gbp_per_mwh is not None and …`. The flag whose
  entire job is to tell a reader **the cap chose this price** was **structurally unable to fire**
  on the one caller where the cap ever chose one. Fail-silent, and it is why the artefact could
  report `endpoint_at_ceiling: 20` while `ceiling_bound` stayed invisible.
- `believed_p_retain` and `believed_expected_value_gbp` — the beliefs the belief-vs-truth column
  scores — were the arm's beliefs at a rate the customer was **never charged**, while the world
  churned them at the capped one. The two sides of that comparison were different prices.

Mutation-tested: pre-fix, the arm asks **£211.75/MWh against a £189.50 cap** — an unlawful offer
that only writer 4 stopped.

### Why this is not the goal-seek R12 forbids

Nothing was tuned so the arm would behave. No constant moved: not `MAX_CHURN_PROBABILITY`, not the
candidate grid, not the support bound, not the churn model's sensitivities. What changed is that
the arm now sees **more** of what its own records already said — its standing charge, its billed
revenue, its observed lifetime — and that the ceiling which already bound it moved from *after* the
decision to *inside* it, where the record can name it.

The direction this cuts is against the arm, not for it. It prices **lower**, it can now be refused
outright where no lawful margin exists, and `ceiling_bound` firing makes visible a fact the old
artefact concealed: on a capped domestic account, the cap really does decide the price. A tighter
bound would have hidden the belief; this exposes it.

### What the record now carries

`ceiling_bound` and `extrapolation_bound` reach the run log and `decision_shape` counts them, so a
reader can tell a supplier that obeyed the price cap from one whose belief ran out. And
`clamped_by_the_price_cap` becomes a **control** rather than a statistic: the arm's `lawful` filter
keeps only margins where `base + m ≤ cap`, and the chain's post-arm rate *is* `base + m`, so a
priced renewal can never afterwards be clamped. A nonzero count means the two reads of the ceiling
have come apart — and it says the published beliefs are beliefs about a price nobody was charged.

R15-proven in `tests/company/pricing/test_value_arm_in_the_renewal_chain.py` §5 (six controls, four
mutation-proven to red on the pre-fix mechanism). Landed `8b450a839`.

---

## 2026-08-26 — the lifetime term was graded, and it is not the one that is wrong

The section above ("The loss is a horizon effect") demoted the ungraded `annuity(lifetime, r)` from
*leading* candidate to standing candidate once the missing standing charge was found. It is now
graded, and it can be demoted further: **the lifetime term is not inflated. Measured two
independent ways it runs SHORT.**

Full record: `docs/staging/done/WORKER_FINDING_THE_CLV_GAP_IS_GRADED_ONLY_ON_THE_CUSTOMERS_WHO_LEFT_2026-08-26.md`.

**Hazard against outcome**, counted from `event_type` over 622 renewal decisions: the company
over-states churn hazard by 2.4x–7.6x in every elevated bucket, and an over-stated hazard gives a
*shorter* believed tenure and a *smaller* CLV. At portfolio level, mean believed tenure 11.74 years
against a realised implied 13.82.

**Where the 5x came from instead.** The `EP1` gap is graded only on accounts whose life ENDED
inside the run — a population selected on the quantity being predicted, whose realised value is
2.96x below the still-supplied book like-for-like (a lower bound; the excluded side is still
accruing). And all 33 graded accounts sat in the one hazard bucket where the model is *right*
(0.05 believed, 0.053 realised). A calibrated estimator graded on exactly the 5% who left scores as
a uniform five-fold over-estimate. `best_single_scale 0.204` was reading the population, not the
horizon.

**And a sharper defect underneath.** Recovering the hazard from EP1's own published horizons, all
33 graded accounts return the *identical* value: one distinct hazard, a flat 20-year tenure for
every account graded. "The error is in the level, not the ranking" was never a finding about the
lifetime term — the lifetime term had no variance to contribute a ranking with. The hazard is
`0.05 + 0.03 x bill_shock_count`, a step function of one integer that is zero for 42% of all
renewal decisions in the run.

So the arm's objective multiplies a per-customer margin by a term that is, on this population, a
constant. **That is the lifetime finding, and it is about dispersion rather than level.** Whether
giving the horizon real per-account dispersion changes the A/B is now a question worth its 45
minutes; grading the level was the precondition, and the level is roughly right.

None of this moves the realised A/B — net **−£93,555**, enterprise value **−£118,252** over ten
years, measured on the whole book with no selection in it. It moves only the explanation.

---

## 2026-08-26 12:35Z — the A/B re-run: every mechanism fix landed, and the loss did not move

The −£118,252 headline was measured at 08:02Z. `8b450a839` — the standing-charge and
ceiling repair its own analysis called *"the better-evidenced explanation of the
loss"* — landed at 08:46Z. Nobody re-ran it. Re-run now, on the same book and the
same window.

**The control reproduces bit-identically** — net £1,145,681.029513 in both runs — so
the only thing that changed is the arm, and the comparison is clean.

**A prediction was stamped before the run**
(`ab_rerun_prediction.md`, scratch) so the result could disagree with it. It did.

**Where the two columns below actually live.** The post-fix run wrote the tool's DEFAULT
path, `docs/observability/value_cycle_ab.json` (`generated_at` 2026-08-26T12:35:29Z),
committed in `b7db3e7b8`. The pre-fix run it is read against was preserved out of the way as
`docs/observability/value_cycle_ab_prior_2026-08-26T0802Z.json` — and was left UNTRACKED
until `6089f90a9`, so for a day this table's left-hand column cited an artefact that existed
in one worktree and nowhere in the repo. A paired reading is only as committed as its
weaker half: the artefact that is *superseded* is the one nothing routine will ever
re-create, so it is the one that has to be landed deliberately.

| | 08:02Z | predicted | 13:35Z | |
|---|---|---|---|---|
| `clamped_by_the_price_cap` | 27 | 0 | **0** | right |
| `median_margin_gbp_per_mwh` | 100.50 | < 60 | **39.75** | right |
| `endpoint_bound` | 36 of 66 | ≪ 10 | **36 of 59** | **wrong** |
| `churned_accounts` | 48 (control 45) | ~45 | **48** | **wrong** |
| `realised_delta.enterprise_value_gbp` | −118,252 | materially better | **−110,731** | **wrong** |

**The repairs worked exactly as designed.** The cap now binds inside the search and
clamps nothing afterwards; `ceiling_bound` fires 20 times where it was structurally
unable to fire at all; `extrapolation_bound` fires twice; declines rise 3 → 10 as the
arm refuses renewals it cannot lawfully and honestly price; and the median chosen
margin more than halves, 100.50 → 39.75.

**And the loss barely moved: −£118,252 → −£110,731, 6.4%.** So over-pricing was not
the mechanism. The arm halved its price and lost the same money.

### What the shape now says

Of 69 renewals seen the arm declines 10 and prices 59. Of those 59, **36 land on a
bound** — 20 at the ceiling (which is now genuinely the price cap deciding) and 16 at
the floor. Add the 2 extrapolation-bound and the arm's own per-customer view chooses
freely on **21 of 69**. On a capped domestic book, the regulator and the floor make
most of the decisions, and that is a finding about what a per-customer arm can even
do here, not a defect to repair.

### The number that does not fit, and is the next thing to open

The arm gives up **£123,006 of gross margin on 3 extra churns**. That is **£41,000 per
churn** against domestic accounts whose whole-life margin averages ~£420. It cannot be
three domestic customers. This book carries five I&C accounts averaging **£221,491** of
lifetime margin, and the artefact reports only aggregates, so it cannot say which
accounts the two arms lost differently.

**If the delta is one large account, then "the value arm loses" is a statement about a
single decision rather than a portfolio property, and n = 1 is not a thesis.** The A/B
tool is being given a churn-roster diff — which accounts churned under one arm and not
the other, with segment and realised lifetime margin — because a delta driven by three
accounts out of 263 must name them. Until it does, neither the loss nor any future win
should be read as a portfolio result.

---

## 2026-08-26 14:20Z — it was one account, and it was priced as a household

The A/B now names where its delta comes from. `margin_movers` over all 259 accounts:

**`concentration_top_n_share_of_absolute_movement` = 0.9968.** Net delta −£94,814, of which
**C_IC3 alone is −£94,314 — 99.5%.**

| account | control | value arm | delta |
|---|---|---|---|
| **C_IC3** | £195,317 | £101,003 | **−£94,314** |
| C_IC1 | £531,323 | £500,195 | −£31,128 |
| C_IC2 | £365,689 | £381,043 | +£15,354 |

So every "the value arm loses" statement in the sections above is a statement about **one
industrial customer**. The churn story is dead: the four accounts the arm loses differently
(C1_2, C3, C6, C7) are worth £6,534 between them and three are BETTER off under the arm.
The loss is not a customer leaving; it is one customer **staying at the wrong price**.

**The mechanism, measured on the company's own estimator.** `renewal_margin_uplift` maps
`segment = "resi" if is_domestic else "SME"` — two values, because `cost_to_serve_for_period`
takes two. `estimate_churn_probability` branches THREE ways, and its I&C arm exists to switch
bill-size-driven churn off (`IC_BILL_STRESS_SENSITIVITY = 0.0`). On the SME path the stress
term is `0.25 × max(0, annual_bill/£3,000 − 1)`, and C_IC3 consumes 3.94 GWh:

| offered margin | SME path (what the arm gets) | I&C path (unreachable) |
|---|---|---|
| £0.50 — the floor | **1.0000** | 0.0288 |
| £2.00 — the control | **1.0000** | 0.0288 |
| £46.00 | **1.0000** | 0.8094 |

The arm believes a 3.9 GWh customer is certain to leave **at any price it can offer, including
one below what it already charges**. `p_retain = 0` flat across the grid leaves nothing to
maximise, so the search falls to the floor — £0.50/MWh, under the control's £2.00. That is
`endpoint_at_floor: 16`, and on 3.94 GWh a £1.50/MWh giveaway compounds to the £94,314 above.

**Why the two earlier repairs could not have helped.** A saturated term notices nothing
downstream of it. `8b450a839` corrected which rate is compared and which ceiling binds; both
were real, and both sit behind a `p_leave` that had already lost all its information. That is
why the loss moved 6.4% and no further.

**Why the probe never saw it.** `tools/couple_value_based_pricing.py` passes the account's TRUE
segment, reaches the I&C branch, and reports C_IC3 at £46.00/MWh endpoint-unbound. Same module,
same book, different information — the second instance of the class `8b450a839` named on its
first, and the reason that finding's own words are worth repeating: *the production caller and
the probe are not asking the same company.*

Full record, including why the one-line repair is filed rather than applied inside a diagnosis
commit (R12 — I already know which way it moves the headline):
`docs/staging/done/WORKER_FINDING_THE_VALUE_ARMS_WHOLE_LOSS_IS_ONE_INDUSTRIAL_ACCOUNT_PRICED_AS_A_HOUSEHOLD_2026-08-26.md`.

---

## 2026-08-26 15:20Z — the segment repair: the sign flips, and the number is still three customers
**[SUPERSEDED — measured on the I&C book. This section already says the win is three industrial
accounts; what it could not know is that those accounts were suspended from the book two days
before it was written. The £3.08M must not be quoted. See the end of this file.]**

The repair: the account's real segment now reaches `estimate_churn_probability` through
world → **door** → desk → arm, so the I&C branch is reachable from a live run for the first
time. A prediction was stamped before the run. Four of five held; the one that failed is the
one that decides how this may be read.

**The control is BIT-IDENTICAL** — net £1,145,681.029513, EV £1,391,261.690785, to the last
decimal place of both runs. The repair does not touch the baseline, so the delta is readable.

| | before repair | predicted | after |
|---|---|---|---|
| `endpoint_at_floor` | 16 | falls | **0** ✅ |
| C_IC3 delta | −£94,314 | ≥ 0 | **+£359,663** ✅ |
| `realised_delta.enterprise_value_gbp` | −£110,731 | positive | **+£2,293,743** ✅ |
| control arm | — | bit-identical | **bit-identical** ✅ |
| `concentration_top_n_share` | 0.9968 | **falls a long way** | **0.9997** ❌ |

**Net margin −£93,555 → +£3,082,499. Enterprise value −£110,731 → +£2,293,743.** The floor
binding is gone entirely: the saturated accounts that had nowhere to go now have a curve that
responds to price.

### Why this is not the thesis proven, stated before anyone quotes the £3.08M

**97% of the win is three customers.** C_IC1 +£1,764,966, C_IC2 +£854,196, C_IC3 +£359,663 —
£2,978,824 of a £2,994,343 net movement. Concentration went UP, from 0.9968 to 0.9997. This
book's economics are three industrial accounts and 256 rounding errors, and that was as true
of the loss as it is of the win. *"A supplier deciding customer-by-customer beats flat rules"*
is not what has been measured. What has been measured is that **pricing three large industrial
accounts on a curve calibrated for them, rather than one calibrated for households, is worth
about £3M on this book.** That is a real finding and a narrower one.

**And the arm now charges 7.0x–16.1x the regulated allowance.** Median chosen margin
£60.00/MWh against Ofgem's EBIT allowance of £3.73–£8.54. `endpoint_at_ceiling` rose 20 → 25
of 58 priced. The arm has stopped being floor-bound and become ceiling-bound; the bound still
decides a large share of its answers, it is simply the other bound.

**The mechanism of the win deserves the same scepticism as the mechanism of the loss.** The
company's churn model OVER-states hazard by 2.4x–7.6x in every elevated bucket (measured
2026-08-26 against a tally of 622 renewal outcomes). So on the I&C branch the arm believes a
large margin will probably lose the customer — P(leave) 0.81 at £46 — charges it anyway
because the expected value still maximises there, and then mostly **does not** lose them.
Four of the five I&C accounts stay. The arm is winning because the world's industrial
customers are stickier than the company believes, which is being wrong in a profitable
direction, not predicting better.

That is the next thing to measure and it is not a tidying task: **an arm that profits from its
own miscalibration has not demonstrated inference advantage.** The honest headline until then
is the narrow one above.

### Two category errors, one repaired

`max_supported_rate_increase_pct()` takes no arguments and derives a single +83.1% bound from
the published **domestic** cap, applied to every segment including industrial. That is the same
error one layer along, it is unrepaired, and `extrapolation_bound` fired 3 times in this run. It
was deliberately left out of this commit: repairing two mechanisms at once makes neither
attributable.

---

## 2026-08-26 16:40Z — inference or luck: measured, and only half of it is visible

`renewal_rate_chain` has logged `believed_p_retain` per priced renewal since the arm was
built, with a comment saying why: *"Carried so the two can be compared afterwards, which is
the only way to find out whether this company's beliefs are worth acting on."* Nothing ever
compared them. `belief_vs_outcome` does — the belief against a **tally** of `event_type`, not
against a second probability.

```
discrimination AUC       0.6463      (0.5 = no information at all)
mean believed retention  0.7042
realised retention       0.7500
calibration error       -0.0458
population               21 retained, 7 left
```

**The belief ranks.** Customers it thought likelier to stay were likelier to stay — modestly,
on a small churned population, but above chance. So the arm's advantage is **not purely a
lucky miscalibration**. It also slightly UNDER-states retention, consistent with the 2.4x–7.6x
hazard over-statement measured this morning.

**And the headline calibration figure is two large errors cancelling:**

| believed p_retain | n | realised |
|---|---|---|
| 0.06 | 2 | **1.00** |
| 0.33 | 4 | **1.00** |
| 0.52 | 2 | 0.00 |
| 0.65 | 5 | **0.20** — inverted |
| 0.93 | 15 | 0.93 |

Well calibrated exactly where most decisions are, and badly wrong in the middle. A single
number would have hidden all of it.

### The caveat is the finding: coverage is 48%

**28 of 58 decisions could be matched to an outcome.** Everything above describes less than
half the arm's answers, and `scored_share_of_priced` is published so it cannot be read as the
whole book.

The artefact now explains its own gap rather than leaving a hole.
`simulation/customer_events.roll_lifecycle_event` returns `None` when `home_move_win_rates`
carries no entry for the renewal month, so these are renewals at which **the world rolled no
churn decision at all** — not renewals whose outcome is unknown. They are excluded rather than
counted as retained, because scoring a belief about retention against a renewal where leaving
was impossible would flatter the arm.

`unmatched_by_year` = 2017: 6, 2018: 6, 2019: 7, 2020: 3, 2021: 2, 2022: 2, 2023: 2, 2024: 2,
and every account in the sample is a **seed** account — C2, C3, C4, C6, C8, C9, at quarterly
term starts. The PROS-* accounts match.

**That is the next thing to open, and it is not a measurement tidy-up.** `home_move_win_rates`
is built from `churn_model._renewal_periods` (acquisition_date + 365n, truncated at the last
settled period) while the arm prices off the run's actual term list, and the seed accounts —
which include the three I&C accounts carrying 97% of the delta — are the ones falling through.
If the accounts that dominate the P&L are also the ones the churn machinery rarely rolls on,
then how much of *any* arm's result is a churn outcome at all is an open question.

---

## 2026-08-26 17:09Z — the answer on the book the director actually asked about

**The instruction, 2026-08-26, restating the ruling of 24 August:** land the I&C suspension,
then re-run the comparison on the book it creates — *"a negative result on the right population
is worth more to me than a £3M headline on the wrong one."*

> **THIS READING PREDATES THE DUAL-FUEL FUNNEL AND IS OWED A RE-RUN.** Both artefacts were
> generated at 17:09Z/17:31Z, before `fb8a8fda5` (2026-08-26 20:35) made the acquisition funnel
> win **gas** legs as well as electricity. Every account the funnel grew inside this A/B's
> window is therefore single-fuel, and the director's own words on that commit are that a
> single-fuel book *"quietly distorts every per-customer number we've been arguing about"* —
> cost-to-serve, churn and lifetime value all move with dual fuel. The figures below are correct
> for the book they ran on and that book is **resi + SME, electricity-only growth**. They are
> **not** superseded in the way the I&C sections above are — the segment question they answer is
> settled — but the magnitude is owed a re-run on the dual-fuel book, and this note is here so
> the next reader does not have to infer it from a commit date. Said once, in the file's own
> terms: an artefact that cannot name its own book is the defect logged as
> `WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26.md`, and this
> paragraph is that finding applied to its own author.

The suspension is now live: `docs/design/curriculum/served_segments.json` reads
`served: ["resi", "SME"]`, and C_IC1, C_IC2, C_IC3, C_IC4 and C_IC3g are in `suspended_accounts`.
The control book is **131 accounts** where the superseded runs had 172. Artefacts:
`docs/observability/value_cycle_ab_resi.json` (resi + SME, the served book) and
`value_cycle_ab_resi_only.json` (households alone).

### Which way it went

**The value arm wins. On households it also wins.** Said plainly, because the instruction was to
say it plainly either way: *per-customer pricing does beat flat rules on this supplier's
residential book* — it is not the negative result the director was braced for.

| | control (flat £2.00/MWh) | value arm | delta |
|---|---|---|---|
| net margin | £79,688.17 | £96,461.44 | **+£16,773.28** (+21.0%) |
| enterprise value | £224,396.37 | £235,196.15 | **+£10,799.78** (+4.8%) |
| gross margin | £433,174.76 | £419,023.25 | **−£14,151.51** |
| bad debt | £32,984.26 | £30,393.17 | −£2,591.09 |
| accounts at end | 131 | 130 | −1 |
| churned | 32 | 34 | +2 |

**Households alone** (I&C *and* SME suspended): net **+£11,828.26**, EV **+£9,759.28**. Same
sign, same magnitude class. SME contributes about £4,900 and changes no conclusion — which is
the measured basis on which SME stays served.

### Why this is a thin positive and not a vindication

The number is real and it is small, and three things about its shape matter more than its sign.

**1. It is still a handful of accounts.** `concentration_top_n_share_of_absolute_movement` =
**0.9941** — barely moved from the 0.9968 of the I&C run. Of 211 accounts compared, 60 moved,
and 15 of them are 99.4% of all movement:

| account | control | value arm | delta |
|---|---|---|---|
| C9 | £1,716.56 | £6,752.46 | **+£5,035.91** |
| C8 | £1,920.42 | £5,591.40 | **+£3,670.98** |
| C6 (SME) | £969.80 | £4,423.08 | **+£3,453.28** |
| C5 (SME) | −£526.04 | £1,070.70 | **+£1,596.74** |
| C2 | £2,037.92 | £2,910.41 | +£872.49 |
| C1 | £1,237.22 | £466.15 | **−£771.06** |
| C3 | £1,676.33 | £964.98 | **−£711.35** |

Every one is a **seed** account. The ~200 accounts the funnel actually grew are the rounding
errors now. Suspending I&C changed *which* small set of accounts carries the result; it did not
make the result broad. "A supplier deciding customer-by-customer beats flat rules" is still not
what has been shown — what has been shown is that **it beats flat rules on about seven
households and two small businesses.**

**2. Half the arm's answers are a bound's, not an inference's.** It priced **42** renewals out of
a 131-account book and declined 8. Of the 42, **20 ended at the ceiling** (`endpoint_at_ceiling`
= 20, `endpoint_at_floor` = 0, `extrapolation_bound` = 2). Median chosen margin **£57.75/MWh**
against the control's £2.00. An account whose price is set by where the grid was cut is not an
account whose price was inferred.

**3. The control is weak and the ratio has to sit beside the win.** This company's flat
£2.00/MWh is **23.4%–53.6%** of the EBIT allowance Ofgem grants an efficient supplier
(£3.73–£8.54/MWh, cap period 11a). A 21% net improvement over a baseline priced at a third of
the regulated allowance is a smaller achievement than the percentage suggests.

### The number that does not fit, and it is the next thing to open

**Gross margin FELL by £14,151 while net margin ROSE by £16,773** — a £30,924 divergence, of
which lower bad debt explains only £2,591. `total_gross` is revenue minus wholesale;
`total_net` is after levies, network, capital and bad debt.

This is recorded as **observed and unexplained** (R9). It is not a rounding artefact and it
matters to the reading: an arm that charges a median £57.75/MWh against £2.00 and ends the run
with *less* gross margin is not obviously winning by pricing at all, and until the £28k is
attributed, the mechanism behind the +£16,773 is not established. The candidate explanations —
volume lost to the two extra churned accounts, and cost lines that fall with it — are
**inferred, not measured**, and are deliberately not asserted here. Attributing that divergence
is the next step, ahead of any further mechanism repair.

`belief_vs_outcome` coverage on this book is **24 of 42 priced** (57%), so the inference-versus-
luck question of the section above is re-opened at this scale and is not carried over: the AUC
of 0.6463 was measured on the I&C book and does not describe this one.

### What this does and does not license

It licenses saying that the per-customer decision engine earns more than this company's flat
rule on the book it actually serves, by £16,773 over the run, with the three caveats above
attached. It does **not** license a headline percentage, a claim about households in general, or
any figure carried over from the superseded sections — and the £3.08M in particular is now a
fact about five accounts the company no longer serves.

---

## 2026-08-26 21:45Z — why the delta concentrates: the arm can only act at renewals, and the book is young

The residential re-read left one thing unexplained. Suspending I&C removed a 500x distortion and
the concentration barely moved — 0.9941 to 0.9935 — and on the resi-only book the top three
movers are C9, C8 and C2, all *residential* seed accounts. So the concentration was never about
segments. This is what it is about, measured rather than argued.

**The arm acts ONLY at renewals**, and on the electricity accounts it can price:

| | count | share |
|---|---|---|
| electricity accounts on the book | 210 | — |
| with at least one renewal decision in the window | 156 | 74.3% |
| **the arm can never act on at all** | **54** | **25.7%** |

And of the 156 it can touch, most it can touch barely:

| renewal decisions | accounts | cumulative |
|---|---|---|
| 1 | 53 | 34.0% |
| 2 | 29 | 52.6% |
| 3 | 28 | 70.5% |
| 4 | 9 | 76.3% |
| 5–9 | 37 | 100% |

Median **2**, mean 2.96. **Only 37 accounts — 17.6% of the priceable book — have five or more
renewals**, and those are where a per-customer strategy has room to compound: each decision moves
the rate the next one starts from, so the effect is cumulative in a way a single decision is not.

That is the concentration, fully explained. C1–C9 were acquired in 2016 and have nine renewals
each; a PROS-2024 account has one. **Exposure to a renewal-time arm is proportional to renewal
count, and this book's renewal count is dominated by nine accounts.** Changing which segments are
served could never have fixed that, and did not.

### What follows, and what does not

**This is not a defect and there is nothing here to repair.** A four-year-old supplier really does
have a young book, and an arm that prices at renewal really can only act when a customer renews.
Both are faithful.

**It does bound what any A/B on this book can show.** A per-customer pricing result measured here
is a result about 37 accounts with room to compound plus 119 with one or two decisions each — and
that is worth stating beside any future headline, positive or negative.

**The lever is the WINDOW or the BOOK'S AGE, and both are curriculum — the director's, not this
seat's (R13).** The baseline world changes only for fidelity reasons decided blind to company
P&L, and this seat has just watched book age move the company's P&L, which makes it exactly the
change it must not make. Recorded here for whoever holds the curriculum. A longer window over the
same real history, or a book seeded with more mature accounts, would give the arm more decisions
per customer; whether either is the world this company should live in is not an engineering call.

---

## 2026-08-26 22:00Z — the two artefacts never disagreed: only one of them passes a ceiling

The delivery seat drew this as arithmetic: *"establish why the value arm's maximiser still runs
to its own bound on half the book, and either make the optimum interior for a reason that is
about the customer, or report in the A/B artefact that the arm's win is a bound's and not an
inference's."* It named two figures that appear to contradict each other and asked for them to
be reconciled with their populations named before anything else was touched.

They do not contradict each other, and the reason is not a population difference alone.

### The two figures, and what each was actually measuring

| | `value_based_pricing_arms.json` (the coupler) | `value_cycle_ab*.json` (the realised A/B) |
|---|---|---|
| unit | **one decision per ACCOUNT** | **one decision per RENEWAL EVENT the run reached** |
| when | a single instant (`as_of_year` 2025) | each term's own start, across the whole window |
| decisions | 397 | 42 priced / 8 declined (resi book, 17:09Z) |
| `endpoint_at_ceiling` | **1** | **20** |
| `endpoint_at_floor` | 18 | 0 |
| `ceiling_bound` | 0 for every account | 20 |
| **lawful ceiling passed** | **none — `max_offered_rate_gbp_per_mwh` is not passed at all** | the Ofgem domestic cap for that term's cap window |

The filed diagnosis (`WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_
UNBOUNDED_2026-08-25`) recorded "interior optima on 255 of 263 accounts" against the A/B's "20 of
42 at the ceiling". Both were true when written. The 255-of-263 figure is also **stale**: the
coupler now prices 397 accounts and reports 19 at a grid edge, of which 18 are at the FLOOR —
micro-consumption meters where the profit-maximising commodity margin is negative — and exactly
**one** at a ceiling.

### Why the same module gives two answers, and it is not the population

`tools/couple_value_based_pricing.py` passes `decide_margin` no `max_offered_rate_gbp_per_mwh`.
Read the module: with no ceiling, `lawful = candidates`, `ceiling_bound` is `False` by
construction for every account, and `endpoint_side == "ceiling"` can only mean *the top of the
candidate grid under the churn model's own support bound*. So the coupler's near-zero ceiling
count is **not evidence that the cap does not bind** — it is a count that could not fire.

That is the same defect class `8b450a839` fixed on the other call site, where the chain passed
the arm no ceiling and the cap landed afterwards as a clamp, leaving `ceiling_bound` — the flag
whose entire job is to say the cap chose the price — structurally unable to fire. Here it was
never a bug in the decision; it was a bug in **reading two artefacts side by side that publish
the same field name over different bounds**. An R15 FAIL-OPEN one level above the arithmetic: a
control that cannot fire reads exactly like a control that fired zero times.

**What landed.** The coupler now publishes a `population` block, and each row carries
`lawful_ceiling_gbp_per_mwh` read off the arguments the call site actually passes — so the
disclaimer lifts by itself the day a ceiling is threaded through, rather than rotting as a
comment. The A/B's new `cross_section_reconciliation` READS that block instead of restating it,
and refuses to reconcile against an artefact that predates it.

### The reconciled answer, in one line

**The optimum IS interior to what the company's own belief supports — and it lies ABOVE what the
company may lawfully charge.** Both artefacts say this and neither could say it alone. Priced
without a cap, the maximiser turns over inside the model's support on 396 of 397 accounts (the
captive-floor repairs of 2026-08-25 worked). Priced under the cap at a real term, roughly half
the arm's answers sit on the cap, because the interior optimum is above it.

That is not a contradiction and it is not flattering. A margin pinned to the ceiling is a margin
the arm did not choose: lift the ceiling and it goes higher, which is precisely what
`ceiling_bound` records. **"The advantage must come from INFERENCE, never ACCESS" fails just as
completely when the advantage comes from a BOUND.**

### So the artefact now says so in its own headline

`bound_attribution` is the section `decision_shape` could not be. That block counted
`ceiling_bound` honestly and left it among fourteen other integers, so a run in which the cap set
half the arm's prices read exactly like one in which it set none. The new section:

- names the two bounds **apart** — the lawful cap is an external constraint a real supplier
  really has; the support bound is this company's own ignorance — and never double-counts a
  decision both reached;
- splits the **median chosen margin** by who decided it, because a ceiling-decided median far
  above the freely-chosen one says the arm wanted more than the law allows on exactly the
  customers it was stopped on;
- attributes the **realised money**, not only the count. On this book `margin_movers` has
  repeatedly reported ~99% of absolute movement on fifteen accounts, so one capped renewal on the
  account carrying the delta *is* the headline and a count-only reading would call it a footnote;
- computes `decided_by` in three reachable branches — `the customer`, `mixed`, `a bound` — and
  writes a sentence from the live counts, so it cannot describe a previous run.

### What must NOT happen next, in the artefact's own words

`bound_attribution.what_would_change_this` begins **"NOT moving the ceiling."** The optimum
becomes interior for a reason about the customer only when the churn belief turns the expected
value over *below* the cap — i.e. when a supplier-specific rise is punished harder than it is
today. Any change to that sensitivity is a fidelity change: it must cite a published source
(Ofgem switching data, a regulatory or academic elasticity estimate), never a chosen number, and
must be decided blind to what it does to this delta (R13, R12). **If no defensible curve makes
the optimum interior, that is the answer and it belongs in the artefact rather than in a moved
bound.** Which is what this section is.

### What is still open, and it is now stated rather than implied

The customer-level question. The cap binding on half the priced renewals means the churn model
does not punish a supplier-specific rise before the law does — the arm asks for a margin the
regulator's own cap has to stop. Beside that sits the credibility figure the coupler already
publishes: a median chosen margin of £65/MWh against an Ofgem EBIT allowance of £2.50–7.58/MWh
for an efficient supplier, roughly 9× the top of the range. The coupler's verdict already says
repricing the control to average behaviour would move it by a factor of two to four and "leave
the arm's answer an order of magnitude away, so the arm is not beating a straw man — it is asking
to charge many times what a regulated efficient supplier earns."

**This is why the arm stays unwired from the renewal desk**, and it is a better-stated reason
than the one it replaces.
