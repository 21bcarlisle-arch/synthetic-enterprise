**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

**Knowledge:** none -- a governance ruling on how work is picked; it states no domain understanding a Knowledge page would carry

# [DIRECTOR-RULING] Retire the maturity-map dials, with a minimum share per lane

**Type:** RULING, through the advisor channel. It answers `for_the_director` row `the-one-work-system-s-decision-map`. The director's words, from chat, Sat 21 Nov 07:15 GMT, to the advisor's recommendation:

- "Yes."

## The ruling

- **Retire the maturity-map dials** as D7 of the one work system's decision map proposed. One rule picks work: the weekly review's share per lane, then the order inside a lane.
- **The advisor's condition, which he accepted:** keep the principle the dials carried, "a dial that orders work but never zeroes it". Give **every lane a minimum share** in the weekly split, so no lane is switched off by a share of zero. Choose the floor and state it in the next weekly review. Make the share table refuse a zero.
- Update the CLAUDE.md wording that quotes the dials, so it describes the share table and its floor. It is his words being re-homed, not changed, so mark it `Director-doc: his-words` citing this ruling.
- Close the row with this resolution.

## Done

Actioned by the delivery seat, 21 Nov 2026.

- **The share table refuses a zero.** `background/work_items.py::load_shares` now refuses a table
  with no stated floor, a floor at or below zero, and any row below the floor. Two tests name the
  defects (a lane switched off by a zero share; a floor stated but not enforced, or absent), and a
  mutation that drops the floor check turns both red.
- **The floor.** `weekly_split.floor: 5` in `docs/direction/priority_order.yaml`: one pick in twenty,
  half the smallest row (knowledge, 10) the 16 Nov review set. It is the seat's choice until the
  next weekly review (Mon 23 Nov) states it, as the ruling asks.
- **CLAUDE.md re-homed.** The line "Everything else is a dial that orders work but never zeroes it"
  now names the share per lane, the order inside a lane and the floor, and says the dials are
  retired. Marked `Director-doc: his-words` citing this ruling. The efficiency-trial draft of
  CLAUDE.md (`docs/operations/EFFICIENCY_E_E_MINIMAL_CLAUDE_MD_DRAFT.md`) carries the same line.
- **Row closed.** `the-one-work-system-s-decision-map` is answered `yes` in
  `docs/direction/DIRECTION.yaml`, with a commitment: `retire-the-maturity-map-dials-from-the-draw-at-cutover`,
  due 4 Dec. The supervisor's self-refill still weights atoms by dial today, because the one work
  system is still in shadow (`docs/work/cutover.yaml`). Retiring the dial weighting from the draw is
  the cutover's work, handed on as that work id.

Decision: harness yes
