<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Owned-quantity registry + gate (make a second source of truth structurally impossible) (2026-07-28)

**Source:** `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §4 + Acceptance item 4
(committed `29361d1c2`).

**Provenance:** RUNG-7 planner mint — one of the six the §4-DEFECT ruling's body creates. Addresses the
class a structural clone detector is **blind** to: **semantic** duplication — two implementations of the
same quantity written differently (three disagreeing net-margin figures ~4.2× apart on one surface;
`payment_channel` label vs `arrears_engine` DD-failure dispatch; M2's duplicated register). None trip a
clone detector. grep-confirmed net-new.

**Serves:** the property the ruling requires — *make it structurally impossible for a second module to
become a second source of truth for a domain quantity that already has one.* The requirement is the
PROPERTY, not the registry; a better mechanism achieving it is welcome.

**Fidelity gained (one sentence):** the recurring "N disagreeing figures for one published quantity" defect
class becomes structurally unreachable — each domain quantity has exactly one declared owning module and a
gate reds when a non-owner computes it.

---
## Candidate to beat (ruling §4)
A registry of domain quantities, each with **one declared owning module**, and a gate that reds when a
non-owner computes an owned quantity. First entries (mandatory coverage per Acceptance item 4): **net
margin, treasury, EV, bad debt, cost-to-serve, carbon.**

## Lane / level / deps
- **Lane:** `H_harness` / build gate. BUILD needs an open front / director BUILD_OPEN (block requested).
  The DISCOVER half (locate each of the 6 quantities' true owner, enumerate current non-owner computations)
  drawable NOW and is high-value on its own — it surfaces the existing second-sources before the gate lands.
- **Target level:** `level_current 0 → 3`, `blocked_on: director_level_up` (R16).
- **Deps:** none upstream; complements (does not duplicate) the structural clone ratchet (§3, distinct
  detection class).

## Exit criteria
- Registry (or better mechanism) covers **at least** net margin, treasury, EV, bad debt, cost-to-serve,
  carbon — each with exactly one declared owning module.
- Gate reds when a non-owner computes an owned quantity.
- **R15 both ways (mandatory):** plant a second computation of an owned quantity in a non-owner module ⇒
  gate REDS; remove ⇒ passes. FAIL-OPEN check: an unrecognised/uncovered quantity must not silently pass
  as "owned by nobody" — the gate's default on the covered set is closed.

## Anti-Goodhart (ruling §7): coverage count is a reported fact, never a score to maximise.

## Walls untouched
- **No level self-bump (R16); no safety/auth/curriculum change.** Enforcement mechanism only; it does not
  itself compute any domain quantity (independence — R15 tautology guard).

## Block requested from the ruling author
WORK-THIS-CREATES block + BUILD_OPEN requested via NTFY (bundled with the other five mints).
