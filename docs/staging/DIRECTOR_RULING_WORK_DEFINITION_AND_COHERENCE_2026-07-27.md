<!-- CONTINUATION BANNER (worker tick 2026-07-27) — this ruling is PARTIALLY ABSORBED; it stays in
staging ROOT (genuine open work) so the tick keeps drawing it, and its own §1+§3 mechanism now keeps
the RULE-0 HARDEN treadmill SUPPRESSED while it is unconsumed (so no busywork masks the remaining work).
WORK THIS CREATES — progress:
  [DONE] Item 1 — §1 HARDEN demotion + §3 rung-order: RULE-0 HARDEN tier SUPPRESSED while an
         unconsumed staged [DIRECTOR-RULING]/[STEER] is present (background/supervisor.py::
         _unconsumed_director_ruling_or_steer + the guard in _self_refill_draw). R15 mutation-proven
         BOTH ways (test_supervisor.py: test_harden_suppressed_while_staged_director_ruling_unconsumed,
         _is_content_driven_not_only_filename, _ignores_parked_and_archived_rulings, _ignores_daemon_
         markers). Reproduces the exact 2026-07-27 08:23-10:25 state as a failing test. 211 supervisor/
         harden/planner tests green.
  [OPEN] Item 2 — §2 rung-7 mint-source extension to rulings/steers + the retrospective mints
         (merit-order/gas-first price reconstruction = the SSP-hold unblock + Board Spec 004
         reconstructibility; DD seasonal cash-flow FRAME; site evidence-pages-behind-diagram). Lane:
         harness (mint source) + product (the retrospective atoms). Director tag: DO THIS FIRST of the
         remainder — unblocks product today.
  [OPEN] Item 3 — §3 rung-1 ordering test at find_work level (a HARDEN candidate + an unconsumed
         staged ruling -> the ruling's `primary` wins and no HARDEN is appended as 'ALSO'). Partially
         covered by item 1's suppression; add the find_work-level assertion to close it explicitly.
  [OPEN] Item 4 — §4 "WORK THIS CREATES" parser + the missing-block defect report (binds the advisor:
         a ruling arriving without the block is a defect — say so and request it). Lane: harness.
  [OPEN] Item 5 — §5 one BACKLOG surface of named-and-not-done (source/atom-or-"unminted"/lane/status/
         age), published with observability, read by the daily note; first output = the current
         named-but-unminted enumeration. Lane: harness/observability.
  [OPEN] Item 6 — §6 COHERENCE BY DERIVATION (THE_MODEL_ON_A_PAGE = truth; node stage COMPUTED from
         atom levels; site renders from the derivation; publish fails on model/diagram/site/map
         disagreement). LARGEST — the ruling authorizes PHASING; propose the phase plan before building.
Each remaining item: failing test FIRST, own commit, shadow rail on any scanner/publish-gate change.
-->

# [DIRECTOR-RULING] — Work definition and coherence: rulings must create atoms; model, diagram, site and map must DERIVE from one truth (2026-07-27)

**Type:** [DIRECTOR-RULING] via advisor bridge. Six parts. Addresses today's HARDEN treadmill and its cause.

## §0 The diagnosis — and where the fault sits

Between 08:23 and 10:25 the tick performed twelve HARDEN re-verifications of **already-at-target** atoms while a director ruling sat unconsumed for 55 minutes, reporting *"no below-target work anywhere."* That claim is literally true of the maturity map and false of reality: merit-order reconstruction, the DD seasonal cash-flow FRAME, and the site evidence pages are all named in ratified rulings and steers, and **none was ever minted into an atom.** Rung-7 mints from `DIRECTOR_AXES` only, so prose in rulings is invisible to it.

**The advisor owns this.** Seventy-plus documents have been staged treating *staging* as though it were *scheduling*. A ruling that names the next piece of work is not a work item; the map is the queue. The silence-bias fixed this morning has simply become a busywork-bias: the machine still cannot see the real queue, it is merely louder about being idle. The director's read is correct — this is a definition failure, not a diligence failure.

## §1 HARDEN re-verification is demoted (not abolished)

Re-verifying at-target atoms has real value — it catches regressions from changes elsewhere (integration blast radius is canon). But it is **not** a substitute for work. Therefore: it sits **below the planner-mint rung**; it is **rate-limited to ~1 per hour**; it should preferentially be **triggered by dependency change** rather than by idleness; and it **never counts as work** for the deadman clock, utilisation, or the product/machinery split. R15: with a below-target atom or an unminted ruling present, a HARDEN re-verify draw must FAIL the test.

## §2 Rung-7 mints from RULINGS and STEERS, not only from AXES

Any ratified ruling or steer that names work is a **mint source**. On consumption, named work becomes atoms in the map with lane, target level, exit criteria and dependencies. **Do this now, retrospectively**, for at minimum: the **merit-order / gas-first price reconstruction** (the SSP hold's unblock condition and Board Spec 004's reconstructibility test), the **DD seasonal cash-flow FRAME** (steer of 2026-07-25), the **site evidence pages behind the diagram nodes**, and any other named-but-unminted work the sweep of §5 surfaces.

## §3 Staged director rulings draw within ONE tick

Rung 1 means rung 1. A staged `[DIRECTOR-RULING]` or `[STEER]` waiting behind HARDEN passes is a rung-order violation. R15 reproducing today's state: with a HARDEN candidate and an unconsumed staged ruling both available, the ruling must draw first.

## §4 Every ruling and steer ends with a "WORK THIS CREATES" block

**Binding on the advisor as well as the machine.** Each ruling/steer closes with named deliverables, acceptance criteria and target lane. The machine mints atoms from that block within one tick. **A ruling arriving without one is a defect in the ruling — say so and request it; do not silently absorb it.** This keeps definition where it belongs (with the author) and map mechanics with the machine.

## §5 One visible BACKLOG surface

A single surface listing everything **named and not done**: source (which ruling/steer/finding), atom (or "unminted"), lane, status, age. Published with the other observability artifacts, and read by the daily note. *"No below-target work"* must be checkable against this, never merely asserted. Its first job is to enumerate the current named-but-unminted set.

## §6 COHERENCE BY DERIVATION — model, diagram, site, map (the director's requirement)

**They must not be kept in sync by hand; three of them must be derived from one.**

- **`THE_MODEL_ON_A_PAGE.md` is the single source of truth** for what the company is and what exists.
- **Every diagram node maps to named atoms.** A node's stage — **Live / Building / Planned** — is **computed from those atoms' levels**, never hand-set.
- **The site renders from the same derivation.** A node cannot read "Live" on the diagram while its atoms sit below target or the site claims it works. The existing reading rule (Timeframe-2 content in present tense is a claim-status defect) becomes **mechanical rather than editorial**.
- **Bidirectional:** a node with no atoms is a gap — either unmodelled work or an unbuilt concept, and it appears in the §5 backlog. An atom with no node is work that serves no part of the model, and must be questioned. **Adding a limb to the model therefore generates its own work definition** (e.g. the acquisition organ, when the growth session rules it in).
- **Gate check:** publish fails when model, diagram, site and map disagree. Disagreement is a defect, not a discrepancy to reconcile by editing whichever is most convenient.

## WORK THIS CREATES (per §4, applied to this ruling)

1. HARDEN demotion + rate limit + exclusion from work accounting — with the §1 R15.
2. Rung-7 mint-source extension to rulings/steers — plus the retrospective mints named in §2.
3. Rung-1 ordering test per §3.
4. "WORK THIS CREATES" parser + the missing-block defect report per §4.
5. Backlog surface per §5, first output = the named-but-unminted enumeration.
6. Coherence derivation per §6: node→atom mapping, computed stages, site rendering from the derivation, and the publish-gate disagreement check.

Acceptance: today's exact state (twelve HARDEN re-verifies, one unconsumed ruling, three named-but-unminted work items) is reproduced as a failing test before each fix.

**Risk & proportionality:** touches draw ordering, the planner's mint sources, the publish gate and the site's rendering path — failing tests first, own commits, shadow rails on scanner changes. §6 is the largest and may be proposed in stages; propose before building if it needs to be phased. Tag: **proceed; §2 retrospective mints first — they unblock product today.**

— Advisor bridge, carrying the director's ruling — and recording the advisor's own share of the definition failure. 2026-07-27.

---

## AMENDMENT (same day) — §1 and §5 restated as PROBLEMS, not prescriptions

The director's challenge, verbatim: *"Should we have given it the problem to solve rather than tell it what to do?"* Yes. Two clauses above were written prescriptively while reacting to a stall, and the advisor's own pre-stage checklist names urgency as the violation trigger. They are restated. Where an amendment conflicts with the original text, **the amendment governs.**

**§1 RESTATED — the problem, not the interval.** The advisor's *"rate-limited to ~1 per hour"* is an invented number with no evidence behind it; **disregard it.** The requirement is: **HARDEN re-verification of at-target atoms must never outrank real work, and must never be able to fill an idle period in place of it** — while remaining available, because today it found four genuine defects (a NaN/Inf fail-open in the structural bill controls, Bacs rails counting calendar rather than working days, an LPCDA s.5A fidelity defect, and a latent fail-silent in weather normalisation). That is valuable work in the wrong queue position, not busywork.

Non-negotiables: it sits below the planner-mint rung; it never counts as work for the deadman clock, utilisation, or the product/machinery split; and with any below-target atom or unminted ruling present, a HARDEN draw must fail the §1 test. **The selection mechanism is yours** — dependency-change triggering, defect-yield-weighted scheduling, budgeted share of ticks, or something better. State your reasoning and the evidence for whatever you choose.

**§5 RESTATED — the requirement, not the artifact.** Ignore the prescribed surface shape. The requirement: **everything named-and-not-done must be *enumerable and checkable*, so that "no below-target work anywhere" can be verified against reality rather than asserted.** Whether that is a published surface, a live query, an assertion in the daily note, or a gate check is yours to design — with one wall: per LAW C it must derive from **primary state**, never from the tick's own enumeration.

**§4 also binds this document.** Its "WORK THIS CREATES" block stands, with items 1 and 5 now reading as the restated problems above.

**Standing correction to the advisor's practice (record it):** decisions transmit as decisions; implementations arrive as problems. The test before writing any mechanism into a ruling — *would someone who knows this system better reach a different and better answer?* If yes: state the problem, state the non-negotiables, and stop.

— Amendment by advisor bridge, on the director's ruling, 2026-07-27.
