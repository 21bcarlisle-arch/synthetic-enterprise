# PRE-REGISTRATION — whether the 2021-2023 episode puts the faced price ratio inside the evidence range

**Filed:** 2026-09-07, BEFORE a single price was read off the 2021-2023 panel and BEFORE the Ofgem
cap level model was opened.
**Claim:** `a49-does-the-2021-2023-episode-reach-the-evidence-range`
**Supersedes nothing. Extends:** `docs/market_research/domestic_shift_response_as_a_function_of_pass_through.md`
(landed 8369a541e), whose own named gaps are the two questions below.

---

## Why this is being measured

The landed Arcturus 2.0 work established the shift response as a function of the peak-to-off-peak
price ratio, and then could not locate the interior optimum, for a reason it named precisely: the
price shape on the panel it had is too flat. The panel's median within-day wholesale ratio is
**1.77:1**, and the household faces **1.26:1** at full pass-through with the commodity share `s`
set to the best-supported 0.40. Arcturus's sample begins at 2:1; Ofgem states a factor of about
three is needed for a material response. **The binding constraint is the price shape, not the
household.**

That panel is Elexon MID over 2016-09 to 2020-12. It ends before the gas crisis **by
construction**, not by choice. Two questions follow, and the finding named both:

1. **The cheap one, and it is a prerequisite.** `s` is the commodity share of the domestic
   electricity **unit rate**. The knowledge map carries wholesale ≈40% of the **bill**. Those are
   different denominators: the standing charge carries network residual and other fixed costs the
   unit rate does not, so the unit-rate share is **higher**, and every published figure in the
   landed finding is understated **by a known sign**. Ofgem's own default-tariff-cap level model
   publishes the component build-up. This is a reading, not an estimate.
2. **The expensive one.** Re-measure the within-day wholesale spread on **2021, 2022, 2023** —
   the years the MID panel excludes — and the ratio a household faces after retail dilution at the
   `s` question 1 returns. Then re-evaluate the Arcturus arc at those ratios.

---

## What "done" means for this turn

Not "the optimum is located". Done is: **both numbers measured from published sources, on the same
window and the same method as the landed panel, with the verdict stated in whichever direction it
falls, and the landed finding's two named gaps either closed or narrowed with the residual named.**

If the episode does clear the bar, the landed figures are superseded and I say so beside them. If it
does not, that is the stronger result — it means the constraint is structural rather than an
artefact of which years we happened to hold, and time-of-use on a domestic book is bounded by the
price shape in every year of the record we can see.

---

## Predictions, filed before measuring

Graded line by line at the foot of the result. A prediction filed after the answer is not a
prediction.

### On `s`, the commodity share of the electricity unit rate

- **P1a.** `s` is **above 0.40** in every cap period read. *(This is the one I am most confident of
  — it is the sign the landed finding already derived from the denominators. If it is refuted, the
  landed finding's reasoning about the standing charge is wrong, not just its number.)*
- **P1b.** In a **pre-crisis** cap period (2021 H1) `s` lands in **0.45–0.60**.
- **P1c.** In the **crisis** periods (2022 H2 through 2023) `s` is **materially higher — above
  0.65** — because the wholesale allowance rose several-fold while network, policy and operating
  allowances did not.
- **P1d.** Therefore `s` is **not a constant** and the landed grid's treatment of it as one row is
  itself a finding. I expect to have to publish a *range keyed to the cap period*, not a scalar.

### On the 2021-2023 within-day wholesale shape

- **P2a.** The **level** of prices rises severalfold. This is not in question and is not the
  measurement. *(Named explicitly because separating level from amplitude is exactly where this
  project has attributed a move to the wrong mechanism before.)*
- **P2b.** The **ratio** — dearest 6 half-hours over cheapest 6 half-hours, the panel's own window
  — is scale-free, so a uniform level shift moves it **not at all**. My prediction is that it
  nonetheless widens, but **modestly**: median in **1.9–2.3**, against 1.77 on the old panel.
- **P2c.** I predict the median **does clear 2:1** (the foot of Arcturus's sample) but **does not
  clear 3:1** (Ofgem's stated material-response threshold), on the **raw wholesale** series before
  any retail dilution.
- **P2d.** The **tail** widens much more than the median: p90 above **4.5** (against 3.36), because
  2022's high-wind overnight periods produced near-zero and negative prices against very dear
  evening peaks, and a ratio with a small denominator is unbounded above.
- **P2e.** **2022 is the widest of the three years**, 2023 second, 2021 narrowest.

### On the faced ratio and the arc

- **P3a.** At the measured `s` and **full** pass-through (alpha = 1.0), the median faced ratio is
  **still below 2:1** — I predict **1.5–1.9**. The retail dilution is strong enough to undo the
  widening. **If this is refuted the whole product question changes**, which is why it is the
  headline prediction.
- **P3b.** The **share of days** whose faced ratio clears 2:1 at full pass-through rises from the
  landed 0.020 (at s = 0.40) to somewhere in **0.15–0.40**.
- **P3c.** Mean modelled response, **opt-out** recruitment, at the argmax pass-through, stays
  **below 3%** of peak usage.
- **P3d.** Company value per household-year at the argmax rises from the landed £0.03 (s = 0.40,
  opt-out) by **more than an order of magnitude**, driven mostly by the created-value level rather
  than by the response, and **still lands under £10**.
- **P3e.** `argmax alpha` remains **unstable across `s` and recruitment** — the landed spread of
  0.09–0.77 narrows by less than half. Locating the optimum was never a data-volume problem.

### On what the measurement will NOT settle

- **P4a.** Persistence is untouched. No source read here measures it.
- **P4b.** Shiftable share is untouched and still multiplies everything. Every figure below is at
  shiftable share 1.0, as the landed ones are.
- **P4c.** 2021-2023 is a **historical episode, not a forecast**. Even a clearing result would not
  establish that a tariff sold today faces those ratios, and I predict I will have to say so on the
  artefact rather than in a footnote.

---

## Method, fixed before the data is read

- **Same reader:** `sim/market_index_history.volume_weighted_mid`, reused, not re-derived — it
  carries two measured fail-opens (a too-wide window returning an empty HTTP 200, and a reporting
  provider publishing 0.00 on volume 0.00) that a fresh join would reproduce.
- **Same day builder and same window:** `whole_days` and a 6-half-hour shift window, from
  `tools/r3_carbon_score_ceiling.py`, so the new panel and the landed one describe **one act**.
- **Same ratio definition:** mean of the day's dearest 6 half-hours over the mean of its cheapest 6.
- **Same bridge:** `ratio(alpha, s) = [1 + alpha·s·(peak_rel − 1)] / [1 + alpha·s·(off_rel − 1)]`.
- **Response computed per day and then averaged**, never the response at the average ratio — those
  are different quantities through a concave function.
- **Days with a non-positive cheapest window are reported, not dropped silently.** 2022 produced
  negative prices; a negative denominator makes the ratio meaningless rather than large, and that
  count is itself a result.
- Any faced ratio evaluated **below 2:1 is an extrapolation outside Arcturus's sample** and is
  labelled as such wherever it appears, exactly as the landed artefact labels its own.
