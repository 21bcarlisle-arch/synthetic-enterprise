# WORKER FINDING — a repair that only commits on green cannot fix what is reddening the gate

**Date:** 2026-08-10 · **Found by:** worker tick, rung-1 publish-gate wedge #10 (~802 min red, 81 failures)
**Closed at:** `818b3212a` (pushed; `origin/main` verified equal)
**Class:** derived-artefact staleness — the class `WORKER_REPORT_FOURTH_WEDGE_CLOSED_THE_DERIVED_ARTEFACT_CLASS_2026-08-10` claimed closed. **It recurred.** R3 two-strike applies to the repair mechanism.

## The wedge, in one line

`tests/background/test_forward_attachment_register.py::test_live_tree_has_no_violations` red at HEAD:

```
[{'atom_id': 'D19_belief_gap_is_distribution_only', 'kind': 'missing_entry',
  'source': 'docs/staging/WORKER_FINDING_THE_BELIEF_GAP_IS_BLIND_TO_WHO_HOLDS_THE_BELIEF_2026-08-10.md'}]
```

The D19 mint put the atom in the map and its finding declared `**Advances:** D19_...`. Both committed.
The committed `FORWARD_ATTACHMENT_LEDGER.md` rendering predated the mint. `missing_entry`, **not**
`unknown_atom` — the derivation resolved D19 fine; only the stored projection was behind.

## The finding — the repair is downstream of the gate it exists to unwedge (observed, R9)

`_repair_derived_artefacts_in` (`process_run_complete.py:909`) ran **every cycle** and logged, every
cycle, `re-rendered 2 stale projection(s) from HEAD -- BLOCKED_ATOM_VISIBILITY.md,
FORWARD_ATTACHMENT_LEDGER.md. Committed with this run.`

It was not committed with that run, or any of the 81. The publish path commits **only after a green
gate** (`Tests FAILED - not committing`). The staleness *is* what reds the gate. So:

    repair writes tree + checkout  ->  gate reds  ->  no commit  ->  HEAD still stale  ->  repeat

The repair can only ever be transient. Its own log line asserts a commit that the control flow
downstream of it forbids whenever the repair was actually needed. **A repair whose durability is
conditional on the gate it repairs is a no-op in exactly the case it was built for.**

### What is observed vs inferred (R9)

**Observed:**
- The repair writes correct bytes. `/tmp/publish-gate-head-reused/docs/design/FORWARD_ATTACHMENT_LEDGER.md`
  contained the D19 row on inspection, while HEAD's copy did not.
- The gate's subject is honest: inside a checkout, `far.PROJECT_DIR` resolves to the checkout, and
  **still does under `PYTHONPATH=/home/rich/synthetic-enterprise`**. This is *not* the
  working-tree-subject disease of `WORKER_FINDING_THE_INDEX_READS_THE_WORKING_TREE`.
- HEAD's stale ledger persisted across all 81 failures. Committing the re-render ended it:
  19/19 green in a clean checkout of `818b3212a`.

**Inferred, NOT established:** why an in-cycle repair that writes the right bytes into the gate's own
checkout did not turn that cycle green. The 03:43Z cycle logged, in the repair→gate window,
`the reused HEAD checkout is held by another publisher` (×3), `could not make the HEAD checkout a git
repo: git is not installed`, and `` `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir ``.
A concurrent publisher re-materialising the shared reused checkout between repair and gate would
explain it, and the lock contention is right there in the window — but **I did not pin it**, and it is
recorded as a hypothesis, not a cause. Disk is not the constraint (897G free on `/`); `/tmp` is a
tmpfs at 70% with 2.4G free and each checkout is 189M, which is *plausible* pressure for `cannot
mkdir` and also unproven.

## Why this outranks the instance

The instance fix (commit the re-render) is done and takes one commit. The class is:

> a self-healing step placed **inside** a pipeline stage that the un-healed state blocks
> cannot heal anything; its output must land on a path that does not require the block to clear first.

Two candidate shapes, both cheap, **recommendation first**:

1. **RECOMMENDED — commit the repair before the gate, by pathspec.** The re-rendered projections are a
   pure function of committed sources, so committing them pre-gate cannot mask a defect (the same
   argument the module docstring already makes for injecting them into the checkout). It makes the
   repair durable on the *first* cycle instead of never. Narrow pathspec = no sweep risk.
2. Keep the repair in place but have a red gate **still** commit the repaired projections — a
   `--repair-only` commit on the failure path.

Either ends the loop. (1) is preferred: it needs no new failure-path branch.

## The rung-1 alarm cited eight suspects. **Zero** were the cause. Fourth consecutive episode.

`cited_findings` was, again, the same list, and again contained nothing implicated — dispositioned in
full at `e780344f7` (wedge #6) and unchanged since. Wedges #5, #6, #9 and now #10 have each recorded
8/8 wrong. **The list is not tracking the failure and should be treated as noise until it is
re-derived from the gate's actual red, not from a frozen set.** That is now filed four times; it wants
a mint, not a fifth observation.

## Evidence

- Cause: `git show HEAD:docs/design/FORWARD_ATTACHMENT_LEDGER.md | grep -c D19` → `0` at `9079d931a`; map at same HEAD → `1`; finding doc at same HEAD → present.
- Fix verified at the gate's real subject: clean `git archive` of `818b3212a`, `pytest tests/background/test_forward_attachment_register.py` → **19 passed**.
- Pre-commit state check: `far.check()` → `problems == []`, 13 entries (vacuity guard non-empty), tree rendering byte-equal to `far.render_markdown(far.derive())`.
- Diffs were pure re-derivations: ledger 12/10/9 → 13/11/10; visibility 258 → 260 atoms.
