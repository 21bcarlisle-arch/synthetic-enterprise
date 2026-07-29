<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- UNBLOCKS ON: nothing external for the CA2-finding-publish leg (drawable now). The four LEVEL_UP moves are UNRELEASED and director-reserved (R16) — see §A. -->

# [PLANNER-MINTED / GOVERNANCE] — CA promotion-batch ratification: consumption report + the act that can release it (2026-07-29)

**Provenance:** processing `DIRECTOR_RULING_CA_PROMOTION_BATCH_RATIFIED_2026-07-29.md` as a mint source
(§2+§4 `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`). The ruling ratifies the CA
promotion batch previously requested by `PLANNER_MINTED_cohort_promotion_disposition_2026-07-28`
(now in `done/`). This doc is the **consumption report** — it does NOT self-write authority (R16).

## §0 — §4 DEFECT recorded, not silently absorbed

The ruling carries **no `WORK THIS CREATES` block**. Per the §4 convention (a ruling/steer arriving
without one is a defect *in the ruling*), the work is minted here from the body AND the block is
**requested from the author** (NTFY this tick) rather than absorbed. Work identified from the body:
(a) release the four level moves, (b) publish the CA2 coverage finding in its own right, (c) the
`SE_DRAW_POPULATION` activation — director-reserved, explicitly **not** ours (§ below).

## §A — the four LEVEL_UP moves are UNRELEASED; here is the act that can release them

The ruling declares (verbatim):

```
LEDGER: LEVEL_UP_PROPOSED CA1_cohort_assignment_live L3
LEDGER: LEVEL_UP_PROPOSED CA2_coverage_report_realised_cohort L3
LEDGER: LEVEL_UP_PROPOSED CA3_segmentation_untestable_ledger_marking L3
LEDGER: LEVEL_UP_PROPOSED CA4_cohort_activation_sequencing_verdict L1
```

Run against the live mechanism this tick (`gate_authorization.report_ruling_release`):

- `parse_ledger_directives(...)` → **`[]`** (zero directives parsed).
- `report_ruling_release(...)` → `{"directives": 0, "released": [], "unreleased": [], "ledger_available": true}`.
- `grep` of `docs/observability/gate_authorizations.jsonl` → **no `LEVEL_UP_PROPOSED` entry for any CA atom** (only a prior `BUILD_OPEN` for `CA1`, 2026-07-28). All four atoms remain `level_current: 0`.

**Two independent reasons the worker cannot consume this (both R16 / R7 / R8):**

1. **The doc is untracked** (`git status` = `??`). A staged doc is not a director-console act and not a
   bridge-authored commit, so it is not a valid `advisor_ruling` authority — staged text carries zero
   authority (R7/R8). No authenticated ledger entry exists for these moves.
2. **The directive lines do not parse.** `_LEDGER_DIRECTIVE_RE` requires a bare digit level
   (`\d+`); the ruling wrote `L3`/`L1`, so every line fails to match and is fail-closed **skipped**.
   Even a committed bridge doc in this exact form would release nothing.

**Per the ruling's own "If this cannot land, say so in one line and name the act that can":**
> The releasing act is the **director's console `record_level_up`** for each atom — `CA1`,`CA2`,`CA3`
> → level `3`; `CA4` → level `1` — OR the advisor committing this ruling **as bridge author**
> (`21bcarlisle-arch`) with the directives in **digit form** (`LEDGER: LEVEL_UP_PROPOSED CA1_cohort_assignment_live 3`),
> which the `advisor_ruling` channel accepts (LEVEL_UP_PROPOSED is on the ROUTINE_ACTIONS allowlist).
> The worker will NOT write these entries by inference. Reported UNRELEASED, not silently done —
> the failure mode that cost eleven hours on 2026-07-28.

**Directive-format finding (minted, harness lane):** the parser rejects the natural director shorthand
`L3`. Either the ruling template must emit digit-form, or `_LEDGER_DIRECTIVE_RE` should tolerate an
optional `L` prefix on the level group. Filed as a candidate harness atom (`ledger_directive_L_prefix_tolerance`),
DISCOVER-workable now; not built this tick (R10: extend the class, don't instance-patch — but flag the
class first, and it is a two-way-door parser change, so it awaits the release-path decision above).

## §B — CA2 coverage finding: drawable now (the result that matters more than the promotion)

The ruling: *"CA2 reports the ~12-cell value knee surviving a real draw at N_scored=198 … Publish it as
a finding in its own right … thin cells are findings, not embarrassments."* The data already exists at
`docs/observability/cohort_coverage_realised.json` (`_meta.atom: CA2_coverage_report_realised_cohort`,
`gate_ok: true`, `code_sha 6bb6789ddea7`). This leg is a **follow-on under the existing `CA2` map atom**
(no new atom — the coverage report is built; only the *standalone-finding surfacing* is outstanding),
and it does **not** depend on the level move.

- **Lane:** SITE/publish (surface the realised cell counts + which cells ran thin as a named finding).
- **Target level:** none new — publishing an existing L3-quality artifact as a finding; no level bump.
- **Exit criteria (R11):** the finding is fetchable on a live surface, states realised cell counts and
  the thin cells at the ~12-cell knee (N_scored=198), and is linked as a finding, not inside a level-up.
- **Deps:** none. Drawable this-or-next tick independent of §A.

## §C — Walls untouched

- **The four LEVEL_UP moves** — director-reserved (R16); reported UNRELEASED, never self-written.
- **`SE_DRAW_POPULATION`** — director-reserved R13 curriculum. The ruling is explicit: *"Do not treat
  these ratifications as the activation."* When ready the director raises it as its own `[ACT]` with the
  terms from `0ac3e1b5e` and `e0056d53e`. **Not armed here.**
- No one-way door. All reversible behind the epistemic wall.

— Planner mint, from DIRECTOR_RULING_CA_PROMOTION_BATCH_RATIFIED_2026-07-29 (§4 defect: no WORK-THIS-CREATES block), 2026-07-29.
