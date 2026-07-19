# DIRECTOR AMENDMENT — Tokens as the second resource dimension (amends RESOURCE_AWARE_SCHEDULING_PROPOSAL, 2026-07-19)

**Type:** [STEER] — an amendment to an EXISTING proposal, deliberately not a new artifact. Absorb into `docs/design/RESOURCE_AWARE_SCHEDULING_PROPOSAL.md` as additional scope; do not spawn a parallel document. (Related in-progress steer: `DIRECTOR_STEER_RESOURCE_AWARE_SCHEDULING_2026-07-19.md`.)

**Reading first, credit where due:** the proposal's root-cause section is exactly right — the seat was never hard-blocked, interleaving was permitted but not the default, and the shared-pool ceiling trimming near-zero-cost light lanes is the real defect. The heavy/moderate/light budget split with I1–I4 and the four R15 mutations is a sound design. This amendment adds the dimension it does not yet model.

---

## 1. The gap: the proposal is CPU-only

Every resource judgment in it is about local CPU. But the binding constraint on the work the director most wants expanded — forward-looking DISCOVER/FRAME research — is **not CPU at all**. Discovery is near-zero local cost and high token cost (one fork consumed ~164k tokens today). If forward discovery becomes a standing parallel lane, the token window binds long before the cores do.

**Director's framing:** *"There is core work and optional. Spend [spare] tokens on optional… we end up with a rhythm, determined by its limit resets."*

## 2. Step zero — establish whether the sensor exists before designing around it

Check `claude --version` on the box. Claude Code exposes a `rate_limits` field in the JSON piped to a statusline command on stdin (reported from v2.1.80; fields include the 5-hour and 7-day windows with used-percentage and reset time; populated for Claude.ai Pro/Max auth, empty on API-key auth). **Verify this against the installed version and the actual stdin payload — do not build on the advisor's report of it.**

- If present: build the sensor. No update, no risk.
- If absent: an update is a *change with real blast radius* on a machine running autonomous loops — read release notes first (there are third-party reports of releases altering rate-limit consumption behaviour), pin the version in-repo (`.claude/settings`) per the IaC rule, and treat it as its own atom.

## 3. The sensor (requirement, not mechanism)

Local, authoritative token-headroom state, readable by the loop and the daemons. Known constraint to design around: the statusline is **push-on-render**, not poll-on-demand — so state goes stale while idle. Evaluate whether a written-to-disk snapshot is fresh enough for scheduling decisions, and what the fallback is if not. **Fail closed on staleness in one direction only** (see §5).

## 4. Two priority classes on top of the existing resource classes

The proposal's `light | moderate | heavy` classifies *cost*. Add an orthogonal classification of *entitlement*:

- **CORE** — campaign work, blockers, safety, the director's standing direction. Guaranteed budget; runs regardless of headroom.
- **OPTIONAL** — forward-looking discovery, red-teaming, exploratory analysis, standing-backlog research. Draws **only** above a headroom threshold, and **yields immediately** when core work needs the budget (preemptible, in the spot-instance sense).

This makes forward discovery affordable without risking core throughput, and gives the treadmill-quiet mechanism something genuinely valuable to reach for instead of either busywork or nothing.

## 5. Non-negotiables — coherence with existing law

- **Headroom is a DIAL, never a WALL** (CLAUDE.md Rule 0). Low or unknown headroom may reorder or defer OPTIONAL work; it must never empty the feasible set or stop CORE work. An empty feasible set caused by a resource reading is a defect in the dial, not a legitimate hold. If the sensor is stale or missing, CORE proceeds unconditionally and only OPTIONAL is withheld.
- **Utilisation is a diagnostic, never a target** (LAW A / R12 anti-goal-seek). Do not optimise for consuming the window. The goal is *not wasting headroom on genuinely valuable work* — never *burning tokens to raise a number*. No metric derived from utilisation may feed reward, selection, or priority in a way that rewards spending.
- **The draw-mix balance still binds** (three clauses, standing). The OPTIONAL lane must not become a loophole for harness polish while product work waits: OPTIONAL is for forward *discovery and research*, and the mirror clause — humming engine ⇒ throttle to the company — applies to it in full.
- **Forward discovery means constraints on the present, not designing the future.** Look ahead to find what today's decisions must accommodate (the varied-population-per-run requirement for the Epoch-4 tournament is the canonical example); do not produce deep design for distant epochs, which decays and consumes director attention.
- **I4 stands untouched** — disjointness, tree lock, merge-or-reap, locked-worktree guard. This adds a dimension to scheduling, not a relaxation of parallel safety. R15 applies: prove any new bound by mutation.

## 6. Housekeeping — reduce the fragmentation this creates

Four docs now touch parallelism/scheduling: this proposal, `FAN_WIDENING_SAFETY_CASE.md`, and two older ones — `PARALLEL_LANES_PROPOSAL.md` and `H20_PARALLEL_MAINTENANCE_LANE_FRAME.md`. **Reconcile them:** state plainly which are superseded and by what, retire or mark them, and leave one authoritative home for scheduling guidance. The director's concern, verbatim: *"we have a habit of stages creating forks in its guidance… keeping coherence is not trivial."* This amendment is deliberately folded into an existing doc for that reason; do the same with the legacy pair.

## 7. Note for the pending fan-widening [ACT]

Today's evidence: three lanes authorized, rarely more than one used — the constraint was authorization, serialisation behind heavy work, and the shared-pool trimming, not the count. **Widening the count buys little until the budget split lands.** Say so in the [ACT] so the director can sequence the two correctly.

**Risk & proportionality:** step 2 is read-only; the sensor is additive (own commit); the priority classes touch the draw — sequence after the budget split, prove bounds by mutation, one change per turn. Tag: **contract-touching — implement with named mitigations; any Claude Code version change or weakening of a safety bound comes back as [ACT].**

— Advisor, carrying the director's steer, 2026-07-19.
