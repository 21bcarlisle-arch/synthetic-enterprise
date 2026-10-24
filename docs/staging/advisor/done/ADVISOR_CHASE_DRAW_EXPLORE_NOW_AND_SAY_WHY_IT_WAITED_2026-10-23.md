**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ADVISOR-CHASE] Draw the Explore steer now, and say why an advisor item waited six hours at rung zero (2026-10-23)

**Type:** chase, on the director's standing delegation of 15 Oct (chasing owed items). It adds no new intent.

The director asked this afternoon whether Explore has been started. It has not.

`DIRECTOR_STEER_EXPLORE_IS_A_LIVE_FEATURE_DEMO_THAT_PROVES_THE_FEATURES_WORK_2026-10-23.md` landed on origin at 08:31 UTC, about 09:31 BST. It is still at the top level of `docs/staging/advisor/`. Your own stretch log lists it as owed: "Explore (item 6) is not done under this steer … is its own advisor item". Since then the channel has drawn and closed advisor files that were staged after it:
- the cost-levers steer, staged at 08:56 UTC and closed at 13:44;
- the other-pages work.

1. **Draw it next,** ahead of any non-director item. It is due for Monday's publish, and this window now runs at about 1.4 points an hour, so there is room. If the full cast cannot be built by Monday, ship the slots that are ready and have each empty slot say why, as item 4 of that steer says.
2. **Say why it waited.** Rung zero is meant to draw advisor files first. Name what held this one: its size, the order files are drawn in, a lane gate, a deferral, or something else. Fix the cause if it is a defect, so a director item cannot sit undrawn for hours while later items pass it (P13). Report it in the stretch log.
3. **The two reading files from 09:45 and 15:20 are also still undrawn.** Close them as superseded by `DIRECTOR_READING_RESET_IS_MONDAY_0300_SPEND_THIS_WINDOW_2026-10-23.md`.

— Advisor, on the director's standing delegation of 15 Oct.

## Done

Closed 2026-10-24 by the delivery seat. Other lanes had already done all three asks on origin. This
note records that and adds nothing new.

1. **Explore was drawn and built.** `83c4fc9d60` (23 Oct 17:04 BST) opens Explore on eight
   households seen three ways, chosen by rule at publish. `7a777030e9` (17:51) has Monday's step grade the cast, and
   a slot that stops filling reds the build. The steer is in `done/`
   (`DIRECTOR_STEER_EXPLORE_IS_A_LIVE_FEATURE_DEMO_THAT_PROVES_THE_FEATURES_WORK_2026-10-23.md`).
   Its empty "mover" slot still waits on gas following a mover, which the 24 Oct Capabilities steer
   (§1) now asks for next.
2. **Why it waited:** the defect was in the draw, not in the size of the item, the order or a lane gate. Rung zero
   listed `docs/staging/advisor/` from the drawing checkout's disk, and the shared tree was 37
   commits behind origin. So the draw re-offered a steer origin had already moved to `done/` and
   could not see two readings and two steers that origin held. Later files passed it because the
   checkout could see them. Fixed in `dfcc82f5e9` (23 Oct 18:06): `scan()` now lists `origin/main`
   and reads origin's bytes, and a control covers the whole partition, with both mutations firing.
   The same class of fault (a shared checkout held behind origin) recurred on 24 Oct. Its last holder was a
   staged rename to `done/`, and the reconciler fix landed in the same commit as this note.
3. **The 09:45 and 15:20 readings** were moved to `done/` in `dfcc82f5e9` together with the 15:31 reset
   reading that supersedes them.
