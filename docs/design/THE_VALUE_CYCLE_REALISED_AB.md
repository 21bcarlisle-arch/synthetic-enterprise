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
> | reading | book — segments, accounts, artefact + commit | net delta | status |
> |---|---|---|---|
> | −£110,731 EV | resi + SME + **I&C** · 172 ctl → 170 val at end · `value_cycle_ab_prior_2026-08-26T0802Z.json` @ `6089f90a9` | −£93,555 | superseded |
> | +£2,293,743 EV | resi + SME + **I&C** · 172 ctl → 170 val at end · `value_cycle_ab.json` @ `b0f5ee0e8` | +£3,082,499 | superseded — 99.97% of it 15 I&C accounts |
> | +£10,800 EV | resi + SME · 131 ctl → 130 val at end · `value_cycle_ab_resi.json` @ `4e884cdbf` | +£16,773 | superseded 2026-08-27 — [the renewal schedule was broken under it](#2026-08-27--the-renewal-schedule-was-repaired-and-the-belief-quality-result-did-not-survive-it): only 28 of 58 priced renewals ever met a churn roll |
> | **+£7,149 EV** | **resi + SME** · **210 billing accounts settled in window** (187 dual-fuel, 89.0%; 210 with an electricity leg), **126 ctl → 123 val at end** · `value_cycle_ab_resi_renewal_fixed.json` @ `353fe96b8` | **+£7,066** | **current — full window (`report_end: null`), generated 2026-08-27T09:49:09Z; [what the £7,066 actually is](#what-the-7066-actually-is--read-straight-off-the-same-artefact)** |
>
> **Clock (R14).** Every delta in this table is *settled* — `net_margin_gbp` summed from the world's
> own settled records after wholesale, levies, network, capital and bad debt, before cost-to-serve.
> The EV column is the arms' `enterprise_value_gbp` difference on the same basis. No figure here is
> billed or banked, and none of them is anything the company believed.
>
> **Provenance note, 2026-08-27.** Rows 1–3 are left exactly as they were written. Reading their
> artefacts back off disk to fill the new book column turned up one disagreement worth stating
> rather than silently correcting: row 1's file records `enterprise_value_gbp: −118,252`, not the
> −£110,731 the row quotes. The row is kept as published; the artefact is the record.
>
> **Why the current row was not re-run at HEAD, checked rather than assumed.** Its artefact is
> stamped `353fe96b8` and HEAD has since moved to `5c1a05283`. `git diff --name-only 353fe96b8..HEAD
> -- company/ saas/ simulation/ sim/ tools/` returns **nothing**: every commit in between is
> documentation, a publish, or this file. The arm, the churn model, the world and the settlement
> path are byte-identical, so a re-run would spend 25 minutes reproducing £7,066. **Do not re-run it
> because the commit stamps differ — run that diff first.** It becomes stale the moment that command
> returns a path.
>
> **What "book" means here, and why it is now in the table.** Until 2026-08-27 the artefacts could
> not name their own population — the book resolves at import time from the curriculum file, so a
> run on the wrong segments produced a clean, complete, entirely plausible artefact
> (`WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26`). Only the last row's
> artefact carries a `book_identity` block; rows 1–3 have their accounts read from the arms
> themselves and their segments inferred from the run that produced them. The filename was never the
> control: `value_cycle_ab_resi.json` in fact served resi **and** SME.
>
> **The block was half the repair, and the other half landed 2026-08-30.** Naming the book at
> ARTEFACT-ASSEMBLY time is a different measurement from naming the book each arm RAN on:
> `served_segments()` resolves from the curriculum file on every call, an arm is a full phase-4c
> pass, and a curriculum edit between the control arm and the value arm therefore put the two arms
> on two books while the artefact reported the second one for both. It also made a cross-arm check
> impossible — comparing one function's value against itself has no failing branch. The run now
> snapshots the book beside each arm (`book_at_run`), records whether it came from the curriculum
> or from an `SE_SERVED_SEGMENTS` override, and **refuses** to report a delta whose arms served
> different segments (`same_book_across_arms`, published inside `book_identity` so the verdict
> cannot be deployed apart from the books it grades). `arm_identity` refuses a third differing
> policy field; this refuses a second population, which is the same class of uncontrolled
> variable. An arm whose book was never recorded reports `served_segments: null` and says why,
> rather than borrowing today's curriculum. Rows 1–3 are unaffected and are not backfilled: their
> books cannot be established honestly after the fact, which is what this paragraph is for.
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

---

## 2026-08-27 — the world answered a 28× price rise with two churns, and neither side is lying: they price against different references

**THE OUTPUT IS A MEASUREMENT, NOT A REPAIR.** Nothing in the company's belief and nothing in the
world's switching response is changed by this section. Where the arithmetic lands on the world's
curve it is recorded for the curriculum (R13) and left there.

Read on `docs/observability/value_cycle_ab_resi.json` (generated 2026-08-26T17:09:29Z). No new run:
both sides were already published.

### The question

The value arm repriced 42 residential renewals at a median `median_margin_gbp_per_mwh` of 57.75
against the control's `control_margin_gbp_per_mwh` of 2.00 — nominally 28× — and the world
returned 34 churn events against the control's 32. Two. If the world does not punish price, then
every realised A/B result to date is a fact about the switching curve and the +£16,773 headline
cannot be attributed to inference. That is the fourth way for the arm's advantage to be hollow,
after ACCESS, after the horizon, and after the BOUND the ceiling section closed.

### Finding 1 — the published `calibration_error` of 0.0107 is a cancellation, not a calibration

`belief_vs_outcome` reports `mean_believed_p_retain` 0.760675 against `realised_retention_rate`
0.750 on 24 matched decisions, a `calibration_error` of 0.0107. Summed into leavers that is the
comparison the direction asked for, and it agrees almost exactly:

| believed p_retain | n | expected leavers | realised leavers | gap |
|---|---|---|---|---|
| 0.3318 | 4 | 2.673 | 0 | **−2.673** |
| 0.5417 | 1 | 0.458 | 1 | +0.542 |
| 0.6158 | 4 | 1.537 | 4 | **+2.463** |
| 0.9283 | 15 | 1.076 | 1 | −0.076 |
| **total** | **24** | **5.744** | **6** | **+0.256** |

The aggregate gap is +0.256 leavers on 5.744 expected — 4.5%. The sum of the *absolute* bucket
gaps is **5.753**, which is 100.2% of the quantity being predicted. Every unit of predictive
error is present; the reported statistic is the residue after two errors of ~2.5 leavers each
cancel in opposite directions. **An aggregate calibration figure over a bimodal decision set is
the R15 net-statistic shape** — it cannot fail on this data, because the two halves are
constructed to net out. `calibration_error` should not be read as evidence of a calibrated belief.

The `discrimination_auc` of 0.6944 is carried entirely by the top bucket: 15 of 24 decisions sit
at believed p_retain 0.928 and 14 of those were retained. Strip that bucket and the ranking on the
9 at-risk decisions is **inverted** — the four the company thought were most likely to leave all
stayed, and four of the five it thought were safer all left. The arm ranks the book correctly only
because most of the book was never at risk.

### Finding 2 — the world is not forgiving; at the arm's own price position it multiplies churn 5.7–7.7×

The price leg is live and wired. `simulation/run_phase2b.py:1676` passes
`new_rate_gbp_per_mwh=unit_rate` — the arm's own chosen rate — into `roll_lifecycle_event`, which
computes `_price_differential_vs_market` against the published SVT and applies
`churn_position_multiplier`. Landed 2026-08-25; this is not the pre-fix world.

The arm's rate sits £55.75/MWh above the control's. Against the SVT of the years in the roster
that is a position 30–40 points of SVT dearer, wherever the control itself sat:

| term | SVT £/MWh | £55.75 as % of SVT | churn multiplier |
|---|---|---|---|
| 2017-04-01 | 140.00 | +39.8% | **×7.72** |
| 2018-04-01 | 152.50 | +36.6% | **×7.06** |
| 2019-04-01 | 185.60 | +30.0% | **×5.73** |

**"28×" is a margin ratio and it is not a rate position.** Twenty-eight times a £2/MWh margin is a
~+37% move in the rate a household actually compares, and the world's response to that is a
five-to-eightfold increase in the chance they leave. The world punishes price hard.

### Finding 3 — the world's own curve predicts 7–18 flips; it produced 3

The dice roll is `_random.Random(f"{billing_account}_{term_start_str}").random()` —
**seeded on the account and term only, so it is byte-identical in both arms.** An arm can only
change an outcome by moving `effective_p_retain` across that fixed roll. The flip window is
therefore exactly the increase in churn probability, and at ×7 with `WORLD_MAX_CHURN_PROBABILITY`
0.95 binding:

| control p_churn | arm p_churn | flip window | expected flips on 24 |
|---|---|---|---|
| 0.05 | 0.350 | 0.300 | 7.2 |
| 0.10 | 0.700 | 0.600 | 14.4 |
| 0.20 | 0.950 | 0.750 | 18.0 |

`churn_roster_diff` records **3** accounts churning only under the arm (C1_2, C3, C7) and 1 only
under the control (PROS-2018-0003). Three, against a floor of seven on the world's own arithmetic.
The world's curve and the world's realised roster disagree with each other — so the shortfall is
not the curve being soft.

### Finding 4 — the reason, and it is that the two sides price against different references

The company's belief keys on a **delta against the customer's own previous rate**
(`company/crm/churn_model.py:305`, `rate_increase_pct = (new − old) / old`, net of
`market_move_pct` at line 310 — a delta against a delta). The world keys on a **level against the
published SVT** (`simulation/customer_events.py:67`, `(new − svt) / svt`).

These are different quantities and they disagree in both directions:

- A supplier that was **cheap and moves to average** reads as a large rise in the company's frame
  (high believed churn) and as **parity** in the world's (multiplier ≈ 1.0). That is bucket 1:
  four accounts believed 67% likely to leave, **none did**.
- A supplier that was **dear and barely moves** reads as flat in the company's frame (low believed
  churn) and as **+30% vs SVT** in the world's (multiplier ≈ 6×). That is bucket 3: four accounts
  believed 38% likely to leave, **all four did**.

That is the observed inversion, in the right direction, on both tails. It also explains Finding 3
without any appeal to a soft curve: the ×7 multiplier is computed against SVT, and most of the 42
renewals were not 37% above SVT — the company's own belief says so. Inverting the model at
believed p_retain 0.928 (base 0.10, tenure discount −0.05, sensitivity 0.8) gives a rate move of
**~3–4%** for 15 of the 24 scored decisions. The decision set is **bimodal — roughly 15 near-flat
renewals and 5 large rises — and the median margin of 57.75 does not describe it.**

### The verdict: it is the third, and the effective n is 4, not 42

Not "the belief over-predicts" — it over-predicts on one tail and under-predicts on the other by
almost identical amounts. Not "the world under-punishes" — its multiplier at the arm's position is
5.7–7.7× and its price leg is correctly wired. **The sample cannot separate them**, and it is far
smaller than 42:

- 42 priced → **24** have any outcome at all. `unmatched_decisions` is **18 (43%)**: the world
  rolled no churn decision, because `build_home_move_win_rates` carries no entry for that renewal
  month. Those decisions are **unpunishable at any multiplier**.
- 24 scored → **9** sit outside the top believed bucket, and those 9 carry all the information.
- The *causal* question — did repricing cause departures — rests on the roster difference, which
  is **3 in and 1 out**. **n = 4.**

A ×7 world response and a bimodal 42-decision sample with 43% of it unrollable cannot distinguish
a mis-calibrated belief from a mis-referenced one on four differing outcomes.

### What would separate them

1. **Close the 18-unmatched hole first.** Any measurement where 43% of the treatment is
   structurally incapable of producing an outcome has a denominator problem before it has a
   calibration problem. `roll_lifecycle_event` returning `None` for a renewal the arm priced is
   the defect; the arm's term list and `churn_model._renewal_periods` derive their schedules
   independently and must be reconciled.
2. **Measure the slope, not the level — a price ladder.** Run the arm at several margin
   multipliers on the same book and the same seeds, and compare the *slope* of believed churn
   against the *slope* of realised churn. Because the roll is fixed per (account, term_start), a
   ladder needs no matched pairs and no distributional assumption: the flip count as a function of
   price is a direct read of the world's curve against the company's. It converts an n=4 level
   comparison into a dose-response with 42 decisions at every rung, and it is the only design here
   that can separate "wrong level" from "wrong reference".
3. **Publish both references side by side per decision.** `value_arm_log` should carry the world's
   `rate_vs_svt_pct` next to the company's `rate_increase_pct`. Finding 4 took an inversion in a
   4-row bucket table to detect; it would have been one column.

### For the curriculum, recorded and not acted on (R13)

Nothing here says the world's switching response is wrong. Its multiplier is steep, its wiring is
correct, and its extrapolation above saturation was already chosen against the company. The one
item that belongs in front of the director is the **reference-frame divergence itself** — the
company is structurally unable to see the quantity the world punishes, because
`rate_increase_pct` never contains the SVT level. Whether a real supplier can see its own position
against the published SVT is a question about the world's observables, not about the company's
model, and it is the director's to rule on. It must be decided blind to what it does to this
delta.

**The +£16,773 headline is not refuted and it is not confirmed.** It rests on four differing churn
outcomes and a belief whose aggregate agreement with the world is arithmetic coincidence.

---

## 2026-08-27 (later) — the ladder: the win is NOT price. The world's curve and the company's agree about how hard price bites, and disagree by 6× about where it starts

> **READ THE FULL-WINDOW LADDER BEFORE THIS ONE — its headline ratio is the better-powered
> reading of the same statistic, and it points the other way.**
>
> | statistic | this section (2019) | [full window, 2016–2025](#2026-08-27-full-window--the-ladder-at-20162025-the-world-bites-less-than-the-company-believes-and-the-2019-reading-said-the-opposite) |
> |---|---|---|
> | common population (effective n) | 6 decisions | **22 decisions** |
> | `median_world_over_believed` | **1.160** — world bites *harder* | **0.768** — world bites *softer* |
> | decisions the world never rolled | 18, on 6 accounts | **0** |
>
> The section below is **kept and not rewritten**, and the reading it rests on — that the win is not
> price — is *unchanged*: both windows agree the world responds to price and that the arm is not
> charging into a curve it cannot see. What does **not** survive is the **direction and size of the
> 1.16× figure**, which was computed on 6 decisions because 18 of the 2019 window's priced renewals
> rolled *after* 2019-12-31 and were silently dropped. That truncation is a known defect, not merely
> less data. The honest statement is **not** "the 2019 result was wrong" but *"the 2019 result was
> never powered, and the full window is the first reading of it that is"* — and 22 is still small.
>
> **Quote 0.768, not 1.160.** Everything else in this section stands.

**THE HEADLINE, because the direction asked for it in the place a reader hits it.** The fourth way
for the arm's advantage to be hollow — that it comes from PRICE rather than from prediction — is
**not supported**. The world punishes price hard and the company's own churn model knows roughly
how hard: over six rungs the world's churn probability rises **1.16× faster** than the company
believes it does (median over decisions), not the many-fold gap a "the world doesn't punish price"
story needs. The arm is not charging into a response it cannot see.

What the ladder *does* find is a **LEVEL error, not a slope error**, and it runs the other way: at
the flat rule the company believes these customers are **33%** likely to leave and the world says
**5.5%**. A supplier that thinks its book is six times more flighty than it is prices *below* what
the world would tolerate. That is money left on the table, not money taken from a forgiving curve.

**THE OUTPUT IS A MEASUREMENT, NOT A REPAIR (R13).** Nothing in the company's belief and nothing in
the world's switching response is changed by this section.

Instrument: `tools/run_price_ladder.py`. Artefact:
`docs/observability/value_cycle_price_ladder_2019.json`.

### What was run, and the one control that makes it readable

The value arm, six times over the same book and the same seeds, at fixed multiples of **its own
chosen uplift over the flat rule** — `flat + k × (chosen − flat)`, for k ∈ {0, 0.25, 0.5, 1, 1.5,
2} — plus a real flat-rules control run.

That parameterisation is chosen so that **k = 0 is the flat rule exactly**, which makes rung zero a
NULL CONTROL rather than a nearby price. It is checked, not asserted:

| | rung 0 | flat-rules control |
|---|---|---|
| accounts churned | 2 | 2 |
| roster difference | — | **none** |
| net margin | £16,354.767758 | £16,354.767758 |

**Identical to the last decimal.** So the multiplier scales the uplift and nothing else, and every
slope below is a reading of the world's curve rather than of the ladder's own plumbing. The
mutation that breaks it is named at the assertion
(`tests/company/pricing/test_price_ladder_rung.py`): parameterise the rung as `k × chosen` and rung
zero becomes a zero-margin offer the control never made.

**The rung is scored at the price it delivers.** `decide_margin` takes the multiplier and re-scores
*inside* the decision. Scaling the uplift afterwards would leave `believed_p_retain` describing a
rate the customer is never offered — the believed leg would be flat across every rung while the
realised leg moved, and "the company cannot see the response" would be an artefact. That is the
same defect the 2026-08-26 ceiling repair closed from the other side, and
`test_the_belief_is_taken_at_the_rung_and_not_at_the_unscaled_choice` fails against it.

**And the scored price is the charged price.** The harness computes each decision's position
against the published SVT independently and reconciles it against the world's own logged
`price_differential_vs_svt` at the same renewal: **58 decisions, largest gap 0.005 percentage
points.** If chain writer 4 had clawed a rung back, the two would diverge.

### The two slopes, side by side

Common population: decisions priced **and** rolled by the world at **every** rung — 6 of them.
Rungs above 1.0 churn accounts earlier, which deletes their later renewals, so each rung's own
population is not comparable to the next one's; the attrition is 12 → 12 → 10 → 8 → 8 → 8 rolled.

| k | delivered uplift | vs own prior rate | vs published SVT | realised non-renewals | believed non-renewal rate |
|---|---|---|---|---|---|
| 0.00 | £0.00 | +1.0% | −12.9% | 0/6 — 0.000 | 0.206 |
| 0.25 | £11.15 | +6.1% | −5.8% | 0/6 — 0.000 | 0.254 |
| 0.50 | £23.94 | +12.5% | +2.8% | 1/6 — 0.167 | 0.337 |
| 1.00 | £54.21 | +28.0% | +24.4% | 3/6 — 0.500 | 0.521 |
| 1.50 | £90.38 | +45.2% | +50.3% | 3/6 — 0.500 | 0.697 |
| 2.00 | £132.33 | +63.7% | +80.2% | 3/6 — 0.500 | 0.840 |

**The two slopes, per £/MWh of delivered uplift: realised +0.004261, believed +0.004955 — a ratio
of 0.86.** Against the company's own reference the pair is +0.009032 / +0.010388 (0.87); against
the world's, +0.006006 / +0.007004 (0.86). The answer does not depend on which reference the x-axis
is drawn in.

**Read the realised leg's saturation before reading its slope.** It stops at 3/6 from k = 1 onward.
That is not the world refusing to respond: the roll is fixed per (account, term_start), and the
three that never flip drew low rolls whose flip thresholds their world curves never reach — C1's
2016-12-31 renewal needs a churn probability above 0.835 and the top rung takes it to 0.271. A flip
count over six decisions can take seven values, so this leg is *coarse by construction*, and its
0.86 is the weakest number in this section.

### The same comparison at full power — the world's own curve against the belief

The world writes its own churn probability into the event log at every renewal it rolls. Comparing
the two probability CURVES is the same question with the sampling noise taken out: **paired per
decision**, six prices each, no matched pairs to find and no population to balance. n stops being
the flip count and becomes 6 decisions × 6 rungs = **36 paired observations**.

| account | renewal | price range | world slope /£ | believed slope /£ | world ÷ believed | world p(leave) low→high | believed low→high |
|---|---|---|---|---|---|---|---|
| C1 | 2016-12-31 | £49.5 | +0.00467 | +0.00907 | 0.515 | 0.030 → 0.271 | 0.360 → 0.808 |
| C1 | 2017-12-31 | £153.0 | +0.00707 | +0.00454 | 1.558 | 0.022 → **0.950** | 0.092 → 0.746 |
| C5 | 2016-12-31 | £79.5 | +0.00849 | +0.00800 | 1.061 | 0.038 → 0.698 | 0.284 → 0.918 |
| C5 | 2017-12-31 | £215.0 | +0.00470 | +0.00374 | 1.258 | 0.043 → **0.950** | 0.092 → 0.843 |
| C7 | 2016-12-31 | £77.5 | +0.00576 | +0.00776 | 0.742 | 0.030 → 0.468 | 0.313 → 0.906 |
| C7 | 2017-12-31 | £219.5 | +0.00460 | +0.00352 | 1.305 | 0.045 → **0.950** | 0.092 → 0.822 |

**Median world ÷ believed = 1.16; mean 1.07.** The company over-predicts the response on 2
decisions and under-predicts on 4. Three of the six hit `WORLD_MAX_CHURN_PROBABILITY` = 0.95 at the
top rungs, which **truncates the world's curve and biases its measured slope DOWNWARD** — so 1.16
is a floor, and the world if anything bites harder than this.

**The pooled figure is 1.98 and it should be distrusted, as the artefact says in its own `caveat`
field.** Pooling weights by whichever account the arm happened to price over the widest range, and
it mixes the level differences below into a slope. The median is the answer; the pooled figure is
published beside it so the disagreement is visible rather than hidden by a choice of estimator.

**The level, which is where the real error is.** Read the last two columns at the LOW rung. The
world puts these customers at 0.022–0.045 chance of leaving under flat pricing; the company
believes 0.092–0.360. Pooled intercepts: **world 0.055, company 0.328.** The company's model is
roughly right about the *derivative* and roughly 6× wrong about the *starting point*.

### The two references, now a count instead of a bucket table

Finding 4 above took an inversion in a four-row table to detect. It is one column now:
`rate_vs_svt_pct` is published beside `rate_increase_pct` on every decision.

**52 of 166 decisions (31%) disagree in SIGN** — the company reads a price rise where the world
reads a position below the SVT, or the reverse. Mean company reference +21.9%; mean world reference
+12.8%. **33 decisions** are the named tail: the company sees a rise above +10% while the world
sees the customer still *below* the standard variable tariff. C4's 2017-10-01 renewal is the
cleanest instance — the company reads **+63.2%** against that customer's own prior rate and the
world reads **+9.7%** against the published SVT, and the company's belief that they are 82% likely
to leave is a belief about a price rise the world barely registers.

Only the company's side is written by the chain. The world's is joined by the harness, deliberately:
**whether a supplier can see its own position against the published SVT is a question about the
world's observables and is the director's under R13**, not something this writer settles by handing
the company the number.

### The 18 unmatched, per account

The direction: *"either close the 18-unmatched hole or state per account why no decision was
rolled."* Stated. It is **18 decisions on 6 accounts** — C2, C3, C4, C6, C8 and C9, each priced at
three renewals — and for every one of the six the world rolled **no lifecycle event at any renewal
inside this window**, so `build_home_move_win_rates` carries no row for them at all and
`roll_lifecycle_event` returned `None`. Not a schedule mismatch on any of them: zero decisions fall
in the "the world's roster names other months" class.

**It is a diagnosis and not a repair.** Closing it means reconciling the arm's contract term list
with `churn_model._renewal_periods`, which changes which renewals the world rolls a churn decision
at — a baseline-world change, decided under R13 blind to what it does to any company delta, and
recorded for the curriculum rather than made here. **It does not bound this ladder**: the roll is
fixed per (account, term_start), so an unrolled decision is absent from every rung equally.

### Which verdict this supports, and what it does not settle

Of the three the 2026-08-27 section left open, plus the fourth the direction named:

| | ladder's answer |
|---|---|
| "the world under-punishes price" | **refused.** World slope +0.0056/£ pooled, and three of six decisions saturate the world's own 0.95 ceiling |
| "the win is price, not prediction" | **refused.** The two slopes agree to within 16%, and the bias is toward the world biting *harder* |
| "the belief over-predicts" | **supported, on LEVEL not slope.** 0.328 believed vs 0.055 actual at the flat rule |
| "the sample cannot separate them" | **superseded for the slope question** — 36 paired observations, not n = 4. Still true of the P&L question |

**What this does NOT do is confirm the +£16,773.** It removes price as an explanation for it and
says nothing about whether the arm ranks customers correctly — that is the discrimination question,
and the AUC of 0.694 carried entirely by one bucket is still the honest reading there.

**Two limits, stated rather than buried.** (1) This ran on the **2016-2019 window**, not the full
one the headline rests on. The truncation should be harmless — the roll is seeded on (account,
term_start) alone and every derivation reads a prefix of the settled book — and that is *checked*
rather than argued: the full-window artefact reports **18** unmatched decisions across 2017/2018/
2019 at six per year, and the 2019-window ladder reports the same **18**, on the same six accounts,
with every row of the full run's published sample present in the ladder's set. What truncation does
cost is population: the common set is 6 where a full-window ladder should reach roughly 15-20,
because the arm keeps pricing renewals after 2019. **Re-running at full window is the immediate
next increment and this section will be re-read against it.** (2) Six decisions is six decisions.
The paired design earns 36 observations from them; it does not turn 6 accounts into 20.

### For the curriculum, recorded and not acted on (R13)

Unchanged from the section above and reinforced by it: the **reference-frame divergence** is the
item for the director. The company is structurally unable to see the quantity the world punishes —
`rate_increase_pct` never contains the SVT level — and 31% of decisions have the two references
pointing in opposite directions. Whether a real supplier can see its own position against the
published SVT is a question about the world's observables. It must be decided blind to what it does
to this delta.

One new item joins it, and it is a *company* question rather than a world one, so it is not R13's:
the company's baseline churn belief is ~6× the world's realised rate at flat pricing. That is a
calibration finding about `company/crm/churn_model.py`, it is the company's own affair, and it is
allowed to be wrong — but it is the largest single belief error this project has measured, and it
biases every value-arm decision toward under-pricing.


## 2026-08-27 — what the full-window instruments COST, measured before either was run

Five stretches named the same two commands and none landed a full-window artefact. The direction
behind this section refused to restate the command a sixth time and asked a different question:
**what does it cost.** This is that measurement, taken *before* anything was run, together with the
verdict it supports. It is recorded here rather than in a finding because a reader arriving at this
file to re-run these instruments is exactly the reader who needs it.

### The two numbers, both read off disk rather than estimated

**One full-window sim pass.** `background/sim_runner.py` runs `tools.run_annual_report` with no
window truncation and logs `Run complete — {elapsed}s` to `docs/observability/sim-runner-log.md`.
That log carries **n = 3,540** completed full-window runs:

| | all 3,540 | most recent 30 |
|---|---|---|
| min | 245 s | 567 s |
| median | 470 s | **632 s** |
| max | 6,175 s | 781 s |

The recent-30 figures are the ones used below: the book has grown, and the all-time median is a
smaller company's number. **632 s is also an upper bound on what the instruments pay per pass** —
`run_annual_report` renders the annual report on top of `run_phase4c_on_phase2b`, and both
`run_value_cycle_ab` and `run_price_ladder` call `run_phase4c` alone. Erring high is the safe
direction for a fit question, so the over-estimate is kept rather than corrected.

**What a tick can hold.** `background/worker-tick.service` sets **`TimeoutStartSec=7200`** (120
min), and the unit is `Type=oneshot` that blocks on its `claude -p` child — so systemd SIGTERMs the
**whole cgroup**, tick and worker and any Agent fork together, at 120 minutes. That file's own
comment records what the bound cost when it was 30 min: 10 kills on 2026-08-03 and 2,566 lines
stranded in dying worktrees. `ExecStopPost=background.fork_salvage` now bounds the fork half of
that, but **a sim pass killed at 119 minutes leaves no artefact at all** — not a partial result, a
zero. The gate a landing must pass costs a further **397 s median** (`commit_hook_duration.jsonl`,
n = 38, recent runs 384-405 s, ceiling 840 s).

### 2026-08-27 11:05Z — the upper bound replaced by a direct measurement of the thing itself

The table above priced a pass off `run_annual_report`, which renders a report on top of the sim, and
said so: **632 s was an upper bound, not the instruments' actual cost.** It has now been measured
directly — one `run_phase4c_on_phase2b.main(report_end=None)` call, nothing else in the process,
`/usr/bin/time -v`, started 10:56:36Z on a machine simultaneously running a `process_run_complete`
publish and a pytest suite (so this is a *contended* number, not a quiet-machine best case):

| | measured |
|---|---|
| one full-window `run_phase4c` pass | **559.8 s** (9 min 20 s) |
| import cost, paid once per process | 3.0 s |
| wall clock incl. interpreter start | 9 min 24.7 s |
| peak resident set | **2.85 GB** |

**The upper bound was 13% high and the fit verdict survives, with more room than it claimed.** Every
row below is therefore conservative. Re-priced at 559.8 s/pass plus the 397 s median gate:

| | sim passes | measured cost, + one gate | share of the 120 min bound |
|---|---|---|---|
| `run_value_cycle_ab` (full window) | 2 | **25.3 min** | 0.21 |
| `run_price_ladder --rungs 0,0.5,1,2` | 5 | **53.3 min** | 0.44 |
| `run_price_ladder` (default 6 rungs) | 7 | **71.9 min** | 0.60 |
| AB then the 4-rung ladder, both landed | 7 | 78.6 min | 0.66 |

The last row now *fits* at the median where the estimate had it at 87 min — but it fits with 41
minutes of slack for orientation, staging and a tail, and the tail is the thing that killed it
before. One instrument per tick stays the recommendation; what changed is that the pair is no longer
arithmetically impossible, only imprudent.

The memory figure is the one that got worse on inspection: **2.85 GB for a single pass**, against a
WSL2 guest whose live total reads 24.0 GB and 94 lifetime OOM kills. A seven-pass ladder holds every
rung's decisions in memory at once, which is how the 02:14 tick reached 15 GB. That is a reason to
prefer the 4-rung ladder that is independent of the clock.

### What each instrument costs, at median and at the observed tail

Pass counts are read from the code, not assumed: `run_value_cycle_ab` runs two arms
(`tools/run_value_cycle_ab.py:1242,1251`); `run_price_ladder` runs **one flat-rules control plus one
pass per rung** (`run_price_ladder:681,690`), and `DEFAULT_RUNGS` is six.

| | sim passes | + one gate, median | + one gate, tail | share of the 120 min bound, at tail |
|---|---|---|---|---|
| `run_value_cycle_ab` (full window) | 2 | **27.7 min** | 40.0 min | 0.33 |
| `run_price_ladder --rungs 0,0.5,1,2` | 5 | **59.3 min** | 79.0 min | 0.66 |
| `run_price_ladder` (default 6 rungs) | 7 | **80.3 min** | 105.1 min | 0.88 |
| **AB then the 4-rung ladder, both landed** | 7 | **87.0 min** | **119.0 min** | **0.99** |
| **AB then the default ladder, both landed** | 9 | 108.0 min | **145.1 min** | **EXCEEDS** |

### Which case this was: IT FITS — for one instrument per tick, and not for two

The assumption behind five stretches was that a full-window run is too big for a tick. **It is not.**
A full-window A/B is a 28-minute job against a 120-minute bound, with 3x headroom; there was never a
mechanical reason it could not run, and this section exists partly to stop that excuse being
available. The 4-rung ladder fits too.

What does **not** fit is the *sequence* every one of those stretches asked for. AB and ladder and two
landings in one invocation is 87 minutes at the median and **119 minutes at the tail against a 120
minute hard kill** — and that arithmetic assumes the worker spends zero time reading its doorbell,
orienting, or dispositioning staging, which is never true (this invocation had spent ~15 minutes
before it started anything). With the *default* six-rung ladder the pair exceeds the bound outright.
So the failures were not a discipline problem and not a capability problem: **the ask was
over-subscribed, and the tail of it was unsurvivable.** That is the finding.

### R4 — the nearest working analogue, and the diff, both measured

The direction named the analogue: the 2019 ladder that ran to completion at 04:45 and produced 141 KB.
Its tick is in the journal — `worker-tick.service`, 04:14:26→04:50:49 BST, **36 min 23 s wall clock,
41 min CPU, 3.5 G memory peak** — and it did the orientation and the landing inside that too. Seven
passes at the 2016-2019 window in ≤36 minutes is ≈5 min/pass against the full window's 10.5, so
**the diff is the window and it is worth roughly 2x per pass.** Nothing else differs, which is why
"the full-window one is different in kind" was never true.

One number from the same journal is worth carrying forward: the 02:14 tick peaked at **15 G**. Against
a WSL2 guest whose live total reads 24.0 G with 19.3 G available (`background.resource_headroom.sample()`,
08:56:46Z) and a machine with 94 lifetime OOM kills, a seven-pass full-window ladder is not only the
longest job in this table, it is the one closest to the memory wall. It should not share a tick with
a publish.

### The cheapest thing that makes the pair runnable, recorded although the answer was "fits"

1. **Free, and it is the actual fix: one instrument per tick, landed.** Each is inside the bound with
   room. The direction's own "land after EACH, never batched" was already the right instinct; what was
   missing is that the *draw* has to be one instrument too, not two.
2. **Cheap, if a full six-rung ladder is ever wanted: `--resume`.** The ladder's rungs are already
   independent `run_phase4c` calls whose results are written per-rung, so skipping any rung already
   present in the output JSON turns a 7-pass job into three ticks of 2-3 passes. No part of the
   design changes — this is a caching flag, not a checkpointing scheme.
3. **Not needed: checkpointing the sim, or a longer-lived lane.** Both were on the table in the
   direction. Neither is warranted: the 7200 s bound is not the binding constraint, the sequencing is,
   and raising a timeout to fit an over-subscribed ask would hide the over-subscription rather than
   fix it.

---

## 2026-08-27 — the renewal schedule was repaired, and the belief-quality result did not survive it

`roll_lifecycle_event` was returning `None` for every renewal whose month fell beyond the settled
window — which is every renewal by construction, since the caller withholds the term it is
pricing. Whether a customer got a churn decision therefore depended on whether their anniversary
landed on the **31st of a month or the 1st**: a term ENDING 2016-12-31 has renewal month 2016-12,
still covered by the records, and rolled; a term STARTING 2017-04-01 has month 2017-04 while the
records stop at 2017-03, and did not. Six of the nine residential seed accounts were priced at 18
renewals across 2017-2019 and produced **not one lifecycle event**.

`build_churn_risk` now takes `through_period`, and the caller passes the month it is asking about.
No future data is read: the bill-shock window for a renewal is the twelve months BEFORE it, which
is entirely inside the records already supplied. Only the horizon check kept it out.

### The A/B, same book, same tool, before and after

| | broken schedule | repaired |
|---|---|---|
| control net | £79,688.17 | £111,269.70 |
| value net | £96,461.44 | £118,335.56 |
| **realised delta** | **+£16,773.28** | **+£7,065.86** |
| `scored_share_of_priced` | 57.1% | **100.0%** |
| `discrimination_auc` | 0.6944 | **0.4653** |
| `calibration_error` | +0.0107 | **−0.0774** |

**The advantage survives and more than halves. The belief-quality result does not survive at all.**

### The finding

`belief_vs_outcome`'s own `reading`, written long before this run, states the verdict:

> *"`discrimination_auc` at 0.5 means the belief carries NO information about who stays, and any
> advantage the arm shows is then a property of its calibration error rather than of inference —
> which is the thesis failing while the P&L improves."*

0.4653 is that case. And the buckets show it is not uniform noise — the middle of the arm's range
is **inverted**:

| believed | realised | n |
|---|---|---|
| 0.346 | 0.818 | 11 |
| 0.557 | 0.250 | 4 |
| 0.616 | **0.000** | 4 |
| 0.928 | 1.000 | 6 |

It is confidently wrong exactly where it is making decisions. `auc_population` is
`{retained: 16, left: 9}`, so the statistic is not degenerate, though 9 is small enough that the
caveat in `reading` applies.

### Why the earlier 0.694 was not a measurement of belief quality

It was computed over the 57% of renewals that could be matched — and that subset was not a sample.
It was **exactly the accounts whose anniversary happened to fall at a month end**, which is
uncorrelated with anything about the customer but perfectly correlated with which accounts the
world allowed to churn at all. The arm was being graded only on customers who could leave.

This is the same shape as the survivorship finding of 2026-08-26 (the CLV gap graded only on
accounts that died), one layer along, and it was invisible for the same reason: the denominator
moved without saying so. `scored_share_of_priced` is the field that made it visible, and it was
already there.

### What this does NOT say

It does not say the arm is worthless. It still beats flat rules by £7,066 on a book of 419. What
it says is that **the win is not yet attributable to inference** — a −0.077 calibration error with
no ranking power is an arm that prices systematically rather than selectively, and a systematic
price change is something flat rules could also make. Distinguishing the two is the next
measurement, not a conclusion available from this one.

Artefact: `docs/observability/value_cycle_ab_resi_renewal_fixed.json`. Prior:
`docs/observability/value_cycle_ab_resi.json`.

### What the £7,066 actually is — read straight off the same artefact

The A/B publishes four fields that together answer "was the advantage inference?" without needing
another run. None of them was added for this question; all four were already there.

| field | value | what it says |
|---|---|---|
| `discrimination_auc` | **0.4653** | the belief carries no information about who stays |
| `decision_shape.median_margin_gbp_per_mwh` | **44.50** vs 2.00 | the arm prices ~22× the flat rule |
| `decision_shape.distinct_margins` | 24 of 25 priced | it does VARY — nearly a unique margin each |
| `bound_attribution.share_of_priced_decided_by_a_bound` | **0.24** | a quarter were set by a bound, not the model |
| `margin_movers.concentration_top_n_share_of_absolute_movement` | **0.9928** | 15 of 211 accounts are 99.3% of the movement |

**The arm varies its price and the variation is uninformative.** 24 distinct margins across 25
decisions is not a flat rule in disguise — it really is choosing per customer. But AUC 0.4653 says
those choices carry no signal about who will stay, so the variation is noise around a level, not
selection.

**A quarter of the decisions were not the model's.** `bound_attribution`'s headline: *"6 of 25
priced renewals (24%) had their margin set by a bound rather than by anything about the customer
— 6 by the lawful price cap ... Those decisions sit on 1 billing account carrying 40% of the
realised margin movement between the arms."* One account, bound-decided, is 40% of the money.

**And 147 of 211 accounts did not move at all.** `margin_movers` reports 64 that moved and a top-15
concentration of 0.9928, with its own reading: *"near 1.0 means a handful of accounts ARE the
headline and it should be read as a case study, not a portfolio result."*

So the honest statement of the result is:

> Priced 22× higher on a handful of accounts whose staying-or-leaving the model could not predict,
> with a quarter of the decisions made by the price cap rather than by the model, and one
> bound-decided account carrying 40% of the difference.

That is not "value-based pricing beats flat rules". It is closer to "raising prices a long way
mostly worked on this book", which is a claim about the book's price elasticity and not about the
company's belief.

`bound_attribution.reading` states the discipline this has to be read under, and it was written
before this run: *"A positive delta under 'a bound' is not a refutation of value-based pricing —
it is a statement that this run did not test it."* `decided_by` here is `"mixed"`, which the same
field defines as "the headline must not be attributed to either without naming which half". Both
halves are named above.

### The measurement that would settle the remainder

A THIRD ARM: flat rules at the value arm's own realised median margin (£44.50), rather than at
`TARGET_MARGIN_GBP_PER_MWH = 2.00`. That holds the LEVEL constant and removes the SELECTION, so:

* if flat-at-£44.50 reproduces the £7,066, the arm is a price rise wearing a model;
* if it does not, the per-customer variation is worth something even at AUC 0.4653, and the next
  question is what it is picking up that the retention belief is not.

It is one run and a constant override. Not built in this session, and named here so it is not
re-derived: the arm's own `decision_shape.median_margin_gbp_per_mwh` is the number to set.

---

## 2026-08-27 (full window) — the ladder at 2016–2025: the world bites LESS than the company believes, and the 2019 reading said the opposite

`docs/observability/value_cycle_price_ladder.json`, `report_end: null`, generated 2026-08-27T11:56:29Z,
rungs `0, 0.5, 1.0, 2.0`. Cost, measured on the same run: **50 min 56 s wall clock, 3,051 s CPU,
10.1 GB peak RSS, exit 0, 122 KB artefact** — five `run_phase4c` passes against a 120-minute tick
bound, which is the fit the section above predicted at 53.3 min including the gate. The estimate was
2.4 minutes low.

**This supersedes nothing and replaces nothing.** `value_cycle_price_ladder_2019.json` and the
reading built on it are kept. What follows is the same instrument over the whole window, and on the
one statistic the 2019 reading rested on it points the other way.

### The null rung, first, because nothing below is readable without it

| | rung zero | flat-rules control |
|---|---|---|
| accounts churned | 37 | 37 |
| net margin, **settled** (R14) | £152,114.248823 | £152,114.248823 |
| accounts only in one roster | 0 | 0 |

Exact to the last penny, and the churn rosters are identical account-for-account. The artefact's own
verdict: *"rung zero reproduces the flat-rules control exactly, so the multiplier scales the uplift
and nothing else."* Rung zero is the null control the whole reading rests on, and it passes.

### The four rungs, and the world does respond to price

Over the common population — the 22 decisions priced **and** rolled by the world at **every** rung,
so the same accounts throughout:

| rung | mean uplift £/MWh | rate vs the company's own previous rate | realised non-renewals | **realised rate** | **believed rate** |
|---|---|---|---|---|---|
| 0.0 | £0.00 | +7.1% | 2 / 22 | **9.1%** | 21.4% |
| 0.5 | £22.38 | +14.1% | 4 / 22 | **18.2%** | 30.2% |
| 1.0 | £48.82 | +24.2% | 7 / 22 | **31.8%** | 42.7% |
| 2.0 | £103.15 | +48.2% | 8 / 22 | **36.4%** | 64.1% |

Monotone in both columns. Price bites; that is not in question and never was.

### The finding: the company over-predicts the bite by ~1.6×, and it does so on all three references

`realised_over_believed` is the ratio of the two response slopes over that same 22-decision set:

| x-axis | realised slope | believed slope | **realised / believed** | realised R² |
|---|---|---|---|---|
| delivered uplift (£/MWh) | 0.00262 | 0.00417 | **0.627** | 0.863 |
| vs the company's own previous rate (%) | 0.00630 | 0.01028 | **0.612** | 0.817 |
| vs the world's SVT reference (%) | 0.00398 | 0.00642 | **0.621** | 0.843 |

Three different x-axes, three answers inside 0.612–0.627. **The company's churn model thinks a price
rise costs it about 1.6 times as many customers as it actually does.** That is a *conservative* error
— it under-prices relative to what the book would bear — and it is the opposite sign of error to the
one a value arm would need to flatter itself.

The per-decision statistic agrees: **`median_world_over_believed` = 0.768** over 22 decisions and 88
observations, with the over/under split almost even (10 decisions where the company over-predicts the
response, 9 where it under-predicts). The pooled figure in the same block reads 1.705 and **must not
be quoted** — the artefact's own caveat says it is weighted by whichever account the arm happened to
price over the widest range, and *"where the two disagree, distrust this one."* They disagree here.

### Against the 2019 ladder — the window was doing more work than anyone had checked

| | 2019 window | **full window** |
|---|---|---|
| common population (effective n) | 6 | **22** |
| `median_world_over_believed` | **1.160** — world bites *harder* | **0.768** — world bites *softer* |
| unmatched decisions | 18, on 6 accounts | **0** |
| accounts the world never rolled at all | 6 | **0** |
| sign disagreements between the two references | 52 / 166 (31.3%) | 45 / 136 (33.1%) |

Two things follow, and only the second is a finding about the company:

1. **The 2019 unmatched set was a truncation artefact, and it is gone.** Those 6 accounts were not
   "never rolled" — their renewals rolled *after* 2019-12-31, and the artefact said as much in a
   comment at `run_price_ladder.py:635`. At full window every priced decision is rolled by the world:
   `unrolled: 0` at all four rungs. **The full window does not merely add data; it removes a known
   defect from the reading.** That, not the extra years, is the reason to prefer this artefact.
2. **The headline ratio flips, and the effective n went 6 → 22.** A statistic computed on 6 decisions
   flipping when computed on 22 is what a statistic on 6 decisions does. The honest statement is not
   "the 2019 result was wrong" but **"the 2019 result was never powered, and this is the first
   reading of it that is."** 22 is still small.

### What this does NOT say

* It does not say the arm's decisions are good. Direction of *response* is not quality of
  *discrimination* — the A/B's AUC of 0.4653 is the statistic for that, and it is unchanged here.
* It does not settle price-vs-prediction. **6 of 24 decisions at rung 2.0 were ceiling-clamped** and
  2 sat above the model's support, so the top rung is partly the cap's answer rather than the
  model's. `above_support_bound` is 0 at every rung at or below 1.0, so the lower three rungs are
  clean.
* It does not survive re-running on a different book. Every figure here is resi + SME, the book at
  `353fe96b8`; the segments are a free variable of the run and the ladder artefact does not yet carry
  a `book_identity` block the way the A/B now does. **That is the next defect in this file**, and it
  is the same one `WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26` raised
  against the sibling tool.

### The reference divergence, unchanged in shape and now in a bigger sample

136 decisions carry both references. They disagree in sign on **45 of them (33.1%)**, and in 30 of
those the company reads its own decision as a *rise* while the world reads the same rate as *below
SVT*. The SVT reconciliation control passes — largest absolute gap 0.005 percentage points against
the world's own logged `price_differential_vs_svt`, so the harness is scoring the rate the customer
was actually charged and the reference comparison is readable at all. The 2019 finding that the two
sides price against different references therefore holds at full window; only its magnitude moved.

### For the curriculum, recorded and not acted on (R13)

The book's realised elasticity is milder than the company's model of it. That is a fact about this
baseline world, arrived at blind to company P&L, and it is **not** a reason to retune either side.
Recorded here so the next reader does not rediscover it as a surprise.

---

## 2026-08-28 — The decision surface the A/B actually has

`decision_shape.priced` = 25. `level_arm_decision_shape.priced` = 34. A book of 210 billing
accounts settled in the window, 127 alive at its end, renewals annual. Nothing in the artefact
could say where the rest went, and that is the reason the headline cannot be resolved: **a
per-decision claim whose denominator cannot be counted is not a measurement.**

The absence was structural, not an oversight in the reading. `renewal_margin_uplift` returns a 0.0
uplift for every renewal it is not eligible to price, and the rate chain wrote *nothing at all* for
such a renewal — so "the world never offered this renewal", "a guard refused it" and "the arm
priced it flat" were one indistinguishable absent log line. R15's FAIL-SILENT pattern applied to a
population rather than to a verdict.

### What was built

`company/pricing/renewal_rate_chain.py` now appends one row per call of `decide_renewal_rate` to
`RenewalRateChain.arm_funnel_entries` — **unconditionally, above the priced/declined branch**, so a
renewal cannot reach the funnel by one path and miss it by another. `run_phase2b` collects them
into `value_arm_funnel_log`; `tools/run_value_cycle_ab.renewal_funnel` publishes them as the
artefact's `renewal_funnel` block, per arm, with the drop named at each stage, and
`decision_population` publishes the arms' denominators beside the advantage. The stage keys are the
arm adapter's own (`FUNNEL_STAGES`), read from it rather than restated — a counter carrying its own
copy of the eligibility rule is how a funnel comes to report a population its subject does not
have. A run predating the log reports `available: false`, never a denominator of 0.

The funnel is written for the **control arm too**. That is deliberate: `run_value_cycle_ab` asserts
`value_arm_log` is empty on the control, so the world's own renewal count cannot live there, and
without it a reader can never see how much of the book this writer can touch at all.

R15: sixteen tests in `tests/tools/test_the_renewal_funnel.py`, three mutations run and reverted —
dropping a stage from `FUNNEL_STAGES` reds two, making the append conditional reds four, and making
an unavailable funnel fail open to `priced: 0` reds two. The null rungs (an arm that priced
everything; the difference symmetric in which arm is larger) stay green through all three.

### (a) Is the decision surface small by construction, or by plumbing?

**By plumbing, and the mechanism is one unset field.** *Observed, with evidence:*

Measured on the control run `docs/reports/run_output_1fb8d894b_20260827T235333Z.json`
(`basis_risk_terms` is appended immediately after the chain call, so its length is exactly the
number of terms that reached `decide_renewal_rate`):

| stage | count |
| --- | --- |
| terms reaching `decide_renewal_rate` | 1,251 |
| — acquisition terms (`term_index` 0, both fuels) | 397 |
| — gas terms | 563 (187 acquisition + 376 renewals) |
| **electricity renewals (`term_index` ≥ 1)** | **478** |
| — on the nine seed accounts C1–C9 | 52 |
| — on drawn `SYN-`/`PROS-` accounts | **426** |

Those 426 are refused by one guard: `tariff_type not in UPLIFTABLE_TARIFF_TYPES`
(`{"fixed", "pass_through"}`). **They are not customers on evergreen or variable products.**
`simulation.population_draw.SyntheticCustomer` declares `tariff_type: Optional[str] = None` and
`_draw_one` never sets it, so all 213 drawn electricity accounts carry `"tariff_type": None`. The
nine hand-authored seed customers C1–C9 have no such key at all, so `c.get("tariff_type", "fixed")`
returns `"fixed"` for them and `None` for everyone else. Directly checked at the adapter:
`decide_renewal_rate(tariff_type=None, …)` under `VALUE_ARM_POLICY` returns stage
`product_not_upliftable`; the same call with `"fixed"` passes that guard.

The world nevertheless settles those 426 terms as ordinary annual fixed contracts —
`build_renewal_schedule` treats `None` as neither `flex` nor `deemed`, strikes a locked unit rate
and carries it into `prev_fixed_unit_rate`. So the term has every property of a fixed product
except the label, and the company's eligibility rule — correctly, on its own terms — refuses to
price a renewal whose product it cannot name.

Corroborated in the published artefact rather than only in the code: `belief_vs_outcome.
matched_sample` in `value_cycle_ab_s1_three_arm.json` names C1, C2, C3, C4, C5, C6, C7, C8, C9 and
nothing else, and every account in `churn_roster_diff.only_in_value_arm` is a seat customer
(C1_2, C2, C7, C8). **The experiment that grades per-customer pricing runs on nine accounts.**

*Inferred, and flagged rather than asserted:* the same unset field also decides whether the
supplier's own cap clamp fires. `renewal_rate_chain` reads `cap_ceiling` only when
`is_domestic and tariff_type in CAPPED_TARIFF_TYPES` (`("fixed",)`), and the world's independent
enforcement (`simulation/price_cap_enforcement` via `hedged_settlement`) is applied inside
`run_deemed_term` only. On that reading no Ofgem ceiling reaches a fixed-shaped term labelled
`None`, which would put 213 of 222 domestic electricity accounts outside the price cap in this
world. **This has not been measured against the struck rates** — whether any of those 426 renewals
actually struck above the cap is unknown, and that measurement is owed. It is a larger question
than the A/B's denominator and does not belong in this file's conclusion.

**What is NOT being done about it, and why.** Giving the drawn population a `tariff_type` is a
change to the BASELINE WORLD, and R13 governs it: the baseline may only change for
fidelity-to-reality reasons decided blind to company P&L. A real supplier's book carries a product
per account, so drawing one is defensible on fidelity grounds — but it would move every published
figure in this project, it would change which accounts the price cap binds, and **it must not be
taken because it makes n bigger.** Doing it as a way to rescue this experiment is R13 straight
through the wall. It is recorded here as owed, to be decided on its own evidence, in its own pass.

### (b) Why two arms differing only in `renewal_margin_arm` see different numbers of renewals

**Sequential-A/B roster divergence, and it is legitimate.** *Observed:* the arms are identical in
eligibility — `renewal_margin_uplift` deliberately does not return early for `FLAT_AT_LEVEL`, so it
passes every guard the value arm passes, and neither arm can see a renewal the other cannot. They
differ in which renewals still exist. A different price changes who churns; `run_phase2b` skips
every remaining term of a churned billing account with a `continue` *above* the chain call; so an
account that leaves in year two removes all of its later renewals from that arm's denominator.

The eligible pool is small enough and concentrated enough for that to be worth nine decisions. On
the control roster the 52 eligible renewals sit in six accounts — C2 (9), C7 (9), C8 (9), C9 (8),
C1 (6), C5 (6), with C3, C4 and C6 contributing 5 between them. `churn_roster_diff.only_in_value_arm`
names C1_2, C2, C7 and C8: the value arm loses three of the four largest contributors to the pool,
earlier than the control does. (The control's 52 is a bound on the pool and a statement of its
concentration, not the value arm's own count — the rosters differ, which is the point.)

This is not a defect to fix. Equalising the denominators would mean pricing renewals for customers
who had already left. The difference *is* the measurement. What was wrong is that it was unstated:
`arm_identity` guards the POLICY fields and nothing guarded the decision POPULATION, so a reader
could take a per-decision figure from one arm and compare it with one from another and be dividing
two different books. `decision_population` now publishes both denominators, their difference, the
mechanism, and the instruction not to do that.

### What this settles about the headline

The five decisions carrying 87% of the money and the six priced by the price cap are five and six
of **twenty-five decisions on nine accounts**. No amount of re-running changes that, because the
population is not a sampling choice — it is 4.2% of the terms the world offers, fixed by a field
the draw never sets. The honest conclusion stands: **change the experiment, do not repeat it.**
R12 throughout — the funnel is a diagnostic, and no stage count is a thing to improve.
