# Backlog-triage receipts — worker tick, 2026-08-10

Dispositions executed under `DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_INTERLEAVE_2026-08-10.md`.
One line per file, naming what answered it or where it went. The drain target is staging root < 20
non-marker files; this tick took it **98 → 79**. The interleave has NOT armed.

## Group C — consumed as live instruction (2 of the list)

| File | Act |
|---|---|
| `DIRECTOR_NOTE_SUSPECT_LIST_REDERIVATION_2026-08-10` | Ratified mint landed: **`H42_wedge_suspect_list_rederived_from_the_red`**. The defect is real and already confessed in the alarm's own text — `process_run_complete.py::filed_findings()` ranks staged findings by RECENCY and prints them beside a failure they are structurally unrelated to. Exit criteria carry R15 both-ways, the fail-silent case (unreadable gate state must read *unrecorded*, never *no suspects*), and R12 on the hit rate. Draw order per the note: **after** the folded-site verification |
| `DIRECTOR_NOTE_UNBLOCK_CHARTS_2026-08-10` | `PLANNER_MINTED_one_node_to_depth_with_charts` flipped `blocked` → self-drawable, normal priority. **The class receipt the director asked for is recorded on the mint doc**: it sat 13 days behind `director_level_up`, an act abolished 2026-07-29 and swept 2026-08-03. The sweep updated the `BLOCK_RELEASE` header and left the body prose intact, so two lines still said "only the director LEVEL move remains" — both now struck through in place. What is actually owed is R11 live-surface evidence (the doc's own verification was deferred to "the next publish"), then self-certification; no director act is involved and none has been since 2026-07-29 |

## Group A — archived as canon (15 files)

**Correction to this group's premise, caught by the pre-commit gate.** The eight scope briefs are
NOT inert prose: `tests/domain/battery_register.py::resolve_brief` reads each brief's
disqualification battery **out of the brief file itself**, deliberately, as an oracle independent
of the AO8 register. Moving them into `docs/design/refs/` broke all eight references at once
(`FileNotFoundError: ... The register cites it, so this is a broken reference, not an empty
battery`) and the commit was refused. `docs/domain_artefact_library/scope_briefs` was **already
declared** as one of the resolver's search roots and had simply never been created — so that, not
`refs/`, is a scope brief's canon home. The eight went there, no code changed, and
`tests/domain/test_battery_register_integrity.py` is 18 passed.

The generalisation, for the rest of this drain: **a staged doc is only reference if nothing
RESOLVES it.** Check for a resolver before moving a cited file. "The registry has absorbed it" and
"the registry no longer reads it" are different claims.

| File | Receipt |
|---|---|
| `ADVISOR_SCOPE_BRIEF_ELECTRICITY_2026-08-04` | → `docs/domain_artefact_library/scope_briefs/` (cited by the battery oracle — see above) |
| `ADVISOR_SCOPE_BRIEF_GAS_2026-08-04` | as above |
| `ADVISOR_SCOPE_BRIEF_CARBON_2026-08-04` | as above |
| `ADVISOR_SCOPE_BRIEF_CFD_AND_ASSETS_2026-08-04` | as above |
| `ADVISOR_SCOPE_BRIEF_INDUSTRY_BOUNDARY_2026-08-04` | as above |
| `ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07` | as above |
| `ADVISOR_SCOPE_BRIEF_NONCOMMODITY_COST_STACK_2026-08-07` | as above |
| `ADVISOR_SCOPE_BRIEF_PREPAYMENT_ESTATE_2026-08-07` | as above |

The remaining seven went to `docs/design/refs/`, indexed in `refs/README.md`:
| `ADVISOR_RESEARCH_PRE_RESEARCH_POINTERS_2026-08-07` | Reference |
| `ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05` | Reference |
| `ADVISOR_RESEARCH_CREDIT_BALANCES_2026-08-04` | Reference |
| `ADVISOR_REVIEW_MATURITY_MAP_TAXONOMY_2026-08-05` | Reference |
| `ADVISOR_NOTE_CCM_PROVENANCE_AND_SEAT_GUARD_2026-08-05` | Historical |
| `ADVISOR_REVIEW_DATA_ARCHITECTURE_AND_SCALE_PROBE_2026-08-05` | **Verified: the probe atom did NOT exist** (grep over `maturity_map.yaml` for the probe/10k/scale-probe returns nothing; `AO4_scale_constraints_executable` is the C-S1..C-S5 checks, a different thing). **Minted `AO12_scale_probe_10k`** |
| `ADVISOR_ANALYSIS_MARKET_PORTABILITY_2026-08-07` | **Verified: no `market`-at-the-seams design-law atom existed** (no map hit for portability/market-at-the-seams; `docs/design/PORTABILITY_DEBT.md` is a debt REGISTER, not a law with a control). **Minted `A9_market_at_the_seams_design_law`** |

Both mints are registered in `tests/design/test_maturity_map_facets.py::REVIEWED_CLOSE_TO_LEARN`
with their on-the-merits classification, and validate: `tests/design/test_maturity_map_facets.py`
+ `test_maturity_map_contract.py` — **36 passed** (the id grammar `^[A-Z]+[0-9]+_[a-z0-9_]+$` is
satisfied without extending `LEGACY_IDS`, which is the defect
`WORKER_FINDING_AN_ATOM_ID_OFF_THE_GRAMMAR_REACHES_THE_MAP` names).

## Group B — answered / superseded → `docs/staging/done/` (17 files)

| File | Answered by |
|---|---|
| `ADVISOR_FINDINGS_MISSING_TEST_TIER_2026-08-04` | AO7's import-measured audit (director's own receipt) |
| `ADVISOR_FINDINGS_STRUCTURAL_AUDIT_2026-08-04` | AO7's import-measured audit (director's own receipt) |
| `ADVISOR_FLAG_SEAT_LIVENESS_WATCHDOG_2026-08-08` | The dead-man switch + PW1 observed-population ARE the watchdog |
| `DIRECTOR_PRIORITY_EPISODE4_TRIPWIRE_AND_RETRY_2026-08-09` | Draws done |
| `DIRECTOR_PRIORITY_PUBLISH_FIRST_2026-08-10` (from `in_progress/`) | Draws 1 and 2 landed (`1060fd727`, class fix already live in `process_run_complete._repair_derived_artefacts_in`); the freeze clause was lifted by `DIRECTOR_RULING_PUBLISH_DECOUPLING`. Draw 3 is the publisher's act, not a tick's — see the gate note below |
| `WORKER_REPLY_A_RULING_ARRIVED_WITHOUT_ITS_WORK_BLOCK_2026-08-09` | Answered in place |
| `WORKER_REPORT_NO_CALLER_CLASS_CENSUS_2026-08-09` | Answers `DIRECTOR_TASK_NO_CALLER_CLASS_CENSUS`; report-only, nothing owed |
| `WORKER_REPORT_OPS5_RETIRED_THE_INTERIM_BYPASS_2026-08-10` | `OPS5_retire_the_interim_bypass_shape` L0→L2, self-certified |
| `WORKER_REPORT_PUBLISH_WEDGE_SUSPECT_DISPOSITION_2026-08-09` | Wedge closed |
| `WORKER_REPORT_THIRD_WEDGE_WAS_A_FULL_DISK_2026-08-09` | Wedge closed |
| `WORKER_REPORT_FOURTH_WEDGE_CLOSED_THE_DERIVED_ARTEFACT_CLASS_2026-08-10` | Wedge closed |
| `WORKER_REPORT_FIFTH_WEDGE_SUSPECT_DISPOSITION_2026-08-10` | Wedge closed |
| `WORKER_REPORT_SIXTH_WEDGE_SUSPECT_DISPOSITION_2026-08-10` | Wedge closed |
| `WORKER_REPORT_THE_TENTH_WEDGE_WAS_THE_GATE_MATERIALISING_ITSELF_TWICE_2026-08-10` | Wedge closed |
| `WORKER_REPORT_THE_TWELFTH_WEDGE_WAS_A_MISSING_CALLEE_2026-08-10` | Wedge closed |
| `WORKER_REPORT_THIRTEENTH_WEDGE_SUSPECT_DISPOSITION_2026-08-10` | Wedge closed |
| `WORKER_REPORT_THE_FOURTEENTH_WEDGE_WAS_A_RUNG_READING_LIVE_DISK_2026-08-10` | Wedge closed |

## Group D deferred, with the reason — five docs the director's list named as fix-landed, whose own status line says otherwise

The triage page's own override applies here in the other direction: *"nothing here overrides a
finding's own status line."* These five were read before being dispositioned and each says QUEUED /
class-open, so they are **mechanism-owed** (Group D, mint then archive) rather than answered. They
stay in the root until their atoms are minted:

- `WORKER_FINDING_RUFF_BASELINE_IS_CALIBRATED_TO_UNCOMMITTED_WORK_2026-08-09` — "QUEUED per SELF_INTERRUPT_DISCIPLINE"; supersedes the earlier committed-HEAD ruff finding
- `WORKER_FINDING_THE_RUFF_RATCHET_IS_RED_AT_HEAD_2026-08-10` — "Queued, not fixed on sight"
- `WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10` — "QUEUED"; the wedge it was found in is closed but the mis-description is not. Carries the CLAUDE.md 32GB-vs-15.9GB constant per `DIRECTOR_NOTE_SUSPECT_LIST_REDERIVATION`
- `WORKER_FINDING_EPISODE_MEMORY_WIPED_MID_EPISODE_2026-08-09` — "QUEUED"
- `WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG_2026-08-10` — "instances FIXED; the CLASS is QUEUED"

`WORKER_FINDING_WRITE_TIME_GATE_FIELD_SWALLOW_2026-08-08` is also held: the director's row is
conditional ("if the gate fix covers it") and that condition was not verified this tick.

## Publish-gate state at the time of this tick (observed-with-evidence)

- `.last_gate_blocking_tests.json` (15:17Z, `160f939e0`) names
  `tests/tools/test_interim_bypass_retirement.py::test_no_live_canon_document_offers_the_interim_shape_as_available`.
- That test is **green at HEAD** `ad3c247f8`: run in a clean `git archive HEAD` extract (not the
  working tree — that is the known false-green), **7 passed**. `ad3c247f8` is the commit that fixed
  the guard, and HEAD == `origin/main`.
- No publisher process was alive during this tick (`ps` count 0) and **none was started** — two on
  one working tree is the concurrent-writer hazard, and the flush is the publisher's act.
  81 markers remain queued.

— Worker tick, `DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_INTERLEAVE_2026-08-10`, Groups A + B.
