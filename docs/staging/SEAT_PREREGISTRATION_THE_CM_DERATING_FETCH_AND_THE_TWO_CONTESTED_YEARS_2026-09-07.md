**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a50-cm-derating-and-the-ic-leg

# PRE-REGISTRATION: what I expect the primary CM register to say, written before I read it

**Written:** 2026-09-07, delivery seat, claim `a50-cm-derating-and-the-ic-leg`.

The drawn item asks for three things at once: fetch the published de-rating factors and apply them
to the I&C leg; upgrade the auction artefact's entries from `secondary` to `primary`; and settle the
two contested years. The first is already answered as I write this — the factors are in hand. The
other two are not, and this file fixes the predictions before I look.

## What is already established as I write (not a prediction)

`emrdeliverybody.com` returns **HTTP 404**, not 403 — the host is retired, not blocking. The
publisher's own register moved to the NESO data portal and is reachable:
`https://api.neso.energy/dataset/0b3ab475-.../capacity-market-de-rating-factors.csv`, 801 rows,
25 auctions from the 2016-17 Transitional auction to the 2029-30 T-4. Every DSR row is there.
That is a **primary** source by this artefact's own legend: the publisher's own auction register.

Two things it already shows that our own artefact's prose got wrong, recorded here because I have
read them and they are therefore not predictions:

1. **DSR is NOT duration-split in the published register.** One DSR factor per auction. Only
   `Storage` carries `(Duration 0.5h)` ... `(Duration 12h)` classes. Our artefact says de-rating is
   "duration-dependent for DSR and storage"; the register says that is true of storage alone.
2. **The DSR factor is keyed to the auction ROUND, not the delivery year.** T-4 for DY *Y* carries
   the identical factor to T-1 for DY *Y-4* in every one of the eleven pairs available — because
   those two auctions are held in the same round, against the same Electricity Capacity Report.
   This is the SAME four-year offset that made `capacity_market.py` the third disagreeing home for
   the clearing price, arriving a second time by a different door.

## Prediction 1 — the DY 2023/24 T-1 clearing price

Ofgem Annex 9 says £60/kW; Montel's T-1 review says £45.00 and puts £60.00 at DY 2021/22.
Our artefact carries `null` and names both.

> **I predict the primary register gives £60.00/kW for DY 2023/24 T-1, and that Montel is the
> source with the one-year attribution slip.**

Reasoning: our artefact already carries Montel's £60.00 at DY 2021/22 *as its own value for that
year*, so if Montel were right about DY 2023/24 = £45.00 the two sources would disagree at two
delivery years, not one. A single slip in one source explains one disagreement; it is the smaller
claim.

**This prediction can be wrong**, and the shape of being wrong is: the register says £45.00, Ofgem
is the slipped source, and our DY 2021/22 T-1 entry — which rests on Montel *alone* and is
explicitly uncorroborated by the Ofgem annex — becomes suspect too.

## Prediction 2 — the DY 2025/26 T-4 clearing price

Montel implies £30.59 as a range maximum; S&P Global's contemporaneous headline says £35.30/kW-yr
for ~42.7 GW.

> **I predict the register gives £30.59, and that the £35.30 is the same auction in delivery-year
> money against £30.59 in the auction's fixed price base.**

The artefact already flags this reading as "plausible but not established". If the register carries
one figure and not the other, the ratio 35.30 / 30.59 = 1.154 is the thing to look at: an indexation
of ~15.4% over four years is about 3.6%/yr, which is a plausible GDP deflator path for 2022-2026 and
would corroborate the reading. If the ratio is not what indexation would give, the two figures are
not the same auction in different money and I have no account of them.

## Prediction 3 — the size of the correction to the I&C leg

The drawn item states the overstatement as **£632/site/yr at 2024 prices on a 35 kW site**. I have
not checked that figure. A 35 kW site at the DY 2024 T-4 price of £18.00/kW grosses £630 before
de-rating, so £632 looks like the *whole gross CM leg*, i.e. it is the overstatement only if the
de-rating factor were ~0. The published DY 2024 T-4 DSR factor is **0.7921**.

> **I predict the true overstatement at DY 2024 on a 35 kW flex site is ~21% of the gross CM leg,
> not 100% of it: of order £130/site/yr, and the drawn item's £632 is off by a factor of ~4.8.**

I also predict the site in the drawn item is not 35 kW of flex. This module's flex is 10% of peak
demand, so a *35 kW flex* site is a ~350 kW peak site — around 2 GWh/yr of consumption. I will
report the correction per site at the real EACs the book uses, not at an assumed 35 kW.

## What "done" means for this item

The drawn item is DIRECTION with no exit test, so I am fixing one:

1. `derating_factor()` stops returning `None` for DSR and returns the published factor for the named
   auction and delivery year — keyed the way the register keys it, with the auction-round offset
   handled in one place and named.
2. The I&C leg's CM revenue multiplies by de-rated flex, and a control asserts it is strictly less
   than the rated-flex product for every established year — a control keyed to the property, not to
   today's number.
3. Every entry the register covers moves to `primary` provenance, with the ones it does not cover
   left where they are rather than promoted by association.
4. The two contested years are settled or the reason they remain contested is written down beside
   this prediction, whichever the record supports.

If the register does not carry clearing prices at all, items 1-2 still land and 3-4 become a
separate finding rather than a silent omission.

---

# OUTCOME, appended after the measurement. The predictions above are left exactly as written.

Full write-up:
`SEAT_FINDING_THE_CM_DERATING_GAP_IS_FILLED_FROM_THE_PRIMARY_REGISTER_AND_IT_MOVED_A_PRICE_NOBODY_WAS_CONTESTING_2026-09-07.md`.

| prediction | outcome |
|---|---|
| 1. DY 2023/24 T-1 is GBP60.00, Montel slipped | **CONFIRMED.** GBP60.00. |
| 2. DY 2025/26 T-4 is GBP30.59 | **CONFIRMED.** GBP30.59. The indexation account of S&P's GBP35.30 remains a guess and is recorded as one. |
| 3. Overstatement ~GBP130/site-yr at DY2024, drawn item off by ~4.8x | **CONFIRMED.** GBP130.98 and 4.81x. |
| 3b. The "35 kW site" is not a 35 kW site | **CONFIRMED.** 350 kW peak, ~2.0 GWh/yr. |

**One claim above is REFUTED, and it was in the section headed "not a prediction".**

I wrote, as something already established because I had read it: *"T-4 for DY Y carries the
identical factor to T-1 for DY Y-4 in every one of the eleven pairs available."* **The offset is
Y-3, not Y-4.** At Y-4, zero of nine pairs match; at Y-3, all nine do. A T-4 held in February of
year H delivers from October H+3.

The control I wrote for the claim refuted it on its first run — which is the only reason it was
caught, because I had read the paragraph three times. My own worked example in it ("T-4 DY2029/30
and T-1 DY2026/27 are both 0.8558") is a THREE-year gap: I had the right pair and wrote the wrong
formula over it, inside a paragraph warning about a four-year offset.

Two lessons, and the second is the one worth keeping:

1. Labelling something "already established as I write (not a prediction)" does not make it
   checked. It exempted the claim from the scrutiny the three numbered predictions got, and it was
   the only claim in the file that was wrong.
2. The general rule is **T-N[Y] == T-1[Y-N+1]** — one auction round, one Electricity Capacity
   Report. The substituted T-3 obeys it too (T-3[2022] == T-1[2020]), which is the evidence it is
   a rule about rounds and not a coincidence of the T-4 series.

Also stated above as established and also wrong in the same direction, though it came from the v1
artefact rather than from me: de-rating is **not** duration-dependent for DSR. One factor per
auction; only `Storage` is duration-split.

**An entry nobody was contesting turned out to be wrong.** DY 2021/22's T-1 was GBP45.00, not the
GBP60.00 carried: one source had transposed two years' figures, and a transposition damages two
entries while a contest flag marks one. I named this as the *wrong* branch of prediction 1 ("the
shape of being wrong is..."). The suspicion was right and the conditional was wrong — that entry
was wrong whichever way the slip went.
