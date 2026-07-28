<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_build_open -- stop-control gap; BUILD needs a director BUILD_OPEN (console-only, one-way door #5), never self-authored -->
# [PLANNER-MINTED] — Stop-control gap characterisation (SPEC_005 §7.13 material-safety) — DISCOVER half (2026-07-28)

> **CLOSED 2026-07-28 (DISCOVER done): inventory published at `docs/design/STOP_CONTROL_GAP.md`.**
> Coverage verdict **PARTIAL** (evidence-backed): backend "stop starting more work" is substantial and tested
> (`executor_governor.kill_switch_enabled`, `sim_runner._check_hold`, both with tested release transitions); the
> TRUE RESIDUAL is a director-window-reachable, authenticated, single stop affordance able to halt an *in-flight*
> turn/simulation — which exists nowhere. [ACT] standing: the BUILD is **category-5 safety-control** work
> (`blocked_on: director_build_open`, console-only, one-way door #5) — never self-authorised. Marker flipped
> self-drawable→blocked.
>
> **STATUS 2026-07-28 (RUNG-7 planner mint): DISCOVER half self-drawable NOW; BUILD half director-reserved.**
> Produce `docs/design/STOP_CONTROL_GAP.md`: an inventory of the EXISTING run-hold / kill / governor
> controls (`background/executor_governor.py`, `background/executor_daemon.py`, `background/sim_runner.py`,
> the documented run/hold flags in the IaC process set) mapped against SPEC_005 disqualification-battery
> item **§7.13** ("no stop control at all — material safety gap"), stating precisely what is covered, what
> the true residual gap is, and what a minimal compliant stop control would require. **No new safety
> control is built in this atom** — that is a category-5 one-way door (safety-control change,
> director-console-only).

**Source:** `docs/design/FIRST_RANKED_GAP_LIST.md` §2 machinery row **M2** (SPEC_005 §7.13, ABSENT,
**material safety**, board-battery weight 3, top of the machinery lane) — disposition *"safety-adjacent;
ranked top of machinery. Existing governance scope — verify against the current run-hold/kill controls
before minting (may already be partly covered)."* This mint performs exactly that verify-then-characterise
step.

**Provenance:** RUNG-7 planner mint. grep-confirmed no existing `PLANNER_MINTED_*`/atom named `stop_control`
or `kill_switch`. NON-duplicate by design: the ranked list flagged partial coverage, so this atom's whole job
is to establish the **true residual** against `executor_governor.py` et al., not to assume a bare gap.

**Serves:** SPEC_005 disqualification battery (a practitioner-named "not credible" item — credibility is not
tradeable, board-battery weight 3) and the governance/operational-coherence lens (OPS1: a control's RELEASE
must be defined and tested — a stop with no tested effect is an orphan transition, R11). Directly relevant to
the director-window axis (axis-1): an operator's window is incomplete without a stop affordance.

**Fidelity gained (one sentence):** no model change — an **operational-safety** legibility artefact that
converts a blanket "no stop control" red into a measured residual (what the existing governor already stops,
what it does not), so the director can decide the category-5 build from an honest baseline rather than a
guess.

## Exit criterion
`docs/design/STOP_CONTROL_GAP.md` exists with: (1) a control inventory (each existing hold/kill/governor
affordance, what it halts, how it is triggered, whether its release/effect is tested); (2) the SPEC_005
§7.13 requirement stated; (3) the **true residual gap** named with evidence (not asserted); (4) a minimal
compliant-stop-control sketch with its guarantees; (5) an explicit **[ACT] escalation to the director** that
the BUILD is category-5 safety-control work (`director_build_open` / console-only), never self-authorised.

## Propose-then-proceed window
DISCOVER PROCEEDS autonomously (doc-only, reversible). The **BUILD is BLOCKED** — `blocked_on:
director_build_open` (category-5 safety-control change, one-way door #5; the agent can NEVER add or alter a
safety control on its own authority, per CLAUDE.md). On completing the DISCOVER doc, flip this marker
`self-drawable → blocked` and leave the BUILD escalation standing as an [ACT].

## Walls untouched
Safety posture (category-5): **no control added or changed** — inventory + characterise only. R16 (no
front/level self-opened). R12 (the coverage assessment is a diagnostic, not a score).
