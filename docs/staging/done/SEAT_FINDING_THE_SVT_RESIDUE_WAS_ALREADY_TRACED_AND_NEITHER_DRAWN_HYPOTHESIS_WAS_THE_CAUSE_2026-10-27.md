**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# The SVT residue was already traced, and neither hypothesis in the drawn item was the cause

Item: `the-svt-residue-is-traced` (delivery seat, drawn 2026-10-27). It asked for a trace of two
residues the 871f674a2 grade left. The first was a standing charge "billed at a neighbouring cap
window's charge". The second was an SVT unit rate "struck once and not re-struck" (SYN-2016-061
runs 13 windows). **The premise is spent.** Both residues were traced and fixed in 2eeb3f0b32
(2026-10-27 12:16), and the register `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml` already
records the result.

## What the causes were, against what the item supposed

| Residue | The item supposed | Traced cause (2eeb3f0b32) | State |
|---|---|---|---|
| INV_STANDING_CHARGE_SVT_ELEC / _GAS (735 / 1,502) | a neighbouring cap window's charge | the printer's penny rounding on periods billed exactly at the cap; a grading tolerance, not a billing defect | exceptions retired; the same book grades 0 on both |
| INV_UNIT_RATE_SVT_ELEC / _GAS (298 / 249) | a term struck once and not re-struck | each prepayment segment *was* re-struck at its own column, then raised by writers 1–2, and writer 4 clamped only at the DD level | clamp fixed: min(published level, the method's own column); exceptions still open until a fresh run grades 0 |

Neither drawn hypothesis survived. The SYN-2016-061 13-window run fits "re-struck every window, then
raised past the prepayment column each time", not "never re-struck".

## What is left, and who holds it

The fix is predicted, not yet observed. The latest completed run,
`run_output_894503ba41_20261027T112811Z`, was cut from 2eeb3f0b32's parent, so no book carries the
clamp yet. The predictions are filed in advance in
`docs/staging/records/SEAT_PREREGISTRATION_THE_NEXT_FRESH_RUN_HOLDS_A_PREPAYMENT_DEFAULT_TARIFF_AT_ITS_OWN_CAP_THROUGH_THE_COMPANYS_CLAMP_2026-10-27.md`
(both unit-rate invariants 298 → 0 and 249 → 0). Grading that run and retiring the two exceptions
is item `the-fresh-run-carries-both-fixes-and-retires-the-exceptions`.

**Correction for the draw.** The draw refused that item because "live worktree
/var/tmp/se-seat-executor holds docs/design/DOMAIN_INVARIANTS.yaml". It does not. This worktree
holds item `the-svt-residue-is-traced`, has never modified `DOMAIN_INVARIANTS.yaml`, and lands only
this note. The refusal was the held-work check reading the worktree's existence as a hold on every
path. Once this turn exits, the next draw can offer the item.

## Done

Released without building. The work was done by 2eeb3f0b32, and the remaining step belongs to the
item above. This note lands in done/ because it leaves no open action at the staging root.
