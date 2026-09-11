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
2. ~~A control that fires when the generated share leaves the band, keyed to the BAND and not to
   today's numbers, so this cannot go quietly out of range again. `tools/svt_generated_share_check`
   is a report with a verdict column and nothing reads it.~~ **DISCHARGED 2026-09-04.** The
   verdict is now the exit code (`0` in band, `1` out, `2` could not measure) and `--out` writes it
   as JSON, on a refusal too. `tests/tools/test_the_svt_share_check_verdict_is_keyed_to_the_band.py`
   holds the property and is mutation-proved on four edits: exit-always-0, an exclusive band edge,
   an unjudged year counted as conformance, and a refusal that writes nothing. The committed
   verdict is `docs/reports/svt_generated_share_verdict.json`.
3. Re-measure the value arm's funnel afterwards and re-publish. The arm's reach will fall and the
   capabilities page already derives its cause from the run rather than from prose, so it will
   follow the world without an edit.

## What was landed today, and what was not

Landed: the published cause under the arm's largest funnel drop is now derived from the run's own
per-product counts rather than from a sentence written when the run was born
(`tools/product_gate_refusal.py`). Not landed: any of the three items above. The re-fit is a world
change with its own evidence to assemble and it is not something to do in the tail of another
turn.

**2026-09-04, later tick: owed item 2 is discharged** (see above). Items 1 and 3 stand, and item 1
is still the world change that needs its own turn. One thing learned in discharging 2 that belongs
beside the finding: **the check was not merely unread, it was FAIL-OPEN.** "Nothing reads it" and
"it returns 0 whatever it finds" are different defects with different repairs, and only the second
one explains why wiring a consumer to it would not have helped. The world's non-conformance is
deliberately NOT asserted as a red test here: `simulation/svt_product.py` and
`tests/simulation/test_svt_product.py` both forbid a control pinned to a year's share, and
`background/head_red_register.py` makes accepting a known red a human's decision and not a lane's.
So the mechanism is now able to fail, and what it reports is 8 of 8 judged years out of band.

---

## 2026-09-04, later tick again: owed item 1 is answered, and the answer is NOT the re-fit this finding asked for

**Owed item 1 above says "a re-fit of the active-renewal rate against the published fixed/SVT
series". That instruction is withdrawn, and the reason is in the record this finding already
cites.** `docs/market_research/svt_rates_active_passive_2016_2025.md` §3 ends: *"Post-2023
recovery: ~one-third of customers on fixed deals by Jul 2025 (Ofgem State of the Market, Jan 2026).
**Closely matches pre-crisis 35% engaged proportion.**"* The published record says the 35% level is
the right level. Re-fitting it to chase 2024's 25pp miss would have broken 2018 and 2019 — which
are 4.3pp and 1.7pp out, i.e. nearly right — to chase a miss concentrated entirely in the years
after the crisis. **Separate level from amplitude before blaming a mechanism**: the level is
anchored and close; the shape is wrong.

The shape defect is the withdrawal WINDOW, and `docs/design/C1B_THE_BOOK_LANDS_ON_THE_SVT_PRODUCT_2026-08-30.md`
had already named it and parked it: *"2023 at 26.9%. `CRISIS_PASSIVE_YEARS` holds `{"2022"}` only.
The published record has fixed deals withdrawn until April 2023. Extending the set is a world change
with a published reason and belongs in its own decision, not folded into this one."*

### What was changed

`simulation/renewal_engagement.py`: `CRISIS_PASSIVE_YEARS = frozenset({"2022"})` →
`FTC_WITHDRAWAL_WINDOW = (2022-01-01, 2023-06-30)`, with `ftc_withdrawn_at()` as the predicate and
`CRISIS_PASSIVE_YEARS` kept as a DERIVED view of the whole years the window covers, so every
control keyed to the old set keeps its meaning and follows the window without an edit.

The end date is Ofgem SotM April 2025's *"Following the re-emergence of FTCs in the second half of
2023"* — a statement about AVAILABILITY, which is what this branch models. The April 2023
"~29m on SVT" reading is a STOCK and says nothing about what was on offer, so it is not the
endpoint even though the C1B note reached for it.

### THE PREDICTION, WRITTEN BEFORE THE CHECK WAS RUN

Recorded here so it can refute me. If any of these is wrong, the mechanism is not what I think it
is and the number below is not the story.

1. **2016–2021 move by exactly zero.** Every day the window gained is in 2023 and a forced stint
   cannot back-date.
2. **2022 stays at 21.5%** — it was already forced end to end, so nothing this change does can
   touch it. It stays OUT (band 10–20%).
3. **2023 falls from 26.9% into 18–25%, and stays OUT.**
4. **2024 falls from 45.0% into 33–42%, and stays far OUT** (band 14–20%). H1-2023 forced stints
   run to their anniversaries in H1 2024, so the effect reaches 2024 without the code naming it.
5. **2025 falls from 50.5% into 42–50%, and stays OUT** (band 30–36%).
6. **The verdict stays OUT in 8 of 8 judged years.** A window fitted to the bands would have closed
   at least one; this one is fitted to two sentences in the record and closes none.

### AND THE CLAIM THAT MATTERS, which this move is the evidence FOR and not against

**2022 is forced passive on every single day and still reads 21.5% fixed, above the published
band's 10–20% ceiling.** That 21.5% is a FLOOR, and no widening of this window can go under it,
because two things put it there and neither is engagement:

  * every account is BORN on a fixed term (`run_phase2b` mints `tariff_type` `"fixed"`), so a
    growing book adds fixed account-days every year no matter what the market is doing; and
  * a fixed term only reaches the forcing at its BOUNDARY — a household mid-term when deals were
    withdrawn stays fixed for up to another year, and there is no mid-term route to SVT.

So the residual after this change is a different defect from the one this finding opened with, and
it should not be worked as if it were the same one: **the world's fixed share cannot fall below its
own first-term floor, and the published crisis years are below that floor.** The two named repairs
are the opening-product draw (C1B's owed item 1: `population_draw` should mint a share of accounts
already on SVT at acquisition, which is the same fact 2016's 100% exposes) and a mid-term route
onto the default tariff. Neither is a re-fit of anything.

### THE RESULT, AND THE PREDICTION IT REFUTES

Run at HEAD+this change, `python3 -B -m tools.svt_generated_share_check`, basis `all_domestic`,
committed at `docs/reports/svt_generated_share_verdict.json`:

```
  year  acct-days    fixed      svt    other  published fixed      was
  2016     13,739   100.0%     0.0%    -0.0%  26%-34%  OUT       100.0%   unmoved
  2017     21,708    57.4%    42.6%    -0.0%  36%-38%  OUT        57.4%   unmoved
  2018     24,183    45.3%    54.7%     0.0%  41%-41%  OUT        45.3%   unmoved
  2019     27,717    44.7%    55.3%     0.0%  41%-43%  OUT        44.7%   unmoved
  2020     32,594    41.8%    58.2%     0.0%  (none)   cannot_tell 41.8%  unmoved
  2021     36,588    42.0%    58.0%     0.0%  (none)   cannot_tell 42.0%  unmoved
  2022     40,015    21.5%    78.5%     0.0%  10%-20%  OUT        21.5%   unmoved
  2023     42,444     9.0%    91.0%     0.0%  10%-20%  OUT        26.9%   -17.9pp
  2024     47,208    41.8%    58.2%     0.0%  14%-20%  OUT        45.0%   -3.2pp
  2025     22,023    46.6%    53.4%     0.0%  30%-36%  OUT        50.5%   -3.9pp
```

Predictions 1, 2, 4, 5 and 6 hold: 2016–2022 moved by exactly zero, 2024 landed at 41.8% inside the
predicted 33–42%, 2025 at 46.6% inside 42–50%, and the verdict is still OUT in 8 of 8. **Prediction
3 is REFUTED and so is the argument under it.** I predicted 2023 would fall to 18–25% and stay out
ABOVE the band. It fell to 9.0% and is out BELOW it, by 1.0pp.

**The refuted argument was the "floor", and it is worth more than the number.** I reasoned that
2022 reads 21.5% while forced on every single day, so 21.5% was a floor made of first terms and
mid-term stickiness that no widening could go under. That was wrong, and the error is a *level for
an amplitude*: 21.5% is not a floor, it is the AVERAGE OF A CONVERSION. 2022 is the first year of
forcing and the book enters it almost entirely on fixed, so the year's account-days are half
pre-conversion. 2023 is the second year, the conversion has completed, and the same mechanism
reads 9.0%. A one-year window could never have shown this and I read the one year I had as a
steady state.

**What survives from that argument, and what does not.** The born-fixed effect is real and is
still the best explanation of 2018–2019 sitting ~2–4pp over a band the 35% anchor otherwise
reproduces — but it is a few points, not the 12 I attributed to it, and it is not a floor. The
mid-term-stickiness half is simply not load-bearing at this magnitude.

### On 2023 now being out on the LOW side, and why the endpoint does not move

The obvious next move is to pull the window's end back to the C1B note's "until April 2023", which
would raise 2023 and could land it in band. **That move is refused.** The endpoint was chosen from
the source's grammar before the check was run — availability is what this branch models and
*"re-emergence of FTCs in the second half of 2023"* is the only published statement about
availability — and changing it now, on sight of a 1.0pp miss, would be fitting the window to the
band. That is the exact thing `simulation/svt_product.py` and the check tool's own docstring forbid,
and the overshoot is the evidence the window was not fitted: a fitted one would have landed inside.

Worth stating plainly for the reader: 9.0% for calendar 2023 sits just under a band whose own note
says *"the year straddles the re-emergence, so the true within-year path falls across this band
rather than sitting at a point in it"*, and next to a published April-2023 stock reading of ~10%
fixed. The world is now much closer to the record here than it was (6.9pp over → 1.0pp under) and
the verdict is still OUT, which is the control working.

### What is owed after this, and it is not what this finding first said

1. ~~A re-fit of the active-renewal rate.~~ **WITHDRAWN** — see the head of this section. The
   record says 35% is the right level.
2. **The opening-product draw.** `run_phase2b` mints every account on `fixed`, so 2016 reads 100%
   and every year carries a born-fixed surplus. C1B already owes this as *"population_draw should
   mint a share of accounts already on SVT at acquisition"*. It is the single largest remaining
   contributor to 2016 (66pp), 2017 (20pp) and, in small part, to every other year.
3. **The post-crisis recovery rate.** 2024 is still 21.8pp over. Ofgem: *"By July 2025, around
   one-third of customers were on FTCs, twice the proportion recorded in July of the previous
   year"* — the real recovery took two years to reach the pre-crisis engaged proportion, and this
   world reaches it in one, because at re-emergence every household's archetype applies at full
   strength immediately. That is a mechanism gap (FTC supply returned gradually and was priced
   against a capped SVT), not a level to re-fit, and it is the next world change.
4. Re-measure and re-publish the value arm's funnel. The arm's reach falls with this change: 2023
   and 2024 renewals that were fixed boundaries are now SVT stints with no renewal decision, so
   the product-gate refusal count RISES. The capabilities page derives its cause from the run's own
   counts (`tools/product_gate_refusal.py`), so it follows the world without an edit — but the
   published feed is from an older run and will not move until the next one.

### What else assumes the old world, checked rather than assumed

**`simulation/departure_level_anchor.YEAR_LEVEL_ANCHOR[2023]` is now fitted to a world that no
longer exists, and this is a NAMED property of that block rather than a new defect.** Its own
docstring says so: *"THE FIT IS EXACT ON THE RUN IT WAS FITTED TO AND APPROXIMATE ON THE NEXT ONE
… raising the level changes the book, so the population the following year is not the one the
anchor was solved against. The iteration is capture -> fit -> capture."* H1-2023 boundaries no
longer produce renewal decisions, so 2023 carries fewer of them than the capture the anchor was
solved against. The remedy is that block's own next capture-fit pass and it is not folded in here.

**`UNFITTED_YEARS[2022]` is untouched and its reasoning still holds exactly.** It rests on 2022
being forced on every day of the year, which the window preserves — 2022 is inside
`fully_withdrawn_years()` and `CRISIS_PASSIVE_YEARS` still contains it. 2023 is NOT added to that
set, deliberately: half of 2023 had supply and a control demanding no fixed term start in H2 2023
would go red for the world being right.

**`company/crm/churn_model.CRISIS_PASSIVE_YEARS` is deliberately NOT changed.** It is the COMPANY's
estimate of the same fact and `simulation/renewal_engagement.py` is explicit that the two may drift
and that pinning them equal would restore the coupling the KNIFE cut removed (R12). The world has
moved onto the record; the company's belief about when fixed deals were unavailable has not, and
that gap is now a real thing the coupled triad can score rather than a guaranteed zero.
