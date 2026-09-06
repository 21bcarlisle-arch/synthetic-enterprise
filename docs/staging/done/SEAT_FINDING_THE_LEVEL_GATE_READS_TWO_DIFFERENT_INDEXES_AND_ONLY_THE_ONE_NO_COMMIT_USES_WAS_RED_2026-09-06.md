**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** OPS2_publish_gate_head_worktree

# The level gate reads two different indexes, and only the one no commit uses was red

**Found:** 2026-09-06, delivery seat, working the priority-zero publish-wedge doorbell.

The doorbell said the publish gate had been failing for ~146 minutes and was blocking all
publishing. **It is spent.** Both causes it names were fixed at HEAD before the doorbell was read,
and three commits have landed since. What I found instead was a different defect, in the gate the
doorbell told me to pre-run.

---

## 1. The wedge the doorbell describes is spent

The doorbell cites the 18:33 UTC refusal as the live state. The log after it says otherwise
(all times UTC; commit times in `git log` are BST and I converted them, per the `date -d` trap):

| time | event |
|---|---|
| 18:33 | publish commit refused — **level-promotion gate**, `W1_27` missing from the map |
| 18:38, 18:48 | liveness heartbeat refused — **orphan-ratchet**, `tools.generate_weather_cells_data` has no runner |
| 18:57 | `490e3938a` liveness heartbeat **published to origin** |
| 19:02 | `1619417b7` landed |
| 19:06 | `d86402a18` landed — wires `generate_weather_cells_data` into `process_run_complete` |

Both named causes are cleared at HEAD, verified directly rather than from the log:
`python3 tools/orphan_ratchet.py` → rc=0, no output. Origin fork closed (`0` commits either way).

**Why the doorbell still fired on it.** `docs/observability/.publish_gate_state.json` still reads
`episode_failures: 4`, `episode_clean_publishes: 0`, `last_clean_publish: null`,
`wedge_since: 16:41`. The three commits that landed did not clear the streak, because only a full
`process_run_complete` cycle writes a clean publish — and the next run is held ~45 minutes. So the
record of the wedge outlives the wedge, and keeps minting priority-zero doorbells against a
condition that no longer exists. This is the same shape already on file for wedge records that name
only test reds: **the wedge record's clearing condition is narrower than its firing condition.**

---

## 2. The live defect: one gate, two indexes, opposite answers

Pre-running the cheap gates as instructed, `tools/level_promotion_gate.py` **refused**:

```
[level-gate] ❌ COMMIT REFUSED (the map's atom set is a HIGH-WATER MARK ...):
  docs/design/maturity_map.yaml: `W1_27_the_cell_decision_and_the_solar_gain_check` was in the
  register at HEAD and is not in it now, and nothing says why.
```

It was telling the truth about what it read, and what it read is a tree no commit would create.

**What was actually true.** `W1_27` is present at HEAD and present in the working tree. It was
missing from **only the shared index**, where some lane had staged a 24-line deletion of the atom's
block from `maturity_map_closed.yaml` and never committed it:

```
HEAD atoms: 339   INDEX atoms: 338
MISSING from index: ['W1_27_the_cell_decision_and_the_solar_gain_check']
```

**Why that made the gate answer two ways.** `_whole_map` resolves both halves from `:path` — the
index — and its docstring argues for this deliberately ("the index holds every tracked file"). But
`git show :path` resolves against `GIT_INDEX_FILE`, and git sets that to a **temporary** index for
a partial commit. Proven in a throwaway repo, both directions:

```
# lane X stages a change to A and never commits; lane Y commits only B by pathspec
$ git commit -m "..." -- B.txt
HOOK: GIT_INDEX_FILE=.git/next-index-4049354.lock
HOOK: git show :A.txt  -> a1          <-- HEAD's copy. X's staged change is INVISIBLE.
$ git show HEAD:A.txt   -> a1          <-- and it is not in the commit either
$ git show :A.txt       -> a2-STAGED-BY-OTHER-LANE   <-- still staged, still wedging the next read
```

So the same gate over the same tree gives opposite verdicts depending on who runs it:

- **from a partial-commit hook** — reads the temp index, other lanes' staged paths invisible, correct;
- **standalone, as the seat is instructed to pre-run it** — reads the shared index, and any lane's
  uncommitted staging is read as this commit's deletion.

`background/process_run_complete.py` commits with `git commit -m msg -- <pathspec>` (lines 5344,
6080), i.e. the partial form. **The stale entry therefore did not cause the 18:33 refusal** — that
one had its own cause, at an earlier HEAD — and I am not attributing it to this. What this defect
costs is the pre-run: a red that no commit could produce, on the exact command CLAUDE.md tells the
seat to run first to avoid burning a full cycle.

**The sharp end.** The refusal offers two remedies: restore the row, or write it into
`maturity_map_retired.yaml` naming what took the subject out of the tree. `W1_27` is at
`level_current: 3`, `level_target: 3`, closed 2026-09-06. A seat trusting the red and taking the
second remedy would have written a retirement record for an atom that is at target — a false entry
in the one register whose whole job is to separate an abolished atom from a lost one.

---

## 3. What I did

Restored HEAD's blob for the closed map into the index, which is exact: the staged diff against
HEAD was that one hunk and nothing else.

```
git update-index --cacheinfo 100644,12cbd41f9aa40c2c7ed7e416d829d9328a34e1d4,docs/design/maturity_map_closed.yaml
```

After: `HEAD 339  INDEX 339  missing: []`, and `tools/level_promotion_gate.py` is silent.

**The working tree was not touched.** A `git add` of the path would have swept 70 insertions and
122 deletions of another lane's in-flight `gain`-rehoming into the shared index. That lane's
unstaged work is intact; its later `git add` supersedes what I put in the index.

Reversible: `git update-index --cacheinfo 100644,e095d4277...,<path>` restores the stale entry.

---

## 4. What is NOT established

- **Which lane staged the deletion, and when.** The index carries no history. The likely shape is a
  `git add` from a tree that predated `W1_27`'s mint (`bbb5d2c70`), left behind because every
  commit since used a pathspec and so never consumed the index — but I did not prove it and it is
  not needed for the repair.
- **Whether any lane commits the whole index.** If one does, it would have committed the deletion
  and the gate would have been right to refuse it. CLAUDE.md forbids `-A` but a bare `git commit`
  is not forbidden anywhere I checked.
- **The 18:33 refusal's own cause.** It was a real refusal at an earlier HEAD; I did not reconstruct
  which staged state produced it, because it is spent and the tree has moved four commits past it.

## 5. The repair this points at, not made here

The gate should read **the tree the commit would create**, and it has no way to know that when it
is run by hand. The honest fix is for the standalone path to say so: when `GIT_INDEX_FILE` is
unset, a refusal sourced from a path this commit does not stage should name that it is reporting
the *shared index*, not this commit — a one-line distinction in the refusal text, not a new
control. Filed rather than built, because it changes a gate's refusal wording on the publish path
and that belongs in a commit with the map lane quiet.
