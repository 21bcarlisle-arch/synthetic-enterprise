**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The world must produce real meter-data faults, and the supplier must find them

**Type:** STEER, through the advisor channel. **It is a world-lane item**, for the one work system's world lane once that exists. Until then it goes in `priority_order.yaml` as world work. The director's words, from chat, Sat 14 Nov 11:05 GMT:

- "One for the SIM backlog. We want smart meter data errors and gaps. We want bumb meter erroneous meter reads. We want meters usage to change with events that causes problems. We want dumb meters to clock. We want manual reads to have the wrong numbers of digits etc."

("bumb" is "dumb", meaning traditional, non-smart meters.)

## What he wants the world to do

Real metering data is messy, and much of a supplier's billing pain starts there. Today's world is too clean for the supplier to learn to cope. The world should generate the faults a real GB supplier meets, keep the truth hidden as an instrument (W7), and let the supplier's validation, estimation and contact processes discover and handle them. His examples, with the obvious kin:

- **Smart meter data errors and gaps.**
  - Missing half-hours and whole days.
  - Comms outages that end in a back-fill.
  - Zero or flat-lined intervals.
  - Spikes.
  - Duplicates.
  - Clock or time-shift errors (BST and GMT).
  - A meter that stops communicating and quietly drops to traditional mode.
  - Gas and electricity hubs failing at different rates.
- **Traditional (dumb) meter read errors.**
  - Misread digits: transposed, a digit dropped or added.
  - Day and night registers swapped on Economy 7.
  - The wrong meter read (crossed meters or a neighbour's).
  - A read taken against the wrong date.
  - Estimated reads that drift away from use.
- **Manual (customer) reads with the wrong number of digits.**
  - A decimal or a red digit included.
  - A leading digit dropped.
  - Imperial gas meters read as metric, and the reverse.
- **Meters that clock.** A register rolls over its digit count (for example 99999 to 00000). That gives an apparent huge negative, or a huge positive if the read is misinterpreted.
- **Usage that changes with events and breaks estimates.**
  - A life event (an EV, a heat pump, a baby, retirement, a lodger, a long absence, a new tenant) shifts use.
  - The estimate (the EAC or AQ) and the direct debit lag behind.
  - The result is catch-up bills, credit build-up or bill shock.

  The life events exist today. Check whether they actually move estimates and payments, and where they do not, close it.
- **Meter exchanges.**
  - Removal and install reads missing or wrong.
  - A smart exchange that resets the history.
  - Mismatched meter serials.

## How (the machine owns the design)

1. **K8, knowledge first.** Write the metering data quality page before building:
   - the industry's own read validation rules and tolerances (BSCP504, REC metering schedules);
   - settlement read rules;
   - published rates of comms failure (DESNZ smart statistics; `meter_reads.py` already uses some);
   - published evidence on read errors, rollover and billing complaints (Ombudsman, Citizens Advice, Ofgem back-billing).

   Label the GAPs. Many rates are not published. Where they are not, model them as stated beliefs with ranges, and do not invent them.
2. **Build on what exists.** `simulation/meter_reads.py` already has:
   - the not-communicating share;
   - read delays and hard-to-read premises;
   - registration error bands;
   - theft;
   - the exchange hazard.

   The tenth cold read, by a meter-data analyst, found four classes on this ground. Start from those. Do not start a parallel module.
3. **Rank faults by frequency times billing harm,** and build the top few first. Each fault is world truth. The supplier sees only the faulty data.
4. **Supplier-side consequences go to the supplier lane.** Validation, estimation, read rejection, customer contact, site visits and back-billing caps are the supplier's job, raised as their own items. Its measure is how many faults it catches before they reach a bill, and at what cost to the household (time, worry) and to itself.
5. **The publish gate's money invariants must still pass.** A world that produces faults must not turn a correct supplier response into a gate breach. Where a fault should reach a bill, the invariant judges the supplier's response, not the fault's existence.

Rank this against the other world-lane items in Sunday's balance proposal. It is not for this weekend under the usage pace.
