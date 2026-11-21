**Severity:** RECORDED · **Lane:** H_harness · **Atom:** `unminted` (direction `the-one-work-system-cut-over-staging-findings`)

# The one work system, increment 3: the staging findings are cut over to the item store (2026-11-21)

This is D9 step 3 of `docs/design/ONE_WORK_SYSTEM_DECISION_MAP_2026-11-20.md` for its first source.
It follows the side-by-side day pre-registered in
`docs/staging/records/SEAT_RECORD_THE_ONE_WORK_SYSTEM_INCREMENT_1_IN_SHADOW_2026-11-20.md`.

## The side-by-side day, graded against the predictions filed before it

Source: `python3 -m background.work_items --compare` over the shared tree's shadow log. It holds 565
draws, from 2026-11-20T13:42Z to 2026-11-21T13:01Z.

| | Predicted | Measured | Verdict |
|---|---|---|---|
| P1 `ladder_names_any_finding` | at most 10% | 133 of 565 (23.5%) | **wrong** |
| P2 `ladder_names_pick` | at most 5% | 96 of 565 (17.0%) | **wrong** |
| P3 distinct picks | at most 5 | 3 | held |
| P4 `SHADOW failed` lines | 0 | 0 real | held |

**Why P1 and P2 were wrong.** Both predictions rested on "the root holds no BLOCKING finding". At
08:57Z on 21 Nov one arrived:
`WORKER_FINDING_THE_STAYERS_CONTROL_IS_RED_ON_EQUAL_ARMS_AND_THREE_HOUSEHOLDS_CARRY_A_0_35_PERCENT_RAISE`.
From that draw on, rung 1c named it and so did `next_item()`. They agreed in 96 of the 97 draws
after it arrived. The other 37 rows that named a finding all fall on 20 Nov. In each, the Lane 0
delivery item was the seat's own choice, and it named a finding as its subject (the E7 roll-to-SVT
finding, the per-debt sale finding). Those draws do not answer "which finding is next", so they
are not a disagreement about the pick. The delivery lane is not yet a source of the store.

**P4, corrected by hand.** A grep for `ONE WORK SYSTEM SHADOW failed` finds 19 lines. All 19 are
this item's own drawn prompt, which quotes that grep string. The line the supervisor writes reads
`ONE WORK SYSTEM SHADOW failed (`. That form occurs 0 times in the live log and 0 times in the
archive capped at 2026-11-20T21:28Z.

**The cut-over test the record named.** P1 failed, so the test is the pair-by-pair reading.
- Where both named a finding, they agreed (96 of 96).
- Each of the three distinct picks is one the triage accepts:
  - the BLOCKING finding first;
  - D48's E2, which the 20 Nov blocking triage graded "real, rank 1, LATENT, stays at root";
  - the oldest LATENT, `ADVISOR_FINDINGS_REGISTER_ERROR_CHANNELS_ARE_INERT`, still open on §2b.

P4 holds. **The test passes, and the cut-over is made.**

## What this commit carries

- **`docs/work/cutover.yaml`:** `staging_findings: "on"`. The value is quoted on purpose: YAML 1.1
  reads a bare `on` as `true`, which `cutover_mode` read as `off`. That was caught on the first
  `--migrate --write`. `cutover_mode` now maps booleans as well.
- **`docs/work/items/`:** 179 items, one per classified finding at the root. By side: world 52,
  supplier 60, building 67. None refused. Re-running `--migrate --write` writes 0.
- **`background/work_items.py`:**
  - **The division of authority.** The store holds STATE. The document holds CONTENT: its title,
    its header's severity and lane, and where it now is.
  - **Moving a document no longer closes anything.** A document moved to `done/` is found there and
    stays open until its item is closed. A regraded header reaches the item on the next read.
  - **The lifecycle verbs:** `--done ID EVIDENCE`, `--obsolete ID REASON`,
    `--park ID REVISIT REASON` and `--reopen ID`.
  - **A finding filed after the migration is already an open item,** derived from its document. It
    is written the first time its state changes.
  - **A re-filed finding whose slug is already closed gets its own dated id.** Without that, the
    closed item would swallow it.
- **`background/supervisor.py`,** applied only when the flag is on and the root is the real root:
  - **Rung 1c** reads the open BLOCKING items rather than scanning headers at the root.
  - **The draw** leads with one line: the open count by severity, the item `next_item()` picks, and
    the verb that closes it.
  - **The root listing** drops every document the store holds.

  A test that points `STAGING_DIR` at a fixture keeps the old read. The first run without that
  guard mixed a fixture root with the live store, and `test_product_interleave` caught it.
- **CLAUDE.md "Orient first" and `staging-protocol` step 3:** findings are closed as items, never
  by moving the document.

## Measured on the real tree after the flip

- The draw's findings line reads 179 open: 1 BLOCKING, 150 LATENT, 28 RECORDED.
- It picks the stayers finding.
- The root listing falls from 161 names to 1, `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`, which
  carries no severity header. The HEAD-red register's clause still leads, as before.

## Not done here, and where it goes

- **Root documents without a `**Severity:**` header** are not items. The staging rooms still hold
  state for those, and `staging_rooms --check` still reads the root. This is the rest of D3 row 1.
- **The OPS9 gates** (`finding_severity`, `finding_classes`) still classify documents at the root.
  That is correct: they grade a document's header, which is content.
- **A new finding moved off the root before its state ever changes** leaves no item. As before the
  cut-over, the move is then its only record. The residue is named here rather than guarded.
- **The other sources** (continuations, the claims, `not_now`, the registers) are still to come,
  one at a time. Each migration deletes its own store.
- **D7** stays with the `for_the_director` row `the-one-work-system-s-decision-map`.
