# Switching by tariff and by payment method: what the published record can grade, and the two drift-route changes it supports

**Knowledge:** how-households-choose

**Researched 2026-10-17, delivery seat, Lane 0, claim `w2-switching-gradient-knowledge-before-the-drift-fix`.**
Opened by `docs/staging/SEAT_FINDING_THE_WORLDS_PAYMENT_GRADIENT_IS_LOST_ON_THE_SVT_DRIFT_ROUTE_AND_ITS_TARIFF_GRADIENT_IS_AN_ERA_2026-10-17.md`.
This is the K8 page for its W-A and W-B, and the research pass for its W-C. **No world value is
changed by this page.** W-A is built after the 19 Oct publish, against the prediction already filed
in the finding.

Sources fetched and read this pass (the text quoted below was read from the documents themselves,
not from a search summary):

- CMA, *Energy market investigation, final report*, **Appendix 9.1: CMA domestic customer survey
  results** (24 June 2016), and the provisional-findings rendering of the same GfK survey,
  **Appendix 8.1: Customer survey** (July 2015). Same sample, same numbers where both state them.
  n = 6,999 weighted. Tariff and payment type are **from supplier records**, not self-report.
- Ofgem, *Consumer engagement in the energy market 2018* (report, October 2018), n ≈ 4,000.
- Ofgem, *Consumer impacts of market conditions survey wave 6 data tables* (XLSX, fetched again and
  parsed): sheet `Index` for the question wording; sheet `Tables`, Tables 28, 56, 57 and 65.

---

## 1. The question W-C asked, and the answer: the published split does not exist, and the surveys that look like one cannot be one

**Wanted:** the annual rate at which households leave their supplier, by the tariff they were on
**before** leaving (fixed term vs default/SVT), for 2016–2020. That is the quantity the world's
"fixed 0.120 /yr vs default 0.205 /yr, ratio 0.59" is.

**What is published, pre-crisis:**

| source | year | what it cuts | result |
|---|---|---|---|
| CMA App. 9.1 ¶48, Table 25 | 2015 | tariff from supplier records × switched supplier in the last year | 68% of respondents on SVT, 27% fixed; **37% of last-year supplier switchers on SVT**; 13% switched in the last year |
| CMA App. 9.1 Table 4 | 2015 | tariff × *ever* switched | fixed: 23% never switched supplier or tariff; SVT: 52% |
| Ofgem 2018 survey §3.5 | 2018 | "not switched supplier or tariff in 4 years" by payment method | SC 68%, PPM 57%, DD 42% |
| Ofgem 2018 survey §3.1–3.3 | 2018 | supplier and tariff switching, last 12 months, all households | supplier 18%, tariff 15%, either 26% |

The 2018 report does **not** cut switching by tariff type anywhere in its text. The CMA figures give
an implied fixed:SVT ratio of 12-month supplier switching, computed here:

```
P(switched | SVT now)   = 0.37 x 0.13 / 0.684 = 0.0703
P(switched | fixed now) = L x 0.13 / 0.271,  L = fixed share of last-year switchers
L lies in 0.28-0.63 (all "mixed/other/unknown" respondents switchers .. none of them)
ratio fixed:SVT  = 1.9 (L = 0.28)   3.7 (L = 0.54, proportional)   4.3 (L = 0.63)
```

and CIM w6 C4 gives 2.8 (fixed 7.0%, variable 2.5%). So **both** survey families, a decade apart,
show fixed-tariff households switching more. Neither says anything about the world's 0.59, and the
reason is exact rather than a caveat:

### 1a. The survey ratio is an identity in where switchers LAND, and the pre-switch gradient does not enter it

Both instruments record the tariff **after** the switch:

- **CIM w6, verified this pass.** Tariff type is question **A13**, *"A fixed term tariff is one
  where your unit rates and standing charge stay the same for the length of the contract you agree
  with your energy supplier. … Are you on a fixed term tariff for gas and electricity / gas /
  electricity?"*: present tense, asked in section A, before C4. The finding's §"tariff gradient"
  item 4 labelled this **unverified**. It is now verified. `gb_domestic_switcher_split_cim_2022_2025.md`
  §3 had already stated it for Table 109.
- **CMA 2015.** Tariff is from the supplier records the sample was drawn from (Annex C ¶13(b)(i)),
  and respondents *"who changed provider between when we received customer records from suppliers
  and when fieldwork was conducted"* were excluded. The record is the **current** supplier's, so a
  last-year switcher's tariff is the one it switched **onto**.

Write `L` for the share of recent switchers on a fix at interview and `F` for the fixed share of the
stock at interview. Then, from the survey's own margins:

```
ratio = [L·s / F] / [(1−L)·s / (1−F)]   =   L(1−F) / ((1−L)F)
```

The switching level `s` cancels, and **nothing about which tariff the switchers left appears**.
Both read on the fixed+SVT base (CMA's mixed/other respondents dropped). Checked against both
instruments: CMA (L = 0.593, F = 0.284) gives 3.68, the same as the direct calculation; CIM
(L = 0.822, F = 0.619) gives 2.84, against the published 2.8. Any
pre-switch gradient from 0 to infinity is consistent with the published margins, because the
pre-switch split of `s` is the one quantity the survey does not record.

**CIM's own internal-switch row shows how much landing contributes.** *"Switched tariff with the same
supplier"* reads **24.7% fixed vs 4.6% variable, 5.4×**. An internal switch is almost by definition a
move onto a fix, so that row is close to pure landing. The external row's 2.8 sits between that
5.4 and 1.

**A second distortion runs the other way and is not sized.** CMA ¶47: against supplier records,
84% of fixed-tariff customers identified their tariff correctly, and only **44%** of variable-tariff
customers did. CIM's self-reported base is 62% fixed against the market's 30–36%
(`gb_domestic_switcher_split_cim_2022_2025.md` §4b). SVT households that report "fixed" put
low-switching households into the fixed column. That pulls the CIM ratio **towards 1**. The CMA
figures use supplier records and do not carry this distortion.

### 1b. What this does to the finding, corrected there beside the claim

The finding's table sets the world's **drawn, pre-switch** ratio (0.59 in 2016–20, 2.61 in
2024–25) against the published 2.8 and reads the 2024–25 agreement as the world matching the survey
in the survey's years. **That comparison is not admissible in either era.** What the world would
show on the survey's instrument depends mainly on `L`. Printed on the finding's own exposure and rates
(one horizon, ignoring roll-off inside the window; arithmetic only, **not a measurement and not a
grade**):

| world era | fixed stock share | world pre-switch ratio | instrument ratio at L = 0.5 / 0.6 / 0.7 / 0.8 |
|---|---|---|---|
| 2016–20 | 0.41 | 0.59 | 1.3 / 1.8 / 2.5 / 4.1 |
| 2024–25 (6-month) | 0.21 | 2.61 | 3.8 / 5.5 / 8.3 / 13.8 |

At the CMA's own landing shares (L = 0.43–0.63 on the fixed+SVT base, 0.59 proportional), the
world's pre-crisis 0.59 gives 1.0–1.95, and about 1.7 at the proportional point. That sits at and
just below the bottom of the CMA's 1.9–4.3. Part of the gap is the stock-share difference between
the world (0.41 fixed) and the CMA's 2015 sample (0.28), because the identity scales with (1−F)/F. At CIM's L = 0.82, the world's 2024–25 rates
give well above the published 2.8. This printed table **inverts the finding's reading**: on the
instrument, the pre-crisis world is roughly where the CMA is, and the late world is the one that
would read high. The table is only suggestive. `L` for the world's own leavers is not modelled,
because the world does not follow a departed household onto its next tariff, and the 6-month CIM
window is approximated by halving annual rates.

**MEASURED 2026-10-17, same day, beside the claim: the arithmetic above was wrong.** The instrument,
emulated on the same book (closed cohort, 12 months, March 2016 – February 2021 pooled), reads
**1.98 / 3.27 / 3.70** at L = 0.43 / 0.593 / 0.63: inside the CMA's 1.9–4.3, just under the CMA at
each matched L. The 0.41 above is the exposure share; the fixed share at interview is 0.31, because
fixed terms roll to default inside the year. A power control then shows the instrument barely sees
the pre-switch gradient (g from 0.3 to 2.8 moves it 3.06 → 3.40), so the pass grades the stock share
F, not the split. See
`docs/staging/SEAT_FINDING_READ_THROUGH_THE_SURVEY_INSTRUMENT_THE_PRE_CRISIS_WORLD_SITS_INSIDE_THE_CMA_BAND_AND_THE_INSTRUMENT_CANNOT_SEE_THE_GRADIENT_2026-10-17.md`.

### 1c. The GAP, restated with its reason

**A pre-switch fixed vs default departure split is not published for any GB year this pass could
reach**, and the consumer-survey family **cannot** supply one, because it records tariff at
interview. The only instrument that could is supplier-returned: losses by the tariff the account was
on when lost. The CMA had those records and published no such cut in Appendix 9.1. Ofgem's RMI
publishes default-tariff stock and tenure, not losses by tariff. `SVT_INERTIA_ANNUAL_RECENT` stays as
it is. Nothing on file is a reason to move it in either direction, and that now includes the 2.8.

**What would close it:** a supplier-returned loss series cut by tariff at loss; or CIM microdata
with a "tariff before you switched" item. CIM w6 has no such item. C5b (reasons for switching) has
no "my fixed term ended" code, which was the other possible route and was checked.

**What the measurement can do instead, filed for a prereg and not run here:** emulate the instrument
in the world. Take `L` from the CMA (0.28–0.63, supplier records, 12 months) as an exogenous input.
Compute the world's post-switch ratio over 2015-like years. Grade it against 1.9–4.3. That is a test
the world can fail, and the drawn-ratio comparison was never one.
**Run 2026-10-17:** it passes, and the power control shows the pass grades F, not the gradient.
No emulation of this instrument can grade the pre-switch split either; the GAP's only closure is a
supplier-returned loss series cut by tariff at loss.

---

## 2. W-A: a payment-channel term on the SVT drift hazard

### What the rules require

Nothing prescribes a switching rate by payment method. The rules that bear on it set direction
only, and they apply on **every** exit route, the default tariff included:

- **Domestic objections** (Ofgem, *Decision on review of domestic objections*, 2016): a supplier may
  object to the transfer of a domestic customer in debt to it.
- **Debt Assignment Protocol** (since 2012): an indebted prepayment customer switches through the DAP,
  and above its debt threshold the switch is blocked.

Both are read in `svt_drift_by_payment_behaviour.md`. Neither is specific to a fixed-term end, so a
world in which the channel gradient exists at the term end and vanishes on the default tariff
contradicts the mechanism the rules describe.

### What published evidence says

- **CIM w6 C4 by payment method** (Table 56, all tariffs; the 2025 base is mostly variable for PPM):
  DD 5.6%, SC 5.7%, PPM 3.1% switched supplier in 6 months. PPM:DD **0.55**. This is
  `household_segments.CIM_SWITCH_RATE_BY_CHANNEL`.
- **Pre-crisis, on the default stock itself** (Ofgem 2018 §3.5): households that had not switched
  supplier or tariff in four years, the CMA-database proxy for 3+ years on default, are **SC 68%,
  PPM 57%, DD 42%**. CMA 2015 ¶50: the SVT share is lower among DD payers than among other payment
  types. So the payment gradient is present **on the default tariff** pre-crisis, in the direction
  W-A gives it. This is a stock measure, not a rate, and it is not used as a number.
- **CIM w6 C4B** (Table 57, households that had not switched in the past 6 months): "switched
  supplier in the last 2 years" is DD 22.1%, SC 22.2%, PPM 8.9%. That is a longer window with the
  same direction and a steeper gradient (0.40).

### What is unknown (GAP)

- **No published payment split of the SVT drift band** (`svt_drift_by_payment_behaviour.md`). The
  band itself is a structural inference (`svt_rates_active_passive_2016_2025.md` §4, confidence M).
- **The payment-method field has the same contamination as tariff type, in a known direction.**
  CIM records payment method at interview. A household that left a PPM and set up a direct debit
  with its new supplier is counted in DD. That makes the published 0.55 **more extreme** than the
  pre-switch gradient. Its size is not published. Credit→PPM migration is not a switching event and
  is not part of this (`gb_payment_method_migration_rates.md` row 3: PPM→credit has no published
  rate).

### Which choices the design makes, and why

1. **Use the existing factor, `engagement_multiplier_for_channel`, unchanged.** No new number. The
   gate and the drift route then carry one statement of the gradient rather than two that could
   diverge.
2. **Normalise over the population's drawn channel mix, as the gate does, not over the SVT stock.**
   The SVT stock holds a little more PPM than the population, so the book's total drift falls
   slightly. The finding's prediction (total drawn switches move by less than 3%) grades exactly
   that. Normalising over the SVT stock instead would hold the band level exactly. It would also need
   a second normaliser computed from a population the world builds as it runs, which is the shape
   `_channel_population_shares` was written to avoid.
3. **Aim below the full 0.55, not at it (F11).** Because of the contamination above, the true
   pre-switch gradient is at or above 0.55 (less extreme). The finding's band of 0.50–0.70 is kept.
   A result below 0.50 would be over-correction, and it would count against the build, not for it.
4. **Named double-count risk, to be measured in W-A's run rather than argued.** On the fixed-term
   route, the archetype mix already carries part of the published marginal (drawn PPM:DD 0.52 =
   factor 0.59 × mix). On the drift route the archetype contributes ~0.98 net, because low-E PPM
   households stay longer on SVT. So the factor should land near 0.58 there and not compound.
   If the whole-book ratio comes in below 0.50, this is the first suspect.

---

## 3. W-B: an active household at an SVT anniversary converts to our fix, and never shops

### Correction to the direction, beside it

The work item says W-B would use *"phi from gb_domestic_switcher_split_cim_2022_2025.md"*. **φ is not
a value there.** `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is `None` with a named reason. It is also the
wrong quantity: φ is the external share at a **fixed-term end**, and W-B is about the **default
tariff**. The quantity W-B needs is the external share of default-tariff movers, `H_svt / (H_svt +
J_svt)`, in the notation of that note's §3.

### What the code does now, and why it is not simply a leak

`customer_events.departure_rolled_at_renewal` returns False after an SVT segment **on purpose**
(91214c720). SVT exits are carried whole by the drift hazard (`inertia_hazard_for_term`), whose
all-cause band is what SVT departures are graded against. A second roll at the anniversary ran SVT
exits about 29% above the band. So the **level** of default-tariff exits is held. What W-B questions
is **who** leaves. An active household is offered a conversion at each anniversary and takes it, so
it leaves the drift-hazard population. The households left drifting are disproportionately the
low-engagement ones. That is the second leak the finding names (PPM mean years on SVT 2.06 against DD
1.85).

### What published evidence says

- **J_svt is bounded, H_svt sits inside the band, and their ratio is not published.** J_svt floor
  0.0449 and ceiling 0.2659 (`tools.published_route_split.svt_internal_conversion_floor` /
  `_ceiling`). The world runs J at 0.1859.
- **The external share of all switching moved by era, for all households and all routes:**
  - Ofgem 2018: supplier 18% against tariff 15% over 12 months. External is the larger, about 0.55
    of the union ignoring overlap.
  - CIM W1 (March 2022): 9.3% against 13.2%.
  - CIM W6 (2025): 5.3% against 17.0%. φ_survey 0.24.

  So pre-crisis, households that moved were more likely to leave than to re-fix with their supplier.
  In 2025 it is the reverse. A world where an engaged household on the default tariff **always**
  converts internally is closer to 2025 than to 2016–19. Not established: how much of each
  survey's internal row is default-tariff households (§4 of the switcher-split note says most of it,
  in every wave).

### What is unknown (GAP)

The route-conditioned split: of default-tariff households that act, the share that leave. No source
located. The era series above is route-mixed, and its rows carry the same tariff-at-interview
contamination as §1, so its tariff banner cannot be used either.

### The design choice it supports, and what waits

**No build proposal yet, and not because of caution.** The change would make the conversion at the
anniversary a competing exit: active households either convert or leave, with the leave share set by
era. That needs a number for that share, and §3's GAP is that number. Inventing one is what K8
forbids. What can go ahead without it is a **diagnostic**: per year, the drawn share of SVT movers who
convert against those who leave, printed beside the published era series as two route-mixed
shapes. That is the next measurement, and it is filed as a hand-off, not built here.

---

## 4. Summary for the next session

| item | status after this pass |
|---|---|
| Pre-crisis fixed vs SVT departure split (W-C) | **GAP, now proved unclosable from consumer surveys**: tariff is recorded after the switch, and the published ratio is an identity in the landing share. Instrument-emulation test named in §1c. |
| CIM w6 C4 tariff at interview | **Verified**: A13, present tense. The finding's item 4 is no longer unverified. |
| Finding's "the era is most of it" | **Corrected beside the claim**: the world's drawn ratio and the survey's are different quantities in both eras. |
| W-A (channel on the drift hazard) | Knowledge page done (§2). Build after 19 Oct against the finding's filed prediction. Aim 0.50–0.70, not 0.55. |
| W-B (convert vs shop) | Knowledge page done (§3). Needs the default-route external share, which is a GAP. φ was the wrong quantity. Diagnostic first. |
