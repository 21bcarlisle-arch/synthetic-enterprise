**Severity:** RECORDED · **Lane:** 0 delivery · **Direction item:** `the-bad-debt-belief-cannot-go-negative`

# Result: the own-book bad-debt belief read by vintage, before and after, per cell, on the `net` arm

Grades `SEAT_PREREG_THE_BAD_DEBT_BELIEF_READ_BY_VINTAGE_BEFORE_AND_AFTER_ON_THE_NET_ARM_2026-10-22.md`
(P1–P4 as written). Fix at `793989589`. The probe ran from a locked worktree at that commit:
`tools._c29_retention_engagement_arm net`, with `PaymentObservationConsumer.default_belief_rate`
wrapped so that every call also computed the pre-fix belief on the same ledger, date and cell. The
probe is `/var/tmp/se-belief-probe/probe.py` and its output is `probe_out.json` beside it. Both are
outside the repo, so the numbers below are the record. The probe's worktree has been removed.

**Run history.** The first launch and r2 both failed. r2 tabulated after the arm returned, by
which point the run had uninstalled the DD stop-notice board. `payment_method_of(as_of=...)` then
refused with `ValueError: get_payment_method('C2', as_of='2018-05-15')`. r3 tabulates during the
run, at each new latest call date, and finished with rc 0 and `OUTCOME: SURVIVED`. **Deviation
from the prereg:** "at report end" became the date of the **last belief call**, 2025-06-03, not the
run's report end.

The run made 15,679 calls from 2016-01-01 to 2025-06-03. No call returned `None` under either
reading.

## P1: no negative belief after. Holds for the new reading, REFUTED as written

| state | calls | old < 0 | new < 0 | old ≠ new | min old | min new | mean old | mean new |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_debt | 12,183 | 0 | 0 | 10,047 | 0.0010 | 0.0008 | 0.0059 | 0.0052 |
| in_arrears_steady | 1,827 | 0 | 0 | 1,680 | 0.0017 | 0.0082 | 0.0100 | 0.0154 |
| worsening | 237 | 0 | 0 | 205 | 0.0200 | 0.0200 | 0.0978 | 0.0941 |
| unknown | 1,432 | 0 | 0 | 590 | 0.0082 | 0.0073 | 0.0159 | 0.0160 |

No call read below 0 under the new observation. **No call read below 0 under the old one either.**
The prereg named that outcome as the refutation: the defect is **not reproduced on this book**, so
the fix is not exercised at real inputs in the region it was built for. It is exercised only by the
synthetic controls in `793989589`, where a paydown cell reds the old observation.

Why the `1ac35d918` pair saw GOOD −0.0083 and POOR −0.0046/−0.0053 and this book shows nothing
below 0.0010: **I cannot yet say.** More than one thing changed between them:

- this run prices with the new belief, so its path is different, as the prereg already said;
- 78 commits separate `1ac35d918` from `793989589`, among them `cda47a346` (E6 early-warning
  provision, default off) and `7a7ad95dc`/`0674199b8` (renewal belief and guard, default off);
- the negative rows were labelled by GOOD/POOR, not by these four arrears states, so they may not
  be the same cells.

The one-variable control would be the old observation pricing its own path at `1ac35d918`'s tree,
with the probe's wrapper. It is not run here.

## P2: the whole book does not move. HOLDS

The `*|*` share at the last call was old 0.0082 and new 0.0081. Unrounded, the difference is
**−0.000128**, under the 0.0005 bar. The charge numerator is £21,013.14 old and £21,013.22 new, an
8p difference. Nothing is lost or counted twice.

The share moves only through its **denominator**. Billed is £2,556,101.99 old and £2,596,427.21
new. The whole £40,325.22 gap is on `prepayment|no_debt`, where the new reading leaves 88
account-years unread against the old one's 179. Those years add billing at a charge of 0. This is
a coverage change on prepayment years, not a change of money. I did not trace why the new reading
reaches 91 more prepayment years.

## P3: the release moves from the arrears cells to the clean ones. HOLDS

Charge share per arrears-state cell at 2025-06-03 (each account-year at its latest reading):

| cell | account-years | billed £ | old charge £ | new charge £ | old share | new share |
|---|---:|---:|---:|---:|---:|---:|
| `*\|no_debt` | 2,663 | 1,705,968 (old 1,665,643) | 6,629.23 | 1,296.02 | 0.0040 | **0.0008** |
| `*\|in_arrears_steady` | 214 | 163,989 | 776.26 | 1,632.81 | 0.0047 | **0.0100** |
| `*\|worsening` | 327 | 247,528 | 9,198.30 | 14,103.26 | 0.0372 | **0.0570** |
| `*\|unknown` | 1,200 | 478,941 | 4,409.35 | 3,981.13 | 0.0092 | 0.0083 |
| `*\|*` | 4,404 | 2,596,427 (old 2,556,102) | 21,013.14 | 21,013.22 | 0.0082 | 0.0081 |

Both arrears cells rise and `no_debt` falls by a factor of five, as predicted. About £5.3k of
charge moves from the years in which the debt was paid down to the years in which it was run up.

Method × state is a diagnostic only. The belief does not learn on it.

| cell | old share | new share |
|---|---:|---:|
| `standard_credit\|worsening` | 0.0580 | 0.1097 |
| `standard_credit\|in_arrears_steady` | 0.0078 | 0.0129 |
| `standard_credit\|no_debt` | 0.0098 | 0.0009 |
| `direct_debit\|worsening` | 0.0193 | 0.0119 |
| `direct_debit\|in_arrears_steady` | 0.0013 | 0.0067 |
| `direct_debit\|no_debt` | 0.0033 | 0.0008 |
| `prepayment\|*` | 0.0000 | 0.0000 |

Pay-on-receipt now carries 2.8% of its billing (was 2.0%) and direct debit 0.33% (was 0.56%). In
the `worsening` cell the move goes in opposite directions by method: standard credit roughly
doubles and direct debit falls. The pooled `worsening` belief therefore now leans on
standard-credit losses more than it did. This is not a defect, but it is the reason the cell
belief should be read with the method mix in mind.

**What decisions see.** For calls dated 2023 and later, the mean belief moved:

| state | calls | old mean | new mean |
|---|---:|---:|---:|
| no_debt | 3,372 | 0.0039 | 0.0020 |
| in_arrears_steady | 763 | 0.0085 | 0.0117 |
| worsening | 67 | 0.0532 | 0.0659 |

Clean renewals are now netted about half as much bad debt, and arrears renewals more.

## P4: in-course effect under 15%. UNGRADED

As pre-registered, the probe was not extended to read bill age at the time of reading. The GAP on
`bad_debt_provisioning.md` stands.

## What this changes

Under the prereg's own rule, P2 holding with P1's new reading clean keeps the fix as the default,
and that is unchanged. P3 holding means the release was where the defect said it was.

P1's refutation is the open item: on this book the fix is a reallocation between cells, worth
£5.3k of a £21k charge, not the repair of a negative belief. The negative belief has not yet been
seen and repaired on a real path. This is not escalated, because the class invariant
(`EXPECTED_LOSS_BELIEF_WITHIN_ZERO_AND_ONE`) refuses a negative belief at both doors whatever the
path.
