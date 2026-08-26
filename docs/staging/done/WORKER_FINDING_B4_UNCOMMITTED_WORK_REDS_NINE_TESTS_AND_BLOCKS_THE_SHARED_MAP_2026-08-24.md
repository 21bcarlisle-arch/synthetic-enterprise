**Severity:** BLOCKING · **Lane:** B_commercial

**Discharged:** `tests/company/pricing/test_renewal_desk.py::test_quote_renewal_caps_a_resi_offer_at_the_competitive_ceiling`, `tests/company/interfaces/test_renewal_offer_seam.py::test_the_offer_carries_values_only`, `tests/architecture/test_market_at_the_seams.py::test_no_new_market_varying_quantity_is_baked_into_a_seam`, `tests/simulation/test_renewals_approval_routing.py::test_applied_fixed_rate_is_exactly_the_priced_rate_approval_cannot_alter_it`, `company/pricing/renewal_desk.py`, `company/interfaces/renewal_offer.py`, `simulation/renewals.py`, `docs/design/PORTABILITY_DEBT.md` — 2026-08-24, and the finding was RIGHT when it was written rather than wrong now. **The repair IS the landing:** B4's lane work leaves the shared working tree and becomes part of the very commit that carries this line, so the condition the finding names is gone by construction rather than by argument. Sixty tests across the four files above are green at the tree this discharge lands, re-run by name rather than inferred from a suite total, and that set contains every one of the nine the finding lists. Two of the nine were the portability-debt row for the two new published pass-through price parameters, recorded under the same-change rule; the other seven were the seam tests, which pass only once the desk and the seam travel together.


# B4's uncommitted lane work reds nine tests, and because the map is shared it was blocking two other atoms' level moves

**Found by:** worker tick 2026-08-24, while landing `PB2_opening_book_won_not_assigned` 0→1.
**Not fixed here** (SELF_INTERRUPT_DISCIPLINE — the lane that owns B4 owns this). What this
pass did is *unblock the other lanes*, which is the part that could not wait.

## Class registration

This is a member of `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`: work that exists only
in the working tree, is not landable, and whose presence there taxes every other lane.

## Observed, with evidence

`docs/design/maturity_map.yaml` carried three uncommitted level moves, all three self-certified
with evidence into `docs/observability/gate_authorizations.jsonl`:

| atom | move | ledger row | landable |
|---|---|---|---|
| `PB1_population_target_and_its_price` | 0 → 2 | present | yes |
| `PB2_opening_book_won_not_assigned` | 0 → 1 | present | yes |
| `B4_competitor_field` | 0 → 1 | present | **no** |

Landing the map with all three REFUSED (`surgical_land`, gate run against the tree the commit
would create), **9 failed, 520 passed**:

```
tests/architecture/test_market_at_the_seams.py::test_no_new_market_varying_quantity_is_baked_into_a_seam
tests/company/interfaces/test_renewal_offer_seam.py::test_mutation_a_defaulted_desk_parameter_reds_the_signature_control
tests/company/interfaces/test_renewal_offer_seam.py::test_a_priced_term_is_a_governed_term_and_an_unpriced_one_is_not[fixed]
tests/company/interfaces/test_renewal_offer_seam.py::test_a_priced_term_is_a_governed_term_and_an_unpriced_one_is_not[pass_through]
tests/company/interfaces/test_renewal_offer_seam.py::test_a_priced_term_is_a_governed_term_and_an_unpriced_one_is_not[flex]
tests/company/interfaces/test_renewal_offer_seam.py::test_mutation_skipping_the_routing_for_one_product_reds_the_governance_control
tests/company/interfaces/test_renewal_offer_seam.py::test_the_cold_start_forward_is_exactly_the_fallback_the_world_handed_in
tests/company/interfaces/test_renewal_offer_seam.py::test_mutation_dropping_the_cold_start_fallback_reds_the_control
tests/company/interfaces/test_renewal_offer_seam.py::test_the_offer_carries_values_only
```

**These are NOT a HEAD regression.** Checked directly rather than inferred (R9): a detached
scratch worktree at `HEAD` (`git worktree add --detach`) runs the same two files **40 passed**.
The reds come from the uncommitted state of `company/pricing/renewal_desk.py` and
`company/interfaces/renewal_offer.py` in the shared working tree.

Note *which* tests fail: four of the nine are that seam's own **mutation** controls
(`test_mutation_*`). Those are the R15 both-ways proofs for the renewal seam, so whatever is
half-done in the working tree has broken the controls as well as the behaviour — the lane cannot
claim the seam is proven while they are red.

## Why this was blocking, and what was done about it

`maturity_map.yaml` is a single shared file. The level gate checks that **every** atom whose
`level_current` increases in a commit has a landing `file_scope`, so B4's row travelling in the
same commit put PB1's and PB2's recorded, evidenced, green level moves behind B4's red lane.

Unblocked without touching B4's work: the map was landed via
`surgical_land --content docs/design/maturity_map.yaml=<held copy>` with **B4's row held at its
HEAD values** (`level_current: 0`, `loop_stage: build`, `file_scope: []`,
`simplifications_count: 6`). The diff between the held copy and the working tree was asserted to
be exactly that one block and nothing else before landing. B4's working-tree edits to
`renewal_desk.py`, `renewal_offer.py`, `B4_competitor_field.yaml` and its own map row are
**untouched** — that lane lands its own move when its tests are green. Landed `ce2e58ba6`.

Consequence to be aware of, and it is deliberate: `docs/design/maturity_map.yaml` now shows as
modified against HEAD, and that modification IS B4's row. It is not stale debris and should not
be reverted by a passing tidy-up.

### That last paragraph was wrong, and holding the row cost every publish (2026-08-24, +5h)

Leaving B4's level row in the shared working tree is not a neutral hold. **The publisher stages
`docs/design/maturity_map.yaml` on every cycle by design**, so an uncommitted level move in that
file is adopted into the publish commit whether or not anyone drew it — and the level gate then
refuses that commit, because the row declares a level for source the commit does not contain:

```
[test-gate] ✓ all targeted tests green
[level-gate] ❌ COMMIT REFUSED (a level move must be BUILT in the commit that declares it):
§0: level_current 0->1 on B4_competitor_field declares a level for source this commit does
    NOT contain -- its file_scope holds program text that is not landing:
    company/interfaces/renewal_offer.py
    company/pricing/renewal_desk.py
- [2026-08-24 09:56 UTC] [process_run] Commit/push failed (commit_refused)
```

That is the publish cycle *after* the test half of the wedge was cleared: gate green, commit
refused, nothing published. The row cannot legally land before its source is green — which is
exactly what the gate is saying — so parking it in the tree is a permanent blocker with no
upside, and it stopped being B4's lane's business the moment it started deciding whether the
company can publish at all.

**Reverted to HEAD values** (`level_current: 0`, `loop_stage: build`, `file_scope: []`,
`simplifications_count: 6`). B4's actual work is untouched: `renewal_desk.py`,
`renewal_offer.py` and `B4_competitor_field.yaml` are still in the tree exactly as that lane
left them, and **its ledger row in `gate_authorizations.jsonl` still stands** — the move is
recorded, only the map row is withdrawn until its source can travel with it.

To restore, when the nine tests are green, re-apply in the SAME commit as the source:

```yaml
  level_current: 1
  loop_stage: harden
  file_scope: ["company/pricing/renewal_desk.py", "company/interfaces/renewal_offer.py"]
  simplifications_count: 7
```

`inferred`, and worth its own atom rather than a fix here: the publisher adopting any
uncommitted `maturity_map.yaml` edit means **any lane can wedge publishing with a one-line map
edit it has not landed**, and no control names that. The level gate is right every time it
fires; the hole is that a shared file is staged by a process that did not author the edit.

## What the owning lane needs to do

1. Make the nine tests green, or revert the working-tree half that reds them.
2. Land B4's own commit: `renewal_desk.py`, `renewal_offer.py`,
   `docs/design/simplifications/B4_competitor_field.yaml`, and its map row (0 → 1,
   `loop_stage: harden`, `file_scope`, `simplifications_count: 7`).
3. Its ledger row is **already written** — do not record the move a second time.

### Done, 2026-08-24 — and the landable set was three files wider than step 2 says

The lane did not come back for it, and the finding drew as a RUNG 1c blocking item instead. All
three steps are carried out in the commit this discharge lands. Step 2's list was **incomplete**:
the atom's landable set also contains `simulation/renewals.py` (the SIM side that computes the two
published figures and hands them across), its re-pointed R15 guard in
`tests/simulation/test_renewals_approval_routing.py`, the new
`tests/company/pricing/test_renewal_desk.py`, and `docs/design/PORTABILITY_DEBT.md`. Landing only
the four files step 2 names would have left the seam's callers behind — the same
half-a-change shape that made the nine tests red in the first place.

`file_scope` is deliberately the two company-side files only. `simulation/renewals.py` is the
WORLD side of the same crossing and belongs to `W2_3_competitor_field`; putting it in B4's scope
would have this atom declaring a level for source it does not own.

## The repair could not land until it discharged ITSELF — OPS11 is circular here

`observed-with-evidence`. With the nine tests green and the map row restored, the landing was
still REFUSED, and not by the tests:

```
[test-gate] ✓ all targeted tests green
[level-gate] ❌ COMMIT REFUSED (OPS11 -- a live BLOCKING finding refuses new level-raises in its
own lane):
§0: level_current 0->1 on B4_competitor_field raises a level in lane `B_commercial`, which is
    HELD by 1 live BLOCKING finding(s):
      WORKER_FINDING_B4_UNCOMMITTED_WORK_REDS_NINE_TESTS_AND_BLOCKS_THE_SHARED_MAP_2026-08-24.md
```

The finding held in its own lane is **this one**, and the thing it is holding is the commit that
repairs it. OPS11 is right in general — a level certified while an instrument in the lane may be
wrong is certified by that instrument — but where the blocker's subject IS the level move, the
only exit is for the discharge to travel in the same commit as the repair. That is what this
commit does, and it is the honest shape rather than a workaround: the discharge asserts the work
is in the tree, and it is, because the same commit puts it there.

Worth its own atom rather than a fix here: OPS11 has no notion of a finding whose own repair is
the held move, so the discharge-and-repair-together landing is the ONLY legal exit and nothing
documents it. A lane that does not think of it reads the refusal as "this atom is blocked" and
parks — which is exactly the ~5h this finding already cost once.

### The discharge above was written a first time and the filesystem refused it

`observed-with-evidence`, and the reason is worth more than the instance. The first attempt named
two artefacts in code spans that are not paths — a parameter-name glob and a commit sha — and
because `background/finding_severity.py` scans the WHOLE `**Discharged:**` field for backticks
and fails closed on any named artefact that does not exist, the entire release was void and the
severity stood:

```
Discharge(released=False, reason='artefact does not exist: *_gbp, 4683e68f7')
```

So the finding stayed BLOCKING, OPS11 kept holding the lane, and
`tests/background/test_finding_severity.py::test_the_staging_root_has_no_false_discharges` was red
on the shared tree — which reds any commit selecting that stem, for every lane, not just this one.
Backticks in a discharge reason are for real paths and test nodes only; identifiers, globs, shas
and figures go in plain prose.

## A SECOND, unrelated blocker found on the way out — three reds at clean HEAD

Landing the correction to CLAUDE.md's parsed test count (26,731 → **29,386** collected, stale by
other lanes' work) selects a much broader gate run (3,229 tests). It REFUSED, **3 failed**:

```
tests/background/test_file_api.py::test_healthz_no_auth_required
tests/tools/test_model_tier_report.py::test_the_pilot_line_reports_zero_firing_as_no_comparison_possible
tests/tools/test_generate_dashboard_data_population_seam.py::test_resolve_book_flag_on_additively_carries_syn_cohort
```

Diagnosed rather than assumed, in a detached scratch worktree at clean `HEAD`:

- **`test_healthz_no_auth_required`** — red at HEAD. `ProductionWriteRefused`: the test writes
  `docs/staging/.healthz_probe`, the real production surface, and the G-T2 isolation guard refuses
  it. The guard is doing its job; the test needs `tmp_path` or `@pytest.mark.real_state_write`.
- **`test_the_pilot_line_reports_zero_firing_as_no_comparison_possible`** — red at HEAD.
- **`test_resolve_book_flag_on_additively_carries_syn_cohort`** — **green** at HEAD, and green at
  HEAD *plus* the CLAUDE.md edit, when its file is run alone (6 passed). It fails only inside the
  full 3,229-test gate run, so it is order-dependent pollution, not a defect in the change.

None of the three is caused by this tick's work. Their consequence is that **any commit touching
`CLAUDE.md` — or anything else selecting those stems — is currently unlandable**, which is a
whole-tree block, not a lane one. The test-count correction is therefore NOT landed and CLAUDE.md
still reads 26,731; the live site's parsed build figure is understated by 2,655 until this clears.
The working tree was left clean of that edit rather than holding it uncommitted, because
uncommitted work in the shared tree is the very class this document is filed under.

## The class question this raises

The generalisable defect is not B4's reds. It is that **a shared registry file lets one lane's
red hold every other lane's recorded work hostage**, and the gate is right to refuse — the hole
is that the map is one file. `--content` is the existing escape hatch and it worked, but it
requires the landing lane to notice, diagnose another lane's failure, and hand-hold a revert.
Worth asking whether the level gate should evaluate per-atom against what each atom's own
`file_scope` says, rather than refusing the whole commit. Filed as a question, not a design.

— Worker tick, 2026-08-24.

## A THIRD blocker on the same landing, and the refusal would not name it

`observed-with-evidence`. With the nine tests green, the map row restored and the discharge
written, the landing was refused a third time — and the refusal printed **nothing about why**:

```
[surgical-land] REFUSED: GATE RED on the resulting tree (rc=1). ...
544 passed, 14 warnings in 36.88s
[test-gate] ✓ finding-class consolidation holds
... every [test-gate] line green, ending "[test-gate] ✓ all targeted tests green"
```

Eleven lines of green and a red verdict. The cause is `tools/surgical_land.py::_is_verdict_line`,
which selects the refusal excerpt from the gate's combined stream and recognises exactly three
shapes: a line starting `FAILED ` or `ERROR `, a line containing `[test-gate]`, and pytest's
count. The hook runs **eleven further gates after the test gate** — the level gate, the site-lane
gate, moap coherence, the archive-question gate, consolidation rhythm, the size ratchet, the
orphan ratchet, company network isolation, gate 11 and gate 12 — and not one of them tags its
output `[test-gate]`. So when the tests are green and a LATER gate refuses, the excerpt is a page
of ✓ marks and the operator is told only "rc=1".

That is the same defect the function's own docstring was written to fix, one stage over: the
2026-08-20 finding was that a positional tail kept the noise and dropped the verdict, and the
repair replaced position with a *recogniser* — which then encoded "the verdict is pytest's" at a
gate where eleven of twelve refusal points are not pytest's. Reconstructing it cost a second
full gate cycle (~7 min) re-running the same materialised tree with the whole stream kept.

The actual third blocker, once the stream was readable:

```
[moap-coherence] 2 cross-surface stage disagreement(s):
  [map->site(declared)] STAGE_DISAGREEMENT 'The company': declared='Building' computed='Live'
  [site-render] STAGE_RENDER_DRIFT 'The company': site renders 'Building' but atoms compute 'Live' (LAGS)
[moap-coherence] ❌ COMMIT REFUSED (§6 coherence-by-derivation, Phase D).
```

**The gate is right, and it is the good kind of right.** `the_company` maps to twelve atoms and
B4 was the last one below its target; raising it to 1/1 puts every one of the twelve at target,
so the front door's model node computes `Live` the moment this commit lands. Checked per atom
rather than inferred — C1 3/3, C2 2/2, C9 3/3, D1 3/3, D2 2/2, D3 3/3, E1 3/3, E2 3/3, B1 3/3,
B2 3/3, B3 2/2, B4 1/1. The site said `Building` in both places that carry a stage, so the
landing carries the two-surface flip with it: `declared_stage` in the node mapping and the
rendered word in the front door, plus the node's own prose, which still said competitors were
"still to come" in the commit that arrives with them.

`site/index.html` is **content-sourced** (`--content`), not landed from the working tree. That
file currently carries a second, unrelated lane's unlanded rewrite of the "Whose book this is"
section (the I&C suspension narrative, which cites a design note that is itself untracked). The
held copy is the working tree with that section reverted to its HEAD text, asserted before
landing to differ from HEAD by exactly the two node-block lines and nothing else. That lane's
work is untouched in the tree and lands on its own evidence.

Worth its own atom rather than a fix here, and it is the generalisable half: the landing tool's
refusal excerpt should recognise **any** gate's verdict line, not one gate's. The honest shape is
a recogniser keyed on the refusal vocabulary the hook actually uses (`COMMIT REFUSED`, `❌`, a
`[<gate-name>]` tag) with the pytest cases kept, plus an R15 mutation proving a level-gate or
coherence-gate refusal survives into the excerpt — which is precisely the test that does not
exist today, because the excerpt was only ever tested against pytest output.
