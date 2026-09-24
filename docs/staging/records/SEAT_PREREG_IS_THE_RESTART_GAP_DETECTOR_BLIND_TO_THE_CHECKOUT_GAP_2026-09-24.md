**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: is the restart-gap detector structurally blind to the checkout gap?

Claim id: `the-shared-checkout-is-the-second-gap-between-a-landed-commit-and-a-running-daemon`.
Written BEFORE measuring. Parent finding:
`docs/staging/SEAT_FINDING_THE_DECLARED_BOOT_STAMPER_HAS_STAMPED_NOTHING_SINCE_2026_09_04_SO_NO_DAEMONS_CODE_VERSION_IS_KNOWN_2026-09-24.md`.

## The setup, already measured and not in question

A landed commit has **two** gaps before a daemon runs it:

1. **CHECKOUT** — `origin/main` has the commit; the shared tree's working checkout does not.
2. **RESTART** — the checkout has it; the running process booted before it.

Gap 2 is measured (`process_reconciler.loaded_code_drift`). Gap 1 is measured by nothing that
watches. Established facts at the time of writing:

* shared tree `/home/rich/synthetic-enterprise` is **3 ahead / 11 behind** `origin/main`, and
  `git merge-base --is-ancestor HEAD origin/main` says **NO** — it is DIVERGED, so it cannot
  fast-forward at all. `origin_reconcile --check` answers `{"behind": 11}`.
* the shared tree's working copy of `background/boot_sha.py` contains **no `__main__`** and no
  `read_boot_ts`; `background/process_reconciler.py` contains no `stamp-predates-process`. All
  three repairs (`ec1012c01`, `7c77466ce`) are on `origin/main` and absent from the box.

## The mechanism I think is there

`boot_sha.changed_paths_since(sha)` runs `git diff --name-only <boot_sha> --` **in the shared
working tree**. It compares the daemon's boot stamp against *the disk*, never against `origin/main`.

If the checkout does not contain a commit, the files that commit changed **are not different on
disk**, so they cannot appear in that diff. The detector would then report a daemon GREEN for a
module whose landed repair it does not hold.

## The prediction, recorded before running anything

**P1.** `changed_paths_since(<any boot sha>)` evaluated in the shared tree returns a set that does
**not** contain `background/boot_sha.py` or `background/process_reconciler.py` on account of
`ec1012c01`/`7c77466ce` — i.e. the 11 unmerged commits contribute **zero** paths to the changed set.

**P2.** Consequently at least one daemon whose closure imports `background/boot_sha.py` is reported
as *not* holding a changed `boot_sha.py`, despite the repair being landed and absent from its disk.

**P3.** The blindness is **total, not partial**: of the 28 paths `git diff HEAD origin/main` names,
the number that `changed_paths_since` can ever surface from the checkout is **0**.

**P4 (the direction that matters).** This failure is **fail-OPEN** — it under-reports staleness.
Every other rule in `loaded_code_drift` was built to fail safe. This one silently answers "clean"
about code the daemon demonstrably does not have.

## What would refute me

Any of: the diff resolving through `origin/main` rather than the working tree; a non-zero count in
P3; or the detector surfacing these paths by some route I have not read (e.g. a second oracle in
`code_closure` or `read_boot_blobs`). If P3 comes back non-zero the mechanism above is wrong and I
will say so beside this file rather than revising it.

## What I will NOT conclude from a confirmation

That the daemons are "more stale than reported" by any particular amount. P1–P3 are about the
**instrument**, not the world — a pre-registered count predicts the instrument
(`feedback_a_pre_registered_count_is_a_prediction_about_an_instrument_not_about_the_world`). The
population-level question of how much real drift is hidden is a separate measurement and is not
claimed here.
