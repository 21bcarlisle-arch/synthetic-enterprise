**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The wedge reproduced on demand, and the repair is green in the same extract — one variable, nothing else moved

Claim id: `trace-where-26d4120ab-enters-the-value-arms-comparison`. Landed `9839fd5a4` (promoted to
`origin/main` from `5ee58a4b1`). Diagnosis and trace:
`docs/staging/SEAT_FINDING_THE_GATES_EXTRACT_POINTS_HEAD_AT_THE_PARENT_SO_A_CONTROL_READING_HEAD_GRADES_THE_PREVIOUS_COMMIT_2026-09-24.md`.

## The prediction, written before the extract was built

From the finding, before any of this was run: *the asymmetry is a property of how the extract is
BUILT, not of the producer* — specifically, `surgical_land._make_standalone_repo` writes the PARENT
commit into `.git/HEAD` while the working tree is `result_tree`, so `git show HEAD:` inside the gate
reads the commit BEFORE the one being graded.

That predicts something falsifiable and specific: **build an extract whose parent's
`publish_provenance.json` names `b2b233ef7_20260922T043219Z` and whose working tree names
`26d4120ab_20260924T002107Z`, and the pre-repair control must red with exactly the two lines the
gate recorded — with no merge, no daemon, and no gate cycle involved.**

## It did, byte for byte

Built with `surgical_land`'s own `_make_standalone_repo` — not a hand-rolled imitation, so the thing
under test is the tool's real behaviour. Working tree `origin/main`, parent `7d0c8ded7`:

```
HEAD (=parent) provenance : run_output_b2b233ef7_20260922T043219Z.json
working tree  provenance : run_output_26d4120ab_20260924T002107Z.json
```

Pre-repair control, spliced back into that same extract:

```
- un_output_26d4120ab_20260924T002107Z.json
+ un_output_b2b233ef7_20260922T043219Z.json
```

Character-for-character the diff the previous finding recorded from three real gate cycles. The
truncated `un_output_` is the string differ skipping the shared `r`, in both.

| in the SAME extract, same parent, same working tree | verdict |
|---|---|
| pre-repair `..._answers_THE_SAME_from_HEADs_committed_bytes` | **RED**, the two run ids above |
| post-repair `..._NAMES_ONLY_RUNS_ITS_OWN_TWO_INPUTS_NAME` | **GREEN** |

One variable. The parent, the working tree, the producer and the machine are identical across those
two rows; the only thing that changed is which property the control asserts. The previous finding
could not attribute its red because three things differed between its green runs and its red runs
(tree, base, and extract-vs-worktree); this separates them.

The `-`/`+` direction also settles which side was which, which the earlier reading had to infer:
`-` is `live` (the working tree, the commit being gated, 09-24) and `+` is `from_head` (the parent,
09-22). The gate was grading the previous commit and reporting it as the tree oscillating.

## The repair can still fail — both rungs mutation-proven

Not asserted, run. Subject file restored from backup after each, and `git diff --stat` confirmed
clean before landing:

| mutation | result |
|---|---|
| `_last_verified_run` reads the pre-2026-09-10 third input (`docs/reports/run_output_latest.json`) | **RED**, naming `last_verified_run_id` |
| the committed dashboard names no run (`DASHBOARD_PATH` at a tracked, run-silent file) | **RED** on the null rung |
| *(first attempt)* `_last_verified_run` bypasses the module global for the literal live path | **GREEN — a no-op**, recorded below |

**The green one is kept because it is the trap, not because it is tidy.** It looked like a faithful
"input from outside the declared path" mutation and it proved nothing: this worktree's working copy
of `publish_provenance.json` is byte-identical to HEAD's, so the bypass it introduced read the same
bytes. A green mutation has three causes and "the mutation was a no-op" is the one that flatters
nobody. The second mutation was chosen specifically because its third input names *no* run at all,
so it cannot coincide with the declared one.

The null rung is what stops the three field legs being vacuous: every one of them compares the
verdict against a blob field, so all three pass on `None == None` — which is exactly what a
run-silent dashboard produces. Mutation two above is that rung's own proof.

## State at the time of writing

`origin/main` carries the repair (`9839fd5a4`). The shared tree `/home/rich/synthetic-enterprise`
is 15 behind and 2 ahead — it was 13 behind and 4 ahead an hour ago, so it is draining. Closing the
remaining fork is `origin_reconcile`'s cadence, and the leg that refused its only door no longer
refuses it.

## What is NOT established here, and is left open rather than implied

1. **That no OTHER control in the tree reads `git show HEAD:` and means "this commit".** This one
   was found because it wedged a lane. The same mistake is invisible anywhere it happens to be
   green, and it is green in every working tree by construction. Not swept — a census of that
   pattern is separate work, and it is handed on rather than claimed as covered.
2. **That the shared tree's fork closes.** The blocker is gone and the tree is draining; that the
   daemon actually finishes is an observation nobody has made yet.
3. **The three orphaned commits.** `d5f71b0ef`, `c0091062a` and `8db5d9c92` were reset away in this
   worktree (reflog `HEAD@{4}`), are in no ref, and the drawn item's claim that they are "gated-green
   and cannot promote" is spent. `c0091062a`'s site/proof work (49 added lines) is genuinely absent
   from `origin/main`; `d5f71b0ef`'s `deploy_restart` work is SUPERSEDED — HEAD's treatment differs
   by 321/300 lines, so landing the orphan would revert it. Both finding documents are in no commit.
   Recovering them is different work and is handed on, not folded in here.
