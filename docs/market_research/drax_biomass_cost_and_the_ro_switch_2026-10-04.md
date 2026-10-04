# What Drax publishes about its biomass cost, and whether it locates the RO units' price switch

**Knowledge:** none -- no knowledge page covers biomass dispatch cost yet; this anchors EP13's reconstruction (`docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` §39), which is where it is read

*2026-10-04. The question EP13 §38 left open: Drax units 2-4 (RO) back off when the day's market
index price (MID) falls below a level that moves by year. Is that level the fuel cost per MWh minus
the ROC value? Scratch, fetched documents and the timestamped prediction are in
`/var/tmp/se-ep13-s39/`.*

## What Drax publishes, by year

Drax does not publish a biomass cost per MWh every year. Most years it publishes a pellet
*production* cost in $/t, FOB at its own plants. That covers only self-supply, before shipping and
before third-party purchases, so it is not a cost per MWh generated.

| year | what Drax published | source |
|---|---|---|
| 2019 | biomass cost "c.£75-80/MWh", target "c.£50/MWh" by 2027 | Drax Capital Markets Day, Nov 2019, *Biomass Operations and Cost Reduction Initiatives* ([pdf](https://www.drax.com/wp-content/uploads/2019/11/3-CMD-2019-Biomass-generation-cost-reduction-FINAL.pdf)) |
| 2020 | pellet production cost $153/t (2019: $161/t). No £/MWh | Drax FY2020 results, 25 Feb 2021 ([pdf](https://www.drax.com/wp-content/uploads/2021/02/Drax-Full-Year-Results-25-February-2021.pdf)) |
| 2021 | FOB production cost $143/t (2018: $166/t). "a higher cost of biomass in GBP, reflecting historic forward foreign exchange hedging". No £/MWh | Drax FY2021 results, 24 Feb 2022 ([pdf](https://www.drax.com/wp-content/uploads/2022/02/Drax-2021-FYR-Announcement.pdf)) |
| 2022 | no cost figure. See the next section | Drax FY2022 results ([pdf](https://www.drax.com/wp-content/uploads/2023/02/Drax-2022-FYR-Announcement.pdf)) |
| 2023 | "all-in contracted cost of biomass for generation in the UK to be over £100/MWh in 2023" (a forecast, made Dec 2022) | [Argus, 2022-12-16](https://www.argusmedia.com/en/news-and-insights/latest-market-news/2401547-drax-pellet-production-generation-costs-up-update) |
| 2024 | none found in the FY2024 presentation | [pdf](https://www.drax.com/wp-content/uploads/2025/02/Drax-2024-FYR-Presentation.pdf) |

**The ROC side.** The buy-out price is in the regulation commons
(`docs/domain_artefact_library/regulatory/ro_obligation_and_buyout.json`): £48.78 (OY2019), 50.05,
50.80, 52.88, 59.01, £64.73 (OY2024). A generator sells a ROC for about buy-out plus the recycle
payment from the buy-out fund. **The recycle value is not in the knowledge layer**, so buy-out is
only a lower bound on what a ROC earns. That makes fuel minus buy-out an *upper* bound on the switch.

## What Drax says set its dispatch in 2022

Drax's FY2022 results describe a different mechanism from fuel cost, in its own words:

> "we have optimised our biomass generation and logistics, buying back positions in the first half
> of the year and reprofiling to the second half ... Over the past 12 months, the cost of biomass in
> the European spot market has increased significantly, making it more challenging to procure and
> generate additional power with a margin. As a result of higher biomass prices, this created
> opportunities for the sale of biomass in addition to generation. Most of the biomass we use is
> under long-term contracts."

So in 2022 the price at which burning a pellet stopped paying was set by what the pellet would fetch
**if sold, or if burned in a later half-year**, not by what it cost under contract. That is an
opportunity cost. No public series for it was found here: the European pellet spot indices
(e.g. Argus CIF ARA) are subscription products.

Drax also forward-sells its ROC output (FY2020: 24.4 TWh for 2021-23 at £48.5/MWh; FY2021: 20.4 TWh
for 2022-24 at £70.2/MWh). A hedge does not move the switch. Against a forward sale the daily choice
is still "generate at fuel cost" or "buy the power back at the day's price", which is the same
comparison.

## Graded against EP13 §38's switch levels

| year | §38 switch (bin reading) | fuel − buy-out from published figures | verdict |
|---|---|---|---|
| 2019 | below the lowest bin (£20-30); no day cheap enough | £75-80 − 48.78 = ≤ £26-31 (upper bound) | **consistent**, not a test: both say the switch is under ~£30 |
| 2020 | ~£20 | no £/MWh cost published | ungraded |
| 2021 | ~£55 | no £/MWh cost published | ungraded |
| 2022 | ~£125 | no cost published; Drax names an opportunity cost instead | ungraded as a fuel-cost switch; the published mechanism is a different one |
| 2023 | ~£75, graded | "over £100" − 59.01: a lower bound on the cost against a lower bound on the ROC, so no bound on the switch either way | ungraded |
| 2024 | ~£55 | none | ungraded |

**Metered check of the 2022 statement.** Drax 2-4 mean output, second half minus first, from
B1610 (§37's per-unit series): 2019 +56, 2020 −224, 2021 +240, **2022 +306**, 2023 −84,
2024 −11 MW. 2022's shift is the largest in the record, as the reprofiling statement implies. But it
is only 66 MW above 2021's, and the half-year comparison carries outage season and the price path
with it. So it is consistent with the statement, and it does not isolate it.

## What this does and does not establish

- **Established:** the published record locates Drax's cost in only one year that can be graded
  (2019). There the cost minus the ROC is consistent with the switch. In 2022 Drax names an
  opportunity cost, spot resale and reprofiling, as what governed dispatch, not contracted fuel cost.
- **Not established:** a biomass cost per MWh for 2020-22 or 2024. A £/MWh figure built from the
  $/t production cost would need the delivered cost of third-party fibre, shipping, FX and plant
  efficiency, and none of those is published per year. **The ROC recycle value by year** is also
  unsourced. It is the next thing to source on the ROC side, from Ofgem's annual RO reports.
- **What follows for a dispatch rule:** "the switch sits at published fuel cost minus ROC" cannot be
  built from public data for five of six years, and in 2022 it would be the wrong mechanism even
  with the data. A rule that takes its location from fuel cost would carry `None` in those years.
</content>
</invoke>
