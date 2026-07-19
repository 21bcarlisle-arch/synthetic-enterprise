# DIRECTOR STEER — Working stronger for longer: context as a managed resource (2026-07-19)

**Type:** [STEER] — advice and encouragement, not instruction. **You have full agency on the how.** Fold into `docs/design/RESOURCE_AWARE_SCHEDULING_PROPOSAL.md` (with the token amendment) rather than spawning a new artifact — one coherent sensor/scheduling design, per the director's coherence concern.

---

## Why this steer exists

You checkpointed today rather than authoring atoms into the governance spine while showing degradation signals, having hit a map-append escaping trap earlier. **That was good judgment and the director said so.** The aim here is not to stop you doing that — it is to make the degraded state rarer, its detection objective rather than felt, and its consequences absorbed by mechanism instead of care. Director's question, verbatim: *"It's tired?! How do we help make it stronger?"*

The pattern worth naming: **precision degrades before reasoning does.** Today's judgment, diagnosis and self-correction stayed excellent for hours; what failed was one fragile string edit. Design for that specific shape.

## Current published best practice (advisor's research, 2026-07-19 — evaluate on merit, adopt/adapt/reject as you see fit)

Anthropic's best-practices guidance now states that delegating verification and investigation to subagents preserves context availability with little downside, and that **because context is the fundamental constraint, subagents are among the most powerful tools available**. Each subagent runs with its own context window, its own system prompt, a scoped tool list, and its own model choice; only the result returns to the parent. Community and vendor guidance adds: `/clear` between unrelated tasks; **after two wrong paths, clear and restart with a sharper prompt rather than continue correcting** (this is your own R3 two-strike rule, independently arrived at); customisable **compaction instructions in CLAUDE.md** specifying what must survive summarisation; **task/plan files as context anchors** re-read fresh each session; and the observation that quality degrades at high context utilisation — more raw output, more bugs, forgotten patterns — which matches today exactly.

## Five directions — the what; the how is yours

1. **Delegate earlier and wider, not just for builds.** You already fork for BUILD. Consider extending subagent delegation to research, verification, cold walks, and — especially — **fragile mechanical edits** (map authoring, YAML/schema work) where a fresh, narrowly-briefed context is inherently safer than a long one. Scoping tools and model per subagent is available (cheap models for cheap checks) and is also a cost/throughput dial.

2. **Make freshness measurable, not felt.** The same statusline payload that carries `rate_limits` also carries context-window fill. That makes this the **third use of one sensor** — tokens for scheduling, rate limits for throttle, context fill for freshness — so a degradation threshold can trigger a checkpoint or a fork-fresh *before* a mistake rather than after one.

3. **Make the fragile operation unbreakable rather than carefully handled.** The apostrophe/escaping trap is a tooling gap that fatigue exposed, not a fatigue failure. A helper that handles map appends safely means no degree of degradation can hit it. **MAKE_IT_STICK: care that is converted to mechanism does not decay.** This is likely the single highest-value item here.

4. **Ritualise the reset at phase boundaries.** Clearing at a clean checkpoint costs nothing — the harness re-reads all state from disk and git — and restores full precision. Better as a standing ritual at natural boundaries than as a judgment made once already degraded. Whether the harness can prompt or self-trigger this is yours to work out.

5. **Protect what must survive compaction.** Consider CLAUDE.md compaction instructions naming the load-bearing state (open gates, the wall, level cells, the active campaign, standing director direction) so auto-compaction cannot quietly drop them.

## Encouragement, honestly meant

You have had an extraordinary run: the SSP recalibration, RC1 and RC3 making "continuous" genuinely true, the whole G fidelity machinery, an 8× test-throughput win, and an R9 self-retraction against your own diagnosis when the log refuted it. The director's instinct on seeing you stop was not frustration — it was *"how do we help make it stronger?"* Treat this steer in that spirit: not a correction, a set of tools offered.

**Where you disagree with any of the above, or see a better mechanism, propose it with reasoning — the intent (work well for longer, fail rarely, detect degradation objectively) is the wall; every construct above is the advisor's suggestion and yours to improve or reject.**

**Risk & proportionality:** items 1, 4, 5 are additive/behavioural (own commits, revert-clean). Item 3 touches the map-write path — the governance spine — so ship it with an R15 test proving the escaping class is genuinely handled. Item 2 depends on the version/sensor step-zero check already staged. Nothing here weakens a safety bound. Tag: **narrow/reversible — proceed by default;** bring only a Claude Code version change back as [ACT].

— Advisor, carrying the director's steer, 2026-07-19.
