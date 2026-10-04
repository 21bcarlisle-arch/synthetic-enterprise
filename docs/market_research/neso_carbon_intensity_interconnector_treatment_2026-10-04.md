# How NESO's carbon intensity treats the interconnectors its factor table does not name

**Knowledge:** none -- no knowledge page covers grid carbon intensity yet; this anchors EP13's reconstruction (`docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` §33), which is where it is read

*2026-10-04. The question EP13 §32 left open: what NESO's own published national series does with
North Sea Link (Norway, `INTNSL`) and Viking Link (Denmark, `INTVKL`). Neither has a row in its
factor table. The answer decides where between §32's two arms the truth sits. Scratch, predictions
and outputs: `/var/tmp/se-ep13-s33/`.*

## What NESO publishes about it

- **The methodology does not say.** *Carbon Intensity Forecast Methodology* (github
  `carbon-intensity/methodology`, last revised 2021-09-24) predates both cables. Its rule for
  imports is that "daily at 6am, the average generation mix of each network the GB grid is
  connected to through interconnectors is collected for the previous 24 hours through the ENTSO-E
  Transparency Platform API", and Table 1's factors are applied to that mix. **Table 1's import
  rows (French ~53, Dutch ~474, Belgium ~179, Irish ~458) are only the defaults used when ENTSO-E is
  down.** The regional methodology and the API definitions page add nothing on either cable.
- **The live `/intensity/factors` endpoint (fetched 2026-10-04)** has French, Dutch and Irish rows
  only. It has no Norway or Denmark row, and it no longer has the Belgium row that Table 1 carries.

## What NESO's own data shows (measured, not stated anywhere)

**Which cables are in NESO's generation mix.** `api.carbonintensity.org.uk/generation` publishes
NESO's mix as percentages. Its imports share over its nuclear share has to equal metered imports
over metered nuclear (`FUELHH`), whatever denominator NESO uses. The instrument check holds: NESO
gas/nuclear matches FUELHH (CCGT+OCGT)/NUCLEAR to the third decimal place in every month of 2022 and 2024.

| mean abs error of the imports/nuclear ratio | 2022 (12 months) | 2024 (12 months) |
|---|---|---|
| all nine cables | 0.022–0.105 | 0.211–0.436 |
| all but Viking | 0.022–0.105 | 0.054–0.266 |
| **all but Viking and ElecLink** | **0.021–0.070** | **0.040–0.119** |
| the seven with a published factor (ElecLink in, NSL and Viking out) | 0.041–0.168 | 0.091–0.269 |

A non-negative regression of NESO's implied import MW on each cable's metered flow, month by month,
gives North Sea Link a coefficient of 0.55–1.12 (mostly 0.95–1.11) in all 24 months. Viking gets
0.00–0.22 and ElecLink 0.00–0.45 (ElecLink imported nothing in four of 2024's months). **NESO counts
North Sea Link as an import. Viking Link and ElecLink are not in its generation mix at all.**

**What factor NESO gives North Sea Link.** The intensity series does not identify it. A joint fit of
NESO's actual intensity on its own mix, with gas split CCGT/OCGT by the meters, gives a scale of
1.006 (2022) and 0.998 (2024). That fit puts NSL at 36 and 23 gCO2/kWh, but the other cable
coefficients are collinear: IFA2 comes out at −62. With the other cables held at Table 1, monthly
NSL estimates scatter from −191 to +152 g. Pooled fixed-factor arms:

| pooled MAE, gCO2/kWh | NSL at 0 | 50 | 120 | 394 (GB CCGT) |
|---|---|---|---|---|
| 2022 | **4.08** | 4.25 | 4.66 | 7.16 |
| 2024 | **6.17** | 6.55 | 7.26 | 10.93 |

**So NSL is priced low by NESO, not like gas.** The error rises steadily as the factor rises from
zero, which matches the methodology applying Table 1 to Norway's mix (mostly hydro, at 0). The
exact figure is not established here.

## What this does and does not establish

- **Established:** NSL is inside NESO's import share and priced low. Viking and ElecLink are absent
  from NESO's mix. When it is published, NESO's intensity counts neither cable in the numerator or
  the denominator.
- **Not established:** NSL's factor as a number. It would need Norway's ENTSO-E mix by day with
  Table 1 applied, which is NESO's rule. That needs an ENTSO-E token and is not fetched. Also not
  established: whether either rule changed in 2025.
- **A second gap this exposes:** `sim/elexon_fuel_outturn.py` gives ElecLink the French factor, which
  is a reasonable reading of the rule. NESO's series does not do that, so the reconstruction prices a
  cable its target leaves out. *(Closed by EP13 s34, 2026-10-04: ElecLink and Viking are now served
  and left out of the mix.)*

## Norway's annual mix: the coarse reading of NESO's rule (added 2026-10-04, EP13 s35)

The daily ENTSO-E mix needs a token. The ANNUAL national mix does not. Statistics Norway table
08307 (*Production, imports, exports and consumption of electric energy*, GWh, `data.ssb.no`,
fetched 2026-10-04) splits production into hydro, wind, solar and thermal. Under Table 1, hydro,
wind and solar are zero. Thermal is not split by fuel in 08307, so Table 1 brackets it between
biomass (120) and CCGT (394).

| year | total GWh | thermal GWh | thermal share | NSL factor at 120 | at 394 |
|---|---|---|---|---|---|
| 2020 | 154,197 | 2,670 | 1.73% | 2.1 | 6.8 |
| 2021 | 157,113 | 1,612 | 1.03% | 1.2 | 4.0 |
| 2022 | 145,942 | 2,319 | 1.59% | 1.9 | 6.3 |
| 2023 | 153,973 | 2,528 | 1.64% | 2.0 | 6.5 |
| 2024 | 157,136 | 2,357 | 1.50% | 1.8 | 5.9 |
| 2025 | 161,793 | 2,070 | 1.28% | 1.5 | 5.0 |

**Established:** on NESO's own rule, applied to Norway's published annual mix, North Sea Link
imports at 1–7 gCO2/kWh. That agrees with §"What factor" above, where 0 g fitted best and 50 g
was already worse. **Not established:** the daily figure, which NESO actually uses. The annual
figure flattens Norway's seasonal thermal. It also ignores that NSL lands in bidding zone NO2,
not the national average. Both effects work inside a band of a few grams, and against a GB
average near 150 g they are second-order.
