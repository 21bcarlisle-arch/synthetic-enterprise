**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the-page-carries-two-floors-and-the-newer-one-is-the-wrong-one) · **Class:** uncommitted_and_orphaned_work

# `--drops` and `refresh_to_head` disagree about the same bytes, and the gap points at a revert

## The instance

`bec6071f7` landed a deliberate deletion with `--content` plus `--drops`, and `surgical_land`
recorded it: *"symbol/landing loss DECLARED by --drops for: site/capabilities/index.html, ..."*.

`--content` does not touch the working tree. So the moment that commit succeeded, the shared
working tree held copies of `site/capabilities/index.html` and `tools/generate_value_arms_data.py`
that HEAD had just superseded — the Kind-A conversion
[[feedback_surgical_land_converts_a_kind_b_copy_into_a_kind_a_one_at_the_moment_it_succeeds]]
describes. The sanctioned repair is `tools/refresh_to_head`. **It refused both paths:**

```
[refresh-to-head] ❌ 2 of 2 path(s) REFUSED -- nothing written.
  site/capabilities/index.html  [refused_supplies_names_head_lacks]
      this copy SUPPLIES 5 name(s) HEAD does not have, so it is not a copy HEAD supersedes --
      it is holder work.  ... + carriedByTheArm + cross + figure + pairStrataBlock + strata
```

`--write --slug` refuses identically; the survey is the gate, not a warning.

## Why the refusal is wrong here, and why it cannot know

The refusal's premise is a symbol-set comparison: a copy supplying names HEAD lacks is holder work
and must be landed, never overwritten. That premise is sound and it is the reason the standing
"never `git checkout <path>`" rule exists.

But it is exactly false for a copy **this lane deliberately dropped one commit ago**. The names it
"supplies" are the names the previous commit removed on purpose, with the removal declared, gated
and printed. `--drops` records that declaration **in the commit**; `refresh_to_head` reads only
HEAD's symbol table and the file on disk. Neither can see the other, so the two halves of one
mechanism give opposite answers about the same bytes:

| | says |
|---|---|
| `surgical_land --drops` | this deletion is deliberate, here is the receipt |
| `refresh_to_head` | this copy is holder work, land it over HEAD |

## Why it is not cosmetic

The working copy is what a pathspec stages
([[feedback_a_pathspec_stages_the_working_tree_copy_so_it_carries_another_lanes_uncommitted_edits_to_that_file]]).
Left in place, the **next** commit from any lane naming either path silently reverts the withdrawal
— restoring a `_skill_pair_strata` that collides with origin's and a renderer that prints
"no comparable pair" for a stratum holding 4,588 of them. The tool that exists to prevent exactly
that refuses, and its stated alternative (`isolate_hunks` — land those hunks over HEAD) is the
revert.

I also regenerated `site/data/value_arms.json` **once from those stale copies before noticing**, and
the output was silently built by the pre-merge generator. Nothing said so; the file simply appeared,
correct-looking and wrong. That is the sharp end of this.

## What I did, and why it was safe here rather than in general

Proved the copies carry nothing outside a commit before touching them:

```
git diff 98a9a090c --stat -- site/capabilities/index.html tools/generate_value_arms_data.py   # EMPTY
```

Empty means these bytes are `98a9a090c` exactly — this lane's own withdrawn work, in the history,
recoverable by sha. Only then `git restore --source=HEAD --worktree -- <the two paths>`. The
standing rule guards the shared tree against destroying another lane's LIVE edits; there were none,
and the proof is the diff above rather than my belief about who touched what.

## What is next

`refresh_to_head` should accept a copy whose only excess names are ones a **reachable ancestor
commit declared via `--drops`** — the receipt is already in the commit and is machine-readable.
Failing that, its refusal should at least name `--drops` as the discriminator, because the refusal
as worded sends the reader to `isolate_hunks`, and on this class `isolate_hunks` lands the revert.
The one-leg version is cheaper than either: refuse, but print the last commit that declared a drop
on this path.
