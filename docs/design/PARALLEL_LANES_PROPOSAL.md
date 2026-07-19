> **[SUPERSEDED 2026-07-19]** by `RESOURCE_AWARE_SCHEDULING_PROPOSAL.md` §1–2 (three-lane concept -> the resource-class model). Retained for history; do not build from this.

# Parallel-Lanes Proposal — the overdue SELF_DIRECTION item 3

**Staged as owed:** SELF_DIRECTION_AND_PARALLELISM.md item 3 (requested
2026-07-10, never delivered until now). **Answering to:**
GOVERNED_COMPANY_AND_THREE_LANES.md Part 2 (director-decided 2026-07-12,
"fork as enforcement, not risk") — that document sets the FRAME (three
lanes: SIM-builder / company-builder / governance+harness, typed-interface-
only communication, single-writer preserved); this proposal is the thing
its own text says must exist: an evaluation of that frame against
tree-lock/worktree/daemon *reality*, recommending mechanics rather than
generic sharding.

**Method note:** every claim about "current reality" below is evidence from
this actual repo/session, not a generic distributed-systems argument —
including three real non-fast-forward push rejections encountered directly
in the session that also built the Part 1/2 thin-starts this proposal
follows.

## 1. Current reality (evidence, not assumption)

**Concurrent writers on one working tree, already true today, not
hypothetical:** `background/sim_runner.py` and `background/supervisor.py`
run as long-lived daemons on this same machine, independent of any
interactive session. `background/tree_lock.py` serializes the actual git
add/commit/push sequence across all of them — but does NOT stop two
writers from having divergent *local* commits that then need a
fetch-and-merge before push. This session hit exactly that three separate
times: `sim_runner.py`'s own "Auto-process run complete" cycle landed a
commit between this session's commit and push twice, and a THIRD time an
advisor-staging-bridge commit (`[ADVISOR-STAGED]`, a distinct legitimate
identity, `21bcarlisle-arch`) landed mid-turn. All three resolved cleanly
via `git fetch` + `git merge --no-edit` + `git push` with zero real
conflicts — because by convention, each writer's changes are scoped to
disjoint files (this session's own commits stayed inside source/tests/docs
it deliberately touched; the background loop's commits stay inside
generated site/data/report artefacts; the advisor bridge only ever adds new
files under `docs/staging/`). **The wall already works today because of
file-scope discipline, not because of any structural isolation mechanism.**
That is the real baseline the three-lane frame is being evaluated against.

**The wall (sim/ vs company/) is the one hard, pre-existing boundary** —
enforced today by `tools/epistemic_verifier.py` (a post-hoc import scan,
catches `company/` importing sim internals) and, as of this session,
piloted at DEVELOPMENT time by `.claude/hooks/lane_wall_hook.py` (denies a
same-session cross-wall Read/Glob/Grep when `SE_LANE` is set). Neither
mechanism existed as *dev-time* enforcement before this session; only the
post-hoc scan did.

**A seam-guarding role already exists and already IS most of "governance+
harness":** `.claude/agents/{sim-engineer,saas-engineer,interface-steward}.md`
already implement almost exactly the three-lane split this document's Part
2 asks for — sim-engineer and saas-engineer are scoped to their own
directory tree, and interface-steward is *already* "the only role permitted
to touch both sides of the seam, and only at the seam itself"
(`interface/`, with a `contracts/` subfolder). **The three-lane frame is
not a new invention here — it is a real, already-partially-built pattern
that is missing two things: physical worktree isolation, and a dev-time
enforcement mechanism (the lane_wall_hook pilot is the first piece of the
second gap).**

## 2. Evaluating the three-lane frame against this reality

**Git worktrees (`EnterWorktree`/`ExitWorktree`/`Agent(isolation:"worktree")`
are already available tools, no new tooling required):** a worktree gives
each lane its own checked-out directory sharing one `.git`, which solves a
real gap the current single-tree convention does NOT solve: two lanes with
*uncommitted* edits to files in their own scope currently share one working
directory, so an accidental edit collision (not just a commit-time
conflict) is possible today, even if it hasn't happened yet by luck of
disjoint scoping. Worktrees remove that risk structurally rather than by
convention. Cost: worktrees are genuinely cheap (a checkout, not a clone);
`tree_lock`'s serialize-the-actual-git-write model composes fine with them
— only the final merge-to-main step needs the lock, same as today.

**Typed interface contracts as "the negotiated artefact":** already
underway — `interface/contracts/` plus the interface-steward role. The
frame doesn't require new mechanism here, it requires *habit*: sim-builder
and company-builder lanes should treat a contract change as a
pull-request-shaped negotiation with interface-steward, not a direct edit,
even though nothing currently stops a session from editing `interface/`
directly today.

**Single-writer preserved, integration serialized per tree:** already true
in practice (see §1) and unaffected by adding worktrees — `tree_lock` is
already the serialization point regardless of how many working directories
feed into it.

## 3. Real gaps found (not glossed over)

1. **The lane_wall_hook pilot activates via an `SE_LANE` environment
   variable, checked at hook-invocation time.** This works cleanly for a
   *single human-directed session* that exports `SE_LANE` before starting
   focused work. It does **not** obviously work for the Agent tool's own
   parallel-subagent-fan-out pattern (SUNDAY_WIDE's own standing default) —
   there is no evident mechanism for the Agent tool to set a custom
   environment variable scoped to one spawned subagent's own tool-call
   environment. **Recommendation:** for genuine multi-agent parallel lanes
   (as opposed to one human's sequential focused sessions), evolve the
   pilot from env-var-keyed to **worktree-path-keyed** — a small marker
   file (e.g. `.se_lane` in the worktree root, checked by the hook via
   `Path.cwd()` or the tool-call's own working directory) naturally scopes
   per-worktree without needing env-var propagation through subagent
   spawning at all. This is a real, honestly-registered follow-up, not
   built in this pass (the pilot's own DoD only asked for env-var-keyed,
   single-session proof).
2. **The "governance+harness" lane is not disjoint from the other two the
   way sim/ and company/ are.** Both other lanes legitimately need to read
   shared reference material that lives outside sim/company entirely —
   `CLAUDE.md`, `PRIORITIES.md`, `docs/design/maturity_map.yaml`,
   `background/*.py`. The lane_wall_hook pilot correctly does NOT restrict
   these paths for any lane — they are shared context, not wall material —
   but this means "three lanes" is really "two mutually-exclusive lanes
   plus one shared-context lane that everyone can read," not three
   symmetric partitions. Naming this precisely rather than implying false
   symmetry.
3. **Bash is out of scope for the current lane_wall_hook pilot** (Read/
   Glob/Grep only) — a `cat sim/foo.py` via Bash is not denied. Registered,
   not fixed: closing this would need command-string path extraction
   (regex over arbitrary shell syntax), a meaningfully harder and more
   false-positive-prone problem than the point-in-time-read hook already
   accepts a similar tradeoff for. Left as a known, bounded gap.

## 4. Recommendation

1. **Adopt git worktrees per lane using the tools already available**
   (`EnterWorktree`/`ExitWorktree` for an interactive session, or
   `Agent(isolation:"worktree")` for a spawned subagent) whenever a lane's
   work is substantial enough to run alongside other lanes' work in the
   same time window. Do not build new worktree tooling — it already exists.
2. **Keep the `SE_LANE` env-var pilot for single-session focused work**
   (the case it was built and proven for this session) but do not yet
   claim it solves multi-agent parallel fan-out — that needs the
   marker-file evolution named in §3.1, which is registered as the next
   real step for `H6_lane_wall_development_pilot`
   (`docs/design/maturity_map.yaml`), not built here.
3. **Formalise the existing agent-role split as THE three-lane
   implementation**, rather than treating GOVERNED_COMPANY_AND_THREE_LANES
   Part 2 as asking for something new: sim-engineer / saas-engineer /
   interface-steward already are SIM-builder / company-builder /
   governance-at-the-seam. The gap this proposal closes is naming that
   correspondence explicitly and adding the two enforcement pieces (dev-
   time hook pilot, worktree isolation) it was previously missing.
4. **Single-writer-to-main stays exactly as-is** (`tree_lock`, sequential
   fetch/merge/push) — nothing about adopting worktrees changes this; it
   is already proven robust under real concurrent writers this session.

## 5. What this proposal deliberately does NOT do

Per the two-way-door filter and R3 (fix the class, don't re-patch): this
does not build the marker-file lane-keying evolution (§3.1), does not
retrofit worktrees onto any currently-running lane, and does not change
`tree_lock.py` itself. All are named, bounded follow-ups, not silent scope
creep into this document.
