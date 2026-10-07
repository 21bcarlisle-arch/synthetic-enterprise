**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `uncommitted_and_orphaned_work`

# Level or park moves stranded in a preserved ref are replayed as written

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `stranded-map-moves-are-replayed-as-written` in `docs/direction/wrong_triage.yaml`. Listed 46 times across orientations, first on 2026-10-01.*

## What it is

Four map moves stranded in a preserved ref were replayed on 2026-10-01; PB4 build->idle was already false when it landed (`a6bd4d77e`), because its release condition had been met. Nothing re-asks a stranded move's release condition. One instance; recorded in `SEAT_FINDING_THREE_OF_FOUR_STRANDED_MAP_MOVES_LANDED_AND_PB4S_PARK_HAD_RELEASED_ITSELF_BEFORE_IT_STRANDED_2026-10-01`.

## Why it is folded here

Stranded work coming back stale is the return leg of this class. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
