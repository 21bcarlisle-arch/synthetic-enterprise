**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: how much of the £2,222 dispute seed a gaining supplier's first read reaches, under the every-case-disputed ceiling (2026-10-17, written before the leg was run on the book)

Direction item `gaining-supplier-first-read-world-leg-ceiling`. Knowledge first (K8):
`docs/market_research/unbilled_energy_and_revenue_assurance.md` §4a, "When the gaining supplier
first reads a non-smart meter" and "What a world build can take from this" (`e41686707`).

**The leg.** For a household that switched away, the world draws the gaining supplier's first
actual read from the read process it already runs (`simulation/meter_reads.simulate_read`, same
household, same persistent read class and smart-mode state), month by month from the switch date.
No new cadence number. A dispute is possible only if that read falls within 12 months of the switch
(REC Schedule 30 7.3(a); BSCP504 §4.4.1(b)) and the closing estimate undercharged by more than
250 kWh (electricity) or 1,200 kWh (gas) (REC 9.4). Whether a possible dispute is raised has no
published rate (a GAP row, `q6_switch_read_dispute_share`). The default draws none. The `ceiling`
arm raises every possible one, an upper bound and published as one.

**Population.** The 17 switcher undercharge open runs over the threshold on
`/var/tmp/closing-money-run-20261017.json` (cc23de757), which carry £2,222.47 of the £3,470.63 new
demand (graded in `SEAT_PREREG_WHICH_OPEN_CLOSING_RUNS_A_DISPUTED_SWITCH_READ_COULD_EVER_REACH_2026-10-17.md`).
Reached money is each run's `new_demand_gbp` from `what_closure_shows`, so the 21BA bar and the
direct-debit balance are applied as before. Whether an amended final bill after a dispute is itself
a back-bill under 21BA is a GAP; this keeps the bar, which errs against the seed (F11).

**Arithmetic known before running** (constants, not the book): an easy-class household is read
within 12 months with probability 0.937, a hard-to-read one 0.215 (monthly 0.206 and 0.02, base
share of hard-to-read 1%).

**Predictions.**
- **G1.** Long runs of estimates select hard-to-read households, so the 17 over-represent the class:
  at least 3 of the 17 are hard-to-read (base rate would give 0.17).
- **G2.** C7 (£1,431) is hard-to-read and its first read falls outside the 12 months, so it is not
  reached.
- **G3.** Under the ceiling arm, between 20% and 60% of the £2,222 is reached.
- **G4.** Under the default (GAP) arm, £0 is reached and no dispute is drawn. A control, not a
  question: if it fails, the GAP is drawing.

**What would refute the framing.** If nearly all of the £2,222 is reached, the read process is not
what limits the seed and the dispute rate alone decides it. If almost none is reached, the seed is
not realisable even at the ceiling, and the closing-estimate money is the losing supplier's to
write off whatever the dispute rate turns out to be.

---

## Graded (2026-10-17, same session, after the leg ran)

`python3 -m tools.closing_estimate_run_money --dispute {register,ceiling} /var/tmp/closing-money-run-20261017.json`.
The DD book rebuild reproduced the run's own summary. The population reproduced exactly: 17 runs,
£2,222.47. No run's window reached past the run's end (2025-06), so none is censored.

| Ceiling arm | runs | new demand £ | raw money £ |
|---|---|---|---|
| disputed (first read inside 12 months) | 12 | **700.74** | 1,072.08 |
| no actual read within 12 months | 5 | 1,521.73 | 5,244.66 |

- **G1 refuted.** 2 of the 17 are hard-to-read, not 3 or more. Still 12% against a 1% base, and they
  are the two longest runs (C7, 42 estimated bills; SYN-2016-167, 48). The other three unread are
  easy-class households: about 0.9 expected from 15 at 0.063, 3 found (P ≈ 0.07).
- **G2 held.** C7 is hard-to-read and its gaining supplier gets no read in the 12 months. £1,431 is
  out of reach even at the ceiling.
- **G3 held.** 31.5% of the £2,222 is reached (£700.74 across 12 runs). Two of the 12 carry £0 of new
  demand, where the 21BA bar or the DD balance already takes it.
- **G4 held.** The default arm reads the GAP row and raises no dispute. Every possible one carries
  the reason "dispute share is a GAP".

**What it says.** Even with every possible dispute raised, a disputed switch read could return at
most **£701 of the £3,471** closing-estimate money to the losing supplier. That bound is
conditional: it assumes the agreed read is the true register and keeps the 21BA bar. The read
process is the binding limit, not the dispute rate: two-thirds of the seed (£1,522) sits on
households whose next supplier does not read the meter inside the window either. Most of that is C7.
Both refutation clauses missed, so the framing stands: the seed is partly realisable, and the
dispute rate decides only the £701.

**Not done here.** Nothing in the run raises the dispute yet. The leg is a world function and a
grading door. The company has no amended-final-bill path for a switch read agreed after closure.
That is the company leg (REC Schedule 30 8.1(b)), handed on.
