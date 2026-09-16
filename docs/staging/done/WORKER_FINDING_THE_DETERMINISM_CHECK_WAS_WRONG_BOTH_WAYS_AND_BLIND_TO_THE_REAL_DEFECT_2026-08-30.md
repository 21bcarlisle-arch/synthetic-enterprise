# [FINDING] The determinism check was wrong in both directions, and the thing that actually blocked the promotion was invisible to it

**Severity:** RECORDED · **Lane:** H_harness · **Class:** `controls_that_cannot_fail`
**Born archived** — a new instance of a class that already holds 25.

## What was asked and what happened

The direction was: run `tools/run_arms_with_the_skill_funnel_20260830.sh --check` and obey it. An
empty diff promotes `value_cycle_ab_s1_three_arm_20260830.json`; a non-empty diff is a finding and
not a publish to force.

It printed `DETERMINISM FAILED -- the re-run is a different measurement`. Obeying it means not
promoting, and the artefact indeed must not be promoted. **Both of those are right and the reason
given for them is wrong.** The check was wrong in both directions at once, and the property that
actually disqualifies the artefact is one it cannot express.

## The first error: an allowlist of additions, which went stale in one night

The check stripped `generated_at`, `method_skill.drop_out` and `method_skill.dropped_sample`, then
compared the serialised JSON with `==`. Its own header states the premise: *"the change this run
carries is PURELY ADDITIVE to `method_skill`"*.

That premise was false by the time it ran. The re-run carried **nine** new keys from **four** lanes
that landed the same night:

| key | landed by |
|---|---|
| `method_skill.drop_out`, `method_skill.dropped_sample` | `158da2878` |
| `belief_vs_outcome.scored_decisions` | `82030bb58` |
| `renewal_funnel.{control,value,level}_arm.by_account_class` (+ `product_label_*`) | `cdbb1a772`, `ae96a5339` |

Seven of the nine were not in the strip list, so a correct run read as a changed measurement.

**A key that did not exist before has no old value to contradict.** An addition is therefore never a
change, and no allowlist is needed to say so. The replaced check needed to be *told the names of
things it had not been written to expect* — which means it goes red exactly when the tree is
busiest, and green only when nothing else is happening.

## The second error: exact equality on floats, so a reordering reads as a re-measurement

Two figures moved:

```
bound_attribution/realised_margin_movement/absolute_movement_gbp_elsewhere
    10359.439809000032 -> 10359.439809000027    (3 ULP)
bound_attribution/realised_margin_movement/net_delta_gbp_elsewhere
    -257.1865309999878 -> -257.18653099998653   (22 ULP)
```

Both are `*_elsewhere` aggregates summed over ~166 accounts. Their `*_on_those_accounts` siblings,
summed over **one** account, are bit-identical — as is every other figure in a 91 KB artefact. That
is the signature of summation **order**, not of different inputs: if the book had moved, the
one-account figures would have moved too and the bit-identity everywhere else would be a miracle.

The repair scales the tolerance in **ULPs, never in pounds**. "£0.01" is a different tolerance at
£10,000 than at £0.50, and the small figure is the one that needs protecting most. Ints and strings
get no tolerance at all: a count that moved, moved.

## The third thing, which no comparison of two artefacts could ever have found

The artefact is unpromotable, and not for either reason above. It is unpromotable because of **when
its process started**.

`docs/observability/arms_skill_funnel_20260830.log` records `START 2026-08-30T04:47:45Z`. Python
binds its modules at process start, so the run executed the working tree of that instant. Three
lanes' instrumentation was already in that tree. A fourth was not: `f9866cd2a`, which replaced a
`book_identity` resolved once at **artefact-assembly** time — reporting the second arm's book for
both arms — with a `book_at_run()` snapshot taken beside each arm.

Settled by **shape, not by timestamp arithmetic**: the artefact's `book_identity` carries
`control_arm` and `value_arm` only, with no `level_arm` block and no `same_book_across_arms` key.
That is exactly the pre-fix shape. And `book_identity.control_arm` reaches the live page as `book`
(`tools/generate_value_arms_data.py:1981`), so promoting it would publish a block measured by code
that a landed fix exists to correct, under a commit whose tree contains the newer labeller.

**The general form: a diff between two artefacts compares two outputs, and can say nothing about
the vintage of the code that wrote either one.** The artefact was byte-perfect against its
predecessor and still wrong. A control built only from artefact-to-artefact comparison is
structurally blind here, however carefully it is written — this is not a bug in the check, it is a
question outside its domain.

## The repair

`tools/artefact_rerun_diff.py`, with `tests/tools/test_artefact_rerun_diff.py` (17 tests). Both
`.sh` runners now `exec` it; the inline `strip()`/`==` is deleted rather than left beside the
correct one.

- Additions are their own reported category and never a change — no allowlist, so nothing to go
  stale.
- Float tolerance in ULPs (`MAX_ULPS = 64`), with a test that the bound **bites at its own edge**:
  `MAX_ULPS` steps passes, `MAX_ULPS + 1` is refused. A tolerance whose failing side is unreachable
  is not a tolerance.
- Ints exact; strings exact; bools never compared as numbers (`True == 1` in Python, and an
  `available` flag flipping is precisely what a reader acts on); NaN never reported as unchanged;
  list length checked before elements.
- `--check-shape` supplies the third clause, **keyed to what the runner emits** rather than to a
  literal, so it cannot go on certifying a shape the code has moved past.

Live verdict, which is the useful one:

```
SAME MEASUREMENT -- the re-run reproduces the published artefact.
STALE SHAPE -- the re-run's `book_identity` lacks ['same_book_across_arms'] ... Do NOT promote it.
```

## Disposition

Not promoted. `method_skill.drop_out` and `belief_vs_outcome.scored_decisions` stay honestly
fail-closed on the live page, each carrying its own reason, which is the behaviour we want.

A re-run against the post-fix tree was launched at `2026-08-30T09:50:08Z` as
`arms-skill-funnel-20260830b.service` (a transient unit of its own: a job started inside a bounded
tick is SIGTERMed with it). Its prediction was filed **before** launch, in
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_POST_FIX_BOOK_IDENTITY_RERUN_MUST_SHOW_2026-08-30.md`:
`book_identity` gains keys and changes no published value. **If `served_segments` or any published
count moves instead, the figure on the live page today is wrong, and that outranks publishing the
drop-out split.**

## The lesson, in one line

The check that guards a promotion was itself unguarded: it hard-coded what it expected to change,
compared floats for exact equality, and asked a question that could not reach the defect. All three
are the same mistake — **a control keyed to today's answer rather than to the property**.
