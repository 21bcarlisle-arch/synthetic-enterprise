# Can the company actually learn `price_sensitivity`?

**Answer: no. Not weakly, not noisily — the declared discovery channel carries exactly
zero information about the drawn trait, by construction. And the instrument that exists to
detect that cannot see it.**

Status: design record, delivery-lane claim `can-the-company-actually-learn-price-sensitivity`.
Written at HEAD `3524ab13c`, with the code open. Nothing here edits
`docs/design/segmentation_curriculum_v1.json` — the marginals and the declared shares are the
director's under R13. What follows records the **contract gap** between what that file declares
and what the build implements.

---

## 0. The contract, as declared

`segmentation_curriculum_v1.json`:

```json
"price_sensitivity_marginals": {
  "value": {"high": 0.3, "medium": 0.45, "low": 0.25},
  "hidden_truth_only": false,
  "note": "discoverable via rate-change churn response (get_churn_estimate)."
}
```

Two claims: the trait is **not** hidden-truth-only, and the channel that makes it discoverable
is `get_churn_estimate`. The first claim depends entirely on the second. The second is false.

---

## 1. The channel cannot carry the signal — proven from the code, not from statistics

The company's inference is `company/analytics/cohort_discovery.py:177`:

```python
def _infer_price_sensitivity(churn_estimate: Optional[float]) -> Optional[str]:
    if churn_estimate is None:      return None
    if churn_estimate >= 0.45:      return "high"
    if churn_estimate <= 0.15:      return "low"
    return "medium"
```

It bands one number. Follow that number:

`SimInterface.get_churn_estimate` → `company/crm/enriched_churn_estimate.py:54
enriched_churn_estimate(...)`, whose complete parameter list is:

> `old_rate_gbp_per_mwh`, `new_rate_gbp_per_mwh`, `tenure_years`, `annual_consumption_kwh`,
> `bill_shock_count`, `behaviour_score`, `satisfaction_score`, `fuel`, `hedge_fraction`,
> `hangover_periods_remaining`, `segment`, `renewal_year`

**The drawn `price_sensitivity` is not among them, and nothing that is among them is a function
of it.** The trait reaches the live world at exactly one site — `simulation/customer_events.py:269`,
the call added by S1:

```python
sensitivity = price_sensitivity_for_customer(billing_account, run_base_seed())
felt = perceived_price_differential(differential, sensitivity)
p_churn_price = (1.0 - effective_p_retain) * churn_position_multiplier(felt)
effective_p_retain = 1.0 - min(p_churn_price, WORLD_MAX_CHURN_PROBABILITY)
```

That modifies `effective_p_retain` — the probability governing the **retain roll**. It is an
**outcome**, and it is downstream of every input the company hands its own estimator. So:

> Two households with identical company observables (same rate move, tenure, consumption, bill
> shocks, behaviour score, satisfaction score, renewal year) and **opposite** drawn
> `price_sensitivity` receive the **identical** churn estimate, and therefore the identical
> believed `price_sensitivity`.

Measured at HEAD: `enriched_churn_estimate(180 → 210 £/MWh, tenure 3.0, 3100 kWh,
bill_shock_count=1, renewal_year=2019) = 0.2775` — one number, for every household of every
sensitivity. The mutual information between the declared channel and the trait is **0**, not
small.

The doorbell's hypothesis — *"the channel reads the company's own belief and therefore cannot"* —
is right, and this is the precise reason. Being a model output is not by itself disqualifying: a
model output could carry the trait if the trait moved the model's inputs. It does not. The
estimator is `build_churn_risk`-shaped, and the 478-renewal grade that reads it as bill-shock
count re-labelled is describing the same fact from the other end.

---

## 2. The pre-S1 baseline, recorded — and why it is not the number the doorbell expected

Recorded into `docs/observability/coupled_gap_ledger.json` at HEAD (`W2_2_population_draw`,
twin `C_cohort_discovery`, `measured_at 2026-08-27T15:36:59Z`, `run_git_commit 3524ab13c`):

| axis | true-tenure cell | n | gap |
|---|---|---|---|
| **price_sensitivity** | social_rent | 434 | **1.0345** ← headline worst cell |
| **price_sensitivity** | own_mortgage | 905 | 0.8701 |
| **price_sensitivity** | private_rent | 565 | 0.7766 |
| **price_sensitivity** | own_outright | 1096 | 0.7069 |
| channel_pref | social_rent … own_outright | — | 0.2621 … 0.1163 |
| accommodation / cars / nssec | all cells | — | 1.0000 (no mechanism, by construction) |

`worst_cell_gap = 1.0344827586206897`, `worst3_mean_gap = 1.011494`.

**Two corrections to the framing of the ask.**

1. **S1 has already landed** — `bca9bb3af`, two commits before this measurement. The baseline was
   not taken before S1.
2. **It did not need to be.** `tools/couple_cohort.py` is deterministic in `base_seed=20260721`
   and reads no live world state, so S1 cannot move it. The HEAD run reproduces the row recorded
   on 2026-08-10 at commit `e6402d53` **bit-for-bit** (same gap to 16 digits, same
   `worst3_mean_gap`, same worst cell, same cell counts). There is no pre-S1/post-S1 distinction
   for this instrument, and therefore no urgency in the run. The urgency premise in the draw is
   false.

Why it is S1-invariant is the subject of §3, and it is the more important finding.

---

## 3. The instrument grades a channel that does not exist

`tools/couple_cohort.py` never calls `get_churn_estimate`. It **fabricates** the observable
directly from the hidden truth (`tools/couple_cohort.py:138-158`):

```python
_CHURN_ESTIMATE_BASE = {"high": 0.65, "medium": 0.35, "low": 0.10}
_CHURN_ESTIMATE_NOISE_SD = 0.15

def _true_price_sensitivity_to_churn_estimate(true_ps, rng):
    return clamp(_CHURN_ESTIMATE_BASE[true_ps] + rng.gauss(0.0, 0.15))
```

That is a channel with **large** mutual information with the trait — the observable is a noisy
readout of the answer. The live channel has none. So the harness grades the company's *banding
thresholds* against a hypothetical channel, and is structurally silent about the channel the
company actually has. Its own docstring's R15 independence argument is sound as far as it goes
(three separately-authored pieces, none fitted to the others) — but independence is not the
issue. **The subject is wrong.** The one component whose behaviour decides the answer — the
source of the number being banded — is substituted out by the harness before the measurement
starts.

This is why the row is S1-invariant, and why it would read the same if the live estimator were
deleted outright.

---

## 4. The headline gap is not monotone in channel skill

Six variants of the harness physics, everything else untouched (truth draw, company banding, gap
metric, `n_min`), at two seeds. "acc" is per-household identification accuracy — did the belief
name this household's actual trait.

```
########## base_seed=20260721  (the seed the ledger uses)
  rung 0  truth-readout (HEAD)                acc=0.7070   headline=1.034483  worst3=1.011494
  null A  resampled trait (ZERO information)  acc=0.3397   headline=1.034483  worst3=1.011494
  null B  constant 0.35 (everyone -> medium)  acc=0.4487   headline=5.005479  worst3=4.909242
  null C  constant 0.90 (everyone -> high)    acc=0.2963   headline=6.413793  worst3=6.257992
  null D  pure noise, no trait                acc=0.3380   headline=2.299492  worst3=2.156200
  anti-E  INVERTED trait (high<->low)         acc=0.2827   headline=1.000000  worst3=1.000000

########## base_seed=19990101
  rung 0  truth-readout (HEAD)                acc=0.7240   headline=1.000000  worst3=1.000000
  null A  resampled trait (ZERO information)  acc=0.3540   headline=1.116788  worst3=1.038929
  null B  constant 0.35 (everyone -> medium)  acc=0.4513   headline=7.248175  worst3=5.475257
  null C  constant 0.90 (everyone -> high)    acc=0.2943   headline=8.562044  worst3=6.798727
  null D  pure noise, no trait                acc=0.3337   headline=3.065693  worst3=2.362115
  anti-E  INVERTED trait (high<->low)         acc=0.2957   headline=1.000000  worst3=1.000000
```

Reproduce: monkeypatch `tools.couple_cohort._true_price_sensitivity_to_churn_estimate`, then
`build_scenario(3000, seed)` → `score_worst_cell(truths, beliefs, n_min=N_MIN)`. No production
code is touched.

Three readings, in order of severity:

1. **At the seed the ledger actually uses, a channel with zero information is bit-identical to
   the real one.** Null A destroys every trait-to-observable link — accuracy falls 0.7070 →
   0.3397, i.e. to chance for a 3-level axis — and the published headline does not move at all.
   The live channel is null A. That is the empirical form of §1.
2. **A maximally *wrong* channel scores the *best* headline.** anti-E inverts high↔low, giving
   the worst accuracy of the six (0.2827 / 0.2957), and prints `1.000000` at **both** seeds — a
   better headline than the correct channel manages at seed 20260721. It wins by dropping out of
   the max: the worst cell becomes `accommodation::own_outright`, one of the three axes pinned at
   exactly 1.0 because they have no discovery mechanism at all. The headline is a **max over a
   mixed population of axes with a 1.0 floor**, so any price_sensitivity channel that is merely
   bad in a distribution-matching sense is masked by that floor. At seed 19990101 the correct
   channel and the inverted channel are indistinguishable — both 1.000000.
3. **The metric scores distribution match per cell, never per-household identification.** A
   channel that assigns the right *mix* of high/medium/low within a tenure cell scores well even
   when every individual assignment is wrong — which is exactly how inverting a near-symmetric
   marginal preserves the shape while destroying every answer. Pricing needs the household, not
   the cell. B (acc 0.4487) scoring far worse than D (acc 0.3380) at seed 20260721 is the same
   non-monotonicity from the other direction.

A single reading of `worst_cell_gap` therefore cannot support the sentence "the company has
partial skill at price_sensitivity", which is what the ledger's own `note` currently invites. The
note is accurate about `accommodation/cars/nssec`; its clause "price_sensitivity/channel_pref
have a noisy discovery mechanism and show partial learning" is true of `channel_pref` (whose
observable, actual contact channels used, is a real behaviour) and false of `price_sensitivity`.

---

## 5. Why this matters to the thesis, and the direction of the error

The thesis is that the advantage comes from **inference**, never from **access**. S1 raised the
world's ceiling: for the first time a household's own drawn sensitivity moves its leave
probability, so there is a real type to infer and a real advantage available. The company cannot
reach any of it through the declared channel. So S1 raises the ceiling and the gap in the same
instant, and the company will read as *getting worse* while nothing about it changed.

Worse for the record: the instrument will not show that either, because §3 and §4 mean the
published number moves for reasons unrelated to the channel's skill. **S1 created the signal; the
declared channel cannot read it; the instrument cannot see that it cannot.**

The error direction is safe — it understates the company, never flatters it — which is why this
is recorded rather than corrected in place (R12: the gap is a diagnostic, never a target).

---

## 6. The observable that could carry it — the owed work

A real supplier does not infer price sensitivity from its own churn model. It observes **each
household's realised accept-or-leave outcome after its own rate change**: *we moved your unit
rate by X% at renewal, and you stayed / you left.* That is a behaviour, not a model output, and
it is the only thing on the company's side of the wall whose distribution genuinely differs
between a high- and a low-sensitivity household once S1 is live.

**The company already records it.** `SimInterface.notify_churn(account_id, event_date, reason=...,
sim_churn_probability=..., company_churn_estimate=...)` and
`notify_retention_attempt(account_id, event_date, company_churn_estimate, discount_pct, outcome=...)`
are live on both `StubSimInterface` and `LiveSimInterface`, and both are readable back
(`churn_notifications`, `retention_notifications`). Paired with the rate move the company itself
chose, that is a per-household `(own_rate_move_pct, stayed|left)` observation — everything the
inference needs. Nothing new has to cross the wall; `cohort_discovery` simply does not read it.

Owed work, filed as `docs/staging/in_progress/WORKER_MINTED_price_sensitivity_observable_channel_2026-08-27.md`:

1. **Re-source the channel.** `InteractionObservation` carries the household's own realised
   rate-change outcomes; `_infer_price_sensitivity` reads those instead of banding
   `get_churn_estimate`. One renewal is a coin flip, so the inference must pool — across a
   household's repeated renewals, and across households at comparable own-rate moves, reading the
   residual against the book's base rate.
2. **Re-subject the instrument.** `tools/couple_cohort.py`'s physics must stop fabricating the
   observable from the hidden truth and instead route the live chain, so the measurement has the
   deployed channel as its subject. Until it does, its `price_sensitivity` leg is not evidence
   about the company either way.
3. **Give the metric a null rung and a monotonicity check** (R15, and the "controls must be able
   to fail" class). The battery in §4 is the shape: a zero-information rung that must score
   materially worse than the real channel, and an inverted rung that must not out-score it. Both
   currently fail. Score the `price_sensitivity` leg on its own rather than reading it out of a
   max whose floor is set by three axes with no mechanism, and report per-household identification
   alongside the distribution-level TV so a channel cannot pass on cell-shape alone.
4. **Then, and only then,** revisit the curriculum's `hidden_truth_only: false`. That flag is the
   director's under R13 and is not touched here. What this document establishes is that it is
   presently **unearned**: the declared channel does not make the trait discoverable, so as built
   the axis behaves as hidden-truth-only, alongside `accommodation`/`cars`/`nssec`. The contract
   gap is recorded here for the director's decision, not resolved by the agent.

---

## 7. What was measured, and what was not

| claim | basis |
|---|---|
| the declared channel carries zero trait information | **observed** — parameter list of `enriched_churn_estimate`; single live trait call site at `customer_events.py:269` writes an outcome, not an input |
| ledger row reproduces 2026-08-10 bit-for-bit at HEAD | **observed** — `python3 -m tools.couple_cohort` at `3524ab13c` |
| the row is S1-invariant | **observed** — instrument is deterministic in `base_seed`, calls no live world code |
| headline is non-monotone in channel skill | **observed** — six-variant battery, two seeds, §4 |
| pooled realised outcomes *would* carry the signal | **inferred** — follows from S1 making leave probability trait-dependent; not yet measured. Item 1 of §6 is what would measure it |
| the right pooling window / estimator for item 1 | **not determined** — one renewal per household per year is thin; whether the residual is readable at book scale is an open question the owed work must answer, not assume |
