**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The prepayment correction moved six measured facts of the W2_11 harness

## What changed in the world

`simulation/payment_behaviour_source.generate_payment_event` sent every household payment method to
the core outcome model as `"direct_debit"`. That bypassed `arrears_engine.payment_outcome`'s own
prepayment branch, which never fails or lates a period because a meter is paid before use. The
correction routes prepayment to that branch. On `tools/couple_w2_11_d5.py`'s n=300 book the only
cells that moved are prepayment ones: seed 7 loses 26 failed and 50 late prepayment periods, seed 11
loses 13 and 41, and seed 23 loses 21 and 46.

## The six facts

Each of these tests asserted a measured fact about this harness's book, not an invariant. Each is
re-keyed to its re-measured value with the same shape, and each cites this file. All six revert to
their old values when prepayment is routed back to the direct-debit tier
(`payment_behaviour_source.PREPAYMENT_METHOD = "direct_debit"`): 49 of 49 harness tests pass under
that routing.

| Test (`tests/tools/test_couple_w2_11_d5.py`) | Old fact | New fact |
|---|---|---|
| `test_detection_latency_is_the_real_thing_and_not_an_as_of_artefact` | retired median moves 30 days for a 30-day `as_of` shift (51 -> 81) | moves 33 (51 -> 84). It still marches with the clock, but no longer one-for-one |
| `test_the_interior_cause_is_the_denominators_not_the_books_placement` | excluded share 0.232-0.237; floor 0.20 | 0.182-0.191; floor 0.157 (the same 14% relative margin below the minimum) |
| `test_the_published_headline_moves_a_third_of_the_sub_readings_step` | headline step 0.32 / 0.36 / 0.27 (seeds 7/11/23), inside the literal band 0.2-0.4 | 0.092 / 0.265 / 0.098. The spread is 2.9x, wider than the old band's 2x, so the band is kept per seed at +/- one third of each measured step |
| `test_the_book_predicts_both_edges_and_the_sweep_measured_them` | the mix saturates one day before belief (+1 vs +2) | both saturate at +2 |
| `test_the_saturation_rule_is_not_keyed_to_a_register_state` | mix edge = oldest failure - window - 1 | mix edge = oldest failure - window |
| `test_bit_equality_counts_a_difference_no_consumer_can_render` | bit-equality and 4dp reader floors agree on every seed of both figures | they agree everywhere except the mix figure on seed 23: bit-equality 1 day, reader 2 days |

## What is not established

Two of these are statements about the instrument rather than the book, and they deserve a reader
before anyone builds on them:

1. **The headline step.** The published detection-latency figure now moves 0.09 days per day of
   company error on two seeds and 0.27 on the third. The caveat's claim that the headline moves
   "about a third" of the sub-reading's step held on the old book and is seed-dependent on this
   one.
2. **The mix figure is no longer blinder than belief.** The register's differential between the two
   belief figures, its evidence that the mix is a blunter instrument, has gone on this book. It may
   reappear on a book with more failure events. Nothing here says which.

## Mutation proof

Each re-keyed test was run unmutated (green), then mutated (red):

- latency: freeze the clock the retired key reads;
- interior: excluded share set to 0.15;
- step: steps doubled;
- edge: mix edge set back to +1;
- law: register mix edge set to +1;
- bit-equality: seed-23 floor set back to 2.

The scratch harness is `test_mut_six.py` in the session scratchpad, not in the repo.
