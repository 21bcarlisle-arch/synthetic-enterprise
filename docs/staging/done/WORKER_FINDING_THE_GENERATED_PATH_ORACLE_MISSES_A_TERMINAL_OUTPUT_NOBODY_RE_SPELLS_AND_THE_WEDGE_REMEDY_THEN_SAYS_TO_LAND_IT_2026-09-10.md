**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-selection-legs-remedy-is-a-lower-bound-until-the-two-floor-legs-run-on-this-book`) · **Class:** publish_gate_and_wedge

# FINDING — the generated-path oracle misses a terminal output nobody re-spells, and the wedge remedy then says to land it

Found while clearing the shared tree so the two floor legs' decomposition would have somewhere to
land. The tree was 9 commits behind `origin/main` and `advance_shared_tree` refused, correctly,
naming three paths. One of the three is a producer's output that the oracle behind the refusal's
own remedy does not know about — so the remedy told me to land it, and landing it would have
reverted another lane's fix.

---

## The instance

`background/origin_reconcile._split_generated` splits the modified blockers into a producer's output
and a lane's work, and it exists for exactly one reason, stated in its own docstring: on 2026-09-09
the path holding the tree was `site/data/value_arms.json`, and the remedy's advice to LAND it "would
have re-published the 'IN THE WORLD AS IT IS NOW' headline that origin's own commit `77d92e0d1` had
just been written to DELETE."

Asked about today's three blockers, it answers:

```
GENERATED: ['site/data/value_arms.json']
AUTHORED : ['site/data/knowledge_review.json',
            'site/test_the_baseline_comparison_reaches_the_reader.py']
```

`site/data/knowledge_review.json` is not a lane's work. Its sole writer is
`tools/generate_knowledge_review.py`, whose module docstring's first line is *"Publish which
Knowledge pages are due for review — `site/data/knowledge_review.json`"*, and whose `generate()`
does `out.write_text(...)` at :92. It is a publisher's exhaust, and the classification is wrong.

The consequence is `_landing_clause`'s, not the oracle's. An AUTHORED path gets:

> the N MODIFIED path(s) are this tree's uncommitted work and clear by LANDING or reverting them
> here — `python3 tools/isolate_hunks.py --survey <path>` … `surgical_land --content` lands your
> bytes without swapping the shared worktree

Following that on this path lands the local bytes over origin's, reverting
`SEAT_RESULT_SIX_PAGES_ADVERTISED_A_CHECK_THAT_COVERED_A_BODY_THE_READER_CANNOT_REACH_2026-09-09` —
**the same defect `_split_generated` was written to prevent, one file along.**

## The mechanism, and my first theory of it was wrong

`tools/file_scope_generated_paths.generated_artefacts()` AST-scans five trees for the tree segments
as *adjacent string constants inside one expression* (`GENERATED_TREES` holds `("site", "data")`).

My first reading was that the producer factors the tree through an intermediate constant —
`SITE = PROJECT / "site"`, then `OUT = SITE / "data" / "knowledge_review.json"` — so the `"site"`
segment is in a different assignment and the pair never joins. **That is refuted by the same file:**
`FEED = SITE / "data" / "knowledge_wholesale.json"` is factored identically at :44, and
`knowledge_wholesale.json` IS in the set. Factoring is not sufficient to hide a path.

What actually decides membership is whether **any** scanned module happens to spell the segments
adjacently, anywhere:

| path | spelled adjacently at | in the 178-member set |
|---|---|---|
| `site/data/knowledge_wholesale.json` | `tools/knowledge_layer_gate.py:80` (a CONSUMER) | yes |
| `site/data/value_arms.json` | `tools/generate_value_arms_data.py:286` (its producer) | yes |
| `site/data/knowledge_review.json` | nowhere | **no** |
| `site/data/knowledge_carbon_price.json` | nowhere | **no** |

So coverage is a coincidence of authoring style across the whole repository, not a property of
being generated. And the bias runs the wrong way: a path is safe if it has a consumer that
re-spells it, or a producer that does not factor. The paths left exposed are **terminal outputs
with a single writer that factors its tree constant** — which is the most likely shape for a
publisher's exhaust, i.e. precisely the class `_split_generated` exists to identify.

`knowledge_wholesale.json` being covered by a *consumer* is the tell. Nothing about that line was
written to make the oracle work; it is load-bearing by accident.

## Why this is LATENT and not BLOCKING

Today's instance is cleared (below) and no lane is currently being misrouted. It is not spent: the
`site/data/` tree is rewritten every publish cycle, so `knowledge_review.json` goes dirty again on
its own, and the next tree that wedges on it gets the same wrong remedy. The oracle is FAIL-CLOSED
by construction (it raises when it cannot compute), and `_split_generated` is deliberately
fail-soft — neither property helps here, because the oracle *answered*, confidently, and was wrong
about a member.

## The fix is a widening, so it is not done here

Resolving intermediate `Path` constants within a module before joining segments would find this
path. That widens a set a **commit gate** consumes (`file_scope` may not name a generated path,
with an eleven-entry `FROZEN` ratchet), so adding members can red atoms that are green today and
wedge every lane. That is a measurement — run the widened oracle, diff the set, see which
`file_scope` declarations newly fail — and it is not a thing to ship inside a bounded tick that is
also holding a 3.9-hour floor leg. **Filed rather than fixed, deliberately.** The next reader
should measure the diff first, not widen and land.

A cheap sufficient check, if the widening proves expensive: assert that every path passed to
`Path.write_text` under a `site/data/` expression in `tools/generate_*.py` is in the set. That is
one leg over the producers rather than a rewrite of the scanner.

## What was done to the tree, and why each path was safe

`advance_shared_tree` refused with *"3 of 7 blocking path(s) are NOT byte-identical to what origin
brings"*. Each was cleared with `_landing_clause`'s own generated-path command,
`git show HEAD:<path> > <path>`, only after its own proof that no uncommitted work was at stake:

* **`site/data/value_arms.json`** — generated, and the local bytes were built by the *stale* local
  generator: they lack `what_would_settle_the_sign` entirely, which origin's `eb0054acf` adds.
  Landing them reverts that block. Novel bytes, so a photograph of a run this tree had superseded.
* **`site/data/knowledge_review.json`** — generated (this finding's subject), same shape.
* **`site/test_the_baseline_comparison_reaches_the_reader.py`** — authored, and NOT work. Its
  working-tree bytes hash to `d83dc9d17`, which is byte-identical to commit `0c91d684a` — a commit
  **both** local `HEAD` and `origin/main` already contain, with 8 later commits to that path on
  origin. It was a checkout of superseded history sitting in the shared tree, and older than local
  `HEAD`'s own copy: its diff against `HEAD` *deletes* controls and reinstates
  `assert "DEFEND" in rendered`, the pinned-to-today's-answer assertion that `HEAD` had already
  replaced with one keyed to the property.

The four untracked blockers were confirmed byte-identical to origin's copies by
`git hash-object` against `git rev-parse origin/main:<path>`, then cleared by the mechanism itself.
Tree is now level with origin (`behind=0 ahead=0`) and the field the Lane 0 item's premise rests on
is back in the working tree.

## The second finding, which is about reading a tree at all

The Lane 0 item's premise is *"the page now states what would settle the selection sign — more than
44.90x this book … more than 2.82x for the centre of its own re-draw family"*. Acting on real disk
and git state, as instructed, that premise read as **withdrawn**:

* `what_would_settle_the_sign` appeared nowhere in the working tree's generator or feed;
* `git log -S` over the local branch found the commit that introduced it, `eb0054acf`, to be a
  **non-ancestor** of local `HEAD`;
* and the very next commit's subject is *"the selection leg has no sign to explain"* — which reads
  exactly like a deliberate retraction of a block about what would settle that sign.

Every one of those observations is true and the conclusion they compose is false. The premise is
live; it is live 9 commits away, on `origin/main`, which local `main` had not been able to
fast-forward to. **A tree that is behind origin does not merely lack work — it can present a live
claim as one the project has already thought better of, with a retraction-shaped commit subject
sitting in the log as corroboration.** The existing repeating alarm for this condition
(`WORKER_FINDING_REPEATING_ALARM_PUBLISH_REFUSED_ORIGIN_AHEAD…`) is about publishing being refused.
This is a different cost and worse: nothing refuses, and the reader concludes.

**The check that separates them is one command and it is cheap:** before treating a drawn premise
as spent, `git rev-list --count HEAD..origin/main`. If it is not zero, the premise has not been
read yet.

## What is next

1. The two floor legs, which is the item. `floor-only` at the nine seeds `11111–99999` on
   `value_cycle_ab_s1_three_arm_20260908.json` is running as
   `longjob-arms-rerun-20260908` (launched 01:14:33Z, ~3.9h, own cgroup verified), writing
   `docs/observability/value_cycle_ab_s1_noise_floor_only_20260908.json`. `floor-except` follows it —
   one at a time, because `floor_run_headroom_refusal` refuses a second concurrent leg at the ~6.4GB
   peak. Then `--decompose` those two against the existing nine-seed `all` leg
   (`value_cycle_ab_s1_noise_floor.json`, same world digest `39a192ce04c1eda8`, same nine seeds) on
   `--contrast selection_gbp`.
2. Measure the widened oracle's set diff against the `file_scope` gate before widening it.
