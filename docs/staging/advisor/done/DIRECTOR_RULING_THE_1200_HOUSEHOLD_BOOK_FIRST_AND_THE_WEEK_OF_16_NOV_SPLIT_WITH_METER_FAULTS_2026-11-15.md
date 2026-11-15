**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] The 1,200-household book first; the week of 16 Nov split as proposed, with meter faults ranked after the write-off rule

**Type:** RULING, through the advisor channel. The director's words, from chat, Sun 15 Nov 17:53 GMT, answering the advisor's two recommendations:

- "Yes to your recommendations"

## 1. `for_the_director` row `the-value-test-s-sized-book-candidate`: answered, as proposed

- Run step 6 as **one 1,200-household book on 12 `churn_roll` draws**. Do not shard it. It resolves about £4.80 per household-year.
- **Do not build the sharding now.** Build it only if A or B shows an effect the 1,200 book cannot separate from zero.
- The advisor's reason, which he accepted: the renewal belief is being retrained (pre-registered 14 Nov, AUC 0.68 target against today's 0.52). Paying for £3 resolution on an engine already known to be weak is premature. Improve the belief, then size the test.
- Close the row with this resolution.

## 2. `docs/operations/WEEKLY_BALANCE_REVIEW_2026-11-16.md`: approved, with one addition

- **The split stands:**

  | Share | % |
  |---|---|
  | Correctness and backlog | 42 |
  | Supplier features | 18 |
  | World features | 15 |
  | Harness | 15 |
  | Knowledge | 10 |

  The feature third is 33%. The accelerate list stands as written.
- **The remedy in §2 is approved.** A pause in a ruling is applied to `feature_share` in the same commit that records it.
- **Addition:** rank `the-world-produces-real-meter-data-faults-for-the-supplier-to-find` (in `priority_order.yaml`, his 14 Nov 11:05 steer) in the world lane **directly after the write-off rule** (§5 item 4). Its first step is the K8 metering data quality page.
- Usage: the week ends at the 03:00 reset. Land nothing new tonight beyond this ruling's records.

## Done

Worker tick, Sun 15 Nov ~18:30 GMT, the only landing made under the 98% reading's "land nothing new tonight beyond this ruling's records".

- **Row 1:** `the-value-test-s-sized-book-candidate` in `docs/direction/DIRECTION.yaml` is now `answered`, with his words and the resolution. Its commitment is `value-test-step-6-the-1200-household-twelve-draw-book`: one unsharded 1,200-household book on 12 `churn_roll` draws after the A/B grades, due 22 Nov. No sharding is built.
- **Row 2, split:** already in force. `priority_order.yaml` carries `feature_share: 0.33`, and the §2 remedy is written in the balance review. No edit was needed.
- **Row 2, addition:** already true on origin. `the-world-produces-real-meter-data-faults-for-the-supplier-to-find` is the first world-lane candidate, directly after `the-worlds-write-off-rule-meets-gb-evidence`, the last world item. No edit was needed.
