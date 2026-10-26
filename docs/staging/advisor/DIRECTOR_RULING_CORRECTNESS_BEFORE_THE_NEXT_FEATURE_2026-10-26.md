**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Correctness before the next feature: the domain-invariant suite and its fixes come before forward years (2026-10-26)

**Type:** RULING, through the advisor channel. The director's words, from chat on Mon 26 Oct:

- 18:27 GMT: "I like extreme cases but these are clearly just unspotted errors. Why did these bugs exist ? Why did tests not find them?"
- 18:29 GMT: "Ok. So what should we and it do about it?"
- 18:30 GMT, on the advisor's plan: "Ok do it"

This ruling implements:
- `DIRECTOR_STEER_EVERY_EXPLORE_EXAMPLE_MUST_MAKE_SENSE_TO_AN_ENERGY_READER_2026-10-26.md`
- `DIRECTOR_QUESTION_WHY_DID_THE_TESTS_NOT_FIND_THE_EXPLORE_ERRORS_2026-10-26.md`

## The ruling

**Correctness comes first. No new feature work is drawn until the steps below are done.** That covers the forward years, the personalised asset world and advice. Work already landing may finish. Put this ahead of the forward years in `priority_order.yaml` as a *correctness stretch*, and record its exit test.

1. **Tonight:** fix the broken Explore examples or show them as honestly empty, as the externals steer says.
2. **First, the crisis gas price.** SYN-2016-476 paid about 3.9p/kWh for gas in Jan 2022, against a cap of about 7.4p.
   - Measure every SVT unit rate, per fuel per period, against both the cap and the period's wholesale cost.
   - If SVTs were materially under the cap through 2021–22, the crisis P&L is wrong. Fix it, re-run, and mark every published figure that moves.
3. **Root causes, not symptoms:**
   - life events drawn only for the fuels a household holds;
   - prepayment billed as prepayment;
   - the 12-month read duty actually firing;
   - EV effects measured on electricity and weather-normalised;
   - the storage-heating and household-count defects.
4. **The domain-invariant suite.**
   - Two-sided ranges per quantity per period: price between wholesale cost and cap, use within the population percentiles for fuel and segment, events consistent with the fuels held, duties firing when due, payment method consistent with billing.
   - **Written from the Knowledge pages and evidence packs, by an agent that has not read the code under test.** Each invariant cites its source.
   - Runs over **every household on every run**. A breach blocks the publish, or is recorded as a named, dated exception.
5. **Examples are a gate.**
   - Each Explore slot ranks by its extreme only among households that pass the suite and the slot's own validity predicate.
   - If none passes, the slot is shown empty with the failing check named.
6. **A cold reader after every publish.**
   - A fresh agent with no code access reads every example as a GB retail-energy professional.
   - Each confirmed objection becomes a new invariant.

**Exit test for the correctness stretch:** the suite runs on the full book of a fresh run with zero unexplained breaches. All eight Explore slots are filled validly or are honestly empty. One cold read finds no new class of error. Report this in a reading, and only then resume the ruled order.

## Standing roles

- **The advisor** runs its own independent cold read every Monday after the run, on Explore plus a random handful of households, and stages what it finds.
- **The director** reads one or two examples a week. If he finds an error the cold reader missed, that is itself a finding about the reader.
