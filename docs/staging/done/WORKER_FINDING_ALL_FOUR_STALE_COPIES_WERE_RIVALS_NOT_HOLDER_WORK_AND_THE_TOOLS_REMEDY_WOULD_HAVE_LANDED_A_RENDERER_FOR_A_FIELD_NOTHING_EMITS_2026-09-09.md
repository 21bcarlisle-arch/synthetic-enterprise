**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — clear-the-four-working-copies-that-would-revert-a-landing)

# All four stale copies were rivals, not holder work, and the tool's own remedy would have landed a renderer for a field nothing emits

**2026-09-09, scheduled tick.** `tools/stale_copy_refusal` now reports **WOULD REVERT A LANDING: 0**,
which is the drawn item's stated done-condition. But only one of the four was cleared the way the
item said, and the reason matters more than the count.

## The drawn item's premise was wrong in the same way for all four

The item stated:

> every one of them is HOLDER WORK supplying names HEAD lacks (`REASONED_FIELDS`,
> `renderWholeBookRung`, two whole-book-rung door tests, and eleven names in
> `tests/tools/test_r1_inference_ceiling.py`), so the move is `isolate_hunks --survey` then
> `surgical_land --content`.

It took that from the tool, and the tool says it too — its `REMEDY:` line reads *"this copy supplies
N name(s) HEAD lacks … so it is HOLDER WORK."* **That test is one-directional.** It asks what the
working copy has that HEAD lacks and never asks the converse. Measured both ways by symbol set:

| path | names only in the working copy | names only at HEAD | kind |
|---|---|---|---|
| `background/self_clearing_alarm_census.py` | 8 | 19 | **rival, both sides real** |
| `site/harness/index.html` | 1 | 5 | rival, HEAD supersedes |
| `site/test_harness_delivery_record.py` | 6 | 46 | rival, HEAD supersedes |
| `tests/tools/test_r1_inference_ceiling.py` | 33 | 69 | rival, HEAD supersedes |

Every one is Kind A. This is the shape already recorded at
`SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES_2026-09-08.md`
— and the tool still prints the holder-work remedy for it, on all four rows.

## What following the printed remedy would have done

`isolate_hunks` diffs against HEAD, so on the two site files the working copy's contribution and
HEAD's landing fall inside **one** hunk (`@@ -441,728 +440,81 @@` on the door test). Keeping "your"
hunk keeps the revert with it. Concretely, `surgical_land --content site/harness/index.html` would
have landed:

- `renderWholeBookRung(c.whole_book, num)` — and **no producer emits `whole_book`**. The live feed
  and `tools/generate_delivery_page.py` at HEAD carry `the_whole_book_rung`; `magnitude_partitions`,
  `magnitude_low`, `magnitude_high` and `magnitude_below_the_floor` appear in **zero** generator
  lines. The renderer would have been handed `undefined` and rendered nothing.
- and deleted, in the same commit: the redraw-stability block, `fmt`, `renderCarbonCeiling`,
  `renderProductCeiling` and both ceiling panels — all live at HEAD.

The door test told the same story from the reader's side. Its unique whole-book test does not fail
on the live feed; it **skips** — `"this tree's ceiling artefact predates the whole-book rung"`. A
control that cannot fire was the thing being called holder work.

The evidence is arithmetic. Restoring the three superseded copies to HEAD's bytes took the two site
suites plus the R1 suite from **41 passed / 6 failed / 1 skipped** to **73 passed**.

## The one that was real, and what it found

`background/self_clearing_alarm_census.py` was a genuine rival: both sides added a distinct rung to
the same module and neither is in the other. Resolved by three-way merge against the copy's true
base (`d6efe4bb8`, found by minimum diff distance — no blob in 10,284 commits matched any of the
four working copies, so all four were base-plus-edits, not stale checkouts). Five conflicts, all
keep-both. The merged module is a strict superset of both symbol sets.

Landing it made HEAD's own `removed_dispositions()` rung live in this tree, and it immediately
caught a **fifth** copy of the same class that the tool cannot see:
`docs/design/self_clearing_alarm_dispositions.json` was four days stale, had dropped
`.origin_race_episode.json`, and was missing the `_retired` and `_shared_provenance` sections that
HEAD's two new rungs read. `stale_copy_refusal` filed it under **NO OPINION (no reader for this
suffix)** along with 389 other paths. *A register that the census's own rungs depend on is invisible
to the census of stale copies.* Merged keep-both (HEAD's register plus the working copy's one
unique row, `.standing_red.json`).

Then the merged resemblance rung fired on three rows of HEAD's own register
(`.sanity_daemon_last_digest_date`, `gate_authorizations.jsonl`, `naive_organ_log.jsonl`), each
citing a sibling row while naming no function attributed to its own path. Repaired by naming the
carrier each claim actually rests on — `_last_digest_date`/`_maybe_send_daily_digest`,
`_append_envelope`/`read_ledger`, and the four own readers of the organ log. The rung is
mutation-proven by its own fixtures, which assert it *fires* on constructed rows, so the green here
is not vacuity.

`publish_standing_reds.json` was undispositioned at HEAD **and** at origin — a red predating this
work, not caused by it. Dispositioned `real`/`guarded` from the module's own code:
`cycles_blocked` counts refusal cycles since the last observed landing and `record_landing` empties
`tests` wholesale, so one passing hook chain takes the published headline to zero with nothing
fixed. Guard tests already existed and are cited.

## What is next

1. **`tools/stale_copy_refusal`'s holder-work verdict should be two-directional.** A row where HEAD
   also supplies names is not holder work and its printed remedy is unsafe. The tool has the data —
   it already computes both symbol sets to write the remedy line.
2. **`isolate_hunks` cannot separate contributions inside a single replacement hunk**, and prints no
   warning when the hunk it offers to keep also reverts. On the door test that hunk was 728 lines.
3. **The NO OPINION bucket is 390 paths and is not a clean verdict**, as it says. At least one
   member (the dispositions register) was a live instance of exactly the defect. `.json` under
   `docs/design/` that a control reads is the cheapest place to start.
4. The three superseded working copies are backed up under `/tmp/lane0_merge_1883722/*.superseded_backup`
   for this session only; nothing in them was unique except the dead renderer, and the measurement
   above is the record.
