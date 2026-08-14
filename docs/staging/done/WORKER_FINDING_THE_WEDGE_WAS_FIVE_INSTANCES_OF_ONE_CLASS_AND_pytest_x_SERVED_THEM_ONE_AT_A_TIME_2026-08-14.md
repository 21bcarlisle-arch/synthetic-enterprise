# WORKER FINDING — the 252-cycle wedge was FIVE instances of one class, and `pytest -x` served them one per tick

**Severity:** BLOCKING · **Lane:** H_harness
**class:** uncommitted-and-orphaned-work
**found:** 2026-08-14, unwedging the publish gate (252 consecutive failures, ~7,163 min)
**status:** INSTANCES LANDED (see the commit list below — each verified in a tree, not in a status
line). CLASS OPEN, and now measured well enough to build the control.

## What was observed (observed-with-evidence)

The publish gate had been RED at every HEAD since `19d8f94da`. It was not one defect with a long
tail. It was **five separate instances of the same mechanism**, stacked behind `pytest -x`:

| # | red the gate printed | what was actually missing | where it was |
|---|---|---|---|
| 1 | `AttributeError: module 'tools.simplifications_store' has no attribute 'atom_name'` | `atom_name` + the 297 store docs | INDEX, never in any tree |
| 2 | `PB3_book_growth_as_earned_outcome: map notes_rehomed=['name'] != store fields ['discover_note','name']` | one line of `maturity_map.yaml` | working tree, unstaged |
| 3 | `growth_desk.py — gbp × 13 (register allows 0)` | its `PORTABILITY_DEBT.md` row | INDEX, never committed |
| 4 | `E402: baseline 193, now 195` / `F811: baseline 95, now 96` | both repairs, comments and all | INDEX, never committed |
| 5 | (would have been next) | `policy_cost_coverage` supplier + its test | unstaged / **untracked** |

Instances 1, 3 and 4 were each **already written and sitting in the index**. Nobody had to diagnose
them. They had to be *committed*.

## The two mechanisms, stated separately because they need different controls

**(a) A pathspec commit names the paths the author EDITED, not the paths their change OBLIGES.**
Already filed twice. Instance 3 widens it past "supplier symbol": what `growth_desk.py` owed was not
code at all, it was a row in the register its own control reads. The obligation can be a *data* file.

**(b) `pytest -x` turns a stack of N independent reds into N sequential ticks.** This is the part
nothing has filed. The gate stops at the first failure, so each tick sees exactly one cause, fixes
it, and hands the next one to the tick after. Five causes therefore cost five diagnose-fix-verify
cycles *at minimum*, and in practice far more, because between them the false-FIXED records
(`WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED...`) sent ticks looking elsewhere. The
wedge's duration was set by the SERIALISATION, not by the difficulty of any one red.

`-x` is right for the *blocking* decision — one red is enough to refuse a publish. It is wrong for
the *diagnostic* the wedge draw reads. Those are two different questions being answered by one run.

## The repairs, in the order they landed

* `c78b7a118` — `atom_name` + 297 store docs + the PB3 map line + the orphan-baseline freeze
* `0e5e5e5ba` — the `growth_desk.py` portability-debt row
* (third landing, this tick) — the E402/F811 repairs and the `policy_cost_coverage` unit

## The controls this actually asks for (R15 — each must be able to fail)

1. **A manifest claiming a path LANDED must be checkable against a tree.** Already proposed by
   `WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED...`; still the right build. Must read
   `git ls-tree`/`git cat-file`, never `git status` alone (TAUTOLOGY), and must RED on an
   unreadable ref rather than pass (FAIL-SILENT).
2. **The wedge draw should see the WHOLE red set, not the first one.** When the publish gate reds,
   re-run once with `-x` dropped (`--maxfail` high) purely to *report*, and put the full list in the
   doorbell. The blocking verdict stays `-x`. Mutation test: inject two independent reds and assert
   the doorbell names both — a version that names one fails.
3. **A dirty-index census on the wedge path.** When the gate is red, the draw should state how many
   paths sit in the index uncommitted. In this episode that number was 311, and it was the answer
   every time. Fails correctly by construction: with a clean index it reports zero and adds nothing.

Control 2 is the cheap one and would have collapsed five ticks into one. It is the recommendation.

## Method note worth keeping

The ruff ratchet's own finding called locating its violations "a bisect over the commits since
2026-08-06". It is not. Extract the freeze commit and HEAD, run the census's own ruff invocation in
each, and diff the violation **location sets grouped BY FILE**: line-number churn cancels inside a
file, and the true delta falls out in a single pass. Two files, +1 each, in about a minute. Recorded
because the bisect framing is what deferred the repair in the first place.
