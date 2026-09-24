**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, landing diagnosis

# The site lane refused on two doors pinned to the shape the change removes — and the stale stamp was not the cause

*Retitled 2026-09-22 by the invocation that landed this work. The original title — "the site lane
refused on a feed regenerated before the merge, and the four reds do not reproduce standalone" —
stated the wrong cause and a claim that is false; both are kept verbatim in the body below, beside
the measurement that refuted them. See **CORRECTION**.*

**Claim:** `the-republished-seed-price-carries-an-unbounded-count-in-every-artefacts-own-bytes`
**Companion result:** `SEAT_RESULT_THE_PAGE_STOPPED_COPYING_THE_SEED_PRICE_AND_THE_BAR_IT_WAS_GRADED_AT_WAS_A_RETIRED_CONSTANT_2026-09-22.md`

Written so the next invocation does not re-derive four hours of gate diagnosis. **The code work is
complete, verified and mutation-proven; only the landing is outstanding.**

## What the gate actually refused on, and how long it took to find out

Three refusals, three different causes, and only the third is interesting:

1. **`[test-gate]` TESTS FAILED** — names elided. My wrapper captured `stdout[-6000:]` and the
   40-file selection line alone is ~1,400 characters, so the failure names fell off the front.
   **Never truncate a gate capture from the front; the verdict is not always at the end.** The
   gate also hands its own fds to pytest (documented at `pre_commit_test_gate.py:1902`), so the
   dots interleave with the gate's narration and cannot be used to locate the failure either.
2. **`[test-gate]` NO PARSEABLE SEVERITY HEADER** — my incidental commons finding carried
   `**Lane:** C_regulation_commons`, which is not in `background/finding_severity.LANES`. The
   regulation commons has no lane of its own; `F_risk_compliance` is the one that owns published
   law. One-line fix.
3. **`[site-lane]` SITE TESTS FAILED** — the real one, and it is a *different gate* from the
   test-gate. Four named doors:

       site/test_the_baseline_comparison_reaches_the_reader.py
         ::test_the_error_bar_says_the_instrument_cannot_resolve_it
         ::test_every_leg_of_the_advantage_reaches_the_reader_with_its_own_verdict
         ::test_the_price_LEVEL_legs_stated_sign_reaches_the_reader
       site/test_the_selection_legs_bias_size_reaches_the_reader.py
         ::test_the_bias_size_never_reaches_the_reader_without_the_sign_on_the_shared_population

## The cause, and it is mine

**I regenerated `site/data/value_arms.json` BEFORE merging `origin/main`.** The feed therefore
carried `publishing_tree_commit: f2aa16899` while the commit the gate was building had `a3f078c4b`
as its parent. The generator stamps the tree it publishes from; a feed produced against a
superseded tree is exactly the "figures on a superseded clock" class, and the site doors read that
provenance. Regenerating at the merged HEAD put `a3f078c4b` in the feed and the four doors pass.

**THE ORDER IS THE LESSON. Merge the base FIRST, regenerate the feed SECOND.** A feed generated
before the merge is stale the moment the merge lands, and the site lane — not the test gate — is
what notices. Doing it the other way round costs a full gate cycle, which on a contended box is
over an hour.

## CORRECTION (2026-09-22, the next invocation): THE CAUSE ABOVE IS WRONG, AND THE SECOND CAUSE WAS REAL

**The stale `publishing_tree_commit` was not the cause of the four reds. It was a real defect and
regenerating after the merge was the right fix, but it fixed something else.** Kept above rather
than revised, because the section below correctly suspected a second cause and the pair is the
evidence that the suspicion was worth acting on.

The one-variable run the section below asks for, done first thing:

| tree | the two door files |
|---|---|
| clean `d28b3e11f`, no change applied | **183 passed, 1 skipped** |
| `d28b3e11f` + the six files, feed regenerated AT `d28b3e11f` | **179 passed, 4 failed** |

So the reds are caused by the change, they reproduce standalone every time, and the stamp is not
in it. **Why the previous invocation saw them pass: it never ran the doors against a correctly
stamped feed at the merged base.** It reasoned from the stamp being wrong to the stamp being the
cause — and the gate agreed with it once, for the ordinary reason that a red clears when you
rebuild anything at all.

**The actual cause is two site doors pinned to the shape the change removes**, which is this
project's named failure and not a new one — *a control pinned to the current state goes red when
the code becomes MORE honest*:

1. **`test_..._bias_size_never_reaches_the_reader_without_the_sign_on_the_shared_population`
   required `seeds_needed_to_state_a_sign` to be an `int > 0` and demanded the page print it.**
   That door existed to make the page publish **1,744** — the defect. Its own docstring says
   "KEYED TO THE PROPERTY, NOT TO -£259.29 … nor the seed price as literals", and that leg was the
   one place it was not. The property it wanted is intact and still both-sided: *a refusal must
   carry its distance.* What changed is that "there is no finite distance" is now one of the
   answers, so the leg is a partition — a finite price reaches the reader, or the block states the
   price is unbounded and the endpoints it was priced over reach the reader.
2. **Three controls compared the producer's refusal to the rendered page BYTE FOR BYTE**, via
   `_graded_legs_or_the_refusal_reached_the_reader` and the `sign_withheld_because` rung. The door
   renders ` -- ` as ` — `. Those comparisons were green only for as long as no producer had ever
   written a ` -- ` into those two fields; `_staleness_caveat` began writing one the moment it
   started PRICING the owed re-run instead of merely naming it, and the match was cut at the first
   separator. **832 of the 1,222 characters matched — the reader was meeting the refusal in full
   the whole time.** The fix is this same file's `_door_prose`, written for this exact transform
   one panel over and not reached for here.

Both fixes are mutation-proven rather than asserted: neutering `_door_prose` to the identity reds
the three doors again (so the normalisation is load-bearing and not a no-op), a reason the page
never carries is still caught, and the new partition dies on all four of deleting the withholding
reason, flipping `has_no_upper_bound` off, nulling every priced endpoint, and moving one endpoint
off the page. Whole `site/` tree: **880 passed, 37 skipped** — the same figure this document
reports for the pre-merge run, now with the change applied.

**THE GENERALISABLE PART, and it is the reason this correction is longer than the finding.** The
previous invocation wrote *"the code work is complete, verified and mutation-proven; only the
landing is outstanding"* while four site doors were red against it. Every one of its checks was
real; none of them was the whole `site/` tree at the base it was landing onto. **A green targeted
suite plus a green gate on a superseded base is not evidence about the tree you are about to
create** — and "only the landing is outstanding" is the sentence to distrust, because it is what a
seat writes when it has stopped looking.

## What I could NOT establish, and it is worth someone's time

**The four reds do not reproduce standalone.** They pass:

- in this worktree (183 passed, 1 skipped on those two files),
- in a faithful clone checked out at `a3f078c4b` with my six files applied, with a real `.git` and
  `GIT_*` scrubbed exactly as `_gitless_env` does,
- and they passed in a whole-`site/` run (880 passed, 37 skipped) taken before the merge.

So the stale `publishing_tree_commit` is a **sufficient** explanation I fixed and verified, but I
have **not** shown it is the *only* difference. The gate builds an extract of the tree the commit
would create and runs the WHOLE `site/` tree there; I never got a whole-`site/` run to complete in
the extract, because the box was saturated. **Someone should reproduce the refusal deliberately** —
re-stamp a feed to a superseded tree, run `pytest site/` in an extract, and confirm those four
doors are the ones that fire. If they are not, there is a second cause still live.

## Two instrument defects found on the way, neither fixed

- **A `git archive` extract has no `.git`,** so my first probe produced six failures that were the
  probe's own artefact. Cost: one wasted 40-file run. The faithful reproduction is a `--local`
  clone of the common git dir plus a forced checkout.
- **`ps -o etime` and `/proc/<pid>/stat` starttime arithmetic both read wrong on this box today**,
  giving process ages of 2–3 minutes for processes alive far longer, while a controlled
  `/proc/uptime` delta across a known `sleep` came back exactly 60.01s against 60s of wall. The
  guest clock also stepped BACKWARDS mid-turn (`date` read 11:14Z after commits stamped 11:32Z) and
  forwards again later. Another lane landed the same class this session
  (`WORKER_RESULT_THE_FOUR_MUTE_DAEMONS_...`: journal REALTIME stamps 14.61h behind their own
  process starts). **Do not price a process's progress off its apparent age here — price it off
  accumulated CPU in `/proc/<pid>/stat` fields 14+15, which was the only reading that stayed
  honest all turn.**

## Why the landing is still outstanding

Box saturation, not the change. At the point of writing, my gate's pytest had accumulated 126s of
CPU and was gaining ~1.3 CPU-seconds per wall minute, against a selection that needs ~350s — three
other lanes were each running a full `tests/` suite concurrently. The landing was left running.

**The next invocation should not rebuild anything.** The working tree holds the finished work; the
feed is correctly stamped at `a3f078c4b`; the severity header is fixed; all 40 test-gate targets and
both site door files are green here. The only outstanding act is `surgical_land` + `promote_worktree_landing`
on a box with enough headroom to finish a gate.
