# The GB domestic external/internal switcher split: Ofgem CIM waves 1–6, 2022–2025

**Research completed 2026-09-04, delivery seat, Lane 0.** Live source fetched this pass: Ofgem's
*Consumer Impacts of Market Conditions* (CIM) survey, wave 6 — main report (PDF) and **data tables
(XLSX, 26MB)**, both parsed locally. The data tables carry all six waves in one banner, so one fetch
supplies the whole series.

**Opened by:**
`docs/staging/SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`
§11, restated by §14 as *"one thing owed, and it is now the only one"*.
**Pre-registration:** `docs/staging/SEAT_PREREGISTRATION_WHETHER_A_PUBLISHED_SWITCHER_SPLIT_CAN_CLOSE_PHI_AT_ALL_2026-09-04.md`,
filed before the fetch. **One home in code:** `tools/published_route_split.SWITCHER_SPLIT_OBSERVATIONS`.

---

## 0. What was wanted, stated before the source is described

φ — `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` — is *the share of households actively renewing at a
fixed-term end who move to a **different supplier**, rather than taking a new deal with their
existing one.* It is `None` in the tree with a named reason, and the identity
`R = s·H_svt + (1−s)·0.35·φ` cannot pin the SVT hazard without it.

**The tree was searched before the web, per §14's own instruction, and it was dry.** What it holds
and why none of it is φ is tabulated in the pre-registration and not repeated here. The one thing
worth carrying forward: `simulation/renewals.py` and `renewal_engagement.py` contain **no
internal-switch concept at all** — no `same_supplier`, no retention move, no re-contract. So there
was no in-tree value that could have been mistaken for this one.

---

## 1. The instrument, and that it is behaviour rather than intention

**Ofgem Consumer Impacts of Market Conditions survey, question C4:**

> *"Which, if any, of these have you or your household done **IN THE PAST 6 MONTHS**?"*
> Base: **all respondents**.

Its response options include, as **separate codes on the same base**:

- *"I/we have switched to a new supplier"* — **external**
- *"I/we have switched tariff with the same supplier"* — **internal**
- *"I/we have compared energy tariffs but have not switched"*
- *"None of these"*

This is the cross-tabulation the finding has asked for since §11. It is **reported behaviour**, not
intention — the wave-6 report separately publishes a *likelihood over the next three months* series
(28% likely to switch tariff with existing supplier, 25% likely to switch to a new supplier), and
that intention series is **not** used here. Intention and behaviour are two different quantities and
this project has paid for treating one as the other.

---

## 2. The series, all six waves, weighted

Source: wave 6 data tables, sheet `W2W Tables`, **Table 108** (Total banner). Weighted counts as
published; shares derived. `Net` is the survey's own union of the two switching actions.

| wave | fieldwork | base (unw.) | switched **supplier** | switched **tariff, same supplier** | net switched | **φ_survey** |
|---|---|---|---|---|---|---|
| W1 | March 2022 | 2,944 | 9.32% | 13.18% | 22.01% | **0.4237** |
| W2 | July 2022 | 2,984 | 8.30% | 12.48% | 20.77% | **0.3994** |
| W3 | November/December 2022 | 3,457 | 7.30% | 14.49% | 21.79% | **0.3351** |
| W4 | July 2023 | 3,434 | 4.60% | 11.04% | 15.64% | **0.2939** |
| W5 | January 2024 | 3,439 | 5.58% | 11.59% | 17.17% | **0.3251** |
| W6 | January/February 2025 | 3,458 | 5.29% | 17.02% | 22.31% | **0.2371** |

`φ_survey` = external ÷ **net**, not ÷ the sum. **In W1 the two differ**: its rows sum to 14.4
weighted respondents more than its published union, so 14.4 respondents reported *both* actions.
In W2–W6 the union equals the sum. A reading that summed would agree with this one in five waves and
disagree in the sixth, which is exactly the kind of silent divergence a register exists to prevent.

**The trend is the striking part.** External switching roughly halves across the series (9.3% → 5.3%)
while internal switching rises (13.2% → 17.0%). W6 is, in Ofgem's own words, *"the highest proportion
since tracking began of consumers who said they had switched tariff with the same supplier, whereas
the proportion who switched supplier is at its joint lowest"*.

---

## 3. What this does NOT establish, and it is the main result

**φ_survey is not φ, and it is not a bound on φ in either direction.**

The survey's base is *all households*. Both of its rows therefore mix the two routes:

```
E  =  s·H_svt  +  (1−s)·0.35·φ          ← external. This IS the published record's R.
I  =  s·J_svt  +  (1−s)·0.35·(1−φ)      ← internal. The survey's new row.
```

`J_svt` — the rate at which **default/SVT households move onto a fix with their existing supplier** —
is published nowhere. The survey supplies one new equation and one new unknown with it, and an
equation that arrives carrying its own unknown identifies nothing. φ_survey is a *mixture* of the two
routes' external shares, weighted by how much switching each route produces.

**The tariff-type banner does not rescue it, and reaching for it is the trap.** Table 109 breaks C4
by the respondent's tariff type, giving φ_survey of 0.221–0.398 among fixed-tariff respondents and
0.356–0.540 among variable-tariff respondents. **Tariff type is recorded *after* the switch**, so a
household that switched onto a fix is counted in the fixed column whichever route it came from. This
is precisely the outcome-contamination `household_switching_response_amplitude.md` §2.4 recorded for
this survey family — *"recorded here so the next session does not reach for the biggest number on
the page"* — and the warning applies to this reading too. **The figures are quoted so the next
session does not have to re-fetch 26MB to learn they are unusable, and they are not used.**

`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is therefore **still `None`**, and it has a better-documented
reason than before.

---

## 4. What it DOES establish, needing only `J_svt ≥ 0`

Drop φ entirely. The fixed-renewal route's internal output is `(1−s)·0.35·(1−φ)`, so its **ceiling**
— the most internal switching it can produce at any φ — is `(1−s)·0.35`, at φ = 0. Internal
switching above that ceiling cannot have come from the renewal route **at any value of φ**.

Taken at the **largest** published fixed share across every calendar year each recall window touches
(`tools/published_tariff_mix`), and with the survey's **six-month rate not annualised** — both
choices conservative, both pushing against the conclusion:

| wave | internal rate (6 mo.) | renewal-route ceiling (annual) | multiple |
|---|---|---|---|
| W1 | 13.18% | 7.00% | **1.88×** |
| W2 | 12.48% | 7.00% | **1.78×** |
| W3 | 14.49% | 7.00% | **2.07×** |
| W4 | 11.04% | 7.00% | **1.58×** |
| W5 | 11.59% | 7.00% | **1.66×** |
| W6 | 17.02% | 12.60% | **1.35×** |

**Six waves of six, every one over its ceiling**, comparing a six-month rate against an annual bound
at the most generous share the record allows. Annualising would roughly double the left column.

> **So most GB domestic internal switching is default/SVT households moving onto a fixed deal with
> their existing supplier. It is not fixed-term renewal at all — there are not enough fixed-term
> households in the record for it to be.**

---

## 5. Why that matters to the thing the finding is actually repairing

§9 of the finding put the world's departure shortfall onto one quantity — the hazard per
SVT-account-year, short by 1.67× and 1.71× — and closed by asking a question it could not settle:

> *"the hazard is drift off the SVT **product**, and the band it is being asked to reproduce is
> external change of **supplier**. Those are not the same event, and nobody has established the
> relation."*

**§4 above is the published half of that relation, and it runs the unfavourable way.** SVT households
leave the SVT product by two routes, and the record's band counts only one of them. `SVT_INERTIA_
ANNUAL_RECENT = 0.20` is sourced as a *product-drift* rate; the share of that drift which is external
is below 1, so the external rate it implies is **below 0.20**, and §9's gap against the record's
required 0.334–0.342 is **wider** than the 1.67×–1.71× already published, not narrower.

The size of the widening is not quoted, because `J_svt` is what would set it and `J_svt` is the
unknown this whole section is about. **A direction with no magnitude is what the evidence supports,
and it is written as that.**

---

## 6. What would still close φ, named so the next attempt does not repeat this one

1. **A route-conditioned instrument**: the internal/external split asked of households *at a
   fixed-term contract end*, rather than of all households. Ofgem's CIM does not condition on the
   respondent's contract status at the time of the move; nothing located this pass does.
2. **`J_svt` directly** — the rate at which default-tariff households take a fix with their existing
   supplier. This would close the system by supplying the unknown rather than the ratio, and it is
   the *easier* of the two to imagine a supplier-returned series carrying.
3. **Not the tariff-type banner**, for the reason in §3. Named here because it is the obvious next
   reach and it does not work.

---

## 7. Sources

- Ofgem, *Consumer impacts of market conditions survey: wave 6 (January to February 2025)* —
  https://www.ofgem.gov.uk/research/consumer-impacts-market-conditions-survey-wave-6-january-february-2025
  (page fetched 2026-09-04)
- **Data tables (the series above):** `Consumer impacts of market conditions survey wave 6 data
  tables.xlsx`, https://www.ofgem.gov.uk/sites/default/files/2025-07/Consumer%20impacts%20of%20market%20conditions%20survey%20wave%206%20data%20tables.xlsx
  (fetched and parsed 2026-09-04; sheet `W2W Tables`, Table 108 for the Total banner, Table 109 for
  the tariff-type banner)
- Ofgem, *CIM Wave 6 Main Report* —
  https://www.ofgem.gov.uk/sites/default/files/2025-07/CIM%20Wave%206%20Main%20Report.pdf
  (fetched and `pdftotext`-parsed 2026-09-04; the C4 narrative and question wording)

**In-repo, followed rather than re-derived:** `gb_switching_rate_denominators.md` §7 (which already
recorded CIM waves 5 and 6 by *stated reason* and stated that the domestic instrument *"does not
split it"* — true of the reason codes it was reading, and not of question C4);
`household_switching_response_amplitude.md` §2.4 (the outcome-contamination warning §3 above obeys);
`svt_rates_active_passive_2016_2025.md` §4 (the 0.35 that is φ's denominator);
`tools/published_tariff_mix` (the fixed-share bands §4 takes its ceiling at).
