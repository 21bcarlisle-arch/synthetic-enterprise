**Severity:** RECORDED · **Lane:** Lane 0 delivery · **Claim:** `land-pb4-swap-with-value-arms-retaken-in-the-new-world`

# Pre-registration: the PB4 fourth pass, taken in the world with the ex-VAT standing charge

Filed 2026-10-01 at about 16:35 BST. Capture C2 was already running and had produced no output.

## Why C2 exists

Capture C and the third-pass block were taken at `e9b79073d`. Origin then took `0407ce0e3`, which
holds the world's standing charge ex-VAT. That is the only commit in `simulation/` or `sim/` since
then. `world_level_identity` digests only the anchor block, so the digest cannot see that change.
A bill that is a different size can still move bill shock and departures. So the fit is re-asked
in the world the arms will actually run in. C2 is origin `0407ce0e3` plus the patch from
`docs/design/UNLANDED_PB4_SWAP_AND_THIRD_PASS_ANCHOR_2026-10-01.md`, using the third-pass block and
the default seed.

## Predictions, written before C2 finished

1. In every fitted year, C2's whole-book level lands within ±0.5pp of C's. The standing charge fell
   by about 5% on every bill, and a bill shock is a RISE FRACTION, so a near-uniform scale mostly
   cancels out of it.
2. 2020 and 2021 still sit low on C2, as they did on C.
3. The refit on C2 moves 2020 and 2021 up again. The fixed point is not reached in one pass.
   So D, the capture under the fourth block, is graded against the band, not against C2.
4. 2023 stays unfittable.

Results go beside this file once they are read, and nothing above will be edited.
