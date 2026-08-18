# WORKER FINDING — the step that ends a document's drawability has no chokepoint, so no control can refuse a premature `done/`

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-18, worker tick, while landing (A) and (B) of
`WORKER_FINDING_THE_RUN_COMPLETE_SWEEP_STAGES_THE_WHOLE_ARCHIVE_DIRECTORY_AND_COMMITS_WITHOUT_A_PATHSPEC_2026-08-18.md`.
That page owed three more items — its (C), (D) and (E) — and archiving it would have ended their
drawability, which is the exact move it was written about. They are restated here, on a page the
staging scanners read.
**Measured at:** HEAD `32b70f644` plus this tick's uncommitted publish-path repair.
`observed-with-evidence` where marked; §1's conclusion is labelled *inferred*.

**Not BLOCKING, and the distinction is load-bearing.** The publish path could archive documents it
did not author; that was BLOCKING and is fixed. What remains is that a document can be archived
*by a person or tick that did author it* before the work it claims has landed. No instrument's
verdict and no published figure depends on this. It is a real defect that loses work, not a reason
to distrust anything currently published.

## 1. The chokepoint that does not exist

`_archive_marker` in `background/process_run_complete.py` is not the archiver — it handles
`run_complete_*.md` markers only. Finding documents reach `docs/staging/done/` by a hand `git mv`
in whichever tick closes them. `grep -rn "staging/done" --include=*.py background/ tools/` returns
readers (`staging_archive_policy`, `primary_state_scan`, `daily_self_note`, `sanity_daemon`) and
no writer for this class of document.

So the parent finding's (C) — *"refuse to move a document INTO `done/` when its `**Discharged:**`
nodes are absent from the tree being committed"* — cannot be one call added to an existing
function, because there is no function. *Inferred:* the only place with the whole class in view is
**a pre-commit gate on any commit that ADDS a path under `docs/staging/done/`**.

## 2. What is owed

* **(C) The archive gate.** For each path added under `docs/staging/done/` in the commit being
  made, parse the document's `**Discharged:**` claim and refuse the commit when
  `background.finding_severity.parse_discharge(text).released` is false. The reader already exists
  and already reads the INDEX rather than the working tree (H27, `32b70f644`), which is the half
  that makes it answerable at commit time at all. Design notes:
  * The subject is the **added path**, not the file's current content — a document already in
    `done/` being edited must not re-trigger.
  * A document making **no** discharge claim returns `None` and must pass; not every archived page
    claims a repair (`from_rich_*`, mint docs, run markers). That is the fail-OPEN edge and needs
    its own mutation test, because it is the shape a real gate degrades into.
  * R15 both ways: an unlanded claim must be REFUSED, and a landed one must be ALLOWED, or the
    gate is a wall on ordinary archiving.
* **(D) The two orphans.** `done/WORKER_FINDING_THE_BELIEF_AXIS_NULL_CONTROL_CANNOT_FAIL…` and
  `done/WORKER_FINDING_THE_DOOR_LEDGER_TRIPWIRE_COMPARED_TEN_OF_NINETEEN_SHARED_FIELDS…` are
  archived with their repairs unlanded. Their 15 dangling citations are declared in
  `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py::_KNOWN_UNLANDED`.
  `tools/couple_w2_11_d5.py` and `tests/tools/test_couple_w2_11_d5.py` are **still modified and
  uncommitted in this working tree** as of this tick (observed-with-evidence: `git status`).
  Whoever lands them MUST delete the matching `_KNOWN_UNLANDED` entries — the stale-entry test
  makes that compulsory, not optional.
* **(E) D30's unwritten store record.** The same uncommitted working-tree change moves D30's
  declared band (`above_edge_range` `(-328, -308)` → `(-333, -308)`) and its axis floor
  (`n_customers` 24 → 17) without writing D30's store record. *Inferred:* belongs on D30's next
  draw, and is recorded here so it does not vanish with the archived page it came from.

## 3. Why this is registered rather than fixed on sight

SELF_INTERRUPT_DISCIPLINE: this tick was drawn on the lane's live BLOCKING finding and landed it.
(C) is a new pre-commit gate with a fail-open edge that needs its own R15 battery — a build, not a
follow-on edit. Registering it is what keeps it drawable, which is precisely what the parent defect
denied its own victims.
