**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_19_who_lives_where_money_and_composition

**Knowledge:** none -- the page this feeds, `how-many-synthetic-households`, is written and cannot land: the site lane is red at HEAD on another lane's uncommitted change (`SEAT_FINDING_THE_SITE_LANE_IS_RED_AT_HEAD...`). Declaring the topic here would name a page no committed tree carries, which the gate rightly calls the same defect as no declaration. This is re-declared the moment the page lands.

# The full vector costs about thirty times the partial one, and lands near three thousand

**Measured 2026-09-07**, delivery seat. Reproduce with
`python3 -m tools.demand_vector_coverage --measure`.

The director asked for a number that is not a floor: every axis in, the uncounted list empty or each
item explained. **Every component of the canon's subject vector is now in the measurement —
`blind_to` is empty for the first time.** The number that comes out is far larger than the partial
one, the prediction is confirmed in mechanism and understated in size, and a *new* limit appeared
that is stated here rather than smoothed.

---

## The prediction, tested

I filed this before payment method was built, expressly so it could be wrong:

> *Payment method (3), read pattern (2) and arrears (~2) are strata and should behave like the
> non-gas one… if the three strata composed independently that is twelve combinations and roughly
> 3,000 households… If payment method lands and moves the figure by a tenth rather than threefold,
> the strata mechanism is wrong.*

**It did not move by a tenth. It moved by a factor of about thirty.**

| what was in it | strata | axes | N at tolerance 0.10 |
|---|---:|---:|---:|
| before payment method | 2 (fuel) | 6 | **102** |
| after payment method and shape | 4 (fuel × payment) | 7 | **~3,000** |

**The mechanism is confirmed and my arithmetic was too kind.** I reasoned that *k* strata multiply
the requirement by about *k*. Doubling the strata multiplied it by roughly **30**, not 2. The reason
is that coverage is owed *within* each stratum on *every* axis, and the smallest stratum —
electrically-heated households not on direct debit, 5.7% of the book — has to be reproduced as
thoroughly as the largest. The binding cost is the smallest cell of the cross, not the count of
cells.

**So the direction of the director's worry was right and mine was too:** strata are what multiply.
My estimate of *how much* was wrong by an order of magnitude, in the direction of optimism.

## What is now in the vector

All seven, and `REDUCES_OVER.blind_to` is empty:

annual gas · annual electricity · seasonal swing · weather sensitivity · **peak-window share** ·
insulation ceiling · turn-down ceiling — stratified by **fuel × payment method**.

**The half-hourly shape is in, and measuring it corrected the canon's premise.** The canon says *"the
world rescales one national profile, so every household has the same half-hourly shape"*. It does
not: across occupancy patterns and household sizes the 16:00–19:00 share runs **0.196 to 0.253**, a
29% relative spread. But `single` and `family` come out identical to four decimal places and only
`elderly` differs — so **the shape varies on effectively one binary rather than on a continuum.** The
concern was right in direction and the literal claim was wrong.

## Does it converge? I said no, and the next point refuted me

I wrote this section first as *"N grows with the reference population, so it has not converged"*, on
two points — 2,716 at 12,000 and 3,824 at 40,000. **The third point refutes that reading and the
claim is withdrawn.**

| reference points | N at tolerance 0.10 |
|---:|---:|
| 12,000 | 2,716 |
| 40,000 | 3,824 |
| 120,000 | **2,748** |

It does not rise; it varies around roughly **3,000**, and the 40,000 figure is the outlier rather
than the trend. Two points looked like a slope because two points always do. **The spread is
measurement noise — ladder granularity and the seeded first pick — not resolution limitation.**

**So the number is about 3,000 at tolerance 0.10**, and the honest uncertainty is the spread across
reference sizes, roughly 2,700 to 3,800.

**That is what I predicted, more precisely than I had any right to expect.** The pre-registration
said *"if the three strata composed independently that is twelve combinations and roughly 3,000
households… so the honest range is low thousands"*. Two of the three strata are built and the answer
is ~3,000. The mechanism is confirmed; the arithmetic that got me there — *k* strata multiply by
about *k* — is still wrong, since two strata pairs gave ×37 rather than ×2. **I got the right number
from the wrong reasoning, and that is worth saying rather than banking the hit.**

## A defect that would have read as a huge answer

The first stratified run returned **"no size accepts"** at every tolerance, up to 5,200 cases. That
looks like a gigantic sample requirement and it was a broken criterion.

**The weights were fitted globally and scored per stratum.** One weight vector was solved to
reproduce the *population*, and then each stratum's sub-sample was scored against *that stratum's*
distribution — asking a sub-sample to match a distribution its weights were never fitted to, which
it can only do by luck.

Fitting **within each stratum** is both the fix and the correct reading of "the mass it stands for":
strata partition the population, so within-stratum weights aggregate to the population weights
exactly. After the fix the same ladder converges smoothly (0.30 → 0.15 → accept).

**This is the second time in this module that a broken criterion produced a plausible large number**
— the first was the random-sample design giving 8,500. A criterion that fails by returning
*more cases needed* is dangerous precisely because more-is-conservative looks like caution.

## What is left uncounted, each explained

| axis | why it is not in |
|---|---|
| payment method's **third** category | DD share is anchored (DESNZ QEP, 72%/75%); the prepayment-vs-standard-credit split of the remainder is a **named gap** in `ASSUMPTIONS.md` — not found in the published commentary. Splitting it would be inventing the number. The two-way split **is** in. |
| meter read pattern | a stratum, not yet built; expected to multiply again |
| arrears position | a stratum, not yet built |
| move history | mostly continuous; expected cheap |
| credit position | correlated with arrears; expected cheap |
| tariff and dates | partly stratum; effect unknown |

**On the mechanism as now measured, the two unbuilt strata should multiply again.** If read pattern
and arrears behave as fuel and payment method did, the full commercial vector is **tens of
thousands**, not thousands. That is the next prediction and it is filed here with the same falsifier
shape: if read pattern lands and moves the figure by less than 2×, the mechanism is wrong.

## Also landed in this run

- **Occupancy conditioned on the address.** `dwelling_records.people_count_for_area` draws household
  size from *that output area's* published distribution, with `people_count_source` reporting
  whether the local or national distribution was used — a national draw wearing a local draw's name
  is the defect being replaced. **It buys little and that is the finding:** an output area explains
  **9%** of household-size variance.
- **A filer for director documents**, so the severity header and Knowledge declaration are the
  machine's bookkeeping rather than the director's. Severity is *read* from the document's own Type
  block and refused if absent; lane is derived where the subject says so and refused where it does
  not; the Knowledge topic is never invented.
