# Delivery-seat stretch log

*What each stretch of work was about, what it got wrong, and the reasoning behind the calls made in
it. The commits record what changed; this records why. Newest first.*

*Written by `tools/stretch_log.py` as part of finishing a piece of work, not as a separate step.
A stretch that lands commits without an entry here is a finding, raised by `--check`.*

---

## 2026-09-06 — Stage 1 housing and people anchors from NEED, two budget dials raised for one window, and a corrected sample size

<!-- head: b01b1dbe392e -->

**What this stretch was about.** Stage 1 of the three-stage sequence the director set on
2026-09-05: build a robust end-to-end SIM (weather, houses, people) before billing correctness, and
both before the supplier optimising. Concretely: anchoring the housing joint against published data,
measuring what the premise draw already carries, and sizing the space-filling sample. Plus two
budget dials raised for one allowance window, and the sequencing of a use-case register that arrived
mid-stretch.

**What was established, all from DESNZ NEED `anon2026_50k.csv` (50,000 dwellings, one row each):**

- *Floor area* is anchored from **HMRC** valuation bands via NEED, not the EPC register the housing
  ruling named. EPC needs a GOV.UK account and is the worse source on the ruling's own terms — ~60%
  coverage, transaction-biased, SAP-*modelled* consumption. NEED is open and metered. Median gas runs
  2.56× from the modal 51–100 m² band to >200 m².
- *Bungalows* are a first-class type at 7.9%, with a distribution unlike detached — closing the
  ruling's "folded into detached" gap with a published share.
- *"Off gas" is a fact about a meter, not the grid.* NEED's `MAIN_HEAT_FUEL` is derived: no matched
  meter **or** under 1,000 kWh in three years. 50.3% of flats read as "not gas", which cannot be
  off-grid — it is communal or electric heating with no individual meter. So the attribute drawn is
  `has_mains_gas_supply`, the fact a supplier actually holds. The true off-grid share stays a gap.
- *Independence invents one house in five.* Drawing the axes independently puts 19.6% of houses in
  cells the stock does not contain (1,303 detached under 50 m²; zero exist) while under-producing
  detached >200 m² — the top consumption band — by 5.15×.
- *Rejecting on labels covers 6.1% of the top-1% tail; rejecting on outputs covers 85.4%.* The
  label-based sample reports 92% overall and is nearly blind to the tail.
- *Area deprivation is mostly the house.* Median gas by IMD quintile spreads 1.38× raw and only
  1.09–1.20× within one floor-area band. Supports the housing ruling's H2; narrows the people
  ruling's geography claim to *composition*, not usage-given-the-house.

**The correction that matters most.** I published "N ≈ 100 houses covers 99.6% of the output space",
flagged as a lower bound because shape and gradient were unavailable. That was too generous. Adding
one further dimension the use cases actually need — inter-year consumption volatility, i.e.
bill-shock exposure — takes N=100 from 99.2% coverage to **32.7%**; at 250 it is 87.7% and still
short. The figure was an artefact of measuring the two dimensions that were easiest to obtain. It is
corrected beside the original claim as well as in a new document, because a figure quoted once gets
quoted again from wherever it was found.

**Calls made, and the reasoning.**

- *Source swapped from EPC to NEED* without asking: evidence in hand, reasoning sound, reversal is a
  one-line change.
- *Fork width raised to 2 — but only after refusing to do it myself.* A control asserted the value
  with "if someone widens this without a director decision, this fails". Widening it and then editing
  that guard would have been self-certifying, so it was backed out and the lever reported instead.
  The director then authorised it. The guard now pins its expected value to the window's **own
  clock** — 2 before 02:50Z on 2026-09-07, 1 after — so if the restore never runs the test reds by
  itself and says the timer did not fire. An earlier draft had the restore script edit the guard too;
  driving that on a copy left the tree red, a restore that breaks what it restores.
- *Tick cadence 1800s → 120s.* Duty cycle measured at 47%; the service is `Type=oneshot`, so systemd
  cannot stack activations — the dial's whole ceiling is ~2×, and that was reported rather than
  discovered later.

**Stopped short of, deliberately.**

- *Flow temperature* stays out of phase 1 and is a registered gap. It has zero occurrences anywhere
  in `simulation/`, and the director's reasoning is recorded: the lever only means something once a
  product could turn it down, and inventing hidden state for a ceiling nothing can act on is not
  fidelity. The consequence is written down so it is not rediscovered as an oversight — the
  turn-down lever's ceiling is *unstateable*, not merely uncomputed.
- *The use-case register's use cases* are stage 3 and none is built, however ready the mechanics look.
  Only its second half — the SIM fidelity each use case depends on — is stage 1, folded into the
  housing and people phase-1 atoms rather than minted as new work.
- *A third fork.* There is no third disjoint scope; W2_19 and W2_21 both touch
  `simulation/population_draw.py`, so it would buy contention.

**Mistakes the tree caught, worth keeping.** The map's hygiene control caught a data-asset atom filed
under the default value stream; the fix for it then landed on a *different* atom's identical two
lines, and the stale-id control named that in the same run. Separately, inserting the N correction
split a sentence and left "this is the number it asked for" standing immediately after the retraction
— worse than either alone, since a skimming reader takes the last sentence.

**Where it stands.** Stage 1 continues: the fitted joint (W2_21), the sample (W2_22) and the people
joint (W2_19) are queued and ranked above billing, which is above the supplier optimising. Both
budget dials revert automatically at 02:50Z on 2026-09-07.

---
