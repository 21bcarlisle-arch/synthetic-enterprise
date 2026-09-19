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

## 4a. The other side of the bound, added 2026-09-19: a CEILING on `J_svt`

**Added by claim `svt-internal-conversion-needs-a-ceiling-not-a-better-floor`. Pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_RECORD_SETS_A_CEILING_ON_J_SVT_AND_WHETHER_THE_BANNER_RULED_OUT_FOR_PHI_IS_ADMISSIBLE_ONE_SIDED_2026-09-19.md`.**

§4 above netted the renewal route's ceiling off `I` to bound `J_svt` from BELOW, and that floor
landed as `tools.published_route_split.svt_internal_conversion_floor` at 0.0449. The world it judges
runs at 0.1859 — **4.14× the floor, so the floor refuses nothing.** The same identity gives the
other side, and it needs *less*:

```
I = s·J_svt + (1−s)·0.35·(1−φ),   and (1−s)·0.35·(1−φ) ≥ 0 at φ = 1   ⟹   J_svt ≤ I / s
```

`φ ≤ 1` is the definition of a share, not an assumption about one. **Every conservative choice
inverts relative to the floor** — smallest published default share rather than largest, maximum
across waves rather than minimum — because for an upper bound the safe direction is upward:

| wave | I (6 mo.) | s_min | **ceiling on `J_svt`** | banner-tightened (§4b) |
|---|---|---|---|---|
| W1 | 0.1318 | 0.80 | 0.1648 | 0.1406 |
| W2 | 0.1248 | 0.80 | 0.1560 | 0.1246 |
| W3 | 0.1449 | 0.80 | 0.1811 | 0.1392 |
| W4 | 0.1104 | 0.80 | 0.1380 | 0.1071 |
| W5 | 0.1159 | 0.80 | 0.1448 | 0.1196 |
| W6 | 0.1702 | **0.64** | **0.2659** ← binding | **0.2389** ← binding |

**The six-month convention flips its sign here and that is the trap.** §4 and the floor both rely on
a six-month rate being a valid *annual* floor — a year carries at least a half-year's switching. The
identical fact makes a six-month rate **not** a valid annual *ceiling*: a year can carry up to twice
a half-year's, and bounding that above needs the repeat-switching assumption this file has declined
to make twice. So **`below` is the established verdict and `above` establishes nothing.**

## 4b. The tariff-type banner is inadmissible for φ and admissible ONE-SIDEDLY for this ceiling

§3 rules Table 109 out and §6.3 names it as the obvious reach that does not work. **That stands for
φ and it does not stand for an upper bound on `J_svt`, because the contamination runs the safe
way.** A `J_svt` event *is* a move onto a fix, so the household is on a fixed tariff when asked, so
every `J_svt` event lands in the **Fixed** column. Dropping the Variable column can only discard
non-conversions — SVT households taking a different *variable* tariff with the same supplier, which
are internal switches and are not `J_svt`.

Table 109's internal row (*"switched tariff with the same supplier"*), weighted, all six waves —
fetched and parsed 2026-09-19 from the same workbook §7 records:

| wave | base (wtd) | internal, **Fixed** | internal, **Variable** | sum | Total row | fixed ÷ all hh |
|---|---|---|---|---|---|---|
| W1 | 2,873.69 | 323.1437 | 55.6556 | 378.7993 | 378.7993 | 0.11245 |
| W2 | 2,954.50 | 294.5112 | 74.1248 | 368.6360 | 368.6360 | 0.09968 |
| W3 | 3,457.00 | 384.9075 | 115.9518 | 500.8593 | 500.8593 | 0.11134 |
| W4 | 3,434.00 | 294.3085 | 84.8972 | 379.2057 | 379.2057 | 0.08570 |
| W5 | 3,439.00 | 328.9266 | 69.5202 | 398.4468 | 398.4467 | 0.09565 |
| W6 | 3,458.00 | 528.7749 | 59.7502 | 588.5251 | 588.5251 | 0.15291 |

**The two columns partition the internal switchers exactly, in every wave** — checked in code
(`the_banner_partitions_the_internal_switchers`) rather than assumed, because dropping a column is
only safe if the pair is exhaustive and the *bases* are a different question with a different
answer: they account for the whole base in W1–W5 and fall **15 unweighted respondents (0.46%) short
at W6**, where some respondents have no tariff type recorded. None of those 15 reported an internal
switch, which is why the switchers still partition at W6. It is the switchers that must be
exhausted here, and they are.

**What the assumption is worth, priced rather than caveated:** the two ceilings differ by *exactly*
the Variable column's internal switchers. If every one of those were a conversion whose mover
mis-reported their new tariff, 0.2389 would be wrong and 0.2659 would still be right. **So 0.2659 is
the published bar and 0.2389 is carried beside it**, in `svt_internal_conversion_ceiling`.

**A tension worth recording, not resolved here.** The banner's own base says 61.9% of W6 respondents
are on a fixed tariff (2,141 of 3,458 weighted), while `published_tariff_mix` puts the 2025 GB fixed
share at 30–36% from Ofgem's State of the Market. Self-reported tariff type and the market statistic
disagree by nearly a factor of two. It does not touch the ceiling above — that argument needs only
where a conversion *lands*, never what the banner's base is a share of — but **any future use of
these columns as a population share has to settle it first**, and this paragraph is here so the next
session does not discover the disagreement after building on it.

## 4c. Annualisation, added 2026-09-19: it moves the FLOOR, and it cannot move the ceiling at all

**Added by claim `svt-internal-conversion-ceiling-needs-annualisation-to-bite`. Pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_PUBLISHED_INSTRUMENT_ANNUALISES_THE_CIM_INTERNAL_ROW_AND_WHICH_SIDE_OF_THE_BAND_IT_WOULD_MOVE_2026-09-19.md`,
filed before the fetch.** §4a closes by saying a six-month rate is not a valid annual ceiling and
that bounding one *"needs the repeat-switching assumption this file has declined to make twice"*.
That sentence is true and it invites a repair that does not exist. **The question was asked and the
answer is that no evidence could ever tighten the ceiling**, so the invitation is withdrawn here.

Write `p` for a six-month incidence, `P12` for the twelve-month one, `q` for the share switching in
both half-years, `r` for the share of annual switchers switching more than once:

```
P12 = 2p − q        (inclusion–exclusion, exact)      0 ≤ q ≤ p        q ≤ r·P12
⟹  a = P12/p ∈ [1, 2] for every population           ⟹  P12 ≥ 2p/(1+r)
```

**A repeat-switching figure bounds `q` from ABOVE. A tighter ceiling needs it bounded from BELOW.**
So the fact the claim asked for floors the annual incidence and therefore raises the *floor*; the
ceiling moves up or not at all. Since `a ≥ 1`, **the six-month bar already in force is the `a = 1`
endpoint — the tightest annual ceiling the published record can ever support**, and the world's
four above-ceiling years are *further* from a breach in annual units, never closer.

| | six-month bar in force | annual, `a = 1` | annual, `a = 2` |
|---|---|---|---|
| **ceiling** | 0.2659 | **0.2659** ← the bar in force is this corner | 0.5319 |

The floor is the one-parameter family the same algebra gives, and **the floor in force is its
`r = 1` corner** — not un-annualised, but annualised at the most conservative repetition there is:

| `r` (share repeating within the year) | 0.00 | 0.25 | 0.50 | 0.75 | 1.00 |
|---|---|---|---|---|---|
| **binding floor on `J_svt`** | **0.1676** | 0.1185 | 0.0858 | 0.0624 | **0.0449** ← in force |

**Which inverts §4a's closing claim.** Against a six-month bar the ceiling looked like the live
side — the world at 0.70 of it, four years above. In annual units the world sits at **0.35–0.70 of
the ceiling and at 1.11–4.14× the floor**, so *the floor is the side of this band that can refuse*,
and it is where any future repeat-switching evidence lands. §4a's sentence is left as written and
this corrects it beside it. One home in code:
`tools.published_route_split.svt_internal_conversion_annualisation`.

### What the search found, and why none of it is usable

**A twelve-month reading of the very same event exists.** Ofgem's annual RMR / Consumer Engagement
survey (TNS BMRB, face-to-face) asks *"whether changed tariff with existing supplier in last 12
months"*: **16% (2014), 17% (2015), 15% (2018)** — the 2018 report adds that 2017 was *"similar"*
and that levels *"have not changed significantly since 2014"*, which is not a published figure and
so 2016–17 are not entered.

It does not annualise the CIM row, **for comparability and not for absence**: not one of its years
overlaps a CIM wave (it ends 2018, CIM begins 2022), its mode is face-to-face against CIM's online
panel, and `household_switching_response_amplitude.md` §2.2 has already measured this survey
family's self-report at about 1.5× the record's level. Dividing 0.15 by a CIM six-month rate yields
a number that is part annualisation, part instrument and part market regime, with nothing in it to
say which part is which. **It is held in code anyway** — `TWELVE_MONTH_INTERNAL_SWITCHING_
OBSERVATIONS` — because *"we looked and found nothing"* sends the next session back to the same
fetch and *"we found a series that cannot be used, and here is why"* does not.

**The one frequency question located is the wrong event on the wrong window.** Ofgem RMR 2015
Q21/Q22 — *"How many times have you ever switched your gas/electricity supplier"* — is **external**
rather than internal and **lifetime** rather than annual. `r` stays `None`
(`REPEAT_INTERNAL_SWITCH_SHARE_WITHIN_A_YEAR`), **a fourth refusal of the same fact**, and it is
now refused on direction as well as on availability.

**What would still supply it:** an instrument following the SAME households across two consecutive
half-years, reporting how many switched internally in both. Nothing located this pass does.

**Sources fetched and `pdftotext`-parsed 2026-09-19:**
`https://www.ofgem.gov.uk/sites/default/files/docs/ofgem_rmr_survey_2015_report_published.pdf`
(§1.2.3, Figures 1.4–1.5);
`https://www.ofgem.gov.uk/system/files/docs/2018/10/consumer_engagement_survey_2018_report_0.pdf`
(§3.2–3.3). Also checked and carrying no household-level repeat measure:
`sim/cache/desnz_switching/table_271__2_.xlsx` (DESNZ/Ofgem transfer counts — meter points, external
only, no household in the series, as `household_switching_response_amplitude.md` §1 already
records).

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
   **PARTLY CORRECTED 2026-09-19, beside the claim and not over it: it does not work for φ, which
   is what this list is about, and it DOES work one-sidedly for an upper bound on `J_svt`.** See
   §4b. The sentence above is left as written because the distinction it misses — a contaminated
   variable being useless for a share and usable for a bound when the contamination runs the safe
   way — is the thing worth carrying forward, and it is only visible next to the claim that missed
   it.

---

## 7. Sources

- Ofgem, *Consumer impacts of market conditions survey: wave 6 (January to February 2025)* —
  https://www.ofgem.gov.uk/research/consumer-impacts-market-conditions-survey-wave-6-january-february-2025
  (page fetched 2026-09-04)
- **Data tables (the series above):** `Consumer impacts of market conditions survey wave 6 data
  tables.xlsx`, https://www.ofgem.gov.uk/sites/default/files/2025-07/Consumer%20impacts%20of%20market%20conditions%20survey%20wave%206%20data%20tables.xlsx
  (fetched and parsed 2026-09-04; sheet `W2W Tables`, Table 108 for the Total banner, Table 109 for
  the tariff-type banner. **Re-fetched and re-parsed 2026-09-19 for §4b — the same workbook, same
  URL, `last-modified: Fri, 19 Jun 2026`, so the cells §2 records were re-read from the file they
  came from rather than trusted.** Table 109 rows *"I/we have switched tariff with the same
  supplier"* and *"Base: All respondents Answering"*, banner group *Tariff type*, columns
  `W1–W6 Fixed` and `W1–W6 Variable`.)
- Ofgem, *CIM Wave 6 Main Report* —
  https://www.ofgem.gov.uk/sites/default/files/2025-07/CIM%20Wave%206%20Main%20Report.pdf
  (fetched and `pdftotext`-parsed 2026-09-04; the C4 narrative and question wording)

**In-repo, followed rather than re-derived:** `gb_switching_rate_denominators.md` §7 (which already
recorded CIM waves 5 and 6 by *stated reason* and stated that the domestic instrument *"does not
split it"* — true of the reason codes it was reading, and not of question C4);
`household_switching_response_amplitude.md` §2.4 (the outcome-contamination warning §3 above obeys);
`svt_rates_active_passive_2016_2025.md` §4 (the 0.35 that is φ's denominator);
`tools/published_tariff_mix` (the fixed-share bands §4 takes its ceiling at).
