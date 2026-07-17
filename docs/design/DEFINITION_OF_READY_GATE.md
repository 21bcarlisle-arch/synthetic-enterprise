# Definition-of-Ready Gate (G10_definition_of_ready_gate)

**Atom:** `G10_definition_of_ready_gate` (maturity_map.yaml, epoch 2, L0->1,
lane H_harness, size S). AUTHORED in `docs/design/METHOD_LENS_AUDIT.md` §3.4 as
the Agile/INVEST-lens proposal (row 5). This is the FRAME pass that gives it a
name and a design.

**Status:** FRAME pass, doc-only. This atom is BUILD-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rule 1), so this doc NAMES and SPECIFIES
the gate; it does not wire it. The mechanised soft-check is an explicitly-named
later BUILD slice (§7).

**Method:** per G6's own audit method — *name what we already have* before
proposing anything new. This project already runs an unnamed Definition of
Ready and an unnamed Definition of Done. The whole point of this atom is to
give them their established Agile names so the gaps become visible, not to
bolt on a new approval layer.

---

## 0. The one-paragraph diagnosis

Agile has two named gates that bracket a work item: a **Definition of Ready
(DoR)** — the checklist a story must satisfy *before* the team pulls it into a
sprint (is it scoped, sized, testable, independent?) — and a **Definition of
Done (DoD)** — the checklist it must satisfy *before* it is called complete.
This repo already enforces both, ad hoc and unnamed: our L0-L5 level gates ARE
a per-level DoD chain, and the `loop_stage` transition from `idle` into a
BUILD-workable state is ALREADY a de facto readiness decision. We keep
re-deriving the ambiguity cost by injury — an atom vague until someone hits it
mid-BUILD — because the readiness check lives in nobody's head as a named,
checkable thing. This doc names it, specifies a concrete DoR checklist, and —
non-negotiably — pins it as a SOFT DIAL that can never zero the feasible set.

---

## 1. The Agile DoR/DoD pattern, and where we already encode it (unnamed)

### 1.1 The pattern, briefly

- **INVEST** (Independent, Negotiable, Valuable, Estimable, Small, Testable) —
  the six properties of a well-formed backlog item.
- **Definition of Ready** — the team's agreed entry gate: a story is *ready to
  be pulled into build* only when it is understood, scoped, small enough,
  and has an acceptance test. Its purpose is to stop half-specified work
  entering the build lane and stalling there. It is a **flow discipline**, not
  a governance approval.
- **Definition of Done** — the team's agreed exit gate: what "complete" means,
  applied identically to every item, so "done" is not self-certified per item.

### 1.2 What we already have — named against the pattern (G6 method)

| Agile concept | This repo's existing, unnamed mechanism | Where it lives |
|---|---|---|
| **Definition of Done, per level** | The L0-L5 "to enter, a capability must have..." column IS a DoD chain — each level states exactly what closes it (L1: "been BUILT in any form"; L2: "passed DISCOVER-lite + VERIFY"; L3: "passed the full loop incl. HARDEN; Expert Hour: *this is real*"). A level is not banked without its stated evidence. | `MATURITY_MAP.md` §3; the Hardening Loop §2 |
| **Definition of Ready (entry gate)** | The `loop_stage` transition off `idle` into a BUILD-workable stage is already the readiness decision — an atom is not BUILD-drawn while `idle`. But *what makes it ready* is not itself checked; the transition is currently a human/twin judgement, not a checklist. | `maturity_map.yaml` `loop_stage`; `supervisor.py` draw; `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rules 7-9 |
| **INVEST: Estimable / Small** | G5's `size: S/M/L/XL` field + the XL->decompose soft gate. | `EFFORT_SIZING_DESIGN.md` §2-3 |
| **INVEST: Independent** | The `file_scope`-disjointness proxy used by the concurrent draw (`_maturity_map_draw_concurrent`). | `THREE_LANES.md`; `supervisor.py` |
| **INVEST: Testable** | The per-level exit test / Expert Hour bar; R15 mutation-testability requirement for any control. | `MATURITY_MAP.md` §1; R15 |
| **DoD applied uniformly, not self-certified** | The phase-close skill + Expert Hour + `epistemic-verifier`; the map's rule "the agent proposes; the director/advisor ratifies level-ups". | `.claude/skills/phase-close/`; `MATURITY_MAP.md` §7 rule 2 |

The conclusion of the naming exercise: **we have a strong, uniform DoD (the
level gates) and a WEAK, implicit DoR (the `idle`->workable transition checks
nothing).** The real gap G10 closes is the DoR, not the DoD. G6's audit row 5
said exactly this: "no explicit Definition of Ready check at FRAME time —
nothing currently verifies an atom has a stated, checkable exit test before
it's opened for BUILD."

---

## 2. The DoR checklist for BUILD-eligibility

An atom is **BUILD-ready** (a diagnostic flag, not a permission — see §4) when
all four hold. Each item reuses an existing mechanism; none is new machinery.

1. **Framed** — a design/FRAME artefact exists for the atom (a charter section,
   a design doc under `docs/design/`, or a lane frame) that states what the
   atom is and what its target level means *in this lane's terms*. Evidence:
   a real file path. (This is the FRAME stage of the Hardening Loop having
   actually run — not a promise that it will.)
2. **Scoped** — `file_scope` is declared on the atom AND is disjoint from every
   other atom currently in a BUILD `loop_stage` (the existing concurrent-draw
   disjointness test — reuse `_maturity_map_draw_concurrent`'s scope check,
   do not reimplement). This is INVEST's *Independent* made concrete.
3. **Sized** — G5's `size` field is set (S/M/L/XL) with a one-line
   `size_basis`, AND the G5 XL->decompose soft gate has been satisfied: an XL
   atom must either have been split into sized child atoms or carry an explicit
   one-line reason decomposition was rejected. **This item does not duplicate
   G5 — it CALLS it.** `tools/effort_calibration.py::xl_decompose_flags()`
   already computes this flag; the DoR check reads that flag, it does not
   recompute sizing.
4. **Exit-test-defined** — the atom's L-target DoD (§3) is stated as a concrete,
   checkable exit test *before* BUILD starts, and — per R15 — that test is
   mutation-testable (there exists a named defect the test would catch). A
   control that cannot fail is worse than none; a DoR that accepted an
   un-failable exit test would be theatre. For an atom whose exit test is an
   LLM judge (not mutation-testable), R15's OUTCOME-test substitute applies.

**Folds, does not add:** items 2/3/4 are each a *read* of an existing
mechanism (`file_scope` disjointness, G5's `xl_decompose_flags`, the level
DoD + R15). The DoR is the checklist that *composes* them at one FRAME-time
moment — it is the union of checks the project already believes in, named and
gathered, not a new gate with its own physics.

---

## 3. Definition of Done: naming the level gates

Our per-level "to enter, a capability must have..." statements (MATURITY_MAP.md
§3) ARE a Definition of Done — one DoD per level transition. Named:

- **DoD(L1)** = "been BUILT in any form."
- **DoD(L2)** = "passed DISCOVER-lite + VERIFY" (genuine artefacts, happy path).
- **DoD(L3)** = "passed the full Hardening Loop incl. HARDEN; Expert Hour
  verdict *this is real*; anchored, epistemically clean."
- **DoD(L4)** = "full loop + governance artefacts; Expert Hour *this is good*."
- **DoD(L5)** = "full loop at scale + typed adapter with a named real twin +
  tournament evidence."

Two properties this naming makes explicit and must preserve:

- The DoD is **per-transition**, not global — "done" for an atom always means
  "done *to its stated L-target*", never an absolute. This is already how the
  map works; naming it stops "done" drifting into an unqualified claim
  (consistent with R11's "done = the rendered value changed" and the
  "Done = named artifact" learning).
- The DoD is **ratified, not self-certified** — L1->L2 by the advisor, L3+ by
  the director; the agent proposes with evidence and never moves its own cell
  (MATURITY_MAP.md §7 rule 2). The DoR (§2) is the agent's own FRAME-time
  self-check; the DoD ratification is the external check. They are different
  organs and stay different — the DoR never becomes a way to self-grant a DoD.

---

## 4. THE GUARDRAIL — the DoR is a SOFT check / DIAL, never a hard gate (non-negotiable)

State it first because it governs everything above.

**The DoR ORDERS and FLAGS readiness. It never blocks all work. It can never
zero the feasible set.**

- **Rule 0 is the wall here.** "An empty feasible set is a DEFECT IN THE DIALS,
  not a reason to hold." A DoR implemented as a hard gate — "no atom builds
  until framed+scoped+sized+tested" — could, on a bad map state, make *every*
  atom fail the check and leave nothing drawable. That is precisely the
  Rule-0 violation the Prime Directive forbids. So the DoR is a **DIAL**: it
  informs draw *order* (a fully-ready atom outranks a half-ready one), and it
  raises a *flag* on an atom that BUILD-draws while not-ready — it never
  removes an atom from the drawable set. If the only drawable work is
  not-yet-ready, the correct behaviour is **draw it anyway and flag the
  readiness gap**, exactly as G5's XL gate flags-but-never-blocks.
- **Anti-goal-seek (R12).** "Ready" is a **diagnostic, never a target.** The
  moment "get the DoR score up" becomes an objective, atoms get cosmetically
  framed/sized to pass the check rather than genuinely understood — the same
  failure mode R12 names for margin and G5 names for `size`. Readiness is read,
  not gamed. A rising not-ready-but-drawn count is a *learning signal about the
  FRAME lane* (we are under-framing before BUILD), never a stick against the
  atom or the fork.
- **DIAL, not WALL, in the CLAUDE.md taxonomy.** Per Rule 0's two classes, the
  DoR is unambiguously a DIAL (it orders work). The only WALLs it *references*
  are pre-existing physics it does not weaken: R15 (a control must be able to
  fail) and the level DoD ratification. The DoR adds no new wall.
- **Fail-open by construction.** Consistent with R15's warning against
  fail-open controls in the *safety* direction, note the asymmetry: a DoR must
  fail-open on *availability* (missing size/scope/frame => flag, still
  drawable) precisely because it is a flow dial, while a *safety* control must
  fail-closed. These are different organs; the DoR is flow, not safety, so its
  safe failure direction is "let the work proceed and flag", the opposite of a
  safety gate. This is stated so a later BUILD slice does not accidentally
  implement it as a blocking check "for consistency" with safety controls.

---

## 5. How it folds — one mechanism, not three

G10 (DoR), G5 (XL->decompose gate), and the director-twin BUILD-open call
(`route_blocking_decision`) are three views of a SINGLE FRAME-time readiness
moment, not three separate gates to satisfy in series. The FRAME pass runs
once and produces one verdict:

```
FRAME an atom for BUILD-eligibility:
  1. DoR checklist (§2): framed? scoped? sized? exit-test-defined?
        |
        |-- sized? delegates to G5: xl_decompose_flags() -----------.
        |     (XL => decompose-or-justify; a flag, never a block)   |
        |                                                           |
  2. Compute a readiness FLAG (ready / not-ready + which items fail) |
        |   (never removes the atom from the drawable set — §4)      |
        |                                                            |
  3. Is a genuine one-way door or director-reserved item implicated? |
        |-- YES: route via director_twin.route_blocking_decision --. |
        |         (twin answers from canon in seconds, OR registers | |
        |          [ACTION NEEDED] for a real one-way door; Law B)  | |
        |-- NO: proceed on the flag; not-ready => draw + flag       | |
        v                                                           v v
     ONE verdict: draw-order weight + readiness flag + (if needed) twin routing
```

The folding rules:

- **G5 is a sub-check of the DoR, not a peer.** DoR item 3 ("sized") IS the G5
  size field + XL gate. G10 does not re-estimate effort or re-implement the XL
  soft gate — it *reads* `xl_decompose_flags()`. One sizing mechanism, one
  caller. This matches G5's own honest partial: the XL gate "is built and
  tested; nothing calls it as part of FRAME yet" (EFFORT_SIZING_DESIGN.md §6) —
  **the DoR IS that missing caller.**
- **The twin call is the escalation edge of the DoR, not a parallel gate.** The
  twin (`route_blocking_decision`) is already the standing approver for
  "BUILD-open within the open epoch" (canon v2 §3a). The DoR does not add a
  second approval; it feeds the twin. A not-ready flag that implicates a
  director-reserved axis (a one-way door, a values/curriculum decision) routes
  to the twin exactly as any blocking decision does today; a not-ready flag on
  a purely reversible atom does NOT route — it just proceeds-and-flags (Rule 0
  + PROCEED_BY_DEFAULT). The DoR must never turn a reversible readiness gap
  into a director-ask; that would reintroduce the very stall
  `route_blocking_decision` was built to remove.
- **Net:** one FRAME-time function computes {draw-order weight, readiness flag,
  whether-to-route-to-twin}. G5 supplies the sizing sub-answer; the twin
  supplies the escalation sub-answer; the DoR is the composition. Three names,
  one mechanism.

---

## 6. Where the DoR flag would surface (design intent, not built)

Consistent with G6's proposals and G7's WIP-dashboard direction, a mechanised
DoR would surface its flag as a diagnostic, not a blocker:

- A per-atom `readiness` flag on the Method door (alongside the WIP / cycle-time
  material G7 proposes), showing which of the four DoR items an atom satisfies.
- An `EFFORT SIZING`-style block (mirroring `background/effort_digest.py`) that
  reports "N atoms BUILD-drawn while not-ready, itemised by which DoR check
  failed" — a learning signal about the FRAME lane, read at each digest.
- Never a gate in the draw path. The `supervisor.py` draw stays as-is; the DoR
  is an annotation layer over it, exactly as G5's `xl_decompose_flags` is.

---

## 7. Honest "not built here" — the named later BUILD slice

This is a FRAME pass. **Nothing is wired.** What remains, explicitly named as a
later BUILD slice (BUILD-gated per epoch rules; this fork authored the design
only):

- **`dor_check()` — the mechanised soft-check.** A read-only function
  (proposed home: `tools/effort_calibration.py` beside `xl_decompose_flags`, or
  a sibling `tools/readiness.py`) that, given an atom, returns the four DoR
  booleans (framed / scoped / sized / exit-test-defined) + an overall
  ready/not-ready flag, by *reading* existing mechanisms (`file_scope`
  disjointness, `xl_decompose_flags`, the presence of a FRAME artefact, the
  presence of a stated L-target exit test). MUST return a flag, never raise or
  block. Mutation-tested per R15: a test proving the check fires on a
  deliberately-unframed / unscoped / unsized / testless fixture atom (a DoR
  that cannot fail is theatre).
- **The FRAME-workflow call site.** Wire `dor_check()` as the FRAME-time
  self-check whose flag folds into the §5 verdict — the missing caller that
  G5's XL gate and this DoR both need. This is the "one mechanism" of §5 made
  real.
- **The digest/door surface.** The `readiness` flag rendered per §6 (Method
  door + a digest block), with the same defensive try/except-log-and-swallow
  discipline as `effort_digest.py` so it can never break publishing.
- **NOT proposed, explicitly:** any change to the draw path, any hard gate, any
  new director approval layer, any edit to `maturity_map.yaml` schema beyond
  fields G5 already proposes (`size`/`size_basis`). The DoR needs no new atom
  fields — it reads what is (or, per G5, will be) already there.

Each item above is DISCOVER/FRAME-complete here and BUILD-opens only when the
epoch/twin opens it. This atom reaches **L1** on this doc (FRAME artefact
exists = "been BUILT in any form" for a design atom); L2 waits on `dor_check()`
built + mutation-tested + wired, ratified by the advisor.

---

## 8. Relationship to already-landed / adjacent work (not re-litigated)

- **G5_effort_sizing_discipline** — supplies DoR item 3 wholesale (size field +
  XL->decompose gate + `xl_decompose_flags()`). The DoR is the FRAME-time
  *caller* G5 says it lacks. No duplication.
- **G6_method_lens_audit** — authored this atom (§3.4, row 5) and supplied the
  naming method used in §1. This doc is the FRAME execution of that proposal.
- **EPOCH_GATING_AND_ATOM_AUTHORSHIP.md** — the `loop_stage: idle` -> workable
  transition is the readiness moment the DoR names; the DoR is the checklist
  for that transition, never a new BUILD gate on top of it.
- **director_twin.route_blocking_decision** — the escalation edge of the DoR
  (§5), unchanged. The DoR feeds it; it does not replace or duplicate it.
- **Rule 0 / PROCEED_BY_DEFAULT / R12 / R15** — the walls the guardrail (§4)
  rests on. The DoR adds no new wall; it is a DIAL that references existing
  physics.

## 9. The mirror gap — a Definition of HARDEN-ability (FRAME finding, 2026-07-17)

**Surfaced by live evidence, not theory.** During a director-gated idle (no
below-target work anywhere), the Rule-0 self-refill correctly yields a dial and
hands the worker at-target atoms to HARDEN/red-team — this is right (Rule 0: the
to-do list is never empty). But it draws them **uniformly**, with no check that
the drawn atom has a *harden-able surface*. Four consecutive HARDEN draws in one
idle window: two landed on harness/safety-control atoms with built controls and
found real fail-silent bugs (high value); one landed on a settled domain atom
(re-verified clean); one landed on **this atom itself** — `level 1`, FRAME-only,
`loop_stage: idle`, whose only built artefact is a design doc. There is no
control to mutation-test, no exit test to re-run, no invariant to red-team on a
FRAME-only atom — so "HARDEN it" degrades to make-work / theatre pressure, the
exact failure `SELF_INTERRUPT_DISCIPLINE` names ("the supply is infinite = the
treadmill") and `R15` forbids (a manufactured test on a non-existent control is
worse than none).

**The principle (the DoR's mirror).** Just as an atom is BUILD-eligible only
when framed/scoped/sized/exit-test-defined (§2), an at-target atom is
**HARDEN-DRAWABLE only when it has something to harden**: a built control /
exit-test / red-teamable invariant — concretely, `level_current >= 2` (a level-1
atom's only "evidence" is that it was framed) **or** an evidence entry pointing
at runnable tests. A FRAME-only / idle atom's honest idle-lane work is
DISCOVER/FRAME refinement (like this section), never "HARDEN".

**Disposition — same SOFT DIAL, same wall (§4).** This is an ordering/eligibility
DIAL on the HARDEN self-refill, never a hard gate: it *deprioritises* non-harden-
able atoms, and if the ONLY at-target candidates lack a harden-able surface it
still yields (offer FRAME refinement or the next dial), never zeroing the set
(Rule 0). Harden-ability, like readiness, is a **diagnostic never a target**
(R12) — the aim is not "maximise harden score" but "spend idle red-team effort
where a control can actually fail" (which is where both real bugs this window
were found). **NOT BUILT HERE** (BUILD-gated, same as `dor_check()` §7): the
mechanised skip/ordering lives in `background/supervisor.py`'s HARDEN self-refill
draw and folds into the SAME FRAME-time verdict as the DoR — one readiness organ
(ready-to-BUILD *and* ready-to-HARDEN), not two. Registered as this atom's own
next BUILD increment; no draw-path change this FRAME pass.
