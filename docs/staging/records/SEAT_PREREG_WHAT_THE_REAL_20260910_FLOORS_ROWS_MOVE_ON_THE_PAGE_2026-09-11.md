**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is a harness/provenance state, not domain understanding.

# Pre-registration: what the REAL nine-seed floor's rows move on the page, as opposed to the probe's

**Written BEFORE `generate_value_arms_data` was run against the new pair, and before
`site/data/value_arms.json` was rebuilt.** The floor artefact now exists, so the thing its
predecessor could not measure is measurable for the first time.

Filed against the Lane 0 item *"pair-move the 20260910 run and its floor"*
(claim `pair-move-20260910-after-the-floor-lands`).

---

## Why this document exists at all

The item's first pre-registration
(`SEAT_PREREG_WHAT_THE_20260910_PAIR_MOVE_CHANGES_AND_WHICH_PAIR_THE_BOUNDS_COME_FROM_2026-09-10.md`)
closes with a scope limit in its own words:

> **A≠C on numbers is NOT established.** `contrasts` came out byte-identical in A and C only because
> the probe reuses the 09-09 floor's seed rows. The real floor will carry different rows and
> different widths.

That is exactly the gap this document fills. **The provenance branches are settled and I am not
re-deriving them.** What is open is what the real rows do, and the honest place to write the
prediction down is before the generator runs — which is now.

## What I have already read, and therefore cannot pre-register

I read the floor artefact's raw fields before writing this, so **nothing below about the floor's own
summary counts as a prediction.** Stating them plainly so a later reader can tell the two apart:

| field | canonical floor on the page today (09-09b) | the new 09-10 floor |
|---|---|---|
| `selection_gbp_spread.mean` | −1078.17 | **−1749.47** |
| `selection_gbp_spread.stdev` | 1810.50 | 1840.39 |
| `selection_gbp_spread.min` / `.max` | −3036.25 / +1260.93 | **−3650.54 / +623.57** |
| `selection_sem_gbp` | 603.50 | 613.46 |
| `selection_distinguishable_from_zero` | `false` | **`true`** |
| seeds | 9, `11111…99999` | 9, `11111…99999` (same family) |
| `world_identity.digest` | `39a192ce04c1eda8` | `39a192ce04c1eda8` (same world) |

And the run half's point estimate, likewise already on disk and already read:
`level_vs_selection.selection_gbp = −332.64`, `level_share_of_advantage = 1.0198`.

**The floor's own selection leg has crossed from indistinguishable-from-zero to
distinguishable-and-negative.** That is a fact about the artefact. What it does to the *page* is
the open question.

## The predictions

Run `python3 -m tools.generate_value_arms_data` against the moved pair and read
`site/data/value_arms.json`.

1. **`contrast_bounds` stays a 7-key dict with `available: true` and `contrasts` of length 3.**
   The shape is provenance-driven and the previous pre-registration established it; the real rows
   should not change the shape, only the widths. Confidence: high. *Refuted by* any other key count
   or a refusal.
2. **`error_bar.staleness_caveat` stays `null`.** It is `null` on the live page today (column A) and
   the new floor is stamped *later* than the point estimate it bounds (23:03:18Z against
   14:04:08Z), which is the direction that keeps it clear. Confidence: high.
3. **Both `is_it_available_today` flags go `false` → `true`** (at
   `/method_skill/churn_auc_within_year/…` and `/decisions/discrimination_auc_within_year/…`).
   This is the item's stated purpose and column C measured it on the probe. Confidence: high.
4. **`floor_tree_pairing.same_tree` stays `False`**, with the hashes moving to floor `4e7938f67` /
   figure `9cf9d16ed`. Not a regression this move introduces. Confidence: high — this one is
   arithmetic over two commit ids, not really a prediction.
5. **The selection contrast's direction STILL cannot be stated.** The point estimate −332.64 sits
   inside the new floor's band [−3650.54, +623.57], as it sat inside the old one
   [−3036.25, +1260.93]. The band moved and the verdict did not. Confidence: high. *Refuted by* the
   page stating a direction for the selection leg.
6. **The `value_advantage_gbp` contrast's `mean_gbp` moves off 18321.31 and its `stdev_gbp` off
   2281.52.** Every contrast is recomputed from new rows, so a byte-identical `contrasts` block
   would mean the generator never read the new floor. Confidence: high, and this is the leg that
   catches a copy that silently did not take.
7. **THE ONE I AM ACTUALLY UNCERTAIN ABOUT: no published sentence changes its verdict because
   `selection_distinguishable_from_zero` flipped `false` → `true`.** I predict the page does not
   read that key at all, and gates instead on the spread-versus-figure rule quoted in
   `contrast_bounds.rule`. Confidence: **low — I have not grepped for the key.** *Refuted by* any
   rendered string or gate that moves with it.

   **This is the prediction worth having.** If it is refuted, the pair move publishes a *new
   directional claim about the selection leg* rather than merely restoring bounds — and that is a
   materially bigger change than the item describes, on a leg this project has already published
   wrongly once (`a553f2f96`). If it holds, the flip is a fact inside the artefact with no reader,
   which is its own finding and a smaller one.

## What I will NOT do

Re-run anything until a seed agrees (R12). The floor is the floor; if the band is wider than the
figure, that is a finding about the instrument and it gets published as one.

---

## RESULT, run 2026-09-11 — six of seven hold, and the seventh is refuted

Measured by `python3 -m tools.generate_value_arms_data` against the moved pair, diffing
`site/data/value_arms.json` against the copy taken before the move.

| # | prediction | verdict |
|---|---|---|
| 1 | `contrast_bounds` 7 keys, `available: true`, `contrasts` len 3 | **CONFIRMED** — 7 keys, 3 contrasts |
| 2 | `staleness_caveat` stays `null` | **CONFIRMED** |
| 3 | both `is_it_available_today` go `false` → `true` | **CONFIRMED**, both |
| 4 | `same_tree` stays `False`, hashes `4e7938f67`/`9cf9d16ed` | **CONFIRMED** |
| 5 | the selection leg's direction still cannot be stated | **CONFIRMED** — −332.64 inside [−3650.54, +623.57] |
| 6 | the contrasts' `mean_gbp`/`stdev_gbp` move off their old values | **CONFIRMED**, all three contrasts |
| 7 | **no published sentence changes because `distinguishable_from_zero` flipped** | **REFUTED** |

**Prediction 7 — REFUTED, and I said it was the one worth having.**
`tools/generate_value_arms_data.py:1287` reads the key straight into the payload as
`error_bar.distinguishable_from_zero`, which duly moved `false` → `true`. I predicted the page did
not read it at all and recorded the confidence as low because I had not grepped; the grep would
have cost one command and settled it before the prediction was written.

**What the refutation is NOT.** It is not the larger failure the prediction was insuring against.
The flipped key is published in the feed and rendered in no sentence — `grep -rn` over `site/`
returns the payload itself and one door test, and no HTML or JS. So the page gained no new
directional claim about the selection leg; prediction 5 holds and the leg is still withheld. **The
prediction's letter was wrong and its stated worry did not materialise, and those are two different
things.** Recording both, because a refutation narrated as "harmless anyway" is how a real one gets
talked past next time.

**And the door had already anticipated this exact flip.**
`site/test_the_baseline_comparison_reaches_the_reader.py:851` asserts
`isinstance(eb["distinguishable_from_zero"], bool)`, under a comment saying in as many words that
an unconditional pin to `is False` would be a control keyed to today's answer, and that a floor
re-run "can flip `distinguishable_from_zero` to True". It was written before the floor existed and
it survived the floor landing without an edit. **That is the rule working, from the one side that
is normally invisible.**

## Two things measured that were not predicted at all

1. **`floor_admission.rule` moved `stamp_proxy` → `declared_book`**, and `contrast_bounds.admitted_by`
   with it. The 09-10 floor is the **first floor on disk to carry a `book_identity` block**, so the
   page's bound stops being admitted by a date standing in for the question and starts being
   admitted on the book itself. This is a strict strengthening and nothing asked for it.
2. **The departure-term re-run block lost its premise** — see the finding filed alongside this
   document. Not a prediction I got wrong; a consequence I did not think to predict.
