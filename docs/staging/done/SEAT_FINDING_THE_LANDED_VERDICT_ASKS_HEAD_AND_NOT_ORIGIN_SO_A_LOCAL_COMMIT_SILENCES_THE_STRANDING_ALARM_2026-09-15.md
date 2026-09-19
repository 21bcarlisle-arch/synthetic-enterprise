**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the two finished runs' artefacts reach origin and the envelope renders)

# The stranding alarm asks three questions and needs a fourth: a local commit silences it without making anything durable

**2026-09-15, delivery seat.** The drawn item said the [LAUNCH UNLANDED] alarm *"has fired 107
times over 106 hours saying the register claims work git says does not exist"*, and named
`docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` as untracked.

Asked of the tree the daemon actually runs in, that is no longer true, and the way it stopped
being true is the finding:

```
arms-rerun-20260910b [artefact]: LANDED -- `docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` is in HEAD
refusals: 0
```

The alarm is **quiet**. The artefact is **absent from `origin/main`**. Both at once.

## What happened

The file was committed on the shared tree's local `main` in `f3d95cc46`. That branch is **42
commits ahead of and 36 behind `origin/main`** — a fork that four `se-lane0-merge-*` worktrees
exist to close and that has not closed. `git cat-file -e HEAD:<path>` succeeds there. Nothing
else does: no clone, no CI, no other worktree, and no reader of `origin/main` can obtain those
bytes.

So the alarm did not go quiet because the stranding was fixed. It went quiet because the
stranding moved somewhere it cannot see — and the silence is **less true than the noise was**.

## The defect, in the control's own words

`launch_liveness.git_membership()` asks three questions, and its docstring is explicit about why
HEAD and the index are asked separately:

> *"`git ls-files` reads the INDEX, and a path that is only in the index has not reached any
> commit — a `reset --mixed` loses it and **no clone has ever seen it**. A control that asked only
> `ls-files` would have called such a path tracked, which is the exact reading that has already
> made one control here green while the thing it guarded was absent from every commit."*

That reasoning is correct and it stops exactly one question short. **It applies verbatim, one
level up, to its own `LANDED` verdict.** A path in HEAD on a diverged local branch has not reached
any *published* commit; a `reset --hard origin/main` loses it; and no clone has ever seen it
either. The sentence that justifies the third question is the sentence that demands the fourth.

`landing_verdict()` returns `LANDED` on `where["head"]` at `background/launch_liveness.py:343-344`.
`HEAD` is whatever this machine's branch happens to point at.

## Why this class is familiar

This repository already has the ruling *"a control asking whether a file reached git must ask three
questions, not one"* — HEAD, index, `.gitignore`. This is that same ruling, applied to itself and
found wanting: **HEAD is not durability.** The four questions are

1. is it in the index? — survives nothing
2. is it in HEAD? — survives a `reset --mixed`, **not** a re-clone
3. is it `.gitignore`d? — its absence is a standing decision, not a stranding
4. **is it reachable from `origin/main`? — the only one that means another reader can get it**

The alarm's own remedy prose says *"Land them, or record why they are not landable."* On this
repository's definitions, a local-only commit is **neither** of those things, and it satisfies the
check.

## What was done about the instance

Both artefacts the item named are now on `origin/main` by the ordinary route — `surgical_land`
then `promote_worktree_landing` — taking their bytes from git (`04dcba655`), not from the shared
tree's working copy, so no other lane's in-place edits rode along. They are byte-identical to the
blobs the shared tree holds:

| Path | blob | was |
|---|---|---|
| `docs/design/blind_envelope_arms_2026-09-11.json` | `22927e908` | staged in the shared index only — in **no commit anywhere** |
| `docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` | `bc3a9b347` | in local `main` HEAD only — **never on origin** |

## What was deliberately NOT done, and why

The envelope still does not render at `origin/main`, and landing these two files does not make it.
That was established before this turn, is recorded in
`PREREG_DOES_THE_BLIND_ENVELOPE_DELTA_APPLY_AND_RENDER_AT_ORIGIN_MAIN_2026-09-15.md` as **P3
(confirmed)**, and is unchanged: the producer that reads `BLIND_ENVELOPE_ARMS_PATH` does not exist
at `origin/main`, so `site/data/value_arms.json` there carries **no `blind_envelope` key at all**.

The verified producer delta is preserved whole as commit `04dcba655` on branch ref
`blind-envelope-landed-20260915`. Of the nine files it touches, **two are held by live claims** —
`tools/generate_value_arms_data.py` and `tests/tools/test_generate_value_arms_data.py`, claimed by
`close-the-fork-fix-the-composer-then-land-ead8f781a` and
`close-the-fork-resolve-the-six-by-rule-and-push`. Those were not taken.

Seven of the nine are uncontested, and landing them anyway was considered and **rejected**:
`site/data/value_arms.json` and `site/capabilities/index.html` would publish a `blind_envelope`
block that `origin/main`'s producer cannot rebuild. That is a **fossil figure** — correct on the
day it lands, green in every door that reads the published copy, and silently wiped by the next
regeneration, with the door going back to skipping. Publishing a number whose producer is absent
is the failure this finding is about, committed a second time on the same surface. Only the two
**inputs** were landed: a data file no producer at origin reads yet is inert, and is already in
place when the re-merge needs it.

The ordering is still forced and still correct: **the fork merge lands first, then the envelope
re-merges onto the merged producer.** These two inputs are now out of that merge's path list.

## The fourth question, built — and one prediction that did not come true

`LANDED_LOCAL_ONLY` is now a verdict: `head and publishable and not published`, and it **refuses**,
so it reaches the alarm's refusal count and its `stranded` line rather than printing as prose
nobody blocks on. `git_membership` asks `origin/main` directly.

The false positive this would otherwise have had is guarded separately. *"There is no `origin/main`
to ask"* and *"the file is absent from `origin/main`"* are opposite claims, and conflating them
would refuse every artefact in every detached `se-*` worktree and in any fresh clone — noise that
gets switched off within a day, taking the real leg with it. So `publishable` is asked as its own
question and a repository with no remote still reads `LANDED`, with the reason saying publication
was never established.

Three mutations, each caught by a different leg:

| Mutation | Caught by |
|---|---|
| ignore publication (the behaviour that went quiet) | the partition leg + the instance leg |
| conflate "no origin" with "unpublished" | the no-remote leg + 3 pre-existing legs |
| verdict refuses but `landed_check` does not count it | the instance leg's `refusals == 1` |

**PREDICTION FILED BEFORE RUNNING IT, AND IT DID NOT HOLD.** I expected the new leg to refuse for
several artefacts, on the reasoning that a 42-commit fork leaves every artefact committed on local
`main` since the divergence in the same state. Run against the real register it refused for
**none**, and the reason is not that the reasoning was wrong — it is that **the register was
rewritten underneath the measurement**, from 12 entries to 4, by another lane, mid-turn. Of the
four that remain, three are `OUTSIDE` (artefacts under `/var/tmp`, which git cannot hold) and one
is in the repository. So the live register no longer contains the population the prediction was
about, and this run neither confirms nor refutes it. Saying "it found nothing, so there was
nothing" would be the wrong reading of a measurement whose subject moved.

What the run *does* establish is the one-variable demonstration, on the file this item named:

> `arms-rerun-20260910b [artefact]: LANDED -- ... is in HEAD and reachable from origin/main`

Before this turn's push that same file, same register, same code returned `LANDED -- is in HEAD`
while being absent from `origin/main`. It is now `LANDED` for a reason that is *true*, and the only
thing that changed is the push. The verdict has stopped being satisfiable by a local commit.

## What is next

Re-run `landed_check` against the register once the fork closes and the register settles, to get
the reading this turn could not: the prediction above is still open, not disproved. Worth asking
separately why `.launch_records.json` lost 8 entries in one turn — a register that forgets is a
different hazard from one that over-claims, and this check is only as good as the records it
iterates.
