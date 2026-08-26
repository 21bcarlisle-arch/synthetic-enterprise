# The 436-file divergence, walked

**Written:** 2026-08-26, delivery-lane tick. **Claim:** `the-uncommitted-disease`.
All claims `observed-with-evidence` unless labelled `inferred` (R9).

Opening state, `python3 -m background.tree_divergence`:

```
436 source file(s) vs HEAD, oldest 156.3h (7 attributed, 429 unattributed)
BREACH: 436 source files diverge from HEAD (threshold 15)
BREACH: the oldest has sat 156.3h (threshold 4.0h): tests/simulation/test_policy_cost_coverage.py
```

29x the file line, 39x the age line. Named correctly in the daily digest for six days
and absorbed every time. This is the walk, by group, so the count falling means
something. **A sweep that makes the count fall without anyone reading the files is the
same defect wearing a smaller number**, so every group below says what it was and what
was decided.

---

## 1. What the 436 actually were

| Group | Files | Disposition |
|-------|-------|-------------|
| `docs/staging/` archive backlog | 419 | **LANDED** by a concurrent lane as `2766c8ca2` mid-walk |
| `docs/observability/` machine-written state | ~89 tracked churn | Runtime state, excluded from the measure by `_is_generated`/`_is_runtime_state`; not part of the 436 |
| Control repairs, finished, tested | 10 | **LANDED** (§2) |
| Test-first work whose subject was never built | 1 | **SUBJECT BUILT** (§3) |
| The escalation change itself | 3 | **LANDED** (§4) |
| Design/DISCOVER docs | 2 | 1 **LANDED**; 1 **OWED**, refused by a control — §6a |

**The dominant group had a single cause, and it was a control.** 419 of the 436 were
`docs/staging/` documents waiting to be archived. They could not be archived because
`tools/landed_manifest_check.py` refused every commit touching `docs/staging`: two
documents honestly mention a `/tmp/.../scratchpad/land.sh` wrapper in backticks,
`is_path_like` called that a repo path, `git ls-tree` answered rc=128, and the checker
raised. A second defect in the same file billed
`DIRECTOR_CONSOLE_2026-08-26.md` for a quoted line reading
"`tests/simulation/test_policy_cost_coverage.py` remains uncommitted" — **the opposite
of a landing claim** — because a document with no `##` heading had its whole body
treated as the header block.

So the backlog was not 419 lanes failing to tidy up. It was one control, wrong in two
ways, refusing the commit that would have cleared it — every day, for six days, while
the divergence alarm counted the result and blamed the tree.

Landed by a concurrent lane as `2766c8ca2` while this tick's gate was running. Adopted,
not rebuilt.

---

## 2. Control repairs — landed

Four defects, all of the shape "the control still reported, but not the thing it claimed":

- **`surgical_land._verdict_excerpt`** sized the stderr budget off stdout's *length*, so
  a gate that printed one **passing** tick before dying collapsed the diagnostic to 45
  characters and truncated the block naming the real refusal. The more checks a gate
  cleared, the less of its failure a reader saw.
- **`abolished_block_classes._load_atoms`** read the maturity map with `yaml.safe_load`
  while the publisher reads it through `map_store.load_atoms` — 74 atoms scanned against
  the published 298. A quarter of the register's dead-rule exposure, reported as the whole.
- **`sanity_adjudication`** raised `KeyError` on a hand-written ledger row with no
  `state`, felling the daily sanity digest — the mechanism that would otherwise have
  reported it. The failure silenced its own alarm.
- **`landed_manifest_check`** — §1, landed by the concurrent lane.

`CLAUDE.md` and `PRIORITIES.md` carried two stale facts (the binding memory figure is the
WSL2 guest's and it moved on 2026-08-24; `three_horizon_clv.py` was renamed
`commitment_actual_forecast.py` on 2026-08-19). Landed with them.

---

## 3. The named oldest — decided, not deferred a seventh day

`tests/simulation/test_policy_cost_coverage.py`, 158h old, 1 passing and 6 failing.
The instruction was to build the subject or delete the tests. **Built** — and the reason
is that the premise turned out to be half wrong:

- The SIM half **already existed and was already wired**.
  `simulation.policy_costs.coverage_report` was built 2026-08-14 and
  `run_phase4c_on_phase2b` has emitted `policy_cost_coverage` in the run output ever
  since. The renderer half was never written, so the whole apparatus resolved to a key
  nothing read. Twelve days of a measurement nobody could reach.
- **Two of the six failures were the tests asserting the model stays bad.**
  `_RO_COST_BY_OY_START`, `_CCL_ELECTRICITY_RATE_BY_YEAR` and `_GAS_CCL_RATE_BY_YEAR`
  have been extended to 2025 since 2026-08-14, so 10 tables clamp in April rather than
  13. The tests froze a census; three tables getting their real rates is the defect being
  *fixed*. Re-aimed at the invariant (the apr_mar/calendar basis split, derived on both
  sides) rather than the count, and the mutation test's subject is now **chosen** from the
  tables that still stop short so it cannot expire again.

Built: `saas/reporting/annual_report._extrapolation_note`, wired under the policy-cost
table, with `policy_cost_coverage` carried through `extract_report_data`. Every count,
date and table name is derived from the block the SIM hands over — extending a table
moves the note, extending every table deletes it. `saas/` still does not import
`simulation/`; the test that pins that **parses** the imports rather than grepping them.

Rendered output, against the live tables:

> Of the 13 year-keyed policy and network rate tables behind these figures, **13 of 13**
> serve at least one date in the reported window (2016-01-31 to 2025-06-07) from outside
> their own tabulated coverage. […] **not a claim that the carried-forward rates are wrong**

That is £391,531.72 of published 2025 policy stack — 8.09% of the total — which until now
was published as though every rate behind it was tabulated. 10 of 10 tests pass.

---

## 4. Why a breach this size was absorbed — and what now stops it

`background/tree_divergence.py` is report-only by deliberate design, and **that design is
right**: the publish gate's subject is a clean HEAD checkout precisely so one lane's
uncommitted work cannot halt publishing. The defect was never the report-only half.

The defect is that report-only had come to mean *one line in a batched digest*, and
`process_run_complete._publish_tree_divergence` chose that digest on **category alone**
(G-N3 lists "divergence" as batchable). So 436 files at 29x the line read exactly like
three files at 1.2x.

**A control that fires and cannot be heard is the same family as a control that cannot
fire** — in both cases the reader learns nothing from the alarm's presence.

The repair is not a louder alarm for everything; that re-teaches the same skimming habit
one volume up. Magnitude is now part of the **routing** decision:

- `tree_divergence.severity()` — pure, returns the multiple over each threshold.
- Past `ESCALATION_MULTIPLE` (5x), the notify leaves the digest (`topic_class=None`,
  which `notification_digest.is_instant` treats as instant) and carries the multiple in
  its headline. An **unmeasurable** tree is severe too — the one state where the reader
  most needs to hear something is the state a fail-open swallows.
- Ordinary breaches stay batched. The transition/re-escalate contract is untouched, so a
  standing severe squat still pages once a day, not every cycle.

**R15, mutation-proven both ways.** Reverting the routing to the unconditional
`topic_class=DIVERGENCE` reds exactly one test —
`test_a_severe_breach_leaves_the_digest_and_arrives_as_itself` — while all six
severity-*grading* tests stay green. That gap is the defect itself: the grading was never
the missing piece, the routing was. `test_an_ordinary_breach_still_goes_to_the_digest`
pins the other side, so deleting the severe branch entirely also fails. 27 tests pass.

---

## 5. The salvage branches — dispositioned, and the premise was wrong

The instruction described "47 remote refs, mostly worktree-agent and salvage". **Observed:
`git ls-remote --heads origin` returns exactly one ref, `refs/heads/main`.** The remote
refs are already gone. What exists is **13 local** `worktree-agent-*` branches, 11 of them
salvage commits from a single 2026-08-03T13:26 sweep.

"Delete the rest" was the expected disposition. **The evidence does not support it**, so
it has not been done. Comparing each branch's salvage commit against `main` file-by-file:

| Branch | Date | Stranded — present on the branch, absent from `main` |
|--------|------|------------------------------------------------------|
| `a0ce4733` | 08-03 | `site/evidence/` (3), `site/shadow/` (5), `tools/moap_evidence.py` + test, `site/data/moap_evidence.json` |
| `a8181339` | 08-03 | `site/evidence/` **7 pages** (`the_world`, `the_wall`, `the_score`, `the_company`, `the_households`, `governance_method`, index), `tools/generate_evidence_pages.py`, `tools/moap_evidence_gate.py` + test |
| `a8661079` | 08-03 | `site/evidence/` (3), `site/moap_evidence.py` + 2 tests, `tools/generate_moap_evidence_data.py` |
| `a878c7c0` | 08-03 | `site/company/index.html` + door test, `site/shadow/` (5), `site/_home_render_harness.mjs` |
| `a6ad9f2b` | 08-03 | `site/shadow/` (5) |
| `ae5594bc` | 08-03 | `site/company/_render_harness.mjs` and siblings |
| `a860ccd6` | 08-03 | `background/console_rescue_detector.py` + test, `advisor_restart_ruling_detector.py`, `origin_freeze_detector.py` |
| `a28e560d` | 08-03 | `tools/build_population_value_frontier.py` |
| `a84b7d9b` | 08-03 | `tests/sim/test_merit_order_price_wiring.py` |
| `a3faa0ac` | 08-03 | `regulation_commons/` (5) + 2 tests — **superseded**: rehomed to `company/compliance/working_days.py`, which is in `main`. Plus 4 `.tmp_*` scratch files. |
| `a416449f` | 07-30 | **nothing absent from main** — the SITE_EH1 rescue landed |
| `a7e53b3f` | 08-18 | **nothing absent from main** — live worktree, 2-line change |

**`site/evidence/` is seven built pages, a generator, a gate and three test files, on three
different branches, none of it in `main`.** That is not residue. Deleting those branches
would destroy the only copy.

Two branches (`a416449f`, `a7e53b3f`) are confirmed fully superseded; `a3faa0ac`'s
substantive half is confirmed rehomed. **Deletion of those three is safe and is the only
deletion this walk authorises.** It has been left undone in this tick rather than done
carelessly, because `a7e53b3f` is a **live** worktree (`git worktree list` shows it
checked out) and deleting a checked-out branch is the kind of tidy that makes the next
alarm.

**What is owed, named rather than swept:** an adopt-or-discard decision on `site/evidence/`
and `site/shadow/`. `inferred` — these look like an abandoned page programme rather than
lost work, but nothing in `main` records that decision, and "it looks abandoned" is
exactly the reasoning that loses a build. That decision is authoring, not tidying, and it
does not belong in a divergence sweep.

---

## 6a. One file was refused, and the refusal was right

`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml` (158.9h, the oldest
non-`PRIORITIES.md` item) was in this walk's pathspec as finished work. The gate refused
it:

```
[test-gate] ❌ A STORE RECORD CLAIMS A LANDING THIS COMMIT'S TREE DOES NOT CARRY
  - the record asserts a landing in prose and states no falsifiable claim.
[test-gate] Five consecutive EP6 passes wrote this claim and no tree ever held the code.
```

**Dropped from the pathspec rather than argued with.** The yaml is the KNIFE lane's step-51
rewrite of its own stale-doorbell notice, and the fix the control asks for — a
`LANDED: <symbol> in <path/prefix>` line — is a claim about what that lane built. Writing
one to clear a red would be this walk authoring another lane's landing record, which is the
precise failure the control exists to catch. It stays uncommitted and is named here as owed,
which is the honest disposition: it is not residue, and it is not mine to certify.

Worth recording that the refusal was *legible at all*. It arrived as a quoted verdict
naming the file and the remedy — which is `surgical_land._verdict_excerpt` (§2) working on
its first real refusal after being repaired in this same walk. Before the fix, the gate's
single passing tick would have collapsed the stderr budget and truncated that block to a
fragment.

---

## 6b. The tree was already red, and the gate could not see it

Landing this walk surfaced a second wedge that had nothing to do with it: **four tests
were failing at `HEAD` in a pristine `git worktree`**, and had been since `fb8a8fda5`,
three commits earlier. Three lanes committed over the top of it.

They stayed invisible because **the pre-commit gate selects test files by filename
stem**, and no commit since `fb8a8fda5` touched a stem that reaches them. They became
this walk's problem only because its pathspec is wide enough that `select_targets()`
pulls them in — 148 files. A red tree that only blocks the lane with the widest pathspec
is a red tree nobody is accountable for.

Both causes were director-ordered changes working correctly, with tests still asserting
the world as it stood before them:

- `test_generate_dashboard_data_population_seam` asserted
  `_resolve_book() == list(CUSTOMERS)`. Since the **2026-08-24 I&C suspension**,
  `live_population` filters the roster through `served_segments()` first — 13 of 18
  accounts are served. The test demanded the book carry five accounts the director had
  suspended. Re-aimed at the served roster, derived from the same predicate, **plus a new
  independence leg** (`test_the_suspension_is_actually_biting_on_this_roster`) so the
  suite cannot silently go back to measuring the whole literal if the filter becomes a
  no-op.
- `test_net_new_acquisition` held `CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG = 1295`. Re-measured
  on this test's own written instruction: **1,115 quotes, £135,285**, moved by the I&C
  suspension and by `fb8a8fda5` fixing the electricity-only funnel. Its window test
  asserted every quote falls inside the reported period — true only while the campaign's
  schedule and the report's period happened to end together. The schedule now runs to
  2025-07-20 against a `REPORT_END` of 2025-06-07, so 49 quotes sit past the last day the
  accounts cover.

That last one deserves its own sentence, because it would have been easy to call a
dropped-spend defect. **It is not.** Every one of the 1,066 quotes inside the period *is*
booked (`events == inside`, exactly). A quote dated 2025-07-20 has not happened yet in
the reported world, and booking it would put £6,000 of cost in a period the ledger does
not report. The filter is right; the assertion had frozen a coincidence. It now states
what it means — nothing before or within the period is dropped, the excluded set is
exactly the post-period tail — and it keeps a **non-vacuity bound**: if that tail ever
exceeds 10% of the campaign it reds, because at that point "outside the period" really
would be the excuse the original assertion was written to catch.

---

## 7. Closing state

```
tree divergence: 22 source file(s) vs HEAD, oldest 158.9h
```

436 → 22, and every one of the 414 is accounted for above by a group that was read. The
remaining 22 are this tick's own work plus two design docs, landing with this record.

Still breaching on both axes at the moment of writing, because this record and its
commits are themselves uncommitted divergence until the gate returns. That is the honest
state, and under §4 it is now the kind of breach that stays in the digest — which is what
the ordinary case is supposed to look like.
