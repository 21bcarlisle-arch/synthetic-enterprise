# [WORKER-FINDING] A control arrived carrying a repo-wide refusal and not one test, and five of its fifteen findings had no repair (2026-08-14)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** repaired and landed this tick, except the
nine-cell map mint it exists to demand, which is stated below and left open on purpose.

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
