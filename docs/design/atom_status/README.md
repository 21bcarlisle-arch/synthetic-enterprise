# atom_status/ — per-atom write-inbox files (H9 / H10 Half B)

This directory is the **map-contention fix**. It exists so concurrent BUILD
forks never contend on the single hand-authored `docs/design/maturity_map.yaml`.

## Why it exists

N concurrent BUILD forks each used to read-edit-write `maturity_map.yaml` to
record their level bump. `background/tree_lock.py` serialises the git *commit*
but **not** the read-edit-write of a shared file — so two forks lost-update
each other's level bump and could corrupt the git index. That was the real cap
on BUILD width.

Fix (WORKTREE_AND_MAP_CONTENTION_DESIGN.md, option (a), "safe by construction,
not by convention"): each fork writes **only its own file** here —
`docs/design/atom_status/<atom-id>.yaml`. Because the paths are disjoint, a
lost update is **impossible with no lock at all**. The integrator then folds
every landed inbox into the canonical map, once, single-threaded, with
`tools/merge_atom_status.py`.

The map stays the single readable source of truth for the draw. Forks **never**
open it for writing.

## Inbox schema (write-inbox fields ONLY)

```yaml
id: H9_map_write_serialisation      # REQUIRED — atom id, must exist in the map
level_current: 1                    # optional — folded onto the atom
append_evidence:                    # optional — appended to the atom's `evidence`
  - "docs/design/WORKTREE_AND_MAP_CONTENTION_DESIGN.md"
append_simplification:              # optional — appended to `simplifications`
  - "2026-07-13 BUILD ..."
written_by: sim-engineer/atom-H9    # provenance only — NOT folded into the map
written_at: 2026-07-13T00:00:00Z    # provenance only — NOT folded into the map
```

Only `level_current`, `append_evidence`, `append_simplification` are folded.
`written_by`/`written_at` are audit metadata for the integrator, left in the
inbox and discarded when it is cleared.

## Integrator flow (the merge / pre-flight contract)

Run by the orchestrator/integrator single-threaded, after each fork's scoped
suite is green:

1. **Pre-flight, git level** (design A2, read-only): for each pair of fork
   branches to merge, compute the merge-base changed-file intersection
   (`merge_atom_status.changed_files` + `preflight_overlap`). Non-empty overlap
   ⇒ a mis-declared `file_scope`; **do NOT auto-merge** — rebase the fork onto
   the integration head, re-run its scoped suite, then retry. Empty ⇒
   `git merge --no-ff` is safe. First-green-first-merged.

2. **Pre-flight, inbox level:** `merge_atom_status.preflight_inbox_overlap`
   rejects the fold if two inboxes target the same atom id (a same-atom lost
   update). The fold aborts rather than silently last-wins.

3. **Fold:** `python3 -m tools.merge_atom_status` folds each landed inbox's
   fields into `maturity_map.yaml` as a **narrow text edit** — only the target
   atoms' specific field lines change; every other atom is byte-identical (the
   hand-authored `simplifications`/`provenance`/`expert_hour`/`depends_on` are
   preserved). It then clears (deletes) each folded inbox.

4. **Full suite once:** the integrator runs the full `make test` suite ONCE on
   the merged integration branch — never per fork. Per-fork forks run only
   their scoped suite (`merge_atom_status.scoped_suite_for`, design A3).

## What this directory holds in git

Only this README (and, transiently, in-flight inbox files a fork has written
but the integrator has not yet folded). Folded inboxes are deleted by the merge
tool. Do **not** commit throwaway/fixture inboxes.

Proof of the no-lost-update guarantee: `tests/background/test_atom_status_merge.py`.
