**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# `H40` and `H48` were REFUSED a repoint, and the reason is a gap in the cause vocabulary: an atom whose deliverable is a RECORD writes no file, and every repair the census can print tells it to name one

Completes the work item that fixed the `HONESTLY_UNBUILT` guard and then repointed the four
`NAMES_ONLY_A_SCOPE` rows naming only directories. **Two of the four were repointed. Two were not,
and this says why rather than inventing a filename to make the count move.**

## What was done, and what it is worth

| row | was | now | cause after |
|---|---|---|---|
| `G4_unified_failure_register` | `[docs/retrospectives, tools, tests]` | the three artefacts `UNIFIED_FAILURE_REGISTER.md` §7 (L2) declares | `HONESTLY_UNBUILT` |
| `SP2_2_rng_substream_primitive` | `[simulation, tests/simulation]` | `simulation/rng_substream.py` + its control | `HONESTLY_UNBUILT` |
| `H40_full_suite_pollution_bisect` | `['tools/', 'tests/']` | unchanged | `NAMES_ONLY_A_SCOPE` |
| `H48_..._idle_hole_at_scale` | `['docs/staging/in_progress/', ...]` | unchanged | `NAMES_ONLY_A_SCOPE` |

Both repoints are DISCOVERY, not invention: each row's own design doc names the files its build
writes, so the map now records a declaration that already existed rather than a filename somebody
picked. Both were delisted from `LEGACY_UNGRADABLE_BUILD_ROWS` (24 → 22), which the allowlist's own
`test_ungradable_build_rows_allowlist_has_no_FIXED_entries` requires.

**And the honest caveat about the count.** `HONESTLY_UNBUILT` is the one cause in
`CAUSES_OWING_NO_REPAIR`, so the owes-a-repair figure fell 26 → 24 on this commit. That is the exact
shape the predecessor finding warned about — "leaves the count by getting vaguer" — and it is worth
saying why this is the other thing. The repair those two rows owed was TO THEIR `file_scope`, and it
has been paid: three named files where three bare directories stood. What remains is a BUILD, which
is what `HONESTLY_UNBUILT`'s repair string says out loud ("build the atom, or close it"). The
verdict is also now self-clearing — it stops being true on the commit that lands the first named
file, where `file_scope: [tools]` could never have changed whatever was built.

## The finding: the repair is unfollowable for `H40` and `H48`, and not because nobody has tried

Both rows name only directories. Neither names a subject module, and — this is the part that is a
finding rather than an excuse — **neither has a design doc naming one anywhere in the tree**, unlike
the two that were repointed. Searched: `git ls-files` for `pollut|bisect` and for `parked` returns
their own `docs/design/simplifications/*.yaml` and nothing else. No FRAME doc, no DISCOVER doc, no
module under any name.

The reason is structural and is in each atom's own exit criteria:

* **`H40`** — "the bisect is EXECUTED and the polluting module is NAMED with the evidence; the
  MECHANISM of the pollution is stated; the class fix is drawn as its own atom; the record says what
  was tried and did NOT reproduce". Five deliverables, all of them a RECORD. The class fix is
  explicitly drawn elsewhere so the diagnosis is not held hostage to the repair — so `H40` writes no
  repair, by design.
* **`H48`** — an audit of 121 parked documents under five dispositions, each carrying an evidence
  line. Its output is dispositions applied to documents, not a module.

`NAMES_ONLY_A_SCOPE` prints one repair: *"name the FILES this atom writes, not the directory they
live in"*. For a row that writes no file, that instruction cannot be followed, and the only way to
make the census look better is to invent a filename — which is how a row leaves the count by getting
vaguer, the exact defect the predecessor finding names.

## Why this is not fixed here, and what would fix it

The tempting repair is a ninth cause: "this atom's deliverable is a record, not a file". **It is not
built, because nothing in the tree can measure it.** The only witness that `H40` produces a record
rather than a module is its own prose, and a detector reading prose to decide whether an atom writes
code would be guessing — and guessing in the direction that excuses rows, which is the direction
this whole family of defects already runs in. A cause that fires on a judgement nobody measured is
`CONTROL_NEVER_WRITTEN` again, one level up.

What would actually settle it is a FIELD the mint writes, not a classifier: an atom declaring at
mint time whether its exit is a file or a record, the way `provenance` and `value_stream` are
declared. Then the census asks the row instead of guessing about it, `NAMES_ONLY_A_SCOPE` stops
being printed at rows that can never answer it, and the two entries can leave
`LEGACY_UNGRADABLE_BUILD_ROWS` on a true statement. That is a map-contract change with a ratchet cost
and it is not this turn's work; it is recorded here so the next turn to reach these two rows does not
re-derive the refusal.

**Until then both rows stay allowlisted and the allowlist comment carries the reason**, so the next
reader finds the refusal beside the entry rather than in a file they would have to know to look for.

## State after the pass

28 candidate rows, 24 owing a repair. `NOTHING_IN_THE_ROW` 10, `CONTROL_UNNAMED` 10,
`HONESTLY_UNBUILT` 4, `NAMES_ONLY_A_SCOPE` 2, `CONTROL_NEVER_WRITTEN` 2, `SUBJECT_NEVER_WRITTEN` 0.

Mutations proving the two halves of the repoint are each load-bearing:

| mutation | reds |
|---|---|
| `G4` re-added to `LEGACY_UNGRADABLE_BUILD_ROWS` | `test_ungradable_build_rows_allowlist_has_no_FIXED_entries` — the delisting was required, not cosmetic |
| `G4`'s `file_scope` reverted to the bare directories, delisting kept | `test_a_new_build_row_names_a_control_a_runner_can_execute` — the repoint is what earns the delisting |
