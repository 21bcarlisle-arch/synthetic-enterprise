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
| **P7** | inversion softens: cross-stratum concordance into 0.28–0.40, AUC into 0.58–0.66 | **REFUTED ON BOTH LEGS, and in the opposite direction.** Concordance 0.2686 → **0.2652**; AUC 0.6667 → **0.6713**. See below |
| **P8** | within-belief AUC stays above pooled−0.02 — *"the one I most expect to be wrong"* | **CONFIRMED.** Pooled 0.6713, within-belief **0.6643**, floor 0.6513. The gap NARROWED, 0.0154 → 0.0070 |
| **P9** | realised net sign — **no prediction filed** | **REPORTED, NOT GRADED.** Selection **−£335.40** (was +£319.10); level share **1.0200** (was 0.9817) |
| **P10** | what would make this item wrong | **SUBSTANTIALLY MET, not literally.** The book moved; every move is inside the noise the page already publishes. See below |

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

---

# P7–P10, graded against the three-arm run

`docs/observability/value_cycle_ab_s1_three_arm_departure_20260909.json`, generated
**2026-09-09T21:35:40Z**, producing commit **`e1895d6c8`** — the departure term's own landing —
world digest **`39a192ce04c1eda8`**. The run finished at 21:35Z and sat **untracked on disk for a
day**; this section is written from it and it is landed in the same commit. Finished work that
never left the tree is worse than work not started.

## First: the pre-registration named the wrong comparison artefact

P7's baseline figures are quoted as coming from
`docs/observability/value_cycle_ab_s1_three_arm_20260909.json`. **The cross-stratum concordance
0.2686 is not in that file and never was** — it has no `method_skill.fixed_horizon.pair_strata`
block at all, because the block was built after that run. 0.2686 lives in
`value_cycle_ab_s1_three_arm_20260909b.json` (producing commit `8b846013e`, generated 13:15Z).

**This does not invalidate the comparison and it is recorded rather than quietly corrected.** The
`b` run carries the **same world digest `39a192ce04c1eda8`** and the same seed as the departure
run, and its own `level_vs_selection` and `method_skill.concordance` are identical to the named
artefact's to every published place — the two are the same world re-read by a later producer. So
the baseline is sound and the address written on it was wrong. *A prediction that names the wrong
file is still a prediction; one whose figure cannot be found in any file is not.*

The margin-against-departure AUC baseline (0.6667 pooled, 0.6513 within belief quartiles) is in no
artefact at all: it was computed ad hoc in the turn that filed
`SEAT_RESULT_THE_ARM_PRICES_UP_A_YEAR_NOT_A_HOUSEHOLD_AND_CANNOT_HEAR_DISTRESS_AT_ALL_2026-09-09.md`.
**Before grading anything against it I re-ran the same statistic on the old artefact and reproduced
0.6667 over 3,320 pairs and 0.6513 over 783, with mean margins 48.98 against 34.30** — every figure
to four places and both pair counts. Only then was it applied to the new run. A baseline I cannot
reproduce is not a baseline, and grading against one would be grading against a memory.

## P7 — REFUTED on both legs, and the direction is the finding

| | baseline | predicted | observed | |
|---|---:|---|---:|---|
| cross-stratum concordance | 0.2686 | rise into **0.28–0.40** | **0.2652** | **REFUTED** — fell 0.0034 |
| …stated as the 73% | 73.14% | fall into **60–72%** | **73.48%** | **REFUTED** — rose |
| margin-against-departure AUC | 0.6667 | fall into **0.58–0.66** | **0.6713** | **REFUTED** — rose 0.0046 |

I predicted the inversion would **soften and not close**. It did neither: on all three readings it
**very slightly hardened**. The arm still gives the customer it is about to lose the higher margin,
and after paying £27.50 for each departure it does so marginally more often than before.

**The mechanism is in the same artefact and it is not subtle.**

| | before | after |
|---|---:|---:|
| priced renewals | 214 | 215 |
| decided by the lawful Ofgem ceiling | 143 | **138** |
| decided by the churn model's support frontier | 1 | 1 |
| **chosen freely** | **70** | **76** |
| share decided by a bound | 0.6729 | **0.6465** |
| median margin, freely chosen | 45.0 | **35.0** |
| median margin, ceiling-decided | 12.0 | 12.0 |

The departure term worked exactly as the function sweep said it would — **on the decisions it can
reach**. It pulled the freely-chosen median down by **10.00 GBP/MWh** and released **six** renewals
from the cap. But **139 of 215 answers are still set by a bound**, and on those the term is
arithmetically incapable of moving anything: a price pinned to the Ofgem ceiling does not care what
a departure costs. P7 assumed a tenth-sized nudge to the objective would produce a tenth-sized
nudge to the book. **It cannot, when two thirds of the book's prices are not being chosen by the
objective at all.** That is the operative reason and I did not have it when I wrote the prediction.

## P8 — CONFIRMED, and it was the one I said I most expected to be wrong

Pooled AUC **0.6713**, within-belief-quartile pooled **0.6643** over 782 pairs, against a stated
floor of pooled−0.02 = **0.6513**. The belief still fails to mediate the arm's own price — and the
gap **narrowed**, from 0.0154 to 0.0070. Making the objective *more* sensitive to `p_retain` made
belief a *worse* explanation of price, not a better one, which is the opposite of the reason I gave
for expecting the prediction to fail. **Consistent with P7's mechanism**: the ceiling, not the
belief, is what sets most of these prices, and adding a belief-weighted term to an objective that
is not binding cannot make belief a better statistic for the answer.

## P9 — reported, and it was correctly not predicted

Declining to predict this was right: the sign flipped.

| `level_vs_selection`, settled-realised clock | before | after |
|---|---:|---:|
| control arm net | £147,954.26 | £147,886.78 |
| value arm net | £165,398.23 | £164,680.47 |
| level arm net | £165,079.13 | £165,015.87 |
| value advantage | £17,443.97 | £16,793.69 |
| **selection** | **+£319.10** | **−£335.40** |
| **level share of advantage** | 0.9817 | **1.0200** |

**The sign of the selection leg flipped and this settles nothing about the sign.** The move is
£654.50 on a quantity whose own nine-seed spread in this same world is **±£1,810.50**, with re-draws
running from −£3,036.25 to +£1,260.93 — a family that already straddles zero. This is **one draw**,
and one draw moving a third of a standard deviation is what one draw does. `site/data/value_arms.json`
already withholds a verdict on that leg for exactly this reason and it still should.

The method-skill reading agrees, and note that it is **a different statistic from P7's**:
`method_skill.concordance` ranks the arm's price against realised value **created** per priced
term, where P7's cross-stratum concordance ranks it against **departure**. It moved 0.5338 →
**0.5442** and remains **inside the null interval** [0.4496, 0.5506] (p 0.1907 → 0.0854, 20,000
permutations at seed 20260828). This run does not distinguish the method from chance in either
direction, before or after.

## P10 — substantially met, and the literal antecedent is not what happened

P10 said: if P1 and P2 hold but P7 fails **in the direction of no book-side movement at all**, the
honest verdict is "this changed nothing that matters". P1 and P2 hold. P7 failed. **But not in the
shape P10 named** — the book did move: six decisions off the cap, the freely-chosen median down
10.00 GBP/MWh, the selection leg through zero, value-arm net down £717.76.

**Every one of those moves is inside the noise this page already publishes**, and the two that
speak to the item's own question — the inversion and the selection leg — moved the wrong way and
by less than a re-draw. So P10's *substance* is met by a route it did not anticipate: not "the term
reaches the function and not the book", but **"the term reaches the function decisively, reaches
the book measurably, and reaches the QUESTION not at all"**. Recorded this way rather than ticked,
because a prediction that is right about the conclusion and wrong about the road is the shape that
gets quoted as understanding — the same correction P4 needed above.

## What this run cannot settle, and what it now says to do

One world, one seed, 215 priced decisions, 124 scored. Nothing here carries an account-level
standard error and the AUC pairs are clustered on 73 accounts.

**The ranked next step changes on this evidence.** The noisy-OR was already step 1 of three, and
this run raises its priority rather than confirming a plan: **while 65% of the arm's answers are
set by the lawful cap, no change to the objective can be measured on the book.** Any further work
on the objective — the noisy-OR included — should expect the same result on the same population
unless it moves decisions off the ceiling. `bound_attribution.what_would_change_this` says what
would, and says correctly that it is a **fidelity** change that must be decided blind to what it
does to this delta.

---

## The honest verdict on the item's own question

The item asked whether this could move the selection leg off zero. **On the function: yes,
decisively — the term is roughly a tenth of the objective and it changes eight of nine answers.
On the book: it moved the leg from +£319.10 to −£335.40, and that answers nothing, because the
same leg re-drawn nine times in this world runs from −£3,036.25 to +£1,260.93.** The leg was not
moved off zero; it was moved by less than a third of its own noise, and it has no sign to be moved
off.

What is settled is that the old objective was not a simplification but a missing cost line; that a
departure now costs the arm the sourced price of replacing the customer instead of zero; and — the
part I did not know when this section was first written — **that the arm's answers are mostly not
the objective's answers at all.** 139 of 215 are set by the lawful cap or the model's support
frontier. That is why a tenth-sized change to the objective bought a book-side movement
indistinguishable from a re-draw, and it is the reading that should govern what is attempted next.

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

## THE RUN IS LANDED — this document was its address

**Superseded 2026-09-10: the run completed at 21:35:40Z on 2026-09-09 and is graded above.** Its
artefact then sat **untracked** — invisible to git, to origin and to every reader — until this
commit. The liveness claim below did its job; nothing was watching for the *finished* artefact to
be filed, which is the second time in three days a completed run stayed in the tree. The launch
record and the deadman both key on the job being alive, so **a job that succeeds and writes an
untracked artefact looks exactly like a job that is done.** Recorded here rather than as a separate
finding, because the remedy belongs to whoever next builds a launch record and not to a register.

The original in-flight block, kept as written:

`background.launch_long_job` was given this file as `--asserted-live-by`, so
`launch_liveness --check` and the deadman re-ask the claim against this paragraph. It is stated
here rather than left implied, because a liveness record whose address does not make the claim is
the vacuity that mechanism exists to close.

| | |
|---|---|
| job | `value-cycle-ab-departure-term-20260909` |
| unit | `longjob-value-cycle-ab-departure-term-20260909.service` — **its own cgroup**, verified at launch, so this tick's teardown cannot reach it |
| command | `python3 -m tools.run_value_cycle_ab --level-arm --out docs/observability/value_cycle_ab_s1_three_arm_departure_20260909.json` |
| artefact | `docs/observability/value_cycle_ab_s1_three_arm_departure_20260909.json` |
| log | `/var/tmp/longjob-value-cycle-ab-departure-term-20260909.log` |
| launched | 2026-09-09T20:58:05Z · **~1h50m**, three full passes |
| producing commit | `e1895d6c8` — the departure term's own landing, so the artefact's run identity contains the change it measures |

**Whoever grades it:** the predictions are at `8a1164c5e` and were landed before any of this ran.
Compare against `docs/observability/value_cycle_ab_s1_three_arm_20260909.json` (world digest
`39a192ce04c1eda8`, producing commit `62334dc76`) — **the same world and seed, so the only thing
that differs between the two artefacts is the departure term.** Re-ask the claim with
`python3 -m background.launch_liveness --check` before assuming it is still running; a dead unit
that wrote no artefact reads exactly like one still working.

## What is next, ranked

1. ~~**The three-arm run, against predictions already landed.**~~ **DONE — graded above.** P7
   refuted on both legs and in the opposite direction, P8 confirmed, P9 reported, P10 met by a
   route it did not name. The artefact is landed in the same commit as this grading.
2. **The bound, ahead of the noisy-OR — and this is a change of order made on the evidence.**
   139 of 215 priced answers are set by the lawful ceiling or the support frontier, so **no change
   to the objective can be measured on this book until fewer of them are.** The noisy-OR is still
   step 1 of the finding's three and still the only repair that reaches 2022 and the silenced
   distress channel — but run on this population it should be expected to produce exactly what the
   departure term produced: a decisive move on the function and a re-draw-sized move on the book.
   `bound_attribution.what_would_change_this` names the only honest lever, and names it as a
   **fidelity** change that must cite a published source and be decided blind to what it does to
   this delta (R13, R12). **Establishing whether any defensible churn curve makes the optimum
   interior below the cap is the question, and if none does, that is the answer.**
3. **The practitioner question, raised on NTFY while this ran.** A retention desk that cannot see
   arrears is odd against how the trade actually works and no published source will say so. That is
   the director's side of the knowledge layer and it is not a thing to build on unasked.
