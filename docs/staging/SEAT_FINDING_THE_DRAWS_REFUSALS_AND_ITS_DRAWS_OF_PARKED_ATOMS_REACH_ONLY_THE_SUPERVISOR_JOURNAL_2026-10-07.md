**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The draw's refusals, and its draws of parked atoms, reach only the supervisor journal

*Console seat, 2026-10-07, from the triage of the delivery seat's carried "what it got wrong" items
(`docs/direction/wrong_triage.yaml`). Three carried items share one cause, so they share this home.*

## The cause

The supervisor decides what is drawable, and when it refuses or keeps drawing something the seat
did not expect, it says so in its own journal. The seat steers from its brief, and the brief does
not read that journal. `atoms_stalled_with_reason` in `background/delivery_seat.py` now prints a
stop reason for stalled atoms that were drawn or are in focus. That is one leg. Refusals of Lane 0
items, and exclusions of atoms that are in neither set, still reach nobody.

## The three defects

1. **The held-work check refuses a Lane 0 item when its prose names a held file**, even when the
   held work is not the item's work. The refusal goes to the supervisor log only, so a focus item
   is never drawn and the seat is not told. On 2026-10-04 two of four focus items were lost this
   way. Carried as `the-held-work-check-refuses-by-prose-and-tells-only-the-log`, 27 listings.

2. **The coupled-triad gate excludes an atom from every BUILD draw, and says so only in the
   journal.** PB4 cost 2,275 wasted draws this way. W2_34, then nine more twinless L3 targets
   (fixed by `873d09651` and `6314e5bc8`), then W2_20 on 2026-10-07 (`8af70203f`), which reached
   the seat only because a worker wrote it into a finding. Carried as
   `a-coupled-triad-refusal-reaches-only-the-supervisor-log`, 10 listings.

3. **A parked atom is still drawn.** `_record_atom_draw_and_check_stall` increments
   `consecutive_unchanged` once per real draw. H45 (parked 2026-10-04) went from 950 to 1,266, and
   PB4 from 2,417 to 2,837, while PB4's work went through Lane 0 slices. Whether each draw spawns a
   tick is not established. Carried as `a-parked-atom-is-still-drawn`, 11 listings.

## What done means

- Every draw refusal of a focus item, Lane 0 or atom, with its reason, is in the brief the next
  orientation reads.
- A parked atom is not drawn, or the brief says why it was. The first step is to measure what one
  of these draws costs: one tick, or one counter bump.

Each leg needs a control that can fail: a focus item refused by the held-work check that must
appear in the brief, and a parked atom in a fixture map that the draw must not select.
