# [WORKER-FINDING] The spine ratchet has eight bytes left, and what refills it is a doorbell notice rewritten every step (2026-08-14)

**Severity:** LATENT · **Lane:** H_harness · **Status:** measured, not repaired — the repair is a
rehome and this tick had no mandate to move another lane's draw text.

Found while landing `OPS13_product_interleave_armed` and KNIFE3 step 27, both of which had to write
to `docs/design/maturity_map.yaml`.

## The measurement, `observed-with-evidence`

`tests/design/test_simplifications_store.py::test_map_within_size_ratchet_when_store_populated`
holds the spine at **409,600 B**. Byte counts taken this tick:

| tree | bytes | headroom |
|---|---|---|
| HEAD before this tick (`0f44bd4ec`) | 409,557 | 43 |
| + OPS13's level move + three count repairs | 409,585 | 15 |
| + KNIFE3 step 27's re-stated notice, as its lane wrote it | 409,667 | **−67, RED** |
| + the same notice, compressed to fit (landed) | 409,592 | **8** |

Eight bytes. The next atom to gain a field, and every future KNIFE3 step, reds this control before
it can be committed — and because the pre-commit gate selects tests by path stem, it reds *at the
commit*, not while the change is being written.

## Why this is not "raise the number"

The ceiling's own history says so in the test file: it was raised 400K → 640K during a ~10h publish
wedge, and `H32_map_size_ratchet_red_on_head` put it back by doing the real work (rehoming the
narrative-note class into the sibling store, 521,770 → 393,692). The comment left the standing
question — *"whether the spine has a new unbounded FIELD to rehome, NOT whether to raise the
number"*. This finding answers it with a name.

## The field

`KNIFE3_wall_crossing_paydown`'s `name:` is **2.6 KB of doorbell notice** and it is REWRITTEN EVERY
STEP, by design: it carries the live cut counts so a drawn step cannot redraw from zero. That makes
it the one spine field whose size is a function of how often the atom is drawn rather than of how
many atoms exist — the same shape as the note class H32 already rehomed, wearing draw-instruction
clothes.

The reason it has not simply been moved: the draw shows the atom's `name:`, so rehoming the notice
into the store's note tenant silences the DO-NOT-REDRAW warning at exactly the moment it matters,
unless the draw hydrates notes first. That is the work, and it is a draw of its own — the ordering
is *hydrate, then move*, never the reverse.

## What is NOT claimed

- No claim that any published figure is affected: this is a repo-size control, not a business one.
- No claim that compression is a fix. It bought 8 bytes and is stated as such in the landing commit,
  not recorded as a repair.
- The 2.6 KB figure is the `name:` field of one atom measured today; no census of the other 244
  atoms' fields was run, so a larger refill source elsewhere is possible and unmeasured.

**Evidence:** `docs/design/maturity_map.yaml` · `tests/design/test_simplifications_store.py`
(ceiling + roll watermark) · commits `b5fa18d3a`, `6caab295e` (the two landings whose byte counts are
tabulated above).

---

## UPDATE (2026-08-14, worker tick, D30 DISCOVER/FRAME draw): it has happened, and the "it reds at the commit" clause above is WRONG

**Severity of the update:** LATENT (repo-size control; no published figure affected).

`docs/design/maturity_map.yaml` at HEAD `401fa828e` is **410,095 B against the 409,600 B ceiling —
495 B RED**, confirmed by running the control:

```
tests/design/test_simplifications_store.py::test_map_within_size_ratchet_when_store_populated
E  AssertionError: maturity_map.yaml is 410095 bytes, over the 409600-byte spine ratchet
```

Byte counts by commit: `185669ba5` 409,592 (the 8-byte landing this finding was written from) →
**`10b65038a` 410,095** (+503, the SITE2 HARDEN landing) → `401fa828e` 410,095. The prediction in
this document — *"the next atom to gain a field ... reds this control before it can be committed"*
— was right about the timing and **wrong about the mechanism**, which is the part worth having.

### The control is not reachable from the commit gate for its own subject

`tests/design/test_simplifications_store.py` appears **nowhere** in `tools/pre_commit_test_gate.py`.
Dry-run of `select_targets(['docs/design/maturity_map.yaml'])` at HEAD:

```
tests/background/test_gate_authorization.py      tests/design/test_maturity_map_facets.py
tests/design/test_atom_notes_store.py            tests/test_coupled_triad_gate.py
tests/design/test_atom_records_store.py          tests/tools/test_generate_proof_coupled_gaps.py
                                                 tests/tools/test_level_promotion_gate.py
```

Seven tests, and the map's own size ratchet is not one of them. So a map edit of any size commits
clean and the red surfaces later, in the full suite — which is how +503 B landed without anything
firing. `LEVEL_SENSITIVE_TESTS` already carries `*STORE_CONTRACT_TESTS` for exactly this class
(the 2026-08-10 note in that list says the store-contract tests "were not reachable from a
maturity_map.yaml change", and three mints landed red on HEAD before they were added); the SIZE
half of the same store contract was left out of that fix.

**Recommendation (not asked bare):** add `tests/design/test_simplifications_store.py` to
`LEVEL_SENSITIVE_TESTS` in the same edit as the rehome. Doing the rehome alone buys headroom and
leaves the control unreachable, so the next refill lands red on HEAD the same way — that is the
drain-vs-instance distinction the 2026-08-10 note in that very list already drew.

**Not done here** (SELF-INTERRUPT DISCIPLINE): this tick's draw was D30 DISCOVER/FRAME and the
repair is another lane's, with the *hydrate-then-move* ordering this document names. The D30 pass
worked around it by not touching the map at all — see the STATUS section of
`docs/design/simplifications/D30_the_belief_band_is_this_books_length.yaml`.
