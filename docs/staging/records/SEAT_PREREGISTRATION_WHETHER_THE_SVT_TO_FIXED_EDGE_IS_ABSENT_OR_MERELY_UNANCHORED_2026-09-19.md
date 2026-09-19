**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** the world's product mix

# Pre-registration: is the SVT → fixed edge ABSENT from this world, or present-but-unanchored?

**Filed 2026-09-19, delivery seat, claim `the-svt-household-has-no-route-back-to-a-fixed-term`,
BEFORE any measurement.** The drawn item's premise is a claim about this tree and therefore an
un-re-asked prediction; this file records what I expect to find before I look, so that whichever
way it lands the answer cannot be read as having been arranged.

---

## 1. The premise as drawn, verbatim in substance

> *"Today it cannot — `tariff_type` is resolved once per customer at schedule-build time and SVT is
> absorbing"*, citing
> `WORKER_FINDING_THE_SVT_CONVERSION_DECISION_IS_REAL_AND_THIS_WORLD_HAS_NO_EDGE_THAT_CAN_EXPRESS_ITS_OUTCOME_2026-09-18.md`
> §3.3, whose three bullets are: `tariff_type` resolved once per customer; the fixed → SVT edge
> exists mid-tenure; **"There is no reverse edge."**

## 2. What I predict, before running anything

**P1 — the premise is FALSE at the TERM level, and the finding's own §3.3 bullet 2 is the reason.**
Reading `simulation/renewals.py` C1b and `run_phase2b._build_gas_renewal_schedule` C1b: a passive
roll does **not** rebuild "the remaining decade". Both builders bound the stint at
`term_start + CONTRACT_LENGTH_DAYS - 1` and then `continue` the term loop, so the household is
re-asked at its next anniversary and an active roll builds it a fixed term. Electricity's own C1b
comment says so in terms — *"WHY A PASSIVE STINT IS BOUNDED BY THE ANNIVERSARY AND NOT ABSORBING …
Making SVT absorbing instead was the first draft and the published split refutes it"*. So I expect
to find households holding `svt` terms and later `fixed` terms in the same schedule, and the
`DONE` condition of the drawn item to be **already met** before I write a line.

**P2 — the premise is TRUE at the CUSTOMER level, and that is a different, smaller defect.** Both
builders open with `if tariff_type == SVT_TARIFF_TYPE: return build_svt_schedule(...)` to
`report_end` — no loop, no anniversary, no roll. A record arriving already ON the product is
genuinely absorbing. This is §3.3's third bullet stated precisely: *"no caller re-enters the term
builder for a household already on SVT."*

**P3 — but I expect NO live producer of such a record.** `population_draw.CustomerRecord.tariff_type`
defaults to `None` and `resolved_tariff_type` maps `None → "fixed"`. If that holds across every
producer, the absorbing branch of P2 is **unreachable in a run today**, and repairing it is
repairing a trap rather than a live defect — which changes what honest delivery looks like and must
be said out loud rather than quietly upgraded into a bigger claim.

**P4 — what is genuinely missing is an ANCHOR, not an edge.** The reverse edge is governed by the
same `rolls_active_renewal(..., active_renewal_probability_for_customer(household))` as the forward
one, so this world's SVT → fixed conversion hazard is **identical by construction** to its
fixed-term active-renewal rate. The published record does not say they are equal: CIM wave 6
Table 56 reads variable-tariff households at 2.5% and fixed-tariff households at 7.0% on switching
supplier in six months (`what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` §3). I
predict **no in-tree constant** names an SVT-side conversion rate, and no published source in
`docs/market_research/` establishes one conditioned on being on SVT — the 13.18% internal-switch
code is on a base of all domestic respondents, not of SVT households.

## 3. How each prediction gets refuted

| prediction | the measurement that would refute it |
|---|---|
| P1 | build the world's real electricity + gas schedules; count households whose term sequence contains `svt` followed later by `fixed`. **Zero such households refutes P1.** |
| P2 | call each builder with `tariff_type="svt"` and read the distinct `tariff_type` values of what comes back. Anything other than `{"svt"}` refutes P2. |
| P3 | grep every assignment to `tariff_type` reaching a customer record. Any producer emitting `"svt"` refutes P3. |
| P4 | grep `simulation/` and `tools/` for a constant conditioned on SVT tenure that governs a move ONTO a fixed term. Finding one refutes P4. |

## 4. What I will do with each outcome, decided now

- **P1 confirmed** → the item's `DONE` is already met by code that predates the claim; I say so
  plainly, do **not** claim credit for it, and deliver against P2/P4 instead — the parts that are
  really missing. A reachability control over the term-level edge is still owed, because nothing
  today asserts the edge can be taken and a silent regression to the refuted absorbing draft would
  pass every existing test.
- **P1 refuted** → build the term-level edge, as drawn.
- **P2 + P3 confirmed** → close the absorbing branch anyway, because it is one `return` away from
  being live the moment any producer assigns the product, and say in the record that it was a trap
  and not a live defect.
- **P4 confirmed** → **declare the gap; mint nothing.** The code carries an honest `None` with its
  named reason, per the item's own instruction and the 2026-09-18 finding §5's third "not to be
  done as a shortcut" — the CIM 9.32/13.18 ratio must not be differenced into an SVT-side leg.

## 5. Not in scope, recorded so the boundary cannot drift

No company-side conversion or targeting desk. `UPLIFTABLE_TARIFF_TYPES` is not relaxed.
`SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md` §3 stands. The
fidelity argument is made blind to company results (R13): whether the value arm's reachable
population grows is a consequence and is not a reason appearing anywhere in the reasoning above.
