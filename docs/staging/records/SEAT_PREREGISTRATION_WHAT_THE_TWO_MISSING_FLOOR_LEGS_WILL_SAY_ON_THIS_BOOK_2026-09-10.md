# PRE-REGISTRATION — what the `only` and `except` floor legs will say on this book

**Severity:** RECORDED
**Lane:** G_data_learning
**Filed:** 2026-09-10
**Claim:** `the-selection-legs-remedy-is-a-lower-bound-until-the-two-floor-legs-run-on-this-book`
**Supersedes nothing; it is the sequel to**
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_A_LOWER_BOUND_ON_THE_SELECTION_REMEDY_MUST_SHOW_2026-09-09.md`

---

## What is being measured, and why the answer is not already known

`site/data/value_arms.json → current_world.selection_leg.what_would_settle_the_sign` publishes two
multipliers — **44.90×** this book to give the published draw (£270.21) a direction, **2.82×** to
give the centre of its own nine-seed re-draw family (−£1,078.17) one. Both were computed at the
corner `V_rest = 0`: *none* of the selection floor's variance is the rest of the book's churn
cascade. That corner was not measured. It was taken because it is the corner at which the
requirement is smallest, and the requirement is strictly increasing in `V_rest`
(`f(x) = (V−x)/(c²−x)`, `f'(x) = (V−c²)/(c²−x)² > 0`), so both figures are **lower bounds**.

This run measures `V_rest` on this book, at the same nine seeds, by running the two legs that
partition the `all` leg's call stream:

* `--redraw-mode only` — re-draw the elasticity of the households the value arm priced;
* `--redraw-mode except` — re-draw everybody else.

`V_only + V_except ≈ V_all` is the control that says they are two halves of one thing rather than
two unrelated runs, and it is published whether it flatters or not.

## The three numbers everything below is a threshold on

Read off `docs/observability/value_cycle_ab_s1_noise_floor.json` (9 seeds 11111–99999, mode `all`,
world `39a192ce04c1eda8`) and `docs/observability/value_cycle_ab_s1_three_arm_20260908.json` (214
priced decisions of 2,035 renewals offered):

| quantity | value |
|---|---|
| `V` — undecomposed `selection_gbp` variance, 9 seeds | **3,277,913 GBP²** (sd £1,810.50) |
| `c_published²` — the published draw, squared | **73,012 GBP²** = **2.227 %** of `V` |
| `c_mean²` — the nine-seed mean, squared | **1,162,441 GBP²** = **35.463 %** of `V` |

The page's own resolution rule is `|c| > sd`, and the irreducible floor is the `except` leg's own
sd. So the whole verdict turns on one comparison, stated here before it is made:

> **A contrast is unresolvable at ANY book size exactly when `V_rest > c²`.**

Which converts the two percentages above into the only two lines that matter:

* if the rest of the book carries **more than 2.227 %** of the two legs' total variance, **no book
  of this shape can ever give the published draw £270.21 a sign** — the "no book can" finding;
* if it carries **more than 35.463 %**, the same is true of the nine-seed mean, and the page's
  remedy block collapses to a single verdict instead of two multipliers.

## What I predict, BEFORE the legs run

| # | Prediction | Refuted by |
|---|---|---|
| P1 | The reconciliation `(V_only+V_except)/V_all` lands in **0.6–1.6** | a ratio outside that band (outside 0.3–3.0 would additionally mean the legs are not two halves of one thing and nothing below is readable) |
| P2 | The priced half **dominates**: `priced_share_of_variance > 0.50` | a share at or below 0.50 |
| P3 | `V_rest > 0` **strictly**, and `V_rest` exceeds **2.227 %** of the two legs' total — so **the published draw is unresolvable at any book size** and `larger_settled_book_would_resolve_it` is `false` for `c = £270.21` | `V_rest` under 2.227 % of the total, which would leave the published draw resolvable at some finite multiplier above 44.90× |
| P4 | `V_rest` stays **under 35.463 %** of the total, so the nine-seed mean **remains** resolvable, at a multiplier strictly above 2.82× and **below 10×** | a share above 35.463 % (mean also unresolvable), or a measured multiplier ≥ 10× |
| P5 | `share_is_decisive` is **true** against the published draw's threshold and I am **not confident** it is true against the mean's | either boolean the other way — P5 is registered as the one I expect to be least reliable |
| P6 | **Instrument control.** The nine `except` seeds are **not all identical**. On the previous book (roster 67, 2026-09-03) the `except` leg returned `selection_gbp = £2,176.70` for all three seeds — variance exactly zero — because it re-drew 5 accounts and 15 of 350 calls. This book's priced roster is 100 accounts of the 165 the world offered a renewal to, so the `except` side is an order of magnitude larger. **If it still returns nine identical values, that is a finding about the instrument, not about the world, and P3/P4 must not be read off it.** | nine identical `selection_gbp` values, or `elasticity_redrawn` under ~5 % of `elasticity_draws` |

**P3 is the interesting one and the one I would most like to be wrong about**, because it is the
only outcome that lets the page state a verdict rather than a price. Note it is *not* a free bet:
2.227 % is a very low bar for the rest of a book to clear, which is exactly why the `V_rest = 0`
corner was never a plausible description of the world and only ever a defensible bound.

## What this run does NOT settle, and the page must keep saying so

* **Reachability.** `settled_book_ceiling(years=1)` is customers × one year; this book's accounts
  are counted over ten. Their ratio is not a quantity (P3 of the 2026-09-09 prereg, refuted there
  and still refuted). No verdict on whether any stated multiplier is *buildable* follows from this
  run, and the block must go on saying so on the surface.
* **Whether growing the priced book is a lever at all.** Unre-measured on this book.
* **The contrast itself.** Both `c` values come from a three-arm run
  (`04361d6c7`, 2026-09-08) whose tree differs from the floor legs' tree (`c066c114b`) by ~2,000
  lines of `simulation/`. That is true of the *published* bound today and is not introduced here —
  it is filed separately as
  `SEAT_FINDING_THE_FLOOR_DECOMPOSITION_CHECKS_THE_WORLD_AND_NOT_THE_TREE_2026-09-10.md`.

## How the legs are run, so a later reader can tell whether they are comparable

Both legs run **at commit `c066c114b`** — the tree that produced the `all` leg they must partition —
in a locked worktree, one at a time (`floor_run_headroom_refusal` refuses a second concurrent leg,
and each peaks at ~6.4 GB against a ~24 GB guest). Roster read, never written down, from
`value_cycle_ab_s1_three_arm_20260908.json`'s own
`renewal_funnel.value_arm.accounts_the_arm_priced`. Artefacts land outside every worktree so a reap
cannot take them. **Running the two legs at HEAD would be the wrong measurement**: HEAD's
`company/pricing/value_based_renewal.py` is a different arm (`04a7e5a57` re-drew the choosing leg
with the objective changed), and its variance is not a component of the published bound's.

## Correction policy

Every refuted prediction is written into this file beside the prediction, and the page states what
was measured rather than what was predicted.

---

## RESULT

*Not yet run. This section is written after the legs land, beside the predictions above.*
