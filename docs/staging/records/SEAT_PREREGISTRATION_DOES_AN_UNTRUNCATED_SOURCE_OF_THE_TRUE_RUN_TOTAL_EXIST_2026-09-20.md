**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"run history total is a floor not a total and nothing renders it"

# Pre-registration: does an untruncated source of the true run total exist?

**Written BEFORE the measurement, delivery seat, 2026-09-20. Left uncorrected beside its results.
The question is §4/§6 of
`SEAT_RESULT_THE_PUBLISHED_SERIES_WAS_FRESH_THE_KPI_WAS_CAPPED_AND_ITS_PAGE_WAS_DELETED_2026-09-19.md`,
which filed the surface decision explicitly rather than taking it.**

---

## What is established before measuring (landed, 858f38dd7, not re-derived here)

- `generate_insights.append_run_history` ends `history = history[-100:]`. The ledger is a 100-entry
  ring buffer.
- `docs/observability/run_history.json` has held exactly 100 entries since 2026-06-30 (`39c15c1b5`),
  so `count_run_history_total` has published exactly `100` on every build for 81 days. **The number
  is a floor. The ledger cannot say by how much.**
- `site/project/` and its `renderKpis()` were deleted 2026-08-20 (`03dd8c49e`). **Nothing under
  `site/` reads `run_history` or `run_history_total`.**

The drawn item names three options and says option 2 — recompute the true total — must be
**measured, not assumed**: "docs/reports/run_output_*.json may be pruned too, so this is a question
to measure, not a number to pick". That is the only open empirical question. This document is that
question's predictions.

## The question

**Q. Does any source in this repository establish how many runs have actually been recorded — a
number that is a TOTAL and not another floor?**

A source qualifies only if it is (a) not truncated by its own writer, and (b) not pruned or
rotated by anything else. A source that is itself a floor does not answer the question; it only
moves the floor.

## Predictions, written now

**P1. `docs/reports/run_output_*.json` is NOT a viable source.** 7 files exist. I predict they are
not a per-run ledger at all — too few, and a run ledger that rotated to 7 would be a worse floor
than 100. Confidence: high.

**P2. The git history of `run_history.json` gives a HIGHER floor, not a total.** The union of
`git_hash` values across every committed revision of the file is the obvious recompute. But the
file was uncommitted for 64 days (the whole subject of the prior finding), so whole windows of runs
were overwritten in the working copy and never reached any commit. I predict the union exceeds 100
and is still **demonstrably** a floor — and I predict I can show it is a floor *by construction*
(gaps between consecutive committed revisions), not merely suspect it. Confidence: high on
"exceeds 100", medium-high on "provably gapped".

**P3. No untruncated source exists.** I predict the repository contains no artefact that can state
the true total. Confidence: medium-high. **This is the prediction most worth refuting** — a
`run_output_*` or a JSONL append-only log that nothing truncates would change the answer.

**P4. The decision will therefore be between option 1 (carry the bound) and option 3 (delete).**
Conditional on P3 holding.

**P5. My leaning, stated before measuring so it can be held against me: DELETE
`run_history_total`, KEEP `run_history`.** Not symmetrical, and the asymmetry is the point:

- `run_history_total` is a scalar that is a floor wearing a total's name, rendered by nobody. A
  floor published as `">=100"` is more honest *and still read by nobody* — the honesty buys nothing
  and the field remains a standing invitation to a future reader to render it as a total. The
  cheapest thing that cannot be misread is the thing that is not there.
- `run_history` is the 10-entry series, and I predict it is **not** unread: the control landed
  yesterday in
  `tests/background/test_the_published_series_and_the_ledger_it_came_from_are_committed_together.py`
  reads the published series to ask whether every run the dashboard publishes is in the committed
  ledger. **If that is so, deleting `run_history` silently disarms a day-old control** — an empty
  list is vacuously in-ledger, which is a textbook fail-open. Confidence that the control reads it:
  high. **If I am wrong about this, the deletion case extends to both fields.**

**P6. The refutation condition for this whole turn.** If a consumer of either field exists that I
have not found — anything outside `site/` that renders, exports or reports it to a human — the
deletion is wrong and option 1 wins. I will census the whole tree, not `site/`, because §4 of the
prior result is precisely the story of a frame built from a comment about a surface.

## What I will measure, in order

1. What `docs/reports/run_output_*.json` actually are, and whether anything prunes them.
2. Every revision of `run_history.json` in git; the union of `git_hash` across them; whether the
   gaps are provable.
3. A whole-tree census of `run_history` and `run_history_total` readers — code, tests, tools,
   docs — not `site/` alone.
4. Whether any other append-only per-run artefact exists that nothing truncates.

## What done means for this item

The surface decision is **taken and landed**, with the reason on the record beside it, and with a
control that fails if the decision is quietly undone. Not "a recommendation filed".
