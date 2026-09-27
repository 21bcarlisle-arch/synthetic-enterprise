**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `measurements_that_mirror`

# Renewal count explains none of the selection residual, and 99.8% of its variance is one discrete £5,388 event in the level arm

**2026-09-27.** Answer to the director's ask of 2026-09-26 09:29, graded against
`SEAT_PREREG_HOW_MUCH_OF_THE_SELECTION_RESIDUAL_RENEWAL_COUNT_EXPLAINS_AND_WHETHER_DEPTH_WOULD_FIX_IT_2026-09-27.md`,
written before any number below was computed. No new run: this is the 18 seeds already on disk at
`/var/tmp/se-floor18-head-20260925/shards/folded18_head_20260925.json`, commit `ba9bc6733`, world
`39a192ce04c1eda8`, clock `settled-realised`. Reproduce with

    python3 -m tools.selection_residual_decomposition \
        /var/tmp/se-floor18-head-20260925/shards/folded18_head_20260925.json

## The answer, in two sentences

**Renewal count explains none of the residual variance — not a small amount, none.** The best of the
eleven pre-registered regressors reaches R² **0.0284** (90% interval **0.0000–0.2845**), and the
permutation null over the whole family has a MEDIAN best-of-eleven R² of **0.0971**: the observed
best sits *below* what chance produces, p = **0.8245**. Two of the depth regressors are literally
constant across all 18 seeds and cannot explain anything at any sample size.

**What the variance actually is: 99.84% of it is the level arm's own net, and it is not a spread but
a switch.** The value arm's net has a seed-to-seed sd of **£129.27**; the level arm's is **£2,309.76**
— **17.9×** larger — and `var(selection) = var(value) + var(level) − 2cov` reconciles exactly, with
the value arm contributing **0.31%**, the level arm **99.84%** and the covariance **−0.15%**.

## The residual is a two-state switch, and that changes which bound is the honest one

Sorted, the 18 residuals fall into two tight clusters with nothing between them:

| state | seeds | mean | span | level-arm net |
|---|---|---|---|---|
| low | **4** (11111, 44444, 99999, 111111) | **−£4,020.79** | £514.60 | £184,017 – £184,541 |
| high | **14** | **+£1,366.86** | £514.60 | £178,666 – £179,190 |

The gap between them is **£4,836.46** against a widest-cluster span of **£514.60** — a separation of
**9.4×**. State distance **£5,387.65**. This is one discrete event worth about £5,400 firing in
**4 of 18** elasticity draws inside the level arm, not many small shocks aggregating.

**So `selection_sem_gbp = £544.86` prices the wrong unknown.** `sd/√n` is the bound for one quantity
wobbling. Here the sd is a state distance times a mixing rate, and the thing actually unknown is the
**rate**. At 4/18 the exact 90% interval on that rate is **0.080–0.439**, which carried through gives
a family mean of **−£997.69 to +£937.49**.

**Both signs are inside it, and so is the published figure.** The −£959.78 served from the
2026-09-10 runs sits inside this interval. **The two runs never disagreed.** "The sign did not
reproduce" is exactly what an unpinned 22%-ish switch looks like sampled twice, and the 2026-09-26
finding's "same priced decisions, different residuals" is the same fact: between-fingerprint
variance is only **4.01%**, and one fingerprint group spans **£5,570** within itself.

## Nothing the shard records tells the two states apart

Of **14** recorded fields tested for *disjoint* ranges between the four low-state seeds and the
fourteen high-state ones — every pre-registered regressor plus `level_gbp_per_mwh`, `control_net_gbp`
and `value_arm_net_gbp` — **zero** separate them. (`level_arm_net_gbp` and `level_advantage_gbp` are
excluded by construction and named as such in the tool: they are the response's own second term, so
separating on them is the identity dressed as a cause.)

The switch is driven by something this artefact does not carry.

## The book IS as shallow as the director thought — and that is not why the residual moves

The depth census confirms the picture and refutes it as the cause. 68.2 of 164 settled accounts are
scored per seed, and of those:

| D2 depth (priced renewals an account faces) | share |
|---|---|
| exactly 1 | **50.2%** |
| 2 or fewer | **82.4%** |
| 5 or more | **1.5%** (max 6) |

D3 — renewals actually *survived* — is shallower still: **36.6%** of scored accounts never retain at
all, **63.4%** manage one or fewer, **11.7%** reach three or more. Median longest streak **1**.

Half the book gets one renewal. A pricing choice has essentially nothing to compound through. **But
that shallowness is a near-constant of the term calendar, which the elasticity re-draw does not
move — which is precisely why it cannot explain seed-to-seed variance.** `accounts_with_5_or_more_
decisions` and `accounts_with_streak_3_or_more` are identical on all 18 seeds. The hypothesis was
right about the book and wrong about the residual, and the two are separate claims.

## Would a deeper book let selection be measured at all?

**At the point estimate, yes — and it is the expensive lever.** Seeds needed scale as
`(t·sd/|mean|)²`; under a k-fold book with the same mix the mean scales with k and the sd with √k
*if per-account contributions are independent*, so seeds needed fall as 1/k:

| book | settled accounts | seeds needed (point estimate) |
|---|---|---|
| ×1 | 164 | **826.9** |
| ×2 | 328 | 413.5 |
| ×5 | 820 | 165.4 |
| ×10 | 1,640 | 82.7 |
| ×50 | 8,200 | 16.5 |
| ×100 | 16,400 | 8.3 |

The invariant is **135,617 seed-account draws** — seeds and accounts are the same purchase at
different unit prices. *(827 is the fixed-t reading at t = 2.1098, the shard's own `seeds_at_the_
point_estimate: 717` is the same arithmetic with t re-derived at each candidate n; the ratio is what
the ladder uses.)*

**Three things bound that answer, and the first two are new:**

1. **The independence premise is now doubtful, and it is what the 1/k rate rests on.** A two-state
   switch worth £5,388 firing in 22% of draws is the signature of ONE event, not of many
   independent per-account shocks. If the event is one account's behaviour, adding small households
   does not dilute it at the √k rate. This is the premise the shard cannot test, for want of
   per-account money.
2. **A far cheaper lever exists.** Were the level arm's net as stable across draws as the value
   arm's is, sd(selection) would be **£181.58** and the sign would cost **5.1 seeds** — **162×
   cheaper than any book growth**. That is arithmetic on measured inputs, and it does **not**
   establish that the level arm's variance is removable: a flat uplift may genuinely produce
   variable outcomes, and rigging the comparator to be quiet would be worse than the present state.
   What it establishes is where to look first.
3. **No depth removes the upper tail.** `distance_to_a_sign.seeds_needed_interval` has a denominator
   spanning −£375 to +£714. The required sample has no upper bound at any book size; depth makes a
   sign **cheaper** to state, never **certain** to be stateable.

## The paired design is not pairing

`corr(value_arm_net, level_arm_net) = +0.0135`. The two arms meet the same seed, the same world and
the same priced renewals, and their outcomes are **independent anyway**: the pairing removes
**0.15%** of the arms' combined variance. A paired A/B exists to make the difference cheap, and this
one is as noisy as the sum. That is not a consequence of book depth either, and it is the second
thing the next run should be built to see.

Both arms' nets are also **discrete**: the value arm takes 4 distinct values across 18 seeds, the
level arm 8. Every Gaussian bound published on this instrument is a normal approximation to a
handful of lumps.

## Predictions, graded — two refuted, and the result was not predicted at all

| # | Prediction | Outcome |
|---|---|---|
| P1 | R²(decisions per seed) < 0.05 | **✓** 0.0284 |
| P2 | median depth ≤ 3; share ≥5 renewals < 20% | **✓** median 1.0; 1.5% |
| P3 | best D3 R² in [0.05, 0.40) | **✗ REFUTED** — 0.0198, below the predicted floor. I expected "real but a minority"; it is not real at all |
| P4 | that interval does not exclude zero | **✓** every interval straddles zero |
| P5 | permutation p > 0.05 | **✓** 0.8245, and stronger than predicted: *below* the null median |
| P6 | a C-account indicator wins, R² > 0.25 | **✗ REFUTED** — best 0.0083; 11 of the 12 C-account regressors are constant on all 18 seeds. Concentration in the declared book is not the cause either |
| P7 | between-fingerprint variance share < 0.30 | **✓** 0.0401 |
| P8 | the artefact cannot answer the depth question | **✓ on the regression, ✗ on the question.** Depth genuinely has no variance to regress against. But the artefact DID answer it, by a route I did not anticipate |

**Nothing in the pre-registration anticipated the level arm carrying 99.8% of the variance, or the
residual being bimodal.** I pre-registered eleven renewal statistics and a concentration arm, all
thirteen of which came back empty, and the answer was in three fields I had not planned to look at:
`value_arm_net_gbp`, `level_arm_net_gbp` and the sort order of `selection_gbp`. The pre-registration
earned its keep by making that visible rather than by being right.

## What must be recorded per run, and it needs no new simulation

Named in `tools/selection_residual_decomposition.py --what-is-missing`:

1. **`selection_by_account_gbp`** — per `customer_id`, `value_arm_net − level_arm_net` on the
   settled-realised clock. **Both sides already exist in every run**: `simulation/run_phase1e.py`
   sums `net_margin_gbp` per `customer_id` off `phase2b.all_records` (~line 436) and the per-account
   split is thrown away when `_arm_measure` folds it to `total_net_gbp`. A field carried, not a
   model changed. **This alone identifies the £5,388 event** — diff one low-state seed against one
   high-state seed, which is a one-variable test needing two runs, not 700.
2. **`renewals_priced_by_account`** — the D2 depth vector, so depth becomes a regressor instead of a
   constant.
3. **`consumption_mwh_by_account`** — without it a concentration reading cannot tell a large account
   from an unlucky small one, and those imply opposite remedies.

With (1) the Herfindahl of per-account selection contribution is computable, and that single number
settles the director's question properly: near 1/N and the 1/k ladder above holds; concentrated and
depth buys nothing.

## What I am doing next, unless the director says otherwise

Carrying the three fields above into the arm runner, then the two-seed diff that names the £5,388
event. No published figure changes and none is withdrawn: the director's 2026-09-26 ruling stands,
and this result strengthens the reason to keep it — the served −£960 and today's +£170 are two draws
from the same unpinned switch, which is the observability working rather than a contradiction.
