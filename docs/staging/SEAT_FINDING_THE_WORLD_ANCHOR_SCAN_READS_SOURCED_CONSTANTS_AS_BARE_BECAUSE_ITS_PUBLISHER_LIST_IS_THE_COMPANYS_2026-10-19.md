**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `anchor-the-446-bare-world-constants-in-impact-order`
**Knowledge:** world-constant anchors -- `docs/design/world_constant_impact_ranking.md`

# The world anchor scan reads sourced constants as bare, because its publisher list is the company's

**What is established.** `tools/world_constant_anchors.py` imports `_CITED` from
`tools/domain_constant_origins.py`: `docs/`, Ofgem, DESNZ, CMA, Elexon, NESO, ONS, BEIS, Cornwall,
Citizens Advice, a URL. The world cites other publishers too. Two examples, read by hand on
2026-10-19, carried full citations and were still registered bare:

- `simulation/arrival_route.py::EHS_HOUSEHOLDS_BY_TENURE_MILLIONS`: "English Housing Survey 2024-25,
  Chapter 1 / Annex Table 1.1 (MHCLG, fetched 2026-09-19)".
- `simulation/premise_population.py::PUBLISHED_EPC_BAND_SHARE`: "EHS 2022-23 Energy Chapter AT1_2
  (MHCLG, July 2024)". This one also sat below `EPC_BANDS`, so the contiguous-block reader gave it
  no comment at all, which is the known hole `_comment_block` records.

Both were anchored in this commit by adding the `docs/market_research/` page that already holds the
figure. The constant values did not change.

**The size, as a first count.** Of the 446 registered rows, 37 have a comment block naming a
publisher outside `_CITED`, such as EHS/English Housing Survey, EFUS, SAP, NEED, ECUK, HMRC, UK ETS or
National Grid. Another 71 name one within 15 lines but outside the block. The match was a loose
regex and gave false positives ("ice" in "price", "need"), so these figures are an upper bound and
are not a census. The register therefore overstates how much of the world is unsourced, and
overstates it most in the best-sourced modules (`premise_trace`, `fabric_physics`,
`premise_population`).

**What I did not do, and why.** I did not widen the world scan's publisher list. A pattern that
accepts any mention of "SAP" or "EHS" would discharge a constant that only names the survey it
should have come from. That is a comment, not a citation, and the company scan already has this
weakness for "Ofgem". The remedy that cannot launder is the one used here: when a constant comes up
in impact order, point it at the knowledge page that holds the figure. That move strikes it from
the register, and the person making it has read the source.

**Proposal (not acted on).** If the register's headline count is going to be published, publish it
as "bare by the scan's pattern" with this upper bound beside it, not as "unsourced".
