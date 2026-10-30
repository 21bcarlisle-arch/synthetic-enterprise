**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The fifth cold read finds one meter serial on up to 34 supply points, because the serial is an order-blind checksum of the account id (2026-10-30)

**Source.** The fifth cold read's O6, on the 3dc5a92948 book
(`docs/staging/records/SEAT_READING_THE_FIFTH_COLD_READ_ON_THE_3DC5A92948_BOOK_2026-10-30.md`, class N10).
It is BLOCKING because it is one of the read's two new classes. The correctness stretch cannot exit while
every page carries it.

**What the page prints.** Meter M00062062 appears on two bills:
- PROS-2023-0291, "1 Oct 2024 – 31 Oct 2024 · meter M00062062 · ESTIMATED READ", supply point 15… (North East);
- OCC-7c2500b09b7b, "1 May 2018 – 31 May 2018 · meter M00062062 · ESTIMATED READ", supply point 10… (Eastern).

A serial names one physical meter, so it cannot sit on two supply points in two distribution regions.
The reader also read one register "running backwards" across the two accounts. That follows from the
shared serial, not from either account's reads.

**How wide** (`/var/tmp/fifth-read-scripts/serials.py` over the rebuilt pages):
- The 1,293 pages carry only **127 distinct serials**.
- 96 of those serials sit on more than one supply point, from 2 up to 34, and every one of the 96
  spans more than one distribution prefix.
- 1,249 accounts carry a shared serial.
- M00062062 alone is on 14 supply points across 18 accounts.

**Confirmed in the code.** `tools/generate_billing_ledger._meter_serial` mints the serial as
`sum(ord(c) * 31 for c in account_id + commodity) % 10**8`. A sum of character codes does not depend on
character order, and the ids share one format, so the sums fall into a narrow band and collide.

The docstring promises "deterministic per account+commodity". The function is deterministic, but it is
not unique. It is keyed through `supply_point_of`, so successive occupants correctly share a serial,
and that part stays right.

**Why no row caught it.** `INV_GAS_SINGLE_REGISTER`, `INV_READ_MONOTONIC` and
`INV_SERIAL_REGISTER_COUNT_STABLE` each key on `meter_serial`, but each takes it as given within an
account. No row grades that one serial maps to one supply point. A shared serial can also make a
serial-keyed row group reads from different meters. Whether the runner groups per account or per
serial is not checked here.

**What closes it.**
1. A row written blind from the knowledge layer: `INV_METER_SERIAL_ONE_SUPPLY_POINT`, in the reading's
   blind-row file and landed with it. No knowledge page covers meter serial numbers, so the row is a
   stated belief (strong logic), and its GAPs are named in the row.
2. A serial minted unique per supply point and meter, such as a collision-free mapping of the supply
   point id, or a registry-held serial. A meter exchange gets a new serial.
3. A test that reds on origin: two supply points whose ids are permutations of each other get distinct
   serials.

Not done here: the item is the reading.
