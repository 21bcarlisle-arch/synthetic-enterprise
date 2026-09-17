**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery

# Pre-registration: what one headcount per house moves through the money path

Delivery seat, 2026-09-17, **written while both arms are still running and before either has printed
a number.** This is P2, owed since 2026-09-16, when the census-headcount change was landed on
fidelity grounds with its margin effect explicitly not measured and not inferable from volume.

Subject: `316983a72`, which makes `people_count_for` delegate so a house has one headcount wherever
it is asked, and gives the shared draw the published 5+ tail. Two arms of `run_phase2b.main()`,
same tree, same book, same weather, differing only in whether the physical layer keeps its own
second draw. The run writes nothing — the publisher does — so neither arm touches the shared tree.

**The run is deterministic.** Two independent runs today (09:35, 11:42) produced byte-identical net
and revenue: £158,380.282597 on £685,541.2784110268. A difference between these arms is the
variable and not the seed, and that is what makes a one-variable reading possible at all.

---

## What changed, stated precisely, because the prediction follows from it

**Two things moved, not one**, and they move different populations:

1. **The fabric path's headcounts were REASSIGNED.** It drew on substream
   `physical_layer_people_count_<id>` and now draws on `people_count_<id>`. Same anchor, same
   estimator: the distribution over 20,000 ids is 2.3584 before and 2.3552 after — unchanged to
   within a thousandth. **Which house gets which headcount changed; how many houses of each size
   there are did not.** This population is 130 of 136 settled premises.
2. **The property record's headcounts moved DISTRIBUTIONALLY, slightly up.** Its draw gained the
   published 5+ tail, so the mean goes 2.3167 → 2.3552, **+1.7%**, entirely in households of six or
   more, which were previously impossible.

## The predictions

**P1 — book volume moves by less than 1%.** The settling population's headcount distribution is
unchanged to a thousandth, so there is almost nothing for volume to respond to. Yesterday's
counterfactual measured the electricity elasticity to headcount at **0.46** and gas at
**0.011**; a distribution that does not move cannot move volume through either.

**P2 — revenue and net margin each move by less than 1%**, for the same reason, and net margin moves
by *less* than revenue in proportion, because the standing charge is per-account and cannot move at
all when no account is gained or lost.

**P3 — I do not predict the DIRECTION and will not guess one.** This is a reassignment: some homes
get more people and some fewer, and which way the book's money lands depends on the interaction
between the reassignment and each premise's fabric and tariff. **A direction I cannot derive is a
direction I must not claim**, and recording that is the point of writing this before the numbers.

**P4 — the fabric-driven population is unchanged at 130 of 136.** Headcount is not an eligibility
input. If this moves, something other than the headcount changed and nothing below is attributable.

## The kill line

**If net margin moves by more than 5%, this is not a one-variable comparison** and the result must be
discarded rather than explained. A reassignment within an unchanged distribution cannot move the
book that far, so a large number means the two arms differ in something I did not control — and the
honest response is to find that, not to write up the difference.

**And the second kill line, from yesterday's lesson:** the two arms must report the same number of
records and the same fabric-premise count. Two populations wearing one number is the defect I
committed on 2026-09-16 by comparing shares across two different books, and it is the first thing
checked here rather than the last.

## How it will be reported

With the population it was computed over, beside every figure. Whichever way it goes.
