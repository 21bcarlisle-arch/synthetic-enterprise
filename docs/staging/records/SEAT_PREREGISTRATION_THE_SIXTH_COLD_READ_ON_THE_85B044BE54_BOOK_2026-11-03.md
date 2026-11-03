**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the sixth cold read, on the 85b044be54 book (2026-11-03)

Written before any page is rendered for the reader and before the reader is briefed. DIRECTION row
`the-sixth-cold-read`. The reading that grades it will be
`records/SEAT_READING_THE_SIXTH_COLD_READ_ON_THE_85B044BE54_BOOK_2026-11-03.md`.

**The premise, re-measured.**
- The credited landing, 491243e096, is the blind tree's own fix and not a reading.
- 03e9332164 held the read until `/var/tmp/fresh-grade-85b044be54/ALLDONE` existed. It now exists.
- No cold read has seen this book. The read is still owed.

**Why 85b044be54 and not 08f267b666.**
- The item reads 08f267b666 only "if it has published".
- Its figures are `last_verified` in `site/data/publish_provenance.json` at 22:04Z.
- Its Explore pages were never built. Origin's `explore_cast.json` is still the 4ae8da9b0f cast, no 08f2 page tree exists
  under /var/tmp, and its hand re-publish was refused (f000ad71dc).
- So the reader reads 85b044be54, whose pages are under `/var/tmp/fresh-grade-85b044be54/tree/site/`.

**The book.**
- 1,293 accounts and 52,828 invoices. 752 households are in the picker.
- It carries the gas-volume build (34b764a0fd) and the one-serial-per-supply-point fix (6ef8f1b678).
- It does not carry a9e9128aa0, 1b709ac0e9 or 8cf2ecb744.
- Its grade is `SEAT_RECORD_THE_85B044BE54_BOOK_GRADED_AGAINST_BOTH_PREREGISTRATIONS_2026-11-02.md`: refused,
  with 9 unexcepted breaches on 4 rows, each traced in that record.

## Method

- **The reader's tree** is made by `tools/blind_worktree.py`: the book's Explore pages and cast, the ruling, and a
  brief that carries the rendered packet. It is checked clean before the reader starts. The reader is told to read
  `BRIEF.md` only.
- **The packet** is rendered with Playwright by the fourth read's route (`/var/tmp/fourth-read-scripts/render.mjs`),
  from the pages served on 127.0.0.1:8793.
  - Section A is every moment of the seven filled slots, plus the empty EV slot.
  - Section B is eight households drawn by `random.Random(20261103).sample(…, 8)`. They are drawn from the picker's
    752, less the 43 ids that appear in any earlier read's packet or record, less the 7 cast households (707 left):
    **OCC-924f5fe3f622, OCC-efcdf9ab970d, PROS-2016-0121, PROS-2017-0293, SYN-2016-498, SYN-2016-492,
    OCC-dbfb5a98d04d, OCC-6387bf64272a.**
  - No household is added by name.
- **The reader's trade** is a GB metering and settlement professional (MRA/REC, BSC, UNC and the gas conversion
  regulations, plus retail billing). The brief names no expected finding and asks no named question.
- **The known breach households are named here, to the grader only.** None is in the packet:
  - unexcepted: OCC-23ee23cb44e4, OCC-7e06d09fc108, PROS-2017-0336, PROS-2024-0010;
  - excepted: C6, PROS-2016-0263, SYN-2016-396, SYN-2016-565, PROS-2025-0106, SYN-2016-582;
  - the open debt survivors: PROS-2020-0191, PROS-2025-0013.
- **What counts as a new class:** an objection that the seat confirms in the record or in the page code, and that no
  earlier read's O/N list, open finding or domain-invariant row already names.
- **The three named checks, made by the seat after the read, over every page:**
  - (a) every gas page prints a volume and a conversion;
  - (b) every storage-heated (PC2) page bills Day and Night;
  - (c) no meter serial sits on two supply points.

## Predictions

| # | prediction | range |
|---|---|---|
| P1 | slots filled. This is known from the grade record, so it is a check, not a forecast | 7 of 8; EV empty |
| P2 | the reader grades the storage-heating slot (PROS-2017-0233), the first time it has been filled | valid |
| P3 | objections | 20–45 |
| P4 | new classes confirmed in the record or the code | at least one, because each of the five earlier reads found one |
| P5 | N10 and N11 (shared serial; gas held as a kWh register) recur as objections | no |
| P6 | named check (a): gas pages with a volume and a conversion | all of them, 0 without |
| P7 | named check (b): PC2 periods billed on one register | 0 on the pages read. Book-wide, only the known two (OCC-23ee23cb44e4, OCC-7e06d09fc108) |
| P8 | named check (c): serials on two or more supply points | 0 |
| P9 | the exit-test legs | leg one met in substance (0 untraced; 9 traced, not excepted, on this book); leg two MET; leg three NOT MET (follows P4), so the stretch does not exit |

P4 and P9 are written against our own thesis, as F11 asks. If P4 is refuted, the read meets leg three.

## Results

*(Filled in the reading, beside each prediction.)*
