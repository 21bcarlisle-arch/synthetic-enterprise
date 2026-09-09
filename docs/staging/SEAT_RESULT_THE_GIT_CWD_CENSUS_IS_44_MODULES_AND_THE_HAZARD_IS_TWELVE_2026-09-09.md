**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the PROJECT_DIR-as-git-cwd census) · **Class:** controls_that_cannot_fail

# RESULT — the `PROJECT_DIR`-as-git-cwd census: 44 modules, 12 in the hazard class, no live defect, and one unguarded invariant

Scores `SEAT_PREREGISTRATION_WHICH_GIT_CALLSITES_ASK_THE_WRONG_TREE_2026-09-09.md`, written before
any callsite was classified. **Three of its five predictions are refuted.**

---

## 0. The drawn premise was spent before the turn started

The item `promote-the-09-08b-value-arms-pair-once-its-floor-lands` asked for the 09-08b arms/floor
pair to be promoted once the floor landed. **It had already landed by another route.**

- The floor finished at 00:29Z (`..._noise_floor_20260908b.json`, `generated_at`
  `2026-09-08T23:29:22Z` — later than the arms' `21:01:30Z`, so the stamp condition the item set is
  satisfied).
- Commit **`a0a62f918`** put BOTH onto the canonical paths in ONE commit. Verified by blob hash, not
  by mtime: `git show HEAD:...three_arm.json | md5sum` matches `..._20260908b.json`, and the same
  for the floor.
- `site/data/value_arms.json` carries `run_generated_at: 2026-09-08T21:01:30Z` — regenerated and
  published.
- `a0a62f918` is an ancestor of `origin/main`, and the shared tree is AT it. Blocker (b) — the
  shared tree could not fast-forward — is also gone.
- Item 4 (the `CURRENT_WORLD_*` judgement) was decided: both constants are **HELD** at the
  `_20260908` pair, and `composition.later_runs_in_this_world` fires naming both newer runs
  (`_20260908b` at 21:01:30Z and a further `_20260909` at 01:24:34Z). The page states its own
  staleness rather than making the two-block structure a tautology.

Nothing was re-done. The rest of this turn went to the item's **"ALSO OWED"** clause.

## 1. The population: 44 modules, 77 callsites — not 29

The item said 29 modules run git with `PROJECT_DIR` as cwd. An AST census over `background/` and
`tools/` for `subprocess`-family calls whose `cwd=` is any module-level name bound to a
`Path(__file__)…parent` chain (`PROJECT_DIR`, `PROJECT`, `ROOT`, `REPO_ROOT`, `_REPO_ROOT`) finds
**44 modules, 77 callsites**.

**My own first scan said 11, and it was aimed left** — it split the `cwd=` expression on `.` and `/`
and so matched `PROJECT_DIR` but never `str(PROJECT_DIR)`, which is the majority spelling. Recorded
because 11 would have been published as the population had I not widened it. Same shape as the
`_GBP_PER_MWH` miss: a scope regex matching one spelling of the concept.

## 2. The discriminator in the item is the wrong one, and it matters

The item asks which modules "ask a question about the shared tree". That is not the fault line.

> **In a linked worktree most of git is ALREADY shared.** Objects and ordinary refs live in the
> common dir, so `git log origin/main`, `git rev-list <sha>` and `git cat-file` answer *identically*
> from either tree. Only `HEAD`, the index, the working tree and per-worktree refs differ.

So the real discriminator is **whether a call names its subject**. `background/delivery_lane.py`
spells `cwd=PROJECT_DIR` at every one of its git calls and is **completely immune**, because each
passes an explicit commit or `origin/main`. A blanket `shared_tree()` sweep would have "fixed" it
into asking a different question.

Applying that: **65 of 77 callsites name their subject and are immune. 12 callsites in 9 modules
read the index or working tree implicitly.**

## 3. There is no live defect of the `origin_reconcile` class — and the hook chain is correct for a
reason nobody wrote down

`core.hooksPath` here is `/home/rich/synthetic-enterprise/tools/git-hooks` — an **absolute path into
the main tree**. So a commit made from a linked worktree runs the *main tree's* copy of every gate,
and `ROOT` inside those gates resolves to the *main tree*. They nevertheless gate the right commit.

**Measured, not reasoned about.** A main-plus-linked pair in `/tmp`, hook fired from the worktree:

```
HOOK cwd=/tmp/hooktest/wt
HOOK GIT_DIR=/tmp/hooktest/main/.git/worktrees/wt
HOOK GIT_INDEX_FILE=/tmp/hooktest/main/.git/worktrees/wt/index
git diff --cached --name-only   (run with cwd=/tmp/hooktest/main)  ->  ONLY_IN_WORKTREE.txt
```

Git exports `GIT_DIR`/`GIT_INDEX_FILE` pointing at the linked worktree, and **those beat `cwd`**.
That, not the `cwd=ROOT`, is why the gates are correct.

**The hazard is one edit wide, and it fails OPEN and SILENT.** Same pair, same command, with the two
variables scrubbed:

```
--- WITH inherited env (what the gates do today) --- SECOND_WORKTREE_FILE.txt
--- WITH env scrubbed of GIT_DIR ---                 (empty)
```

An empty staged list means the gate finds nothing to object to and **passes having examined
nothing**. And this repository already contains *two* functions whose entire purpose is to strip
exactly those variables — `site_lane_gate._gitless_env` and `pre_commit_test_gate._gitless_env`,
near-identical inline comprehensions, built because a git-touching *pytest* child obeying the
in-progress commit's index once corrupted it (phantom deletions). **Both are correctly aimed at
`pytest` today.** Point either at a `git` call and the gate goes quietly vacuous. One rule, two
implementations, correctness resting on an invariant nothing asserts — the VAT shape again.

## 4. What was built

`tools/git_subject_census.py` + `tests/architecture/test_a_git_call_gating_a_commit_keeps_its_git_dir.py`.

The refusal is deliberately narrow — **not** "never spell `cwd=PROJECT_DIR`" (44 modules, mostly
correct), but *"a **git** call that reads the index or working tree implicitly must not be handed an
environment that drops `GIT_DIR`"*. It takes source TEXT so the refusal is provable against a
poisoned module without editing a real gate, and the poison round runs **before** the
tree-is-clean assertion, because a green over an empty row set is the same fail-open.

**The control had a fail-open, and its own poison round caught it.** The first draft asked
`"environ" in env_source`. That passes
`{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}` — which *is* the defect, since
it mentions `os.environ` and then strips what matters. Corrected to ask what the expression
**removes**, not what it reads from. A second near-miss: clearing the one false positive
(`write_time_gate`, whose env is environ-derived and merely passed by name) by accepting bare names
would have re-opened the hole for `env=gitless`; the name is resolved through its assignment
instead, and an unresolvable name stays refused.

Current state: **77 callsites, 12 local-state readers, `check: PASS`.**

## 5. Scorecard

| # | Prediction | Outcome |
|---|---|---|
| 1 | >50 of 79 callsites are per-worktree readers | **REFUTED** — 12 of 77 by the subject test; 35 even by the coarse subcommand test |
| 2 | Fewer than 15 in the hazard class | **CONFIRMED (12)** — but see the caveat below |
| 3 | At least one NEW live defect of the `origin_reconcile` class | **REFUTED** — none. A latent unguarded invariant, not a live defect |
| 4 | Fewer than 6 modules genuinely resolve the main tree | **REFUTED** — 9 do; the item's "only 6" is an undercount too |
| 5 | The remedy is NOT to fix all 44 | **CONFIRMED** — 65 of 77 are immune by naming their subject |

**Caveat on 2, stated because it flatters me.** Prediction 2 was written against the *subcommand*
discriminator and is scored against the *subject* discriminator, which I improved mid-census. That
is a moved goalpost. Against the measure it was actually written for the answer is 35, and
prediction 2 would be **refuted**. I am recording it as refuted-on-its-own-terms.

## 6. What is next, and what this does NOT claim

It does not claim the 44 are defects; 65 of 77 callsites are correct as written. It does not claim
the hazard class is firing — it is not.

Owed, and not done here:

1. **The two `_gitless_env` implementations should become one**, in the module that already owns the
   hazard. Two copies of a rule is how the VAT shape starts, and this pair is already drifting
   (`site_lane_gate`'s strips `GIT_*`; `write_time_gate`'s strips only `GIT_PREFIX` — different
   rules, same-looking code).
2. **`shared_tree` and `shared_tree_dir` have OPPOSITE failure semantics** — `origin_reconcile`'s
   returns `None` and refuses; `seat_continuation`'s falls back to `project_dir`. Each is right for
   its own module and neither cites the other. Worth one comment in each naming the other, at least.
3. **`core.hooksPath` being an absolute path into the main tree is not recorded anywhere a reader
   would find it.** It means a gate fix landed from a worktree is *not active* until the shared
   tree's working copy carries it — which is a live trap for exactly the seat that lands gate fixes.
