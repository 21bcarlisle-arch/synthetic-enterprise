# [WORKER-REPORT] Fifth publish wedge: the cause, and the disposition of the eight cited suspects (2026-08-10)

The rung-1 doorbell cited eight filed findings as "ALREADY HOLDING THE SUSPECTS" and asked that each
be drawn first and dispositioned. **None of the eight was the cause.** The cause is named below with
evidence, and it is closed. The eight are re-frozen with provenance — they remain real, queued, and
unchanged in priority; they were suspects by proximity (all filed during the previous episodes), not
by any evidence tying them to this red.

## The actual cause, observed

Blocking test, from the gate's own output:
`tests/design/test_atom_notes_store.py::test_declarations_match_the_store`.

Commit `192e29792` minted `H38` and `H39` into `docs/design/maturity_map.yaml` with
`notes_rehomed:` declarations, and added `build_note` to `H36`'s — and touched **no file** in
`docs/design/simplifications/`. H32's contract checks both directions on purpose ("a declared field
with no stored note is a lost record"), so three atoms declared prose that lived nowhere:

```
H36...: map notes_rehomed=['build_note','origin_note'] != store fields ['origin_note']
H38...: map notes_rehomed=['origin_note'] != store fields []
H39...: map notes_rehomed=['origin_note'] != store fields []
```

Closed at `f0493363b` by writing the four missing notes from their real sources (192e29792's own
commit body; the two findings in the H36 section of `BAND_NULL_SWEEP.md`) — recovered, not invented.
A **second** red at HEAD surfaced behind it, `test_the_committed_document_agrees_with_the_live_derivation`
(the derived-artefact staleness class, deadlocked because the repair can only land after a green
gate), closed at `a06726529`.

Two things this episode added to the record, both filed separately:

* `WORKER_FINDING_THE_WEDGE_ALARM_IS_DISARMED_BY_RUNS_THAT_PUBLISH_NOTHING_2026-08-10.md` — the
  alarm cleared at 00:59Z while HEAD was provably red.
* The working tree held a **second** entire uncommitted pass (H38, 922 lines), one commit after
  `192e29792` landed H36 for exactly that reason. Landed here; the class is already filed as
  `WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09.md`, and this is its
  second instance in two commits.

## The eight, re-frozen with provenance

Each was checked against the gate's actual failure output before being set down. None appears in the
gate's red path; the gate runs with `-x` and stopped at the note-store test both before and after.

| cited finding | disposition |
|---|---|
| `..._THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10` | not implicated — no test of its subject reached the gate's stop point. Re-frozen. |
| `..._TWO_UNIMPORTABLE_PHASE2A_MODULES_2026-08-09` | not implicated — the phase2a modules sit under the gate's own heavy-ignore list. Re-frozen. |
| `..._WRITE_TIME_GATE_FIELD_SWALLOW_2026-08-08` | not implicated. Re-frozen. |
| `..._THE_SECOND_DIRECTION_NEEDS_ITS_OWN_POPULATION_2026-08-09` | not implicated. Re-frozen. |
| `..._TWO_NUMBERS_ONE_NAME_2026-08-09` | not implicated. Re-frozen. |
| `..._THE_INDEX_READS_THE_WORKING_TREE_2026-08-09` | not implicated in this red, and note the gate's subject has since moved to a clean HEAD checkout, which is the same disease this one describes. Re-frozen, worth re-reading against that change. |
| `..._THE_MODELS_STORAGE_HEATER_IS_NOT_ONE_2026-08-09` | not implicated. Re-frozen — and adjacent to H38's landing, which nets the water heater but explicitly does not touch the storage-heater question. |
| `..._THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09` | **implicated, but as the ENABLER, not the cause.** `tests_for()` returns `[]` for any non-`.py` path, so `192e29792`'s map-only mint selected zero tests and reached HEAD green. This is now its **second** wedge. Not fixed here — instance-fixing it inside the unwedge would have buried the unwedge — but it should be read as having earned R3's two-strike treatment. |

## Recommendation

Take the pre-commit-gate finding next, at rung 1 rather than as ordinary queue: it is the only one of
the eight with a causal link to a wedge, it now has two, and the fix already exists in-repo
(`tools/select_impacted_tests.py` refuses to narrow on an unmappable path, which is the correct
policy and is already mutation-proven). Proceeding on that unless redirected.

— Worker report, 2026-08-10.
