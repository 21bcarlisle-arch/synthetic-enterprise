# `docs/design/refs/` — reference canon

Advisor-authored scope briefs, research notes and structural reviews that have stopped being
*instructions* and become *reference*. Nothing here is a live draw: each document was dispositioned
out of `docs/staging/` under Group A of
`DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_INTERLEAVE_2026-08-10.md` ("archive as canon"). Where a
document named a mechanism that did not yet exist, the atom is recorded in the receipt line below —
the prose is reference, the build lives on the maturity map.

Read these for domain grounding and prior analysis. Do not read them as a queue.

## Scope briefs — NOT here: `docs/domain_artefact_library/scope_briefs/`

The eight briefs that scoped the industry surface went to
`docs/domain_artefact_library/scope_briefs/`, not to this directory, and the reason is worth
recording because it corrects the premise the triage was run on.

The briefs are **not** inert prose. `tests/domain/battery_register.py::resolve_brief` reads each
brief's disqualification battery out of the brief file itself — deliberately, as an oracle
independent of the AO8 register — and locates it by basename across a fixed list of search roots.
Moving the eight into `docs/design/refs/` broke every one of those references at once
(`FileNotFoundError: ... The register cites it, so this is a broken reference, not an empty
battery`), and the pre-commit gate refused the commit. `docs/domain_artefact_library/scope_briefs`
was **already declared** as a search root and simply had never been created, so that is where a
scope brief's canon home was always meant to be. No code changed; the directory now exists.
`tests/domain/test_battery_register_integrity.py` — 18 passed.

The lesson generalises past these eight: a staged doc is only reference if nothing RESOLVES it.
Check for a resolver before moving a cited file.

| Document | Subject |
|---|---|
| `ADVISOR_SCOPE_BRIEF_ELECTRICITY_2026-08-04.md` | Electricity supply surface |
| `ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md` | Gas supply surface |
| `ADVISOR_SCOPE_BRIEF_CARBON_2026-08-04.md` | Carbon signal and abatement ledger |
| `ADVISOR_SCOPE_BRIEF_CFD_AND_ASSETS_2026-08-04.md` | CfDs and asset-backed positions |
| `ADVISOR_SCOPE_BRIEF_INDUSTRY_BOUNDARY_2026-08-04.md` | Where the supplier ends and industry begins |
| `ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md` | CoT process physics |
| `ADVISOR_SCOPE_BRIEF_NONCOMMODITY_COST_STACK_2026-08-07.md` | Network / policy / market cost lines |
| `ADVISOR_SCOPE_BRIEF_PREPAYMENT_ESTATE_2026-08-07.md` | Prepayment meter estate |

## Research notes

| Document | Subject |
|---|---|
| `ADVISOR_RESEARCH_PRE_RESEARCH_POINTERS_2026-08-07.md` | Where to look before commissioning research |
| `ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md` | Counterparty API landscape for the Epoch-3 adapter set |
| `ADVISOR_RESEARCH_CREDIT_BALANCES_2026-08-04.md` | Customer credit-balance behaviour and treatment |

## Structural reviews and analyses

| Document | Subject | Receipt |
|---|---|---|
| `ADVISOR_REVIEW_DATA_ARCHITECTURE_AND_SCALE_PROBE_2026-08-05.md` | The state layer is files, not a database; defines the 10k probe | Probe atom did not exist → minted `AO12_scale_probe_10k` (2026-08-10) |
| `ADVISOR_REVIEW_MATURITY_MAP_TAXONOMY_2026-08-05.md` | Lane/value-stream taxonomy of the map | Reference |
| `ADVISOR_NOTE_CCM_PROVENANCE_AND_SEAT_GUARD_2026-08-05.md` | CCM provenance and the seat guard | Historical |
| `ADVISOR_ANALYSIS_MARKET_PORTABILITY_2026-08-07.md` | Preconditions P1–P5; what travels, parameterises, adapter-swaps, rebuilds | Design-law atom did not exist → minted `A9_market_at_the_seams_design_law` (2026-08-10) |

Related, and deliberately not moved here: `docs/design/PORTABILITY_DEBT.md` is a live register, not
reference.
