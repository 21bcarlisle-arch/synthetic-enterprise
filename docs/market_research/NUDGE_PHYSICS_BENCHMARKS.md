# Nudge Physics — Behavioural Economics Benchmarks

Grounding doc for `docs/staging/NUDGE_PHYSICS.md`. Recalled-from-training literature review (no live
fetch access this pass — see caveat per row). Follow-up discovery pass should re-verify primary
sources, especially Ofgem's exact switching-rate series and the BIT/Cabinet Office 2012 report,
before treating any range below as final.

| Mechanism | SIM parameter | Range | Confidence | Source |
|---|---|---|---|---|
| Defaults / status-quo bias (auto-renewal) | relative reduction in switch probability | 15-35% | H (phenomenon) / M (magnitude) | Madrian & Shea (2001) QJE 116(4); Pichert & Katsikopoulos (2008) J. Env. Psych. 28(1); CMA Energy Market Investigation 2016 |
| Social norms / neighbour comparison (Opower) | usage reduction | 1.4-3.3% (~2% central); no payment/churn evidence found | H (usage) / gap (payment) | Allcott (2011) J. Public Econ. 95(9-10); Ayres, Raseman & Shih (2013); Allcott & Rogers (2014) AER 104(10) |
| Loss aversion in offer framing | relative uplift in acceptance probability | 10-35% | H (phenomenon) / M (magnitude) | Kahneman & Tversky (1979) Econometrica 47(2); Ganzach & Karsahi (1995) J. Bus. Research 32(1); Levin, Schneider & Gaeth (1998) OBHDP 76(2) |
| Anchoring in tariff/price presentation | relative uplift in acceptance/perceived value | 8-20% | H (phenomenon) / M (magnitude) | Tversky & Kahneman (1974) Science 185(4157); Ariely, Loewenstein & Prelec (2003) QJE 118(1); Urbany, Bearden & Weilbaker (1988) JCR 15(1) |
| Friction costs / switching effort ("sludge") | per-step completion decay; crisis-year macro multiplier | 5-10%/step; 0.3-0.4x in 2021-2023 | M (trend) / L (per-step magnitude) | Ofgem retail market indicators (not re-verified this pass); CMA 2016; Sunstein (2019) Duke Law Journal 68 |
| Present bias (payment timing) | quasi-hyperbolic beta, delta | beta in [0.6,0.85], delta in [0.95,0.99]/month | H (phenomenon) / L (magnitude - no UK energy study) | Laibson (1997) QJE 112(2); Frederick, Loewenstein & O'Donoghue (2002) JEL 40(2); DellaVigna & Malmendier (2006) AER 96(3) |
| Debt-collection letter tone/framing | additive uplift in payment response | +3 to +10pp | M (cross-sector: tax/fines, not energy) | Cabinet Office/BIT, "Applying Behavioural Insights to Reduce Fraud, Error and Debt" (2012) |
| Commitment devices (opt-in payment plans) | relative reduction in missed-payment probability | 20-40% | H (phenomenon) / L (magnitude - imported from savings-product studies) | Ashraf, Karlan & Yin (2006) QJE 121(2); Thaler & Benartzi (2004) JPE 112(S1) |

## Cross-cutting notes
- Only Opower (usage) and the UK switching-rate trend are energy-sector-specific studies; the rest
  are cross-domain imports (retirement savings, tax debt, retail pricing, lab tasks) - directionally
  credible, magnitude not UK-energy-verified.
- Per this project's population-anchoring convention (see `ASSUMPTIONS.md`), sample each customer's
  susceptibility from a distribution across the published range rather than a fixed constant.
- Keep selection effects (who opts into a nudge) conceptually separate from treatment effects (what
  the nudge does) - especially for commitment devices, where the cited evidence is partly
  correlational (Direct Debit vs credit customers).
- Status: seeded 2026-07-07, no prior entry existed for this topic.
