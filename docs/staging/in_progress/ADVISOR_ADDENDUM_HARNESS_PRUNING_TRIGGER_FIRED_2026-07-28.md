<!-- SUPERVISOR_DRAW: blocked -->
<!-- REGISTRATION ONLY. This document mints nothing, opens no front, and does not grant a turn.
     It amends the HELD docs/staging/in_progress/PARALLEL_RUNG_HARNESS_PRUNING_EVALUATION.md.
     It is explicitly SUBORDINATE to DIRECTOR_RULING_HARNESS_INVESTMENT_AND_ITS_EVIDENCE_2026-07-27:
     harness investment terminates on evidence. If actioning this would compete with content work
     or pre-empt the pending exit criterion, it waits. -->

# [ADVISOR-ADDENDUM] — The harness-pruning trigger has fired. Registration only; nothing to action now. (2026-07-28)

**Type:** [ADVISOR-ADDENDUM] via advisor bridge. Amends a held doc; does not replace it.

## 0. Why this is an addendum and not a programme

A canon-first check before staging found the shape already exists and is director-decided. `PARALLEL_RUNG_HARNESS_PRUNING_EVALUATION.md` (staged 2026-07-17, **HELD — DO NOT ACTION DURING OPS1**) already carries the ADOPT/ADAPT/REJECT standard, the ritual trigger ("re-check first-party practice at every epoch boundary / major release"), the governance-layer exclusion, and the verdict honesty bar ("argue each REJECT against the first-party baseline, not alongside it; every adoption deletes the bespoke path it replaces").

The advisor's initial framing duplicated that. It has been withdrawn. This document does exactly three things:

1. Records that the trigger fired, with the dated inventory, so the fact is not lost.
2. Adds items the 2026-07-17 list **predates**.
3. Separates the one item that does not belong in the harness lane at all.

**Recording is not actioning.** The hold stands.

## 1. The trigger (fact, recorded)

An Anthropic product release dated on or before 2026-07-28 announced: an **in-app browser** in the desktop app (sandboxed, configurable session persistence); **Claude Code artifacts** (session-built interactive pages, publishable, able to call MCP connectors); **iOS simulator support**; a **Linux desktop app** (Ubuntu/Debian) with parallel sessions under Git isolation, CI monitoring with auto-fix/auto-merge, inline diff review, sharing the CLI's `CLAUDE.md`/MCP/skills config; plus guidance on **model and effort-level selection** and on the **seven steering surfaces** (`CLAUDE.md`, rules, skills, subagents, hooks and others).

**Second source, better provenance (added 2026-07-28):** a 2026-07-27 interview with the Claude Code creator (Root Access / YC Startup School, `ycrootaccess.com/p/boris-cherny-building-claude-code`) — **the same author whose earlier "Steps of AI Adoption" the held 07-17 doc already reasons from, director-ratified.** It supplies method rather than feature copy, and is the source for items 9 and 10 below.

**Provenance caveat (R9):** the release inventory above is marketing copy relayed by the director; the interview is a transcript of claims, not documentation and not observed behaviour. Nothing in either is a fact about this machine until step-zero verifies it, as was done once before for the statusline `rate_limits` payload. In particular the named ablation instruments (a `--system-prompt` override; an undocumented `CLAUDE_CODE_SIMPLE=1` that strips all system and tool prompts) are **claims to verify, not facts to build on**.

**Transcript-noise correction (R9, self-caught).** The interview transcript is auto-generated and visibly garbled in places ("Quad" for Claude throughout; at least one mangled proper noun). The line item 9 rests on reads *"every six months, delete your quantum D, delete your skills, delete your hooks."* **"quantum D" is read here as `CLAUDE.md`** — the trio of user-side steering surfaces is CLAUDE.md / skills / hooks and the surrounding passage addresses users rather than harness builders. That reading is a **strong inference, not a quotation**, and it was written into an earlier revision of this document as though it were the term. The video was not watched, so it is not settled from source. Item 9's substance does not depend on the exact token — the accretion gap it names is observable directly in this repo — but the attribution should not be treated as verbatim.

## 2. Additions to the held list (items 1–5 of the 07-17 doc stand unchanged)

- **6. Effort levels ↔ our resource-class scheduling.** A dial the 07-17 list predates. Candidate consumer already exists and is inert: `executor_governor.py::max_tokens_per_window`, alongside `RESOURCE_AWARE_SCHEDULING_PROPOSAL`'s ≤1-heavy/N-light class model and `G5_effort_sizing_discipline`. R12 applies: a dial, never a target.
- **7. Skills ↔ `CLAUDE.md` bulk.** No `.claude/skills/` appears in canon. Every fresh seat pays for all of `CLAUDE.md`; a skill loads on demand. Steering *and* token-economy question, not either alone.
- **8. Native Git-isolated parallel sessions ↔ our fork machinery.** Items 1 and 3 of the held list now have a concrete first-party form. Relevant bespoke surface: `tree_lock`, merge-or-reap, the fork-lifecycle reconciler, the reap-guard — machinery whose cost is on record (33 salvage-tagged stranded branches; three live forks destroyed before the reap-guard landed). Likely ADAPT, not ADOPT: the governance layer above it is excluded by the 07-17 doc and stays.

  *Evidence note — **CORRECTED 2026-07-28**, the earlier version of this note conflated two different things and the correction is the point:*

  **There are two kinds of parallelism here and they are not comparable.** Ours is **lane parallelism** — N disjoint atoms, each a separate piece of product work, each a concurrent **writer** to a shared tree, each needing a merge home. That is why ≤3 is expensive to widen and why widening it is genuinely dangerous; the cap is a cap on *writers*, and its cost is on record (33 stranded branches, three forks destroyed pre-reap-guard). The source describes **task-decomposition parallelism** — one task, fanned out inside a sandbox, a second wave verifying or summarising, re-fanning, with only the finished result coming home. That is **one writer with a wide interior**. Going from 3 lanes to 8 lanes is eight writers and eight merge collisions; adopting the source's model is not widening lanes at all. An earlier revision of this note implied the source's numbers bear on our cap. **They answer a different question, and the misreading is the one that could actually hurt us** — read as pressure to widen writers.

  *Second, unnamed factor:* the cap may be **partly a hardware fact wearing a governance costume**. Every fork runs the suite; the throughput measurement found it CPU-bound single-core on one box with no GPU. A hosted sandbox does not inherit that constraint. If this holds, part of *"≤3 is inherent"* is really *"≤3 is what this box can compile"* — **checkable from primary state, not assumed here.**

  *On the standing challenge:* the naive-organ question (*was "1-3 max" measured, or picked and relabelled "inherent"?* — unanswered >24h, asked many ways) stands on its own merits and the honest answer remains that nothing wider than 3 has been run here. **It is not gated on this doc and should not wait for the parallel rung** — but note that the source's numbers are not the evidence that answers it.

- **9. An ablation ritual ↔ our monotonically-accreting rule set.** *The highest-value item here, and the one that cuts against us.* The source's method: on each new model generation, **delete** the system prompt / `CLAUDE.md` / skills / hooks, **use it**, and restore a line only where the model is observed to stumble **repeatedly on the same thing** — because the model reads every instruction every time, and much of what accumulates was correcting behaviours a newer model no longer exhibits. Their own harness had ~80% of its system prompt deleted on the current generation.

  **The gap this names in us:** every incident here forges a rule — R1 through R17, phase-close checklists, tiered approval — and **nothing has ever retired one.** There is a mechanism for adding and none for removing. That is the idle-hole class already known to this project: a correct decision with nothing watching the ground underneath it.

  **Scope — non-negotiable, and the whole reason this is safe to register:** the 07-17 doc's governance exclusion applies unchanged and with full force. **The epistemic wall, R12 anti-goal-seek, R13 baseline/curriculum split, console sanctity, the one-way-door predicate, HELD/dark/enabled semantics, seed-must-not-auto-advance are NOT ablatable at any model generation.** They are business and safety constraints, not model-capability patches; they do not become unnecessary because the model got cleverer. Ablation is scoped **only** to the model-behaviour-correcting half of the rule set. If a rule's justification is "the model would otherwise get this wrong," it is in scope. If its justification is "a real UK supplier could not know this" or "the director alone decides this," it is out.

  **Candidate test case to argue over, not a decision:** R9 (evidence-before-narrative) was forged by a real incident and has been cited many times since — but whether it is still load-bearing on the current model has never been checked, because there is no mechanism that would ever check it.

- **10. Loops / routines ↔ bespoke maintenance machinery.** Extends held item 2. The source describes ~20–30 daily one-sentence routines maintaining their own codebases: dead-code removal by static and dynamic analysis, an "abstraction police" that finds near-duplicate abstractions across a codebase and unifies them, and **deletion of useless tests added by older models**. Two direct hits on this project's own record: the `DirectDebitBook` / `dd_mandate_register` duplication that consumed several passes and was ultimately closed by enrichment rather than consolidation is precisely abstraction-police shape; and at 17,000+ tests collected, some fraction is ballast that no human pass will ever remove by hand. Note the tension to argue, not assume: this project's test suite is also its eval set, and the same source holds that **evals are the most durable artefact and should be appended to** — so "delete useless tests" and "never weaken a control" (R15) must be reconciled before anything is deleted.

## 3. The one item that is not harness pruning

**The in-app browser closes a documented verification ceiling, not a bespoke-vs-first-party question.** There is nothing to prune; nothing bespoke would be deleted. It belongs wherever SITE/R11 work lives, and its justification is independent of the parallel rung.

Evidence already in canon: phase entries repeatedly state *"no browser is available in this execution environment"* and name that honestly as the verification ceiling rather than claiming a pixel check. Every render-harness proof (`test_home_door.py`, `test_proof_door.py`, `test_world_door.py`, `test_company_door.py`) executes the page's real inline JS **in Node against published JSON** — genuinely load-bearing and R15-mutation-proven, but not pixels. And the axis-1 front-door verdict **FAIL 1/5, "It still looks awful"** is a visual judgement no Node harness can produce or catch.

**Independently corroborated (2026-07-28).** The source names verification as *the* thing practitioners most often get wrong, and its flagship long-running example is exactly this shape: run the old app in a VM, screenshot it, compare **pixel by pixel** against the rewrite, don't stop until done — a task still running after two weeks. It also concedes the current model remains imperfect at "in-the-weeds UI verification, something off by a pixel." So: the ceiling is real and worth closing, and closing it is not free.

**Open, not decided — and the first step is a fact-check, not a build:** the browser ships in the *desktop app*; the seat is a WSL2 CLI on Skynet. Whether it is reachable at all from this seat, and at what cost, is unknown to the advisor. No plan should be written on the assumption that it is.

## 4. The director's three questions, answered as requirements

Transmitted as requirements, not mechanisms. Where a mechanism is named it is a candidate to beat.

**(a) Cadence.** Requirement: the trigger must be a **sensed fact from primary state**, never a calendar interval — a second scheduler outside the draw is a known failure class in both directions (HARDEN doorbell thrash; RC1 starvation), and ONE_FRAMEWORK holds the draw as sole arbiter. Candidate to beat: a seat-version delta, already read once at step-zero (2.1.215). Epoch boundaries remain the second trigger per the 07-17 doc.

**(b) Not breaking everything.** Requirements: **one item, one verdict, one level** — never a bundle; REJECT must remain a real outcome (precedent: HARNESS_BEST_PRACTICE item 3 rejected — *"no new setting needed beyond the already-shipped `fallbackModel`"*); pilot before adopt and adapt before take (precedent: `phase-close-evaluator` written against the studied pattern rather than taking the generic built-in, because the bar here is specific). **Non-negotiable:** harness changes carry the highest blast radius in the project because the thing being changed is the thing that would catch the breakage — the seam that let three site wedges through was exactly this shape. R15-failable **both ways** on any adopted mechanism, one change per draw, with a named revert.

**(c) Not forgetting.** Requirement: every studied item carries a **recorded verdict** — adopt / adapt / reject / hold-until-X — in a form something reconciles, and **both HOLDs and REJECTs carry a re-check condition**. This is the idle-hole class (#8, E2): a correct decision going stale with nothing watching the ground underneath it, fixed each time by a machine-readable field plus a reconciler. Two live instances: **ULTRACODE**, held for post-OPS1; and item 3's REJECT above, which was true against the harness as it then was and has no re-check attached.

**The split that reconciles (a) with (b):** studying is read-only and cheap; adopting is gated and expensive. They should run at different rates. Sensing and recording a verdict fits the forward-discovery register's existing shape (DISCOVER-only, optional, preemptible). Only the adopt half needs a gated turn.

## 4b. Additions from the 07-27 interview that are not on the held list

**11. Routine-as-transport reconciles with ONE_FRAMEWORK — and it is an ADAPT, not an ADOPT.** The source distinguishes a *dynamic workflow* (one task broken into chunks) from *loops and routines* (one repetitive task run over and over, **no shared context but shared memory**; loop = cron running locally, routine = the same hosted so the machine can be closed). The obvious objection is that a clock-fired job competes with the draw as arbiter of what gets worked. That objection dissolves: **the routine is the transport, and its first act is to consult the draw.** The draw stays sole arbiter; the governance layer rides above the plumbing exactly as the 07-17 doc requires.

  Worth stating plainly: **this project already derived the routine model independently, from failure** — the scheduled bounded-invocation scheduler that replaced persistent-seat continuity, adopted to kill input-blocking heartbeat, death-on-API-error and token burn at rest. "No shared context, shares memory" is already how this works: every invocation re-anchors from primary state, canon-first forbids reconstruction from memory, and the director's paste-drafting rule exists because a fresh seat must be self-contained. **The repo is the shared memory.** What is new is that the primitive now exists first-party. And it matters because **both of this project's loop pathologies are scheduling bugs in a hand-rolled scheduler** — the ~2-min HARDEN doorbell thrash on one side; RC1 starvation, the overnight-rest draw bug and the seventh-class stall on the other. A cron-shaped transport has neither by construction.

**12. The cloud/local split forces a daemon triage nobody has run.** If a routine is hosted, the question stops being *should we adopt routines* and becomes **which of the thirteen running daemons are GitHub-API-only, and which genuinely need the box?** sim-runner needs the Elexon cache, the suite and the GPU; supervisor needs the tree. staging-watcher, ntfy-responder, director-comments and discovery-daemon look like pure API work. **One stands out well beyond the others: the deadman's switch runs on the machine it monitors** — the classic flaw, and not theoretical here, since the record shows stale-code deadman and supervisor daemons crying frozen while health_check restarted things underneath them. An external observer would be a real architectural upgrade, not a port.

  Also relevant to R2 ("committed ≠ deployed", a rule this project needed *because of* this class): the source's routines are one sentence each, ~20–30 of them; ours are thirteen Python daemons with systemd units, EnvironmentFile secrets, IaC drift and restart casualties. A platform-managed routine cannot be running July-22 code.

  **Gating unknown — step-zero, not an assumption:** a hosted routine can almost certainly reach GitHub and almost certainly cannot reach Skynet. If so the adoptable set is only the API-only daemons and everything touching the tree stays local. Establish that before any of this is planned.

**13. Sensor before pilot — the real gate is tokens, not safety.** The seven-day window was last read at 74% used and `executor_governor.py::max_tokens_per_window` is still inert. Any fan-out, workflow or routine pilot should be sequenced **after** the token-headroom sensor lands, not run alongside it while watching. This is a sequencing correction to the held doc's "bounded pilot" language, which is right but silent on what bounds it.

**14. A REJECT with no re-check attached — the live instance of §4c.** HARNESS_BEST_PRACTICE item 2 studied the real long-running-agents repo and built `phase-close-evaluator` rather than taking the generic `/goal`, because this project's phase-close bar is specific and judgement-heavy. That was a defensible REJECT **against a model generation**. The source now states of the current generation that the scaffolding is unnecessary — *"you don't need slash goal... it just knows it needs to do the task."* Nothing was attached to that REJECT that would ever cause it to be revisited. **This is not an argument that the reject was wrong; it is the concrete example of the requirement §4c states in the abstract**, and the first candidate for a re-check condition.

## 4a. Flagged, explicitly NOT recommended — Tier 1

The source claims prompt injection is effectively closed on current models (alignment training plus an interpretability-based classifier plus the auto-mode classifier), and that this materially changes harness and agent design. That bears on the reasoning behind the console-sanctity contract, the injection-shaped quarantine of safety-reducing requests arriving via commit or NTFY, and the friction the director has named in the phone-authority channel.

**This is registered as a re-check question and nothing more.** Any change to a safety control is **Tier 1 — the director typing at an idle console, no timeout, no staged commit however authored, including this one.** A vendor's claim that a threat class is handled is not a reason to remove a control that also defends against non-injection failure modes. If anything, the correct reading is the reverse: the value of the console contract was never only injection defence.

## 5. Proposed adoption bar — argue back

**An item qualifies for adoption only if it closes a gap already logged as costing us something.** "It is new" does not qualify. The browser passes easily (a documented verification ceiling and a real failed director verdict). Effort levels pass on the standing token-headroom finding. Artifacts-for-the-site does **not** — the site is a published product under SITE_CONSTITUTION with render-not-author discipline, and an artifact channel would sit outside it. The one plausible artifacts fit is `A3_approval_interface` (director decision packs, registered and unbuilt).

**R12:** the number of practices adopted is a diagnostic, never a score, target or headline.

## RISK

- **What it touches:** nothing executable. Doc-only registration in `in_progress/`. No map edit, no front, no gate.
- **Blast radius — attention, not code.** The probable failure mode is that this reads as licence to reopen the H lane the day after a ruling that harness work must terminate on evidence, and the day of a ruling that the published gap registers are the backlog. Mitigated by the draw-blocked marker and the explicit subordination in the header. **If that marker is insufficient to keep it out of the draw, say so and move this to `fyi/`** — that is the correct outcome, not a defect in the finding.
- **Second failure mode:** the browser item is the most appealing thing here ("we could finally see the site"), which is exactly how a genuine content-blocking gap becomes a harness detour. Mitigation: it is scoped in §3 as a SITE/R11 capability question with a **fact-check as its first step**, not a build.
- **Third:** §2 item 8 could be read as authorising deletion of fork machinery. It is not. Any ADAPT verdict there is gated behind the parallel rung exactly as the 07-17 doc has it.
- **FOURTH — the highest-blast-radius item in this document, added 2026-07-28.** §2 item 9 (ablation) could be misread as licence to delete rules from `CLAUDE.md`. **It is not, and the failure mode is severe and quiet:** deleting a governance rule removes the thing that would have caught the resulting breakage, and the loss would surface as a fidelity or honesty defect weeks later with no obvious cause. Guards, all of which must hold together: (i) the governance layer named in §2.9 is out of scope at any model generation; (ii) any proposal to retire a rule whose justification is safety, the epistemic wall, or director authority is **[ACT] first**, not propose-then-proceed; (iii) one rule per verdict, never a sweep; (iv) a retirement must state which incident forged the rule and what evidence shows that incident can no longer recur — absence of recent recurrence is **not** that evidence, since the rule is why it has not recurred; (v) reversible by construction, with the retired text preserved and a re-check condition attached. If those guards cannot all be met for a given rule, the answer is HOLD, not adopt.
- **Fifth:** items 9 and 10 both propose *deleting* things (rules, tests, abstractions) at a moment when the director has ruled that the published gap registers are the backlog. Deletion work is not content work and must not be counted as such against the pending harness exit criterion.
- **Proportionality:** reversible / narrow — registration only.

## WHAT THIS CREATES

Nothing drawable. Two facts on record (the trigger fired; its inventory), **nine** additions to a held list (items 6–14), and **three self-caught corrections** (the two-kinds-of-parallelism conflation, the hardware-vs-governance factor in the cap, and the transcript-noise attribution). The next action on any of it is the director's, or the parallel rung's — whichever comes first.

**One exception, and it is not created by this doc:** the standing naive-organ challenge on the fan-out cap (§2.8 evidence note) is already open, already unanswered, and answerable from primary state without adopting anything. It should not wait behind this.
