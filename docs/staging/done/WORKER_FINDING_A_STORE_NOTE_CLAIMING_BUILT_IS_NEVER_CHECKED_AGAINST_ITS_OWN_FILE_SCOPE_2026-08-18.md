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

---

**Discharged:** 2026-08-19, H27 Expert Hour #39, by
`tests/architecture/test_no_committed_store_claims_an_unlanded_symbol.py`.

§4.1 said MEASURE FIRST, and the measurement changed the design. Keyed as §2 proposed -- symbols
inside a clause carrying the literal word `BUILT` -- the population at HEAD is 34 clauses and SIX
symbol mentions across 297 stores, 0 violations: the parent finding's own one-marker defect with a
different word. The subject was widened from the marker to the CLAIM SHAPE and the discrimination
moved to the INDEX/WORKTREE SPLIT, which needs no disclaim lexicon at all -- 423 (store, symbol)
pairs over 266 stores, 387 (91.5%) resolving in the atom's own committed `file_scope`, 34 in
neither tree (honest: atom ids, SHAs, English inside backticks), 2 in the working tree only.

§4.2 said reuse the two registers. Only `_KNOWN_UNLANDED` was needed and it ships EMPTY; there is
no `_STALE_CITATION` shape here, because a symbol is checked against the tree that exists rather
than against a name that may have been renamed.

**Both worktree-only symbols were real, and both were in H27's own store**: `door_only` (index 0,
worktree 4) and `dimension_caveats` (index 0, worktree 2), credited by a committed
`level_hold_note` that also states *"#38 landed #37's work"*. It had not -- the store half landed
at `9821a52a5` and the code stayed on disk. Landed rather than ratcheted (573 passed in
`tests/tools/test_couple_w2_11_d5.py` before staging), which is what took the control green.

**Evidence:** R15 both directions on REAL state, not a fixture -- RED against the live index with
the code unstaged (2 violations named), GREEN once staged. 18 passed, of which 12 are mutations.

**Amended 2026-08-19, H27 Expert Hour #40 — the discharge above stood on a control that had never
been run by anyone but its author, and #39 never committed it.** The tick after #39 (`e8834cf37`)
preserved the staged hunk and landed other work, so this document sat in `done/` describing a
control in no commit — the same shape it was written about. Run independently, the control was RED
on a FALSE POSITIVE: `OPS3_first_post_ruling_publish` `git_hash`, whose declared `file_scope` is two
artefacts a live daemon rewrites, while the symbol itself has been committed in
`background/process_run_complete.py` for a long time. #39's premise was false in one clause —
`file_scope` declares what an atom OWNS, not that those files are CODE — and the verdict was
decided by which background process wrote last.

Repaired by `_is_code`, which narrows the VERDICT corpus to authored source while the LANDED corpus
keeps every entry (forgiving too readily can only remove a violation, never invent one). The
tempting repo-wide "is it landed anywhere" backstop was measured and REJECTED: at HEAD it forgives
both founding violations (`door_only` in 6 committed files, `dimension_caveats` in 11) and would
have left the control unable to fire on the only case it has ever caught; a mutation now pins that
so it cannot return as an obvious improvement. 22 passed, RED still reproducible against a
throwaway copy of the index with this atom's modules reset to HEAD. **The finding stays discharged;
the control that discharges it is the repaired one, and it landed in the same commit as this line.**
