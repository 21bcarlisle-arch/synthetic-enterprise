**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-QUESTION] Why did these bugs exist, and why did the tests not find them? (2026-10-26)

**Type:** QUESTION, through the advisor channel. This follows `DIRECTOR_STEER_EVERY_EXPLORE_EXAMPLE_MUST_MAKE_SENSE_TO_AN_ENERGY_READER_2026-10-26.md`. These are the director's words from chat on Mon 26 Oct:

- 18:27 GMT: "I like extreme cases but these are clearly just unspotted errors. Why did these bugs exist ? Why did tests not find them?"

**Extremes stay.** The director likes them, and they are what surfaced these errors. The fix is the validity predicate, not milder examples.

## The advisor's hypotheses (unconfirmed; confirm or refute each from the code)

1. **One-sided tests.** The cap check asks whether a price is over the cap. Nothing asks whether a price is implausibly *under* the cap or under wholesale cost. Tests assert the rule someone thought of, not the range a domain expert holds in their head.
2. **Same author, same blind spot.** The tests were written by the same agent that wrote the code, from the same model of the domain. If the model lets a gas-only household acquire an EV, the test writer did not think to forbid it either.
3. **Units pass and the joins fail.**
   - Life events are drawn without checking which fuel legs the household holds.
   - The EV effect is measured on whatever leg exists, with no season or weather normalisation.
   - The prepayment payment method sits beside monthly credit billing.
   - Each module can pass its own tests while the combination is nonsense.
4. **Aggregates hide tails.** Population checks (means, totals, cap breaches) can be green while individual households are absurd. The extreme selector reads the tail, which is why it found them.
5. **Provenance was mistaken for correctness.** "No figure typed by hand" proves that a figure came from the run. It does not prove that the figure is right. The post-publish readers check bytes, freshness and structure, not meaning.

## Ask

- For each defect in the Explore steer, record the **root cause**: which module, and which of the five classes above (or a sixth). Also record **why no test caught it**, and which predicate or test now does.
- Check whether the same classes of error exist outside Explore:
  - life events against fuel legs, across the whole book;
  - SVT prices against wholesale and against the cap, over every period;
  - prepayment accounts against billing;
  - runs of estimates against the read duty;
  - use per household against population percentiles.

  Report the counts.
- Add a standing **domain-invariant suite**. It holds two-sided ranges per quantity per period, it is written from the Knowledge pages and the evidence packs rather than from the code, and it runs over every household, not only the published examples.
