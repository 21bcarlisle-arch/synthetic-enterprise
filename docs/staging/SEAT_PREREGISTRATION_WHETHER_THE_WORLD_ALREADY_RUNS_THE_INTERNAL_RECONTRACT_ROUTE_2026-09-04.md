**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: whether the world already runs the internal re-contract route §15 says it lacks

*Delivery seat, 2026-09-04, filed at `63cdcf76c` BEFORE any measurement of the capture and before
the reading module exists. Subject:
`SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`
§16.*

---

## What prompted this, and what is already established before the predictions

§15 closed the chain's φ sourcing with a result that runs against us and one owed item:

> *"What is now established, with no assumption beyond `J_svt ≥ 0`, is that **the dominant
> internal-switching route in the GB record is default/SVT households re-contracting with their own
> supplier — a route `simulation/renewals.py` does not model at all**."*
>
> *"One thing owed … **not φ, but `J_svt`** … unlike φ it names a mechanism the world is missing
> rather than a constant the world would have to be given."*

**Two things were read before this file was written, and neither is a prediction.** They are
established and are recorded here so that the predictions below cannot borrow credit for them.

1. **`simulation/renewals.py` L150–L168 builds an SVT stint bounded by the household's next
   anniversary, and then re-enters its own term loop.** The comment block says so in terms:
   *"WHY A PASSIVE STINT IS BOUNDED BY THE ANNIVERSARY AND NOT ABSORBING … Making SVT absorbing
   instead was the first draft and the published split refutes it: with no route back, the fixed
   share decays to 12% by the second renewal."* On re-entry `rolls_active_renewal` is drawn again,
   and an active draw builds **a fixed term with this same supplier**. That is a re-contract with
   the incumbent — `J_svt` — under a different name. §15's grep for `same_supplier` was correct;
   its conclusion that the route is not modelled does not follow from it, and this file exists
   because I read the mechanism rather than the label.

2. **The draw at that anniversary is `PASSIVE_RENEWAL_RATE = 0.35`, and 0.35 is sourced for a
   different event.** `docs/market_research/svt_rates_active_passive_2016_2025.md` §4 row 6:
   *"Fixed at expiry → active switch | ~35% | Inverse of SVT rollover share at expiry"*. It is a
   rate defined **at a fixed-term expiry**. `simulation/svt_product.py`'s own docstring says the
   product it is being applied to has *"No term boundary … A segment ending is a price change, not
   an expiry: nothing is renewed, nothing is offered, and the household makes no decision"*. One
   published anchor, two uses, and the second use is the one that sets how long an account stays on
   the SVT product. Nothing in the tree sources the second use.

Neither of those is measured yet. What follows is.

## What will be measured, and on what

`docs/reports/c6_second_pass_departure_factors_svt_segment_decisions.json` — the committed capture
the whole chain has used, at `NO_LEVEL_CORRECTION`, with no new run and no re-fit. The reading is
of the world's **internal re-contract rate**: SVT stints that end with the account still on the book
and back on a fixed term, per SVT account-year, and per account of the whole book.

The record it is compared against is §15's own register, `SWITCHER_SPLIT_OBSERVATIONS` — Ofgem CIM
question C4's *"switched tariff with the same supplier"* row, base all respondents, six waves.
**The comparison keeps §15's conservative direction**: the record's row is a SIX-MONTH recall and
the world's rate is ANNUAL, and the world's annual figure is compared against the record's
six-month one without annualising the record. Where that comparison says the world is short, it is
short by at least that much.

## The predictions

- **P1 — The world HAS the route, and §15's sentence is refuted as a claim about the mechanism.**
  The capture will contain SVT stints that end with the account returning to a fixed term rather
  than departing. Predict **more than 100** such returns across 2016–2025. If it is zero, the code
  I read at L150–L168 does not reach this capture and the whole section is withdrawn — that is the
  falsification, and unlike §12's P1 it is a real one, because the two states are genuinely
  distinguishable in the artefact.

- **P2 — The internal return rate per SVT account-year lands in [0.28, 0.42] in non-2022 years, and
  is exactly 0.0 in 2022.** The 2022 half is near-certain and is filed because
  `CRISIS_PASSIVE_YEARS` forces every draw passive, so an internal return in 2022 would mean the
  crisis forcing does not reach this call site. The [0.28, 0.42] half is the one that can fail: the
  per-household engagement archetype threads a distribution through the 0.35, so the realised rate
  need not centre on it, and a household that departs mid-stint never reaches its anniversary.

- **P3 — On the CIM base, the world is BELOW the record in at least 4 of the 6 waves, comparing the
  world's ANNUAL rate against the record's SIX-MONTH row.** Reasoning: the world's internal rate
  over the whole book is roughly the SVT stock share (§10 measured 0.43–0.72 of account-days) times
  the anniversary draw, so 0.15–0.25 a year, against a record row of 0.110–0.170 per six months.
  That is closer than I would like and the prediction may fail in either direction; I hold it at
  about 65/35. **The waves covering 2022 are excluded from the "at least 4" because the world's
  2022 is a forced zero and would flatter the claim** — the count is over W4, W5, W6 and any wave
  whose window touches a non-2022 year, and if that leaves fewer than 4 judgeable waves the
  prediction is graded on the fraction instead and said so.

- **P4 — `exposure`, §9's second factor, is this route seen from the other side.** §9 measured
  exposure at 0.64–0.81 with no account of what sets it. Predict that in every fitted year the
  internal return is the ONLY way a surviving account leaves the SVT product in this world, so
  `1 − exposure` is attributable to the anniversary return plus mid-window arrival and to nothing
  else. Gradeable by enumerating the exits from `build_svt_schedule`'s callers: if a third exit
  exists, this is refuted.

- **P5 — This does not close rung 1, and that is knowable before the reading runs.** §9's
  saturation bound put reach and exposure at their ceilings **together**, abolishing the renewal
  route with them, and reached the band's low endpoint in 1 year of 7. The internal return is a
  mechanism *inside* exposure, so abolishing it entirely cannot do more than that bound already
  did. Predict the reading states this, claims no repair to rung 1, and that
  `emergent_level_verdict` is unmoved at six of seven outside their bands. **A section that came
  back claiming this closes rung 1 would be a section that had double-counted, and this prediction
  is here to make that visible rather than to be collected.**

- **P6 — Constraint 4, a twelfth time.** No constant edited, no solver aim point moved,
  `YEAR_LEVEL_ANCHOR` untouched, `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` still `None`, and
  `PASSIVE_RENEWAL_RATE` still 0.35 — the finding that its second use is unsourced is a finding and
  not a licence to change it. Verified by a **structural walk over the parsed artefacts**, not by a
  line diff: §14's P8 lesson, applied.

## What this pass will NOT do

It will not source `J_svt`. §15 handed that on as the owed item and it stays owed; what changes is
that it is owed as a **check on a mechanism the world already runs** rather than as a mechanism to
build. It will not change `PASSIVE_RENEWAL_RATE`, and it will not re-run the world — the capture is
the subject, as it has been since §9.

— Delivery seat, 2026-09-04.
