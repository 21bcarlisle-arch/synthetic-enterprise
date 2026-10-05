**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# The publish named the map on every cycle and wrote it on none, so it was refused for a file it never changed

Item: `the-publish-collides-only-on-what-it-changed`.

## Premise

The item's DONE line is already met. `a88fb2436` is the publisher's `site/data/dashboard.json`
commit, dated 2026-10-05 23:00, and it is on origin/main. It got there through the seat's hand
merge `556b24b4e`, not by the publisher landing unattended. The structural defect was still live, so
this item fixed it.

## What was measured

`sim-runner-log.md` shows three `behind_origin` refusals on 2026-10-05 whose collision named the
map. The clause names only the first colliding path in sorted order.

| UTC | Collisions | First path |
|---|---|---|
| 12:48 | 2 | `docs/design/maturity_map.yaml` |
| 14:53 | 7 | `docs/design/maturity_map.yaml` |
| 19:34 | 1 | `docs/design/maturity_map.yaml` (the only collision) |

The publisher has one writer of the map: the pre-gate `atom_status` fold. Its last
`Pre-gate fold: reconciled` line is dated **2026-07-16**. So the publisher wrote the map in none of
these cycles. `PUBLISH_EXTRA_RELATIVE` still names the map on every cycle, and the collision set
intersected origin's incoming paths with the whole pathspec.

## What landed

`_publish_surface_collisions` now intersects with `_paths_differing_from_head`, which is
`git diff HEAD` plus untracked files, failing closed on any git error. A named path whose working
copy equals HEAD adds nothing to the HEAD-plus-paths landing and can no longer refuse the publish.
A path this commit does change still refuses and is named. The commit message lists the controls;
the intersection mutation was run and turned them red.

## What it does not fix, and the next step

At 19:34 the shared tree held a lane's stale in-place draft of the map. See
`SEAT_FINDING_A_DELETION_ORIGIN_ALSO_MAKES_HELD_THE_FAST_FORWARD_AND_THE_PUBLISH_BEHIND_ORIGIN_2026-10-05.md`.
In that state the map **does** differ from HEAD, so the refusal still fires, and it should: the
pathspec stages the working copy, so publishing would sweep another lane's stale draft into the
publish commit.

The item suggested landing the map's bytes with `--content` against origin's tip. That is the wrong
remedy here, because those bytes are not the publisher's.

**Proposed next increment:** name `PUBLISH_EXTRA_RELATIVE` in the pathspec only on a cycle where
`merge_atom_status.merge()` folded something. Use one pathspec at both sites, which keeps
`test_the_refusal_and_the_landing_name_one_pathspec` true. This needs the fold's result carried from
the run step to `git_commit_push`. That makes it a separate change, not part of this one.
