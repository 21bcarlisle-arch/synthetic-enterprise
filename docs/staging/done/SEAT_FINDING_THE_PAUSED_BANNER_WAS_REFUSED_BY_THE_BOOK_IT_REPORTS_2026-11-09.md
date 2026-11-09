**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The paused banner was refused by the book it reports, so poesys.net said "Verified 3 Nov" through every refusal on 8–9 Nov

Found by the seat executor on Mon 9 Nov, 05:20 GMT, reading the live status line after the 04:00
publish attempt (drawn item `read-the-monday-status-line-against-the-gate`; subject 58d90c457, the
change that makes a domain-invariant refusal print as `paused_gate` in the rule's words).

## What the live line said

`https://poesys.net/data/publish_provenance.json` at 05:20Z: `verification_state: verified`,
`written_at: 2026-11-03T02:24:29Z`, `paused_gate: null`. The director's 7 Nov item 3 — "'Not
updated' should never be silent" — was not just silent on the live site. The site said the
opposite: that it was verified.

The shared tree's own copy said the right thing: `paused` since 2026-11-08T20:48:26Z, with the gate
sentence. **58d90c457 works up to the file. The file never reached origin.**

## Why: two defects, both observed

**1. The banner commit was gated on the refused book (the cause of the silence).** In
`sim-runner-log.md`: `Provenance banner commit FAILED (rc=1)` at 8 Nov 20:59, 9 Nov 04:29 and
04:58. Each time it was the site lane:
`site/explore/test_the_tariff_label_is_the_term_in_force.py::test_every_printed_tariff_is_the_term_the_bills_record_at_that_moment`,
4 labels on PROS-2017-0183. That test reads `site/data/explore_cast.json` **from disk**. On a red
cycle the shared tree's `site/data/` holds the refused book: 1,337 modified files, written by the
publisher and then not committed. On origin's feed the same test passes (2 passed, run in this
worktree at 05:25Z). `_commit_and_push_paths` was a pathspec `git commit` in the shared tree, and
the hook chain grades the working copy. So the gate refused the banner because of the content the
banner exists to say was refused. That is the partial-commit defect `tools/surgical_land.py` was
written to close (its docstring, "THE SECOND DEFECT IT CLOSES"). The content publish moved to it on
2026-09-08; the banner never did.

**2. The gate sentence was cut mid-clause.** `plain_refusal` capped each statement at 200
characters but not the sentence. With three rules it ran past `PAUSED_GATE_CHARS` (900), and
`record_paused` sliced it: the stored line ends "(unit: book: its successful DD collections,". The
control asserted `len(plain) <= 900` on a two-rule fixture, so it was keyed to that answer rather
than to the property.

## What changed (this commit)

- `_commit_and_push_paths` lands through `surgical_land.land` (new `_land_liveness_surface`), which
  gates a clean extract of HEAD plus the named path. The shared index and working copy are no
  longer read. A lost race is retried inside `land`, so the old git ref-race re-land
  (`_lost_the_ref_race`, `_reland_after_lost_ref_race`) is gone along with the `git commit` it
  served.
- `surgical_land.NothingToLand` (a `LandingRefused` subclass) marks the byte-identical steady state
  by type, so the banner stays quiet when nothing changed.
- `plain_refusal(..., limit=)` fits the sentence to the line. Statements shorten first, then go;
  only then are trailing rules counted ("and N more"). Every rule's ID and count survives. The
  publisher passes `publish_provenance.PAUSED_GATE_CHARS`.
- Controls: `tests/background/test_the_banner_is_gated_on_its_commit_not_on_the_refused_working_copy.py`
  (this replaces the ref-race file), and the fitted-sentence leg in
  `test_the_status_line_names_the_gate_that_refuses_the_publish.py`, run against both live
  refusals. Three mutations were run and all three fired: ignore `limit`; drop the `NothingToLand`
  arm; restore a `git commit` call.
- Deleted: four `test_process_run_complete.py` tests whose subject was the removed `git commit` /
  `git add` call (the env on `git commit`, the liveness-vs-content deadline asymmetry, and two
  `git add` refusal legs). The asymmetry is now impossible by construction, because both routes run
  the same landing. `_commit_hook_env` and `_git_add_or_refuse` now have no production caller.
  They are left for a cleanup rather than widening this commit.

## Pre-registration (filed before the next cycle runs)

LATENT, not BLOCKING: the repair is in the commit that files this. What is still owed is the live grade below. Archive to `done/` once predictions 1–4 are graded.

Predictions for the first red publish cycle the shared tree's publisher runs on a checkout that
contains this commit:

1. `sim-runner-log.md` shows no `Provenance banner commit FAILED` that names a `site/**` test which
   passes on origin's feed.
2. A `chore(provenance): verification paused banner` commit reaches origin within that cycle.
3. `https://poesys.net/data/publish_provenance.json` reads `verification_state: paused` with
   `paused_since` = 2026-11-08T20:48:26Z (the stamp is preserved, not re-stamped).
4. Its `paused_gate` ends with "." and is at most 900 characters.

If 1 holds and 2 fails, the next suspect is a refusal the clean extract also gives: a red on HEAD
itself, or the behind-origin refusal. Name it from the log; don't re-derive it. If the publisher's
next cycle is GREEN, predictions 2–4 cannot be graded. Say so, and do not count it as a pass.

## Not done here

The 900-character line is long for a status banner. Whether the banner should carry the sentence
or link to `docs/reports/DOMAIN_INVARIANTS.md` is a presentation call I have not made.

## Addendum, 06:40Z: the banner reached origin by the old route at 05:54, and carries defect 2 live

While this repair was gating, another lane landed `0f4c93eea4` (05:30Z, "The Explore tariff check
reads a per-fuel label"), which fixed the site test that had been refusing the banner. The
publisher's next cycle then committed the banner through the old `git commit` route:
`Provenance banner published to origin.` at 05:54Z, commit `0c711545b8`. So since then the live line reads
`paused` since 2026-11-08T20:48:26Z, which is correct, but its `paused_gate` is the sliced 900-character
sentence ending "(unit: book: its successful DD collections,".

What this changes. Defect 1 is not refuted, but its instance cleared because the red test was
fixed, not because the route changed. Any `site/**` test that reds on a refused book's working copy
will silence the banner again on the old route; the repair (`955520f65` on origin) removes that
route. Defect 2 is now on the live site, and it clears at the next pause write that runs the
repaired `plain_refusal`. Prediction 4 is unchanged and is the one to grade. Predictions 1–3 now
need the next red cycle whose working copy reds a site test, or a cycle on the repaired code; a
cycle that publishes on the old route proves nothing about the new one.

## Grade, 08:15Z: predictions 1–4 hold on the 06:39 cycle; the next cycle lost the race twice

Graded by the seat executor on Mon 9 Nov (drawn item `grade-the-paused-banner-pre-registration`).
Sources: `docs/observability/sim-runner-log.md` on the shared tree, `git show f986cfc48c`, and
`https://poesys.net/data/publish_provenance.json` read at 08:06Z.

The first red cycle on a checkout containing `955520f65` (merged 06:20:37Z) refused at 06:39Z
(git=b9ad453df0, 299 breaches across 3 rules).

1. **Holds.** That cycle logged no `Provenance banner commit FAILED`; it logged `Provenance banner
   published to origin.` at 06:51Z.
2. **Holds.** `f986cfc48c chore(provenance): verification paused banner` reached origin at
   06:51:28Z. It carries a `[surgical-land receipt]`: gate run in a clean extract, rc 0, 1883 passed,
   one path (`site/data/publish_provenance.json`). This is the new route, not the old `git commit`.
3. **Holds.** Live: `verification_state: paused`, `paused_since: 2026-11-08T20:48:26Z`. The stamp
   was preserved, not re-stamped.
4. **Holds.** Live `paused_gate` is 896 characters, names all three rules with their counts, and
   ends "(unit: book: its successful DD collections, graded on Leg A)." Defect 2 is cleared on the
   live site.

Caveat on 1: I did not check whether that cycle's working copy would have redded a `site/**` test.
So this shows the new route lands. It does not show that the new route survives the exact condition
that silenced the old one. The control in `test_the_banner_is_gated_on_its_commit_not_on_the_refused_working_copy.py`
holds that leg.

### What the grade turned up: a lost race leaves the live line one refusal behind

The 07:10Z cycle refused at git=298149a1fc with **2** rules (71 + 80 breaches;
`INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE` no longer breaks). Its banner
landing ended at 07:33Z: `the landing lost the race for HEAD on all 2 attempt(s) ... Nothing was
committed.` So at 08:06Z the live line still names git=b9ad453df0 and three rules. It is correct
that the site is paused, and the paused stamp is right. The *reason* is one refusal stale.

This is the liveness cost of gating an 11-minute suite (`f986cfc48c`: 672 s) for a one-file JSON
write, with `PUBLISH_LAND_ATTEMPTS = 2`. The measured rate at that cost: origin/main took 19
first-parent commits over 460 minutes today (mean gap 25.5 min, median 16.8). Under a Poisson
reading, one gate survives with p ≈ 0.65, and both attempts lose with p ≈ 0.13 per cycle. One loss
in the two cycles seen on the new route fits that reading, so this does not show a defect.

**Pre-registration (written 08:15Z, before the 07:58 cycle's landing has reported):** on that model
the 07:58 cycle lands its banner with p ≈ 0.87, and the live line then names git=298149a1fc and two
rules. If it loses again, that is two in three. The next question would then be whether the race is
against the shared tree's local HEAD rather than origin (local commits and pulls the origin count
does not see). I would ask that before touching the attempt count.

The shared tree's reflog answers the local-HEAD question already. HEAD moved at 07:03:58, 07:19:46
and 07:30:46, each by `surgical-land`, and each is a commit on origin. The banner's attempt 1
(begun about 07:10) lost to 07:19:46, and attempt 2 lost to 07:30:46. That is two arrivals inside
about 23 minutes, which is the bad tail of the rate above, not a hidden local mover.

### The pre-registration graded, 08:30Z: the gate won the race, and the push lost it to origin

The 07:58Z cycle's landing committed the banner on the shared tree as `525696cb2` at 08:09:44Z, on
parent `994f7e56d5`. The prediction was right that the gate would survive the local race. I did not
foresee the next step: `push did NOT advance origin (rc=1, origin=2adea4045, head=525696cb2)`. Two
commits reached origin from linked worktrees during the gate (`81baa1fc9` at 07:59, `2adea4045` at
08:01) without moving the shared tree's HEAD. `surgical_land` races the LOCAL HEAD, and the push
races ORIGIN. The second race is invisible to the first. I count this as **refuted as stated**: the
live line did not move.

`reconcile_watch` should merge that fork, since it is diverged (1 ahead, 2 behind). At 08:13 and
08:18 it was REFUSED by a red that `81baa1fc9` itself put on origin.
`docs/staging/done/SEAT_FINDING_OWN_CODE_REVIEW_UNUSED_DUPLICATED_AND_WALL_CROSSING_2026-10-24.md`
cites its advisor file at the pre-archive path `docs/staging/advisor/DIRECTOR_STEER_REVIEW_...`.
The landed-manifest check reads that as a LANDED claim to a path absent from the tree, and any
commit that stages the document fails on it. The reconciler's merge of origin stages it. So every
red cycle's banner would have stacked locally behind that red. **Fixed in this commit:** the
citation now points at `docs/staging/advisor/done/...`. `tools.landed_manifest_check --at-tree
<this tree> --since-tree 994f7e56d5` reports OK. On origin's tree it reports the ABSENT finding.

Consequence for the repair in `955520f65`: it closes defect 1 and defect 2. It still leaves a
liveness gap. On a busy trunk an 11-minute gate can win locally and lose at the push, and only the
reconciler then carries the banner. That is acceptable while the reconciler is green; this addendum
records that it was not. Not re-designed here: the next cycle and the reconciler, both now
unblocked, are the cheaper test.

Predictions 1–4 are graded (all hold). Archived to `done/`.

**Outcome, 08:35Z.** Once `b595f2af0` cured the red, `525696cb2` reached origin by 08:25. The live
line read at 08:35Z: `written_at 2026-11-09T07:58:07Z`, `paused` since 2026-11-08T20:48:26Z (stamp
preserved), git=298149a1fc, two rules, `paused_gate` 603 characters ending ".". The banner is one
refusal current again. It got there through the reconciler, not through the cycle's own push.
