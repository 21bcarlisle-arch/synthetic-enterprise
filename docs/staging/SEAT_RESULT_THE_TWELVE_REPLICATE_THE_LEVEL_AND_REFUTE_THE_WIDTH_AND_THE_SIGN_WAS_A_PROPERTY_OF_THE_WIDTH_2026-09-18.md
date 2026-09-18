**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The twelve replicate the level and refute the width, and the published sign was a property of the width

**Filed:** 2026-09-18 · **Claim id:** `read-next12-alone-as-the-last-family-on-the-old-instrument-and-label-it-so`
**Pre-registration:** `docs/staging/records/PREREG_THE_NEXT12_FAMILY_IS_STAMPED_A_SALVAGE_COMMIT_AND_SHARES_AN_INSTRUMENT_WITH_THE_AUC_THREE_2026-09-17.md`
**Artefact:** `docs/observability/value_cycle_ab_s1_noise_floor_next12_20260917.json` (producer bytes
untouched; one `instrument_stamp` key appended on copy and marked `added_after_the_fact: true`).

The run settled at **11:07:45Z**, 24 minutes ahead of the corrected 11:31 estimate and 15 h 56 m
after it `exec`'d. Fourteen-plus hours of compute, and it is the **last family on the superseded
instrument**.

---

## The twelve, ALONE, pooled with nothing

| | value |
|---|---|
| n | 12 (seeds 3100001–3100012, disjoint from every other family) |
| mean `selection_gbp` | **−£1,069.48** |
| stdev | **£5,398.31** |
| sem | £1,558.36 |
| sems from zero | **0.69** (bar is 2.0) |
| `selection_distinguishable_from_zero` | **false** |
| `sign_if_it_were_stateable` | negative |
| seeds it would need at today's estimate | **102** |

Per seed: +5823.40, +489.22, −4179.11, −6411.38, +385.00, −565.86, −4699.55, −6354.40, −9809.82,
−293.58, +6946.59, +5835.80. Seven negative, five positive, range £16,756.

**The twelve state no sign.**

## The reading that matters: the LEVEL replicates, the WIDTH does not

Against the published single-arm eighteen (`NOISE_FLOOR_PATH`, mean −£959.78, sd £1,631.80,
sem £384.62, **NEGATIVE at 2.50 sems**):

| | published 18 | next12 | |
|---|---|---|---|
| mean | −959.78 | **−1,069.48** | gap £109.69 — **0.07** of next12's own sem, 0.29 of the eighteen's |
| stdev | 1,631.80 | **5,398.31** | **3.31×** |

The dispersion difference is not sampling noise: **F = 10.94 on df (11, 17), two-sided p = 2.3×10⁻⁵.**

Both estimate the same quantity — the redraw dispersion of `selection_gbp`, same world digest
`39a192ce04c1eda8`, same `redraw_key: elasticity`, same `redraw_scope.mode: all`, disjoint seeds.
Differing seed sets are not a confound for a *noise floor*; varying the seed is what the family
does, and the F-test prices exactly that sampling variability.

**So the twelve do not contradict the published number. They contradict the published width — and
the published sign rests entirely on the width.** −959.78 is NEGATIVE at sd 1,631.80 and is
nothing at all at sd 5,398.31. Separating level from amplitude before attributing is the only
reason this reads as one finding rather than two.

**The artefact's own rule fires, and it was written by the producer before any seed was readable:**

> *"If the spread is WIDER than the published `selection_gbp`, the level-vs-selection instrument
> cannot yet resolve the question being asked of it, and every reading built on it carries that
> caveat. That is a finding about the INSTRUMENT and not about the pricing arm — it is not a cue to
> re-run until a seed agrees (R12)."*

## The pre-registered decision rule fired, on its second clause

The rule, fixed before the seeds existed: *"if the next12 selection mean lands positive, **or** its
own sign is not negative, `NOISE_FLOOR_PATH` is the first thing to re-open."*

- **Clause one is clean.** The mean landed negative, and at the same level.
- **Clause two fired.** The family states *no* sign, so its own sign is not negative.

Stated plainly because the comfortable reading is available and wrong: "no sign" is not "negative",
and a rule written in advance does not get re-read once the answer is in. The re-open is owed and
was done.

**What the re-open concluded: `NOISE_FLOOR_PATH` does not move.** Not because the twelve are
unwelcome — because the only two moves available are both defects. Folding them in recreates the
pooling this constant exists to name (third instrument, 18 files over the value-arm paths).
Swapping to them is choosing between two instruments *by their answers*. What is owed is the
**one-variable run — these same twelve seeds at `4e7938f673`** — which is the only thing that
separates the instrument from the seed set. **Until it exists I cannot say which width is right,
and I am not going to say.** What did change: the constant's own comment now carries the contest.

## The instrument, and why the stamp had to be written

`producing_commit` is **`a178b56d6`** — exactly as predicted, `unavailable_because: null`,
`resolved_at` 2026-09-17T19:11:53Z against a predicted 19:11:48Z. Prediction 1 **holds**;
Finding 1 of the prereg stands and the reader is spared re-deriving it.

The instrument is **two arms over unequal priced populations**, and it is established in the code,
not in this artefact:

- At `a178b56d6`, `decide_margin`'s **value** arm FILTERS on both the lawful ceiling and the churn
  support bound (`lawful` → `allowed`) and **raises `MarginDecisionUnavailable` when `allowed` is
  empty** (`value_based_renewal.py:876`) — it can decline. The **level** arm applies the lawful
  ceiling as a **clamp** (`min(level, headroom)`) and never applies the support bound — it prices
  everything it reaches. `selection_gbp = value_advantage_gbp − level_advantage_gbp` differences
  two advantages earned over populations the arms do not share.
- The raise at :876 is **present at `a178b56d6` and absent at `b329e702b`**, the arm fix.
- The **departure-cost term is present** (`e1895d6c8` is an ancestor): £27.50 sourced single-fuel
  PCS commission for resi, a declared `0.0`-with-a-reason for SME/I&C.

**What the artefact cannot show, said on its face rather than in a footnote.** This producer writes
no per-arm priced/declined counts into a floor artefact. The 214-priced / 281-priced / 64-decline
figures on file are from the **three-arm runs over a 280-renewal book**; this floor's book is
**154 settled billing accounts**. They are different populations and reading one onto the other
would be this project's most expensive recurring shape. The stamp records the counts as `null` with
the reason attached.

## Prediction grades

| # | prediction | verdict |
|---|---|---|
| 1 | `producing_commit.commit` = `a178b56d6…`, `unavailable_because: null`, `resolved_at` ≈ 19:11:48Z | **HELD** (19:11:53Z, 5 s out) |
| 2 | carries `redraw_key`, `run_identity_fields`, `discrimination_auc`, `auc_unavailable_because` | **HELD** — all four present; `discrimination_auc` on all twelve seeds, `auc_scored_share_of_priced: 1.0` |
| 3 | 12 seed rows, `folded` absent/false, world digest `39a192ce04c1eda8` | **HELD** — 12 rows, no `folded` key, digest matches |
| 4 | no prediction of the mean, sem or sign | honoured — nothing above was written before the seeds were readable |

## The secondary fifteen, reported because it was pre-registered

Prereg rule 2: *"It is reported **whatever it says** — including when it disagrees with the twelve…
A fifteen computed and then not published because it was unflattering is the defect this section
exists to prevent."* All five identity rows hold — world digest, `redraw_key`, `redraw_scope.mode`,
disjoint seeds, and `git diff c9bd2eae7 a178b56d6` over the four value-arm paths is **empty**. So
it is eligible, and here it is:

**n = 15 · mean −£410.29 · sd £5,113.39 · sem £1,320.27 · 0.31 sems · NO SIGN.**

It rescues nothing and it is weaker than the twelve. It is **wired into nothing** and the primary
reading stands alone, which is what the drawn item asked for. The item's "pool them with nothing"
and the prereg's "report it whatever it says" are both honoured: nothing is pooled into a published
family, and nothing computed was suppressed.

*(auc3 alone, for the record: n=3, mean +£2,226.47, 1.24 sems, no sign.)*

## Interconnection — what landing this artefact made false, and why the repair is NOT in this commit

`AUC_FAMILY_FLOOR_PATH`'s comment in `tools/generate_value_arms_data.py` reads **"THE ONLY FAMILY
IN THIS REPOSITORY THAT CARRIES THE DISCRIMINATION AUC PER SEED."** The next12 artefact carries
`discrimination_auc` on all twelve of its seeds, so **that sentence is false as of this commit** —
a falsehood this work created rather than found. The sibling clause "twelve more seeds in flight"
is likewise now false.

**The repair is written and it could not be landed.** All three comment blocks were edited (the
narrowing to "on this page", the landed result kept beside the `HOW IT GETS REFUTED` prediction,
and the "in flight" clause), and `tools.promote_worktree_landing` **refused**:

```
DuplicateWork: another live claim holds paths this work would move:
  the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term
  already holds: tools/generate_value_arms_data.py
```

That claim was 102.5 minutes old — past the standing 100-minute threshold — and
`delivery_lane --sweep` **released 0**, so it is live, not stranded. Releasing another lane's live
claim is not this seat's to do, so this commit was **narrowed to the two uncontested paths** and
the publisher repair is owed. Recorded here rather than retried silently, because a landed artefact
whose partner comment repair vanished with a turn is exactly how the 26,731-for-20-days shape
happens.

**The repaired text is not lost** — it is `f690a6407` in this worktree's reflog, and it is
reproduced in full in the "Still owed" item 0 below.

## Why this is BLOCKING

`site/data/value_arms.json` publishes a **NEGATIVE** selection sign. A same-world, same-redraw-key
family on a third instrument now puts a 3.31× width disagreement against it at p = 2.3×10⁻⁵, and
the sign is a property of the width. The page states the sign with no indication that it is
contested. The constant's comment now carries the contest; **the rendered surface does not**, and
that is the gap — *a fact established in an artefact and unread by the surface that turns on it is
not published* is the finding this atom already paid for once.

## Still owed, in order

0. **FIRST, AND IT IS A LIVE FALSEHOOD: the three comment blocks in
   `tools/generate_value_arms_data.py`.** Land them the moment
   `the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term` releases
   `tools/generate_value_arms_data.py`. All three are content-only comment edits; `--content` from
   `f690a6407` lands them without reading the file, so a rival's in-place edits are not at risk.
   - `AUC_FAMILY_FLOOR_PATH`: **"THE ONLY FAMILY IN THIS REPOSITORY"** → **"THE ONLY FAMILY ON THIS
     PAGE"**, plus a block naming next12 as what falsified it and stating that the two are the same
     instrument (`git diff c9bd2eae7 a178b56d6` over the four value-arm paths is empty), so a
     15-seed AUC family is arithmetically available and is deliberately **not** taken.
   - `NOISE_FLOOR_PATH`, under `HOW IT GETS REFUTED`: the landed result kept **beside** the
     prediction, not edited into it — the figures above, which clause of the decision rule fired
     (the second), and why the constant does not move.
   - The `WHY IT IS A SECOND CONSTANT` clause: "twelve more seeds in flight" → what happened.

1. **The one-variable run: seeds 3100001–3100012 at `4e7938f673`.** The only thing that separates
   instrument from seed set. ~16 h at the observed rate. Nothing about which width is right can be
   settled without it, and no amount of further reading substitutes.
2. **Surface the contest on the page.** The sign is published bare. `error_bar` needs a field that
   says a same-world family on another instrument disagrees about the width — the `_floor_value_arm
   _pairing` shape, one level up: not "were these drawn by one arm" but "does another family in
   this world disagree about this family's dispersion".
3. **A post-fix floor family at `b329e702b`.** Every floor family on disk, including this one, is
   pre-arm-fix. The page's error bar is bounded by an instrument the company no longer runs.
