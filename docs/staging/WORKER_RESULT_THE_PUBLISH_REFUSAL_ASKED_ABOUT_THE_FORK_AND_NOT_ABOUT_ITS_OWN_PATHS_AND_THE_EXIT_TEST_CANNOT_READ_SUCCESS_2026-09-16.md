**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the-publisher-has-never-recorded-a-clean-publish-in-this-episode"

# The publish refusal asked about the fork and not about its own paths, and the exit test cannot read success

Worker seat, scheduled tick, 2026-09-16. The drawn item's premise was spent on arrival and both of
its named follow-ups miss. The wedge's actual cause is measured below and the repair is landed.

---

## Premise check: spent, and both branches miss

The item said *"HEAD and origin are level at `c2d8ac167`, and `behind_origin` — the cause of the
most recent refusal — cannot fire."* At turn start HEAD was `8ca0a6858`, origin/main was
`e9ad946cd`, and the tree was **1 ahead / 5 behind**. `c2d8ac167` was not HEAD and the two were not
level. All four cited commits were indeed already ancestors of origin/main, exactly as the draw
warned.

The item then named two conditional repairs, and neither is the live cause:

* *"the refusal must carry the `red_at_head` attribution"* — no red is named on either recorded
  failure, and both carry `red_at_head: not_established` with the honest reason *"no red is named on
  this failure, so there is no red to attribute to a tree."* There is no red to attribute.
* *"if the cause is the `cannot lock ref 'HEAD'` race, THAT race is the repair"* — it is not. Both
  of the last two failures record `cause: behind_origin`, `rc: 77`, and the publisher's own scoped
  suite **GREEN** on each.

So the exit test stands, the two named remedies do not, and the cause was a third thing.

## What was actually holding it: a refusal that never asked about its own subject

`_divergence_refusal` refused every publish commit on `ahead > 0` **alone**. It knew how far behind
the tree was and nothing whatever about whether the fork came anywhere near the thing it was
refusing to commit.

Measured on this tree, at real inputs:

| | |
|---|---|
| origin commits HEAD lacked | 6 |
| paths those commits touch | 19 |
| publish-surface paths on disk | 6,187 |
| **paths in both** | **0** |

Not one of origin's 19 incoming paths was under `site/`, `docs/reports/` or `docs/status/` — they
were `background/`, `tools/`, `tests/` and `docs/staging/`. **The commit `behind_origin` refused
could not have conflicted with a single thing it was refused for.**

### Why the original refusal was right, and what changed under it

This narrows the guard; it does not reverse it. The 2026-09-01 incident behind
`_divergence_refusal` was real — `HEAD..origin/main` = 23, two of the three local commits made by
the publish loop itself after its own push had already been rejected. What made those retries
poisonous was that they re-committed **the same publish surface origin was moving underneath
them**: the fork did not merely get wider, it got wider in the one place a merge has to adjudicate.

That is precisely the condition now measured, and it is the condition that has changed since:
`background/origin_reconcile` now closes the fork unattended, in an isolated worktree, on the
deadman cadence — and did so during this turn, pushing a merge that carried HEAD onto origin. A
disjoint publish commit is one it absorbs without a judgement call. A **colliding** one still
refuses, because resolving two lanes' edits to one file is still not a cadence's decision.

### The deadlock this had settled into

Worth naming because no bounded tick can see it. The publisher waits on `behind_origin`;
`behind_origin` clears when the shared tree advances; the advance is blocked by any uncommitted work
at a path origin also touches. At turn start that was **14 paths**, of which 7 were byte-identical
to origin's copies and 7 held live work — and the two most contested were
`background/process_run_complete.py` and `background/supervisor.py`, *the files every lane is
editing to fix the wedge*. The more attention the wedge got, the more firmly it held. Six days dark
is what that costs.

## The exit test cannot read its own success

**This is the part that needs the director's eye, because it has now consumed three stretches.**

The item says: *"Finished when `episode_clean_publishes` is non-zero. That is the same exit test I
set two stretches running and I am not softening it."*

That field **resets to 0 on a clean publish that drains the queue** — by design, at HEAD and on
origin alike:

```python
episode_clean = 0 if episode_closed else ((int(prev_clean) if ... else 0) + 1)
```

It is episode-scoped on purpose, and a sibling lane's own mutation-proven control says so in its
name: `test_draining_the_queue_to_zero_closes_the_episode_and_forgets_the_publishes` — *"the null
control for the memory: episode-scoped means it MUST reset on a real close."* It has to reset, or
every later episode reads as intermittent.

**`docs/staging/` currently holds no unprocessed `run_complete_*.md` at all.** The queue is already
drained. So the very next clean publish closes the episode and writes `episode_clean_publishes: 0`
— the exact value the exit test reads as failure. The test can only pass on a clean publish that
happens while the queue still holds work, which is the one case nobody is waiting for.

The field that answers the question actually being asked — *has this publisher published cleanly?*
— is **`last_clean_publish`**, and it was nulled on close until earlier today: commit `8dfb28f9f`,
*"a clean close now says a publish happened, not merely that nothing failed."* That fix is on
origin and **is not at this tree's HEAD**, so at HEAD a recovered publisher and one that has never
run are still byte-for-byte identical.

> **Recommendation, not a question.** The exit test becomes `last_clean_publish` non-null. It is
> the same claim the director means, on the field that can carry it, and it is not a softening —
> `episode_clean_publishes` cannot express the claim at all. Proceeding on that reading; say so if
> it is wrong.

## A second defect, found by the controls that caught the first

The refusal's evidence reaches the reader through `publish_cause.write_cause`, which keeps
`evidence[:600]`. The refusal was **already 620 characters** before this turn — 450 of them the
standing *"Reconcile first / Do NOT run `surgical_land --merge`"* advice, identical on every
refusal and diagnosing nothing. That left 150 characters for the one part that tells a reader
whether they are looking at a hot origin or a real fork.

The first draft of the collision clause spent 131 of those 150. Four controls in
`test_the_publisher_dropped_a_cycle_after_a_single_lost_race_it_could_have_re_run` went red,
correctly: the attribution had been pushed off the end of the field. **Any sentence added to the
front of a capped diagnostic silently evicts the one at the back, and only a control keyed to the
survivor notices.** There was no such control; there is now.

The standing advice was shortened to 367 characters and moved behind the variable facts, so the cap
now drops the sentence a reader can look up and keeps the one they cannot.

## What landed

* `_publish_surface_collisions` — which of origin's incoming paths this commit would also write.
  Returns `[]` for *disjoint* and `None` for *could not look*, kept distinct for the reason
  `paths_blocking_fast_forward` already records: rendering them the same is how a fail-open reads
  as a clean bill. Reuses `origin_reconcile._arriving_paths` rather than asking git a third time.
* `_divergence_refusal(publish_paths=None)` — publishes when the fork is disjoint, refuses and
  **names the colliding path** when it is not, refuses when the overlap cannot be established, and
  refuses unchanged when no caller passed paths.
* `PUBLISH_EXTRA_RELATIVE` — the extra-paths tuple hoisted out of the landing site, so the
  disjointness verdict is asked over the same set the commit writes. Re-typed at two sites they
  would drift, and a verdict over a different set is not a verdict about this commit.
* Wired at all four refusal sites, including both liveness-surface ones, each over the paths it
  actually commits; re-computed after a fast-forward rather than reused, because the advance
  rewrites both sides of the question.
* Eight controls, each mutation-proven. Two mutations fired first time; the third
  (`ValueError` -> `continue`) did **not**, and establishing which of *missing test* or
  *equivalence* it was showed a missing test: the control had used one unmatchable path alone, so
  the refusal came from the empty-set guard below and never touched its subject. Rewritten with a
  mix, it fires.

Verified in a clean `git archive HEAD` extract with the change overlaid: the failure set is
**identical to the pristine-HEAD baseline over the same selection** (14 either way, all of them
git-absence artefacts of an archive extract). No new red.

## What this does not fix, said out loud

Publishing while behind still widens the fork by one commit per cycle. It widens it in paths
nothing else is touching, which is the whole claim — but *disjoint* is not *free*, and if the
reconciler stops, that grows without limit. The deadman's `[ORIGIN FORK]` page remains the alarm
that this has stopped being true.

And this does not make `episode_clean_publishes` non-zero. Nothing can, on a drained queue. The
publisher's route to a recorded clean publish is open; the field the item reads for it is the wrong
field.

## Handed on

1. **The exit test.** Read `last_clean_publish`, not `episode_clean_publishes`. Above.
2. **`8dfb28f9f` is not at HEAD.** Until the shared tree advances, a recovered publisher here still
   records as one that never ran.
3. **The advance is still blocked** by 7 genuinely contested paths. Not touched this turn: they are
   another lane's live mid-repair work, minted 10:54–11:30 today, and the `--survey`/`--content`
   route belongs to the lane holding them.
