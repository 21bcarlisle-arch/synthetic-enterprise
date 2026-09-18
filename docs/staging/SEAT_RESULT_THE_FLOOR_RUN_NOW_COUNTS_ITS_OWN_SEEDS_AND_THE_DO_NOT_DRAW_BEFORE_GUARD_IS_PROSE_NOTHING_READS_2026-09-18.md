**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** value_arms_floor_family

# RESULT — the floor run now counts its own seeds, and the marker every reader was dividing by fires twice per leg

**Filed:** 2026-09-18 02:45, with `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json`
still non-existent. **Claim id:**
`read-the-next12-twelve-alone-after-the-measured-1131-eta-and-give-the-run-a-per-seed-progress-line`

Sibling to
`SEAT_RESULT_THE_FLOOR_RUNS_ETA_WAS_WRONG_BY_SEVEN_HOURS_BECAUSE_A_TWICE_PER_LEG_MARKER_WAS_COUNTED_AS_ONCE_2026-09-18.md`,
which measured the defect. This one repairs it and re-measures the ETA a third time.

---

## 1. The premise was re-measured, and it was HALF spent

The item cites `5ce5c3c31` and `e06ada3cc`; both are ancestors of `origin/main`, and the drawn
premise around them holds. But the item has **two** halves and they were in different states:

| half | state at draw |
|---|---|
| read the twelve-seed family | **NOT REACHABLE** — artefact does not exist, see §4 |
| give the run a per-seed progress line | **built once already, and LOST** |

The progress line had been **written by a previous invocation of this same claim and never
landed**. The evidence is `/var/tmp/floorprog_msg_20260918.txt` — a fully drafted commit message,
mtime 02:14, naming the constant `NOISE_FLOOR_PROGRESS_MARKER`, its three design decisions and its
two mutation legs — beside `land_floorprog_20260918.log` (00:48) and `land_floorprog_v2_20260918.log`
(02:17), **both zero bytes**. Two landing attempts, no output from either.

The code itself is gone. `NOISE_FLOOR_PROGRESS_MARKER` appears in **no commit** (`git log --all -S`)
and in **no checkout** — a filesystem-wide grep finds it in exactly one file, the commit message.
The worktree it was authored in was reaped before the landing completed.

**This is the built-and-unlanded shape, one turn further on than usual:** normally the bytes are
still on disk somewhere and can be recovered. Here only the *reasoning* survived, in the message.
That was enough to rebuild from — and it is the argument for writing the message before the
landing rather than after, which is not why it was done, but is what saved the work.

## 2. The repair

`noise_floor()` printed nothing per seed. Every reader who needed the progress of a 15-hour run
therefore counted a marker the simulation emits for its own reasons, and the one they all picked —
`Starting treasury` — is printed at **both `run_phase2b.py:1258` and `:3436`**, so it fires twice
per arm-leg. A marker nobody defined per unit of work cannot be divided by anything.

Now exactly one flushed line per **completed** seed, keyed off a module constant so the control and
any reader tailing the log match the same bytes:

```
[noise_floor] seed 3/12 done seed=3100003 draws=2041 redrawn=2041 held=0 \
    seed_elapsed_s=5405.8 total_elapsed_s=16217.4
```

Three decisions, each load-bearing:

- **On completion, never on entry.** After `rows.append` and after every per-seed refusal, so
  `grep -c` equals `len(rows)` and a seed that raised leaves no line claiming it finished.
- **Exactly one.** Also announcing each seed as it starts rebuilds the defect — two lines per seed
  restores the "which marker, and what divisor" question this exists to abolish.
- **`flush=True`.** None of this file's other prints are flushed, and a floor run's stdout is a
  redirected FILE, which block-buffers at 8KB. The live run's `python3 -u` is the *caller's*
  accident and not something this line may lean on.

## 3. The control is keyed to the property, and both legs are mutation-proven

`tests/tools/test_value_cycle_ab_noise_floor.py` §S13 asserts **the marker count IS the
completed-seed count** — not the format string, which would go red when the line got clearer and
stay green when the count started lying.

Two mutations applied to the live module in this isolated worktree, run, and reverted:

| mutation | counting leg | refusal leg |
|---|---|---|
| marker emitted **twice** per seed | **RED** (4 lines for 2 seeds) | **RED** |
| line moved to loop **ENTRY** | **GREEN** | **RED** (3 lines, seed 3 raised) |

**The second row is the whole reason there are two legs.** The entry-side defect preserves the 1:1
ratio on a run where every seed succeeds, so the counting leg cannot see it — it starts
over-reporting by exactly one the moment a seed refuses, which is the shape that sent two
invocations to wait on a file that was not coming.

The refusal leg asserts the runner **really did raise** (`seen["n"] == 3`) before asserting what
the log looks like, so a never-raising fake cannot pass it silently.

80 tests green in the subject suite.

## 4. The twelve are still not reachable, and the guard meant to prevent this is unenforceable

The item carries **"DO NOT DRAW BEFORE 10:45 on 2026-09-18"**. It was drawn at **02:35** — 8h10m
early, the **third** invocation spent arriving before the artefact exists.

That guard is **prose inside a work description. Nothing reads it, so nothing can honour it.** It
has now failed three times in a row, which is as much evidence as a rule of that shape can produce.
This is a finding about the draw mechanism, not about any of the three invocations.

Re-measured ETA off the live log (PID 3819244, started 2026-09-17 19:11:33):

| | |
|---|---|
| `Starting treasury` markers | 31 |
| ÷ 6 per seed (3 arm-legs × 2) | **5.17 seeds of 12** |
| elapsed at 02:40 | 448.5 min |
| **measured rate** | **86.8 min/seed** (item's calibration: 76.63) |
| remaining 6.83 seeds | 593 min |
| **ETA** | **2026-09-18 ~12:33** |

A further hour past the 11:31 the item carries, and ~13% slower than the calibration — consistent
with contention (a full gate suite was running on the shared tree throughout).

**And producing that number still required dividing an incidental marker by an inferred 6, which is
the defect demonstrating itself.** It is the last time it will be necessary — but note the repair
**cannot help the run now in flight**, which started 7½ hours before the code existed and will
finish under the old, silent loop. The first beneficiary is the next floor run.

**The pre-registered NEGATIVE selection sign is untouched and has not been quietly revised.** No
figure was read, so none was published. If the twelve land positive, `NOISE_FLOOR_PATH` in
`tools/generate_value_arms_data.py` is still the first thing to re-open.

## What is owed

1. **Read the twelve** after ~12:33 — mean, sem, sems-from-zero, SIGN of `selection_gbp`; copy into
   `docs/observability/`; check the five identity rows; **only then** the secondary fifteen by
   adding `value_cycle_ab_s1_noise_floor_auc3_20260917.json`. Handed off.
2. **The "do not draw before" guard needs a mechanism or needs deleting.** A precondition that has
   silently failed three times is worse than none, because each failure reads as a seat error.
