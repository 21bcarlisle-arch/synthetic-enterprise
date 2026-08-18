# WORKER FINDING (QUEUED) — a pass records progress in the working tree and verifies it with a working-tree instrument, so no term in it can go red when nothing is committed

**Severity:** BLOCKING · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight, per SELF-INTERRUPT DISCIPLINE)

**Found by:** the 2026-08-18 worker tick (KNIFE3 step 36), which drew intending to plan the next cut
against the 6 owed rows and instead found the last five steps had never been committed.

## Observed, with evidence

`python3 -m tools.wall_crossing_dispositions --at-head`, run this tick before any edit:

```
measured against HEAD (the committed tree): 8 live crossings (6 direct, 2 indirect); 91 ruled (cut 85, owed 6)
  FINDING: simulation.run_phase2b -> saas.property_model: ruled `cut` but the import IS STILL IN HEAD
  FINDING: simulation.run_phase4c_on_phase2b -> company.billing.dd_review_runner: ruled `cut` but the import IS STILL IN HEAD
```

against the bare command's `6 live crossings … OK — every live crossing is examined`.

* `git show HEAD:docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md | grep '^## 3[a-z]*\.'` → last
  section **§3y (step 30)**. §3z/§3aa/§3ab/§3ac/§3ad existed only in the working tree.
* `git cat-file -e HEAD:simulation/dwelling_records.py` → `fatal: exists on disk, but not in 'HEAD'`.
  `company/interfaces/dd_review.py` likewise: both were **untracked**, not modified.
* The atom yaml's own progress field read `35 steps landed as of 2026-08-18`.

All `observed-with-evidence`. No external actor is implied or needed: the tree has documented
concurrent writers and no lane claimed these paths.

## Why every cheap check passed

This is the generalisable half. Five sources agreed on 6 owed and all five read the same one
uncommitted tree:

| source | said | why it could not know |
|---|---|---|
| `tools.wall_crossing_dispositions` (bare) | 6 live, OK | measures THE WORKING TREE — by construction |
| `tools.knife_hotspot_measure` | 6 live | same tree |
| the register §3ad | cut 85, owed 6 | a working-tree document describing itself |
| the atom yaml progress field | "35 steps landed" | a working-tree document describing itself |
| the KNIFE3 pytest set | 121 passed | imports resolve because the tree has the new modules |

The atom's own stale-doorbell notice — the mechanism built to stop exactly this class — pointed the
next step at the bare command: *"NEVER TRUST THIS FIELD'S COUNTS OVER THE TOOL: run `python3 -m
tools.wall_crossing_dispositions`, which measures the WORKING TREE."* True, and the hole: **a
working-tree instrument cannot detect that the working tree is the only place the work exists.** The
one instrument that disagreed, `--at-head`, is the one nothing in the doorbell named.

This is an R15 **FAIL-SILENT** instance with a twist worth naming: the check was not unavailable, it
was *available and unrun*, because the document telling the next agent which check to run named the
wrong one. A control that is correct and mis-cited is a control that does not fire.

## Class, not instance (R10)

Registered against the class **"a cut recorded as EXECUTED had never been committed"** — 3 prior
instances, deepest 4 steps. This is instance 4 and the largest: **5 steps, 2 real cuts, 2 new
modules**. The instance was closed by landing (step 36, register §3ae). The CLASS is not:

> Any pass that (a) records its own progress in a working-tree document and (b) verifies that
> progress with a working-tree instrument has **no term anywhere in it that can go red when nothing
> is committed**.

`docs/design/simplifications/` holds other passes with the same two properties; a sweep for progress
fields whose stated verification command reads the working tree is the class-level work, not a
second manual `--at-head`.

## Recommendation — and I have taken the reversible half already

**RECOMMENDED (unbuilt, queued):** make the close-time check structural rather than remembered —
`wall_crossing_dispositions` grows a mode that is FAIL-CLOSED on the HEAD/worktree divergence, and
the KNIFE3 exit criteria name it, so a step cannot report a cut that the repo does not contain. R15
mutation both ways: a tree with an uncommitted cut must go RED, and a fully-landed tree must go
GREEN (a check that is always red at a dirty desk would be turned off within a day, and this tree is
permanently dirty — that is the design constraint, not an objection).

**DONE THIS TICK (reversible, so not asked about):** landed steps 31–35 via `tools.surgical_land`;
corrected the yaml notice to say **built** where it said *landed* and to name `--at-head` alongside
the bare command; recorded §3ae.

**NOT DONE:** the sweep of other `simplifications/` passes for the same shape, and the fail-closed
mode itself. Both are this finding's own build, and both are queued rather than taken, because the
supply of harness findings is infinite and fixing on sight is the treadmill.
