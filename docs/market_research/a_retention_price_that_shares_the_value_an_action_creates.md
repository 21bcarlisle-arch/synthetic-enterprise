# A retention price that shares the value an action creates: the GB rules on pricing a retention or renewal offer, and what such a price does to C34's 18 cases

**Knowledge:** next-best-action-and-cross-sell

**Written 2026-10-16** for the director's open row `c34-now-ranks-next-best-action-on`. That row
proposes that an advice action which creates value but costs us should travel with a renewal or
retention price that brings our side to at least zero (M2: created, then shared). This page is
knowledge and measurement only. It changes no decision rule.

Its sibling, `how_a_supplier_prices_a_share_of_value_it_creates_for_a_household_2026-10-14.md`,
covers a **one-off fee** (C35). This page covers the other shape: a **price change on the tariff**,
paid for each month the household stays.

## 0. The quantity, stated before any source

> For one account, the smallest rise in our monthly margin, carried by the tariff the household is
> on, that brings our forward-value change from the advice action to at least zero. It is read
> with the household's own floor, so the household still ends up better off than with no action.

Three things follow from that definition.

- **The rise is a transfer.** The module holds the hazard fixed, so every pound the rise adds to
  our side comes off the household's side. The joint value of the action is unchanged. At the
  *smallest* rise our side is exactly zero, so **the household holds 100% of the joint value by
  construction.** That column in §4 says nothing new; it confirms the arithmetic. The informative
  column is how much of its *gross* benefit the household keeps.
- **The household pays the rise only in months it is supplied.** The benefit of the advice is
  counted over the whole horizon, as `next_best_action.joint_value` counts it.
- **A price rise is not neutral for staying.** A household asked to pay more leaves more often.
  The module's arithmetic leaves this out, so §4 carries a second column that adds it from the
  published slope. Read that column first (F11: erring against our own thesis is the safe direction).

## 1. The cap (SLC 28AD)

**ESTABLISHED (in this repo, `a_save_offer_against_the_switching_rules_and_the_seam.md` §6, read
2026-10-08 from the consolidated licence).** The default tariff cap reaches **default and deemed
contracts only**, not a fixed tariff the household chose. So:

- **On a default tariff,** a rise is lawful only up to the cap. A supplier already pricing at the
  cap has no headroom, so no rise is possible there. **GAP:** none of the 18 cases carries its
  headroom under the cap, and the "margin" in each case is contribution, not headroom. The verdict
  for this route is therefore given for the at-cap case only.
- **On a fixed tariff,** the cap sets no ceiling. The household's alternative is still the cap,
  because it can let the fix lapse onto the default tariff or move to another supplier.

## 2. SLC 22B: the ban on acquisition-only tariffs, its retention carve-out, and the 2024 proposal to lift it

**ESTABLISHED (R1, R6, R7 of the save-offer page; Ofgem press release, 30 July 2024, fetched
2026-10-16).**

| date | what Ofgem did | source |
|---|---|---|
| 14 April 2022 | BAT (SLC 22B) in force. Every domestic tariff must be open to new and existing customers. The Market-wide Derogation permits **Fixed Retention Tariffs**: fixed-term, existing customers only, "with the aim of retaining the loyalty of those customers", and notified to Ofgem | R1, R6 |
| April 2022 to April 2024 | the Market Stabilisation Charge ran alongside, and was removed in April 2024 | save-offer page §6 |
| 3 February 2023 | Market-wide derogation decision and Directions for Fixed Retention Tariffs | R6 |
| February 2024 | BAT extended to 31 March 2025 | Ofgem consultation page *Future of the BAT after March 2025* (search result, 2026-10-16) |
| May 2024 | **Ofgem proposed to remove the ban, with an intended end date of 1 October 2024** | Ofgem press release *Ofgem retains ban on acquisition-only tariffs*, 30 July 2024 |
| 30 July 2024 | **Ofgem reversed that proposal.** It retained the BAT to at least 31 March 2025, citing the risk of "returning to an unfair market for inactive switchers – often referred to as the 'loyalty penalty'" and of harm to customers in debt who cannot switch | same |
| November 2024 | BAT extended to 31 March 2026 | Cornwall Insight alert, 15 November 2024 (title only, not read) |
| 13 November 2025 | BAT and derogation renewed to **31 March 2027** | R7 |

**So the ban has not been lifted.** A lift was proposed once, in May 2024, and withdrawn. **GAP:**
what happens after 31 March 2027. Ofgem treats a permanent ban as a separate workstream, and its
statutory consultation was unpublished at R7.

**What this means for a sharing price.** A price offered only to existing customers who take an
advice action is a criterion about being an existing customer. Outside the derogation, 22B.1 bars
it. Inside the derogation it is lawful **only as a fixed-term tariff**. A variable-tariff surcharge
for advice-takers has no carve-out. If the ban were lifted, the carve-out would no longer be
needed. Lifting it would also bring back cheaper acquisition-only deals elsewhere, which raises the
household's outside option. **That direction is reasoned, not measured.**

**The derogation names no price rule.** Save-offer page §7a, ESTABLISHED: there is no formula, no
floor, no ceiling and no reference price. Ofgem's own words in R7 §3.3: "not seen any substantial
evidence to date of the Market-wide Derogation's impact on pricing and tariffs". **A Fixed Retention
Tariff may be priced above the household's present tariff.** Nothing in the text requires it to be
a discount.

## 3. The other limits on a retention price

- **(a) SLC 0, the Standards of Conduct.** SLC 0.6 excludes the *amount* of a charge. SLC 0.3
  bounds how the offer is presented: the information must be complete and accurate, the product
  appropriate, and there must be no "material imbalance" in the licensee's favour (sibling page §1).
  A retention tariff priced above the household's present rate, sold on the strength of the advice,
  has to show the household its net position honestly.
  **GAP:** no Ofgem guidance applies this to a tariff bundled with advice.
- **(b) DMCC Act 2024, in force 6 April 2025.** No false urgency and no drip pricing (save-offer
  page §6). The rise must be in the headline price, not added on later.
- **(c) The form.** A rise on a fixed retention tariff is the tariff's own price. It is not credit
  extended to the household, so **reasoned, not established:** it avoids the consumer-credit regime
  that an instalment-recovered share falls under (Green Deal, SI 2012/2798; sibling page §1).
  **GAP:** no source confirms this boundary for a bundled advice tariff.
- **(d) Term length.** The horizon is 48 months. A rise priced on 48 months needs one fix of that
  length, or a fresh retention tariff at each renewal. **GAP:** no licence maximum on a fix's length
  was found. Whether a supplier may re-strike a retention tariff each year under the derogation is
  covered by its text, which carries no frequency limit.
- **(e) Analogue: the FCA's 2022 ban on price walking in insurance.** It bans pricing a renewal above
  the new-business price. BAT is energy's nearest equivalent, and it reaches *who may be offered* a
  price, not how high the price may go (`next_best_action_and_cross_sell.md`).
- **(f) Vulnerability and payment method.** SLC 0 and SLC 27 still apply (save-offer page §6).
  **GAP:** none of the 18 cases carries a vulnerability flag.

**Verdict used in §4.** A rise is **lawful as a Fixed Retention Tariff** in every case where the
household still ends up better off: the form is permitted and the depth is unregulated, subject to
(a) to (d). It is **not lawful on a default tariff priced at the cap**. A default tariff below the
cap is a GAP (§1).

## 4. The 18 cases, through `company/crm/next_best_action.py`'s own arithmetic

**The inputs** are §6.1 of `next_best_action_and_cross_sell.md`:

- margin £5, 15 or 30 a month
- departure hazard 0.5% or 3% a month
- horizon 48 months
- three advice effects, each a margin given up and a hazard cut: (£2, 0.1 point), (£2, 0.3 points)
  and (£3, 0.3 points)
- the household's yearly benefit taken as 12 x the margin given up

§6.1 does not list the grid. This one was **reconstructed** because it reproduces every published
range: joint value +£13.4 to +£107.0, our side −£0.3 to −£122.2. A second grid also reproduces them:
margin {5, 30} x hazard {0.5, 1.5, 3%} x the same three effects. Its counts are given beside this
grid's.

**The arithmetic.** `value_change` and `joint_value` are imported unchanged. The rise d (£ a month)
enters as `margin_change = −give_up + d`, and the smallest d with our side ≥ 0 is found by
bisection.

**The last column** adds the price's own effect on staying. The published within-household
renewal slope is 0.0013–0.0016 of P(stay) per £ a year of price gap (Deller et al. 2021, average
marginal effect; `retention_slope_per_pound_of_renewal_cut.md` §1). At 0.0015, a rise of £d a month
adds 0.0015·d to the monthly hazard. That slope was measured on opted-in collective-switch
households, so for an inactive book it probably **overstates** the response. It is a bound against
our thesis, not a central estimate.

The **"lawful?" column** abbreviates two routes: a Fixed Retention Tariff, and a default tariff
priced at the cap.

| margin £/mo | hazard /mo | advice gives up £/mo | hazard cut | joint value £ | our side £ | smallest rise £/mo | household keeps £ | household share of joint | share of its gross benefit kept | rise £/yr | lawful? | rise with the price's own hazard (slope 0.0015/£·yr) £/mo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 0.5% | 2 | 0.1 pt | +13.4 | -82.6 | 1.89 | 13.4 | 100% | 14% | 22.7 | FRT: yes · capped default at the cap: no | 2.28 |
| 5 | 0.5% | 2 | 0.3 pt | +19.6 | -76.4 | 1.67 | 19.6 | 100% | 20% | 20.0 | FRT: yes · capped default at the cap: no | 2.00 |
| 5 | 0.5% | 3 | 0.3 pt | +21.8 | -122.2 | 2.67 | 21.8 | 100% | 15% | 32.0 | FRT: yes · capped default at the cap: no | 3.21 |
| 5 | 3.0% | 2 | 0.1 pt | +46.2 | -49.8 | 1.91 | 46.2 | 100% | 48% | 22.9 | FRT: yes · capped default at the cap: no | 2.22 |
| 5 | 3.0% | 2 | 0.3 pt | +49.2 | -46.8 | 1.73 | 49.2 | 100% | 51% | 20.7 | FRT: yes · capped default at the cap: no | 2.00 |
| 5 | 3.0% | 3 | 0.3 pt | +70.1 | -73.9 | 2.73 | 70.1 | 100% | 49% | 32.7 | FRT: yes · capped default at the cap: no | 3.16 |
| 15 | 0.5% | 2 | 0.1 pt | +23.2 | -72.8 | 1.66 | 23.2 | 100% | 24% | 20.0 | FRT: yes · capped default at the cap: no | 3.48 |
| 15 | 0.5% | 2 | 0.3 pt | +50.0 | -46.0 | 1.00 | 50.0 | 100% | 52% | 12.0 | FRT: yes · capped default at the cap: no | 2.00 |
| 15 | 0.5% | 3 | 0.3 pt | +52.2 | -91.8 | 2.00 | 52.2 | 100% | 36% | 24.0 | FRT: yes · capped default at the cap: no | 4.09 |
| 15 | 3.0% | 2 | 0.1 pt | +51.0 | -45.0 | 1.73 | 51.0 | 100% | 53% | 20.7 | FRT: yes · capped default at the cap: no | 2.97 |
| 15 | 3.0% | 2 | 0.3 pt | +63.9 | -32.1 | 1.18 | 63.9 | 100% | 67% | 14.2 | FRT: yes · capped default at the cap: no | 2.00 |
| 15 | 3.0% | 3 | 0.3 pt | +84.9 | -59.1 | 2.18 | 84.9 | 100% | 59% | 26.2 | FRT: yes · capped default at the cap: no | 3.72 |
| 30 | 0.5% | 2 | 0.1 pt | +38.0 | -58.0 | 1.33 | 38.0 | 100% | 40% | 15.9 | FRT: yes · capped default at the cap: no | none: no rise reaches zero |
| 30 | 0.5% | 2 | 0.3 pt | +95.7 | -0.3 | 0.01 | 95.7 | 100% | 100% | 0.1 | FRT: yes · capped default at the cap: no | none: no rise reaches zero |
| 30 | 0.5% | 3 | 0.3 pt | +97.8 | -46.2 | 1.01 | 97.8 | 100% | 68% | 12.1 | FRT: yes · capped default at the cap: no | none: no rise reaches zero |
| 30 | 3.0% | 2 | 0.1 pt | +58.2 | -37.8 | 1.45 | 58.2 | 100% | 61% | 17.4 | FRT: yes · capped default at the cap: no | none: no rise reaches zero |
| 30 | 3.0% | 2 | 0.3 pt | +86.1 | -9.9 | 0.37 | 86.1 | 100% | 90% | 4.4 | FRT: yes · capped default at the cap: no | none: no rise reaches zero |
| 30 | 3.0% | 3 | 0.3 pt | +107.0 | -37.0 | 1.37 | 107.0 | 100% | 74% | 16.4 | FRT: yes · capped default at the cap: no | none: no rise reaches zero |

**Count.**

- **Holding the hazard, as the module does:** a lawful sharing price rescues **18 of 18** cases as a
  Fixed Retention Tariff, on both grids. It rescues **0 of 18** on a default tariff priced at the
  cap. The rise needed is £0.01 to £2.73 a month (£0.1 to £32.7 a year). The household keeps 14% to
  100% of its gross benefit.
- **Adding the price's own effect on staying (published slope):** **10 of 18** are rescued (9 of 18
  on the second grid).
  - **None of the six £30-margin cases** is rescued. There, every pound of price costs more in lost
    staying than it brings in, so no rise brings our side to zero.
  - All 12 cases at £5 and £15 margin are rescued with a rise of £2.00 to £4.09 a month.
  - Of those 12, **10 also clear the household's floor**. The two that fail are both at £15 margin
    and 0.5% hazard: (£2, 0.1 point) and (£3, 0.3 points). There the rise takes more than the advice
    saves.

**What this says, and what it does not.**

- **The cases a price can rescue are the low-margin ones.** At high margin, the loss in staying
  that a rise causes costs more than the margin it recovers.
- **The rescue is a transfer.** It does not create value. Creating the value is the advice's job,
  and the price only moves it.
- **Every rescued case turns on two unestablished numbers.** One is the household's benefit horizon
  (§6.1 GAP). The other is whether the published slope applies to a household that has just been
  helped.

**I cannot yet say** whether a household offered advice together with a higher fixed price
responds like Deller's switchers. No published source measures a bundle. That is the measurement a
holdout would make (`hazard_estimate_from_holdout`, B8).

### 4a. What the world says (measured 2026-10-17)

Pre-registered in `docs/staging/records/SEAT_PREREG_THE_WORLDS_STAYING_SLOPE_UNDER_A_RETENTION_RISE_2026-10-17.md`,
before this analysis. The instrument is `tools/decision_probe.py` on the default book: 260 renewals,
192 accounts. At each renewal the world was asked its true P(stay) at the offer, with nothing else
changed. A rise of £d a month is placed at margin £M a month over each decision's own base, for the
page's bands M = 5, 15 and 30. That gives 443 graded band-decisions over 179 accounts. The rest fall
off the probe's grid, mostly at M = 30.

**The slope: the world's own, not Deller's.** The median fall in P(stay) per £/yr of rise, at
d = £2/month, is:

| band | median slope | share ≥ 0.0015 |
|---|---|---|
| M = 5 | 0.00064 | 19% |
| M = 15 | 0.00070 | 25% |
| M = 30 | 0.00065 | 8% |
| pooled | **0.00065** | 20% |

- Both fuels give similar figures: electricity 0.00062–0.00068, gas 0.00041–0.00087 (gas n = 10–30).
- The pooled median is below **0.00085**, where the page's count starts to fall. At 0.00065 the
  arithmetic above rescues **18 of 18**, and 17 of 18 also clear the household's floor.
- 38% of decisions are individually steeper than 0.00085.
- The slope per £ is steeper for small users: electricity at M = 15 gives 0.00134, 0.00070 and
  0.00048 by volume tercile. A £ a month is a bigger rate step on a small bill. The world responds
  to the rate, so its slope per £/yr scales roughly with 1/volume.

**The binding constraint is not the slope. It is that a stayer is never billed a fix above the
default.** In the world, a domestic household that stays and is offered a fixed renewal above the
default goes onto the default instead (`DECLINE_A_FIX_ABOVE_THE_DEFAULT`, `run_phase2b`). The share
of a £2 rise that a stayer is billed was measured:

- Under half of it is collected in **67%** of decisions at M = 5, **86%** at M = 15 and **94%** at
  M = 30.
- The room between the company's flat renewal offer and the default is **£1.35 a month at the
  median** (p10 −£5.90, p90 +£12.38).
- The rises the table needs are £0.01–2.73 a month holding the hazard, and £2.00–4.09 with the
  price's own effect. A stayer can be billed a rise of £1 in 53% of renewals, £2 in 43%, £2.73 in
  37% and £4 in 30%.

**The page's bands sit above the world's book.**

- The company's flat renewal margin is £0.64 / £1.33 / £2.27 a month (quartiles), against the
  page's £5–30.
- The default leaves room for a £5 margin in 35% of renewals, £15 in 9%, and £30 in 1%.
- The world's P(stay) at renewal is 0.54 / 0.61 / 0.68 (quartiles). Read as (1 − P)/12, almost
  every decision is in the page's 3% hazard band. The 0.5% band holds 2–4 decisions per margin
  band and could not be graded.

**Graded against the predictions:**

- **P1 held.** The median is 0.00064–0.00070 in every band.
- **P2 held pooled (19.6%) and was refuted in the M = 15 band (25%).**
- **P3 refuted at M = 5:** the slope rises slightly with d, from 0.00063 to 0.00068. It held at
  M = 15 (0.00074 → 0.00063). At M = 30 it is flat.
- **P4 ungradable:** see the hazard band above.
- **P5 held, and is the result.**

**What this answers for the open row.** The slope question resolves towards the count of 18/18,
not 10/18. That count is about the arithmetic, though, and the arithmetic assumed something the
world does not allow: that the household pays the rise. In the world a sharing rise is collectable
only where the fixed renewal sits at least that far below the default. That is 37–53% of renewals
for the rises the table needs, and it is fewest exactly where the page's margins are high. So
**whether a sharing price rescues a case is decided first by the default's headroom on that
account, and only then by the slope.** A design would have to read that headroom per account; the
company can read it, since the default is published. The world's rule is a behavioural one: a
household that stays declines a fix that costs more than doing nothing. It was pre-registered and
graded on 2026-10-02 (`DECLINE_A_FIX_ABOVE_THE_DEFAULT`). **GAP:** whether the licence also stops a
supplier rolling a passive household onto a fix dearer than the default has not been read into
this page or the commons. Until it is, the rule stands on behaviour alone.

**Correction to §4's table, beside it.** The "FRT: yes" column is lawful in form. In the world it
is billed only where the FRT stays at or under the default the household would otherwise pay. The
column does not say that, and it should be read with this section.

Scripts: `/var/tmp/retention_rise/bands.py` and `rescue.py`. They are not in the tree, and their
logic is stated above. One bug was fixed in `bands.py` before grading: its "collected" share was
divided by 12 twice, which read every decision as collecting under a twelfth of the rise. The P5
figures above are after the fix.

**Reproduce:** from the repo root, `PYTHONPATH=. python3` the snippet below.

```python
from company.crm.next_best_action import AccountState, ActionEstimate, Action, forward_value, value_change, joint_value
H, K = 48, 0.0015   # K: monthly hazard per GBP/month of price, from 0.0015 P(stay) per GBP/yr
def ours(m, h, g, c, d, k=0.0):
    return value_change(AccountState("a", m, h, 0, ()), ActionEstimate(Action.TARIFF_ADVICE, g*12, -g+d, -c+k*d), H)
def smallest(m, h, g, c, k=0.0):          # None when no rise up to GBP 200/month reaches zero
    if ours(m, h, g, c, 0, k) >= 0: return 0.0
    if ours(m, h, g, c, 200, k) < 0: return None
    lo, hi = 0.0, 200.0
    for _ in range(80):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if ours(m, h, g, c, mid, k) < 0 else (lo, mid)
    return hi
for m in (5, 15, 30):
    for h in (0.005, 0.03):
        for g, c in ((2, .001), (2, .003), (3, .003)):
            d, dk = smallest(m, h, g, c), smallest(m, h, g, c, K)
            paid_k = None if dk is None else dk * forward_value(1.0, h - c + K*dk, H)
            print(m, h, g, c, round(joint_value(ours(m, h, g, c, 0), g*12, H), 1), round(d, 2),
                  None if dk is None else (round(dk, 2), paid_k <= g*12*H/12))
```

### 4b. The count on the world's own renewals (measured 2026-10-17)

§4a showed that the 18 constructed cases do not describe the world's book. This section counts again,
one renewal at a time, on the same probe. It was pre-registered in
`docs/staging/records/SEAT_PREREG_THE_RETENTION_RISE_RESCUE_COUNTED_PER_RENEWAL_UNDER_THE_DEFAULT_2026-10-17.md`
before the count was run.

**The method.** Every one of the 260 renewals (192 accounts) is graded, and each one supplies its own
inputs:

- **Margin:** its own flat renewal margin, as billed to a stayer.
- **Hazard:** its own monthly hazard, 1 − P(stay)^(1/12).
- **The rise:** placed on its own level grid. The world's P(stay) and the billed price are read there.
- **The cap:** only what a stayer is actually billed counts as collected, so the rise is capped at
  the default.

Our side is `value_change`, unchanged, at a 48-month horizon, for each of the page's three effects.
The count has two arms. The **world arm** adds the rise's own effect on staying, read from the grid.
The **module arm** holds the hazard fixed.

**The count.** A rise counts as a rescue when it brings our side to ≥ 0 and is actually billed:

| effect (gives up £/mo, hazard cut) | world arm | module arm | accounts (world) |
|---|---|---|---|
| £2, 0.1 pt | **110 / 260 (42%)** | 113 | 95 / 192 |
| £2, 0.3 pt | **112 / 260 (43%)** | 113 | 95 / 192 |
| £3, 0.3 pt | **92 / 260 (35%)** | 94 | 81 / 192 |
| all cases | **314 / 780 (40%)** | 320 | |

- **Reading the hazard as (1 − P)/12, §4a's convention,** changes no count by more than one.
- **148 renewals (57%) are rescued under no effect.** In 94 of them the flat renewal already sits at
  or above the default, so no rise can be billed. In 53 the room is under £2 a month. Only 1 has
  room of £2 or more and still fails.
- **Every rescued case clears the household's floor.** At the median the household keeps 53–54% of
  its gross benefit (quartiles 46–60%).
- **The rise needed is almost exactly what the advice gives up:** median £1.99–3.00 a month. The
  world's flat margin is thin (quartiles −£0.05 / £0.72 / £1.69 a month) and its hazard is high (h0
  quartiles 3.2 / 4.1 / 4.9% a month). So a hazard cut of 0.1–0.3 points is worth almost nothing to
  us, and the sharing price in practice charges back what the advice cost us.
- **The year decides it.** For effect (£2, 0.3 pt) the count is:

  | renewals starting in | rescued |
  |---|---|
  | 2020 | 39 of 40 |
  | 2019 | 20 of 28 |
  | 2017 | 28 of 99 |
  | 2021 | 4 of 29 |
  | 2024–25 | 8 of 24 |

  No renewal on the default book starts in 2022. The headroom under the default is a property of the
  cap against cost in that year, not of the household.

**A trap the world arm springs, excluded above.** Counted naively, the world arm rescues *more* than
the module arm: 126, 128 and 105. The 13–16 extra cases all collect £0. They are renewals already at
or over the default, where we lose money on every month supplied. There the "rise" is declined onto
the default and billed to nobody. It reaches zero only because the higher offer drives some of
those households away. That is shedding an account, not sharing value, so it is not counted.

**Graded against the predictions:**

- **Q1 held.** The module arm rescues 43%, 43% and 36%.
- **Q2 refuted as stated.** The naive world arm sits above the module arm, for the reason in the
  trap above. With that excluded, it sits 1–3 renewals below.
- **Q3 held.** 100% of rescued cases clear the floor.
- **Q4 refuted, the other way round.** Below-median-margin renewals are rescued *less* often (37%
  against 50%, module arm). A low flat margin goes with a flat that is already at the default, not
  with room under it.
- **Q5 held, on the wrong reason.** No renewal needs zero rise. That is because giving up £g always
  costs us, and a hazard cut costs us too wherever the margin is below g. The pre-registration
  credited it to negative-margin renewals.

**What this answers for the open row.** On the world's own book a sharing rise rescues **40% of
advice cases (314 of 780), across 95 of 192 accounts**. The 18-case figures (10 of 18 at Deller's
slope, 18 of 18 at the world's) do not describe this book. What decides a case is whether the
account's fixed renewal sits at least £g a month under the default. That fails in most renewals
from 2021 onward and in nearly none in 2020. In the world arm the price's own effect on staying
moves the count by 1–3 renewals.

**What a design would have to read.** The default's headroom per account, in the year of the
renewal. The company can read it: the cap is published. **I cannot yet say** whether the 57% of
renewals no rise can reach would be better served by the one-off fee (C35, sibling page) or by no
advice at all. That needs the fee's own count on the same book.

Script: `/var/tmp/retention_rise/per_renewal.py`. It is not in the tree; its logic is stated
above. `python3 <script> <probe json> [linear]`, from the repo root with `PYTHONPATH=.`.

### 4c. The choices the build makes (`next_best_action.price_retention_rise`, 2026-10-17)

The build gives the company §4b's decision using only what it holds. Where §4b read the world, the
build makes these choices:

- **The cap is the published default, not the rate a stayer is billed.** Headroom is the published
  default unit rate minus our own Fixed Retention Tariff offer, ex VAT, times the account's annual
  volume over 12 (`save_offer.published_default_rate_ex_vat`). Through the EPG the published rate
  is EPG-net. That is what the household pays, so it is the comparison it makes.
- **Before 2019 the cap is unknown, and the rise is refused.** Ofgem published no per-fuel default
  unit rate before the cap; it published a dual-fuel annual bill only (`svt_rates_active_passive_2016_2025.md`
  §1a). The company could read its own default tariff instead, but no such record crosses the seam
  today. So the rise fails closed and names the GAP. It does not borrow the world's table.
- **The hazard is the company's forecast.** It is B11's per-account departure p, turned into a
  constant monthly hazard and read at both ends slice 13 brackets: the full fit window, and the
  cut-year window. Neither end is preferred. Slice 13 found the level is not identified at the cut.
- **The staying response is the published slope**, 0.0015 P(stay) per £/yr, applied as +0.0015·d to
  the monthly hazard. It overstates the world's own response (§4a: 0.00065), which errs against us
  (F11).
- **Our floor holds twice, and a shed account is not a share.** The smallest rise must bring our side
  to ≥ 0 both with the hazard held and with the slope applied. A rise that clears zero only because
  it drives a loss-making account away is refused. That is §4b's trap, stated as a rule.
- **The household's floor** is the rise paid over its expected supplied months, at most its benefit
  over the horizon.
- **It is off by default** (`DecisionPolicy.next_best_action_shares_by_retention_rise`). With it
  off, `decide` is unchanged.

### 4d. The count through the company's own code (DEVELOPMENT, 2026-10-17)

This is §4b's 260 renewals, priced by `price_retention_rise` on the company's own inputs
(`python3 -m tools.retention_rise_count <probe json>`). The prediction and the grades are in
`docs/staging/records/SEAT_PREREG_C35_THE_RETENTION_RISE_THROUGH_THE_COMPANYS_OWN_CODE_AT_BOTH_HAZARD_ENDS_2026-10-17.md`.

- **The count is 211 of 780 (27%), at both hazard ends.** It is 71, 71 and 69 for the three effects.
  The hazard end changes the rise and what the household keeps (median 40% of its gross benefit on
  the full window, 38% on the cut-year window). It changes no case.
- **314 − 211 = 103.** The world rescues 104 cases before 2019, and there the company has no
  published default to read, so it refuses. One case runs the other way, and its cause is not
  established.
- **From 2019 the company's count matches the world arm to within one case** (71/71, 71/71, 69/68).
  The headroom under the published cap is the world's own headroom, read from the company's side.
- **Of the 372 cases from 2019, 158 are refused because the rise needed is above the headroom.** None
  is refused on the household's floor.

### 4e. The rise BILLED, not only recorded (C34's price half, 2026-10-24)

Through §4d the rise was priced and written in the decision log, and the household was billed
the fix as struck: "records only" (prereg of 20 Oct, R1). This section is the knowledge for billing
it. `company.pricing.renewal_rate_chain.bill_the_shared_rise` is writer 7, and its switch is
`DecisionPolicy.renewal_rate_bills_the_shared_rise`, off on every standing policy.

**What the rules require, read again for a billed price.** Nothing new is needed beyond §1–§3. The
rise is part of the fixed offer in the renewal notice (SLC 22C, 31I). The notice states the price
before the household accepts it, so this is not a mid-term variation. On a Fixed Retention Tariff
the cap sets no ceiling (§1). The ceiling the design keeps is the **published default**, because a
stayer offered a fix above it goes onto the default instead (§4a). That makes it a commercial
ceiling, not a legal one, and the design treats it as binding.

**The choices the build makes:**

- **Where:** at the renewal notice, after the rate chain has closed and before the world's roll is
  asked. The household therefore answers the raised price, by the same route a retention offer's
  price takes (`ask_world_at_offer`). The rise is priced on the churn belief, and the churn belief
  reads the struck rate, so the rise cannot sit inside the chain.
- **Which leg:** the roll leg alone. The notice carries one price, and the riding leg is priced later
  on the same start, so it is not raised. A dual household's rise is therefore priced on less room
  than the recorded decision uses (that sums both legs, `HouseholdRenewalTerms`). This errs towards
  fewer rises.
- **Which effect:** the smallest hazard cut in the stated range, (GBP 2, 0.1 pt)
  (`renewal_advice_desk.BILLED_ADVICE_EFFECT`). One price needs one effect. Crediting the advice
  with the least it might do makes the rise the largest our side needs (F11).
- **Both floors stay.** Ours holds twice (hazard held, and the published slope applied), and the
  household's floor holds too. The writer re-checks the headroom. Every refusal leaves the struck
  rate and names its reason. A rise above the headroom is refused, never trimmed to fit: a trimmed
  rise would leave our side below zero, and that is the refusal C34 already makes.
- **Unit:** GBP/month over the account's own annual volume, as GBP/MWh (rise × 12 / MWh).

**The table over the 18 B11-scale cases** (offer GBP 200/MWh, 2.7 MWh, effect as billed per row,
headroom at the §4a quartiles; C34 alone advises **none** of the 18). Each cell shows GBP/month
and GBP/MWh billed, or the reason:

| margin | hazard | effect | headroom unknown (pre-2019) | 0 | 1.35 (median) | 4.00 | 12.38 (p90) |
|---|---|---|---|---|---|---|---|
| 5 | 0.5% | 2, 0.1 | refused | refused | refused | 2.28 / 10.13 | 2.28 / 10.13 |
| 5 | 0.5% | 2, 0.3 | refused | refused | refused | 2.00 / 8.89 | 2.00 / 8.89 |
| 5 | 0.5% | 3, 0.3 | refused | refused | refused | 3.21 / 14.27 | 3.21 / 14.27 |
| 5 | 3% | 2, 0.1 | refused | refused | refused | 2.22 / 9.87 | 2.22 / 9.87 |
| 5 | 3% | 2, 0.3 | refused | refused | refused | 2.00 / 8.89 | 2.00 / 8.89 |
| 5 | 3% | 3, 0.3 | refused | refused | refused | 3.17 / 14.09 | 3.17 / 14.09 |
| 15 | 0.5% | 2, 0.1 | refused | refused | refused | refused | refused |
| 15 | 0.5% | 2, 0.3 | refused | refused | refused | 2.00 / 8.89 | 2.00 / 8.89 |
| 15 | 0.5% | 3, 0.3 | refused | refused | refused | refused | refused |
| 15 | 3% | 2, 0.1 | refused | refused | refused | 2.97 / 13.20 | 2.97 / 13.20 |
| 15 | 3% | 2, 0.3 | refused | refused | refused | 2.00 / 8.89 | 2.00 / 8.89 |
| 15 | 3% | 3, 0.3 | refused | refused | refused | 3.73 / 16.58 | 3.73 / 16.58 |
| 30 | 0.5% | 2, 0.1 | refused | refused | refused | refused | refused |
| 30 | 0.5% | 2, 0.3 | refused | refused | 0.33 / 1.47 | 0.33 / 1.47 | 0.33 / 1.47 |
| 30 | 0.5% | 3, 0.3 | refused | refused | refused | refused | refused |
| 30 | 3% | 2, 0.1 | refused | refused | refused | refused | refused |
| 30 | 3% | 2, 0.3 | refused | refused | refused | 2.00 / 8.89 | 2.00 / 8.89 |
| 30 | 3% | 3, 0.3 | refused | refused | refused | refused | refused |
| **billed** | | | **0 / 18** | **0 / 18** | **1 / 18** | **12 / 18** | **12 / 18** |

Reading it:

- **At the median account's headroom (GBP 1.35/month), the switch bills 1 case in 18.** The rises
  our side needs are GBP 2.00–3.73/month. This is §4d's finding seen from the billing side: 158 of
  the 372 cases from 2019 were refused above the headroom.
- **The 12 are not §4's 10, and I cannot yet say why.** §4 counted 10 of 18 clearing both floors
  under the published slope, and none of the six GBP 30 cases. Here two GBP 30 cases are billed,
  at (2, 0.3 pt), and the two GBP 15 cases §4 lost to the household's floor are refused, as §4 said.
  I first wrote that the difference was volume (2.7 MWh here, 3.6 in §4). That is refuted: at 3.6
  MWh the count is still 12. It is not the desk's clamp on the cut either, since no case here has a
  cut above its hazard. §4's script was not kept in the tree, so the two cannot be diffed line by
  line.
- The repeated GBP 2.00 is the published slope's arm setting the floor of the search, not a
  coincidence of inputs. At each of those rows the hazard-held rise is smaller.
- Script: `/var/tmp/c34_shared_rise/table.py` (not in the tree), run from the repo root with
  `PYTHONPATH=.`.

**What a run with it on can and cannot say.** The world delivers no advice: no world mechanism
gives an advised household the hazard cut or the saving the company credits (searched `simulation/`
and `sim/`, 2026-10-24). An arm with the switch on therefore bills a rise on exactly the accounts
C34 would advise, and the world answers the price alone. Its margin delta is a **transfer**, plus the
world's own staying response to it. It cannot show value created (M2), and a positive delta must not
be read as the price half working. What it *can* test is the cost side of the company's claim: that
a rise priced to the company's floor, with the published slope applied, does not cost more in
departures than the company predicted. The arm pair is pre-registered in
`docs/staging/records/SEAT_PREREG_THE_SHARED_RISE_BILLED_AT_THE_NOTICE_AGAINST_RECORDED_ONLY_2026-10-24.md`
and has not been launched.

**GAP (new):** an advised household's effect in the world. Until the world delivers advice, created
and shared cannot be measured together in one run.

## 5. Gaps, in one place

1. Each case's headroom under the cap, if it is on a default tariff (§1).
2. What happens to the BAT after 31 March 2027, and the permanent-ban workstream (§2).
3. How Ofgem reads SLC 0.3 for a retention tariff bundled with advice (§3a).
4. Whether a tariff-price share avoids consumer-credit treatment (§3c).
5. The longest permitted fix (§3d).
6. The household's benefit horizon from supplier advice (inherited, §6.1).
7. The staying response to a bundle of advice and a higher price. The Deller slope is a bound, not
   a measure (§4). The world's own price-only slope at a rise is now measured: 0.00065 per £/yr at
   the median (§4a). The bundle is still unmeasured.
8. Whether the licence stops a passive household being rolled onto a fix dearer than the default
   (§4a). The world's decline-and-stay rule rests on behaviour alone.
9. The default a household would roll onto before 2019, as the company could know it (§4c). No
   per-fuel default was published, and the company's own default-tariff record does not cross the
   seam. The rise is refused there, which accounts for 104 of §4b's 314 cases.
10. What advice does to a household in the world (§4e). No world mechanism delivers it, so a billed
    rise can be graded only as a transfer.

## Sources

- Ofgem, *Ofgem retains ban on acquisition-only tariffs*, press release, 30 July 2024
  (ofgem.gov.uk/press-release/ofgem-retains-ban-acquisition-only-tariffs, fetched 2026-10-16).
- Ofgem, *Future of the Ban on Acquisition-only Tariffs (BAT) after March 2025*, consultation page
  (ofgem.gov.uk/consultation/future-ban-acquisition-only-tariffs-bat-after-march-2025), and
  *Final Consultation Future of the BAT*, May 2024 (ofgem.gov.uk/sites/default/files/2024-05/Final_Consultation_Future_of_the_BAT.pdf).
  Both were seen as search results on 2026-10-16 and were not read in full.
- Cornwall Insight, *Ofgem's decision to retain the BAT*, alert, 15 November 2024. Title only.
- R1, R6 and R7, as cited in `a_save_offer_against_the_switching_rules_and_the_seam.md`. The
  November 2025 renewal to 31 March 2027 is R7.
- Deller, Waddams Price, Giulietti, Loomes, Moniche and Jeon (2021), *Energy Journal* 42(3), via
  `retention_slope_per_pound_of_renewal_cut.md`.
- `how_a_supplier_prices_a_share_of_value_it_creates_for_a_household_2026-10-14.md` (consumer
  credit, SLC 0.6).
