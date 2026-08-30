**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE1_expert_doors`

# Preregistration — what the post-fix `book_identity` re-run must show

**Filed 2026-08-30, BEFORE the run was launched.** The run is
`value_cycle_ab_s1_three_arm_20260830b.json`. Its launch time is in
`docs/observability/arms_skill_funnel_20260830b.log`; this file's commit precedes it.

## Why there is a second run at all

`value_cycle_ab_s1_three_arm_20260830.json` (`generated_at 05:32:11Z`) cannot be promoted. Not
because its numbers moved — they did not — but because of **when its process started**.

The log records `START 2026-08-30T04:47:45Z`. Python binds its modules at process start, so that
run executed the working tree as it stood at 04:47:45Z. Three lanes' instrumentation was already
in that tree and appears in the artefact (`method_skill.drop_out`,
`belief_vs_outcome.scored_decisions`, `renewal_funnel.*.by_account_class`). A fourth was not:
`f9866cd2a`, which replaced a `book_identity` resolved at **artefact-assembly** time with a
`book_at_run()` snapshot taken beside each arm.

This is settled by shape, not by comparing a commit date to a run timestamp. The artefact's
`book_identity` carries `control_arm` and `value_arm` only — **no `level_arm` block and no
`same_book_across_arms` key** — which is precisely the pre-fix shape. `book_identity.control_arm`
reaches the live page as `book` (`tools/generate_value_arms_data.py:1981`), so promoting it would
publish a block measured by code that a landed fix exists to correct.

## The prediction

The fix's own claim is that asking `served_segments()` once, after both arms have run, reports the
**second** book for both of them. On a run where no curriculum edit happened between the arms, that
mistake is invisible — the two resolutions agree. So:

**PREDICTED (filed before the answer): the re-run's `book_identity` GAINS keys and CHANGES NO
PUBLISHED VALUE.** Specifically —

1. `book_identity` gains `level_arm` and `same_book_across_arms`. **Additive.**
2. `same_book_across_arms` resolves to agreement, **not** to the tri-state null. A null here would
   mean an arm recorded no book, which is a defect in the snapshot, not a finding about the books.
3. `book_identity.control_arm.served_segments` is **unchanged** at `["resi", "SME"]`, and every
   other count inside `control_arm` is unchanged. This is the leg that reaches the page.

**If 3 is refuted — if `served_segments` or any published count moves — the fix was not cosmetic on
this run, the figure currently on the live page is wrong, and that is a finding that outranks
publishing the drop-out split.** I do not expect it. I am writing it down because the only version
of this check worth anything is one whose refutation was described before it ran.

## What the comparison must NOT be allowed to conclude

The 08-29 → 08-30 comparison already produced one false verdict, and the repaired comparator
(`tools/artefact_rerun_diff.py`) must not repeat either half:

- **Additive instrumentation is not a re-measurement.** Nine keys were added and zero removed, and
  the old check called that "a different measurement" because its `strip()` named two of the nine.
- **A last-bit float move is not a re-measurement.** Two figures moved, by 3 and 22 ULPs, both of
  them `*_elsewhere` aggregates summed over ~166 accounts; their `*_on_those_accounts` siblings,
  summed over one account, are bit-identical, as is every other figure in a 91 KB artefact. That is
  summation order, and the tolerance must be scaled to the magnitude, never to what looks small in
  pounds.

The bar for promotion is therefore: **no removed key, no changed value outside an ULP-scale
tolerance, and a `book_identity` whose shape matches the code in the tree that will carry the
commit.** The third clause is the one no diff between two artefacts can supply, and it is the clause
that would have caught this.

---

## DISCHARGED 2026-08-30. All three predictions held; the promotion bar did not.

Measured against `value_cycle_ab_s1_three_arm_20260830.json` (`generated_at 05:32:11Z`) — the run
this one was ordered to replace — and not against the 08-29 run, which is a different question.

1. **HELD.** `book_identity` gained exactly `level_arm` and `same_book_across_arms`, and lost
   nothing. Additive, as predicted.
2. **HELD.** `same_book_across_arms.same_book` is `true` over all three arms;
   `arms_with_no_recorded_book` is empty and `distinct_books` holds one entry, `["resi", "SME"]`.
   Not the tri-state null.
3. **HELD.** `control_arm.served_segments` is unchanged at `["resi", "SME"]` and **no count inside
   `control_arm` moved** — not `billing_accounts_settled_in_window`, not the leg counts, not
   `accounts_at_end_of_window`. The only fields that appeared are the three the snapshot adds to
   say how it resolved (`served_segments_resolved_from`, `..._override_env`,
   `..._unavailable_because`).

So `f9866cd2a` is **confirmed cosmetic on this run**, which is what the fix's own claim predicted:
resolving `served_segments()` once after both arms is invisible on a run where no curriculum edit
happened between them. The refutation branch — *"if `served_segments` or any published count
moves, the figure currently on the live page is wrong"* — did not fire.

### The clause that was wrong, kept beside the ones that were right

> **the bar for promotion is therefore: no removed key, no changed value outside an ULP-scale
> tolerance, and a `book_identity` whose shape matches the code in the tree that will carry the
> commit.**

The third clause passes this artefact and should not have. This run started **09:50:08Z**;
`7e598a84b` landed **10:24:36Z**, moved `DEFAULT_SEGMENT_WEIGHTS` to `{resi: 1.00}` and took the
segment dial out of the draw. So its 167 accounts / 149 electricity / 113 at end were drawn by a
population the tree no longer generates — and because `f9866cd2a` was already in the tree at
09:50:08Z, the artefact's `book_identity` shape matches the tree **perfectly**. The bar I wrote
was satisfied by exactly the artefact it existed to catch.

The error is the same one, one field over, for the second stretch running: I guarded the field the
previous trap had named — first `book_identity`'s resolution point, then its shape — rather than
the property behind both, which is that **a run longer than the tree's landing cadence has two
trees, and only the producing process knows which one bound its code.** A shape check is a check
on the assembly tree; the question is about the draw tree; no diff between two artefacts can
answer it, because both sides of such a diff are outputs.

What replaces it is not a better bar, it is a stated fact: `run_value_cycle_ab.PRODUCING_COMMIT`
is resolved at **import**, so every artefact this runner writes carries the commit its code was
bound at, and `generate_value_arms_data` fails closed on a run that cannot state one. The counts
above are therefore withheld from the live page with their reason, and the first stamped run
promoted restores them with nobody editing a string. The classification the run was really wanted
for — 0 join, 4 coverage, 10 eligibility — does not depend on the population and is published.
