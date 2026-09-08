<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none — this is a harness state, not domain understanding.

# Eleven byte-identical duplicates return to the staging root every few minutes, and the instrument built to catch it has been silent for two days

> **The title of this document overclaimed and the body is corrected below.** I first wrote that the
> duplicates "wedge every lane's commit". They do not wedge `surgical_land`, and I had three of my
> own landings in hand proving it while I wrote that sentence. The correction is kept here beside
> the claim rather than revised away. The filename is left alone because renaming it would break the
> class register that now names it.

## What was found

`background/finding_classes --check` read `check: FAIL (11 failures)`, all `TWO ROOMS`: a
preregistration present in both `docs/staging/` and `docs/staging/records/`.

Measured per pair rather than assumed:

| | root copy | `records/` copy |
|---|---|---|
| in the index | no (9 of 11 staged `D`) | no (untracked) |
| at `HEAD` | 9 yes, 2 no | none |
| at `origin/main` | 11 yes | none |
| **sha256 vs the other room** | **identical, all 11** | **identical, all 11** |

Every pair byte-identical. Each has a landed result or finding that consumed it — the switching-band
preregistration against `SEAT_FINDING_THE_SWITCHING_BANDS_OWN_PUBLISHER_DISAGREES...`, the VAT one
against `SEAT_RESULT_THE_ELECTRICITY_SVT_TABLE_IS_A_SECOND_HOME...`, the divisor one against
`SEAT_RESULT_THE_CAP_COMPOSITION_NOW_COVERS_ALL_33_PERIODS...` — so `records/` is the right room.

## THE CORRECTION: what this actually blocks, and what it does not

**It does not block `surgical_land`.** I ran three landings through that door during this tick and
all three passed `finding_classes` and failed on something else entirely (`symbol_landing_check`,
then two test reds). The reason is structural: `surgical_land` gates a **checkout built from HEAD
plus the pathspec**, and the `records/` copies are *untracked*, so they are not in that checkout and
the collision cannot exist there. `finding_severity` likewise exits 1 on a pre-existing
FALSE-DISCHARGE in another lane's document, and landings pass anyway.

**It does block the working-tree commit path** — `process_run_complete`'s publish, which is exactly
what `SEAT_FINDING_THE_REPAIR_THAT_CLEARS_THE_PUBLISH_WEDGE_RUNS_45_MINUTES_BEFORE_THE_GATE_THAT_
READS_IT_2026-09-04` measured, and why `_clear_two_rooms_before_commit()` was added there.

**So the "door asymmetry" is real but it is not a defect.** `tools/surgical_land.py` imports
`staging_root_resurrection_watch` and not `staging_two_rooms_repair`, and that is *correct*: it
does not need the repair, because its gate cannot see the duplicate. Wiring the repair into it would
have been a mechanism built against a failure that door cannot have. I nearly did it.

## The part that is a live defect

**The restoration is continuous, and its instrument is blind to it.** I cleared all eleven three
times during this tick. Each time they came back within minutes:

- All eleven restored at **one shared mtime, 05:03:48** — a single atomic operation, the same
  signature `WORKER_FINDING_ARCHIVED_RUN_MARKERS_RETURN_TO_THE_STAGING_ROOT..._2026-08-20` recorded
  ("ten files, one shared mtime").
- Cleared again; `--check` went `PASS`. Within two minutes, `FAIL (11)` again.

`docs/observability/staging_root_resurrection.jsonl` — the instrument built for precisely this —
was last written **2026-09-06T22:57:42**, two days earlier. Its own last entry carries the label
`"surgical-land gat..."`, so the bracket has worked before and does write to the shared log. It
recorded none of today's three restorations.

**What I cannot say:** what performs the restoration. The index state (`D ` staged deletion plus an
untracked file present at the same path) is not what `staging_two_rooms_repair._git_rm` leaves — that
runs `git rm -f`, clearing index and disk together. Something restores the disk copies afterwards,
repeatedly, on a period of roughly minutes. I have not established what, and I have written no guard
against a cause I cannot name.

## What is next

1. **Find the writer.** It is on a short period, so it is cheap to catch: watch `docs/staging/` and
   record the writing process, rather than censusing before-and-after a window that keeps missing it.
   The existing bracket is the wrong shape for a periodic writer — it only looks either side of a
   gate.
2. **Ask why the bracket is silent** before adding anything beside it. Either its census misses this
   route, or these restorations fall outside every bracketed window — both are answerable by
   measurement, and one of them means the instrument is fail-silent, which is the killer category.
3. **Do not wire the repair into `surgical_land`** — see the correction above.

— Delivery seat, 2026-09-08.
