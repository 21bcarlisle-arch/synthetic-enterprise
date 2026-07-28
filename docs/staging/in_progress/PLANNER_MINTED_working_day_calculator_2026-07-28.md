<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_level_up -- working-day calculator primitive; BUILD lands at build-quality, level move director-reserved (R16) -->
<!-- DISCOVER half CLOSED 2026-07-28: docs/design/WORKING_DAY_CALCULATOR_DISCOVER.md (22 callers found vs ~17 est; gov.uk/alphagov calendar source recommended, 2016-18 marked TO-BE-SOURCED not fabricated; AST guard designed). BUILD half remains blocked_on director_build_open. -->
# [PLANNER-MINTED] — Canonical working-day calculator with a dated UK bank-holiday calendar (class fix) (2026-07-28)

**Source:** `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §2.1 + Acceptance item 1
(committed `29361d1c2`). Extends the class of the already-fixed instance defect in
`DIRECTOR_RULING_HARNESS_INVESTMENT_AND_ITS_EVIDENCE_2026-07-27` ("Bacs rails counting calendar rather
than working days") — R10 requires the **class** fix, not a second instance.

**Provenance:** RUNG-7 planner mint from a director ruling flagged §4-DEFECT (no WORK-THIS-CREATES block);
this atom is one of the six the ruling's body creates. Census verified against the live tree today: only
3 main-tree modules mention bank holidays (`simulation/bacs_rails.py`, `sim/profile_class_1.py`,
`sim/profile_class_3.py`); ~17 modules compute working-day arithmetic independently, none England-&-Wales
bank-holiday-aware. grep-confirmed no existing `PLANNER_MINTED_*` fixes this.

**Serves:** `REGULATORY_RULES_AS_FIDELITY_ORACLE` — a fidelity gap of the first kind: regulatory deadline
arithmetic (GSOP, SLC obligations, complaint clocks, Bacs) is specified in *working days*, so the SIM
currently cannot produce a deadline breach that a real supplier would be fined for. Closing it makes those
breaches reachable.

**Fidelity gained (one sentence):** deadline/settlement dates that fall on a UK bank holiday move correctly
across all ~17 callers, and a class of regulatory-breach outcomes that were structurally unreachable
becomes reachable — a genuine correctness gain, not tidiness.

---
## Lane / level / deps
- **Lane:** correctness class fix touching `company/**` compliance-deadline logic + `simulation/bacs_rails.py`
  cash timing. §5 of the ruling calls §2 **[ACT]-first**. BUILD requires an **open front** (fronts.yaml) or
  director BUILD_OPEN — see the block request below; the DISCOVER/design half (enumerate the ~17 callers,
  choose the calendar source, design the one canonical API) is drawable NOW.
- **Two-pass build shape (ruling §8 mitigation, mandatory):** (1) land the calculator + a dated
  England-&-Wales bank-holiday calendar + its second-definition guard with **call sites UNCHANGED**,
  verified in isolation; (2) migrate the ~17 callers in a **separately-verified** pass. Four-nations split
  is a materiality judgement to make and record.
- **Target level:** `level_current 0 → 3` on the migrated result, `blocked_on: director_level_up` (R16 —
  the agent cannot self-promote).
- **Deps:** none upstream; independent of §2.2 (disjoint file_scope — may run concurrently).

## Exit criteria
- One canonical working-day module with a **real, dated** UK bank-holiday calendar (never fabricated dates;
  England & Wales at minimum).
- All ~17 existing callers migrated; a guard test **reds if any other module defines its own** working-day
  arithmetic.
- **R15 both ways (mandatory):** inject a second working-day definition ⇒ guard REDS; remove it ⇒ passes.
- **Moved-figure diff published (ruling §8):** any published financial/compliance figure that moves is
  published as an explicit before/after **with its `//` basis clock**, not left to appear as silent drift.
  Baseline diffs here are EXPECTED and must not be read as regressions.

## Walls untouched
- **R10:** closes the whole class (guard on second definitions), not the Bacs instance again.
- **R13 / curriculum / generator ground truth:** untouched — this corrects the company/SIM's own date
  arithmetic to reality; it does not tune any world parameter toward an outcome.
- **R14:** every moved figure carries its basis clock.
- **No level self-bump (R16); no safety/auth change.**

## Block requested from the ruling author
This ruling arrived without a WORK-THIS-CREATES block (§4 defect). BUILD of a `company/**`-wide correctness
migration needs an **open front / director BUILD_OPEN**. Requested via NTFY alongside the other five mints.
