**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `fabric-trace-held-per-window-year-is-the-founders-slope`

# Does the fabric trace own the founders slope, and does storing it as arrays remove it

Follows "What is still open" in
`SEAT_FINDING_THE_TERM_LOOPS_MEMORY_THAT_SCALES_WITH_ACCOUNTS_IN_THE_BOOK_2026-10-07.md`.

## Premise, checked when this was drawn (2026-10-07)

- **Premise:** live. HEAD equals origin/main (`3e752c8f8`), and `build_fabric_series` still stores
  each day as three `list(...)` copies of 48 floats.
- **Duplicate-work note:** the live claim it named is this draw's own id. No rival seat or
  `surgical_land` process was running.
- **Consumers checked before the change.** Every reader of `gross_electricity_kwh`,
  `pv_generation_kwh` and `gas_kwh` indexes, sums, zips, takes `max`/`min`/`len`, or copies the day
  with `list(...)`. No reader mutates a day, serialises it to JSON, or checks it is a `list`.
  `fabric_shape_fn` already returns a fresh `list`, so settlement never sees the storage type.

## Pre-registration (written before either control run)

Instrument: `/var/tmp/scale-shape-ctl/scale_series_probe.py`. It is `scale_series_orig.py` with one
addition: it wraps `run_phase2b.fabric_providers_for_book` and records how many traces it returns,
how many trace-days they hold, and their deep size in bytes (containers plus float objects, floats
de-duplicated by `id` within each trace). The control is the same as before: `--founders 40 --end
2019-12-31 --no-extract`. There are two arms and one variable. **A** is HEAD's code. **B** is HEAD
plus `array('d')` days in `build_fabric_series`.

The reference is `fix40` at the same code as A: peak 2,397.4 MB; 112,805 records; 178 accounts;
308.8 settled customer-years; final treasury 284,184.7176…

- **P1, bytes per trace-year as lists (arm A).** Between 1.2 and 1.9 MB. This is a reading of the
  layout: 3 × (a 440-byte list plus 48 floats of 24 bytes) per day, plus the key and the dict
  slots. That comes to about 5 KB a day.
- **P2, bytes per trace-year as arrays (arm B).** Between 0.45 and 0.65 MB. That is 3 × 448 bytes a
  day plus the same key and slot overhead.
- **P3, does the trace own the slope.** Arm A's total trace bytes divided by 308.8 settled
  customer-years falls between 0.9 and 1.8 MB. **Refuted if it is below 0.7 MB.** That would mean
  the trace is too small to be the slope's owner. One book size cannot show a slope, so P3 checks
  that the trace is the right size to be the slope. It does not prove the slope is the trace.
- **P4, peak.** B's peak is lower than A's by between 55% and 85% of (A's trace bytes minus B's
  trace bytes). It is below 100% because pymalloc does not always return freed arenas. It is above
  55% because the traces are all alive together at the peak.
- **P5, value.** B's settled book is identical to A's: records, accounts, customer-years, and the
  final treasury to the last digit. **Any difference refutes "a change of representation, not of
  value"**, and the change does not land.

## Result

The two arms ran at the same time on one box. Each one's peak RSS belongs to its own process, so
running them together does not change either peak. It does affect the wall times, which are not
graded. The output files are `/var/tmp/scale-shape-ctl/armA40.json` and `armB40.json`.

| | A (lists, HEAD) | B (`array('d')`) |
|---|---|---|
| traces held / trace-years | 72 / 288.0 | 72 / 288.0 |
| trace bytes (deep) | 373.3 MB | 161.4 MB |
| MB per trace-year | 1.296 | 0.561 |
| RSS right after the trace build | 2,098.8 MB | 1,802.9 MB |
| peak (`ru_maxrss`) | **2,388.2 MB** | **2,099.9 MB** |
| records / accounts / settled customer-years | 112,805 / 178 / 308.8 | 112,805 / 178 / 308.8 |
| final treasury · register points · events | 284,184.71764401573 · 68,263 · 49 | identical |

- **P1 holds:** 1.296 MB per trace-year, inside 1.2 to 1.9.
- **P2 holds:** 0.561 MB, inside 0.45 to 0.65.
- **P3 holds, with its stated limit:** 373.3 MB over 308.8 settled customer-years is 1.21 MB, inside
  0.9 to 1.8 and about 90% of the 1.35 MB slope. **A correction to the inherited reading:** the
  traces do not belong to "every premise that settles". They belong to the 72 fabric-eligible
  electricity premises, out of 178 accounts. Their 288 trace-years happen to be close to the
  308.8 settled customer-years. Whether that ratio holds at 160 founders is the open question that
  would turn "the right size" into "is the slope".
- **P4 is refuted, on the high side.** The trace shrank by 211.9 MB and the peak fell by
  288.3 MB, which is 136% of the shrink. I predicted 55% to 85%. My model of the error was wrong
  in direction: I assumed freed memory would only partly come back, but the long-lived float
  objects in A seem to pin pymalloc arenas, along with the transient objects allocated between
  them. That is a guess. The deep-size probe counts only live objects, so it cannot see the
  pinned arenas. The RSS gap after the build (296 MB) matches the peak gap, so the whole saving
  happens during the trace build and lasts to the peak. **I cannot yet say** what the extra
  ~76 MB is.
- **P5 holds:** every settled figure is identical, so this is a change of representation and not
  of value.

**Landed:** `build_fabric_series` stores each day as `array('d')`. The 40-founder control's peak
drops 12%, from 2,388 to 2,100 MB. The 107 module tests and 19 dependent tests pass unchanged.

## What is still open, and handed on

1. **Is the slope the trace?** Run the same probe at `--founders 160`, which the earlier finding
   measured at the old code. If trace-years per settled customer-year stays near 0.93, the slope
   is the trace. B then predicts a slope of about 0.6 MB per settled customer-year, or lower
   given P4's excess.
2. **Remedy 2** from the predecessor finding (start a won leg's trace a year before it joins) is
   still unmeasured and still needs care with `OWN_READS_FIRST_YEAR`.

**Correction (2026-10-07, after the 160-founder run):** item 1 is answered *no*. At 160 founders
there are 75 traces and 300 trace-years, against 72 and 288 at 40, while settled customer-years
rise from 308.8 to 485.9. Converted back to lists, the trace contributes 0.088 MB per settled
customer-year to the slope, not about 1.2. P3's "right size" at 40 founders was a coincidence of
one book size. See `SEAT_FINDING_THE_FABRIC_TRACE_AT_160_FOUNDERS_2026-10-07.md`.
