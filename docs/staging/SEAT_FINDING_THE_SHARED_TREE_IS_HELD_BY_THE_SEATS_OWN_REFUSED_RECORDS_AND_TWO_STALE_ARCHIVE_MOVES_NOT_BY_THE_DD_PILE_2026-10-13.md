**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-publish-lands-once-the-shared-tree-reaches-origin` (Lane 0 delivery)

# The shared tree is held by the seat's own refused records and two stale archive moves, not by the DD pile

*Continues `done/SEAT_FINDING_THE_PUBLISH_IS_HELD_BY_THE_SHARED_TREES_STALE_HEAD_NOT_BY_A_LIVE_RED_2026-10-13.md`.
That finding was archived by dbe4f7167 with the cause given as "the console seat's staged DD pile". That cause is now spent; this finding gives the one that replaced it.*
**Re-measured a fourth time, 2026-10-13 ~17:35Z (delivery seat, executor, claim
`the-publish-lands-once-the-shared-tree-reaches-origin`).** The shared HEAD is still 2248e3baf.
It is now 62 behind origin 756e9c293, 0 ahead, and still lacks 81c129fe8. `publish_provenance.json`
on the shared tree reads `verification_state: paused`, paused since 10:03:21Z, for the same census
test at git=2248e3baf.

46 incoming paths are dirty. `origin_reconcile.identical_tracked_twins` proves **39** of them
byte-equal to origin. So the DD pile is **on origin**, and it holds nothing: the reconciler would
clear it the moment nothing else stood. The **5** that remain are not a landing sequence:

| Path | What it is | Who clears it |
|---|---|---|
| `docs/direction/DIRECTION.yaml`, `docs/direction/decisions.jsonl`, `docs/status/SEAT_STRETCH_LOG.md` | **The orientation seat's own records.** It rewrites them on the shared tree every three hours and lands them on origin through `delivery_seat.commit_direction`. | The orientation seat itself. |
| `docs/staging/ADVISOR_FINDINGS_THE_HARNESS_HAS_NO_WIDE_EVENT…_2026-10-11.md`, `…THE_KNOWLEDGE_LAYER_HAS_NO_PUBLISHED_WHEN_CLOCK…_2026-10-10.md` | An **archive move to `done/`** in the shared tree (written 2026-10-13 05:22 and 2026-10-12 15:00) that never reached origin. Origin's fates sweep (259ac97ca, 756e9c293) kept both at the root as ATOMs and amended them there. The `done/` copies differ from origin only in an auto-applied staging-watcher header. | A hand resolution: return both to the root, which is origin's ruled fate. Not a hash proof, so the reconciler correctly will not do it. |

**The cause the earlier three re-measures missed: the seat's record landing failed four stretches
running.** `docs/observability/delivery-seat-log.md` shows the record landing refused at 05:29,
08:31, 11:27 and 14:31Z. Each time the message was *"SEAT_STRETCH_LOG.md on origin/main is not kept
whole by this tree's copy"*. Each failed landing left all three record files dirty against an
advancing origin, so the fast-forward could not run and the publish stayed at the stale HEAD.
ed07176b1 (16:30Z) hand-landed those records onto origin. The shared stretch log now reads as
origin's copy plus one inserted block at line 8 (the diff has no `-` lines), which is the shape
`commit_direction` accepts.

**Prediction, filed before it is observed.** The orientation that started at 17:22:54Z wrote its
records at 17:27:20Z, and when this was written it was still in `commit_direction`. (1) Its log line
will read `commit rc=0; landed <sha> on origin/main`. (2) After that, the three record files will be
identical twins of origin's, and only the two staging notes will block the fast-forward.
(3) The shared tree will **not** advance until those two are resolved by hand. If (1) fails, the
record-landing door is the blocker, not the staging notes.

**Not done, deliberately:** I did not modify the shared tree. This executor runs isolated, and both
residual classes are another writer's working copy.

**Built in the commit that carries this note: the record landing's half of the loop.** This is the
proposal from `done/WORKER_FINDING_A_BEHIND_SHARED_TREE_STOPS_THE_SEAT_LANDING_ITS_ORIENTATION_…_2026-10-05.md`,
which was archived and never built.

- `delivery_seat.rebase_append_only` carries a HEAD-plus-one-block copy onto origin. It no longer
  refuses that copy.
  - A prepend goes under the header, snapped to a line start.
  - An append goes after everything origin appended, because `last_orientation` reads the final row.
  - A block origin already holds returns origin's copy unchanged.
  - Anything else is still refused by name.
- `settle_shared_copies` then writes origin's bytes over each shared append-only copy the seat read,
  so the copy becomes a twin the reconciler clears. It does this only when everything the seat
  added is on origin, and only when the copy is still the bytes the seat read (compare-and-swap).

Printed at today's real inputs: both shared files carry onto origin with 0 lines lost; the stretch
log adds 27 lines origin lacked and `decisions.jsonl` adds 1. Controls are in
`tests/background/test_the_direction_record_lands_on_origin.py` (15 pass). Seven mutations each
fire: refusal restored, end-append removed, settle removed, compare-and-swap removed, the
held-block branch removed, the line snap removed, and the prefix-agreement check removed. The line
snap's mutation was green at first: a missing test, because a dated heading makes the unsnapped
insertion a byte rotation of the right answer. The prepend leg now uses an undated heading, and
the mutation fires.

**Still open:** the two archive moves. Origin ruled both notes ATOM (259ac97ca). Returning them to
the root in the shared tree is a one-line `git checkout HEAD -- <both>` plus deleting the two
untracked `done/` copies. Every byte in those copies is on origin except one auto-applied header,
so nothing is lost. It is left for the console seat or a hand landing, because this executor does
not write to the shared tree.

**The prediction, graded (~18:05Z).**
- (1) **Held.** The 17:22Z orientation landed its record (3143bf196). Separately, 98a5eb6d7 hand-landed
  the 18:27 records on a fresh origin base.
- (2) **Held.** Re-measured with `paths_blocking_fast_forward`: the three record files no longer
  block.
- (3) **Held, with one addition.** The shared tree is still at 2248e3baf, now 70 behind. Six paths
  block the fast-forward, and three of those are twins. The other three are the two archive moves
  named above, plus
  `tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py`.
  That test file was rewritten and staged in the shared tree at 17:49Z: a second implementation of
  the returned-name walk that 81c129fe8 already fixed on origin. It is another lane's live work, and
  it is left alone.

**The fix (70bbfdfbd, promoted in 5d0ad359f) is inert in the orientation seat until the shared tree
fast-forwards.** `delivery-seat.service` imports `background/delivery_seat.py` from the shared
checkout. Until the fast-forward, the next HEAD-plus-block record is refused exactly as before.

**One misattribution, corrected here.** `WORKER_FINDING_THE_PUBLISHERS_RETRIES_…_2026-10-13.md`
gives pid 1911763 as the writer of the three record paths. pid 1911763 is this executor, which ran
in an isolated worktree. The orientation seat (`delivery-seat.service`, MainPID 1884575) wrote them.
