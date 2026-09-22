**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "SVT internal conversion ceiling needs annualisation to bite"

# The fact the ceiling asked for cannot tighten it, and the floor is the live side of the band

*Nothing is broken. A published bound was read as the side that can refuse and it is the side that
cannot, and the repair the record invited does not exist. Left alone, the next invocation spends a
turn looking for a number that would have moved the bound the wrong way.*

**Delivery seat, Lane 0, 2026-09-19.** Claim
`svt-internal-conversion-ceiling-needs-annualisation-to-bite`. **Pre-registration:**
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_PUBLISHED_INSTRUMENT_ANNUALISES_THE_CIM_INTERNAL_ROW_AND_WHICH_SIDE_OF_THE_BAND_IT_WOULD_MOVE_2026-09-19.md`,
filed before any fetch. All four of its predictions are graded in §4, including the one that was
wrong.

---

## 1. What was asked, and the answer

The claim asked whether a published GB domestic instrument supports annualising the CIM six-month
internal-switching rate, on the stated motive that *"a repeat-switching figure is the single
published fact that turns this bound from live into firing"*.

**Two answers, and the second is the one that matters:**

1. **No instrument supplies it.** A twelve-month reading of the same event exists and cannot be
   used; the one frequency question that exists is the wrong event on the wrong window. §3.
2. **It would not do that if it did.** The annualisation factor is in [1, 2] for every population
   by inclusion–exclusion, so an annual ceiling is *at least* the six-month bar. **The bar already
   in force is the tightest annual ceiling the published record can ever support.** No evidence
   about repeat switching can tighten it, because a repeat figure bounds the both-halves overlap
   from ABOVE and a tighter ceiling needs it bounded from BELOW.

**And the fact is real evidence — about the other bound.** `P12 ≥ 2p/(1+r)` raises the *floor*,
from 0.0449 at total repetition to 0.1676 at none. The floor in force is the `r = 1` corner of that
family: **not un-annualised, but annualised at the most conservative repetition there is.**

## 2. The consequence: which side of the band is live

| | six-month reading (as landed) | annual reading (this work) |
|---|---|---|
| ceiling | 0.2659, world at **0.70** of it, 4 years above | [0.2659, 0.5319], world at **0.35–0.70** |
| floor | 0.0449, world at **4.14×** | [0.0449, 0.1676], world at **1.11–4.14×** |

`svt_internal_conversion_ceiling` landed under the heading *"the side that can refuse"*, and against
a six-month bar it looked like it. **In the world's own units the floor is the closer bound**, and
it is the one a change to the SVT-side decision could actually trip. Both sentences are left
standing where they are written; the correction sits beside them, in
`_internal_return_vs_the_annualised_band` and in §4c of the research file.

**The four above-ceiling years (2018, 2021, 2023, 2025) get FURTHER from a breach**, not closer.
They were recorded as not being breaches and that recording is now permanent rather than pending
evidence.

## 3. What the search found

| located | what it is | why it is not the fact |
|---|---|---|
| Ofgem RMR / Consumer Engagement survey, 12-month internal switching: 16% (2014), 17% (2015), 15% (2018) | a twelve-month reading of the SAME event | no year overlaps a CIM wave (ends 2018, CIM begins 2022); face-to-face vs CIM's online panel; this family's self-report already measured at ~1.5× the record |
| Ofgem RMR 2015 Q21/Q22, *"how many times have you ever switched"* | the only frequency question located | **external** not internal; **lifetime** not annual |
| DESNZ/Ofgem transfer counts (`table_271__2_.xlsx`) | meter-point transfer volumes | no household in the series at all; external only |

**The twelve-month series is held in code anyway** (`TWELVE_MONTH_INTERNAL_SWITCHING_OBSERVATIONS`).
*"We looked and found nothing"* sends the next session back to the same fetch; *"we found a series
that cannot be used, and here is why"* does not.

`REPEAT_INTERNAL_SWITCH_SHARE_WITHIN_A_YEAR` is `None`. **This is the fourth refusal of the same
fact** — after `svt_internal_conversion_floor`, `_internal_return_vs_record` and
`_internal_return_vs_the_published_ceiling` — and the claim that drew this work named a quietly
reversed fourth refusal as the defect to avoid. It is not reversed; it is now refused on **direction
as well as availability**, which is a stronger refusal than the first three carry, and one test leg
exists only to red if a number ever appears there.

## 4. The pre-registration, graded — including the one that was wrong

| | prediction | outcome |
|---|---|---|
| **P1** | a repeat figure cannot tighten the ceiling | **HELD.** Now in code and mutation-proven. |
| **P2** | the same figure tightens the floor, 0.0449 → toward 0.1676 | **HELD, to the digit.** The `r = 1` corner reproduces the landed floor exactly, which is the join asserted by a test. |
| **P3** | no instrument gives `r` **or a 12-month internal incidence on a comparable base** | **HALF WRONG, and recorded as such.** I predicted the twelve-month *window* would not be published. It is — 2014, 2015, 2018 — and I had put ~0.75 on the other reading. The half that held is the comparability half: no year overlaps CIM. Had I stopped at "nothing published", the finding would have been true in conclusion and false in its reason, and the next session would have re-fetched. |
| **P4** | what would land | **HELD**, plus the band-inversion in §2, which I did not predict and which is the most useful thing here. |

## 5. What this record travels with

*Named as the contents of the commit that carries this file, not as a landing claim: the commit is
the evidence, and a record asserting its own artefacts landed before one exists is the shape
`tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py` refuses.*

- `tools.published_route_split.svt_internal_conversion_annualisation` — the reading; the factor
  band as structural arithmetic, the floor family indexed by `r`, the twelve-month series and why
  it is unusable, and the refusal.
- `tools.fit_year_level_anchor._internal_return_vs_the_annualised_band` — the world beside both
  bounds in annual units, with the live side **derived** and printed by `--internal-return`.
- `tests/tools/test_annualising_the_internal_row_moves_the_floor_and_never_the_ceiling.py` — 9
  legs. Five mutations run: factor band's lower endpoint 1.0 → 0.5, the annualisation dropped from
  the floor family, the live-side verdict frozen to `FLOOR`, the floor's direction sentence blanked,
  and the ceiling's sentence reused for the floor. **The fourth did not fire on the first attempt**
  — inequality of two sentences is satisfied by blanking one — so the leg was strengthened to
  require each sentence to NAME its own bound, and both then fired.
- §4c of `docs/market_research/gb_domestic_switcher_split_cim_2022_2025.md`; the knowledge map's
  two `J_svt` cells.

## 6. What is still open

**`J_svt` is still `None` and this did not move it.** A band is not a point estimate and neither
corner of the family is one.

**The floor is now worth tightening and the ceiling is not.** Any future work on this band should
go at `r` — the share of a year's internal switchers who switch internally more than once — or at
an instrument following the same households across two consecutive half-years. **Both bounds are
built from an INCIDENCE and the world's figure is an EVENT count** (returned stints over exposure);
they coincide only at the `r = 0` corner, and away from it the world's numerator is the larger,
which flatters the floor verdict and harshens the ceiling one. That is recorded in
`what_this_cannot_say` and is the next thing a sharper floor would have to settle.
