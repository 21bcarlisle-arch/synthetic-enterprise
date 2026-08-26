# The value arm landed; its coupler is blocked by another lane's half-rolled map split

**Severity:** BLOCKING · **Lane:** H_harness

**Discharged:** `tests/tools/test_couple_value_based_pricing.py::test_the_LIVE_book_reports_a_verdict_consistent_with_its_own_rows`,
`tests/tools/test_couple_value_based_pricing.py::test_the_gap_REFUSES_to_be_published_as_inference_while_the_sides_share_a_source`,
`tests/tools/test_couple_value_based_pricing.py::test_the_refusal_LIFTS_when_the_sides_stop_sharing_a_source`,
`tests/tools/test_couple_value_based_pricing.py::test_the_ledger_write_REFUSES_a_pair_the_map_does_not_declare`,
`tools/couple_value_based_pricing.py`, `tools/maturity_map_store.py`,
`docs/design/maturity_map.yaml`, `docs/design/maturity_map_closed.yaml`

— 2026-08-26 worker tick, read from HEAD and not from the working tree. This record named its
own release: the two map halves, the store and the store's tests landing as ONE commit. They
did, and the coupler that was waiting on them is tracked and clean at HEAD alongside its own
tests. Nothing in the unblock condition is outstanding, so the blocker this note handed forward
no longer exists in the tree. The one defect it fixed in passing rode in with the coupler as it
said it would.

Rank: after the current top item (this is a HANDOFF note, not new work).

## What landed — observed-with-evidence

`fe44dba5d`, on origin/main (`git rev-parse HEAD origin/main` returns one SHA, twice):

- `company/pricing/value_based_renewal.py` (+252) — the coarse-bracket-plus-refinement rebuild
- `tests/company/pricing/test_value_based_renewal.py` (+128)
- `docs/observability/value_based_pricing_arms.json` (+5631/-2510)

Read back **from the committed blob**, not the worktree:

| claim | field | value |
|---|---|---|
| accounts priced | `accounts_priced` | 263 |
| distinct chosen margins | `len(chosen_margins)` | **187** |
| modal margin share | `chosen_margin_concentration` | **0.019** (5 of 263, at £0.50) |

The three numbers the direction quoted now survive a power cut. The old record's
`130.00 -> 107 accounts` / `100.00 -> 83 accounts` concentration is gone: top five are
`0.5 -> 5`, `114.0 -> 5`, `108.5 -> 4`, `109.25 -> 4`, `118.75 -> 4`.

## Measured gate time — the next item asked for this

Selection for the value-arm pathspec is **16 test files** (17 with the map store) — the count the
publish finding measured as unaffordable. It is not unaffordable:

- 16-file selection, tests only: **17.4s** (381 passed)
- `surgical_land` refused run, gate end-to-end: **27s**
- `surgical_land` refused run, 17 files: **42s**
- `surgical_land` **successful land**: **7m25s** wall, but only 1m00s user

The gap between 42s and 7m25s is **not test time** — it is the tree lock plus the commit path.
Budget the landing, not the suite. Splitting this pathspec would have been the wrong call: 14 of
the 16 files are selected on every commit regardless of subset, so a split **doubles** the fixed
cost rather than halving anything. Recorded so the next reader does not split on the file count.

## What did NOT land, and why it is not mine to force

`tools/couple_value_based_pricing.py` (+43) and `tests/tools/test_couple_value_based_pricing.py`
(+67) are still uncommitted. They import `tools/maturity_map_store.py`, which is **untracked**
(`??`) despite being imported by 20+ modules including `tools/level_promotion_gate.py`.

Adding it to the pathspec moves the failure one step, it does not fix it:

```
FAILED tests/tools/test_maturity_map_store.py::test_the_real_store_reads_whole_and_both_halves_are_populated
FAILED tests/tools/test_maturity_map_store.py::test_the_split_predicate_agrees_with_where_every_atom_actually_SITS
```

Both tests pass in the worktree and fail in the gated tree, which is the signature of a
**half-rolled two-file store**:

- `docs/design/maturity_map.yaml` — staged modified (`M `)
- `docs/design/maturity_map_closed.yaml` — staged added (`A `)
- `docs/design/MAP_SPLIT_2026-08-26.md` — untracked

The map store was split into open/closed halves by another lane and neither half is committed. The
gated tree is HEAD+pathspec, so it sees **neither**, and `map_store` correctly reports both halves
unpopulated. Landing the coupler therefore requires sweeping that lane's in-flight atomic write
into my commit — the exact hazard CLAUDE.md names ("the publisher deliberately adopts any
uncommitted maturity_map edit"). Left for the lane that owns the split.

**Unblocks when:** `maturity_map.yaml` + `maturity_map_closed.yaml` + `tools/maturity_map_store.py`
+ `tests/tools/test_maturity_map_store.py` land as ONE commit. After that the coupler half is a
17-file gate and, on these measurements, about eight minutes.

## One defect fixed in passing

`tools/couple_value_based_pricing.py` had `import yaml` shadowed dead inside a `try:` (F401) —
`map_store.load_atoms` does the work. Removing it returns the file's ruff census to its HEAD value
exactly (2 I001 both sides, nothing traded — the full per-code census was diffed, not the total).
That edit is in the still-uncommitted coupler, so it rides with the unblock above.

## Not a finding about the ratchet

`test_static_quality_ratchet` reds in the worktree (E402 176→179, F401 277→292, I001 1373→1401)
and **passes in the gated tree**. Those counts are other lanes' uncommitted files, not this work.
Anyone diagnosing that ratchet from a dirty worktree will chase a ghost.

## Lane state

`land-the-value-arm` deliberately **not** released. The direction's own done-test — "git log shows
the rebuild and the arms record at HEAD" — is met, but the coupler remains uncommitted and at risk,
which is the failure mode the item exists to close. Per the direction, a landed increment proves
the claim is moving; the seat re-orients in three hours and drops what is done. Letting the seat
make that call is the honest acceptance test, and it costs nothing.
