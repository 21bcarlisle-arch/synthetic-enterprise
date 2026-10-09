**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The DD failure correction moved measured facts, and the W2_11 harness was pinned rather than re-keyed

## What changed in the world

- `simulation/arrears_engine._DD_FAILURE_PROB`: the LOW tier now reads the register's
  `dd_return_rate_first_presentation` (0.0087). MODERATE and HIGH keep their old ratios to LOW (4x
  and 35/3x), which are still unsourced. The tiers were 3% / 12% / 35% and are now 0.87% / 3.48% /
  10.15%.
- `simulation/payment_behaviour_source.later_settlement_date`: a returned Direct Debit is now
  re-presented. It is collected 14 days after its due date with probability
  `dd_representation_success_share` (0.46), drawn from its own substream (`dd_representation`). The
  bill's record stays `failed`. A bill that is not cured draws exactly the later settlement it drew
  before.

## Facts re-keyed (shape kept)

| Test | Old fact | New fact |
|---|---|---|
| `tests/simulation/test_debt_objection.py::test_a_live_run_cures_some_unpaid_bills_and_leaves_others_unpaid` | every cure lands after day 28 | every cure is either the re-presentation (day 14, DD only) or lands after day 28, and both kinds occur |
| `tests/simulation/test_payment_behaviour_source_later_settlement.py::test_every_branch_is_taken_at_the_published_shares_and_dated_at_its_window_end` | three branches (3 months / 22 months / never) | four branches (re-presented at s, then each of the old three at (1 - s) times its old share). The sample grows from 6000 to 24000, because HIGH now fails 10.15% and the old sample fell under the test's own floor |
| same file, `test_the_cited_rates_and_windows_are_ofgems` | `REPRESENTATION_SUCCESS_SHARE is None` | equals the register's toggle |

## Figures re-pinned (`tests/background/test_live_payment_triad.py::test_q3_EVERY_PUBLISHED_FIGURE_IS_UNCHANGED_BY_THE_NEW_LEGS`)

| Figure | Old | New |
|---|---|---|
| detection | 0.009375 | 0.0192307692 |
| detection latency | 1.549839 | 1.717391 |
| belief | 0.0666666667 | 0.0615384615 |
| population mix | 0.1066666667 | 0.0533333333 |
| ageing | 0.1629183071 | 0.3857259762 |
| ageing, later settlement off | 0.0720759646 | 0.1168776875 |

The test reproduces the old figures exactly when the old tiers are restored and re-presentation is
switched off. A new block in the test holds that.

Re-presentation on its own moves only the ageing figure. At the new tiers, ageing is 0.1427 without
re-presentation and 0.3857 with it.

## The W2_11 harness: pinned, not re-keyed. This decision needs a reader

At the world's new level, 52 tests in `tests/tools/test_couple_w2_11_d5.py` went red. The harness
books are 300-400 accounts, and the corrected level leaves them about 3.4x fewer failures. Many of
the reds are the harness's own anti-vacuity guards firing, for example "the ageing numerator is
EMPTY", "not one dimension moved over the sweep" and "a near-identity permutation". These are not
facts that changed: the tests' populations thinned out or vanished.

The harness measures the company's detection instrument. Its population is declared scaffolding
(`_STRESS_MIX`, "exists only to generate a population with a real mixture of ... DD-failed cases").
So its book now draws at a declared table of its own, `HARNESS_BOOK_DD_FAILURE_PROB`, set to the
pre-correction 3/12/35%. The draw goes through `generate_payment_event(..., dd_failure_prob=...)`,
whose None default is the world's table. With the pin in place no harness fact moves.

The alternative was to re-key about 52 facts. That would also have meant raising n by about 3.4x to
restore the tests' power, and the file already takes about 30 minutes. This was not chosen. The
pre-correction route did let the harness follow the world.

**What is not established:** whether any published W2_11 figure is read anywhere as a statement
about how often the world's households fail. If one is, the pin makes that reading wrong, and the
figure should carry the harness's own failure density as its basis.

## Not changed, and still named

- Every domestic credit method (DD, standing order, card, standard credit) fails at the one
  DD-derived tier. Only a DD is re-presented.
- The billing-ledger path (`arrears_engine._resolve_bills`, `tools/generate_billing_ledger.py`,
  `dd_collection_book`) reads the new first-presentation tiers but has no re-presentation, so it
  overstates failures there by about 1/(1 - 0.46).
- A re-presentation collection crosses as `ARREARS_REPAYMENT` in the live triad, not as a DD
  collection.
- `simulation/payment_timing.py` keeps its own copy of 3/12/35% (`_DD_FAILURE_PROBABILITY`). This
  is a second implementation, not migrated here.
