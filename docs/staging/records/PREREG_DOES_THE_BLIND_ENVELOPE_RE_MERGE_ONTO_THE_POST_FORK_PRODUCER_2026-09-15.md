# PREREG — does the blind envelope re-merge onto the post-fork producer?

**Written:** 2026-09-15, before any apply, any test run and any render.
**Subject:** re-merging the 5 remaining files of `04dcba655` (branch ref
`blind-envelope-landed-20260915`) onto `origin/main` at `760637dd7`, after the 41/35 fork closed.
**Claim:** `the-blind-envelope-re-merges-onto-the-merged-producer`

---

## What is already established, and is therefore NOT a prediction

Stated here so that nothing below can be read as a prediction that was really a lookup:

- `04dcba655` carries 9 files. **4 are already at HEAD and byte-identical** — both JSON inputs
  (`docs/design/blind_envelope_arms_2026-09-11.json`,
  `docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json`) and both staging documents.
  Checked by comparing `git rev-parse 04dcba655:<path>` against `git rev-parse HEAD:<path>` — same
  blob on all four. So the re-merge is 5 files, not 9.
- **`DEPARTURE_TERM_BASELINE_PATH` EXISTS at HEAD**, `tools/generate_value_arms_data.py:335`, with
  live callers at lines 1702, 1781, 9000 and 9676. At `33b78a519` it appeared in zero files, which
  is why the four controls grading it were dropped from `04dcba655` rather than resolved. **The fork
  merge brought it in.** The drop's stated reason — "the producer cannot answer them" — is spent.

## The predictions

**P1 — the apply conflicts, and every conflict is additive on both sides.**
Last time all six conflicts were unions. The drawn item says the fork merge has since rewritten the
same hunks, including a composer refusal keyed to the withdrawal register. I predict the 3-way apply
of `tools/generate_value_arms_data.py` conflicts again, and that **re-resolving as unions is correct
for every one** — i.e. no hunk requires choosing a side, because both sides only add.
*Refuted by:* any conflict where origin's side and the envelope's side write the same fact two ways,
so that keeping both publishes one quantity from two homes. That would be the VAT shape and the
union would be the wrong resolution.

**P2 — the four dropped controls now PASS, and I carry them in.**
Given `DEPARTURE_TERM_BASELINE_PATH` is live at HEAD, the four controls named in the entangled delta
(`test_the_runs_own_answer_to_which_side_of_zero_reaches_the_reader` and three others) should now
have a producer that can answer them. **Prediction: all four pass against the merged producer with
no edit to their bodies.**
*Refuted by:* any of the four going red, or needing its assertion changed to pass. If one reds, the
honest move is to carry it in red-and-named rather than tune it — a control edited until it agrees
is fitted to the conclusion.

**P3 — the envelope controls RUN rather than skip, and the door does not lose controls.**
At `04dcba655` the door was 144 passed / 1 skipped, up from 137/8, the 7 envelope controls having
gone from skipping to running. I predict against the merged producer: **the 7 envelope controls run
(not skip), and the passed count is ≥ 144** — the fork merge added controls, so I expect strictly
more than 144, but I am not predicting the exact number.
*Refuted by:* any envelope control still reporting the "this publish carries no available blind
envelope (None)" skip. That skip was the 106-hour defect; if it returns, the re-merge did not land
the feature, it landed the bytes.

**P4 — the rendered panel carries the same five verdicts.**
Gross margin 3.81% INSIDE, Revenue 5.82% INSIDE, Bad debt 36.82% ABOVE, Net margin 3.75% BELOW, Net
after cost to serve 4.56% BELOW. These are computed at publish time from an artefact that is
byte-identical at HEAD, so **the merged producer should reproduce all five unchanged.**
*Refuted by:* any verdict or percentage moving. If one moves, the fork merge changed an input the
envelope reads and the block's numbers were never a property of the artefact alone — that is a
finding, not a rounding difference to absorb.

## What "done" means for this claim

No exit test was written; this is direction. Done is all four of:

1. The 5 files are on `origin/main`, re-resolved, not replayed blind.
2. `site/data/value_arms.json` at HEAD renders a span and a position on all five lines.
3. The door runs the envelope controls rather than skipping them, and is green.
4. P1–P4 are each marked HELD or REFUTED **in this file**, beside the prediction, before release.

---

## RESULTS

Measured 2026-09-15 against `760637dd7`, in an isolated worktree.

### P1 — HELD, with one resolution that was neither a union nor a side-choice.

`git apply -3` of the 5 remaining files: `site/capabilities/index.html` applied **cleanly**; the
other four conflicted. Six conflicts in source, and **every one was additive on both sides**:

| File | Conflict | Resolution |
|---|---|---|
| `tools/generate_value_arms_data.py` | `build()` signature | union — `departure_baseline` **and** `blind_envelope_arms` |
| `tools/generate_value_arms_data.py` | `sources` list | union — both paths, plus the `blind_envelope` key |
| `tools/generate_value_arms_data.py` | `generate()` signature | union — both `*_path` parameters |
| `tools/generate_value_arms_data.py` | `generate()` → `build()` call | union — both `_read(...)` arguments |
| `tests/tools/test_generate_value_arms_data.py` | the `opened` citation list | union — seventh **and** eighth entry, both comments kept |
| `site/test_the_baseline_comparison_reaches_the_reader.py` | end-of-file append | union — both sections, ours then theirs |

No conflict wrote the same fact two ways, so the refutation condition never triggered.

**The exception worth naming.** `site/data/value_arms.json` conflicted in 6 places and was **not**
resolved at all — it is a GENERATED feed, and a generated companion resolved by hand is a derived
figure with two homes, which is the shape `_blind_envelope`'s own docstring exists to avoid. It was
rebuilt by running the resolved producer. That is the correct move and it is also why the six JSON
conflicts are not in the table above: they were never resolved, they were discarded and regenerated.

### P2 — REFUTED IN ITS PREMISE, held in its substance.

The prediction said "the four dropped controls now pass, **and I carry them in**". I carried nothing
in: **all four were already at HEAD**, on the *ours* side of the end-of-file conflict. The fork merge
brought the controls in along with `DEPARTURE_TERM_BASELINE_PATH`, not just the constant. Writing
"carry them in" assumed the fork merge landed the producer feature and left its controls behind —
that assumption was wrong and I had not checked it before predicting.

The substance held: against the merged producer,
`test_the_runs_own_answer_to_which_side_of_zero_reaches_the_reader`,
`test_MUTATION_the_two_rules_disagreeing_renders_LOUDLY_and_states_no_side` and
`test_MUTATION_a_baseline_that_is_not_the_pages_current_run_SAYS_SO` **pass**, and
`test_the_live_page_does_NOT_disclaim_a_baseline_that_IS_its_current_run` **skips for its stated
reason** — on this publish the pinned baseline is not the page's current run, so the disclaimer is
correct to render and the mutation test above owns that branch. No body was edited to make any of
them agree.

### P3 — HELD.

Door: **150 passed, 2 skipped.** ≥144 as predicted, and strictly more, as expected from the fork
merge adding controls. All **8** controls in the blind-envelope section RUN and PASS — the 106-hour
`"this publish carries no available blind envelope (None)"` skip does not appear anywhere in the
run. The two remaining skips are unrelated and both name their own reason (the error bar and point
estimate coming from one run; the disclaimer branch above).

Producer suite `tests/tools/test_generate_value_arms_data.py`: **204 passed.**

*One thing a re-checker needs.* The door's `_live_feed()` reads `git show :<path>` — the INDEX. Run
before staging the resolved files it gives 70 failed / 75 errors, which is the control failing
closed on a conflicted index, not a red. Stage first, then run.

### P4 — HELD, and the commit message's figures are SPAN WIDTHS, not distances.

All five reproduce exactly on the merged producer:

| Line | `span_pct` | stated | position | stated |
|---|---|---|---|---|
| Gross margin | 3.8056% | 3.81% | `inside` | INSIDE |
| Revenue | 5.8230% | 5.82% | `inside` | INSIDE |
| Bad debt | 36.8182% | 36.82% | `above_all` | ABOVE |
| Net margin | 3.7490% | 3.75% | `below_all` | BELOW |
| Net after cost to serve | 4.5627% | 4.56% | `below_all` | BELOW |

`blind_arm_count` 4, `first_hand_blind_arm_count` 3, `world_digest` `39a192ce04c1eda8`.

**Read the unit before reusing these numbers.** `04dcba655`'s message says "Gross margin 3.81%
INSIDE the span", which reads as a distance from the span. It is not: 3.81% is the WIDTH of the
blind span on that line, and gross margin's `distance_pct` is `null` precisely *because* the chosen
book is inside it — there is no nearest blind book to be a distance from. The two `inside` lines
carry a null distance and the three outside lines carry a real one (bad debt +23.34%, net margin
−3.01%, net after cost to serve −4.17%). Differencing a span width against a distance because both
are percentages on the same row is this repository's named shape, and the message's phrasing invites
exactly that.

## Verdict against "what done means"

1. ✅ 5 files re-resolved, not replayed blind — the `33b78a519` resolution was never applied.
2. ✅ The feed renders a span and a position on all five lines.
3. ✅ The door runs the envelope controls rather than skipping them, and is green.
4. ✅ P1–P4 marked above, P2's premise recorded as refuted rather than quietly dropped.
