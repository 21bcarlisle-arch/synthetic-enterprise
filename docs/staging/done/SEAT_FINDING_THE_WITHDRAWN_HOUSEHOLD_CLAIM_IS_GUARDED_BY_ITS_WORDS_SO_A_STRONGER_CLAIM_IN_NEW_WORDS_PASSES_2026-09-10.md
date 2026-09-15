# SEAT FINDING — the withdrawn household claim is guarded by its WORDS, so a stronger claim in new words passes every control

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, found while confirming the lane-0 value-arms withdrawal item)

**Class:** `controls_that_cannot_fail`

---

## The short version

`site/test_the_stratified_concordance_reaches_the_reader.py` protects the 2026-09-10 withdrawal of
the household reading of the concordance figure. Its negative assertion is a literal substring:

```python
HOUSEHOLD_CLAIM = "real information about who stays"
assert "the belief carried " + HOUSEHOLD_CLAIM not in live_decisions
```

I replaced the producer's un-earned sentence with a **stronger** household claim in different words
— *"the belief told us which individual households would leave and which would not"* — and the file
went **14 passed**. The guard forbids one sentence, not the claim that sentence makes.

## How the drawn item led here

The Lane-0 item asked me to land an uncommitted value-arms withdrawal repair. **It was already
landed**: `8c53c35e5` put all four named fields *and* their page readers at HEAD (`712a7fc4e`,
= `origin/main`). Evidence is in the section below. Confirming that meant reading
`_auc_reading`, which is where this seam is.

## The seam

`tools/generate_value_arms_data.py::_auc_reading` gates the strong sentence on `household_earned`
— the *stratified* figure clearing its null. That gating is correct and well-built. When it is not
earned, the branch publishes instead:

> "so on this population the belief separated those who stayed from those who left."

The withdrawal's own stated reason, in the same feed, is:

> `"who"` is a household claim and the stratified figure does not carry it.

So the replacement sentence is built from the same `who`-construction the withdrawal condemns, and
the guard is structurally unable to notice. The unit the statistic is actually computed over is a
**decision** (123 decisions on 100 accounts, 3,320 ordered pairs) — not a person — which is what
makes the `who` wording avoidable rather than merely infelicitous.

## What is NOT wrong here, and it matters

- The page does **not** currently mislead a reader. `BUT THE PAIRS BEHIND IT COMPARE ERAS, NOT
  HOUSEHOLDS` lands in the very next sentence. I read it before writing any of this.
- The control already carries
  `test_a_run_whose_belief_DOES_rank_within_the_year_keeps_its_household_reading` — a real
  reachability leg proving the gate does not refuse everything. That is the shape CLAUDE.md asks
  for, it is correct, and this finding does not question it.
- The severity is LATENT for exactly that reason. Nothing published is wrong today. What is wrong
  is that nothing would catch it becoming wrong.

## Evidence — the poison rounds, graded against the pre-registration

Pre-registered before any of it, in
`docs/staging/records/SEAT_PREREG_IS_THE_WITHDRAWN_HOUSEHOLD_CLAIM_GUARDED_BY_ITS_WORDS_OR_BY_ITS_PROPERTY_2026-09-10.md`.
Poison applied to the working tree only; producer restored from a pre-run copy and verified with
`md5sum -c` (`tools/generate_value_arms_data.py: OK`), tree confirmed clean by `git status` after.

| # | Prediction | Result | Held? |
|---|---|---|---|
| P2 | literal-string poison turns `test_the_withdrawal_reaches_the_rendered_page` RED | `1 failed, 13 passed` | **held** |
| P1 | paraphrase poison leaves the file GREEN | `14 passed` | **held** |
| P3 | collected count does not move | 14 in all three states | **held** |

P2 ran first on purpose: `green` under P1 means two opposite things unless the control is first shown
able to fire at all. Nothing was refuted, and that is the weaker result — I went looking for a seam
I already suspected and found it where I expected. Recorded as such.

## Why the fix is not in this commit

The honest remedy is coupled and touches a file I must not land into right now:

1. **Reword the un-earned branch** to name the unit the statistic uses — *"the belief scored the
   retained decisions above the departed ones"* — which drops the `who`-construction and is also
   more accurate than the current sentence.
2. **Re-key the guard to the property**, so a reword must be a deliberate two-file act rather than a
   silent upgrade.

Step 1 changes `decisions.auc_reading`, which requires regenerating `site/data/value_arms.json`. That
file is **uncommitted and dirty in the shared tree right now** — another lane is mid-regeneration of
it (`generated_at`, `publishing_tree_commit` → `8c53c35e5`, dashboard run identity). Landing into a
file another lane holds dirty wedges the shared tree's fast-forward.

Landing step 1's producer change *without* the feed would be worse: the door test
`site/test_the_baseline_comparison_reaches_the_reader.py` grades the **index** copy of the feed as of
`712a7fc4e`, so a producer saying one thing and a published feed saying another recreates — pointed
the other way — precisely the defect that commit was written to kill. Splitting a coupled change
across a wedged file is not a smaller increment, it is a broken one.

So this commit lands the evidence and names the remedy. That is the part that was finished.

## What is next

- Reword `_auc_reading`'s un-earned branch and regenerate `site/data/value_arms.json` **in one
  commit**, once the shared tree's copy is clean. Verify the rendered page moved, not just the feed.
- Re-key the `HOUSEHOLD_CLAIM` negative assertion to the property. A wordlist would be the same
  blindness in a longer form; the mechanism that can actually fail is a sentence the producer and the
  control must both name.

## The lane-0 item's own status — closed on the evidence

The drawn item's done-condition was *"a clean `git archive HEAD` extract carries all four fields and
`site/test_the_baseline_comparison_reaches_the_reader.py` is green against those extracted bytes."*

The first half holds — verified in a `git archive HEAD` extract:

| field | at HEAD |
|---|---|
| `withdrawn_claim.withdrawn_on` | `2026-09-10` |
| `decisions.discrimination_auc_within_year` | present, `auc` 0.444, `available: true` |
| `decisions.auc_reading` | reworded, carries `COMPARE ERAS` |
| `producing_commit.objective.clause` | present |

All four also have readers in `site/capabilities/index.html` at HEAD (lines ~1946–1957, ~2298,
~2323), and the producer builds all four.

**The second half is unsatisfiable as written, by construction.** Commit `712a7fc4e` made that door
test's subject the **index** copy (`git show :<path>`), deliberately and correctly — a `git archive`
extract has no index, so the test fails closed there with the path and git error named. Running it
where the index *is* HEAD (this worktree, clean tree) gives **137 passed, 1 skipped**. That is the
faithful reading of the condition, and it passes. The stated form of the condition was written
against the pre-`712a7fc4e` door and simply predates it; noting it here so the next lane to inherit
a `git archive`-phrased done-condition does not read a fail-closed refusal as a red.
