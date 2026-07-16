# ERROR BUDGET & TOIL TRACKING — quantifying the treadmill, soft-gating discretionary work

**Atom:** `G9_error_budget_toil_tracking` (maturity_map.yaml, epoch 2, lane
`H_harness`, L0→1, size M). **Provenance:** proposal, authored by
`G6_method_lens_audit` (the SRE row of `docs/design/METHOD_LENS_AUDIT.md` §1
row 4 + §3 proposal 3). **This pass:** FRAME, doc-only. BUILD-gated per
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1 — no `background/`/`tools/` code
is written here; the counters + digest wiring are a NAMED later BUILD slice
(§7).

**One-line thesis:** SRE spent two decades working out how to keep a system
reliable without freezing feature work forever, and how to know whether
automation is winning against repetitive manual work. This repo already has
the raw material — a self-caught-failure register (`G4`), retros, and live
anti-decay digest counters — but no *quantified* error budget and no *toil
percentage*. This doc specifies both as DIAGNOSTIC INSTRUMENTS (dials, never
targets), built ON `G4`, not duplicating it.

---

## 0. GUARDRAIL — READ FIRST (this frames everything below)

Three non-negotiable guardrails, stated up front because they gate every
metric and every gate in this doc:

1. **Budget % and toil % are DIALS / diagnostics (R12 anti-goal-seek,
   extended to process metrics per `METHOD_LENS_AUDIT.md` §0).** They are read,
   never targeted. The moment "toil must be under X%" or "we must not burn the
   error budget" becomes a thing to *hit* rather than a signal to
   *investigate*, it reintroduces exactly the deadline pressure R12 was written
   to stop — and here it does something worse (guardrail 3).

2. **The soft gate must NEVER zero the feasible set (RULE 0).** The error
   budget SOFT-gates *discretionary net-new feature work* by re-ordering the
   draw toward toil-paydown / reliability work — it never HOLDS. Rule 0 is
   explicit: an empty feasible set is a defect in the dials, not a reason to
   hold; dials yield in reverse priority until work exists. Toil-paydown work
   IS work (it is the highest-value work when the budget is burned), so the
   feasible set is never empty. If ever the gate would leave nothing drawable,
   the gate is the defect and yields — same mechanism as
   `supervisor.py`'s empty-draw → widen-scope.

3. **A "0 toil" target would incentivise HIDING self-caught failures — the
   exact opposite of what we want.** This is the load-bearing guardrail.
   SELF_INTERRUPT_DISCIPLINE (CLAUDE.md) says the treadmill is INFINITE by
   design: the supply of self-caught harness findings is unbounded, so we QUEUE
   them rather than fix-on-sight. A self-caught failure is *the system working*
   — a control fired, a retro was written, a false-positive was registered as
   an atom. If we scored ourselves on "drive self-caught-failure count to
   zero", the cheapest way to win is to STOP CATCHING failures — stop firing
   controls, stop writing retros, stop registering false-positives. That is
   catastrophic: it converts our best reliability signal into a suppression
   incentive. **Self-caught failures are a HEALTH signal, not a defect count.**
   The budget measures them to *allocate attention*, never to be minimised.
   (Compare SRE's own doctrine: an unused error budget means you are shipping
   too slowly / being too conservative — zero is not the goal there either.)

---

## 1. SRE definitions, adapted to a one-principal AI-executor shop

Adopt the PRINCIPLE, reject the CEREMONY (`METHOD_LENS_AUDIT.md` §2 SRE row:
reject on-call rotations, paging theatre, formal SLA review boards; adopt error
budget as a quantified diagnostic trigger + toil as a tracked percentage).

- **TOIL** (SRE: manual, repetitive, automatable, tactical, no-enduring-value
  work that scales with the system). **Adapted here:** recurring
  manual/repetitive SELF-CAUGHT work — *the treadmill*. Concretely: harness
  false-positives to triage, stale-process restarts, staging re-archival, map-
  truth reconciliation, publish-gate un-wedging. Toil is not "bad work"; it is
  work that a real supplier's ops team would call KTLO (keep-the-lights-on).
  The question SRE asks and we should: is automation eliminating toil faster
  than new toil arrives?

- **ERROR BUDGET** (SRE: `1 − SLO`; an *allowance* of failure. While budget
  remains, ship features; when burned, freeze features and spend on
  reliability). **Adapted here:** an allowance of self-caught failures /
  control-fires per rolling window. While budget remains, discretionary net-new
  feature atoms draw freely. When the budget is burned (self-caught failures
  arriving faster than they are paid down), the draw SOFT-shifts toward
  toil-paydown and reliability work — spend the budget fixing the treadmill,
  not adding to it. **Soft, never hard** (§0 guardrail 2).

- **DISCRETIONARY work** = net-new feature/capability atoms (a new SIM world, a
  new company capability, a new site surface). **Non-discretionary** =
  toil-paydown, reliability hardening, the WALLS (exit tests, epistemic
  honesty, safety controls — these NEVER yield to any budget). The gate only
  ever re-orders discretionary vs. toil-paydown; it never touches a wall.

---

## 2. TOIL TAXONOMY — grounded in this repo's actual recurring toil

Each row is a REAL recurring toil class, cited from CLAUDE.md / retros / recent
commits. This is the taxonomy the toil metric counts against. It is the SRE
counterpart to Lean's seven-wastes taxonomy that `METHOD_LENS_AUDIT.md` §1 row
1 named as missing.

| # | Toil class | Real evidence in this repo | Automatable? / current automation |
|---|---|---|---|
| T1 | **Publish-gate wedges** — a HELD/reject control fires on legitimate input and silently stalls the whole publish pipeline | Commit `1efbb30bc` "Fix publish-gate wedge + archive-on-consumption backstop + archive 6 stuck staging docs"; MEMORY `control_false_positive_jams_pipeline` (a valid credit bill tripping a HELD control). | Partly — archive-on-consumption backstop added; legitimate-edge-case tests are the durable fix. Recurring ⇒ toil. |
| T2 | **Stale-daemon-not-restarted (R2)** — a code fix is committed but the running process keeps executing pre-fix code | CLAUDE.md Current state: "the CANNOT-draw was R2 (`supervisor` tmux daemon running stale pre-fix code since 14:14)"; R2 itself; MEMORY `fail_silent_control_patterns`. | Partly — `start_worker.sh` / watchdog restart. Restart-after-fix is still manual triage ⇒ toil. |
| T3 | **Map-truth reconciliation** — folding per-atom `atom_status/` inboxes into the canonical map, resolving level-write races | `atom_status/README.md` (the map-contention fix); `tools/merge_atom_status.py`; commit `206c534c1` "fold pending inbox backlog (F1 reconcile)". | Partly — F1 `_default_fold` folds each cycle; reconciliation drift still surfaces ⇒ toil. |
| T4 | **Worktree-scan false positives** — tree-scanning controls trip on stale fork copies under `.claude/worktrees/` | MEMORY `worktree_scan_hazard` (64 stale fork copies false-positiving, jamming publish). | Partly — exclude-path convention; new scanners re-introduce it ⇒ recurring toil. |
| T5 | **Staging re-archival** — actioned `from_rich_*` / `run_complete_*` files left in the scanned root re-granting supervisor turns | CLAUDE.md multi-part-staged-instructions note (a built-but-unarchived `B2_OPEX_TAXONOMY_EXPANSION.md` re-granted a turn every ~2 min for hours); MEMORY `staging_archival_verify`, `archive_after_ntfy`. | Partly — `in_progress/`/`done/` conventions + staging-watcher. Verify-the-mv is still manual ⇒ toil. |
| T6 | **Remote-staging / archived-doc resurrection** — a doc already archived to `done/` gets resurrected by the bridge | Commit `686ad482b` "Remote-staging bridge: don't resurrect a doc already archived to done/". | Fixable structurally; each recurrence is toil until then. |
| T7 | **Harness false-positive triage** — a self-caught harness finding that turns out to be a false positive, QUEUED as an atom | SELF_INTERRUPT_DISCIPLINE (the treadmill = "harness findings/false-positives, QUEUE-by-default"); "the supply is infinite = the treadmill". | This is the archetypal toil class — inherently recurring; the metric exists to watch its *volume trend*, not to zero it. |

**How to quantify it (data sources — reuse, do not build new stores):**
- **Primary: `G4_unified_failure_register`** (the append-only cross-retro index
  with GLOBAL per-class strike-counting). G9 is a *reader* of G4: each toil
  class T1–T7 maps to one or more G4 theme-tags; the toil count for a class =
  the register's strike-count for that tag over the rolling window. **G9 does
  NOT re-implement the register** (`METHOD_LENS_AUDIT.md` §5: "G9's proposal is
  the error-budget half only, not a re-implementation of G4"). If G4's tags do
  not yet cover a T-class, the fix is to add the tag in G4, not to build a
  parallel store in G9.
- **Secondary: retros** (`docs/retrospectives/`) — each retro that produced an
  R-rule is a toil-class datapoint; the retro ritual already appends to G4.
- **Tertiary: the live digest counters** (§3) — turns-waiting, escalations-
  later-reversible, idle-turns-with-atoms are already computed each digest.

Toil % ≈ (turns/cycles spent on T1–T7 triage) ÷ (total turns/cycles) over the
window. It is a TREND to watch (is automation winning?), reported per digest,
never a target (§0).

---

## 3. THE ERROR-BUDGET VIEW

### 3a. What counts against the budget
Self-caught failures / control-fires over a rolling window (e.g. per digest /
per week), sourced from G4 + the digest counters:
- Each **control-fire** that caught a real defect (publish-gate HELD a bad
  artefact, epistemic verifier FAILed, a mutation test fired) — a *credit* to
  reliability, *counted* against budget-spend for attention allocation, NOT a
  demerit (§0 guardrail 3).
- Each **self-caught false-positive** registered as an atom (T7) — counted, so
  a rising false-positive rate signals a control needs tuning (the control is
  eating budget without catching real defects).
- Each **recurrence of a known toil class** (a second publish-gate wedge, a
  third stale-daemon incident) — weighted by G4's GLOBAL strike-count, so
  repeat-cause classes (which R3 says should trigger redesign) burn budget
  faster and surface sooner.

### 3b. Anti-decay metrics that ALREADY exist as proto-error-budget signals
CLAUDE.md's MAKE_IT_STICK block already defines "anti-decay metrics, alarmed
every digest". These ARE proto-error-budget signals — G9 names them as the
budget's live inputs rather than inventing new ones:
- **turns-waiting-on-a-human** (target ZERO except a genuine one-way door) —
  every non-door wait is a self-caught process failure ⇒ budget spend.
- **escalations-later-judged-reversible** (target ZERO) — an escalation that
  should have been proceed-and-logged is a self-caught judgment failure ⇒
  budget spend. (ONE_WAY_DOOR_DEFAULTS_TO_ACT.md burden-of-proof.)
- **idle-turns-with-atoms-available** (already zero) — a Rule-0 violation is the
  purest self-caught process failure ⇒ budget spend.
- **twin answer latency** — a slow verdict organ; degradation is a reliability
  signal.

These are computed today in the digest path (`supervisor.py` anti-decay block;
`background/naive_organ.py::render_digest_section` and
`background/effort_digest.py::render_digest_section` are the block-managed
digest-render precedent to follow). G9's error-budget block is a THIRD such
render section, reading the same counters.

### 3c. The SOFT gate
When the rolling self-caught-failure rate exceeds the budget allowance
(discretionary failures arriving faster than paid down):
- **Re-order the draw**, do NOT hold: toil-paydown / reliability atoms rank
  ABOVE net-new discretionary feature atoms in the next draw cycle. Mechanised
  as a dial-yield in the existing draw path (`supervisor.py` /
  `executor_governor.run_loop`), NOT a new hold state.
- **Surface it in the digest**: "error budget N% burned this window; draw
  soft-shifted toward toil-paydown (T-classes: …)". A transition INTO
  budget-burned is an R5 state transition ⇒ one NTFY line, with the diagnostic
  payload (which T-classes, what would pay them down).
- **Release is defined and tested (R11 no-orphan-transitions):** when the rate
  falls back under budget, the draw returns to normal discretionary ordering,
  and that release must have a tested effect (the next-cycle draw order
  actually changes back) — a release whose effect is nothing is a defect.

The gate NEVER makes the feasible set empty (§0 guardrail 2): toil-paydown is
always drawable, and if somehow it were not, the gate yields.

---

## 4. R15 — the controls feeding the budget must themselves be able to FAIL

The budget's inputs are control-fires and self-caught failures. Per R15
(controls-must-fail), **a self-caught-failure count is only meaningful if the
controls that catch failures can themselves fail** — otherwise the budget is
fail-silent theatre:
- Every control that feeds a count into the budget (publish-gate, epistemic
  verifier, staging scanners, the anti-decay counters) must be MUTATION-TESTABLE
  — a mutation test proves it fires on its own named defect (R15). A control
  that cannot fail contributes a *constant* to the budget, which is worse than
  no signal (illusion of measurement).
- The three R15 killer patterns apply directly to the budget itself:
  - **TAUTOLOGY** — the budget must not derive its "failures caught" count from
    the same source it is judging (independence). G4 is an independent register;
    do not compute the count from the very daemon whose health it measures.
  - **FAIL-OPEN** — a missing/zero/empty count must not read as "0 failures,
    budget healthy". A control that went silent (produced no events) is an
    UNAVAILABLE check = a FAILED check = budget spend, never a green.
  - **FAIL-SILENT** — if the counter itself is unavailable, the budget view
    must say so loudly (an unavailable budget is a burned budget for gating
    purposes), never render a reassuring number from stale data.
- This is why G9 STRENGTHENS G4 rather than sitting beside it: the register's
  own R15 mutation-testing (tracked under G4's own level path and
  `H18_harness_self_mutation_audit`, "point R15 inward at the verdict organs")
  is the *precondition* for the budget being real. G9 inherits that; it does
  not re-establish it.

---

## 5. Relationship to G4 and sibling atoms (no duplication)

- **`G4_unified_failure_register`** — the DATA SOURCE. G9 reads its per-class
  strike-counts; the toil taxonomy §2 maps onto its theme-tags. G9 adds the
  *error-budget view* and *toil %* ON TOP; it writes no register of its own.
  (`METHOD_LENS_AUDIT.md` §5.)
- **`H18_harness_self_mutation_audit`** — supplies the R15 §4 precondition
  (mutation-testing the verdict organs). G9 depends on that discipline being
  applied to its input controls; it does not own it.
- **`G7_wip_and_cycle_time_dashboard` / `G8_constraint_identification_ritual`**
  — sibling method-lens proposals; G8's "what is the current constraint" query
  is a natural consumer of the budget-burned signal (a burned budget often
  *names* the current constraint). No overlap in ownership.
- **`G5_effort_sizing_discipline` / `effort_digest.py`** — supplies the
  block-managed digest-render PATTERN the BUILD slice reuses (§7); `size:` is
  itself a dial per R12/G5, same doctrine.

---

## 6. Portability / scale lenses (brief, per CLAUDE.md standing constraints)
- **C-S2 idempotency / deterministic replay:** the budget is a *pure read* over
  the append-only G4 register + digest counters — replaying the same window
  reproduces the same budget figure. No new mutable state; counting an event
  twice must be harmless (dedupe on G4's event identity).
- **C-S1 event-arrival tolerance:** the budget must be correct if failure
  events arrive late / out of order (a retro written days after the incident
  still lands in the right window) — it reads the register, it does not assume
  batch completeness.
- **Obligations-register / product-first lenses:** N/A — this is an internal
  ops instrument, no counterparty or product hardcoding.

---

## 7. NOT BUILT HERE — the named later BUILD slice (honest gap)

This is a FRAME pass only. **Nothing in `background/` or `tools/` is written.**
The implementation is a NAMED later BUILD slice, to be opened per epoch gating,
and it FOLDS with existing work rather than standing alone:

1. **A toil/error-budget digest block** — a new
   `render_digest_section()` following the exact block-managed pattern of
   `background/effort_digest.py` and `background/naive_organ.py`
   (`EFFORT_SIZING_DESIGN.md` §§2-6): read-only, never mutates the map, never
   blocks anything, renders an honest "N failures this window, budget X%,
   0 T-classes active" line rather than breaking if data is absent.
2. **A budget computation that reads G4** — a thin reader over the unified
   failure register (§2 data source) + the existing anti-decay digest counters
   (§3b). No new store. Depends on `G4` reaching a level where its per-class
   strike-count is queryable.
3. **The soft-gate dial-yield in the draw path** — a re-ordering hook in
   `supervisor.py` / `executor_governor.run_loop` (NOT a new hold state),
   with the R11 release path tested (§3c).
4. **R15 mutation tests** for the counters feeding the budget (§4), inheriting
   `H18`'s inward-pointed discipline.

Because it folds with `G4` + the `effort_digest.py` block pattern, the BUILD
slice is small (size M) and adds discipline, not architecture (SIMPLICITY
GUARD). It stays `loop_stage: idle` for BUILD until opened; this doc takes the
atom to **L1 (FRAME/DISCOVER complete, design specified)** only.

---

## 8. DoD self-audit (this FRAME pass)
- [x] SRE TOIL / ERROR BUDGET / DISCRETIONARY definitions adapted to this shop — §1.
- [x] Concrete toil taxonomy grounded in REAL repo toil, with evidence + data source — §2.
- [x] Error-budget view: what counts, anti-decay proto-signals named, soft gate — §3.
- [x] Guardrails stated prominently: dial-not-target, never-zero-feasible-set, no-0-toil-target (with the hiding-failures argument) — §0.
- [x] R15 note: input controls must be mutation-testable else fail-silent theatre — §4.
- [x] Strengthens G4, no duplication — §5.
- [x] Honest not-built-here: FRAME only, background/tools counters + digest wiring a named later BUILD slice folding with G4 + effort_digest block pattern — §7.
- [x] Doc-only, written under `docs/design/` only; no code, no map edit, no commit.
