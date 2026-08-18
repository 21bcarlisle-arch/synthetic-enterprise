**Severity:** LATENT · **Lane:** H_harness

# A store note claiming BUILT names symbols nothing checks against the atom's own declared file_scope — the atom hands the check its subject and no one takes it

**Found:** 2026-08-18, worker tick, while discharging
`WORKER_FINDING_THE_DISCHARGE_CONTROL_READS_MARKDOWN_ONLY_SO_THE_REGISTER_LEVELS_ARE_ARGUED_IN_IS_INVISIBLE_2026-08-18.md`.
That document's §5.2 recorded this as *"the cheaper control that is not in this finding's lane,
recorded so it is not lost"*. Registering it rather than absorbing it silently is the whole point
of this document.
**Class:** `uncommitted_and_orphaned_work`.
**Measured at:** HEAD `e844ee864`. §1 is `observed-with-evidence` (R9); §3 is inferred and labelled.
**Intended rank (P-1):** H_harness LATENT band, below the BLOCKING band.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the tick that found it was landing a
different repair, and the machine is not blocked.

---

## 1. The gap, stated against what now exists

Three controls now read committed records and check a cited artefact against the index:

| control | subject |
|---|---|
| `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py` | a `**Discharged:**` line in a markdown record |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` | a `tests/**.py` citation in an atom store |
| `site/test_the_site_lane_runs_no_untracked_control.py` | the SITE lane's own controls |

All three take a **path** as the subject (the first two also take the node). **None takes a
SYMBOL.** A store note that says *"BUILT (this atom's own file_scope) … `door_only`,
`required_missing`, `_abbrev`"* is asserting that named symbols exist in named modules, and nothing
compares that assertion to `git show HEAD:<file_scope>`.

That is exactly the shape of the instance that opened the parent finding. Expert Hour #37's store
note, committed at `65b26e4e4`, named `door_only`, `required_missing` and `_abbrev` as built; at
that same commit `tools/couple_w2_11_d5.py` carried **0** occurrences of each and the working tree
carried 3, 2 and 3. The over-claim was in a committed record for over 20 hours, and every control
listed above would have passed it, because the *file* it names is tracked — it is the *symbols*
that were not there.

## 2. Why this one needs no grammar, which is what makes it cheap

The parent finding's control needed a citation grammar because a store's prose mentions files it is
not claiming (globs, DoD items, absence reports — 9 of 10 leads). This check has no such problem:
the atom **already declares its own `file_scope`** in `docs/design/maturity_map.yaml`, so the
subject is handed over rather than inferred. The check is:

    for a store note whose text asserts BUILT,
    every backticked symbol it names that resolves to an identifier
    must appear in `git show HEAD:<one of the atom's declared file_scope paths>`

with the same declared-debt ratchet the other two carry.

## 3. Why LATENT and not BLOCKING (inferred)

The parent finding argued BLOCKING on the ground that three records agreed and all three were
wrong. That instance is now closed from two directions — the store half landed with the parent, and
the D36 orphan it found was landed with it. This is the *third* angle on the same class rather than
a live wedge: no lane is blocked, nothing published is currently known to be wrong, and the
population is unmeasured. **The population is the first thing the BUILD must measure**, and the
count is not asserted here precisely because it has not been.

## 4. Recommendation, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **Measure first, build second.** Count store notes asserting `BUILT` whose named symbols are
   absent from their own declared `file_scope` at HEAD. If that count is small, it is a ratchet on
   day one; if it is large, the symbol-extraction rule is wrong and needs the same
   claim-vs-location treatment the store grammar needed.
2. **Reuse the two registers, do not invent a third.** The store control's split — `_KNOWN_UNLANDED`
   (waits on a named uncommitted change set) versus `_STALE_CITATION` (a named commit deliberately
   retired it) — is the disposition vocabulary this class has converged on, and a symbol check will
   meet both shapes for the same reasons.
