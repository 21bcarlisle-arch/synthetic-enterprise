<!-- DISCOVER artefact — GAP1 exit criterion (a). BUILD half (b)(c)(d) stays blocked_on director BUILD_OPEN. -->
# Gap-Register → Mint-Source Contract (GAP1, DISCOVER half)

**Serves:** `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` §1 (the published gap
registers are first-class mint sources) + §5 (the registers exist; nothing read them as work).
**Acceptance the ruling turns on:** *a saturation/rest claim is impossible while any published
register holds an open, un-triaged item.*
**Mint:** `PLANNER_MINTED_gap_registers_as_mint_sources_2026-07-28`, exit criterion (a).

This is the DISCOVER/design deliverable only: it names, per published register, its **primary-state
path** and the **field that marks a row OPEN**, and specifies the reader contract the BUILD half (b)
will implement. The BUILD half — an independent reader emitting the OPEN residue + a `gap_register`
level in `authorized_set_enumeration()` — is **blocked_on director BUILD_OPEN** (the standing
harness-BUILD demotion; `H_harness/close_to_learn` is off every open product front, R16: the agent
cannot self-authorize a `BUILD_OPEN`/`FRONT_OPEN`). Nothing here closes, reclassifies, or reranks a
gap — that is GAP2 (method) and GAP3 (ranked list), which return for ratification.

## Reader-contract invariants (bind the BUILD half)
1. **Independent read (LAW-C).** The reader imports **nothing** from `background/supervisor.py`; it
   reads primary state directly, exactly as `background/primary_state_scan.py` does. A reader that
   restated the tick's own belief could not falsify a saturation claim (R15 tautology, forbidden).
2. **FAIL-SAFE toward work (exit (d)).** A parse/read error on any register reads **drawable** (the
   Rule-0 direction — ambiguity forbids rest), mirroring `_safe()`'s existing contract. An
   unreadable register is a *reason the residue may be non-empty*, never a silent empty.
3. **R12 non-negotiable.** The *count* of open/closed rows is a diagnostic on the enumeration line
   only — never a score, target, or headline. The reader emits the residue; it never scores it.
4. **Diagnostic, not closure.** A row appearing in the residue means *drawable*, i.e. "a saturation
   claim is illegitimate while this is open." Whether the row is worth *minting* vs.
   deliberate-and-staying is GAP2's taxonomy, applied only after director ratification.

> **Correction pass (2026-07-28, `PLANNER_MINTED_gap1_reader_contract_failopen_fix`, DISCOVER half (a)):**
> the GAP3 live-register enumeration pass proved **two of the OPEN rules below would FAIL-OPEN** — report an
> empty residue while open rows demonstrably exist, the exact R15 tautology/fail-open invariant 1 forbids.
> Both are corrected inline (registers **1** and **6**), each with the live-data evidence that proved the
> defect (R9: evidence before narrative). Both OPEN rules are now keyed on fields that **exist in the live
> data**. No BUILD, no reader change here — the reader (b) remains `blocked_on director_build_open`; this
> pass fixes only the contract it will implement, and adds the two old-key mutations to the R15 spec (c).
>
> **Live counts as of 2026-07-28 (read-only, R9 observed-with-evidence):** register 1 = 621 free-text
> `simplifications` strings / 146 atoms / 0 `measured_bound` fields; register 6 = 18 open residue rows
> (3 `open` + 15 `adjudicated-real`), 8 `adjudicated-false-positive` excluded, 0 real under `audit:*`.

## The registers, their primary-state paths, and the OPEN-marking field

| # | Register | Primary-state path | A row is OPEN when… |
|---|----------|--------------------|---------------------|
| 1 | **Deliberate-simplifications register** | `docs/design/maturity_map.yaml` — the per-atom `simplifications:` lists (**621 free-text string entries across 146 atoms**, live-counted 2026-07-28; the stale "157" was ~4× low). These entries are **plain strings, not structured records** — `measured_bound` appears **zero** times in the file (verified), and the list has become an **append-only dated FRAME/HARDEN log** (many entries are `YYYY-MM-DD <VERB> …` progress lines, not simplifications). | **[CORRECTED 2026-07-28 — the original `measured_bound` key FAILS-OPEN: it keys on a field that exists nowhere in the data, so the reader reads all-open or all-closed, never the true residue — the exact R15 tautology invariant 1 forbids.]** A row is OPEN when the entry (a) is **not a dated progress-log line** (does not begin with an ISO date `YYYY-MM-DD` followed by a log verb such as UPGRADED/AUTHORED/DISCOVER/LANDED) **and** (b) carries **no inline measured bound** — no numeric/interval/`±`/`%`/comparison token stating how wrong the simplification is. An entry that argues its bound inline is deliberate-and-staying pending GAP2; a bare, unmeasured, non-log simplification is OPEN (§3: a simplification must be argued **with a measured bound** to stay deliberate). **BUILD-half recommendation (for the director):** add a structured `measured_bound` field to the schema so the progress-log is mechanically separable from true simplifications — until then the reader must use the text heuristic above, and must FAIL-SAFE toward OPEN on an entry it cannot classify (invariant 2). |
| 2 | **Fidelity-evidence ledger** | `docs/observability/fidelity_evidence_ledger.json` — dict keyed `atom_id::evidence_id`, each with `per_cell_lift[]` | any `per_cell_lift` cell with `lift <= 0` **or** `err_model >= err_naive` at `commercial_weight > 0` (the model is at/below its own naive baseline on a commercially-weighted cell — the gap the coupled triad exists to surface). SSP baseline cells that are director-**HELD** (R13/R12) are routed to `blocked-on-director` by GAP2, not silently dropped. |
| 3 | **Board-spec reconciliations 001–006** | `docs/design/BOARD_SPEC_00{2,3,4,5,6}_RECONCILIATION.md` (+ `WHOLESALE_TRADING_BOARD_RECONCILIATION_2026-07-22.md`) | any row marked **PARTIAL** or **ABSENT** in the reconciliation table. (`001` currently has no standalone reconciliation file — its absence is itself an OPEN row: "reconciliation not yet published.") |
| 4 | **Disqualification battery** | the `## Disqualification battery` / practitioner-credibility sections inside the board-spec + wholesale reconciliation docs above | any battery item whose status is not **met** (a "a practitioner would say this makes the build not credible" item still standing). Board-battery weight is a GAP2 ranking dimension. |
| 5 | **Claim-status placeholders** (designed-but-not-working) | code carrying a `claim_status`/placeholder marker; **seed instance: the carbon ledger** — `company/carbon/carbon_ledger.py`, map atom `E5_carbon_three_ledger` (idle, `level_current 0 → 3`), FRAME `docs/design/frame/E5_carbon_three_ledger_FRAME.md` | a surface claims a capability whose implementation is a placeholder / not wired to a live consumer (R11: claim ≠ pixel). Seed the residue with `E5_carbon_three_ledger`; enumerate the rest on the BUILD pass. |
| 6 | **Standing sanity findings** | `docs/observability/sanity_adjudication_ledger.json` — a dict keyed by `<prefix>:<finding>`, each value carrying a **`state`** field ∈ {`open`, `adjudicated-real`, `adjudicated-false-positive`}. **Key on `state`, across ALL prefixes** — never on a prefix. | **[CORRECTED 2026-07-28 — the original `audit:*` prefix key FAILS-OPEN: live-counted, all 5 `audit:*` rows are false-positive (3) or open (2), with ZERO `adjudicated-real`; the **15** `adjudicated-real` findings live under `coldwalk:`(7), `harden_sweep:`(3), `expert_hour:`(2), `population:`(2), `bill_to_ledger_linkage*`(1). A reader keyed on `audit:*` misses all 15 real findings.]** A row is OPEN when its `state` is **`open`** (un-triaged — still needs adjudication) **or `adjudicated-real`** (confirmed real, remediation unminted/unresolved) — **verdict-filtered, prefix-agnostic**. `adjudicated-false-positive` rows are **not** residue. (Live residue on 2026-07-28: 3 `open` + 15 `adjudicated-real` = 18 rows; the `audit:*`-only reader would have reported 0 real.) |
| 7 | **MODEL_ON_A_PAGE Timeframe 2** | `docs/design/THE_MODEL_ON_A_PAGE.md` — the "Timeframe 2" / near-term section | any Timeframe-2 capability line not yet backed by a live surface or a minted atom. |
| 8 | **Registered follow-ons** | `docs/design/proposals/PROPOSE_SCENARIO_FOLLOWONS_RANKED.md` and any `PROPOSE_*_FOLLOWONS*` under `docs/design/proposals/` | a ranked follow-on row neither minted (a `PLANNER_MINTED_*`/map atom names it) nor explicitly retired. |

## BUILD half — the still-blocked residue (for the director's BUILD_OPEN decision)
- **(b)** an independent reader (`background/gap_register_scan.py`, imports nothing from `supervisor`)
  emits the OPEN residue across registers 1–8 from primary state; a new `gap_register` level appears
  in `authorized_set_enumeration()` reading that residue (Y ⇒ drawable ⇒ rest illegitimate).
- **(c) R15 both ways (mandatory):** neuter the read (residue → `[]`) ⇒ the `gap_register` level reads
  empty **while open rows demonstrably exist** (control FIRES); restore ⇒ green. Second mutation: a
  register seeded with one open row must flip the level to Y. **Third+fourth mutation (the two keys this
  correction fixed — each must FIRE, proving the old key fail-opened):** (i) restore register-1's OLD
  `measured_bound` key ⇒ residue reads all-open or all-closed (the field exists nowhere) while true
  unmeasured simplifications exist — control FIRES; corrected text-heuristic key ⇒ true residue non-empty.
  (ii) restore register-6's OLD `audit:*`-only prefix key ⇒ residue reports **0 real** while the 15
  `adjudicated-real` rows demonstrably exist under other prefixes — control FIRES; corrected `state`-keyed,
  prefix-agnostic rule ⇒ residue = 18 (3 open + 15 real).
- **(d)** parse/read error on any register ⇒ **drawable** (fail-safe toward work).
- **blocked_on:** `director_build_open` (H-lane BUILD demotion; R16 — ledger-only, agent cannot
  self-authorize). Lands at build-quality with `blocked_on: director_level_up` for the 0→3 move.

## Walls untouched
- **R13 / curriculum / generator ground truth:** reads existing published state only; changes what is
  *drawable*, never a baseline or difficulty parameter. SSP-baseline HELD cells route to
  `blocked-on-director`, never self-closed.
- **No level self-bump (R16):** DISCOVER contract only; BUILD half restores draw eligibility, no
  `level_current` move here.
- **No closure/reclassification (§3):** GAP1 only *enumerates*; the deliberate-vs-mint call is GAP2,
  ratified by the director.
