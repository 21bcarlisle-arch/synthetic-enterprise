<!-- SUPERVISOR_DRAW: self-drawable -->

# [PLANNER-MINTED] Self-authority release sweep — release everything within own authority NOW, report before/after (2026-07-29)

**Source rulings (BOTH — same deliverable, deduped):**
`DIRECTOR_RULING_LITERAL_ACTS_2026-07-29.md` (WORK-THIS-CREATES #2: "Everything releasable under
existing authority, released and reported") **and** `DIRECTOR_RULING_LITERAL_ACT_LIST_2026-07-29.md`
(WORK-THIS-CREATES #4: "Everything self-releasable already released before the list is sent"). Minted
ONCE here. The document half is the sibling atom
`PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29.md`.
**Serves:** the ruling's empowerment clause: "Anything releasable at your own authority — take it now,
do not list it. The list is only for what genuinely requires the director." Directly shrinks the
director's act-list before it is sent.
**Real-world fidelity gained:** none directly — operational hygiene. Value = the batch the director
receives contains ONLY genuinely-director-blocked items, so his acceptance test (count falls on his
action) is not polluted by items the agent could have cleared itself.

**Lane:** FRAME + self-release action (self-authority level/window/mint releases only; no production
behaviour change, no walls). Self-drawable now. **Runs BEFORE the sibling document is sent** (ruling
#4: released before the list).
**Target level:** operational action + a committed before/after report. No maturity-map level claimed.

## Scope of "own authority" (what may be released here — and what may NOT)
Per the ruling and standing rules, self-releasable classes:
- **Stale / elapsed propose-then-proceed windows** — any mint whose window has elapsed self-releases
  (this is what the planner already did at 02:16Z for 5 mints; sweep for any NEW ones since).
- **Consumed-ruling self-drawable mints** — mints whose source ruling is already consumed and which
  carry `SUPERVISOR_DRAW: self-drawable` are DRAWABLE, not blocked; confirm they are being drawn, not
  sitting (memory: "execute self-drawable mints, don't re-bookkeep").
- **Twin standing L1/L2 authorization** — `DIRECTOR_TWIN` is the standing approver for **routine**
  L1/L2 (project memory `twin_ratifies_routine_levels`) and for BUILD-within-the-open-epoch. Route any
  genuinely twin-authorizable release via `director_twin.py::route_blocking_decision` and REPORT it.
- **NOT self-releasable — leave for the director (these dominate the current blocked set):** map-atom
  `director_level_up` moves are **director-reserved (R16, no self-bump)** — the ~14 Channel-A items in
  the sibling atom are NOT self-releasable, they go on the director's list. One-way doors (Channel C,
  `generator_draw_wiring` activation) are never self-authorised. Director-ratification-of-a-set
  (Channel D) is his. Do NOT clear these — that is the R16/one-way-door wall, and clearing them to make
  the count fall would be the R12 goal-seek the ruling explicitly forbids.

## Exit criteria
- Every mint in `docs/staging/in_progress/` is classified: **self-releasable** (release it now) vs
  **genuinely director-blocked** (leave, hand to sibling atom's list). Classification committed.
- Everything in a self-releasable class is actually released this pass (not re-registered, not
  re-stamped — memory: rest-proof gate can't be fresh while `self_drawable != []`; DRAW and EXECUTE).
- A committed report states the blocked count BEFORE and AFTER the sweep, and names each item released
  and under which authority — so the director's subsequent action starts from an honest, minimal count.
- R12: no item cleared by re-scoping it into nothing; a released item must have a real elapsed window /
  twin authorization / consumed ruling, cited.

## Coverage mapping
- LITERAL_ACTS #2 = LITERAL_ACT_LIST #4 → **this atom.**
- The other three deliverables of each ruling → sibling atom
  `PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29.md`.

**Propose-then-proceed window:** proceed by default (both rulings tagged **priority; proceed** /
**priority zero**; releases only under authority already granted, R16 / one-way-door / R12 walls held).

## Deliverable (verbatim, both rulings)
> Everything releasable under existing authority, released and reported.
> Everything self-releasable already released before the list is sent.
