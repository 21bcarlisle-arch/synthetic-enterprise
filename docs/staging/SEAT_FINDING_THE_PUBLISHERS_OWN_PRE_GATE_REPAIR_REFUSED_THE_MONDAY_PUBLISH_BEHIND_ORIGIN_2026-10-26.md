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

**Disposition of the Lane 0 item `the-publish-lands-from-a-trunk-worktree-not-the-primary-checkout`
(worker, 06:45Z).** The item asked for the publish to gate and land in a detached worktree on
origin/main, so that "origin moving during the gate can no longer refuse a green publish". Re-measured
against c2fc7b207, that rework is not built, for three reasons:

- Both measured refusals are already closed: 05:14 by 410c1131d, 05:46 by c2fc7b207.
- Origin moving *during* the gate is already absorbed. The commit lands on the old base and the push
  is rejected non-fast-forward. `_publish_is_absorbable` then reads that as a race over paths we do not
  write and hands it to `origin_reconcile`. A real collision on a publish path refuses with its reason.
  `tests/background/test_the_publish_verdict_asks_reachability_and_not_equality.py::
  test_only_a_lost_race_over_paths_we_do_not_write_is_absorbable` checks both branches, with a stated
  mutation. That is the control the item asked for, keyed to the route the code actually takes.
- A worktree route would make this case worse. `promote_worktree_landing` refuses anything that is not
  a fast-forward and leaves the re-gate to the caller. So an unrelated mid-gate commit, which is
  absorbed today, would become a refusal plus a second full gate.

The one remaining shape is the reconciler fast-forwarding the shared HEAD during the gate. That is
`BaseMoved`: a lost race that `land()` re-gates. It is the hot-tree class, not an origin class, and a
worktree route would pay the same re-gate.

Done instead: run_output_4ae8da9b0f_20261026T022647Z was re-offered at 06:40Z as
`run_complete_20261026T064020Z.md`, with c2fc7b207 on the shared tree. Its outcome lands in that
marker's `Publish outcome` section. `mondays-window-published-the-b2bc3d8da5-run` already counts as
delivered, so no premise-spent was recorded against it.

## The 06:40Z re-offer was refused too, and on a third cause (delivery seat, 07:05Z)

Checked under `mondays-window-published-the-b2bc3d8da5-run`. The publisher took
`run_complete_20261026T064020Z.md` at 06:46Z and refused it `behind_origin` at 06:58Z. c2fc7b207's
pre-landing fast-forward ran; git refused it because another writer held the shared
`.git/index.lock`. The advance loop treats every refusal to advance as terminal, so attempts 2 and 3
went unspent and the cycle was discarded. That is right for a real fork, a collision and an
unreadable origin. It is wrong for a held lock, which a live git process holds and will release.

Three refusals of one clean run, each on a different cause: behind_origin (the repair commit),
commit_refused (the primary checkout behind), behind_origin (the lock). `last_landed_publish` is
still 1792401343. Not one of the three refusals was about the run's own figures.

**Fixed in the landing that carries this paragraph.** A refusal naming git's `index.lock': File
exists` now waits for the lock to clear, with surgical_land's own deadline. It then re-runs the
advance within the existing three attempts. A lock still held at the deadline is refused and named
as possibly stale, and it is never deleted. Control:
`tests/background/test_a_held_index_lock_is_waited_out_not_taken_for_a_fork.py`. Three mutations
each turn it red: dropping the retry, a wait that always succeeds, and widening the match to
"REFUSED".

**Prediction, filed before the next attempt:** the re-offer after this lands either publishes 4ae8da9b0f
or is refused on a cause that is neither the lock nor behind-origin-by-repair. If it is refused
`behind_origin` again with the lock named, this fix is wrong.

## The fourth attempt cleared behind_origin and met the stale-copy guard (07:40Z)

The prediction above held: the 07:00Z re-offer (07:27Z cycle, with the lock fix on the shared tree)
reached 0 behind and 0 ahead and was NOT refused on the lock. It was then refused `commit_refused`
by `tools/stale_copy_refusal.py`: "19 path(s) would revert work that has already landed". Those are
18 knowledge pages (against 0913f9818) and `site/explore/index.html` (against 16823067a). Measured
on the live tree: every page's mtime is NEWER than its landing. On each page, the only distinctive
line that landing added was the 19 Oct run's own `RUN-CLOCK` provenance line or its `cast:static`
stamp. The publish exists to rewrite exactly those, so rule 1 ("contains not one distinctive line")
read a correct regeneration as a revert. It would refuse the first publish after any commit that
reaches a page only through its stamp.

**Fixed in the landing that carries this paragraph.** `distinctive_lines` drops lines inside the
two generator-owned regions (`PUBLISH_WRITTEN_REGIONS`). Any other line the commit added stays
evidence. Re-run over the live tree with the new code, 0 of the 19 refuse. The one remaining
refused path (`site/test_the_opening_direct_debit_comparison_reaches_the_reader.py`, a working
copy from 5 Oct) is not in the publish set and was not named by the publisher. Control:
`tests/tools/test_a_publish_rewriting_its_own_run_stamp_is_not_a_revert.py`. Two mutations turn it
red: no filter, and a filter that takes every line. A third test pins the tokens to the generators.

**Prediction, filed before the next attempt:** the next re-offer of 4ae8da9b0f either lands or is
refused on a cause that is none of the four above. If the stale-copy guard names a knowledge page
again, this fix is wrong.

**A second fix for the same refusal landed in parallel, and it is retired (worker, 08:10Z).**
78a6dfacc (this worker) reached the same diagnosis from the other side. It exempted every `.html`/`.js`
publish path this cycle had rewritten, by mtime, as printed `drops`. It was gated while ae03a6317 was
being gated, and it reached the shared HEAD as a fork of origin. ae03a6317's region filter is
narrower: it removes only the stamp lines and keeps every other added line as evidence. It also sits
in the guard, where every caller benefits. So the merge that closes the fork also removes
`_pages_rendered_this_cycle` and its test, leaving one mechanism for one requirement.

What the checks behind 78a6dfacc add to this record:

- The page producers were not dirty in the shared tree.
- `refuse_stale_producers` already refuses to run a producer whose working copy reverts HEAD.
- `origin_reconcile.generated_output_verdicts`' static oracle does not know the glob-stamped
  knowledge pages. That is still open, because the reconciler's advance treats a dirty knowledge
  page as authored work.
