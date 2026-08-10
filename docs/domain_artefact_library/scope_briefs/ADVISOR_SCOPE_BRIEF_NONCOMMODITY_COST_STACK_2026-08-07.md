# [ADVISOR-SCOPE-BRIEF] — The non-commodity cost stack (2026-08-07)

**Type:** [SCOPE BRIEF — domain-first, written before reading the code]. What every non-energy pound on a GB domestic bill actually is: who levies it, on what basis, driven by which data, reconciled on which clock. This is the anatomy under the £4.9M reconciliation gap and the cost side of the abatement engine — time-shifting only creates value where the stack is time-varying. `~` marks figures/dates that move: verify current before hard-coding. Refute with evidence.

## The stack, line by line (E=electricity-only, G=gas-only, B=both)

| Line | Levied by / via | Billing basis | Data driver | Clock |
|---|---|---|---|---|
| DUoS (E) | DNO, CDCM published tariffs | p/kWh by time band + fixed p/MPAN/day, per LLFC | settled HH volumes by band | monthly invoice, restated on settlement reruns |
| TNUoS demand (E) | NESO | ~post-TCR: FIXED residual by consumption band per site — does NOT vary with peak behaviour for domestic | band assignment | annual tariff, ex-ante |
| BSUoS (E) | NESO | ~post-2023 reform: fixed ex-ante £/MWh, demand-only | settled volume | fixed tariff periods |
| Losses (E) | not a price line — a VOLUME uplift | LLF × TLM multipliers (~1.05–1.10 typical) | metered→settled kWh | applied in settlement itself |
| Gas transport (G) | GDN + NTS via UK Link invoices | LDZ capacity + commodity + fixed customer charge; NTS entry/exit | AQ, SOQ | monthly, AQ-driven restatements |
| RO (E) | obligation on supplier | ~£/MWh = obligation level × buyout; mutualisation risk when others default | supplied volume | obligation year, late true-up |
| CfD supplier obligation (E) | LCCC | Interim Levy Rate p/kWh + quarterly reconciliation to actuals | supplied volume | daily ILR / quarterly true-up |
| Capacity Market (E) | via EMRS | charge on demand in the ~winter weekday 16:00–19:00 window | HH shape in-window | forecast then reconciled |
| FiT levelisation (E) | Ofgem quarterly | £/MWh-equivalent share by market share | supplied volume | quarterly true-up |
| ECO (B) | obligation, not per-unit levy | delivery cost internalised, allocated by share | market share | scheme-phase |
| WHD (B) | per-account obligation | ~£/account contribution + rebates delivered | account count | scheme year |
| GGL (G) | per-meter | ~pence/meter/day | meter count | quarterly |
| AAHEDC (E) | levy | ~small p/kWh | volume | annual |
| Industry bodies (B) | Elexon BSC, RECCo, Xoserve DSC, DCC, Ofgem licence | mixed fixed + per-MPAN/MPRN + volumetric | meter counts, volumes | invoice cycles |

**Cap linkage:** every line above maps to a cap-annex allowance category (wholesale/network/policy/operating/EBIT/headroom + PAP/PAAC adjustments). The company's stack should reconcile to the annex decomposition per cap period — divergence named, never silent.

**Time-variance census (the abatement engine's ground):** genuinely time-varying = wholesale shape, DUoS bands, CM window exposure, losses-weighted volume. NOT time-varying for domestic despite folklore = ~TNUoS (fixed bands post-TCR), ~BSUoS (fixed ex-ante post-reform). A model that rewards peak-avoidance through TNUoS/BSUoS is rewarding the wrong decade.

## Simplification candidates (register, never hide)
Collapse AAHEDC+GGL+minor body fees into one "minor levies" line (materiality ~£10–20/yr) with a Birth-Certificated register entry. ECO/WHD as flat per-account allowances at current rung. NOT simplifiable: DUoS band structure, CfD ILR+reconciliation, CM window, losses — these carry the personalisation signal and the true-up physics.

## Disqualification battery (a real GB supplier test on each)
- **B1 Build-up reconciles:** for any MPAN/period, the non-commodity build-up sums to the cap-annex allowance for that period within materiality, or every divergence carries a named driver.
- **B2 Wrong-decade signals:** if shifting a customer's evening peak changes their TNUoS or BSUoS cost, DISQUALIFIED (~post-reform both are shape-invariant for domestic).
- **B3 Fuel purity:** a gas bill carrying RO, CfD, CM, or AAHEDC is disqualified; an electricity bill carrying GGL likewise.
- **B4 Losses as volume:** settled kWh = metered × LLF × TLM; losses appearing as a p/kWh price line instead is disqualified.
- **B5 Provenance:** every constant traces to a published artefact (CDCM sheet version, ILR notice, cap annex cell) — an untraceable constant is invented physics.
- **B6 Three clocks:** a settlement rerun that restates volumes must restate DUoS/CfD/CM charges through the billed/settled/banked discipline — a stack that never true-ups is disqualified.
- **B7 Mutualisation:** the model can book an RO mutualisation surcharge in a supplier-failure year replay; if the mechanism cannot exist, the 2021–22 cost physics cannot be reproduced.

— Advisor scope brief, 2026-08-07; domain from industry knowledge as of early 2026, `~` items verify-current.
