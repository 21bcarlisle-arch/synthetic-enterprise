**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The 6af7fd0bfd publish hid three refusals behind its two site reds; it is live, and its first reader grade is 1 red

*Worker tick, 2026-11-18, drawn on the publish-gate wedge (61 failures). Outcome: the book reached
origin as 43fa9534d → 7a4af086a → merge 7f0723b46, Pages and Cloudflare deployed it, and
`https://poesys.net/data/dashboard.json` serves `6af7fd0bfd` (re-fetched 11:0xZ).*

## What refused it, in order

1. **09:43Z, two site reds.** Both were already answered on origin (49d41097b re-keys INV5940 by its
   period; 22639d0ad stops the empty-field sweep counting a given English "undefined").
2. **10:03Z, stale-base guard.** Origin moved to 22639d0ad mid-commit. No test ran.
3. **10:03–10:06Z, the hand re-drive died silently.** 6cb6d687a re-drove the marker by hand (pid 274211)
   from inside `seat-executor.service`. The pid was still generating surfaces when that unit finished
   at 10:06:14Z, and systemd tore down its cgroup. The log stops at `margin_bridge.json` with no
   outcome line. **A publisher started from inside a timer unit cannot outlive that unit.** Use
   `background.launch_long_job --detach` instead.
4. **`launch_long_job` does not carry the NTFY topic.** The first detached re-drive died at import:
   `ntfy_utils` raised `SE_NTFY_TOPIC is not set`. It worked with
   `--setenv SE_NTFY_TOPIC=…` loaded from the env file. A launcher for long jobs that cannot start the
   publisher without that flag is a trap for the next lane.
5. **10:45Z, gated locally, then refused at the merge by the channel-F census.** The publish commit
   widened channel F's nested surface by six names. It passed its own gate because
   `_wall_channel_census_check` (`tools/pre_commit_test_gate.py`) runs only when a `.py` file or the
   baseline is staged, and a publish stages neither. The widening surfaced one step later, on the
   merge with origin's `.py` files, where it blocks a reconcile that did not cause it.
   **Ruled and re-frozen in 7a4af086a:** all six are the supplier's own acts
   (`bills.catchup_lines_by_rate/net_gbp/rate`, `credit_refund_log.set_off_against/set_off_gbp`,
   `per_customer_behavioral.debit_asked_gbp`). Reverse by restoring the baseline from 43fa9534d.

**Proposal, not built:** run the channel-F half of the census when a staged path is a published
artefact the census reads, not only when a `.py` is staged. Then a widening refuses the commit that
makes it.

## Post-publish readers on the live book: ran, 1 red of 44 files

`test_the_published_book_charges_its_contracted_tariff`: 3 of 53,605 bills DISAGREE.
- PROS-2016-0253, 2017-09
- PROS-2017-0286, 2018-09
- PROS-2021-0313, 2022-09

Each is a profile-class-2 (time-of-use) fixed term that rolls to the SVT mid-month. This is the
control's first live read: the ledger before this book had no `contracted_terms`, so the test
skipped. That makes it a first reading, not a regression.

Worked case, PROS-2016-0253 Sept 2017, 998.2 kWh:
- The biller prints commodity at 11.093p, which is £110.73.
- It adds non-commodity at £54/MWh, which is £53.90.
- So it charges £164.63, or 16.49p/kWh.
- The validator's range is £61.28..£147.35. Its ceiling is every kWh at the SVT's 14.7619p.

Three explanations fit, and **I cannot yet say** which:
- (a) Contracted rates are all-in, and the biller adds non-commodity on top only on a crossing bill.
- (b) The validator's range omits non-commodity on a crossing bill.
- (c) The biller blends at the wrong rate.

**Read the same tick, on the same account's neighbouring bills.** The single-term bills are all
AGREED, to the penny, at commodity plus non-commodity:

| Bill | Commodity | Non-commodity | Agreed claim |
|---|---|---|---|
| Jul | £58.97 | £46.99 | £105.96 |
| Aug | £57.77 | £45.05 | £102.82 |
| Oct (SVT) | £132.37 | £59.96 | £192.33 |

October works out to 11.92p commodity and 17.32p all-in. Neither is the contracted SVT rate of
14.7619p.

The crossing bill's range is exactly kWh × [lowest, highest] contracted rate: 6.1394p night and
14.7619p SVT give £61.28..£147.35. That basis matches nothing the single-term path agrees on. **This
points to (b): the validator's crossing-bill branch prices on a basis its single-term branch does
not use.** It is not a biller defect. I have not read the validator's code, so this is still a
ranking, not a verdict. The fix belongs in `tools/independent_bill_validator.py`'s crossing range,
and once it is fixed this red should clear without a rerun of the book.

**Corrected, later the same day (worker tick): the cause is none of (a)-(c), and the ranking above
was wrong.** The validator prices the single-term bills and the crossing bound on the same all-in
basis, so (b) does not hold. On all three bills, the record for the SVT term that starts inside the
bill (e.g. 2017-09-08 to 10-01) carries `tou_unit_rates: null`. The biller settled that stub on the
Day/Night pair (rate line `time_of_use: true`, 17.51p), so the bound's ceiling was the flat 14.76p.
The defect is in the ledger's term record: `generate_billing_ledger._tou_terms` read the pair only
through `term_of_bill`, and no bill starts inside a stub term. The fix reads each crossing line's own
`time_of_use`. On the live book, measured in memory: 29 SVT stub terms gain their pair; verdicts go
from 53,373 / 229 / 3 (AGREED / BOUNDED / DISAGREED) to 53,373 / 232 / 0. The prediction was filed
before the run. The published red clears at the **next publish**, when the ledger is regenerated,
and **not** without a rerun as said above.

NEXT: none -- the contract red is fixed at its source and clears at the next publish; the channel-F census proposal and the launch_long_job NTFY trap stay open here
