<!-- SUPERVISOR_DRAW: self-drawable -->
# [WORKER FINDING] — The `in_progress/` doorbell is a BUILD queue, not a staging backlog (2026-08-03)

**Provenance:** worker tick, 2026-08-03. The scheduled doorbell named 18 `docs/staging/in_progress/PLANNER_MINTED_*`
files as "unprocessed staging". They were classified against real disk state rather than archived.

## The finding

`in_progress/` **is** scanned by design — `background/supervisor.py:326` ("DURABLE draw-visibility fix
(2026-07-20, the 3-hour silent-stall root cause)") deliberately re-surfaces *misparked* items via
`misparked_actionable_in_progress` / `misparked_open_campaign_in_progress` / `selfdrawable_mint_in_progress`.
The CLAUDE.md line saying `in_progress/` is excluded from the scan is **stale** and should be corrected:
the exclusion was superseded by the 2026-07-20 fix.

The 18 flagged files are exactly the `SUPERVISOR_DRAW: self-drawable` + `BLOCK_RELEASE: propose_then_proceed`
set — items whose park reason was `director_build_open` or `director_level_up`, **acts abolished 2026-07-29
and swept 2026-08-03**. The doorbell is correct. What is wrong is the *disposition* each tick applies to it.

**These are not homogeneous, and treating them as one archive-batch would bury real work.** Measured split:

### CLASS A — BUILD DONE, only the (now-abolished) level move remained → self-certify + archive (~6)
`director_window_delta_view`, `privacy_policy_page`, `ruling_consumption_ledger_release`,
`unstated_reason_block_impossible`, `reversible_draws_dont_queue_for_permission` (§4), `first_ranked_gap_list`.

Ledger check (`docs/observability/gate_authorizations.jsonl`): only `ruling_consumption` has entries (6).
The other five level claims are **genuinely unrecorded** — so the archive is NOT a formality; each needs its
level re-verified against evidence and recorded via `record_level_up_self_certified` (R16). Deliberately NOT
bulk-stamped this tick: a control passing for the wrong reason is not evidence, and clearing `blocked_on`
never moved `level_current` (the abolished-block stale-cells class).

### CLASS B — DISCOVER/DESIGN closed, BUILD half genuinely NOT BUILT → real drawable work (12)
`gap1_reader_contract_failopen_fix`, `inbound_ratification_batch_path`, `intra_year_price_cap_granularity`,
`payment_channel_dd_consistency_invariant`, `working_day_calculator`, `money_representation_evidence`,
`owned_quantity_registry_gate`, `rng_substream_primitive`, `shared_primitive_ensuring_activity`,
`size_and_clone_ratchet`, `stop_control_gap_characterisation`, `supply_start_semantic_separation`.

Each has a **closed DISCOVER doc under `docs/design/` with a designed mechanism** and a BUILD half that was
parked behind `director_build_open`. That block no longer exists, so **all twelve are BUILD-drawable now.**

## Why this matters (consumed ≠ absorbed)

Twelve designed, ranked, non-duplicate build items have been invisible as *work* while being highly visible
as *staging noise* — re-flagged every tick, dispositioned as "archive me", never executed. The steers were
CONSUMED into design docs and never ABSORBED into the drawable queue. That is the R17 stall class, and the
recurring doorbell was the symptom being silenced rather than read.

## Disposition taken this tick

- `working_day_calculator` (Class B) **dispatched to BUILD** — the R10 class fix (canonical working-day
  primitive + dated EW bank-holiday calendar + AST guard). Chosen as highest-value: regulatory deadline
  arithmetic is specified in working days, so the SIM currently cannot produce a deadline breach a real
  supplier would be fined for. Closing it makes that breach class reachable.
- The other 11 Class B items remain drawable; they are BUILD work, not archive candidates.
- Class A left unarchived **on purpose** pending per-item level verification. Archiving them without the
  ledger record would clear the doorbell while leaving `level_current` stale — the exact defect above.

## CORRECTION (later tick, 2026-08-03) — the Class A premise was wrong

Item 2 said the five unrecorded Class A items needed `record_level_up_self_certified`. **They do not.**
Checked against `docs/design/maturity_map.yaml`: **none of the five exists as an atom at all** —
`director_window_delta_view`, `privacy_policy_page`, `unstated_reason_block_impossible`,
`reversible_draws_dont_queue_for_permission`, `first_ranked_gap_list` return zero matches. There is no
`level_current` to move, so R16 does not apply to them; they are staged mint-docs, and their correct
closure is **artifact verification then archive**, not a ledger stamp. Stamping a level for a
non-existent atom would have been exactly the wrong-reason evidence item 2 set out to avoid.

Artifact verification (grep/ls on real disk, this tick):

| item | evidence | verdict |
|---|---|---|
| `privacy_policy_page` | `site/privacy/index.html` present | BUILT |
| `unstated_reason_block_impossible` | live in `tools/pre_commit_test_gate.py`, `background/staging_disposition.py`; tests in `tests/design/test_maturity_map_facets.py`, `tests/tools/test_pre_commit_test_gate.py` | BUILT |
| `reversible_draws_dont_queue_for_permission` | `background/one_way_door.py`, `background/decision_log.py` present | BUILT (§4) |
| `first_ranked_gap_list` | `docs/design/FIRST_RANKED_GAP_LIST.md` (the deliverable IS the doc) + `background/gap_register_scan.py` | BUILT |
| `director_window_delta_view` | `window_delta` appears **only** in `docs/design/*.md` — **no code, no test** | **NOT BUILT — reclassify to Class B** |

So the split is **4 archivable + 13 Class B BUILD halves**, not 6 + 12. `gap1_reader_contract_failopen_fix`
also already carries a `gate_authorizations.jsonl` entry despite being filed Class B — its record and its
build state disagree and need reconciling before it is drawn.

Deliberately NOT archived this tick: the three concurrent BUILD forks (W1_6b, DD, HX2) all hold
`docs/design/maturity_map.yaml`, so any minting is deferred until they merge rather than raced.

## Work this creates

1. ~~Correct the stale CLAUDE.md line asserting `in_progress/` is excluded from the staging scan.~~
   **DONE** (commit `08d31bcce`, pushed) — line 26 rewritten against `supervisor.py:326-355`; CLAUDE.md
   also trimmed 35007 → 34789 chars, having arrived over its own 35k hard limit.
2. ~~Level-verify the five Class A claims.~~ **SUPERSEDED by the correction above** — four are verified
   BUILT and are plain archive-to-`done/` candidates (no ledger record applies, they are not atoms);
   `director_window_delta_view` is reclassified Class B.
3. Rank the **13** Class B BUILD halves into the normal draw so they compete as build work rather than
   re-presenting as staging noise each tick. **This is now the top residual item** — it is the one that
   converts invisible designed work into drawable work (the R17 consumed-≠-absorbed stall class).
4. Reconcile `gap1_reader_contract_failopen_fix`: it has a `gate_authorizations.jsonl` record but was
   filed as an unbuilt BUILD half. One of the two is wrong.
