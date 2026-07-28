<!-- PARKED in_progress 2026-07-28 (RUNG-7 planner tick). -->
<!-- §4-DEFECT (per DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE §4): this ruling arrived with NO
     'WORK THIS CREATES' block. Handled per §4 = mint the work I can identify + request the block from
     the author; NOT silently absorbed.
   MINTED (docs/staging/, drawn next tick): the six Acceptance items —
     1 working_day_calculator (§2.1)          2 rng_substream_primitive (§2.2)
     3 size_and_clone_ratchet (§3)            4 owned_quantity_registry_gate (§4)
     5 shared_primitive_ensuring_activity (§5.1–5.4, Acceptance 5&6)
     7 money_representation_evidence (§6, Acceptance 7 — DISCOVER-only, decision director-reserved).
   BLOCKING SUB-ITEMS (why parked, not done): (a) the WORK-THIS-CREATES block is requested from the author
     via NTFY 2026-07-28; (b) §2/§3/§4 BUILD needs an open front / director BUILD_OPEN (each mint's DISCOVER
     half is drawable now; its BUILD half is blocked_on director_build_open); (c) Acceptance item 7 stops at
     the wall (money representation is director-reserved) — evidence-gathering queued, migration forbidden.
   UNBLOCKS ON: author's WORK-THIS-CREATES block + a BUILD_OPEN/front for §2–§4 + the director's item-7
     ruling. Archive only when Acceptance items 1–6 land and item 7's evidence is returned. -->

# [DIRECTOR-RULING] — Shared primitives, code standards, and making "should this have been shared?" an ensuring activity (2026-07-28)

**Type:** [DIRECTOR-RULING] via advisor bridge. Written as decisions plus problems. Where this document names a mechanism, treat it as a candidate to beat, not a specification — you are closer to the detail.

**Staged:** 2026-07-28 ~08:40 BST. **Proportionality:** §2 is [ACT]-first (touches domain correctness). §3–§4 are contract-touching — implement with the named mitigations. §5 is reversible/narrow — just do it.

---

## 0. Provenance — this is a census, not an impression

The advisor pulled the repository tarball and ran AST-level structural clone detection over all **788 source modules** (tests excluded). Every number below is reproducible by re-running that analysis; none of it is recalled or inferred. Method: normalise each function body to its node-type sequence (identifiers and constants discarded), hash, group identical fingerprints of ≥45 nodes appearing in ≥2 distinct files.

**Result: 70 clone-sets, 223 structurally identical function instances across different files.**

The census also found: **91 register modules** under `company/`; **17 files** defining their own working-day arithmetic; **3 files** in the entire source tree that mention bank holidays; **one** shared utility module in the whole repo (`background/ntfy_utils.py`); VAT logic touching **107 files** with 9 raw `0.05` literals; and layer back-edges (`sim → simulation`, `company → saas`) against a stack the architecture diagram declares strictly one-directional.

**This is not a discovery of carelessness.** An agent that builds one register per phase, against a phase-close checklist that asks *"is it tested, does it pass?"* and never asks *"does this already exist?"*, will produce exactly 91 hand-rolled registers. It is the predictable output of the incentive. That is why §5 matters more than §2–§4: exhortation will not fix an incentive, and a mechanism will.

---

## 1. What this connects to that is already ratified

**It is the same class as a defect you already found.** `DIRECTOR_RULING_HARNESS_INVESTMENT_AND_ITS_EVIDENCE_2026-07-27` records, as a real defect surfaced by a HARDEN pass, *"Bacs rails counting calendar rather than working days."* That was fixed as an instance. **R10 requires the class fix.** The census says the class is at least 17 modules wide and that no member of it knows UK bank holidays exist.

**It has a home in the live governance model.** `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` made the published gap registers first-class planner mint sources. This ruling adds one more register to that list (§5.1) rather than opening a competing campaign. Rank it by the triage method being minted under GAP2; do not special-case it.

---

## 2. DECISION — two class fixes proceed now, because they are correctness defects

Neither of these is tidiness. Both change what the model can be right about.

**2.1 Working days.** Regulatory deadline arithmetic — GSOP, SLC obligations, complaint clocks, Bacs — is specified in *working days*. It is currently computed by ~17 independent implementations, none bank-holiday-aware. Under `REGULATORY_RULES_AS_FIDELITY_ORACLE`, this is a fidelity gap of the first kind: the SIM cannot produce the failure the rule exists to prevent, so a deadline breach that a real supplier would be fined for is currently unreachable.

**Requirement:** one canonical working-day calculator with a real, dated UK bank-holiday calendar (England & Wales at minimum; the four-nations split is yours to judge on materiality). Every existing caller migrates. A guard test reds if any other module defines its own.

**2.2 RNG substream derivation.** `_substream()` exists in 8 independent copies across `simulation/`. Determinism and reproducibility are the foundation of varied-population-per-run and, downstream, of the epoch-4 evolutionary tournament — a tournament over lives whose seeding is derived eight different ways is not a tournament. This is the same class as the draw bug (level-matched dependency gate): shared semantics, unshared implementation.

**Requirement:** one canonical substream primitive; all callers migrate; a guard test on second definitions.

**Both fixes must be R15-proven failable** — inject a second definition, confirm the guard reds; clean, confirm it passes.

---

## 3. DECISION — the remaining debt drains by ratchet, never by remediation sprint

The 91 registers and the remaining ~220 clones are **not** to be refactored as a campaign. They must not compete with the epoch arc for a draw slot.

**Required shape (this part is decided; the implementation is yours):**

- No existing source file may exceed its current line count.
- New files and new functions are capped (600 / 60 are candidate numbers to beat).
- Any file touched by other work must come out no larger than it went in.
- The clone census gets a **ceiling at today's 223**, not a target of zero.

Debt then drains as a side-effect of ordinary work. A register nobody opens stays duplicated indefinitely, and that is the correct trade.

**Explicitly in scope for the ratchet, not for a sprint:** a base `Register` class for the 91 (migrated on touch); a shared `log()` for the 8 background daemons; `_clamp_term_end` across the 6 phase runners; `season_for_date` across the two profile classes; VAT as one constant.

---

## 4. PROBLEM — structural clone detection is blind to your worst recurring class

A structural detector catches *identical* bodies. It cannot see **semantic** duplication: two implementations of the same quantity, written differently.

That is precisely the class that keeps recurring: three disagreeing net-margin figures ~4.2x apart on one published surface; `payment_channel`'s profile label vs `arrears_engine`'s per-bill DD-failure dispatch; M2's duplicated register. **None of those would trip a clone detector.**

**The problem to solve:** make it structurally impossible for a second module to become a second source of truth for a domain quantity that already has one.

**Candidate to beat:** a registry of domain quantities, each with one declared owning module, and a gate that reds when a non-owner computes an owned quantity. Net margin, treasury, EV, bad debt, cost-to-serve, carbon are the obvious first entries. You may well have a better mechanism; the requirement is the property, not the registry.

---

## 5. PROBLEM — none of the above is an *ensuring activity*, and that is the real gap

Everything in §2–§4 is a **gate**: it fires on a diff and returns pass/fail. Gates catch regression. **No gate ever asks "should this have been shared?" or notices "this is the 92nd register."** Nothing so far makes the machine look at the codebase as a whole, which is why the duplication accumulated silently through hundreds of green phases.

**5.1 The census becomes a standing register.** Publish it as a gap register — clone count, register count, shared-primitive inventory, quantity-registry coverage — and wire it as a planner mint source under the 2026-07-28 gaps ruling. Drift then enters the backlog the same way every other published gap does.

**5.2 The phase-close checklist gains one question:** *"Does this capability already exist elsewhere — did I search before building?"* One line, at the exact point where 91 registers became 91 registers.

**5.3 A standing structural review** on the existing retro cadence (~50 phases / 2 weeks): run the census, report drift, give a verdict.

**5.4 Route 5.3 through the fresh-context evaluator you already run at phase close.** This is the load-bearing part. The same context that wrote the 91 registers is the least able to see them as a problem; a fresh context has no investment in defending them.

---

## 6. RESERVED TO THE DIRECTOR — do not decide this one alone

**Money representation.** Every module the advisor sampled — including `saas/bill_generator.py` and `saas/reporting/annual_report.py` — computes money in `float`. There are zero uses of `Decimal` in the sampled set. Against a Tier-1 standing rule of *bills accurate above all*, the current position is not "float" or "Decimal" — it is **undeclared**, which is the worst of the three.

**Bring the director a recommendation and the evidence** (worst observed rounding drift across a full billing run; blast radius of a boundary conversion). Either answer can be right. The ruling is his. **Do not migrate money types on your own initiative.**

---

## 7. Anti-Goodhart clause — binding

Clone count, register count and file size are **tripwires and reported facts, never scores to minimise, and never inputs to any reward, fitness or selection mechanism.** Made a target, clone count is trivially gamed by structural perturbation that raises real duplication while lowering the metric. Per standing canon: degenerate emergent behaviour here would be a fidelity bug report, not progress. Survival of the gates stays a hard constraint, never folded into a scalar.

---

## 8. RISK

**What this touches.** §2 touches date arithmetic used by compliance-deadline logic and by Bacs cash timing — i.e. it can move published financial and compliance figures. §2.2 touches RNG derivation, so it can move *every* stochastic output. §3 touches the build gate. §5 touches the phase-close checklist and the planner mint sources.

**Blast radius — highest concern.** Migrating 17 working-day callers to a bank-holiday-aware calculator **will change outcomes**, correctly: deadlines that previously fell on a bank holiday will move, and some breaches that were unreachable will start firing. That is the point, but it means baseline diffs are expected and must not be read as regressions. **Mitigation:** land the calculator and its guard first with call sites unchanged; migrate callers in a second, separately-verified pass; publish an explicit before/after on any moved figure with its `//` basis clock rather than letting it appear as silent drift.

**Second concern — RNG migration invalidates comparability.** Unifying `_substream` will change draw sequences, so any frozen baseline or lift table computed under the old derivation is no longer comparable. **Mitigation:** treat this as a deliberate baseline break — re-freeze after migration, and do not run it concurrently with any campaign whose evidence depends on an UNMOVED lift table (W1_6 is the live example).

**Third — the ratchet can wedge the publish gate.** A size ratchet that reds on any growth will block legitimate work mid-phase. **Mitigation:** ratchet warns for one full cycle before it gates, and carries a named, logged override rather than a silent one.

**Probable failure mode.** The most likely way this goes wrong is the familiar one: the guards get written and their *dependents* don't get retested — the stale-test class that produced four publish-gate wedges in one day. Every guard added here must be R15-proven failable in both directions before it is relied upon.

**Sequencing note.** If §2.2 and any live UNMOVED-baseline campaign contend, the campaign wins and §2.2 waits. Say so rather than doing both.

---

## 9. Acceptance

1. One working-day module with a dated bank-holiday calendar; 17 call sites migrated; second-definition guard R15-proven both ways; the moved-figure diff published.
2. One RNG substream primitive; 8 call sites migrated; guard R15-proven; baseline re-frozen and the break declared.
3. Ratchet live (warn ≥1 cycle, then gate); clone ceiling recorded at 223; override path named.
4. Quantity registry (or a better mechanism achieving the same property) covering at least net margin, treasury, EV, bad debt, cost-to-serve, carbon — with the gate proven failable on a planted second computation.
5. Census published as a gap register and enumerated as a planner mint source.
6. Phase-close question added; standing structural review scheduled on the retro cadence and routed through the fresh-context evaluator.
7. Money-representation recommendation + evidence returned to the director as one [ACT]. **Not actioned.**

Items 1–6 proceed. Item 7 stops at the wall.
