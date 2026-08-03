<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BLOCK_RELEASE: propose_then_proceed -- was 'director_level_up', an act abolished 2026-07-29 and swept 2026-08-03: propose, record, act. Original note: RNG substream primitive; BUILD lands at build-quality, level move director-reserved (R16) -->
<!-- DISCOVER half CLOSED 2026-07-28: docs/design/RNG_SUBSTREAM_PRIMITIVE_DISCOVER.md (16 derivations found vs ~8 est, 5 distinct formulas, concrete Formula-A namespace-collision risk; canonical namespaced primitive + R15 both-ways designed; W1_6 sequencing citation corrected). BUILD half remains blocked_on director_build_open. -->
# [PLANNER-MINTED] — Canonical RNG substream primitive (unify 8 copies of `_substream`) (2026-07-28)

**Source:** `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §2.2 + Acceptance item 2
(committed `29361d1c2`).

**Provenance:** RUNG-7 planner mint — one of the six the §4-DEFECT ruling's body creates. Census verified
today: `def _substream` appears in ≥8 independent `simulation/` modules (`sme_distress`,
`conversation_response`, `payment_behaviour_source`, `population_draw`, `willingness_classification`,
`premise_demand`, `adoption_geography`, `household_budget`, `self_rationing`, `dd_attribution`, …). Same
class as the level-matched draw bug: shared semantics, unshared implementation. grep-confirmed net-new.

**Serves:** determinism + deterministic replay (C-S2 RNG-substream discipline) — the foundation of
varied-population-per-run and, downstream, the epoch-4 evolutionary tournament. A tournament over lives
whose seeding is derived eight different ways is not a tournament.

**Fidelity gained (one sentence):** every stochastic subsystem draws from one canonical, named,
seeded-substream derivation, so replaying a history reproduces identical state and a new subsystem's draw
provably cannot shift another's outputs.

---
## Lane / level / deps
- **Lane:** `simulation/**` (disjoint from §2.1's date arithmetic — may run concurrently). §2 is
  **[ACT]-first**; BUILD needs an open front / director BUILD_OPEN (block requested). Design half
  (enumerate the 8 call sites, define the one canonical `_substream` signature/semantics) drawable NOW.
- **Target level:** `level_current 0 → 3`, `blocked_on: director_level_up` (R16).
- **Deps:** none upstream.

## Exit criteria
- One canonical substream primitive; all 8 callers migrated.
- Guard test **reds on a second definition** of substream derivation.
- **R15 both ways (mandatory):** inject a second `_substream` ⇒ guard REDS; remove ⇒ passes.
- **Baseline re-frozen and the break declared (ruling §8):** unifying the derivation WILL change draw
  sequences, so any frozen baseline or lift table computed under the old derivation is no longer
  comparable. Treat as a **deliberate** baseline break — re-freeze after migration and declare it.

## Sequencing wall (ruling §8, binding)
- **Do NOT run concurrently with any live campaign whose evidence depends on an UNMOVED lift table.**
  **W1_6 is the live example.** If §2.2 and such a campaign contend, **the campaign wins and §2.2 waits** —
  say so rather than doing both. Check the open-campaign register before the BUILD half is drawn.

## Walls untouched
- **R13 / curriculum / generator ground truth:** the derivation mechanism is unified; no world/generator
  VALUE changes — draw *sequences* move (declared break), distributions do not.
- **C-S2** honoured (named seeded substream per subsystem); **no level self-bump (R16); no safety change.**

## Block requested from the ruling author
WORK-THIS-CREATES block + BUILD_OPEN requested via NTFY (bundled with the other five mints).
