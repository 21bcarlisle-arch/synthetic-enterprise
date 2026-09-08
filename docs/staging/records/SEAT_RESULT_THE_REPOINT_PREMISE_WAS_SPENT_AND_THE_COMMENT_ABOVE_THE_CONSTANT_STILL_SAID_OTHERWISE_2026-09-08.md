# The re-point premise was spent, and the comment above the constant still said otherwise

*Lane 0 delivery, 2026-09-08. Drawn item: re-point `CURRENT_WORLD_THREE_ARM_PATH` and
`CURRENT_WORLD_NOISE_FLOOR_PATH` together once the undecomposed floor finishes.*

---

## The premise was spent before the draw

The drawn item asked for work that had already landed. Measured, not assumed:

| Check | Reading |
|---|---|
| Floor unit | `Result=success`, `ExecMainStatus=0`, `ActiveState=inactive` |
| Floor artefact | `/var/tmp/value_cycle_ab_current_book_floor_2026-09-08.json`, rc `0` |
| Copied to observability? | Yes — byte-identical to `docs/observability/value_cycle_ab_s1_noise_floor_20260908.json`, and TRACKED |
| Both constants re-pointed? | Yes, at HEAD **and** at `origin/main` |
| Which commit | `8e90037a5`, which moved **both** in one commit — the legal move |

The acceptance test the item really wanted, run in a clean `HEAD` extract rather than the shared
tree (a green in the shared tree measures several lanes):

```
three_arm generated_at: 2026-09-08T00:19:54Z   digest 39a192ce04c1eda8
floor     generated_at: 2026-09-08T04:10:26Z   digest 39a192ce04c1eda8
_staleness_caveat(floor, three_arm) -> None
```

Same world, bound stamped later than the figure it bounds, caveat withdrawn. **The page publishes a
bounded figure.** Nothing about the re-point remained to do.

## What was actually wrong, and is now fixed

`8e90037a5` added its new "MOVED ... TOGETHER" paragraph and did **not** delete the paragraph it
replaced. So HEAD and `origin/main` carried, directly above a constant pointing at `_20260908`:

> `#: DELIBERATELY STILL THE 09-03 RUN`

…followed eighteen lines later by a paragraph correctly saying it had moved. Two contradictory
present-tense claims about the same constant, with the false one first.

This is not cosmetic, and it is why this item was drawn at all. A reader — or the next scheduled
tick — arriving at that comment learns that the constant is deliberately un-moved and that the
unblocking floor "is running", and the cheapest correct-looking response is to re-run a floor that
finished hours ago and re-point a constant already pointed. **The stale comment is a work
generator.** It cost this turn's draw.

The fix keeps the history and removes the false tense. The reverted attempt — the 7.6x unbounded
republication, `GBP 2,335.87 -> 17,738.64` — is retained verbatim under *"WHY THIS WAS PINNED TO THE
09-03 RUN FOR A DAY"*, in the past tense, because a reverted attempt kept beside its result is the
only evidence the constraint was understood before the answer was known. The load-bearing rule
("moving either alone is the defect") survives in both constants' comments, and the resolving commit
`8e90037a5` is now named where the next reader will be standing.

Prose only: both constant values are byte-identical, and the change is 30 lines in one comment block.

## What was NOT adopted, and why

The shared working tree holds an uncommitted rewrite of this same comment block (part of a larger
356-line survivorship change, four files, belonging to another lane in flight). That rewrite was
**not** taken, for a reason worth recording:

- It states *"`CURRENT_WORLD_THREE_ARM_PATH` had already been moved to the 09-08 re-take; this
  constant had not."* `git show 8e90037a5` refutes this — both moved in that one commit. The prose
  describes a state that existed only before the commit it sits downstream of.
- It **deletes** the "moving either alone is the defect, in BOTH directions" rule from the
  three-arm constant, leaving the pairing invariant stated on only one side of the pair.

That lane's own work is untouched: this landed via `surgical_land --content` from a
`HEAD`-plus-this-hunk file built outside the repo, so the shared tree's dirty copy was never read
and never swapped. Their rewrite will conflict on this block when they land; the note above is what
they need to resolve it.

## What is next

Nothing on the re-point. The pair is whole, the bound is admitted, and the record beside it is now
consistent with the code. The open item in this neighbourhood is the other lane's survivorship work
— findings staged, code not at `HEAD`.
