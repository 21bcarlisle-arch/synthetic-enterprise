**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `declare-run-identity-on-every-promote-target`) · **Class:** `controls_that_cannot_fail`

# The run-identity definition now comes from the producer, and every target on disk answers "we cannot tell" until it next runs

**2026-09-09, scheduled tick, LANE 0 DELIVERY.** The drawn direction: *"Each of the four
promote-by-copy targets declares WHICH OF ITS FIELDS ARE ITS RUN IDENTITY, and
`promoted_artefact_claim_census._artefact_dates` reads only that declaration — returning nothing
for a target that declares nothing."* No exit test was written for it, so what follows is what I
decided done means, what I measured, and the one thing I decided NOT to do.

---

## 1. Five targets, not four

The direction named four producers. The tree has **five** promote-by-copy targets, because
`docs/observability/value_cycle_ab_s1_noise_floor.json` acquired dated siblings since the direction
was written. It is discovered rather than listed — which is the census working as designed — and it
is written by the same producer as the three-arm target, so it cost nothing extra.

## 2. What was measured before the change (2026-09-09, this tree)

```
targets 5   claims 14   STALE 2   ungradable 0   cannot_tell 0   feed 70
```

Not one of the five declared anything, and the census guessed identity by walking every shallow
scalar. What that guess actually returned:

| target | tokens | what they were |
|---|---|---|
| `run_output_latest.json` | 18 | **zero** are this run. `wholesale_credit_exposure.mark_date` 2025-06-07, `mc2_collateral_death_test.stressed_date` 2021-12-31, `clv_snapshot_as_of` 2016-12-31…2024-12-31 — **dates inside the simulated world** |
| `LATEST.json` | 8 | `snapshot_ts` (correct) **and** `agent_status.last_updated`, a folded-in artefact's clock |
| `live_decisions_latest.json` | 7 | `decision_run_at`, `portfolio_as_of` (both correct) **and** `market_as_of_date` 2026-09-08, a settlement date in the world |
| `three_arm.json` / `noise_floor.json` | 8 / 7 | correct, by luck of shape |

**Both STALE rows were accidents.** `tools/dd_opening_arms.py:1` cites "2026-09-01" about
`run_output_latest.json` and was refused because 2026-09-01 happens not to be among that artefact's
twelve simulation-world dates. Had the world's record contained it, the claim would have graded as
SUPPORTED against a collateral stress test. That is the leg being right for a reason that has
nothing to do with what it measures.

## 3. Why no consumer-side rule can fix it, and the one that was refuted

A field-NAME list was measured on 2026-09-09 and **is refuted**: the five producers name one fact
five ways — `generated_at`, `snapshot_ts`, `decision_run_at`, `refused_at`, `portfolio_as_of` — so a
list drawn from the first strips all 15 tokens from `LATEST.json` and `live_decisions_latest.json`
and silences grading that works today.

A DEPTH rule is refuted by the same measurement from the other end. `portfolio_as_of` is the
upstream portfolio artefact's own `generated_at` — a real-world stamp naming the input run this
decision consumed — and `wholesale_credit_exposure.mark_date` is a date in 2025 the company lived
through. **Same English, same depth, opposite populations.** Nothing on the census's side of the
seam can separate them, which is why the first repair's docstring recorded
`run_output_latest.json` going "to none" and that number was seventeen five days later with nothing
going red.

## 4. What landed

**The producers declare, in the artefact, under `run_identity_fields` — a list of dotted paths.**
Additive: every field named was already there, so no consumer of any of these five artefacts sees a
field move or change type.

| producer | declares |
|---|---|
| `tools/run_annual_report._run_identity_header` | `generated_at`, `producing_commit.commit`, `producing_commit.resolved_at`, `world_identity.digest` |
| `tools/run_value_cycle_ab` (three-arm, noise floor) | the same four, from one constant `_RUN_IDENTITY_FIELDS` |
| `tools/run_value_cycle_ab.floor_refusal_artefact` | `refused_at` in place of `generated_at` — a refusal is still a run and must still say which |
| `tools/generate_snapshot` | `snapshot_ts`, `snapshot_label` |
| `tools/run_live_decisions.run_decisions` | `decision_run_at`, `portfolio_as_of` |

**`_artefact_dates` reads that declaration and nothing else.** Absent, empty, or the wrong shape
all mean the same thing — no declaration — and the target routes to `ungradable_targets` /
`cannot_tell`. The census surface now prints each target's declaration beside it, or
`DECLARES NOTHING`.

**The asymmetry that stops this firing as a false red.** A *dated sibling* a reader pinned by name
is read WHOLE (`_tokens_anywhere_in`, the old shallow walk). Nothing is ever copied onto a dated
file, so there is no promotion hazard and no declaration is possible for artefacts written before
today; requiring one would have turned every pin to a 2026-09-08 artefact into a STALE row caused by
the control changing rather than the tree. `feed_claims` uses the same reader for the same reason.
**Measured: the feed leg is unchanged at 70 rows either side of the change** — the split moved
nothing it was not meant to move.

## 5. What I decided NOT to do, and the cost I am accepting

**After the change, all five targets are ungradable and the refusing leg refuses nothing today.**

```
targets 5   claims 14   STALE 0   ungradable 5   cannot_tell 6   feed 70
```

I did not hand-write the declaration into the artefacts on disk. It would have restored grading in
minutes and it changes no figure — but a control that works because someone patched its inputs is a
control keyed to today's answer, and the honest reading of this tree is that **no promote target can
currently be graded**, which is exactly what the census now says out loud instead of quietly. The
declarations arrive as each producer next runs: `live_decisions_latest.json` is regenerated by a
daemon and will be first, `run_output_latest.json` needs a ~13-minute annual report,
`value_cycle_ab_*` need a full A/B.

`docs/reports/run_output_latest.json` deserves naming separately: it will stay ungradable even after
the run that carries the new header lands, if that run predates it — the header was added on
2026-09-08 and the artefact on disk still has no `generated_at` at top level. It is the most-read
promote target in the tree, with eighteen binders, and it has never been able to say which run it is.

**So the refusing leg's reachability is proven by fixture, not by the tree**, and that is stated
rather than left to be discovered: `tests/tools/test_promoted_artefact_claim_census.py` runs the
poison round on both directions, and the live-artefact control
(`test_a_declared_field_that_no_longer_resolves_is_caught_on_the_live_artefacts`) declares itself an
equivalence today and asserts the census is REPORTING the emptiness rather than being quiet about it.

## 6. The control that stops this rotting the way the last one did

`tests/tools/test_every_promote_target_producer_declares_its_run_identity.py` — an AST scan, because
three of these four producers cannot be invoked in a test (a subprocess, a 13-minute world run, and
three of them). For each producer it asserts every dict literal carrying that producer's anchor key
also carries `run_identity_fields`, **and asserts the anchor is still found at all** — a scan that
matches no payloads passes exactly like one that matches six compliant ones.

Poison round run first and kept as its own test: the declaration is removed from
`tools/run_live_decisions.py`'s source text and the scan must name the line. Six payload dicts are
in scope across the four modules and all six declare.

## 7. Six baseline rows, and why they are not six new scanners

`tools/substring_source_scan_census --check` went from 0 NEW to 6, all in
`promoted_artefact_claim_census.py`, and I checked the cause before recording it rather than after:
with HEAD's copy of that one file in place the census reports **0 NEW**, so the rows are mine.

They are attribution churn, not mechanism. One nested closure moved out of `_artefact_dates` into
`_tokens_anywhere_in`, and taint that used to terminate inside that closure now crosses a call --
which is the same thing the baseline's own `why_this_count` records happening tree-wide on
2026-09-09 (187 → 352). The module's single real source-as-text reader, `_module_strings`, already
goes through `ast` and `tokenize` and is correctly not flagged. Rows added **by hand**; `--freeze`
would have rewritten every other lane's rows from a dirty tree.

## 8. One red I did not cause and did not bank

`tests/architecture/test_static_quality_ratchet.py` is red in the shared tree: `I001` counts 1308
against a frozen 1309. It is the mirror case -- the working tree is BETTER than the baseline --
and the file responsible is `tests/tools/test_generate_maturity_map_data.py`, another lane's
uncommitted import fix. Re-freezing to bank it would wedge every lane behind an uncommitted
change, so this lands via `tools.surgical_land`, which gates the tree the commit would create
(HEAD plus my hunks) rather than the shared working tree.

## 9. What is next

- **Not this turn:** the four producers' next natural runs are what make the census gradable again.
  Nothing needs doing to cause that except letting them run; the first one to land should be checked
  against `python3 -m tools.promoted_artefact_claim_census` to confirm its declaration resolves.
- **Open, and named here rather than filed as a separate finding:** `feed_claims` still cannot tell
  a dated historical record from a claim about the current run and still fails open at 70 rows. The
  repair is the same shape as this one — each feed FIELD declaring which population it is in — and
  it is now the only leg of this census left guessing.
