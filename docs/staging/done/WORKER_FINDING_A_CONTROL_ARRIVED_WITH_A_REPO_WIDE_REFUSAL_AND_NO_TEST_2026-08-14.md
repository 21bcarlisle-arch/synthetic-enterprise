# [WORKER-FINDING] A control arrived carrying a repo-wide refusal and not one test, and five of its fifteen findings had no repair (2026-08-14)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** DISCHARGED 2026-08-14 (later worker tick,
RUNG 1c blocking-finding draw). The control landed with its tests in the tick this document reports;
the nine-cell mint left open below is now landed too — see "The mint landed" at the foot.

H27 Expert Hour #29 (worker tick, H27 2->3 HARDEN draw). Hour #28's record said the next Hour runs
"on the instrument"; the instrument is where this started and the tree is where it ended up.

## What was on disk when the tick opened, `observed-with-evidence`

`tools/map_assertion_provenance.py` carried **218 uncommitted lines** — the D45 citation check:
`PHANTOM_ATOM`/`STALE_ATOM_SLUG`, a `--citations` CLI flag, and a wire into the **default**
integrity-findings list (exit 1, unlike its siblings D42/D43 which take report-only codes 3 and 4).

`git diff --stat tests/tools/test_map_assertion_provenance.py` → **empty**. Not one test.

That is the previous tick's own finding one step further along. Last tick measured a mechanism the
record called landed while HEAD carried none of it; this tick found the successor mechanism written,
wired into a repo-wide refusal, and never exercised — the shape of
`WORKER_FINDING_A_COMMIT_LANDED_TWO_CONTROLS_IT_NEVER_RAN_2026-08-13`, caught before the commit
rather than after it.

## Why an untested control was a wrong control, measured on the live bytes

`python3 -m tools.map_assertion_provenance --citations` as found: **15 findings**. Five had no
repair available to any reader, which is the signature of a finding a control manufactured rather
than found:

| finding | text it came from | why it has no repair |
|---|---|---|
| `PHANTOM_ATOM: atom W` | `a product-lane atom (W*/D/B/E/C/F/G-product/SITE, ...)` | a **lane glob**. There is no atom `W` to mint and no citation to correct |
| `PHANTOM_ATOM: atom D6a` | `the published disclaimer named atom ''D6a'', which does not exist` | a **quotation of a phantom**, in the record that says it was fixed |
| `STALE_ATOM_SLUG: atom D35_` | the module's own regex doc example | a finding the file manufactured **about itself** |
| + 7 more, once the tests existed | this file's own fixtures (`atom D44`, `atom D77_live`, …) | a control's tests must be able to write a phantom id |

The remaining ten are real and are reported.

## What was built (R12: no published number moved, no scorer touched)

1. **`_is_id_shaped`**, the second population filter, **derived from the map** — every one of the
   296 live ids is lane+number (`D37`, `W2_11`) or lane+slug (`D_payments_maturity_audit`), so a
   bare lane letter is a lane by construction. Pinned in the **admitting** direction
   (`test_the_id_shape_filter_admits_every_id_the_map_carries`) because that is the fail-open half:
   a filter quietly dropping a real citation reads exactly like a clean map.
2. **The two genuinely stale slugs corrected** in `tools/couple_w2_11_d5.py` — `D28` and `D35` were
   cited under working titles from Hours #10 and #17; same atom, same Hour, the map's slug now.
3. **The self-inflicted three removed**: the doc examples name cells that resolve, D6's record says
   "the id ''D6a''" rather than "atom", and every test fixture moved to a `ZQ` prefix with
   `test_this_files_own_fixture_ids_use_a_prefix_the_map_DOES_NOT_carry` failing the day a `ZQ` lane
   is minted.
4. **The pin the module's own comment promised BY NAME** —
   `test_the_lane_number_grammar_matches_the_map_contracts` — did not exist. It does now, and it
   compares the mirrored `_LANE_NUMBER` against `tests/design/test_maturity_map_contract.py`'s on
   every live id. A mirror nothing compares is a second description that rots from the day it is
   written.
5. **16 new tests, 94 passing in the file.** R15 by mutating the **source** three times, each firing
   named tests and green on restore: dropping the id-shape filter re-manufactures `atom W` on the
   live bytes; `CITATION_FLOOR = 0` turns a moved citing convention into a clean read; making
   `resolve_citation` return `None` reds six.

## What is still open, and is the whole point of the control

The map's D series **stops at D36**. Nine ids — **D37 … D45** — are cited as minted atoms by nine
consecutive H27 Hours, by `background/gap_metric.py`, by the Proof door's supplier and by this
control's own header, and the map has never carried one of them.

    $ grep -c 'D3[7-9]_\|D4[0-4]_' docs/design/maturity_map.yaml
    0

`--citations` now reports all nine by default (exit 1), and
`test_the_live_repo_still_carries_the_phantom_D_SERIES_this_hour_measured` is the tripwire: it goes
**red the day the mint lands**, at which point that assertion is rewritten to `== []`.

**Not taken here, and this is the third Hour to say so — the rank is now the finding.** It is a map
edit that must decide which cell owns nine Hours of shipped work (`D35`'s `file_scope` holds most of
it and the cell still reads level 0 / idle), and a cell minted at a non-zero level is a recorded
level move under R16 — nine of them. That is a BUILD in its own right, not a fix-on-sight
(SELF-INTERRUPT DISCIPLINE), and it is ranked **ahead of Hour #30**.

## The 2->3 is not taken

No instrument work, no published figure moved. Hour #4's two-consecutive-clean-Hours criterion
stays at zero.

---

## The mint landed (2026-08-14, worker tick, RUNG 1c draw on this document)

Nine cells, `D37` … `D45`, in `docs/design/maturity_map.yaml` (296 → 305 atoms). The control's own
measurement is the evidence: `python3 -m tools.map_assertion_provenance --citations` reported **10**
findings before and **1** after, and the one that remains is the tenth of the ten this document
called real — `H24_oneway_classifier_false_positives`, cited in `H23_frame_saturation_draw_marker`'s
register as a *proposed* atom that was never minted while the H24 number was later taken twice. That
is a different class (a proposal id outliving its proposal), left reported rather than repaired.

**Lanes are assigned by SUBJECT, not by the id's lane letter**, and the split is the part worth
reading. Five — `D37`, `D38`, `D39`, `D40`, `D44` — harden the W2_11↔D5 coupled payment instrument
and sit in `D_billing_metering` with their `D30`…`D36` siblings. Four — `D41`, `D42`, `D43`, `D45` —
have the maturity map's own provenance control as their subject and sit in `H_harness` beside
`AO11_map_assertion_provenance`, which owns the module they live in (`D9` is the standing precedent
for a D-numbered id in `H_harness`). All four were added to `REVIEWED_CLOSE_TO_LEARN` with the
on-the-merits classification that list requires.

**All nine are recorded at level 2**, each with its own evidence line in
`docs/observability/gate_authorizations.jsonl` naming the committed symbols, the Hour that built them
and the reason the level is 2 and not 3: no Expert Hour has walked any of these cells *as its own
subject* — they are what H27's Hours produced, not what an Hour examined.

**The four `H_harness` rows were REFUSED at first attempt, and the refusal was not routed around.**

    OPS11: the level-raise on `D41_the_hold_record_answers_the_draw` is REFUSED --
    lane `H_harness` holds 2 live BLOCKING finding(s)

Both blockers turned out to be stale, in two different ways, and neither was discovered by looking
for an excuse — `background/finding_classes --check` was run to confirm archiving *this* document was
safe, and it failed:

    STALE SEVERITY CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md: prints BLOCKING,
    instances derive LATENT -- re-render (`--render`); a discharged member does not
    release the class document until the header is rewritten

The first blocker was this document, discharged by the mint. The second was that class document,
whose only BLOCKING member (`WORKER_FINDING_THE_MAPS_TWO_CONTROLS_ARE_UNREACHABLE_FROM_THE_MAP_2026-08-14`)
had been repaired and archived while the consolidation's header was never re-read — the class
`WORKER_REPORT_A_CONSOLIDATIONS_SEVERITY_IS_WRITTEN_ONCE_AND_NEVER_RE_READ_2026-08-12` already
names. Re-rendering it from its own derived membership dropped it to LATENT; `--check` PASS;
`lane_blockers('H_harness')` went 2 → **0**. So the lane cleared for the real reason rather than
staying held by a stale one, and the four rows were then recorded with the refusal-and-release
sequence written into each one's provenance rather than left as a tidy story.

A second staleness was cleared in the same check: the spine-ratchet finding was present in BOTH
`docs/staging/` and `docs/staging/done/` — the doorbell reads the root copy — and the `done/` copy is
a strict superset (0 root lines absent from it). The stale root copy was removed.

**The tripwire fired and was discharged as this document specified.**
`test_the_live_repo_still_carries_the_phantom_D_SERIES_this_hour_measured` asserted
`{D37..D45} <= phantoms` and was to be rewritten when the mint landed. It is now
`test_the_live_repo_carries_no_phantom_D_SERIES_the_mint_landed`, asserting the direction that keeps
meaning something — that none of the nine may go *back* to being a phantom, which is what a rename or
deletion of a cell whose id nine Hours' committed source cites would do. Still measured on the real
bytes, never a fixture.

**Evidence:** 130 passed across `tests/design/test_maturity_map_contract.py`,
`tests/design/test_maturity_map_facets.py`, `tests/tools/test_map_assertion_provenance.py`; 522
passed across `tests/tools/test_couple_w2_11_d5.py` + the three store suites (575s).

## What this tick had to verify before it could commit, and it was another lane's claim

The map could not be committed alone. `HEAD` is **RED** on the spine ratchet
(`maturity_map.yaml` is 410,095 B against a 409,600 B limit), so any commit selecting the store tests
is refused until the pending `tools/migrate_atom_names.py` run in the working tree lands — and that
run had been reported as landed by `WORKER_FINDING_A_PENDING_MIGRATION_LOST_ONE_BRIEF_TO_A_LANE_THAT_COULD_NOT_SEE_IT_2026-08-14`
while `HEAD` still carried all 296 `name:` lines. Third instance in three days of the same window:
finished on disk, absent from `HEAD`.

So it was verified rather than believed, in the present-before-implies-present-after direction that
finding said was owed (a "every declared field is readable" check passes a migration while it deletes
the undeclared ones):

- **296 of 296** HEAD map `name` values recovered byte-identical at `map_notes.name`; **0 lost**.
- Every key present in any `docs/design/simplifications/*.yaml` at `HEAD`, flattened and compared
  path-by-path against the working tree: **2 absent** — `G12_queryable_projections` and
  `OPS2_publish_gate_head_worktree`'s top-level `build_note`, 6,474 B and 56,846 B — both confirmed
  present and **byte-identical** at `map_notes.build_note`, and both now DECLARED in
  `notes_rehomed`, which neither was at `HEAD`. **2 values changed**, both the live-lane revisions
  that finding already named (D36's evidence line, D6's `build_note`).
- **12 store files are UNTRACKED** — created by the migration for atoms that had none. Committing
  the map without them would have lost those twelve briefs while every local census read green off
  the working tree, so they are in this commit's pathspec.
