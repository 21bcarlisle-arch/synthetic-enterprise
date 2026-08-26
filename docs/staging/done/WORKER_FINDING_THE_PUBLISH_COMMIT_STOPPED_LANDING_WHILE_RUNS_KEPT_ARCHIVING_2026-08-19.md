**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/background/test_a_refused_publish_commit_reaches_the_wedge_detector.py::test_the_null_control_the_pre_fix_code_disarms_the_alarm`,
`tests/background/test_a_refused_publish_commit_reaches_the_wedge_detector.py::test_every_outcome_that_did_not_publish_reports_a_non_zero_code`,
`tests/background/test_a_duplicate_marker_is_not_a_publish.py::test_no_new_no_publish_path_may_quietly_return_zero`,
`background/process_run_complete.py`, `background/sim_runner.py` — a refused publish commit now exits 77 instead of 0, so the wedge detector records a failure rather than clearing the streak; the silence is closed, the live surface has caught up, and the one recommendation not taken is recorded below as an accepted limitation with its own successor finding.

# FINDING — the publish commit stopped landing while runs kept completing and archiving themselves

**Found by:** the `G13_projection_consumers` draw, 2026-08-19, while checking why that atom's own
feed returned 404 on the live site.
**Class:** the publish path regenerates and STAGES the whole site data surface, then archives its
trigger as done, and nothing checks that the commit which would deploy it ever landed.

## Observed, with evidence

Every claim below is `observed-with-evidence` (R9). Nothing here is inferred.

**The public site is serving figures about eleven and a half hours stale.** Fetched live, not
read off disk:

| | `generated_at` | `git_commit` |
|---|---|---|
| `https://poesys.net/data/dashboard.json` (LIVE) | `2026-08-19T00:17:34Z` | `5e0f964ab` |
| `git show :site/data/dashboard.json` (STAGED, undeployed) | `2026-08-19T11:50:56Z` | `a8f602bf6` |

**The last publish commit is `ec2ea630a`, 2026-08-19 01:43:49 +0100** — "Auto-process run
complete: report + LATEST.md + site/". `git log -- site/data/` shows no auto-process commit after
it.

**Four runs completed AFTER it and archived themselves as done anyway:**
`docs/staging/done/run_complete_20260819T095100Z.md`, `…T100247Z.md`, `…T105329Z.md`,
`…T114605Z.md`. The last of those is 11:46:05Z, i.e. ten hours after the last publish commit.

**33 regenerated `site/data/*.json` files are staged and uncommitted** (`git diff --cached
--name-only -- site/data | wc -l` = 33), against 48 tracked in HEAD. The regeneration worked; the
deployment did not.

## Why this is silent

The three steps are each individually "successful":

1. the generators run and write `site/data/` — logged as success;
2. the paths are `git add`ed — the `site/data/*.json` glob at `process_run_complete.py:3357` is
   correct and does cover every file, including new ones;
3. the run_complete trigger is moved to `docs/staging/done/` — which is the signal a human or a
   later tick reads as "published".

Nothing between step 2 and step 3 asserts that a commit exists. So the archive says done, the log
says generated, and the live site says something eleven hours old. This is the already-recorded
class *"archiving is done by a process that cannot know whether the work landed"* — but observed
here on the **public surface**, not on an internal record, which is what makes it HIGH rather
than LATENT.

R11 is the rule this defeats: "verify to the rendered value." Every layer of local evidence —
generator log, `git status`, the archived trigger — reads green while the rendered value is
stale. Only a fetch catches it, and no automated fetch runs.

## What this already cost, concretely

`site/data/projections.json` (atom `G13_projection_consumers`) has **never been live at all** —
`https://poesys.net/data/projections.json` → 404, while sibling feeds `proof.json`,
`dashboard.json` and `wip_flow.json` all → 200. Its generator was wired into the publish path at
`c9430c326` (11:19:25 +0100 today), which is *after* the last publish commit, so no commit has
ever carried it. That atom's own build note had cited the live feed as its strongest evidence
without fetching it; the fetch refutes the citation.

## Recommendation — and this is what I would take

**Do not hand-commit the 33 staged files.** They belong to several lanes and sweeping them into
one commit is the exact defect CLAUDE.md's pathspec rule exists to prevent. The repair is at the
publish path, not on the tree:

1. **Make the archive conditional on the commit.** `process_run_complete.py` must not move a
   `run_complete_*.md` to `done/` until it has verified the commit exists — `git rev-parse` the
   new HEAD and confirm it contains the staged paths. An archive is a claim of completion and
   must be R1 consumer-verified like any other.
2. **Find why the commit stopped.** The generators ran, so the process reached step 2 and then
   either raised or was killed between `git add` and `git commit`. The auto-process log for the
   four runs above is where that lives, and it should be read before any code change — this
   finding deliberately does not guess.
3. **Add the fetch that would have caught it.** A published-freshness control that fetches
   `poesys.net/data/dashboard.json` and reds when its `generated_at` is behind the newest local
   `run_output_*.json` by more than one cycle. R15: it must fail on its own named defect, which
   is exactly today's state, so it can be mutation-tested against this very tree.

## On the BLOCKING severity, since it holds a lane

`BLOCKING` is the ruling's own wording — "a published figure may be wrong" — and the published
figures on `poesys.net` are eleven and a half hours behind the tree, which R14 makes a wrongness
and not a cosmetic lag. I considered `LATENT` on the grounds that this finding blocks no specific
promotion, and rejected it: `background/finding_severity` names that reasoning explicitly as the
anti-pattern ("deciding one's own finding is not BLOCKING in order to keep a lane open"). The
ruling's own escape hatch stays open for anyone who needs an H_harness raise before the repair —
record and accept the limitation explicitly, which is a decision rather than an accident.

**Not taken this tick, deliberately** (SELF-INTERRUPT DISCIPLINE): all three are BUILD changes to
`process_run_complete.py`, a heavily shared file, and the drawn atom was G13. Registered here
rather than fixed on sight. The one thing done inline was landing G13's own feed by pathspec,
which takes no other lane's staged work with it.

---

# DISPOSITION — 2026-08-19, drawn as the RUNG-1c blocking finding on lane `H_harness`

## Recommendation 2 first, because it said not to guess: WHY THE COMMIT STOPPED

`observed-with-evidence` (R9), read out of `docs/observability/sim-runner-log.md`, not inferred.

**The commit was REFUSED by the pre-commit hook chain, fourteen times in a row**, between
01:56Z and 11:45Z — every one logged `Commit/push failed (commit_refused)` with the hook's own
output in the tail. The gates that refused, by name:

| gate | occurrences in the window |
|---|---|
| `[test-gate] FINDING-CLASS CONSOLIDATION BROKEN` | 8 |
| `[test-gate] TESTS FAILED` | 2 |
| `[site-lane] SITE TESTS FAILED` | 2 |

The 10:01Z refusal quotes the cause verbatim: *"TWO ROOMS
WORKER_FINDING_AN_EPOCH_3_CURRICULUM_BLOCK_WAS_DISCHARGED_CITING_A_DIRECTOR_INSTRUCTION_WITH_NO_ARTEFACT_2026-08-19.md:
present in done AND root"*. So the publish path was refusing to commit onto a tree another lane
had left red — which is the gate doing its job — and it retried every cycle, correctly, because
`_process` withholds the fingerprint on a non-retryable outcome.

**So the finding's premise "the regeneration worked; the deployment did not" is right, and its
guess at the mechanism is not.** Nothing raised and nothing was killed between `git add` and
`git commit`. The publish path ran to completion every time and was told no.

## The defect that is actually mine to fix, and it is not where the finding pointed

The finding's §"Why this is silent" says *"nothing between step 2 and step 3 asserts that a
commit exists"*. There IS such a mechanism — the publish-gate wedge detector, three failures in
an hour, `[ACTION NEEDED]` to NTFY, `PUBLISH_GATE_ITEM_ID` in the durable register, and a
RUNG-1 unwedge draw off `.publish_gate_state.json`. It did not fire, and the reason is worse
than absence:

**`_process` returned 0 after logging the refusal.** rc is the ONE input
`record_publish_gate_outcome` consumes. The router's independent evidence for rc=0 is
`_green_is_on_record_for`, which reads `.last_tested_hash` — and on this path that check is
TRUE, because the publisher's own scoped suite really had passed; the refusal came afterwards,
from a different gate, on a red the publish did not cause. So the router did not merely stay
quiet. It called `record_publish_gate_success()` and cleared the streak:

> `[2026-08-19 07:23 UTC] [process_run] Publish gate recovered -- cleared wedge state, re-armed
> alarm.`

logged in the middle of the outage, with `.publish_gate_state.json` reading `failures: []`,
`wedge_since: null`, `episode_failures: 0` for the whole eleven and a half hours.

This is the THIRD DOOR of a fail-open this module has already closed twice — `EXIT_LOCK_SKIPPED`
(2026-07-29, a lock-skip read as a publish) and `EXIT_NOTHING_PUBLISHED` (2026-08-12, a
duplicate marker read as a publish). Both of those are about a publish that never STARTED. This
one is a publish that ran the whole way and did not LAND, and no check keyed to the suite could
ever have caught it, because the suite was green.

## What was built

`EXIT_PUBLISH_DID_NOT_LAND = 77`, and `publish_exit_code(reason)` deriving it from
`RETRYABLE_PUBLISH_OUTCOMES` — the SAME closed set that already decides whether to fingerprint
the cycle, so "retry this" and "alarm on this" cannot drift into two lists that disagree. The
drift is the incident: the fingerprint was correctly withheld fourteen times while the exit code
said 0 every time. Fail-closed, so an outcome added later without being classified reports "did
not land" rather than inheriting rc=0.

The router gets a named branch with `kind="commit_did_not_land"`, not the generic rc>0 path —
`_classify_gate_failure` would have labelled it `test_regression` and sent the RUNG-1 draw
hunting a red test at a HEAD whose suite was green, the same laundering that `deadline_kill`
exists to prevent. `sim_runner` gets its own branch: the generic one says *"marker left for
background_worker"*, which is false here — the publisher archives the marker BEFORE attempting
the commit, so no sweep ever sees it again and the retry is the next cycle's marker.

R15, both halves mutated and both fire:

| mutation | reds |
|---|---|
| `publish_exit_code` returns 0 unconditionally (the pre-fix tail) | 3 |
| the tail's `if rc == 0:` guard removed | 1, by name, in the rc=0 register |
| the router's `kind=` dropped | 1 |

The null control is the one that matters: `test_the_null_control_the_pre_fix_code_disarms_the_alarm`
re-runs the identical fixture — same marker, same green `.last_tested_hash`, same three-deep
streak — with rc=0, and asserts the streak is CLEARED. A green result in that file is therefore
a statement about the exit code and not about the fixture.

## The finding's recommendation 1, and why it is NOT what was built

*"Do not move a `run_complete_*.md` to `done/` until the commit exists"* would break a live
invariant in the opposite direction. The marker is moved to `done/` BEFORE the commit
deliberately, and the code says why: *"so the archive itself lands in the same commit as the run
it documents, instead of sitting untracked forever (observed: 7+ done/ markers never made it
into any commit)"*. Ordering the archive after the commit re-opens that. The claim the archive
was making falsely was never "the file is in `done/`" — it was "rc=0, this cycle published". So
the repair is at the claim, not at the move.

## The limitation explicitly recorded and accepted (clause 2)

**Recommendation 3 — the published-freshness FETCH — is NOT built.** What is closed is the
silence: a publish that does not land now raises the alarm from the inside, on the third
consecutive cycle, roughly thirty minutes rather than eleven and a half hours. What is still
absent is an outside check: nothing fetches `poesys.net` and compares its `generated_at` against
the newest local run, so a class of staleness whose cause is NOT a refused commit — a push that
reports success without advancing origin, a CDN that serves a stale object, a deploy that never
ran — remains unmonitored. That is a real gap, it is defence-in-depth rather than the root
cause, and it is filed as its own successor finding rather than claimed here:
`WORKER_FINDING_NOTHING_FETCHES_THE_PUBLISHED_SURFACE_TO_CHECK_ITS_OWN_FRESHNESS_2026-08-19.md`.

## R11 — the live surface, fetched, not read off disk

The acute condition in the finding's own table has cleared. `589dc119b` landed at 12:20Z once
the tree went green, and the fetch agrees with HEAD:

| | `generated_at` | `git_commit` |
|---|---|---|
| `https://poesys.net/data/dashboard.json` (LIVE, fetched 2026-08-19) | `2026-08-19T11:50:56Z` | `a8f602bf6b458dad49db35cb59f4e995620f3a14` |
| `git show HEAD:site/data/dashboard.json` | `2026-08-19T11:50:56Z` | `a8f602bf6b458dad49db35cb59f4e995620f3a14` |

`https://poesys.net/data/projections.json` now returns **HTTP 200**, where this finding recorded
404. So the `G13_projection_consumers` citation that the finding refuted is now true — and it is
true because a commit landed, which is exactly the thing that had stopped being checked.
