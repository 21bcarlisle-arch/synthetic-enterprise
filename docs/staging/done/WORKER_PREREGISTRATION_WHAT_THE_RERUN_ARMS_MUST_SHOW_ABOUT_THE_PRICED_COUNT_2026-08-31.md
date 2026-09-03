**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question` · **Claim:** `the-value-arms-ab-runs-in-the-world-as-it-now-is`

*Drawn as Lane 0, the delivery seat's own decision; filed under `B_commercial` because that is the
lane the value-arm pricing measurement belongs to and the severity gate knows.*

# PREREGISTRATION — what the re-run value arms must show about the PRICED COUNT

**Filed:** 2026-08-31, **before** the run reported. `tools/run_value_cycle_ab.py --level-arm` was
launched detached at 04:11:51 BST (`systemd-run --user --unit=value-arms-ab-20260831`, out
`docs/observability/value_cycle_ab_s1_three_arm_20260831.json`) and this file was written while it
was still settling 2017 on the first of three arms. That ordering is the whole point: a prediction
filed after the answer is not a prediction.

The run takes hours and does not fit a bounded invocation. This is the increment that fits one.

---

## Why the priced count is the figure, and why it comes before the money

The published comparison (`site/data/value_arms.json`) was **re-rendered, not re-run**:
`generated_at` 2026-08-31T02:25:22Z against `run_generated_at` **2026-08-30T10:37:06Z**. Three
world changes have landed since that run — the departure-level anchor, C1a/C1b's standard-variable
product, and the switching-belief correction of last night. Every headline on that page is computed
in a world that no longer exists.

The page's own headline names its blocker, and it is a COUNT, not a sum: the arm priced **20**
renewals of **1,369** the world offered (`decisions.value_arm_priced`,
`decisions.renewals_the_world_offered`). The single largest exclusion was
`product_not_upliftable` at **662** (48.4% of everything offered) — drawn accounts whose
`tariff_type` was `None` because the world had no standard-variable product to set it to.

At n=20 the instrument cannot resolve its own effect, so no money figure from it is readable. The
count decides whether anything else on the page can be read at all.

### The two thresholds, re-derived rather than quoted

Shrinking a spread by a factor k needs k² times the decisions. From the published artefact:

* **Level-vs-selection leg.** `spread_to_point_estimate_ratio` = 1.4197 (£1,816 contrast against
  ±£2,578). n = 20 × 1.4197² = **40.3 ≈ 41 priced decisions.**
* **Headline leg.** £607 contrast against ±£990 → k = 1.631, n = 20 × 1.631² = **53.2 ≈ 53
  priced decisions.**

The doorbell that drew this work said ~27 for the headline leg. I get ~53 by the arithmetic above
and cannot reproduce ~27 from any figure in the artefact. R8: the doorbell carries no authority, so
**53 is the number I am predicting against** and the discrepancy is recorded here rather than
quietly reconciled. The ~41 the doorbell gave for the second leg reproduces exactly, which is why I
believe the method and not the first figure.

## The mechanism, traced in the code before the run answers

`simulation/run_phase2b.py:1197` is the repair, and it is **not** an assignment of `svt` to the
drawn book:

```python
tariff_type=c.get("tariff_type") or "fixed",
```

`or`, not `.get(..., "fixed")` — because `population_draw.to_customer_dict` renders the key
*present with value `None`*, so the default was never reached for 137 of 146 accounts. That is
where the 662 came from.

What the drawn book gets now is a **first term that is fixed**, with every boundary after it
decided by the household's own engagement roll (`simulation/renewals.py:151`). A resi fixed term
whose household does not roll an active renewal gets a **bounded SVT stint to its anniversary**,
then returns to fixed. SVT is a passive stint interleaved into a fixed schedule, **not an absorbing
state** — `renewals.py:141-145` records that making it absorbing was the first draft and the
published fixed share refuted it.

Two consequences that set the prediction, both checked in the code rather than assumed:

1. **SVT segments are quarterly** (`svt_product.build_svt_schedule`, one segment per cap period).
   An account-year on SVT produces ~4 schedule rows where a fixed year produced 1.
2. **SVT segments still reach `decide_renewal_rate`.** The call is at `run_phase2b.py:1439`; the
   `_indexed_tariff` gate is at **1489, below it**, and neither `continue` above (1414 churned,
   1422 unactivated successor) excludes them. So SVT segments are counted in
   `renewals_the_world_offered` and land in `product_not_upliftable` — with the value `svt` now,
   where it was `None` before.

`tools/svt_generated_share_check.py`, run 2026-08-31, confirms the product is live and assigned:
42.6%–78.5% of account-days on SVT across 2017–2025.

## The predictions

Numbered so each can be refuted separately. All against the value arm's funnel in
`value_cycle_ab_s1_three_arm_20260831.json`.

1. **`renewals_the_world_offered` RISES sharply from 1,369** — to roughly **2,000–2,900**. The
   quarterly fragmentation of SVT stints adds rows faster than the fixed terms they displace
   remove them. *Refuted if it falls, or if it lands under 1,800.*

2. **`product_not_upliftable` RISES in absolute count** from 662, and its composition flips from
   `None` to `svt`. Its *share* of renewals offered rises above 48.4%. *Refuted if the count
   falls.*

3. **`priced` RISES from 20, and clears both thresholds** — I predict **200–350**, an order of
   magnitude, not a marginal move. Reasoning: the 662 blocked rows represented roughly 662
   drawn account-years; at the measured ~45% fixed share of account-days those become ~300 fixed
   terms, less term-0 exclusions. *Refuted if priced lands below 53 — and if it lands below 41 the
   lever has not delivered readability on either leg.*

4. **The money figures move, and I will not be able to attribute the movement.** Three world
   changes landed between the published run and this one. Whatever the sign, single-variable
   attribution is unavailable. **I am recording in advance that an improvement is as suspect as a
   loss here**, so that a flattering result cannot later be read as a confirmation.

### What prediction 3 would mean if it holds

The blocker was never book *size*. It was one line where a present-but-`None` key ate a default,
and the fix multiplies the instrument's resolution without acquiring a single customer. If it
holds, "book depth is the constraint on the thesis" is refuted as the explanation for n=20.

### What it would mean if prediction 3 fails

If priced stays near 20 while the SVT share is 40–78%, then the drawn book's fixed terms are not
reaching the arm for some *other* reason the funnel's stage breakdown will name — and the funnel
already has a gap that would hide it: `product_not_upliftable.means` instructs the reader to
"READ THE PER-VALUE BREAKDOWN BESIDE THIS COUNT" and **no such breakdown is emitted**. The stage
dict carries `stage`, `count`, `share_of_renewals_offered` and `means` only. With `None` and `svt`
now both landing in that one bucket, the prose points at the exact discriminator the artefact does
not publish. That is owed work either way, and it is cheap.

---

## C3 — the blocker re-stated, with the pointer landed

C3 ("the price the household is shown") remains **NOT LANDED**, blocked on this same run. What is
specifically still missing is the run above, and nothing else that I can find.

The arm itself is not lost and is not in a `/tmp` worktree. It is **two source files and a test**,
reachable from the salvage tag — the tag, never the branch, because the orphan reaper's enforce
mode deletes the name:

```
git diff 915bfab9b salvage/c3-shown-price-measure -- \
    simulation/shown_price.py simulation/customer_events.py tests/simulation/test_shown_price.py
```

`salvage/c3-shown-price-measure` = `f93fd1ea9`. Verified 2026-08-31: `simulation/shown_price.py`
(+122), `simulation/customer_events.py` (+60/-6), `tests/simulation/test_shown_price.py` (+162).

C3's exit needs its sign bounded **across price positions**, which needs a resolvable instrument,
which is prediction 3. If prediction 3 holds, C3 is unblocked by the same run. If it fails, C3's
blocker is not the run — it is the priced count, and that is a different piece of work.

## What is owed after this file

* Read `value_cycle_ab_s1_three_arm_20260831.json` when the unit exits; score predictions 1–4
  **beside** these words, not in place of them.
* The noise floor is measured on the run of 2026-08-29T17:04:23Z and bounds a point estimate from
  2026-08-30T10:37:06Z — the page says so itself (`error_bar.staleness_caveat`) and
  `point_estimate_inside_the_measured_band` is already `false`. A re-run point estimate against a
  twice-stale floor is not a confidence interval. The floor is owed a re-run too, and until it has
  one the new headline carries no bound.
* Emit the per-value breakdown under `product_not_upliftable`, now that two different values with
  opposite meanings share the bucket.

---

# SCORED — 2026-08-31, against `value_cycle_ab_s1_three_arm_20260831.json`

*Written beside the predictions above, not in place of them. The run finished 03:47:57Z,
`producing_commit` `fe4df178b`, which has all three world changes as ancestors (checked, not
assumed: `067a00dfd` SVT product, `56718a719`/`71242c941` departure level, `ae12a334e` switching
correction).*

**THE PRICED COUNT FIRST, because it is what decides whether any money figure is readable.**

| | before (2026-08-30) | after (2026-08-31) |
|---|---|---|
| renewals the world offered | 1,369 | **1,953** |
| priced by the value arm | 20 | **120** |
| accounts the arm priced | 10 | **65** |
| of those, drawn households (`SYN-`) | 0 | **25** |
| accounts the company *won* rather than started with | 0 | **58** |

## The predictions, each scored separately

1. **HOLDS.** Offered rose 1,369 → 1,953, inside the predicted 2,000–2,900 band only just below
   its floor — 1,953 against a "refuted if under 1,800" line. It cleared the refutation condition
   and undershot the band by 47. Recorded as a hold on the stated test and a near-miss on the
   stated range; the mechanism (quarterly SVT fragmentation adding rows) is the right one.

2. **HOLDS on both stated legs.** `product_not_upliftable` rose 662 → 1,223 in absolute count and
   48.4% → 62.6% in share. **The composition flip from `None` to `svt` is STILL NOT CHECKABLE** —
   the per-value breakdown the prose points at is still not emitted. That was named as owed work
   before the run and it remains owed; it is not evidence either way and is not counted as a hold.

3. **THE BAND IS REFUTED. THE CONSEQUENCE HOLDS.** I predicted **200–350** and said "refuted if
   priced lands below 53". Actual: **120**. Both statements were in the same prediction and they
   disagree about this result, so both are reported: the *magnitude* was over-predicted by roughly
   a factor of two, and the *readability threshold* — the thing the prediction existed to decide —
   was cleared, 120 against 53 and against 41. My reasoning (662 blocked rows → ~300 fixed terms)
   over-counted; the SVT stints are quarterly and most of the new rows land back in
   `product_not_upliftable` as `svt` rather than becoming priceable fixed terms. **"Book depth is
   the constraint on the thesis" is refuted as the explanation for n=20.** The blocker was one
   line where a present-but-`None` key ate a default, and no customer was acquired to fix it.

4. **HOLDS, and it is recorded as unattributable.** Realised net margin delta, value arm over
   control: **+£12,071**. Enterprise value £140,443 against £130,676. **I cannot attribute this.**
   Three world changes landed between the two runs and single-variable attribution is not
   available. It moved in our favour, which is exactly the direction I pre-committed to treating
   as suspect, and I am treating it that way: this is not evidence the pricing arm is worth
   £12,071, and the page does not state a direction for it (see below).

## What I did not predict, and it is the strongest result here

`belief_vs_outcome.discrimination_auc` moved **0.13 → 0.655** and the who-priced verdict moved
**`structural` → `reached`**. The page's standing claim — "the method has NEVER priced a customer
the company won… there is no book size at which the first one is priced" — **is now false**, and
the arm has priced 58 such accounts. No prediction was filed on either, so neither is scored; both
are recorded because they are the deepest confirmation the lever worked.

## C3 — the blocker RE-STATED, not discharged

C3's exit needs its sign bounded **across price positions**. The A/B run it was blocked on has now
happened and the instrument is resolvable at n=120, so **that blocker is discharged**. It is
replaced by a specific, smaller one: **every bound on this page was measured on the 20-decision
book of 2026-08-29 and none of them bounds this run.** No sign can be stated across price positions
against a floor from a different book. The floor re-run is launched
(`systemd-run --user --unit=value-arms-floor-20260831`, three legs, `all`/`only`/`except` against
`value_cycle_ab_s1_three_arm.json`); C3 is landable when it lands and not before. The arm itself
remains two source files and a test at salvage tag `salvage/c3-shown-price-measure` (`f93fd1ea9`)
against `915bfab9b` — the tag, never the branch.

## What promoting the run exposed, and what was repaired here

Publishing this run put a second book on the page and three separate controls could not see it:

* **The remedy paragraph** priced "about 27 priced renewals against this book's 20" and said "all
  10 accounts the arm priced are the founding roster… The lever is a PRODUCT, not a size" — off a
  floor decomposition measured before the product shipped, while `decisions` on the same page read
  120. The decomposition carries **no timestamp and no producing commit**, so nothing could notice.
  Now reconciled on the two counts the artefact does publish, and refused when they disagree.
* **Every directional claim** was gated on a spread from 2026-08-29. "£12,071 MORE than flat rules,
  clearing the ±£990" named a winner against a bound earned on the smaller book — fail-open in the
  flattering direction, since a staler and smaller bound makes every contrast look more decisive.
  `error_bar.staleness_caveat` had been saying so in words on the same page while the gate went on
  using the number. The bounds are now withheld when the floor predates the run.
* **The refusal that replaced it named the wrong cause** — "no seed spread has been measured" when
  one had been, on another book. That is a refusal citing a cause nobody observed; it now repeats
  the real reason.

Eleven controls were keyed to the 2026-08-29 run's answers rather than to their properties and
went red because the world improved. Re-keyed, not deleted: run-specific claims now cite that run's
own dated artefact, and `AUC_RUN_HISTORY`'s 2026-08-29 entry stopped citing the canonical path that
every new run is promoted to.
