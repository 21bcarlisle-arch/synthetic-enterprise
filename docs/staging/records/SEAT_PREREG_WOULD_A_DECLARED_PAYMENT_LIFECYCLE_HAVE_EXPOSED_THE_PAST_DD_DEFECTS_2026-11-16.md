**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: would a declared payment lifecycle have exposed the past DD defects? (2026-11-16)

*Filed with the lifecycle (`company/compliance/payment_lifecycle.yaml`) and its knowledge section
(`docs/market_research/payments_and_direct_debit_2026-10-25.md`, "The payment lifecycle, stage by
stage"), in the same commit, before any finding below is opened. Ruling:
`docs/staging/advisor/done/DIRECTOR_RULING_EP11_REFRAME_APPROVED_AND_TEST_A_DECLARED_PAYMENT_LIFECYCLE_AGAINST_PAST_DD_DEFECTS_2026-11-16.md`, part 2.*

## The sample, fixed by rule

Every finding file tracked under `docs/staging/` (root, `done/`, `records/`) whose name matches
`(SEAT_|WORKER_)?FINDING_*` and contains `DIRECT_DEBIT`, `_DD_` or `_DDS_`. At 16 Nov that is **36
files**. The list is the `git ls-files` output at this commit. No file is added or dropped by judgement.
A file whose subject turns out not to be a defect (a tree or harness note that only mentions DDs) is
graded **X** and leaves the denominator, with its reason.

## The grades

Each finding's own statement of what went wrong is quoted, then graded:

- **I, illegal:** the record it describes takes a move the diagram does not list, or breaks one of its
  six invariants.
- **U, undefined:** the account was in a condition no state names, so a check that every account sits
  in a declared state would have fired.
- **N, neither:** the defect is real but outside one account's lifecycle (an instrument, a page, a
  price, a cost, a provision rate, a test).

**Exposed = I + U.** Reading 1 uses the whole diagram. Reading 2 drops the two invariants written with
known defects in mind (`one_regular_amount`, `collections_on_processing_days`), as the knowledge
section states. **Reading 2 decides.**

## The decision rule (the ruling's, made numeric)

- **Exposed is more than half the defects in reading 2:** propose the file as the declared home the DD
  code checks against, as one check, not a framework.
- **Otherwise:** say so and drop it.

## Prediction

- **Reading 2: about 12 of about 33 defects exposed (36%), range 25% to 50%.** So the predicted verdict
  is **drop**, narrowly. The reason is that most DD findings here are about instruments, pages,
  provision buckets and pricing, which a lifecycle cannot see. The lifecycle-shaped ones (a DD running
  after the mandate ended, a collection before supply, a missed instalment never made good) are the
  minority.
- **Reading 1:** reading 2 plus 2 to 4 more.
- **The three named families:**
  - The half-month first DD is exposed in reading 1 only, because of contamination.
  - Bill shock is N: it is a definition failure, not a move.
  - The journey's end with two homes is N: it is about where code lives, not what the account does.
