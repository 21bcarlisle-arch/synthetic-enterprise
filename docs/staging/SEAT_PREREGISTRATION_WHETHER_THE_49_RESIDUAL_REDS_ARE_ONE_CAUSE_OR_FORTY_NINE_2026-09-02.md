# [SEAT PRE-REGISTRATION] Whether the 49 residual HEAD reds are one cause or forty-nine

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`
**Filed:** 2026-09-02, BEFORE any traceback is read. Continues
`SEAT_PREREGISTRATION_WHETHER_THE_TMPFS_DIAGNOSIS_EXPLAINS_THE_830_RED_2026-09-02.md`, which
graded run 2 and ended by naming exactly this as unanswered:

> `FileNotFoundError x29` is the dominant cause and was 2 in run 1. Fourteen-fold, unexplained,
> flagged under C4 above, and **it is not assumed to be the same thing as the 26 `sim` reds until
> somebody reads a traceback.**

This files what I expect before I read one, so the answer cannot be retrofitted.

---

## Why this is the next thing and not more grading

Run 2 is graded (4 confirmed / 1 refuted / 1 dead-band) and its 49 reds are drawn: the register
sits at rank 37, position 8, in the live `work_queue()` — measured, not argued. So the census's
question is answered and the **backlog's** question is not. The register names 49 subjects. Nobody
has established whether that is 49 pieces of work or a much smaller number wearing 49 node ids,
and **the draw cannot be sized until somebody says which.** A count with no cause is not
actionable — the same defect the census's own message carried until `bc57c8e30`.

## The population, from the store, before I touch it

49 currently red at `f5b19b43f`. Of these, 39 were first seen in run 2 and 10 are the C3
residuals at `runs_red: 2`.

| file | red nodes | first seen |
|---|---:|---|
| `tests/sim/test_renewable_capacity_trend.py` | 25 | run 2 |
| `tests/simulation/test_publish_market_feed.py` | 4 | run 2 |
| `tests/test_fidelity_emitter.py` | 3 | run 2 |
| `tests/tools/test_billing_tab_fix.py` | 2 | run 1 (C3) |
| `tests/simulation/test_home_move_undeliverable_win.py` | 2 | run 1 (C3) |
| `tests/background/` | 2 | run 2 |
| eleven other files | 1 each | mixed |

Causes histogram for run 2, which the census's own docstring says is **a floor on named causes,
never a partition**: `FileNotFoundError` 29 · `AssertionError` 13 · `TypeError` 3 · `IndexError` 1.
These sum to 46 against 49 reds, so at least three reds print no type name at all.

## The clauses. Each graded separately; the split reported, including any clause refuted.

**P1 — the big file is ONE cause, not twenty-five.** The 25 red nodes in
`tests/sim/test_renewable_capacity_trend.py` share a single proximate cause, such that one repair
clears ≥ 20 of them. **Refuted if they resolve into ≥ 5 distinct proximate causes**, in which case
that file is a genuine multi-defect backlog and must be drawn as more than one item.

**P2 — the dominant cause is a MISSING ARTEFACT, not a logic defect.** `FileNotFoundError x29` is
the largest bucket and 29 ≈ 25 + 4, the two files first seen in run 2. I predict the 29 are
dominated by those two files and that the missing thing is a **data or fixture artefact absent
from the census's subject checkout** — i.e. an artefact the census cannot see, not code that is
wrong. **Refuted if the `FileNotFoundError`s are spread across ≥ 6 files, or if the missing path
is one the checkout demonstrably does contain.**

**P3 — and if P2 holds, this is a CENSUS defect as much as a code defect.** `head_subject_checkout`
calls `prc._overlay_untracked_data(tmp)` precisely so that untracked data reaches the subject. If
the missing artefact is untracked data that the overlay did not carry, then **the census is
manufacturing reds that do not exist at HEAD for anybody else**, and the register is asking for
work that is not owed. **Refuted if the missing artefact is tracked in git** — in which case the
checkout is faithful and the red is real.

> P3 is the clause that matters and it is the one I most expect to be wrong. It is written down
> because a census that invents its own reds would be the same shape as R15's fail-open, one level
> up: a control whose subject is not the thing it claims to measure.

**P4 — the ten C3 residuals are NOT the same cause as the 39.** The ten have survived two censuses
and an environmental change that removed 781 of their neighbours; the 39 appeared at once. I
predict **no overlap of proximate cause** between the two groups. **Refuted if ≥ 3 of the ten fail
for the same proximate cause as the dominant bucket.**

## What I will run, and the constraint on it

**One test module at a time, never the suite.** A full-suite `process_run_complete` (pid 581333)
has been live on the shared tree throughout, and a second heavy run beside it would manufacture
the failure being measured — the mistake run 2 already made against its own constraint 1. Reading
a traceback needs one module, not thirty thousand tests.

Evidence for that constraint is a pasted `ps` line, not a recollection of my own behaviour.

I run in an isolated worktree at `e3830f542`, **not** the census's subject `f5b19b43f`. That is a
named limit, not a detail: a red I reproduce here is evidence about the cause and **not** evidence
about the count, because the trees differ. Any node that does not reproduce is reported as
"did not reproduce at a different commit", never as "fixed".

## What is owed when it returns

The four clauses graded beside their result, including any refuted; the 49 restated as however
many pieces of work they actually are; and — if P3 holds — a finding against the census itself.

---

# GRADED IN FULL, 2026-09-02 — 4 confirmed, 0 refuted, and P3 confirmed by a mechanism I named wrongly

Measured from `/var/tmp/se-seat-executor` at `e3830f542`, one module at a time. The full finding
is `SEAT_FINDING_THE_CENSUS_OVERLAYS_ITS_LAUNCH_TREES_DATA_AND_MANUFACTURES_THE_REDS_IT_REPORTS_2026-09-02.md`.

## The split, clause by clause. Not averaged.

| clause | threshold | observed | verdict |
|---|---|---|---|
| P1 the big file is ONE cause | ≥ 20 cleared by one repair (refuted ≥ 5 causes) | **1 cause, 25 of 25** | **CONFIRMED** |
| P2 dominant cause is a MISSING ARTEFACT | not a logic defect (refuted if spread ≥ 6 files) | **2 files, absent cache** | **CONFIRMED, with a correction** |
| P3 it is a CENSUS defect | refuted if the artefact is tracked | **`.gitignore:3:sim/cache/`** | **CONFIRMED, mechanism restated** |
| P4 the ten C3 residuals are a different cause | refuted if ≥ 3 share it | **0 of 10** | **CONFIRMED** |

## P1 — CONFIRMED, at the ceiling

`25 failed, 41 passed, 1 xfailed in 0.16s`, and every one of the 25 printed the same line:
`FileNotFoundError: .../sim/cache/elexon_demand_full.json`. One absent file, twenty-five node
ids. The clause asked that one repair clear ≥ 20; one repair clears all 25.

## P2 — CONFIRMED, and the correction matters more than the confirmation

The dominant cause is a missing artefact, not a logic defect, and it is concentrated in two files
rather than spread across six. **But the arithmetic I offered for it was wrong.** I wrote that
`FileNotFoundError x29 ≈ 25 + 4`, the two files first seen in run 2. It is not:
`tests/simulation/test_publish_market_feed.py`'s four reproduce as `assert None is not None` and
`assert 0 == 3` — **AssertionError, not FileNotFoundError** — because the price feed fails open and
returns `None` where the capacity trend raises. Same absent cache, different exception name.

So **four of run 2's 29 `FileNotFoundError`s are not located by this reproduction.** They are
recorded as unlocated, not attributed. This is the third time on this subject that the cause
histogram has been treated as a partition when the census's own docstring says it is a floor —
I did it in the very clause that quoted the docstring saying so.

## P3 — CONFIRMED, and I named the wrong mechanism

I predicted the overlay **"did not carry"** untracked data into the subject. What it actually
does is worse and is the reason it was invisible: **it carries the wrong tree's.**
`_overlay_untracked_data` resolved its source as `PROJECT_DIR / rel`, and `PROJECT_DIR` is the
tree the module was imported from. Reproduced with the census's own `head_subject_checkout`:

```
subject sim/cache exists: True | symlink: True
  resolves to: /var/tmp/se-seat-executor/sim/cache
  entries: ['elexon_ssp_live_rolling.json']       <- 1 of the machine's 12
elexon_demand_full.json present: False
```

A symlink that exists and points somewhere real is why no error was ever logged: the overlay
believed it had succeeded. My predicted mechanism would have left `sim/cache` absent and been
obvious. **The clause is confirmed and my reasoning for it was not the reasoning that was true.**

### The scope limit I did NOT write down, and it is load-bearing

P3 said the census "is manufacturing reds that do not exist at HEAD for anybody else". That is
true of a **worktree-launched** census and false of the nightly one:
`head-green-census.service` sets `WorkingDirectory=/home/rich/synthetic-enterprise`, which holds
all twelve cache files. **Run 1 (nightly) is clean. Run 2b (hand-launched from this worktree) is
contaminated. Tonight's run at 03:34 is clean.** I did not bound the clause that way when I wrote
it, and an unbounded version of it would have condemned the whole instrument.

## P4 — CONFIRMED, 0 of 10

None of the ten C3 residuals lives in either affected file, and none carries the absent-cache
cause. The ten survived a run whose 29 largest reds were an artefact of the launch tree, which
makes them *more* solid, not less: they are nightly-observed, they reproduce here, and they are
the honest first draw.

## What this does to the 49

**The 49 is not 49 pieces of work.** At least 29 are the launch tree. The residual owed at HEAD is
**≤ 20**, with the C3 ten as its confirmed core, and the register will shed the rest on the next
run from a corrected tree — by passing, not by anybody forgiving them.

## Constraint compliance, pasted rather than recalled

Both measurements ran one module at a time, never the suite, beside a live
`process_run_complete` full suite that was left undisturbed:

```
581333    1363 /usr/bin/python3 -m pytest tests/ -q --tb=short -m not operational and not ...
```

That process was still running at the end of this work.
