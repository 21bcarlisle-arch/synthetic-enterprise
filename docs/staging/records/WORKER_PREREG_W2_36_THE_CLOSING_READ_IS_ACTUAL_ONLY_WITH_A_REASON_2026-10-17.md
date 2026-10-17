**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`
**Knowledge:** unbilled-energy-and-revenue-assurance

# Pre-registration: what changes when the world's closing read is actual only where it has a reason (2026-10-17, written before any replay)

Direction item `the-worlds-closing-read-is-actual-only-when-the-world-has-a-reason`. Finding:
`../SEAT_FINDING_THE_WORLDS_CLOSING_READ_IS_ALWAYS_ACTUAL_2026-10-17.md`. Knowledge (K8, already
written): `docs/market_research/home_moves.md` §3 and §8.4 ("a final read (actual if smart or
customer-read, otherwise estimated)").

**What changes.** `simulation/meter_reads.final_read_for` returns an actual read on the day only
for a smart meter in smart mode (a remote read on demand). A customer-own read is real but its share
is a GAP, so it is carried by name and contributes nothing: otherwise the world returns the
ordinary read `read_for` drew for that period, which is estimated (the call is made only when it
was). The company keeps asking at closure; the answer is no longer always yes.

**Instrument facts read before predicting.** The published run book (`run_output_latest.json.gz`,
78f77c34e) carries 39,084 read-log rows, 408 of them forced (`forced_catch_up`): 392 traditional,
16 smart. The finding counted 91 forced among 135 electricity move-out boundary reads.

**Predictions** (a replay of the new rule over the book's forced rows; no full run):
- **C1.** All 392 traditional forced reads become estimated.
- **C2.** Of the 16 smart forced reads, **between 4 and 12** stay actual. A smart meter reaches the
  forced path either out of smart mode (about 1 in 10 meters, but read like a traditional one, so
  over-represented among the unread) or in smart mode with a read later than the cutoff.
- **C3.** The 135 electricity move-out boundary reads go from 135 actual to **44 to 46** actual.
- **C4.** At least **90%** of the 408 forced bills carry a read true-up today (a traditional
  meter is read about one month in five, so the run of estimates before closure is rarely empty).
  Each that turns estimated loses its true-up, so closure true-ups fall by **350 to 400**.
- **C5.** The empty-period flag's judged void stubs fall from **16 to 10**: the 6 resting on a
  forced read lose their actual opening read, unless their forced read was a smart one in smart
  mode.

*Refutation.* C1 fails if any traditional forced read stays actual: the rule leaks. C2 at 16 would
mean every forced smart read was a late remote read, so out-of-smart-mode meters never reach
closure unread, which contradicts their read rate. C4 below 90% would mean closure true-ups were
not where the estimation error was being hidden, and the finding's second harm is smaller than
argued.

## Graded (same day)

The new `simulate_final_read` was replayed over the run book's forced rows. The book is stamped
`producing_commit` 2248e3baf. The read statuses were replaced, and the bills and the probe were run
again (`tools.theft_void_screen_probe.structural_run_table`). This is a replay, not a fresh run.
It shows which closing reads change status. It does not show the money the unresolved runs carry on
a final bill.

- **C1 held.** All 392 traditional forced reads become estimated.
- **C2 refuted: 2 of 16 smart forced reads stay actual**, against the 4 to 12 predicted. 14 of
  the 16 were meters out of smart mode. The weighting was underestimated. A meter in smart mode
  reaches the forced path only through a read later than the cutoff, which is about 2.6% of
  months. A meter out of smart mode reaches it about four months in five.
- **C3 held: 45 actual of 137** electricity move-out boundary reads (previously 137 of 137). The
  denominator is 137, not the finding's 135. Here the closing read is matched as the period ending
  the day before `move_date`; the finding matched it its own way. The difference is not
  reconciled.
- **C4 refuted: 320 of 408 forced bills (78%) carried a true-up**, against at least 90%
  predicted, and all 320 lose it. The prediction missed one thing. A closing month whose own read
  is estimated has an empty run before it whenever the month before was read, and that happens at
  the read rate (about one in five).
- **C5 held on the difference: judged void stubs fall by 6, from 17 to 11.** All are still
  `void/void`. The baseline is 17, not the earlier probe's 16, on the same file. It was not
  reconciled. Incoming accounts that open on an actual read fall from 130 to 45, with 85 now
  estimated and 5 with no read.

**What this means.** At closure, 320 runs of estimates that a forced read used to settle now end
on an estimated final bill. That is the CoT dispute seed in the scope brief's B3, and it now
exists in the world. The money in those runs is not measured here. It needs a fresh run.
