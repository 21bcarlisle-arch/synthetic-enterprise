**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The payment-belief harness detects late DDs the world no longer has (2026-10-28)

**What changed.** The world now collects a DD on its date or returns it
(`arrears_engine.A_DD_IS_NEVER_LATE`; knowledge: `payments_and_direct_debit_2026-10-25.md`, "A DD is
never late"). Before this, a stressed DD paid 14 to 90 days late, and that lateness was impossible.

**What it did to the H27 harness.** `tools/couple_w2_11_d5.py` builds its calibration book through the
world's `generate_payment_event`. On the corrected world, 14 of its tests go red; on origin all 623
pass. The reds are in the detection dimension:
- the drift register (-1d no longer moves the reading);
- the counted-population register, at (14, 23);
- the complement-of-truth and never-flaggable denominators, which no longer differ fivefold;
- the 4dp `note` and `gap-val` render sites, which the scoring no longer produces;
- the door walk.

All of these were measured on a book where DDs are late.

**What was done.** The harness declares its book's DD lateness as scaffolding,
`HARNESS_BOOK_DD_NEVER_LATE = False`, with the same status as `HARNESS_BOOK_DD_FAILURE_PROB` and the
same precedent (the 2026-10-09 failure-level correction). Its two "published books" also drive
the shipped live triad, which draws through the world's switch. `_publish_one_book` holds the
switch at the book's value for that drive, because on the corrected world the two all-HIGH books give
one detection figure to 4dp (0.004944 and 0.004938), and the render-site walk cannot tell a render from
a constant. So its figures still describe the instrument on that book, not the world, and no harness
figure moved. The live triad's own figures on a run DO move: `test_live_payment_triad` is re-pinned,
with detection going from 0.0194444444 to 0.0049435028.

**What is open.** The question is what the company's detection instrument should be graded against,
now that the world's DD is collected or returned. On the world's own book, the "late" signal comes only
from pay-on-receipt payers and from returns followed by a later settlement. Re-measure the detection
dimension, its registers and its door on a book with `HARNESS_BOOK_DD_NEVER_LATE = True`. Then either
re-pin to that book or state why the harness keeps the old one. Erring against our own thesis, the
instrument's published detection skill should be presumed overstated for DD payers until then.
