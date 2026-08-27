<!-- SUPERVISOR_DRAW: self-drawable -->

# [WORKER-MINTED] The `price_sensitivity` discovery channel reads a model output, not a behaviour (2026-08-27)

**Type:** owed work filed out of the delivery-lane claim
`can-the-company-actually-learn-price-sensitivity`. Design record and full evidence:
`docs/design/CAN_THE_COMPANY_LEARN_PRICE_SENSITIVITY.md` (HEAD `3524ab13c`).
**Self-drawable.** No wall is crossed by any item below; item 4 is explicitly *not* drawable and
stays the director's.

## The finding, in one line

`segmentation_curriculum_v1.json` declares `price_sensitivity` `hidden_truth_only: false`,
"discoverable via rate-change churn response (`get_churn_estimate`)". The drawn trait is not a
parameter of `enriched_churn_estimate` and does not move any of its parameters, so the declared
channel carries **exactly zero** information about it. As built, the axis behaves as
hidden-truth-only.

**Observed, not inferred:**
- `company/analytics/cohort_discovery.py:177` bands `get_churn_estimate` at 0.45 / 0.15.
- `get_churn_estimate` → `company/crm/enriched_churn_estimate.py:54`, whose parameters are rate
  move, tenure, consumption, bill shocks, behaviour score, satisfaction, fuel, hedge fraction,
  hangover periods, segment, renewal year. The trait is absent from all of them.
- The trait's only live call site is `simulation/customer_events.py:269` (added by S1,
  `bca9bb3af`), where it modifies `effective_p_retain` — an **outcome**, downstream of every
  input the company hands its estimator.
- Consequence: two households identical in company observables and opposite in trait get the
  identical estimate and therefore the identical belief.

## Why it was not caught

`tools/couple_cohort.py` — the instrument that grades this leg — never calls
`get_churn_estimate`. It fabricates the observable from the hidden truth
(`_CHURN_ESTIMATE_BASE = {"high": 0.65, "medium": 0.35, "low": 0.10}` + N(0, 0.15)), i.e. a
channel with large mutual information with the answer. It grades the company's *banding
thresholds* against a channel that does not exist. Six-variant null battery (design doc §4,
two seeds): a **zero-information** channel scores **bit-identical** to the real one at the seed
the ledger uses (headline 1.034483 both), and an **inverted** channel — worst per-household
accuracy of the six — scores the **best** headline (1.000000 at both seeds) by dropping below the
1.0 floor set by the three axes that have no discovery mechanism at all.

R15 classes in play: **mixed subject** (headline is a max over axes, three pinned at 1.0), and a
control whose subject is not the deployed mechanism.

## Work items

1. **Re-source the channel.** Carry the household's own realised rate-change outcomes on
   `InteractionObservation`; `_infer_price_sensitivity` reads those instead of banding
   `get_churn_estimate`. The observable already exists company-side and crosses no new wall:
   `notify_churn(...)` / `notify_retention_attempt(..., outcome=...)` are live on both
   `StubSimInterface` and `LiveSimInterface` and read back via `churn_notifications` /
   `retention_notifications`. Paired with the rate move the company itself chose, that is a
   per-household `(own_rate_move_pct, stayed|left)` record. One renewal is a coin flip, so the
   inference must pool — over a household's repeated renewals, and across households at
   comparable own-rate moves, reading the residual against the book's base rate.
   **Open question, do not assume:** whether that residual is readable at book scale with ~1
   renewal/household/year. Measure it before building on it; a negative answer is a complete
   answer and should be recorded as one.
2. **Re-subject the instrument.** `tools/couple_cohort.py`'s physics must route the live chain
   rather than fabricating the observable from the truth, so the deployed channel is the subject.
   Until it does, the `price_sensitivity` leg of `W2_2_population_draw` is not evidence about the
   company in either direction, and should not be cited as if it were.
3. **Give the metric a null rung and a monotonicity check (R15).** The design doc §4 battery is
   the shape and is reproducible without touching production code. Required: a zero-information
   rung that must score materially worse than the real channel, and an inverted rung that must
   not out-score it — **both currently fail**. Score the `price_sensitivity` leg on its own rather
   than reading it out of a max floored by three mechanism-less axes, and report per-household
   identification accuracy alongside the distribution-level TV, so a channel cannot pass on
   cell-shape alone.
4. **NOT DRAWABLE — director's, under R13.** The curriculum's `hidden_truth_only: false` for this
   axis is presently unearned. `segmentation_curriculum_v1.json` is not to be edited by the agent;
   the contract gap is recorded in the design doc for the director's decision. Item 4 unblocks
   only on his word, and items 1–3 do not depend on it.

## Why it matters

S1 raised the world's ceiling — a household's own sensitivity now moves its leave probability, so
there is a real type to infer. The company cannot reach any of it through the declared channel,
so the gap widens at the same instant the ceiling rises and the company reads as getting worse
while nothing about it changed. The thesis is that the advantage comes from inference and never
from access; a trait the company structurally cannot learn is neither. The error direction is
safe (it understates the company, never flatters it), which is why this is filed rather than
patched on sight — R12, and self-interrupt discipline.
