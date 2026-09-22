**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the eighteen times is the CONTROL arm, the share's own seed noise is ten times the gap,
and every family on disk says the selection leg is NEGATIVE

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-arms-page-cannot-say-whether-the-advantage-is-choosing-or-the-price-level`.
Pre-registration: `docs/staging/records/SEAT_PREREG_WHY_THE_TWO_THREE_ARM_RUNS_DISAGREE_BY_EIGHTEEN_TIMES_2026-09-22.md`,
written before the verifying measurement. **All five predictions confirmed.**

**No re-run was launched, and the item's re-run would not have settled it.** The whole answer was in
columns already carried by the two artefacts and the three floor families on disk. §5 is why the
re-run the item specified is insufficient.

---

## 1. The eighteen times is 97.5% the CONTROL arm — the arm that prices nothing

`level_advantage_gbp = level_arm_net − control_net`. One variable at a time, between the two runs:

| | 2026-09-08 | 2026-09-18 | Δ |
|---|---|---|---|
| `level_arm_net_gbp` | 157,608.98 | 158,059.09 | **+450.11 (+0.29%)** |
| `control_net_gbp` | 140,140.54 | 157,806.88 | **+17,666.33 (+12.61%)** |
| `level_advantage_gbp` | 17,468.44 | 252.21 | −17,216.22 |
| `selection_gbp` | 270.21 | 4,327.01 | +4,056.81 |
| `level_share_of_advantage` | 0.9848 | 0.0551 | the 17.9× |

450.11 − 17,666.33 = −17,216.22 exactly. **The control arm carries 97.52% of the absolute
movement.** The control arm does not price: its net is a property of the BOOK alone, and no change
to arm code can reach it. So of the three movers the drawn item names — book, commit, arm code —
the one that did the work is the **book**, and it is attributable after all.

## 2. The level constant doubled and moved the level arm by a third of a percent

`level_gbp_per_mwh` went 20.0 → 41.0 (+105%). The level arm's net moved **+0.29%**. The level
constant is a passenger, not a driver — P3 confirmed, and more strongly than predicted.

## 3. The share's own seed noise is TEN TIMES the gap being attributed

`value_cycle_ab_s1_noise_floor_next12_20260917.json` — same world `39a192ce04c1eda8`, seed re-draw
only, **nothing else changed** — takes `level_share_of_advantage` from **0.0666 to 12.0735: a 181×
range**. The two published runs differ by 17.9×.

**The disagreement the item asks me to attribute is an order of magnitude smaller than the range the
share takes with no confounder at all.** No seed family is needed to explain a 17.9× gap in a
statistic whose own noise spans 181×.

## 4. The floor families split exactly by book — and the right-book family is locked out

| family | constant that reads it | book | n |
|---|---|---|---|
| `folded18_single_arm_20260917` | `NOISE_FLOOR_PATH` | **164** | 18 |
| `next12_20260917` | `AUC_FAMILY_FLOOR_PATH` | **154** | 12 |
| `20260909b` | `CURRENT_WORLD_NOISE_FLOOR_PATH` | **not recorded** | 9 |

The 09-08 run's book is 164; the 09-18 run's is 154. So **a family on the published figure's own
book already exists on disk** — `next12`. The page says "re-running the noise floor on the point
estimate's own run is owed work" while that family sits there.

It is locked out by its own constant block, which says: *"Its seeds' `selection_gbp` must not join
the error bar's family, and its spread must not become any figure's interval."* That prohibition was
written to stop a **fold** (18 → 21 draws) and to stop its spread becoming an interval. Neither
purpose covers reading it as a floor in its own right for a run on its own book. **The prohibition is
correct for what it was written about and over-broad for what the page now needs.** That is the one
actionable item here.

The third family, `20260909b`, records **no book at all** — the "field structurally unable to answer
agrees with every answer" shape. It cannot discharge a book pairing in either direction, and
`floor_tree_pairing.rule` is already `declared_unavailable`.

## 5. Why the item's re-run would not have settled it

`level_source` on both artefacts, verbatim: *"the value arm's own realised median margin in THIS run
(`decision_shape.median_margin_gbp_per_mwh`), not a constant"*. Confirmed: `decision_shape` reads
20.0 on the 09-08 run and 41.0 on the 09-18 run — the level arm's price level **is** that field.

**The level arm's price level is endogenous to the run.** Fixing commit, book and seed family does
not fix it: the level arm is re-levelled to whatever the value arm does in that run. This is a
FOURTH mover, and the drawn item names three (book, commit, arm code). A re-run built to the item's
specification would have produced a fourth number and no attribution.

## 6. The thesis leg points the other way, and all three families agree

> "The advantage must come from INFERENCE, never from ACCESS."

Its one measurable consequence is the selection leg. Every family on disk:

| family | book | n | mean `selection_gbp` | sd | t |
|---|---|---|---|---|---|
| `folded18` | 164 | 18 | **−959.78** | 1,631.80 | −2.50 |
| `next12` | 154 | 12 | **−1,069.48** | 5,398.31 | −0.69 |
| `20260909b` | — | 9 | **−1,078.17** | 1,810.50 | −1.79 |

Three families, two books, three commits — and the central estimate is negative every time, within
£119 of each other. On the present evidence **selection destroys about a thousand pounds a run**, and
the leg that would carry the thesis is the one pointing against it.

The 09-18 run's +£4,327 — the figure that makes selection look like 94% of the advantage — sits at
**z = +1.00 SD above its own book's family mean, and that mean is negative.** It is an ordinary
upward excursion from a negative family, not a contrary finding.

## 7. Both halves of the item's either/or are correctly refused, and here is the second one

The item asks the page to "state the selection leg's sign **or** say how many seeds it needs".

**The sign.** Already refused, correctly, with its reason named:
`sign_withheld_despite_clearing_the_bar_because` states the book mismatch (164 against 154–155) in
words. The page is more honest than the item's brief credits it.

**The seed count.** `seeds_needed_to_state_a_sign` is `null`, keyed to `clears_bar`, with the stated
reason that more seeds of the wrong book buy nothing. Also correct. But it leaves the question
unanswered, so I priced it on the **figure's own book** (`next12`) with the repo's own
`seeds_to_state_a_sign`:

| denominator | seeds required |
|---|---|
| mean − 1 sem (−£2,627.83) | **19** |
| mean (−£1,069.48) | **101** |
| mean + 1 sem (+£488.88) | **471** |

**101 seeds — and across one standard error of its own denominator, 19 to 471.** At +1 sem the mean
crosses zero, so past that the requirement is not large, it is **unbounded above**: the count is
`(t·s/|m|)²` and `m`'s sign is undetermined (t = −0.69).

**So the page cannot honestly answer the second half either, and the reason is not the one it
gives.** A finite seed price quoted here would be a point estimate of an unbounded quantity — the
`n/t²` shape. Fail-closed is a result, and this is the sentence the page is owed:

> We cannot state a sign, and we cannot tell you what it would cost to state one, because the
> quantity we would divide by has an undetermined sign.

That is publishable today and is strictly more than the page says now.

---

## What I predicted and what happened

| | prediction | outcome |
|---|---|---|
| P1 | control net rose 12–13%, level arm <1% | **CONFIRMED** (+12.61% / +0.29%) |
| P2 | level leg's collapse >90% the control arm | **CONFIRMED** (97.52%) |
| P3 | level constant a passenger | **CONFIRMED** (+105% → +0.29%) |
| P4 | level constant endogenous; re-run insufficient | **CONFIRMED** from `level_source` |
| P5 | no floor carries the 09-18 arms' commit `b329e702b7` | **CONFIRMED** |

P2's margin was the one I was least sure of and it came in above the band I named.

## What is owed, ranked

1. **Widen the `AUC_FAMILY_FLOOR_PATH` prohibition to name what it forbids** — the fold and the
   interval — so the family may be read as a floor for a run on its own book. `tools/generate_value_arms_data.py`
   was held by a live `surgical_land` from another lane for this whole turn, so I did not touch it.
2. **Publish the §7 sentence**, and a control keyed to the property: *a seed requirement may not be
   published when the estimate it divides by does not clear its own bar*, because the requirement is
   then unbounded above. No such control exists — `write_time_gate --explain` returned no covering row.
3. **Not** the re-run as specified. §5 is why. If one is run, the level arm must be levelled on a
   constant fixed across arms and runs, or the contrast is unattributable by construction.

## Note on the draw

The duplicate-work check named `the-belief-ceiling-names-no-world-and-the-grader-never-stamps-one`
as holding `tools/generate_value_arms_data.py`. It does — PID 31294, a live `surgical_land`, running
from before this turn began and still running at the end of it. Genuinely different work on the same
file, so I carried on, and confined myself to paths it does not hold.
