**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** publish-gate-wedge

# WORKER RESULT — the gate's red had a repair sitting on origin, and the reconciler that carries it has lost 95 races to the gate's own lock today

**Drawn as:** PUBLISH-GATE WEDGE self-refill (RUNG 1, PRIORITY ZERO), doorbell 2026-09-18 ~22:00Z
**Class:** `publish_gate_and_wedge`

---

## The one-line cause

**The red test is not broken and never needed repairing here: it was repaired on `origin/main` at
21:19 and 21:48, and the shared tree is 15 commits behind and could not take it — because the
mechanism that closes the fork refuses while the publish gate holds its run lock, and the gate was
red *precisely because* the tree was behind.** Two correct mechanisms holding each other shut.

---

## The timeline, measured

| When | What |
|---|---|
| 15:10 | `2984864c7` lands **on the shared tree**: the residual disposition learns to speak (`_nothing_answered` now emits `CANNOT ANSWER, not 'nothing landed': …`). This is the PRODUCER half. |
| ~15:50 | The publish gate begins failing. Five reader legs across three suites still assert `evidence == ""`, which the producer can no longer emit. |
| 15:50→22:00 | **11 consecutive gate failures.** For most of this window there was genuinely no fix to fetch. |
| 21:19 | `c2f1fb822` lands **on origin/main** (a sibling lane, isolated worktree): three of the legs re-keyed. |
| 21:48 | `1cbf684ed` lands on origin/main: the remaining legs, and the predicate gets one home — `tests/background/residual_voices.py` (`could_not_ask` / `looked_and_found_nothing`). |
| 21:39, 22:03 | Gate runs #3 and #4 grade a throwaway checkout of **local** `HEAD 7fe96413d`, which has the producer and not the readers. Red, necessarily. |

The red as the gate reports it:

```
tests/background/test_a_swept_row_names_which_of_the_three_dispositions_it_was.py:238
    assert got[CREDITED_ID]["evidence"] == ""
E   AssertionError: assert 'CANNOT ANSWE...s never asked' == ''
```

**This was never one test.** The doorbell said "it is ONE test — repairing it should clear the
wedge". That is the fail-fast verdict talking: `-x` stops at the first. The class is **five legs
across three suites**, and origin's repair names all five.

---

## Why the repair could not reach the tree — and this is the part worth keeping

`background/origin_reconcile.py` owns closing the fork, merges in an isolated worktree, and
**refuses while the gate holds its run lock**. That refusal is correct and director-ruled
(2026-09-02): a push landing under a running gate turns a green gate into a non-fast-forward at the
last step and spends the whole run.

But it runs on the deadman cadence, which *samples* for a window between gate runs. Counted in
`docs/observability/deadmans-switch-log.md`:

| Date | `ORIGIN FORK (GATE_RUNNING)` refusals |
|---|---|
| 2026-09-15 | 34 |
| 2026-09-16 | 35 |
| 2026-09-17 | 104 |
| 2026-09-18 | **95** |
| since 2026-09-02 | **737** |

**The deadlock is symmetric and neither side is defective.** The gate is red because the tree is
behind. The tree stays behind because the reconciler will not move under a running gate. The gate
re-runs on the run-complete queue, which the wedge itself keeps refilling. Each mechanism is doing
exactly what it was built to do.

The reconciler's own docstring records that it "closed 41 real forks unaided" on 2026-09-04 — so it
does win this race when the gate is idle. What changed is the gate's duty cycle: a wedged gate runs
almost continuously, so the window it samples for closes as the fork it must fix grows.

---

## Second blocker: eleven contested working-copy paths

Even with a window, the fast-forward was refused by 11 paths. **Every one was the stale side.**
Checked individually rather than assumed:

**4 modified tracked paths.** Working copies dated 2026-09-18 10:24 and 17:37 — an *earlier,
weaker* draft of the same repair, asserting the property inline (`LENDER_ID not in evidence`).
Origin's versions supersede them by routing through the shared `residual_voices` predicate home,
which local `HEAD` does not even contain (`git cat-file -e HEAD:tests/background/residual_voices.py`
→ does not exist). Overwritten with origin's bytes.

**7 untracked staging docs.** Six byte-identical to origin's copies. The seventh
(`SEAT_RESULT_THE_DRAWN_ITEM_WAS_ALREADY_LANDED_UNDER_ITS_OWN_ID_…`) differed: ours 6,873 bytes,
origin's 10,445. `comm` over sorted lines shows the **only** line ours holds that origin lacks is
the heading `## 5. Still owed`, which origin renumbered to `## 7.` after adding two sections. A
strict superset. Removed.

All 11 are backed up out-of-repo at `/var/tmp/unwedge_backup_20260918T2205Z/` — nothing was
discarded on inference, and the diff direction was checked per path before writing.

---

## Prediction, written before it resolved

**Recorded at 22:07Z, while gate run #4 was still in flight:** that run grades a checkout of
`7fe96413d`, which carries the producer and not the readers, so **it will be RED on the same test —
failure #4, not a recovery.** The wedge clears only when `origin/main` reaches the shared tree.
Confirm or refute against `docs/observability/sim-runner-log.md`.

---

## What was done

1. The 11 contested paths cleared to origin's bytes (backed up first, each verified superseded).
2. `/var/tmp/unwedge_race_reconcile.py` — a **one-shot racer**, not a daemon and not a new rule. It
   polls the same lock `origin_reconcile` polls, at 2s instead of a cadence, and calls the **same**
   `reconcile()`. It re-implements no merge, no gating, no push; it changes only *when* the existing
   call is made. It carries its own deadline and is to be deleted once the fork is closed.

**The racer is a workaround and should not become the fix.** The structural answer is that the
reconciler needs a window the gate cannot starve — the gate releasing its lock should *hand off* to
the reconciler rather than leaving it to re-sample a cadence later. That is a design question for
the seat, filed here rather than built: building it now would be a new mechanism minted inside an
incident, which is how this tree got 117 harness atoms.

---

## Honest limits

- **The 11-failure episode is not one cause.** Only the failures from ~20:41 are established as this
  test. The earlier ones in the 6-hour window are *not* attributed here and this document does not
  claim them.
- **The repair is ~45 minutes old, not 6 hours.** For most of the wedge there was nothing to fetch.
  The reconciler's 95 lost races are real and are the reason the fix has not landed *since* 21:19 —
  they are not the reason the wedge began.
- **Whether the merged tree is green is not yet established.** Origin's suite measured 4 passed /
  5 skipped in a `git archive` extract; the skips are the extract's missing `.git`, not a result.
  The merged tree must be graded by the gate itself.
