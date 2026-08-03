<!-- MOVED TO in_progress/ 2026-08-03 (worker tick) -- this file is a BUILD QUEUE, not a
  message, and the scanned root was making it read as unprocessed staging every tick. Its Class B
  list (13 designed, unbuilt halves) is still open and still drawable; nothing here is archived.
  THIS TICK DID NOT DRAW FROM IT: the self-refill draw handed over W1_11_fabric_physics_core
  (level 2->3), which was built to a measured blocker -- see commit 66d73d1e0 and the W1_11 cell.
  The next tick should draw a Class B half by name rather than re-triaging this list again;
  re-triage is the treadmill this finding itself warned about. -->
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

---
## PROGRESS 2026-08-03 (worker tick) — the three-lane draw was a STALE-CELL job, and it hid a control fail-open

This tick drew the same three atoms as the last one. Checking real state first (R7) showed why: two of
the three had their builds **adopted onto main this morning** (`08acb5f60` evidence pages, `094bbc007`
expert doors) while their `level_current` cells still read the pre-build value. The UNMERGED-WORK guard
flagged all three, but the answer was neither "rebuild" nor "adopt" — the work was already home and only
the *record* was stale. **Re-verified rather than re-stamped**, per the standing rule that a control
passing for the wrong reason is not evidence.

**Two levels recorded, each against its own named condition** (`gate_authorizations.jsonl`):
- `SITE_director_window_delta_view` **L1→L2**. Not a judgement call: the ledger's own L1 correction from
  earlier today named the unblock condition verbatim — *"L2 becomes claimable on the next publish via
  `site/live_pixel_verify.py --door /director/`"*. Tested, not assumed. main==origin, `/director/` 200,
  live run PASS, delta panel rendering real derived values.
- `SITE_evidence_pages_behind_nodes` **L0→L2**. 25/25 tests, live `/evidence/` renders 6395 elements of
  primary-state evidence, and the **orphan transition closed**: `generate_evidence_data.generate()` was
  never wired into `process_run_complete.py` despite its own docstring saying it was safe to call from
  there. A page derived entirely from moving sources would have frozen at its build-day state.
  *Honest bound:* at wiring time the regenerated page differed only in `generated_at`/`git_hash` — the
  freeze was structural and future-facing, not an observed stale page.

### The finding worth carrying: coverage derived from the sitemap was a FAIL-OPEN

`site/live_pixel_verify.py` — the control `SITE1_expert_doors` rests its R11 evidence on — derived its
door list from `site/sitemap.xml` alone. The sitemap deliberately excludes off-nav surfaces. So **every
deployed-but-unadvertised door was skipped while the tool reported "8/8 doors verified"**. Two live doors
sat outside coverage: `/evidence/` (200, linked six times from the front-door diagram, missing from the
sitemap in breach of that file's *own* stated inclusion rule) and `/director/` (200, `NEVER_ADVERTISED`
by design, so it could **never** be covered by a default run — its R11 evidence rested on a manual
`--door` flag that nothing repeated).

Fixed both ways, as **class guards not instance fixes** (R10): `/evidence/` added to the sitemap;
`INTERNAL_DOORS`+`all_doors()` so a default run covers every *deployed* door. Two new controls derive
their door set from the **repo** and cross-check against `site/_redirects` as an *independent* oracle —
deriving it from the sitemap would have been the tautology pattern. R15 both ways: with `/evidence/`
removed the control fails naming exactly `/evidence/`, and passes restored. **Live coverage 8/8 → 11/11.**

`SITE1_expert_doors` **held at 2**: its remaining L3 residual is the SITE_CONSTITUTION's own Final DoD
line, a genuine Expert Hour across all doors. Closing a fail-open in its control does not discharge that.

**Still open, unchanged:** the 11 remaining Class B BUILD halves; `SP2_1` Pass 2 (migrate the 25 callers);
the auto-processor broad-`add` finding (queued, not blocking).

---
## PROCESS FINDING 2 (2026-08-03 worker tick) — the run_complete queue cannot drain, and the doorbell will say "unprocessed staging" forever

**Observed with evidence, not inferred.** 13 `run_complete_*.md` markers sat unprocessed in
`docs/staging/` spanning `093145Z` → `122143Z`. Measured at 12:37 UTC:

- Last successful auto-process commit: `c0eee24e9`, **09:30 UTC — 3h07m earlier**.
- `background/background_worker.py` logged the whole backlog twice (12:06, 12:36) as
  *"Lock-skipped … (another instance holds the run lock) — still pending, will retry next cycle"*.
- `ps` showed `process_run_complete.py` **alive and working** (PID 1376812, 8m06s elapsed, 35% CPU,
  2m52s CPU time) — and running against the **newest** marker `122143Z`, not the oldest.
- `docs/observability/.publish_gate_state.json` is `{"failures": [], "wedge_since": null}` — **no wedge**.

**The machine is not blocked, so this is QUEUED not fixed on sight (SELF_INTERRUPT_DISCIPLINE).** The
mechanism is a throughput inequality, not a fault: a publish takes ~8-16 min (its gate runs the suite),
markers arrive every ~10-15 min, and the worker's leftover-sweep can never take the run lock. Processing
the newest marker is *correct* — the latest sim state is what should publish — but the superseded markers
are never archived, so the queue only grows. Every future tick's doorbell will therefore report
"unprocessed staging" from a queue that is working as designed, which is exactly how a real stall would
be camouflaged next time (cf. the `in_progress/` doorbell finding at the top of this file — same class:
a recurring doorbell read as noise instead of as state).

---
## PROGRESS 2026-08-03 (worker tick) — Class B: `intra_year_price_cap_granularity` BUILT, and its DISCOVER was wrong in three places

Drew the named self-refill atom `W3_1b_intra_year_price_cap_granularity` (Class B, the second of the 12
to be built). **L0→L2**, recorded in `gate_authorizations.jsonl`. Sourcing artefact
`docs/market_research/ofgem_cap_windows.md`; 15 new tests + 3 rewritten; **8 mutations, each firing its
own named test**, baseline restored green.

**What was built:** `get_cap_unit_rate_for_date()` + a 21-window schedule keyed on Ofgem's real cap
cadence (six-monthly Apr/Oct to 30 Sep 2022, quarterly after), with the Energy Price Guarantee as a
separate `min(cap, EPG)` overlay for Oct-2022→Jun-2023 so the two instruments stay individually legible.
The annual lookup is deliberately unchanged for callers whose own grain is a year.

**R10 class, not an instance.** The DISCOVER named one binding site; there are **two** —
`run_phase2b.py:1115` also clamps resi *fixed* terms on `int(term_start_str[:4])`. Both re-threaded, and
a source-scan control now fails if either regresses to the annual lookup or loses its clamp entirely
(mutations 7 and 8).

**The measurement found a second defect nobody had predicted.** The named finding is confirmed and is
the largest deviation in the table — Jan–Mar 2022 was clamped at 305.0/95.0 £/MWh against a real
208.0/40.7, i.e. **47% (elec) and 133% (gas) too loose in exactly the quarter the crisis bit**. But
comparing *every* window against the old blend showed the annual table is not merely mis-*timed*: it is
systematically mis-*levelled*, sitting **10–80 £/MWh below the published cap in almost every non-crisis
period** (2025 elec 190.0 against a real 248.6–270.3). The hand-built ballpark had drifted low. So the
correction moves the ceiling **down** in the crisis window and **up** nearly everywhere else — both
toward the published source, both R13 baseline corrections measured blind to P&L. **Published financial
figures will move on the next full run; that is the correction landing, not a regression.**

**Worth carrying: "two sources agreeing" is not corroboration.** The DISCOVER cited
`pricecaprates.co.uk` for the cap schedule, and a second aggregator agrees with it — but *both* carry
wrong effective dates (1 Jul 2019 / 1 Feb 2021 for changes Ofgem dates to 1 Apr 2019 / 1 Apr 2021) and
both omit two whole cap levels. They agree because they share a lineage, not because they are
independent. The build sourced the window boundaries from **Ofgem's own enumeration** instead. This is
the same shape as the TAUTOLOGY pattern R15 names, one level up: independence has to be checked, not
inferred from the count of sources.

**Second consecutive atom whose closed DISCOVER doc contained build-blocking errors** (`SP2_1` had a
caller undercount and a backwards interval; this one had a missing binding site, a bad primary source,
and an understated impact). Three errors, three kinds. **A closed DISCOVER doc is a hypothesis, not a
specification** — the remaining 10 Class B items have had no more scrutiny than these two had.

**Still open, unchanged by this tick:** the **10** remaining Class B BUILD halves; `SP2_1` Pass 2
(migrate the 25 callers); `W3_1b`'s own L3 residual (the coupled-triad population-level gap needs a full
sim run, which a bounded tick does not take); the `_PRICE_CAP_QUARTERLY` calendar-quarter offset
(registered as debt on `W3_1`, out of this atom's scope); the auto-processor broad-`add` finding.

---
## PROGRESS 2026-08-03 (worker tick) — C14 drawn from self-refill, and a prior tick's build was found half-landed

This tick's draw was the self-refill atom **`C14_thermal_parameter_inference`** (the COMPANY leg of the
fabric coupled triad), not a Class B item. **L0→L2**, recorded in `gate_authorizations.jsonl`.
`company/pricing/thermal_inference.py` + its suite: 44 pass + 1 strict-xfail; epistemic_verifier PASS.

**Three fail-opens found by MEASURING rather than by review**, each now a control with a mutation proof:
the reported confidence barely moved between daily and monthly reads while the error grew from 0.2% to
18%; a flat assumed SCOP put a heat pump 55% out with no widening; and a **summer-only read history
passed the degree-day span test**, extrapolating winter fabric loss from July hot water, because the
searched balance point drifts up to 18 C. Stating the uncertainty honestly then *improved* the estimates
(monthly 18.4% → 7.5%), because the shrinkage weights became right — worth carrying: a fail-open in an
UNCERTAINTY model is not merely cosmetic, it corrupts the estimate that consumes it.

**A negative result was recorded rather than tuned away.** The lag-based thermal-response estimate does
not recover fabric-mass ordering (pre-1919 solid wall 13.3h vs post-2000 flat 21.8h — backwards). It is
pinned as a **strict xfail** so an estimator improvement FAILS and forces the docstring claim to be
corrected, rather than the claim being silently outgrown.

**PROCESS FINDING 3 — a prior tick's build was left half-landed, and only building on it revealed it.**
`observed with evidence`: `simulation/premise_trace.py` and `tests/simulation/test_premise_trace.py` were
`git add`-ed but never committed, and `simulation/fabric_physics.py` carried an uncommitted deliberate
fail-loud change (`reconstruct_ambient_profile` lost its silent `DEFAULT_LATITUDE_DEG` fallback). The
production callers were updated; the **committed test file was not**, so `tests/simulation/test_fabric_physics.py`
had 9 failures sitting in the working tree. The W1_12 map cell already claimed L2. Landing C14 was
blocked by it (C14's harness leg imports `simulation.premise_trace`), so the 7 call sites were fixed and
the whole set landed together. **The map cell said L2 while the build was uncommitted and its sibling
suite was red** — same class as the stale-cells finding above, one step earlier: a level recorded before
its build was actually *landed*, not merely before it was verified.

---

**Recommended fix, not yet built:** when `process_run_complete.py` successfully publishes marker N, it
should archive every *older* marker to `done/` as SUPERSEDED-BY-N in the same commit — they describe runs
whose output the newer publish already contains. That converts an unbounded queue into a bounded one and
restores the doorbell's signal value. Registered here as a finding; it is the second recorded defect in
`process_run_complete.py`'s staging handling, alongside the broad-`add` sweep above. **Two findings on
one component is an R3 two-strike trigger** — the next touch should redesign its staging discipline
(stage own named paths; archive superseded markers) rather than patch a third time.

---
## PROGRESS 2026-08-03 (worker tick) — H_GAP drawn, and the build already on disk was measuring nothing

This tick's draw was the self-refill atom **`H_GAP_fabric_belief_truth_gap`** (the HARNESS leg of the
fabric triad), not a Class B item. Commit `8cfe10997`, pushed, origin verified. **L0→L2**, recorded in
`gate_authorizations.jsonl`.

**R7 paid off immediately: the build was already on disk, uncommitted.** `background/fabric_gap_ledger.py`
(1,600 lines) and `tests/harness/test_premise_two_level.py` (1,072 lines) were untracked in the working
tree from a prior tick — 77 pass + 2 strict xfail, landed RED against the shipped demand path exactly as
the spec's birth condition requires. Rebuilding it would have been the waste; the job was to verify it,
find what it was missing, and land it. **Three defects, every one found by RUNNING it rather than reading
it:**

1. **THE ORPHAN TRANSITION.** `write_fabric_gap_entries` had **no production caller** — grep-verified, the
   only references were its own definition and its unit test. The fabric gap existed as a *function* and
   never as a *number*. This is the **second** recorded instance of that exact shape
   (`generate_evidence_data.generate()` before it), so it is a **class, not an accident**: a measurement
   function reads as "done" to a reviewer the moment its test is green, and nothing about a green test says
   anyone runs it. `tools/couple_fabric.py` (+ 14 tests) is the caller it never had.
2. **A WRONG ATOM ID.** `FABRIC_WORLD_ATOM` was `"W1_11_premise_fabric_physics"` — which has **never been
   an atom**; the real id is `W1_11_fabric_physics_core`. Nothing would have failed: `write_gap_entry`
   writes any key it is given, and the Proof door derives its *rows* from the map. The write would have
   "succeeded" every run and rendered **nowhere, forever**. Now pinned by a test.
3. **A FAIL-OPEN IN THE COUPLED-TRIAD GATE ITSELF.** `build_coupling()` **derives** `W1_12->C14` from
   C14's own `depends_on`, but assembles the final coupling from `_AUTHORITATIVE_COUPLING` **alone** — so a
   derived-but-unregistered pair is **silently dropped**. `W1_12` sat at L2 as a coupled world atom with no
   measured gap while the Proof panel's own D1 detector ("depth nobody copes with") stayed blind to it and
   `world_l3_blocked` never fired. **The table reads like a cross-check and behaves like a whitelist.**
   Both fabric pairs registered; Proof door `pair_count` 10 → 12, measured 12, unmeasured 0.

### The measured result, recorded and deliberately not tuned (R12)

EPC-vs-actual gap **0.2049**, inferred-vs-actual **0.2397** — C14's posterior is a **worse point estimate**
than the register prior it started from. On the *same panel* the money consequence runs the other way:
deciding a fabric measure on the EPC belief misranks **10%** of premises (£162, 2.3 t CO2e/yr), on the
inferred belief it misranks **none**. They disagree because `prediction_gap` is a **level** statistic and
the decision is an **ordering** one: the register understates heat loss on every premise, C14 corrects
every one upward and overshoots on some, costing level accuracy and buying rank accuracy. **A
level-and-sum gap metric read alone would have called the company's own inference a regression while
hiding that it strictly improved every decision anyone would take on it.** That is this atom's founding
lesson — the control SET had a hole shaped like the defect — recurring one level up, in the gap metric
itself.

### The R15 finding worth carrying: a test that was itself a tautology

Five real **source** mutations, each firing its own named test with the others green. The fifth —
replacing the WORST-CELL selection with an average — initially fired **nothing**, because
`test_the_verdict_is_WORST_CELL_not_an_average` ended
`assert generated_worst(textures) == approx(min(textures))` with `generated_worst = min` defined three
lines below. `min(x) == min(x)`: it cannot fail, and it never called `evaluate_two_level` at all. **The
R15 TAUTOLOGY pattern, inside the test named for the rule, in a suite whose own docstring defends against
tautology** — and only mutating the source found it. Reading the file did not, twice. **A test that
asserts a helper against the same helper passes forever and the green count never blinks.**

**Still open, unchanged by this tick:** the remaining Class B BUILD halves; `SP2_1` Pass 2 (migrate the 25
callers); the auto-processor broad-`add` finding; the superseded-`run_complete`-marker queue. **New
residual on H_GAP:** it is L2 not L3 — panel-scale not population-scale, two cells unanchored (NEED:
SERL diversity, EPC-linked metered annual consumption), Expert Hour not attempted, and
`tools/couple_fabric.py` is **manual like all ten of its `couple_*.py` siblings**, so its ledger rows go
stale unless a tick re-runs it — *the same orphan-transition class this atom just closed one level up*,
registered rather than declared solved. R11 bound stated honestly: the Proof rows were verified in the
**generated** panel data, not on the live poesys.net pixel; that lands with the next publish.

---
## PROGRESS 2026-08-03 (worker tick) — W1_13 drawn as the BLOCKER of the drawn atom, and the envelope was the side that was wrong

The doorbell handed over `W1_11_fabric_physics_core` (level 2→3). Its L2→L3 step was held on a **named,
measured blocker** — `W1_13_high_tail_gas_anchor` — so the blocker *was* the feasible work (Rule 0: yield
dials until work exists; the blocker is not a reason to hold when it is itself drawable). **Network was
PROBED, not assumed**, and was available, which is what made the external DISCOVER drawable at all.

**`W1_13` L0→L2, commit `89103080d`, pushed, origin verified.** Full write-up:
`docs/market_research/need_domestic_gas_high_tail.md`.

### The verdict: the ENVELOPE moves, the fabric is FLAGGED not falsified
`RESI_CONSUMPTION_ENVELOPE_GAS.high` **40,000 → 50,000 kWh/yr**, anchored on DESNZ NEED 2026's own
domestic-gas validity threshold. **The justification does not depend on C4** — the old bound flagged
**1.02% of all gas-heated E&W homes and 14.1% of pre-1930 detached homes** as implausible. An
absurdity-catcher rejecting one in seven of a real, common dwelling class had to move regardless of what
the fabric model produced.

### Three method points worth carrying to the remaining Class B items
1. **The metadata was the evidence, not the tables.** Two facts nobody would have guessed decided this:
   `PROP_AGE_BAND 1` is *"before 1930"*, not pre-1919 (so the measured tail is an UNDER-estimate of the
   true pre-1919 solid-wall tail — recorded because the bias runs *against* the conclusion), and the data
   is **right-censored at 50,000** because DESNZ removes larger readings. That censoring fact turned out
   to be the whole answer: it hands you the publisher's own threshold for domestic absurdity, which is the
   same *kind* of object as the invariant being judged. Reading the tables without the metadata would have
   produced confidently wrong percentiles computed on a retained subset.
2. **Two artefacts from one publisher is still ONE source.** The record-level sample was cross-checked
   against the published aggregate before use — but that validates the **sampling**, not the source, and is
   recorded as such. The prior lesson (*agreeing sources may share lineage*) applies to a publisher's own
   two files just as much as to two aggregator websites.
3. **State the R12 counterfactual when the ordering invites suspicion.** Moving a band right after a
   measurement breached it looks exactly like goal-seeking. The defence has to be a counterfactual, not a
   protest: *had C4 come in at 55,000, this anchor would not have covered it and the physics would have
   been the side that moved.* The anchor was chosen by what it **is**, not by what it clears.

### Two findings registered, neither fixed on sight (SELF_INTERRUPT_DISCIPLINE — machine not blocked)
- **The bound is the wrong SHAPE, not merely the wrong value.** 43 MWh/yr is unremarkable for a pre-1919
  detached and would be a screaming defect on a 2-bed post-2000 flat. A single national scalar was
  simultaneously too tight for old detached stock (14.1% false positives) and far too loose for a modern
  flat, where the same reading is ~4× the class median and passes silently. **Widening it to 50,000 fixes
  the first problem and makes the second slightly worse** — said plainly rather than left to be discovered.
  The right shape is a class-conditioned envelope keyed on dwelling type/age/floor area, and the published
  distribution needed to build it is now in the anchor doc.
- **THIRD instance of the orphan-transition class**, and this one corrects a claim in `W1_11`'s own cell:
  the note asserting `tools/fabric_settlement_gap.py` "is its production caller and writes the artefact
  each run" is **false on both halves** — grep finds no caller anywhere outside its own module/test/prose,
  and it writes only under `--write`. **Caught by verifying rather than trusting the note:** after the
  envelope move the tool *printed* every premise inside the envelope while the artefact on disk still read
  `[1500, 40000]` and `inside_envelope_gas: false` — the artefact this atom's blocker rested on was stale.
  Joins `generate_evidence_data.generate()` and `write_fabric_gap_entries`. The durable fix is one
  reconciliation running the measurement tools with `--write` from the publish path, designed once for the
  whole `couple_*`/gap-tool family rather than patched per tool.

### Control-set hole closed en route
`RESI_CONSUMPTION_ENVELOPE_GAS` had **no test of its own** — the one test named for the envelope class
exercises only the *electricity* invariant, so the gas bound could have been any number at all and the
suite would have stayed green. R15 both ways: three real source mutations, each firing its own named test,
baseline restored green.

**NEXT TICK'S DRAW, named:** `W1_11`'s settlement switch is now **unblocked and drawable** — throw it, run
the full sim, measure the population-level belief-vs-truth gap through `H_GAP`, and only then claim L3.
Expect published financial figures to move; that is the R13 baseline correction landing, not a regression.

**Still open, unchanged by this tick:** the remaining Class B BUILD halves; `SP2_1` Pass 2 (migrate the 25
callers); the auto-processor broad-`add` finding; the superseded-`run_complete`-marker queue.
