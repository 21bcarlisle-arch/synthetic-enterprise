**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `publish_gate_and_wedge`

# A publish control whose shape changes does not re-run the fixtures that build a synthetic tree to drive it

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `a-changed-control-does-not-rerun-its-synthetic-fixtures` in `docs/direction/wrong_triage.yaml`. Listed 86 times across orientations, first on 2026-09-25.*

## What it is

The trim-on-read repair to `_publish_gate_wedge_active` (2026-09-24) changed the wedge reader's population screen, and a sibling test whose fixture sat inside the old screen broke; that held publishing shut. The same thing recurred through the landing door's second hook chain. The live symptom since: `citation_at_head`, `red_at_head` and `fork_state` in the publish gate's state read `not_established`.

## Why it is folded here

Every instance is the publish gate or its wedge reader, and the remedy is the class's: a change to the gate re-runs the gate's own fixtures. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
