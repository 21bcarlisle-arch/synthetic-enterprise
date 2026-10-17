**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: what the UNC M5.10 gas must-read reaches on the graded run (2026-10-17, written before the count was run)

Direction item `gas-must-read-at-24-months-world-leg`. Knowledge page:
`docs/market_research/read_access_and_theft_duties.md` §2.7 and §6 code gap 7 (f10a51da2).

**The rule as built.** At the end of a month when a Class 4 Annual Read gas meter has no valid read
in the preceding 24 months, the CDSP notifies the Transporter, which attempts a read (M5.10.1(b),
5.10.2). In `simulation/meter_reads.simulate_read`, the attempt falls on the period after the
notification: a gas account on a traditional meter (an Annual Read Meter, M5.9.1(b)) whose bill
arrives with 24 or more estimated bills before it, and whose ordinary read did not arrive. Its
outcome reads `q6_read_visit_access_failure_rate`. That row is null, so the `register` arm draws no
read and publishes `must_read_attempted`. The `ceiling` arm has every attempt read, and it is an
upper bound, not an estimate.

**The grade** (`tools/closing_estimate_run_money --must-read`, on
`/var/tmp/closing-money-run-20261017.json`, cc23de757). Two parts. First, the trigger is counted
from the run's own bills: a gas bill on a traditional meter with an incoming estimated count of 24 or
more. Second, the money is decomposed, without a re-run: under the ceiling arm, each estimate that
falls on an attempt becomes an actual read and trues up the estimates before it while the customer
is on supply. The money a closing run would still carry is its last segment only.

**Predictions.**
- **G1.** The trigger fires on more accounts than the two closing runs the item names (SYN-2016-167,
  SYN-2016-471). Accounts still on supply can run as long. I predict 2 to 6 accounts.
- **G2.** The register-arm attempts on those two runs total (48 − 24) + (38 − 24) = 38. That is
  arithmetic, not a prediction. It is checked here so that a wrong offset in the trigger shows up.
- **G3.** Under the ceiling arm, the open new demand the two closing runs carry falls by less than
  £60. The item says "about 40 GBP of new demand".
- **G4.** Electricity is untouched: the trigger fires on 0 electricity bills, and the register arm
  changes no bill in any run (the read stream is byte-identical while the row is null).

## Graded (2026-10-17, after the build, same run)

`python3 -m tools.closing_estimate_run_money --must-read /var/tmp/closing-money-run-20261017.json`

| | prediction | result | |
|---|---|---|---|
| G1 | 2–6 accounts reached | **4**: SYN-2016-167 (24 attempts), SYN-2016-471 (14), OCC-49cf03d82fea (10, on supply), PROS-2020-0190g (8, on supply) | held |
| G2 | 38 attempts on the two closing runs | **38** (24 + 14), and the first attempt on SYN-2016-167 falls on its 25th bill | held |
| G3 | the ceiling takes less than £60 of new demand | at most **£39.91** (£26.01 + £13.90). Raw open money: £90.76 → £37.24 and £226.18 → £65.11 | held |
| G4 | 0 electricity attempts; the register arm moves no bill | 0 electricity. The register arm's status and delay match the pre-build stream on 600 ids (control) | held |

56 attempts in all, on 4 of the book's gas accounts. The value is what the item said it would be:
fidelity, not money. Under the published code a gas run of estimates is capped at 24 unless the
visit fails, and whether it fails is the null row. The bound is a decomposition of this run, not a
re-run. A ceiling read would also start a fresh run, and would change the 21BA bar and the
direct-debit balance that the open new demand is computed through.

**Not built, and why.** M5.10.1's trigger for a smart (Monthly Read) gas meter was not read (GAP),
so a gas meter that is not in smart mode gets no must-read. The must-read charge sits in each
Transporter's Metering Charging Statement, which was not read, so no cost reaches the company. A
company-side reader of `must_read_attempted` (the CDSP notifies the User, so a supplier would know)
is not built.
