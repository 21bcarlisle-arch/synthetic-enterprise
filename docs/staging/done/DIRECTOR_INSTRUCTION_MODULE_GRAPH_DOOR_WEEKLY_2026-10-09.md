# [DIRECTOR] The site carries a module-graph door, regenerated weekly

Date: 2026-10-09. Director request, staged by the advisor. This is a decided
instruction for a new capability; how it is built is the seat's to choose, and
it slots into the existing plan wherever the seat judges — it does not jump
drawn work.

## The outcome asked for

The site gains a door that shows the codebase as a living structure: every
non-test module as a node, every internal import as an edge, regenerated from
HEAD on a **weekly** cadence so a visitor (and the director) can watch the
architecture grow and the boundary tighten over time without anyone drawing it
by hand.

## What the view must convey (content, not mechanism)

- **Layers are the organising idea.** Each top-level layer is a visible
  cluster, coloured per the brand constitution — colour is information, never
  decoration.
- **The boundary is the signature.** Crossings between the company side and the
  world are the one thing the view exists to make visible: sanctioned crossings
  through the interface distinguished from any that bypass it, with their
  counts stated. Red is reserved for a bypass; today that count is zero, and a
  zero on display is the point.
- **Size means size.** A module's visual weight reflects its lines of code, so
  the funnels (the run processor, the annual report) are visible as what they
  are.
- **A reader can interrogate it.** Selecting a module gives at least its name,
  size and edge count. Headline counts (modules, edges, crossings) appear in
  the house glyph grammar.
- **The page states its own limits honestly**, as every door does: static
  imports only; dynamic dispatch and data coupling are invisible; a module with
  no import edges is not thereby dead.
- A week-on-week delta line is welcome if cheap; the seat's call.

## The measurement definition (so numbers agree across surfaces)

Use the same census the advisor's findings use
(`ADVISOR_FINDINGS_IMPORT_GRAPH_CENSUS_2026-10-09.md`): non-test Python
modules under the top-level layers, static import edges resolved against the
repo's own module set, boundary crossings classified by whether they route
through the interface. If the seat improves the census definition, the
findings' definition yields to the improved one — but one definition serves
both surfaces, so the door and any advisor reading never disagree by
construction.

## Non-negotiables

- **R12 applies.** The door is a diagnostic. No gate, reward or draw decision
  moves on its numbers, and nothing is tuned to make the picture prettier.
- Generated figures only — every count computed from HEAD at generation time,
  never typed.
- An advisor-built prototype of this view exists and the director has approved
  its look (dark ground, layer gravity wells, red/blue boundary edges, glyph
  stats line); match the spirit under the site constitution, not the artefact.

## Risk

- **Touches:** the site and one recurring generation step. Read-only over the
  codebase; no simulation output, gap value or financial figure passes through
  it.
- **Blast radius:** a broken generation leaves a stale or absent door; nothing
  downstream consumes it. Weekly cadence bounds the compute cost.
- **Probable failure mode:** the graph's size makes the page heavy or illegible
  on a phone; mitigation is the seat's choice of rendering and defaults (the
  prototype hid unwired modules by default, which worked).
- **Consume-path note:** landings/publishing are currently blocked by the
  holder fork; this instruction is dated, self-contained and valid whenever
  read.
- **Proportionality:** reversible / narrow.
