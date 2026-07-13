# WORKTREE AND MAP CONTENTION DESIGN — H10 (worktree isolation) + H9 (map write serialisation)

**Status:** DISCOVER/FRAME (Lane-3, doc-only). Supersedes the interim "orchestrator is sole `maturity_map.yaml` writer" rule in `docs/design/THREE_LANES.md` Lane 1 with a structural fix.
**Source requirements:** `docs/staging/done/WORKTREE_ISOLATION_AND_SEAMS.md` Half 1; maturity_map atoms `H10_worktree_isolation` (HIGH), `H9_map_write_serialisation`.
**Author:** discovery fork, 2026-07-13. NO code changed by this doc.

## Problem

N concurrent BUILD forks share one working tree and each read-edit-write the single `maturity_map.yaml` to record their level. `background/tree_lock.py` serialises the git *commit* (index collision in one tree) but not the *read-edit-write* of a shared file, so two forks lost-update each other's level bump and can corrupt the index. The interim fix (orchestrator is the sole map writer; forks report level back and it records serially) removes corruption but re-serialises level recording — the exact bottleneck. The proper fix has two halves: give each fork its own working tree (H10), and make the map read-only during a build so level recording never contends (H9).

---

## Half A — Worktree isolation (H10)

### A1. How a fork is launched worktree-isolated in THIS repo

Build agents are already subagents: `.claude/agents/saas-engineer.md` and `.claude/agents/sim-engineer.md` (both `model: opus`, tools `Read, Write, Edit, Bash, Grep, Glob`). The read-only agents (`discovery-agent`, `epistemic-verifier`, `interface-steward`, `phase-close-evaluator`) do not need isolation.

**Confirmed by direct read:** none of the six frontmatters currently contain any isolation directive — each carries only `name`, `description`, `tools`, `model`. So worktree isolation is **not yet wired in this repo**.

**Intended shape** (per `WORKTREE_ISOLATION_AND_SEAMS.md`): add `isolation: worktree` to the frontmatter of the two build agents, which provisions a fresh git worktree + branch per parallel invocation over the shared `.git` object store. A build fork is then launched exactly as build subagents are launched today (Task/Agent dispatch of `saas-engineer` / `sim-engineer`), and the harness gives it its own tree.

**BUILD-TIME VERIFICATION (cannot confirm here — no network/official docs):** the exact frontmatter key and value (`isolation: worktree` vs a `--worktree` CLI flag vs a per-invocation parameter), the branch-naming scheme it generates, and the worktree path it checks out to. Verify against current official Claude Code subagent docs before writing frontmatter. Do not assume the key name — the staging doc itself says "verify the directive against current official docs before adopting."

### A2. Merge model — orchestrated sequential merge + pre-flight conflict detection

One integrator (the orchestrator) merges fork branches into an integration branch, one at a time, after each fork passes its scoped checks (A3).

**Order rule:** first-green-first-merged (a fork is merge-eligible the moment its scoped suite is green). Before each merge, run pre-flight merge-base conflict detection against the current integration head; a fork whose changed-file set intersects work already merged is **re-sequenced** (rebased onto the new integration head, scoped suite re-run) rather than merged blind. Because Lane 1 only dispatches forks whose `file_scope`s are declared non-intersecting, the intersection should normally be empty; the pre-flight is the belt-and-braces that catches a mis-declared scope before it becomes a dirty merge.

**Pre-flight detection (concrete git, read-only):**
```
base=$(git merge-base <integration-head> <fork-branch>)
a=$(git diff --name-only $base <integration-head>)
b=$(git diff --name-only $base <fork-branch>)
# overlap = comm -12 <(sort a) <(sort b)
```
Non-empty overlap ⇒ do NOT auto-merge; rebase the fork on the integration head, re-run its scoped suite, then retry. Empty overlap ⇒ `git merge --no-ff <fork-branch>`.

PR-per-agent is the documented alternative; at ≤4–5 concurrent forks (us) the orchestrated model is the right simplicity tier, per the staging doc.

### A3. Test economics — scoped suite per worktree, full suite once

Test tree mirrors source tree; counts today: `tests/sim` 25, `tests/simulation` 85, `tests/saas` 82, `tests/company` 557, `tests/background` 32, `tests/tools` 83 files (~17k cases total). Scope is derived from the atom's top-level `file_scope` dir:

| Atom `file_scope` root | Scoped suite in the worktree |
|---|---|
| `sim/**` or `simulation/**` | `pytest tests/sim tests/simulation` |
| `saas/**` | `pytest tests/saas` |
| `company/**` | `pytest tests/company` |
| `interface/**` (seam) | `pytest tests/company tests/saas` (both consumers) — build-time verify |
| `background/**`, `.claude/**`, `tools/**` (harness) | `pytest tests/background` and/or `tests/tools` |
| `site/**` | no python suite; pixel-verify the live surface per R11 (SITE constitution) |

The **full ~17k suite (`make test` → `pytest tests/`) runs ONCE**, by the integrator, on the merged integration branch — never per fork. This is the whole point of scoping: N forks pay N small suites, integration pays one full suite.

### A4. Per-worktree environment — what a fork needs, what breaks if absent

A native worktree is a sibling checkout at a different path. It shares the `.git` object store but **nothing runtime**. Enumerated against this repo:

- **Secrets / env files — OK, carry over.** `SE_NTFY_TOPIC`, `SE_WAKE_HMAC_KEY`, `FILE_API_KEY` load from `~/.config/synthetic-enterprise/.env.ntfy` and `.env.file-api` (moved out of the tree, 2026-07-11, `background/secrets_location.py`). Because they live outside any worktree, they resolve identically from a fork. Env *vars* must still be exported into the fork's shell (see the tmux/`set-environment` note in `background/start_worker.sh`). For **scoped tests specifically this is a non-issue**: `tests/conftest.py` `setdefault`s `SE_NTFY_TOPIC`/`SE_WAKE_HMAC_KEY` so collection never fails; and `SIM_FAST_MODE=1` is autouse, so tests need no Ollama.
- **Python venv — BREAKS if absent.** `.venv` sits at the main checkout root and is not inside a sibling worktree. A fork must reuse the shared interpreter by absolute path (`/home/rich/synthetic-enterprise/.venv/bin/python`) or `VIRTUAL_ENV` export; do not `pip install` per fork. Build-time: decide share-vs-recreate and wire it into the fork bootstrap.
- **Ports / daemons — MUST NOT be relaunched.** Singletons bound to fixed localhost ports: token proxy `:8801` (`background/token_proxy.py`), the file-api service (`background/file-api.service`), Ollama `:11434` (external, shared read-only). The daemon stack launched by `background/start_worker.sh` (`session_watchdog`, `staging_watcher`, `dispatcher`, `sim_runner`, `background_worker`, `supervisor`, `ntfy_mirror`, `sanity_daemon`, `deadmans_switch`) is a **singleton owned by the main checkout**. A fork must NOT start any of these — doing so collides on ports and on the NTFY topic. A fork consumes the already-running shared instances; scoped tests avoid them entirely via `SIM_FAST_MODE`.
- **Data lake — build-time verify.** `data/lake` is likely large/gitignored and won't populate in a fresh worktree checkout. If any scoped test reads it, the fork needs a symlink to the shared `data/lake`. Verify which scoped suites touch `data/`.
- **`tree_lock` lock file — per-worktree gotcha.** `LOCK_FILE` resolves via `__file__` to `<this-worktree>/docs/observability/.tree.lock`, so each worktree has its *own* lock — a `tree_lock` in a fork does not serialise against the main checkout or sibling forks. This is acceptable for worktree isolation (each worktree has its own git index; commits to distinct branches don't collide), but it is fatal to any cross-worktree map lock — see Half B, why option (c) is rejected.

---

## Half B — Map becomes read-during-build (H9)

### B1. Mechanism choice: per-atom status files (option a). Recommended.

The atom names three options. Evaluation:

- **(a) Per-atom status files `docs/design/atom_status/<id>.yaml`, map merged from them.** Each fork writes ONLY its own `<id>.yaml` — disjoint paths, so lost-update is **impossible by construction**, with no lock at all. Matches an existing repo pattern: `maturity_map.yaml` already *generates* `site/data/*.json` via `tools/generate_maturity_map_data.py` and `tools/generate_simplified_data.py` — a status→map fold is the same shape, low novelty. Simplicity-guard clean: N tiny YAML files + one merge function, no DB, no repository pattern.
- **(b) Append-only journal replayed into a view.** A *single* shared journal file re-introduces the exact concurrent-append race (needs a lock or relies on `O_APPEND` atomicity edge cases). To dodge the race you'd shard to per-fork journal files — at which point it is option (a) with a heavier schema plus a replay/compaction engine nobody needs at 2–3 forks. Over-built.
- **(c) Lock-for-map-writes-only, extending `tree_lock`.** Keeps the shared write and merely serialises it — i.e. it *codifies the interim bottleneck* instead of removing it, and it re-serialises the very level-record step H9 exists to de-serialise. Worse, `tree_lock`'s flock file is per-worktree (A4), so it would not even serialise across worktrees without relocating the lock to a shared path (`git rev-parse --git-common-dir`, or `~/.config/...`). More failure surface, keeps the bottleneck. **Reject.**

**Recommendation: (a).** It is the simplest construct that removes the contention *structurally* (director's "safe by construction, not by convention").

**Critical design detail — do NOT regenerate the map wholesale.** `maturity_map.yaml` carries rich hand-authored content (`simplifications` prose, `provenance`, `expert_hour`, `depends_on`). Regenerating it from status files would risk destroying that. Instead:

- A status file is a **narrow write-inbox** carrying only the fields a build fork mutates, keyed by atom id: `level_current`, plus any `evidence` / `simplification` entries to append. Example `docs/design/atom_status/H9_map_write_serialisation.yaml`:
  ```yaml
  id: H9_map_write_serialisation
  level_current: 1
  append_evidence: ["docs/design/WORKTREE_AND_MAP_CONTENTION_DESIGN.md"]
  append_simplification: ["2026-07-13 BUILD ..."]
  written_by: <fork-branch>
  written_at: <iso8601>
  ```
- A build-time merge tool (`tools/merge_atom_status.py`, to be built) folds each landed status file's specific fields into the existing `maturity_map.yaml`, in the integrator's single-threaded context, then clears the status file. `maturity_map.yaml` stays the hand-authored canonical, readable source of truth for the draw; forks never open it for writing.

Net: forks write disjoint inboxes concurrently (no lock, no lost update); the integrator does one mechanical, serial fold. The interim "orchestrator is sole map writer" convention is retired — the orchestrator is still the sole *committer* of the map, but it is now a mechanical fold of pre-computed inboxes, not a coordination point that forks block on.

---

## Proof test spec (director's DoD)

Two disjoint BUILD atoms building simultaneously in separate worktrees, both status updates landing, no lost writes, merged cleanly. New test (proposed `tests/background/test_atom_status_merge.py`) asserts:

1. **Concurrent writes are safe.** Two threads/processes write `docs/design/atom_status/<A>.yaml` and `<B>.yaml` simultaneously (stress loop, M iterations). After each round both files exist and parse as valid YAML — no partial/corrupt file.
2. **No lost update after merge.** Snapshot `maturity_map.yaml`; run `merge_atom_status.py`; reload. **Both** atom A and atom B show their new `level_current` — neither overwrote the other.
3. **Map integrity.** Post-merge `maturity_map.yaml` round-trips as valid YAML, and the set of changed atoms == exactly {A, B}; every other atom is byte-identical to the snapshot (the fold touched only its two targets, preserved all hand-authored fields).
4. **Clean git merge.** Branch A and branch B (disjoint `file_scope`s, neither touching `maturity_map.yaml`) merge into an integration branch with no conflict.
5. **Pre-flight is correct.** The merge-base changed-file intersection of branch A and branch B is empty; and a deliberately-overlapping pair is detected as non-empty and flagged for re-sequence (positive + negative case).

---

## Ordered BUILD task list

1. **Verify the isolation directive** against current official Claude Code subagent docs (frontmatter key/value, branch naming, worktree path). Record the confirmed form. (Gate for step 2.)
2. **Wire isolation** into `.claude/agents/saas-engineer.md` and `.claude/agents/sim-engineer.md` frontmatter only (read-only agents unchanged).
3. **Fork bootstrap plumbing:** point forks at the shared `.venv` by absolute path; export required env vars into the fork shell; ensure forks do NOT launch the daemon stack or bind ports; symlink `data/lake` if scoped tests need it (verify first).
4. **Build the status-file layer:** define `docs/design/atom_status/<id>.yaml` schema (write-inbox fields only) and `tools/merge_atom_status.py` (fold status → `maturity_map.yaml`, then clear inbox), following the existing `tools/generate_*` pattern.
5. **Scoped-suite selector:** a small helper mapping an atom's `file_scope` root → the `pytest tests/<dir>` set (table in A3); forks run only their scope.
6. **Integrator flow:** pre-flight merge-base conflict detection → orchestrated sequential merge (first-green-first, re-sequence on overlap) → run `merge_atom_status.py` → run full `make test` once on the integration branch.
7. **Write the proof test** (`tests/background/test_atom_status_merge.py`, spec above) and make it green.
8. **Retire the interim rule** in `docs/design/THREE_LANES.md` Lane 1 (orchestrator-sole-writer → status-file model) once the proof test lands.

---

## Open questions / build-time verification

- **[HIGHEST RISK] The `isolation: worktree` directive is unverified in-repo and undocumentable here** (no network). Its exact frontmatter form, branch-naming, and worktree path must be confirmed against official docs before step 2. Everything in Half A downstream of "a fork gets its own tree" assumes this works as the staging doc describes.
- Shared-`.venv` vs per-fork venv decision (deps, disk, activation).
- Which scoped suites actually read `data/lake` (drives the symlink decision).
- Exact scoped suite for `interface/**` atoms (both consumers, or a dedicated seam suite).
- Whether any fork ever legitimately needs a running daemon (if so, it must attach to the shared instance, never start its own).
- If a future need forces a cross-worktree lock, relocate `tree_lock`'s file to a shared path (`git rev-parse --git-common-dir`); option (a) avoids needing this.

## Recommended mechanism (summary)

Per-atom write-inbox files `docs/design/atom_status/<id>.yaml` — each fork writes only its own file (disjoint paths ⇒ lost-update impossible with no lock), and a build-time `tools/merge_atom_status.py` folds each landed inbox's `level_current`/evidence into the hand-authored `maturity_map.yaml`, run once serially by the integrator. The map stays the single readable source of truth for the draw; the interim "orchestrator-sole-writer" convention becomes structural. Rejected the lock-extension option (it just re-serialises the bottleneck, and `tree_lock`'s flock file is per-worktree so it wouldn't even serialise across worktrees) and the journal option (a shared journal re-creates the concurrent-append race; sharding it just reinvents option a).

**Single biggest build-time risk:** the `isolation: worktree` subagent directive is not used anywhere in this repo today and cannot be verified without official docs/network here — its exact frontmatter form and behaviour must be confirmed before any of Half A is wired.
