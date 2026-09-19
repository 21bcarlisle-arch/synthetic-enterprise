# The stale-copy census graded against a base the trunk had moved past, and named the revert as the remedy

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — H_harness control repair

**DISCHARGED 2026-09-15** by the commit carrying this line, which lands the surface repair and its
two controls together. The finding is not revised below; what the discharge adds is the mutation
run the finding called for, including one mutation that did not fire and what it turned out to be.

**Found:** 2026-09-15, on a scheduled tick drawn to re-merge the blind envelope onto the post-fork
producer. That work was already spent (see §"What the tick was drawn for"); the defect is what the
tick found on the way to establishing that.

## What is wrong

`tools/stale_copy_refusal.py` is the control that stops a pathspec commit reverting another lane's
landed work. Its census computes every verdict against `HEAD`:

```python
changed = [p for p in _git_text(root, "diff", "--name-only", "HEAD").splitlines() ...]
loss = judge(root, path, blob_at(root, "HEAD", path), work)
```

`HEAD` in a shared checkout is routinely **behind** `origin/main`. On the live tree this morning it
was **seven commits behind**, and had been for long enough that `background/tree_divergence.py`
was already breaching on it.

The module's own `gains_over` docstring says what that number decides:

> Empty here means the copy is a rival HEAD strictly supersedes and `tools/refresh_to_head.py` is
> the door; non-empty means it is holder work and `isolate_hunks` is.

So the base does not weaken the remedy. **It inverts it.** Against a behind base, `gains_over` asks
"which names does HEAD lack" and gets back **names the trunk already has** — so a copy the trunk
strictly supersedes comes back non-empty, reads as HOLDER WORK, and the door named for holder work
is `surgical_land --content`, which writes those bytes over the trunk.

## The instance, measured

`tools/generate_value_arms_data.py` in the shared root, `python3 -m tools.stale_copy_refusal
--census`, with `HEAD` at `0142fc891` and `origin/main` at `79f1bd9bc`:

```
  tools/generate_value_arms_data.py  [predates_landing]
      your copy contains NOT ONE of the 142 distinctive line(s) commit 2212d0eed added here,
      so it was taken before that landing and this commit reverts it:
        - distance_to_a_sign,
        - FLOOR_PARTITION_PROBE_PATH = (
        ...
      REMEDY: this copy supplies 5 name(s) HEAD lacks (BLIND_ENVELOPE_ARMS_PATH,
      _BLIND_ENVELOPE_MINIMUM_ARMS, _BLIND_POSITIONS...), so it is HOLDER WORK.
      `python3 -m tools.isolate_hunks --survey tools/generate_value_arms_data.py`, ...
      then `surgical_land --content tools/generate_value_arms_data.py=<file>`.
```

Both halves are on the page, three lines apart: *this copy reverts 142 lines* and *land this copy*.

All five names it called holder work were already on the trunk, put there by the envelope re-merge
at `78829dbf9`:

| name | occurrences at `origin/main` |
|---|---|
| `BLIND_ENVELOPE_ARMS_PATH` | 3 |
| `_BLIND_ENVELOPE_MINIMUM_ARMS` | 4 |
| `_BLIND_POSITIONS` | 1 |

And everything the `predates_landing` half said the copy reverts was also on the trunk —
`distance_to_a_sign` (3), `FLOOR_PARTITION_PROBE_PATH` (2), `rest_of_book_half_is_degenerate` (3).
Against the trunk the copy supplies **nothing**: the honest door was `refresh_to_head` all along.

The same working copy held **823 fewer lines** than `origin/main` across five files, and was armed
to revert both the fork close (`760637dd7`) and the envelope re-merge (`78829dbf9`) on the next
pathspec commit naming any of them.

## Why nothing caught it

`background/tree_divergence.py` **does** check its own base, and says so on its surface:

> BREACH: HEAD is 7 commit(s) behind origin/main (and 0 ahead), so this count is measured against a
> stale base

Two controls read one tree. One knows its base can be stale and states it; the other does not — and
the one that does not is **the one that writes the instruction**. `tree_divergence` reports a count;
`stale_copy_refusal` names a door and a command to type. The caveat was on the surface that could
afford to be wrong and absent from the surface that could not.

This is the catalogued shape *a control keyed to today's answer rather than to the property*, one
layer up: the verdict was keyed to "what does this checkout happen to have" rather than to "what
does the trunk have", and those two are the same only when nobody else has landed.

## The repair

`base_caveat()` in `tools/stale_copy_refusal.py`, printed **above** the findings, not appended after
them — a caveat below several hundred lines of census is a caveat nobody reads before acting on the
first entry. It reuses `background.tree_divergence._base_state` rather than re-cutting the question,
because a second opinion about the trunk inside this module would be the very
one-question-several-implementations shape the census exists to catch in everybody else.

**A stated reading, not a refusal, and that is deliberate.** This module is wired into the
pre-commit door. A refusal here would red every lane in the tree for a condition — a behind base —
that is the normal resting state of a shared checkout and that no single lane's commit caused. The
duty a wrong base creates is a duty to *say so where the remedy is read*.

Three branches, matching `_base_state`'s three answers: read, no-remote-base, and the refusal when
the ref exists and git will not answer. Collapsing "no trunk to be stale against" into "level with
the trunk" would be the same error one layer down.

### The mutation run

| mutation | result |
|---|---|
| caveat never fires (the pre-fix behaviour) | **RED** — `test_the_census_states_when_its_own_base_is_behind_the_trunk` |
| `no_remote_base` returns a caveat (fires on a repo with no trunk) | **RED** — same control, other leg |
| `no_remote_base` early return replaced by fall-through | **GREEN — and it is an EQUIVALENCE, not a missing test** |

The third is recorded rather than left to the reader, which is the rule. That dict carries no
`behind` key, so `.get("behind") or 0` is `0` and the next branch returns `""` regardless. The
branch is kept explicit because the two states genuinely differ, and a later reader adding a
`behind` key to the no-remote case would otherwise get the caveat on every archive checkout
silently. The behaviour is held both ways round by the mutations above.

The second control, `test_a_copy_the_trunk_supersedes_reads_as_holder_work_when_the_base_is_behind`,
**reproduces the inversion** rather than asserting about it: it builds a real repo where the trunk is
ahead, and shows `gains_over` returning `("freshly_landed_helper",)` against the behind base and
`()` against the trunk. If that first leg ever stops holding, the caveat is guarding nothing and the
control says so.

## What the tick was drawn for, and why there was nothing to deliver

The draw asked for the blind envelope (`04dcba655`) to be re-merged onto
`tools/generate_value_arms_data.py` after the origin fork closed. All three steps were already on
origin before the tick started:

* `760637dd7` — the fork closed.
* `78829dbf9` — the envelope re-merged; `site/test_the_baseline_comparison_reaches_the_reader.py`
  carries 152 controls against the envelope commit's 145, a superset by function name.
* `35aa7e8b1` — the entanglement finding discharged, including the draw's own NOTE about revisiting
  the departure-baseline exclusion. That NOTE's premise was false and the discharge says so: the
  fork merge brought `DEPARTURE_TERM_BASELINE_PATH` in *together with* its four controls.

One thing the re-merge did that the draw did **not** anticipate, and it was right to. The draw said
resolve all six conflicts as UNIONS, never picking a side. The merge did not union
`spread_to_point_estimate_ratio`: that key was **retired on 2026-09-10**, replaced by
`selection_leg.sign_is_stateable`, because the ratio divided a nine-seed standard deviation by a
one-run figure — the population mix the page was repaired to stop making. Unioning it would have
resurrected a quantity the page had withdrawn. *A union is the right default across additive
changes and the wrong one across a supersession, and the draw could not tell them apart from
outside.*

Disposition recorded via `delivery_lane --premise-spent`.

## What is next

1. **Done in this commit.** The five stale copies restored, the base advanced `0142fc891` →
   `79f1bd9bc` (0 ahead, so no commit was at risk), and `tree_divergence`'s stale-base BREACH gone.
   `tools/generate_value_arms_data.py` has dropped off the census entirely.
2. **Not this commit's subject, and still live.** `tree_divergence` names **four** more files
   holding an older committed version and armed to revert HEAD —
   `docs/design/orphan_baseline.json`, `docs/design/simplifications/A49_…yaml`,
   `docs/institutional/knowledge_map.md`. They belong to other lanes and may be in-flight; they are
   not stale-by-being-behind the way these five were, so the same losslessness proof does not carry
   over and they need their owners.
3. **Observed, unowned.** `tests/tools/test_generate_value_arms_data.py::test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes`
   fails in the shared root (net margin £147,886.78 vs £147,954.26) and **passes in a clean worktree
   at `origin/main`**. The cause is a dirty `site/data/dashboard.json` in the shared tree, not the
   trunk. Noting the harness trap that cost a cycle: a `git archive` extract cannot answer this at
   all — it has no `.git`, so a test that shells out to `git show HEAD:…` fails closed there and
   reads as a red. Use a worktree, not an archive, to ask a HEAD-reading control anything.
