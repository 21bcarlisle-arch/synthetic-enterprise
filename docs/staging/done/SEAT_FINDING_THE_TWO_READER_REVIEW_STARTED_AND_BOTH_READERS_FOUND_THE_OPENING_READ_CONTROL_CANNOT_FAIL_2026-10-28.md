**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The two-reader review started on 28 Oct, and both readers found that `INV_OPENING_READ` cannot fail (2026-10-28)

*Delivery seat, executor turn. This acts on
`docs/staging/advisor/done/DIRECTOR_RULING_GO_ON_THE_TWO_READER_REVIEW_AND_START_IT_NOW_2026-10-28.md`
(his 06:39 "Go"). BLOCKING because one finding below is a control in the correctness stretch's exit
test that reports CLEAN and cannot fail.*

## The trial, as ruled

- **Started:** 2026-10-28.
- **Review date: 2026-11-11.** Stop rule: if fewer than half the filed findings are confirmed, the
  trial stops.
- **Readers:** two blind, non-blocking Opus `phase-close-evaluator` readers per qualifying commit.
  Each reader saw only `git archive <sha>` (no `.git`), the `.py` diff, the stat, and the commit message
  as the statement of intent. It was told to fix nothing. Both verdicts on each commit are recorded in
  `docs/observability/trust_ledger.json` under `reading-review-live-2026-10-28:<sha>:arm{A,B}`.
- **Filing rule:** a finding is filed only when both readers raise it. I then check it at HEAD like
  any other finding.

## Which commits qualified, and the share

The mechanical test is: the commit adds a non-test `.py` module. Of the **157** non-merge commits on
origin/main since 2026-10-26T00:00Z, **2 qualified (1.3%)**: `529a6b05a8` (the domain-invariant runner)
and `a3f6926173` (W2_37, complaint generation). The ruling's feared failure, a test so broad the spend
balloons, did not happen. Four Opus reads in all, taking 1 to 2.5 minutes each.

**What the test misses (GAP).** The ruling's second class, "re-implements a rule something else
already computes", has no mechanical selector. The readers find that class anyway (reader A on
`529a6b05a8` #3: the cross-fuel check applies the gas DD cap that `INV_UNIT_RATE_SVT_GAS` limits to DD
windows). But nothing *selects* a commit for that class unless it also adds a module. So the 1.3% is
a lower bound on what the ruling covers.

## Readings

Both commits came back NEEDS_WORK from both arms.

### `529a6b05a8`: the domain-invariant runner

Raised by both readers, then checked at HEAD:

1. **`INV_OPENING_READ` cannot fail. CONFIRMED, live.** `ev_opening_read`
   (`tools/domain_invariant_runner.py:549`) measures days from supply start to the earliest read of any
   type. The raw export writes a `carried_forward` opening read dated on `period_start`. **On the 1691ec0ecd
   book, 1,293 of 1,293 accounts' first read is a `carried_forward` read on the start day**, so the gap
   is 0 days every time and the row reports CLEAN 1,293. Excluding `carried_forward`, **921 of 1,293**
   accounts' first other read falls more than 8 days after supply start. Not every one of those reads is
   actual or deemed, which is what the invariant's statement requires, so 921 is an upper bound on the
   flags the row should raise, not a count. The test makes the row fire only by hand-editing the opening
   read to 12 days late, a value the exporter never writes. This weakens the stretch exit leg one's
   "zero unexplained breaches", and it is the same shape as the 28 Oct orientation's N1: the suite
   reports CLEAN over a record that cannot show the defect.
2. **Register count pooled over the account's life. PARTLY SPENT.** `36ce8dc532` now classes SVT terms
   by their own periods' registers. The annual-use check still uses the account-level set
   (`tools/domain_invariant_runner.py:476`, `len(a.registers) >= 2`). That leg is live.
3. **Back-billing day-count mismatch. CONFIRMED, live.** `:716` multiplies an exclusive day count by a
   daily average whose denominator (`:723`) is inclusive. Every catch-up expectation is about one day
   short, which tilts the proxy toward flagging. This is a MINOR.

Raised by one reader only, and **not filed** under the rule: `AMBIGUOUS_REGIONAL` not implemented (B);
cross-fuel DD cap on non-DD gas (A); `"M"` prepayment reads not counted as actual (A); the account-level
prepayment flag (A); register-label keying in the monotonic check (B); the gas standing-charge
denominator (B). They are kept in the trust-ledger notes and in this record so the 11 Nov review can
see what the vote discarded.

### `a3f6926173`: W2_37, complaint generation (L1, unwired)

4. **The silent-unhappy window does not match. CONFIRMED at HEAD, latent.** `silent_unhappy_probability`
   subtracts a badly-handled share annualised over four quarters
   (`tests/simulation/test_complaint_generation.py:80`, "a year of quarters"). But
   `draw_silent_unhappy` excludes only *this quarter's* complainants. The docstring promises "met a
   trigger in the trailing year and did not complain", and the API takes one quarter's booleans. So a
   household that complained in Q1 can be drawn silent in Q2, and the "sums to 6%" identity holds only by
   construction. Nothing calls the module yet (`grep` finds no caller), so no figure moves. It must be
   fixed before L2 wires it in.
5. **Complaints counted as complainants. Raised by both, MINOR.** 1,011 per 100k is a complaint count,
   and `draw_complaints` can fire several causes for one household. Reader B measured the gap as small
   on the test book (4.12% complaints against 4.03% distinct complainants).

Not filed (one reader each): Ofgem's dual-fuel two-accounts denominator (B, MAJOR, and the page's own
warning at §3.3 makes it worth a look before L2); the 57% being assumed a subset of the 6% (B); the
cumulative silent share over a year (A; I do not confirm it, because a quarter-scoped state is a
defensible reading of a point-in-time 6%); the scorecard's 700/100k red line against the 1,011 world
calibration (B).

## Score so far, for the 11 Nov review

5 findings filed under the vote. 4 confirmed live or latent, 1 partly spent by a later commit, 0
refuted. The rule does not count a finding a later commit already fixed as unconfirmed.

## Owed

- The fixes: `ev_opening_read` should read the first actual or deemed read (and decide `"M"`). The
  annual-use leg should take the per-period register set. Back-billing needs the `+ 1`. W2_37's window
  must be fixed before L2. Each fix moves suite figures, so it lands with the run that grades it, not
  inside a pre-registered grade.
- **The trial is not yet automatic.** Today's readings were run by hand from this turn. A post-commit
  lane that selects qualifying commits and runs the two readers is the continuation
  `the-two-reader-review-runs-on-every-qualifying-commit`, due 2026-10-30. If it has not landed by then,
  it is overdue, and that is the director's 28 Oct steer applied to this very close.
