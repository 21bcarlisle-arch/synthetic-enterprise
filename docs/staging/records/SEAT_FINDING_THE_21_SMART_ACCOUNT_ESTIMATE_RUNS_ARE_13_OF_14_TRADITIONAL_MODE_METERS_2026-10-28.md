# The 21 runs of seven estimated bills on smart-read accounts: 13 of 14 accounts are smart meters in traditional mode

**Severity:** info (the flags are the model working as designed; one account unexplained; one real gap on the page)
**Book:** `/var/tmp/fresh-run-out-129e7de698` run, ledger `/var/tmp/third-read/ledger.json`, 1,293 accounts.
**Probe:** `/var/tmp/mt_probe.py` (labels from `meter_types_billed`, d575b53d2b's helper).

## What was measured

With the meter type taken from the reads the bills were cut on, `INV_SMART_METER_BILLED_ON_ITS_OWN_READS`'s
account leg flags **21 runs on 14 accounts** (7+ consecutive estimated bills, first bill excluded).
It reproduces the count in the work item exactly. The world's `meter_read_log` labels every one of
these reads `smart`, status `estimated`, so the label and the reads agree (N8 holds); the runs are not a
labelling fault.

## Cause (diagnosis only: this uses the world's draw, which the company cannot see)

`simulation.meter_reads.is_not_in_smart_mode(customer_id, commodity)` is a per-household, per-fuel draw
made once (DESNZ Q4 2024: 6.8% of electricity, 14.2% of gas smart meters). Of the 14 flagged accounts,
**13 are in traditional mode in the world** (4 of 5 electricity, 9 of 9 gas). Smart accounts in the book:
159 electricity (10 in traditional mode), 123 gas (16 in traditional mode). So the draw produces 26
traditional-mode accounts and the account leg's flag finds 13 of them, which is what a sticky state with
the occasional customer read breaking a run would give. The row's own severity text anticipated this:
"a single meter may lawfully sit in traditional mode for a year; the book share is what grades the supplier".

**Not explained:** `PROS-2021-0383` (electricity). Not in traditional mode by the draw, never changes
meter type, yet 14 estimated bills from 2022-11 to 2023-11 with one actual on 2022-10-31 before them.
Not traced here. Prediction filed before tracing: a call site that passes a different `commodity` or
`half_hourly` into `is_communicating` than the draw used.

## What it means for the row

1. The account leg's flag is correct and should stay a flag. It would be wrong to turn it into a breach.
2. The page prints "Smart" for a meter that has been in traditional mode for 13 months, and the
   supplier's record has no field for the mode. A real supplier sees the loss of comms (DCC/WAN alerts),
   so this is a representation gap rather than an epistemic breach. Not built here.
3. The blind row for the meter type (`INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT`) cannot split "smart in
   traditional mode" from "traditional", because neither the bill nor the raw export carries it.

## The blind row, and what the runner can and cannot grade of it

`INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT` was written by an agent forbidden to read
`generate_customer_data.py`, `generate_customer_sample.py`, `site/explore/index.html` or `simulation/`,
from the smart-metering knowledge pages only. The row is verbatim from `/var/tmp/blind_meter_row.yaml`.

- **Leg 1 (panels agree), graded.** `load_printed` now reads the sample record's `smart_meter` and the
  cast's "Smart meter" truth rows beside the header. The cast and sample share one source today, so on a
  correct book it is CLEAN by construction; its job is to go red if a panel re-acquires its own record.
  Against the committed `site/data` (built before d575b53d2b) it reads 256 breaches, all sample "Not
  recorded" under a header that prints Smart/Traditional: stale pages, not the fresh book. The live gate
  grades the pages written earlier in the same cycle.
- **Leg 2 (agrees with the reads billed), reachable but not live.** The published page carries no meter
  type per bill, and the world's `meter_read_log` is not something the runner may read in the gate. The
  evaluator grades `printed["meter_of_reads"]` where a harness supplies it and is silent otherwise.
  Closing it needs the supplier-visible meter type on the bill record, which a real MPxN record has.
- **Leg 3 (day-clock sentence), not graded here.** The sentence is drawn by the browser from the header
  field; it belongs to the site door test.
