**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `founders-slope-unattributed-residue`

# The founders-only slope's unattributed ~0.33 MB per settled customer-year: slack, transient, or a second copy?

Follows "Open" in `SEAT_FINDING_THE_FOUNDERS_ONLY_SLOPE_AT_CURRENT_CODE_2026-10-07.md` (that file is
untracked on the shared tree; its numbers are quoted here so this one stands alone). At origin/main
`9bbc0e751`, founders-only, `--end 2019-12-31`, budget 0.0, the 40→160 peak-RSS slope is **1.11 MB
per settled customer-year** (332.8 added): `all_records` 0.49, fabric trace 0.26, treasury 0.03,
**unattributed ~0.33**.

## Premise, checked at draw (2026-10-07 ~21:55Z)

- Worktree HEAD equals origin/main (`fa3ea8cdb`); no commit since `9bbc0e751` touches `simulation/`
  (upstream was docs and the W2_39 landing).
- **Duplicate-work note:** the live claim it named is this draw's own id (my process was 9 s old;
  no rival probe or `surgical_land` in `ps`). Not a duplicate; carried on.
- **Already in hand before any run:** the ctl0 legs' own phase marks. Peak minus end-of-phase-2b
  RSS is 26.6 MB at 40 and 55.3 MB at 160, so a transient freed before 2b returns accounts for only
  **0.09 MB/scy** of the peak slope. The end-of-2b RSS slope is (1,983.1 − 1,641.1) / 332.8 =
  **1.03**. So about 0.25 of the residue is still resident when 2b returns.

## Pre-registration (written before either leg)

Instrument: `/var/tmp/scale-shape-ctl/ctl0_residue.py N OUT [--trace]`, everything read at the
return of `run_phase2b`. Untraced legs: RSS, glibc `mallinfo2`, pymalloc arena stats, deep
`getsizeof` over the whole returned result (shared objects once). Traced legs: `tracemalloc` (depth
3) from before the first simulation import; snapshot by line; every object reachable from the result
attributed to its allocation line; unreturned-by-line = traced − returned. A **planted control**
(~20 MB of record-shaped dicts, held and never returned) must surface at the probe's own plant line
at roughly its deep size, or the traced leg is void.

- **R1, the book.** 37 / 157 accounts, 89.7 / 422.5 settled customer-years, 32,757 / 154,308
  records, exactly. Otherwise void.
- **R2, untraced end-of-2b RSS slope:** 0.95–1.10 (reproduces 1.03).
- **R3, slack** (pymalloc available blocks + unused pools + glibc `fordblks`), slope:
  **0.05–0.20**. I expect slack NOT to be the main residue.
- **R4, live unreturned** (traced): slope = (trace, if it is held but not returned: ~0.26) + X.
  I predict **X between 0.05 and 0.25**, and that the line carrying most of X is named by the
  snapshot.
- **R5, returned deep size slope:** 0.50–0.60 (records 0.49 + treasury 0.03 + the small keys).

**Decision rule.** Residue is *allocator slack* if R3 ≥ 0.2 and X < 0.1. It is *a held second
copy* if X ≥ 0.2 with a line named. Between, it is mixed and I give both shares.

## What the first legs did to the plan (written before the rerun)

- **Untraced legs, first run, are partly void.** They read the allocators *after* the deep walk,
  and the walk's own `seen` id-set (an mmapped table) and its int objects (pymalloc) grow with the
  book. The 40-founder garbage census (`ctl0_gcsave.py`, below) found `hblkhd` already at 17.7 MB at
  return, so the 49.7 / 145.7 MB the legs read were mostly the instrument. RSS and the returned deep
  size are still valid, because they were read before or independent of the walk.
- **Traced legs abandoned, not failed.** tracemalloc at depth 3 slowed the 40-founder leg more than
  15× (35 min without flushing 8 KB of stdout; the untraced leg takes 2 min). The two legs held
  ~7 GB and pushed the box to ~400 MB free, which in turn depressed the concurrent untraced legs' RSS.
  R4 is therefore **not tested by a line-level snapshot**. The live-minus-returned difference from
  the allocators is the substitute, and it cannot name a line.
- **Cyclic garbage at return, 40 founders:** 16,391 objects, ~2 MB (company billing / conversation
  objects). It is not the residue.

Rerun: allocators read before the walk, and RSS split into anon and file-backed, with a 0.5 s
sampled anon peak. Both legs run concurrently and nothing else of mine runs.

- **R2′.** Anon RSS at return, slope 0.85–1.10.
- **R4′.** Live (pymalloc allocated + glibc `uordblks` + `hblkhd`) minus returned deep: slope
  **≤ 0.15**. From correcting the void legs I expect live ≈ 0.6 against returned 0.54.
- **R6.** If R4′ holds, the gap between anon RSS and live is allocator slack (pymalloc free pools
  and arenas, glibc `fordblks`), and I predict it is **0.2–0.45 MB/scy**: memory freed before
  return, the fabric trace among it, that the allocators keep resident.

## Result

Outputs in `/var/tmp/scale-shape-ctl/`: `res2_u40.json`, `res2_u160.json` (the clean rerun),
`alive40.json`, `alive160.json` (`ctl0_alive.py`: `gc.get_objects()` census at return), and `gc40.json`.
Both legs read budget 0.0, with 32,757 / 154,308 records and 89.7 / 422.5 settled customer-years,
exactly as ctl0 (**R1 holds**).

Per settled customer-year, slope across 332.8 added (`res2`):

| quantity | 40 | 160 | slope |
|---|---|---|---|
| `ru_maxrss` | 1,662.5 | 2,033.3 | **1.114** (ctl0: 1.11, reproduced) |
| anon RSS at return | 1,493.7 | 1,830.5 | **1.012** |
| allocator-committed (pymalloc arenas + glibc arena + mmap) | 1,486.2 | 1,821.9 | 1.009 |
| returned deep size | 50.6 | 229.6 | **0.538** |
| live (pymalloc allocated + glibc in use + mmap) | 1,250.5 | 1,479.6 | 0.688 |
| live minus returned | | | **0.151** |
| pymalloc arena slack (arenas − allocated) | 137.6 | 219.3 | **0.245** |
| glibc free (`fordblks`) | 98.1 | 123.0 | **0.075** |

Anon RSS minus allocator-committed is 7.5 / 8.6 MB. **The allocators account for the whole resident
heap**, and file-backed RSS is flat (134.9 / 134.7).

`ctl0_alive` at return, both legs: **0 `FabricDemandSeries` and 0 `array('d')` alive** (21 and 60
were built). **Record-shaped dicts alive = `all_records` + 5** (32,762 / 154,313). No other large
list holds record objects.

**The founders-only slope, decomposed:**

| component | MB/scy | status |
|---|---|---|
| returned: `all_records` 0.49 + treasury 0.03 + small keys | 0.54 | owned, live |
| fabric trace: built, used, **freed before return**; its pools stay inside pymalloc arenas pinned by live neighbours | 0.245 (vs 0.26 traced bytes) | live at build, slack after |
| glibc free heap | 0.075 | slack |
| live, not returned, neither records nor trace | **0.15** | **line not named** |
| above return level at the peak (transient) | 0.10 | transient |
| **sum** | **1.11** | |

- **R2 / R2′.** The first run read 0.92, because the box was at ~400 MB free under my own traced
  legs and that run's RSS sat 120 MB below its allocators at 160. Clean, it reads 1.012, so **R2′
  holds**. The first run's RSS is void. Swap is the likely cause, but I did not measure it for that
  run.
- **R3 fails.** Slack is 0.32, not 0.05–0.20. But 0.245 of it is the freed fabric trace, which the
  earlier finding already counted as owned.
- **R4′ holds at its edge** (0.151 against ≤ 0.15). **R5 holds** (0.538). **R6 holds** (0.32).
- **Decision rule: mixed, and not a dropped second copy of the records.** The earlier finding's
  "unattributed ~0.33" is about 0.15 of live company or run state that the result does not return,
  about 0.075 of glibc free heap, and about 0.10 transient at the peak. The 0.15 cannot be named by
  line: the tracemalloc legs were not viable on this box.

## What this changes

- **Narrowing the records is still the lever, and it is safe to aim at.** There is exactly one
  copy of them. A narrower record acts on 0.49 of the 1.11, and nothing else holds a hidden 0.3.
- **Freeing the fabric trace earlier returns nothing to the OS.** It is already freed before return,
  and its memory stays as pymalloc arena slack, pinned by interleaved long-lived objects. A layout
  that put each trace-year in one buffer over 512 bytes (glibc or mmap, which can be returned) would
  change that. Whether it moves the *peak* depends on whether the trace is alive at the peak, and
  **that is not established here**.
- **Method:** a peak-RSS slope read while other heavy jobs are running is not comparable. 0.88 and
  1.11 came from the same code. Read allocator-committed memory beside RSS, and check that they
  agree before trusting a slope. A deep `getsizeof` walk must be read *after* the allocators: its
  own id-set grows with the book.
- **What the type census (top 20 by count, `alive*.json`) already says about the 0.15.** Dicts
  rose by 160,865 from 40 to 160, of which 121,551 are the records. `ConversationLeg` rose by 19,608
  and `LedgerEvent` by 15,211 (company side), and their instance dicts are most of the other ~39k.
  Lists rose by 74,772. At 40 founders, every `ConversationLeg` alive at return was cyclic garbage
  awaiting a gen-2 collection (`gc40.json`: 5,270 in `gc.garbage`, ~2 MB shallow). By count the
  0.15 looks like company-side conversation and ledger objects plus unexplained lists, but **sizes
  are not measured**, so I do not claim it.
- **Open, ranked:** (1) Name the 0.15 by size: deep `getsizeof` per type over `gc.get_objects()`
  at return, differenced 40→160, run as an untraced pair of about 7 minutes with no other heavy
  job running. (2) Is the trace alive at the RSS peak? The sampled-peak timestamp against the trace's
  build and free will tell.
