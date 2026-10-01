**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# A settled home's EAC is its own smoothed reads, and the world draws it blind to the dwelling

Claim `settle-the-eac-against-demand-gap-before-pb4s-swap`. This finding is the knowledge leg only.
The world fix and the bill-shock swap stay with the worker that holds the same claim (session
`synthetic-enterprise-59`, drawn 20 minutes before this one). The split was sent to it in writing,
so this is not a release and not a second build.

It answers the question left open by
`SEAT_FINDING_THE_YEAR_ONE_SHOCK_TAIL_IS_AN_EAC_A_FRACTION_OF_THE_HOMES_USE_2026-10-01.md`. When
this was written, that finding was still untracked on the shared tree. Its facts are restated here
so that this one stands alone. 7 of 31 first renewals rise by more than 100%, and the homes involved
carry a registry EAC of 1,600–2,500 kWh while being billed many times that.

## The answer: not history-true

**Published record**: BSCP504 *Non-Half Hourly Data Collection* v53.0, 1 Oct 2024.

- **The EAC is computed from the meter's own reads.** On each valid reading, the NHHDC calculates an
  Annualised Advance (AA) over the read period. From that AA and the previous EAC it calculates a new
  EAC, using a stored, positive smoothing parameter (§3.3.11.3, footnote 80; Appendix 4.9). It then
  sends both to the NHHDA and the Supplier on the D0019 (§3.3.11.5). Elexon's glossary says the EAC
  is "the forward looking estimate based on an average of previous Annualised Advances".
- **The EAC survives a change of supplier.** The new NHHDC sends "initial EAC (class average **or,
  where provided by the Old Supplier, the latest EAC**)" (§3.2.6.51, D0052). A gaining supplier
  therefore inherits the home's own history-derived EAC. A class average is the fallback only for a
  meter with no history, and on a change of Profile Class (footnote 62).
- **How fast it follows.** An AA covers one read period (the system processes advances of up to 15
  months, App. 4.9). Remote-read PC1–4 meters need only be processed once every three months
  (App. "Remote Data Retrieval"). The EAC is a smoothed average of AAs, so after a real change in use
  it lags by roughly a read period or two. A home whose use has been stable does not sit at a fifth
  of its use.
- **Storage heating is not Profile Class 1.** Economy 7 / storage-heated domestic supply is PC2. Ofgem
  publishes separate PC2 TDCVs and notes they are "bound to be below their actual value"
  (`docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md`, §3 notes). Even the
  fallback case would draw a PC2 class average, not a PC1 band.

**Not established anywhere I found** (carried forward as the gap it already is: gap 4 of the
direct-debit research note): *how far* a registry EAC typically sits from realised use. The
mechanism is published; the error distribution is not.

**Conclusion.** For a settled, electrically heated home, a real gaining supplier would be handed an
EAC near that home's own ~10–20 MWh. An EAC of 1,600–2,500 kWh on such a home is a world defect,
not a shock a real supplier would see. The director's practitioner reading in the earlier finding
now has its published support.

## Where the world puts demand above the EAC

The disagreement is **two independent statements of one home's consumption**. It is not an overlay
running away:

1. **The registry EAC** is `population_draw._draw_one`:
   `eac = rng.uniform(*TDCV_BANDS_KWH[commodity][band])`. That is a PC1 single-rate band
   (1,400–4,000 kWh), drawn *before* the dwelling and independent of it. `SyntheticCustomer.to_customer_dict`
   copies it verbatim into the supplier's roster.
2. **The demand** is the W1_11 fabric trace (`simulation/fabric_physics.py` via
   `fabric_demand_path`). It is physics on the drawn dwelling, and for direct-electric or storage
   heating it includes the space-heating load. `run_phase2b`'s fabric branch *replaces* every legacy
   overlay. It does not scale to the EAC, so `simulation/household_demand.py`'s multiplier is not
   the cause. That multiplier only reaches the company's first-term estimate
   (`_company_eac_estimate(..., base_eac_override=EFFECTIVE_EAC * eac_multiplier_for_date)`), and
   for a non-ASHP electric home it is just the EPC factor.
3. `profile_class` is unset (so it defaults to 1) on every drawn home, storage-heated ones included.

`_base_profile_eac`'s own docstring already names the structural repair as owed: "a world-side
true EAC and a supplier-side declaration that may differ, with a read error between them".
`docs/staging/done/WORKER_PREREGISTRATION_WHAT_SCALING_EACH_HOUSEHOLDS_PROFILE_TO_ITS_OWN_EAC_MUST_SHOW_2026-08-31.md`
records it. **This is that parked atom, not a new one.**

## The tail is the heating system, exactly

On the one-world run behind the earlier finding (`/var/tmp/se-pb4-shock-out/events.json`), I joined
each account to its dwelling through
`HouseholdDemandRegister(CUSTOMERS, drawn_households=live_drawn_households())`:

| first renewals | n | rise > 100% |
|---|---|---|
| electrically heated (2 `ELECTRIC_DIRECT`, 3 `ELECTRIC_STORAGE`) | 5 | **5** (+1.44 to +7.15) |
| gas heated | 26 | 2 — `SYN-2016-018` at +1.04 (marginal), and `C9` (HH-metered, `eac_kwh=None`, so its quote is not an EAC at all) |

All five electric homes carry EACs of 1,622–2,478 kWh. So the earlier finding's "7 of 31" is
5 of 5 electric plus 2 that need their own explanation. C9 especially: a 3.2× rise on an account
with no EAC is quoted on something else, and nobody has yet said what.

## What the world fix must do (for the holder of the world leg)

- At acquisition, give the registry EAC the home's **own** recent annualised consumption: the
  trailing year of its fabric trace, smoothed as App. 4.9 smooths. Give a home with no history (a
  new connection) the class average of its **profile class**. Make storage-heated homes PC2.
- Carry the **read error between truth and EAC as an explicit, named gap** (`None` with a reason, or
  zero error stated as a lag-only model). Do not use a picked dispersion. Nothing published sizes
  it.
- Pre-register before the run. Predictions written now, before any measurement: the 5 electric
  first-renewal rises fall below +1.0; the first-renewal shock share falls from 17/31 toward the
  later-renewal rate (0.32); later renewals move little, because they are reviewed against the
  home's own bills. Expect TDCV-band counts to stop matching the published band shares for electric
  homes, which is correct.
- Run order: after item one (the switching-reference VAT fix) is on origin, because that moves churn.
  Do it as one world, one variable, blind to company results.

Sources: [BSCP504 v53.0 (Elexon, via MHHS programme library)](https://www.mhhsprogramme.co.uk/api/documentlibrary/Background%20Programme%20Context/P478_BSCP504_v53.1.pdf)
§3.2.6.51, §3.3.11, App. 4.9 · [Elexon glossary: Estimated Annual Consumption](https://www.elexon.co.uk/bsc/glossary/estimated-annual-consumption/)
· [Elexon: Estimation of Annual Consumption System URS](https://bscdocs.elexon.co.uk/user-requirements-specifications/estimation-of-annual-consumption-system)
· Ofgem TDCV decision 25 May 2023 (PC2 bias), as cited in `docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md`.
