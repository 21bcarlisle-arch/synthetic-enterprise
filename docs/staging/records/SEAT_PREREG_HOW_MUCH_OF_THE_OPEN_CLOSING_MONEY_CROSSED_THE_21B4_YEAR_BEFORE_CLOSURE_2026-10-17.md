**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: how much of the £3,471 open closing money sits on runs that crossed the SLC 21B.4 year before closure (2026-10-17, written before the split was run)

Direction item `c7-forty-two-month-estimate-run-needs-a-read-request-not-a-dispute`. It follows
`bc4c80fca`: even with every possible switch-read dispute raised, £701 of the £3,471 comes back,
and C7 (£1,431, hard-to-read, 42 estimated bills) cannot be reached. The lever left is the losing
supplier's own SLC 21B.4 effort while the customer is still on supply.

**The question.** Of the 403 open closing runs on `/var/tmp/closing-money-run-20261017.json`
(cc23de757), which ones reached 12 estimated bills in a row before the account closed? That is a
`company/billing/read_duty_register.py` row inside the open run: the company could see the year
pass and the duty asked it to take steps. How much of the run's money and new demand do they carry?

**The split** (`tools/closing_estimate_run_money.read_duty_reach`): an open run crossed the year if
its run of estimates holds a bill with `consecutive_estimated_count == 12`. The run's money is split
at that bill. Bills 1–12 are what a read at the year would have trued up on supply. Under the 21BA
bar that is all within 12 months of the read. Bills 13 onward are what a read at the year would have
started again on a fresh run. This is a decomposition of the money, not a counterfactual. Whether a
request at the year gets a read is the GAP the knowledge page names. The world cannot answer one
yet.

**Predictions.**
- **Y1.** Between 2 and 15 of the 403 open runs crossed the year. Long runs are rare, and the
  run-length tail is the hard-to-read class (1% base) plus easy-class bad luck.
- **Y2.** Those runs carry at least 55% of the £3,471 new demand. C7 alone is 41%.
- **Y3.** On those runs the raw money (true − billed) is more than twice the new demand. The 21BA
  bar takes everything consumed more than 12 months before the closing demand.
- **Y4.** At least 25% of those runs' raw money falls in bills 1–12. A read at the year would have
  billed that on supply, inside the 12 months.

**What would refute the framing.** If under a third of the £3,471 sits on runs that crossed the year,
the read request is not the lever for the seed. The money is short runs that closed before any duty
fell due, and only the closing read itself could reach it. If almost all of it does, the year is the
right point for the company to act. What the company does there is the K8 page's question.

---

## Graded (2026-10-17, same session, after the split ran)

`python3 -m tools.closing_estimate_run_money --read-duty /var/tmp/closing-money-run-20261017.json`.
The DD book rebuild reproduced the run's own summary. The undercharge new demand reproduced exactly:
£3,470.63.

| Open closing runs | runs | undercharge runs | undercharge raw £ | undercharge new demand £ |
|---|---|---|---|---|
| crossed the 21B.4 year before closure | 25 | 12 | 5,776.61 | **1,761.88** |
| closed inside the year | 378 | 198 | 2,764.94 | **1,708.75** |

- **Y1 refuted.** 25 runs crossed the year, not 2–15. 13 of them are overcharges, which a 12-month
  register sees as readily as undercharges. 5 of the 25 are hard-to-read (20% against a 1% base).
  The rest are easy-class runs of 12 to 21 bills.
- **Y2 refuted, narrowly.** The crossed runs carry 50.8% of the £3,471, not 55% or more. C7 is
  41.2% on its own. The other 11 crossed undercharges add £331.
- **Y3 held.** On the 12 crossed undercharges the raw money is 3.3 times the new demand
  (£5,776.61 against £1,761.88). The 21BA bar adds £3,929.05, of which £3,586.08 is C7's.
- **Y4 held.** 30.7% of their raw money (£1,771.59) falls in bills 1–12. Excluding C7 it is 64%:
  the shorter crossed runs had most of their money in the year that the read would have closed.

**Both refutation clauses missed.** Half the seed is on runs where the licence asked the company
to act. Half is on short runs that closed before any duty fell due. Each half needs a different
lever: the read request at the year for the first, the closing read for the second. One percentage
across both would have hidden that.

**What it found that was not asked.** Two gas runs (SYN-2016-167, 48 bills; SYN-2016-471, 38) went
past 24 months unread. UNC M5.10 has the Transporter attempt a read at 24 months on a Class 4 Annual
Read meter, at the shipper's cost. The world has no such attempt. This is a fidelity gap from a
published rule, written up in `read_access_and_theft_duties.md` §2.7 and §6 code gap 7.

**K8 for the read request** is in that same §2.7. Gas has a code backstop: a "shall secure" read
each 12 months (M5.9.9) and the 24-month must-read. Electricity has none: the supplier instructs its
data collector, and each failed visit comes back as a coded D0004. That trail is the evidence both
21B.4 and 21BA.2(c) need. What a supplier sends before the year, and how often a visit gets a read,
are still GAPs.
