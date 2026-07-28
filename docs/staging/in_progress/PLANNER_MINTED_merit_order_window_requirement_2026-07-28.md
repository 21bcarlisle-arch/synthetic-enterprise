<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- UNBLOCKS ON: nothing external — drawable now (doc-only DISCOVER/statement, R13 window elapsed today) -->

# [PLANNER-MINTED / DISCOVER] — Merit-order window requirement: state what the R13 window needs, return a curriculum proposal only if one is needed (2026-07-28)

**Provenance:** MINT from `DIRECTOR_RULING_UNBLOCK_BATCH_2026-07-28.md` WORK-THIS-CREATES item 1 (§2+§4 DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE — rulings are a mint source). The ruling §1: `merit_order` is "held behind an R13 propose-then-proceed window and is not drawing", is the ratified next product draw (`61e368f7e`), the SSP-baseline-hold unblock (`90110af48`), and Board Spec 004's reconstructibility answer — twice named most important. **"A blocked item of this rank must not sit silent again."** This deliverable is distinct from the reconstruction BUILD (`W1_6b_merit_order_reconstruction`, map atom, already minted) — it is the owed **statement** of what the window needs, plus a curriculum proposal only if one is required.

**Coverage note (no re-mint):** `W1_6b_merit_order_reconstruction` (maturity_map.yaml) already carries the BUILD; `PLANNER_MINTED_merit_order_reconstruction_discover_2026-07-25.md` already discharged DISCOVER+FRAME. Neither is the requirement-statement deliverable — that is this doc.

**Lane:** W1_market_weather / DISCOVER (doc-only, drawable now per THREE_LANES L3; no engine code).
**Target level:** n/a — a statement + register-publish deliverable, not a level move. (The reconstruction's own level move stays `blocked_on: director_level_up`, R16.)
**Deps:** none blocking. Reads `W1_6b_merit_order_reconstruction` blocked_on + the open-question register (`project_open_question_register_built`).

---

## THE REQUIREMENT, STATED (the ruling's "state plainly what that window needs")

**Which values:** NONE. This work sets no curriculum values. Per R13 the curriculum (difficulty, scenario mix) is director-reserved; this reconstruction touches the **BASELINE** price-formation FORM for fidelity-to-reality reasons, decided **blind to company P&L**. No `Scenario:` artefact, no difficulty knob, no marginal/strength tuning.

**Which scope:** `sim/` price-engine reconstruction to a merit-order / gas-first SRMC stack (fuel-over-efficiency + carbon per plant type, dispatched against residual demand; scarcity as a tight-hours term, not an every-hour multiplier). FRAME + DISCOVER already discharged (`docs/design/frame/W1_6_merit_order_reconstruction_FRAME.md`, `docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md`).

**Which decision the window offered:** a chance for the director/advisor to revise the target FORM or the acceptance bar before the baseline-touching BUILD proceeds with no interim tuning. **The window closes 2026-07-28 (today).** No revision was returned during the window → per propose-then-proceed the BUILD proceeds on the FRAMED form.

**Is a curriculum proposal needed? NO.** This is a baseline-fidelity change, not a curriculum change — it does not belong to the director-reserved curriculum class, so no curriculum ruling is required to proceed. (The director may still *choose* to revise the target form or acceptance bar — that is a director act, but it is **not required**; the window's default is proceed.)

**What the window needs to actually draw:** the window is a **scheduling artifact, not an epoch/front gate and not a dependency** (confirmed in `RESPONSE_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27.md` §Deliverable-4). The one residual risk is exactly the class the director warned of — a decision hiding inside a schedule: `W1_6b`'s `blocked_on` string still literally reads the elapsed-window text, which keeps the BUILD draw excluding it. **The requirement is therefore purely mechanical:** flip `W1_6b.blocked_on` from the elapsed-window clause to its real state — BUILD **drawable** (lane W1_market_weather = SIM_ACTORS front, OPEN), LEVEL move `blocked_on: director_level_up` (R16) — so the next tick draws the reconstruction. No director act needed to open; only the level move stays director-reserved.

## Drawable work this atom creates (the "advance it" half of the ruling's acceptance)

1. **Publish the statement above into the open-question register** (`project_open_question_register_built` surface) as the merit_order row's answer — the ruling's acceptance channel ("blocked with its requirement stated in the open-question register", or advanced). Per R11 verify it renders on the daily note / register surface.
2. **Flip `W1_6b_merit_order_reconstruction.blocked_on`** in `maturity_map.yaml` from the elapsed-window text to `director_level_up` (BUILD drawable; level move director-reserved). YAML-validate; orchestrator is the map writer (THREE_LANES). This is the concrete un-silencing — a date is not a reason, and the window has elapsed.
3. **NTFY transition** on the state change (was: R13-window-held → now: BUILD-drawable, no curriculum needed) — a rank-1 item leaving blocked is a transition worth one line (R5).

## Walls untouched
- **Curriculum values** — R13, director-reserved; explicitly NOT set here (the whole point of the statement is that none are needed).
- **One-way doors** — none; doc-only + a git-reversible blocked_on flip behind the epistemic wall.
- **Level move** — stays `blocked_on: director_level_up` (R16, no self-bump). This atom does not build the reconstruction; it un-silences it and states the requirement.
- **R12/R13 on the BUILD itself** — no interim tuning, unmoved naive baseline (governed by `W1_6b`'s own exit criteria).

— Planner mint, from DIRECTOR_RULING_UNBLOCK_BATCH_2026-07-28 item 1, 2026-07-28.
