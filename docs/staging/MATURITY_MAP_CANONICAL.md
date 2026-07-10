# MATURITY_MAP_CANONICAL — ratified map + implementation (P1)

**Staged:** 2026-07-10 by advisor. **RATIFIED by the director** ("Ratify",
in-conversation, after two review rounds — v1.0 then v1.1 with his amendments:
the Expert Hour bar, the hardening loop for depth, lane charters, the
simplifications register, capability-as-atom data model).
**Place in the arc:** this IS the arc's territory. All future phases name the
capability cell(s) they move. The full map document follows this instruction
in the same staging commit (docs/staging/MATURITY_MAP_v1.1.md) — treat it as
canonical content, to be installed, not reviewed.

## What to build (in order)

### 1. Install the canon
- `docs/design/MATURITY_MAP.md` ← the v1.1 document (verbatim from staging).
- `docs/design/maturity_map.yaml` ← seed the capability atoms per the schema in
  the map's section 6. Seed scope: decompose each of the 12 lanes into its
  known capabilities from existing sources (DESTINATION_VISION backlog items,
  EPOCH2_EVIDENCE findings, CORE_FIDELITY phases, compliance programme,
  WALLED_INTERFACES sketch, this week's director decisions). Every capability
  gets: lane, value_stream, epoch, level_current (honest, evidence-cited),
  level_target, loop_stage, dial_inherited, real_world_twin, depends_on.
  Expect ~60-120 atoms. Where level_current is uncertain, mark it and say why
  rather than guessing.

### 2. Wire the supervisor to the map
Self-refill now draws from the YAML: pick work from lanes proportional to
dials, respecting loop_stage pipelining (DISCOVER/FRAME/HARDEN tasks are
background-lane eligible; BUILD is foreground). The dials in the map's
section 8 are the director's ratified initial settings. Dial changes come only
from the director (any authenticated channel); the agent may PROPOSE dial
changes with rationale.

### 3. Render it — the map the director can see
Project tab: the four views as toggles over the YAML (function matrix,
value-stream flow, campaign/epoch view, activity view showing what's in
DISCOVER/BUILD/HARDEN now and next). Simplifications register visible.
Follow existing site design laws; this replaces/absorbs the current epoch
storytelling section rather than duplicating it.

### 4. Adopt the operating rules (CLAUDE.md)
The map's section 9 verbatim: cells move only at phase close with evidence
having passed the loop; agent proposes, director ratifies L3+ level-ups
(advisor may ratify L1→L2); every staged phase names capability ids; silent
simplification = R10-class defect; Expert Hour at every L3/L4 claim.

### 5. First acts under the new regime
- Retro-tag the CURRENT in-flight work with capability ids (segments work,
  hedge-fix aftermath, comments-box backlog items).
- The two hot lanes (W1, D) enter DISCOVER/FRAME immediately: background-lane
  research on (a) reveal-over-time market/weather engine best practice +
  rederive-history implications, (b) NHH estimated-billing/rebilling and
  settlement-timetable mechanics. Output: distilled findings + charters for
  W1 and D (their dials are 3+, so charters are owed). These feed the epoch-2
  framing the advisor is drafting — do NOT start epoch-2 BUILD work yet.
- Your pending parallel-lanes proposal: redesign against the loop (concurrency
  from lane separation + stage pipelining), then file for director ranking.

## DoD
Map + YAML installed and pushed; supervisor drawing from dials (evidence: next
self-refill log cites lane+dial); Project tab renders all four views from the
YAML on the deployed site; rules in CLAUDE.md; W1+D charters drafted; in-flight
work tagged. One NTFY with the activity view's first snapshot.
