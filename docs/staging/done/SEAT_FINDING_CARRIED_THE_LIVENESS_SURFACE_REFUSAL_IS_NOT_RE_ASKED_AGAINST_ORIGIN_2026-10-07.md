**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `publish_gate_and_wedge`

# A publish refusal naming a commit is not re-asked against origin before a reader sees it

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `a-refusal-naming-a-commit-is-not-reasked-against-origin` in `docs/direction/wrong_triage.yaml`. Listed 84 times across orientations, first on 2026-09-25.*

## What it is

`liveness_surface_refusal` in `docs/observability/.publish_gate_state.json` recorded `push_never_landed` for `38086de23`, then for `7bcf2518f`, while origin already contained each one (`git merge-base --is-ancestor` true). The field has since rotated and now reads None. `c0f71f95b` re-asks the episode's cause; nothing re-asks a refusal that names a commit.

## Why it is folded here

It is a field of the publish gate's state, read by the brief and the front door, and belongs with that gate's other attribution defects. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
