# Director evidence: spain compared with GB (knowledge only)

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 07:17 GMT: "To be clear this is not to turn into SIM or supplier action at this stage it just to understand how transferable what we are building in the UK is to other markets and where new SIM and new supplier features would have to be built."
- 07:22 GMT: "You may have to look at cooling and cooking  too? Also switching, homemove? Does debt sit with supplier or dno?"

This is one of seven country packs: Australia, France, Germany, Italy, Spain, Belgium and Japan. The cover steer is `DIRECTOR_STEER_OTHER_MARKETS_ARE_KNOWLEDGE_ONLY_2026-10-25.md`.

## What to do with it

- **Knowledge only. Build nothing from this pack, and don't change any world or supplier priority.**
- Publish it as a Knowledge page in an "Other markets" section, and register its concepts.
- Keep its transferability ratings and its lists of new features as the record of what each component would need.

---

# Spain vs Great Britain: household energy market evidence pack for Poesys

*Knowledge only, not a build plan. Compiled 25 Oct 2026. Labels: **[derived]** means my own arithmetic; **[unverified]** means from memory and not confirmed in this research pass. GB comparison figures are mostly [unverified] because the research budget went on Spain.*

**Research limits.** The shared web-search budget ran out partway through. Four checks I planned were never run: REE's 2025 full-year mix, 2025 EV sales, the typical household kWh, and full Eurostat HDD series. Where those gaps matter they are marked [unverified] or listed in (d). If you want them closed, a follow-up message can resume searching.

---

## 1. Weather and climate

- **Spain degree days:** HDD 1,478 and CDD 384 in 2022. The EU averages were HDD 2,858 and CDD 140 ([Energy Institute, citing Eurostat](https://knowledge.energyinst.org/new-energy-world/article?id=137740)). Spain's CDD was 302.7 in 2024 ([Eurostat nrg_chdd_a via DBnomics](https://db.nomics.world/Eurostat/nrg_chdd_a)).
- **GB degree days:** about 2,800–3,100 HDD a year, with CDD close to zero [unverified]. Ireland's 2022 CDD was 0.03 ([same Energy Institute source](https://knowledge.energyinst.org/new-energy-world/article?id=137740)), which is a fair stand-in for the British Isles.
- **Regional variation is extreme.**
  - More than 86% of Canary Islands homes have no heating, and only about a third of homes in Extremadura and Andalucía have it ([El Independiente, citing INE 2021](https://www.elindependiente.com/espana/2023/02/24/el-20-de-los-hogares-en-espana-no-tiene-calefaccion-ni-coche-propio/amp/)).
  - Gas heating demand per gas-heated home differs about 2x by climate zone: Atlántico-Norte 2,789 kWh, Mediterránea 3,372 kWh, Continental 5,672 kWh ([SPAHOUSEC II, IDAE/MITECO](https://www.miteco.gob.es/content/dam/miteco/images/es/estudio_spahousec-ii_270619_tcm30-498994.pdf)).
- **Seasonality:** electricity demand peaks twice, in winter and summer (see §12). GB has one winter peak.
- **Separate systems:** the Balearic Islands, the Canary Islands, Ceuta and Melilla are non-peninsular systems with their own dispatch rules and a different 2.0TD calendar in Ceuta and Melilla ([Endesa](https://www.endesa.com/es/te-ayudamos/sobre-tu-factura/cambios-peajes-factura-luz-2021)).

## 2. Energy system

**Generation mix, 2024** ([REE via Renewable Energy Magazine](https://www.renewableenergymagazine.com/panorama/espaa-exporta-mas-electricidad-que-la-que-20241219)):
- Renewables 56%, a record and up about 6 points: wind 23%, solar PV 17% (about 45 TWh), hydro 13%.
- Nuclear 19%. Coal 1.1%. Gas and coal output together fell about 24%.
- Demand about 248 TWh. Net exports about 10 TWh, the third year in a row as a net exporter.
- Renewables are 64% of about 130 GW installed capacity.

**Solar boom:**
- PV capacity rose from 32.35 GW (Jan 2025) to 41.24 GW (Jan 2026) ([El Independiente](https://www.elindependiente.com/economia/2026/02/24/paradoja-solar-espana-precios-negativos-luz-2026/)).
- A record 10.1 GW was added in 2025. PV supplied 18.4% of generation, or 21.3% counting self-consumption ([Energías Renovables, citing UNEF](https://www.energias-renovables.com/fotovoltaica/espa-a-bate-su-r-cord-fotovoltaico-20260915)).
- Prices were at or below zero for 797 hours in 2025 and about 900 hours by early September 2026. The average price PV captured fell from €42.28/MWh (2024) to €29.68/MWh (H1 2026) (same source).

**Nuclear phase-out:** Almaraz I closes Nov 2027 and Almaraz II in 2028; Vandellós II and Trillo close in 2035. Congress rejected extending reactor lives in Nov 2025 ([Noticias Ambientales](https://noticiasambientales.com/energy/spain-confirms-the-closure-of-all-its-nuclear-plants-congress-rejects-extending-the-lifespan-of-seven-reactors/)).

**Wholesale market:**
- MIBEL is a single Iberian bidding zone shared with Portugal, run as an energy-only market. OMIE operates the day-ahead and intraday auctions plus continuous intraday trading [unverified for design detail].
- The day-ahead market moved to 15-minute products on 1 Oct 2025, with the first trading day 30 Sep 2025 ([APG](https://markt.apg.at/en/news-press/sdac-go-live-of-15-minute-market-time-unit-in-day-ahead-market-coupling-successful-as-of-september-30-2025/)). Continuous intraday went quarter-hourly from 18 Mar 2025 ([tarifaluzhora](https://tarifaluzhora.es/info/nuevo-mercado-cuarto-horario-electricidad)).
- Interconnection with France is weak, about 3 GW or about 3% of capacity [unverified]. The IEA has long flagged this ([IEA](https://iea.org/news/iea-praises-spain-for-robust-energy-security-but-sees-need-for-further-improvement-in-other-areas)).
- **Iberian exception (gas price cap):** approved May 2022. It capped the gas price used in power bids at €40/MWh for six months, then raised it €5/MWh a month to €70/MWh. Gas plants were compensated for the difference ([IEA policy page](https://www.iea.org/policies/15621-price-control-in-the-iberian-electricity-market-mibel)). Brussels said it could not run past Dec 2023 ([Euro Weekly](https://euroweeklynews.com/2023/01/20/brussels-informs-spain-the-iberian-exception-can-not-extend-beyond-december-2023/)). For price replay this is a regime break: 2022–23 Iberian prices are not a pure market outcome.
- **Gas:** the hub is MIBGAS. Supply relies heavily on LNG terminals ([IEA](https://iea.org/news/iea-praises-spain-for-robust-energy-security-but-sees-need-for-further-improvement-in-other-areas)). The 2024 gas wholesale price averaged about €35/MWh ([CNMC](https://www.cnmc.es/sites/default/files/editor_contenidos/20250804_NP_Informe_Minorista_ElectricidadyGas_2024.pdf)).
- **Blackout, 28 Apr 2025:** the whole Iberian peninsula went dark. The ENTSO-E final report blamed systemic failures in voltage and reactive-power control ([pv magazine](https://www.pv-magazine.com/2026/03/23/entso-e-report-finds-systemic-failures-behind-2025-iberian-blackout/)).

## 3. Grid

**Operators:**
- REE is the TSO and system operator.
- There are several hundred DSOs, about 330 [unverified]. Five groups (Endesa/e-distribución, Iberdrola/i-DE, Naturgy/UFD, EDP, Viesgo) hold 26.3m of 29.5m supply points, about 89% [derived] ([Energías Renovables, 2021](https://www.renewableenergymagazine.com/panorama/cinco-empresas-controlan-el-90-del-mercado-20210629)).
- GB has 14 licensed DNO areas under 6 groups, plus IDNOs [unverified].

**Connection: a capacity subscription.** This is the biggest structural difference from GB.
- Households contract power in kW. In 2024, 43.2% contracted 4–6 kW and 30.3% contracted 0–3 kW ([CNMC Panel de Hogares Q2 2024](https://cnmc.es/en/node/412028)).
- The smart meter trips if the contracted power is exceeded [unverified].
- Most homes are single-phase [unverified].
- GB households have a fuse, typically 60–100 A, with no subscribed capacity [unverified].

**Network tariff 2.0TD** (all supplies under 15 kW, since 1 June 2021) ([Endesa](https://www.endesa.com/es/te-ayudamos/sobre-tu-factura/cambios-peajes-factura-luz-2021)):
- Three energy periods on weekdays:
  - Punta: 10–14h and 18–22h
  - Llano: 8–10h, 14–18h and 22–24h
  - Valle: 0–8h, plus all day on weekends and holidays
- Two contracted powers: punta-llano (8–24h weekdays) and valle.
- Two power changes are free within 12 months.
- It replaced six earlier tariffs (2.0A and the DHA and DHS variants) ([CNMC Circular 3/2020 material](https://cnmc.es/file/304523/download)).

**Distributor data hub:** distributors run the SIPS supply-point database. Under RD 88/2026 it is centralised, with replies due in 10 days, and a data hub run by the System Operator ([PwC](https://periscopiofiscalylegal.pwc.es/real-decreto-88-2026-de-11-de-febrero-por-el-que-se-aprueba-el-reglamento-general-de-suministro-comercializacion-y-agregacion-de-energia-electrica/)).

## 4. Population and households

- 19.31m households at 1 Jan 2024, average size 2.50, 28.1% single-person. Projected 23.0m by 2039 ([INE](https://ine.es/dyngs/Prensa/PROH20242039.htm?print=1)).
- About 29.5m electricity supply points, including non-domestic ([source above](https://www.renewableenergymagazine.com/panorama/cinco-empresas-controlan-el-90-del-mercado-20210629)).
- GB has about 28m households of 2.4 people [unverified].

## 5. Housing

- **Tenure, 2025:** 73.3% owner-occupied (an INE series low), 20.2% rented, 6.5% other ([Vozpópuli, citing INE ECV](https://www.vozpopuli.com/economia/el-modelo-de-vivienda-en-espana-se-transforma-cae-el-acceso-a-la-propiedad-y-crece-la-concentracion.html)).
- **Flats:** 66% of the population lives in apartments ([EPOV Spain report](https://energy-poverty.ec.europa.eu/system/files/2024-05/epov_member_state_report_-_spain.pdf)). GB is about 20% flats [unverified]. Flats in Spain often have shared (comunitaria) heating; communities of owners can take TUR4 gas ([Selectra](https://selectra.es/energia/info/tur-gas)).
- **Heating fuel, among homes with heating (2021):** gas about 40%, electricity about 34%, the rest oil-derived (heating oil and LPG). About one in five households lacks heating and a car ([INE via El Independiente](https://www.elindependiente.com/espana/2023/02/24/el-20-de-los-hogares-en-espana-no-tiene-calefaccion-ni-coche-propio/amp/)).
- **Heating systems, older survey (2015):** gas boiler 32.7%, electric heat pump (mostly reversible air-to-air) 16.3%, storage heaters 6.1% ([CNMC Panel 2015](https://cnmc.es/eu/node/271580)).
- **Gas consumption:** a gas-heated home uses 7,921 kWh/yr (flat 7,384, house 11,635). Heating is 57%, hot water 38%, cooking 5% ([SPAHOUSEC II](https://www.miteco.gob.es/content/dam/miteco/images/es/estudio_spahousec-ii_270619_tcm30-498994.pdf)). GB averages about 11,500 kWh [unverified].
- **Electricity consumption:** about 3,000–3,500 kWh/yr per household [unverified]. Average spend was €47.8 a month in Q2 2024 ([CNMC](https://cnmc.es/en/node/412028)).
- **Gas reach:** about 7.9m gas consumers [derived from 3.1m TUR = 39%], so only about 40% of households have mains gas [derived]. GB is about 85% [unverified].

## 6. Core regulation

**Regulator and market structure:**
- The regulator is CNMC; the ministry is MITECO.
- Electricity sales shares in 2024: Endesa 28%, Iberdrola 23%, Naturgy 8%. The domestic market remains concentrated ([CNMC 2024](https://www.cnmc.es/sites/default/files/editor_contenidos/20250804_NP_Informe_Minorista_ElectricidadyGas_2024.pdf)).
- Gas shares: Naturgy 27%, Endesa 15%, Repsol 12% (same source).

**PVPC, the regulated electricity price:**
- Open to households and micro-businesses up to 10 kW. Only the comercializadoras de referencia (COR) can supply it; the COR are the incumbents' regulated arms ([eseficiencia](https://www.eseficiencia.es/2023/06/14/nueva-formula-calculo-tarifa-electrica-regulada-aportara-estabilidad-facturas-energeticas)).
- It used to be fully indexed hourly to the day-ahead price. RD 446/2023 blends in futures: 25% in 2024, 40% in 2025, 55% in 2026. The futures basket is 10% monthly, 36% quarterly and 54% annual products. The hourly day-ahead shape is kept (same source).
- Uptake: 8.4m PVPC consumers in 2024 (28.5%) ([CNMC 2024](https://www.cnmc.es/sites/default/files/editor_contenidos/20250804_NP_Informe_Minorista_ElectricidadyGas_2024.pdf)). By end-2025 it was 8.2m (27.4%), about 17 TWh or 22% of household demand ([Diario de León, citing CNMC 2025 report](https://www.diariodeleon.es/economia/260814/2094189/numero-consumidores-acogidos-pvpc-luz-cae.html)).
- Unlike GB's cap, the PVPC is a dynamic price. It is not a ceiling over tariffs that suppliers set freely.

**TUR, the regulated gas price:**
- Assigned by consumption band: RL.1 up to 5 MWh, RL.2 5–15 MWh, RL.3 15–50 MWh; TUR4 for communities of owners.
- Revised quarterly in the BOE. Supplied only by the COR ([Selectra](https://selectra.es/energia/info/tur-gas)).
- 3.1m consumers (39%) in 2024 ([CNMC](https://www.cnmc.es/sites/default/files/editor_contenidos/20250804_NP_Informe_Minorista_ElectricidadyGas_2024.pdf)).

**Licensing:**
- A retailer files a declaración responsable with MITECO. It must lodge guarantees with REE and OMIE and start buying on the market within 6 months. CNMC publishes the list of retailers.
- A retailer without guarantees gets no new supply points or switches ([MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/distribuidores/comercializadores.html)).
- Spain has hundreds of retailers (341 in 2019 ([source](https://www.renewableenergymagazine.com/panorama/cinco-empresas-controlan-el-90-del-mercado-20210629))). The licence bar is lower than GB's Ofgem licence plus its post-2022 capital rules [unverified].

**Consumer protection — new RD 88/2026** (in force 12 Feb 2026; it repeals RD 1435/2002, RD 1718/2012 and Orden ITC/1659/2009) ([PwC](https://periscopiofiscalylegal.pwc.es/real-decreto-88-2026-de-11-de-febrero-por-el-que-se-aprueba-el-reglamento-general-de-suministro-comercializacion-y-agregacion-de-energia-electrica/); [GA-P](https://ga-p.com/wp-content/uploads/2026/02/Energia_electrica.pdf)):
- Cold sales calls are banned.
- Consumers get a separate summary of key terms.
- Price changes need 1 month's notice, with a free right to leave.
- Complaints must be resolved within 15 days.
- Exit fees are removed for non-fixed 2.0TD contracts. On fixed-price contracts the fee is capped at 5% of the estimated remaining energy.
- Retailers with more than 200,000 customers must offer dynamic-price contracts.
- A new independent-aggregator role is created.

**Supplier failures:** unlike GB, there was no wave of failures, and no Supplier of Last Resort or Special Administration regime equivalent was needed [unverified]. The fallback for a failed retailer's customers is transfer to a COR [unverified in detail, see §16].

## 7. Smart meters

- Rollout complete by end-2018: about 27m meters up to 15 kW had remote reading, 99.14% integrated into the remote-management system ([CNMC](https://cnmc.es/mas-de-un-99-de-los-contadores-de-la-luz-ya-eran-inteligentes-diciembre-de-2018-375485)).
- The DSO owns and operates the meters; the consumer pays a meter rental (same source).
- Hourly load curves are on the distributor's portal, and distributors must pass them to retailers (same source).
- Most meters record hourly. After the 15-minute market change, REE interpolates quarter-hour values from hourly reads, and PVPC bills use the average of the four quarter-hour prices ([tarifaluzhora](https://tarifaluzhora.es/info/nuevo-mercado-cuarto-horario-electricidad)).
- GB: the supplier is responsible for the meter and the DCC carries the data. About two-thirds are smart, many not working in smart mode [unverified].

## 8. Billing

- **Basis:** bills use actual reads, not estimated advances plus an annual true-up. RD 1718/2012 required real reads from Apr 2013 and set bimonthly billing ([Xataka](https://www.xatakahome.com/iluminacion-y-energia/nuevo-proceso-de-facturacion-electrica-en-espana-mejorando-el-control-de-consumo)). Monthly billing is now common [unverified]. RD 1718/2012 is now repealed by RD 88/2026, and the new billing-period rule was not confirmed.
- **Payment:** default due date is 20 days from the invoice ([MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/contratacion-suministro/cortes-suministro.html)). Paying by bank direct debit (domiciliación) after the bill is the norm. There is no fixed monthly direct debit building a credit balance, and no prepayment meters [unverified]. The GB prepayment segment and "DD smoothing" have no equivalent.
- **Bill structure:** a power term (€/kW per day × two powers) plus an energy term (€/kWh by period) plus meter rental.
- **Taxes:** electricity tax (IEE) 5.11% plus VAT 21%. During the crisis these fell to 0.5% and 10%/5%, and have since been restored ([Selectra](https://selectra.es/energia/info/factura-luz/iva-luz-impuestos)). The VAT recovery drove the 2024 household price rise ([CNMC](https://www.cnmc.es/sites/default/files/editor_contenidos/20250804_NP_Informe_Minorista_ElectricidadyGas_2024.pdf)). GB VAT is 5% [unverified].

## 9. Settlement

- **Interval:** household supplies are settled on hourly measured data, interpolated to quarter-hours since Oct 2025 ([tarifaluzhora](https://tarifaluzhora.es/info/nuevo-mercado-cuarto-horario-electricidad)). The imbalance settlement period is 15 minutes [unverified date]. Profiling is now only a fallback for meters not integrated into remote reading [unverified].
- **Settlement runs:** REE produces five settlements: initial provisional 1 and 2 (about M+1), intermediate (about M+3), final provisional (about M+8) and final definitive (about M+11) ([REE calendar guide 2024](https://www.ree.es/sites/default/files/12_CLIENTES/Documentos/Guia_calendario_sistema_informacion_liquidaciones_clientes_2024.pdf)). GB MHHS runs about 4 months to its final run (RF) [unverified].
- **Balance responsibility:** the retailer is the settled party (sujeto de liquidación) toward REE and OMIE, with guarantees lodged at both ([MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/distribuidores/comercializadores.html)).
- **Network charges:** the retailer pays access tolls and charges to the DSO (same source).

## 10. Debt and vulnerability

**Disconnection process** (PVPC and free-market households up to 10 kW, primary residence) ([MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/contratacion-suministro/cortes-suministro.html)):
1. Within 2 months of the missed due date, the retailer sends a formal demand for payment with proof of receipt.
2. **Non-vulnerable customers:** the retailer can ask the DSO to cut supply 2 months after that demand.
3. **Bono social customers:** after 4 months, supply drops to a 3.5 kW Suministro Mínimo Vital (SMV) for 6 months, during which it cannot be cut.
4. After payment, supply must be reconnected within 24 hours.

**Supplies that cannot be cut:**
- Electro-dependent medical cases.
- Severely vulnerable households supported by social services.
- Bono social homes with a child under 16, dependency grade II or III, or disability of 33% or more.

**Crisis bans:** a broader ban on cutting basic supplies to vulnerable households runs to 31 Dec 2026 under the Dec 2025 omnibus RDL ([Forbes](https://forbes.es/economia/850166/el-boe-publica-la-prorroga-de-la-prohibicion-de-desahucios-y-cortes-de-suministros-basicos-a-vulnerables/)).

**Bono social:**

| Period | Vulnerable | Severely vulnerable | Source |
|---|---|---|---|
| H1 2025 | 50% | 65% | [SmartGridsInfo](https://www.smartgridsinfo.es/2025/02/14/congreso-extiende-hasta-final-ano-proteccion-energetica-consumidores-vulnerables) |
| H2 2025 | 42.5% | 57.5% | same |
| 2026 | 42.5% | 57.5% | [Forbes](https://forbes.es/economia/850166/el-boe-publica-la-prorroga-de-la-prohibicion-de-desahucios-y-cortes-de-suministros-basicos-a-vulnerables/) |

The structural fallback is 35% and 50%.
- The bono is available only on the PVPC through a COR, and only up to an annual kWh cap.
- 1.71m beneficiaries in Oct 2025 ([Selectra report](https://selectra.es/sites/selectra.es/files/informe_bono_social_2025_0.pdf)).
- The heating bonus (bono social térmico, minimum €40) is paid automatically to bono social holders (same source).
- Spain has no GB-style supplier-run Priority Services Register. Vulnerability is a state-certified status attached to the regulated tariff.

**Energy poverty:**
- 17.5% of Spaniards could not keep the home adequately warm in 2024, against an EU average of 9.2% ([Spotmedia, citing Eurostat](https://spotmedia.ro/en/news/social/romania-outperforms-spain-and-greece-on-the-ability-to-heat-homes)).
- Utility-bill arrears were 7.2% in 2018 ([EPOV](https://energy-poverty.ec.europa.eu/system/files/2024-05/epov_member_state_report_-_spain.pdf)).

## 11. EV, PV, batteries and heat pumps

**Rooftop PV (self-consumption, autoconsumo):**
- 8,137 MW cumulative by end-2024. 2024 additions were 1,182 MW, of which 275 MW residential, about 51,000 homes ([eseficiencia, citing UNEF](https://eseficiencia.es/2025/01/24/espana-acumula-total-8-137-mw-potencia-instalada-autoconsumo-fotovoltaico)). APPA counts 1,431 MW, of which 346 MW residential ([SmartGridsInfo](https://www.smartgridsinfo.es/2025/02/17/2024-instalaciones-autoconsumo-cubrieron-37-demanda-electrica-espana)).
- 2025 additions: 1,139 MW ([Energías Renovables](https://www.energias-renovables.com/fotovoltaica/espa-a-bate-su-r-cord-fotovoltaico-20260915)).
- 683,719 self-consumers, up 48% in a year ([CNMC](https://www.cnmc.es/sites/default/files/editor_contenidos/20250804_NP_Informe_Minorista_ElectricidadyGas_2024.pdf)).

**Self-consumption rules (RD 244/2019)** ([Pérez-Llorca](https://www.perezllorca.com/wp-content/uploads/2019/04/P%C3%A9rez-Llorca-Nota-Jur%C3%ADdica-Marco-regulatorio-para-el-autoconsumo-de-energ%C3%ADa-el%C3%A9ctrica.pdf)):
- Three modes: no-export, export Type A and export Type B.
- **Simplified compensation (Type A):** renewable, 100 kW or less, outside the specific remuneration regime.
  - The retailer credits exported energy on each monthly bill. The credit cannot exceed what was consumed in that period, so there is never a cash payout.
  - VAT applies to the net amount.
- Collective self-consumption is allowed within 500 m on low voltage.
- How exports are valued (at the PVPC hourly price, or an agreed price on the free market) was not confirmed in the fetched excerpt [unverified]. Retailers' "virtual battery" products that carry the credit forward are commercial, not regulatory [unverified].
- GB comparison: SEG export payments with no cap tied to the import bill [unverified].

**Batteries:** 327 MWh of self-consumption batteries in 2024 (down 34%), 2,205 MWh cumulative since 2022 ([Forbes, citing UNEF](https://forbes.es/economia/754574/el-almacenamiento-con-baterias-para-autoconsumo-cayo-un-34-en-2024-segun-unef/)).

**EVs:** 115,932 plug-in cars in 2024 (11.4% share, BEV plus PHEV) ([Interempresas, citing ANFAC](https://www.interempresas.net/Estaciones-servicio/583797-Las-ventas-de-turismos-electrificados-crecen-un-1-9-por-ciento-en-2024.html)). The MOVES III grant scheme ran out of funds in several regions ([Bolsamanía](https://www.bolsamania.com/noticias/ultimas/economiamotor--anfac-senala-su-preocupacion-por-el-agotamiento-de-los-fondos-del-plan-moves-iii-en-nueve-comunidades--20907362.html)). GB's EV share is about 20% or more [unverified].

**Heat pumps:**
- Heat pump sales fell 5.5% in 2024. Air-to-water units' share fell from 18.2% to 15.3%. Air-to-water heat pumps (aerotermia) are chosen in 45% of new single-family homes ([Interempresas, citing AFEC](https://www.interempresas.net/Construccion/589333-El-mercado-espanol-de-HVAC-se-mantiene-estable-con-un-crecimiento-del-0-8-por-ciento.html)).
- Reversible air-to-air units are already widespread (§12), so Spain has a large existing base of heat pumps.

## 12. Cooling

- 42.8% of households had air conditioning in 2015 ([CNMC Panel](https://cnmc.es/eu/node/271580)). Today it is likely over 50% [unverified].
- 1.38m residential AC, heat pump and hot-water units were sold in 2024 ([AFEC via Interempresas](https://www.interempresas.net/Construccion/589333-El-mercado-espanol-de-HVAC-se-mantiene-estable-con-un-crecimiento-del-0-8-por-ciento.html)).
- Spain's CDD (300–390) is more than double the EU average ([sources in §1](https://knowledge.energyinst.org/new-energy-world/article?id=137740)).
- The summer peak (July–August afternoons) rivals the winter evening peak, both near 40 GW [unverified].
- The cooling load overlaps solar output, so it partly offsets midday surplus. Evening cooling falls in the 18–22h punta window.

## 13. Cooking

- 57.3% of homes have a ceramic or induction hob; 36.9% have a gas hob ([CNMC 2015](https://cnmc.es/eu/node/271580)).
- About 1.08m homes cook on mains gas ([SPAHOUSEC](https://www.miteco.gob.es/content/dam/miteco/images/es/estudio_spahousec-ii_270619_tcm30-498994.pdf)). The rest of the gas hobs run on LPG.
- Bottled butane is still common and its price is regulated by the state [unverified on penetration, about several million households]. It is outside the electricity and gas supplier relationship entirely.

## 14. Switching

- **Rates:** 23.9% for electricity and 19% for gas in 2024 ([CNMC](https://www.cnmc.es/sites/default/files/editor_contenidos/20250804_NP_Informe_Minorista_ElectricidadyGas_2024.pdf)). Movement from the PVPC to the free market sped up in 2025 ([Diario de León](https://www.diariodeleon.es/economia/260814/2094189/numero-consumidores-acogidos-pvpc-luz-cae.html)).
- **Process:** the gaining retailer starts the switch through the DSO. It must complete within 10 business days at no charge ([PwC on RD 88/2026](https://periscopiofiscalylegal.pwc.es/real-decreto-88-2026-de-11-de-febrero-por-el-que-se-aprueba-el-reglamento-general-de-suministro-comercializacion-y-agregacion-de-energia-electrica/)).
- **Exit fees:** none on non-fixed 2.0TD contracts. On fixed-price contracts the fee is capped at 5% before the first renewal (same source).
- **Cooling-off:** 14-day withdrawal right under general consumer law [unverified].
- **Blocks for debt:** no confirmed debt block like GB prepayment's [unverified]. Lack of guarantees blocks the gaining retailer instead ([MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/distribuidores/comercializadores.html)).
- Contracts are annual with tacit renewal ([PwC](https://periscopiofiscalylegal.pwc.es/real-decreto-88-2026-de-11-de-febrero-por-el-que-se-aprueba-el-reglamento-general-de-suministro-comercializacion-y-agregacion-de-energia-electrica/)).

## 15. Home moves

- A new occupant must contract with a retailer by name. Either the holder changes on a live supply (cambio de titular), or a dormant supply is reactivated (alta), with DSO connection and access fees [unverified].
- There is no confirmed deemed contract in which the incumbent supplier automatically supplies the new occupant, as GB has. Supply can stay in the previous occupant's name until changed [unverified].
- New contracts must include the cadastral reference ([PwC](https://periscopiofiscalylegal.pwc.es/real-decreto-88-2026-de-11-de-febrero-por-el-que-se-aprueba-el-reglamento-general-de-suministro-comercializacion-y-agregacion-de-energia-electrica/)).
- Final bills come from an actual smart read, so there is no read dispute [derived from §7].

## 16. Where debt sits

- **Who holds the debt:** the retailer; there is no central body. The retailer starts disconnection, and **the DSO physically cuts supply** at the retailer's request.
- **Cost of cuts:** the DSO bears disconnection and reconnection costs, and pays compensation for wrongful cuts ([MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/contratacion-suministro/cortes-suministro.html)).
- **Retailer's own exposure:** the retailer pays access tolls whether or not its customer pays, so it carries bad debt ([MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/distribuidores/comercializadores.html)).
- **Bono social funding:** paid by electricity groups and retailers, not general taxation, under RDL 7/2016 and later rules after court challenges [unverified].
- **Supplier of last resort:** the COR also supply customers without a valid free-market contract. The old Orden ITC/1659/2009 transfer rules were repealed by RD 88/2026 ([GA-P](https://ga-p.com/wp-content/uploads/2026/02/Energia_electrica.pdf)). What replaces them was not confirmed.
- **Does debt follow the customer?** No; it stays with the old retailer and is pursued as an ordinary civil debt [unverified]. GB's Debt Assignment Protocol has no confirmed Spanish equivalent.

---

## (a) Contrast table: Spain vs GB

| # | Dimension | Spain | GB | Difference that matters |
|---|---|---|---|---|
| 1 | Climate | HDD about 1,480, CDD about 300–380, big regional spread | HDD about 2,800+ [unverified], CDD about 0 | Two demand peaks; regions need distinct weather |
| 2 | Generation and wholesale | 56% renewable, 19% nuclear (closing 2027–35), Iberian zone, 15-min day-ahead, 800+ hours at or below zero | Gas-marginal, 30-min settlement [unverified] | Solar-dominated price shape; 2022–23 cap is a regime break |
| 3 | Grid and network tariff | About 330 DSOs; kW subscription; 2.0TD with 3 energy periods and 2 powers | 14 DNO areas; fuse; unit-rate network charges [unverified] | Capacity term and time-of-use network tariff are compulsory |
| 4 | Households | 19.3m, 2.50 people | About 28m, 2.4 people [unverified] | Scale similar order |
| 5 | Housing and fuel | 66% flats, 73% owners, only about 40% on mains gas, heating oil and LPG remain | Mostly houses, about 85% on gas [unverified] | Gas is optional; many all-electric homes |
| 6 | Regulation | PVPC (dynamic, partly hedged) via COR only; TUR gas; light licensing | Ofgem cap over supplier tariffs | Regulated product is a tariff run by named incumbents, not a ceiling |
| 7 | Smart meters | 99% DSO meters since 2018, hourly reads | Supplier/DCC, partial [unverified] | Meter data comes from the DSO and is universal |
| 8 | Billing | Actual reads, monthly or bimonthly, paid after the bill, VAT 21% + IEE 5.11% | Fixed DD with true-up, prepayment, VAT 5% | No credit balances; no prepayment; heavy tax share |
| 9 | Settlement | Hourly or quarter-hourly measured; final run at M+11 | MHHS, about 4 months [unverified] | Longer reconciliation tail |
| 10 | Debt and vulnerability | 2 or 4 months, then 3.5 kW SMV; bono social 42.5/57.5%; cut ban to end-2026 | Supplier codes, PSR, winter protections | State-certified vulnerability tied to the PVPC |
| 11 | EV, PV, heat pumps | 683k self-consumers; simplified monthly netting capped at consumption; EVs 11% | SEG; EVs about 20%+ [unverified] | Self-consumption is mass-market; netting rules live on the bill |
| 12 | Cooling | AC 43%+ of homes | Negligible | New summer load model needed |
| 13 | Cooking | About 57% electric hobs, mains gas plus butane | Gas and electric [unverified] | Butane is outside the supplier relationship |
| 14 | Switching | 24% a year, 10 business days, capped fees | Fast switching, lower rates post-2022 [unverified] | High churn; PVPC to free market flow |
| 15 | Home moves | Name change or reactivation needed [unverified] | Deemed contract | No automatic supply to a new occupant [unverified] |
| 16 | Debt location | Retailer holds debt; DSO cuts; COR as fallback | Supplier holds debt; prepayment meter fitting | No prepayment route; DSO executes cuts |

## (b) Transferability of the GB build

**World components**

| Component | Rating | Why |
|---|---|---|
| Weather-driven demand | Medium | Engine reusable; needs cooling and multiple climate zones plus islands |
| Building thermal model | Low–Medium | Flats, low insulation and AC dominate; gas boilers are a minority |
| Household behaviour and finances | Medium | Needs kW-limit behaviour, PVPC vs fixed choice, bono social eligibility |
| Wholesale price replay | Medium | Works mechanically; needs the OMIE 15-min feed, negative prices and the 2022–23 cap flag |
| Settlement clock and reconciliation | Medium | Interval logic fits; run schedule changes to M+1/3/8/11 |
| Smart-meter data feed | High | Simpler: universal hourly reads, but sourced from the DSO |
| Network and connection limits | Low | Must add contracted kW, trips and two-power optimisation |

**Supplier components**

| Component | Rating | Why |
|---|---|---|
| Tariffs and price regulation | Low | No cap; the PVPC formula is available only to the COR; dynamic offer mandatory above 200k customers |
| Quoting, acquisition and switching | Medium | Similar flow; cold-call ban; 10-day switch; exit fee caps |
| Billing and payments | Low–Medium | Rebuild to actual-read monthly billing with power and energy terms, IEE and VAT |
| Direct debit, collections and debt | Low | No prepayment; 2/4-month process with SMV; DSO executes cuts |
| Vulnerability duties | Low | Bono social administration and essential-supply flags replace the PSR |
| Hedging and wholesale buying | Medium | Same concepts; solar cannibalisation and a thin interconnector shift risk |
| Settlement and imbalance | Medium | 15-min imbalance, REE/OMIE guarantees, longer reconciliation |
| Capital and financial rules | Medium | Guarantee posting replaces Ofgem capital rules |
| Advice and asset offers | Medium–High | Strong PV case; batteries, EVs and air-to-water heat pumps less mature |

## (c) New features needed

**New simulation ("world") features**
1. Contracted-kW subscription per home, including trip events and a 3.5 kW SMV mode.
2. 2.0TD calendar: three energy periods, two power periods, weekends and holidays as valle, island variants.
3. Cooling demand with AC ownership, set points and summer peak.
4. Multi-zone climate (Atlántica, Continental, Mediterránea, Canary Islands) and non-peninsular systems.
5. Flat-dominated stock with shared heating, butane and LPG users, and homes off the gas grid.
6. OMIE 15-min day-ahead replay with negative prices, plus a flag for the 2022–23 gas-cap regime.
7. PVPC price generator (futures blend plus day-ahead shape) and quarterly TUR.
8. DSO-originated meter data with hourly-to-15-min interpolation.
9. Mass rooftop PV with export, and collective self-consumption.
10. Bono social eligibility and certification process; essential-supply status.

**New supplier features**
1. Power-term plus energy-term billing; recommending contracted power and the two-power split.
2. Actual-read monthly billing, IEE and 21% VAT; collection after the bill.
3. Simplified self-consumption netting capped at consumption; optional virtual battery.
4. Dynamic-price contract with risk warnings (required above 200k customers).
5. Free-market offers that compete against the PVPC, including PVPC to free-market conversion.
6. Debt workflow: formal demand, 2/4-month clocks, SMV request to the DSO, cut and 24-hour reconnection.
7. Guarantee posting with REE and OMIE; 5-run settlement reconciliation.
8. Handling of RD 88/2026 rules: summary document, complaints within 15 days, no cold calling.
9. Optional COR role, with PVPC, bono social and fallback duties, as a separate regulated entity.
10. Advice on AC and heat-pump efficiency, batteries for solar shifting, EV off-peak charging.

## (d) Named gaps

1. A current Eurostat HDD series for Spain and the UK, and AC penetration after 2015.
2. Typical annual household electricity kWh, by zone.
3. REE 2025 full-year mix; GB comparison figures generally.
4. Exact DSO count; single-phase vs three-phase split.
5. Exact quarter-hourly imbalance start date; profiling rules for any meters still read manually.
6. Billing period and the COR transfer rules after RD 88/2026; whether debt follows the customer (no transfer is assumed).
7. Home-move default-supply rules (cambio de titular, alta).
8. Bono social funding mechanism after court rulings; annual kWh caps; certification flow.
9. How self-consumption exports are valued, and the status of virtual batteries.
10. Butane cylinder penetration; payment-method mix (direct debit share); arrears data after 2018.
11. 2025 EV sales; heat pump stock.