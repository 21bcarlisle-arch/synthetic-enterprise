**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The world's fixed-deal share is outside the published band in every one of the eight years that has one

**Class:** `measurements_that_mirror` (primary)
**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`the-arms-reach-is-a-missing-world-product-not-a-company-choice`
**Subject:** `simulation/renewals.py` (the C1b passive-roll branch), `simulation/renewal_engagement.py`
(the 35% anchored active-renewal rate), measured by `tools/svt_generated_share_check`.

**LATENT, not BLOCKING, and the distinction matters here.** Nothing published today states the
world's product mix as a figure, so no page is currently wrong because of this. What it bounds is
the fidelity of the book every other figure is measured on — and, specifically, the size of the
value arm's reachable surface, which the same claim has just restated on the capabilities page.

## What

`tools/svt_generated_share_check` builds the electricity schedules the world builds, counts
domestic account-days on each product per calendar year, and prints the generated fixed-deal share
against the published band in `tools/published_tariff_mix.DEFAULT_TARIFF_SHARE`
(`docs/market_research/gb_domestic_default_tariff_share_2016_2025.md`). Run at
`c963acf1f` on 2026-09-04, basis `all_domestic`:

```
  year  acct-days    fixed      svt    other  published fixed
  2016     13,739   100.0%     0.0%    -0.0%  26%-34%  OUT
  2017     21,708    57.4%    42.6%    -0.0%  36%-38%  OUT
  2018     24,183    45.3%    54.7%     0.0%  41%-41%  OUT
  2019     27,717    44.7%    55.3%     0.0%  41%-43%  OUT
  2020     32,594    41.8%    58.2%     0.0%  (no established figure)
  2021     36,588    42.0%    58.0%     0.0%  (no established figure)
  2022     40,015    21.5%    78.5%     0.0%  10%-20%  OUT
  2023     42,444    26.9%    73.1%     0.0%  10%-20%  OUT
  2024     47,208    45.0%    55.0%    -0.0%  14%-20%  OUT
  2025     22,023    50.5%    49.5%    -0.0%  30%-36%  OUT
```

Eight years carry a published band. **All eight are OUT, and all eight are out in the same
direction: the world holds MORE households on a fixed deal than the published record does.** The
misses are not uniform — 2018 and 2019 are 3.7pp and 1.7pp over, which is close; 2024 is 25.0pp
over and 2016 is 66pp over.

## Why it is one finding and not two

**2016 is a different failure from the rest and must not be fixed by the same lever.** Every
account enters the book on a fixed term (`run_phase2b` passes `tariff_type=c.get("tariff_type") or
"fixed"`, and that opening label is correct — an account the company won or drew arrived by taking
a deal). A household cannot reach SVT until its first anniversary, so the first year of any
account's life is 100% fixed by construction. In 2016 almost the whole book is in its first year.
That is a burn-in artefact of where the window starts, not a behaviour defect, and a fit that tries
to pull 2016 down to 26–34% would be fitting the start of the simulation rather than the market.

**2017–2025 is the behaviour.** The mechanism is `renewals.py`'s C1b branch: at each non-first
resi fixed boundary, `rolls_active_renewal` decides whether the household shops or rolls onto the
cap, at an anchored 35% population active-renewal rate with a per-household engagement archetype
and a 2022 crisis-year forcing. The generated share it produces is too high in every year with a
band, which means **too few households roll**, which means the world under-states how much of a
domestic book sits on the default tariff.

## Which way the repair runs, and that it runs against us

Moving the world onto the published series puts MORE households on SVT. An SVT household has no
renewal decision, so the value arm's reachable surface gets SMALLER — on the run published today,
1,223 of 1,953 renewals are already refused at the product gate for exactly this reason, and
closing this gap raises that count. **The change costs the company measured margin and costs the
value-arm experiment its `n`, and it is required anyway**: the baseline changes for fidelity
reasons, decided blind to what it does to company results (R13, and the epistemic wall's third
clause). Recording the direction here, before the fit, so that a later "the fit made things worse"
cannot be read as a reason to abandon it.

## What is NOT the justification

`docs/reports/svt_composition_vs_published.json` measured whether re-composing the published series
closes any of these years and reports `years_newly_closed_by_composition` EMPTY. So the gap is not
an artefact of which published population the band is drawn over, and nothing here may be sold as
"the comparison basis was wrong". The `as_published` basis is a second reading of the same data and
disagrees with `all_domestic` by ~6pp on the pre-crisis years — enough to flip 2018 and 2019 and
not enough to touch 2022, 2023, 2024 or 2025. **The finding survives either basis on at least four
years, and that is the claim being filed.**

## What is owed

1. A re-fit of the active-renewal rate against the published fixed/SVT series, on the years that
   carry a band, excluding the burn-in years where the window start dominates the answer. The
   published split stays a CHECK on the output and never becomes an input — `simulation/svt_product.py`
   is explicit that a split which has to be set to land in range means the behaviour is wrong.
2. A control that fires when the generated share leaves the band, keyed to the BAND and not to
   today's numbers, so this cannot go quietly out of range again. `tools/svt_generated_share_check`
   is a report with a verdict column and nothing reads it.
3. Re-measure the value arm's funnel afterwards and re-publish. The arm's reach will fall and the
   capabilities page already derives its cause from the run rather than from prose, so it will
   follow the world without an edit.

## What was landed today, and what was not

Landed: the published cause under the arm's largest funnel drop is now derived from the run's own
per-product counts rather than from a sentence written when the run was born
(`tools/product_gate_refusal.py`). Not landed: any of the three items above. The re-fit is a world
change with its own evidence to assemble and it is not something to do in the tail of another
turn.
