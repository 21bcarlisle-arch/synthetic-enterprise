**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `founders-slope-unattributed-residue`

# The founders-only slope's live-but-unreturned 0.15 MB per settled customer-year, named by type

Follows "Open (1)" in `SEAT_FINDING_THE_FOUNDERS_SLOPE_RESIDUE_2026-10-07.md` (`b9dde81d0`). That
finding settled the item's own question: the residue is **not a dropped second copy of the
records**. It split it into 0.245 pymalloc slack (the freed fabric trace), 0.075 glibc free and
0.10 transient at the peak, and left **0.15 live, not returned, not named**.

## Disposition at draw (2026-10-07 23:30 BST)

- This draw is the same id as the landed work. The duplicate-work note named this id itself, and
  `ps` showed no rival probe. `b9dde81d0` is on origin. Its commit says the 0.15 was "handed on as
  a seat continuation", but `seat_continuation --list` holds no successor; the only live entry is
  this id. **The handoff was never written**, and that is why the item came back. Open (1) is
  therefore the remainder, and this turn takes it.
- A prior tick had started it. `/var/tmp/scale-shape-ctl/ctl0_typesize.py` exists; `tsize40.json`
  finished at 23:23, and the 160 leg's log stops at 2019-11 (23:27) with no JSON and no process
  alive. It died with its tick. Since the 40 leg ran, B8 has landed 375 lines in `company/` and
  `simulation/` (`fa3ea8cdb..d88b078bb`), so **both legs are rerun together at `d88b078bb`** and the
  old 40 leg is not differenced against a new 160 leg.
- The continuation the draw named (`w2-20-publish-the-head-arms…`) is unrelated W2_20 work.

## Pre-registration (written before either leg)

Instrument: `ctl0_typesize.py N OUT`, unchanged. Runs at the return of `run_phase2b`, after
`gc.collect()`. It walks everything reachable from the result, then labels each GC-tracked object
NOT reachable from it by type: an instance `__dict__` by its owner's type, a list by its first
element's type. Each untracked leaf is charged once, to the first container that refers to it.
Slope = (160 − 40) / 332.8 settled customer-years.

- **P1.** The unreturned total's slope is **0.10–0.25 MB/scy**. The allocator reading was 0.151;
  getsizeof misses allocator overhead and charges shared leaves only once.
- **P2.** The garbage collector runs first, so `ConversationLeg` rises by **fewer than** the
  19,608 counted without a collection. (At 40, every leg alive was cyclic garbage.)
- **P3.** At least **half** of the slope is company-side conversation and ledger state
  (`ConversationLeg`, `LedgerEvent`, their dicts, and the lists and floats they own).
- **P4.** The 202k `list of float` at 40 (54 MB) is fixed-cost market or weather data; its slope
  is **< 0.02**.

Done means: the 0.15 is named by type to within 0.05, or the instrument is shown unable to name it,
with the reason. The answer to whether the trace is alive at the peak (Open 2) is handed on.

## Result, leg pair 1 (`tsz2_40.json`, `tsz2_160.json`, both at `d88b078bb`, 105 s and 255 s)

The unreturned total reads 978.2 → 1,174.7 MB, a slope of **0.590**. 190.9 MB of that is one label,
`builtins.set`, whose count is unchanged at 5,722. **It is the instrument's own `returned` id-set**,
alive when `gc.get_objects()` runs. For 883,215 and 3,993,460 ids it predicts 59.0 and 249.9 MB;
the label reads 61.8 and 252.7, and the 2.8 MB left over is the same in both legs. The prior
finding's method note (an id-set grows with the book) applies to this instrument too, and the
earlier tick that wrote it did not exclude its own set.

With the id-set removed: **919.2 → 924.8 MB, slope 0.017.** The only other label that moves is
plain `dict` (+1,919, +5.4 MB). No `ConversationLeg` or `LedgerEvent` label reaches 0.2 MB in either
leg after `gc.collect()`.

- **P1 fails** (0.017, against 0.10–0.25). **P2 holds**: those classes are below the reporting floor.
  **P3** cannot be graded, because there is no slope to share out. **P4 holds**: no `list of float`
  slope.
- The GC-tracked objects the result does not return do **not** carry the 0.15. The instrument has a
  stated blind spot: dicts and tuples holding only atomic values are untracked, and it charges them
  one level deep, not their contents. So 0.017 is a floor on unreturned Python state, not a total.

## Pre-registration, leg 2 (written before the run)

Hypothesis: the 0.15 is **allocator overhead on the returned book itself**. `getsizeof` reports
requested bytes. pymalloc rounds every block up to 16 bytes (a float asks for 24 and gets 32), and
the key tables of dicts over 512 bytes go to glibc and carry chunk headers. In the prior finding,
"live minus returned" was therefore allocator bytes minus `getsizeof` bytes: two different units.

Instrument: `ctl0_recpickle.py` pickles the real `all_records` at 40 founders. A fresh process loads
it 4 times (131,028 records, close to the 121,551 added from 40 to 160). It reads pymalloc allocated
blocks plus glibc `uordblks` and `hblkhd` before and after, and the deep `getsizeof` of the copies.

- **P5.** Allocator bytes ÷ deep `getsizeof` for real records is **1.15–1.35**. On the book's 0.49
  that is 0.07–0.17 MB/scy, enough to close most or all of the 0.15.
- **Void if** the loaded copies' deep size per record is not within 10% of 1.37 KB (pickle has
  dropped or added sharing).

## Result, leg 2 (`recpickle_load.json`)

| | value |
|---|---|
| real records loaded (4 × 32,757) | 131,028 |
| deep `getsizeof` | 188.8 MB, **1.475 KB/record** (ctl0: 1.37, so 7.7% off and **not void**) |
| pymalloc allocated delta | 119.1 MB |
| glibc in use delta (the dicts' key tables, over 512 B each) | 98.8 MB |
| mmap delta | 0.3 MB |
| **allocator ÷ getsizeof** | **1.156** |

**P5 holds, at its lower edge.** Applied to the returned deep slope (0.538), allocator overhead on
the returned book is **0.084 MB/scy**.

## The 0.15, named

| component | MB/scy | how known |
|---|---|---|
| allocator overhead on the returned book (block rounding, glibc chunk headers) | **0.084** | leg 2, real record shape |
| unreturned GC-tracked Python state | **0.017** | leg pair 1, id-set removed (a floor) |
| still unnamed: untracked leaves below one level, or memory outside Python objects | **0.050** | remainder |
| **live minus returned (prior finding)** | **0.151** | |

Done-means is met at its edge: named to within 0.05. **More than half of the 0.15 was a units error.**
"Live" was read in allocator bytes and "returned" in `getsizeof` bytes, and their difference is
mostly the book's own overhead, not a second population.

## What this changes

- **The founders-only slope is now about 0.95 owned by the book.** The records take 0.49 by
  `getsizeof`, 0.57 with allocator overhead. The freed trace's pymalloc slack is 0.245, glibc free is
  0.075, and the transient at the peak is 0.10. Only ~0.07 is anything else.
- **Narrowing the records is the lever, with a sharper aim.** 45% of a record's allocator bytes
  (98.8 of 218.2 MB) are dict key tables in glibc. A record that is not a 33-key dict (`__slots__`,
  a tuple row, or columnar storage) removes most of that, as well as narrowing the values.
- **Method, a second time in one day:** an instrument that keeps an id-set alive while it censuses
  `gc.get_objects()` counts itself. And a difference between an allocator reading and a `getsizeof`
  reading is a difference between units.
- **Still open, handed on:** whether the fabric trace is alive at the RSS peak (prior Open 2). That
  decides whether a trace layout above 512 bytes per year would move the *peak*.
