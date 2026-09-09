**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — give the renewal objective the departure term it has never had) · **Class:** measurements_that_mirror

# RESULT — the departure term moves eight of nine years down. The ninth is 2022, and it moves by exactly zero.

Graded against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_A_DEPARTURE_TERM_IN_THE_RENEWAL_OBJECTIVE_MOVES_2026-09-09.md`,
landed at **`8a1164c5e`** — *before the changed code had been run once*. Every figure below was
predicted first and is reported the way it fell. **Six of the ten predictions are settled here;
four are book-side and need the three-arm run, which is launched and named at the bottom.**

Subject: `company/pricing/value_based_renewal.expected_value_gbp`, which now reads

```python
p_retain × contribution × annuity  −  (1 − p_retain) × replacement_cost
```

`replacement_cost` is **not a new number**: it is `saas.growth_mandate.cost_per_acquisition_gbp`,
reading `saas.opex_ledger`'s sourced single-fuel PCS commission of **27.50 GBP** against
`docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`. That constant was cited, tested and **unwired
for seven weeks**. `max()` in `enriched_churn_estimate` is untouched, so every move below is
attributable to this one term.

---

## The answer, in one paragraph

Giving a departure a price makes the arm **buy retention**, and it does so everywhere except where
it matters most. The chosen margin falls at eight of the nine years — between **4.25 and 6.00
GBP/MWh**, about 5% of the offer — and at **2022 it does not move at all**. 2022 is the year the
finding said was priced hardest, and it is the one year this repair cannot reach: the arm's answer
there is not an interior optimum but the **support frontier**, the edge of what its own churn model
has evidence for, and a term that shaves the objective's slope cannot move an argmax pinned to a
boundary the slope is still climbing toward. **The crisis-year defect is not fixed by this and I
predicted that it would not be** — though not for the reason that turned out to operate. The
unpredicted result is larger: the arm's sensitivity to household **size** nearly doubles (spread
18.25 → 35.25 GBP/MWh), because a replacement cost is a fixed number of pounds while the
contribution it is weighed against scales with volume. The smallest household in the sweep is now
offered **18.50 GBP/MWh less** and the largest **1.50 less**.

## The nine years — HEAD's baseline re-read this turn, against the changed rule

`python3 -m tools.renewal_rule_price_response`, anchor household, `periods = 1.0`.

| year | mkt move | flat to | **before** | **after** | Δ | p_retain before → after |
|---:|---:|---:|---:|---:|---:|---|
| 2017 | 0.00 | 12.0 | 113.25 | 108.25 | **−5.00** | 0.5289 → 0.5508 |
| 2018 | 0.00 | 12.0 | 91.75 | 86.25 | **−5.50** | 0.5065 → 0.5347 |
| 2019 | 0.00 | 12.0 | 88.25 | 82.50 | **−5.75** | 0.5034 → 0.5339 |
| 2020 | −0.05 | 5.0 | 80.50 | 74.50 | **−6.00** | 0.4702 → 0.5027 |
| 2021 | 0.17 | 45.0 | 110.00 | 104.50 | **−5.50** | 0.5930 → 0.6209 |
| **2022** | **0.67** | **130.0** | **160.00** | **160.00** | **0.00** | 0.9574 → 0.9574 |
| 2023 | −0.13 | 0.5 | 114.50 | 110.25 | **−4.25** | 0.5086 → 0.5262 |
| 2024 | −0.21 | 0.5 | 92.25 | 87.00 | **−5.25** | 0.4429 → 0.4662 |
| 2025 | −0.10 | 0.5 | 95.75 | 90.50 | **−5.25** | 0.4759 → 0.5002 |

## The predictions, graded

| | prediction | outcome |
|---|---|---|
| **P1** | no year's chosen margin RISES | **CONFIRMED.** All nine ≤ baseline; eight strictly below |
| **P2** | at least one year falls by more than 0.25 — the term reaches the DECISION | **CONFIRMED.** Eight of nine. Not an equivalence |
| **P3** | 2019 falls into 78–88 | **CONFIRMED.** 88.25 → **82.50**, a fall of 5.75, mid-band |
| **P4** | 2022's fall is strictly smaller than 2019's | **CONFIRMED, and to the limit — but my stated MECHANISM was incomplete.** See below |
| **P5** | `bill_shock_count` and `satisfaction_score` stay SILENCED | **CONFIRMED.** Both 0.00 GBP/MWh. The falls are ~5 GBP/MWh and 2019's payment floor binds only below 12.0, so the arm never walks into the band that would have un-silenced them |
| **P6** | `test_the_household_distress_channel_cannot_reach_the_price` stays GREEN | **CONFIRMED.** 7 passed. The `max()` is untouched, as intended |
| **P7–P10** | book-side: inversion, AUC, mediation, realised sign | **NOT SETTLED HERE.** Three-arm run launched; see "What is next" |

### P4 — confirmed, and my reason for it was not the operative one

I predicted 2022 would move least because its believed `p_retain` is 0.9574, so `p'` is small near
its optimum and the new gradient `p' × K` is the smallest of the nine. **That is true and it is not
what stopped the move.** Interrogated directly, the 2022 decision reports
`endpoint_side="ceiling"`, `ceiling_bound=False`, `extrapolation_bound=True` — the answer is the
**support frontier**, not a lawful cap and not an interior peak. Its `considered` grid is still
*rising* at the top rung (441.97 at 160.00 against 441.85 one step below). A term that shifts the
slope cannot move an argmax pinned to a boundary while the slope at that boundary stays positive,
and 27.50 GBP is nowhere near enough to flip it.

The small `p'` is upstream of that — it is *why* the objective is still climbing at the frontier —
so the prediction was right through a chain I had only written the first link of. **Recorded
because a confirmed prediction with a wrong mechanism is the shape that gets quoted as
understanding.**

### The unpredicted result: the arm's size gradient nearly doubles

Not in the pre-registration at all, and the largest single effect measured:

| eac_kWh | **before** | **after** | Δ |
|---:|---:|---:|---:|
| 1,000 | 74.75 | **56.25** | **−18.50** |
| 2,000 | 84.75 | 75.50 | −9.25 |
| 3,100 | 88.25 | 82.50 | −5.75 |
| 5,000 | 90.75 | 87.25 | −3.50 |
| 8,000 | 92.50 | 90.00 | −2.50 |
| 12,000 | 93.00 | 91.50 | −1.50 |
| **spread** | **18.25** | **35.25** | **+17.00** |

The arithmetic is immediate once printed and I did not print it in advance: `K` is a fixed 27.50
GBP, while `p_retain × contribution` scales with volume. On a 1,000 kWh household the departure
term is a large fraction of what is being maximised; on a 12,000 kWh one it is a rounding error.
So the arm pulls back hardest exactly where it has least to lose.

**This sharpens an existing reading rather than reversing it.**
`SEAT_RESULT_THE_ARM_PRICES_UP_SMALL_HOUSEHOLDS_AND_ITS_BELIEF_IS_WORST_EXACTLY_WHERE_IT_PRICES_HIGHEST_2026-09-09.md`
established that the rule already protects the small household and harvests the large one; this
widens that gap by 93%. **Whether that helps or hurts the inversion is exactly what P7 asks and is
not answerable from a response surface** — it depends on whether departures on the real book are
small households, which this sweep cannot see.

## The honest verdict on the item's own question

The item asked whether this could move the selection leg off zero. **On the function: yes,
decisively — the term is roughly a tenth of the objective and it changes eight of nine answers.
On the book: not yet established, and this result does not claim it.** What is settled is that the
old objective was not a simplification but a missing cost line, and that a departure now costs the
arm the sourced price of replacing the customer instead of zero.

## What is still wrong, said plainly

* **The crisis year is untouched.** The mechanism the original finding names — the `max()` netting
  that collapses the rate channel in a year the cap moved — is not addressed here and 2022's
  160.00 GBP/MWh stands. This was step 2 of three and step 1 (noisy-OR) is the one that reaches it.
* **A household in distress is still inaudible at every price.** P5 confirming is P5 being bad
  news: `bill_shock_count` and `satisfaction_score` still cannot move the answer by a penny.
* **The replacement cost is a FLOOR and the code says so.** Not counted: the replacement's
  onboarding cost, the margin foregone between departure and replacement, and the broker trail for
  SME/I&C — where `cost_per_acquisition_gbp` correctly returns 0.0 for the one-off and the
  objective therefore charges **nothing** for losing a business account. That zero is carried on
  the decision as `departure_cost_unsourced` with its reason, rather than summed silently, because
  a silent zero there tells the arm a business departure is free.
* **`K` is undiscounted**, on purpose: discounting would shrink it, so this is the direction that
  does not flatter the maximiser.

## The controls, and the poison round that graded them

`tests/company/pricing/test_value_based_renewal.py`, six new legs. **Four poisons, all caught:**

1. **Term dropped** (`return retained`) → 2 red, including the choice-moves leg.
2. **Sourced call replaced by the literal `27.5`** → 2 red. Note which one did *not* fire:
   `test_the_replacement_cost_is_the_SOURCED_constant_and_not_a_literal_here` compares *values*, so
   a literal equal to today's source passes it. **The partition leg is what actually catches a
   literal** (it hard-codes SME's zero away), and this is recorded so nobody reads the first leg as
   stronger than it is.
3. **Every segment given a named zero** → 4 red, including the partition leg. This is the
   fail-open shape the partition control exists for.
4. **`departure_cost_gbp` given a `= 0.0` default** → the fail-silent leg red, alone and correctly:
   a default would let any caller restore the pre-change objective and publish it under the new
   field's name.

`test_the_replacement_cost_partition_can_be_taken_BOTH_ways` asserts both branches reachable in
**one statement** before describing either, per the rare-branch rule — a helper that returned a
named zero for every segment would otherwise satisfy a leg-per-branch battery.

## What this cannot settle

One anchor household, one probe. **The sweep is a statement about the FUNCTION, not the book**: a
row that moves proves the term *can* reach the price at these inputs and says nothing about how
often it does. Direction, not magnitude, on everything book-side — which is not measured here at
all.

## What is next, ranked

1. **The three-arm run, against predictions already landed.** P7 (cross-stratum concordance
   0.2686 → 0.28–0.40, the 73% into 60–72%; AUC 0.6667 → 0.58–0.66, not reaching 0.50), P8 (the
   within-belief gap survives — *the one I most expect to be wrong*), P9 (**no prediction** on the
   realised sign), P10 (what "this changed nothing" would look like). Those are at `8a1164c5e` and
   are unreadable-ahead by construction, so whoever grades them inherits a real pre-registration.
2. **The noisy-OR.** Step 1 of the finding's three, and the only one that reaches 2022 and the
   silenced distress channel. It changes every churn estimate in the tree and needs its own
   three-arm run.
3. **The practitioner question, raised on NTFY while this ran.** A retention desk that cannot see
   arrears is odd against how the trade actually works and no published source will say so. That is
   the director's side of the knowledge layer and it is not a thing to build on unasked.
