# SEAT RESULT — the DD stopping rule was drawn twice; the rival worker is building it (2026-10-03)

**Severity:** LOW — process note, no defect in the subject.

The executor drew `build-the-supplier-dd-stopping-rule` into an isolated seat worktree at
14:29 BST. That same id was already held in `.seat_work_in_hand.json` by a live scheduled
worker (pid 2590080, started about 14:06, running its gates at draw time). Its work was
already on the shared tree, uncommitted:
`company/billing/dd_collections_desk.py` (+38/-1) adds `DD_STOP_THRESHOLD_CONSECUTIVE_RETURNS = 2`
with the British Gas single-supplier citation, `pays_by_direct_debit`, a refusal to present
against a cancelled mandate, and `record_collection_outcome` returning True when it calls
`cancel_mandate`.

**Disposition: no build here, and no `--release`.** A second build would be the same work
twice and would collide with that worker's landing. `--release` would mark the item finished
while it is unlanded, so if the rival fails, the item would be lost.
If the rival lands, the next draw's premise and path checks will show it as spent. If it
does not, the item comes back to the pool untouched, which is the right outcome.
