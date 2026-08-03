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

## DISPOSITION COMPLETE (later tick, 2026-08-03) — all 18 flagged items closed, none bulk-archived

Item 3 above ("rank the Class B BUILD halves into the normal draw") was the named top residual. It is now
**done**, and item 4 is **resolved by verification**. Every one of the 18 flagged files was dispositioned
individually. Final split — **11 minted / 6 verified-built / 1 closed NO-BUILD**:

### 11 minted as real map atoms (`docs/design/maturity_map.yaml`, 167 → 178 atoms)
`SP2_1_working_day_calculator`, `SP2_2_rng_substream_primitive`, `SP3_size_and_clone_ratchet`,
`SP4_owned_quantity_registry_gate`, `SP5_shared_primitive_ensuring_activity`,
`W3_1b_intra_year_price_cap_granularity`, `W2_payment_channel_dd_consistency_invariant`,
`C_supply_start_semantic_separation`, `D_money_boundary_reconciliation`,
`H_stop_control_gap_characterisation`, `SITE_director_window_delta_view`.

Each carries `blocked_on: null` (the `director_build_open` park is abolished), its own `file_scope`, the
exit criteria from its mint doc, and its R15 both-ways obligation written into `simplifications:` rather
than left in a staged file no draw reads. They now compete as BUILD work. `D_money_boundary_reconciliation`
is deliberately a **new** id, not a re-mint of `money_representation_evidence` — that atom was DISCOVER-only
and its DISCOVER is closed; what is registered is the BUILD half its own recommendation named (the 37.0% of
bills whose rounded line items do not sum to the printed total), with the float→Decimal core migration
kept separate on its merits.

Six of the eleven are `close_to_learn` and were each classified **individually**, with reasons, into
`tests/design/test_maturity_map_facets.py::REVIEWED_CLOSE_TO_LEARN` — the other five went to
`meter_to_cash` / `price_to_bill`, because "everything I just added is close_to_learn" is exactly the
unreviewed default that list exists to catch. 19/19 facet tests pass.

### 6 verified BUILT → archived to `done/`
The four from the correction above, plus `ruling_consumption_ledger_release`, plus
**`gap1_reader_contract_failopen_fix` — which resolves item 4**. Its two `gate_authorizations.jsonl`
entries are `BUILD_OPEN` grants (a now-abolished *permission* act), **not** level records, so there was
never a contradiction to reconcile. The only `LEVEL_UP_SELF_CERTIFIED` entry matching "GAP1" belongs to a
different atom (`GAP1_gap_registers_as_mint_sources`, level 3). The fix itself is **built and live**:
`background/gap_register_scan.py:25-27` keys register 1 on a text heuristic (not the non-existent
`measured_bound` field) and register 6 on `state` across ALL prefixes (not `audit:*`) — the two fail-opens
the mint named.

### 1 closed NO-BUILD
`inbound_ratification_batch_path` — it asks for a hold-until-ratified mechanism, i.e. the permission
machinery `background/inbound_ratification.py` that CLAUDE.md requires to **stay deleted** (guarded by
`test_the_permission_surface_is_gone`). Verified gone on disk. Reasoning recorded in the archived file.

### Still in `in_progress/` on purpose — the next tick's named draw
`PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md`. Its stated blocker ("the agent cannot
self-cross the R16 wall") **is now false** — R16 was rescoped 2026-08-03 to *record*, not *authorise*. Its
residual is 15 reversible level moves that are now self-certifiable, and they are deliberately NOT
bulk-stamped: each needs re-verification against artifacts first. This tick is its own evidence for why —
one of the five "build done, level move pending" items (`director_window_delta_view`) had no code and no
test at all.

## PROCESS FINDING — the auto-processor swept this tick's in-flight work into its own commit

**Observed with evidence, not inferred:** commit `c0eee24e9` is messaged
"Auto-process run complete: report + LATEST.md + site/ (git=1f4cda668, net=£1,501,001)" but its diff
contains **this tick's 11-atom mint** (`docs/design/maturity_map.yaml` +191, and the regenerated
`site/data/maturity_map.json` +231) **and the 18 staging archive moves** — none of which is auto-process
output. `git log --oneline -2 -- docs/staging/done/PLANNER_MINTED_privacy_policy_page_2026-07-28.md`
returns `c0eee24e9`.

Nothing was lost and the site JSON regeneration was in fact correct, so this is recorded rather than
reverted — rewriting history on a tree with three concurrent writers would cost more than the mislabel.
But the commit message is now a false record of what that commit contains, which is the known broad-`add`
hazard: `process_run_complete.py` stages by directory, so any uncommitted work in those paths at sweep time
is absorbed under a message that does not describe it. This is the third recorded instance of the class.
The durable fix is for the auto-processor to stage its **own named paths** rather than broad-add, which is
registered here as a finding rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE: queue, don't fix on
sight, unless the machine is blocked — it is not).

---
## PROGRESS 2026-08-03 (next worker tick) -- Class B: 1 of 12 built, 11 still drawable

`working_day_calculator` (the item the previous tick dispatched but did not land) is now **BUILD Pass 1
complete** as map atom `SP2_1_working_day_calculator`, `level_current 0 -> 1`, recorded in
`gate_authorizations.jsonl` (R16). Landed `company/compliance/working_days.py` + a three-way-reconciled
England-&-Wales bank-holiday table 2012-2028, and `tools/working_day_guard.py` + R15 test, with **all 25
call sites unchanged** per the mandatory two-pass shape. Level is 1 and not 2 deliberately: Pass 2
migration is untouched, so no deadline the company actually computes has moved yet.

**Two errors in the closed DISCOVER doc were found by building it** (both corrected in the doc):
its census of 22 callers was an undercount -- the real number is **25**, and the three it missed include
two copies of the same arithmetic renamed to `_add_wd`, which is precisely the rename fail-open a
name-only guard passes; and its `working_days_between` interval was specified backwards
(`[start, end)` vs the shipped `(start, end]`), which would have silently moved every deadline the
primitive is supposed to leave alone. **A closed DISCOVER doc is a hypothesis, not a specification** --
worth carrying into the other 11 Class B items, whose designs have had no more scrutiny than this one had.

**STILL OPEN, unchanged by this tick:**
- **Class B: 11 items** (all except `working_day_calculator`) remain drawable BUILD work.
- **Class B residual on this item:** Pass 2 -- migrate the 25 callers, shrinking `BASELINE_ALLOWLIST`
  to empty, then `SP2_1` can claim L2+. Expect published deadline figures to move; that is R13 baseline
  correction (the company was computing deadlines early across bank holidays), not regression.
- **Class A: 5 items** still need `level_current` re-verified against real artifacts before any archive.
- The auto-processor broad-`add` finding above is still unfixed (queued, not blocking).

---
## PROGRESS 2026-08-03 (worker tick) — Class B: SITE lane drawn, and a rival-branch trap avoided

This tick drew the three-lane set (1 BUILD + 2 SITE) rather than re-triaging the queue.

**`SITE1_expert_doors` (SITE lane) — residual (b) CLOSED, level deliberately NOT moved.** Commit
`80055c4ff`. Its L2→L3 note recorded (b) as "R11 live-pixel verify (no autonomous network)". Network
was **probed, not assumed**, and was available — so the live surface was actually driven rather than the
residual re-stated for a fourth tick. `site/_live_harness.mjs` + `site/live_pixel_verify.py` fetch each
canonical door AND its live JSON from poesys.net and run the door's own boot path against them, so the
assertion lands on the rendered pixel. 7/8 doors verified live; the 8th was a **real live defect the
control found on its first honest run** — `/proof/` served the literal text
`belief_coeffs: [object Object]` — now fixed and re-verified. R15 both ways, 13/13, four mutations each
firing exactly their own test. **Level held at 2**: residual (c) is genuinely unbuilt.

**The rival-branch trap, worth recording as a class.** Before building, the two unmerged branches holding
`SITE1` proof-door work were audited (memory: *guard flags unmerged → ADOPT, don't rebuild*).
Both turned out to be **fully superseded by main**: `worktree-agent-ac55b4bffa0425237`'s
`test_site1_proof_citations.py` is an 85-line *subset* of main's, and
`worktree-agent-a6ad9f2b324019a71` (2026-07-30) would have **re-added the deleted permission machinery**
(`fronts.yaml`, `fronts_reconciler.py`, `inbound_ratification.py`, `director_authority_channels.py`) that
CLAUDE.md requires to stay deleted and `test_the_permission_surface_is_gone` guards. Adopting it on the
strength of "an unmerged branch holds unique work" would have reverted a ratified rip-out. **"Ahead of
main" is not "holds work main lacks"** — diff against main in BOTH directions before adopting. Neither
branch was reaped this tick (not the drawn work, and the rescue branches carry other atoms' content).

**Stale evidence corrected on the atom:** its evidence list still cites `site/method/`,
`site/simplified/` and `site/tours/` as built doors with their own render harnesses. All three now
**301 to `/proof/`** under the SITE_V5 five-surface ruling, so that evidence describes doors that are no
longer reachable. The canonical live set is the 8 URLs in `site/sitemap.xml`, which is what the verifier
derives its door list from rather than hand-typing one.

**Still open, unchanged by this tick:** the remaining Class B BUILD halves; the auto-processor
broad-`add` finding (queued, not blocking).
