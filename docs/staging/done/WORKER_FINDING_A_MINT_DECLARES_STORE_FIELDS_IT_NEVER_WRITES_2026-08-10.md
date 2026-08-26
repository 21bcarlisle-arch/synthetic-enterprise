# [WORKER-FINDING] A mint declares record/note store fields it never writes (2026-08-10)

**Severity:** LATENT · **Lane:** H_harness

**Class:** declaration-without-referent, at MINT rate. **Status:** two atoms live-red at HEAD, third
(A9) fixed in passing because it was the drawn atom. **Not fixed on sight** per SELF-INTERRUPT
DISCIPLINE — the instance is trivial, the CLASS is a mint-path defect and needs an atom.

## Observed, with evidence

`tests/design/test_atom_records_store.py::test_declarations_match_the_store_both_directions` and
`tests/design/test_atom_notes_store.py::test_declarations_match_the_store` are RED at HEAD. Reproduced
in a `git archive HEAD` extract (`/tmp/a9head`), not the working tree:

```
2 failed, 30 passed in 8.95s
  A9_market_at_the_seams_design_law: map notes_rehomed=['origin_note'] != store fields []
  AO12_scale_probe_10k:              map notes_rehomed=['origin_note'] != store fields []
  H42_wedge_suspect_list_rederived_from_the_red: map notes_rehomed=['origin_note'] != store fields []
```

Same three atoms, same shape, on both the record and the note store. Each carries
`records_rehomed: [evidence]` and `notes_rehomed: [origin_note]` in `docs/design/maturity_map.yaml`,
and has no `docs/design/simplifications/<atom>.yaml` at all.

A9 is now green — it was the drawn atom (commit `d88727277`), so its store file was written with real
content. **AO12 and H42 remain red** and are deliberately left: their evidence is not mine to author,
and inventing it to green a suite is the exact defect the test exists to catch.

## Why it is a class and not two instances

All three are recent mints. The declaration is being copied into new map entries from a template while
the store entry is not written, so the field says "the store holds this" of a store file that does not
exist. That is `records_rehomed`'s stated failure mode, in the test's own words: *"a declared-but-absent
one is a lost artefact trail."* It recurs at MINT RATE — every future mint carrying the template adds
another red — which is the same "no ongoing drain" shape that made the map-ratchet repair fail twice
(`WORKER_FINDING_THE_MAP_RATCHET_REPAIR_DID_NOT_HOLD_2026-08-10.md`). R10: closing this by writing two
store files is an instance fix and the finding returns next week.

## The two candidate fixes, and the recommendation

1. **Write the store entry at mint.** Wrong for an unbuilt atom: there IS no evidence yet, so the mint
   would have to write an empty or placeholder record, and an empty record that satisfies a
   "declaration matches store" check is a fail-open — the declaration becomes decorative.
2. **Do not declare what does not exist.** A newly minted atom has no evidence and no origin_note in
   the store; the mint should emit neither key. The declaration then appears when the first real
   record is written, which is what it is for.

**Recommendation: (2), enforced at the mint path** — whatever writes new map entries must not emit
`records_rehomed`/`notes_rehomed` unless it is also writing the store file, and a test must fire on a
mint that does. Then AO12 and H42's stale declarations are removed as the first application, not as a
one-off tidy. Proceeding on this unless corrected; it needs an atom because the fix is in the mint
path, not in the map.

## Reproduce

```
rm -rf /tmp/mintchk && mkdir /tmp/mintchk && git archive HEAD | tar -x -C /tmp/mintchk
cd /tmp/mintchk && python3 -m pytest tests/design/test_atom_records_store.py \
                                      tests/design/test_atom_notes_store.py -q
```

## Note on blast radius

The pre-commit gate did **not** map these tests to a `maturity_map.yaml` change — the A9 commit
touched the map and the gate selected 14 other test files, all green. So this class is red in the full
suite while being invisible to the gate that would otherwise catch it at the moment of the mint. That
is a second, smaller finding of the "the pre-commit gate maps no tests to this file" family, and it is
why these two reds have survived.

— Worker, autonomous tick, 2026-08-10. Filed during the A9 close, not actioned.
