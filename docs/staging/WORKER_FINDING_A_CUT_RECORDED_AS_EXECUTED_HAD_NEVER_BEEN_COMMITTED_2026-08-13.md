# WORKER FINDING — a cut recorded as EXECUTED had never been committed, and nothing was red

**severity:** MEDIUM
**class:** uncommitted-and-orphaned-work
**found:** 2026-08-13, during KNIFE3 step 24 (`A_composition_lift`, the renewal rate chain)
**status:** DISCHARGED IN THE SAME TICK — step 23 and step 24 landed together; see below for why the
discharge does not close the class.

## What was observed (observed-with-evidence)

`tools/knife_hotspot_measure.py` reported `company_orphans UNMEASURED — the capability index exited
1`. Running the index directly gave the reason:

```
UNTRACKED ROW: 4 row(s) have no committed file behind them, so a fresh checkout does not have
them and the index is answering for one working tree:
  company/interfaces/hedge_desk.py, company/interfaces/renewal_rate_chain.py,
  company/pricing/renewal_rate_chain.py, company/trading/hedge_desk.py
```

Two of those four were step 24's own, being written at that moment. The other two were **KNIFE3 step
23's**, landed — per its own record — on 2026-08-13, several hours earlier.

`git status --porcelain` confirmed `company/interfaces/hedge_desk.py`,
`company/trading/hedge_desk.py` and `tests/company/interfaces/test_hedge_desk_seam.py` as `??`, and
`git ls-tree -r HEAD` returned nothing for `hedge_desk`.

## Why nothing was red (this is the part worth generalising)

`HEAD` was **internally consistent**. `git show HEAD:simulation/run_phase2b.py` still imported
`company.trading.forward_book` and `company.trading.hedge_decision` directly, and
`HEAD`'s `test_epistemic_wall_ratchet.py` still carried those three census entries. A fresh checkout
built, imported and passed. The whole of step 23 — the desk, the door, the 26-test control, the
census shrink, the register's §3r — lived in **one working tree** and nowhere else.

So the usual detectors could not fire:

* the **wall ratchet** measures the working tree, and the working tree had the cut;
* `tools/wall_crossing_dispositions.py` says so on its own label — *measured against THE WORKING
  TREE* — and reported the cut as real, because in that tree it was;
* the **pre-commit gate** never ran, because no commit was attempted;
* nothing at `HEAD` referenced the missing files, so no import error existed to notice.

The only instrument that saw it was the capability index's **untracked-row integrity check**, whose
whole subject is "is this index answering for the repo or for one desk?" — and its verdict was
reaching the knife ledger only as the single word `UNMEASURED`.

## Why this is not just an instance

The register's §0a already states the law: *a `cut` is a claim about the REPO, not about your desk.*
§0b names the commit-time check that enforces it. Both are correct and both were bypassed by the same
gap — **a step that is never committed never meets the commit-time check.** The class is:

> Every control this project has for "did the cut really happen" runs against the working tree or at
> commit time. A step that lands in neither state is invisible to all of them, and its own record
> says EXECUTED.

`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3s now records the instance.

## What has NOT been fixed, and is the remaining owed work

The discharge here is an instance fix (R10: an instance fix is not closure). What is still owed:

1. **The knife ledger must not flatten an integrity finding to `UNMEASURED`.** A hotspot that cannot
   be measured because the index refuses to answer for one working tree is a DIFFERENT event from a
   hotspot that is fine, and it currently prints as neither. `tools/knife_hotspot_measure.py` should
   surface the index's own finding text.
2. **A step-close check that the step's files are TRACKED.** The KNIFE pass writes its evidence list
   into `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml::map_records.evidence`. Every
   path in that list should be required to exist in `HEAD`, not merely on disk — the same shape as
   the existing "archiving a document breaks every atom record that cited it" control, applied to
   tracking rather than to path validity.

Both are queued rather than built here, per SELF-INTERRUPT DISCIPLINE: the tick's drawn work was
step 24, and the machine was not blocked.

## Evidence

* `git ls-tree -r HEAD --name-only | grep hedge_desk` → empty, before the landing commit.
* `git show HEAD:simulation/run_phase2b.py | grep hedge` → the pre-step-23 direct imports.
* `python3 -m tools.capability_index` → rc=1, the untracked-row finding quoted above.
* `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3s, "STEP 23 WAS NEVER LANDED".
