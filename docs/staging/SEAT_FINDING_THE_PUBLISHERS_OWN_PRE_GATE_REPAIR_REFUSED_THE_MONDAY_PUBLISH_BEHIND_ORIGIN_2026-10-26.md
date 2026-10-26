**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** none -- the publish machinery's own git behaviour; no domain claim

# The publisher's own pre-gate repair refused the Monday publish `behind_origin`

Found by the delivery seat on 26 Oct, while checking the one-shot `mondays-window-marker-20261026`.

**What the one-shot did.** At 04:05Z it wrote `run_complete_20261026T040501Z.md`. The marker was for
`run_output_4ae8da9b0f_20261026T022647Z`, NOT the `b2bc3d8da5_20261025T1230Z` the drawn item expected.
The script offers whatever run sits on `run_output_latest.json`, and an overnight run finished at
03:27Z and took that slot. That run is not a lesser one:

- `4ae8da9b0f` descends from `b2bc3d8da5` (81 commits later), so it carries the four billing fixes and
  the held-cash fix.
- It is the same full-scale shape: 52,791 bills against 53,194, with the same top-level keys.

So the item's goal is served by the newer run. Publishing `b2bc` over it would have put older code on
the site.

**What the publisher did.** The worker picked the marker up at 04:16, and at 05:14 the publish did not
land, with outcome `behind_origin`, rc=77. The chain:

1. At 04:37, `_repair_derived_artefacts_in` re-rendered `docs/design/BLOCKED_ATOM_VISIBILITY.md` and
   `_land_repaired_artefacts` landed it as `b681cc4d7` in the shared tree. Nothing pushed it.
2. Origin took one unrelated commit (`bf56dd579d`, PB8) during the 36-minute gate.
3. At 05:14, `_unabsorbed_publish_commits` counted `b681cc4d7` as a stranded earlier publish ("1
   commit(s) here ALREADY write this publish surface"). `_advance_to_origin_or_say_why` refused to
   fast-forward a tree that holds a commit of its own. The publish was refused before staging.

A full run and a green gate were refused by a projection commit the process made itself. The two
commits were disjoint: one design doc against PB8 code. Origin moves every few minutes, so any cycle in
which a pre-gate repair lands should expect this.

**Fix (this landing).** `_deliver_repair_landing` pushes `HEAD:main` straight after the repair lands.
It grades the push by the remote ref (`_push_reached_origin`), the same way as every other push in the
module.

- A lost race leaves the state that existed before. Git refuses a non-fast-forward push, and
  `origin_reconcile` already owns that state.
- The log now says when a `behind_origin` refusal this cycle is the repair commit and not the run.
- Tests: the ordering test now requires land → deliver → gate. Mutation: deleting the call turns it red.
  A new test drives both outcomes of the push verdict.

**Recovery, and a second defect it found.** `origin_reconcile` closed the fork unaided at 05:16. At
05:17 the seat re-offered the same run with `python3 -m background.sim_runner --promote`, the
direction's route for a run made by hand, which wrote `run_complete_20261026T051730Z.md`. That cycle's
tests were cached, so it reached the landing at 05:40. It ended `commit_refused` at 05:46, and nothing
was gated.

1. Origin had moved one commit and the shared tree held none of its own.
2. `_divergence_refusal` admits that state as disjoint, so the fast-forward never ran.
3. `surgical_land` then refused, because a PRIMARY checkout behind origin may not commit (the
   land-twice class).

So the two doors disagree about a tree that is merely behind. The publisher's classifier also logged
the refusal as "UNNAMEABLE", because it does not know `surgical_land`'s wording. That gap is not fixed
here.

**Second fix (same lane, landed after the first).** `_land_publish_commit` now calls
`_level_with_origin_before_landing`, which runs `_advance_to_origin_or_say_why` (a fast-forward only,
with git's own refusal as the guard). It runs after the quiet-tree wait and before EACH landing
attempt, because origin moves during that wait too.

- Test: `tests/background/test_the_publish_levels_with_origin_before_each_landing.py` requires the
  order wait → advance → land on attempt 1 and after a lost race. Mutation: deleting either call turns
  it red.
- The run is re-promoted once this code is on the shared tree. That cycle's outcome is in its marker's
  `Publish outcome` section in `docs/staging/done/`.

**What this does not fix.** Two windows remain:

- If origin moves between the repair landing and its push (a window of seconds, not 36 minutes), the
  first refusal can still happen. Closing that would mean `land()` building on origin's head instead
  of HEAD's.
- If origin moves between the fast-forward and `land()`'s own pre-check (also seconds), the second
  refusal can still happen.
