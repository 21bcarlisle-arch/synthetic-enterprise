# Disposition — the SEAT_RESULT premise rule landed twice, and the two landings compose

**Severity:** low — no work lost; the shared tree could not reconcile with origin until this merge.

Item `a-landed-seat-result-spends-its-preregs-grading-premise` was drawn again after it had been
built. Two lanes landed it about a minute apart:

- `75b5f6ce6` (on origin/main, 12:35) adds `result_note`. It puts a RESULT CHECK line in the doorbell
  and **does not withhold the item**, because the C1-bracket item names the same prereg.
- `d3b12ad3d` (only in the shared tree's HEAD, 12:36) adds `prereg_result` / `_result_landed`. It
  **skips** an item whose prereg result landed on origin *after* the item was written. A result that
  landed before the item is treated as context.

Both edited the same `_PREREG_NAME` block in `background/delivery_lane.py`, so the reconciler could
not merge HEAD into origin/main.

**Resolution:** keep both functions and the one `_PREREG_NAME` regex, which was identical on both
sides. Landed as merge `8fe6eefb0` via `surgical_land --merge origin/main --resolve` (gate-rc 0).

**Why the two compose:** an item written after its result is exactly the case `75b5f6ce6` was
protecting. The filter lets that item through, and the note still names the result to whoever picks
it up. Both controls pass together (12/12). In the live pool, `grade-the-c1-bracket-run-c` is still
handed out (not skipped, no note).

**Premise:** the work was spent before this draw. The draw is released from both claim stores. No
rebuild was done.
