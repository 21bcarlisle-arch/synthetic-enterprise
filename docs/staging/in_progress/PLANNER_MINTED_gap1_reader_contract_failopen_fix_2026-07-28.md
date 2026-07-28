<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_build_open -- GAP1 reader-contract fail-open fix; H-lane BUILD demotion needs a director BUILD_OPEN -->
<!-- DISCOVER half (a) LANDED 2026-07-28; remaining work is BUILD half (b)(c), blocked_on director_build_open. -->
# [PLANNER-MINTED] — GAP1 reader-contract FAIL-OPEN correction (register-1 field + register-6 prefix) (2026-07-28)

> **STATUS 2026-07-28 (worker tick): DISCOVER half (a) DONE — self-drawable → blocked.**
> Exit criterion (a) landed in `docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md`: both fail-open OPEN
> rules corrected against **verified live data** (register 1 — `measured_bound` exists 0× across 621
> free-text strings / 146 atoms → text heuristic + structured-field recommendation; register 6 — all 5
> `audit:*` rows are false-positive/open, the 15 `adjudicated-real` findings live under
> `coldwalk`/`harden_sweep`/`expert_hour`/`population`/`bill_to_ledger_linkage` → keyed on `state`,
> prefix-agnostic, residue = 3 open + 15 real = 18). The two old-key mutations are now written into the
> BUILD half's R15 spec (c). **BLOCKING SUB-ITEM:** BUILD half (b)(c) — the `background/gap_register_scan.py`
> reader implementing the corrected keys — **UNBLOCKS ON:** `director_build_open` (H-lane BUILD demotion,
> R16; the agent cannot self-authorize). Marker flipped to `blocked` so the rest-proof freshness check no
> longer treats this atom as drawable.

**Source:** `PLANNER_MINTED_first_ranked_gap_list_2026-07-28` (GAP3) §0 + `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28`
§1 (the registers ARE the backlog; a reader that cannot see open rows is not an enumeration). Net-new:
surfaced only by the GAP3 live-register enumeration pass, which found **two ways the GAP1 reader contract
(`docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md`), as written, would FAIL-OPEN** — report an empty
residue while open rows demonstrably exist, the exact R15 tautology/fail-open GAP1's own invariant 1
forbids.

**Provenance:** RUNG-7 planner mint (autonomous — `mint` direction per GAP_TRIAGE_RATIFIED §2). grep-confirmed
no existing `PLANNER_MINTED_*`/atom fixes the contract keying. NOT a re-mint of GAP1 (which *wrote* the
contract) — this *corrects* two keying bugs the live data proved.

**Serves:** the acceptance test the whole ruling turns on — *"a saturation/rest claim is impossible while
any published register holds an open, un-triaged item."* A reader keyed on a non-existent field / wrong
prefix would let a saturation claim stand while 15+ real findings sit open. This fix makes that acceptance
test real.

**Fidelity gained (one sentence):** none directly — an **enumeration-integrity** fix so the backlog reader
cannot fail-open (report empty while open), the failure mode that would silently re-authorise rest.

---
## The two defects (both R15 FAIL-OPEN)
1. **Register 1 keys on a field that does not exist.** Contract OPEN rule = "carries no `measured_bound`";
   but `maturity_map.yaml`'s `simplifications:` entries are **plain free-text strings (621 across 146
   atoms), zero structured `measured_bound` fields**, and the list is now an append-only dated FRAME/HARDEN
   **log** (~4× the contract's stale "157"). A reader keying on `measured_bound` reads all-open or
   all-closed, never the true residue.
2. **Register 6 keys on the wrong prefix.** Contract keys standing sanity findings on `audit:*`; but the
   **15 adjudicated-real** findings live under `coldwalk:` / `expert_hour:` / `harden_sweep:` / `population:`.
   The 9 `audit:*` rows are only false-positive / un-adjudicated. A reader keyed on `audit:*` **misses all
   15 real findings**.

## Lane / level / deps
- **Lane:** `H_harness`. **DISCOVER half (drawable NOW, doc-only L3):** correct the GAP1 contract doc —
  register-1 OPEN rule keyed on *the actual data* (an entry with no inline numeric/interval bound token AND
  not a dated progress-log line), and a recommendation to add a structured `measured_bound` field so the
  log is separable from true simplifications; register-6 OPEN rule keyed on **adjudicated-real** rows across
  **all** finding prefixes (`coldwalk:`/`expert_hour:`/`harden_sweep:`/`population:`/`audit:`), verdict-filtered.
- **BUILD half (b/c):** the GAP1 reader (`background/gap_register_scan.py`) implements the corrected keys.
  **blocked_on:** `director_build_open` — same H-lane BUILD demotion as GAP1's own reader (R16: ledger is
  authority; the agent cannot self-authorize a `BUILD_OPEN`).
- **Target level:** contract correction (doc) autonomous; reader BUILD → `level_current 0 → 3`,
  `blocked_on: director_level_up`.

## Exit criteria
- **(a) DISCOVER (now):** the corrected GAP1 contract — both OPEN rules keyed on fields that **exist in the
  live data**, with the register-1 log-vs-simplification split named and the register-6 prefix set enumerated.
- **(b) BUILD:** the reader emits the true residue under the corrected keys.
- **(c) R15 both ways (mandatory):** MUTATION — restore the OLD keys (`measured_bound` / `audit:*`-only) ⇒
  the reader reports **empty** while the 6 SSP cells / 15 real findings demonstrably exist (control FIRES);
  corrected keys ⇒ residue non-empty. FAIL-SAFE — an unparseable register reads **drawable** (invariant 2).

## Walls untouched
- **No R13 / curriculum / generator move:** reads published state only; changes what is *drawable*.
- **No level self-bump (R16):** DISCOVER contract correction only; reader BUILD stays `blocked_on director_level_up`.
- **R12:** the residue count is a diagnostic; the reader emits residue, never scores it.
