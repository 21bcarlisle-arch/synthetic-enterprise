**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

**Fate (2026-10-15):** DONE -- counted, zero plain commits on the shared main while behind since 2026-10-02 and none at all since 10-13; no pre-commit refusal added, salvage tag deleted as superseded; reopen on the first such commit.

# Is the pre-commit door used to commit on a shared checkout that is behind origin?

*Delivery seat, 2026-10-15, direction item `the-land-twice-control-is-salvaged-and-must-not-refuse-every-tick`.*

## Pre-registration (written 2026-10-15 ~17:15 BST, before the count was run)

ed7e89d12 refuses a `surgical_land` on the primary checkout whose parents lack origin/main. The
salvaged version (tag `salvage/detached-90b25caf661c`) also refused a plain `git commit` there,
through the pre-commit hook. **Question:** since 2026-10-13, how many reflog entries of kind
`commit` (not `surgical-land`, not `merge`) moved `refs/heads/main` in the shared checkout while
the local `origin/main` ref was not an ancestor of the commit's parent?

**Prediction:** non-zero, small (1-10). Worker ticks and the publisher commit under `tree_lock`
with a plain `git commit`, and the shared checkout sat 29-97 behind for ~19h on 10-14/15.

**Decision rule:** zero → drop the item, delete the salvage tag's code as superseded. Non-zero →
the same refusal goes into `tools/git-hooks/pre-commit`, keyed as ed7e89d12 keys it.

## Result (measured after the pre-registration, over `.git/logs/refs/heads/main` in the shared checkout)

For each entry, "behind" means the local `origin/main` ref at that moment was not an ancestor of
the entry's old value. The ref's value at that moment is read from the reflog of `refs/remotes/origin/main`.

- **2026-10-13 00:00 → 2026-10-15 17:09: plain `commit` entries = 0**, whether behind or not. The
  ref moved only by `surgical-land` (17 level, 17 behind) and `merge origin/main` (33).
  **The prediction (1-10) was wrong.**
- Over the whole reflog (from 2026-09-15): 158 plain commits were made while behind, the last on
  **2026-10-02 21:26**. All 158 came from two writers. `delivery seat: direction for the next stretch`
  has landed on origin, not the shared HEAD, since 2026-10-04 (`background/delivery_seat.py`,
  `land_direction_on_origin`). The publisher's `chore(liveness)`/`chore(provenance)` commits sit
  behind `process_run_complete._divergence_refusal`. Both writers are retired from this door by
  construction, not just quiet.

**Decision (per the rule above):** zero, so no pre-commit refusal is added. The salvaged
`background/shared_head_fork.py`, its hook line and its test are superseded. Tag
`salvage/detached-90b25caf661c` (sha `90b25caf661cf969e1180fd9a07622d4bc71bdda`) is deleted. To
reverse it before gc: `git tag salvage/detached-90b25caf661c 90b25caf661c`. **Reopen when:** any
plain `commit` entry appears on the shared `main` reflog while it is behind. Re-run the count with the
script described above.

## Residual the count surfaced (not this item's ask)

`surgical-land` 8cf05c7e7 landed at 16:58:30 on 2026-10-15 on parent 47e544e24, **after** the
ed7e89d12 guard had reached the shared HEAD. Origin had moved to 7bc3e3d3a at 16:57:14. The guard
runs in `land()` before the ~20-minute gate (that is deliberate: a refusal costs seconds), so origin
moving *during* the gate is unseen. Cost this time: 1 behind, and the reconciler merged it onto
origin as 0426fac1a 2.5 min later, with no duplicate landing. It is a time-of-check race, so it
cannot be closed by re-asking before the gate. If it recurs with a stranding, the cheap leg is to
re-ask `_refuse_a_landing_a_behind_checkout_would_strand` just before `update-ref`.
