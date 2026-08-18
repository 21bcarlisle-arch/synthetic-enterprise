# [WORKER FINDING] An atom's cited evidence is never checked against any commit, so an untracked artefact reads as evidence

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-18, on the LANE-3 DISCOVER/FRAME draw for `EP5_settlement_true_ups`.
**Class:** `uncommitted_and_orphaned_work`.

## What happened

The draw for `EP5_settlement_true_ups` re-fired with the atom reading `level_current: 0`,
`loop_stage: idle`, no evidence. It re-fired because the **previous** DISCOVER/FRAME pass had
already done the work: a 262-line artefact,
`docs/design/EP5_SETTLEMENT_TRUE_UPS_DISCOVER_FRAME.md`, dated 2026-08-17, plus an evidence line
appended to `docs/design/simplifications/EP5_settlement_true_ups.yaml`.

Neither was in any commit on any ref. `git ls-files --error-unmatch` on the artefact returned
*"did not match any file(s) known to git"*; the yaml carried an unstaged diff. So the atom's own
record cited a path that existed nowhere except this working tree, and the citation looked
exactly like the two committed evidence lines above it.

Landed this tick as `9eae51afa` after re-verifying its load-bearing claims at HEAD.

## Why no control caught it

**Nothing checks that an atom's cited evidence path exists — not in a commit, not even on disk.**
The per-atom store has real controls, and they are all about SHAPE: `evidence` is a list and
`exit_evidence` is prose (`test_atom_records_store.py:180`), records are declared and match
(`:244-252`), no record field appears inline in the map (`:218-222`). A grep across
`tests/design/*.py` for an evidence check using `exists`, `is_file`, `ls-files`, `cat-file` or
`rev-parse` returns **nothing**.

That gap is what makes this a member of this class rather than an EP5 incident: the record and
the artefact are two writes, and only one of them was ever required to land.

## The measured population

Census over the 275 atoms carrying `evidence`, extracting path-shaped tokens conservatively (a
token containing `/` and a known extension — deliberately narrow, because an evidence line reads
every backtick as a path and prose citations would inflate this):

| | |
|---|---|
| atoms carrying `evidence` | 275 |
| distinct cited paths | 837 |
| **cited paths not in `origin/main`** | **77** |
| atoms citing at least one missing path | **84 (31%)** |

The 77 split into two different defects, and conflating them would hide the one that matters:

* **75 are absent everywhere** — neither in `origin/main` nor on disk. These are the
  already-filed moved/archived class (`WORKER_FINDING_EIGHTY_ATOMS_CITE_EVIDENCE_AT_A_PATH_THAT_MOVED_2026-08-13`,
  which counted *eighty*). My census independently re-derives 84 five days later: that finding is
  still open at the same magnitude, and no control shipped for it. Most are `docs/staging/*.md`
  citations broken by archiving, but not all — `background/fronts_reconciler.py` is a deleted
  module, and `docs/observability/gate_authorizations.json` is cited by two atoms under a name
  the live ledger does not use (`.jsonl`).
* **2 are present on disk and in no commit** — the EP5 shape, and the sharper one:

| Path | Cited by | Lines |
|---|---|---|
| `tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py` | `KNIFE3_wall_crossing_paydown` | 359 |
| `tests/tools/test_no_orphan_published_customer_artefacts.py` | `D36_bill_render_footing_and_pence` | 168 |

**Both are test files.** Two atoms cite, as their evidence, falsifiers that exist on no ref —
which is precisely the defect HEAD's own `8b53a3517` recorded for the site lane one day earlier
("pytest collects from the WORKING TREE, so an untracked green test is indistinguishable from a
tracked one at the only moment anyone looks"). The class is recurring, and it recurs because that
finding hardened one lane's control rather than the shared record.

## The trap for whoever builds the control

A referential-integrity check written the obvious way — resolve each evidence path with
`Path.exists()` — **passes on all three instances that motivated this finding**. EP5's artefact
was on disk. Both untracked falsifiers are on disk. A tree-reading control cannot see this defect
by construction; it can only ever catch the 75 already-filed moved paths, and would then be
reported as having addressed the class.

The check has to resolve against a **commit**.

## Proposed control and its mutation (R15)

Not built here — this is queued, not fixed on sight (SELF_INTERRUPT_DISCIPLINE), and the repair
is shared with the still-open 2026-08-13 finding, so building it under this document alone would
harden the smaller half.

**Control.** For every `evidence` entry in the per-atom store, resolve each path-shaped token
against `git cat-file -e HEAD:<path>`. Fail listing each path that does not resolve, and mark
separately those that resolve on disk but not in the commit.

**Mutation A (the load-bearing one).** Swap the resolver from `git cat-file -e HEAD:` to
`Path.exists()`. The two untracked-falsifier instances must go GREEN. If they stay red, the
control is not actually reading the commit and the tree/commit distinction — the entire point —
is not what is being tested.

**Mutation B.** Add an evidence line citing a fabricated path to one atom's store → RED.

**Null control** (a falsifier needs one that moves the sample, not the law): point the same
control at a ref where the EP5 artefact *is* committed (`9eae51afa`) with the same atom set. It
must go green for EP5 specifically while the other instances stay red — proving the control
tracks the commit contents and not some property of the atom list.

**Scope warning.** This is a repo-wide census and is therefore not decomposable by pathspec: a
per-commit gate that only checks atoms whose files are in the current pathspec would never see an
evidence line broken by a *different* commit's archive move, which is how the 75 accumulated.

## Disposition

Filed, not fixed. The EP5 artefact and its evidence line are landed (`9eae51afa`). The two
untracked falsifiers belong to `KNIFE3_wall_crossing_paydown` and
`D36_bill_render_footing_and_pence` and are **not** landed here — they are other atoms' work,
their greenness is unverified, and landing another lane's uncommitted test under this finding
would be the same defect in the opposite direction.
