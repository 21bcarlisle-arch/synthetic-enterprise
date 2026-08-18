# FINDING — three committed records say DISCHARGED and name falsifiers that are in no commit, and none of the three can be landed because the repair each one certifies is uncommitted too

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** DISCHARGED AT THE CLASS for the `tests/` half (`tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py`); the three instances are DECLARED debt owed to their own lanes — see "Why this is a ratchet" below

**Atom:** `H27_payment_belief_gap` (self-refill 2→3 HARDEN draw, Expert Hour #36, 2026-08-18)
**Class:** `uncommitted_and_orphaned_work` — consolidates as a member of
`docs/staging/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` (same lane, `H_harness`)

**Discharged:** `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py` — the `tests/` half of the class Expert Hour #35 built the SITE half of and deliberately left open; R15 both ways against real history, four mutations proven, ratchet checked in both directions.

## What this was, before it was anything else: the owed item, built

H27's store note has ranked this first since Hour #35 wrote it:

> (A) THE `tests/` HALF OF HOUR #35's CLASS — the publish gate collects from the WORKING
> TREE exactly as the site lane did, so an untracked control counts toward its green there
> too; NOT built as a bare untracked census because it would be born red on other lanes'
> live in-flight work, and the honest subject is *"untracked AND cited by a committed record
> as a discharge or as covered scope"*.

That subject is now implemented and green. What it found on its first run is the finding.

## The observation, `observed-with-evidence`

Reading every `**Discharged:**` line **from the git index** across 72 committed records
(88 distinct cited paths), three cited falsifiers are in no commit on any ref:

    tests/saas/test_clv_margin_basis.py
    tests/tools/test_derived_basis_parentage_gate.py
        <- docs/staging/done/WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK_2026-08-17.md
    tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py
        <- docs/staging/done/WORKER_FINDING_THE_WORLDS_DWELLING_FOR_A_DRAWN_HOME_IS_THE_COMPANYS_OWN_ESTIMATE_2026-08-17.md

All three are on disk (13:37, 13:38 on 2026-08-17 and 02:06 on 2026-08-18), none is
ignored, `git log --all` on each is empty, and all three are GREEN in the working tree:

    $ python3 -m pytest <the three> -q
    28 passed, 1 warning in 2.92s

## Why this is worse in kind than the site instance, not a second copy of it

Hour #35's instance was one untracked test whose **subject was committed**, so the repair
was a one-line `git add`. These are not. Run against a detached worktree at HEAD, all three
fail to even import — the mechanism each one certifies as repaired is uncommitted as well:

    $ git worktree add --detach /tmp/h36_head_clone HEAD && cd /tmp/h36_head_clone
    $ python3 -m pytest <the three copied in> -q
    3 errors during collection
    E ImportError: cannot import name 'CLV_MARGIN_BASIS' from 'saas.clv_model'
    E ImportError: cannot import name 'UNKNOWN_COST_BASIS' from 'tools.generate_dashboard_data'
    E ImportError: cannot import name 'BASIS_SAAS_APPROXIMATION' from 'saas.property_model'

Counted with `git show HEAD:<file>` against the working copy — HEAD occurrences / worktree
occurrences:

| symbol | HEAD | worktree |
|---|---|---|
| `tools/generate_dashboard_data.py` `UNKNOWN_COST_BASIS` | 0 | 5 |
| `tools/generate_dashboard_data.py` `_check_derived_basis_parentage` | 0 | 3 |
| `saas/clv_model.py` `CLV_MARGIN_BASIS` | 0 | 3 |
| `saas/property_model.py` `BASIS_SAAS_APPROXIMATION` | 0 | 2 |

So the record does not merely cite a missing test. **The whole repaired mechanism a
committed document declares closed exists on one machine.**

`observed-with-evidence`, and it corrects a guess made earlier in this same pass: HEAD is
**not** broken. `simulation/dwelling_records.py` is also in no commit and eight tracked
modules in the working tree import it — but at HEAD *nothing* references it
(`git grep -l dwelling_records HEAD -- '*.py'` is empty). The whole KNIFE3 B12 dwelling
split, module and all five importer edits, is one lane's in-flight change set. A clone is
internally consistent; it simply does not have the repair.

## What this falsifies — and it is Hour #35's own reasoning

#35 chose this subject specifically to escape the sequencing problem, on the reasoning that
a committed discharge is a closed claim and therefore not a race. The first half of that
holds: none of the three is a transient editor state, and the control is not fighting
another lane's keyboard. The second half does not. **The population of committed discharge
claims is itself made of uncommitted work** — picking a better-defined subject did not avoid
the sequencing problem, it selected for it. That is the class, and it is why the shape below
is a ratchet rather than an assertion.

## Why this is a ratchet, and why the three are not fixed here

The three cannot be greened from this lane. Landing them means landing another lane's
uncommitted repairs to `saas/clv_model.py`, `saas/property_model.py`,
`tools/generate_dashboard_data.py` and the untracked `simulation/dwelling_records.py` —
sweeping a live lane's work into this commit, which the shared-tree rules forbid outright.
Deleting the falsifiers to go green is worse. So the three are **declared** in
`_KNOWN_UNLANDED` with the date and the change set each waits on, and everything else fires
immediately. The list is checked in **both** directions: an entry that stops being a
violation must be deleted, so the ratchet cannot rot into a permanent exemption
(`test_every_declared_exemption_is_still_a_real_violation`, proven to fire).

Owed to the lanes that own them: land each falsifier **in the same commit as the repair it
certifies**, then delete its line from `_KNOWN_UNLANDED`.

## R15 — both ways against real history, not a fixture

**RED** with `_KNOWN_UNLANDED` emptied on the tree exactly as found: 1 failed / 7 passed,
naming all three with their citing records. **GREEN** with the debt declared: 8 passed.

Four mutations, each performing a named killer pattern and asserted to pass on it:

- **TAUTOLOGY** — resolving cited paths against the filesystem (`Path.exists()`) instead of
  the index. All three violations are on disk, so that checker is green on the shipped
  defect. Not hypothetical: it is the same shape that let 77 dead evidence paths sit
  unnoticed across 84 atoms.
- **FAIL-OPEN** — a marker matching nothing (population 0) with the vacuity floor removed.
- **FAIL-SILENT** — `git` absent from PATH, and `git` exiting non-zero, each swallowed into
  an empty set. Both raise instead: an unavailable check is a FAILED check.
- **FAIL-SILENT, third door** — `git ls-files` succeeding and returning nothing.

Floors are measured, not guessed: 72 records carrying a discharge line, 88 distinct cited
paths (floors 30 / 40).

### The gate caught this control being the thing it polices, `observed-with-evidence`

The first draft was **refused by the pre-commit gate** — 1 failed / 445 passed — and the
failure was the TAUTOLOGY mutation test, not the tripwire:

    FAILED tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py
           ::test_MUTATION_resolving_citations_against_the_filesystem_goes_blind

It asserted `"precondition: at least one live violation is present on this machine"`. That
holds here and nowhere else: `tools/surgical_land` builds the tree the commit WOULD create
in an isolated worktree, where all three violations are absent from disk precisely because
they are untracked. **A control about machine-local state was itself depending on
machine-local state** — the same defect one level in, in the file written to close it.

Repaired by splitting the mutation into two arms: a structural arm on explicit subject sets
that proves the blindness deterministically and runs everywhere, and a real-history arm that
runs additionally wherever the tree physically carries the defect and says so when it does
not. Green in both environments (8 passed here; 8 passed in a detached worktree at HEAD),
and the R15 RED direction re-proven after the change: 1 failed / 7 passed with
`_KNOWN_UNLANDED` emptied.

This is worth recording rather than quietly fixing: the gate's "build the tree this commit
creates" step is what made the difference between a control that is true and a control that
is true here, which is the whole subject of this finding.

**R12:** no figure this instrument computes was touched. Nothing in this pass moved a
published number.

## Scope, stated so it is not read as wider than it is

The subject is `**Discharged:**` lines only. Two neighbouring citation surfaces were
measured and deliberately excluded:

- the maturity map's `file_scope` — **forward-looking by design**; 24 of its paths name
  files not yet built, so it cannot carry a landed/unlanded verdict. (Two of its entries are
  on disk and untracked: `simulation/dwelling_records.py` and
  `tests/architecture/test_live_payment_triad_is_the_only_bridge.py`.)
- `evidence` fields on the map and the 297 committed simplification stores — long narrative
  prose, not path-structured, so extraction is unreliable. Measured anyway: **0** cited-and-
  untracked. The 75 absent ones there are the already-filed archiving class
  (`WORKER_FINDING_EIGHTY_ATOMS_CITE_EVIDENCE_AT_A_PATH_THAT_MOVED_2026-08-13`), a different
  defect — a path that MOVED, not a path that never landed.

The bare "untracked `tests/**/test_*.py`" census #35 refused is still refused, for #35's
reason, which this pass re-measured and confirms: 13 untracked `.py`/`.mjs` files are on
disk right now, most of them one lane's live B12 work.
