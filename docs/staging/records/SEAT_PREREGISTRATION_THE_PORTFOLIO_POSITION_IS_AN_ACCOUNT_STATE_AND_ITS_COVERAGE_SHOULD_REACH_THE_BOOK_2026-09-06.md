**Severity:** INFO · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# Pre-registration: the portfolio position is account state, and its coverage should reach the book

**Written:** 2026-09-06, delivery seat, claim `r1-ceiling-needs-coverage-not-correction`, BEFORE
the run that tests it. The "before" run is `run_output_cc8caa857_20260906T195137Z`, which started
20:51:36 BST and imported `simulation/run_phase2b.py` six minutes before this change was written to
it — so that run is a clean pre-image and the next one is the test.

---

## The prediction

`mean_recent_margin_rate` and `portfolio_premium_pct` are declared `account_state` in
`tools/r1_inference_ceiling.py::OBSERVABLE_FIELD_SCOPE` — "the portfolio position the pricing chain
reads at every priced term". On `run_output_3851553ec` they reached **149 of 164 households**, and
every one of them came from `dynamic_pricing_log`.

**They were not short because fifteen accounts had no position. They were short because
`decide_renewal_rate` wrote the position down only where it moved a rate.** Writer 1 fires on
`abs(portfolio_prem) > 1e-6`; a book earning exactly its target margin produces a premium of zero
and records nothing, while `mean_recent_margin_rate = 0.08` is a reading the company genuinely took.
The same accounting accident as `company_eac_kwh`, which the company computed for everyone and
wrote down at renewals.

**I predict, on the first run that carries this change:**

1. `field_provenance` for both fields gains an `account_state_log:<n>` source beside the existing
   `dynamic_pricing_log:149`.
2. Their household count rises from 149 toward the book — specifically to **the number of
   households holding at least one term struck after the company's first completed term of that
   commodity**. NOT necessarily 164: `portfolio_position` returns `None` on an empty history, which
   is an honest absence and the one case where there is no reading to record. If the book is 164 I
   expect 160–164 and I will not treat a shortfall of a few as a failure.
3. The **whole-book pair rung** gains `mean_recent_margin_rate x portfolio_premium_pct` at a
   household count at or near the book, rather than 149. That pair already wins 13 of 40 partitions
   on that rung, so this is the pair most likely to move.

**I predict it does NOT fix the pair rung's refusal.** The all-candidate rung is stuck at 69
households because its winner is `perceived_bill_saving_gbp x portfolio_premium_pct`, and the first
of those is `decision_only` — it exists only where a renewal window opened. The instrument needs
~72 households carrying **both** fields of a pair. This change cannot supply that, because
manufacturing a bill saving for an account that never renewed would invent the coverage rather than
record it. **If the pair rung clears after this, I have done something wrong and should look for
it.**

## What would refute me

- Both fields still show only `dynamic_pricing_log` → the write never reached the record.
- Coverage lands well below the book with a non-empty history → `None` is being returned where a
  reading exists, or the position is being taken after the history moves.
- The figures disagree with `dynamic_pricing_log`'s on any household carrying both → there are two
  implementations again, which is the thing
  `test_the_position_is_the_same_reading_the_rate_was_struck_against` exists to stop.

## Where to read the answer

`python3 -m tools.r1_inference_ceiling`, the `WHERE EACH OBSERVABLE COMES FROM` block. Note that
`tools/r1_inference_ceiling.py` is itself contested in the shared tree — see
`SEAT_FINDING_TWO_LANES_EACH_BUILT_R1S_UNBIASED_MAGNITUDE_ESTIMATOR_AND_A_PATHSPEC_LAND_DELETES_NINE_OF_HEADS_SYMBOLS_2026-09-06.md`
— so read it from a tree whose copy of that file you have checked.
