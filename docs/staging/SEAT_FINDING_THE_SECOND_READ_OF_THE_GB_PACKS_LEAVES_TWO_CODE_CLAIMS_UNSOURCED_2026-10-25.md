**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** none -- the knowledge content is in the 25 Oct market_research notes' "Second read" sections; this records the code that still disagrees with them

# The second read of the GB packs leaves two code claims unsourced (2026-10-25)

Found while applying the advisor's verification of the 21 GB packs
(`docs/staging/advisor/done/DIRECTOR_EVIDENCE_VERIFICATION_OF_THE_GB_PACKS_UNVERIFIED_ITEMS_2026-10-25.md`).
Each code hit from that pass was read. Three were plain factual errors and were fixed in the commit
that files this: `standing_charge_assessor` paired 2,900 kWh (the 2020-23 TDCV) with 11,500 gas and
is now 2,700; `licence_monitor` labelled SLC 47 as the PSR; the consumption generator's docstring
said MHHS ends per-customer HH consent. Two are not fixed, because the fix is a number nobody has
established yet.

1. **`company/regulatory/licence_monitor.py` `_SLC_CATALOGUE`.** Only the SLC 47 label is now
   sourced. The rest look wrong from memory (SLC 22 is not smart metering; the PSR is SLC 26). They
   are catalogue labels, not used in a calculation. The fix is to read each against the
   consolidated supply licence, not to relabel them from recall.
2. **`company/pricing/fabric_intervention.py` `OFFER_BOOK["insulate"]` at GBP 6,000.** It is used
   in calculations. The second read gives cavity wall at GBP 1,000-3,000 (12-37 year payback), and
   solid wall costs far more. One "insulate" offer at GBP 6,000 is neither. It needs splitting by
   measure, with each cost taken from `heat_pumps_and_fabric_measures_2026-10-25.md`, before the
   fabric offer's payback is published as advice. GAP until then.

Not defects, recorded so nobody re-checks them: `bad_debt_provision.CAP_LEVEL_KWH` (2,700/11,500)
weights cap rates over a 2016-2025 run and never reaches July 2026. `affordability_inference`'s
2,900 is labelled illustrative and serves only as a ratio anchor. The ECO4 end year (2026) is the
same whichever end date (March or December) turns out to be right.
