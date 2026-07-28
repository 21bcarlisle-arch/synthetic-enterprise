<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_level_up -- size-and-clone ratchet; level move director-reserved (R16) -->
<!-- DESIGN half CLOSED 2026-07-28: docs/design/SIZE_AND_CLONE_RATCHET_DISCOVER.md (live census 789 files/169,852 lines corroborates ruling's 788; no existing clone tool — minimal AST detector designed; warn-then-gate + logged override + R15 both-ways designed; ceiling 223). BUILD half remains blocked_on director_build_open. -->
# [PLANNER-MINTED] — Size + clone ratchet (debt drains by side-effect, never by remediation sprint) (2026-07-28)

**Source:** `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §3 + Acceptance item 3
(committed `29361d1c2`).

**Provenance:** RUNG-7 planner mint — one of the six the §4-DEFECT ruling's body creates. The 91 registers
and ~220 remaining clones are explicitly **NOT** to be refactored as a campaign and **must not compete with
the epoch arc for a draw slot**; debt drains as a side-effect of ordinary touch. grep-confirmed net-new.

**Serves:** the incentive fix (ruling §0) — an agent building one register per phase against a checklist
that never asks "does this already exist?" produces 91 hand-rolled registers. A ratchet makes non-growth
the default without a sprint.

**Fidelity gained (one sentence):** none directly — a **build-discipline** mechanism that caps duplication
at today's level and lets it drain on touch, so the codebase stops silently accreting duplicate registers
through green phases.

---
## Required shape (decided by the ruling; implementation is mine to beat)
- No existing source file may exceed its current line count.
- New files / new functions capped (600 / 60 are candidate numbers **to beat**, not gospel).
- Any file touched by other work comes out **no larger** than it went in.
- The clone census gets a **ceiling at today's 223**, never a target of zero.

## Lane / level / deps
- **Lane:** `H_harness` / build gate. BUILD needs an open front / director BUILD_OPEN (block requested).
  The design half (choose line-count baseline capture, clone-census re-run integration, override mechanism)
  drawable NOW.
- **Target level:** `level_current 0 → 3`, `blocked_on: director_level_up` (R16).
- **Deps:** the clone census (§5.1 mint `clone_census_gap_register`) supplies the 223 ceiling number —
  soft dep; the ratchet can record 223 from the ruling directly and reconcile when the census lands.

## Exit criteria
- Ratchet live, **warns for ≥1 full cycle before it gates** (ruling §8 mitigation — a hard gate would wedge
  the publish gate mid-phase).
- Clone ceiling recorded at **223**; a **named, logged override path** (not silent) for legitimate growth.
- **R15 both ways (mandatory):** grow a file past its recorded count / add a 224th clone ⇒ ratchet
  WARNS-then-GATES; revert ⇒ passes. Prove the override is logged, not silent.

## Anti-Goodhart (ruling §7, BINDING)
- Clone count, register count, file size are **tripwires and reported facts, NEVER scores to minimise and
  NEVER inputs to any reward/fitness/selection mechanism.** A ratchet that reds is a hard constraint, never
  folded into a scalar. Degenerate metric-gaming (structural perturbation that lowers the count while
  raising real duplication) is a fidelity **bug report**, not progress.

## Probable failure mode (ruling §8)
- The familiar one: guards added, dependents not retested (the stale-test class that wedged the publish gate
  four times in one day). Run the full gate after; R15-prove failable both ways before relying on it.

## Walls untouched
- **No level self-bump (R16); no safety/auth/curriculum change.** Build-discipline only.

## Block requested from the ruling author
WORK-THIS-CREATES block + BUILD_OPEN requested via NTFY (bundled with the other five mints).
