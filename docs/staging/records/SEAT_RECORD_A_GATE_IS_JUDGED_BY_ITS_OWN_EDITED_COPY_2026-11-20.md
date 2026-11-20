**Severity:** BLOCKING · **Lane:** H_harness · **Atom:** `unminted` (steer `gates-judge-from-the-base`)

# A gate is judged by the change's own copy of itself: confirmed (2026-11-20)

This is step 1.1 of `docs/staging/advisor/DIRECTOR_STEER_GATES_JUDGE_FROM_THE_BASE_PROPERTY_TESTS_FOR_BILLING_AND_DIFF_TRIGGERED_CHECKS_2026-11-20.md`:
"Can a commit that weakens a gate, or a module it imports, pass under the weakened version?" **Yes.** It is demonstrated
below and the fix is shown working. Nothing weakened was landed. The steer stays in the queue for steps 1.2–1.5, item 2
(property tests) and item 3 (diff-triggered checks).

## Why it happens

Every line of `tools/git-hooks/pre-commit` runs a gate as `python3 -m tools.<gate>` or `python3 tools/<gate>.py`, with
cwd set to the root of the tree being committed. Python puts that root first on `sys.path`, so the gate that runs is the
committing tree's copy, and so is every module it imports.

- **`git commit`** takes the hook *script* from `core.hooksPath`, which is the shared tree's working copy. That copy is
  neither the base nor the change: it was 32 commits behind origin today, which is what `tools.live_hook_drift`
  reports. The *gates* the script calls still come from the change.
- **`surgical_land`** (the sanctioned door) runs the extract's own `tools/git-hooks/pre-commit`
  (`tools/surgical_land.py`, `HOOK_REL`). So the change supplies the script **and** every gate. On the door we tell
  every lane to use, a change can rewrite whatever judges it.

## The demonstration (throwaway worktree off origin/main, removed afterwards)

One gate is enough to settle it, and the cheapest one is `tools/ukds_microdata_refusal.py`. I staged an empty file
named `probe_not_microdata.dta` (not microdata; the gate refuses on the suffix) and ran the hook's own line,
`python3 -m tools.ukds_microdata_refusal --staged`, three ways against the same index:

| Gate that ran | What it was | Exit |
|---|---|---|
| origin/main's copy, in the change's tree | base | **1** (refused, "a statistical-package microdata file (.dta)") |
| the change's copy, with `found = violations(...)` replaced by `found = []`, also staged | weakened, as the hook would run it | **0** (passes) |
| origin/main's `tools/` from `git archive`, run with `PYTHONPATH=<base> python3 -P -m ...` from the change's root | base, materialised | **1** (refused) |

The third row is the shape of the fix, and it already works. `-P` stops cwd being put first on the path, so the base
copy is the one imported, while `--staged` still reads the change's index. The first row is the control: the probe
file is one the gate refuses.

## What this does not yet show

- **Only one gate was probed.** The mechanism is the same for every line (all of them are `-m tools.X` or `tools/X.py`
  from cwd). But gates that read *data* from the tree, such as ratchet baselines, `*.mode` files or frozen lists, have a
  second channel. A change can loosen a baseline file without touching any code. Judging from the base has to say
  which files are the gate's own (code and baselines, taken from the base) and which are the change under judgement
  (read from the change). That split is the design question for step 1.2, and it must be settled before observe mode.
- **Cost is not measured.** `git archive origin/main` is about 650 MB. `tools/` alone is 13 MB, but gates import
  `background/`, `company/` and others. A persistent read-only worktree at origin/main, advanced by the reconciler,
  probably avoids materialising a tree on every commit. This is unmeasured.
- **Bootstrapping (step 1.3).** A legitimate gate fix that the old gate refuses must be split. Observe mode (step 1.4)
  is what shows how often that happens before anything is refused.

## Next

Step 1.2–1.5, handed on as a continuation: write the base-or-change split for each gate's files, build observe mode
(log what judging-from-base would have refused, refuse nothing), then add the mutation control: a change that
weakens a gate must be caught.
