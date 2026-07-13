# PARALLEL BUILD: worktree isolation (harness, soon) + internal seams (Epoch 3) — the two halves

**Staged:** 2026-07-13 by advisor, director-decided, after a review of current
published practice (Apr-Jul 2026 sources). Disposition: **QUEUE** — register as
atoms; the worktree half ranks HIGH (it is the last known cap on build width).
Fold the recurring re-check into HARNESS_BEST_PRACTICE_ADOPTION.

## Why this matters: our exact problem is the documented headline problem
Published practice describes our failure precisely: multiple agents in ONE
working directory overwrite each other's edits, read half-modified files, and
corrupt the git index. Our own version: builds serialise behind
`maturity_map.yaml`, and a 17k-test gate runs per change. We did not hit an
exotic problem. We hit THE problem, and the answer already exists.

## Half 1 — WORKTREE ISOLATION (harness change; do soon; largely native)
Git worktrees are now the standard isolation primitive for parallel AI agents:
each agent gets its own checked-out directory and branch, sharing one .git
object store. Claude Code supports this natively — a `--worktree` flag, and
(the important one for us) an **`isolation: worktree` directive in SUBAGENT
frontmatter**, which provisions a fresh worktree per parallel agent invocation.
**Our build agents are already subagents with model assignments in
`.claude/agents/`.** Verify the directive against current official docs, then
adopt.

Requirements (mechanisms yours):
1. **Concurrent BUILD atoms run in isolated worktrees**, one branch each. No
   two agents share a working tree.
2. **Kill the map contention properly:** `maturity_map.yaml` becomes
   READ-DURING-BUILD; per-atom status/evidence is written to its own file (or an
   append-only journal) and the map is generated/merged from those. Published
   practice says the shared task file must be readable but not written by agents
   mid-work — our bug exactly. **The map remains the single source of truth for
   the draw; no update may be lost.**
3. **Merge model:** orchestrated sequential merge — one integrator merges
   branches in a defined order after each passes its checks. (PR-per-agent is
   the alternative; sources say the simple model is right below ~4-5 concurrent
   agents, which is us.)
4. **Test economics:** run the SCOPED suite per worktree; the full 17k suite runs
   ONCE at integration, not per fork.
5. **Per-worktree environment is real plumbing, not free:** env files, ports,
   dependencies, and our daemon stack do not carry over. Handle it explicitly;
   do not assume.
6. **Pre-flight conflict detection** before merging (e.g. merge-base diffing) so
   overlap is caught early and the orchestrator can re-sequence rather than
   discover a mess at merge time.

## Half 2 — INTERNAL SEAMS (Epoch 3; the other half, and the harder one)
**Worktrees solve FILE-SYSTEM collisions. They do NOT solve LOGICAL
dependencies.** Published practice is explicit: if Agent B needs Agent A's
signatures while working, worktree isolation will not help — those tasks must be
SEQUENCED, not parallelised. Two agents both reaching into
`hedged_settlement.py` still collide at the merge, in meaning if not in bytes.

**The fix is the doctrine we already have, applied inward.** We built an
epistemic wall between sim and company and enforced it with hooks and tests —
not with a network. Apply the identical pattern INTERNALLY: typed interfaces
between billing / pricing / settlement / collections, enforced the same way.
That is exactly what "walled interfaces" means, and it is Epoch 3.

**Consequence for the roadmap (record it):** the architecture work and the
velocity work are THE SAME WORK. Epoch 3's internal seams are not only the
go-live boundary — they are what makes concurrent building safe. Rank Epoch-3
DISCOVER/FRAME accordingly (thinking is never gated).

**And it answers the monolith challenge honestly:** the monolith did not cause
this — one working tree did, and worktrees fix that. But a monolith stays
modular only by DISCIPLINE (microservices enforce it through pain). We chose the
monolith and have not yet discharged that obligation. Internal seams are how we
pay it.

## DoD
Worktree isolation live for concurrent BUILD atoms (prove: two disjoint atoms
building simultaneously in separate worktrees, both status updates landing, no
lost writes, merged cleanly); map contention structurally eliminated; scoped
tests per fork + full suite at integration; per-worktree env handled; conflict
pre-flight in place. Epoch-3 internal-seam design registered and progressing in
the DISCOVERY lane. Recurring harness re-check absorbs this area (it is moving
monthly).
