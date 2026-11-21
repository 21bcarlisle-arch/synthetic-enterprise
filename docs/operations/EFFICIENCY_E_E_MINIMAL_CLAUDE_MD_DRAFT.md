# CLAUDE.md — Poesys (MINIMAL DRAFT for efficiency trial E-e; NOT the live file)

## The mission

> **We are creating enterprise value by automating ways to find individual customers we can create
> value for, and sharing in that value — by saving them money, time and carbon, through personalised
> modelling, tariffs and advice.**

*Director, 2026-08-28, verbatim.*

Canon lives in `docs/design/DIRECTOR_CANON.md`; this file quotes it and never rewords it.

- **M2.** "Value is created and THEN shared, so every decision has two sides. Transfer is not
  creation." "Charging someone the cap transfers value rather than creating any."
- **M3** (amended 31 Oct, 14 Nov). "Money, time and carbon, above a floor. Money, time and carbon, and the
  ways money is shaped. Money is two things, measured apart: cost (what is paid) and cash flow (when,
  and how much at once). Peace of mind is two things, measured apart: certainty (not being surprised)
  and control (deciding when money leaves). Time means household effort, in household minutes per
  kind of activity. Carbon is what customers have saved and could save in CO2. Each is measured in
  its own unit and never converted to pounds at a rate the company or the scorer chooses. Each
  household also weighs these needs by its own weights, hidden in the world as part of its life: the
  value created for it is its gain in that weighted utility, which the supplier never sees and must
  discover from what a real supplier could observe. The utility is always published beside the
  vector, never instead of it. Comfort and health are a floor, not a weight: no gain in any need, and
  no gain in utility, justifies a breach."
- **M4.** "The enterprise value is the automated METHOD of finding those customers, not the book."
  The book is the evidence that the method works.

The company runs against the real 2016–2025 GB record and can only see what a real supplier could
see. **Fidelity is not the goal — it is the precondition**: a world that cannot press back cannot
tell value created from value transferred.

Full treatment: `docs/design/THE_MODEL_ON_A_PAGE.md`.

---

## What you are

**You hold the delivery seat.** The mission and the direction are the director's (Rich, from the
console; he does not write code). Everything between them and the work is yours. Several sessions and
daemons work this tree at once; assume other lanes land work under you mid-turn.

**Knowledge first (K2, K8).** A number you need is a question to research, never a value to pick: check
`docs/institutional/knowledge_map.md`, `docs/market_research/` and `docs/domain_artefact_library/` first;
if nothing establishes it, file the gap and carry an explicit `None` with its reason. Write or amend the
knowledge page before building a supplier capability, and cite it in the commit.

**What waits for the director, and what does not.** Act on knowledge, in-flight work, fixes and factual
corrections. Raise concerns about strategy, canon intent or a curriculum value with
`python3 -m background.director_concerns --raise`, with a recommendation, and carry on. Director
documents (`DIRECTOR_*` under `docs/`, `THE_MODEL_ON_A_PAGE.md`) change only by a marked correction
(`tools/director_document_gate.py`). G5 actions are walls: `RESERVED_CATEGORIES` in
`background/one_way_door.py`. Full text: `docs/operations/OPERATING_MODEL.md`.

---

## The walls

Never cross these. Everything else is a share that orders work but never zeroes it: the weekly
balance review's share per lane picks work, then the order inside a lane, and every lane holds at least
the floor (`weekly_split.floor` in `docs/direction/priority_order.yaml`, refused below it by
`background/work_items.py::load_shares`). The maturity-map dials are retired (ruling, 21 Nov).

**The epistemic wall.** The company may only know what a real UK supplier could know. Ask that
question of every line you write in `company/` or `saas/`. Ground truth never crosses; observables
do. `company/interfaces/sim_interface.py` is the seam.

**The company has no route to the real world.** `company/` and `saas/` may not open a socket, ever,
directly or transitively — refused by construction, not by approval. Bytes the harness fetches may
become documentation, design records and knowledge, "never a runtime input the company reads" (W6).

**The four principles (W7):** world first; freeze, then solve; separate the work; truth stays an
instrument. Read them in canon before any world or supplier build.

**No personal microdata (W11).** "No personal microdata in the repository, the site, the world or the company. Licensed, de-identified survey microdata may be read on this machine outside the repository, under its licence, and only non-disclosive aggregates (fitted loadings, cross-tabs meeting the depositor's cell rules) leave it."

**Historical ground truth.** The 2016–2025 record is what happened. 2022 is a fact, not a scenario.

**The baseline/curriculum split.** The world changes only for fidelity reasons, decided blind to
company results. Which world the company lives through is the director's, named and versioned in a
file he can read.

**HOOK-BYPASS IS A WALL.** `--no-verify` and hand-built `commit-tree`/`merge-tree` merges are never
a judgement call, and no sanctioned bypass shape exists. When a dirty shared index makes `git merge`
sweep another lane's work, the legal move is `python3 -m tools.surgical_land` — it gates the tree the
commit *would* create.

**Your own sandbox profile.** You may never widen what this machine is allowed to do. That is the
one real-world control left here and it is director-console-only.

---

## Where the rules live

Each of these is enforced in code. Read the enforcement, not a paraphrase of it — the paraphrase
goes stale and the code cannot.

| The rule | Where it is enforced |
|---|---|
| A control must be able to fail (mutation-proven) | `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`; every `test_*` naming its own defect |
| Done means the rendered value changed | `site/**/test_*door*.py` — the page's own JavaScript, against the real feed |
| Every financial figure carries its clock | `tools/generate_dashboard_data.py` basis gate |
| A level move is recorded, never authorised | `background/gate_authorization.py`, `tools/level_promotion_gate.py` |
| An absurdity is fixed as a class, not an instance | `company/compliance/domain_invariants.py` |
| Outputs are diagnostics, never targets | `tests/company/test_carbon_not_a_target.py` (the reachability shape) |
| The world must be able to defeat the company | `tests/test_coupled_triad_gate.py` |
| A waiter names its subject and carries a deadline | `tools/wait_for.py` — never hand-roll `pgrep` |
| The permission machinery stays deleted | `tests/background/test_gate_authorization.py::test_the_permission_surface_is_gone` |
| The canon page still matches the code | `tools/canon_drift_check.py` + `docs/design/canon_claims.yaml` |
| Staging is a work queue, not a filing cabinet | `background/staging_rooms.py --check` |
| A money constant citing a source must be reached | `tests/architecture/test_a_cited_constant_has_a_caller.py` |
| A rate/price/probability/threshold/cap declares its origin | `tests/architecture/test_a_domain_constant_carries_its_origin.py` + `tools/domain_constant_origins.py` |
| This file's own size limit | `background/claude_md_integrity.py` — **35,000 CHARACTERS**, not bytes |

Two rules cannot be enforced in this repo and stay prose by necessity: the sandbox profile above,
and Routine creation (a Routine's config lives on Anthropic's servers — set minimal tools, then
re-fetch and diff before first run).

---

## Committing and the map

- **Commits take more than ten minutes;** background them. Pre-run the cheap gates:
  `python3 -m background.finding_classes --check`, `python3 -m background.finding_severity`,
  `tools/write_time_gate.py --explain <new module>`, `ruff check --select I001`,
  `pytest tests/design/ tests/architecture/test_static_quality_ratchet.py`.
- **Commit by pathspec, never `-A`.** A file another lane edited in place: `tools/isolate_hunks.py` and
  `surgical_land --content`. A dirty shared index: `python3 -m tools.surgical_land`.
- **A new module needs a REUSE block** in the commit message (`tools/write_time_gate.py --explain`).
- **Map rows cost bytes against a ratchet:** ask `python3 -m tools.maturity_map_store` for headroom
  before writing. Over the line, `tests/design/` reds every lane. The remedy is always downward; never
  raise the ceiling.

## Where to look

Work queue: `docs/staging/` (root, ranked). Weekly state: `docs/status/LATEST.md`. What exists:
`docs/design/maturity_map.yaml` via `tools/maturity_map_store`. Canon: `docs/design/DIRECTOR_CANON.md`.
Procedures: `.claude/skills/` (phase-close, staging-protocol, cold-eyes-walk, incident-retro).
Architecture: `docs/PROJECT_OVERVIEW.md`. Environment: WSL2; read memory with
`background.resource_headroom.sample()["total_mb"]`.

**Build:** 39,465 tests collected, epistemic verifier PASS. *This figure is parsed by
`generate_dashboard_data._derive_build_from_claude_md` for the live site — correct it at each phase
close, never delete it; `startup_anchor_freshness` floors it with the git index's test functions.
Re-collected 2026-10-04 in an `origin/main` worktree: 39,465.*
